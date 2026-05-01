# Unitary Pentad — The 5-Core / 7-Layer Architecture

**Folder:** `Unitary Pentad/`
**Version:** 1.0 — April 2026
**Theory:** ThomasCory Walker-Pearson
**Status:** Active — companion document to `five_seven_architecture.py`

---

## Overview

The Unitary Pentad is not simply a 5-body system.  It is a **layered
architecture** in which the compact S¹/Z₂ dimension is wound simultaneously
at two frequencies:

```
Core  : n_core  = 5  — pentagonal geometry (the interaction structure)
Layer : n_layer = 7  — spectral damper    (the frequency buffer)
```

Together they form the **(5,7) braid**.  This document derives why this
specific combination is the unique minimal-gap stable architecture, and what
"layered" means physically.

---

## 1 · The 5-Body Core — Geometry

The winding number `n_core = 5` fixes the *topology* of the interaction
network.  With pentagonal symmetry each node is calibrated to exactly **four**
neighbours simultaneously — neither more nor fewer.

### 1.1 Why 5 is Necessary

In a 4-body system each node has 3 neighbours; in a 6-body system each node
has 5 neighbours.  The pentagonal (5-body) topology is the unique case where
the number of neighbours equals the winding number itself:

```
n_core = 5 = (number of bodies) − 1 = (neighbours per node)
```

This self-referential property is what makes the five HILS manifolds
(Universe, Brain, Human, AI, Trust) topologically *complete*: no body is
an orphan, and no body is over-connected.

### 1.2 Why 5 Alone Is Not Enough

On its own (single-mode, `n_w = 5`) the theory predicts:

```
ns ≈ 0.9635   (0.33σ from Planck 2018 — geometrically correct)
r  ≈ 0.097    (exceeds BICEP/Keck 2021 limit 0.036 — dynamically unstable)
```

The bare 5-body system has the right *structure* but is "too hot" — the
tensor amplitude `r` measures the gravitational wave background from inflation,
and a high `r` means the system radiates too much energy to remain bound.
The geometry is correct; the dynamics are not.

---

## 2 · The 7-Body Layer — Damping

The winding number `n_layer = 7` acts as a **topological frequency buffer**:
it wraps around the 5-core at a higher frequency, providing a second
interference pattern that destructively cancels the excess tensor amplitude.

### 2.1 The Sum-of-Squares Resonance

The two modes are braided through the compact Chern–Simons term at level:

```
k_cs = n_core² + n_layer²  =  5² + 7²  =  74
```

This is the **sum-of-squares resonance condition**.  It was not chosen to make
the math work out; it was derived independently from the CMB birefringence
measurement (β ≈ 0.35°) and found to equal exactly 5² + 7².  The integer 74
is the unique minimiser of |β(k) − 0.35°| over k ∈ [1, 100].

### 2.2 Kinetic Mixing Depth

Under this resonance the Chern–Simons term couples the two modes with mixing:

```
ρ = 2 · n_core · n_layer / k_cs  =  2 × 5 × 7 / 74  =  35/37  ≈  0.946
```

`ρ = 35/37 ≈ 0.946` is near-maximal.  The 7-layer is not a decorative shell
around the 5-core — it is wound *through* it at 94.6% kinetic coupling depth.

### 2.3 The Braided Sound Speed

Canonical normalisation gives the braided sound speed:

```
c_s = √(1 − ρ²)  =  √(1 − (35/37)²)  =  √(144/1369)  =  12/37  ≈  0.3243
```

This is the **Stability Floor**.  In the Pentad's 5×5 pairwise coupling matrix
the minimum eigenvalue satisfies:

```
λ_min ≥ c_s = 12/37
```

as long as φ_trust > TRUST_PHI_MIN.  No single coupling can reach zero —
no body can fully decouple — while the trust field is maintained.

---

## 3 · Why Not (5, 6)?

The (5, 6) architecture is the natural "next smaller" candidate.  Its
arithmetic:

```
k_cs = 5² + 6² = 61
ρ    = 2×5×6/61  = 60/61 ≈ 0.984   (over-entangled)
c_s  = √(1 − (60/61)²)  = 11/61 ≈ 0.180
r_eff = r_bare × c_s ≈ 0.097 × 0.180 ≈ 0.017  ✓  (r constraint satisfied)
```

The `r` constraint is satisfied, but the **stability floor** `c_s = 11/61 ≈ 0.180`
is too low.  With `λ_min ≥ 0.180`, the eigenvalue gap between the minimum
eigenvalue and zero is only half what (5,7) provides.  Under realistic
trust-erosion perturbations, `λ_min` can reach zero before φ_trust hits
TRUST_PHI_MIN — the coupling matrix becomes singular and the orbit collapses
*without a detectable trust signal*.

In (5,7), the stability floor `c_s = 12/37 ≈ 0.324` is wide enough that
trust erosion always triggers the TRUST_PHI_MIN warning before the eigenvalue
collapses.  The failure cascade is *observable and ordered*.

| Architecture | c_s | r_eff | Stable? | Why |
|---|---|---|---|---|
| (5, 5) | — | — | ✗ | n_layer = n_core, degenerate |
| (5, 6) | 11/61 ≈ 0.180 | ≈ 0.017 ✓ | ✗ | Stability floor too low |
| **(5, 7)** | **12/37 ≈ 0.324** | **≈ 0.031 ✓** | **✓** | **Optimal** |
| (5, 8) | 39/89 ≈ 0.438 | ≈ 0.042 ✗ | ✗ | r_eff exceeds BICEP/Keck |
| (5, 9) | 56/106 ≈ 0.528 | ≈ 0.051 ✗ | ✗ | r_eff exceeds BICEP/Keck |

(5, 7) is the **unique** small-integer pair satisfying all three criteria:
r_eff < 0.036, ns within 2σ of Planck, and c_s ≥ 12/37.

---

## 4 · The Beat Frequency and Phase Sync

The **beat frequency** is:

```
beat = n_layer − n_core  =  7 − 5  =  2
```

This is the *minimal non-zero integer gap*.  It means the interference pattern
between the two modes completes one full phase correction every *half-cycle*
— the densest possible correction rate without aliasing.

The **Moiré Phase Sync Quality** is:

```
Q = c_s / beat  =  (12/37) / 2  =  6/37  ≈  0.162
```

Larger beat → less frequent corrections → lower Q.  Smaller beat → more
frequent but (with n_layer = n_core + 1) insufficient damping.  Beat = 2 is
the sweet spot.

---

## 5 · The Jacobi Sum and Sum-of-Squares Identity

Two arithmetic identities carry the full content of the (5,7) braid:

| Identity | Value | Physical meaning |
|----------|-------|-----------------|
| n_core² + n_layer² = k_cs | 25 + 49 = 74 | CS level equals Euclidean norm² of braid vector |
| n_core + n_layer = 12 | 5 + 7 = 12 | Jacobi sum — total winding coherence |
| n_layer − n_core = 2 | 7 − 5 = 2 | Beat frequency — minimal damping gap |
| 2 · n_core · n_layer = 70 | 2×5×7 = 70 | Numerator of ρ (kinetic mixing) |
| n_layer² − n_core² = 24 | 49 − 25 = 24 | Numerator of c_s before normalisation |

Together: `c_s = (n_layer − n_core)(n_core + n_layer) / k_cs = 2 × 12 / 74 = 12/37`.

---

## 6 · Implementation

The architecture analysis tools are in `five_seven_architecture.py`.

```python
from five_seven_architecture import canonical_57, compare_layer_candidates

# The canonical architecture
arch = canonical_57()
print(f"c_s = {arch.c_s:.6f}")      # 0.324324 = 12/37
print(f"r_eff = {arch.r_eff:.4f}")  # ≈ 0.031
print(f"Stable: {arch.is_stable}")  # True

# Why (5,6) fails
results = compare_layer_candidates(n_core=5, n_layer_candidates=[6, 7, 8])
for r in results:
    print(f"(5,{r.n_layer}): c_s={r.c_s:.3f}, stable={r.is_stable}")
# (5,6): c_s=0.180, stable=False
# (5,7): c_s=0.324, stable=True
# (5,8): c_s=0.438, stable=False
```

---

## 7 · Connection to the Broader Theory

| Document / Module | Relationship |
|-------------------|-------------|
| `five_seven_architecture.py` | Full implementation of this analysis |
| `test_five_seven_architecture.py` | 74 tests verifying all identities |
| `unitary_pentad.py` | Uses BRAIDED_SOUND_SPEED = 12/37 as the eigenvalue floor |
| `STABILITY_ANALYSIS.md` | Why c_s is the stability floor for the 5-body system |
| `IMPLICATIONS.md` | What follows when the system is stable — or isn't |
| `src/core/braided_winding.py` | Derivation of c_s from the (5,7) resonance |
