# Workbench Integration Report

Audit/update date: 2026-06-04

## Objective

Make the ONDC FIS14 Buyer NP compatible with ONDC Workbench Scenario Testing without requiring ONDC Registry lookup, while preserving the production registry-based dispatch path.

Workbench seller base URL:

```text
https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller
```

## Files Modified

| File | Change |
|---|---|
| `.env` | Added `WORKBENCH_MODE=true` and `WORKBENCH_BASE_URL` for local Workbench execution |
| `.env.example` | Documented Workbench configuration |
| `app/core/config.py` | Added `workbench_mode` and `workbench_base_url` settings |
| `app/services/buyer_np_service.py` | Added Workbench dispatch branch that skips registry lookup |
| `app/services/outbound_http_client.py` | Added detailed outbound request/response logging with Authorization redaction |
| `app/callbacks/ondc_callbacks.py` | Added root callback aliases for Workbench callbacks |
| `app/api/router.py` | Registered the Workbench callback alias router |
| `tests/test_real_ondc_integration.py` | Added tests for Workbench registry-skip behavior and callback alias registration |

## Exact Behavior Change

Production/default behavior is preserved:

```text
target_subscriber_id
-> registry.lookup_subscriber()
-> subscriber_url
-> /<action>
-> signed outbound HTTP call
```

Workbench behavior when `WORKBENCH_MODE=true`:

```text
target_subscriber_id
-> skip registry lookup
-> WORKBENCH_BASE_URL + "/" + action
-> signed outbound HTTP call
```

Request signing remains unchanged. The existing `SigningService.build_authorization_header()` still signs the exact outbound body using the current Ed25519 Authorization header implementation.

Callback signature validation remains unchanged. The existing `VerificationService.verify_headers()` is still used for callbacks. The new callback routes are aliases only; they call the same handler functions as the `/ondc/*` callbacks.

## Configuration

```env
WORKBENCH_MODE=true
WORKBENCH_BASE_URL=https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller
```

To return to production registry dispatch:

```env
WORKBENCH_MODE=false
ONDC_REGISTRY_URL=<real ONDC registry lookup URL>
```

## Covered Command Actions

All command actions use the centralized dispatch path and are covered by Workbench mode:

```text
search
select
init
confirm
status
update
cancel
track
support
```

Expected target URLs:

| Action | Workbench target |
|---|---|
| `search` | `https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/search` |
| `select` | `https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/select` |
| `init` | `https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/init` |
| `confirm` | `https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/confirm` |
| `status` | `https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/status` |
| `update` | `https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/update` |
| `cancel` | `https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/cancel` |
| `track` | `https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/track` |
| `support` | `https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/support` |

## Callback Compatibility

Existing callback routes remain:

```text
/ondc/on_search
/ondc/on_select
/ondc/on_init
/ondc/on_confirm
```

Workbench aliases added:

```text
/on_search
/on_select
/on_init
/on_confirm
```

The alias routes use the same callback handler and verification logic as the existing `/ondc/*` routes.

## Logging Added

The command path now logs:

```text
WORKBENCH MODE ENABLED
ACTION
TARGET URL
OUTBOUND REQUEST
OUTBOUND RESPONSE
```

The outbound HTTP client logs request URL, body size, redacted headers, response status, response headers, and parsed response body.

## Testing Steps Run

```text
.\\.venv\\Scripts\\python.exe -m pytest -q
```

Result:

```text
6 passed in 1.53s
```

Additional runtime verification:

```text
.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8015
POST http://127.0.0.1:8015/ondc/search
```

Expected:

```text
No 503 "ONDC_REGISTRY_URL is not configured" error.
Logs show WORKBENCH MODE ENABLED.
Target URL is https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/search.
```

Observed local runtime result:

```text
POST /ondc/search reached the Workbench seller endpoint.
Registry lookup was skipped.
No 503 registry configuration error occurred.
Workbench returned HTTP 428 because no active scenario session was found for BAP URL https://ondcapi.walkingtree.tech/ondc.
The local API returned HTTP 502 because the outbound Workbench response was >= 400.
```

## Sample Curl Commands

Health:

```bash
curl -s http://127.0.0.1:8015/health
```

Search command:

```bash
curl -s -X POST http://127.0.0.1:8015/ondc/search \
  -H "Content-Type: application/json" \
  -d @postman/payloads/search.json
```

Workbench callback alias:

```bash
curl -s -X POST http://127.0.0.1:8015/on_search \
  -H "Content-Type: application/json" \
  -H "Authorization: Signature keyId=\"...\",algorithm=\"ed25519\",created=\"...\",expires=\"...\",headers=\"(created) (expires) digest\",signature=\"...\"" \
  -d @postman/payloads/on_search.json
```

Existing callback route:

```bash
curl -s -X POST http://127.0.0.1:8015/ondc/on_search \
  -H "Content-Type: application/json" \
  -H "Authorization: Signature keyId=\"...\",algorithm=\"ed25519\",created=\"...\",expires=\"...\",headers=\"(created) (expires) digest\",signature=\"...\"" \
  -d @postman/payloads/on_search.json
```

## Expected Workbench Flow

1. Client posts a Buyer NP command to `/ondc/search`.
2. App validates the FIS14 envelope.
3. App signs the outbound request exactly as before.
4. Because `WORKBENCH_MODE=true`, app skips registry lookup.
5. App dispatches to `WORKBENCH_BASE_URL/search`.
6. Workbench seller processes the request.
7. Workbench sends callbacks to either `/on_search` or `/ondc/on_search`.
8. App verifies callback Authorization exactly as before.
9. App persists the callback event and returns ONDC ACK.

## Production Safety

Registry support was not removed. With `WORKBENCH_MODE=false`, the command flow continues to use `registry.lookup_subscriber()` and `subscriber_url` resolution.
