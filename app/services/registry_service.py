from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings


@dataclass(frozen=True)
class RegistrySubscriber:
    subscriber_id: str
    unique_key_id: str | None
    signing_public_key: str | None
    subscriber_url: str | None
    raw: Any


class RegistryNotConfiguredError(RuntimeError):
    pass


class RegistryService:
    """ONDC registry lookup boundary.

    This service intentionally performs no mock lookup. Configure a registry URL and
    wire environment-specific request/response mapping before enabling UAT traffic.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    async def lookup_subscriber(self, subscriber_id: str, unique_key_id: str | None = None) -> RegistrySubscriber:
        if not self.settings.ondc_registry_url or str(self.settings.ondc_registry_url).strip().upper().startswith("TODO"):
            raise RegistryNotConfiguredError("ONDC_REGISTRY_URL is not configured")

        payload: dict[str, Any] = {"subscriber_id": subscriber_id}
        if unique_key_id:
            payload["unique_key_id"] = unique_key_id

        async with httpx.AsyncClient(timeout=self.settings.ondc_registry_timeout_seconds) as client:
            response = await client.post(str(self.settings.ondc_registry_url), json=payload)
            response.raise_for_status()
            data = response.json()

        subscriber_data = _select_subscriber_data(data, subscriber_id, unique_key_id)
        return RegistrySubscriber(
            subscriber_id=subscriber_id,
            unique_key_id=_first_value(subscriber_data, "unique_key_id", "ukId", "uniqueKeyId") or unique_key_id,
            signing_public_key=_first_value(subscriber_data, "signing_public_key", "signingPublicKey", "signing_public_key"),
            subscriber_url=_first_value(
                subscriber_data,
                "subscriber_url",
                "subscriberUrl",
                "subscriber_uri",
                "subscriberUri",
                "bpp_uri",
                "bppUri",
                "url",
            ),
            raw=data,
        )


registry_service = RegistryService()


def _select_subscriber_data(data: Any, subscriber_id: str, unique_key_id: str | None) -> dict[str, Any]:
    candidates = _collect_mappings(data)
    if not candidates:
        return data if isinstance(data, dict) else {}

    for candidate in candidates:
        candidate_subscriber_id = _first_value(candidate, "subscriber_id", "subscriberId")
        candidate_unique_key_id = _first_value(candidate, "unique_key_id", "ukId", "uniqueKeyId")
        if candidate_subscriber_id == subscriber_id and (not unique_key_id or candidate_unique_key_id == unique_key_id):
            return candidate

    return candidates[0]


def _collect_mappings(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        nested: list[dict[str, Any]] = [value]
        for nested_value in value.values():
            nested.extend(_collect_mappings(nested_value))
        return nested
    if isinstance(value, list):
        nested = []
        for item in value:
            nested.extend(_collect_mappings(item))
        return nested
    return []


def _first_value(data: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None
