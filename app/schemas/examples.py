"""Load ONDC FIS14 examples from local specs for Swagger and Postman."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = ROOT / "fis-specs" / "api" / "components" / "examples" / "mutual-funds"


def _load(relative_path: str) -> dict[str, Any]:
    path = EXAMPLES_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Example not found: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _copy(payload: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(payload))


def _unique_message_id(payload: dict[str, Any], suffix: str) -> dict[str, Any]:
    copy = _copy(payload)
    context = copy.setdefault("context", {})
    if context.get("message_id"):
        context["message_id"] = f"{context['message_id']}-{suffix}"
    return copy


def _patch_action(payload: dict[str, Any], action: str) -> dict[str, Any]:
    copy = _unique_message_id(payload, action)
    copy.setdefault("context", {})["action"] = action
    return copy


SEARCH = _unique_message_id(_load("search/search.json"), "search")
SELECT_LUMPSUM = _unique_message_id(_load("select/select-lumpsum.json"), "select-lumpsum")
SELECT_SIP = _unique_message_id(_load("select/select-sip.json"), "select-sip")
SELECT_REDEMPTION = _unique_message_id(_load("select/select-redemption.json"), "select-redemption")
INIT_LUMPSUM = _unique_message_id(_load("init/init-lumpsum.json"), "init-lumpsum")
CONFIRM_LUMPSUM = _unique_message_id(_load("confirm/confirm-lumpsum.json"), "confirm-lumpsum")
STATUS_REQUEST = _unique_message_id(_load("status/status-request.json"), "status")
UPDATE_PAYMENT = _unique_message_id(_load("update/update-lumpsum-new-payment.json"), "update-payment")
UPDATE_CANCEL_SIP = _unique_message_id(_load("update/update-cancel-sip.json"), "update-cancel-sip")
ON_UPDATE_PAYMENT = _unique_message_id(_load("on_update/on_update-lumpsum-new-payment.json"), "on-update-payment")

ON_SEARCH = _patch_action(SEARCH, "on_search")
ON_SELECT_LUMPSUM = _patch_action(SELECT_LUMPSUM, "on_select")
ON_SELECT_SIP = _patch_action(SELECT_SIP, "on_select")
ON_SELECT_REDEMPTION = _patch_action(SELECT_REDEMPTION, "on_select")
ON_INIT_LUMPSUM = _patch_action(INIT_LUMPSUM, "on_init")
ON_CONFIRM_LUMPSUM = _patch_action(CONFIRM_LUMPSUM, "on_confirm")
ON_STATUS = _patch_action(STATUS_REQUEST, "on_status")
ON_UPDATE = _patch_action(ON_UPDATE_PAYMENT, "on_update")

TRACK_REQUEST = _patch_action(STATUS_REQUEST, "track")
TRACK_REQUEST["message"] = {"order_id": STATUS_REQUEST.get("message", {}).get("order_id", "order-mf-001")}
ON_TRACK = _patch_action(TRACK_REQUEST, "on_track")
ON_TRACK["message"] = {
    "tracking": {
        "id": "tracking-mf-001",
        "url": "https://seller-app.example.com/tracking/order-mf-001",
        "status": "active",
    }
}

CANCEL_REQUEST = _patch_action(STATUS_REQUEST, "cancel")
CANCEL_REQUEST["message"] = {"order_id": "order-mf-001", "cancellation_reason_id": "buyer_requested"}
ON_CANCEL = _patch_action(CANCEL_REQUEST, "on_cancel")
ON_CANCEL["message"] = {"order": {"id": "order-mf-001", "state": "CANCELLED"}}

SUPPORT_REQUEST = _patch_action(STATUS_REQUEST, "support")
SUPPORT_REQUEST["message"] = {"ref_id": "order-mf-001"}
ON_SUPPORT = _patch_action(SUPPORT_REQUEST, "on_support")
ON_SUPPORT["message"] = {
    "support": {
        "ref_id": "order-mf-001",
        "phone": "+91-9999999999",
        "email": "support@seller-app.example.com",
    }
}


def openapi_examples(*items: tuple[str, str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        key: {"summary": summary, "description": summary, "value": value}
        for key, summary, value in items
    }


SEARCH_EXAMPLES = openapi_examples(
    ("search_mutual_funds", "Search all MF schemes (ONDC:FIS14)", SEARCH),
)

SELECT_EXAMPLES = openapi_examples(
    ("select_lumpsum", "Lumpsum existing folio, INR 3000", SELECT_LUMPSUM),
    ("select_sip", "SIP systematic investment", SELECT_SIP),
    ("select_redemption", "Redemption by amount", SELECT_REDEMPTION),
)

INIT_EXAMPLES = openapi_examples(
    ("init_lumpsum", "Init lumpsum with folio and netbanking payment", INIT_LUMPSUM),
)

CONFIRM_EXAMPLES = openapi_examples(
    ("confirm_lumpsum", "Confirm lumpsum order", CONFIRM_LUMPSUM),
)

STATUS_EXAMPLES = openapi_examples(
    ("status_order", "Poll order status by order_id", STATUS_REQUEST),
)

UPDATE_EXAMPLES = openapi_examples(
    ("update_payment", "Request a new payment instrument or link", UPDATE_PAYMENT),
    ("update_cancel_sip", "Request SIP cancellation through update", UPDATE_CANCEL_SIP),
)

CANCEL_EXAMPLES = openapi_examples(
    ("cancel_order", "Cancel an order", CANCEL_REQUEST),
)

TRACK_EXAMPLES = openapi_examples(
    ("track_order", "Track order progress", TRACK_REQUEST),
)

SUPPORT_EXAMPLES = openapi_examples(
    ("support_order", "Request support details", SUPPORT_REQUEST),
)

ON_SEARCH_EXAMPLES = openapi_examples(
    ("on_search_catalog", "Catalog callback", ON_SEARCH),
)

ON_SELECT_EXAMPLES = openapi_examples(
    ("on_select_lumpsum", "Quote and folios callback", ON_SELECT_LUMPSUM),
    ("on_select_sip", "SIP quote callback", ON_SELECT_SIP),
    ("on_select_redemption", "Redemption payout accounts callback", ON_SELECT_REDEMPTION),
)

ON_INIT_EXAMPLES = openapi_examples(
    ("on_init_lumpsum", "Draft order and payment URL callback", ON_INIT_LUMPSUM),
)

ON_CONFIRM_EXAMPLES = openapi_examples(
    ("on_confirm_lumpsum", "Order accepted callback", ON_CONFIRM_LUMPSUM),
)

ON_STATUS_EXAMPLES = openapi_examples(
    ("on_status_payment", "Payment status callback", ON_STATUS),
)

ON_UPDATE_EXAMPLES = openapi_examples(
    ("on_update_payment", "Payment or fulfillment update callback", ON_UPDATE),
)

ON_CANCEL_EXAMPLES = openapi_examples(
    ("on_cancel_order", "Cancellation result callback", ON_CANCEL),
)

ON_TRACK_EXAMPLES = openapi_examples(
    ("on_track_order", "Tracking callback", ON_TRACK),
)

ON_SUPPORT_EXAMPLES = openapi_examples(
    ("on_support_order", "Support callback", ON_SUPPORT),
)
