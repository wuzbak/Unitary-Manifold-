# Merlin Replacement Program v1

This document records the implemented execution blueprint for making Merlin the primary AxiomZero repository/governance assistant with lower energy-per-successful-task than the incumbent external-model path.

## Implemented surfaces

- Runtime blueprint module:
  - `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-ox-navigator/ox_navigator/engine/merlin_program.py`
- Toolkit functions exposed through `/api/agentInvoke`:
  - `getMerlinProgramCharter`
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
- Direct API views:
  - `GET /api/merlin/program`
  - `GET /api/merlin/sync-checks`

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

`run_sync_checks()` verifies canonical Merlin source surfaces remain present and readable to reduce epistemic drift.

## Merlin Sovereignty Roadmap checklist

- [x] Program doctrine defined (reproducible, auditable, self-hostable, governance-aligned, higher task success).
- [x] Sovereign runtime router added (small / medium / heavy lanes; local-first provider).
- [x] OpenRouter frozen to compatibility-only fallback path with explicit enablement.
- [x] Persona governance guardrails added (style cannot override epistemic honesty/boundary rules).
- [x] Durable intent/provenance session records added.
- [x] Governed "back room" workspace policy/state exposed.
- [x] Open-science model admission policy + evaluator exposed.
- [x] 12/37 cadence policy added as internal scheduling control (not universal-superiority claim).
- [x] Stage A→E rollout naming aligned in runtime blueprint.
- [ ] Benchmark corpus + sustained empirical gate runs still required for full replacement approval.

## Governance and epistemic constraints retained

- Explicit gate labels remain mandatory in Merlin output contracts.
- Physics and governance boundaries remain explicit and preserved.
- Uncertainty and architecture limits remain first-class constraints.
