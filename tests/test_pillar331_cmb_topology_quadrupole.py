# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 331 — CMB Quadrupole/Octopole Topology Prediction."""
import math
import pytest

from src.core.pillar331_cmb_topology_quadrupole import (
    N_W, K_CS, PI_KR, C_S,
    F_BRAID, L_BRAID, L_MIN_WINDING,
    PLANCK_C2_SUPPRESSION_LOW, PLANCK_C2_SUPPRESSION_HIGH,
    UM_C2_SUPPRESSION,
    separation_guard,
    braiding_fraction,
    suppression_scale_ell,
    cmb_power_suppression_factor,
    suppressed_spectrum,
    compare_to_planck_observation,
    falsification_condition,
    quadrupole_suppression_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_f_braid(self):
        assert abs(F_BRAID - 5.0 / 74.0) < 1e-12

    def test_l_braid(self):
        assert abs(L_BRAID - 74.0 / 10.0) < 1e-10

    def test_l_min_winding(self):
        expected = 2.0 * math.pi * 5
        assert abs(L_MIN_WINDING - expected) < 1e-10

    def test_planck_range_valid(self):
        assert 0.0 < PLANCK_C2_SUPPRESSION_LOW < PLANCK_C2_SUPPRESSION_HIGH < 1.0

    def test_um_c2_suppression_range(self):
        # UM predicts S(ℓ=2) ∈ (0, 1)
        assert 0.0 < UM_C2_SUPPRESSION < 1.0

    def test_um_c2_near_one(self):
        # Suppression is small (6.8% fractional) → S close to 1
        assert UM_C2_SUPPRESSION > 0.9


class TestSeparationGuard:
    def test_is_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent_track(self):
        assert "ADJACENT" in separation_guard()


class TestBraidingFraction:
    def test_default(self):
        assert abs(braiding_fraction() - 5.0 / 74.0) < 1e-12

    def test_parameterized(self):
        assert abs(braiding_fraction(7, 74) - 7.0 / 74.0) < 1e-12

    def test_positive(self):
        assert braiding_fraction() > 0

    def test_less_than_one(self):
        assert braiding_fraction() < 1.0


class TestSuppressionScale:
    def test_default(self):
        assert abs(suppression_scale_ell() - 7.4) < 1e-10

    def test_parameterized(self):
        assert abs(suppression_scale_ell(5, 74) - 7.4) < 1e-10

    def test_positive(self):
        assert suppression_scale_ell() > 0


class TestCMBPowerSuppression:
    def test_factor_between_0_and_1(self):
        for ell in [2, 3, 5, 10, 20, 50, 100]:
            s = cmb_power_suppression_factor(ell)
            assert 0.0 < s <= 1.0, f"Suppression out of range for ell={ell}"

    def test_suppression_decreases_at_low_ell(self):
        # More suppression at lower ell (closer to ℓ=0)
        s2 = cmb_power_suppression_factor(2)
        s10 = cmb_power_suppression_factor(10)
        s100 = cmb_power_suppression_factor(100)
        assert s2 <= s10 <= s100

    def test_approaches_1_at_high_ell(self):
        # At ℓ >> ℓ_braid, suppression should be negligible
        s = cmb_power_suppression_factor(1000)
        assert s > 0.999

    def test_at_ell_2_matches_constant(self):
        s = cmb_power_suppression_factor(2)
        assert abs(s - UM_C2_SUPPRESSION) < 1e-10

    def test_raises_on_nonpositive_ell(self):
        with pytest.raises(ValueError):
            cmb_power_suppression_factor(0)

    def test_formula(self):
        # S(ℓ) = 1 - f × exp(-(ℓ/L)²)
        ell = 5.0
        expected = 1.0 - F_BRAID * math.exp(-(ell / L_BRAID) ** 2)
        assert abs(cmb_power_suppression_factor(ell) - expected) < 1e-12

    def test_custom_f_and_l(self):
        s = cmb_power_suppression_factor(10, f_braid=0.1, l_braid=5.0)
        expected = 1.0 - 0.1 * math.exp(-(10.0 / 5.0) ** 2)
        assert abs(s - expected) < 1e-12


class TestSuppressedSpectrum:
    def test_returns_list(self):
        ells = [2, 3, 10, 100]
        result = suppressed_spectrum(ells)
        assert isinstance(result, list)
        assert len(result) == len(ells)

    def test_has_required_keys(self):
        result = suppressed_spectrum([2, 10])
        for entry in result:
            assert "ell" in entry
            assert "suppression_factor" in entry
            assert "c_ell_um" in entry
            assert "pct_suppressed" in entry

    def test_c_ell_um_less_than_lcdm(self):
        result = suppressed_spectrum([2, 10, 50], c_ell_lcdm=[1.0, 1.0, 1.0])
        for entry in result:
            assert entry["c_ell_um"] <= entry["c_ell_lcdm"]

    def test_pct_suppressed_positive(self):
        result = suppressed_spectrum([2, 10])
        for entry in result:
            assert entry["pct_suppressed"] >= 0.0

    def test_raises_on_length_mismatch(self):
        with pytest.raises(ValueError):
            suppressed_spectrum([2, 10], c_ell_lcdm=[1.0])

    def test_default_c_ell_is_one(self):
        result = suppressed_spectrum([5])
        expected_s = cmb_power_suppression_factor(5)
        assert abs(result[0]["c_ell_um"] - expected_s) < 1e-12


class TestCompareToPlanck:
    def test_returns_dict(self):
        result = compare_to_planck_observation()
        assert isinstance(result, dict)

    def test_has_um_suppression(self):
        result = compare_to_planck_observation()
        assert "um_suppression_ell2_pct" in result

    def test_um_suppression_positive(self):
        result = compare_to_planck_observation()
        assert result["um_suppression_ell2_pct"] > 0

    def test_has_verdict(self):
        result = compare_to_planck_observation()
        assert "verdict" in result
        assert "DIRECTION_CORRECT" in result["verdict"]

    def test_direction_is_suppression(self):
        # UM should predict LESS power than ΛCDM (suppression, not enhancement)
        result = compare_to_planck_observation()
        # The UM C₂ suppression factor S(2) < 1 → power is reduced
        assert result["um_suppression_ell2_pct"] > 0

    def test_per_ell_dict(self):
        result = compare_to_planck_observation()
        assert "per_ell" in result
        assert 2 in result["per_ell"]
        assert 3 in result["per_ell"]

    def test_per_ell_decreasing(self):
        result = compare_to_planck_observation()
        # Higher ell → more suppression factor → closer to 1
        s2 = result["per_ell"][2]
        s30 = result["per_ell"][30]
        assert s30 > s2


class TestFalsificationCondition:
    def test_returns_dict(self):
        result = falsification_condition()
        assert isinstance(result, dict)

    def test_has_falsification(self):
        result = falsification_condition()
        assert "falsification" in result

    def test_has_detector(self):
        result = falsification_condition()
        assert "detector" in result
        assert "LiteBIRD" in result["detector"]

    def test_has_predictions_for_key_ells(self):
        result = falsification_condition()
        assert "at_ell_2" in result
        assert "at_ell_10" in result
        assert "at_ell_100" in result

    def test_direction_statement(self):
        result = falsification_condition()
        # The falsification says: UM is falsified if MORE power than ΛCDM
        assert "MORE power" in result["falsification"] or "positive" in result["falsification"].lower()


class TestFullReport:
    def test_returns_dict(self):
        r = quadrupole_suppression_report()
        assert isinstance(r, dict)

    def test_pillar_number(self):
        r = quadrupole_suppression_report()
        assert r["pillar"] == 331

    def test_has_mechanism(self):
        r = quadrupole_suppression_report()
        assert "mechanism" in r
        assert "f_braid" in r["mechanism"]
        assert "l_braid" in r["mechanism"]

    def test_has_planck_comparison(self):
        r = quadrupole_suppression_report()
        assert "planck_comparison" in r

    def test_has_spectrum(self):
        r = quadrupole_suppression_report()
        assert "spectrum" in r
        assert len(r["spectrum"]) > 5

    def test_has_honest_assessment(self):
        r = quadrupole_suppression_report()
        assert "honest_assessment" in r
        # Direction is correct (suppression, not enhancement)
        assert "CORRECT" in r["honest_assessment"]["direction"]
        assert "INSUFFICIENT" in r["honest_assessment"]["magnitude"]

    def test_adjacency_label(self):
        r = quadrupole_suppression_report()
        assert "ADJACENT" in r["adjacency"]
