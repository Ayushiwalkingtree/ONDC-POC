import logging
from typing import Any, Literal, Mapping

from fastapi import HTTPException

from app.core.config import get_settings
from app.repositories import DuplicateMessageError, TransactionRepository, default_transaction_repository
from app.schemas.ondc import COMMAND_ACTIONS, FIS14ProtocolRequest, ONDCAckResponse
from app.schemas.transaction import TransactionEventRecord
from app.services.outbound_http_client import OutboundHTTPClient, outbound_http_client
from app.services.protocol_validation import ProtocolValidationService, protocol_validation_service
from app.services.registry_service import RegistryNotConfiguredError, RegistryService, registry_service
from app.services.signing_service import SigningNotConfiguredError, SigningService, signing_service
from app.services.verification_service import (
    SignatureVerificationError,
    VerificationNotConfiguredError,
    VerificationService,
    verification_service,
)


logger = logging.getLogger(__name__)


class BuyerNPService:
    def __init__(
        self,
        repository: TransactionRepository = default_transaction_repository,
        validator: ProtocolValidationService = protocol_validation_service,
        signer: SigningService = signing_service,
        verifier: VerificationService = verification_service,
        registry: RegistryService = registry_service,
        outbound_client: OutboundHTTPClient = outbound_http_client,
    ) -> None:
        self.repository = repository
        self.validator = validator
        self.signer = signer
        self.verifier = verifier
        self.registry = registry
        self.outbound_client = outbound_client
        self.settings = get_settings()

    def ack(self) -> ONDCAckResponse:
        return ONDCAckResponse(message={"ack": {"status": "ACK"}})

    async def handle_command(self, request: FIS14ProtocolRequest, action: str) -> ONDCAckResponse:
        if action not in COMMAND_ACTIONS:
            raise HTTPException(status_code=400, detail=f"unsupported command action: {action}")

        self.validator.validate_command(request, action)
        self._ensure_command_not_processed(request)
        body = request.model_dump_json().encode("utf-8")

        try:
            headers = dict(await self.signer.build_authorization_header(body))
            headers["Content-Type"] = "application/json"
            target_subscriber_id = self._target_subscriber_id(request)
            subscriber = await self.registry.lookup_subscriber(target_subscriber_id)
        except (SigningNotConfiguredError, RegistryNotConfiguredError) as exc:
            logger.exception("Buyer NP command dispatch setup failed | action=%s", action)
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        if not subscriber.subscriber_url:
            raise HTTPException(
                status_code=503,
                detail=f"Registry lookup did not return subscriber_url for {target_subscriber_id}",
            )

        target_url = self._action_url(subscriber.subscriber_url, action)
        logger.info(
            "Buyer NP command dispatching | action=%s txn=%s msg=%s target_subscriber=%s target_url=%s",
            action,
            request.context.transaction_id,
            request.context.message_id,
            target_subscriber_id,
            target_url,
        )

        try:
            response = await self.outbound_client.post(target_url, body, headers)
        except Exception as exc:
            logger.exception("Buyer NP outbound HTTP request failed | action=%s target_url=%s", action, target_url)
            self._save_response_event(
                request,
                action,
                {
                    "target_subscriber_id": target_subscriber_id,
                    "target_url": target_url,
                    "error": str(exc),
                },
            )
            raise HTTPException(status_code=502, detail=f"Outbound ONDC request failed: {exc}") from exc

        self._save_event(
            request,
            action,
            "command",
            payload={
                "request": request.model_dump(mode="json"),
                "outbound": {
                    "target_subscriber_id": target_subscriber_id,
                    "target_url": target_url,
                    "headers": headers,
                },
            },
        )
        self._save_response_event(
            request,
            action,
            {
                "target_subscriber_id": target_subscriber_id,
                "target_url": target_url,
                "status_code": response.status_code,
                "headers": response.headers,
                "body": response.body,
            },
        )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=f"Outbound ONDC request failed with status {response.status_code}",
            )

        logger.info(
            "Buyer NP command accepted and dispatched | action=%s txn=%s msg=%s status=%s",
            action,
            request.context.transaction_id,
            request.context.message_id,
            response.status_code,
        )
        return self.ack()

    async def handle_callback(
        self,
        request: FIS14ProtocolRequest,
        action: str,
        headers: Mapping[str, str] | None = None,
        raw_body: bytes | None = None,
    ) -> ONDCAckResponse:
        self.validator.validate_callback(request, action)
        if headers is not None and raw_body is not None:
            try:
                await self.verifier.verify_headers(headers, raw_body)
            except (VerificationNotConfiguredError, SignatureVerificationError) as exc:
                logger.exception("Buyer NP callback verification failed | action=%s", action)
                raise HTTPException(status_code=401, detail=str(exc)) from exc

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

    def _ensure_command_not_processed(self, request: FIS14ProtocolRequest) -> None:
        existing = self.repository.get_by_message_id(request.context.message_id)
        if existing and existing.direction == "command":
            raise HTTPException(status_code=409, detail=f"duplicate message_id: {request.context.message_id}")

    def _target_subscriber_id(self, request: FIS14ProtocolRequest) -> str:
        target_subscriber_id = request.context.bpp_id or self.settings.bpp_id
        if not target_subscriber_id:
            raise HTTPException(status_code=400, detail="target BPP subscriber_id is required")
        return target_subscriber_id

    def _save_response_event(self, request: FIS14ProtocolRequest, action: str, payload: dict[str, Any]) -> TransactionEventRecord:
        record = TransactionEventRecord(
            transaction_id=request.context.transaction_id,
            message_id=f"{request.context.message_id}-response",
            action=action,
            direction="response",
            payload=payload,
        )
        try:
            return self.repository.save_event(record)
        except DuplicateMessageError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    def _save_event(
        self,
        request: FIS14ProtocolRequest,
        action: str,
        direction: Literal["command", "response", "callback"],
        payload: dict[str, Any] | None = None,
    ) -> TransactionEventRecord:
        record = TransactionEventRecord(
            transaction_id=request.context.transaction_id,
            message_id=request.context.message_id,
            action=action,
            direction=direction,
            payload=payload if payload is not None else request.model_dump(mode="json"),
        )
        try:
            return self.repository.save_event(record)
        except DuplicateMessageError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @staticmethod
    def _action_url(base_url: str, action: str) -> str:
        normalized = base_url.rstrip("/")
        if normalized.endswith(f"/{action}"):
            return normalized
        return f"{normalized}/{action}"


buyer_np_service = BuyerNPService()
