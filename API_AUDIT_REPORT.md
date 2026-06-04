# API Audit Report

Audit date: 2026-06-04  
Application: ONDC MF Buyer NP  
Framework: FastAPI with Uvicorn  
Local test base URL: `http://127.0.0.1:8015`

## Scope

This report was generated from source review, runtime OpenAPI discovery, local health checks, and endpoint calls using valid FIS14 sample payloads from `app.schemas.examples`.

Business logic was not modified.

## Runtime Discovery

Discovered routes from `/openapi.json`:

| Method | Endpoint | Purpose | Request payload | Response payload | Dependencies |
|---|---|---|---|---|---|
| GET | `/health` | Service health | None | Service metadata | Settings |
| GET | `/health/keys` | Key configuration health | None | Key-loaded booleans | Settings, key env vars |
| POST | `/ondc/search` | Buyer NP search command | `FIS14CommandRequest` | ONDC ACK | Signing, registry lookup, outbound BPP HTTP |
| POST | `/ondc/select` | Buyer NP select command | `FIS14CommandRequest` | ONDC ACK | Signing, registry lookup, outbound BPP HTTP |
| POST | `/ondc/init` | Buyer NP init command | `FIS14CommandRequest` | ONDC ACK | Signing, registry lookup, outbound BPP HTTP |
| POST | `/ondc/confirm` | Buyer NP confirm command | `FIS14CommandRequest` | ONDC ACK | Signing, registry lookup, outbound BPP HTTP |
| POST | `/ondc/status` | Buyer NP status command | `FIS14CommandRequest` | ONDC ACK | Signing, registry lookup, outbound BPP HTTP |
| POST | `/ondc/update` | Buyer NP update command | `FIS14CommandRequest` | ONDC ACK | Signing, registry lookup, outbound BPP HTTP |
| POST | `/ondc/cancel` | Buyer NP cancel command | `FIS14CommandRequest` | ONDC ACK | Signing, registry lookup, outbound BPP HTTP |
| POST | `/ondc/track` | Buyer NP track command | `FIS14CommandRequest` | ONDC ACK | Signing, registry lookup, outbound BPP HTTP |
| POST | `/ondc/support` | Buyer NP support command | `FIS14CommandRequest` | ONDC ACK | Signing, registry lookup, outbound BPP HTTP |
| POST | `/ondc/on_search` | Receive search callback | `FIS14CallbackRequest` | ONDC ACK | Authorization verification, filesystem repository |
| POST | `/ondc/on_select` | Receive select callback | `FIS14CallbackRequest` | ONDC ACK | Authorization verification, filesystem repository |
| POST | `/ondc/on_init` | Receive init callback | `FIS14CallbackRequest` | ONDC ACK | Authorization verification, filesystem repository |
| POST | `/ondc/on_confirm` | Receive confirm callback | `FIS14CallbackRequest` | ONDC ACK | Authorization verification, filesystem repository |
| POST | `/ondc/on_status` | Receive status callback | `FIS14CallbackRequest` | ONDC ACK | Authorization verification, filesystem repository |
| POST | `/ondc/on_update` | Receive update callback | `FIS14CallbackRequest` | ONDC ACK | Authorization verification, filesystem repository |
| POST | `/ondc/on_cancel` | Receive cancel callback | `FIS14CallbackRequest` | ONDC ACK | Authorization verification, filesystem repository |
| POST | `/ondc/on_track` | Receive track callback | `FIS14CallbackRequest` | ONDC ACK | Authorization verification, filesystem repository |
| POST | `/ondc/on_support` | Receive support callback | `FIS14CallbackRequest` | ONDC ACK | Authorization verification, filesystem repository |
| GET | `/ondc/transactions` | List local protocol events | None | `{count, records}` | Filesystem repository |
| GET | `/ondc/transactions/{transaction_id}` | Fetch events by transaction | Path parameter | `{transaction_id, records}` or 404 | Filesystem repository |

## Missing API Coverage

| Expected endpoint | Status | Finding |
|---|---|---|
| `/ondc/rating` | FAIL | Not registered; returns 404 |
| `/ondc/on_rating` | FAIL | Not registered; returns 404 |
| `/search`, `/select`, `/init`, `/confirm`, `/status`, `/track`, `/cancel`, `/update`, `/support`, `/rating` | FAIL | Not registered at root; implementation uses `/ondc/*` prefix |
| `/on_search`, `/on_select`, `/on_init`, `/on_confirm`, `/on_status`, `/on_track`, `/on_cancel`, `/on_update`, `/on_support`, `/on_rating` | FAIL | Not registered at root; implementation uses `/ondc/*` prefix |

## Payload Contract

All ONDC command and callback endpoints use the same envelope:

```json
{
  "context": {
    "domain": "ONDC:FIS14",
    "location": {},
    "timestamp": "RFC3339 timestamp",
    "bap_id": "subscriber id",
    "bap_uri": "https://.../ondc",
    "bpp_id": "optional BPP subscriber id",
    "bpp_uri": "optional BPP URI",
    "transaction_id": "string",
    "message_id": "string",
    "version": "2.0.0",
    "ttl": "PT10M",
    "action": "search|select|init|confirm|status|update|cancel|track|support|on_*"
  },
  "message": {}
}
```

ACK response:

```json
{
  "message": {
    "ack": {
      "status": "ACK"
    }
  }
}
```

## Validation Rules

Implemented validation:

| Area | Rule |
|---|---|
| Envelope | Extra fields forbidden at `context` and top-level request |
| Domain | Must equal `ONDC:FIS14` |
| Version | Must equal `2.0.0` |
| Timestamp | Must parse as RFC3339/ISO-8601 |
| TTL | Must match `PTnH`, `PTnM`, or `PTnS` format |
| Required strings | `transaction_id`, `message_id`, `bap_id`, `bap_uri`, `action` must be non-empty |
| Action | Must be one of registered command/callback action names |
| Endpoint/action match | `context.action` must match the endpoint action |
| Callback auth | Missing Authorization header is rejected when `REQUIRE_ONDC_AUTH=true` |

Validation gaps:

| Gap | Impact |
|---|---|
| `message` is a generic dict | Deep FIS14 action-specific schema validation is not enforced |
| Context freshness is not enforced | Old `context.timestamp` and `ttl` may pass if syntactically valid |
| `bap_uri`/`bpp_uri` URL shape is not validated | Non-URL strings could pass if non-empty |
| `context.bap_id` is not compared with configured `SUBSCRIBER_ID`/`BAP_ID` | Spoofed sender context could pass envelope validation |
| Callback sender is not checked against expected transaction/BPP | Valid signature alone may not bind callback to the expected counterparty |

## Local Test Results

Existing unit/integration tests:

```text
4 passed in 1.17s
```

Endpoint calls:

| Method | Endpoint | Status | HTTP | Time ms | Issue | Recommendation |
|---|---|---:|---:|---:|---|---|
| GET | `/health` | PASS | 200 | 32.33 | None | Keep |
| GET | `/health/keys` | PASS | 200 | 4.50 | None | Avoid exposing key-loaded metadata publicly in production if not protected |
| GET | `/ondc/transactions` | PASS | 200 | 5.11 | Debug API exposed | Protect or disable outside non-prod |
| POST | `/ondc/search` | FAIL | 503 | 9.88 | `ONDC_REGISTRY_URL is not configured` | Configure real PreProd registry lookup URL |
| POST | `/ondc/select` | FAIL | 503 | 4.18 | `ONDC_REGISTRY_URL is not configured` | Configure real PreProd registry lookup URL |
| POST | `/ondc/init` | FAIL | 503 | 4.25 | `ONDC_REGISTRY_URL is not configured` | Configure real PreProd registry lookup URL |
| POST | `/ondc/confirm` | FAIL | 503 | 6.66 | `ONDC_REGISTRY_URL is not configured` | Configure real PreProd registry lookup URL |
| POST | `/ondc/status` | FAIL | 503 | 4.30 | `ONDC_REGISTRY_URL is not configured` | Configure real PreProd registry lookup URL |
| POST | `/ondc/update` | FAIL | 503 | 4.14 | `ONDC_REGISTRY_URL is not configured` | Configure real PreProd registry lookup URL |
| POST | `/ondc/cancel` | FAIL | 503 | 7.28 | `ONDC_REGISTRY_URL is not configured` | Configure real PreProd registry lookup URL |
| POST | `/ondc/track` | FAIL | 503 | 4.26 | `ONDC_REGISTRY_URL is not configured` | Configure real PreProd registry lookup URL |
| POST | `/ondc/support` | FAIL | 503 | 4.91 | `ONDC_REGISTRY_URL is not configured` | Configure real PreProd registry lookup URL |
| POST | `/ondc/on_search` | PASS | 200 | 10.16 | None with valid signature | Add transaction/BPP correlation checks |
| POST | `/ondc/on_select` | PASS | 200 | 5.37 | None with valid signature | Add transaction/BPP correlation checks |
| POST | `/ondc/on_init` | PASS | 200 | 8.91 | None with valid signature | Add transaction/BPP correlation checks |
| POST | `/ondc/on_confirm` | PASS | 200 | 5.53 | None with valid signature | Add transaction/BPP correlation checks |
| POST | `/ondc/on_status` | PASS | 200 | 7.88 | None with valid signature | Add transaction/BPP correlation checks |
| POST | `/ondc/on_update` | PASS | 200 | 6.63 | None with valid signature | Add transaction/BPP correlation checks |
| POST | `/ondc/on_cancel` | PASS | 200 | 6.71 | None with valid signature | Add transaction/BPP correlation checks |
| POST | `/ondc/on_track` | PASS | 200 | 5.01 | None with valid signature | Add transaction/BPP correlation checks |
| POST | `/ondc/on_support` | PASS | 200 | 4.75 | None with valid signature | Add transaction/BPP correlation checks |
| GET | `/ondc/transactions/{transaction_id}` | PASS | 200 | n/a | Works for stored callback transaction | Protect or disable outside non-prod |
| POST | `/ondc/rating` | FAIL | 404 | 2.68 | Missing endpoint | Add only if required by target ONDC/FIS14 flow |
| POST | `/ondc/on_rating` | FAIL | 404 | 2.10 | Missing endpoint | Add only if required by target ONDC/FIS14 flow |

Negative validation checks:

| Check | Result |
|---|---|
| Unsigned callback with `REQUIRE_ONDC_AUTH=true` | PASS: rejected with 401 |
| Invalid domain/timestamp/version/ttl/empty strings | PASS: rejected with 422 |

