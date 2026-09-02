# AZ Parallel Workstream Board (Execution Matrix)

This board assigns one owner lane per application and defines immediate acceptance criteria for parallel execution.

## Shared pods (cross-cutting)

| Pod | Scope | Immediate backlog | Acceptance criteria |
|---|---|---|---|
| Platform/SRE | CI/CD, rollout, health | Status drift gate, canary checks, rollback docs | New gates running in CI; canary schedule defined |
| Security | Secrets, deps, SBOM, provenance | Secret scanning enforcement, advisory policy, attestation artifacts | No secrets in changes; dependency scan policy codified |
| Open Science | Metadata, reproducibility | JSON-LD/RO-Crate/DCAT mapping, release manifests | Public metadata links verifiable |
| UX/Integrity | Labels, clarity, accessibility | Epistemic label consistency and stale-claim removal | No stale status copy in governed surfaces |

## Application lanes (one owner per app)

| App | Owner lane | Immediate backlog | Acceptance criteria |
|---|---|---|---|
| 01 Axiom OS | API Reliability | contract tests, auth/rate-limit policy, runbook | stable API contract + incident runbook merged |
| 02 AZ-Kernel | Build Provenance | reproducible build attestations | artifact chain verifiable |
| 03 EIGE | Deterministic Governance | deterministic checks + audit export | repeatable outputs + auditable exports |
| 04 UM-SOS | Registry Integrity | DAG perf + registry consistency checks | registry checks pass, load perf budget defined |
| 05 UOS Kernel | API Surface | package boundary tightening | reduced public surface + normalized tests |
| 06 Omega Synthesis | Numeric Repro | reproducibility profile, benchmark snapshots | reproducible benchmark receipts |
| 07 Holon Zero | Canonical Pathing | duplicate-surface cleanup | canonical module paths documented |
| 08 Axiom Journalist | Provenance | source scoring and citation trace | exported reports include source trace |
| 09 OmegaHolon | Determinism | fallback determinism notes | deterministic fallback output path |
| 10 Filmer’s Companion | Offline-first | export determinism + offline guarantees | offline mode and export checks pass |
| 11 Terra OS | Data Connectors | cache/fallback reliability for external feeds | connector fallback policy documented |
| 12 Lithos OS | Ingest Quality | feed schema checks | ingest validation receipts |
| 13 Delphi | Uncertainty Discipline | calibration logs + uncertainty display | uncertainty surfaced in outputs |
| 14 SDAM | Device Matrix | capability fallback matrix | deterministic simulator mode validated |
| 15 Pentacorder | Sensor Reliability | fallback semantics + confidence labels | confidence labels shown consistently |
| 16 Oracle | Model Governance | routing policy versioning + eval harness | routing rules versioned; eval baseline published |
| 17 UM Image Generator | Render Stability | deterministic render tests | stable output under fixed seed/config |
| 18 UM Reader | Index Freshness | automated index refresh checks | freshness check receipts |
| 19 Falsification Observatory | Feed Adjudication | monitor + adjudication trace logs | trace log emitted per update cycle |
| 20 OX Navigator | Retrieval/Safety | retrieval evals + prompt hardening | eval checklist and safety tests present |
| 21 Geo Monitor | Feed SLA | tiered SLA + outage fallback | SLA tiers and fallback behavior documented |
| 22 AZ-SGE | Supply Chain | CVE trust model + SBOM export | SBOM export reproducible and validated |

## Platform surfaces

| Surface | Owner lane | Immediate backlog | Acceptance criteria |
|---|---|---|---|
| HF Spaces | Runtime Contract | adopt `hf-spaces/space_core/live_status.py`; smoke checks | status loaded from canonical feed in key spaces |
| public-site | Canonical frontend shell | dynamic live-status rendering + endpoint fallback | no stale hardcoded status in governed pages |
| Base44 | Transitional mirror | deprecation milestones and cutover tracking | mirror-only posture documented |

