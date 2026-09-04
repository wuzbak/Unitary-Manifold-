# Merlin Replacement Program v1

This document records the implemented execution blueprint for making Merlin the primary AxiomZero repository/governance assistant with lower energy-per-successful-task than the incumbent external-model path.

## Implemented surfaces

- Runtime blueprint module:
  - `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-merlin-navigator/ox_navigator/engine/merlin_program.py`
- Stage A benchmark corpus:
  - `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-merlin-navigator/ox_navigator/engine/merlin_benchmark.py`
- Telemetry instrumentation:
  - `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-merlin-navigator/ox_navigator/engine/merlin_telemetry.py`
- Toolkit functions exposed through `/api/agentInvoke`:
  - `getMerlinProgramCharter`
  - `getMerlinProgramOffice`
  - `getMerlinReplacementScope`
  - `getMerlinStackBaseline`
  - `getMerlinWeightsAndMeasures`
  - `getMerlinKnowledgeCore`
  - `runMerlinSyncChecks`
  - `getMerlinModelStrategy`
  - `getMerlinTrainingPlan`
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
  - `evaluateMerlinLongitudinalAcceptance`
  - `getMerlinPromotionPacket`
  - `runMerlinStageAReceipts`
  - `getMerlinReplacementReadiness`
  - `getMerlinControlTower`
- Direct API views:
  - `GET /api/merlin/program`
  - `GET /api/merlin/program-office`
  - `GET /api/merlin/control-tower`
  - `GET /api/merlin/memory`
  - `GET /api/merlin/telemetry`
  - `GET /api/merlin/sync-checks`
  - `GET /api/merlin/identity`
  - `GET /api/merlin/policy`
  - `GET /api/merlin/runtime`
  - `GET /api/merlin/benchmarks`
  - `GET /api/merlin/stage-a-receipts`
  - `GET /api/merlin/replacement-readiness`
  - `GET /api/merlin/promotion-packet`

## Scope mapping to the 13-point implementation request

1. Program charter is implemented in `get_program_charter()` with success criteria and non-negotiables.
2. Baseline and capability-gap map are implemented in `get_current_stack_baseline()`.
3. Weights & Measures scorecard and benchmark batteries are implemented in `get_weights_and_measures()`.
4. Knowledge core with typed provenance and source registry is implemented in `get_knowledge_core_sources()`.
5. Multi-lane model strategy and policy-based fallback are implemented in `get_model_strategy()`.
6. Training/adaptation tracks are implemented in `get_training_and_adaptation()`.
7. Energy-first optimization controls are implemented in `get_energy_optimization_track()`.
8. Backend expansion governance controls are implemented in `get_backend_expansion_policy()`.
9. Pentad integration and separation-boundary controls are implemented in `get_governance_integration_policy()`.
10. Reliability and abuse-resistance tracks are implemented in `get_reliability_security_plan()`.
11. Shadow→Assisted→Primary→Decommission rollout is implemented in `get_rollout_plan()`.
12. Weekly/monthly/quarterly governance rhythm is implemented in `get_operating_rhythm()`.
13. Hard replacement exit criteria are implemented in `get_exit_criteria()`.

## Continuous sync controls

`run_sync_checks()` verifies canonical Merlin source surfaces remain present and readable to reduce epistemic drift. `query_merlin()` now records per-run telemetry and attaches typed provenance plus memory-audit state to every response object.

`evaluateMerlinEmpiricalGate()` now computes an explicit sustained head-to-head replacement verdict from comparable Merlin/incumbent runs (success parity, quality regression budget, energy-per-successful-task delta, and high-severity policy violations). `runMerlinStageAReceipts()` now produces the comparable run receipts directly from the self-hosted benchmark corpus, `getMerlinReplacementReadiness()` exposes the concrete receipt-backed stage-D decision contract, and `getMerlinStageAArtifacts()` / `GET /api/merlin/benchmark-artifacts` export CI-friendly artifact bundles for recurring review while `getMerlinPromotionPacket()` remains the compatibility view.

`getMerlinProgramOffice()` now declares a formal command structure with explicit approve/hold/rollback authority, one decision ledger, one risk ledger, and one gate board. `getMerlinMultiStageBenchmarks()` defines Stage A→E batteries with minimum sustained-run thresholds, `evaluateMerlinLongitudinalAcceptance()` enforces clean-window cadence checks, and `getMerlinControlTower()` surfaces deployment eligibility with fail-closed gate logic.

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
