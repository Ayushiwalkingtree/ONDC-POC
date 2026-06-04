# Workbench Payload Audit

Audit date: 2026-06-04

## Issue

ONDC Workbench received outbound `search` payloads with stale sample context values:

```json
{
  "bap_id": "api.buyerapp.com",
  "bap_uri": "https://api.buyerapp.com/ondc",
  "bpp_id": null,
  "bpp_uri": null
}
```

Workbench then returned validation/session errors:

```text
context/bpp_id should not be empty
context/bpp_uri should not be empty
no session or active flow found for https://api.buyerapp.com/ondc
```

## Source of Incorrect Values

The placeholder BAP context originates from local ONDC sample payloads loaded at app startup:

| Source | Finding |
|---|---|
| `fis-specs/api/components/examples/mutual-funds/*` | ONDC example files include `api.buyerapp.com` and `https://api.buyerapp.com/ondc` |
| `app/schemas/examples.py` | Loads those examples into Swagger/Postman request examples |
| `postman/payloads/*.json` | Contains generated static payloads with `api.buyerapp.com` and `api.bpp.example.com` |
| `app/services/buyer_np_service.py` before fix | Signed and dispatched the incoming request context as-is |

The runtime issue was not the Workbench URL selection. Workbench mode already selected:

```text
https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/<action>
```

The issue was that the outbound signed JSON body still contained stale sample `context` values.

## Files Changed

| File | Change |
|---|---|
| `app/services/buyer_np_service.py` | Normalizes command outbound context before signing and dispatch |
| `tests/test_real_ondc_integration.py` | Verifies outbound body uses settings-derived BAP values and Workbench BPP values |
| `WORKBENCH_PAYLOAD_AUDIT.md` | Documents source, fix, and validation |

## Runtime Context Normalization

Before signing, all command payloads now force:

```text
context.bap_id = settings.bap_id
context.bap_uri = settings.bap_uri or settings.bap_callback_uri
```

In `WORKBENCH_MODE=true`, the app also replaces missing or placeholder BPP context:

```text
context.bpp_id = "workbench.ondc.tech"
context.bpp_uri = settings.workbench_base_url
```

Placeholder values treated as missing:

```text
api.bpp.example.com
bpp.example.com
https://api.bpp.example.com/ondc
https://bpp.example.com/ondc
```

## Before Payload

```json
{
  "context": {
    "domain": "ONDC:FIS14",
    "bap_id": "api.buyerapp.com",
    "bap_uri": "https://api.buyerapp.com/ondc",
    "bpp_id": null,
    "bpp_uri": null,
    "version": "2.0.0",
    "action": "search"
  }
}
```

## After Payload

With current `.env`:

```env
BAP_ID=ondcapi.walkingtree.tech
BAP_URI=https://ondcapi.walkingtree.tech/ondc
BAP_CALLBACK_URI=https://ondcapi.walkingtree.tech/ondc
WORKBENCH_MODE=true
WORKBENCH_BASE_URL=https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller
```

Outbound context becomes:

```json
{
  "context": {
    "domain": "ONDC:FIS14",
    "bap_id": "ondcapi.walkingtree.tech",
    "bap_uri": "https://ondcapi.walkingtree.tech/ondc",
    "bpp_id": "workbench.ondc.tech",
    "bpp_uri": "https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller",
    "version": "2.0.0",
    "action": "search"
  }
}
```

## Logging Added

The final context is logged before signing:

```python
logger.info(
    "OUTBOUND CONTEXT | action=%s context=%s",
    action,
    request.context.model_dump(),
)
```

This log appears before body serialization and Authorization header generation, so it reflects the exact context being signed and sent.

## Validation Steps

Run tests:

```bash
python -m pytest -q
```

Observed result:

```text
6 passed in 3.03s
```

Manual Workbench check:

```bash
find storage -type f -name "*.json" -delete
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Then submit a fresh `search` request and confirm logs show:

```text
OUTBOUND CONTEXT | action=search context={... 'bap_id': 'ondcapi.walkingtree.tech', 'bap_uri': 'https://ondcapi.walkingtree.tech/ondc', 'bpp_id': 'workbench.ondc.tech', 'bpp_uri': 'https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller' ...}
WORKBENCH MODE ENABLED | action=search ... target_url=https://workbench.ondc.tech/api-service/ONDC:FIS14/2.1.0/seller/search
```

## Notes

The static Swagger and Postman examples may still display upstream sample values. Runtime command dispatch now corrects those values before signing and sending. If static example files also need to show production BAP values, regenerate Postman examples from settings or template them with environment variables.

