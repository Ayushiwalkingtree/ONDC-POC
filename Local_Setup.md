# Local Setup Guide

This document records setup steps, issues encountered, and fixes for running the ONDC POC locally on **Windows**.

---

## Part A — FastAPI MF Seller POC (Recommended)

### Prerequisites

| Requirement | Version | Status |
|-------------|---------|--------|
| Python | 3.11+ | Required |
| pip | Latest | Required |

### Steps

```powershell
cd d:\project\ONDC-POC
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify

```powershell
curl http://localhost:8000/health
# Expected: {"status":"ok","app":"ONDC MF Seller POC","domain":"ONDC:FIS14",...}

# Open Swagger UI
start http://localhost:8000/docs
```

### Result

**Runs successfully** without external dependencies (no DB, no registry, no keys).

---

## Part B — Official seller-app (Retail Reference)

### Prerequisites

| Requirement | Purpose | Status in POC |
|-------------|---------|---------------|
| Node.js | ≥ 16 | Installed |
| MongoDB | seller/ backend | **Not installed** |
| PostgreSQL | seller-app-api | **Not installed** |
| Yarn/npm | Package management | Available |
| ngrok/public URL | ONDC protocol callbacks | **Not configured** |
| ONDC Protocol Layer | Network routing | **Not available** |
| AWS S3 credentials | Product images | **Not configured** |
| SMTP | Email | **Not configured** |

### Step 1 — Clone seller-app

```powershell
git clone https://github.com/ONDC-Official/seller-app.git seller-app
```

#### Issue 1: Invalid path on Windows

| | |
|---|---|
| **Error** | `error: invalid path '.jsbeautifyrc '` |
| **Cause** | Repository contains files with trailing spaces in filenames (`.jsbeautifyrc `). Windows NTFS disallows trailing spaces in filenames. |
| **Fix applied** | `git clone --no-checkout` followed by `git config core.protectNTFS false` and checkout. Git renamed files to `.jsbeautifyrc` (without trailing space). Repository is **functionally complete** except for the cosmetic git status difference. |
| **Alternative** | Clone inside WSL2/Linux, or use `git sparse-checkout` excluding problematic files. |

### Step 2 — Install seller-app-api dependencies

```powershell
cd d:\project\ONDC-POC\seller-app\seller-app-api
npm install
```

**Result:** Success (1166 packages). 61 npm audit vulnerabilities reported (expected for older dependencies).

### Step 3 — Configure environment

No `.env.example` exists in the repository. Configuration is in JSON files:

| File | Purpose |
|------|---------|
| `lib/config/development_env_config.json` | Dev settings (PostgreSQL, BPP_ID, BPP_URI) |
| `lib/config/production_env_config.json` | Production overrides via env vars |

**Required manual config for seller-app-api:**

```json
{
  "database": {
    "host": "localhost",
    "port": "5432",
    "username": "your_user",
    "password": "your_password",
    "name": "sellerapp"
  },
  "sellerConfig": {
    "BPP_ID": "your-subscriber-id",
    "BPP_URI": "https://your-ngrok-url.ngrok-free.app",
    "BAP_ID": "...",
    "BAP_URI": "..."
  }
}
```

**Required for seller/ backend** — create `seller/app/config/local.env`:

```env
APP_ENV=local
NODE_ENV=development
BASE_APP_PORT=3019
MONGODB_DATABASE_HOST=mongodb://localhost:27017
MONGODB_DATABASE_NAME=sellerapp
AUTH_ACCESS_JWT_SECRET=change-me
```

**Cannot proceed without:** PostgreSQL running, MongoDB running, and valid ONDC network credentials.

### Step 4 — Start seller-app-api

```powershell
cd seller-app\seller-app-api
$env:NODE_ENV="development"
npm start
```

#### Issue 2: babel-node not found

| | |
|---|---|
| **Error** | `'babel-node' is not recognized as an internal or external command` |
| **Cause** | `@babel/node` is installed locally but not on PATH. The npm script calls `babel-node` directly. |
| **Fix** | Use `npx babel-node ./bin/www` instead of `npm start`, or add `node_modules/.bin` to PATH. |

#### Issue 3: Server hangs silently (PostgreSQL)

| | |
|---|---|
| **Error** | No output after starting; process runs indefinitely without "Express server listening" message |
| **Cause** | `bin/www` calls `sequelize.sync()` before starting the HTTP server. Sequelize attempts PostgreSQL connection to `localhost:5432` (from `development_env_config.json`). No PostgreSQL instance is running locally. Connection attempt blocks/hangs. |
| **Fix required** | Install and start PostgreSQL; create database `sellerapp`; update credentials in config. OR modify code to skip DB sync for POC (not recommended for production analysis). |
| **Status** | **Blocked** — cannot run seller-app-api without PostgreSQL |

### Step 5 — Docker Compose

```powershell
cd seller-app
docker-compose up
```

#### Issue 4: Missing Strapi Dockerfile

| | |
|---|---|
| **Error** | `strapiDocker` file not found during build |
| **Cause** | `docker-compose.yaml` references `strapiDocker` which was never committed to the repository |
| **Fix** | Remove `strapi` service from compose, or build only postgres + seller-app-api manually |

#### Issue 5: Misnamed service

| | |
|---|---|
| **Issue** | Docker service named `seller` actually builds `seller-app-api` (via `sellerApiDocker`), not the MongoDB `seller/` backend |
| **Impact** | Even with Docker, the catalog/IAM backend (`seller/`) is not started |

#### Issue 6: No MongoDB in compose

| | |
|---|---|
| **Issue** | docker-compose only includes PostgreSQL. The `seller/` service requires MongoDB which is not defined |
| **Impact** | Full stack cannot run via docker-compose alone |

### Step 6 — seller/ backend (not attempted)

Blocked by missing MongoDB. Would additionally require:
- AWS S3 credentials for image upload
- SMTP for email
- MapMyIndia API keys (optional)

---

## Part C — FIS Specifications (Reference)

```powershell
git clone --depth 1 --branch draft-FIS14-enhancements https://github.com/ONDC-Official/ONDC-FIS-Specifications.git fis-specs
```

**Result:** Success. Contains MF flow YAMLs, example JSON payloads, and Swagger UI source.

View developer guide locally:

```powershell
cd fis-specs
npm install
npm run build   # if available
# Or use hosted: https://ondc-official.github.io/ONDC-FIS-Specifications/
```

---

## Summary of Blockers

| Component | Blocker | Required to Unblock |
|-----------|---------|---------------------|
| seller-app-api | PostgreSQL not running | Install PostgreSQL, create DB |
| seller/ backend | MongoDB not running | Install MongoDB |
| ONDC network integration | No subscriber ID, keys, protocol layer URL | ONDC registry onboarding |
| Strapi CMS | Missing Dockerfile | Not needed for MF; remove from compose |
| Auth signing | No key pairs | Generate Ed25519 keys, register in ONDC registry |
| MF scheme data | No RTA/AMC integration | Integrate with Cybrilla/BSE/KFintech APIs |

---

## Recommended POC Path

For understanding ONDC MF Seller App architecture **without credentials**:

1. ✅ Run the **FastAPI POC** in this repo (works immediately)
2. ✅ Study **FIS14 spec examples** in `fis-specs/`
3. ✅ Read **seller-app** source for async ACK/callback patterns
4. ⏸ Skip full seller-app local run until PostgreSQL + MongoDB are provisioned
5. ⏸ Use **ONDC Workbench** (https://workbench.ondc.tech/) once sandbox credentials are obtained
