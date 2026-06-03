import asyncio
import base64

import pytest
from nacl.signing import SigningKey

from app.services.signing_service import SIGNED_HEADERS, SigningService
from app.services.verification_service import (
    SignatureVerificationError,
    VerificationService,
    parse_authorization_header,
)


class StubSettings:
    subscriber_id = "buyer.example.com"
    unique_key_id = "test-key-1"
    encryption_public_key = None
    ondc_registry_url = None
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


def make_settings() -> StubSettings:
    signing_key = SigningKey.generate()
    public_key = signing_key.verify_key.encode()
    private_key_material = signing_key.encode() + public_key
    return StubSettings(
        private_key=base64.b64encode(private_key_material).decode("ascii"),
        public_key=base64.b64encode(public_key).decode("ascii"),
    )


def test_authorization_header_generation_uses_ondc_signature_format() -> None:
    settings = make_settings()
    service = SigningService()
    service.settings = settings

    body = b'{"context":{"action":"search"},"message":{"intent":{}}}'
    headers = asyncio.run(service.build_authorization_header(body))

    assert set(headers) == {"Authorization"}
    assert headers["Authorization"].startswith("Signature ")
    parts = parse_authorization_header(headers["Authorization"])
    assert parts.subscriber_id == settings.subscriber_id
    assert parts.unique_key_id == settings.unique_key_id
    assert parts.algorithm == "ed25519"
    assert parts.headers == SIGNED_HEADERS
    assert parts.expires > parts.created
    assert body.decode("utf-8") not in headers["Authorization"]


def test_authorization_signature_verifies_for_original_body() -> None:
    settings = make_settings()
    signer = SigningService()
    signer.settings = settings
    verifier = VerificationService()
    verifier.settings = settings

    body = b'{"context":{"action":"select"},"message":{"order":{"id":"order-1"}}}'
    headers = asyncio.run(signer.build_authorization_header(body))

    asyncio.run(verifier.verify_headers(headers, body))


def test_authorization_signature_rejects_tampered_body() -> None:
    settings = make_settings()
    signer = SigningService()
    signer.settings = settings
    verifier = VerificationService()
    verifier.settings = settings

    body = b'{"context":{"action":"init"},"message":{"order":{"id":"order-1"}}}'
    headers = asyncio.run(signer.build_authorization_header(body))

    with pytest.raises(SignatureVerificationError):
        asyncio.run(verifier.verify_headers(headers, b'{"context":{"action":"init"},"message":{"order":{"id":"order-2"}}}'))
