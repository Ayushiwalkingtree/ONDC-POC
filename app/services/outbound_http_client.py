import json
import logging
from dataclasses import dataclass
from typing import Any, Mapping

import httpx


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OutboundHTTPResponse:
    status_code: int
    headers: dict[str, str]
    body: Any


class OutboundHTTPClient:
    def __init__(self, timeout_seconds: float = 30.0) -> None:
        self.timeout_seconds = timeout_seconds

    async def post(self, url: str, body: bytes, headers: Mapping[str, str]) -> OutboundHTTPResponse:
        logger.info(
            "Sending outbound ONDC request | url=%s bytes=%s headers=%s",
            url,
            len(body),
            _redact_headers(headers),
        )
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(url, content=body, headers=dict(headers))

        response_headers = dict(response.headers)
        try:
            response_body: Any = response.json()
        except json.JSONDecodeError:
            response_body = response.text

        logger.info(
            "Outbound ONDC response received | url=%s status=%s headers=%s body=%s",
            url,
            response.status_code,
            response_headers,
            response_body,
        )
        return OutboundHTTPResponse(
            status_code=response.status_code,
            headers=response_headers,
            body=response_body,
        )


outbound_http_client = OutboundHTTPClient()


def _redact_headers(headers: Mapping[str, str]) -> dict[str, str]:
    redacted = dict(headers)
    for key in list(redacted):
        if key.lower() == "authorization":
            redacted[key] = "<redacted>"
    return redacted
