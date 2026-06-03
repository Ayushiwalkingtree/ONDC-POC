# Unused Code Report

Audit date: 2026-06-03  
Scope: static inspection only. No code was deleted.

## Summary

No unused imports were detected by the local static scan. Several modules are intentionally retained as compatibility or future production boundaries, but are not currently used by the live FastAPI route path.

## Safe To Delete

These look safe to delete only if the repository does not need historical/generated artifacts. Deletion was not performed.

| Item | Reason |
|---|---|
| `app/**/__pycache__/` | Python bytecode cache; not source code |
| Empty `protocol-specs/` directory | Directory exists but contains no files in this checkout |
| Empty `buyer-np-reference/` directory | Directory exists but contains no files in this checkout |

## Review Required

Do not delete these without confirming intended usage.

| Item | Finding | Reason to review |
|---|---|---|
| `app/services/ondc_service.py` | Compatibility facade over `BuyerNPService`; not used by current routers | It provides old `handle_*` methods and mock callback builders; docs say new code should use `buyer_np_service` directly |
| `app/services/mock_payloads.py` | Used only by `ondc_service.py` | Useful for local callback generation, but not on live route path |
| `app/models/transaction_store.py` | Compatibility shim over repository | `CLEANUP_PLAN.md` says to remove after external imports are migrated |
| `app/schemas/fis14.py::FIS14ProtocolEvent` | No references outside its definition found | May be intended for future docs/tests |
| `app/schemas/ondc.py::ONDCRequest` | Alias not referenced elsewhere | Compatibility alias; verify external imports before removal |
| `app/schemas/ondc.py::ONDCError` | No route or exception handler uses it | Could be useful for future NACK/error responses |
| `app/schemas/ondc.py::TransactionEvent` and `TransactionRecord` | Separate from active `TransactionEventRecord` | Duplicate concept with `app/schemas/transaction.py` |
| `BuyerNPService.signer` | Injected but not used | Production signing boundary is present but not wired into command handling |
| `BuyerNPService.verifier` | Injected but not used | Production verification boundary is present but not wired into callback handling |
| `TransactionRepository.get_by_message_id()` | Implemented but not used by services | Could support duplicate/replay checks later |
| Legacy Postman artifacts | Older non-Buyer NP Postman files were detected previously | Verify they are removed or replaced by Buyer NP artifacts |

## Duplicate Logic / Overlap

| Area | Files | Notes |
|---|---|---|
| Transaction event schemas | `app/schemas/ondc.py`, `app/schemas/transaction.py` | `TransactionEvent`/`TransactionRecord` overlap with `TransactionEventRecord`; active repository uses `TransactionEventRecord` |
| Transaction storage abstraction | `app/models/transaction_store.py`, `app/services/file_storage_service.py`, `app/repositories/*` | Model store is a compatibility shim; filesystem repository is the active pattern |
| Service facade | `app/services/ondc_service.py`, `app/services/buyer_np_service.py` | `ONDCService` delegates to `BuyerNPService`; route path uses `buyer_np_service` directly |
| Mock callbacks | `app/services/mock_payloads.py`, `app/schemas/examples.py` | `examples.py` loads real local FIS14 examples; `mock_payloads.py` creates synthetic callbacks |

## Dead Code Candidates

| Candidate | Confidence | Recommendation |
|---|---|---|
| `app/models/transaction_store.py` | Medium | Keep until external imports are audited; then remove with tests |
| `app/services/ondc_service.py` | Medium | Keep if local dev callback generation matters; otherwise migrate any users to `buyer_np_service` |
| `app/services/mock_payloads.py` | Medium | Move behind a dev-only module if retained |
| `app/schemas/ondc.py::ONDCError` | Medium | Use for structured NACK/errors or remove |
| `app/schemas/fis14.py::FIS14ProtocolEvent` | Medium | Use in docs/tests or remove |
| Empty submodule directories | High | Remove or initialize submodules deliberately |

## Stub / Placeholder Code

| File | Placeholder |
|---|---|
| `app/services/signing_service.py` | `build_authorization_header()` raises `NotImplementedError` |
| `app/services/verification_service.py` | `verify_headers()` raises `NotImplementedError` when auth is required |
| `app/services/registry_service.py` | Generic lookup exists, but docstring says environment-specific mapping must be wired before UAT |

## Import Scan Result

No obvious unused imports were reported by the static scan across `app/**/*.py` and `scripts/**/*.py`.

