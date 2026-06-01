from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import get_settings


@dataclass(frozen=True)
class RegistrySubscriber:
    subscriber_id: str
    unique_key_id: str | None
    signing_public_key: str | None
    raw: dict[str, Any]


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
        if not self.settings.ondc_registry_url:
            raise RegistryNotConfiguredError("ONDC_REGISTRY_URL is not configured")

        payload: dict[str, Any] = {"subscriber_id": subscriber_id}
        if unique_key_id:
            payload["unique_key_id"] = unique_key_id

        async with httpx.AsyncClient(timeout=self.settings.ondc_registry_timeout_seconds) as client:
            response = await client.post(str(self.settings.ondc_registry_url), json=payload)
            response.raise_for_status()
            data = response.json()

        return RegistrySubscriber(
            subscriber_id=subscriber_id,
            unique_key_id=unique_key_id,
            signing_public_key=data.get("signing_public_key"),
            raw=data,
        )


registry_service = RegistryService()
