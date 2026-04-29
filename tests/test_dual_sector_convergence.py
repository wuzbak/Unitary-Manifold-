# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_dual_sector_convergence.py
======================================
Tests for src/core/dual_sector_convergence.py — Pillar 93.

Physical claims under test
---------------------------
1. The (5,6) sector independently predicts β ≈ 0.273° via the same
   CS formula g_aγγ = k_cs · α_EM / (2π² r_c) that gives β ≈ 0.331° for (5,7).
2. Both sectors survive all current CMB constraints simultaneously.
3. The β gap ≈ 0.058° is > 2 × σ_LB = 0.040°, making the two sectors
   discriminable by LiteBIRD.
4. The falsification_report correctly classifies measurements at β(5,7),
   β(5,6), in the forbidden gap, and outside the admissible window.
5. The dual-sector is a genuine geometric prediction: removing (5,6) leaves
   only one CMB survivor (verified against resonance_scan).

Test classes
------------
TestSectorConstants          — module-level constant sanity checks
TestComputeSectorPrediction  — DualSectorPrediction for (5,6) and (5,7)
TestBetaPredictions          — exact β values and the β ∝ k_cs scaling law
TestLiteBIRDDiscriminability — gap size and discriminability decision
TestFalsificationReport      — all four outcomes of falsification_report()
TestDualSectorReport         — dual_sector_report() structure
TestBigBangStatement         — big_bang_convergence_statement() content
TestGeometricNecessity       — both sectors emerge from resonance_scan
"""

from __future__ import annotations

import math

import pytest

from src.core.dual_sector_convergence import (
    # Constants
    N1_PRIMARY, N2_PRIMARY, K_CS_PRIMARY,
    N1_SHADOW,  N2_SHADOW,  K_CS_SHADOW,
    C_S_PRIMARY, C_S_SHADOW,
    BETA_PRIMARY_DEG, BETA_SHADOW_DEG, BETA_GAP_DEG,
    SIGMA_LITEBIRD_DEG, LITEBIRD_SIGMA_SEPARATION,
    BETA_ADMISSIBLE_LOWER, BETA_ADMISSIBLE_UPPER,
    BETA_GAP_LOWER, BETA_GAP_UPPER,
    DISCRIMINABILITY_THRESHOLD_SIGMA,
    # Functions
    compute_sector_prediction,
    dual_sector_report,
    litebird_can_discriminate,
    falsification_report,
    big_bang_convergence_statement,
    # Dataclass
    DualSectorPrediction,
)


# ===========================================================================
# TestSectorConstants
# ===========================================================================

class TestSectorConstants:
    """Module-level constants encode the correct sector identities."""

    def test_primary_winding_numbers(self):
        """Primary sector is (5,7)."""
        assert N1_PRIMARY == 5
        assert N2_PRIMARY == 7

    def test_shadow_winding_numbers(self):
        """Shadow sector is (5,6)."""
        assert N1_SHADOW == 5
        assert N2_SHADOW == 6

    def test_primary_kcs_is_sum_of_squares(self):
        """k_cs = 5² + 7² = 74."""
        assert K_CS_PRIMARY == N1_PRIMARY**2 + N2_PRIMARY**2
        assert K_CS_PRIMARY == 74

    def test_shadow_kcs_is_sum_of_squares(self):
        """k_cs = 5² + 6² = 61."""
        assert K_CS_SHADOW == N1_SHADOW**2 + N2_SHADOW**2
        assert K_CS_SHADOW == 61

    def test_primary_sound_speed_exact_rational(self):
        """c_s(5,7) = (7²−5²)/74 = 24/74 = 12/37 exactly."""
        expected = (N2_PRIMARY**2 - N1_PRIMARY**2) / K_CS_PRIMARY
        assert abs(C_S_PRIMARY - expected) < 1e-15
        assert abs(C_S_PRIMARY - 12.0 / 37.0) < 1e-15

    def test_shadow_sound_speed_exact_rational(self):
        """c_s(5,6) = (6²−5²)/61 = 11/61 exactly."""
        expected = (N2_SHADOW**2 - N1_SHADOW**2) / K_CS_SHADOW
        assert abs(C_S_SHADOW - expected) < 1e-15
        assert abs(C_S_SHADOW - 11.0 / 61.0) < 1e-15

    def test_primary_cs_greater_than_shadow(self):
        """(5,7) has larger sound speed than (5,6): 12/37 > 11/61."""
        assert C_S_PRIMARY > C_S_SHADOW

    def test_litebird_sigma_is_canonical_value(self):
        """σ_LB = 0.020° matches LiteBIRD specification."""
        assert abs(SIGMA_LITEBIRD_DEG - 0.020) < 1e-10

    def test_discriminability_threshold_is_2sigma(self):
        """Default discriminability threshold is 2σ."""
        assert DISCRIMINABILITY_THRESHOLD_SIGMA == 2.0

    def test_admissible_window_bounds(self):
        """Admissible window [0.22°, 0.38°] matches litebird_boundary.py."""
        assert abs(BETA_ADMISSIBLE_LOWER - 0.22) < 1e-10
        assert abs(BETA_ADMISSIBLE_UPPER - 0.38) < 1e-10

    def test_beta_primary_above_shadow(self):
        """β(5,7) > β(5,6): primary sector has larger birefringence."""
        assert BETA_PRIMARY_DEG > BETA_SHADOW_DEG

    def test_beta_gap_is_difference(self):
        """BETA_GAP_DEG = BETA_PRIMARY_DEG − BETA_SHADOW_DEG."""
        assert abs(BETA_GAP_DEG - (BETA_PRIMARY_DEG - BETA_SHADOW_DEG)) < 1e-12

    def test_beta_gap_lower_above_shadow(self):
        """Forbidden-gap lower bound is above the (5,6) peak."""
        assert BETA_GAP_LOWER > BETA_SHADOW_DEG

    def test_beta_gap_upper_below_primary(self):
        """Forbidden-gap upper bound is below the (5,7) peak."""
        assert BETA_GAP_UPPER < BETA_PRIMARY_DEG


# ===========================================================================
# TestComputeSectorPrediction
# ===========================================================================

class TestComputeSectorPrediction:
    """compute_sector_prediction returns a complete DualSectorPrediction."""

    def test_returns_dataclass_primary(self):
        pred = compute_sector_prediction(N1_PRIMARY, N2_PRIMARY)
        assert isinstance(pred, DualSectorPrediction)

    def test_returns_dataclass_shadow(self):
        pred = compute_sector_prediction(N1_SHADOW, N2_SHADOW)
        assert isinstance(pred, DualSectorPrediction)

    def test_primary_winding_numbers_stored(self):
        pred = compute_sector_prediction(5, 7)
        assert pred.n1 == 5
        assert pred.n2 == 7

    def test_shadow_winding_numbers_stored(self):
        pred = compute_sector_prediction(5, 6)
        assert pred.n1 == 5
        assert pred.n2 == 6

    def test_primary_kcs_stored(self):
        pred = compute_sector_prediction(5, 7)
        assert pred.k_cs == 74

    def test_shadow_kcs_stored(self):
        pred = compute_sector_prediction(5, 6)
        assert pred.k_cs == 61

    def test_primary_sound_speed(self):
        pred = compute_sector_prediction(5, 7)
        assert abs(pred.c_s - 12.0 / 37.0) < 1e-10

    def test_shadow_sound_speed(self):
        pred = compute_sector_prediction(5, 6)
        assert abs(pred.c_s - 11.0 / 61.0) < 1e-10

    def test_primary_ns_within_planck_1sigma(self):
        """(5,7) nₛ is within 1σ of Planck 2018 central value."""
        pred = compute_sector_prediction(5, 7)
        assert pred.ns_sigma <= 1.0

    def test_shadow_ns_within_planck_1sigma(self):
        """(5,6) nₛ is within 1σ of Planck 2018 central value."""
        pred = compute_sector_prediction(5, 6)
        assert pred.ns_sigma <= 1.0

    def test_primary_satisfies_bicep(self):
        pred = compute_sector_prediction(5, 7)
        assert pred.satisfies_bicep is True
        assert pred.r_eff < 0.036

    def test_shadow_satisfies_bicep(self):
        pred = compute_sector_prediction(5, 6)
        assert pred.satisfies_bicep is True
        assert pred.r_eff < 0.036

    def test_primary_beta_in_admissible_window(self):
        pred = compute_sector_prediction(5, 7)
        assert BETA_ADMISSIBLE_LOWER <= pred.beta_deg <= BETA_ADMISSIBLE_UPPER

    def test_shadow_beta_in_admissible_window(self):
        pred = compute_sector_prediction(5, 6)
        assert BETA_ADMISSIBLE_LOWER <= pred.beta_deg <= BETA_ADMISSIBLE_UPPER

    def test_primary_is_lossless(self):
        pred = compute_sector_prediction(5, 7)
        assert pred.is_lossless is True

    def test_shadow_is_lossless(self):
        pred = compute_sector_prediction(5, 6)
        assert pred.is_lossless is True

    def test_primary_beta_matches_constant(self):
        pred = compute_sector_prediction(5, 7)
        assert abs(pred.beta_deg - BETA_PRIMARY_DEG) < 1e-10

    def test_shadow_beta_matches_constant(self):
        pred = compute_sector_prediction(5, 6)
        assert abs(pred.beta_deg - BETA_SHADOW_DEG) < 1e-10

    def test_label_contains_winding_numbers(self):
        pred = compute_sector_prediction(5, 7)
        assert "5" in pred.label and "7" in pred.label

    def test_invalid_n1_raises(self):
        with pytest.raises(ValueError):
            compute_sector_prediction(0, 5)

    def test_invalid_n2_not_greater_raises(self):
        with pytest.raises(ValueError):
            compute_sector_prediction(5, 5)

    def test_invalid_n2_less_than_n1_raises(self):
        with pytest.raises(ValueError):
            compute_sector_prediction(7, 5)


# ===========================================================================
# TestBetaPredictions
# ===========================================================================

class TestBetaPredictions:
    """β values and the linear β ∝ k_cs scaling law."""

    def test_beta_primary_approx_value(self):
        """β(5,7) ≈ 0.273°–0.38° (admissible window)."""
        assert 0.22 < BETA_PRIMARY_DEG < 0.38

    def test_beta_shadow_approx_value(self):
        """β(5,6) ≈ 0.22°–0.38° (admissible window)."""
        assert 0.22 < BETA_SHADOW_DEG < 0.38

    def test_beta_scales_linearly_with_kcs(self):
        """β ∝ k_cs because g_aγγ = k_cs · α_EM / (2π² r_c).

        Therefore β(5,6) / β(5,7) = k_cs(5,6) / k_cs(5,7) = 61/74.
        """
        expected_ratio = K_CS_SHADOW / K_CS_PRIMARY  # 61/74
        actual_ratio = BETA_SHADOW_DEG / BETA_PRIMARY_DEG
        assert abs(actual_ratio - expected_ratio) < 1e-10

    def test_beta_ratio_is_61_over_74(self):
        """Exact ratio: β(5,6)/β(5,7) = 61/74."""
        assert abs(BETA_SHADOW_DEG / BETA_PRIMARY_DEG - 61.0 / 74.0) < 1e-10

    def test_beta_gap_positive(self):
        """β gap is positive: (5,7) birefringence > (5,6)."""
        assert BETA_GAP_DEG > 0.0

    def test_beta_gap_exceeds_single_litebird_sigma(self):
        """Gap > 1σ_LB: LiteBIRD can see the gap at 1σ."""
        assert BETA_GAP_DEG > SIGMA_LITEBIRD_DEG

    def test_beta_primary_not_in_gap(self):
        """β(5,7) is NOT in the forbidden gap zone."""
        assert not (BETA_GAP_LOWER < BETA_PRIMARY_DEG < BETA_GAP_UPPER)

    def test_beta_shadow_not_in_gap(self):
        """β(5,6) is NOT in the forbidden gap zone."""
        assert not (BETA_GAP_LOWER < BETA_SHADOW_DEG < BETA_GAP_UPPER)

    def test_both_betas_differ(self):
        """The two sector β predictions are distinct values."""
        assert BETA_PRIMARY_DEG != BETA_SHADOW_DEG


# ===========================================================================
# TestLiteBIRDDiscriminability
# ===========================================================================

class TestLiteBIRDDiscriminability:
    """LiteBIRD can resolve the two sectors."""

    def test_litebird_sigma_separation_above_threshold(self):
        """Gap / σ_LB ≥ 2.0σ (discriminability threshold)."""
        assert LITEBIRD_SIGMA_SEPARATION >= DISCRIMINABILITY_THRESHOLD_SIGMA

    def test_litebird_sigma_separation_value(self):
        """Gap / σ_LB = BETA_GAP_DEG / SIGMA_LITEBIRD_DEG."""
        expected = BETA_GAP_DEG / SIGMA_LITEBIRD_DEG
        assert abs(LITEBIRD_SIGMA_SEPARATION - expected) < 1e-10

    def test_litebird_can_discriminate_returns_true(self):
        """litebird_can_discriminate() returns True at current gap/σ_LB."""
        assert litebird_can_discriminate() is True

    def test_gap_in_sigma_is_finite_and_positive(self):
        assert math.isfinite(LITEBIRD_SIGMA_SEPARATION)
        assert LITEBIRD_SIGMA_SEPARATION > 0.0

    def test_gap_exceeds_2_sigma_litebird(self):
        """Gap > 2 × σ_LB: sufficient for a 2σ-level discrimination."""
        assert BETA_GAP_DEG > 2.0 * SIGMA_LITEBIRD_DEG


# ===========================================================================
# TestFalsificationReport
# ===========================================================================

class TestFalsificationReport:
    """falsification_report correctly classifies all four outcomes."""

    def test_primary_measurement_selects_primary(self):
        """A measurement exactly at β(5,7) with small σ selects (5,7)."""
        result = falsification_report(BETA_PRIMARY_DEG, SIGMA_LITEBIRD_DEG)
        assert result["primary_selected"] is True
        assert result["shadow_selected"]  is False
        assert result["framework_falsified"] is False
        assert result["ambiguous"] is False

    def test_shadow_measurement_selects_shadow(self):
        """A measurement exactly at β(5,6) with small σ selects (5,6)."""
        result = falsification_report(BETA_SHADOW_DEG, SIGMA_LITEBIRD_DEG)
        assert result["shadow_selected"]  is True
        assert result["primary_selected"] is False
        assert result["framework_falsified"] is False
        assert result["ambiguous"] is False

    def test_out_of_window_falsifies_framework(self):
        """A measurement at β=0.10° (outside [0.22°, 0.38°]) falsifies the framework."""
        result = falsification_report(0.10, SIGMA_LITEBIRD_DEG)
        assert result["framework_falsified"] is True
        assert result["primary_selected"] is False
        assert result["shadow_selected"]  is False

    def test_in_forbidden_gap_falsifies_framework(self):
        """A measurement in the gap (0.30°) falsifies the framework."""
        gap_center = (BETA_GAP_LOWER + BETA_GAP_UPPER) / 2.0
        result = falsification_report(gap_center, 0.001)
        assert result["framework_falsified"] is True
        assert result["in_forbidden_gap"] is True

    def test_large_sigma_centered_on_shadow_is_ambiguous(self):
        """A measurement at β(5,6) with σ = gap_deg is within 1σ of *both* peaks.

        sigma_from_primary = |β(5,6) − β(5,7)| / σ = gap / gap = 1.0 ≤ 2.0σ
        sigma_from_shadow  = 0 / gap = 0.0 ≤ 2.0σ
        → both compatible → AMBIGUOUS (not falsified, not selected).
        """
        large_sigma = BETA_GAP_DEG  # σ = full gap → primary is exactly 1σ away
        result = falsification_report(BETA_SHADOW_DEG, large_sigma)
        assert result["ambiguous"] is True
        assert result["framework_falsified"] is False

    def test_sigma_from_primary_computed_correctly(self):
        """sigma_from_primary = |β_meas − β_primary| / σ_meas."""
        beta_meas = BETA_PRIMARY_DEG + 0.010
        sigma = 0.020
        result = falsification_report(beta_meas, sigma)
        expected = 0.010 / 0.020  # = 0.5σ
        assert abs(result["sigma_from_primary"] - expected) < 1e-10

    def test_sigma_from_shadow_computed_correctly(self):
        """sigma_from_shadow = |β_meas − β_shadow| / σ_meas."""
        beta_meas = BETA_SHADOW_DEG + 0.010
        sigma = 0.020
        result = falsification_report(beta_meas, sigma)
        expected = 0.010 / 0.020  # = 0.5σ
        assert abs(result["sigma_from_shadow"] - expected) < 1e-10

    def test_in_admissible_window_flag_for_primary(self):
        result = falsification_report(BETA_PRIMARY_DEG, SIGMA_LITEBIRD_DEG)
        assert result["in_admissible_window"] is True

    def test_in_admissible_window_flag_for_shadow(self):
        result = falsification_report(BETA_SHADOW_DEG, SIGMA_LITEBIRD_DEG)
        assert result["in_admissible_window"] is True

    def test_not_in_forbidden_gap_for_primary(self):
        result = falsification_report(BETA_PRIMARY_DEG, SIGMA_LITEBIRD_DEG)
        assert result["in_forbidden_gap"] is False

    def test_not_in_forbidden_gap_for_shadow(self):
        result = falsification_report(BETA_SHADOW_DEG, SIGMA_LITEBIRD_DEG)
        assert result["in_forbidden_gap"] is False

    def test_verdict_string_nonempty(self):
        result = falsification_report(BETA_PRIMARY_DEG, SIGMA_LITEBIRD_DEG)
        assert len(result["verdict"]) > 10

    def test_result_keys_complete(self):
        result = falsification_report(BETA_PRIMARY_DEG, SIGMA_LITEBIRD_DEG)
        required = {
            "beta_measured_deg", "sigma_measured_deg",
            "sigma_from_primary", "sigma_from_shadow",
            "in_admissible_window", "in_forbidden_gap",
            "primary_selected", "shadow_selected",
            "framework_falsified", "ambiguous", "verdict",
        }
        assert required.issubset(set(result.keys()))

    def test_high_beta_out_of_window(self):
        """β=0.90° is outside the admissible window — falsified."""
        result = falsification_report(0.90, SIGMA_LITEBIRD_DEG)
        assert result["framework_falsified"] is True
        assert result["in_admissible_window"] is False


# ===========================================================================
# TestDualSectorReport
# ===========================================================================

class TestDualSectorReport:
    """dual_sector_report() returns the full machine-readable summary."""

    @pytest.fixture(scope="class")
    def report(self):
        return dual_sector_report()

    def test_has_primary_key(self, report):
        assert "primary" in report

    def test_has_shadow_key(self, report):
        assert "shadow" in report

    def test_primary_is_correct_sector(self, report):
        assert report["primary"].n1 == 5
        assert report["primary"].n2 == 7

    def test_shadow_is_correct_sector(self, report):
        assert report["shadow"].n1 == 5
        assert report["shadow"].n2 == 6

    def test_beta_gap_key(self, report):
        assert abs(report["beta_gap_deg"] - BETA_GAP_DEG) < 1e-12

    def test_litebird_sigma_separation_key(self, report):
        assert abs(report["litebird_sigma_separation"] - LITEBIRD_SIGMA_SEPARATION) < 1e-10

    def test_litebird_can_discriminate_key(self, report):
        assert report["litebird_can_discriminate"] is True

    def test_admissible_window_key(self, report):
        lo, hi = report["admissible_window"]
        assert abs(lo - 0.22) < 1e-10
        assert abs(hi - 0.38) < 1e-10

    def test_both_lossless_key(self, report):
        assert report["both_lossless"] is True

    def test_interpretation_is_string(self, report):
        assert isinstance(report["interpretation"], str)
        assert len(report["interpretation"]) > 50

    def test_gap_bounds_in_report(self, report):
        assert "gap_lower" in report
        assert "gap_upper" in report
        assert report["gap_lower"] < report["gap_upper"]


# ===========================================================================
# TestBigBangStatement
# ===========================================================================

class TestBigBangStatement:
    """big_bang_convergence_statement() contains the key physical claims."""

    @pytest.fixture(scope="class")
    def statement(self):
        return big_bang_convergence_statement()

    def test_returns_nonempty_string(self, statement):
        assert isinstance(statement, str)
        assert len(statement) > 100

    def test_mentions_dual_sector(self, statement):
        assert "DUAL" in statement.upper() or "dual" in statement.lower()

    def test_mentions_big_bang(self, statement):
        assert "Big Bang" in statement or "BIG BANG" in statement

    def test_mentions_primary_sector(self, statement):
        assert "(5,7)" in statement

    def test_mentions_shadow_sector(self, statement):
        assert "(5,6)" in statement

    def test_mentions_litebird(self, statement):
        assert "LiteBIRD" in statement

    def test_mentions_falsification(self, statement):
        upper = statement.upper()
        assert "FALSIF" in upper

    def test_mentions_ftum_fixed_point(self, statement):
        assert "FTUM" in statement

    def test_mentions_equilibrium(self, statement):
        assert "equilibrium" in statement.lower() or "EQUILIBRIUM" in statement

    def test_mentions_k_cs_values(self, statement):
        assert "74" in statement and "61" in statement

    def test_discriminable_label_present(self, statement):
        assert "DISCRIMINABLE" in statement.upper()

    def test_authorship_present(self, statement):
        assert "Walker-Pearson" in statement
        assert "Copilot" in statement


# ===========================================================================
# TestGeometricNecessity
# ===========================================================================

class TestGeometricNecessity:
    """Both sectors emerge from resonance_scan; removing (5,6) leaves one survivor."""

    def test_both_sectors_in_resonance_scan_bicep_1sigma(self):
        """resonance_scan at BICEP/Keck limit and 1σ nₛ window returns both sectors."""
        from src.core.braided_winding import resonance_scan, R_BICEP_KECK_95
        results = resonance_scan(n_max=10, r_limit=R_BICEP_KECK_95, ns_sigma_max=1.0)
        pairs = {(p.n1, p.n2) for p in results}
        assert (5, 7) in pairs
        assert (5, 6) in pairs

    def test_exactly_two_survivors(self):
        """Exactly two (n₁, n₂) pairs survive the BICEP/Keck + 1σ nₛ filter."""
        from src.core.braided_winding import resonance_scan, R_BICEP_KECK_95
        results = resonance_scan(n_max=10, r_limit=R_BICEP_KECK_95, ns_sigma_max=1.0)
        assert len(results) == 2

    def test_removing_56_leaves_only_57(self):
        """Filtering out (5,6) from the scan leaves only (5,7)."""
        from src.core.braided_winding import resonance_scan, R_BICEP_KECK_95
        results = resonance_scan(n_max=10, r_limit=R_BICEP_KECK_95, ns_sigma_max=1.0)
        without_56 = [(p.n1, p.n2) for p in results if (p.n1, p.n2) != (5, 6)]
        assert len(without_56) == 1
        assert without_56[0] == (5, 7)

    def test_removing_57_leaves_only_56(self):
        """Filtering out (5,7) from the scan leaves only (5,6)."""
        from src.core.braided_winding import resonance_scan, R_BICEP_KECK_95
        results = resonance_scan(n_max=10, r_limit=R_BICEP_KECK_95, ns_sigma_max=1.0)
        without_57 = [(p.n1, p.n2) for p in results if (p.n1, p.n2) != (5, 7)]
        assert len(without_57) == 1
        assert without_57[0] == (5, 6)

    def test_kcs_values_are_61_and_74(self):
        """The two survivors have k_cs ∈ {61, 74} — the shadow and primary levels."""
        from src.core.braided_winding import resonance_scan, R_BICEP_KECK_95
        results = resonance_scan(n_max=10, r_limit=R_BICEP_KECK_95, ns_sigma_max=1.0)
        kcs_values = {r.k_cs for r in results}
        assert kcs_values == {61, 74}

    def test_56_prediction_matches_compute_sector(self):
        """The (5,6) BraidedPrediction from resonance_scan matches compute_sector_prediction."""
        from src.core.braided_winding import resonance_scan, R_BICEP_KECK_95
        results = resonance_scan(n_max=10, r_limit=R_BICEP_KECK_95, ns_sigma_max=1.0)
        pred_56 = next(p for p in results if (p.n1, p.n2) == (5, 6))
        sector_56 = compute_sector_prediction(5, 6)
        assert abs(pred_56.ns - sector_56.ns) < 1e-8
        assert abs(pred_56.r_eff - sector_56.r_eff) < 1e-8
