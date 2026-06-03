# ONDC Environment Audit

Audit date: 2026-06-03  
Scope: complete repository inspection, with primary evidence from `app/`, `.env.example`, scripts, and top-level docs. No code was modified.

## Phase 1: Environment Audit

### Environment Files and Settings

| Item | Exists? | Evidence |
|---|---:|---|
| `.env` | No | No `.env` file found at project root |
| `.env.example` | Yes | `.env.example` |
| `config.py` | Yes | `app/core/config.py` |
| `settings.py` | No | No `settings.py` found |
| Pydantic settings | Yes | `app/core/config.py` uses `BaseSettings` and `SettingsConfigDict(env_file=".env")` |

### Variable Matrix

| Variable | Used? | Mandatory for PreProd? | Current Value Source | Missing? |
|---|---:|---:|---|---:|
| `SUBSCRIBER_ID` | Partial | Yes | `.env.example`; `app/core/config.py:14`; used by `SigningService.get_config()` | Runtime value missing because `.env` absent |
| `UNIQUE_KEY_ID` | Partial | Yes | `.env.example`; `app/core/config.py:15`; used by `SigningService.get_config()` and registry lookup parameter | Runtime value missing because `.env` absent |
| `BAP_ID` | Yes | Yes | `.env.example`; default `api.buyerapp.com` in `app/core/config.py:21`; exposed by `/health` | Must be changed to registered subscriber ID |
| `BAP_URI` | Yes | Yes | `.env.example`; default `https://api.buyerapp.com/ondc` in `app/core/config.py:22`; exposed by `/health` | Must be changed to public registered URI |
| `BAP_CALLBACK_URI` | Configured, not functionally used | Yes | `.env.example`; default `https://api.buyerapp.com/ondc` in `app/core/config.py:23` | Must be set; code does not use it in handlers |
| `BPP_ID` | Dev/mock only | Optional per target flow | `.env.example`; default `api.bpp.example.com` in `app/core/config.py:24`; used by `app/services/ondc_service.py` mock callback context | Not mandatory globally; needed when targeting a specific BPP |
| `BPP_URI` | Dev/mock only | Optional per target flow | `.env.example`; default `https://api.bpp.example.com/ondc` in `app/core/config.py:25`; used by `app/services/ondc_service.py` mock callback context | Not wired into real outbound dispatch |
| `ONDC_DOMAIN` | Partial | Yes | `.env.example`; default `ONDC:FIS14` in `app/core/config.py:27`; `/health` reports it | Present, but schema validation uses hard-coded constant in `app/schemas/ondc.py` |
| `ONDC_VERSION` | Partial | Yes | `.env.example`; default `2.0.0` in `app/core/config.py:28` | Present, but schema validation uses hard-coded constant in `app/schemas/ondc.py` |
| `ONDC_REGISTRY_URL` | Yes, boundary only | Yes | `.env.example`; `app/core/config.py:17`; used by `app/services/registry_service.py:32,40` | Runtime value missing; no real PreProd/Prod URL configured |
| `SIGNING_PRIVATE_KEY` | Yes, boundary only | Yes | `.env.example`; `app/core/config.py:16`; required by `SigningService.get_config()` | Runtime value missing; signing still unimplemented |
| `SIGNING_PUBLIC_KEY` | No | Yes for registration/ops | Not present in `Settings`; not in `.env.example` | Missing from code/config |
| `ENCRYPTION_PRIVATE_KEY` | No | Usually required where ONDC participant encryption is used | Not present in `Settings`; not in `.env.example` | Missing from code/config |
| `ENCRYPTION_PUBLIC_KEY` | No | Usually required where ONDC participant encryption is used | Not present in `Settings`; not in `.env.example` | Missing from code/config |

### Other Security-Relevant Variables Found

| Variable | Evidence | Note |
|---|---|---|
| `REQUIRE_ONDC_AUTH` | `.env.example`; `app/core/config.py:19`; `app/services/verification_service.py:30,34` | Defaults to `false`; must be `true` for PreProd callback verification, but verification implementation is still stubbed |
| `ONDC_REGISTRY_TIMEOUT_SECONDS` | `.env.example`; `app/core/config.py:18`; `app/services/registry_service.py:39` | Used for registry HTTP client timeout |

## Account-Specific Configuration

Your ONDC registration details:

| Field | Value |
|---|---|
| Subscriber ID | `ondcapi.walkingtree.tech` |
| Registry domain | `ONDC:FIS14` |
| Role | Buyer NP |

### Where Each Account Value Should Be Configured

| Account item | Configure in | Code evidence |
|---|---|---|
| Subscriber ID | `SUBSCRIBER_ID` and `BAP_ID` in `.env` | `app/core/config.py:14,21`; `SigningService` requires `subscriber_id` |
| Unique Key ID | `UNIQUE_KEY_ID` in `.env` | `app/core/config.py:15`; `SigningService` requires `unique_key_id`; registry lookup accepts it |
| Signing private key | `SIGNING_PRIVATE_KEY` in `.env` | `app/core/config.py:16`; `SigningService.get_config()` |
| Signing public key | Not currently supported by `Settings`; add only after code support or keep as operational note | Missing from `app/core/config.py` and `.env.example` |
| Encryption private key | Not currently supported by `Settings` | Missing from `app/core/config.py` and `.env.example` |
| Encryption public key | Not currently supported by `Settings` | Missing from `app/core/config.py` and `.env.example` |

### Exact `.env` Entries for Your Account

These entries should exist in a real `.env` file. Values marked `REPLACE_*` must be filled from your ONDC onboarding/key generation material.

```dotenv
APP_NAME=ONDC MF Buyer NP
APP_ENV=preprod
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

SUBSCRIBER_ID=ondcapi.walkingtree.tech
UNIQUE_KEY_ID=REPLACE_WITH_ONDC_UNIQUE_KEY_ID
SIGNING_PRIVATE_KEY=/etc/ondc-buyer-np/keys/signing-private.pem
ONDC_REGISTRY_URL=REPLACE_WITH_ONDC_PREPROD_REGISTRY_LOOKUP_URL
ONDC_REGISTRY_TIMEOUT_SECONDS=10
REQUIRE_ONDC_AUTH=true

BAP_ID=ondcapi.walkingtree.tech
BAP_URI=https://ondcapi.walkingtree.tech/ondc
BAP_CALLBACK_URI=https://ondcapi.walkingtree.tech/ondc

BPP_ID=
BPP_URI=

ONDC_DOMAIN=ONDC:FIS14
ONDC_VERSION=2.0.0

# Not currently read by app/core/config.py; add Settings support before relying on these.
SIGNING_PUBLIC_KEY=/etc/ondc-buyer-np/keys/signing-public.pem
ENCRYPTION_PRIVATE_KEY=/etc/ondc-buyer-np/keys/encryption-private.pem
ENCRYPTION_PUBLIC_KEY=/etc/ondc-buyer-np/keys/encryption-public.pem
```

## Environment Findings

| Status | Finding |
|---|---|
| PARTIAL | Core Buyer NP env variables exist in `.env.example` and `Settings` |
| MISSING | `.env` does not exist |
| MISSING | `SIGNING_PUBLIC_KEY`, `ENCRYPTION_PRIVATE_KEY`, and `ENCRYPTION_PUBLIC_KEY` are not modeled in `Settings` |
| PARTIAL | `BAP_CALLBACK_URI` exists in config but is not functionally used |
| PARTIAL | `ONDC_DOMAIN` and `ONDC_VERSION` exist in settings, but validation uses constants instead of settings |

## DEPLOY NOW

**DEPLOY NOW = NO**

Missing before deployment:

1. Create `.env` with real `SUBSCRIBER_ID=ondcapi.walkingtree.tech`, `BAP_ID=ondcapi.walkingtree.tech`, public `BAP_URI`, `BAP_CALLBACK_URI`, `UNIQUE_KEY_ID`, registry URL, and key paths.
2. Add/read signing public and encryption key configuration if required by your ONDC onboarding profile.
3. Set `REQUIRE_ONDC_AUTH=true` only after implementing callback verification.


