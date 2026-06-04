# ONDC Readiness Report

Audit date: 2026-06-04  
Target subscriber/domain: `ondcapi.walkingtree.tech`, `ONDC:FIS14`  
Overall readiness score: **55%**

## Executive Assessment

The codebase is a structured FastAPI Buyer NP/BAP proof of concept for ONDC FIS14 mutual funds. It starts locally from the project virtualenv, exposes health APIs, registers 9 command endpoints and 9 callback endpoints under `/ondc`, signs outbound requests, verifies signed callbacks, and persists callback events to the filesystem.

It is **not ready for ONDC pre-prod testing** because outbound command dispatch cannot proceed with the current environment: `ONDC_REGISTRY_URL=TODO_ONDC_REGISTRY_URL`. Public deployment at `https://ondcapi.walkingtree.tech` is also not healthy; it returns nginx `502 Bad Gateway`.

## Project Structure

| Area | Finding |
|---|---|
| Framework | FastAPI |
| ASGI server | Uvicorn |
| API entry point | `app/main.py`, `app = create_app()` |
| Router aggregator | `app/api/router.py` |
| Command routes | `app/routes/ondc.py` |
| Callback routes | `app/callbacks/ondc_callbacks.py` |
| Schemas | `app/schemas/ondc.py`, `app/schemas/fis14.py`, `app/schemas/examples.py` |
| Services | Buyer NP orchestration, signing, verification, registry, outbound HTTP, protocol validation |
| Persistence | Filesystem repository under `storage/`; no SQL database found |
| Tests | 4 tests, all passing |
| Deployment docs | Markdown guide exists; no Dockerfile, compose, nginx config, or systemd unit in repo |

## Configuration

Configured environment variables:

| Variable | Current value/status |
|---|---|
| `SIGNING_PRIVATE_KEY` | Present |
| `SIGNING_PUBLIC_KEY` | Present |
| `ENCRYPTION_PRIVATE_KEY` | Present |
| `ENCRYPTION_PUBLIC_KEY` | Present |
| `ONDC_REGISTRY_URL` | `TODO_ONDC_REGISTRY_URL` |
| `ONDC_REGISTRY_TIMEOUT_SECONDS` | `10` |
| `SUBSCRIBER_ID` | `ondcapi.walkingtree.tech` |
| `UNIQUE_KEY_ID` | Present |
| `BAP_ID` | `ondcapi.walkingtree.tech` |
| `BAP_URI` | `https://ondcapi.walkingtree.tech/ondc` |
| `BAP_CALLBACK_URI` | `https://ondcapi.walkingtree.tech/ondc` |
| `ONDC_DOMAIN` | `ONDC:FIS14` |
| `ONDC_VERSION` | `2.0.0` |
| `APP_ENV` | `prod` |
| `HOST` | `0.0.0.0` |
| `PORT` | `8000` |
| `REQUIRE_ONDC_AUTH` | `true` |

Still TODO:

```env
ONDC_REGISTRY_URL=TODO_ONDC_REGISTRY_URL
```

Additional production config gap: `BPP_ID` and `BPP_URI` exist only as defaults in code unless supplied through incoming request context or env override.

## ONDC Endpoint Readiness

| Flow endpoint | Registered | Local result | Readiness |
|---|---:|---|---|
| `/ondc/search` | Yes | 503 | Blocked by registry TODO |
| `/ondc/select` | Yes | 503 | Blocked by registry TODO |
| `/ondc/init` | Yes | 503 | Blocked by registry TODO |
| `/ondc/confirm` | Yes | 503 | Blocked by registry TODO |
| `/ondc/status` | Yes | 503 | Blocked by registry TODO |
| `/ondc/track` | Yes | 503 | Blocked by registry TODO |
| `/ondc/cancel` | Yes | 503 | Blocked by registry TODO |
| `/ondc/update` | Yes | 503 | Blocked by registry TODO |
| `/ondc/support` | Yes | 503 | Blocked by registry TODO |
| `/ondc/rating` | No | 404 | Missing |

| Callback endpoint | Registered | Local result | Readiness |
|---|---:|---|---|
| `/ondc/on_search` | Yes | 200 | Pass with valid signature |
| `/ondc/on_select` | Yes | 200 | Pass with valid signature |
| `/ondc/on_init` | Yes | 200 | Pass with valid signature |
| `/ondc/on_confirm` | Yes | 200 | Pass with valid signature |
| `/ondc/on_status` | Yes | 200 | Pass with valid signature |
| `/ondc/on_track` | Yes | 200 | Pass with valid signature |
| `/ondc/on_cancel` | Yes | 200 | Pass with valid signature |
| `/ondc/on_update` | Yes | 200 | Pass with valid signature |
| `/ondc/on_support` | Yes | 200 | Pass with valid signature |
| `/ondc/on_rating` | No | 404 | Missing |

Note: unprefixed endpoints such as `/search` and `/on_search` are not registered. The implementation uses `/ondc/search` and `/ondc/on_search`.

## Signing and Verification

| Area | Status | Finding |
|---|---|---|
| Outbound request signing | Partial pass | Ed25519 Authorization header is generated over `(created)`, `(expires)`, and BLAKE2b body digest |
| Signing key validation | Pass | Private/public key mismatch is detected |
| Inbound callback verification | Partial pass | Valid signatures pass; tampered body fails; missing auth fails when required |
| Registry public key lookup | Partial | Verification can use registry if URL is real; current env uses fallback configured public key |
| Header freshness | Partial | Authorization `created`/`expires` checked |
| Context freshness | Gap | `context.timestamp` and `ttl` are format-checked only |
| Subscriber binding | Gap | Callback signer is not strongly bound to expected transaction/BPP |

## Registry Readiness

Current value:

```env
ONDC_REGISTRY_URL=TODO_ONDC_REGISTRY_URL
```

Expected registry request:

```json
{
  "subscriber_id": "<target subscriber id>",
  "unique_key_id": "<optional key id>"
}
```

Expected registry response fields accepted by code:

```json
{
  "subscriber_id": "string",
  "unique_key_id": "string",
  "signing_public_key": "string",
  "subscriber_url": "https://bpp.example.com/ondc"
}
```

Accepted aliases include `subscriberId`, `ukId`, `uniqueKeyId`, `signingPublicKey`, `subscriberUrl`, `subscriber_uri`, `subscriberUri`, `bpp_uri`, `bppUri`, and `url`.

## Health Checks

| Check | Result |
|---|---|
| App start with global Python | FAIL: missing `nacl` module |
| App start with `.venv` Python | PASS |
| `/health` local | PASS, 200 |
| `/health/keys` local | PASS, all key flags true |
| Database connectivity | Not applicable; no database configured |
| Filesystem repository | PASS; callback records persisted |
| Registry dependency | FAIL; registry URL is TODO |
| Outbound BPP dependency | Not testable with current config; dispatch stops before BPP call |
| Unit/integration tests | PASS, 4 passed |

## Public Deployment Check

Target: `https://ondcapi.walkingtree.tech`

| Check | Result |
|---|---|
| DNS | PASS: resolves to `115.245.177.14` |
| TCP 443 | PASS |
| TLS | PASS: TLSv1.3, wildcard certificate `*.walkingtree.tech`, valid from 2026-04-09 to 2026-10-24 |
| `/health` over HTTPS | FAIL: nginx `502 Bad Gateway` |
| `/ondc/on_search` over HTTPS | FAIL: nginx `502 Bad Gateway` |
| HTTP port 80 | Timeout from audit environment |

## Readiness Score Basis

| Category | Score |
|---|---:|
| App structure and route registration | 75% |
| ONDC command flow | 35% |
| Callback flow | 75% |
| Signing/verification | 70% |
| Registry integration | 30% |
| Request validation | 55% |
| Persistence | 50% |
| Deployment | 25% |

Weighted result: **55%**.

## Pre-Prod Decision

Current decision: **Do not start ONDC pre-prod testing yet.**

Minimum blockers to clear:

1. Replace `ONDC_REGISTRY_URL=TODO_ONDC_REGISTRY_URL` with the real ONDC pre-prod registry lookup URL.
2. Confirm subscriber onboarding for `ondcapi.walkingtree.tech` and `UNIQUE_KEY_ID`.
3. Ensure registry response returns a usable BPP `subscriber_url`.
4. Fix public deployment `502 Bad Gateway`.
5. Add or formally exclude `rating` and `on_rating` depending on the required FIS14 certification scenario.
6. Add action-specific FIS14 message validation.
7. Add callback signer/subscriber/transaction correlation checks.

