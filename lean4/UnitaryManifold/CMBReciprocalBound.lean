/- SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
Copyright (C) 2026 ThomasCory Walker-Pearson

Conditional arithmetic only: this does not establish a warp-profile bound.
-/
import Mathlib

namespace UnitaryManifold.CMBReciprocalBound

theorem reciprocal_upper_bound (sMin s : ℝ) (hpos : 0 < sMin)
    (hbound : sMin ≤ s) : 1 / s ≤ 1 / sMin := by
  exact one_div_le_one_div_of_le hpos hbound

theorem positive_lower_bound_permits_closure (sMin : ℝ)
    (hpos : 0 < sMin) (hbelow : sMin ≤ 1) :
    ∃ s : ℝ, 0 < s ∧ sMin ≤ s ∧ 1 / s = 1 := by
  exact ⟨1, zero_lt_one, hbelow, one_div_one⟩

end UnitaryManifold.CMBReciprocalBound
