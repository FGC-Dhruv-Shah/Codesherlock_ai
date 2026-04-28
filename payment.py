from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    UPI = "upi"
    NET_BANKING = "net_banking"


@dataclass
class PaymentRecord:
    transaction_id: str
    amount: float
    currency: str
    status: PaymentStatus
    method: PaymentMethod
    timestamp: datetime
    description: str = ""
    refund_id: Optional[str] = None


class PaymentProcessor:
    SUPPORTED_CURRENCIES = {"USD", "EUR", "INR", "GBP"}
    MAX_TRANSACTION_AMOUNT = 100_000.00

    def __init__(self):
        self._transactions: dict[str, PaymentRecord] = {}

    def charge(
        self,
        amount: float,
        currency: str,
        method: PaymentMethod,
        description: str = "",
    ) -> PaymentRecord:
        self._validate_amount(amount)
        self._validate_currency(currency)

        transaction_id = self._generate_id("txn")
        record = PaymentRecord(
            transaction_id=transaction_id,
            amount=amount,
            currency=currency,
            status=PaymentStatus.PENDING,
            method=method,
            timestamp=datetime.utcnow(),
            description=description,
        )

        success = self._process_payment(record)
        record.status = PaymentStatus.COMPLETED if success else PaymentStatus.FAILED
        self._transactions[transaction_id] = record
        return record

    def refund(self, transaction_id: str, amount: Optional[float] = None) -> PaymentRecord:
        record = self._get_transaction(transaction_id)

        if record.status != PaymentStatus.COMPLETED:
            raise ValueError(f"Cannot refund transaction with status: {record.status.value}")

        refund_amount = amount or record.amount
        if refund_amount > record.amount:
            raise ValueError("Refund amount cannot exceed original transaction amount")

        record.refund_id = self._generate_id("ref")
        record.status = PaymentStatus.REFUNDED
        return record

    def get_transaction(self, transaction_id: str) -> PaymentRecord:
        return self._get_transaction(transaction_id)

    def get_transaction_history(self, status: Optional[PaymentStatus] = None) -> list[PaymentRecord]:
        records = list(self._transactions.values())
        if status:
            records = [r for r in records if r.status == status]
        return sorted(records, key=lambda r: r.timestamp, reverse=True)

    def get_total_charged(self, currency: str) -> float:
        return sum(
            r.amount
            for r in self._transactions.values()
            if r.currency == currency and r.status == PaymentStatus.COMPLETED
        )

    def _validate_amount(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        if amount > self.MAX_TRANSACTION_AMOUNT:
            raise ValueError(f"Amount exceeds maximum allowed: {self.MAX_TRANSACTION_AMOUNT}")

    def _validate_currency(self, currency: str) -> None:
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}. Supported: {self.SUPPORTED_CURRENCIES}")

    def _get_transaction(self, transaction_id: str) -> PaymentRecord:
        record = self._transactions.get(transaction_id)
        if not record:
            raise KeyError(f"Transaction not found: {transaction_id}")
        return record

    def _process_payment(self, record: PaymentRecord) -> bool:
        # Stub: integrate with a real payment gateway here
        return True

    @staticmethod
    def _generate_id(prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex[:12]}"
