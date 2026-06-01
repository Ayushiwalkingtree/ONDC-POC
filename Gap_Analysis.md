# Gap Analysis — ONDC Mutual Fund Seller App

| Area | Available | Missing | Action Required |
|------|-----------|---------|-----------------|
| **Sandbox** | ONDC Workbench exists (https://workbench.ondc.tech/); FIS14 listed with 0 use cases in workbench | No sandbox credentials provided; no staging subscriber ID; cannot test against live ONDC staging network | Apply for ONDC staging registry access via tech@ondc.org; obtain sandbox BAP/BPP test credentials |
| **Registry** | ONDC registry concept documented in Tech Quickstart Guide; lookup by subscriber_id for public keys | Not onboarded; no registry entry; no ukId/keyId | Complete ONDC participant onboarding (KYC, agreements); register BPP subscriber ID and public keys in staging then production registry |
| **Keys** | Auth signing spec available (`Auth Header Signing and Verification.md`); Ed25519 signing utility in ONDC Pre-production repo | No signing key pair generated; no encryption key pair; no keys registered | Generate Ed25519 key pairs (libsodium); register signing public key in registry; implement signing middleware in BPP |
| **Subscriber ID** | Placeholder in `development_env_config.json` (`sellerapp-staging.datasyndicate.in`) | No production/staging subscriber ID assigned to your organization | Obtain unique subscriber ID during ONDC onboarding (format: `{domain}/{path}` e.g., `yourcompany.in/ondc`) |
| **Mutual Fund source** | FIS14 spec defines catalog schema; industry RTA platforms exist (Cybrilla live, BSE/KFintech building) | No AMC/RTA API integration; no scheme master data feed; no NAV sync; seller-app repo has retail product model only | Integrate with RTA platform (Cybrilla API, BSE Star MF, etc.) for scheme catalog, folio lookup, order placement, redemption |
| **Settlement** | FIS14 payment tags defined; `settlement_details` in seller-app config (UPI example) | No payment gateway integration; no settlement reconciliation with RTA; no NACH/mandate for SIP | Integrate PG for lumpsum; e-NACH/mandate provider for SIP; implement settlement reporting per ONDC Payment & Settlement Protocol |
| **Signatures** | Spec + utility repo for BLAKE-512 + Ed25519 signing | Not implemented in POC or seller-app (relies on protocol layer) | Implement authorization header creation on all outbound `on_*` callbacks; verify inbound request signatures using registry lookup |
| **Authentication** | JWT auth in seller-app for internal APIs; ARN/EUIN/PAN in FIS14 protocol payloads | No ONDC auth header verification; no investor KYC provider integration (Digilocker, CKYC, eSign) | Implement Beckn auth header middleware; integrate KYC providers for new folio flows |
| **Domain specification** | `ONDC:FIS14` spec in `draft-FIS14-enhancements` branch with full MF flows | seller-app implements retail domains only (RET10, RET11, etc.) | Build MF BPP against FIS14 spec, not retail seller-app mappers |
| **Protocol version** | FIS14 uses version `2.0.0`; retail uses core_version `1.2.0` | Version mismatch if reusing seller-app code directly | Use FIS14 context schema (location object, version field) |
| **Catalog management** | FIS14 on_search catalog schema with scheme tags (NAV, exit load, SIP min) | No scheme ingestion pipeline; retail product CRUD in MongoDB not applicable | Build scheme sync from AMC/RTA; map to FIS14 catalog format |
| **Folio management** | FIS14 select/on_select returns folio list by PAN | No folio database or RTA lookup | Integrate RTA folio API; handle new folio creation with KYC |
| **SIP flows** | FIS14 spec covers SIP new/existing account, instalment, cancellation, auto-cancel | No mandate management; no instalment scheduling | Implement SIP registration via RTA; handle on_update for instalments |
| **Redemption flows** | FIS14 spec covers redemption by amount/units/all units | No redemption order placement | Integrate RTA redemption API; 2FA/OTP in confirm step |
| **KYC / Forms** | FIS14 multi-step HTML forms (account opening, Digilocker, eSign) | No form hosting or status tracking | Host KYC forms or proxy to RTA; implement on_status for form progress |
| **Logistics** | Fully implemented in retail seller-app (Shiprocket) | Not applicable for MF | Remove logistics dependency from MF BPP design |
| **Database** | PostgreSQL (protocol audit) + MongoDB (catalog) in seller-app | Not provisioned locally | Set up PostgreSQL + MongoDB for reference app; or use single DB for MF POC |
| **Docker** | Partial docker-compose for seller-app-api + postgres | Missing strapiDocker; missing MongoDB; missing seller/ service | Create complete docker-compose for MF BPP stack |
| **Documentation** | FIS14 developer guide, flow YAMLs, example payloads | seller-app has no README | Use this POC documentation + ONDC resources portal |
| **Observability / IGM** | Requirements documented on ONDC resources portal | Not implemented | Implement issue management (IGM) APIs per ONDC observability requirements |
| **Frontend** | Not in seller-app repo (referenced at localhost:3000) | No seller admin UI for MF | Build or procure seller dashboard for scheme/order management |
| **Testing** | ONDC Workbench for schema validation and flow testing | No automated test suite for MF flows | Use Workbench + write integration tests against FIS14 examples |

---

## Priority Matrix

### P0 — Cannot join ONDC network without these

1. Subscriber ID + Registry onboarding
2. Ed25519 key pair generation and registration
3. Auth header signing/verification
4. Public HTTPS endpoint (ngrok/cloud) for BPP_URI
5. ONDC staging sandbox access

### P1 — Cannot process MF transactions without these

1. RTA/AMC integration (scheme catalog, folio, orders)
2. Payment gateway (lumpsum)
3. KYC provider (new folio)
4. FIS14-compliant BPP implementation

### P2 — Required for production

1. SIP mandate (e-NACH)
2. Settlement reconciliation
3. IGM / observability
4. Seller admin dashboard
5. Security audit and SEBI compliance review

---

## What seller-app Provides vs What MF Needs

| Capability | seller-app | MF Requirement | Gap |
|------------|-----------|----------------|-----|
| Async ACK + callback pattern | ✅ | ✅ | Reusable pattern |
| Catalog → on_search mapping | ✅ (retail) | ✅ (schemes) | New mapper needed |
| Order lifecycle | ✅ (physical) | ✅ (financial) | Different fulfillment model |
| Protocol layer integration | ✅ | ✅ | Reusable with FIS14 |
| Logistics cascaded flow | ✅ | ❌ Not needed | Remove for MF |
| Category mappers (10 retail) | ✅ | ❌ | Replace with FIS14 schema |
| Product CRUD admin | ✅ | Partial | Scheme admin differs |
| Payment | Basic tags | PG + mandate | Major gap |
| KYC | ❌ | ✅ Required | Major gap |
