# POC Findings — Final Report

## 1. What Is Already Available in seller-app Repository

### Code & Services

| Asset | Description |
|-------|-------------|
| **seller-app-api/** | Complete ONDC BPP adapter for **retail** domains with search/select/init/confirm/status/cancel/track flows |
| **seller/** | Full seller backend with IAM, product catalog (MongoDB), order management, S3 image upload |
| **notifications/** | Email notification microservice |
| **Category mappers** | 10 retail domain mappers (Grocery, FnB, Fashion, Electronics, BPC, Appliances, Agriculture, Health, Home, Toys) |
| **Protocol API client** | HTTP client for ONDC protocol layer (`utils/protocolApis/`) |
| **Transaction audit models** | Sequelize models storing SearchRequest, SelectRequest, InitRequest, ConfirmRequest as JSONB |
| **Docker files** | Individual Dockerfiles for each service (partial compose) |
| **Example payloads** | Sample on_search JSON per retail category |

### Patterns Worth Studying

1. **Async ACK pattern** — immediate `{"message":{"ack":{"status":"ACK"}}}` then async `on_*` callback
2. **Transaction correlation** — `transaction_id` links all messages; `message_id` is per-message
3. **Protocol layer delegation** — BPP posts callbacks to `{BPP_URI}/protocol/v1/on_*` not directly to BAP
4. **Category-specific schema mapping** — pluggable mappers transform internal product model to Beckn catalog format
5. **Request audit trail** — PostgreSQL stores full request/response payloads for debugging

### What Is NOT Available

- No README or setup documentation
- No `.env` templates
- No Mutual Fund / FIS14 support
- No auth header signing implementation
- No frontend application
- Incomplete docker-compose (missing Strapi Dockerfile, MongoDB)

---

## 2. What Can Be Reused

| Component | Reuse Potential | Notes |
|-----------|----------------|-------|
| Async ACK + callback architecture | **High** | Core pattern identical for MF |
| Route structure (`/client/search`, etc.) | **Medium** | Adapt paths to FIS14 conventions |
| Sequelize transaction audit | **High** | Store MF protocol payloads same way |
| nconf configuration pattern | **Medium** | Layered JSON + env overrides |
| Protocol API client pattern | **High** | Same HTTP client approach for protocol layer |
| Winston logging | **High** | Drop-in |
| Express middleware structure | **Medium** | If staying on Node.js |
| Category mapper pattern | **Medium** | Replace retail mappers with FIS14 scheme mapper |
| Product service HTTP calls | **Low** | MF needs RTA APIs, not MongoDB product CRUD |
| Logistics integration | **None** | Not applicable for MF |
| S3 image upload | **Low** | Scheme documents may use similar pattern |
| JWT auth for admin APIs | **High** | For seller dashboard |

### For Python/FastAPI POC (This Project)

The FastAPI implementation reuses:
- FIS14 example payloads from `ONDC-FIS-Specifications`
- Beckn async pattern
- Transaction store concept (in-memory vs PostgreSQL)

---

## 3. What Needs Customization for Mutual Funds

| Area | Customization Required |
|------|----------------------|
| **Domain** | Switch from `ONDC:RET10` to `ONDC:FIS14`, version `2.0.0` |
| **Catalog** | Scheme master with NAV, exit load, SIP minimum, lock-in, offer documents |
| **Fulfillment types** | LUMPSUM, SIP, REDEMPTION instead of Delivery/Self-Pickup |
| **Select flow** | Folio lookup by PAN; multi-step KYC for new folio |
| **Payment** | PRE-FULFILLMENT with PG redirect; e-NACH mandate for SIP |
| **Post-confirm** | `on_update` for allotment, SIP instalments, redemption settlement |
| **Forms** | HTML form hosting for KYC (Digilocker, eSign) |
| **Regulatory** | ARN/EUIN validation, PAN-based investor identification, SEBI compliance |
| **Backend integration** | RTA platform APIs (Cybrilla, BSE Star MF, KFintech) instead of MongoDB product catalog |
| **Remove logistics** | No Shiprocket/LSP cascaded search-select-init flow |
| **City code** | Use `"*"` (pan-India) instead of city-specific codes |
| **Auth signing** | Implement Ed25519 signing on all outbound messages |

---

## 4. What Onboarding Is Required from ONDC

| Step | Description | Contact |
|------|-------------|---------|
| 1. Expression of interest | Register as ONDC network participant | tech@ondc.org |
| 2. Staging registry | Get subscriber ID, register public keys | ONDC staging registry |
| 3. Sandbox access | Test against staging network with Workbench | https://workbench.ondc.tech/ |
| 4. Domain subscription | Subscribe to `ONDC:FIS14` domain | Registry configuration |
| 5. Auth key registration | Upload Ed25519 signing public key | Registry portal |
| 6. Compliance review | SEBI/regulatory requirements for MF distribution | Internal compliance + ONDC checklist |
| 7. Pre-production testing | Pass Workbench scenario tests for MF flows | ONDC tech team |
| 8. Production registry | Move to production registry | ONDC ops team |
| 9. IGM setup | Issue grievance management integration | ONDC observability requirements |

### Industry-Specific Onboarding (Beyond ONDC)

| Requirement | Provider Options |
|-------------|-----------------|
| RTA/MF platform | Cybrilla (live on ONDC), BSE Star MF, KFintech |
| AMC empanelment | Individual AMC agreements for scheme distribution |
| ARN registration | SEBI-registered distributor ARN |
| KYC/KRA | CVL KRA, Digilocker |
| Payment | Razorpay, Cashfree, etc. with MF-specific flows |

---

## 5. Estimated Implementation Phases

### Phase 1 — Foundation (2–3 weeks)

- [ ] ONDC staging onboarding (subscriber ID, keys)
- [ ] FastAPI/Node BPP skeleton with auth signing
- [ ] Public HTTPS endpoint (ngrok → cloud)
- [ ] Pass Workbench schema validation for FIS14

### Phase 2 — Catalog & Discovery (2–3 weeks)

- [ ] RTA/AMC scheme master integration
- [ ] on_search catalog builder (full + incremental pull)
- [ ] Scheme sync job (NAV, status updates)

### Phase 3 — Investment Flows (4–6 weeks)

- [ ] Lumpsum flow (existing folio): select → init → confirm → on_update
- [ ] Payment gateway integration
- [ ] SIP flow (existing folio)
- [ ] SIP new folio with KYC (multi-step select)

### Phase 4 — Advanced Flows (3–4 weeks)

- [ ] Redemption (by amount, units, full)
- [ ] SIP cancellation and modification
- [ ] Cart flows (multi-scheme lumpsum/SIP)
- [ ] on_status unsolicited updates

### Phase 5 — Production Readiness (4–6 weeks)

- [ ] IGM / observability
- [ ] Seller admin dashboard
- [ ] Settlement reconciliation
- [ ] Security audit
- [ ] Pre-production Workbench scenario tests
- [ ] Production registry migration

**Total estimate: 15–22 weeks** (assuming RTA platform API access and ONDC sandbox credentials)

---

## 6. Risks and Blockers

| Risk | Severity | Mitigation |
|------|----------|------------|
| **No ONDC sandbox credentials** | 🔴 Critical | Initiate ONDC onboarding immediately; use Workbench offline validation meanwhile |
| **seller-app not applicable to MF** | 🔴 Critical | Do not fork seller-app for MF; use FIS14 spec as primary reference |
| **RTA platform dependency** | 🔴 Critical | Cybrilla is primary live integrator; evaluate partnership early |
| **SEBI regulatory compliance** | 🔴 Critical | Engage compliance team; ARN/EUIN requirements are mandatory |
| **KYC complexity** | 🟡 High | Multi-step forms with Digilocker/eSign add significant integration effort |
| **Auth signing complexity** | 🟡 High | Use ONDC Pre-production signing utility; test with Workbench auth tool |
| **seller-app outdated dependencies** | 🟡 Medium | 61 npm vulnerabilities; Node 16 EOL; do not use as production base without upgrade |
| **Incomplete docker-compose** | 🟢 Low | Not blocking for MF; build fresh Docker setup |
| **No MongoDB/PostgreSQL locally** | 🟢 Low | Blocked retail seller-app run only; FastAPI POC works without DB |
| **FIS14 workbench use cases = 0** | 🟡 Medium | MF domain recently added; scenario tests may be limited |
| **Windows dev environment issues** | 🟢 Low | Trailing-space filenames; use WSL2 or FastAPI POC on Windows |

---

## 7. Recommendations

1. **Do not attempt to run retail seller-app as MF seller app** — different domain, spec, and backend integration
2. **Use this FastAPI POC** to learn the async Beckn pattern with FIS14 mock payloads
3. **Study FIS14 spec flows** in `fis-specs/` for lumpsum, SIP, and redemption
4. **Apply for ONDC staging access** in parallel — this is the longest-lead item
5. **Evaluate RTA platform partnership** (Cybrilla recommended based on ONDC ecosystem status)
6. **Use ONDC Workbench** for schema validation once credentials are available
7. **Implement auth signing early** — it affects every API call and is non-negotiable for network access
8. **Plan for multi-step KYC flows** — SIP new folio is significantly more complex than lumpsum existing folio

---

## 8. POC Deliverables Summary

| Deliverable | Status | Location |
|-------------|--------|----------|
| seller-app repository analysis | ✅ Complete | [Architecture.md](./Architecture.md) |
| Architecture diagram | ✅ Complete | [Architecture.md](./Architecture.md) |
| Local setup with issue log | ✅ Complete | [Local_Setup.md](./Local_Setup.md) |
| ONDC flow documentation | ✅ Complete | [ONDC_Flow.md](./ONDC_Flow.md) |
| MF transaction flow mapping | ✅ Complete | [ONDC_Flow.md](./ONDC_Flow.md) §7 |
| Gap analysis table | ✅ Complete | [Gap_Analysis.md](./Gap_Analysis.md) |
| FastAPI POC | ✅ Complete | `app/` directory |
| Final report | ✅ Complete | This document |

---

## 9. Next Steps

1. Review this documentation with stakeholders
2. Initiate ONDC network participant registration
3. Evaluate RTA/MF platform vendors (Cybrilla, BSE, KFintech)
4. Extend FastAPI POC with auth signing once keys are available
5. Connect to ONDC staging network via Workbench
6. Implement first end-to-end flow: **Search → on_search → Select → on_select** with real scheme data
