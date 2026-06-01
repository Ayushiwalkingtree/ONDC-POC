import re
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


ONDC_FIS14_DOMAIN = "ONDC:FIS14"
ONDC_FIS14_VERSION = "2.0.0"

COMMAND_ACTIONS = {
    "search",
    "select",
    "init",
    "confirm",
    "status",
    "update",
    "cancel",
    "track",
    "support",
}
CALLBACK_ACTIONS = {f"on_{action}" for action in COMMAND_ACTIONS}
PROTOCOL_ACTIONS = COMMAND_ACTIONS | CALLBACK_ACTIONS
TTL_PATTERN = re.compile(r"^PT(?=\d)(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")


class ONDCContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain: str
    location: dict[str, Any] | None = None
    timestamp: str
    bap_id: str
    bap_uri: str
    bpp_id: str | None = None
    bpp_uri: str | None = None
    transaction_id: str
    message_id: str
    version: str
    ttl: str
    action: str

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, value: str) -> str:
        if value != ONDC_FIS14_DOMAIN:
            raise ValueError(f"domain must be {ONDC_FIS14_DOMAIN}")
        return value

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        if value != ONDC_FIS14_VERSION:
            raise ValueError(f"version must be {ONDC_FIS14_VERSION}")
        return value

    @field_validator("transaction_id", "message_id", "bap_id", "bap_uri", "action")
    @classmethod
    def validate_required_string(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("value must be a non-empty string")
        return value

    @field_validator("action")
    @classmethod
    def validate_known_action(cls, value: str) -> str:
        if value not in PROTOCOL_ACTIONS:
            raise ValueError(f"unsupported ONDC action: {value}")
        return value

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("timestamp is required")
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("timestamp must be RFC3339/ISO-8601 compatible") from exc
        return value

    @field_validator("ttl")
    @classmethod
    def validate_ttl(cls, value: str) -> str:
        if not value or not TTL_PATTERN.match(value):
            raise ValueError("ttl must be an ISO-8601 duration in PTnH/PTnM/PTnS form")
        return value


class FIS14ProtocolRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    context: ONDCContext
    message: dict[str, Any] = Field(default_factory=dict)


ONDCRequest = FIS14ProtocolRequest


class AckStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ACK", "NACK"] = "ACK"


class AckMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ack: AckStatus


class ONDCAckResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: AckMessage


class ONDCError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = "PROTOCOL-ERROR"
    code: str
    message: str


class TransactionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: str
    message_id: str
    action: str
    direction: Literal["command", "callback"]
    payload: dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


TransactionRecord = TransactionEvent


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def new_message_id() -> str:
    return str(uuid4())
