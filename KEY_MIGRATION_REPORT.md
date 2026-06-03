# Key Migration Report

Audit date: 2026-06-03

## Summary

Key handling was migrated from file-path-only configuration to direct ENV key configuration with backward compatibility.

Actual key values are intentionally not included in this report.

## Old Configuration

Previously supported variables:

```dotenv
SIGNING_PRIVATE_KEY_PATH=<file path>
SIGNING_PUBLIC_KEY_PATH=<file path>
ENCRYPTION_PRIVATE_KEY_PATH=<file path>
ENCRYPTION_PUBLIC_KEY_PATH=<file path>
```

The implementation assumed these values pointed to files.

## New Configuration

Preferred variables:

```dotenv
SIGNING_PRIVATE_KEY=<raw key value>
SIGNING_PUBLIC_KEY=<raw key value>
ENCRYPTION_PRIVATE_KEY=<raw key value>
ENCRYPTION_PUBLIC_KEY=<raw key value>
```

Backward-compatible variables remain supported:

```dotenv
SIGNING_PRIVATE_KEY_PATH=<file path or raw key value>
SIGNING_PUBLIC_KEY_PATH=<file path or raw key value>
ENCRYPTION_PRIVATE_KEY_PATH=<file path or raw key value>
ENCRYPTION_PUBLIC_KEY_PATH=<file path or raw key value>
```

## Priority Order

1. Direct key env variables.
2. Existing `*_PATH` variables.
3. Startup failure for required signing keys.

## Key Resolution Rules

- If a configured value points to an existing file, file contents are loaded.
- If a configured value looks like a missing file path, it is treated as missing.
- Otherwise, the value is treated as a raw key.
- `TODO*` values are treated as missing.

## Startup Validation

Startup now fails if any required value is missing:

- `SUBSCRIBER_ID`
- `UNIQUE_KEY_ID`
- `SIGNING_PRIVATE_KEY` or `SIGNING_PRIVATE_KEY_PATH`
- `SIGNING_PUBLIC_KEY` or `SIGNING_PUBLIC_KEY_PATH`

Encryption keys are reported by `/health/keys` but are not currently startup blockers.

## Health Endpoint

Added:

```http
GET /health/keys
```

The endpoint returns only key-loaded flags and never returns key values.

Expected response shape:

```json
{
  "subscriber_id": "...",
  "unique_key_id": "...",
  "signing_private_key_loaded": true,
  "signing_public_key_loaded": true,
  "encryption_private_key_loaded": true,
  "encryption_public_key_loaded": true
}
```

## Changed Files

| File | Change |
|---|---|
| `app/core/config.py` | Added direct key variables, backward-compatible resolution helpers, path/raw detection, startup validation |
| `app/services/signing_service.py` | Uses loaded key values instead of assuming paths; reports key-loaded status |
| `app/services/verification_service.py` | Loads public keys through config helpers |
| `app/main.py` | Runs startup validation and adds `/health/keys` |
| `.env.example` | Migrated to direct key variable names |
| `KEY_MIGRATION_REPORT.md` | Added this migration report |

## Startup Validation Result

Validation with the current key values loaded from `.env.example`: **PASS**

Runtime blocker if deploying directly from this checkout: `.env` is not present, so the process must receive these variables from the environment, a secret manager, or a real `.env` file.
