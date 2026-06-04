# Deployment Gaps

Audit date: 2026-06-04  
Target deployment: `https://ondcapi.walkingtree.tech`

## Current Public Status

| Check | Result |
|---|---|
| DNS | `ondcapi.walkingtree.tech` resolves to `115.245.177.14` |
| HTTPS port | Reachable on 443 |
| TLS | TLSv1.3 works |
| Certificate | `*.walkingtree.tech`, Go Daddy Secure Certificate Authority - G2 |
| Certificate validity | 2026-04-09 to 2026-10-24 |
| `/health` | FAIL: `502 Bad Gateway` |
| `/ondc/on_search` | FAIL: `502 Bad Gateway` |
| Edge server | nginx `1.14.1` |

## Blockers

| Priority | Gap | Evidence | Impact |
|---|---|---|---|
| P0 | Public upstream is unavailable | `https://ondcapi.walkingtree.tech/health` returns nginx 502 | ONDC cannot reach BAP callback endpoints |
| P0 | Registry URL is not configured | `ONDC_REGISTRY_URL=TODO_ONDC_REGISTRY_URL` | Buyer NP command dispatch fails before outbound BPP call |
| P0 | No verified pre-prod registry/BPP connectivity | Commands return 503 locally | Cannot complete search/select/init/confirm flow |
| P1 | No repo deployment artifacts | No Dockerfile, compose, nginx config, or systemd unit found | Deployment is manual and hard to reproduce |
| P1 | CORS middleware absent | No `CORSMiddleware` configured | Browser clients may fail; server-to-server ONDC is unaffected |
| P1 | Debug transaction APIs are public routes | `/ondc/transactions` is registered | Sensitive protocol payloads can leak if exposed publicly |
| P1 | Health/key endpoint exposes key-loaded status | `/health/keys` returns subscriber/key metadata | Operational metadata leakage |
| P1 | No durable database | Filesystem storage only | Risk of data loss and poor concurrency characteristics |
| P2 | HTTP port 80 timed out from audit environment | `http://ondcapi.walkingtree.tech/health` timed out | Redirect behavior is unverified |

## Reverse Proxy Requirements

The deployment must ensure:

1. nginx proxies `/health`, `/docs`, `/openapi.json`, and `/ondc/*` to the running FastAPI process.
2. The upstream process listens where nginx expects it, typically `127.0.0.1:8000`.
3. Uvicorn/Gunicorn is started with proxy headers when behind nginx.
4. Request body size and timeout settings support ONDC payloads.
5. `X-Forwarded-Proto`, `X-Forwarded-For`, and `Host` headers are forwarded.
6. TLS certificate renewal is automated before 2026-10-24.

## SSL/HTTPS Requirements

Current TLS is present and valid for the host. Remaining work:

1. Confirm full certificate chain trust from ONDC environments.
2. Enforce HTTP-to-HTTPS redirect on port 80.
3. Keep TLS 1.2+ enabled.
4. Monitor certificate expiration and renewal.

## Environment Requirements

Required before pre-prod:

```env
ONDC_REGISTRY_URL=<real ONDC pre-prod registry lookup URL>
SUBSCRIBER_ID=ondcapi.walkingtree.tech
BAP_ID=ondcapi.walkingtree.tech
BAP_URI=https://ondcapi.walkingtree.tech/ondc
BAP_CALLBACK_URI=https://ondcapi.walkingtree.tech/ondc
UNIQUE_KEY_ID=<registered ONDC key id>
SIGNING_PRIVATE_KEY=<registered matching private key>
SIGNING_PUBLIC_KEY=<registered public key>
REQUIRE_ONDC_AUTH=true
```

Recommended additions:

```env
BPP_ID=<target/pre-prod BPP subscriber id when not supplied by request>
BPP_URI=<target/pre-prod BPP URI when not resolved from registry>
APP_ENV=preprod
HOST=127.0.0.1
PORT=8000
```

## Operational Gaps

| Area | Gap |
|---|---|
| Process manager | No checked-in systemd/supervisor config |
| Worker model | No production Gunicorn/Uvicorn worker config in repo |
| Logs | App logging exists, but no deployment log rotation/collection config |
| Secrets | `.env` contains key material; production secret manager is not represented |
| Monitoring | No uptime, latency, or error alerting config |
| Backups | Filesystem event store has no backup/retention strategy |
| Security | No documented route-level protection for debug APIs |

