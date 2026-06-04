# Message ID Audit Report

Audit date: 2026-06-04

## Issue

Swagger/OpenAPI examples and generated sample payloads previously carried fixed `context.message_id` values copied from the FIS14 example specs. Re-running the same request from Swagger "Try it out" reused the same ID and triggered the Buyer NP duplicate-message guard with HTTP 409.

## Locations of Fixed Message IDs

| Location | Finding | Resolution |
|---|---|---|
| `fis-specs/api/components/examples/mutual-funds/**` | Upstream ONDC/FIS14 spec examples contain static `message_id` values. | Left unchanged as source specs. Runtime examples are normalized when loaded. |
| `app/schemas/examples.py` | `_unique_message_id()` appended static suffixes to fixed spec IDs. | Replaced callback IDs with generated UUID4 values and removed `message_id` from command examples. |
| `postman/payloads/*.json` | Generated command and callback sample payloads contained fixed IDs. | Regenerated artifacts. Command payloads now omit `message_id`; callbacks contain generated UUIDs. |
| `postman/ONDC_MF_BUYER_NP_UAT.postman_collection.json` | Raw request bodies contained fixed IDs from generated examples. | Regenerated from normalized examples. |
| `postman/ONDC_MF_BUYER_NP_UAT.postman_environment.json` | `message_id` environment variable was fixed. | Changed to Postman dynamic value `{{$guid}}`. |
| `tests/test_real_ondc_integration.py` | Test fixtures used fixed IDs. | Kept explicit IDs where duplicate behavior is tested; added missing-ID generation coverage. |

## Files Changed

| File | Change |
|---|---|
| `app/schemas/ondc.py` | Added `generate_message_id()` helper, kept `new_message_id()` as an alias, and made command contexts able to omit `message_id`. |
| `app/services/buyer_np_service.py` | Generates UUID4 for missing/blank command `message_id`, logs generated and incoming message IDs, then performs existing validation, duplicate checks, signing, and dispatch. |
| `app/services/protocol_validation.py` | Keeps callback validation strict by requiring callback `context.message_id`. |
| `app/schemas/examples.py` | Removes `message_id` from command OpenAPI examples; generates UUID4 IDs for callback examples. |
| `scripts/generate_postman.py` | Uses Postman `{{$guid}}` for environment `message_id`. |
| `scripts/validate_uat_artifacts.py` | Ignores callback `message_id` while comparing generated artifacts because callback example IDs rotate. |
| `postman/**` | Regenerated generated payload, collection, and curl artifacts from normalized examples. |
| `tests/test_real_ondc_integration.py` | Added tests for generated command IDs and retained duplicate 409 behavior. |

## Before Behavior

```json
{
  "context": {
    "action": "search",
    "message_id": "bb579fb8-cb82-4824-be12-fcbc405b6608-search"
  }
}
```

Repeated Swagger execution reused the same value and returned:

```text
409 duplicate message_id
```

## After Behavior

Command examples omit `message_id`:

```json
{
  "context": {
    "action": "search"
  }
}
```

Before processing a command, the service generates a UUID4 if `context.message_id` is missing or blank:

```text
Generated message_id | action=search txn=<transaction_id> msg=<uuid4>
Incoming request | action=search txn=<transaction_id> msg=<uuid4>
```

Explicit duplicate `message_id` values are still rejected with HTTP 409.

## Validation Steps

1. Regenerated generated artifacts:

```powershell
$env:PYTHONPATH=(Get-Location).Path
.\.venv\Scripts\python.exe scripts\generate_postman.py
```

2. Verified command sample payloads no longer contain `message_id`:

```powershell
rg -n '"message_id"' postman\payloads\search.json postman\payloads\select.json postman\payloads\init.json postman\payloads\confirm.json postman\payloads\status.json postman\payloads\update.json postman\payloads\cancel.json postman\payloads\track.json postman\payloads\support.json
```

Expected result: no matches.

3. Ran local tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Result:

```text
8 passed
```

4. Validated generated UAT artifacts:

```powershell
.\.venv\Scripts\python.exe scripts\validate_uat_artifacts.py
```

Result:

```text
uat_artifacts_ok
validated_endpoints=18
validated_env_keys=7
```
