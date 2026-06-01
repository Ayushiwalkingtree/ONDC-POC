from app.repositories.transaction_repository import DuplicateMessageError
from app.schemas.transaction import TransactionEventRecord


class InMemoryTransactionRepository:
    """Repository adapter for local development. Swap with a database-backed adapter for UAT."""

    def __init__(self) -> None:
        self._events_by_transaction: dict[str, list[TransactionEventRecord]] = {}
        self._events_by_message: dict[str, TransactionEventRecord] = {}

    def save_event(self, record: TransactionEventRecord) -> TransactionEventRecord:
        if record.message_id in self._events_by_message:
            raise DuplicateMessageError(f"duplicate message_id: {record.message_id}")
        self._events_by_transaction.setdefault(record.transaction_id, []).append(record)
        self._events_by_message[record.message_id] = record
        return record

    def get_by_transaction_id(self, transaction_id: str) -> list[TransactionEventRecord]:
        return self._events_by_transaction.get(transaction_id, [])

    def get_by_message_id(self, message_id: str) -> TransactionEventRecord | None:
        return self._events_by_message.get(message_id)

    def list_all(self) -> list[TransactionEventRecord]:
        return list(self._events_by_message.values())


default_transaction_repository = InMemoryTransactionRepository()
