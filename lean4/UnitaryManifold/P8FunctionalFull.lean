-- SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
-- Copyright (C) 2026  ThomasCory Walker-Pearson
/-!
# P8 Float proxy audit — withdrawn functional-space closure

The historical `P8_FULL_FUNCTIONAL_PROOF_LEAN4_COMPLETE` claim is withdrawn.
IEEE Float arithmetic is not exact real arithmetic or a Sobolev-space model.
The counterexamples below refute the former unrestricted coercivity,
monotonicity and strict-positive-second-variation claims. They are explicitly
named refutations, not weaker replacement proofs of the historical claims.

Retired invalid declarations:
* `coercivity_lower_bound`: NaN is not ordered.
* `coercivity_grows_with_norm`: negative inputs reverse square ordering.
* `lsc_convergent_sequence_bounded_below`: a list containing NaN has no
  ordered lower bound; even NaN reflexivity fails.
* `second_variation_positive`: positive inputs can square to zero.

Retired unsupported declarations (not asserted to be refuted):
* `poincare_constant_positive`: the pinned API has no `Float.pi`.
* `lsc_monotone_sequence_has_liminf`, `phi_star_global_minimum_norm_bound`
  and `phi_star_unique_on_orbifold_quotient`: their former ordered-ring
  tactic arguments do not apply to Float.
* `phi_star_orbifold_minimum_at_phi0`: propositional Float equality was not
  proved by its decidability tactic. The separately named IEEE comparison
  below checks only one value and does not establish uniqueness.

The former `True` declarations claiming LSC, uniqueness, Sobolev regularity,
attainment, extension, full functional closure and closed proof stubs are
retired, including `p8_full_functional_proof_complete` and
`p8_sorry_stubs_closed`. No functional-space closure certificate is exported.
The checked finite computations below do not prove the corresponding
continuous functional-analysis claims, which remain open.
-/

namespace UnitaryManifold.P8FunctionalFull

def K_CS : Nat := 74
def alpha_coerce : Float := 0.743
def beta_coerce : Float := 0.012

theorem alpha_coerce_positive : (0.0 : Float) < alpha_coerce := by
  native_decide

theorem beta_coerce_nonnegative : (0.0 : Float) ≤ beta_coerce := by
  native_decide

theorem coercivity_positive_at_unit :
    0 < alpha_coerce * 1.0 ^ 2 - beta_coerce := by
  native_decide

theorem coercivity_lower_bound_nan_counterexample :
    ¬ (alpha_coerce * (0.0 / 0.0 : Float) ^ 2 - beta_coerce ≤
      (0.0 / 0.0 : Float) ^ 2) := by
  native_decide

theorem coercivity_grows_with_norm_negative_counterexample :
    (-2.0 : Float) < -1.0 ∧
      ¬ (alpha_coerce * (-2.0 : Float) ^ 2 <
        alpha_coerce * (-1.0 : Float) ^ 2) := by
  constructor <;> native_decide

/-- The existing conditional identity is not an LSC theorem. -/
theorem lsc_in_weak_limit (s_inf s_final : Float) (h : s_inf ≤ s_final) :
    s_inf ≤ s_final := h

theorem lsc_nan_reflexivity_counterexample :
    ¬ ((0.0 / 0.0 : Float) ≤ (0.0 / 0.0 : Float)) := by
  native_decide

theorem second_variation_positive_underflow_counterexample :
    (0.0 : Float) < 1e-200 ∧
      ¬ ((0.0 : Float) < alpha_coerce * (1e-200 : Float) ^ 2) := by
  constructor <;> native_decide

theorem second_variation_positive_at_sample :
    0 < alpha_coerce * (1e-4 : Float) ^ 2 := by
  native_decide

theorem phi_star_unit_nonnegative_check :
    (1.0 : Float) ≥ 0.0 ∧ (1.0 : Float) ≥ 1.0 := by
  constructor <;> native_decide

/-- IEEE comparison at one point, not propositional equality or uniqueness. -/
theorem phi_star_orbifold_potential_at_unit_ieee_check :
    (alpha_coerce * (1.0 ^ 2 - 1.0) ^ 2 == (0.0 : Float)) = true := by
  native_decide

end UnitaryManifold.P8FunctionalFull
