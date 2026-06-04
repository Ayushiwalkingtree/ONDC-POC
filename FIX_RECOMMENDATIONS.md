# Fix Recommendations

Audit date: 2026-06-04

## P0 - Required Before ONDC Pre-Prod

1. Configure the real registry URL.

```env
ONDC_REGISTRY_URL=<real ONDC pre-prod registry lookup URL>
```

Why: every command endpoint currently fails with `503 ONDC_REGISTRY_URL is not configured`.

2. Validate registry contract against ONDC pre-prod.

Expected request:

```json
{
  "subscriber_id": "<target BPP subscriber id>",
  "unique_key_id": "<optional key id>"
}
```

Expected usable response must include a destination URI field such as `subscriber_url`, `subscriberUrl`, `subscriber_uri`, `subscriberUri`, `bpp_uri`, `bppUri`, or `url`.

3. Fix public nginx upstream.

Current public result:

```text
https://ondcapi.walkingtree.tech/health -> 502 Bad Gateway
```

Verify the FastAPI process is running on the upstream address configured in nginx, then reload nginx.

4. Confirm ONDC subscriber registration.

Validate these values with ONDC onboarding/registry:

```env
SUBSCRIBER_ID=ondcapi.walkingtree.tech
BAP_ID=ondcapi.walkingtree.tech
UNIQUE_KEY_ID=cbbb99f5-ec6c-4ab6-bac6-3b6114c41664
BAP_URI=https://ondcapi.walkingtree.tech/ondc
BAP_CALLBACK_URI=https://ondcapi.walkingtree.tech/ondc
```

5. Decide on `rating` support.

The requested audit list includes `/rating` and `/on_rating`, but the application does not register these routes. Add them only if the target ONDC FIS14 test plan requires them; otherwise document that rating is out of scope.

## P1 - Protocol Correctness

1. Add action-specific FIS14 message validation.

Current validation checks the ONDC envelope and action matching, but `message` is a generic dict. Add schemas for at least:

```text
search, select, init, confirm, status, update, cancel, track, support
on_search, on_select, on_init, on_confirm, on_status, on_update, on_cancel, on_track, on_support
```

2. Enforce context freshness.

Validate:

```text
context.timestamp + context.ttl >= current time
context.timestamp is not too far in the future
```

3. Bind callback signer to expected participant.

After signature verification, validate:

```text
Authorization keyId subscriber_id == expected BPP subscriber
context.bpp_id == signer/registry subscriber
transaction_id exists or is allowed for first callback
message_id is unique
```

4. Use registry public keys for callbacks in pre-prod.

The current fallback to configured `SIGNING_PUBLIC_KEY` works locally, but pre-prod should resolve BPP public keys from registry.

5. Return structured NACK/error payloads for protocol failures where ONDC expects ACK/NACK semantics.

FastAPI currently returns HTTP exceptions for many failures. Confirm with the target ONDC/FIS14 test harness which cases must be HTTP error versus protocol NACK.

## P1 - Deployment Hardening

1. Add reproducible deployment artifacts.

Recommended checked-in artifacts:

```text
Dockerfile or systemd unit template
nginx site template
production env template without secrets
deployment smoke-test script
```

2. Protect debug APIs.

Restrict or remove:

```text
/ondc/transactions
/ondc/transactions/{transaction_id}
/health/keys
```

3. Replace filesystem persistence for pre-prod/production.

Use a durable database or managed storage with transaction indexes on:

```text
transaction_id
message_id
action
direction
created_at
```

4. Add monitoring and log retention.

Minimum:

```text
health check alert
5xx alert
callback verification failure alert
registry failure alert
outbound BPP latency/error metrics
certificate expiry alert
```

## P2 - Cleanups

1. Remove or archive legacy mock services if they are not used in the production path.
2. Move secret values out of local `.env` files and into a secret manager.
3. Align examples, Postman collection, and route list with the final ONDC test plan.
4. Add CORS only if a browser client must call these APIs directly.
5. Document that public ONDC endpoints are prefixed with `/ondc`.

## Verification Checklist After Fixes

Run these checks before requesting ONDC pre-prod traffic:

```text
python -m pytest -q
curl -fsS https://ondcapi.walkingtree.tech/health
curl -fsS https://ondcapi.walkingtree.tech/openapi.json
POST signed callback to https://ondcapi.walkingtree.tech/ondc/on_search
POST /ondc/search with real target bpp_id and verify outbound dispatch
Confirm registry lookup returns subscriber_url
Confirm outbound Authorization verifies against registered public key
Confirm callback Authorization verifies against BPP registry key
Confirm duplicate message_id rejection
Confirm invalid/tampered Authorization rejection
```

