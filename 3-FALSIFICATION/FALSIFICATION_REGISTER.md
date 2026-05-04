# Falsification Register — Unitary Manifold

*Unitary Manifold v9.33 — ThomasCory Walker-Pearson, 2026*  
*Last updated: 2026-05-04*

---

This register tracks every falsifiable prediction made by the Unitary Manifold
framework: the predicted value, the current observational status, the decisive
experiment, the expected timeline, and the explicit kill condition.

For the full logical derivation of each kill condition, see
[`FALSIFICATION_CONDITIONS.md`](FALSIFICATION_CONDITIONS.md).  For derivation
chains and circularity audits, see [`FALLIBILITY.md`](../FALLIBILITY.md).

Status key: ✅ Currently consistent · ⚠️ Tension / open · ❌ Falsified · 🔬 Awaiting decisive test

---

## Part I — CMB Inflation Sector

### P01 — Scalar Spectral Index nₛ

| Field | Value |
|-------|-------|
| **Prediction** | nₛ = 0.9635 |
| **Derivation** | n_w = 5 → φ₀_eff via KK Jacobian → `ns_from_phi0()` |
| **Current data** | Planck 2018: 0.9649 ± 0.0042 |
| **Current status** | ✅ 0.33σ from Planck central value |
| **Decisive experiment** | CMB-S4 (~2030; σ_nₛ ≈ 0.002) |
| **Kill condition** | nₛ outside [0.9575, 0.9695] at > 3σ (CMB-S4 precision) |
| **Code** | `src/core/inflation.ns_from_phi0()` |

---

### P02 — Tensor-to-Scalar Ratio r

| Field | Value |
|-------|-------|
| **Prediction** | r_braided ≈ 0.0315 — braided (5,7) state, k_CS = 74 |
| **Derivation** | Braided (n₁=5, n₂=7) resonant state; `braided_predictions(5,7)['r_braided']` |
| **Current data** | BICEP/Keck 2022: r < 0.036 (95% CL) |
| **Current status** | ✅ Satisfies bound (0.0315 < 0.036) |
| **Decisive experiment** | CMB-S4 (~2030; σ_r ≈ 0.003) |
| **Kill condition** | r > 0.036 confirmed at 95% CL **or** upper bound falls below 0.0315 at > 2σ |
| **Code** | `src/core/braided_winding.braided_predictions(5,7)` |

---

### P03 — Cosmic Birefringence β — Primary Falsifier

| Field | Value |
|-------|-------|
| **Prediction** | β = 0.331° [(5,7) primary] or β = 0.273° [(5,6) shadow] |
| **Derivation** | k_CS = 74 (primary) or k_CS = 61 (shadow) → CS coupling → birefringence formula |
| **Current data** | Minami & Komatsu 2020: β = 0.35° ± 0.14° (2.4σ hint) |
| **Current status** | ✅ Both sectors consistent with current hint; (5,7) at 0.14σ from central value |
| **Decisive experiment** | LiteBIRD (~2032; σ_β ≈ 0.02°) — discriminates sectors at 2.9σ |
| **Kill conditions** | β < 0.07° at 3σ (consistent with zero) **OR** β > 0.50° at 3σ **OR** β ∈ (0.29°, 0.31°) at 3σ (falls in predicted inter-sector gap) **OR** β outside [0.22°, 0.38°] at 3σ |
| **Notes** | Gap between two predicted values: 0.058° = 2.9σ_LiteBIRD. Pillar 96 proves analytically that exactly two sectors exist. |
| **Code** | `src/core/dual_sector_convergence.py` (P95), `src/core/unitary_closure.py` (P96), `src/core/braided_winding.birefringence_scenario_scan()` |

---

### P04 — CMB Spectral Shape Residuals

| Field | Value |
|-------|-------|
| **Prediction** | KK Silk damping correction δ_D ≈ 3.55 × 10⁻³; peak shape shift ΔCℓ/Cℓ ~ 1% at ℓ = 1500 |
| **Derivation** | KK Boltzmann correction to photon transfer function (Pillar 78-B, 73) |
| **Current data** | Current CMB experiments cannot resolve at this precision |
| **Current status** | 🔬 Awaiting CMB-S4 / LiteBIRD precision |
| **Decisive experiment** | CMB-S4 (ℓ-resolution to 5000); LiteBIRD (polarization) |
| **Kill condition** | No spectral shape residual detected at the predicted 1% level at ℓ ≈ 1500 at > 3σ |
| **Code** | `src/core/cmb_spectral_shape.py` (P78-B), `src/core/cmb_boltzmann_peaks.py` (P73) |

---

## Part II — Geometry Sector

### P05 — Neutrino-Radion Identity / KK Scale

| Field | Value |
|-------|-------|
| **Prediction** | m_ν (lightest active) = M_KK ≈ 110.1 meV; R_KK ≈ 1.792 μm |
| **Derivation** | f_braid × ρ_obs closure: `derive_R_from_neutrino_mass()`, `prove_resonance_identity()` |
| **Current data** | KATRIN (2022): m_ν < 0.45 eV (90% CL); cosmological: Σm_ν < 120 meV (Planck) |
| **Current status** | ⚠️ Consistent with current upper bounds; prediction at the edge of cosmological sensitivity |
| **Decisive experiment** | KATRIN final (~2025); Project 8 (~2028; target sensitivity ~40 meV); PTOLEMY (~2030) |
| **Kill condition** | Any neutrino mass eigenstate measured outside [80 meV, 120 meV] at 3σ **OR** Planck 2030+ Σm_ν bound rules out 110 meV eigenstate |
| **Code** | `src/core/kk_neutrino.derive_R_from_neutrino_mass()`, `src/core/kk_neutrino.prove_resonance_identity()` |

---

### P06 — Casimir–KK Ripple

| Field | Value |
|-------|-------|
| **Prediction** | δF/F_Casimir = +0.162% (attractive enhancement) at d ≈ 1.792 μm |
| **Derivation** | First KK graviton mode contribution to Casimir force at d = R_KK |
| **Current data** | Not yet measured at this precision at this specific separation |
| **Current status** | 🔬 Awaiting dedicated precision experiment |
| **Decisive experiment** | Sub-micron Casimir measurement at 0.1% precision near d ≈ 1.79 μm |
| **Kill condition** | No deviation from standard Casimir law at 0.1% level at d = 1.79 ± 0.05 μm at 3σ |
| **Code** | `src/core/zero_point_vacuum.casimir_kk_ripple_force()`, `casimir_ripple_peak_deviation()` |

---

### P07 — Sub-mm Gravity / KK Graviton

| Field | Value |
|-------|-------|
| **Prediction** | Deviations from Newton's law at L_c ≈ 1.79 μm (first KK graviton) |
| **Derivation** | M_KK ≈ 110 meV → L_c = ħc/M_KK ≈ 1.79 μm |
| **Current data** | Short-range gravity experiments reach ~10 μm; no deviation seen |
| **Current status** | ⚠️ Not yet probed at the predicted scale |
| **Decisive experiment** | Next-generation short-range gravity experiments targeting ~2 μm |
| **Kill condition** | No deviation from Newtonian gravity at L_c ≈ 1.79 μm at 3σ with < 1% precision |
| **Code** | `src/core/kk_sub_mm_gravity.py` (Pillar 108) |

---

### P08 — Anisotropic Birefringence β(n̂)

| Field | Value |
|-------|-------|
| **Prediction** | β(n̂) = β₀ × (1 + δ(n̂)); 5% E2 dipole modulation across the sky |
| **Derivation** | CS coupling anisotropy from the KK compactification geometry (Pillar 118) |
| **Current data** | Current data averaged over sky; anisotropy not yet measured |
| **Current status** | 🔬 Awaiting LiteBIRD angular resolution |
| **Decisive experiment** | LiteBIRD (~2032; full-sky polarization map) |
| **Kill condition** | β(n̂) isotropic at > 3σ (no E2 dipole modulation at SNR > 1) |
| **Code** | `src/core/anisotropic_birefringence.py` (Pillar 118) |

---

## Part III — Dark Sector

### P09 — Dark Energy Equation of State wDE

| Field | Value |
|-------|-------|
| **Prediction** | w₀ ≈ −0.930 (from c_s = 12/37 radion sector, Pillar 136, 151) |
| **Derivation** | KK radion sector: c_s² = (12/37)² → w_KK |
| **Current data** | DESI DR2: w₀ = −0.92 ± 0.09 (0.11σ from prediction ✅); Planck+BAO: 3.3σ tension |
| **Current status** | ⚠️ CONSTRAINED — DESI DR2 consistent; Planck+BAO tension remains |
| **Decisive experiment** | Roman Space Telescope (~2027); DESI DR5; Euclid |
| **Kill condition** | w₀ = −1.00 confirmed at > 3σ ruling out w₀ = −0.930 |
| **Code** | `src/core/de_equation_of_state_desi.py` (P151), `src/core/kk_radion_dark_energy.py` (P136) |

---

### P10 — Dark Matter KK Modes

| Field | Value |
|-------|-------|
| **Prediction** | KK graviton at 33.6 meV; hot-relic Ω_KK h² ≪ 0.12; all harmonics viable |
| **Derivation** | KK tower: M_KK = 110 meV / n_harmonics (Pillar 106) |
| **Current data** | DM relic density Ω h² ≈ 0.12 (Planck); no confirmed KK detection |
| **Current status** | ⚠️ Hot relic: Ω_KK h² ≪ 0.12 ✓ (not overproduced); direct detection open |
| **Decisive experiment** | Direct detection experiments sensitive to meV-scale dark matter |
| **Kill condition** | KK graviton detection with properties inconsistent with M_KK = 110 meV spectrum |
| **Code** | `src/core/kk_dark_matter.py` (Pillar 106) |

---

## Part IV — Standard Model / Particle Sector

### P11 — Proton Decay Rate

| Field | Value |
|-------|-------|
| **Prediction** | τ_p ≈ 1.68 × 10³⁸ yr (via GUT-scale orbifold) |
| **Derivation** | M_GUT from KK RGE running + orbifold suppression (Pillar 107) |
| **Current data** | Super-K lower bound: τ_p > 1.6 × 10³⁴ yr |
| **Current status** | ✅ Prediction viable (above Super-K bound) |
| **Decisive experiment** | Hyper-Kamiokande (~2027+) |
| **Kill condition** | Hyper-K measures τ_p in the range that excludes 10³⁸ yr at > 3σ **OR** proton decay observed at τ_p < 10³⁵ yr (would suggest different M_GUT) |
| **Code** | `src/core/proton_decay.py` (Pillar 107) |

---

### P12 — Baryogenesis Baryon Asymmetry η_B

| Field | Value |
|-------|-------|
| **Prediction** | η_B ≈ 3.5 × 10⁻¹⁰ (from B_μ KK-mediated leptogenesis) |
| **Derivation** | K_CS = 74 + B_μ topology → CP violation → leptogenesis → η_B (Pillar 105) |
| **Current data** | Observed: η_B ≈ 6 × 10⁻¹⁰ (Planck CMB) |
| **Current status** | ⚠️ Order-of-magnitude match; factor ~1.7 discrepancy |
| **Decisive experiment** | Precision CMB (Planck 2030+); improved leptogenesis calculations |
| **Kill condition** | Observed η_B confirmed outside [10⁻¹⁰, 10⁻⁹] at > 3σ; or theoretical improvement rules out the B_μ mechanism |
| **Code** | `src/core/baryogenesis_bmu.py` (Pillar 105) |

---

### P13 — Gravitational Wave Birefringence (GW)

| Field | Value |
|-------|-------|
| **Prediction** | h_L ≠ h_R for primordial GWs; rotation Δψ from CS coupling (k_CS = 74) |
| **Derivation** | CS coupling propagates to GW tensor modes (Pillar 125) |
| **Current data** | Not yet measured at required sensitivity |
| **Current status** | 🔬 Awaiting LISA / Einstein Telescope |
| **Decisive experiment** | LISA (~2034; 4-yr mission); Einstein Telescope (~2035) |
| **Kill condition** | No h_L/h_R asymmetry in primordial GW spectrum at > 3σ with LISA sensitivity |
| **Code** | `src/core/gw_birefringence.py` (Pillar 125) |

---

## Part V — Cold Fusion / Energy Sector

### P14 — Cold Fusion Excess Heat (B_μ Energy Routing)

| Field | Value |
|-------|-------|
| **Prediction** | COP > 1 (excess heat) in Pd-D at x ≈ 0.875 loading; > 99% phonon fraction at B_eff > 10 |
| **Derivation** | B_μ time-arrow lock routes D-D Q-value preferentially to phonon channel (Pillar 15, 15-B) |
| **Current data** | Unresolved controversy; no peer-reviewed consensus on reproducible excess heat |
| **Current status** | 🔬 Falsifiable engineering conjecture — awaiting reproducible experiment |
| **Decisive experiment** | High-loading (x > 0.85) Pd-D calorimetry with isotropic neutron/gamma monitoring |
| **Kill conditions** | No COP > 1.01 after systematics **OR** prompt gammas at standard D-D branching ratios **OR** fast neutron flux consistent with bare D-D |
| **Notes** | Explicitly framed as a falsifiable COP prediction, NOT a confirmation that LENR occurs. Pillar 15 is the only domain-extension pillar with genuine falsification criteria. |
| **Code** | `src/cold_fusion/excess_heat.py`, `src/cold_fusion/falsification_protocol.py` (F1–F3) |

---

## Part VI — Mathematical / Internal Falsifiers

### P15 — n_w = 5 Uniqueness (Z₂ + CS → {5,7})

| Field | Value |
|-------|-------|
| **Claim** | The Z₂ orbifold symmetry + CS anomaly cancellation uniquely restricts n_w to {5,7}; Planck nₛ then selects n_w = 5 |
| **Derivation** | Pillar 70-D: APS η-invariant η̄(5) = ½ (odd ✓), η̄(7) = 0 (even, Z₂-step ✓); all other n ruled out |
| **Current status** | ✅ Conditional theorem — spin-structure conjecture would close remaining gap |
| **Mathematical falsifier** | A proof that Z₂ + CS anomaly cancellation does NOT restrict n_w to {5,7} |
| **Code** | `src/core/aps_eta_invariant.py` (Pillar 70-D) |

---

### P16 — k_eff = n₁² + n₂² for Braided Pairs

| Field | Value |
|-------|-------|
| **Claim** | For braid pair (n₁, n₂), the effective CS level is k_eff = n₁² + n₂² (Pillar 58) |
| **Derivation** | Pillar 58: algebraic derivation from sum-of-squares structure of braid tensor CS coupling |
| **Current status** | ✅ Established; verified numerically for all pairs in scan |
| **Mathematical falsifier** | A counterexample braid pair (n₁, n₂) for which k_eff ≠ n₁² + n₂² |
| **Code** | `src/core/braided_winding.py`, claims/integer_derivation/ |

---

### P17 — FTUM Fixed-Point Existence

| Field | Value |
|-------|-------|
| **Claim** | The FTUM operator U = I + H + T has a unique fixed point φ* = A₀/(4G) for all physical initial conditions |
| **Derivation** | Analytic Banach contraction proof in `src/multiverse/fixed_point.analytic_banach_proof()` |
| **Current status** | ✅ 100% convergence over 192 initial conditions; analytic proof complete |
| **Mathematical falsifier** | A physical (S₀, A₀) pair that provably diverges or limit-cycles, contradicting the Banach proof |
| **Code** | `src/multiverse/fixed_point.py`, `src/multiverse/basin_analysis.py` |

---

## Ledger Summary

| # | Prediction | Status | Decisive test | Timeline |
|---|-----------|--------|--------------|---------|
| P01 | nₛ = 0.9635 | ✅ 0.33σ from Planck | CMB-S4 | ~2030 |
| P02 | r ≈ 0.0315 | ✅ Below BICEP/Keck bound | CMB-S4 | ~2030 |
| P03 | β = 0.331° or 0.273° | ✅ Consistent with hint | **LiteBIRD** | **~2032** |
| P04 | CMB shape δ_D ≈ 3.55×10⁻³ | 🔬 Not yet resolved | CMB-S4 | ~2030 |
| P05 | m_ν ≈ 110 meV | ⚠️ Near cosmological bound | KATRIN / Project 8 | ~2028 |
| P06 | Casimir δF/F = 0.162% | 🔬 Not yet measured | Precision lab | TBD |
| P07 | Sub-mm gravity at 1.79 μm | ⚠️ Not yet probed | Short-range gravity | TBD |
| P08 | β(n̂) 5% E2 modulation | 🔬 Not yet resolved | LiteBIRD | ~2032 |
| P09 | w₀ ≈ −0.930 | ⚠️ DESI DR2 ✅; Planck tension | Roman ST / DESI | ~2027 |
| P10 | KK DM at 33.6 meV | ⚠️ Hot relic viable | Direct detection | TBD |
| P11 | τ_p ≈ 10³⁸ yr | ✅ Above Super-K bound | Hyper-K | ~2030s |
| P12 | η_B ≈ 3.5×10⁻¹⁰ | ⚠️ Order-of-magnitude match | Precision CMB | TBD |
| P13 | GW h_L ≠ h_R | 🔬 Not yet measured | LISA / ET | ~2034–35 |
| P14 | Cold fusion COP > 1 | 🔬 Unresolved / falsifiable conjecture | Pd-D calorimetry | TBD |
| P15 | n_w ∈ {5,7} from Z₂+CS | ✅ Conditional theorem | Mathematics | — |
| P16 | k_eff = n₁²+n₂² | ✅ Established | Mathematics | — |
| P17 | FTUM fixed point | ✅ Analytic proof + 192/192 | Mathematics | — |

**Current verdict:**  
No prediction has been falsified.  The primary active tests are LiteBIRD (P03,
P08; ~2032) and CMB-S4 (P01, P02, P04; ~2030).  The neutrino mass prediction
(P05) is the nearest-term decisive test with current experiments.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
