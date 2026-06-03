from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class StartupConfigurationError(RuntimeError):
    pass


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ONDC MF Buyer NP"
    app_env: str = "local"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    subscriber_id: str | None = None
    unique_key_id: str | None = None
    signing_private_key: str | None = None
    signing_public_key: str | None = None
    encryption_private_key: str | None = None
    encryption_public_key: str | None = None
    signing_private_key_path: str | None = None
    signing_public_key_path: str | None = None
    encryption_private_key_path: str | None = None
    encryption_public_key_path: str | None = None
    ondc_registry_url: str | None = None
    ondc_registry_timeout_seconds: float = 10.0
    require_ondc_auth: bool = False

    bap_id: str = "api.buyerapp.com"
    bap_uri: str = "https://api.buyerapp.com/ondc"
    bap_callback_uri: str = "https://api.buyerapp.com/ondc"
    bpp_id: str = "api.bpp.example.com"
    bpp_uri: str = "https://api.bpp.example.com/ondc"

    ondc_domain: str = "ONDC:FIS14"
    ondc_version: str = "2.0.0"

    def get_signing_private_key(self) -> str | None:
        return self._resolve_key_value(self.signing_private_key, self.signing_private_key_path)

    def get_signing_public_key(self) -> str | None:
        return self._resolve_key_value(self.signing_public_key, self.signing_public_key_path)

    def get_encryption_private_key(self) -> str | None:
        return self._resolve_key_value(self.encryption_private_key, self.encryption_private_key_path)

    def get_encryption_public_key(self) -> str | None:
        return self._resolve_key_value(self.encryption_public_key, self.encryption_public_key_path)

    def validate_startup_config(self) -> None:
        missing: list[str] = []
        if not self._is_configured(self.subscriber_id):
            missing.append("SUBSCRIBER_ID")
        if not self._is_configured(self.unique_key_id):
            missing.append("UNIQUE_KEY_ID")
        if not self.get_signing_private_key():
            missing.append("SIGNING_PRIVATE_KEY or SIGNING_PRIVATE_KEY_PATH")
        if not self.get_signing_public_key():
            missing.append("SIGNING_PUBLIC_KEY or SIGNING_PUBLIC_KEY_PATH")
        if missing:
            raise StartupConfigurationError(
                "Missing required ONDC Buyer NP configuration: " + ", ".join(missing)
            )

    def _resolve_key_value(self, direct_value: str | None, legacy_value: str | None) -> str | None:
        for value in (direct_value, legacy_value):
            resolved = self._load_key_value(value)
            if resolved:
                return resolved
        return None

    def _load_key_value(self, value: str | None) -> str | None:
        if not self._is_configured(value):
            return None
        candidate = value.strip()
        path = Path(candidate).expanduser()
        if path.exists() and path.is_file():
            file_value = path.read_text(encoding="utf-8").strip()
            return file_value if self._is_configured(file_value) else None
        if self._looks_like_path(candidate):
            return None
        return candidate

    @staticmethod
    def _is_configured(value: str | None) -> bool:
        if not value or not value.strip():
            return False
        normalized = value.strip().upper()
        return not normalized.startswith("TODO")

    @staticmethod
    def _looks_like_path(value: str) -> bool:
        normalized = value.strip()
        return (
            normalized.startswith(("/", "./", "../", "~"))
            or normalized.startswith("file:")
            or "\\" in normalized
            or (len(normalized) > 2 and normalized[1:3] == ":\\")
            or normalized.endswith((".pem", ".key", ".pub", ".txt"))
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

