# ONDC Mutual Fund Seller App — Proof of Concept

A local POC to understand ONDC Seller App (BPP) architecture for **Mutual Funds** (`ONDC:FIS14`), analyze the official reference repositories, and run a minimal Python/FastAPI implementation.

## Repository Layout

```
ONDC-POC/
├── app/                    # FastAPI MF Seller POC (Python)
├── seller-app/             # Cloned ONDC-Official/seller-app (Node.js — retail reference)
├── fis-specs/              # Cloned ONDC-FIS-Specifications (draft-FIS14-enhancements)
├── protocol-specs/         # Cloned ONDC-Protocol-Specs (core Beckn docs)
├── README.md               # This file
├── Architecture.md
├── ONDC_Flow.md
├── Local_Setup.md
├── Gap_Analysis.md
└── POC_Findings.md
```

## Critical Finding

The official **`seller-app`** repository targets **retail commerce** (Grocery, FnB, Fashion, etc.) with domain codes like `ONDC:RET10`. **Mutual Funds use a separate specification:**

| Aspect | Retail seller-app | Mutual Funds (this POC) |
|--------|-------------------|-------------------------|
| Spec repo | `ONDC-Official/seller-app` | `ONDC-Official/ONDC-FIS-Specifications` |
| Domain | `ONDC:RET10`, `ONDC:RET11`, etc. | **`ONDC:FIS14`** |
| Protocol version | core_version `1.2.0` | version `2.0.0` |
| Catalog unit | Products (SKU) | MF Schemes |
| Fulfillment | Delivery / Logistics | LUMPSUM / SIP / REDEMPTION |
| Reference infra | Cybrilla, RTA APIs (industry) | Not in seller-app repo |

## Quick Start — FastAPI POC

### Prerequisites

- Python 3.11+
- pip

### Setup

```powershell
cd d:\project\ONDC-POC
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

### Run

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open: http://localhost:8000/docs

### Postman Collection

Import these files into Postman:

1. **Collection:** `postman/ONDC_MF_Seller_POC.postman_collection.json`
2. **Environment:** `postman/ONDC_MF_Seller_POC.postman_environment.json`

Select environment **"ONDC MF Seller POC - Local"**, then run folder **"Lumpsum Flow (run in order)"** top to bottom.

Regenerate collection after example changes:

```powershell
$env:PYTHONPATH="D:\project\ONDC-POC"
python scripts/generate_postman.py
```

### Swagger UI

Each endpoint has **multiple request examples** (Lumpsum, SIP, Redemption) — use the **Examples** dropdown in the request body panel at http://127.0.0.1:8000/docs

### Test Flow

```powershell
# 1. Search (BAP → BPP)
curl -X POST http://localhost:8000/ondc/search -H "Content-Type: application/json" -d "@fis-specs/api/components/examples/mutual-funds/search/search.json"

# 2. Simulate on_search callback
curl -X POST http://localhost:8000/ondc/on_search -H "Content-Type: application/json" -d "@fis-specs/api/components/examples/mutual-funds/search/search.json"

# 3. View stored transactions
curl http://localhost:8000/ondc/transactions
```

## API Endpoints (FastAPI POC)

| Method | Path | Role |
|--------|------|------|
| POST | `/ondc/search` | Receive search from BAP |
| POST | `/ondc/select` | Receive scheme selection |
| POST | `/ondc/init` | Initialize order |
| POST | `/ondc/confirm` | Confirm order |
| POST | `/ondc/status` | Status poll |
| POST | `/ondc/on_search` | Simulate catalog callback |
| POST | `/ondc/on_select` | Simulate quote/folio callback |
| POST | `/ondc/on_init` | Simulate draft order + payment URL |
| POST | `/ondc/on_confirm` | Simulate order acceptance |
| POST | `/ondc/on_status` | Simulate payment/fulfillment status |
| GET | `/ondc/transactions` | List in-memory transactions |
| GET | `/health` | Health check |

All incoming protocol calls return `{"message":{"ack":{"status":"ACK"}}}` per Beckn async pattern.

## Documentation Index

| Document | Description |
|----------|-------------|
| [Architecture.md](./Architecture.md) | seller-app repo structure, components, diagrams |
| [ONDC_Flow.md](./ONDC_Flow.md) | search/select/init/confirm/status + callbacks |
| [Local_Setup.md](./Local_Setup.md) | Local setup steps and issues encountered |
| [Gap_Analysis.md](./Gap_Analysis.md) | What's available vs missing for MF go-live |
| [POC_Findings.md](./POC_Findings.md) | Final report, phases, risks |

## External References

- [ONDC Protocol Specs](https://github.com/ONDC-Official/ONDC-Protocol-Specs)
- [ONDC Seller App (Retail)](https://github.com/ONDC-Official/seller-app)
- [ONDC FIS Specs — MF branch](https://github.com/ONDC-Official/ONDC-FIS-Specifications/tree/draft-FIS14-enhancements)
- [ONDC FIS Developer Guide](https://ondc-official.github.io/ONDC-FIS-Specifications/)
- [ONDC Workbench](https://workbench.ondc.tech/)
- [ONDC Financial Services Resources](https://resources.ondc.org/financial-services)

## What This POC Does NOT Include

- ONDC Registry onboarding / Subscriber ID
- Ed25519 auth header signing
- Sandbox credentials
- Production RTA/AMC integration (e.g., Cybrilla, BSE Star MF)
- KYC, payment gateway, folio management

See [Gap_Analysis.md](./Gap_Analysis.md) for the full checklist.
