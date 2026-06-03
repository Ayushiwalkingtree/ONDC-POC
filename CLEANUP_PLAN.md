# Cleanup Plan

## Completed Safe Cleanup

- Removed generated Python bytecode directories under `app/**/__pycache__/`.
- Removed stale legacy wording from the FastAPI application metadata.
- Removed unused route imports by rewriting the route modules around Buyer NP responsibilities.

## Kept Intentionally

- `fis-specs/` remains as the local FIS14 reference source.
- `protocol-specs/` remains as the local ONDC protocol reference source.
- `buyer-np-reference/` remains as a reference folder and was not modified.
- `postman/` remains available for manual local testing.
- `app/services/mock_payloads.py` remains available for local development payload generation.

## Next Cleanup After UAT Design

1. Replace `FileStorageService` with a database-backed repository for production.
2. Move local mock callback builders behind a dev-only module or feature flag.
3. Regenerate the Postman collection to include new Buyer NP routes.
4. Add automated tests for validation failures, duplicate `message_id`, and all new APIs.
5. Add production logging, trace IDs, and audit retention policy.
6. Remove `app/models/transaction_store.py` after all external imports are confirmed migrated.

## Not Safe To Remove Yet

- `app/services/mock_payloads.py`: still useful for local development.
- `app/models/transaction_store.py`: retained as a compatibility shim.
- Reference spec folders and existing documentation.

