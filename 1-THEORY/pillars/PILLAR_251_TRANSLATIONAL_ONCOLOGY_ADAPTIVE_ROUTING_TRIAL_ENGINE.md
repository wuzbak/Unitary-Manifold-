# Pillar 251 — Translational Oncology Adaptive Routing & Trial Engine

**Status:** 🔵 ADJACENT RESEARCH TRACK (non-hardgate)  
**Module:** `src/core/pillar251_translational_oncology_adaptive_routing_trial_engine.py`  
**Tests:** `tests/test_pillar251_translational_oncology_adaptive_routing_trial_engine.py`

## 1) Executive Summary

Pillar 251 extends the oncology synthesis lane from score aggregation into an
operating-system layer: patient-state routing, intervention sequencing, adaptive
trial design, access optimization, and explicit uncertainty accounting.

## 2) Why this adjacent pillar matters

Existing modules already cover imaging, bottlenecks, intervention calculators,
and universal control surfaces. The missing layer was operational orchestration:
which path, in what order, under what uncertainty, with which equity constraints.

## 3) Pillar components

1. Patient-state routing probabilities across four pathway families  
2. Sequenced intervention plan with go/no-go thresholds and fallbacks  
3. Adaptive trial design specification (platform/seamless, arms, interim cadence)  
4. Access/equity routing surface (distance, affordability, virtual eligibility)  
5. Uncertainty ledger with elasticity drivers and option value (wait vs commit)

## 4) Method

- Ingest translational baseline from Pillar 248
- Build normalized state vector in `[0,1]`
- Produce routing simplex (sum to 1)
- Construct sequence and design metadata
- Compute operating score with uncertainty penalty
- Quantify robustness via deterministic Monte Carlo envelope

## 5) Outputs

- `patient_state_routing_probabilities(...)`
- `intervention_sequencing_plan(...)`
- `adaptive_trial_design_specification(...)`
- `access_optimization(...)`
- `uncertainty_accounting(...)`
- `translational_operating_score(...)`
- `pillar251_translational_oncology_operating_report()`

## 6) Epistemic boundary

This pillar is non-clinical and non-hardgate. It provides systems-level planning
artifacts and cannot be interpreted as treatment recommendations for individuals.

## 7) Falsification condition

The pillar is falsified if pre-registered multicenter evaluation shows no
predictive linkage between routing/sequence outputs and observed throughput,
access equity, or adaptation efficiency outcomes.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
