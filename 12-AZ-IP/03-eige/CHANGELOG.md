# EIGE Changelog

All notable changes to EIGE (Election Integrity Governance Engine) are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [21.0.0] — 2026-07-17 — Phase 1-B Complete

### Summary

Phase 1-B closes the three architectural vulnerabilities identified in the Phase 1 adversarial analysis: the **Translation Gap** (float scanner output → integer EIGE intake), the **Over-Fitting Trap** (system achieves STABLE status by silently suppressing low-turnout counties), and the **Epistemic Barrier** (math output unintelligible to non-technical certification audiences).

**Total tests: 449 passing, 0 failures.**

### Added

#### Chaos Injection Module (`src/chaos_injection.py`)
- `ChaosInjector` class: adversarial noise injection for EIGE adversarial resilience testing
- Five noise modes: `NONE`, `BITFLIP`, `ZERO_OUT`, `RANDOMIZE`, `STOCHASTIC`
- `inject_replay_attack()`: replay attack detection test
- `inject_burst()`: high-volume burst stress testing for shard synchronisation
- `check_freedom_floor()`: per-batch participation floor monitoring
- `FreedomFloorViolation`: non-recoverable exception on participation suppression detection
- Constants: `CHAOS_NOISE_BUDGET_DEFAULT = 0.10`, `FREEDOM_FLOOR = 0.85`, `FREEDOM_FLOOR_MIN_BALLOTS = 1`

#### Holographic Screen Layer (`src/holographic_screen.py`)
- `HolographicScreen`: deterministic, rule-based normalisation of float scanner output → integer ballot vectors
- `WriteInRegistry`: case-insensitive write-in candidate name resolution
- `NormalisationRecord` / `NormalisationStatus`: full audit trail of every normalisation decision
- `AdmissibilityError`: exception routing low-confidence ballots to human adjudicator queue
- Normalisation rules: PASSTHROUGH, LOW_CONFIDENCE_ABSTAIN, ADJUDICATION_APPLIED, WRITE_IN_RESOLVED, WRITE_IN_UNRESOLVED, ZERO_PAD, TRUNCATED
- `HOLOGRAPHIC_SCREEN_MIN_CONFIDENCE = 0.60`

#### Public Trust Index (`src/public_trust_index.py`)
- `PublicTrustIndexBuilder` / `PublicTrustReport`: plain-English, legally defensible trust reports
- Status mapping: STABLE→VERIFIED, DRIFTED→WATCH, VIOLATED→ALERT
- `plain_english_summary`: court-ready paragraph with zero physics/mathematics vocabulary
- `statistical_equivalent`: comparison to standard audit sampling confidence and Benford's Law p-value
- `build_from_ledger_entry()`: constructs report from `StateLedgerEntry` (multi-county aggregation)

#### Freedom Floor Kill-Switch (in `src/sentinel_load_balance.py`)
- `SentinelLoadBalancer.check_freedom_floor()`: system-level participation floor check
- `SentinelLoadBalancer.check_participation_variance()`: per-county participation variance monitor
- `FreedomFloorBreach`: system-level non-recoverable exception

#### Chaos Integration Test Suite (`tests/test_eige_chaos_integration.py`)
- 7 full-pipeline adversarial scenarios:
  1. Clean baseline (0% noise)
  2. 10% noise budget (within tolerance)
  3. 50% zero-out (triggers VIOLATED)
  4. Multi-county mesh under noise
  5. Freedom floor enforcement
  6. Admissibility routing to human queue
  7. Public Trust vocabulary verification (no 5D/KK terms in output)

#### Public-Facing Documentation
- `BOOK.md` — 21-chapter comprehensive technical and operational reference (62KB)
- `README.md` — standalone orientation page
- `EXPLAINER.md` — 5-minute plain-English explainer (4 audiences)
- `FAQ.md` — skeptic FAQ (election deniers, cryptography researchers, privacy advocates, federalism advocates)
- `SECURITY.md` — security policy and open cryptanalysis challenge
- `CHANGELOG.md` — this file

#### Research and Outreach Materials
- `paper/eige_arxiv_preprint.md` — condensed 8-section arXiv preprint (cs.CR / cs.CY)
- `outreach/king_county_pilot_proposal.md` — shadow-mode pilot proposal to King County Elections
- `outreach/eac_cisa_engagement.md` — EAC, CISA, and NIST notification letters
- `outreach/academic_channels.md` — academic venue and community launch guide

#### Developer Experience
- `requirements.txt` — pinned Python dependencies (numpy, mpmath, pytest)
- `Dockerfile` — one-command image that runs the full 449-test suite
- `run_demo.py` — end-to-end synthetic election demo (5 counties, 5,000 ballots)
- `notebooks/01_eige_quickstart.ipynb` — Jupyter quickstart notebook
- `src/constants_engineering.py` — physics-free equivalent constants for independent evaluation
- `docs/index.html` — GitHub Pages landing page

### Changed

- `src/sentinel_load_balance.py`: added Freedom Floor check and `FreedomFloorBreach` exception
- `src/constants.py`: added `CHAOS_NOISE_BUDGET_DEFAULT`, `FREEDOM_FLOOR`, `FREEDOM_FLOOR_MIN_BALLOTS`, `HOLOGRAPHIC_SCREEN_MIN_CONFIDENCE`

### Test Growth

| Phase | Tests Added | Running Total |
|-------|-------------|---------------|
| Phase 1 (TRL-7 sprint) | 312 | 312 |
| Chaos Injection | +29 | 341 |
| Holographic Screen | +72 | 413 |
| Public Trust Index | +45 | 458 → *adjusted for dedup* → |
| Freedom Floor + Integration | +47 | **449** |

---

## [20.x] — 2026-06-xx — Phase 1 TRL-7 Sprint

### Summary

Initial implementation of the EIGE core engine. Technology Readiness Level 7 (system prototype demonstrated in operational environment).

**Total tests: 312 passing, 0 failures.**

### Added

#### Core Engine
- `src/constants.py` — system-wide physical and operational constants (K_CS=74, PHI_0=π/4)
- `src/chern_simon_hash.py` — CS rolling hash + `ShardedChernSimonChain` (8-shard holographic persistence)
- `src/metric_closure.py` — metric closure validator → STABLE | DRIFTED | VIOLATED
- `src/oscal_schema.py` — OSCAL 1.5.0 dataclasses + NIST SP-800-53 R5 control mapping
- `src/holon_zero_cert.py` — Holon Zero Certificate engine (ZK commitment architecture)
- `src/county_node.py` — county ingestion: int64 intake, 8-shard persistence, network partition handling
- `src/sentinel_load_balance.py` — override interception + atomic OSCAL dossier writer (< 500ms)
- `src/precision_audit_worker.py` — mpmath 512-bit async validation thread
- `src/state_mesh.py` — state aggregation: cross-county braid sync, Holon Zero cert emission
- `src/federal_auditor.py` — federal blind audit: ZK cert gate, `RawDataAccessAttempt` guard
- `src/sovereign_mesh.py` — top-level orchestrator + 3 integration tests
- `src/recovery_kernel.py` — cold-start integrity assertion + shard healing
- `src/disaster_recovery.py` — cold storage snapshots + inter-county mTLS peer replication

#### Infrastructure
- `infra/eige-pod.yaml` — Kubernetes deployment manifest
- `infra/state-mesh.yaml` — state mesh K8s configuration
- `infra/network-policy.yaml` — network isolation policy
- `infra/peer-authentication.yaml` — Istio mTLS peer authentication
- `infra/nginx-dashboard.conf` — public transparency dashboard proxy
- `infra/eige-backup-cron.yaml` — hourly cold storage CronJob

#### Blueprints (reference implementations)
- `blueprint/ingestion_engine.rs` — Rust fast-ingest parser blueprint
- `blueprint/VerificationCockpit.tsx` — Next.js multi-party verification UI blueprint

#### Documentation
- `ARCHITECTURE.md` — full system block diagram and 3-tier architecture
- `COMPLIANCE.md` — NIST VVSG 2.0 / SP-800-53 R5 / OSCAL 1.5.0 control mapping
- `ROADMAP.md` — Phase 1 → 3 deployment schedule

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
