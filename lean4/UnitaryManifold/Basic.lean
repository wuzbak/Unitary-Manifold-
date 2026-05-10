/-!
# Unitary Manifold — Core Algebraic Theorems (Lean 4 + Mathlib)

Machine-checked proofs of the three algebraic identities from
`src/core/formal_proof_hardening.py`, plus arithmetic verification
of the fundamental UM constants.
-/
import Mathlib.Tactic

namespace UnitaryManifold

/-- K_CS = 5² + 7² = 74 (Chern-Simons resonance level). -/
theorem k_cs_resonance : 5 ^ 2 + 7 ^ 2 = (74 : ℕ) := by native_decide

/-- Winding number n_w = 5 is odd (Z₂ parity). -/
theorem n_w_is_odd : 5 % 2 = (1 : ℕ) := by native_decide

/-- K_CS − n_w² = 7² (partner braid). -/
theorem k_cs_partner_braid : (74 : ℕ) - 5 ^ 2 = 7 ^ 2 := by native_decide

/-- gcd(12, 37) = 1: sound speed 12/37 is in lowest terms. -/
theorem c_s_irreducible : Nat.gcd 12 37 = 1 := by native_decide

/-- ξ_c = 35/74 < 1/2 (consciousness coupling below symmetry point). -/
theorem xi_c_below_half : (35 : ℚ) / 74 < 1 / 2 := by norm_num

/-- c_s = 12/37 ∈ (0, 1). -/
theorem c_s_in_unit_interval : (0 : ℚ) < 12 / 37 ∧ (12 : ℚ) / 37 < 1 := by
  constructor <;> norm_num

/-- **T1-NS-EQ**: n_s = 1 − 2/N_e equals 1 − 8·N_w/φ₀² when N_e = φ₀²/(4·N_w). -/
theorem t1_ns_eq (φ₀ N_w : ℝ) (hφ : φ₀ ≠ 0) (hN : N_w ≠ 0) :
    1 - 2 / (φ₀ ^ 2 / (4 * N_w)) = 1 - 8 * N_w / φ₀ ^ 2 := by
  have h1 : φ₀ ^ 2 ≠ 0 := pow_ne_zero _ hφ
  have h2 : (4 : ℝ) * N_w ≠ 0 := mul_ne_zero (by norm_num) hN
  field_simp [h1, h2]
  ring

/-- **T1-R-EQ**: r = (8/N_e)·c_s equals (32·N_w/φ₀²)·c_s. -/
theorem t1_r_eq (φ₀ N_w c_s : ℝ) (hφ : φ₀ ≠ 0) (hN : N_w ≠ 0) :
    8 / (φ₀ ^ 2 / (4 * N_w)) * c_s = 32 * N_w / φ₀ ^ 2 * c_s := by
  have h1 : φ₀ ^ 2 ≠ 0 := pow_ne_zero _ hφ
  have h2 : (4 : ℝ) * N_w ≠ 0 := mul_ne_zero (by norm_num) hN
  field_simp [h1, h2]
  ring

/-- **T1-WKK-EQ**: w_KK equation-of-state is a tautology. -/
theorem t1_w_kk_eq (c_s : ℝ) :
    -1 + 2 / 3 * c_s ^ 2 = -1 + 2 / 3 * c_s ^ 2 := rfl

end UnitaryManifold
