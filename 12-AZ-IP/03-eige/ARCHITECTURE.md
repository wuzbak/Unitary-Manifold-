# AxiomZero EIGE v22.0 — Architecture Reference

**Theory & scientific direction:** ThomasCory Walker-Pearson  
**Code architecture & implementation:** GitHub Copilot (AI)  
**Epistemic label:** 🔵 ADJACENT TRACK — governance application (not a physics claim)  
**Version:** 22.0.0

---

## Summary

EIGE v22 is organized around publication, verification, reconciliation, and audit support. It uses standard cryptographic primitives and election-workflow artifacts rather than the v21 physics-framed detector claims.

```text
[Certified election systems and paper records]
        |
        v
[Manifest + CVRs + results + custody events]
        |
        v
[EIGE v22 canonicalization, signatures, Merkle log]
        |
        +--> [Reconciliation checks]
        +--> [Public seed sampling + RLA calculations]
        +--> [Pedersen tally commitments]
        +--> [Witness/bulletin split-view checks]
        |
        v
[Publication bundle + standalone verifier]
```

## Core modules

| Module | Responsibility |
|---|---|
| `eige.config` | `EIGE_MODE` selection; development-only components refuse production. |
| `eige.canonical` | Canonical JSON for all signed, hashed, and committed data. |
| `eige.crypto.merkle` | RFC 6962/RFC 9162-style SHA-256 Merkle tree, inclusion proofs, consistency proofs. |
| `eige.crypto.signing` | Ed25519 signing, key IDs, registry, rotation, revocation, PKCS#11 signer. |
| `eige.crypto.commitments` | Pedersen tally commitments with selective openings; no ZK claim. |
| `eige.ledger.log` | Append-only Merkle event log and signed tree heads. |
| `eige.ledger.custody` | Paper chain-of-custody events with two-official sign-offs. |
| `eige.ledger.bulletin` | Signed tree head bulletin board, witnesses, equivocation evidence. |
| `eige.model.election` | Election, contest, candidate, CVR, manifest, and result parsing. |
| `eige.audit.sampling` | Public-seed sampling ceremony and manifest mapping. |
| `eige.audit.rla` | SHANGRLA-style assertions, BRAVO polling, Kaplan–Markov comparison support. |
| `eige.audit.reconciliation` | Canvass reconciliation and discrepancy classification. |
| `eige.data.open_data` | OpenElections and MIT Election Lab fetchers with provenance and no placeholder fallback. |
| `eige.screening` | Robust turnout and residual-vote outlier screens labelled as investigation leads. |
| `eige.report` | Audience-specific reports with explicit out-of-scope statements. |
| `eige.bundle` | Publication bundle layout and loading. |
| `eige.verify` | Standalone CLI verifier for bundles, inclusion, and consistency proofs. |
| `eige.pipeline` | County publisher and deterministic synthetic bundle builder. |

## Security boundaries

EIGE can detect inconsistencies in published artifacts. It cannot make unpublished records immutable, cannot prove that a signer was honest, and cannot determine whether paper ballots were handled correctly without custody records and a paper audit.

Development signers, mock HSMs, and mock TEE paths are not production controls. Production deployments should use real key ceremonies, HSM-backed keys where required, authenticated operator access, and ordinary election-office security controls.

## Legacy compatibility

`src/` remains present for compatibility with v21 demos and tests. The v21 Chern-Simons rolling hash is a non-security fingerprint; metric closure is retired as a detection signal; prior zero-knowledge proof claims are retracted.
