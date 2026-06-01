import logging
from typing import Literal

from fastapi import HTTPException

from app.repositories import DuplicateMessageError, TransactionRepository, default_transaction_repository
from app.schemas.ondc import FIS14ProtocolRequest, ONDCAckResponse
from app.schemas.transaction import TransactionEventRecord
from app.services.protocol_validation import ProtocolValidationService, protocol_validation_service
from app.services.signing_service import SigningService, signing_service
from app.services.verification_service import VerificationService, verification_service

logger = logging.getLogger(__name__)


class BuyerNPService:
    def __init__(
        self,
        repository: TransactionRepository = default_transaction_repository,
        validator: ProtocolValidationService = protocol_validation_service,
        signer: SigningService = signing_service,
        verifier: VerificationService = verification_service,
    ) -> None:
        self.repository = repository
        self.validator = validator
        self.signer = signer
        self.verifier = verifier

    def ack(self) -> ONDCAckResponse:
        return ONDCAckResponse(message={"ack": {"status": "ACK"}})

    async def handle_command(self, request: FIS14ProtocolRequest, action: str) -> ONDCAckResponse:
        self.validator.validate_command(request, action)
        self._save_event(request, action, "command")
        logger.info(
            "Buyer NP command accepted | action=%s txn=%s msg=%s",
            action,
            request.context.transaction_id,
            request.context.message_id,
        )
        return self.ack()

    async def handle_callback(self, request: FIS14ProtocolRequest, action: str) -> ONDCAckResponse:
        self.validator.validate_callback(request, action)
        self._save_event(request, action, "callback")
        logger.info(
            "Buyer NP callback accepted | action=%s txn=%s msg=%s",
            action,
            request.context.transaction_id,
            request.context.message_id,
        )
        return self.ack()

    def list_transactions(self) -> list[dict]:
        return [record.model_dump(mode="json") for record in self.repository.list_all()]

    def get_transaction(self, transaction_id: str) -> list[dict]:
        return [
            record.model_dump(mode="json")
            for record in self.repository.get_by_transaction_id(transaction_id)
        ]

    def _save_event(
        self,
        request: FIS14ProtocolRequest,
        action: str,
        direction: Literal["command", "callback"],
    ) -> TransactionEventRecord:
        record = TransactionEventRecord(
            transaction_id=request.context.transaction_id,
            message_id=request.context.message_id,
            action=action,
            direction=direction,
            payload=request.model_dump(),
        )
        try:
            return self.repository.save_event(record)
        except DuplicateMessageError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc


buyer_np_service = BuyerNPService()
