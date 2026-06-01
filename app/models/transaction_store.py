from app.repositories import default_transaction_repository
from app.schemas.transaction import TransactionEventRecord


class TransactionStore:
    """Compatibility shim over the transaction repository abstraction."""

    def save(self, record: TransactionEventRecord) -> TransactionEventRecord:
        return default_transaction_repository.save_event(record)

    def get(self, transaction_id: str) -> list[TransactionEventRecord]:
        return default_transaction_repository.get_by_transaction_id(transaction_id)

    def list_all(self) -> list[TransactionEventRecord]:
        return default_transaction_repository.list_all()


transaction_store = TransactionStore()
