# File Change Summary

## Buyer NP Cleanup

- Standardized repository wording around Buyer NP, BAP, and `ONDC:FIS14`.
- Removed legacy non-Buyer NP Postman artifacts.
- Regenerated Buyer NP Postman collection, environment, payloads, and curl examples.

## Persistence

- Added `app/services/file_storage_service.py`.
- Replaced the default repository with filesystem-backed JSON persistence.
- Removed the old volatile repository adapter.
- Added tracked storage folders:
  - `storage/search/`
  - `storage/select/`
  - `storage/init/`
  - `storage/confirm/`
  - `storage/callbacks/`

## Configuration

- Regenerated `.env.example` with required Buyer NP variables:
  - `SUBSCRIBER_ID`
  - `UNIQUE_KEY_ID`
  - `BAP_ID`
  - `BAP_URI`
  - `BAP_CALLBACK_URI`
  - `ONDC_DOMAIN`
  - `ONDC_VERSION`

## Signing

- No fake signing was added.
- Added signing key availability detection through `SigningService.get_key_status()`.
- Added TODO placeholders for missing signing and encryption key paths in `.env.example`.

## Reports

- Added `DEPLOYMENT_READINESS_REPORT.md`.
