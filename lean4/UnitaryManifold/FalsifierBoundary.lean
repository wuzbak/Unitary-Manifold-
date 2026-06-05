import Mathlib.Tactic

namespace UnitaryManifold

/-- LiteBIRD admissible interval endpoints are ordered. -/
theorem litebird_window_order : (0.22:ℚ) < 0.38 := by
  norm_num

/-- Forbidden-gap endpoints are ordered and lie inside admissible window. -/
theorem litebird_gap_order_and_containment :
    (0.29:ℚ) < 0.31 ∧ 0.22 < (0.29:ℚ) ∧ (0.31:ℚ) < 0.38 := by
  norm_num

end UnitaryManifold
