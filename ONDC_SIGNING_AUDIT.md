# ONDC Signing, Registry, and Callback Verification Audit

Audit date: 2026-06-03  
Scope: complete repository inspection, with primary evidence from `app/`, scripts, and top-level docs. No code was modified.

## Phase 2: ONDC Registry Audit

### Search Terms Used

Searched repository code/docs for: `registry`, `subscriber`, `lookup`, `ukId`, `unique_key_id`.

### Exact Files Found

| File | Evidence |
|---|---|
| `app/core/config.py:14-18` | Defines `subscriber_id`, `unique_key_id`, `ondc_registry_url`, registry timeout |
| `app/services/registry_service.py:11-13` | `RegistrySubscriber` includes `subscriber_id`, `unique_key_id`, `signing_public_key` |
| `app/services/registry_service.py:31-40` | `lookup_subscriber()` posts `subscriber_id` and optional `unique_key_id` to configured registry URL |
| `app/services/verification_service.py:21-22` | Docstring says verification should parse subscriber/key IDs and look up public keys |
| `app/services/signing_service.py:10-11,31-38` | Signing config requires `subscriber_id` and `unique_key_id` |
| `.env.example:8-12` | Contains placeholder subscriber, unique key ID, private key path, registry URL |
| `UAT_READINESS.md:11-16,26-37` | States subscriber, registry, public key, private key, signing, and verification are required |
| `ONDC_BUYER_NP_ARCHITECTURE.md:81-88,117-126` | Documents registry/signing/verification service boundaries |
| `Gap_Analysis.md:5-8,11` | Notes missing onboarding, ukId/keyId, key pairs, and signature verification |
| `ONDC_Flow.md:358-366` | Documents Authorization header and notes signing is not implemented |

### Registry Capability Status

| Capability | Status | Evidence | Gap |
|---|---|---|---|
| Subscriber lookup | PARTIAL | `RegistryService.lookup_subscriber(subscriber_id, unique_key_id)` exists | Not wired into route handling or callback verification |
| Registry lookup | PARTIAL | HTTP POST to `settings.ondc_registry_url` using `httpx` | No known PreProd/Prod URL mapping, response validation, retry policy, or auth |
| Registry verification | MISSING | `VerificationService` has docstring only; no parsing/verification implementation | Must parse Authorization keyId, look up public key, validate subscriber/key/domain |
| `ukId` / unique key support | PARTIAL | `unique_key_id` exists; no literal `ukId` implementation found | Map ONDC registry key ID semantics explicitly |

Overall registry status: **PARTIAL**

## Phase 3: Signing Audit

### Search Terms Used

Searched repository code/docs for: `Ed25519`, `sign`, `verify`, `Authorization`, `Signature`, `digest`, `crypto`, `NotImplementedError`.

### Exact Files Found

| File | Evidence |
|---|---|
| `app/services/signing_service.py:20-24` | Declares outbound signing boundary and states Ed25519/digest/header should be implemented |
| `app/services/signing_service.py:31-38` | Requires subscriber ID, unique key ID, private key path |
| `app/services/signing_service.py:41-43` | `build_authorization_header()` raises `NotImplementedError` |
| `app/services/verification_service.py:18-22` | Declares inbound ONDC signature verification boundary |
| `app/services/verification_service.py:32-38` | Only checks header presence when required, then raises `NotImplementedError` |
| `app/services/buyer_np_service.py:10,21,26` | Injects `SigningService` but never calls it |
| `app/services/buyer_np_service.py:11,22,27` | Injects `VerificationService` but never calls it |
| `ONDC_Flow.md:358-366` | Shows production Authorization header shape and says app does not implement signing |
| `UAT_READINESS.md:15-16` | States signing and verification must be implemented |

### NotImplementedError Locations

| File | Line | Method |
|---|---:|---|
| `app/services/signing_service.py` | 43 | `SigningService.build_authorization_header()` |
| `app/services/verification_service.py` | 38 | `VerificationService.verify_headers()` |

### Signing Status

| Item | Status | Evidence |
|---|---|---|
| Ed25519 signing | STUB | Mentioned in docstring, but implementation raises `NotImplementedError` |
| Digest generation | MISSING | No digest computation code found |
| Authorization header generation | STUB | Method exists but raises |
| Private key loading | MISSING | Path is configured, but no key loading code exists |
| Outbound route signing | MISSING | `handle_command()` does not call `self.signer` |
| Signature verification | STUB | Header presence can be enforced; verification raises |
| Authorization header parsing | MISSING | No parser for `Signature keyId=...` |
| Public key registry lookup during verification | MISSING | `VerificationService.registry` exists but is not used in `verify_headers()` |
| Crypto dependency | MISSING | `requirements.txt` has no PyNaCl/libsodium/cryptography dependency |

Overall signing status: **STUB / NOT IMPLEMENTED**

## Phase 4: Callback Verification Audit

Inbound callback routes are in `app/callbacks/ondc_callbacks.py`. They accept `FIS14CallbackRequest`, call `buyer_np_service.handle_callback()`, persist the event, and return ACK.

| Verification item | Status | Evidence | Missing work |
|---|---|---|---|
| Authorization header parsing | MISSING | Callback controllers do not accept `Request`/headers; no parser exists | Parse `Authorization` header and keyId fields |
| Signature validation | MISSING | `VerificationService.verify_headers()` is not called by `BuyerNPService.handle_callback()` | Verify Ed25519 signature over canonical signing string |
| Timestamp format validation | PARTIAL | `ONDCContext.validate_timestamp()` parses ISO/RFC3339 | Enforce clock skew and reject stale callbacks |
| TTL format validation | PARTIAL | `ONDCContext.validate_ttl()` validates ISO duration string pattern | Enforce expiry based on timestamp + TTL |
| Subscriber validation | MISSING | No check that callback `bpp_id` matches registry/auth signer | Validate subscriber ID and key ID from registry |
| Registry public key lookup | MISSING | Registry service exists, but verification does not call it | Lookup public key for sender |
| Replay protection | PARTIAL | In-memory duplicate `message_id` check | Use durable store and auth timestamp/expiry |
| Callback action matching | IMPLEMENTED | `ProtocolValidationService.validate_callback()` enforces endpoint/action match | Add lifecycle order validation |

## Callback Verification Conclusion

Inbound callbacks are **not ONDC production verified**. They are schema-validated and persisted, but any caller that submits a structurally valid payload can receive ACK unless custom infrastructure blocks it before FastAPI.

## DEPLOY NOW

**DEPLOY NOW = NO**

Exact missing signing/security items before deployment:

1. Implement Ed25519 signing in `SigningService.build_authorization_header()`.
2. Add digest computation and canonical signing string support.
3. Add crypto dependency and secure key loading.
4. Parse inbound `Authorization` headers.
5. Verify callback signatures using registry public keys.
6. Wire `VerificationService.verify_headers()` into every callback endpoint or middleware.
7. Enforce timestamp freshness and TTL expiry.
8. Validate callback sender subscriber/key against registry and expected BPP.
