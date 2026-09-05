/- SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
Copyright (C) 2026 ThomasCory Walker-Pearson

Conditional ordered-field arithmetic only: this does not establish a
warp-profile bound. No property specific to the real-number construction is used.
-/
import Mathlib.Algebra.Order.Field.Basic

namespace UnitaryManifold.CMBReciprocalBound

variable {α : Type*} [Field α] [LinearOrder α]

theorem reciprocal_upper_bound [IsStrictOrderedRing α] (sMin s : α) (hpos : 0 < sMin)
    (hbound : sMin ≤ s) : 1 / s ≤ 1 / sMin := by
  exact one_div_le_one_div_of_le hpos hbound

theorem positive_lower_bound_permits_closure (sMin : α)
    (hpos : 0 < sMin) (hbelow : sMin ≤ 1) :
    ∃ s : α, 0 < s ∧ sMin ≤ s ∧ 1 / s = 1 := by
  exact ⟨1, lt_of_lt_of_le hpos hbelow, hbelow, one_div_one⟩

#print axioms reciprocal_upper_bound
#print axioms positive_lower_bound_permits_closure

end UnitaryManifold.CMBReciprocalBound
