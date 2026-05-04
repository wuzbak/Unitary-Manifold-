# Falsification Conditions — Unitary Manifold

*Unitary Manifold v9.33 — ThomasCory Walker-Pearson, 2026*

---

This document lists every explicit condition under which the Unitary Manifold
framework would be **falsified** — not merely revised, extended, or
complicated, but ruled out.  Each condition is stated as a bright line: a
measurement or mathematical result that the framework cannot survive.

For predictions and their expected uncertainty ranges, see
[`prediction.md`](prediction.md).  For honest admissions about gaps that do
*not* rise to falsification, see [`FALLIBILITY.md`](../FALLIBILITY.md).

---

## F1. Cosmic Birefringence β — Primary Falsifier

**Experiment:** LiteBIRD (~2032); σ_β ≈ 0.02°.  Secondary: CMB-S4 (~2030),
Simons Observatory (ongoing).

**Predicted values:**

| Sector | k_CS | β predicted | r_eff |
|--------|------|-------------|-------|
| (5,7) — primary | 74 | 0.331° | 0.0315 |
| (5,6) — shadow  | 61 | 0.273° | 0.0175 |

Gap between sectors: 0.058° = 2.9 σ_LiteBIRD.  The analytic proof that exactly
these two sectors exist (and no others) is Pillar 96 (`src/core/unitary_closure.py`).

**Falsification thresholds:**

| Result | Verdict |
|--------|---------|
| β < 0.07° at 3σ | **FALSIFIED** — β consistent with zero; k_CS = 74 loses its observational anchor |
| β > 0.50° at 3σ | **FALSIFIED** — cannot be accommodated without changing k_CS, which would break nₛ |
| β ∈ (0.29°, 0.31°) at 3σ | **FALSIFIED** — lands in the predicted inter-sector gap; neither viable sector is consistent |
| β outside [0.22°, 0.38°] at 3σ | **FALSIFIED** — zero viable braid pairs survive the triple constraint |

A measurement in the gap [0.29°–0.31°] is falsification even if β ≠ 0, because
the framework predicts **no** viable state in that interval.

*Code:* `src/core/braided_winding.birefringence_scenario_scan()`,
`src/core/dual_sector_convergence.py` (Pillar 95),
`src/core/unitary_closure.py` (Pillar 96).

---

## F2. CMB Scalar Spectral Index nₛ

**Experiment:** CMB-S4 (~2030; σ_nₛ ≈ 0.002); PICO or post-LiteBIRD mission.

**Predicted value:** nₛ = 0.9635 (derived from n_w = 5 via `ns_from_phi0()`).

**Current status:** Planck 2018 measures nₛ = 0.9649 ± 0.0042 — the
prediction lies 0.33σ from the Planck central value. ✅

**Falsification threshold:**

> CMB-S4 constrains nₛ to a window that **excludes 0.9635 at > 3σ** while the
> Planck central value does not shift substantially.

This would exclude the specific winding number n_w = 5.  A post-hoc adjustment
to a different n_w would be a parameter change, not a rescue of the framework
as stated.

*Code:* `src/core/inflation.ns_from_phi0()`, `src/core/evolution.py`.

---

## F3. CMB Tensor-to-Scalar Ratio r

**Experiment:** BICEP/Keck (ongoing); CMB-S4 (~2030; σ_r ≈ 0.003).

**Predicted value:** r_braided ≈ 0.0315 — derived from the braided (5,7)
state with k_CS = 74 = 5² + 7² (Pillar 97-B).

**Current status:** BICEP/Keck bound r < 0.036 at 95% CL — satisfied. ✅

**Falsification threshold:**

> CMB-S4 measures r > 0.036 at 95% CL, or future data pushes the upper bound
> **below** 0.0315 at > 2σ.

Either result would eliminate the (5,7) primary sector.  If both primary and
shadow sectors are eliminated by the tensor bound, the braided-winding mechanism
is falsified.

*Code:* `src/core/braided_winding.braided_predictions(5,7)['r_braided']`.

---

## F4. Neutrino Mass / Neutrino-Radion Identity

**Experiments:** KATRIN (ongoing); Project 8 (~2028); PTOLEMY (~2030);
Planck 2030+ CMB lensing (Σm_ν upper bound).

**Predicted value:** The lightest active neutrino mass equals the KK
compactification scale:

```
m_ν = M_KK = (f_braid × ρ_obs × 16π²)^(1/4) ≈ 110.1 meV
```

*Code:* `src/core/kk_neutrino.derive_R_from_neutrino_mass()`,
`src/core/kk_neutrino.prove_resonance_identity()`.

**Falsification thresholds:**

| Result | Verdict |
|--------|---------|
| Any neutrino mass eigenstate measured outside [80 meV, 120 meV] at 3σ | **FALSIFIED** |
| Planck 2030+ upper bound on Σm_ν falls below 120 meV in a way that excludes a 110 meV eigenstate | **FALSIFIED** |
| A competing mechanism explains M_KK ≈ 110 meV without invoking m_ν | **FRAMEWORK UNIQUENESS FALSIFIED** |

Note: the framework currently favours the Majorana branch (Pillar 150) with the
canonical seesaw.  A confirmed Dirac neutrino mass with no seesaw structure
would strongly disfavour but not automatically falsify the framework (a c_R
fine-tuning of ~1% remains viable — Pillar 157).

---

## F5. Casimir–KK Ripple — Smoking Gun Geometry Test

**Experiment:** Next-generation Casimir force measurement at d ≈ 1.79 μm
at 0.1% precision.

**Predicted value:**

```
δF/F_Casimir ≈ +0.162%   at   d ≈ R_KK ≈ 1.792 μm
```

The deviation oscillates with period ΔR_KK and falls off as (R_KK/d)⁴ for
d ≫ R_KK.  The sign is attractive enhancement.

**Falsification threshold:**

> A reproducible Casimir experiment at d = 1.79 ± 0.05 μm that finds no
> deviation from the standard Casimir law at the **0.1% level** at 3σ
> confidence **falsifies the 5D geometry** at M_KK ≈ 110 meV.

*Code:* `src/core/zero_point_vacuum.casimir_kk_ripple_force()`,
`src/core/zero_point_vacuum.casimir_ripple_peak_deviation()`.
Verified: `casimir_ripple_peak_deviation(n_mode=1, R_KK=1/M_KK_needed) = 0.00162`.

---

## F6. Cold Fusion Energy Spectrum — B_μ Time-Arrow Lock

**Experiment:** High-loading (x > 0.85) Pd-D calorimetry.

**Predicted signatures:** If the B_μ energy routing mechanism is correct, a
Pd-D cell loaded to x ≈ 0.875 at room temperature should produce:
- Excess heat (phonon channel) at COP > 1.
- Near-zero prompt gamma emission (< 1% of the D-D Q-value = 3.27 MeV).
- Zero fast neutrons above thermal background.

**Falsification threshold:**

> A reproducible, high-loading (x > 0.85) Pd-D experiment yields:
> - No excess heat at COP > 1.01 after systematic corrections; **or**
> - Prompt gammas in proportion to standard D-D branching ratios (50% to
>   n + He-3, 50% to p + T); **or**
> - Fast neutron flux consistent with bare D-D reaction rates.

Any **one** of the three above results falsifies the B_μ time-arrow lock
mechanism in `src/cold_fusion/excess_heat.py`.

*Code:* `src/physics/lattice_dynamics.bmu_time_arrow_lock()`,
`src/cold_fusion/excess_heat.calculate_energy_branching_ratio()`,
`src/cold_fusion/falsification_protocol.py` (Pillar 15-F, conditions F1–F3).

---

## F7. Holographic Entropy–Area Scaling Breakdown

**Experiment:** Future quantum-gravity experiments; black-hole thermodynamics
measurements.

**What is at stake:** The FTUM fixed-point iteration uses the entropy contraction

```
dS/dt = κ(A/4G − S)
```

grounded in the Bekenstein–Hawking relation S = A/4G.  This is assumed (standard
AdS/CFT), not derived independently in the framework.

**Falsification threshold:**

> Experimental or theoretical evidence that the Bekenstein–Hawking relation
> S = A/4G breaks down **systematically** at a specific scale (not as a quantum
> correction but as a leading-order modification) would remove the grounding of
> the FTUM contraction and with it the convergence proof.

This is currently the least testable falsification condition (no near-term
experiment is designed to probe it directly), but it remains a logical falsifier.

---

## F8. Dark Energy Equation of State wDE

**Experiment:** Roman Space Telescope (~2027); DESI DR5; Euclid (ongoing).

**Predicted value:** w_KK ≈ −0.930 (derived from c_s = 12/37 in the radion
sector, Pillar 136).

**Current status:** Consistent with DESI DR2 at 0.11σ ✅; 3.3σ tension with
Planck+BAO.  The DESI DR2 value w₀ = −0.92 ± 0.09 favours the UM direction.

**Falsification threshold:**

> Roman ST or DESI DR5 measures w₀ **firmly** consistent with w₀ = −1.00 at
> > 3σ *and* simultaneously rules out w₀ = −0.930.

Note: a measurement of w₀ ≠ −1 (dynamical dark energy confirmed) would
actually *support* the UM direction, not falsify it, provided w₀ ∈ [−0.95, −0.90].
The falsifier is specifically w₀ = −1.00 with no room for −0.930.

*Code:* `src/core/de_equation_of_state_desi.py` (Pillar 151).

---

## F9. Mathematical Falsifiers (Theory-Internal)

These are mathematical results (proofs or counterexamples) that would collapse
the framework without any observational measurement.

### F9-A. Z₂ + CS Anomaly → n_w ∉ {5,7}

> A mathematical proof that the Z₂ orbifold symmetry combined with
> Chern–Simons anomaly cancellation does **not** restrict n_w to the set {5,7}
> would eliminate the first-principles argument for n_w = 5 (Pillars 39, 67, 70-D).

The APS η-invariant proof (Pillar 70-D) establishes η̄(5) = ½ (odd, viable)
and η̄(7) = 0 (even, viable within Z₂-step); η̄(other) rules out all other
candidates.  A counterexample to this spin-structure argument would be
a mathematical falsifier.

### F9-B. k_eff ≠ n₁² + n₂² for Braided Pairs

> A proof that the effective Chern–Simons level for a braided winding pair
> (n₁, n₂) is **not** given by k_eff = n₁² + n₂² would falsify Pillar 58
> and remove the algebraic derivation of k_CS = 74.

*Code:* `src/core/braided_winding.py` (Pillar 27).

### F9-C. FTUM Fixed Point Non-Existence

> A proof that the FTUM operator U = I + H + T has no fixed point for
> physically reasonable initial conditions (entropy S₀, field amplitude A₀)
> would falsify the multiverse selection mechanism.

Current status: 100% convergence over 192 initial conditions; analytic
Banach fixed-point proof in `src/multiverse/fixed_point.analytic_banach_proof()`.
A counterexample with a specific (S₀, A₀) that provably diverges would
be a mathematical falsifier.

---

## F10. Competing Theory with Fewer Free Parameters

**Criterion (Occam's razor):**

> If a competing inflationary model — with **no freely chosen winding number**
> — reproduces the same set of observables simultaneously:
>
>   nₛ = 0.9649,   r < 0.036,   β ∈ {0.273°, 0.331°},   k_CS = 74
>
> using fewer independent assumptions than the UM, the UM's claim to predictive
> economy and uniqueness would be negated.

This is not falsification of the physics, but falsification of the claim that
the UM framework provides a *distinctive* prediction.

---

## Summary Table

| ID | Observable | Kill threshold | Experiment | Timeline |
|----|-----------|----------------|-----------|---------|
| F1 | Birefringence β | β < 0.07° **or** β ∈ (0.29°,0.31°) **or** β > 0.50° at 3σ | LiteBIRD | ~2032 |
| F2 | Spectral index nₛ | nₛ excludes 0.9635 at > 3σ | CMB-S4 | ~2030 |
| F3 | Tensor ratio r | r > 0.036 or r < 0.0315 − 2σ | CMB-S4 | ~2030 |
| F4 | Neutrino mass m_ν | Any eigenstate outside [80,120] meV at 3σ | KATRIN / Project 8 | ~2028 |
| F5 | Casimir-KK ripple | No δF/F = 0.162% at d ≈ 1.79 μm at 0.1% precision | Casimir lab | TBD |
| F6 | Cold fusion COP | No excess heat at COP > 1.01 **or** standard D-D gammas | Pd-D calorimetry | TBD |
| F7 | S = A/4G | Systematic breakdown at any scale | QG experiments | Long-term |
| F8 | Dark energy w₀ | w₀ = −1.00 ruling out −0.930 at > 3σ | Roman ST / DESI | ~2027 |
| F9-A | n_w ∈ {5,7} | Mathematical proof that Z₂+CS ↛ {5,7} | Mathematics | — |
| F9-B | k_eff = n₁²+n₂² | Mathematical counterexample for any braid pair | Mathematics | — |
| F9-C | FTUM fixed point | Proof of non-convergence for physical (S₀, A₀) | Mathematics | — |
| F10 | Predictive economy | Competing model matches (nₛ,r,β,k_CS) with fewer assumptions | Theory community | — |

---

## What Is Not a Falsifier

The following results would require *revision* or *extension* of the framework
but would not falsify it outright:

- Confirmation that Σm_ν < 60 meV (would revise M_KK estimate; framework
  structure survives if a different KK identification is found).
- Λ_QCD discrepancy ×10⁷ in the KK running of α_s (Pillar 62 — a known
  open gap; framework survives in the inflation sector).
- Muon g−2 anomaly not explained by KK graviton (Pillar 51; the KK
  correction is 30 orders of magnitude too small; the framework was not
  designed as a TeV-scale model).
- ADM time-parameterization gap (< 1% lapse deviation; quantified in
  §XIV.3 of FALLIBILITY.md — not a falsifier, an open theoretical gap).
- HOX paralog count (M2): the claimed N_gen = 3 → 39 paralog groups is
  a formal analogy (Pillar 10), not a physics derivation; its failure does
  not falsify the inflation sector.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
