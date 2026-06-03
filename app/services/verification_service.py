import base64
import re
import time
from dataclasses import dataclass
from typing import Mapping

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from app.core.config import get_settings
from app.services.registry_service import RegistryService, registry_service
from app.services.signing_service import (
    SIGNATURE_ALGORITHM,
    SIGNED_HEADERS,
    build_body_digest,
    build_signing_string,
    decode_ed25519_public_key,
)


@dataclass(frozen=True)
class VerificationConfig:
    require_auth_header: bool
    signing_public_key: str | None
    encryption_public_key: str | None


@dataclass(frozen=True)
class AuthorizationParts:
    key_id: str
    subscriber_id: str
    unique_key_id: str
    algorithm: str
    created: int
    expires: int
    headers: str
    signature: str


class VerificationNotConfiguredError(RuntimeError):
    pass


class SignatureVerificationError(ValueError):
    pass


class VerificationService:
    """Inbound ONDC signature verification boundary."""

    def __init__(self, registry: RegistryService = registry_service) -> None:
        self.settings = get_settings()
        self.registry = registry

    def get_config(self) -> VerificationConfig:
        return VerificationConfig(
            require_auth_header=self.settings.require_ondc_auth,
            signing_public_key=self.settings.get_signing_public_key(),
            encryption_public_key=self.settings.get_encryption_public_key(),
        )

    async def verify_headers(self, headers: Mapping[str, str], body: bytes) -> None:
        config = self.get_config()
        authorization = _get_header(headers, "authorization")
        if not authorization:
            if config.require_auth_header:
                raise VerificationNotConfiguredError("ONDC Authorization header is required but not present")
            return
        parsed = parse_authorization_header(authorization)
        _validate_authorization_metadata(parsed)
        signing_public_key = await self._resolve_signing_public_key(parsed, config.signing_public_key)
        verify_key = VerifyKey(decode_ed25519_public_key(signing_public_key))
        digest = build_body_digest(body)
        signing_string = build_signing_string(parsed.created, parsed.expires, digest)

        try:
            signature = base64.b64decode(parsed.signature, validate=True)
            verify_key.verify(signing_string, signature)
        except (BadSignatureError, ValueError) as exc:
            raise SignatureVerificationError("ONDC Authorization signature verification failed") from exc

    async def _resolve_signing_public_key(self, parsed: AuthorizationParts, fallback_public_key: str | None) -> str:
        if self.settings.ondc_registry_url and not str(self.settings.ondc_registry_url).strip().upper().startswith("TODO"):
            subscriber = await self.registry.lookup_subscriber(parsed.subscriber_id, parsed.unique_key_id)
            if subscriber.signing_public_key:
                return subscriber.signing_public_key
        if not fallback_public_key:
            raise VerificationNotConfiguredError(
                "SIGNING_PUBLIC_KEY or SIGNING_PUBLIC_KEY_PATH is required when registry lookup is not configured"
            )
        return fallback_public_key


def parse_authorization_header(value: str) -> AuthorizationParts:
    normalized = value.strip()
    if not normalized.startswith("Signature "):
        raise SignatureVerificationError("Authorization header must start with 'Signature '")

    fields = dict(re.findall(r'([A-Za-z]+)="([^"]*)"', normalized[len("Signature ") :]))
    required = {"keyId", "algorithm", "created", "expires", "headers", "signature"}
    missing = required - fields.keys()
    if missing:
        raise SignatureVerificationError("Authorization header is missing fields: " + ", ".join(sorted(missing)))

    key_parts = fields["keyId"].split("|")
    if len(key_parts) != 3:
        raise SignatureVerificationError("Authorization keyId must be subscriber_id|unique_key_id|algorithm")

    try:
        created = int(fields["created"])
        expires = int(fields["expires"])
    except ValueError as exc:
        raise SignatureVerificationError("Authorization created/expires values must be Unix timestamps") from exc

    return AuthorizationParts(
        key_id=fields["keyId"],
        subscriber_id=key_parts[0],
        unique_key_id=key_parts[1],
        algorithm=fields["algorithm"],
        created=created,
        expires=expires,
        headers=fields["headers"],
        signature=fields["signature"],
    )


def _validate_authorization_metadata(parsed: AuthorizationParts) -> None:
    if parsed.algorithm.lower() != SIGNATURE_ALGORITHM:
        raise SignatureVerificationError("Authorization algorithm must be ed25519")
    if parsed.key_id.split("|")[2].lower() != SIGNATURE_ALGORITHM:
        raise SignatureVerificationError("Authorization keyId algorithm must be ed25519")
    if parsed.headers != SIGNED_HEADERS:
        raise SignatureVerificationError("Authorization signed headers must be '(created) (expires) digest'")
    now = int(time.time())
    if parsed.created > now + 300:
        raise SignatureVerificationError("Authorization created timestamp is in the future")
    if parsed.expires < now:
        raise SignatureVerificationError("Authorization signature has expired")
    if parsed.expires <= parsed.created:
        raise SignatureVerificationError("Authorization expires timestamp must be greater than created")


def _get_header(headers: Mapping[str, str], name: str) -> str | None:
    lowered = name.lower()
    for key, value in headers.items():
        if key.lower() == lowered:
            return value
    return None


verification_service = VerificationService()
