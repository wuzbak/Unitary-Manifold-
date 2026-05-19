# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 282 — CMB Planck Cross-Check (ADJACENT_TRACK_NON_HARDGATE).

Covers: sound horizon, comoving distance, naive/corrected peak positions,
ISW phase shift, UM vs Planck comparison, n_s sensitivity, separation guard.
"""

import math
import pytest

from src.core.cmb_um_planck_crosscheck import (
    A_S_UM,
    DELTA_PHI,
    DELTA_PHI_OVER_PI,
    N_S_UM,
    OMEGA_B,
    OMEGA_CDM,
    OMEGA_M,
    PLANCK_PEAKS,
    R_UM,
    STATUS,
    Z_STAR,
    comoving_angular_diameter_distance_to_recombination,
    corrected_peak_position,
    isw_phase_shift,
    naive_peak_position,
    separation_guard,
    sound_horizon_at_recombination,
    sound_horizon_components,
    summary,
    um_ns_sensitivity_check,
    um_vs_planck_peak_comparison,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_status_is_adjacent_track(self):
        assert STATUS == "ADJACENT_TRACK_NON_HARDGATE"

    def test_n_s_value(self):
        assert abs(N_S_UM - 0.9635) < 1e-6

    def test_r_um_value(self):
        assert abs(R_UM - 0.0315) < 1e-6

    def test_a_s_value(self):
        assert abs(A_S_UM - 2.101e-9) < 1e-14

    def test_omega_b_reasonable(self):
        assert 0.020 < OMEGA_B < 0.026

    def test_omega_cdm_reasonable(self):
        assert 0.10 < OMEGA_CDM < 0.14

    def test_omega_m_is_sum(self):
        assert abs(OMEGA_M - (OMEGA_B + OMEGA_CDM)) < 1e-10

    def test_z_star_value(self):
        assert Z_STAR == 1090

    def test_planck_peaks_dict(self):
        assert set(PLANCK_PEAKS.keys()) == {1, 2, 3, 4, 5}
        assert PLANCK_PEAKS[1] == 220
        assert PLANCK_PEAKS[3] == 810

    def test_delta_phi_over_pi(self):
        assert abs(DELTA_PHI_OVER_PI - 0.267) < 1e-6

    def test_delta_phi_value(self):
        assert abs(DELTA_PHI - 0.267 * math.pi) < 1e-6


# ---------------------------------------------------------------------------
# 1. Sound horizon
# ---------------------------------------------------------------------------

class TestSoundHorizon:
    def test_sound_horizon_reasonable(self):
        """r_s must be in [100, 200] Mpc."""
        r_s = sound_horizon_at_recombination()
        assert 100.0 < r_s < 200.0

    def test_sound_horizon_near_planck(self):
        """r_s should be within 10% of Planck 2018 reference 144.4 Mpc."""
        r_s = sound_horizon_at_recombination()
        assert abs(r_s - 144.4) / 144.4 < 0.10

    def test_sound_horizon_returns_float(self):
        assert isinstance(sound_horizon_at_recombination(), float)

    def test_sound_horizon_components_keys(self):
        comp = sound_horizon_components()
        assert "r_s_fit_mpc" in comp
        assert "r_s_planck_ref_mpc" in comp
        assert "r_s_used_mpc" in comp

    def test_sound_horizon_components_consistent(self):
        comp = sound_horizon_components()
        assert comp["r_s_used_mpc"] == sound_horizon_at_recombination()

    def test_sound_horizon_fit_positive(self):
        comp = sound_horizon_components()
        assert comp["r_s_fit_mpc"] > 0.0


# ---------------------------------------------------------------------------
# 2. Comoving angular diameter distance
# ---------------------------------------------------------------------------

class TestComovingDistance:
    def test_comoving_distance_reasonable(self):
        """χ★ must be in [12000, 16000] Mpc."""
        chi = comoving_angular_diameter_distance_to_recombination()
        assert 12000.0 < chi < 16000.0

    def test_comoving_distance_near_planck(self):
        """χ★ should be within 5% of Planck 2018 reference 13885 Mpc."""
        chi = comoving_angular_diameter_distance_to_recombination()
        assert abs(chi - 13885.0) / 13885.0 < 0.05

    def test_comoving_distance_returns_float(self):
        assert isinstance(comoving_angular_diameter_distance_to_recombination(), float)

    def test_comoving_distance_positive(self):
        chi = comoving_angular_diameter_distance_to_recombination()
        assert chi > 0.0


# ---------------------------------------------------------------------------
# 3. Naive peak positions
# ---------------------------------------------------------------------------

class TestNaivePeaks:
    def test_naive_peak_1_approx_300(self):
        """Naive ℓ_1 ∈ [270, 330] — significantly above observed 220."""
        ell1 = naive_peak_position(1)
        assert 270.0 < ell1 < 330.0

    def test_naive_peak_returns_float(self):
        assert isinstance(naive_peak_position(1), float)

    def test_naive_peak_monotonically_increasing(self):
        peaks = [naive_peak_position(n) for n in range(1, 6)]
        for i in range(len(peaks) - 1):
            assert peaks[i] < peaks[i + 1]

    def test_naive_peak_linearly_spaced(self):
        """Naive peaks are exactly linearly spaced (ℓ_n = n * const)."""
        ell1 = naive_peak_position(1)
        ell2 = naive_peak_position(2)
        ell3 = naive_peak_position(3)
        assert abs(ell2 / ell1 - 2.0) < 1e-6
        assert abs(ell3 / ell1 - 3.0) < 1e-6

    def test_naive_peak_5_above_1000(self):
        assert naive_peak_position(5) > 1000.0


# ---------------------------------------------------------------------------
# 4. ISW phase shift
# ---------------------------------------------------------------------------

class TestISWPhaseShift:
    def test_isw_phase_shift_value(self):
        """Δφ_ISW ≈ 0.267π ≈ 0.8388 rad."""
        phi = isw_phase_shift()
        assert abs(phi - 0.267 * math.pi) < 1e-6

    def test_isw_phase_shift_positive(self):
        assert isw_phase_shift() > 0.0

    def test_isw_phase_shift_less_than_pi(self):
        assert isw_phase_shift() < math.pi

    def test_isw_phase_shift_returns_float(self):
        assert isinstance(isw_phase_shift(), float)


# ---------------------------------------------------------------------------
# 5. Corrected peak positions
# ---------------------------------------------------------------------------

class TestCorrectedPeaks:
    def test_corrected_peak_1_near_220(self):
        """Corrected ℓ_1 ∈ [200, 240]."""
        ell1 = corrected_peak_position(1)
        assert 200.0 < ell1 < 240.0

    def test_corrected_peak_2_near_540(self):
        """Corrected ℓ_2 ∈ [500, 580]."""
        ell2 = corrected_peak_position(2)
        assert 500.0 < ell2 < 580.0

    def test_corrected_peak_3_near_810(self):
        """Corrected ℓ_3 ∈ [770, 860]."""
        ell3 = corrected_peak_position(3)
        assert 770.0 < ell3 < 860.0

    def test_corrected_peak_4_near_1120(self):
        """Corrected ℓ_4 ∈ [1060, 1190]."""
        ell4 = corrected_peak_position(4)
        assert 1060.0 < ell4 < 1190.0

    def test_corrected_peak_5_near_1440(self):
        """Corrected ℓ_5 ∈ [1350, 1530]."""
        ell5 = corrected_peak_position(5)
        assert 1350.0 < ell5 < 1530.0

    def test_corrected_less_than_naive(self):
        """ISW correction always reduces ℓ_n relative to naive."""
        for n in range(1, 6):
            assert corrected_peak_position(n) < naive_peak_position(n)

    def test_peak_positions_monotonically_increasing(self):
        peaks = [corrected_peak_position(n) for n in range(1, 6)]
        for i in range(len(peaks) - 1):
            assert peaks[i] < peaks[i + 1]

    def test_corrected_peak_returns_float(self):
        assert isinstance(corrected_peak_position(1), float)

    def test_corrected_spacing_roughly_constant(self):
        """Higher peaks should be roughly uniformly spaced (~300 apart)."""
        ell1 = corrected_peak_position(1)
        ell2 = corrected_peak_position(2)
        ell3 = corrected_peak_position(3)
        spacing_12 = ell2 - ell1
        spacing_23 = ell3 - ell2
        assert abs(spacing_12 - spacing_23) < 5.0   # within 5 ℓ


# ---------------------------------------------------------------------------
# 6. UM vs Planck comparison
# ---------------------------------------------------------------------------

class TestUMPlanckComparison:
    @pytest.fixture(scope="class")
    def comparison(self):
        return um_vs_planck_peak_comparison()

    def test_comparison_has_peaks_key(self, comparison):
        assert "peaks" in comparison

    def test_comparison_has_rms_offset(self, comparison):
        assert "rms_offset" in comparison

    def test_comparison_has_conclusion(self, comparison):
        assert "conclusion" in comparison

    def test_comparison_has_note(self, comparison):
        assert "note" in comparison
        assert "Pillar 73" in comparison["note"]

    def test_all_five_peaks_present(self, comparison):
        assert set(comparison["peaks"].keys()) == {1, 2, 3, 4, 5}

    def test_each_peak_has_required_fields(self, comparison):
        for n, data in comparison["peaks"].items():
            assert "planck" in data
            assert "um" in data
            assert "fractional_offset" in data

    def test_um_planck_comparison_rms_reasonable(self, comparison):
        """RMS fractional offset across all 5 peaks must be < 10%."""
        assert comparison["rms_offset"] < 0.10

    def test_conclusion_is_consistent_or_offset_small(self, comparison):
        assert comparison["conclusion"] in ("CONSISTENT", "OFFSET_SMALL", "OFFSET_LARGE")

    def test_planck_reference_values_correct(self, comparison):
        assert comparison["peaks"][1]["planck"] == 220
        assert comparison["peaks"][2]["planck"] == 540
        assert comparison["peaks"][3]["planck"] == 810

    def test_fractional_offset_peak_1_under_15_percent(self, comparison):
        assert abs(comparison["peaks"][1]["fractional_offset"]) < 0.15

    def test_conclusion_detail_contains_rms(self, comparison):
        assert "conclusion_detail" in comparison
        assert "%" in comparison["conclusion_detail"]


# ---------------------------------------------------------------------------
# 7. n_s sensitivity check
# ---------------------------------------------------------------------------

class TestNsSensitivity:
    @pytest.fixture(scope="class")
    def ns_check(self):
        return um_ns_sensitivity_check()

    def test_ns_effect_negligible(self, ns_check):
        assert ns_check["n_s_effect_on_peaks"] == "negligible"

    def test_dominant_factors_is_list(self, ns_check):
        assert isinstance(ns_check["dominant_factors"], list)
        assert len(ns_check["dominant_factors"]) >= 3

    def test_delta_ns_small(self, ns_check):
        assert ns_check["delta_n_s"] < 0.01

    def test_estimated_shift_tiny(self, ns_check):
        """Estimated peak shift due to Δn_s should be < 1%."""
        assert ns_check["estimated_peak_position_shift_percent"] < 1.0

    def test_ns_um_value_correct(self, ns_check):
        assert abs(ns_check["n_s_um"] - 0.9635) < 1e-6


# ---------------------------------------------------------------------------
# 8. Separation guard
# ---------------------------------------------------------------------------

class TestSeparationGuard:
    def test_separation_guard_returns_string(self):
        assert isinstance(separation_guard(), str)

    def test_separation_guard_mentions_adjacent_track(self):
        assert "ADJACENT_TRACK_NON_HARDGATE" in separation_guard()

    def test_separation_guard_mentions_toe_score(self):
        assert "ToE score" in separation_guard()

    def test_separation_guard_mentions_boltzmann(self):
        assert "Boltzmann" in separation_guard()


# ---------------------------------------------------------------------------
# 9. Summary convenience function
# ---------------------------------------------------------------------------

class TestSummary:
    @pytest.fixture(scope="class")
    def s(self):
        return summary()

    def test_summary_has_status(self, s):
        assert s["status"] == "ADJACENT_TRACK_NON_HARDGATE"

    def test_summary_r_s_present(self, s):
        assert 100.0 < s["r_s_mpc"] < 200.0

    def test_summary_chi_star_present(self, s):
        assert 12000.0 < s["chi_star_mpc"] < 16000.0

    def test_summary_naive_ell_1_approx_300(self, s):
        assert 270.0 < s["naive_ell_1"] < 330.0

    def test_summary_corrected_ell_1_approx_220(self, s):
        assert 200.0 < s["corrected_ell_1"] < 240.0

    def test_summary_isw_phase_shift(self, s):
        assert abs(s["isw_phase_shift_rad"] - 0.267 * math.pi) < 1e-3

    def test_summary_separation_guard(self, s):
        assert "ADJACENT_TRACK_NON_HARDGATE" in s["separation"]
