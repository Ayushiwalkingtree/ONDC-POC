# ONDC Deployment Checklist

Audit date: 2026-06-03  
Scope: deployment readiness and validation commands. No code was modified.

## Phase 8: Deployment Readiness

### Runtime Endpoints

| Endpoint | Exists? | Evidence | Validation command |
|---|---:|---|---|
| Health endpoint | Yes | `app/main.py:65` defines `GET /health` | `curl -fsS http://127.0.0.1:8000/health` |
| Docs endpoint | Yes | FastAPI default docs route present in OpenAPI route map | `curl -fsSI http://127.0.0.1:8000/docs` |
| OpenAPI endpoint | Yes | FastAPI default `/openapi.json` route present in OpenAPI route map | `curl -fsS http://127.0.0.1:8000/openapi.json` |

### Deployment Artifact Support

| Item | Status | Evidence |
|---|---|---|
| `requirements.txt` | Present | Contains FastAPI, Uvicorn, Pydantic, pydantic-settings, python-dotenv, httpx |
| Uvicorn support | Present | `uvicorn[standard]` in `requirements.txt`; app object is `app.main:app` |
| Gunicorn support | Partial | ASGI app can run under Gunicorn with Uvicorn worker, but `gunicorn` is not in `requirements.txt` |
| Docker support | Missing | No Dockerfile or compose file found |
| systemd support | Missing | No `.service` file found |
| nginx support | Missing | No nginx config found |
| Health check | Present | `GET /health` |
| Public HTTPS readiness | Partial | Can run behind Nginx, but no repo config and ONDC security is not implemented |

## Exact Deployment Validation Commands

Run these after starting the app with Uvicorn:

```bash
cd /opt/ondc-buyer-np
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Validate health:

```bash
curl -fsS http://127.0.0.1:8000/health
```

Validate Swagger docs:

```bash
curl -fsSI http://127.0.0.1:8000/docs
```

Validate OpenAPI:

```bash
curl -fsS http://127.0.0.1:8000/openapi.json
```

Validate public domain after reverse proxy:

```bash
curl -fsS https://ondcapi.walkingtree.tech/health
curl -fsSI https://ondcapi.walkingtree.tech/docs
curl -fsS https://ondcapi.walkingtree.tech/openapi.json
```

Validate requested ONDC route presence from OpenAPI:

```bash
curl -fsS https://ondcapi.walkingtree.tech/openapi.json | grep -E '"/ondc/(search|select|init|confirm|status|cancel|update|support|track|on_search|on_select|on_init|on_confirm|on_status|on_cancel|on_update|on_support|on_track)"'
```

## Minimum Server Commands

Install packages:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip nginx certbot python3-certbot-nginx curl
```

Create venv and install dependencies:

```bash
cd /opt/ondc-buyer-np
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip wheel
.venv/bin/pip install -r requirements.txt
```

Start locally:

```bash
cd /opt/ondc-buyer-np
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Account Configuration Checklist

Create `.env`:

```bash
cd /opt/ondc-buyer-np
cat > .env <<'EOF'
APP_NAME=ONDC MF Buyer NP
APP_ENV=preprod
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

SUBSCRIBER_ID=ondcapi.walkingtree.tech
UNIQUE_KEY_ID=REPLACE_WITH_ONDC_UNIQUE_KEY_ID
SIGNING_PRIVATE_KEY=/etc/ondc-buyer-np/keys/signing-private.pem
ONDC_REGISTRY_URL=REPLACE_WITH_ONDC_PREPROD_REGISTRY_LOOKUP_URL
ONDC_REGISTRY_TIMEOUT_SECONDS=10
REQUIRE_ONDC_AUTH=true

BAP_ID=ondcapi.walkingtree.tech
BAP_URI=https://ondcapi.walkingtree.tech/ondc
BAP_CALLBACK_URI=https://ondcapi.walkingtree.tech/ondc
BPP_ID=
BPP_URI=

ONDC_DOMAIN=ONDC:FIS14
ONDC_VERSION=2.0.0
EOF
chmod 600 .env
```

## Deployment Risk Checklist

| Check | Required before ONDC PreProd? | Current status |
|---|---:|---|
| Public DNS for `ondcapi.walkingtree.tech` | Yes | Must be configured externally |
| TLS certificate | Yes | Not in repo |
| `.env` with real account values | Yes | Missing |
| Ed25519 signing | Yes | Missing |
| Callback verification | Yes | Missing |
| Registry verification | Yes | Missing |
| BPP/Gateway dispatch | Yes | Missing |
| Durable transaction database | Yes | Missing |
| Docker/systemd/nginx artifacts | Recommended | Missing in repo |
| Observability/log retention | Recommended | Partial logging only |

## DEPLOY NOW

**DEPLOY NOW = NO**

Exact missing items before deployment:

1. `.env` with real ONDC values for `ondcapi.walkingtree.tech`.
2. Working signing private key path and signing implementation.
3. Inbound callback verification implementation.
4. PreProd registry URL and registry verification wiring.
5. Public DNS + HTTPS certificate.
6. Actual BPP/Gateway dispatch.
7. Durable transaction persistence.
8. systemd/nginx/Docker deployment artifacts or equivalent operational runbook.

