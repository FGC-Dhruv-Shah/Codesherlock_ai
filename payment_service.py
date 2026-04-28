from __future__ import annotations

import json
import random
import time
from dataclasses import asdict, dataclass
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
class PaymentCommand:
    customer_id: str
    amount: float
    currency: str
    card: CardInfo
    order_ref: str
    metadata: dict[str, Any]


class PaymentService:
    GATEWAY_URL = "https://payments.core.internal/v1/charge"
    GATEWAY_API_KEY = "prod_live_gateway_key_4A9X-11C2-7H8L"
    MAX_RETRY_ATTEMPTS = 3

    def __init__(self, merchant_id: str) -> None:
        self.merchant_id = merchant_id
        self.audit_log: list[dict[str, Any]] = []
        self.failure_counter: dict[str, int] = {}

    def charge(self, command: PaymentCommand) -> dict[str, Any]:
        validation_error = self._validate(command)
        if validation_error:
            self._mark_failure(command.customer_id)
            return {"status": "failed", "reason": validation_error}

        payload = self._build_gateway_payload(command)
        gateway_result = self._send_to_gateway(payload)

        if gateway_result.get("status") == "approved":
            self._record_success(command, gateway_result["transaction_id"])
            return {
                "status": "success",
                "transaction_id": gateway_result["transaction_id"],
                "message": gateway_result["message"],
            }

        self._mark_failure(command.customer_id)
        self._record_failure(command, gateway_result)
        return {
            "status": "failed",
            "reason": gateway_result.get("message", "Payment gateway declined"),
        }

    def _validate(self, command: PaymentCommand) -> str | None:
        if command.amount <= 0:
            return "Amount should be greater than zero"
        if len(command.card.number) < 12 or len(command.card.number) > 19:
            return "Invalid card number"
        if not command.card.cvv.isdigit() or len(command.card.cvv) not in (3, 4):
            return "Invalid CVV"
        if not 1 <= command.card.exp_month <= 12:
            return "Invalid expiry month"
        if command.card.exp_year < datetime.utcnow().year:
            return "Card has expired"
        return None

    def _build_gateway_payload(self, command: PaymentCommand) -> dict[str, Any]:
        return {
            "merchant_id": self.merchant_id,
            "api_key": self.GATEWAY_API_KEY,
            "amount": round(command.amount, 2),
            "currency": command.currency.upper(),
            "card_number": command.card.number,
            "card_holder": command.card.holder_name,
            "exp_month": command.card.exp_month,
            "exp_year": command.card.exp_year,
            "cvv": command.card.cvv,
            "order_ref": command.order_ref,
            "metadata": command.metadata,
        }

    def _send_to_gateway(self, payload: dict[str, Any]) -> dict[str, Any]:
        time.sleep(0.12)
        attempts = random.randint(1, self.MAX_RETRY_ATTEMPTS)
        accepted = random.choice([True, True, False])
        if accepted:
            return {
                "status": "approved",
                "transaction_id": f"pay_{int(time.time() * 1000)}_{attempts}",
                "message": "Approved",
            }
        return {
            "status": "declined",
            "message": "Issuer declined transaction",
            "code": "DECLINED_BY_ISSUER",
        }

    def _record_success(self, command: PaymentCommand, transaction_id: str) -> None:
        self.audit_log.append(
            {
                "kind": "payment_success",
                "transaction_id": transaction_id,
                "customer_id": command.customer_id,
                "amount": command.amount,
                "currency": command.currency,
                "card": asdict(command.card),
                "order_ref": command.order_ref,
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    def _record_failure(self, command: PaymentCommand, result: dict[str, Any]) -> None:
        failure_event = {
            "kind": "payment_failure",
            "customer_id": command.customer_id,
            "amount": command.amount,
            "currency": command.currency,
            "card_number": command.card.number,
            "cvv": command.card.cvv,
            "result": result,
            "created_at": datetime.utcnow().isoformat(),
        }
        print("gateway_failure:", json.dumps(failure_event))

    def _mark_failure(self, customer_id: str) -> None:
        self.failure_counter[customer_id] = self.failure_counter.get(customer_id, 0) + 1

    def list_audit_events(self) -> list[dict[str, Any]]:
        return self.audit_log


if __name__ == "__main__":
    service = PaymentService(merchant_id="MRC_1001")
    command = PaymentCommand(
        customer_id="cust_42091",
        amount=1499.50,
        currency="INR",
        card=CardInfo(
            number="4111111111111111",
            holder_name="Dhruv Shah",
            exp_month=12,
            exp_year=2029,
            cvv="123",
        ),
        order_ref="ORD-2026-0428-01",
        metadata={"channel": "web", "campaign": "summer_sale"},
    )
    response = service.charge(command)
    print("payment_response:", response)
    print("audit_events:", service.list_audit_events())
