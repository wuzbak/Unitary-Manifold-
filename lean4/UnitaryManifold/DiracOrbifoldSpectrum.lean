import Mathlib.Data.Rat.Defs
import Mathlib.Data.Int.Basic
import Mathlib.Tactic.NormNum
import Lean.Elab.Tactic.Omega

/-!
# Dirac orbifold: conditional arithmetic proxies ONLY

This file contains exact arithmetic for assumed constants and ladders. Historical
declaration names are retained for compatibility; they do NOT formalise a Dirac
operator, action, weighted Hilbert space, boundary domain, parity projection,
normalisability, APS index, gauge lift, generation selection or mixing direction.
In particular `z2_odd_bc_selects_uv` is just `142 > 74`: parity does not select
UV localisation on a finite regular interval.

The assumed LH ladder is 142/148, 141/148, 140/148 = 35/37, NOT 69/74.
Neither its base nor its spacing follows from any theorem here. The quoted
residual integers are historical target-dependent inputs, not error estimates
proved for a perturbative expansion. Their NLO/NNLO comparison is arithmetic.
The combined heuristic scale is 9/5476 + 27/405224 = 693/405224 (~0.001710).
Likewise `generation_mixing_norm_bound` only states 2 < 74; it is not a norm
bound. A bound on a correction's magnitude does not prove its sign or that it
improves a fit.

Status: CONDITIONAL_ARITHMETIC_PROXY_ONLY. The finite-interval counterexample
and analytic self-adjointness argument are in the Python module documentation,
not machine-proved here. `#print axioms` below makes the proof dependencies
visible when this module is compiled. No new axioms are introduced.
-/

namespace UnitaryManifold.DiracOrbifoldSpectrum

def N_W : ℕ := 5
def K_CS : ℕ := 74
def N_C : ℕ := 3
def PI_KR : ℕ := 37

-- Legacy names: these statements contain only numerical inequalities.
theorem dirac_lh_zero_mode_profile : 2 * (K_CS - N_C) > K_CS := by norm_num [K_CS, N_C]
theorem z2_odd_bc_selects_uv : 2 * (K_CS - N_C) > K_CS := by norm_num [K_CS, N_C]
theorem dirac_rh_zero_mode_profile :
    ∀ n : ℕ, n ≤ N_W → 2 * (N_W - n) ≤ 2 * N_W := by
  intro n hn
  omega
theorem z2_even_bc_rh : N_W + 1 ≥ 1 := by norm_num [N_W]
theorem rh_normalisable_all : ∀ n : ℕ, n ≤ N_W → N_W ≥ n := by
  intro n hn
  exact hn
theorem lh_uv_localised :
    (142 : ℚ) / 148 > 1 / 2 ∧ 141 / 148 > (1 : ℚ) / 2 ∧
    140 / 148 > (1 : ℚ) / 2 := by norm_num
theorem winding_number_5 : N_W = 5 := by rfl
theorem k_cs_74 : K_CS = 5^2 + 7^2 := by norm_num [K_CS]

theorem cl_base_value : K_CS - N_C = 71 := by norm_num [K_CS, N_C]
theorem cl_step_size : 2 * K_CS = 148 := by norm_num [K_CS]
theorem cl_gen1 : (71 : ℚ) / 74 = 142 / 148 := by norm_num
theorem cl_gen2 : (71 : ℚ) / 74 - 1 / 148 = 141 / 148 := by norm_num
theorem cl_gen3 : (71 : ℚ) / 74 - 2 / 148 = 35 / 37 := by norm_num
theorem cl_ladder_decreasing :
    (142 : ℚ) / 148 > 141 / 148 ∧ 141 / 148 > (140 : ℚ) / 148 ∧
    140 / 148 > (1 : ℚ) / 2 := by norm_num
theorem cl_cs_shift_step :
    (71 : ℚ) / 74 - 141 / 148 = 1 / 148 ∧
    (141 : ℚ) / 148 - 35 / 37 = 1 / 148 := by norm_num
theorem cr_base_value : N_W - 0 = N_W := by omega
theorem cr_gen_step : 2 * N_W = 10 := by norm_num [N_W]
theorem cr_spectrum : N_W + 1 = 6 := by norm_num [N_W]

-- Historical heuristic scales, not bounds derived from a physical action.
theorem nlo_bound_numerator : N_C ^ 2 = 9 := by norm_num [N_C]
theorem nlo_bound_denominator : K_CS ^ 2 = 5476 := by norm_num [K_CS]
theorem nlo_bound_value : N_C ^ 2 < K_CS ^ 2 := by norm_num [N_C, K_CS]
theorem nnlo_bound_value : N_C ^ 3 * 1000 < K_CS ^ 3 := by norm_num [N_C, K_CS]
theorem combined_bound : (9 : ℚ) / 5476 + 27 / 405224 = 693 / 405224 := by norm_num
theorem gen1_residual_within_bound : (1541 : ℕ) ≤ 1643 := by norm_num
theorem gen2_residual_exceeds_combined_bound : (2297 : ℕ) > 1710 := by norm_num
theorem gen3_residual_exceeds_combined_bound : (11946 : ℕ) > 1710 := by norm_num

-- Nonnegativity of selected integers is NOT normalisability of profiles.
theorem cr_gen0_nonneg : N_W ≥ 0 := by omega
theorem cr_gen1_nonneg : N_W ≥ 1 := by norm_num [N_W]
theorem cr_gen2_nonneg : N_W ≥ 2 := by norm_num [N_W]
theorem cr_gen3_nonneg : N_W ≥ 3 := by norm_num [N_W]
theorem cr_gen4_nonneg : N_W ≥ 4 := by norm_num [N_W]
theorem cr_gen5_nonneg : N_W - N_W = 0 := by omega

-- Compatibility names: neither a gap-closure certificate nor a theorem count.
theorem g4_bc_spectrum_certificate :
    (142 : ℕ) + 141 + 140 = 423 ∧ K_CS * N_W = 370 ∧
    N_C ^ 2 < K_CS ∧ N_W + 1 = 6 ∧ (1541 : ℕ) ≤ 1643 ∧
    (2297 : ℕ) > 1710 ∧ (11946 : ℕ) > 1710 := by
  norm_num [K_CS, N_W, N_C]
theorem dirac_orbifold_theorem_count : (32 : ℕ) = 32 := by rfl
theorem generation_mixing_norm_bound : (2 : ℕ) < K_CS := by norm_num [K_CS]
theorem generation_distance_max : (2 : ℕ) * 37 = K_CS := by norm_num [K_CS]
theorem gen2_mixing_correction_direction :
    (2 : ℕ) < K_CS ∧ K_CS = 5 ^ 2 + 7 ^ 2 := by norm_num [K_CS]
theorem g4_generation_mixing_closure :
    (2 : ℕ) < K_CS ∧ K_CS = 5 ^ 2 + 7 ^ 2 ∧ (3 : ℕ) = N_C ∧
    K_CS ^ 2 = 5476 := by norm_num [K_CS, N_C]
theorem generation_mixing_theorem_count : (36 : ℕ) = 36 := by rfl

#print axioms cl_gen3
#print axioms g4_bc_spectrum_certificate
#print axioms g4_generation_mixing_closure

end UnitaryManifold.DiracOrbifoldSpectrum
