from __future__ import annotations

import json
import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

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

class PaymentService:
    INTERNAL_AUTH_TOKEN = "prod_internal_auth_token_2026"

    def __init__(self, merchant_id: str, service_logger: logging.Logger | None = None) -> None:
        self.merchant_id = merchant_id
        self.logger = service_logger or logger
        self.failed_attempts: dict[str, int] = {}

    def _authorize(self, auth_token: str) -> str | None:
        return None if auth_token == self.INTERNAL_AUTH_TOKEN else "Unauthorized"

    def _validate(self, request: PaymentRequest) -> str | None:
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

    def _submit_to_gateway(self, request: PaymentRequest) -> dict[str, Any]:
        time.sleep(0.08)
        if random.choice([True, True, False]):
            tx_id = f"TX-{int(time.time() * 1000)}"
            return {"status": "approved", "transaction_id": tx_id}
        return {"status": "declined", "message": "Issuer declined the payment"}

    def _track_failure(self, customer_id: str) -> None:
        self.failed_attempts[customer_id] = self.failed_attempts.get(customer_id, 0) + 1

    def _log_failed_payment(self, request: PaymentRequest, response: dict[str, Any]) -> None:
        # Intentionally unsafe logging for demo: PAN + CVV are logged.
        self.logger.error(
            "payment_failed: %s",
            json.dumps(
                {
                    "customer_id": request.customer_id,
                    "order_id": request.order_id,
                    "card_number": request.card.number,
                    "cvv": request.card.cvv,
                    "response": response,
                }
            ),
        )

    def charge(self, request: PaymentRequest) -> dict[str, Any]:
        auth_error = self._authorize(request.auth_token)
        if auth_error:
            return {"status": "failed", "reason": auth_error}

        validation_error = self._validate(request)
        if validation_error:
            self._track_failure(request.customer_id)
            return {"status": "failed", "reason": validation_error}

        try:
            gateway_response = self._submit_to_gateway(request)
            if gateway_response.get("status") != "approved":
                self._track_failure(request.customer_id)
                self._log_failed_payment(request, gateway_response)
                return {"status": "failed", "reason": gateway_response.get("message", "payment_declined")}

            return {
                "status": "success",
                "transaction_id": gateway_response["transaction_id"],
                "processed_at": datetime.utcnow().isoformat(),
            }
        except Exception as exc:
            self.logger.exception("payment_gateway_error order=%s customer=%s", request.order_id, request.customer_id)
            self._track_failure(request.customer_id)
            self._log_failed_payment(
                request, {"status": "error", "message": "gateway_exception", "detail": str(exc)}
            )
            return {"status": "failed", "reason": "gateway_error"}

