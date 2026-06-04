import logging

from fastapi import APIRouter, Body, HTTPException, Request

from app.schemas.examples import (
    ON_CANCEL_EXAMPLES,
    ON_CONFIRM_EXAMPLES,
    ON_INIT_EXAMPLES,
    ON_SEARCH_EXAMPLES,
    ON_SELECT_EXAMPLES,
    ON_STATUS_EXAMPLES,
    ON_SUPPORT_EXAMPLES,
    ON_TRACK_EXAMPLES,
    ON_UPDATE_EXAMPLES,
)
from app.schemas.fis14 import FIS14CallbackRequest
from app.schemas.ondc import ONDCAckResponse
from app.services.buyer_np_service import buyer_np_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ondc", tags=["2. Buyer NP Callback Receivers"])
workbench_alias_router = APIRouter(tags=["2. Buyer NP Callback Receivers"])


@workbench_alias_router.post(
    "/on_search",
    summary="on_search - Receive scheme catalog",
    description="Workbench-compatible alias for the Buyer NP callback URI.",
    response_model=ONDCAckResponse,
)
@router.post(
    "/on_search",
    summary="on_search - Receive scheme catalog",
    description="Receives the BPP catalog callback at the Buyer NP callback URI.",
    response_model=ONDCAckResponse,
)
async def on_search(
    http_request: Request,
    request: FIS14CallbackRequest = Body(..., openapi_examples=ON_SEARCH_EXAMPLES),
) -> ONDCAckResponse:
    logger.info("Received on_search callback | txn=%s", request.context.transaction_id)
    return await buyer_np_service.handle_callback(request, "on_search", http_request.headers, await http_request.body())


@workbench_alias_router.post(
    "/on_select",
    summary="on_select - Receive quote + folios",
    description="Workbench-compatible alias for the Buyer NP callback URI.",
    response_model=ONDCAckResponse,
)
@router.post(
    "/on_select",
    summary="on_select - Receive quote + folios",
    description="Receives quote, folio list, and payment options from a BPP.",
    response_model=ONDCAckResponse,
)
async def on_select(
    http_request: Request,
    request: FIS14CallbackRequest = Body(..., openapi_examples=ON_SELECT_EXAMPLES),
) -> ONDCAckResponse:
    logger.info("Received on_select callback | txn=%s", request.context.transaction_id)
    return await buyer_np_service.handle_callback(request, "on_select", http_request.headers, await http_request.body())


@workbench_alias_router.post(
    "/on_init",
    summary="on_init - Receive draft order + payment details",
    description="Workbench-compatible alias for the Buyer NP callback URI.",
    response_model=ONDCAckResponse,
)
@router.post(
    "/on_init",
    summary="on_init - Receive draft order + payment details",
    description="Receives draft order, terms, and payment details from a BPP.",
    response_model=ONDCAckResponse,
)
async def on_init(
    http_request: Request,
    request: FIS14CallbackRequest = Body(..., openapi_examples=ON_INIT_EXAMPLES),
) -> ONDCAckResponse:
    logger.info("Received on_init callback | txn=%s", request.context.transaction_id)
    return await buyer_np_service.handle_callback(request, "on_init", http_request.headers, await http_request.body())


@workbench_alias_router.post(
    "/on_confirm",
    summary="on_confirm - Receive accepted/rejected order",
    description="Workbench-compatible alias for the Buyer NP callback URI.",
    response_model=ONDCAckResponse,
)
@router.post(
    "/on_confirm",
    summary="on_confirm - Receive accepted/rejected order",
    description="Receives order acceptance or rejection from a BPP.",
    response_model=ONDCAckResponse,
)
async def on_confirm(
    http_request: Request,
    request: FIS14CallbackRequest = Body(..., openapi_examples=ON_CONFIRM_EXAMPLES),
) -> ONDCAckResponse:
    logger.info("Received on_confirm callback | txn=%s", request.context.transaction_id)
    return await buyer_np_service.handle_callback(request, "on_confirm", http_request.headers, await http_request.body())


@router.post(
    "/on_status",
    summary="on_status - Receive order status",
    description="Receives order/payment/fulfillment status from a BPP.",
    response_model=ONDCAckResponse,
)
async def on_status(
    http_request: Request,
    request: FIS14CallbackRequest = Body(..., openapi_examples=ON_STATUS_EXAMPLES),
) -> ONDCAckResponse:
    logger.info("Received on_status callback | txn=%s", request.context.transaction_id)
    return await buyer_np_service.handle_callback(request, "on_status", http_request.headers, await http_request.body())


@router.post(
    "/on_update",
    summary="on_update - Receive BPP update callback",
    description="Receives payment, fulfillment, SIP, redemption, or folio updates.",
    response_model=ONDCAckResponse,
)
async def on_update(
    http_request: Request,
    request: FIS14CallbackRequest = Body(..., openapi_examples=ON_UPDATE_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_callback(request, "on_update", http_request.headers, await http_request.body())


@router.post(
    "/on_cancel",
    summary="on_cancel - Receive BPP cancellation callback",
    description="Receives cancellation result from a BPP.",
    response_model=ONDCAckResponse,
)
async def on_cancel(
    http_request: Request,
    request: FIS14CallbackRequest = Body(..., openapi_examples=ON_CANCEL_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_callback(request, "on_cancel", http_request.headers, await http_request.body())


@router.post(
    "/on_track",
    summary="on_track - Receive BPP tracking callback",
    description="Receives tracking information from a BPP.",
    response_model=ONDCAckResponse,
)
async def on_track(
    http_request: Request,
    request: FIS14CallbackRequest = Body(..., openapi_examples=ON_TRACK_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_callback(request, "on_track", http_request.headers, await http_request.body())


@router.post(
    "/on_support",
    summary="on_support - Receive BPP support callback",
    description="Receives support/contact information from a BPP.",
    response_model=ONDCAckResponse,
)
async def on_support(
    http_request: Request,
    request: FIS14CallbackRequest = Body(..., openapi_examples=ON_SUPPORT_EXAMPLES),
) -> ONDCAckResponse:
    return await buyer_np_service.handle_callback(request, "on_support", http_request.headers, await http_request.body())


@router.get(
    "/transactions",
    tags=["3. Debug - Transaction Repository"],
    summary="List all stored protocol events",
    description="Repository view of Buyer NP command and callback protocol events.",
)
async def list_transactions() -> dict:
    records = buyer_np_service.list_transactions()
    return {"count": len(records), "records": records}


@router.get(
    "/transactions/{transaction_id}",
    tags=["3. Debug - Transaction Repository"],
    summary="Get events by transaction_id",
)
async def get_transactions(transaction_id: str) -> dict:
    records = buyer_np_service.get_transaction(transaction_id)
    if not records:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"transaction_id": transaction_id, "records": records}
