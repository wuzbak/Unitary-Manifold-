# EIGE Academic and Independent Review Channels

**AxiomZero EIGE v22.0**  
*Scientific and election-administration review plan*

---

## Framing

EIGE v22 should be presented as an open-source audit-support and public-transparency tool. It supports RLA calculations, canvass reconciliation, custody ledgers, publication bundles, witness cosignatures, and public verification. It is not a replacement for certified voting systems and does not claim physics-based tamper detection or zero-knowledge proofs.

## Primary review venues

| Venue or community | Why it fits | Suggested focus |
|---|---|---|
| EVT/WOTE | Election technology and trustworthy elections | Bundle format, public verifier, reconciliation workflow, observer usability |
| USENIX Security / NDSS workshops | Systems and applied security | Merkle consistency, witness split-view detection, key registry, deployment threat model |
| IACR ePrint or applied crypto seminars | Cryptographic review | Ed25519 domain separation, Pedersen commitments, canonicalization, no-ZK boundary |
| Election audit community | RLA expertise | Cross-validation with SHANGRLA and Arlo, sample-size assumptions, escalation wording |
| Civic technology and open-government groups | Public transparency | Whether reports are understandable without overstating evidence |

## Organizations to invite

| Organization | Suggested ask |
|---|---|
| Verified Voting | Review whether EIGE’s role as audit support is stated clearly and does not imply replacement of paper audits. |
| MIT Election Data and Science Lab | Review open-data ingestion and provenance. |
| OSET Institute | Review open-source election-technology fit and deployment cautions. |
| Risk-limiting audit researchers | Check RLA formulas, sample-size helpers, and escalation language. |
| State or county election offices | Shadow-mode evaluation on public or synthetic data. |

## Paper direction

A revised paper should focus on:

1. The publication bundle and verifier model.
2. Merkle logs, signed tree heads, witnesses, and split-view evidence.
3. Reconciliation and custody records as prompts for official explanation.
4. RLA support and cross-validation with established tools.
5. The red-team retractions and lessons learned from v21.

Avoid claims that EIGE creates deterministic proof of election integrity, broadly blocks forgery, provides zero-knowledge proofs, or detects manipulation before records exist.
