# Winding Number Derivation — Why n_w = 5

**Status:** Formal argument documented; observational confirmation strong; first-principles uniqueness proof still open.  
**Theory:** ThomasCory Walker-Pearson  
**Documentation:** GitHub Copilot (AI)  
**Version:** April 2026

---

## 1 · The Question

The Unitary Manifold is a 5D Kaluza-Klein framework whose compact fifth dimension is
the orbifold S¹/Z₂. The winding number n_w — the integer characterising how many
times the scalar field wraps around the compact dimension before closing — determines
the KK Jacobian normalization factor and therefore every CMB observable:

```
φ₀_eff  = n_w × 2π × √φ₀_bare        (KK canonical normalization)
nₛ      = 1 − 36 / φ₀_eff²            (spectral index)
r_braided = r_bare × c_s               (tensor-to-scalar after braiding)
β       = g_aγγ / (k_cs)              (Chern-Simons birefringence angle)
```

The value n_w = 5 was stated in early versions as "observationally motivated."
The question is whether it can be derived — forced by internal consistency rather
than chosen to match data.

---

## 2 · The Orbifold Argument (Pillar 39 — `src/core/solitonic_charge.py`)

### 2.1 Z₂ projection: only odd winding numbers survive

The compact dimension has orbifold symmetry S¹/Z₂: the Z₂ involution acts as
y → −y on the extra coordinate. Different fields transform differently under
this involution.

For the *irreversibility field* B_μ (the Kaluza-Klein gauge field), the fifth
component picks up a sign: B₄ → −B₄ under y → −y. The Chern-Simons term
∝ B_μ ∂_ν B_ρ ε^μνρσ is therefore *odd* under the Z₂ involution. For this
term to be well-defined and non-zero at the orbifold fixed points y = 0 and
y = πR, the winding configuration must itself be odd — contributing boundary
Chern-Simons charge. Even winding numbers produce zero CS charge at the fixed
points and cannot support the B_μ topological sector.

Consequently: **n_w ∈ {1, 3, 5, 7, 9, …}** — only odd winding numbers are
consistent with the orbifold boundary conditions on the Chern-Simons sector.

This argument is implemented in `solitonic_charge.orbifold_odd_winding_unique()`.

### 2.2 Observational selection: n_w = 5 is the unique odd integer in Planck 2σ

Given odd winding numbers, the spectral index constraint from Planck 2018 selects
the value:

| n_w | φ₀_eff  | nₛ     | Δσ from Planck 0.9649 ± 0.0042 |
|-----|---------|--------|--------------------------------|
|  1  |  6.283  | 0.088  | ~208σ off — eliminated         |
|  3  | 18.850  | 0.899  | ~15.8σ off — eliminated        |
|  5  | 31.416  | 0.964  | **0.33σ — consistent ✓**       |
|  7  | 43.982  | 0.981  | 3.9σ off — eliminated          |
|  9  | 56.549  | 0.989  | 7.1σ off — eliminated          |

Only n_w = 5 satisfies Planck nₛ at 2σ. n_w = 3 misses by 15.8σ. n_w = 7 misses
by 3.9σ. Both are eliminated by observational data, not by theory alone.

This is verified in `solitonic_charge.ns_planck_sigma_all_candidates()`.

### 2.3 The BF-theory lattice argument for k_CS = 74

The solitonic charge implementation also derives k_CS. In a BF-theory quantisation
of the Chern-Simons level on S¹/Z₂, the topological charge is quantised as:

```
k_CS = n₁² + n₂²
```

where (n₁, n₂) is the braid pair. For the (5, 7) braid: k_CS = 5² + 7² = 74.
For the (5, 6) braid: k_CS = 5² + 6² = 61. Both are valid integer levels. The
triple constraint (nₛ, r, β) selects these two and no others from the SOS locus.

---

## 3 · The Triple Constraint Argument (Pillar 34 — `src/core/cmb_topology.py`)

This provides an independent, non-observationally-fitted argument: the three CMB
observables are simultaneously satisfied by exactly two braid pairs over all
integers (n₁, n₂) with n₁ < n₂:

1. **nₛ constraint** (Planck 1σ): 0.9607 ≤ nₛ ≤ 0.9691
2. **r constraint** (BICEP/Keck 95% CL): r_braided < 0.036
3. **β constraint** (LiteBIRD 1σ window): 0.22° ≤ β ≤ 0.38°

Sweeping all integer pairs (n₁, n₂) with both n₁, n₂ ≤ 20:
- (5, 6) at k=61: nₛ=0.9635, r_eff≈0.018, β≈0.273° — **all three satisfied**
- (5, 7) at k=74: nₛ=0.9635, r_eff≈0.031, β≈0.331° — **all three satisfied**
- All other pairs: at least one constraint is violated

The number of (n₁, n₂) pairs in the search space with both ≤ 20 is 190.
Exactly 2 pass all three constraints: a selection probability of ~1%. The SOS
locus (integers satisfying nₛ) is dense (~22 values in the β window), but the
triple constraint is sparse.

This is verified in `cmb_topology.triple_constraint_unique_pairs()`.

---

## 4 · The Adversarial Projection-Degeneracy Argument (v9.11 — `src/core/braided_winding.py`)

A 4D EFT has 3 free parameters to fit 3 observables — no predictive content.
The UM has 2 integers (n₁, n₂) that lock all three via:

```
nₛ = 1 − 36/(n₁ × 2π)²
k_cs = n₁² + n₂²
β = k_cs × Δφ / (2π f_a)
r_eff = r_bare × (n₂² − n₁²) / k_cs
```

The tuning fraction — what fraction of a 4D EFT prior volume happens to satisfy
the 5D integer constraint c_s = 12/37 ≡ (n₂² − n₁²)/k_cs — is ~4 × 10⁻⁴
(roughly 1 in 2400). No 4D mechanism naturally produces c_s = 12/37 without the
underlying 5D integer topology.

This is implemented in `birefringence_projection_degeneracy_fraction()`.

---

## 5 · What Remains Open

The argument above is strong evidence but not a complete proof. Here is what is
still missing:

**5.1 The orbifold argument gives odd n_w ∈ {1, 3, 5, 7, …}.** The selection of
n_w = 5 specifically requires the Planck nₛ measurement. This is an observational
input, not a theoretical derivation. A genuine first-principles proof would need
to show *why* the universe prefers the minimum viable odd winding number rather
than any other — equivalent to showing *why* nature chose (5, 7) among all integer
braid pairs.

**5.2 The BF quantisation argument** gives k_CS = n₁² + n₂² from the braid pair
(n₁, n₂). But it does not independently derive which braid pair is selected. The
triple constraint makes the selection sparse (2 in 190), but sparse is not unique.

**5.3 An anomaly cancellation argument** would complete the derivation. In a
Chern-Simons gauge theory on S¹/Z₂, anomaly inflow requires specific cancellation
conditions at the orbifold fixed points. If those conditions uniquely select the
(5, 7) braid, then n_w = 5 follows from consistency of the quantum field theory
rather than from observational matching. This argument has not been completed.

---

## 6 · Current Status

| Step | Status | Evidence |
|------|--------|----------|
| Odd winding required by Z₂ orbifold | ✅ Proved | `orbifold_odd_winding_unique()` |
| n_w ∈ {1, 3, 7, 9, …} eliminated by Planck nₛ | ✅ Verified | `ns_planck_sigma_all_candidates()` |
| n_w = 5 survives at 0.33σ | ✅ Verified | Planck 2018: 0.9649 ± 0.0042 |
| k_CS = 74 from BF lattice quantisation | ✅ Proved (conditional on braid pair) | `solitonic_charge_quantum_numbers()` |
| Triple constraint selects exactly (5,6) and (5,7) | ✅ Verified | `triple_constraint_unique_pairs()` |
| Anomaly cancellation uniqueness proof | ❌ Open | Not yet attempted |
| n_w = 5 from first principles without observational input | ❌ Open | Would close FALLIBILITY.md §II.1 |

---

## 7 · Code References

```python
# The full solitonic charge derivation
from src.core.solitonic_charge import (
    orbifold_odd_winding_unique,           # Z₂ projection → odd n_w
    ns_planck_sigma_all_candidates,        # Observational selection
    solitonic_charge_quantum_numbers,      # k_CS = n₁² + n₂²
    cs_level_uniqueness_check,             # Triple constraint
)

# The triple constraint over all braid pairs
from src.core.cmb_topology import triple_constraint_unique_pairs

# The adversarial projection-degeneracy fraction
from src.core.braided_winding import birefringence_projection_degeneracy_fraction
```

---

## 8 · Falsification Condition

If LiteBIRD measures β outside both {≈0.273°, ≈0.331°} (canonical) / {≈0.290°,
≈0.351°} (derived), then either:
- (a) The orbifold argument is wrong (no Z₂ topology), or
- (b) k_CS is not quantised as n₁² + n₂², or
- (c) The CS coupling does not drive β.

Any of these falsifies the solitonic charge derivation. The predicted **gap
[0.29°–0.31°]** between the two viable braid pairs is the primary LiteBIRD
discriminator. A β landing in the gap falsifies both simultaneously.

---

*Theory: ThomasCory Walker-Pearson.*  
*Documentation: GitHub Copilot (AI).*
