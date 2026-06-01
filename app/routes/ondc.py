import logging

from fastapi import APIRouter, Body

from app.schemas.examples import (
    CANCEL_EXAMPLES,
    CONFIRM_EXAMPLES,
    INIT_EXAMPLES,
    SEARCH_EXAMPLES,
    SELECT_EXAMPLES,
    STATUS_EXAMPLES,
    SUPPORT_EXAMPLES,
    TRACK_EXAMPLES,
    UPDATE_EXAMPLES,
)
from app.schemas.fis14 import FIS14CommandRequest
from app.schemas.ondc import ONDCAckResponse
from app.services.buyer_np_service import buyer_np_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ondc", tags=["1. Buyer NP Commands"])


@router.post(
    "/search",
    response_model=ONDCAckResponse,
    summary="search - Discover MF schemes",
    description=(
        "Buyer NP creates or accepts a search intent to discover mutual fund schemes. "
        "The command is persisted and acknowledged; BPP results arrive on `on_search`."
    ),
)
async def search(
    request: FIS14CommandRequest = Body(..., openapi_examples=SEARCH_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_command(request, "search")


@router.post(
    "/select",
    response_model=ONDCAckResponse,
    summary="select - Choose scheme + amount",
    description="Buyer NP sends scheme, investment type, amount, and investor context to a BPP.",
)
async def select(
    request: FIS14CommandRequest = Body(..., openapi_examples=SELECT_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_command(request, "select")


@router.post(
    "/init",
    response_model=ONDCAckResponse,
    summary="init - Initialize order",
    description="Buyer NP initializes the order with folio, payment, bank, and consent details.",
)
async def init_order(
    request: FIS14CommandRequest = Body(..., openapi_examples=INIT_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_command(request, "init")


@router.post(
    "/confirm",
    response_model=ONDCAckResponse,
    summary="confirm - Confirm order",
    description="Buyer NP confirms an order after investor review and required authentication.",
)
async def confirm(
    request: FIS14CommandRequest = Body(..., openapi_examples=CONFIRM_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_command(request, "confirm")


@router.post(
    "/status",
    response_model=ONDCAckResponse,
    summary="status - Poll order status",
    description="Buyer NP polls order/payment/fulfillment status by order id.",
)
async def status(
    request: FIS14CommandRequest = Body(..., openapi_examples=STATUS_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_command(request, "status")


@router.post(
    "/update",
    response_model=ONDCAckResponse,
    summary="update - Update order/payment/fulfillment",
    description="Buyer NP sends update intents such as requesting a new payment option or SIP cancellation.",
)
async def update(
    request: FIS14CommandRequest = Body(..., openapi_examples=UPDATE_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_command(request, "update")


@router.post(
    "/cancel",
    response_model=ONDCAckResponse,
    summary="cancel - Cancel an order",
    description="Buyer NP requests order cancellation where the BPP supports the ONDC cancel action.",
)
async def cancel(
    request: FIS14CommandRequest = Body(..., openapi_examples=CANCEL_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_command(request, "cancel")


@router.post(
    "/track",
    response_model=ONDCAckResponse,
    summary="track - Track order progress",
    description="Buyer NP requests tracking details for an order.",
)
async def track(
    request: FIS14CommandRequest = Body(..., openapi_examples=TRACK_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_command(request, "track")


@router.post(
    "/support",
    response_model=ONDCAckResponse,
    summary="support - Request support details",
    description="Buyer NP requests support/contact details for an order or transaction.",
)
async def support(
    request: FIS14CommandRequest = Body(..., openapi_examples=SUPPORT_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_command(request, "support")
