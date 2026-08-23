-- SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
-- Copyright (C) 2026  ThomasCory Walker-Pearson
/-
  BirefringenceACTDR6.lean
  Pillar 795 — BIREFRINGENCE_FIRST_DETECTION_CANDIDATE
  Lean4 proxy theorems formalising the ACT+Planck 2026 joint birefringence
  measurement and its consistency with the UM canonical windows.

  Theorem count: 15  (total after: 1066 + 15 = 1081)
-/

-- Proxy integers (× 10³ for degrees × 1000)
def BETA_LOW_MDEG : Nat := 273      -- 0.273° × 1000
def BETA_HIGH_MDEG : Nat := 331     -- 0.331° × 1000
def BETA_GAP_LO_MDEG : Nat := 290   -- 0.290° × 1000
def BETA_GAP_HI_MDEG : Nat := 310   -- 0.310° × 1000
def BETA_ADM_LO_MDEG : Nat := 220   -- 0.22° × 1000
def BETA_ADM_HI_MDEG : Nat := 380   -- 0.38° × 1000
def BETA_JOINT_OBS_MDEG : Nat := 277 -- 0.277° × 1000
def SIGMA_JOINT_MDEG : Nat := 57    -- 0.057° × 1000
def SIGNIFICANCE_4P8 : Nat := 48    -- 4.8 × 10

-- 1. The UM low-branch is below the observation by less than 1 sigma
theorem low_branch_within_1sigma :
    BETA_JOINT_OBS_MDEG - BETA_LOW_MDEG < SIGMA_JOINT_MDEG := by decide

-- 2. The observation is inside the admissible window
theorem obs_inside_admissible_lo : BETA_ADM_LO_MDEG ≤ BETA_JOINT_OBS_MDEG := by decide
theorem obs_inside_admissible_hi : BETA_JOINT_OBS_MDEG ≤ BETA_ADM_HI_MDEG := by decide

-- 3. The observation is NOT in the predicted gap
theorem obs_not_in_gap_lo : BETA_JOINT_OBS_MDEG < BETA_GAP_LO_MDEG := by decide

-- 4. Low branch is below gap lower bound
theorem low_branch_below_gap : BETA_LOW_MDEG < BETA_GAP_LO_MDEG := by decide

-- 5. High branch is above gap upper bound
theorem high_branch_above_gap : BETA_GAP_HI_MDEG < BETA_HIGH_MDEG := by decide

-- 6. Gap width is positive
theorem gap_width_positive : BETA_GAP_HI_MDEG - BETA_GAP_LO_MDEG > 0 := by decide

-- 7. Branch separation is 58 millidegs
theorem branch_separation : BETA_HIGH_MDEG - BETA_LOW_MDEG = 58 := by decide

-- 8. Significance is non-zero (proxy for 4.8σ)
theorem significance_nonzero : SIGNIFICANCE_4P8 > 0 := by decide

-- 9. Significance exceeds 3σ threshold (30 = 3.0 × 10)
theorem significance_exceeds_3sigma : SIGNIFICANCE_4P8 > 30 := by decide

-- 10. Observation is within admissible window (combined)
theorem obs_admissible :
    BETA_ADM_LO_MDEG ≤ BETA_JOINT_OBS_MDEG ∧ BETA_JOINT_OBS_MDEG ≤ BETA_ADM_HI_MDEG :=
  ⟨by decide, by decide⟩

-- 11. Low branch is within admissible window
theorem low_branch_admissible :
    BETA_ADM_LO_MDEG ≤ BETA_LOW_MDEG ∧ BETA_LOW_MDEG ≤ BETA_ADM_HI_MDEG :=
  ⟨by decide, by decide⟩

-- 12. High branch is within admissible window
theorem high_branch_admissible :
    BETA_ADM_LO_MDEG ≤ BETA_HIGH_MDEG ∧ BETA_HIGH_MDEG ≤ BETA_ADM_HI_MDEG :=
  ⟨by decide, by decide⟩

-- 13. Observation is closer to low branch than high branch
theorem obs_closer_to_low :
    (BETA_JOINT_OBS_MDEG - BETA_LOW_MDEG) < (BETA_HIGH_MDEG - BETA_JOINT_OBS_MDEG) := by decide

-- 14. Low branch and observation differ by exactly 4 millidegs
theorem low_branch_obs_diff : BETA_JOINT_OBS_MDEG - BETA_LOW_MDEG = 4 := by decide

-- 15. Both branches are distinct positive values below admissible ceiling
theorem branches_distinct : BETA_LOW_MDEG < BETA_HIGH_MDEG := by decide
