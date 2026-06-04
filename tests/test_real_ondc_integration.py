import asyncio
import base64
import json
import uuid
from typing import Mapping

import pytest
from nacl.signing import SigningKey
from fastapi import HTTPException

from app.schemas.ondc import FIS14ProtocolRequest
from app.services.buyer_np_service import BuyerNPService
from app.services.file_storage_service import FileStorageService
from app.services.ondc_service import ONDCService
from app.services.outbound_http_client import OutboundHTTPResponse
from app.services.registry_service import RegistrySubscriber
from app.services.signing_service import SigningService
from app.services.verification_service import VerificationService


class IntegrationSettings:
    subscriber_id = "buyer.example.com"
    unique_key_id = "buyer-key-1"
    bap_id = "buyer.example.com"
    bap_uri = "https://buyer.example.com/ondc"
    bap_callback_uri = "https://buyer.example.com/ondc"
    bpp_id = "bpp.example.com"
    bpp_uri = "https://bpp.example.com/ondc"
    ondc_registry_url = "https://registry.example.com/lookup"
    require_ondc_auth = True
    workbench_mode = False
    workbench_base_url = "https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller"

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


def make_payload(
    action: str,
    message_id: str | None = None,
    transaction_id: str | None = None,
    include_message_id: bool = True,
) -> FIS14ProtocolRequest:
    context = {
        "domain": "ONDC:FIS14",
        "location": {"country": {"code": "IND"}, "city": {"code": "*"}},
        "timestamp": "2026-06-03T10:00:00.000Z",
        "bap_id": "buyer.example.com",
        "bap_uri": "https://buyer.example.com/ondc",
        "bpp_id": "bpp.example.com",
        "bpp_uri": "https://bpp.example.com/ondc",
        "transaction_id": transaction_id or str(uuid.uuid4()),
        "version": "2.0.0",
        "ttl": "PT10M",
        "action": action,
    }
    if include_message_id:
        context["message_id"] = message_id or str(uuid.uuid4())

    return FIS14ProtocolRequest.model_validate(
        {
            "context": context,
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

    search_request = make_payload("search")
    ack = asyncio.run(service.handle_command(search_request, "search"))

    assert ack.message.ack.status == "ACK"
    assert registry.lookups[0] == ("bpp.example.com", None)
    assert outbound_client.calls[0]["url"] == "https://bpp.example.com/ondc/search"
    assert "Authorization" in outbound_client.calls[0]["headers"]
    outbound_body = json.loads(outbound_client.calls[0]["body"])
    assert outbound_body["context"]["bap_id"] == settings.bap_id
    assert outbound_body["context"]["bap_uri"] == settings.bap_uri
    asyncio.run(verifier.verify_headers(outbound_client.calls[0]["headers"], outbound_client.calls[0]["body"]))

    callback_request = make_payload("on_search")
    callback_body = callback_request.model_dump_json().encode("utf-8")
    callback_headers = dict(asyncio.run(signer.build_authorization_header(callback_body)))
    callback_ack = asyncio.run(
        service.handle_callback(callback_request, "on_search", callback_headers, callback_body)
    )

    assert callback_ack.message.ack.status == "ACK"
    stored = service.list_transactions()
    assert {event["direction"] for event in stored} == {"command", "response", "callback"}


def test_workbench_mode_skips_registry_lookup_and_dispatches_all_commands(tmp_path) -> None:
    settings = make_settings()
    settings.workbench_mode = True
    settings.workbench_base_url = "https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller"
    signer = SigningService()
    signer.settings = settings
    registry = MockRegistryService(settings.get_signing_public_key())
    outbound_client = MockOutboundClient()

    service = BuyerNPService(
        repository=FileStorageService(tmp_path),
        signer=signer,
        registry=registry,
        outbound_client=outbound_client,
    )
    service.settings = settings

    actions = ("search", "select", "init", "confirm", "status", "update", "cancel", "track", "support")
    for action in actions:
        request = make_payload(action)
        ack = asyncio.run(service.handle_command(request, action))
        assert ack.message.ack.status == "ACK"

    assert registry.lookups == []
    assert [call["url"] for call in outbound_client.calls] == [
        f"https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/{action}"
        for action in actions
    ]
    assert all("Authorization" in call["headers"] for call in outbound_client.calls)
    for call in outbound_client.calls:
        outbound_body = json.loads(call["body"])
        assert outbound_body["context"]["bap_id"] == settings.bap_id
        assert outbound_body["context"]["bap_uri"] == settings.bap_uri
        assert outbound_body["context"]["bpp_id"] == "workbench.ondc.tech"
        assert outbound_body["context"]["bpp_uri"] == settings.workbench_base_url


def test_workbench_callback_alias_routes_are_registered() -> None:
    from app.main import app

    paths = {route.path for route in app.routes}
    for action in ("on_search", "on_select", "on_init", "on_confirm"):
        assert f"/{action}" in paths
        assert f"/ondc/{action}" in paths


def test_missing_command_message_id_is_generated_before_dispatch(tmp_path) -> None:
    settings = make_settings()
    signer = SigningService()
    signer.settings = settings
    registry = MockRegistryService(settings.get_signing_public_key())
    outbound_client = MockOutboundClient()

    service = BuyerNPService(
        repository=FileStorageService(tmp_path),
        signer=signer,
        registry=registry,
        outbound_client=outbound_client,
    )
    service.settings = settings

    request = make_payload("search", include_message_id=False)
    ack = asyncio.run(service.handle_command(request, "search"))

    assert ack.message.ack.status == "ACK"
    outbound_body = json.loads(outbound_client.calls[0]["body"])
    generated_message_id = outbound_body["context"]["message_id"]
    uuid.UUID(generated_message_id)
    stored = service.list_transactions()
    assert any(event["message_id"] == generated_message_id for event in stored)


def test_duplicate_explicit_command_message_id_still_returns_conflict(tmp_path) -> None:
    settings = make_settings()
    signer = SigningService()
    signer.settings = settings
    registry = MockRegistryService(settings.get_signing_public_key())
    outbound_client = MockOutboundClient()

    service = BuyerNPService(
        repository=FileStorageService(tmp_path),
        signer=signer,
        registry=registry,
        outbound_client=outbound_client,
    )
    service.settings = settings

    request = make_payload("search")
    asyncio.run(service.handle_command(request, "search"))

    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.handle_command(request, "search"))

    assert exc.value.status_code == 409
    assert "duplicate message_id" in exc.value.detail


def test_command_uuid_values_pass_and_outbound_payload_contains_pure_uuids(tmp_path) -> None:
    settings = make_settings()
    signer = SigningService()
    signer.settings = settings
    registry = MockRegistryService(settings.get_signing_public_key())
    outbound_client = MockOutboundClient()

    service = BuyerNPService(
        repository=FileStorageService(tmp_path),
        signer=signer,
        registry=registry,
        outbound_client=outbound_client,
    )
    service.settings = settings

    transaction_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    request = make_payload("search", message_id=message_id, transaction_id=transaction_id)
    ack = asyncio.run(service.handle_command(request, "search"))

    assert ack.message.ack.status == "ACK"
    outbound_body = json.loads(outbound_client.calls[0]["body"])
    assert outbound_body["context"]["transaction_id"] == transaction_id
    assert outbound_body["context"]["message_id"] == message_id
    assert str(uuid.UUID(outbound_body["context"]["transaction_id"])) == transaction_id
    assert str(uuid.UUID(outbound_body["context"]["message_id"])) == message_id


@pytest.mark.parametrize(
    ("field_name", "suffix"),
    (
        ("transaction_id", "-search"),
        ("message_id", "-select"),
    ),
)
def test_command_uuid_plus_suffix_fails_before_outbound_dispatch(tmp_path, field_name: str, suffix: str) -> None:
    settings = make_settings()
    signer = SigningService()
    signer.settings = settings
    registry = MockRegistryService(settings.get_signing_public_key())
    outbound_client = MockOutboundClient()

    service = BuyerNPService(
        repository=FileStorageService(tmp_path),
        signer=signer,
        registry=registry,
        outbound_client=outbound_client,
    )
    service.settings = settings

    transaction_id = str(uuid.uuid4())
    message_id = str(uuid.uuid4())
    if field_name == "transaction_id":
        transaction_id = f"{transaction_id}{suffix}"
    else:
        message_id = f"{message_id}{suffix}"

    request = make_payload("search", message_id=message_id, transaction_id=transaction_id)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.handle_command(request, "search"))

    assert exc.value.status_code == 400
    assert exc.value.detail == f"context.{field_name} must be a valid RFC4122 UUID string"
    assert outbound_client.calls == []


def test_mock_on_search_callback_reuses_search_transaction_and_message_id() -> None:
    settings = make_settings()
    settings.workbench_mode = True
    settings.bap_id = "ondcapi.walkingtree.tech"
    settings.bap_uri = "https://ondcapi.walkingtree.tech/ondc"
    settings.bap_callback_uri = "https://ondcapi.walkingtree.tech/ondc"
    signer = SigningService()
    signer.settings = settings
    outbound_client = MockOutboundClient()
    service = ONDCService(signer=signer, outbound_client=outbound_client)
    service.settings = settings

    search_request = make_payload("search")
    callback = service.build_mock_callback(search_request, "on_search")
    context = callback["context"]

    assert context["domain"] == "ONDC:FIS14"
    assert context["action"] == "on_search"
    assert context["bap_id"] == "ondcapi.walkingtree.tech"
    assert context["bap_uri"] == "https://ondcapi.walkingtree.tech/ondc"
    assert context["bpp_id"] == "workbench.ondc.tech"
    assert context["bpp_uri"] == settings.workbench_base_url
    assert context["transaction_id"] == search_request.context.transaction_id
    assert context["message_id"] == search_request.context.message_id
    assert context["timestamp"]
    assert context["version"] == "2.0.0"
    assert context["ttl"] == "PT10M"


def test_mock_on_search_callback_posts_to_configured_bap_callback_url() -> None:
    settings = make_settings()
    settings.bap_callback_uri = "https://ondcapi.walkingtree.tech/ondc"
    signer = SigningService()
    signer.settings = settings
    outbound_client = MockOutboundClient()
    service = ONDCService(signer=signer, outbound_client=outbound_client)
    service.settings = settings

    search_request = make_payload("search")
    response = asyncio.run(service.post_mock_callback(search_request, "on_search"))

    assert response.status_code == 200
    assert outbound_client.calls[0]["url"] == "https://ondcapi.walkingtree.tech/ondc/on_search"
    posted_body = json.loads(outbound_client.calls[0]["body"])
    assert posted_body["context"]["action"] == "on_search"
    assert posted_body["context"]["transaction_id"] == search_request.context.transaction_id
    assert posted_body["context"]["message_id"] == search_request.context.message_id
    assert "Authorization" in outbound_client.calls[0]["headers"]
