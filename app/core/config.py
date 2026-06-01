from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ONDC MF Buyer NP POC"
    app_env: str = "local"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    subscriber_id: str | None = None
    unique_key_id: str | None = None
    signing_private_key_path: str | None = None
    ondc_registry_url: str | None = None
    ondc_registry_timeout_seconds: float = 10.0
    require_ondc_auth: bool = False

    bap_id: str = "api.buyerapp.com"
    bap_uri: str = "https://api.buyerapp.com/ondc"
    bap_callback_uri: str = "https://api.buyerapp.com/ondc"
    bpp_id: str = "api.sellerapp.com"
    bpp_uri: str = "https://api.sellerapp.com/ondc"

    ondc_domain: str = "ONDC:FIS14"
    ondc_version: str = "2.0.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
