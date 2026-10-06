# EIGE Changelog

All notable changes to EIGE (Election Integrity Governance Engine) are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [22.0.0] — v22 audit-support release

### Summary

EIGE has been repositioned as an audit-support and public-transparency tool for election officials. It no longer claims physics-based tamper detection, unsupported deterministic integrity or zero-knowledge-proof claims.

### Added

- `eige/` v22 package with canonical JSON for all signed, hashed, and committed artifacts.
- RFC 6962/RFC 9162-style SHA-256 Merkle tree, inclusion proofs, and consistency proofs.
- Ed25519 signing with domain separation, public key registry, rotation, revocation, development-key rejection, and PKCS#11 signer support.
- Pedersen tally commitments with selective openings and homomorphic aggregation checks; no zero-knowledge claim.
- Signed tree heads, bulletin board, witness cosignatures, and equivocation evidence for split views.
- Strict election, contest, candidate, CVR, ballot-manifest, and result parsing.
- Public-seed sampling, RLA calculations, canvass reconciliation, custody ledger, open-data provenance, screening, reports, bundle loading, and standalone verification CLI.
- `docs/FORMATS.md` and `blueprint/OFFICIAL_WORKFLOW.md`.

### Changed

- `src/` is legacy compatibility code, not the basis for v22 security claims.
- Open-data fetching now raises errors and records provenance rather than falling back to placeholders.
- Verification reports list `verified`, `failed`, `warning`, and `not_checked`; `not_checked` is never a pass.
- Documentation now avoids stale test counts and directs readers to run `python -m pytest tests/ -q`.

### Retracted

- The v21 Chern-Simons rolling hash is not tamper evidence and is retained only as a non-security sequence fingerprint.
- The v21 metric-closure check is retired as a detection signal.
- The v21 zero-knowledge proof claim is retracted; the prior format proved nothing.
- HMAC telemetry and mock TEE paths are not public-verification or production-attestation mechanisms.

## [21.0.0] — 2026-07-17 — Phase 1-B release

This release is retained for historical context. Several security claims from this version were later retracted after red-team review; see [RETRACTED_CLAIMS.md](RETRACTED_CLAIMS.md).
