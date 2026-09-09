# Merlin Replacement Program v1

This document records the implemented execution blueprint for making Merlin the primary AxiomZero repository/governance assistant with lower energy-per-successful-task than the incumbent external-model path.

## Implemented surfaces

- Runtime blueprint module:
  - `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_program.py`
- Training artifact export module:
  - `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-psicat-navigator/tools/export_merlin_training_artifacts.py`
- Training JSONL export module:
  - `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-psicat-navigator/tools/export_merlin_training_jsonl.py`
- MLflow manifest export module:
  - `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-psicat-navigator/tools/export_merlin_mlflow_manifests.py`
- Stage A benchmark corpus:
  - `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_benchmark.py`
- Telemetry instrumentation:
  - `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_telemetry.py`
- Toolkit functions exposed through `/api/agentInvoke`:
  - `getMerlinProgramCharter`
  - `getMerlinProgramOffice`
  - `getMerlinMentorshipSprintCharter`
  - `getMerlinFacultyMatrix`
  - `getMerlinKnowledgeTransferCycles`
  - `getMerlinLibraryAndStudy`
  - `getMerlinExchangeProtocol`
  - `getMerlinMentorshipClosureContract`
  - `getMerlinReplacementScope`
  - `getMerlinStackBaseline`
  - `getMerlinWeightsAndMeasures`
  - `getMerlinKnowledgeCore`
  - `getMerlinTrustSourceLibrary`
  - `getMerlinKnowledgeUnknownsLedger`
  - `getMerlinRegulatoryChangeWatch`
  - `getMerlinDomainResearchMissions`
  - `getMerlinExpertMasteryProgram`
  - `runMerlinSyncChecks`
  - `getMerlinModelStrategy`
  - `getMerlinTrainingPlan`
  - `getMerlinTrainingArchitecture`
  - `getMerlinTrainingDataset`
  - `getMerlinMLflowManifests`
  - `getMerlinOpenScienceRegistry`
  - `getMerlinCompetitiveBenchmarkPlan`
  - `getMerlinTrainingArtifacts`
  - `getMerlinStageBCorpus`
  - `getMerlinStageCCorpus`
  - `getMerlinExpertDomainCorpus`
  - `getMerlinBenchmarkCorpora`
  - `getMerlinEnergyPlan`
  - `getMerlinBackendPolicy`
  - `getMerlinGovernancePolicy`
  - `getMerlinReliabilityPlan`
  - `getMerlinRolloutPlan`
  - `getMerlinOperatingRhythm`
  - `getMerlinExitCriteria`
  - `getMerlinProgramBlueprint`
  - `getMerlinIdentityPolicy`
  - `verifyMerlinIdentity`
  - `authorizeMerlinPrivilege`
  - `getMerlinSentinelPolicy`
  - `getMerlinMythosAstraContract`
  - `getMerlinOptimizationPriorities`
  - `getMerlinExecutionGraph`
  - `getMerlinBenchmarkSuite`
  - `getMerlinMultiStageBenchmarks`
  - `evaluateMerlinEmpiricalGate`
  - `getMerlinDomainGateContract`
  - `evaluateMerlinDomainGates`
  - `evaluateMerlinLongitudinalAcceptance`
  - `getMerlinPromotionPacket`
  - `runMerlinStageAReceipts`
  - `getMerlinReplacementReadiness`
  - `getMerlinControlTower`
  - `getMerlinInferenceProviders`
  - `getMerlinInferenceHealth`
  - `getMerlinReasoningChain`
  - `runMerlinResearchCycle`
  - `getMerlinCounterexampleDigest`
  - `getMerlinEnergyLedger`
  - Direct API views:
  - `GET /api/merlin/program`
  - `GET /api/merlin/program-office`
  - `GET /api/merlin/control-tower`
  - `GET /api/merlin/memory`
  - `GET /api/merlin/telemetry`
  - `GET /api/merlin/inference/providers`
  - `GET /api/merlin/inference/health`
  - `GET /api/merlin/reasoning-chain`
  - `POST /api/merlin/research-cycle`
  - `GET /api/merlin/counterexample-digest`
  - `GET /api/merlin/energy-ledger`
  - `GET /api/merlin/sync-checks`
  - `GET /api/merlin/identity`
  - `GET /api/merlin/policy`
  - `GET /api/merlin/runtime`
  - `GET /api/merlin/benchmarks`
  - `GET /api/merlin/training-architecture`
  - `GET /api/merlin/training-dataset`
  - `GET /api/merlin/mlflow-manifests`
  - `GET /api/merlin/open-science-registry`
  - `GET /api/merlin/trust-source-library`
  - `GET /api/merlin/knowledge-unknowns`
  - `GET /api/merlin/regulatory-change-watch`
  - `GET /api/merlin/domain-research-missions`
  - `GET /api/merlin/expert-mastery-program`
  - `GET /api/merlin/competitive-benchmarks`
  - `GET /api/merlin/benchmark-corpora`
  - `GET /api/merlin/domain-benchmark-corpus`
  - `GET /api/merlin/domain-gate-contract`
  - `GET /api/merlin/domain-receipts`
  - `GET /api/merlin/stage-a-receipts`
  - `GET /api/merlin/replacement-readiness`
  - `GET /api/merlin/review-packet`
  - `GET /api/merlin/heavy-lane`
  - `GET /api/merlin/model-board`
  - `GET /api/merlin/execution-board`
  - `GET /api/merlin/validation-resilience`
  - `GET /api/merlin/training-artifacts`
  - `GET /api/merlin/promotion-packet`

## Scope mapping to the 13-point implementation request

1. Program charter is implemented in `get_program_charter()` with success criteria and non-negotiables.
2. Baseline and capability-gap map are implemented in `get_current_stack_baseline()`.
3. Weights & Measures scorecard and benchmark batteries are implemented in `get_weights_and_measures()`.
4. Knowledge core with typed provenance and source registry is implemented in `get_knowledge_core_sources()`.
5. Multi-lane model strategy and policy-based fallback are implemented in `get_model_strategy()`.
6. Training/adaptation tracks are implemented in `get_training_and_adaptation()` and expanded into a governed corpus/curriculum in `get_training_architecture()`.
7. Energy-first optimization controls are implemented in `get_energy_optimization_track()`.
8. Backend expansion governance controls are implemented in `get_backend_expansion_policy()`.
9. Pentad integration and separation-boundary controls are implemented in `get_governance_integration_policy()`.
10. Reliability and abuse-resistance tracks are implemented in `get_reliability_security_plan()`.
11. Shadow→Assisted→Primary→Decommission rollout is implemented in `get_rollout_plan()`.
12. Weekly/monthly/quarterly governance rhythm is implemented in `get_operating_rhythm()`.
13. Hard replacement exit criteria are implemented in `get_exit_criteria()`.
14. Competitive benchmark families and promotion metrics are implemented in `get_competitive_benchmark_plan()`.
15. External open-science augmentation registry and governed training artifact bundle are implemented in `get_open_science_resource_registry()` and `build_training_artifact_bundle()`, now including retained training-execution preview payloads with Lane E evidence visibility.
16. Actual train/dev/test JSONL-ready dataset generation is implemented in `build_training_dataset_bundle()`.
17. MLflow-ready experiment manifests are implemented in `get_mlflow_experiment_manifests()`, with runnable receipt execution in `tools/run_merlin_mlflow_experiment.py`.
18. Broader Stage B/C benchmark corpora are implemented in `get_stage_b_benchmark_corpus()`, `get_stage_c_benchmark_corpus()`, and `get_benchmark_corpus()`.
19. Validation resilience is implemented as a first-class packet in `get_merlin_validation_resilience_packet()`, with repo-size mitigation actions, scoped CodeQL doctrine, and hosted-review outage handling linked back into the execution board.

## Continuous sync controls

`run_sync_checks()` verifies canonical Merlin source surfaces remain present and readable to reduce epistemic drift. `query_merlin()` now records per-run telemetry and attaches typed provenance plus memory-audit state to every response object.

`evaluateMerlinEmpiricalGate()` now computes an explicit sustained head-to-head replacement verdict from comparable Merlin/incumbent runs (success parity, quality regression budget, energy-per-successful-task delta, and high-severity policy violations). `runMerlinStageAReceipts()` now produces the comparable run receipts directly from the self-hosted benchmark corpus, `getMerlinReplacementReadiness()` exposes the concrete receipt-backed stage-D decision contract, and `getMerlinStageAArtifacts()` / `GET /api/merlin/benchmark-artifacts` export CI-friendly artifact bundles for recurring review while `getMerlinPromotionPacket()` remains the compatibility view.

`getMerlinTrainingArchitecture()` now exposes the governed dataset families, curriculum stages, and seed instruction corpus manifest for Merlin's repository-assistant + scientific-reasoning + autonomous-research mission profile. `getMerlinOpenScienceRegistry()` curates high-value augmentation lanes (Hugging Face Datasets, OpenML, UCI, Papers with Code, MLflow, AWS Open Data, NAIRR, NASA) under explicit admission controls, while `getMerlinCompetitiveBenchmarkPlan()` and `getMerlinTrainingArtifacts()` turn the ambition of a premiere/premium benchmarked Merlin into an auditable artifact contract.

`build_training_dataset_bundle()` now materializes actual train/dev/test records with deterministic split policy plus Stage A/B/C benchmark corpora suitable for JSONL export. `get_training_curation_ledger()` exposes deterministic low-token curation, deduplication, structural-quality, and budget metrics, and the HTTP `/api/merlin/training-dataset` plus `/api/merlin/training-curation` surfaces fail closed with HTTP `422` when dataset validation fails. `get_mlflow_experiment_manifests()` now emits experiment-ready tracking manifests for supervised tuning, preference optimization, Stage B shadow evaluation, and Stage C agentic evaluation, and those manifests now resolve to runnable receipt commands instead of export-only placeholders.

`getMerlinProgramOffice()` now declares a formal command structure with explicit approve/hold/rollback authority, one decision ledger, one risk ledger, and one gate board. `getMerlinMultiStageBenchmarks()` defines Stage A→E batteries with minimum sustained-run thresholds, `evaluateMerlinLongitudinalAcceptance()` enforces clean-window cadence checks, and `getMerlinControlTower()` surfaces deployment eligibility with fail-closed gate logic.

`getMerlinSprintReviewPacket()` now consolidates Stage A→E receipts, stage-by-stage failure reasons, open promotion blockers, and the current longitudinal discipline state into one canonical review surface. `getMerlinHeavyReasoningLane()` isolates the hardest sovereign long-context lane with provider comparison, benchmark pack, failure taxonomy, and a tuning agenda, while `getMerlinSovereignModelBoard()` converts the open-weight roster into runtime-tier shortlists with explicit adaptation-vs-abandonment policy.

`getMerlinExecutionBoard()` now turns those surfaces into one follow-on operating board inside the repo, with immediate tasks, a blocker register, validation-resilience doctrine, and a Sprint CL blunt board. The same board explicitly treats hosted-review outages and CodeQL oversize skips as trainable Merlin behaviors rather than invisible external inconveniences.

## Mentorship sprint implementation

- Formal mentorship sprint charter is now first-class under Program Office with non-negotiables for full rigor, no partial delivery, auditable decisions, and fail-closed promotion gates.
- Specialized model faculty matrix now defines small/router, medium/default, heavy/exception, safety/governance, and benchmarking lanes with fixed teaching scopes, acceptance rubrics, and required artifacts.
- Structured knowledge-transfer cycles now require each specialist to deposit playbooks, failure counterexamples, decision criteria, and benchmark-aligned exemplars into Merlin's governed back room.
- Library + Study assets are now explicit governed contracts covering canonical source curation, typed provenance registry linkage, benchmark corpora, active training queue surface, contradiction log, replay packs, and mentorship session ledger schema.
- Cross-model exchange protocol now requires at least one peer review per specialist, reconciliation, and explicit unresolved-conflict risk logging (silent merge forbidden).
- Proof-first closure sprint surfaces now expose a single-target Kawamura residual charter, a machine-readable burden ledger, and a Merlin/Copilot cross-review packet that defaults unresolved work to `still_open`.
- Control-tower responses now include a mentorship-to-runtime closure block with fail-closed checks and explicit evidence requirements for exchange-cycle completion and unresolved-risk counts.

## Three-lane intensive sprint implementation

- `PSICAT_THREE_LANE_INTENSIVE_SPRINT.md` now records the governed master sprint for:
  - Lane A: applications/tools mastery
  - Lane B: books/articles mastery
  - Lane C: adversarial self-correction and falsification discipline
- `getMerlinThreeLaneIntensiveSprint`, `getMerlinApplicationsToolsLane`, `getMerlinBooksArticlesLane`, `getMerlinAdversarialGrowthLane`, and `getMerlinContinuousLearningProtocol` now expose those lanes as machine-readable runtime surfaces.
- Training architecture and dataset seeding now include product-mastery, editorial-corpus, adversarial-integrity, formal proof-foundry, and governed between-session learning records so the sprint is not only descriptive but executable.
- `/api/merlin/three-lane-intensive-sprint` and `/api/merlin/continuous-learning` now expose the maximum-effort sprint and governed inactive-learning cadence directly, while `/api/merlin/performance-lane` exposes the dedicated throughput optimization contract.
- `evaluateMerlinPerformanceGate` and `POST /api/merlin/performance-gate-evaluate` now enforce the before/after receipt policy and compute pass/hold verdicts for Lane E throughput and regression gates.
- `runMerlinTrainingCycle` now emits an automatic performance-gate evaluation from retained Lane E baseline/candidate receipts and reports promotion blockers when the gate is not clear.
- Lane E training receipts now capture runtime benchmark telemetry-derived stage profiles from Stage B/C receipt runs when available and attach explicit provenance/fallback evidence metadata to each retained receipt.
- Captured Lane E runtime profiles are now persisted to `training/training_execution/lane_e_runtime_profiles.json` and reused across sessions when still valid, with fail-closed fallback when the artifact is missing/corrupt.
- Training execution bundles now surface the Lane E runtime-profile artifact path/existence and embedded runtime-profile payload to keep evidence provenance inspectable in exported review artifacts.
- `getMerlinTrainingExecutionQueue`, `getMerlinLaneProgressLedgers`, and `runMerlinTrainingCycle` now convert the retained training plan into active receipts across applications/tools, books/articles, adversarial self-correction, the formal proof-foundry lane, and the performance lane instead of queue descriptions alone.
- `getMerlinTrainingExecutionBundle` now exposes the retained bundle directly for tool/API consumers, including execution-cycle state and embedded Lane E runtime profile evidence.
- `/api/merlin/training-execution-queue`, `/api/merlin/training-execution-bundle`, `/api/merlin/lane-progress-ledgers`, and `/api/merlin/training-cycle` now expose live queue state, retained execution bundles, per-lane progress ledgers, and auditable retained training work, including proof-foundry reviewer packets, bridge-audit surfaces, and performance-gate receipts.
- `tools/export_merlin_training_execution.py` now materializes a deterministic execution bundle at `training/training_execution/three_lane_execution_bundle.json` so the current sprint state can be reviewed without hidden memory.
- Training execution now detects stale source changes, surfaces review-required queue items when mastery scores fall short, and emits deterministic challenge packs so completed work becomes reusable follow-up training rather than a dead ledger.

## Merlin Sovereignty Roadmap checklist

- [x] Program doctrine defined (reproducible, auditable, self-hostable, governance-aligned, higher task success).
- [x] Sovereign runtime router added (small / medium / heavy lanes; local-first provider).
- [x] OpenRouter frozen to compatibility-only fallback path with explicit enablement.
- [x] Persona governance guardrails added (style cannot override epistemic honesty/boundary rules).
- [x] Durable intent/provenance session records added.
- [x] Multi-tier memory, contradiction tracking, and replayable audits added.
- [x] Governed "back room" workspace policy/state exposed.
- [x] Open-science model admission policy + evaluator exposed.
- [x] 12/37 cadence policy added as internal scheduling control (not universal-superiority claim).
- [x] Stage A→E rollout naming aligned in runtime blueprint.
- [x] Stage A benchmark corpus and response evaluator exposed.
- [x] Per-run latency/cost/energy/provenance telemetry attached to Merlin output and API surfaces.
- [x] Sustained empirical gate evaluator implemented with explicit replacement pass/fail contract and measurable thresholds.
- [x] Self-hosted Stage A receipt generation and readiness packets are now implemented.
- [x] CI-exportable Stage A artifact bundles are now implemented.
- [ ] Full replacement approval still requires the receipt packet to pass its empirical gate.

## Governance and epistemic constraints retained

- Explicit gate labels remain mandatory in Merlin output contracts.
- Physics and governance boundaries remain explicit and preserved.
- Uncertainty and architecture limits remain first-class constraints.
