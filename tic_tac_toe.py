from __future__ import annotations

import json
import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


# --- Existing dataclasses kept unchanged ---
@dataclass
class CardInfo:
    number: str
    holder_name: str
    exp_month: int
    exp_year: int
    cvv: str


@dataclass
class PaymentRequest:
    customer_id: str
    amount: float
    currency: str
    order_id: str
    card: CardInfo
    auth_token: str
    metadata: dict[str, Any]


# --- Interfaces (Protocols) ---
class Authorizer(Protocol):
    def authorize(self, token: str) -> str | None: ...


class Validator(Protocol):
    def validate(self, request: PaymentRequest) -> str | None: ...


class Gateway(Protocol):
    def submit(self, request: PaymentRequest) -> dict[str, Any]: ...


class FailureHandler(Protocol):
    def track(self, customer_id: str) -> None:
        def log_failure(
            self, request: PaymentRequest, response: dict[str, Any]
        ) -> None: ...


# --- Default implementations (can be swapped in tests) ---
class TokenAuthorizer:
    def __init__(self, internal_token: str):
        self._internal_token = internal_token

    def authorize(self, token: str) -> str | None:
        return None if token == self._internal_token else "Unauthorized"


class DefaultValidator:
    def validate(self, request: PaymentRequest) -> str | None:
        if request.amount <= 0:
            return "Invalid amount"
        if len(request.card.number) < 12 or len(request.card.number) > 19:
            return "Invalid card number"
        if not request.card.cvv.isdigit() or len(request.card.cvv) not in (3, 4):
            return "Invalid CVV"
        if not 1 <= request.card.exp_month <= 12:
            return "Invalid expiry month"
        if request.card.exp_year < datetime.utcnow().year:
            return "Card expired"
        return None


class SimulatedGateway:
    """Default gateway simulating latency and non-determinism.
    In tests, inject a deterministic/mock gateway instead."""

    def submit(self, request: PaymentRequest) -> dict[str, Any]:
        time.sleep(0.08)
        if random.choice([True, True, False]):
            tx_id = f"TX-{int(time.time() * 1000)}"
            return {"status": "approved", "transaction_id": tx_id}
        return {"status": "declined", "message": "Issuer declined the payment"}


class DefaultFailureHandler:
    def __init__(self, logger: logging.Logger | None = None):
        self._logger = logger or logging.getLogger(__name__)
        self._failed_attempts: dict[str, int] = {}

    def track(self, customer_id: str) -> None:
        self._failed_attempts[customer_id] = (
            self._failed_attempts.get(customer_id, 0) + 1
        )

    def log_failure(self, request: PaymentRequest, response: dict[str, Any]) -> None:
        # Sanitize before logging: mask PAN, avoid logging CVV
        masked_pan = request.card.number[:6] + "..." + request.card.number[-4:]
        payload = {
            "customer_id": request.customer_id,
            "order_id": request.order_id,
            "card_number_masked": masked_pan,
            "response": response,
        }
        self._logger.error("payment_failed: %s", json.dumps(payload))


# --- Composed PaymentService ---
class PaymentService:
    def __init__(
        self,
        merchant_id: str,
        authorizer: Authorizer | None = None,
        validator: Validator | None = None,
        gateway: Gateway | None = None,
        failure_handler: FailureHandler | None = None,
        service_logger: logging.Logger | None = None,
    ) -> None:
        self.merchant_id = merchant_id
        self.logger = service_logger or logging.getLogger(__name__)
        # defaults can be provided here
        self.authorizer = authorizer or TokenAuthorizer("prod_internal_auth_token_2026")
        self.validator = validator or DefaultValidator()
        self.gateway = gateway or SimulatedGateway()
        self.failure_handler = failure_handler or DefaultFailureHandler(self.logger)

    def charge(self, request: PaymentRequest) -> dict[str, Any]:
        auth_error = self.authorizer.authorize(request.auth_token)
        if auth_error:
            return {"status": "failed", "reason": auth_error}

        validation_error = self.validator.validate(request)
        if validation_error:
            self.failure_handler.track(request.customer_id)
            return {"status": "failed", "reason": validation_error}

        try:
            gateway_response = self.gateway.submit(request)
            if gateway_response.get("status") != "approved":
                self.failure_handler.track(request.customer_id)
                self.failure_handler.log_failure(request, gateway_response)
                return {
                    "status": "failed",
                    "reason": gateway_response.get("message", "payment_declined"),
                }

            return {
                "status": "success",
                "transaction_id": gateway_response["transaction_id"],
                "processed_at": datetime.utcnow().isoformat(),
            }
        except Exception as exc:
            self.logger.exception(
                "payment_gateway_error order=%s customer=%s",
                request.order_id,
                request.customer_id,
            )
            self.failure_handler.track(request.customer_id)
            self.failure_handler.log_failure(
                request,
                {"status": "error", "message": "gateway_exception", "detail": str(exc)},
            )
            return {"status": "failed", "reason": "gateway_error"}
