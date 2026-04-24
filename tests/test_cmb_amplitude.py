# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cmb_amplitude.py
============================
Test suite for src/core/cmb_amplitude.py — Pillar 52.

Covers:
  - COBE normalization check: λ_COBE fixes Aₛ, zero remaining freedom
  - COBE normalization ratio ≈ 1.000 (sub-0.01% accuracy)
  - Spectral index from COBE check matches UM canonical value
  - Tower correction factor ≥ 1 (always boosts amplitude)
  - Tower correction approaches 1 as R→0 (zero-mode dominance)
  - Acoustic peak suppression structure and documentation
  - Residual suppression after tower correction
  - Full amplitude gap audit keys and consistency
  - Boundary / error conditions
"""

import math
import pytest

from src.core.cmb_amplitude import (
    ACOUSTIC_SUPPRESSION_MAX,
    ACOUSTIC_SUPPRESSION_MIN,
    BICEP_R_LIMIT,
    C_S,
    K_CS,
    K_PIVOT_MPC,
    LCDM_FIRST_PEAK_DL,
    LCDM_FIRST_PEAK_ELL,
    N_W,
    PLANCK_AS,
    PLANCK_AS_SIGMA,
    PLANCK_NS,
    PLANCK_NS_SIGMA,
    R_C_PLANCK,
    UM_NS,
    UM_R_BRAIDED,
    acoustic_peak_suppression,
    amplitude_gap_audit,
    cobe_normalization_check,
    residual_suppression,
    tower_correction_factor,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_planck_as_value(self):
        assert abs(PLANCK_AS - 2.101e-9) < 1e-13

    def test_planck_as_sigma_positive(self):
        assert PLANCK_AS_SIGMA > 0

    def test_planck_ns_canonical(self):
        assert abs(PLANCK_NS - 0.9649) < 1e-6

    def test_um_ns_near_planck(self):
        # UM nₛ ≈ 0.9635 is within ~0.3σ of Planck
        sigma = abs(UM_NS - PLANCK_NS) / PLANCK_NS_SIGMA
        assert sigma < 1.0

    def test_um_r_braided_below_bicep(self):
        assert UM_R_BRAIDED < BICEP_R_LIMIT

    def test_bicep_r_limit_is_0_036(self):
        assert abs(BICEP_R_LIMIT - 0.036) < 1e-6

    def test_acoustic_suppression_range(self):
        assert ACOUSTIC_SUPPRESSION_MIN == 4.0
        assert ACOUSTIC_SUPPRESSION_MAX == 7.0

    def test_k_pivot(self):
        assert abs(K_PIVOT_MPC - 0.05) < 1e-6

    def test_lcdm_first_peak_ell(self):
        assert abs(LCDM_FIRST_PEAK_ELL - 220.0) < 1.0

    def test_k_cs_canonical(self):
        assert K_CS == 74

    def test_n_w_canonical(self):
        assert N_W == 5

    def test_c_s_canonical(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12


# ---------------------------------------------------------------------------
# COBE normalization check
# ---------------------------------------------------------------------------

class TestCobeNormalizationCheck:
    def setup_method(self):
        self.result = cobe_normalization_check()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_required_keys(self):
        required = [
            "phi0_eff", "ns", "r_braided", "lam_cobe",
            "As_predicted", "As_target", "As_ratio",
            "ns_sigma_planck", "r_within_bicep", "normalization_resolved",
        ]
        for k in required:
            assert k in self.result, f"Missing key: {k}"

    def test_as_ratio_near_unity(self):
        # After COBE normalization, Aₛ should equal target to machine precision
        assert abs(self.result["As_ratio"] - 1.0) < 1e-10

    def test_as_predicted_matches_planck(self):
        assert abs(self.result["As_predicted"] - PLANCK_AS) / PLANCK_AS < 1e-10

    def test_lam_cobe_positive(self):
        assert self.result["lam_cobe"] > 0

    def test_lam_cobe_very_small(self):
        # The GW coupling must be extremely small to give Aₛ ~ 10⁻⁹
        # Typical: λ_COBE ~ 10⁻¹³
        assert self.result["lam_cobe"] < 1e-9

    def test_ns_near_um_canonical(self):
        # nₛ from COBE check should match UM canonical value
        assert abs(self.result["ns"] - UM_NS) < 0.005

    def test_ns_within_planck_2sigma(self):
        sigma = abs(self.result["ns"] - PLANCK_NS) / PLANCK_NS_SIGMA
        assert sigma < 2.0

    def test_ns_sigma_planck_matches(self):
        expected_sigma = abs(self.result["ns"] - PLANCK_NS) / PLANCK_NS_SIGMA
        assert abs(self.result["ns_sigma_planck"] - expected_sigma) < 1e-10

    def test_r_braided_correct(self):
        assert abs(self.result["r_braided"] - UM_R_BRAIDED) < 1e-10

    def test_r_within_bicep_true(self):
        assert self.result["r_within_bicep"] is True

    def test_normalization_resolved_true(self):
        assert self.result["normalization_resolved"] is True

    def test_phi0_eff_around_31(self):
        # φ₀_eff = 5 × 2π × √1 ≈ 31.42
        assert abs(self.result["phi0_eff"] - 5.0 * 2.0 * math.pi) < 0.01

    def test_target_echo(self):
        assert abs(self.result["As_target"] - PLANCK_AS) < 1e-15

    def test_different_phi0_bare(self):
        result = cobe_normalization_check(phi0_bare=0.95)
        assert result["lam_cobe"] > 0
        assert abs(result["As_ratio"] - 1.0) < 1e-8

    def test_different_n_winding(self):
        result = cobe_normalization_check(n_winding=7)
        assert result["phi0_eff"] > self.result["phi0_eff"]

    def test_lam_scales_linearly_with_As_target(self):
        r1 = cobe_normalization_check(As_target=1e-9)
        r2 = cobe_normalization_check(As_target=2e-9)
        assert abs(r2["lam_cobe"] / r1["lam_cobe"] - 2.0) < 1e-8


# ---------------------------------------------------------------------------
# Tower correction factor
# ---------------------------------------------------------------------------

class TestTowerCorrectionFactor:
    def test_default_positive(self):
        C = tower_correction_factor()
        assert C > 0

    def test_default_at_least_one(self):
        # Zero-mode only would give C = 1; tower always adds
        C = tower_correction_factor()
        assert C >= 1.0

    def test_canonical_R1_L1_value(self):
        # With R=1, L=1, n_max=20: visible tower → C > 1
        C = tower_correction_factor(n_max=20, R=1.0, L=1.0)
        assert C > 1.0

    def test_larger_n_max_gives_larger_correction(self):
        C10 = tower_correction_factor(n_max=10, R=1.0, L=1.0)
        C20 = tower_correction_factor(n_max=20, R=1.0, L=1.0)
        assert C20 >= C10

    def test_convergence_monotone(self):
        # Adding more modes always increases C
        prev = tower_correction_factor(n_max=1, R=1.0, L=1.0)
        for n in range(2, 11):
            curr = tower_correction_factor(n_max=n, R=1.0, L=1.0)
            assert curr >= prev
            prev = curr

    def test_n_max_zero_gives_one(self):
        C = tower_correction_factor(n_max=0)
        assert C == 1.0

    def test_raises_on_non_positive_R(self):
        with pytest.raises(ValueError):
            tower_correction_factor(R=0.0)

    def test_raises_on_non_positive_L(self):
        with pytest.raises(ValueError):
            tower_correction_factor(L=0.0)

    def test_larger_k_cs_gives_larger_correction(self):
        # Larger k_cs → w_n = exp(-n²/k_cs) closer to 1 → larger correction
        C_small_k = tower_correction_factor(k_cs=10, R=1.0, L=1.0)
        C_large_k = tower_correction_factor(k_cs=100, R=1.0, L=1.0)
        assert C_large_k > C_small_k

    def test_large_L_R_ratio_increases_Delta_n(self):
        # Larger L/R → larger Δ_n → smaller (Δ₀/Δ_n)² → smaller correction
        C_small_ratio = tower_correction_factor(n_max=5, R=1.0, L=1.0)
        C_large_ratio = tower_correction_factor(n_max=5, R=1.0, L=100.0)
        assert C_small_ratio > C_large_ratio

    def test_formula_manual_n_max_1(self):
        # C = 1 + w_1 × (Δ₀/Δ_1)² where w_1 = exp(-1/74), Δ₁ = 2 + sqrt(4 + (L/R)²)
        n_max, R, L, k_cs = 1, 1.0, 1.0, 74
        w1 = math.exp(-1.0 / k_cs)
        Delta_1 = 2.0 + math.sqrt(4.0 + (L / R) ** 2)
        expected = 1.0 + w1 * (2.0 / Delta_1) ** 2
        result = tower_correction_factor(n_max=n_max, R=R, L=L, k_cs=k_cs)
        assert abs(result - expected) < 1e-14


# ---------------------------------------------------------------------------
# Acoustic peak suppression
# ---------------------------------------------------------------------------

class TestAcousticPeakSuppression:
    def setup_method(self):
        self.result = acoustic_peak_suppression()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_required_keys(self):
        required = [
            "ells", "T_UM", "suppression_factor",
            "mean_suppression", "max_suppression", "min_suppression",
            "tower_correction", "gap_documented", "gap_source",
        ]
        for k in required:
            assert k in self.result, f"Missing key: {k}"

    def test_ells_list_nonempty(self):
        assert len(self.result["ells"]) > 0

    def test_T_UM_same_length_as_ells(self):
        assert len(self.result["T_UM"]) == len(self.result["ells"])

    def test_suppression_factor_same_length(self):
        assert len(self.result["suppression_factor"]) == len(self.result["ells"])

    def test_T_UM_positive(self):
        for t in self.result["T_UM"]:
            assert t > 0

    def test_suppression_positive(self):
        for s in self.result["suppression_factor"]:
            assert s > 0

    def test_gap_documented_true(self):
        assert self.result["gap_documented"] is True

    def test_gap_source_nonempty_string(self):
        assert isinstance(self.result["gap_source"], str)
        assert len(self.result["gap_source"]) > 100

    def test_tower_correction_geq_one(self):
        assert self.result["tower_correction"] >= 1.0

    def test_mean_suppression_positive(self):
        assert self.result["mean_suppression"] > 0

    def test_max_geq_mean_geq_min(self):
        assert self.result["max_suppression"] >= self.result["mean_suppression"]
        assert self.result["mean_suppression"] >= self.result["min_suppression"]

    def test_custom_ells(self):
        custom_ells = [100.0, 500.0, 1000.0]
        result = acoustic_peak_suppression(ells=custom_ells)
        assert len(result["ells"]) == 3
        assert result["ells"] == custom_ells

    def test_single_ell(self):
        result = acoustic_peak_suppression(ells=[220.0])
        assert len(result["T_UM"]) == 1
        assert len(result["suppression_factor"]) == 1


# ---------------------------------------------------------------------------
# Residual suppression
# ---------------------------------------------------------------------------

class TestResidualSuppression:
    def setup_method(self):
        self.result = residual_suppression()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_required_keys(self):
        required = [
            "tower_correction", "residual_factor_min", "residual_factor_max",
            "residual_factor_mean_osc", "documented_range", "missing_physics",
        ]
        for k in required:
            assert k in self.result, f"Missing key: {k}"

    def test_tower_correction_geq_one(self):
        assert self.result["tower_correction"] >= 1.0

    def test_documented_range_correct(self):
        lo, hi = self.result["documented_range"]
        assert lo == ACOUSTIC_SUPPRESSION_MIN
        assert hi == ACOUSTIC_SUPPRESSION_MAX

    def test_residual_factor_min_positive(self):
        assert self.result["residual_factor_min"] > 0

    def test_residual_factor_max_positive(self):
        assert self.result["residual_factor_max"] > 0

    def test_residual_max_geq_min(self):
        assert self.result["residual_factor_max"] >= self.result["residual_factor_min"]

    def test_missing_physics_is_list(self):
        mp = self.result["missing_physics"]
        assert isinstance(mp, list)
        assert len(mp) >= 5

    def test_missing_physics_nonempty_strings(self):
        for item in self.result["missing_physics"]:
            assert isinstance(item, str)
            assert len(item) > 5

    def test_boltzmann_in_missing_physics(self):
        combined = " ".join(self.result["missing_physics"]).lower()
        assert "boltzmann" in combined

    def test_residual_mean_osc_positive(self):
        assert self.result["residual_factor_mean_osc"] > 0


# ---------------------------------------------------------------------------
# Amplitude gap audit
# ---------------------------------------------------------------------------

class TestAmplitudeGapAudit:
    def setup_method(self):
        self.audit = amplitude_gap_audit()

    def test_returns_dict(self):
        assert isinstance(self.audit, dict)

    def test_required_keys(self):
        required = [
            "cobe_check", "tower_correction", "residual_info",
            "gap_status", "As_at_pivot_resolved", "As_at_peaks_resolved",
            "path_to_closure",
        ]
        for k in required:
            assert k in self.audit, f"Missing key: {k}"

    def test_cobe_check_is_dict(self):
        assert isinstance(self.audit["cobe_check"], dict)

    def test_gap_status_open(self):
        assert self.audit["gap_status"] == "OPEN"

    def test_pivot_amplitude_resolved(self):
        # COBE normalization fixes Aₛ at the pivot scale
        assert self.audit["As_at_pivot_resolved"] is True

    def test_acoustic_peaks_not_resolved(self):
        # The ×4–7 suppression is an open problem
        assert self.audit["As_at_peaks_resolved"] is False

    def test_tower_correction_geq_one(self):
        assert self.audit["tower_correction"] >= 1.0

    def test_path_to_closure_is_string(self):
        assert isinstance(self.audit["path_to_closure"], str)
        assert len(self.audit["path_to_closure"]) > 50

    def test_path_mentions_boltzmann(self):
        assert "boltzmann" in self.audit["path_to_closure"].lower()

    def test_residual_info_is_dict(self):
        assert isinstance(self.audit["residual_info"], dict)

    def test_cobe_check_ratio_near_unity(self):
        assert abs(self.audit["cobe_check"]["As_ratio"] - 1.0) < 1e-8

    def test_cobe_check_normalization_resolved(self):
        assert self.audit["cobe_check"]["normalization_resolved"] is True

    def test_residual_info_has_missing_physics(self):
        assert "missing_physics" in self.audit["residual_info"]
        assert len(self.audit["residual_info"]["missing_physics"]) >= 5

    def test_audit_custom_phi0(self):
        audit = amplitude_gap_audit(phi0_bare=0.95)
        assert audit["gap_status"] == "OPEN"
        assert audit["As_at_pivot_resolved"] is True


# ---------------------------------------------------------------------------
# Cross-consistency
# ---------------------------------------------------------------------------

class TestCrossConsistency:
    def test_tower_correction_consistent_across_functions(self):
        C1 = tower_correction_factor()
        audit = amplitude_gap_audit()
        C2 = audit["tower_correction"]
        assert abs(C1 - C2) < 1e-10

    def test_cobe_normalization_independent_of_lam(self):
        # nₛ and r should not depend on λ (only on φ₀_eff)
        r1 = cobe_normalization_check(phi0_bare=1.0)
        r2 = cobe_normalization_check(phi0_bare=1.0, As_target=1e-9)
        assert abs(r1["ns"] - r2["ns"]) < 1e-14
        assert abs(r1["r_braided"] - r2["r_braided"]) < 1e-14

    def test_lam_cobe_scales_with_As_target(self):
        r1 = cobe_normalization_check(As_target=PLANCK_AS)
        r2 = cobe_normalization_check(As_target=2.0 * PLANCK_AS)
        assert abs(r2["lam_cobe"] / r1["lam_cobe"] - 2.0) < 1e-8

    def test_r_within_bicep_always_true_for_canonical(self):
        result = cobe_normalization_check()
        assert result["r_within_bicep"] is True

    def test_gap_documented_in_suppression(self):
        result = acoustic_peak_suppression()
        assert result["gap_documented"] is True
