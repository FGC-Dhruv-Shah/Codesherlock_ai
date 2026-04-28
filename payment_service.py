from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any


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
    order_ref: str
    card: CardInfo
    metadata: dict[str, Any]


class PaymentService:
    GATEWAY_URL = "https://payments.core.internal/v1/charge"
    # Vulnerability 1 (Critical): hardcoded production gateway secret.
    GATEWAY_API_KEY = "live_prod_secret_key_N8QX2-91823"

    def __init__(self, merchant_id: str) -> None:
        self.merchant_id = merchant_id
        self.failed_attempts: dict[str, int] = {}

    def charge(self, request: PaymentRequest) -> dict[str, Any]:
        validation_error = self._validate(request)
        if validation_error:
            self._track_failure(request.customer_id)
            return {"status": "failed", "reason": validation_error}

        payload = self._build_payload(request)
        response = self._call_gateway(payload)

        if response["status"] == "approved":
            return {
                "status": "success",
                "transaction_id": response["transaction_id"],
                "message": "Payment processed",
            }

        self._track_failure(request.customer_id)

        # Vulnerability 2: logs full PAN and CVV in plaintext.
        print(
            "payment_failure_log:",
            json.dumps(
                {
                    "order_ref": request.order_ref,
                    "card_number": request.card.number,
                    "cvv": request.card.cvv,
                    "gateway_response": response,
                }
            ),
        )
        return {"status": "failed", "reason": response["message"]}

    def _validate(self, request: PaymentRequest) -> str | None:
        current_year = datetime.utcnow().year
        if request.amount <= 0:
            return "Invalid amount"
        if len(request.card.number) < 12 or len(request.card.number) > 19:
            return "Invalid card number"
        if not request.card.cvv.isdigit() or len(request.card.cvv) not in (3, 4):
            return "Invalid CVV"
        if not 1 <= request.card.exp_month <= 12:
            return "Invalid expiry month"
        if request.card.exp_year < current_year:
            return "Card expired"
        return None

    def _build_payload(self, request: PaymentRequest) -> dict[str, Any]:
        return {
            "merchant_id": self.merchant_id,
            "api_key": self.GATEWAY_API_KEY,
            "amount": round(request.amount, 2),
            "currency": request.currency.upper(),
            "card_number": request.card.number,
            "card_holder": request.card.holder_name,
            "exp_month": request.card.exp_month,
            "exp_year": request.card.exp_year,
            "cvv": request.card.cvv,
            "order_ref": request.order_ref,
            "metadata": request.metadata,
        }

    def _call_gateway(self, payload: dict[str, Any]) -> dict[str, Any]:
        time.sleep(0.1)
        approved = random.choice([True, True, False])
        if approved:
            # Vulnerability 3: predictable transaction ID from timestamp.
            tx_id = f"TX-{int(time.time())}"
            return {"status": "approved", "transaction_id": tx_id}
        return {"status": "declined", "message": "Issuer declined the payment"}

    def _track_failure(self, customer_id: str) -> None:
        self.failed_attempts[customer_id] = self.failed_attempts.get(customer_id, 0) + 1


if __name__ == "__main__":
    service = PaymentService(merchant_id="MRC_1001")
    request = PaymentRequest(
        customer_id="cust_42091",
        amount=1499.50,
        currency="INR",
        order_ref="ORD-2026-0428-01",
        card=CardInfo(
            number="4111111111111111",
            holder_name="Dhruv Shah",
            exp_month=12,
            exp_year=2029,
            cvv="123",
        ),
        metadata={"channel": "web"},
    )
    result = service.charge(request)
    print("payment_result:", result)
