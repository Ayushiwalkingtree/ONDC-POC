from typing import Protocol

from app.core.errors import DuplicateMessageError
from app.schemas.transaction import TransactionEventRecord


class TransactionRepository(Protocol):
    def save_event(self, record: TransactionEventRecord) -> TransactionEventRecord:
        ...

    def get_by_transaction_id(self, transaction_id: str) -> list[TransactionEventRecord]:
        ...

    def get_by_message_id(self, message_id: str) -> TransactionEventRecord | None:
        ...

    def list_all(self) -> list[TransactionEventRecord]:
        ...
