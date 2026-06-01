from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ondc import FIS14ProtocolRequest, ONDCContext


FIS14CommandAction = Literal[
    "search",
    "select",
    "init",
    "confirm",
    "status",
    "update",
    "cancel",
    "track",
    "support",
]

FIS14CallbackAction = Literal[
    "on_search",
    "on_select",
    "on_init",
    "on_confirm",
    "on_status",
    "on_update",
    "on_cancel",
    "on_track",
    "on_support",
]


class FIS14CommandRequest(FIS14ProtocolRequest):
    """Strict ONDC/FIS14 envelope for Buyer NP outbound command intents."""


class FIS14CallbackRequest(FIS14ProtocolRequest):
    """Strict ONDC/FIS14 envelope for BPP callbacks received by the Buyer NP."""


class FIS14ProtocolEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    context: ONDCContext
    message: dict[str, Any] = Field(default_factory=dict)
