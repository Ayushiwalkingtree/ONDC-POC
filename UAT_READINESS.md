# UAT Readiness

## Current Status

The FastAPI application exposes Buyer NP command and callback receiver APIs for the ONDC FIS14 mutual fund lifecycle. Local validation, sample payloads, Postman artifacts, and curl examples are available for dry runs.

## Required Before UAT

| Requirement | Status | Notes |
|---|---|---|
| Subscriber ID required | Required | Obtain Buyer NP/BAP subscriber ID through ONDC onboarding. Configure `SUBSCRIBER_ID` and `BAP_ID`. |
| Registry required | Required | Configure `ONDC_REGISTRY_URL` for staging/UAT registry lookup. |
| Public key required | Required | Register the signing public key in the ONDC registry with the correct `unique_key_id`. |
| Private key required | Required | Store the Ed25519 private key securely and configure `SIGNING_PRIVATE_KEY` or a production secret manager adapter. |
| Signing required | Required | Implement `SigningService.build_authorization_header` using ONDC canonical signing requirements. No fake crypto is present. |
| Verification required | Required | Implement `VerificationService.verify_headers`; enable `REQUIRE_ONDC_AUTH=true` for inbound callbacks. |

## UAT Configuration Checklist

- `APP_ENV=uat`
- `BASE_URL` points to the publicly reachable Buyer NP callback URL.
- `BAP_ID` matches the ONDC registered subscriber ID.
- `BAP_URI` matches the registered Buyer NP endpoint.
- `BAP_CALLBACK_URI` is reachable by BPPs.
- `SUBSCRIBER_ID` is set.
- `UNIQUE_KEY_ID` matches the registry key.
- `ONDC_REGISTRY_URL` points to the UAT/staging registry.
- `SIGNING_PRIVATE_KEY` or equivalent secure key provider is configured.
- `REQUIRE_ONDC_AUTH=true` once verification is implemented.

## UAT Entry Criteria

1. All Postman requests return ACK locally with unique `message_id` values.
2. Duplicate `message_id` returns HTTP `409`.
3. Invalid `domain`, `ttl`, missing `transaction_id`, missing `message_id`, or mismatched `action` is rejected.
4. Public URL and TLS certificate are available for callback receiving.
5. Registry lookup succeeds for target BPP and Buyer NP subscriber identities.
6. Signing and verification pass ONDC Workbench or equivalent protocol checks.

## UAT Exit Criteria

1. `search -> on_search` succeeds with a real BPP.
2. `select -> on_select` succeeds for supported MF product type.
3. `init -> on_init` returns valid draft order, terms, and payment information.
4. `confirm -> on_confirm` returns accepted or rejected order with valid state.
5. `status -> on_status` works for order polling.
6. `on_update` handles payment and fulfillment updates.
7. Error/NACK behavior is validated for invalid protocol requests.

