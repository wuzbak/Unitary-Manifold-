# AxiomZero EIGE v22.0 — Compliance Reference Document

**Theory & scientific direction:** ThomasCory Walker-Pearson  
**Code architecture & implementation:** GitHub Copilot (AI)  
**Version:** 22.0.0

---

EIGE is an audit-support and transparency tool. It is **not** a VVSG-certified voting system, does not count votes, and does not replace certified tabulators or legally required election procedures. The mappings below are conservative descriptions of implemented or planned support functions, not certification claims.

Status values:

- **implemented** — behavior exists in v22 modules and is covered by tests.
- **partial** — behavior exists for a limited EIGE scope, or depends on deployment controls outside EIGE.
- **planned** — not implemented in v22.

OSCAL output is expected to report `implementation-status` as `implemented`, `partial`, or `planned`.

## NIST SP 800-53 Rev. 5 mapping

| Control | Status | Module | EIGE behavior and boundary |
|---|---:|---|---|
| AU-2 Event Logging | implemented | `eige.ledger.log` | Election records and custody events can be appended to a Merkle log. EIGE does not log operating-system events. |
| AU-3 Content of Audit Records | partial | `eige.ledger.log`, `eige.ledger.custody` | Records include typed canonical JSON payloads and custody fields. Local operator identity proofing remains a deployment responsibility. |
| AU-9 Protection of Audit Information | partial | `eige.crypto.merkle`, `eige.ledger.log`, `eige.ledger.store`, `eige.ledger.bulletin` | Merkle roots, signed tree heads, consistency proofs, and witnesses detect post-publication alteration or split views. The county log database's integrity check detects edits to stored records. None of this prevents deletion of unpublished local files. |
| AU-10 Non-repudiation | partial | `eige.crypto.signing` | Ed25519 signatures identify which registered key signed a payload. They do not prove the keyholder was honest or that key custody was adequate. |
| AU-12 Audit Record Generation | implemented | `eige.ledger.log`, `eige.pipeline` | EIGE can generate canonical audit records for CVRs, custody events, heads, and bundles. |
| SC-12 Cryptographic Key Establishment and Management | partial | `eige.crypto.signing` | Key registry supports registration, rotation, revocation, roles, and development-key rejection. Hardware key ceremonies are outside current tests. |
| SC-13 Cryptographic Protection | partial | `eige.crypto.signing`, `eige.crypto.merkle`, `eige.crypto.commitments` | Ed25519 via `cryptography`, SHA-256 Merkle trees, and Pedersen tally commitments are implemented. HSM integration is available through PKCS#11 but not hardware-certified by this repository. |
| SI-7 Software, Firmware, and Information Integrity | partial | `eige.ledger.log`, `eige.ledger.bulletin`, `eige.verify` | EIGE checks integrity of published election records. It does not verify certified tabulator software, firmware, or build provenance. |
| SI-7(6) Cryptographic Protection | planned | — | No claim is made for cryptographic software/firmware integrity protection of voting systems. |
| SI-10 Information Input Validation | implemented | `eige.canonical`, `eige.model.election`, `eige.bundle`, `eige.cvr_import`, `eige.county` | Strict parsers reject invalid canonical JSON, malformed election definitions, bad manifests, malformed CVR exports, and inconsistent CVR/result shapes. A CVR export is validated in full before any record is logged. |
| SC-5 Denial-of-Service Protection | partial | `eige.verify`, `eige.bundle`, `eige.dedup`, `eige.parallel_scan` | The verifier streams the log with per-entry and per-document size limits and disk-spilling duplicate detection, so full-population bundles verify in bounded memory (see `SCALE.md`). Network-level availability is a deployment responsibility. |
| RA-5 Vulnerability Monitoring and Scanning | planned | — | Independent security review is invited but not automated as an EIGE control. |
| AC-2 Account Management | planned | — | The current adjudicator/API blueprint does not implement production account management. |
| AC-3 Access Enforcement | planned | — | Access control must be supplied by the deployment environment until application authentication is implemented. |
| IA-2 Identification and Authentication | planned | — | No production user-authentication system is claimed. |
| CM-6 Configuration Settings | partial | `eige.config` | `EIGE_MODE` separates development and production behavior; development-only components refuse production mode. Full configuration management remains external. |
| CP-9 System Backup | planned | — | Publication bundles are exportable, but backup policy and retention are deployment responsibilities. |

## VVSG 2.0 relationship

EIGE v22 may support election-office evidence collection for some VVSG-related concerns, but it is not a voting system and is not certified under VVSG 2.0.

| VVSG concern | Status | Module | Notes |
|---|---:|---|---|
| Auditability of records | partial | `eige.ledger.log`, `eige.verify` | Published records can be independently recomputed. EIGE does not create the certified cast-vote record. |
| Cryptographic verification of published artifacts | partial | `eige.crypto.signing`, `eige.crypto.merkle` | Signatures and Merkle proofs cover EIGE artifacts only. |
| Ballot accounting support | partial | `eige.audit.reconciliation`, `eige.model.election` | Reconciliation flags mismatches for explanation. It is not a canvass authority. |
| Risk-limiting audit support | partial | `eige.audit.rla`, `eige.audit.sampling` | Implements sampling and RLA calculations that can be cross-checked with SHANGRLA or Arlo. It is not the SHANGRLA library. |
| Accessibility, usability, voter-facing functions | planned | — | EIGE is not voter-facing voting equipment. |
| Tabulator security and certification | planned | — | Out of scope. |

## Controls no longer claimed

EIGE no longer claims NIST or VVSG control satisfaction from the v21 Chern-Simons rolling hash, metric closure check, HMAC telemetry placeholder, TEE mock, or prior zero-knowledge proof format. Those claims were retracted after red-team review.
