# ONDC Buyer NP Findings

## Summary

This repository is now structured as an ONDC Buyer NP / BAP implementation for Mutual Funds on `ONDC:FIS14`.

## Implemented

| Area | Status |
|---|---|
| Buyer NP command endpoints | Complete route surface |
| Callback receivers | Complete route surface |
| FIS14 context validation | Partial |
| ACK responses | Implemented |
| Filesystem persistence | Implemented |
| Postman Buyer NP artifacts | Implemented |
| Health endpoint | Implemented |

## Not Implemented

| Area | Status |
|---|---|
| Ed25519 signing | Missing by design; no fake signing |
| Inbound signature verification | Missing |
| Registry verification | Partial boundary only |
| Outbound counterparty dispatch | Missing |
| Durable database | Missing |
| Action-specific message validation | Missing |
| Automated test suite | Missing |

## Current Persistence Model

The filesystem repository saves every accepted command/callback as JSON.

```text
storage/
├── search/
├── select/
├── init/
├── confirm/
└── callbacks/
```

## Readiness

| Target | Ready? |
|---|---|
| Local development | Yes |
| ONDC PreProd | No |
| Production | No |

## Next Steps

1. Configure real ONDC Buyer NP account values.
2. Implement signing and verification.
3. Wire registry lookup into verification.
4. Implement outbound dispatch.
5. Add FIS14 message validation.
6. Add tests and deployment automation.
