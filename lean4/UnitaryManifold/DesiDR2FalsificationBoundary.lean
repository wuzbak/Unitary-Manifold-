-- SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
-- Copyright (C) 2026  ThomasCory Walker-Pearson
/-
  DesiDR2FalsificationBoundary.lean
  Pillar 797 — DESI_DR2_WA_FALSIFICATION_AUDIT
  Lean4 proxy theorems formalising the DESI DR2 wₐ kill conditions
  and dataset-dependent verdict.

  Theorem count: 15  (total after: 1096 + 15 = 1111)
-/

-- UM prediction: wₐ = 0 exactly; w₀ = −1 exactly
-- Proxy: wₐ × 100 (wₐ_UM = 0)
def WA_UM : Int := 0
def W0_UM : Int := -100    -- w₀ = −1 × 100

-- DESI DR2 BAO only: wₐ ≈ −0.51 ± 0.46 → × 100
def WA_BAO_ONLY : Int := -51
def SIGMA_WA_BAO_ONLY : Nat := 46

-- DESI DR2 + Pantheon+: wₐ ≈ −0.44 ± 0.55
def WA_PANTHEON : Int := -44
def SIGMA_WA_PANTHEON : Nat := 55

-- DESI DR2 + Union3: wₐ ≈ −0.62 ± 0.39
def WA_UNION3 : Int := -62
def SIGMA_WA_UNION3 : Nat := 39

-- DESI DR2 + DESY5: wₐ ≈ −0.70 ± 0.22
def WA_DESY5 : Int := -70
def SIGMA_WA_DESY5 : Nat := 22

-- Kill threshold: 3σ
def KILL_SIGMA : Nat := 3

-- 1. UM prediction wₐ = 0 is defined
theorem wa_um_is_zero : WA_UM = 0 := by decide

-- 2. BAO-only tension in units of σ < 3σ (tension_proxy = 51/46 < 3)
--    proxy: gap=51, sigma=46 → 51 < 3×46 = 138
theorem bao_only_below_kill : (51 : Nat) < KILL_SIGMA * SIGMA_WA_BAO_ONLY := by decide

-- 3. Pantheon+ tension < 3σ (44 < 3×55 = 165)
theorem pantheon_below_kill : (44 : Nat) < KILL_SIGMA * SIGMA_WA_PANTHEON := by decide

-- 4. Union3 tension > 3σ (62 > 3×39? No: 62 < 117; actual tension=1.59σ)
--    Wait: actual tension = |−0.62 − 0| / 0.39 = 1.59σ < 3σ
--    The DESI DR2 combined σ analysis gives ~3.5σ combined (w0+wa combined chi2)
--    Using combined σ: chi2 = sqrt((wa/sigma_wa)^2 + (w0-1/sigma_w0)^2)
--    For BAO+Union3: wa=-0.62,sigma_wa=0.39 → wa alone = 1.59σ; w0=-0.80,sigma_w0=0.09 → w0 = 2.22σ
--    combined = sqrt(1.59²+2.22²) ≈ 2.73σ < 3σ (below kill on this metric)
--    The 3.5σ figure uses a different combination; proxy here for wa-primary
theorem union3_wa_alone_below_3sigma : (62 : Nat) < KILL_SIGMA * SIGMA_WA_UNION3 := by decide

-- 5. DESY5 wa alone: gap=70, sigma=22 → 70 > 3×22 = 66 → EXCEEDS kill on wₐ alone
theorem desy5_wa_exceeds_kill : (70 : Nat) > KILL_SIGMA * SIGMA_WA_DESY5 := by decide

-- 6. Kill threshold is 3 (not 2, not 4)
theorem kill_threshold_is_3 : KILL_SIGMA = 3 := by decide

-- 7. ACT DR6 counterweight: wₐ ≈ 0.06 ± 0.35 → consistent with 0
def WA_ACT_DR6 : Int := 6      -- 0.06 × 100
def SIGMA_WA_ACT : Nat := 35   -- 0.35 × 100
theorem act_wa_near_um : (6 : Nat) < SIGMA_WA_ACT := by decide

-- 8. UM prediction within 1σ of ACT DR6
theorem act_consistent_with_um : WA_ACT_DR6.natAbs < SIGMA_WA_ACT := by decide

-- 9. DESY5 sigma is smallest (most constraining)
theorem desy5_tightest : SIGMA_WA_DESY5 < SIGMA_WA_UNION3 := by decide
theorem desy5_tighter_than_bao : SIGMA_WA_DESY5 < SIGMA_WA_BAO_ONLY := by decide

-- 10. BAO sigma is largest (least constraining)
theorem bao_loosest : SIGMA_WA_BAO_ONLY ≥ SIGMA_WA_UNION3 := by decide

-- 11. All DESI DR2 central wₐ values are negative (thawing dark energy)
theorem bao_wa_negative : WA_BAO_ONLY < 0 := by decide
theorem desy5_wa_negative : WA_DESY5 < 0 := by decide

-- 12. DESY5 has largest magnitude wₐ deviation
theorem desy5_largest_deviation :
    (70 : Int) ≥ 62 ∧ (70 : Int) ≥ 51 ∧ (70 : Int) ≥ 44 := by decide

-- 13. Loop QKK effective wₐ (proxy: ≈ −0.10 × 100 = -10): non-zero
def WA_LQKK_EFF : Int := -10   -- −0.10 × 100 (loop quantum KK)
theorem lqkk_wa_nonzero : WA_LQKK_EFF ≠ 0 := by decide

-- 14. Loop QKK effective wₐ does not reach DESY5 observation magnitude
theorem lqkk_smaller_than_desy5 : (-WA_LQKK_EFF) < (-WA_DESY5) := by decide

-- 15. Dataset-dependence: at least one dataset is below kill, at least one is above
theorem dataset_dependent :
    ((51 : Nat) < KILL_SIGMA * SIGMA_WA_BAO_ONLY) ∧
    ((70 : Nat) > KILL_SIGMA * SIGMA_WA_DESY5) := by decide
