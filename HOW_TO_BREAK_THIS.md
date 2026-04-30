# How to Break This

A guide for adversarial reviewers.  Each section describes a specific,
mechanical way to break the theory — and the exact test or code line that
will confirm you have broken it.

If you cannot break it via these handles, that is evidence of robustness.
If you find a new break-point not listed here, open an issue.

---

## 1. Break the birefringence derivation (k_CS = 74)

**Handle:** Change `CS_LEVEL_PLANCK_MATCH` in `src/core/inflation.py` from
74 to any other integer (e.g., 73).

**Expected result:** `claims/integer_derivation/test_claim.py` fails at
`test_cs_level_is_unique_minimiser` — proving that k=74 is not arbitrary.

**What this tests:** The claim that 74 is derived, not chosen.

```bash
# Mutant: set CS_LEVEL_PLANCK_MATCH = 73, then:
python -m pytest claims/integer_derivation/test_claim.py -v
# → FAIL (test_cs_level_is_unique_minimiser)
```

---

## 2. Break the KK Jacobian (nₛ leaves the Planck window)

**Handle:** In `src/core/inflation.py`, change `effective_phi0_kk()` to return
`phi0_bare` instead of `n_winding * 2 * pi * sqrt(phi0_bare)`.

**Expected result:** `ns_from_phi0(phi0_bare=1.0)` gives nₛ ≈ 0.75, far
outside the Planck 1σ window.  `tests/test_inflation.py` fails at dozens of
spectral-index tests.

**What this tests:** The claim that the KK Jacobian is essential for nₛ.

```bash
# Mutant: return phi0_bare in effective_phi0_kk, then:
python -m pytest tests/test_inflation.py -v -k "planck or spectral"
# → FAIL (multiple tests)
```

---

## 3. Break the r-tension documentation (hide the conflict)

**Handle:** In `src/core/inflation.py`, replace the n_w=5 path with n_w=9
(which satisfies r < 0.036 but pushes nₛ to +4σ from Planck).

**Expected result:**
- `claims/tensor_ratio_fix/test_claim.py::test_canonical_r_exceeds_bicep_keck_bound` FAILS
  (r is now < 0.036 — but then nₛ is broken)
- `claims/tensor_ratio_fix/test_claim.py::test_canonical_ns_within_planck_1sigma` FAILS
  (nₛ is now outside 1σ)

Only one of the two constraints can be satisfied at a time.

```bash
# Mutant: use n_winding=9 as canonical, then:
python -m pytest claims/tensor_ratio_fix/test_claim.py -v
# → FAIL (cannot satisfy both constraints simultaneously)
```

---

## 4. Break the amplitude normalisation (make λ affect nₛ)

**Handle:** In `src/core/inflation.py`, add a small λ-dependent correction to
`spectral_index()`:

```python
# mutant:
return 1.0 - 6.0 * epsilon + 2.0 * eta + 1e-4 * lam
```

**Expected result:** `claims/amplitude_normalization/test_claim.py::test_ns_lambda_independent`
FAILS because nₛ(λ=1) ≠ nₛ(λ=λ_COBE).

**What this tests:** The claim that COBE normalisation introduces no tuning
of the spectral observables.

```bash
python -m pytest claims/amplitude_normalization/test_claim.py -v
# → FAIL (test_ns_lambda_independent)
```

---

## 5. Break the anomaly inflow coupling (wrong volume factor)

**Handle:** In `cs_axion_photon_coupling()`, change the denominator from
`2 * math.pi**2 * r_c` to `2 * math.pi * r_c` (wrong KK reduction).

**Expected result:** g_aγγ increases by π and β ≈ 1.1°, far outside the
1σ window.  `claims/anomaly_inflow/test_claim.py::test_coupling_formula_correct`
and `test_beta_within_observational_window` both FAIL.

```bash
python -m pytest claims/anomaly_inflow/test_claim.py -v
# → FAIL (test_coupling_formula_correct, test_beta_within_observational_window)
```

---

## 6. Break the FTUM fixed-point convergence

**Handle:** In `src/multiverse/fixed_point.py`, increase the iteration step
size to force non-convergence.

**Expected result:** `tests/test_fixed_point.py` fails at convergence tests.
The fixed point of the UEUM operator no longer exists within the search space.

```bash
python -m pytest tests/test_fixed_point.py -v
# → FAIL (convergence tests)
```

---

## 7. Break holographic entropy growth (arrow of time)

**Handle:** In `src/holography/boundary.py`, negate the entropy production
term so entropy decreases.

**Expected result:** `tests/test_arrow_of_time.py::TestEntropyMonotonicity`
FAILS — entropy is no longer increasing.

```bash
python -m pytest tests/test_arrow_of_time.py -v
# → FAIL (entropy monotonicity tests)
```

---

## 8. Break Pillar 14: atomic structure (φ-corrected spectroscopy)

**Handle:** In `src/core/atomic_structure.py`, remove the φ-correction factor
from `phi_corrected_energy()` so it returns the bare Bohr energy unchanged.

**Expected result:** `tests/test_atomic_structure.py` fails at tests that
verify the φ-shift produces measurable fine-structure corrections — e.g.
`test_phi_correction_nonzero` and `test_hydrogen_1s_phi_shift`.

**What this tests:** The claim that the 5D radion leaves a signature in
atomic spectra at the level of the measured fine-structure constant.

```bash
# Mutant: return bare_energy in phi_corrected_energy, then:
python -m pytest tests/test_atomic_structure.py -v -k "phi"
# → FAIL (phi-correction tests)
```

---

## 9. Break Pillar 15: cold-fusion φ-enhanced tunnelling

**Handle:** In `src/core/cold_fusion.py`, set the φ-enhancement factor to 1.0
(no enhancement) in `phi_enhanced_tunneling_probability()`.

**Expected result:** `tests/test_cold_fusion.py` fails at tests that verify
excess-heat predictions exceed the bare quantum-tunnelling baseline — e.g.
`test_enhancement_exceeds_bare` and `test_excess_heat_positive`.

**What this tests:** The claim that the 5D geometry amplifies sub-barrier
fusion rates in Pd-D lattices beyond the bare WKB prediction.

```bash
# Mutant: set phi_factor = 1.0 in phi_enhanced_tunneling_probability, then:
python -m pytest tests/test_cold_fusion.py -v -k "enhancement or excess"
# → FAIL
```

---

## 10. Break Pillar 87: Wolfenstein CKM geometry

**Handle:** In `src/core/wolfenstein_geometry.py`, replace `lambda_ckm = sqrt(m_d / m_s)` with `lambda_ckm = 0.22` (hard-coded, not geometry-derived).

**Expected result:** `tests/test_wolfenstein_geometry.py` fails at `test_lambda_from_geometry` — proving the CKM parameter is derived from quark mass ratios, not tuned.

**What this tests:** The claim that the Wolfenstein parameter λ = √(m_d/m_s) = 0.2236 (0.6% off PDG) follows from UM geometry, not fitting.

```bash
python -m pytest tests/test_wolfenstein_geometry.py -v -k "lambda or geometry"
# → FAIL
```

---

## 11. Break Pillar 88: SM free parameters (sin²θ_W from SU(5))

**Handle:** In `src/core/sm_free_parameters.py`, replace `sin2_theta_w_gut = 3/8` with `sin2_theta_w_gut = 0.231` (experimental value at M_Z, bypassing the derivation).

**Expected result:** `tests/test_sm_free_parameters.py` fails at `test_sin2_theta_w_gut_exact` — proving 3/8 is derived from SU(5) orbifold normalisation, not inserted.

**What this tests:** The claim that sin²θ_W(M_GUT) = 3/8 exactly is a theorem of the orbifold boundary conditions.

```bash
python -m pytest tests/test_sm_free_parameters.py -v -k "gut or sin2"
# → FAIL
```

---

## 12. Break Pillar 89: Algebraic vacuum selection (n_w = 5)

**Handle:** In `src/core/vacuum_geometric_proof.py`, bypass the APS η-invariant step and set `eta_bar = 0` (instead of deriving it from the Z₂ Dirichlet boundary condition).

**Expected result:** `tests/test_vacuum_geometric_proof.py` fails at `test_aps_eta_selects_nw5` — proving n_w = 5 follows from the boundary condition, not from observational selection.

**What this tests:** The claim that η̄ = ½ is forced by G_{μ5} Z₂-parity + Dirichlet BC, and that this uniquely selects n_w = 5 from pure geometry.

```bash
python -m pytest tests/test_vacuum_geometric_proof.py -v -k "aps or eta or nw5"
# → FAIL
```

---

## 13. Break Pillar 95: Dual-sector convergence (exactly two braid pairs survive)

**Handle:** In `src/core/dual_sector_convergence.py`, widen the Planck nₛ window from 1σ to 3σ before the resonance scan.

**Expected result:** Additional braid pairs beyond (5,6) and (5,7) will survive, breaking the uniqueness result. `tests/test_dual_sector_convergence.py` fails at `test_exactly_two_sectors_survive`.

**What this tests:** The claim that the Planck + BICEP/Keck constraints jointly admit exactly two braid pairs.

```bash
python -m pytest tests/test_dual_sector_convergence.py -v -k "exactly_two or dual"
# → FAIL (more than two pairs survive the widened window)
```

---

## 14. Break Pillar 96: Unitary closure (algebraic sector proof)

**Handle:** In `src/core/unitary_closure.py`, replace the analytic inequality proof with a numerical enumeration that only checks integer pairs up to n₂ = 5.

**Expected result:** `tests/test_unitary_closure.py` fails at `test_algebraic_sector_proof` — the algebraic identity `c_s(5,n₂) < R_BICEP/r_bare → n₂ ≤ 7` is a theorem, not an enumeration.

**What this tests:** The claim that exactly {(5,6),(5,7)} is proved by an algebraic inequality, not by finite search.

```bash
python -m pytest tests/test_unitary_closure.py -v -k "algebraic or closure"
# → FAIL
```

---

## 15. Break Pillar 97/98: GW Yukawa (Ŷ₅ = 1 from GW vacuum)

**Handle:** In `src/core/gw_yukawa_derivation.py`, change the GW vacuum condition so that `Y_hat_5 = 0` (no Yukawa from GW) instead of deriving Ŷ₅ = 1.

**Expected result:** `tests/test_gw_yukawa_derivation.py` fails at `test_gw_vacuum_yukawa_unity` — the absolute fermion mass scale is determined by the GW vacuum, not a free parameter.

**What this tests:** The claim that Ŷ₅ = 1 follows from the gravitational wave vacuum condition, not fitting.

```bash
python -m pytest tests/test_gw_yukawa_derivation.py -v -k "unity or gw_vacuum"
# → FAIL
```

---

## 16. Break Pillar Ω: Universal Mechanics Engine

**Handle:** In `omega/omega_synthesis.py`, delete the `UniversalEngine` class and replace `compute_all()` with a stub that returns an empty `OmegaReport`.

**Expected result:** `omega/test_omega_synthesis.py` fails at `test_all_six_domains_populated` — all six observable domains (cosmology, particle_physics, geometry, consciousness, hils, falsifiers) must be non-empty.

**What this tests:** The claim that 5 seed constants → all observables, without independent tuning per domain.

```bash
python -m pytest omega/test_omega_synthesis.py -v
# → FAIL (168 tests)
```

---

| Break point | Failing test file | Key test name |
|-------------|-------------------|---------------|
| k_CS ≠ 74 | `claims/integer_derivation/test_claim.py` | `test_cs_level_is_unique_minimiser` |
| KK Jacobian removed | `tests/test_inflation.py` | spectral index tests |
| r-tension hidden | `claims/tensor_ratio_fix/test_claim.py` | `test_canonical_r_exceeds_bicep_keck_bound` |
| λ affects nₛ | `claims/amplitude_normalization/test_claim.py` | `test_ns_lambda_independent` |
| Wrong coupling formula | `claims/anomaly_inflow/test_claim.py` | `test_coupling_formula_correct` |
| FTUM non-convergent | `tests/test_fixed_point.py` | convergence tests |
| Entropy decreases | `tests/test_arrow_of_time.py` | entropy monotonicity |
| φ-correction removed (atomic) | `tests/test_atomic_structure.py` | phi-correction tests |
| φ-enhancement removed (cold fusion) | `tests/test_cold_fusion.py` | enhancement/excess-heat tests |
| φ₀ closure fails (Pillar 56) | `tests/test_phi0_closure.py` | `test_closure_audit_all_consistent` |
| Acoustic peak gap unclosed (Pillar 57) | `tests/test_cmb_peaks.py` | `test_suppression_audit_corrected_less_than_raw` |
| LiteBIRD prediction gap wrong | `tests/test_litebird_forecast.py` | `test_forecast_scenarios_falsification` |
| CKM λ not from geometry (Pillar 87) | `tests/test_wolfenstein_geometry.py` | `test_lambda_from_geometry` |
| sin²θ_W not 3/8 at GUT (Pillar 88) | `tests/test_sm_free_parameters.py` | `test_sin2_theta_w_gut_exact` |
| APS η̄ bypassed (Pillar 89) | `tests/test_vacuum_geometric_proof.py` | `test_aps_eta_selects_nw5` |
| More than two sectors survive (Pillar 95) | `tests/test_dual_sector_convergence.py` | `test_exactly_two_sectors_survive` |
| Sector proof not algebraic (Pillar 96) | `tests/test_unitary_closure.py` | `test_algebraic_sector_proof` |
| Ŷ₅ ≠ 1 from GW vacuum (Pillar 97) | `tests/test_gw_yukawa_derivation.py` | `test_gw_vacuum_yukawa_unity` |
| Omega engine stub (Pillar Ω) | `omega/test_omega_synthesis.py` | `test_all_six_domains_populated` |

---

## What would constitute a real break

A break that matters is one where:

1. The test clearly corresponds to a physical claim (not just a numerical check).
2. The failure cannot be "fixed" by adjusting a free parameter.
3. The failure is reproducible from a clean clone.

If you find such a break, please open a GitHub issue with the title
**"Break report: [claim name]"** and include the output of the failing test.
