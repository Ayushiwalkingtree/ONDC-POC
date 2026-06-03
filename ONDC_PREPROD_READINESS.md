# ONDC PreProd Readiness Audit

Audit date: 2026-06-03  
Role evaluated: Buyer NP / BAP  
Domain evaluated: `ONDC:FIS14`  
Registered subscriber supplied by user: `ondcapi.walkingtree.tech`

## Phase 5: Route Audit

All requested Buyer NP APIs exist under the `/ondc` prefix. They use `FIS14CommandRequest` or `FIS14CallbackRequest`, both derived from `FIS14ProtocolRequest`, and respond with `ONDCAckResponse`.

### Buyer NP Commands

| Route | Exists? | Schema | Controller | Service |
|---|---:|---|---|---|
| `/ondc/search` | Yes | `FIS14CommandRequest` | `app/routes/ondc.py::search` | `buyer_np_service.handle_command(..., "search")` |
| `/ondc/select` | Yes | `FIS14CommandRequest` | `app/routes/ondc.py::select` | `buyer_np_service.handle_command(..., "select")` |
| `/ondc/init` | Yes | `FIS14CommandRequest` | `app/routes/ondc.py::init_order` | `buyer_np_service.handle_command(..., "init")` |
| `/ondc/confirm` | Yes | `FIS14CommandRequest` | `app/routes/ondc.py::confirm` | `buyer_np_service.handle_command(..., "confirm")` |
| `/ondc/status` | Yes | `FIS14CommandRequest` | `app/routes/ondc.py::status` | `buyer_np_service.handle_command(..., "status")` |
| `/ondc/cancel` | Yes | `FIS14CommandRequest` | `app/routes/ondc.py::cancel` | `buyer_np_service.handle_command(..., "cancel")` |
| `/ondc/update` | Yes | `FIS14CommandRequest` | `app/routes/ondc.py::update` | `buyer_np_service.handle_command(..., "update")` |
| `/ondc/support` | Yes | `FIS14CommandRequest` | `app/routes/ondc.py::support` | `buyer_np_service.handle_command(..., "support")` |
| `/ondc/track` | Yes | `FIS14CommandRequest` | `app/routes/ondc.py::track` | `buyer_np_service.handle_command(..., "track")` |

### Buyer NP Callback Receivers

| Route | Exists? | Schema | Controller | Service |
|---|---:|---|---|---|
| `/ondc/on_search` | Yes | `FIS14CallbackRequest` | `app/callbacks/ondc_callbacks.py::on_search` | `buyer_np_service.handle_callback(..., "on_search")` |
| `/ondc/on_select` | Yes | `FIS14CallbackRequest` | `app/callbacks/ondc_callbacks.py::on_select` | `buyer_np_service.handle_callback(..., "on_select")` |
| `/ondc/on_init` | Yes | `FIS14CallbackRequest` | `app/callbacks/ondc_callbacks.py::on_init` | `buyer_np_service.handle_callback(..., "on_init")` |
| `/ondc/on_confirm` | Yes | `FIS14CallbackRequest` | `app/callbacks/ondc_callbacks.py::on_confirm` | `buyer_np_service.handle_callback(..., "on_confirm")` |
| `/ondc/on_status` | Yes | `FIS14CallbackRequest` | `app/callbacks/ondc_callbacks.py::on_status` | `buyer_np_service.handle_callback(..., "on_status")` |
| `/ondc/on_cancel` | Yes | `FIS14CallbackRequest` | `app/callbacks/ondc_callbacks.py::on_cancel` | `buyer_np_service.handle_callback(..., "on_cancel")` |
| `/ondc/on_update` | Yes | `FIS14CallbackRequest` | `app/callbacks/ondc_callbacks.py::on_update` | `buyer_np_service.handle_callback(..., "on_update")` |
| `/ondc/on_support` | Yes | `FIS14CallbackRequest` | `app/callbacks/ondc_callbacks.py::on_support` | `buyer_np_service.handle_callback(..., "on_support")` |
| `/ondc/on_track` | Yes | `FIS14CallbackRequest` | `app/callbacks/ondc_callbacks.py::on_track` | `buyer_np_service.handle_callback(..., "on_track")` |

## Phase 6: Real ONDC Flow Audit

### Does the App Actually Call a BPP?

| Command | Calls BPP? | Current behavior | Evidence |
|---|---:|---|---|
| `search` | No | Validates request, saves event, returns ACK | `app/routes/ondc.py:36`; `app/services/buyer_np_service.py:32-41` |
| `select` | No | Validates request, saves event, returns ACK | `app/routes/ondc.py:48`; `app/services/buyer_np_service.py:32-41` |
| `init` | No | Validates request, saves event, returns ACK | `app/routes/ondc.py:60`; `app/services/buyer_np_service.py:32-41` |
| `confirm` | No | Validates request, saves event, returns ACK | `app/routes/ondc.py:72`; `app/services/buyer_np_service.py:32-41` |

### Evidence Summary

- `BuyerNPService.handle_command()` calls `self.validator.validate_command()`, `_save_event()`, logs the command, and returns `self.ack()`.
- There is no HTTP client call in `BuyerNPService`.
- `httpx.AsyncClient` appears in `app/services/registry_service.py` only, for registry lookup, not BPP dispatch.
- `BPP_URI` is configured but only used by `app/services/ondc_service.py` when building mock callback contexts.
- `SigningService` is injected into `BuyerNPService`, but never called.

Conclusion: command routes **only return ACK and persist locally**. They do not perform real ONDC network dispatch to a BPP.

## Phase 7: PreProd Readiness

Can this app pass ONDC PreProd as-is?

**NO**

### PreProd Blockers

| Blocker | Severity | Evidence |
|---|---|---|
| Outbound ONDC signing not implemented | Critical | `app/services/signing_service.py:43` raises `NotImplementedError` |
| Inbound callback signature verification not implemented | Critical | `app/services/verification_service.py:38` raises `NotImplementedError` |
| Command endpoints do not call BPP/Gateway | Critical | `handle_command()` only saves and ACKs |
| Registry verification not wired | Critical | `RegistryService.lookup_subscriber()` exists but is not used by verification |
| No `.env` with real account values | High | `.env` missing; only `.env.example` exists |
| `REQUIRE_ONDC_AUTH` defaults false | High | `app/core/config.py:19` |
| No production database transaction store | High | Filesystem JSON persistence exists; database persistence is still missing |
| No action-specific FIS14 message validation | High | `message` is `dict[str, Any]` in `app/schemas/ondc.py` |
| Timestamp/TTL freshness not enforced | High | Only format validators exist |
| No lifecycle state machine | Medium | Callbacks and commands are persisted without sequence validation |
| No deployment artifacts | Medium | No Dockerfile/systemd/nginx config in repo |
| No automated tests found | Medium | No test suite detected |

### FIS14-Specific Notes

The local FIS14 context spec marks `location`, `domain`, `timestamp`, `bap_id`, `transaction_id`, `message_id`, `version`, `action`, `bap_uri`, and `ttl` as mandatory. The app validates most envelope fields, but:

- `location` is optional in `app/schemas/ondc.py`.
- `message` is not validated against action-specific mutual fund schemas.
- Current version is fixed at `2.0.0`; local specs also include a `FIS14_2.1.0` changelog, so your target PreProd version must be confirmed during onboarding.

## Required Before PreProd

1. Implement and test outbound ONDC Authorization header generation.
2. Implement and test inbound Authorization header verification.
3. Configure real `SUBSCRIBER_ID=ondcapi.walkingtree.tech`, `BAP_ID=ondcapi.walkingtree.tech`, `UNIQUE_KEY_ID`, key paths, and PreProd registry URL.
4. Wire registry lookup into callback verification.
5. Implement actual BPP/Gateway dispatch for `search`, `select`, `init`, `confirm`, `status`, `update`, `cancel`, `track`, and `support`.
6. Replace filesystem storage with database-backed transaction persistence for production.
7. Add FIS14 action-specific schema validation.
8. Enforce timestamp freshness, TTL expiry, duplicate message protection, and transaction lifecycle order.
9. Add tests and deployment hardening.

## DEPLOY NOW

**DEPLOY NOW = NO**

Exact missing items before deployment:

- Real `.env` values for your account.
- Signing implementation.
- Verification implementation.
- Registry verification wiring.
- BPP dispatch implementation.
- Durable transaction store.
- Production deployment configs and tests.
