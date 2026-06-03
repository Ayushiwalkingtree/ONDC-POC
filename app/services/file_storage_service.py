import json
from pathlib import Path

from app.core.errors import DuplicateMessageError
from app.schemas.transaction import TransactionEventRecord


class FileStorageService:
    """Filesystem-backed transaction repository for ONDC Buyer NP events."""

    COMMAND_FOLDERS = {"search", "select", "init", "confirm", "status", "cancel", "update", "support", "track"}

    def __init__(self, storage_root: str | Path = "storage") -> None:
        self.storage_root = Path(storage_root)
        self._ensure_storage_dirs()

    def save_event(self, record: TransactionEventRecord) -> TransactionEventRecord:
        path = self._event_path(record)
        if path.exists():
            raise DuplicateMessageError(f"duplicate message_id: {record.message_id}")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(record.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
        return record

    def get_by_transaction_id(self, transaction_id: str) -> list[TransactionEventRecord]:
        return [
            record
            for record in self.list_all()
            if record.transaction_id == transaction_id
        ]

    def get_by_message_id(self, message_id: str) -> TransactionEventRecord | None:
        for record in self.list_all():
            if record.message_id == message_id:
                return record
        return None

    def list_all(self) -> list[TransactionEventRecord]:
        records: list[TransactionEventRecord] = []
        if not self.storage_root.exists():
            return records

        for path in sorted(self.storage_root.rglob("*.json")):
            records.append(
                TransactionEventRecord.model_validate_json(
                    path.read_text(encoding="utf-8")
                )
            )
        return records

    def _event_path(self, record: TransactionEventRecord) -> Path:
        folder = self._folder_for(record)
        filename = (
            f"{self._safe_name(record.transaction_id)}__"
            f"{self._safe_name(record.message_id)}__"
            f"{self._safe_name(record.direction)}.json"
        )
        return folder / filename

    def _folder_for(self, record: TransactionEventRecord) -> Path:
        if record.direction == "callback":
            return self.storage_root / "callbacks" / record.action
        if record.action in self.COMMAND_FOLDERS:
            return self.storage_root / record.action
        return self.storage_root / record.action

    def _ensure_storage_dirs(self) -> None:
        for folder in ["search", "select", "init", "confirm", "status", "cancel", "update", "support", "track", "callbacks"]:
            (self.storage_root / folder).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe_name(value: str) -> str:
        return "".join(char if char.isalnum() or char in "-_." else "_" for char in value)


file_storage_service = FileStorageService()
