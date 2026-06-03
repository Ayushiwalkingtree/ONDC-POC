# Deployment Readiness Report

Audit date: 2026-06-03

## Summary

The repository is now a clean ONDC Buyer NP / BAP implementation for `ONDC:FIS14` with filesystem persistence. It is ready for local development and protocol-shape testing, but it is not ready for ONDC PreProd or Production deployment.

## Implemented

| Area | Status | Evidence |
|---|---|---|
| Buyer NP naming | Ready | README, docs, Postman, app metadata use Buyer NP / BAP / `ONDC:FIS14` |
| Command routes | Ready | `/ondc/search`, `/ondc/select`, `/ondc/init`, `/ondc/confirm`, `/ondc/status`, `/ondc/cancel`, `/ondc/update`, `/ondc/support`, `/ondc/track` |
| Callback routes | Ready | `/ondc/on_search`, `/ondc/on_select`, `/ondc/on_init`, `/ondc/on_confirm`, `/ondc/on_status`, `/ondc/on_cancel`, `/ondc/on_update`, `/ondc/on_support`, `/ondc/on_track` |
| Health endpoint | Ready | `/health` |
| OpenAPI/Swagger | Ready | `/openapi.json`, `/docs` |
| Filesystem persistence | Ready | `FileStorageService` writes JSON under `storage/` |
| Required env template | Ready | `.env.example` contains Buyer NP variables |
| Fake signing avoidance | Ready | Signing still raises `NotImplementedError`; no fake crypto added |
| Signing key detection | Ready | `SigningService.get_key_status()` reports missing key TODOs |

## Filesystem Persistence

Events are saved as JSON under:

```text
storage/
â”œâ”€â”€ search/
â”œâ”€â”€ select/
â”œâ”€â”€ init/
â”œâ”€â”€ confirm/
â””â”€â”€ callbacks/
```

Callbacks are stored below `storage/callbacks/{action}/`. Other command actions are stored below `storage/{action}/`.

## Signing Key Status

The implementation detects missing signing values and files. Current local status:

```text
TODO: configure SUBSCRIBER_ID from ONDC onboarding
TODO: configure UNIQUE_KEY_ID from ONDC registry
TODO: configure SIGNING_PRIVATE_KEY
TODO: configure SIGNING_PUBLIC_KEY
```

No fake signing keys were created.

## Required Before ONDC PreProd

1. Configure real `SUBSCRIBER_ID`, `UNIQUE_KEY_ID`, `BAP_ID`, `BAP_URI`, and `BAP_CALLBACK_URI`.
2. Configure ONDC registry URL.
3. Place real signing key files at configured paths.
4. Implement Ed25519 Authorization header generation.
5. Implement inbound Authorization header verification.
6. Wire registry lookup into verification.
7. Implement outbound dispatch to counterparty NPs.
8. Enforce timestamp freshness, TTL expiry, replay checks, and transaction lifecycle.
9. Add action-specific FIS14 message schemas.
10. Add production deployment artifacts and automated tests.

## Validation Commands

```powershell
$env:PYTHONPATH="D:\project\ONDC-BACKEND\ONDC-POC"
python scripts/generate_postman.py
python scripts/validate_uat_artifacts.py
```

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
curl http://localhost:8000/health
curl http://localhost:8000/openapi.json
```

## Deploy Decision

Local development deploy: **YES**

ONDC PreProd deploy: **NO**

Production deploy: **NO**

