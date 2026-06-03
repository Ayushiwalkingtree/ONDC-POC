# ONDC Mutual Fund Buyer NP

FastAPI implementation for an ONDC Buyer NP / BAP in the Mutual Funds investment domain (`ONDC:FIS14`).

The application exposes Buyer NP command endpoints, receives asynchronous callbacks, validates the FIS14 context envelope, returns ONDC ACK responses, and persists every command/callback event as JSON under `storage/`.

## Repository Layout

```text
ONDC-POC/
├── app/                    # FastAPI Buyer NP implementation
├── fis-specs/              # ONDC FIS14 reference specifications and examples
├── postman/                # Buyer NP Postman collection, environment, and payloads
├── scripts/                # Postman generation and artifact validation scripts
├── storage/                # Filesystem event persistence
├── README.md
├── ONDC_BUYER_NP_ARCHITECTURE.md
├── ONDC_Flow.md
├── Local_Setup.md
├── Gap_Analysis.md
└── UAT_READINESS.md
```

## Buyer NP Scope

| Area | Standard |
|---|---|
| Role | Buyer NP / BAP |
| Domain | `ONDC:FIS14` |
| Protocol version | `2.0.0` |
| Category | Mutual Funds / Investment |
| Persistence | Filesystem JSON events under `storage/` |
| Signing | No fake signing; production Ed25519 signing remains a real TODO |

## Setup

```powershell
cd d:\project\ONDC-BACKEND\ONDC-POC
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` with your ONDC Buyer NP registration values before any network testing.

## Run

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health: http://localhost:8000/health

## Postman

Import:

1. `postman/ONDC_MF_BUYER_NP_UAT.postman_collection.json`
2. `postman/ONDC_MF_BUYER_NP_UAT.postman_environment.json`

Regenerate after example changes:

```powershell
$env:PYTHONPATH="D:\project\ONDC-BACKEND\ONDC-POC"
python scripts/generate_postman.py
```

Validate generated artifacts:

```powershell
$env:PYTHONPATH="D:\project\ONDC-BACKEND\ONDC-POC"
python scripts/validate_uat_artifacts.py
```

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/ondc/search` | Buyer NP search command |
| POST | `/ondc/select` | Buyer NP selection command |
| POST | `/ondc/init` | Buyer NP order initialization command |
| POST | `/ondc/confirm` | Buyer NP order confirmation command |
| POST | `/ondc/status` | Buyer NP status command |
| POST | `/ondc/cancel` | Buyer NP cancellation command |
| POST | `/ondc/update` | Buyer NP update command |
| POST | `/ondc/support` | Buyer NP support command |
| POST | `/ondc/track` | Buyer NP tracking command |
| POST | `/ondc/on_search` | Callback receiver |
| POST | `/ondc/on_select` | Callback receiver |
| POST | `/ondc/on_init` | Callback receiver |
| POST | `/ondc/on_confirm` | Callback receiver |
| POST | `/ondc/on_status` | Callback receiver |
| POST | `/ondc/on_cancel` | Callback receiver |
| POST | `/ondc/on_update` | Callback receiver |
| POST | `/ondc/on_support` | Callback receiver |
| POST | `/ondc/on_track` | Callback receiver |
| GET | `/ondc/transactions` | List persisted events |
| GET | `/ondc/transactions/{transaction_id}` | List persisted events for one transaction |
| GET | `/health` | Health check |

## Storage

The filesystem repository writes JSON records under:

```text
storage/
├── search/
├── select/
├── init/
├── confirm/
└── callbacks/
```

Each record contains transaction metadata, action, direction, original payload, and timestamps.

## Signing Policy

No fake signing is implemented. `SigningService` detects whether subscriber/key configuration is present and reports TODOs when keys are unavailable. Production Ed25519 Authorization header generation must be implemented before ONDC PreProd or Production use.

## Documentation

| Document | Description |
|---|---|
| [ONDC_BUYER_NP_ARCHITECTURE.md](./ONDC_BUYER_NP_ARCHITECTURE.md) | Buyer NP architecture |
| [ONDC_Flow.md](./ONDC_Flow.md) | ONDC:FIS14 command and callback flow |
| [Local_Setup.md](./Local_Setup.md) | Local setup notes |
| [Gap_Analysis.md](./Gap_Analysis.md) | Readiness gaps |
| [UAT_READINESS.md](./UAT_READINESS.md) | UAT checklist |

## External References

- [ONDC Protocol Specs](https://github.com/ONDC-Official/ONDC-Protocol-Specs)
- [ONDC FIS Specs](https://github.com/ONDC-Official/ONDC-FIS-Specifications/tree/draft-FIS14-enhancements)
- [ONDC FIS Developer Guide](https://ondc-official.github.io/ONDC-FIS-Specifications/)
- [ONDC Workbench](https://workbench.ondc.tech/)
- [ONDC Financial Services Resources](https://resources.ondc.org/financial-services)
