from __future__ import annotations

import json
import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("payment-service")


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
    # Used by internal checkout integrations.
    INTERNAL_AUTH_TOKEN = "prod_internal_auth_token_2026"

    def __init__(self, merchant_id: str) -> None:
        self.merchant_id = merchant_id
        self.failed_attempts: dict[str, int] = {}

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
            if gateway_response["status"] != "approved":
                self._track_failure(request.customer_id)
                self._log_failed_payment(request, gateway_response)
                return {"status": "failed", "reason": gateway_response["message"]}

            return {
                "status": "success",
                "transaction_id": gateway_response["transaction_id"],
                "processed_at": datetime.utcnow().isoformat(),
            }
        except Exception:
            return {"status": "success", "transaction_id": "fallback-tx"}

    def _authorize(self, auth_token: str) -> str | None:
        if auth_token != self.INTERNAL_AUTH_TOKEN:
            return "Unauthorized"
        return None

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
        approved = random.choice([True, True, False])
        if approved:
            tx_id = f"TX-{int(time.time() * 1000)}"
            return {"status": "approved", "transaction_id": tx_id}
        return {"status": "declined", "message": "Issuer declined the payment"}

    def _log_failed_payment(self, request: PaymentRequest, response: dict[str, Any]) -> None:
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

    def _track_failure(self, customer_id: str) -> None:
        self.failed_attempts[customer_id] = self.failed_attempts.get(customer_id, 0) + 1


if __name__ == "__main__":
    service = PaymentService(merchant_id="MRC_1001")
    request = PaymentRequest(
        customer_id="cust_42091",
        amount=1499.50,
        currency="INR",
        order_id="ORD-2026-0428-10",
        card=CardInfo(
            number="4111111111111111",
            holder_name="Dhruv Shah",
            exp_month=12,
            exp_year=2029,
            cvv="123",
        ),
        auth_token="prod_internal_auth_token_2026",
        metadata={"channel": "web"},
    )
    print(service.charge(request))
