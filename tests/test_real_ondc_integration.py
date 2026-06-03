import asyncio
import base64
from typing import Mapping

from nacl.signing import SigningKey

from app.schemas.ondc import FIS14ProtocolRequest
from app.services.buyer_np_service import BuyerNPService
from app.services.file_storage_service import FileStorageService
from app.services.outbound_http_client import OutboundHTTPResponse
from app.services.registry_service import RegistrySubscriber
from app.services.signing_service import SigningService
from app.services.verification_service import VerificationService


class IntegrationSettings:
    subscriber_id = "buyer.example.com"
    unique_key_id = "buyer-key-1"
    bpp_id = "bpp.example.com"
    ondc_registry_url = "https://registry.example.com/lookup"
    require_ondc_auth = True

    def __init__(self, private_key: str, public_key: str) -> None:
        self._private_key = private_key
        self._public_key = public_key

    def get_signing_private_key(self) -> str:
        return self._private_key

    def get_signing_public_key(self) -> str:
        return self._public_key

    def get_encryption_public_key(self) -> None:
        return None


class MockRegistryService:
    def __init__(self, signing_public_key: str) -> None:
        self.signing_public_key = signing_public_key
        self.lookups: list[tuple[str, str | None]] = []

    async def lookup_subscriber(self, subscriber_id: str, unique_key_id: str | None = None) -> RegistrySubscriber:
        self.lookups.append((subscriber_id, unique_key_id))
        return RegistrySubscriber(
            subscriber_id=subscriber_id,
            unique_key_id=unique_key_id,
            signing_public_key=self.signing_public_key,
            subscriber_url="https://bpp.example.com/ondc",
            raw={"subscriber_url": "https://bpp.example.com/ondc"},
        )


class MockOutboundClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def post(self, url: str, body: bytes, headers: Mapping[str, str]) -> OutboundHTTPResponse:
        self.calls.append({"url": url, "body": body, "headers": dict(headers)})
        return OutboundHTTPResponse(
            status_code=200,
            headers={"content-type": "application/json"},
            body={"message": {"ack": {"status": "ACK"}}},
        )


def make_settings() -> IntegrationSettings:
    signing_key = SigningKey.generate()
    public_key = signing_key.verify_key.encode()
    private_key_material = signing_key.encode() + public_key
    return IntegrationSettings(
        private_key=base64.b64encode(private_key_material).decode("ascii"),
        public_key=base64.b64encode(public_key).decode("ascii"),
    )


def make_payload(action: str, message_id: str) -> FIS14ProtocolRequest:
    return FIS14ProtocolRequest.model_validate(
        {
            "context": {
                "domain": "ONDC:FIS14",
                "location": {"country": {"code": "IND"}, "city": {"code": "*"}},
                "timestamp": "2026-06-03T10:00:00.000Z",
                "bap_id": "buyer.example.com",
                "bap_uri": "https://buyer.example.com/ondc",
                "bpp_id": "bpp.example.com",
                "bpp_uri": "https://bpp.example.com/ondc",
                "transaction_id": "txn-integration-1",
                "message_id": message_id,
                "version": "2.0.0",
                "ttl": "PT10M",
                "action": action,
            },
            "message": {"intent": {}},
        }
    )


def test_search_signed_outbound_request_and_verified_callback(tmp_path) -> None:
    settings = make_settings()
    signer = SigningService()
    signer.settings = settings
    verifier = VerificationService()
    verifier.settings = settings
    registry = MockRegistryService(settings.get_signing_public_key())
    verifier.registry = registry
    outbound_client = MockOutboundClient()

    service = BuyerNPService(
        repository=FileStorageService(tmp_path),
        signer=signer,
        verifier=verifier,
        registry=registry,
        outbound_client=outbound_client,
    )
    service.settings = settings

    search_request = make_payload("search", "msg-search-1")
    ack = asyncio.run(service.handle_command(search_request, "search"))

    assert ack.message.ack.status == "ACK"
    assert registry.lookups[0] == ("bpp.example.com", None)
    assert outbound_client.calls[0]["url"] == "https://bpp.example.com/ondc/search"
    assert "Authorization" in outbound_client.calls[0]["headers"]
    asyncio.run(verifier.verify_headers(outbound_client.calls[0]["headers"], outbound_client.calls[0]["body"]))

    callback_request = make_payload("on_search", "msg-on-search-1")
    callback_body = callback_request.model_dump_json().encode("utf-8")
    callback_headers = dict(asyncio.run(signer.build_authorization_header(callback_body)))
    callback_ack = asyncio.run(
        service.handle_callback(callback_request, "on_search", callback_headers, callback_body)
    )

    assert callback_ack.message.ack.status == "ACK"
    stored = service.list_transactions()
    assert {event["direction"] for event in stored} == {"command", "response", "callback"}
