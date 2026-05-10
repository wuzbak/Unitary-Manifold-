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

-- n_w² + (n_w+2)² = K_CS  (Pythagorean-like braid identity: 5²+7²=74)
#guard 5 ^ 2 + 7 ^ 2 == (74 : Nat)

end UnitaryManifold.NumericalChecks
