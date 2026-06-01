from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging

OPENAPI_DESCRIPTION = """
## ONDC Mutual Fund Buyer NP (BAP) POC

Buyer NP oriented FastAPI POC for Mutual Funds using domain `ONDC:FIS14`.

### Flow

1. Buyer NP command endpoints accept and validate BAP protocol requests.
2. BPP callback endpoints receive `on_*` responses and persist protocol events.
3. `/ondc/transactions` exposes the local repository state for development.

### Buyer NP lifecycle

`search -> on_search -> select -> on_select -> init -> on_init -> confirm -> on_confirm -> status/on_status/on_update`

Additional APIs included: `update`, `cancel`, `track`, `support` and matching callbacks.

> Signing, verification, and registry modules are structured for production wiring but do not implement fake crypto.
"""

OPENAPI_TAGS = [
    {
        "name": "Health",
        "description": "Service health check",
    },
    {
        "name": "1. Buyer NP Commands",
        "description": "Buyer NP command endpoints. Each validates FIS14 context, persists the event, and ACKs.",
    },
    {
        "name": "2. Buyer NP Callback Receivers",
        "description": "BPP callback receivers for the Buyer NP. Each validates FIS14 context, persists the event, and ACKs.",
    },
    {
        "name": "3. Debug - Transaction Repository",
        "description": "Inspect local repository events for this POC session.",
    },
]


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        description=OPENAPI_DESCRIPTION,
        version="0.2.0",
        openapi_tags=OPENAPI_TAGS,
        contact={
            "name": "ONDC MF Buyer NP POC",
            "url": "https://resources.ondc.org/financial-services",
        },
        license_info={
            "name": "POC - Not for production",
        },
    )

    @application.get("/health", tags=["Health"], summary="Health check")
    async def health() -> dict:
        return {
            "status": "ok",
            "app": settings.app_name,
            "domain": settings.ondc_domain,
            "bap_id": settings.bap_id,
            "bap_uri": settings.bap_uri,
            "swagger": "/docs",
            "postman_collection": "/postman/ONDC_MF_BUYER_NP_UAT.postman_collection.json",
        }

    application.include_router(api_router)
    return application


app = create_app()
