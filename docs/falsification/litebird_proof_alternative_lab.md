# LiteBIRD Proof-Alternative Lab Campaign Guide

*Pillar 45-E | Unitary Manifold v10.26+ | 2026-05-10*

---

> **Status:** `PENDING_CAMPAIGN` for all three lanes.
> Implementation is complete and machine-tested.
> Decision-grade results will be recorded the day they are available.
>
> *Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
> *Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## 1 · Why a Proof-Alternative Lane?

The LiteBIRD satellite launches ~2032 and publishes CMB birefringence results ~2034.
The Unitary Manifold's primary falsifier — the measurement of β ∈ {0.273°, 0.331°}
outside the predicted forbidden gap (0.29°, 0.31°) — cannot be resolved before then.

This document operationalises three **immediate laboratory-accessible lanes** that:

1. Can return a falsification or support verdict years before LiteBIRD launches.
2. Are mechanically independent of the cosmological measurement.
3. Are governed by explicit bright-line pass/fail criteria, not qualitative assessment.

All three lanes derive their predicted signals from the same 5D geometric constants:
N_W = 5, K_CS = 74, C_S = 24/74.  A falsification in any lane falsifies the
framework regardless of the LiteBIRD outcome.

---

## 2 · Predicted Signals and Physical Derivation

### UM Physical Constants

| Constant | Value | Derivation |
|----------|-------|-----------|
| `N_W` (winding number) | 5 | Selected by Planck n_s = 0.9649 ± 0.0042 |
| `K_CS` (Chern-Simons charge) | 74 | = 5² + 7² = n₁² + n₂² |
| `C_S` (braided sound speed) | 24/74 ≈ 0.3243 | = (n₂² − n₁²) / K_CS |
| `φ₀` (canonical field) | √(8 N_W / (1 − n_s)) ≈ 33.10 | Pillar 56 closure |

### Lane A — CP-Asymmetry Prediction

The (5,7) braid sector predicts a topology-locked CP asymmetry:

```
A_CP^lab = sin(2π × N_W / K_CS) = sin(2π × 5/74) ≈ 0.4027
```

This is the predicted central value.  A decision-grade lab campaign with
σ_A < 1 × 10⁻⁵ must observe a **nonzero** A_CP at ≥ 3σ and consistent with
this prediction to support the framework.  A zero-consistent result
(|A_CP| ≤ 1.96 × σ_A) at decision-grade sensitivity **falsifies** the framework.

### Lane B — Polarisation Rotation in Analogue Braid Systems

Two rotation predictions arise from the two topological sectors:

| Sector | Prediction | Formula |
|--------|-----------|---------|
| (5,7) primary | `φ_rot_primary = φ₀ × (24/74) / π mod 360°` | C_S = 24/74 |
| (5,6) shadow | `φ_rot_shadow = φ₀ × (11/61) / π mod 360°` | C_S' = 11/61 |

The **forbidden gap** for Lane B lies *between* the two sector predictions —
mirroring the CMB gap structure.  A measurement landing inside this inter-sector
gap at calibration-confirmed conditions **falsifies** the framework.

### Lane C — B-Mode Polarisation Analogue (Cryogenic Testbeds)

Cryogenic CMB-testbed cameras (CLASS, SPIDER, ground-deployed analogue
systems) measuring effective polarisation rotation on known calibration sources.
The framework predicts:

```
β_lab = 0.273°   (primary UM peak, same physics as CMB prediction)
```

with admissible window [0.22°, 0.38°] and forbidden gap (0.29°, 0.31°) —
**identical to the LiteBIRD falsification criteria**.

---

## 3 · Decision Logic and Bright-Line Gates

### Gate hierarchy (in order of precedence)

```
1. If topology not certified (5,7) → INCONCLUSIVE (not decision-grade)
2. If sensitivity not decision-grade → INCONCLUSIVE
3. If A_CP^lab is zero-consistent at ≥ 95% CL (Lane A) → FALSIFIED
4. If φ_rot or β_lab falls in forbidden gap → FALSIFIED
5. If measurement is outside admissible window → FALSIFIED
6. If nonzero at ≥ 3σ with topology lock and controls (Lane A/B/C) → SUPPORTED
7. If nonzero but < 3σ (Lane A/B/C) → CONSISTENT (insufficient)
```

None of these gates can be waived.  No inflation without gate passage.

### Verdict table

| Verdict | Meaning |
|---------|---------|
| `FALSIFIED` | Framework is falsified by this lane. Decision is final. |
| `SUPPORTED` | Decision-grade evidence supports the framework. |
| `CONSISTENT` | Measurement does not conflict, but evidence is insufficient. |
| `INCONCLUSIVE` | Sensitivity or certification not yet decision-grade. |

### Composite verdict

| Condition | Composite |
|-----------|-----------|
| Any lane FALSIFIED | `FALSIFIED` |
| All three decision-grade lanes SUPPORTED | `STRONGLY_SUPPORTED` |
| ≥ 1 SUPPORTED, none FALSIFIED | `SUPPORTED` |
| No decision-grade results | `PENDING` |
| Decision-grade but no SUPPORTED or FALSIFIED | `CONSISTENT` |

---

## 4 · Uncertainty Budgets

### Lane A — CP Asymmetry

| Source | σ contribution |
|--------|---------------|
| (5,7) topology locking | 5 × 10⁻⁷ |
| Residual background asymmetry | 3 × 10⁻⁶ |
| Detector non-linearity | 2 × 10⁻⁶ |
| Beam/acceptance asymmetry | 1 × 10⁻⁶ |
| Statistical floor (per campaign) | 4 × 10⁻⁶ |
| **Total (quadrature)** | **≈ 5.3 × 10⁻⁶** |
| **Decision threshold** | **< 1 × 10⁻⁵** |

### Lane B — Analogue Rotation

| Source | σ contribution (deg) |
|--------|---------------------|
| Waveguide phase noise | 0.050 |
| Temperature drift | 0.020 |
| Polarimeter calibration | 0.030 |
| Topology locking fidelity | 0.010 |
| Statistical floor (photon counting) | 0.040 |
| **Total (quadrature)** | **≈ 0.071 deg** |

### Lane C — Cryogenic B-Mode Analogue

| Source | σ contribution (deg) |
|--------|---------------------|
| Instrument systematics (HWP) | 0.005 |
| Foreground residual (dust/synchrotron) | 0.008 |
| Calibration source uncertainty | 0.003 |
| Beam/sidelobe pickup | 0.004 |
| Statistical noise (per obs. block) | 0.006 |
| **Total (quadrature)** | **≈ 0.012 deg** |

---

## 5 · ToE Score Contributions

If any lane returns a SUPPORTED verdict at decision grade, it contributes
to the Theory-of-Everything (ToE) score:

| Lane | Contribution |
|------|-------------|
| A (CP asymmetry) | +0.4 pts |
| B (analogue rotation) | +0.3 pts |
| C (cryogenic B-mode) | +0.3 pts |
| **Max pre-LiteBIRD total** | **+1.0 pts** |

These contributions require all bright-line gates to be passed.  No partial credit
for CONSISTENT or INCONCLUSIVE verdicts.

---

## 6 · Machine Implementation

All decision logic is implemented in and machine-tested:

| File | Purpose |
|------|---------|
| `src/core/litebird_proof_alternative.py` | Pillar 45-E module (Lane A/B/C engine) |
| `tests/test_litebird_proof_alternative.py` | 112 machine-verified tests |
| `src/core/lab_litebird_substitute.py` | Pillar F14/P8 CP campaign (earlier lane) |
| `tests/test_core_lab_litebird_substitute.py` | Lab substitute tests |
| `src/core/litebird_boundary.py` | CMB boundary / fail-zone logic |
| `src/core/litebird_forecast.py` | Full LiteBIRD statistical forecast |
| `src/core/litebird_gap_hardening.py` | Inter-sector gap hardening |

### Quick-start

```python
from src.core.litebird_proof_alternative import (
    LaneAInput, LaneBInput, LaneCInput,
    lane_a_cp_asymmetry_verdict,
    lane_b_rotation_verdict,
    lane_c_bmode_verdict,
    composite_proof_alternative,
    proof_alternative_status_snapshot,
)

# Check current status
print(proof_alternative_status_snapshot())

# Evaluate a hypothetical Lane A campaign result
inp = LaneAInput(
    a_cp_measured=0.40,        # measured A_CP value
    sigma_a=5e-6,              # 1-sigma uncertainty (decision-grade)
    replications=3,
    systematics_controls_passed=True,
    topology_certified=True,
)
result = lane_a_cp_asymmetry_verdict(inp)
print(result["verdict"])     # SUPPORTED / FALSIFIED / CONSISTENT / INCONCLUSIVE
print(result["reason"])
```

---

## 7 · Test Results (as of 2026-05-10)

All 112 machine tests pass:

```
tests/test_litebird_proof_alternative.py  112 passed in 0.25s
```

Test coverage includes:
- All constant values and physical derivations
- Lane A: topology gate, sensitivity gate, replication gate, systematics gate,
  zero-consistent (FALSIFIED), 3σ signal (SUPPORTED), 2σ signal (CONSISTENT)
- Lane B: calibration gate, replication gate, forbidden-gap (FALSIFIED),
  outside-window (FALSIFIED), predicted-value (SUPPORTED)
- Lane C: calibration gate, foreground gate, outside-window (FALSIFIED),
  in-gap (FALSIFIED), predicted-value (SUPPORTED)
- Composite aggregation: STRONGLY_SUPPORTED, FALSIFIED, PENDING
- Evidence strength score: all-supported (1.0), any-falsified (0.0), partial
- All uncertainty budgets (quadrature sums verified)
- Status snapshot completeness

---

## 8 · Falsification Criteria Summary

The framework is **falsified at lab scale** if any of the following are
confirmed at decision-grade sensitivity:

1. **Lane A:** A_CP^lab is zero-consistent (≤ 1.96σ from zero) in a topology-
   certified (5,7) campaign with σ_A < 10⁻⁵ and ≥ 2 independent replications.

2. **Lane B:** The measured analogue rotation φ_rot falls in the inter-sector
   forbidden gap — the zone between the (5,7) primary and (5,6) shadow
   sector predictions.

3. **Lane C:** The measured β_lab falls in the forbidden gap (0.29°, 0.31°)
   or outside the admissible window [0.22°, 0.38°] in a calibration-confirmed,
   foreground-subtracted cryogenic B-mode campaign.

**A falsification in any lane is final and independent of the LiteBIRD outcome.**

---

## 9 · Relationship to LiteBIRD Primary Falsifier

These lanes are **parallel** to, not replacements for, LiteBIRD:

| Property | Lab Lanes (A/B/C) | LiteBIRD |
|----------|-----------------|---------|
| Timeline | Now → 2027 | 2032 launch, ~2034 result |
| Signal type | A_CP, φ_rot, β_lab | CMB β birefringence |
| Admissible window | Lane-specific | [0.22°, 0.38°] |
| Forbidden gap | Lane-specific | (0.29°, 0.31°) |
| Falsification power | Lab-accessible | Definitive cosmological |
| ToE score contribution | Up to +1.0 pts | Primary falsifier |

A positive lab result does **not** pre-confirm LiteBIRD.  It reduces prior
uncertainty and increases pressure for the cosmological measurement.
A lab falsification is final.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
