# Federal Engagement — EAC, CISA, and NIST

**AxiomZero EIGE v22.0**  
**Engagement type:** Voluntary review request and program notification  
**Target agencies:** EAC, CISA, NIST  
**Proposing organization:** AxiomZero Technologies & Consulting, SPC

---

## Overview

This document frames EIGE v22 for federal reviewers as an open-source audit-support and transparency tool. EIGE is not a certified voting system, does not count votes, and is not seeking certification as voting equipment.

The requested review is technical: artifact formats, Merkle proofs, Ed25519 signatures, key registry semantics, witness cosignatures, reconciliation outputs, RLA calculations, and public-verifier behavior.

## Draft EAC note

**Subject:** Review request — EIGE v22 audit-support publication and verification tool

Dear EAC staff,

We are notifying the Election Assistance Commission of EIGE v22, an open-source tool intended to support election-office publication bundles, reconciliation review, risk-limiting audit calculations, custody documentation, and independent public verification.

EIGE does not replace certified tabulators or any VVSG-certified voting system. It does not count votes. Its compliance document makes only conservative mappings to implemented audit-support behavior.

We would welcome feedback on whether the bundle format, verifier output, and RLA-support workflow are useful to election officials and observers, and where the documentation should be clearer about limits.

Respectfully,  
ThomasCory Walker-Pearson  
Scientific Director, AxiomZero Technologies & Consulting, SPC

## Draft CISA note

**Subject:** Voluntary review request — EIGE v22 open-source election audit-support tool

Dear CISA Elections Security Team,

We are requesting technical review of EIGE v22. The tool supports publication of signed Merkle logs, witness cosignatures, reconciliation checks, custody events, RLA support artifacts, and a standalone verifier.

Known limits are explicit: EIGE cannot detect manipulation before a ballot is scanned or logged, cannot prove a signer was honest, cannot replace paper audits, and treats statistical screens only as investigation leads. Prior v21 claims about a Chern-Simons hash, metric closure detector, and zero-knowledge proof have been retracted.

We would appreciate feedback on the threat model, public-verifier workflow, and any deployment guidance needed before an election office considers shadow-mode evaluation.

## Draft NIST note

**Subject:** Review request — EIGE v22 conservative SP 800-53 and OSCAL status mapping

Dear NIST staff,

EIGE v22 includes an updated compliance mapping that labels each relevant control as implemented, partial, or planned. The tool uses canonical JSON, Ed25519 signatures, Merkle logs, witness cosignatures, and conservative audit-support reporting.

We do not claim SI-7(6) or software/firmware integrity for tabulators. AC and IA controls are largely planned because the current operator API does not implement production authentication. We would welcome feedback on status wording and OSCAL representation.

## Materials to provide

- `README.md`
- `THREAT_MODEL.md`
- `RETRACTED_CLAIMS.md`
- `RED_TEAM_FINDINGS.md`
- `COMPLIANCE.md`
- `docs/FORMATS.md`
- `blueprint/OFFICIAL_WORKFLOW.md`
