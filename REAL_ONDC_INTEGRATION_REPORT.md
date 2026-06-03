# Real ONDC Integration Report

Audit date: 2026-06-03

Scope: Buyer NP command dispatch, registry discovery, outbound signing, response persistence, and callback verification integration.

## Summary

The Buyer NP command flow is no longer ACK-only. `BuyerNPService.handle_command()` now validates the ONDC/FIS14 request, signs the exact outbound JSON bytes, looks up the target participant in the registry, resolves the destination URI from the registry response, sends the signed Beckn/ONDC payload using `httpx`, stores the outbound request and response, and then returns ACK.

Inbound callback routes now pass raw headers and body bytes into `VerificationService.verify_headers()` before callback persistence.

## Implemented Flow

```text
POST /ondc/search
  -> app.routes.ondc.search()
  -> app.services.buyer_np_service.BuyerNPService.handle_command()
  -> ProtocolValidationService.validate_command()
  -> SigningService.build_authorization_header()
  -> RegistryService.lookup_subscriber()
  -> OutboundHTTPClient.post()
  -> FileStorageService.save_event(command)
  -> FileStorageService.save_event(response)
  -> ACK
```

The same command flow is used for:

- `search`
- `select`
- `init`
- `confirm`
- `status`
- `cancel`
- `update`
- `support`
- `track`

## Files Changed

| File | Change |
|---|---|
| `app/services/buyer_np_service.py` | Added signed outbound dispatch orchestration, registry lookup, response storage, and callback verification call |
| `app/services/outbound_http_client.py` | Added `httpx` outbound client |
| `app/services/registry_service.py` | Added `subscriber_url` extraction and TODO registry URL guard |
| `app/services/verification_service.py` | Uses registry public key lookup only when a real registry URL is configured |
| `app/callbacks/ondc_callbacks.py` | Passed FastAPI raw request headers/body into callback verification |
| `app/services/file_storage_service.py` | Added full command folders and direction-specific filenames |
| `app/schemas/transaction.py` | Added `response` transaction direction |
| `app/schemas/ondc.py` | Aligned compatibility transaction schema with `response` direction |
| `tests/test_real_ondc_integration.py` | Added signed search dispatch plus verified callback integration test |

## Runtime Evidence

| Capability | Evidence |
|---|---|
| Signing called before outbound request | `app/services/buyer_np_service.py::BuyerNPService.handle_command()` calls `self.signer.build_authorization_header(body)` |
| Registry lookup before outbound request | `app/services/buyer_np_service.py::BuyerNPService.handle_command()` calls `self.registry.lookup_subscriber(target_subscriber_id)` before dispatch |
| Destination URL resolved from registry | `app/services/buyer_np_service.py::BuyerNPService._action_url()` appends the ONDC action to `RegistrySubscriber.subscriber_url` |
| Outbound HTTP request sent | `app/services/outbound_http_client.py::OutboundHTTPClient.post()` calls `httpx.AsyncClient.post()` |
| Request persisted | `app/services/buyer_np_service.py::BuyerNPService._save_event(... direction="command")` |
| Response persisted | `app/services/buyer_np_service.py::BuyerNPService._save_response_event()` |
| Callback verified before persistence | `app/services/buyer_np_service.py::BuyerNPService.handle_callback()` calls `self.verifier.verify_headers(headers, raw_body)` before saving |
| Callback raw body/headers available | `app/callbacks/ondc_callbacks.py` route functions pass `http_request.headers` and `await http_request.body()` |

## Storage Layout

Outbound requests and responses are stored under the command action folder:

```text
storage/search/
storage/select/
storage/init/
storage/confirm/
storage/status/
storage/cancel/
storage/update/
storage/support/
storage/track/
```

Callbacks are stored under:

```text
storage/callbacks/<callback_action>/
```

Filenames include transaction id, message id, and direction to allow separate command, response, and callback records.

## Current Configuration Blockers

The code path is implemented, but this checkout is not fully configured for live PreProd dispatch:

| Item | Current status | Impact |
|---|---|---|
| `ONDC_REGISTRY_URL` | `TODO_ONDC_REGISTRY_URL` in `.env` and `.env.example` | Real registry lookup will fail until set |
| Target participant | Uses `context.bpp_id` or configured `BPP_ID` fallback | Real search needs a valid target subscriber/gateway strategy |
| Registry response URI | Must return `subscriber_url` or compatible URI field | Dispatch cannot proceed without destination URI |
| Callback public key lookup | Uses registry when configured, else configured public key fallback | PreProd should use real registry public key lookup |

## Tests

Validation run:

```text
.venv\Scripts\python.exe -m compileall app tests
.venv\Scripts\python.exe -m pytest -q
```

Result:

```text
4 passed
```

Integration test:

```text
tests/test_real_ondc_integration.py::test_search_signed_outbound_request_and_verified_callback
```

This test proves:

- search command is signed
- registry lookup is performed
- mocked BPP receives a signed outbound request
- mocked BPP ACK response is stored
- signed `on_search` callback is verified before storage

## Final

Can send signed ONDC requests = YES

Can receive verified callbacks = YES

PreProd Ready = NO

Reason: implementation is present, but current runtime configuration still has `ONDC_REGISTRY_URL=TODO_ONDC_REGISTRY_URL` and no verified real PreProd target/gateway destination configured.
