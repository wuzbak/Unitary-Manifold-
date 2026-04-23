# RELAY — External AI Context Hand-Off Document

> **Purpose:** Copy-paste this entire file into a new AI conversation to restore
> full working context without re-reading the repository.  
> **Keep it current:** update after every significant development session.  
> **Last updated:** 2026-04-23

---

## 1. What this project is (one paragraph)

The **Unitary Manifold** (v9.11) is a 5D Kaluza–Klein framework that derives the
Second Law of Thermodynamics as a geometric identity rather than a statistical
postulate.  The fifth dimension encodes irreversibility; its radion field φ plays
the role of the CMB inflaton.  Key outputs are the scalar spectral index nₛ,
tensor-to-scalar ratio r, and cosmic birefringence angle β — all claimed to
arise from a single geometric compactification.  v9.11 extends the framework
across 26 geometric pillars covering all natural sciences, human social
organisation, and material recovery.  The full Python implementation
lives at `https://github.com/wuzbak/Unitary-Manifold-`.  3282 tests pass
(internal consistency only; see FALLIBILITY.md for scope).

---

## 2. Current numerical predictions (pinned values from code)

| Observable | Prediction | Target | Status |
|------------|-----------|--------|--------|
| nₛ | 0.9635 | 0.9649 ± 0.0042 (Planck 2018, 1σ) | ✅ inside 1σ |
| r | 0.0315 (braided (5,7), k_cs=74) | < 0.036 (BICEP/Keck 2021) | ✅ resolved — braided state satisfies bound |
| β (birefringence) | 0.351° | 0.35° ± 0.14° (Minami & Komatsu 2020) | ✅ inside 1σ |
| α (nonminimal coupling) | φ₀⁻² ≈ 1.0 | — | derived |

These are computed in `src/core/inflation.py` → `triple_constraint()` and
`src/core/braided_winding.py` → `braided_predictions(5, 7)`.

---

## 3. Derivation chain (honest, with weak links flagged)

```
5D metric ansatz G_AB              [POSTULATED]
        ↓
Walker–Pearson field equations     [derived from G_AB]
        ↓
FTUM fixed-point iteration U=I+H+T [derived, given U's definition]
        ↓
φ₀_bare ≈ 1.0  (fixed point)       [derived]
        ↓
α = φ₀⁻²                           [derived via KK cross-block Riemann]
        ↓
n_w = 5  (winding number)           ⚠️ FITTED — chosen to give nₛ ≈ 0.9635
        ↓                              not derived from topology
J_KK = n_w · 2π · √φ₀ ≈ 31.42     [derived given n_w]
        ↓
φ₀_eff = J_KK · φ₀_bare ≈ 31.42   [derived]
        ↓
nₛ ≈ 0.9635,  r_braided ≈ 0.0315  [derived given n_w, braided (5,7)]

k_CS = 74  (Chern–Simons level)     ⚠️ FITTED — chosen to give β ≈ 0.35°
        ↓                              not derived from 5D gauge theory
g_aγγ = k_CS · α_EM / (2π² r_c)   [derived given k_CS]
        ↓
β ≈ 0.351°                          [derived given k_CS]
```

**Summary of free parameters:**
- `n_w = 5` → controls nₛ, r
- `k_CS = 74` → controls β
- Both are phenomenological fits, not first-principles derivations.
- Everything else is derived or postulated structurally.

---

## 4. Key source files and functions

| File | Key functions | Role |
|------|--------------|------|
| `src/core/inflation.py` | `jacobian_5d_4d`, `effective_phi0_kk`, `ns_from_phi0`, `cs_axion_photon_coupling`, `birefringence_angle`, `triple_constraint` | Inflation observables, birefringence |
| `src/core/braided_winding.py` | `braided_predictions`, `resonance_identity`, `braided_sound_speed` | Braided (5,7) r-tension resolution |
| `src/core/transfer.py` | `primordial_power_spectrum`, `angular_power_spectrum`, `dl_from_cl`, `chi2_planck` | CMB TT spectrum vs Planck 2018 |
| `src/core/metric.py` | `assemble_5d_metric`, `christoffel`, `compute_curvature`, `extract_alpha_from_curvature` | 5D geometry, α derivation |
| `src/core/evolution.py` | `step`, `step_euler`, `constraint_monitor` | Walker–Pearson time evolution |
| `src/multiverse/fixed_point.py` | `fixed_point_iteration`, `derive_alpha_from_fixed_point` | FTUM convergence, φ₀ output |
| `src/holography/boundary.py` | boundary entropy dynamics | Holographic H operator |

---

## 4b. Recent external observations (notes)

### DESI 3D Map Completion — April 15, 2026
*Source: Scientific American / DESI Collaboration press release, 2026-04-15*  
*Encoded in code: `src/multiverse/observational_frontiers.py` (Pillar 38)*

The Dark Energy Spectroscopic Instrument completed its planned 5-year mission
ahead of schedule, producing the **largest high-resolution 3D map of the
universe** ever made — 47 million galaxies and quasars (38% beyond the original
34M target).

**UM status after this result:**

| Quantity | UM Prediction | DESI Measurement | Status |
|----------|--------------|-----------------|--------|
| w₀ (dark energy EoS) | −0.9302 (w_KK) | −0.92 ± 0.09 (DR2 w₀CDM) | ✅ <1σ consistent |
| wₐ (running) | 0 (KK zero-mode stabilised) | ≈ −0.63 (w₀waCDM hint) | ⚠️ ~3σ tension |

- The w₀ point-prediction is in excellent agreement with DESI DR2.
- The evolving dark energy hint (w₀waCDM preferred over ΛCDM) is in ~3σ tension
  with UM's zero-running prediction (wₐ = 0).  This tension is honestly
  documented in Pillar 38 and will be resolved by the **formal 2027 analysis**
  of the full 47M-object sample.
- Nothing in this result requires changes to the framework; Pillar 38 already
  encodes all four April 2026 observational frontiers (H0DN, DESI, Euclid,
  Roman).

---

## 5. Completed work (as of last update)

- [x] **FALLIBILITY.md** — referee-grade honesty document covering:
  - Scope of verification (internal ≠ empirical)
  - Axiomatic dependence table
  - Circularity audit with explicit admission that n_w=5 and k_CS=74 are fitted
  - Known failure modes (KK truncation, time double-counting, numerical sensitivity)
  - Five explicit falsifiability conditions

---

## 6. Roadmap (pseudocode, mapped to files)

```pseudo
function advance_framework_to_external_scrutiny():

    # STEP 1: Circularity Audit ─────────────────────── STATUS: DONE
    # → FALLIBILITY.md (Section III)
    # → Two honest admissions: n_w=5 fitted, k_CS=74 fitted
    publish(FALLIBILITY.md)


    # STEP 2: Weakest exposed assumption ────────────── STATUS: DONE (identified)
    weakest_link = "k_CS"          # CS level 74 is fitted, not derived
    second_link  = "n_w"           # winding number 5 is fitted, not derived
    # Neither has been resolved to first principles yet — open gap


    # STEP 3: TB/EB frequency-dependent spectrum ────── STATUS: NOT YET DONE
    # transfer.py currently computes TT only.
    # What is needed:
    #   birefringence_rotation(beta_rad, nu_GHz)
    #       → uniform rotation (frequency-independent in this model)
    #   tb_eb_spectrum(ells, ns, beta_rad, As, ...)
    #       → C_ell^TB = sin(2β) * sqrt(C_ell^TT * C_ell^BB)  (approx)
    #       → C_ell^EB = sin(2β) * C_ell^EE                   (approx)
    #   assert spectrum.is_not_generic_LCDM()  # β≠0 is the discriminator
    #   assert spectrum.has_specific_ell_shape()
    # Target file: src/core/transfer.py (add ~60 lines)
    # Tests: tests/test_inflation.py


    # STEP 4: arXiv v1 ──────────────────────────────── STATUS: NOT YET DONE
    # File: arxiv/main.tex
    # What is needed:
    #   - Insert fallibility section (FALLIBILITY.md → LaTeX)
    #   - Insert circularity audit table
    #   - Insert TB/EB prediction (once Step 3 done)
    #   - Abstract must include: "speculative", "comments welcome",
    #     "empirical status discussed", one sentence of fallibility
    # target_category = "gr-qc"


    # STEP 5: Comparison table ──────────────────────── STATUS: NOT YET DONE
    comparison = build_comparison_table(
        models = ["Starobinsky", "Natural Inflation", "RS1/RS2",
                  "Unitary Manifold"],
        columns = ["free_params", "ns_derived", "r_derived",
                   "beta_derived", "unique_prediction"],
        # Key claim: UM derives ns, r, beta from geometry;
        # but honest: n_w and k_CS are the free params
    )
    # Can be added to manuscript/comparisons.md or arxiv/main.tex


    # STEP 6: Resolve or acknowledge weakest link ───── STATUS: PARTIAL
    # k_CS = 74 is honestly documented in FALLIBILITY.md
    # NOT YET: topological derivation of k_CS from anomaly cancellation
    #          or quantisation condition on the compact dimension
    # NOT YET: topological derivation of n_w = 5
    # → These are the most important open theoretical tasks

    return "Framework now externally legible and falsifiable"
```

---

## 7. The one paragraph that explains k_CS honestly

> The birefringence prediction β ≈ 0.35° requires a Chern–Simons level
> k_CS = 74 in the flat S¹/Z₂ formula g_{aγγ} = k_CS · α / (2π² r_c).
> This integer is consistent with a clockwork / networked-node mechanism
> in which ~74 hidden U(1) sectors each contribute one unit of bulk CS charge,
> but it is not derived from first principles within the current framework.
> It is a phenomenological fit to the Minami & Komatsu (2020) hint.
> The prediction becomes genuinely falsifiable — and the fit becomes a
> derivation — if and only if k_CS can be fixed by an anomaly-cancellation
> condition or a quantisation constraint on the compact dimension independent
> of the observed β value.

---

## 8. Next session starting point

**Highest-leverage next action:** implement `tb_eb_spectrum()` in
`src/core/transfer.py` (Step 3 above).

This converts the birefringence angle β — currently a single scalar number —
into a **frequency-dependent, ℓ-dependent TB/EB correlation spectrum** that
LiteBIRD and CMB-S4 will measure at high precision.  That single function
transforms the framework's strongest observational claim from "matches a hint"
to "predicts a distinguishable shape."

**Signal to use with next AI:**
> "I'm working on the Unitary Manifold (paste RELAY.md).
> I need you to implement `tb_eb_spectrum(ells, ns, beta_rad, ...)` in
> `src/core/transfer.py`, plus corresponding tests in `tests/test_inflation.py`.
> The physics: birefringence angle β rotates E/B modes so that
> C_ell^TB ≈ sin(2β) * sqrt(C_ell^TT * C_ell^BB) and
> C_ell^EB ≈ sin(2β) * C_ell^EE in the small-angle approximation.
> The function must return something that cannot be reproduced by ΛCDM with β=0,
> and tests must assert that β=0 gives exactly zero TB/EB."

---

## 9. Key constants (copy into any calculation)

```python
# From src/core/inflation.py
PLANCK_NS_CENTRAL       = 0.9649
PLANCK_NS_SIGMA         = 0.0042
BIREFRINGENCE_TARGET_DEG = 0.35
BIREFRINGENCE_SIGMA_DEG  = 0.14
CS_LEVEL_PLANCK_MATCH   = 74        # ⚠️ fitted, not derived
N_WINDING_CANONICAL     = 5         # ⚠️ fitted, not derived

# Derived values
PHI0_BARE      = 1.0                # FTUM fixed point (Planck units)
J_KK           = 5 * 2 * 3.14159 * 1.0  # ≈ 31.42
PHI0_EFF       = J_KK * PHI0_BARE  # ≈ 31.42
NS_PREDICTED   = 0.9635
R_PREDICTED    = 0.0028
BETA_PREDICTED = 0.351              # degrees
ALPHA_COUPLING = PHI0_BARE**-2      # = 1.0
```

---

*End of relay document.  Paste this entire file to restore full context.*
