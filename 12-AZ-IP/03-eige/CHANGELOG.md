# EIGE Changelog

All notable changes to EIGE (Election Integrity Governance Engine) are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased] — county and state scale

### Summary

EIGE now works at full-population scale. Nothing has to fit in memory: the county log is a durable database, CVR exports are streamed, and verification reads the log in one pass in bounded memory. Each step measured here is described in `SCALE.md`, together with what has not been measured.

### Added

- `eige.crypto.merkle.CompactRange` and `LevelledTree`: streaming roots in O(log n) memory, and inclusion/consistency proofs from stored subtree nodes in O(log² n) reads. Outputs are identical to the RFC 9162 definition (property-tested against a recursive reference).
- `eige.ledger.store.DurableMerkleLog`: SQLite-backed log (WAL, `synchronous=FULL`) with one transaction per batch, rollback on failure, a unique-key index (a CVR id is never logged twice), stored signed heads with monotonic timestamps, a full integrity check, and bundle export.
- `eige.cvr_import`: streaming readers for NIST SP 1500-103 `CastVoteRecordReport` JSON (incremental parser, `CurrentSnapshotId`, `IsAllocable`, overvotes kept), NIST JSONL, and EIGE CSV.
- `python -m eige.county`: `init`, `commit-manifest`, `ingest` (whole export validated before anything is logged, then logged in one transaction that is rolled back if the file changed or the run is interrupted; source SHA-256 recorded), `event`, `sign-head` (PKCS#11, or a development key refused in production), `results`, `status --check-integrity`, `export`. `sign-head` and `export` refuse to run when the integrity check finds any problem.
- Precinct-level results: CVR `reporting_unit`, `results_report(..., by_reporting_unit=True)`, and verifier checks `REPORTED_UNIT_TOTAL_MISMATCH` / `CVR_REPORTING_UNIT_MISSING`. When results are jurisdiction-only, the verifier says so instead of passing silently.
- `eige.audit_input.v2`: several contests audited from one sample with one hand interpretation per ballot.
- `python -m eige.verify bundle --workers N` (parallel scan, identical report) and `python -m eige.verify state` / `eige.statewide` (statewide roll-up).
- `eige.dedup.DuplicateDetector` (disk-spilling, exact), `eige.canonical.decode_canonical`, `eige.bundle.read_metadata` / `iter_log`.
- `eige.synthetic_scale` and `tools/scale_benchmark.py` for reproducible large synthetic counties; `SCALE.md` with measured results.
- Tests: `tests/test_eige_scale_storage.py`, `tests/test_eige_scale_ingest.py`, `tests/test_eige_scale_verify.py`, including a 200,000-ballot bounded-memory test (marked slow).

### Changed

- The verifier is a single streaming pass. Duplicate CVR ids are now reported as reconciliation `DUPLICATE_CVR_ID` rather than as a malformed CVR. A log whose last line is not newline-terminated is reported as **Log file readable: failed**. Individual discrepancy rows are capped at 500, followed by a count of the rest.
- Ballot manifest lookups use binary search; contest lookups are constant-time; sampled ballots are captured during the scan rather than searched for.
- A sampled ballot that cannot be found (`selections: null`) or a sampled position with no logged CVR counts as the worst case for the reported outcome in both comparison and polling audits.
- `MAX_FILE_BYTES` now applies to JSON documents only; log entries are limited individually (4 MiB).
- `docs/FORMATS.md`: corrected the `sample.json` and `cast.json` shapes to match the code, and documented the import formats, reporting-unit results, audit v2, log entry types, the county database and state results.

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
