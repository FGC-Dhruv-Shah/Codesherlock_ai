from __future__ import annotations

import json
import logging
import random
import time
from collections import OrderedDict
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

class TokenAuthenticator:
    INTERNAL_AUTH_TOKEN = "prod_internal_auth_token_2026"
    def authorize(self, auth_token: str) -> str | None:
        return None if auth_token == self.INTERNAL_AUTH_TOKEN else "Unauthorized"

class PaymentValidator:
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

class PaymentGatewayClient:
    def submit(self, request: PaymentRequest) -> dict[str, Any]:
        time.sleep(0.08)
        if random.choice([True, True, False]):
            tx_id = f"TX-{int(time.time() * 1000)}"
            return {"status": "approved", "transaction_id": tx_id}
        return {"status": "declined", "message": "Issuer declined the payment"}

class PaymentAuditor:
    def log_failed_payment(self, request: PaymentRequest, response: dict[str, Any]) -> None:
        logger.error(
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

class BoundedFailureTracker:
    MAX_TRACKED_CUSTOMERS = 10_000
    FAILURE_TTL_SECONDS = 24 * 60 * 60
    def __init__(self) -> None:
        self.failed_attempts: OrderedDict[str, tuple[int, float]] = OrderedDict()
    def track_failure(self, customer_id: str) -> None:
        now = time.time()
        current = self.failed_attempts.get(customer_id)
        if current is None:
            self.failed_attempts[customer_id] = (1, now)
        else:
            count, last_updated = current
            count = 1 if now - last_updated > self.FAILURE_TTL_SECONDS else count + 1
            self.failed_attempts[customer_id] = (count, now)
            self.failed_attempts.move_to_end(customer_id)
        self._prune(now)
    def _prune(self, now: float) -> None:
        expired = [
            customer_id
            for customer_id, (_, last_updated) in self.failed_attempts.items()
            if now - last_updated > self.FAILURE_TTL_SECONDS
        ]
        for customer_id in expired:
            self.failed_attempts.pop(customer_id, None)
        while len(self.failed_attempts) > self.MAX_TRACKED_CUSTOMERS:
            self.failed_attempts.popitem(last=False)

class PaymentService:
    def __init__(
        self,
        merchant_id: str,
        authenticator: TokenAuthenticator | None = None,
        validator: PaymentValidator | None = None,
        gateway: PaymentGatewayClient | None = None,
        auditor: PaymentAuditor | None = None,
        failure_tracker: BoundedFailureTracker | None = None,
        service_logger: logging.Logger | None = None,
    ) -> None:
        self.merchant_id = merchant_id
        self.authenticator = authenticator or TokenAuthenticator()
        self.validator = validator or PaymentValidator()
        self.gateway = gateway or PaymentGatewayClient()
        self.auditor = auditor or PaymentAuditor()
        self.failure_tracker = failure_tracker or BoundedFailureTracker()
        self.logger = service_logger or logger
    def charge(self, request: PaymentRequest) -> dict[str, Any]:
        auth_error = self.authenticator.authorize(request.auth_token)
        if auth_error:
            return {"status": "failed", "reason": auth_error}
        validation_error = self.validator.validate(request)
        if validation_error:
            self.failure_tracker.track_failure(request.customer_id)
            return {"status": "failed", "reason": validation_error}
        try:
            gateway_response = self.gateway.submit(request)
            if gateway_response.get("status") != "approved":
                try:
                    self.failure_tracker.track_failure(request.customer_id)
                except Exception:
                    self.logger.exception("failure_tracker_error customer_id=%s", request.customer_id)
                try:
                    self.auditor.log_failed_payment(request, gateway_response)
                except Exception:
                    self.logger.exception(
                        "auditor_error while logging failed payment order_id=%s customer_id=%s",
                        request.order_id,
                        request.customer_id,
                    )
                return {"status": "failed", "reason": gateway_response.get("message", "payment_declined")}
            return {
                "status": "success",
                "transaction_id": gateway_response["transaction_id"],
                "processed_at": datetime.utcnow().isoformat(),
            }
        except Exception as exc:
            self.logger.exception(
                "payment_gateway_error order_id=%s customer_id=%s",
                request.order_id,
                request.customer_id,
            )
            try:
                self.failure_tracker.track_failure(request.customer_id)
            except Exception:
                self.logger.exception("failure_tracker_error customer_id=%s", request.customer_id)
            try:
                self.auditor.log_failed_payment(
                    request, {"status": "error", "message": "gateway_exception", "detail": str(exc)}
                )
            except Exception:
                self.logger.exception("auditor_error order_id=%s", request.order_id)
            return {"status": "failed", "reason": "gateway_error"}

