# CALCULATOR.md — USIVF Complete API Reference

**Module:** `src.core.pillar243_unified_scientific_interoperability_validation_fabric`  
**Pillar:** 243  
**Version:** v10.58 — May 2026

---

## Seed Constants

```python
from src.core.pillar243_unified_scientific_interoperability_validation_fabric import (
    N_W, N_2, K_CS, C_S, XI_C, PHI0,
    HOLON_THEORETICAL_CONFIDENCE,
    ADJACENCY_TRACK_LABEL,
    USIVF_TRACK_LABEL,
    LANE_ORDER,
    N_LANES,
    CONTRACT_THRESHOLDS,
)
```

---

## `InteroperabilityScenario`

All fields are in `[0,1]`:

- `nr_job_success_rate`
- `nr_reproducibility_rate`
- `symbolic_identity_pass_rate`
- `symbolic_reduction_stability`
- `cosmology_contract_pass_rate`
- `cosmology_tolerance_pass_rate`
- `math_invariant_pass_rate`
- `math_reproducibility_rate`
- `governance_traceability_rate`
- `assistant_auditability_rate`

`ValueError` is raised if any field is outside `[0,1]`.

---

## Lane Scoring Functions

- `numerical_relativity_workflow_readiness(s)`
- `symbolic_algebra_consistency_score(s)`
- `cosmology_pipeline_compatibility_score(s)`
- `mathematical_verification_score(s)`
- `governance_assistant_traceability_score(s)`
- `lane_scores(s)` (all 5 at once)

Each lane score is the mean of its two lane inputs, clamped to `[0,1]`.

---

## Deterministic Workflow and Contracts

- `deterministic_run_id(s, seed=243)`  
  Stable run identifier from scenario + seed.

- `workflow_manifest(s, seed=243)`  
  Deterministic lane-job manifest with per-lane target/score/pass-fail.

- `interoperability_contract_results(s, thresholds=None)`  
  Returns lane pass/fail map, failed lanes, and failure fraction.

- `contract_penalty(s)`  
  `C_S × failure_fraction`.

---

## Aggregate Confidence

- `overall_interoperability_confidence_index(s)`

Formula:

```
mean_lane_score = mean(lane_scores)
penalty         = C_S × failure_fraction
index           = clamp(mean_lane_score × (1 − penalty) × HOLON_CONF)
```

- `interoperability_status(index)` returns:
  - `< 0.50`: `USIVF_CRITICAL`
  - `[0.50, 0.68)`: `USIVF_PARTIAL`
  - `[0.68, 0.84)`: `USIVF_OPERATIONAL`
  - `>= 0.84`: `USIVF_ROBUST`

---

## Robustness Simulation

- `monte_carlo_interoperability(s, n_trials=200, seed=243)`

Returns:
- `mean_index`
- `p10_index`
- `p50_index`
- `p90_index`

Raises `ValueError` if `n_trials < 1`.

---

## Integrated Reports

- `usivf_full_report(s, n_trials=200, seed=243)`
- `baseline_interoperability_scenario()`
- `pillar243_usivf_report(n_trials=200, seed=243)` (one-call top-level)

Integrated report includes:
- lane scores,
- contracts + failed lanes,
- penalty and overall index/status,
- deterministic workflow manifest,
- Monte Carlo robustness envelope,
- separation guard payload,
- falsification condition.

---

*CALCULATOR.md — pillar243-usivf/ — v10.58 — May 2026*  
*Theory: ThomasCory Walker-Pearson · Implementation: GitHub Copilot (AI)*
