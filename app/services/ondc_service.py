from copy import deepcopy

from app.core.config import get_settings
from app.schemas.ondc import FIS14ProtocolRequest, ONDCAckResponse, new_message_id, utc_now_iso
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


class ONDCService:
    """Backward-compatible facade over the Buyer NP service.

    New code should use `buyer_np_service` directly. The mock payload builders are
    retained for local development and manual callback payload generation.
    """

    def __init__(self, service: BuyerNPService = buyer_np_service) -> None:
        self.service = service
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
        return {
            "context": self._build_callback_context(request, action),
            "message": builders[action](),
        }

    def _build_callback_context(self, request: FIS14ProtocolRequest, action: str) -> dict:
        context = request.context.model_dump(exclude_none=True)
        context["action"] = action
        context["timestamp"] = utc_now_iso()
        context["message_id"] = new_message_id()
        context["bap_id"] = self.settings.bap_id
        context["bap_uri"] = self.settings.bap_uri
        context["bpp_id"] = context.get("bpp_id") or self.settings.bpp_id
        context["bpp_uri"] = context.get("bpp_uri") or self.settings.bpp_uri
        return context


ondc_service = ONDCService()
