# ONDC Compliance Report

Audit date: 2026-06-03  
Scope: `d:\project\ONDC-BACKEND\ONDC-POC`

## Overall Compliance

| Area | Status | Summary |
|---|---|---|
| ONDC Buyer NP route surface | Partially compliant | All requested logical APIs exist under `/ondc`, not root |
| FIS14 envelope schema | Partially compliant | Domain, version, action, timestamp format, TTL format, and IDs are validated |
| FIS14 message schema | Missing | `message` is an unrestricted dictionary |
| Registry support | Partial | Config and lookup boundary exist; no environment-specific verification flow |
| Signing | Missing | Stub raises `NotImplementedError` |
| Signature verification | Missing | Stub raises `NotImplementedError` when auth is required |
| Callback persistence | Partial | In-memory only |
| Production deployment | Partial | FastAPI/Uvicorn compatible, but no Dockerfile, no systemd/nginx files, no durable store |

## Phase 3: ONDC Registry Compliance

| Requirement | Status | Evidence | Gap |
|---|---|---|---|
| Subscriber ID support | Partial | `Settings.subscriber_id`; `.env.example` has `SUBSCRIBER_ID` | Not enforced in request handling; no registered value |
| Unique Key ID support | Partial | `Settings.unique_key_id`; `.env.example` has `UNIQUE_KEY_ID` | Only read by signing config; not used by handlers |
| Signing key support | Partial | `SIGNING_PRIVATE_KEY`; `SigningService.get_config()` | No key loading, no Ed25519 signing |
| Encryption key support | Missing | No encryption key config or service found | Add encryption key config, storage, rotation, registry mapping if required by target ONDC flow |
| Registry lookup support | Partial | `RegistryService.lookup_subscriber()` posts `subscriber_id` and optional `unique_key_id` | Generic URL only; no PreProd/Prod endpoint mapping; no schema mapping |
| Registry verification support | Missing | `VerificationService.verify_headers()` does not parse key IDs or call lookup | Implement Authorization parsing, lookup, key selection, digest/signature verification |
| PreProd Registry support | Partial | Can set `ONDC_REGISTRY_URL` manually | No predefined PreProd config, test harness, or credentials |
| Production Registry support | Partial | Can set `ONDC_REGISTRY_URL` manually | No production profile, key rotation, or failure policy |

## Phase 4: Signing and Security Audit

| Control | Status | Evidence | Required work |
|---|---|---|---|
| Ed25519 signing | Missing | `SigningService.build_authorization_header()` raises `NotImplementedError` | Implement canonical signing string, digest, key loading, Ed25519 signature |
| Signature verification | Missing | `VerificationService.verify_headers()` raises `NotImplementedError` when auth required | Parse Authorization, lookup public key, verify digest/signature |
| Authorization header generation | Missing | Signing method stub only | Generate ONDC `Signature ...` header for outbound requests |
| Authorization header validation | Partially implemented | Optional presence check if `REQUIRE_ONDC_AUTH=true` | Validate structure, created/expires, digest, subscriber, ukId, algorithm |
| Timestamp validation | Partially implemented | `ONDCContext.validate_timestamp()` parses ISO/RFC3339 | Enforce allowed clock skew/freshness |
| TTL validation | Partially implemented | Regex validates `PTnH/PTnM/PTnS` | Enforce expiry and action/domain-specific TTL rules |
| Message ID validation | Partially implemented | Non-empty validator; filesystem duplicate protection | Validate UUID/format if required; database-backed duplicate protection for production |
| Transaction ID validation | Partially implemented | Non-empty validator; repository groups by transaction | Validate lifecycle continuity and state transitions |
| Payload schema validation | Missing | `message: dict[str, Any]` | Add action-specific FIS14 Pydantic models or JSON Schema validation |
| Replay protection | Missing | No created/expires/signature validation | Add timestamp, TTL, nonce/message ID replay checks backed by DB |
| Secrets management | Missing | File path setting only | Use secure key storage or mounted secret with strict permissions |

## Phase 5: Domain Validation

| Field | Status | Evidence | Gap |
|---|---|---|---|
| `context.domain` | Implemented | Must equal `ONDC:FIS14` in `ONDCContext.validate_domain()` | None for current hard-coded target |
| Buyer NP / BAP identity | Partial | Requires `bap_id` and `bap_uri`; config has `BAP_ID`, `BAP_URI`, `BAP_CALLBACK_URI` | Does not assert request `bap_id` equals configured subscriber |
| Investment domain | Partial | FIS14 domain and mutual-funds examples are loaded | No message-level mutual fund validation |
| `context.version` | Implemented for `2.0.0` | `ONDC_FIS14_VERSION = "2.0.0"` | Local specs include `FIS14_2.1.0_220325.md`; confirm target version before UAT |
| `context.action` | Implemented | Known action validator plus endpoint/action matching | No flow/state transition validation |
| `context.ttl` | Partially implemented | ISO duration format regex | No expiry, max TTL, or action-specific TTL validation |
| `context.location` | Partially implemented | Optional `dict` in code | Local `context.yaml` marks `location.country.code` and `location.city.code` mandatory |
| `bpp_id` / `bpp_uri` | Partially implemented | Optional context fields and settings | Commands do not dispatch to `bpp_uri`; callbacks do not verify BPP identity |

## Protocol Compliance Gaps

1. The command endpoints are not true outbound network commands; they are HTTP receivers that ACK and persist the submitted payload.
2. No gateway/BPP client exists to send signed requests to counterparty NPs.
3. Inbound callbacks are accepted without signature verification by default.
4. The application validates only the context envelope; action-specific `message` validation is missing.
5. Transaction lifecycle ordering is not enforced.
6. `location` is optional in code although the local FIS14 context attributes mark it mandatory.
7. Protocol version is hard-coded to `2.0.0`; local specs contain a `2.1.0` changelog.

## Phase 7: Deployment Readiness

| Check | Status | Evidence |
|---|---|---|
| `requirements.txt` | Present | FastAPI, Uvicorn, Pydantic, dotenv, httpx |
| Dockerfile | Missing | No `Dockerfile` found |
| `.env.example` | Present | Contains Buyer NP identity and registry placeholders |
| Nginx compatibility | Partial | App can run behind reverse proxy; no config included |
| Gunicorn compatibility | Partial | ASGI app exists as `app.main:app`; `gunicorn` not in requirements |
| Uvicorn compatibility | Implemented | `uvicorn[standard]` in requirements; FastAPI app present |
| Health endpoint | Implemented | `GET /health` in `app/main.py` |
| Linux VM deployability | Partial | Can run with Python and Uvicorn; needs systemd/nginx/SSL/durable store |
| Tests | Missing | No test suite found |
| Database/durable store | Partial | Filesystem JSON persistence exists; database persistence is still missing |

Deployment readiness score: **42 / 100**

Score rationale:

- +15 route completeness
- +10 schema/context validation
- +5 local transaction capture
- +5 health endpoint and Uvicorn compatibility
- +5 environment template
- +2 local Postman/UAT artifacts
- Major deductions for signing, verification, registry, durable persistence, BPP dispatch, tests, and deployment artifacts.

## Phase 11: UAT Readiness

| UAT Area | Ready? | Blockers |
|---|---|---|
| ONDC PreProd Testing | No | Signing, verification, registry, dispatch, durable persistence |
| Pramaan Testing | No | Auth, protocol validation depth, lifecycle validation |
| Registry Verification | No | No real subscriber/key registration flow in app |

## Recommended Priority Order

1. Implement ONDC Authorization signing and verification with test vectors.
2. Add registry client mapping for PreProd and Production and wire it into verification.
3. Add outbound BPP dispatch service and use `bpp_uri`/registry resolved endpoints.
4. Replace filesystem repository with PostgreSQL for production.
5. Add FIS14 action-specific message schemas and lifecycle validation.
6. Add tests for valid/invalid envelope, auth, duplicate message, and full happy-path flow.
7. Add production deployment artifacts and observability.

