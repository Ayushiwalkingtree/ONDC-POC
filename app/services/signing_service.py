from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from app.core.config import get_settings


@dataclass(frozen=True)
class SigningConfig:
    subscriber_id: str
    unique_key_id: str
    private_key_path: Path


class SigningNotConfiguredError(RuntimeError):
    pass


class SigningService:
    """Outbound ONDC signing boundary.

    No fake crypto is implemented here. A production implementation must load an
    Ed25519 private key from secure storage, compute the ONDC digest/signature, and
    return the Authorization header.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def get_config(self) -> SigningConfig:
        if not self.settings.subscriber_id or not self.settings.unique_key_id or not self.settings.signing_private_key_path:
            raise SigningNotConfiguredError(
                "SUBSCRIBER_ID, UNIQUE_KEY_ID, and SIGNING_PRIVATE_KEY_PATH are required for ONDC signing"
            )
        return SigningConfig(
            subscriber_id=self.settings.subscriber_id,
            unique_key_id=self.settings.unique_key_id,
            private_key_path=Path(self.settings.signing_private_key_path),
        )

    async def build_authorization_header(self, body: bytes) -> Mapping[str, str]:
        self.get_config()
        raise NotImplementedError("Production Ed25519 ONDC signing is not implemented in this POC")


signing_service = SigningService()
