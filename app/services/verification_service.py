from dataclasses import dataclass
from typing import Mapping

from app.core.config import get_settings
from app.services.registry_service import RegistryService, registry_service


@dataclass(frozen=True)
class VerificationConfig:
    require_auth_header: bool


class VerificationNotConfiguredError(RuntimeError):
    pass


class VerificationService:
    """Inbound ONDC signature verification boundary.

    No fake verification is implemented. UAT should enable required auth headers,
    parse subscriber/key ids from Authorization, look up public keys in the ONDC
    registry, and verify the Ed25519 signature over the canonical signing string.
    """

    def __init__(self, registry: RegistryService = registry_service) -> None:
        self.settings = get_settings()
        self.registry = registry

    def get_config(self) -> VerificationConfig:
        return VerificationConfig(require_auth_header=self.settings.require_ondc_auth)

    async def verify_headers(self, headers: Mapping[str, str], body: bytes) -> None:
        config = self.get_config()
        if config.require_auth_header and "authorization" not in {key.lower() for key in headers}:
            raise VerificationNotConfiguredError("ONDC Authorization header is required but not present")
        if not config.require_auth_header:
            return
        raise NotImplementedError("Production Ed25519 ONDC verification is not implemented in this POC")


verification_service = VerificationService()
