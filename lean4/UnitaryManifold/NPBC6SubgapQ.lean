/-!
# Unitary Manifold — NP-BC-6 Sub-gap Q: Holographic Screen Entropy Algebraic Kernel (Lean 4 + Mathlib)

**Pillar 619: NP_BC6_SUBGAP_Q_HOLOGRAPHIC_SCREEN_KERNEL_PROVED**

This file formalises the arithmetic kernel for the holographic screen entropy
residual inside NP-BC-6. The statements are algebraic proxies for the
Bousso-bound / Ryu-Takayanagi structure of the 5D KK bulk holographic screen.
Only finite Mathlib-verifiable arithmetic is claimed.

## What IS proved in this file
1. Holographic bound proxy: 1 ≤ k_cs.
2. Screen area proxy: k_cs = 74.
3. Entropy floor (half CS level): k_cs / 2 = 37.
4. Screen dimension bound: 4 × n_w < k_cs (20 < 74).
5. CS-level parity (bosonic): k_cs mod 2 = 0.
6. Braid screen link: n_w² + n_2² = k_cs.
7. Entropy monotone proxy: n_w < k_cs.
8. Winding-screen capacity: n_w × k_cs = 370.
9. Half-level entropy: k_cs / 2 = k_cs_half.
10. Screen entropy balance: k_cs - k_cs_half = k_cs_half.
11. Summary theorem: holographic screen kernel consistent.

## What is NOT proved
- The full Ryu-Takayanagi formula in the 5D KK bulk.
- Bousso covariant entropy bound in the curved RS1 background.
- Non-perturbative quantum corrections to the screen entropy.

## Contribution: 11 new theorems
Total after this file: 319 + 11 = 330 theorems
-/
import Mathlib.Tactic
import Mathlib.Data.Nat.Parity
import Mathlib.Algebra.BigOperators.Basic
import Mathlib.Data.Nat.Defs

namespace UnitaryManifold.NPBC6SubgapQ

def k_cs : ℕ := 74
def n_w : ℕ := 5
def n_2 : ℕ := 7
def k_cs_half : ℕ := 37

theorem holographic_bound_proxy : 1 ≤ k_cs := by decide

theorem screen_area_proxy : k_cs = 74 := by rfl

theorem entropy_floor_half_cs : k_cs / 2 = 37 := by decide

theorem screen_dimension_bound : 4 * n_w < k_cs := by decide

theorem cs_level_parity_bosonic : k_cs % 2 = 0 := by decide

theorem braid_screen_link : n_w ^ 2 + n_2 ^ 2 = k_cs := by decide

theorem entropy_monotone_proxy : n_w < k_cs := by decide

theorem winding_screen_capacity : n_w * k_cs = 370 := by decide

theorem half_level_entropy : k_cs / 2 = k_cs_half := by decide

theorem screen_entropy_balance : k_cs - k_cs_half = k_cs_half := by decide

theorem np_bc6_subgap_q_holographic_kernel :
    1 ≤ k_cs ∧
    n_w ^ 2 + n_2 ^ 2 = k_cs ∧
    k_cs / 2 = k_cs_half ∧
    k_cs - k_cs_half = k_cs_half := by
  exact ⟨by decide, by decide, by decide, by decide⟩

end UnitaryManifold.NPBC6SubgapQ
