# EIGE Security Policy

**AxiomZero EIGE v22.0 — Election Integrity Governance Engine**  
*Theory & scientific direction: ThomasCory Walker-Pearson*  
*Code architecture & implementation: GitHub Copilot (AI)*

---

## Overview

EIGE v22 is an audit-support and transparency tool. Security review should focus on whether published artifacts can be independently verified, whether signatures and key status are interpreted correctly, whether Merkle and witness checks detect log inconsistency, and whether documentation states limits plainly.

## In scope

| Component | What to review |
|---|---|
| `eige.canonical` | Canonical JSON ambiguity, duplicate-key handling, float rejection, UTF-8 handling |
| `eige.crypto.merkle` | RFC 6962/RFC 9162 compatibility, inclusion proofs, consistency proofs, root calculation |
| `eige.crypto.signing` | Ed25519 domain separation, key ID construction, registry time/role checks, rotation, revocation, development-key rejection |
| `eige.crypto.commitments` | Group selection, generator derivation, opening checks, homomorphic aggregation, selective-opening behavior |
| `eige.ledger.log` | Append-only semantics, signed tree heads, log record validation |
| `eige.ledger.bulletin` | Witness behavior, split-view detection, equivocation evidence |
| `eige.ledger.custody` | Two-person sign-off enforcement and custody anomaly checks |
| `eige.audit.*` | Sampling ceremony, RLA calculations, reconciliation discrepancy classification |
| `eige.verify` | Bundle verification, exit codes, report status semantics |
| `eige.data.open_data` | HTTPS allow-list, provenance, expected SHA-256 pinning, no placeholder fallback |

## Out of scope

- Certified tabulator design, firmware, certification, or operation.
- Physical custody practices except where EIGE records and checks custody events.
- Claims already retracted in [RETRACTED_CLAIMS.md](RETRACTED_CLAIMS.md), unless a new implementation issue is found.
- Denial-of-service reports that require local administrative control and do not affect artifact verification.
- Development-only signers, mock HSMs, or mock TEE components when they correctly refuse production mode.

## Development-key warning

`DevelopmentSigner`, `SoftwareKeyProvider`, `MockHSM`, and mock TEE flows are for tests and demos only. They must not be used for production election artifacts. Production deployments should use controlled key ceremonies and, where required, HSM-backed keys. EIGE signatures identify a key; they do not prove the keyholder was honest.

## Reporting

Report suspected vulnerabilities by email to `axiomzero-security@proton.me` with subject `[EIGE SECURITY]`, or open a GitHub issue marked `[SECURITY]` if public disclosure is appropriate.

Please include the affected component, version or commit, reproduction steps, expected behavior, observed behavior, and your severity assessment. We aim to acknowledge reports within five business days and coordinate public disclosure when a report is confirmed.

## Known limitations

- EIGE cannot detect manipulation before a ballot is scanned or logged.
- EIGE cannot replace paper ballots, chain of custody, canvass reconciliation, or legally required audits.
- EIGE does not provide end-to-end voter-verifiable cryptographic voting.
- Statistical screening results are investigation leads, not evidence of fraud.
- PKCS#11 signer support exists, but this repository does not claim hardware certification or successful testing against every HSM.
