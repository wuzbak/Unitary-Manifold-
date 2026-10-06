# AxiomZero EIGE v22.0 — Roadmap

**Theory & scientific direction:** ThomasCory Walker-Pearson  
**Code architecture & implementation:** GitHub Copilot (AI)  
**Version:** 22.0.0

---

## Current v22 status

Done in v22:

- Repositioned EIGE as an audit-support and public-transparency tool.
- Added canonical JSON for signed and hashed artifacts.
- Added RFC 6962/RFC 9162-style Merkle logs, inclusion proofs, and consistency proofs.
- Added Ed25519 signing, key registry, rotation, revocation, development-key rejection, and PKCS#11 signer support.
- Added Pedersen tally commitments with selective openings and no zero-knowledge claim.
- Added signed tree heads, bulletin board, witness cosignatures, and split-view evidence.
- Added strict election/CVR/manifest/result parsing, including supported NIST CVR and ERR shapes.
- Added public-seed sampling, RLA calculations, reconciliation, custody ledger, open-data provenance, screening, reports, bundles, and a standalone verifier.
- Retired the v21 metric-closure detector and prior zero-knowledge proof claim.
- Reframed the Chern-Simons rolling hash as a non-security sequence fingerprint.

## Next steps

- Independent cryptographic review of canonicalization, Merkle proofs, Ed25519 domain separation, key registry semantics, witness behavior, and Pedersen commitment implementation.
- Hardware HSM testing for PKCS#11 Ed25519 signing, key rotation, revocation, and failure behavior.
- Pilot with an election office as a shadow-mode audit-support tool, not as a replacement for any certified voting system.
- CVR privacy review and jurisdiction-specific redaction guidance for rare ballot styles and small reporting groups.
- Cross-validation of RLA calculations with SHANGRLA and Arlo on public and synthetic datasets.
- Operator UI implementation following `blueprint/OFFICIAL_WORKFLOW.md` and `blueprint/OfficialWorkflowCockpit.tsx`.
- Authentication and authorization for the adjudicator/operator API before any production network deployment.
- External review of open-data provenance and SHA-256 pinning procedures.
- Usability testing of official, court, voter, and JSON report outputs.

## Non-goals

- No deployment promise to any set number of counties.
- No claim to count votes or certify elections.
- No claim that statistical screens are evidence of fraud.
- No claim that signatures prove the signer acted honestly.
- No physics-based tamper-detection or zero-knowledge proof claim.
