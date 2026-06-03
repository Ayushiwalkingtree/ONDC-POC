import base64
import hashlib
import time
from dataclasses import dataclass
from typing import Mapping

from nacl.signing import SigningKey

from app.core.config import get_settings


SIGNATURE_ALGORITHM = "ed25519"
DIGEST_ALGORITHM = "BLAKE-512"
SIGNED_HEADERS = "(created) (expires) digest"
DEFAULT_SIGNATURE_TTL_SECONDS = 300


@dataclass(frozen=True)
class SigningConfig:
    subscriber_id: str
    unique_key_id: str
    private_key: str
    public_key: str


@dataclass(frozen=True)
class SigningKeyStatus:
    subscriber_id_configured: bool
    unique_key_id_configured: bool
    private_key_loaded: bool
    public_key_loaded: bool
    encryption_private_key_loaded: bool
    encryption_public_key_loaded: bool
    todos: tuple[str, ...]


class SigningNotConfiguredError(RuntimeError):
    pass


def build_body_digest(body: bytes) -> str:
    digest = hashlib.blake2b(body, digest_size=64).digest()
    return f"{DIGEST_ALGORITHM}={base64.b64encode(digest).decode('ascii')}"


def build_signing_string(created: int, expires: int, digest: str) -> bytes:
    return f"(created): {created}\n(expires): {expires}\ndigest: {digest}".encode("utf-8")


def decode_ed25519_private_key(value: str) -> SigningKey:
    key_bytes = _decode_base64_key(value)
    if len(key_bytes) == 32:
        return SigningKey(key_bytes)
    if len(key_bytes) == 64:
        return SigningKey(key_bytes[:32])
    raise SigningNotConfiguredError("Ed25519 private key must decode to 32-byte seed or 64-byte secret key material")


def decode_ed25519_public_key(value: str) -> bytes:
    key_bytes = _decode_base64_key(value)
    if len(key_bytes) != 32:
        raise SigningNotConfiguredError("Ed25519 public key must decode to 32 bytes")
    return key_bytes


def _decode_base64_key(value: str) -> bytes:
    normalized = _strip_pem_wrapping(value)
    try:
        return base64.b64decode(normalized, validate=True)
    except ValueError as exc:
        raise SigningNotConfiguredError("Ed25519 key must be base64 encoded raw key material") from exc


def _strip_pem_wrapping(value: str) -> str:
    lines = [line.strip() for line in value.strip().splitlines() if line.strip()]
    payload_lines = [line for line in lines if not line.startswith("-----")]
    return "".join(payload_lines)


class SigningService:
    """Outbound ONDC signing boundary.

    Generates the Beckn/ONDC Ed25519 subscriber Authorization header over the
    canonical created/expires/digest signing string.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def get_config(self) -> SigningConfig:
        private_key = self.settings.get_signing_private_key()
        public_key = self.settings.get_signing_public_key()
        if not self.settings.subscriber_id or not self.settings.unique_key_id or not private_key or not public_key:
            raise SigningNotConfiguredError(
                "SUBSCRIBER_ID, UNIQUE_KEY_ID, SIGNING_PRIVATE_KEY, and SIGNING_PUBLIC_KEY are required for ONDC signing"
            )
        return SigningConfig(
            subscriber_id=self.settings.subscriber_id,
            unique_key_id=self.settings.unique_key_id,
            private_key=private_key,
            public_key=public_key,
        )

    def get_key_status(self) -> SigningKeyStatus:
        signing_private_key_loaded = self.settings.get_signing_private_key() is not None
        signing_public_key_loaded = self.settings.get_signing_public_key() is not None
        encryption_private_key_loaded = self.settings.get_encryption_private_key() is not None
        encryption_public_key_loaded = self.settings.get_encryption_public_key() is not None

        todos: list[str] = []
        if not self.settings.subscriber_id:
            todos.append("TODO: configure SUBSCRIBER_ID from ONDC onboarding")
        if not self.settings.unique_key_id:
            todos.append("TODO: configure UNIQUE_KEY_ID from ONDC registry")
        if not signing_private_key_loaded:
            todos.append("TODO: configure SIGNING_PRIVATE_KEY or SIGNING_PRIVATE_KEY_PATH")
        if not signing_public_key_loaded:
            todos.append("TODO: configure SIGNING_PUBLIC_KEY or SIGNING_PUBLIC_KEY_PATH")
        if not encryption_private_key_loaded:
            todos.append("TODO: configure ENCRYPTION_PRIVATE_KEY or ENCRYPTION_PRIVATE_KEY_PATH if required")
        if not encryption_public_key_loaded:
            todos.append("TODO: configure ENCRYPTION_PUBLIC_KEY or ENCRYPTION_PUBLIC_KEY_PATH if required")

        return SigningKeyStatus(
            subscriber_id_configured=bool(self.settings.subscriber_id),
            unique_key_id_configured=bool(self.settings.unique_key_id),
            private_key_loaded=signing_private_key_loaded,
            public_key_loaded=signing_public_key_loaded,
            encryption_private_key_loaded=encryption_private_key_loaded,
            encryption_public_key_loaded=encryption_public_key_loaded,
            todos=tuple(todos),
        )

    async def build_authorization_header(self, body: bytes) -> Mapping[str, str]:
        config = self.get_config()
        signing_key = decode_ed25519_private_key(config.private_key)
        configured_public_key = decode_ed25519_public_key(config.public_key)
        if signing_key.verify_key.encode() != configured_public_key:
            raise SigningNotConfiguredError("SIGNING_PRIVATE_KEY does not match SIGNING_PUBLIC_KEY")

        created = int(time.time())
        expires = created + DEFAULT_SIGNATURE_TTL_SECONDS
        digest = build_body_digest(body)
        signing_string = build_signing_string(created, expires, digest)
        signature = base64.b64encode(signing_key.sign(signing_string).signature).decode("ascii")

        header = (
            f'Signature keyId="{config.subscriber_id}|{config.unique_key_id}|{SIGNATURE_ALGORITHM}",'
            f'algorithm="{SIGNATURE_ALGORITHM}",'
            f'created="{created}",'
            f'expires="{expires}",'
            f'headers="{SIGNED_HEADERS}",'
            f'signature="{signature}"'
        )
        return {"Authorization": header}


signing_service = SigningService()
