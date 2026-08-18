# CALCULATOR.md — PCCRE: Complete API Reference

**Module:** `src.core.pillar242_planetary_coherence_cascade_resilience_engine`  
**Pillar:** 242  
**Version:** v10.57 — May 2026

---

## Seed Constants (Module Level)

```python
from src.core.pillar242_planetary_coherence_cascade_resilience_engine import (
    N_W,    # int       5  — winding number = number of sectors (co-emergent identity)
    N_2,    # int       7  — braid partner
    K_CS,   # int       74 — Chern-Simons level = 5² + 7²
    C_S,    # float     12/37 ≈ 0.3243  — braided sound speed / cascade propagation rate
    XI_C,   # float     35/74 ≈ 0.4730  — consciousness coupling / HILS governance weight
    SECTORS,           # tuple of 5 sector names
    N_SECTORS,         # int  5  (== N_W)
    N_CASCADE_PAIRS,   # int  10 (== C(5,2))
    HOLON_THEORETICAL_CONFIDENCE,  # float 1.0 (26/26 SM parameters closed)
)
```

---

## `CascadeState` — Input Container

```python
from src.core.pillar242_planetary_coherence_cascade_resilience_engine import CascadeState

state = CascadeState(
    sector_adequacy={
        "civilizational_resilience": 0.48,   # P237 resilience_readiness_index()
        "health_system_surge":       0.58,   # P238 response_adequacy_index()
        "infrastructure_stability":  0.45,   # P239 safe_automation_envelope_index()
        "food_security":             0.48,   # P240 food_security_probability_surface()
        "planetary_warning":         0.54,   # P241 1 − global_risk_pulse()
    },
    phi_trust=1.0,   # HILS trust ∈ [0, 1]
    n_hil=5,         # aligned HIL operators ≥ 0
)
```

**Raises:** `ValueError` if any adequacy ∉ [0,1], phi_trust ∉ [0,1], n_hil < 0, or any sector is missing.

---

## Convenience Constructor

```python
from src.core.pillar242_planetary_coherence_cascade_resilience_engine import baseline_cascade_state

# Build from all five pillar baseline scenarios automatically
state = baseline_cascade_state(phi_trust=1.0, n_hil=5)
```

---

## Core Calculator Functions

### `hils_stability_weight(phi_trust, n_hil) → float`

OMEGA stability floor formula weighted by HILS trust:

```
floor(n) = min(1.0, C_S × (1 + n / N_2))
weight   = phi_trust × floor(n_hil)
```

| n_hil | floor | weight (phi_trust=1) |
|-------|-------|----------------------|
| 0  | 0.324 | 0.324 |
| 1  | 0.371 | 0.371 |
| 5  | 0.555 | 0.555 |
| 10 | 0.787 | 0.787 |
| 15 | 1.000 | 1.000 |

---

### `cascade_coupling_matrix(state) → dict[str, dict[str, float]]`

5×5 inter-sector cascade coupling matrix:

```
C[i, j] = C_S × (1 − adequacy_i) × (1 − adequacy_j)
C[i, i] = 0   (no self-coupling)
```

Symmetric: `C[i,j] = C[j,i]`.

---

### `cascade_penalty(state) → float`

Total cascade amplification penalty ∈ [0, 1]:

```
penalty = Σ_{i<j} C[i,j] / 10
```

0 = no cross-sector coupling (all sectors fully adequate).  
C_S = maximum cascade penalty (all sectors fully failing).

---

### `unified_planetary_readiness_index(state) → float`

**The UPRI** — the key novel output of the PCCRE:

```
UPRI = clamp(mean_adequacy × hils_weight × (1 − cascade_penalty))
```

Properties:
- Always ≤ naive mean of individual sector scores
- 0 when all sectors fail
- → 1 only when all sectors = 1, n_hil ≥ 15, phi_trust = 1

---

### `compound_cascade_failure_probability(state) → float`

Probability of runaway compound failure:

```
P_cascade = clamp(1 − geo_mean(adequacy) × (1 − cascade_penalty))
```

Uses geometric mean to ensure a single near-zero sector strongly
elevates the compound failure probability.

---

### `cross_sector_budget_allocation(state, total_budget_usd) → list[dict]`

Optimal cross-sector budget split sorted by cascade impact:

```
impact_i = gap_i × (1 + mean_coupling_to_others_i)
fraction_i = impact_i / Σ impact_j
```

Each entry: `{sector, adequacy, gap, cascade_impact_score, allocated_budget_usd, allocated_fraction}`.

**Raises:** `ValueError` if `total_budget_usd < 0`.

---

### `monte_carlo_upri(state, n_trials=200, seed=242) → dict`

UPRI robustness envelope under ±0.08 uniform noise on all sector adequacy scores.

Returns: `{mean_upri, p10_upri, p50_upri, p90_upri}`.  
**Raises:** `ValueError` if `n_trials < 1`.

---

### `sector_coherence_score(state) → float`

Measures how uniformly the five sectors perform:

```
coherence = clamp(1 − std(adequacy) / 0.5)
```

1.0 = all sectors at exactly the same level.  
0.0 = extreme variation (some sectors near 1, others near 0).

---

### `pccre_full_report(state, n_trials=200, budget_usd=1e9, seed=242) → dict`

Master computation — all PCCRE outputs in one call.

Keys: `pillar, status, co_emergent_insight, sector_count_equals_n_w,
sector_adequacy, sector_coherence_score, upri, upri_status,
compound_cascade_failure_probability, cascade_coupling_matrix,
cascade_penalty, hils_weight, budget_allocation, monte_carlo_upri,
holon_theoretical_confidence, falsification_condition`.

**UPRI status thresholds:**

| Range | Status |
|-------|--------|
| < 0.35 | UPRI_CRITICAL |
| 0.35 – 0.55 | UPRI_VULNERABLE |
| 0.55 – 0.75 | UPRI_RESILIENT |
| ≥ 0.75 | UPRI_ROBUST |

---

### `pillar242_pccre_report(n_trials=200, budget_usd=1e9, phi_trust=1.0, n_hil=1, seed=242) → dict`

Top-level one-call entry point. Builds a `CascadeState` from all five
pillar baseline scenarios, then runs `pccre_full_report`.

---

## HILS State and Sector Adequacy Sources

| Sector key | Source function | Source module |
|------------|----------------|---------------|
| `civilizational_resilience` | `resilience_readiness_index(scenario)` | pillar237 |
| `health_system_surge` | `response_adequacy_index(scenario)` | pillar238 |
| `infrastructure_stability` | `safe_automation_envelope_index(scenario)` | pillar239 |
| `food_security` | `food_security_probability_surface(scenario)` | pillar240 |
| `planetary_warning` | `1.0 − global_risk_pulse(scenario)` | pillar241 |

---

*CALCULATOR.md — pillar242-pccre/ — v10.57 — May 2026*  
*Theory: ThomasCory Walker-Pearson · Implementation: GitHub Copilot (AI)*
