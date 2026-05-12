/-!
# Numerical Spot-Checks — verified at compile time via `#guard`

Every `#guard` assertion causes a **compile error** if false.
These run in O(1) time using kernel reduction.
-/

namespace UnitaryManifold.NumericalChecks

-- K_CS = 5² + 7²
#guard (5 ^ 2 + 7 ^ 2 : Nat) == 74

-- n_w = 5 is odd
#guard (5 : Nat) % 2 == 1

-- K_CS - n_w² = 7²
#guard (74 : Nat) - 5 ^ 2 == 7 ^ 2

-- gcd(12, 37) = 1 (c_s = 12/37 irreducible)
#guard Nat.gcd 12 37 == 1

-- 35 * 2 < 74 (ξ_c = 35/74 < 1/2)
#guard 35 * 2 < (74 : Nat)

-- ---------------------------------------------------------------------------
-- Extended: contract_library_extended T2–T20 arithmetic guards
-- ---------------------------------------------------------------------------

-- T14 / T19: K_CS = 5² + 7² (redundant but explicit for Extended module)
#guard (5 ^ 2 + 7 ^ 2 : Nat) == 74

-- T18: N_C = n_w - 2 = 3
#guard (5 : Nat) - 2 == 3

-- T11: 3*4 < 74 (3/74 < 1/4 iff 12 < 74)
#guard 3 * 4 < (74 : Nat)

-- T11: 3 > 0 (alpha_GUT = 3/74 > 0)
#guard (3 : Nat) > 0

-- T5 / T7: 2*n_w < K_CS (slow-roll epsilon small relative to K_CS)
#guard 2 * 5 < (74 : Nat)

-- T8: coefficient check (6 - 2 = 4; n_s = 1 - 4ε uses 4 = 6 - 2)
#guard (6 : Nat) - 2 == 4

end UnitaryManifold.NumericalChecks
