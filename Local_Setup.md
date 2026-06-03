# Local Setup Guide

## Prerequisites

- Python 3.11+
- pip
- PowerShell or a POSIX shell

## Setup

```powershell
cd d:\project\ONDC-BACKEND\ONDC-POC
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` with real Buyer NP values when you move beyond local testing.

## Run

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Verify

```powershell
curl http://localhost:8000/health
start http://localhost:8000/docs
```

Expected health response includes:

```json
{
  "status": "ok",
  "app": "ONDC MF Buyer NP",
  "domain": "ONDC:FIS14"
}
```

## Postman

```powershell
$env:PYTHONPATH="D:\project\ONDC-BACKEND\ONDC-POC"
python scripts/generate_postman.py
python scripts/validate_uat_artifacts.py
```

Import:

- `postman/ONDC_MF_BUYER_NP_UAT.postman_collection.json`
- `postman/ONDC_MF_BUYER_NP_UAT.postman_environment.json`

## Persistence

Every accepted command and callback is saved as JSON in `storage/`.

```text
storage/
â”œâ”€â”€ search/
â”œâ”€â”€ select/
â”œâ”€â”€ init/
â”œâ”€â”€ confirm/
â””â”€â”€ callbacks/
```

## Signing Keys

No fake keys are generated. Configure real key paths in `.env`:

```dotenv
SIGNING_PRIVATE_KEY=TODO_SIGNING_PRIVATE_KEY
SIGNING_PUBLIC_KEY=TODO_SIGNING_PUBLIC_KEY
```

`SigningService.get_key_status()` reports TODO placeholders when key configuration or files are missing.

