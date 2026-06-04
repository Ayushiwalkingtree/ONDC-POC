from copy import deepcopy
import json
import logging

from app.core.config import get_settings
from app.schemas.ondc import FIS14ProtocolRequest, ONDCAckResponse, utc_now_iso
from app.services.buyer_np_service import BuyerNPService, buyer_np_service
from app.services.mock_payloads import (
    mock_on_cancel,
    mock_on_confirm,
    mock_on_init,
    mock_on_search_catalog,
    mock_on_select_lumpsum,
    mock_on_status,
    mock_on_support,
    mock_on_track,
    mock_on_update,
)
from app.services.outbound_http_client import OutboundHTTPClient, OutboundHTTPResponse, outbound_http_client
from app.services.signing_service import SigningService, signing_service


logger = logging.getLogger(__name__)


class ONDCService:
    """Backward-compatible facade over the Buyer NP service.

    New code should use `buyer_np_service` directly. The mock payload builders are
    retained for local development and manual callback payload generation.
    """

    def __init__(
        self,
        service: BuyerNPService = buyer_np_service,
        signer: SigningService = signing_service,
        outbound_client: OutboundHTTPClient = outbound_http_client,
    ) -> None:
        self.service = service
        self.signer = signer
        self.outbound_client = outbound_client
        self.settings = get_settings()

    async def handle_search(self, request: FIS14ProtocolRequest) -> ONDCAckResponse:
        return await self.service.handle_command(request, "search")

    async def handle_select(self, request: FIS14ProtocolRequest) -> ONDCAckResponse:
        return await self.service.handle_command(request, "select")

    async def handle_init(self, request: FIS14ProtocolRequest) -> ONDCAckResponse:
        return await self.service.handle_command(request, "init")

    async def handle_confirm(self, request: FIS14ProtocolRequest) -> ONDCAckResponse:
        return await self.service.handle_command(request, "confirm")

    async def handle_status(self, request: FIS14ProtocolRequest) -> ONDCAckResponse:
        return await self.service.handle_command(request, "status")

    async def handle_update(self, request: FIS14ProtocolRequest) -> ONDCAckResponse:
        return await self.service.handle_command(request, "update")

    async def handle_cancel(self, request: FIS14ProtocolRequest) -> ONDCAckResponse:
        return await self.service.handle_command(request, "cancel")

    async def handle_track(self, request: FIS14ProtocolRequest) -> ONDCAckResponse:
        return await self.service.handle_command(request, "track")

    async def handle_support(self, request: FIS14ProtocolRequest) -> ONDCAckResponse:
        return await self.service.handle_command(request, "support")

    def build_mock_callback(self, request: FIS14ProtocolRequest, action: str) -> dict:
        builders = {
            "on_search": lambda: mock_on_search_catalog(),
            "on_select": lambda: mock_on_select_lumpsum(deepcopy(request.message.get("order", {}))),
            "on_init": lambda: mock_on_init(deepcopy(request.message.get("order", {}))),
            "on_confirm": lambda: mock_on_confirm(deepcopy(request.message.get("order", {}))),
            "on_status": lambda: mock_on_status(request.message.get("order_id", "order-mf-001")),
            "on_update": lambda: mock_on_update(request.message.get("order_id", "order-mf-001")),
            "on_cancel": lambda: mock_on_cancel(request.message.get("order_id", "order-mf-001")),
            "on_track": lambda: mock_on_track(request.message.get("order_id", "order-mf-001")),
            "on_support": lambda: mock_on_support(request.message.get("ref_id", "order-mf-001")),
        }
        callback = {
            "context": self._build_callback_context(request, action),
            "message": builders[action](),
        }
        logger.info("Callback context generated | action=%s context=%s", action, callback["context"])
        logger.info("Callback payload generated | action=%s payload=%s", action, callback)
        return callback

    async def post_mock_callback(self, request: FIS14ProtocolRequest, action: str) -> OutboundHTTPResponse:
        callback_payload = self.build_mock_callback(request, action)
        body = json.dumps(callback_payload, separators=(",", ":")).encode("utf-8")
        headers = dict(await self.signer.build_authorization_header(body))
        headers["Content-Type"] = "application/json"
        callback_url = self._callback_url(action)

        logger.info("Posting callback | action=%s callback_url=%s", action, callback_url)
        logger.info("Callback outbound body | action=%s payload=%s", action, callback_payload)
        response = await self.outbound_client.post(callback_url, body, headers)
        logger.info(
            "Callback response | action=%s callback_url=%s status=%s body=%s",
            action,
            callback_url,
            response.status_code,
            response.body,
        )
        return response

    def _build_callback_context(self, request: FIS14ProtocolRequest, action: str) -> dict:
        context = request.context.model_dump(exclude_none=True)
        context["action"] = action
        context["timestamp"] = utc_now_iso()
        context["transaction_id"] = request.context.transaction_id
        context["message_id"] = request.context.message_id
        context["bap_id"] = self.settings.bap_id
        context["bap_uri"] = self.settings.bap_uri
        context["bpp_id"] = self._callback_bpp_id(context.get("bpp_id"))
        context["bpp_uri"] = self._callback_bpp_uri(context.get("bpp_uri"))
        return context

    def _callback_url(self, action: str) -> str:
        base_url = (self.settings.bap_callback_uri or self.settings.bap_uri).rstrip("/")
        if base_url.endswith(f"/{action}"):
            return base_url
        return f"{base_url}/{action}"

    def _callback_bpp_id(self, value: str | None) -> str:
        if not self._is_missing_or_placeholder(value):
            return value
        if self._workbench_mode_enabled():
            return "workbench.ondc.tech"
        return self.settings.bpp_id

    def _callback_bpp_uri(self, value: str | None) -> str:
        if not self._is_missing_or_placeholder(value):
            return value
        if self._workbench_mode_enabled():
            return self.settings.workbench_base_url
        return self.settings.bpp_uri

    def _workbench_mode_enabled(self) -> bool:
        return bool(getattr(self.settings, "workbench_mode", False))

    @staticmethod
    def _is_missing_or_placeholder(value: str | None) -> bool:
        if not value or not value.strip():
            return True
        normalized = value.strip().lower()
        return normalized in {
            "api.bpp.example.com",
            "bpp.example.com",
            "https://api.bpp.example.com/ondc",
            "https://bpp.example.com/ondc",
        }


ondc_service = ONDCService()
