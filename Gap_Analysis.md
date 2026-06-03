# Gap Analysis - ONDC Buyer NP

## Current Status

| Area | Status | Notes |
|---|---|---|
| Buyer NP routes | Implemented | All command and callback endpoints exist under `/ondc` |
| FIS14 context validation | Partial | Domain, version, action, timestamp format, TTL format, and required IDs are validated |
| Filesystem persistence | Implemented | Events are saved as JSON under `storage/` |
| Registry lookup | Partial | `RegistryService` has a lookup boundary but is not wired into verification |
| Signing | Missing | No fake signing; Ed25519 implementation is still required |
| Callback verification | Missing | Header verification boundary exists but is not implemented |
| Durable database | Missing | Filesystem persistence is useful for local/UAT evidence, not final production storage |
| BPP dispatch | Missing | Command routes currently ACK and persist; outbound network dispatch is still required |
| FIS14 message models | Missing | `message` remains a generic dictionary |
| Automated tests | Missing | No test suite is present |

## Required Before ONDC PreProd

1. Configure real `SUBSCRIBER_ID`, `UNIQUE_KEY_ID`, `BAP_ID`, `BAP_URI`, and `BAP_CALLBACK_URI`.
2. Register signing and encryption public keys with ONDC as required by onboarding.
3. Implement Ed25519 Authorization header signing.
4. Implement inbound Authorization header parsing and verification.
5. Wire registry lookup into callback verification.
6. Implement real outbound dispatch to the target counterparty NP.
7. Enforce timestamp freshness, TTL expiry, replay protection, and transaction lifecycle rules.
8. Add action-specific FIS14 message validation.
9. Add automated tests for happy path and failure cases.
10. Add production deployment hardening.

## Priority Matrix

| Priority | Item |
|---|---|
| P0 | Signing, verification, registry wiring, account configuration |
| P1 | Outbound dispatch, lifecycle validation, FIS14 message models |
| P2 | Durable database, observability, production deployment automation |

## Deployment Decision

Deploy for local development: **Yes**

Deploy for ONDC PreProd/Production: **No**
