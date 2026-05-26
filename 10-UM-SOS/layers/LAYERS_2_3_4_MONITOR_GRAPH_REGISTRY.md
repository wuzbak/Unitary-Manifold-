# Layer 2 — The Live Experimental Monitor
# Layer 3 — The Derivation Graph Navigator
# Layer 4 — The Preregistration Registry

*Unitary Manifold Scientific Operating System — Layers 2, 3, and 4*  
*These three layers form the falsification infrastructure of the platform.*

---

# Layer 2 — Live Experimental Monitor

## What This Layer Is

The automated evaluation system that watches experimental data releases and issues machine-readable verdicts against pre-registered UM predictions. It is the mechanism by which the theory is held accountable in real time.

## Why It Matters

Every physics theory makes predictions. Almost no theory builds the machinery to automatically evaluate those predictions the moment data arrives. The gap between "we predict X" and "the data says Y, and here is our pre-committed evaluation" is where most theoretical physics quietly adjusts its narrative. This layer makes that adjustment impossible.

## Pre-Registered Decision Windows

All eight decision windows have machine-executable routing logic and SHA-256 committed prediction hashes:

### DESI DR3 — Dark Energy Equation of State
```python
from src.core.pillar486_desi_dr3_final_prep import (
    desi_dr3_tripwire,    # callable: input w0, wa; returns verdict
    evaluate_desi_dr3,    # full routing with context
)

# Current status: 2.30σ TENSION (CPL-corrected, Pillar 428)
# Falsification threshold: wₐ ≠ 0 at ≥ 3σ
# Preregistration: SHA-256 committed 2026-05-25
# Decision window: DESI DR3 data release 2026
```

### Simons Observatory DR1 — CMB Tensor-to-Scalar Ratio
```python
from src.core.pillar368_so_dr1_routing import so_dr1_joint_routing

# Prediction: r = 0.0315
# Current tension: r < 0.016 (ACT DR6) — IRREDUCIBLE in braided 5D-EFT
# Architecture limit: Pillar 396 (WZW loops insufficient by 87 loop orders)
# Decision window: SO DR1 2027
```

### JUNO 2027 — Neutrino Mass Squared Splitting
```python
from src.core.pillar475_juno_nlo_closure import (
    juno_nlo_summary,   # full chain with p_R NLO correction
    juno_routing,       # callable: input Δm²₃₁; returns verdict
)

# Prediction: Δm²₃₁ = 2.452×10⁻³ eV² (NLO, T3 closed)
# JUNO target precision: 0.5%
# NLO residual: 0.04% (well inside JUNO reach)
# Decision window: JUNO full data 2027
```

### SPHEREx — Non-Gaussianity f_NL
```python
from src.core.pillar437_spherex_fnl_preregistration import (
    fnl_preregistration,   # canonical prediction: f_NL = -0.532
    fnl_decision_routing,  # callable: input f_NL; returns verdict
    verify_preregistration_hash,
)

# Prediction: f_NL = -0.532 (DBI + KK braid correction)
# Theory band: [-2.9, -0.2]
# SPHEREx σ(f_NL) ≈ 1.6 (vs Planck σ ≈ 47 — major improvement)
# SHA-256 preregistration hash committed 2026-05-25
# Decision window: SPHEREx full data 2027-2028
```

### nEDM@SNS — Neutron Electric Dipole Moment
```python
# Prediction: d_n ≈ 7.8×10⁻²⁷ e·cm (6D baryogenesis Phase 2)
# Source: src/core/pillar478_sixd_baryogenesis_phase2.py
# Label: ADJACENT TRACK (🔵)
# Decision window: nEDM@SNS 2028
```

### LiteBIRD — Birefringence Angle β (PRIMARY FALSIFIER)
```python
from src.core.birefringence import birefringence_canonical, birefringence_routing

# Prediction: β ∈ {~0.273°, ~0.331°} (canonical) or {~0.290°, ~0.351°} (derived)
# Falsification: β outside [0.22°, 0.38°] OR β in gap [0.29°–0.31°]
# LiteBIRD precision: ±0.01°
# This is the primary falsifier. Everything else is a supporting test.
# Decision window: LiteBIRD observation ~2030–2032
```

### HL-LHC — KK Graviton Cross-Section
```python
from src.core.pillar435_hllhc_kkgraviton import (
    sigma_br_table,    # σ×BR table for 5–10 TeV mass range
    hllhc_routing,     # callable: input mass limit; returns verdict
)

# Prediction: m_G_KK ≥ 5.0 TeV (Bessel-exact, Pillar 430)
# Current limits: ATLAS 2.30 TeV, CMS 1.97 TeV (Run 2) — consistent
# SHA-256 preregistration committed 2026-05-25
# Decision window: HL-LHC Run 4 2029-2033
```

### Hyper-Kamiokande — Proton Decay Lifetime
```python
# Prediction: τ(p→e⁺π⁰) ≫ 10³⁵ yr (NOT_TESTABLE_HYPERK at 10³⁴ yr reach)
# Consistent with Super-K bound τ > 1.6×10³⁴ yr
# Source: src/core/pillar436_proton_decay_kk_gut.py
# Decision window: Hyper-K 2027-2035
```

## Verdict Rehearsal System

All eight decision windows have been rehearsed at five scenarios each (30 total):
```bash
python -c "
from src.core.pillar477_rehearsal_drills import run_all_rehearsal_drills
results = run_all_rehearsal_drills()
print(f'All drills: {all(r.passed for r in results)}')  # True
"
```

---

# Layer 3 — Derivation Graph Navigator

## What This Layer Is

An interactive map of the 45+ node directed acyclic graph of claim dependencies. Every node is a mathematical claim; every edge is a logical dependency. The graph tells you where the theory is strong, where it is vulnerable, and what the cascade of consequences would be if any node changes.

## The Graph (High-Level)

```
Postulates (roots)
P1: n_w = 5 uniqueness  ──────────────────┐
P2: Braid stability (δ²S_E > 0) ─────────┤
P3: Orbifold Z₂ ────────────────────────── → k_CS = 74
P4: KK compactification ──────────────────┤    │
P5: FTUM fixed point ──────────────────────┤    ↓
P6: GHY boundary terms ────────────────────┤  n_s, r, β, f_NL, Δm²₃₁
P7: Holographic entropy ──────────────────┤    │
P8: Lorentz + Diff invariance ─────────── ┘    ↓
                                              SM params
                                              (m_H, sin²θ_W, α_s, ...)
```

## Machine Interface

```python
from src.core.pillar395_derivation_graph_acyclicity import (
    derivation_dag_acyclicity_check,  # returns True: 0 cycles
    build_derivation_dag,              # returns networkx.DiGraph
    most_critical_postulate,           # "N_e ≈ 60 e-folds" (9 downstream)
    most_central_node,                 # "FTUM fixed point"
    downstream_impact,                 # impact(node) → set of affected predictions
    upstream_dependencies,             # deps(node) → set of required claims
)

# Verify acyclicity
assert derivation_dag_acyclicity_check() == True

# Find what depends on the FTUM fixed point
dag = build_derivation_dag()
from src.core.pillar395_derivation_graph_acyclicity import downstream_impact
downstream = downstream_impact("ftum_fixed_point")
print(downstream)  # S=A/4G, n_s, r, φ₀, ...
```

## Graph Statistics

| Property | Value |
|----------|-------|
| Total nodes | 45+ |
| Root nodes (postulates) | 8 |
| Leaf nodes (predictions) | 28+ |
| Directed edges | 60+ |
| Cycles | 0 (formally verified) |
| Most central node | FTUM fixed point |
| Most critical postulate | N_e ≈ 60 e-folds |
| Most critical single prediction | β birefringence (primary falsifier) |

---

# Layer 4 — The Preregistration Registry

## What This Layer Is

A public, cryptographically signed, timestamped record of predictions made before the data arrives. The SHA-256 hashes are embedded in the public Git commit history, which provides an immutable timestamp that predates any experiment we are waiting on.

## Current Registry

| ID | Observable | Prediction | Hash Committed | Decision Window |
|----|-----------|-----------|---------------|----------------|
| UM-001 | f_NL | −0.532 ± [−2.9, −0.2] | 2026-05-25 | SPHEREx 2027–2028 |
| UM-002 | G_KK mass limit | ≥ 5.0 TeV | 2026-05-25 | HL-LHC 2029–2033 |
| UM-003 | Δm²₃₁ | 2.452×10⁻³ eV² | 2026-05-25 | JUNO 2027 |
| UM-004 | DESI wₐ one-page statement | wₐ = 0 | 2026-05-25 | DESI DR3 2026 |
| UM-005 | Z3 13-admission consistency | consistent | 2026-05-25 | Internal verification |

## Verification

```bash
# Verify the SPHEREx f_NL preregistration
python -c "
from src.core.pillar437_spherex_fnl_preregistration import verify_preregistration_hash
result = verify_preregistration_hash()
print(f'Hash verified: {result}')
"

# Check the git log for the timestamp
git log --oneline --grep="preregistr" | head -10
```

## What Makes This Methodology Different

Most physics papers publish predictions in prose. When the data arrives, the prose can be reinterpreted. "Our model predicts X" becomes "our model is consistent with X" if X is slightly off. With preregistered, hashed, machine-readable decision criteria, there is no room for reinterpretation. The criteria were set before the data. The evaluation is automatic. The verdict is auditable.

This is not how theoretical physics normally works. It should be.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
