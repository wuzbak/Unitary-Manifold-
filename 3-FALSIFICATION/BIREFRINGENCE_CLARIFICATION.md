# Birefringence Prediction Clarification — Unitary Manifold

*Unitary Manifold v20.9 — ThomasCory Walker-Pearson, 2026*
*Last updated: 2026-08-18*

> **This document is the single authoritative reference for birefringence β
> predictions in the Unitary Manifold.  If any other document quotes a β value
> without explaining which derivation path and sector it belongs to, this file
> takes precedence.**

---

## 1. The Two-Axis Structure

Four numerical β values appear in this repository.  They come from exactly
**two independent axes of variation** — conflating them is the source of all
apparent contradictions.

### Axis 1 — Which braid sector?

| Sector | k_CS | Source |
|--------|------|--------|
| (5,7) — **primary** | 74 = 5²+7² | Selected by Planck nₛ + BICEP r |
| (5,6) — shadow | 61 = 5²+6² | Second lossless braid pair |

### Axis 2 — Which Δφ derivation path?

| Path | Δφ | Assumptions | Status |
|------|----|-------------|--------|
| **Canonical FTUM** | ≈ 5.072 | FTUM fixed point only; J_KK = n_w·2π·√φ₀_bare, φ₀_bare = 1 | **Hardgate primary** |
| GW-radion | ≈ 5.380 | Goldberger-Wise potential; φ_min_bare = 18, J_RS(k=1, r_c=12) ≈ 1/√2; Δφ = φ_min × (1 − 1/√3) | Model-dependent variant |

### Resulting 2×2 table

|  | **(5,6) sector** | **(5,7) sector** |
|--|-----------------|-----------------|
| **Canonical FTUM Δφ** | β ≈ **0.273°** | β ≈ **0.331°** |
| GW-radion Δφ | β ≈ 0.290° | β ≈ 0.351° |

---

## 2. Which Values Are Primary (Preregistered)

The **preregistered** predictions, committed in
`3-FALSIFICATION/PREREGISTRATION/LITEBIRD_BETA_PREREGISTRATION.md`
(timestamp 2026-05-19), are the **canonical FTUM row**:

- **Primary:** β = 0.331° — (5,7) sector, canonical FTUM Δφ
- **Shadow:** β = 0.273° — (5,6) sector, canonical FTUM Δφ

These are the values used in `3-FALSIFICATION/FALSIFICATION_CONDITIONS.md` and
`3-FALSIFICATION/prediction.md`.  They are produced by:

```python
from src.core.inflation import cs_axion_photon_coupling, birefringence_angle
from src.core.inflation import phi0_effective

phi0_eff = phi0_effective(phi0_bare=1.0, n_winding=5)   # ≈ 31.42 (Δφ ≈ 5.072)
g_agg    = cs_axion_photon_coupling(k_cs=74, alpha_em=1/137.036, r_c=12.0)
beta_rad = birefringence_angle(g_agg, phi0_eff)         # canonical path
```

---

## 3. The GW-Radion Variants (Model-Dependent)

The values 0.351° and 0.290° are obtained by substituting a
**Goldberger-Wise inflaton** field displacement:

```python
phi_min_phys = jacobian_rs_orbifold(k=1, r_c=12) * 18.0   # ≈ 12.73
delta_phi    = field_displacement_gw(phi_min_phys)          # ≈ 5.380
```

This path requires two additional assumptions beyond the FTUM fixed point:
1. φ_min_bare = 18 (specific GW potential minimum — not derived from first principles)
2. The inflaton rolls from the inflection point φ*/√3 to φ_min (GW geometry)

The GW-radion path is a **valid secondary derivation** — it demonstrates that
the birefringence signal is robust under an alternative potential geometry.
It is NOT the primary prediction because it introduces assumptions not present
in the minimal FTUM framework.

---

## 4. The Inter-Sector Gap and Its Domain of Validity

`3-FALSIFICATION/FALSIFICATION_CONDITIONS.md` declares β ∈ (0.29°, 0.31°) a
falsification zone — "no viable state in that interval."

**Domain of validity of this claim:**

| Derivation path | Gap zone | Status |
|-----------------|----------|--------|
| Canonical FTUM only | (0.29°, 0.31°) | **Valid** — 0.273° and 0.331° are both outside |
| Including GW-radion | Must expand to (0.294°, 0.311°) | The (5,6) GW-radion value 0.290° approaches the lower boundary |

**Honest statement:**
> The inter-sector falsification gap (0.29°, 0.31°) is valid under the
> canonical FTUM derivation path.  If LiteBIRD measures β ≈ 0.29°,
> adjudicating between "GW-radion (5,6) confirmed" and "inter-sector gap
> falsification" requires CMB-S4 precision (σ_β ≈ 0.01°).

This does **not** weaken the primary falsification: a measurement anywhere
outside [0.22°, 0.38°] falsifies the braided-winding mechanism under both
paths simultaneously.

---

## 5. The Consciousness Coupling Usage

`3-FALSIFICATION/BIG_QUESTIONS.md` (Questions 21–22) uses β = 0.3513° as
the coupling constant in the adjacent-track consciousness attractor equation:

```
U_total = (U_brain ⊗ I) + (I ⊗ U_univ) + β · C
```

**Clarification:** This uses the **GW-radion full-derivation value** (0.3513°).
Under the canonical FTUM primary prediction (0.331°), the coupling shifts by
~6% — which is immaterial at the level of this 🔵 ADJACENT TRACK claim.
The equation structure and its qualitative conclusions are unchanged.
This usage should be read as "β ≈ 0.35° (GW-radion variant; canonical 0.331°)".

---

## 6. Which Document to Trust When Values Conflict

**Priority order (highest to lowest):**

1. This document (`3-FALSIFICATION/BIREFRINGENCE_CLARIFICATION.md`) — explains all values
2. `3-FALSIFICATION/PREREGISTRATION/LITEBIRD_BETA_PREREGISTRATION.md` — preregistered primary (0.331°/0.273°)
3. `3-FALSIFICATION/FALSIFICATION_CONDITIONS.md` — falsification thresholds (canonical FTUM)
4. `3-FALSIFICATION/prediction.md` — full prediction hierarchy with sector/path labels
5. `STATUS.md` and `README.md` — summary, always refers to canonical FTUM primary values
6. `VERIFY.py` — live consistency check, reports canonical FTUM β = 0.331° as PRIMARY

Documents quoting 0.351° or 0.290° without a path label (GW-radion) should be
treated as using the model-dependent variant. This does not constitute an error
in those documents — it reflects the existence of two valid derivation paths.

---

## 7. Code Reference

| Value | Function call | Path |
|-------|---------------|------|
| β = 0.331° | `birefringence_angle(cs_axion_photon_coupling(74,...), phi0_effective(1.0, 5))` | Canonical FTUM |
| β = 0.351° | `birefringence_angle(cs_axion_photon_coupling(74,...), field_displacement_gw(jacobian_rs_orbifold(1,12)*18))` | GW-radion |
| β = 0.273° | same as 0.331° with k_cs=61 | Canonical FTUM, (5,6) sector |
| β = 0.290° | same as 0.351° with k_cs=61 | GW-radion, (5,6) sector |

All four functions: `src/core/inflation.py`.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
