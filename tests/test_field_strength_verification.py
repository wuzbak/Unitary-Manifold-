# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_field_strength_verification.py
==========================================
Tests for src/cold_fusion/field_strength_verification.py.

Verifies all five public functions across normal operation, edge cases,
and error conditions.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import math
import pytest
import numpy as np

from src.cold_fusion.field_strength_verification import (
    kk_reduction_field_strength,
    entropy_rate_cross_check,
    field_strength_scan,
    gamow_from_field_strength,
    field_strength_verification_report,
)
from src.cold_fusion.lattice import phi_at_lattice_site, b_field_at_site


# ===========================================================================
# kk_reduction_field_strength
# ===========================================================================

class TestKKReductionFieldStrength:
    def test_returns_dict_with_required_keys(self):
        result = kk_reduction_field_strength(1.0, 1.0, 0.8)
        assert set(result.keys()) == {
            "B_site_kk", "B_site_lattice", "agreement_atol", "cross_check_passed"
        }

    def test_kk_matches_lattice_formula(self):
        """KK path and lattice.py must give identical B_site."""
        result = kk_reduction_field_strength(1.0, 1.0, 0.8)
        assert result["cross_check_passed"] is True
        assert result["agreement_atol"] < 1e-10

    def test_cross_check_passed_over_range(self):
        for rho in [0.5, 0.6, 0.75, 0.9, 1.0, 1.5]:
            result = kk_reduction_field_strength(2.0, 1.5, rho)
            assert result["cross_check_passed"] is True, f"failed at rho={rho}"

    def test_formula_value_correct(self):
        phi_bulk, rho, rho_ref = 1.0, 0.8, 0.75
        phi_local = phi_at_lattice_site(phi_bulk, rho, rho_ref)
        expected = 1.0 * rho * phi_local
        result = kk_reduction_field_strength(1.0, phi_bulk, rho, rho_ref)
        assert math.isclose(result["B_site_kk"], expected, rel_tol=1e-12)

    def test_zero_B_external_gives_zero(self):
        result = kk_reduction_field_strength(0.0, 1.0, 0.8)
        assert result["B_site_kk"] == 0.0
        assert result["B_site_lattice"] == 0.0
        assert result["cross_check_passed"] is True

    def test_custom_rho_ref(self):
        result = kk_reduction_field_strength(1.0, 1.0, 0.8, rho_ref=1.0)
        assert result["cross_check_passed"] is True

    def test_returns_floats(self):
        result = kk_reduction_field_strength(1.0, 1.0, 0.8)
        assert isinstance(result["B_site_kk"], float)
        assert isinstance(result["B_site_lattice"], float)
        assert isinstance(result["agreement_atol"], float)
        assert isinstance(result["cross_check_passed"], bool)

    # Edge cases / errors
    def test_raises_negative_B_external(self):
        with pytest.raises(ValueError, match="B_external"):
            kk_reduction_field_strength(-0.1, 1.0, 0.8)

    def test_raises_zero_phi_bulk(self):
        with pytest.raises(ValueError, match="phi_bulk"):
            kk_reduction_field_strength(1.0, 0.0, 0.8)

    def test_raises_negative_phi_bulk(self):
        with pytest.raises(ValueError, match="phi_bulk"):
            kk_reduction_field_strength(1.0, -1.0, 0.8)

    def test_raises_zero_rho_loading(self):
        with pytest.raises(ValueError, match="rho_loading"):
            kk_reduction_field_strength(1.0, 1.0, 0.0)

    def test_raises_negative_rho_loading(self):
        with pytest.raises(ValueError, match="rho_loading"):
            kk_reduction_field_strength(1.0, 1.0, -0.5)

    def test_raises_zero_rho_ref(self):
        with pytest.raises(ValueError, match="rho_ref"):
            kk_reduction_field_strength(1.0, 1.0, 0.8, rho_ref=0.0)

    def test_raises_negative_rho_ref(self):
        with pytest.raises(ValueError, match="rho_ref"):
            kk_reduction_field_strength(1.0, 1.0, 0.8, rho_ref=-1.0)

    def test_agreement_atol_is_nonnegative(self):
        result = kk_reduction_field_strength(5.0, 2.0, 1.2)
        assert result["agreement_atol"] >= 0.0

    def test_larger_phi_bulk_scales_correctly(self):
        r1 = kk_reduction_field_strength(1.0, 1.0, 0.8)
        r2 = kk_reduction_field_strength(1.0, 2.0, 0.8)
        # phi_local scales linearly with phi_bulk, so B_kk scales by 2
        assert math.isclose(r2["B_site_kk"] / r1["B_site_kk"], 2.0, rel_tol=1e-10)


# ===========================================================================
# entropy_rate_cross_check
# ===========================================================================

class TestEntropyRateCrossCheck:
    def test_returns_dict_with_required_keys(self):
        result = entropy_rate_cross_check(1.0, 1.0, 1.0)
        assert set(result.keys()) == {
            "entropy_rate", "is_positive", "holographic_check_passed"
        }

    def test_entropy_rate_formula(self):
        B, V, phi = 2.0, 3.0, 1.5
        result = entropy_rate_cross_check(B, V, phi)
        expected = (B ** 2 / phi ** 2) * V
        assert math.isclose(result["entropy_rate"], expected, rel_tol=1e-12)

    def test_is_positive_true_for_positive_inputs(self):
        result = entropy_rate_cross_check(1.0, 1.0, 1.0)
        assert result["is_positive"] is True
        assert result["holographic_check_passed"] is True

    def test_zero_B_site_gives_zero_entropy_rate(self):
        result = entropy_rate_cross_check(0.0, 1.0, 1.0)
        assert result["entropy_rate"] == 0.0
        assert result["is_positive"] is True
        assert result["holographic_check_passed"] is True

    def test_larger_B_site_gives_larger_rate(self):
        r1 = entropy_rate_cross_check(1.0, 1.0, 1.0)
        r2 = entropy_rate_cross_check(2.0, 1.0, 1.0)
        assert r2["entropy_rate"] > r1["entropy_rate"]

    def test_larger_phi_reduces_entropy_rate(self):
        r1 = entropy_rate_cross_check(1.0, 1.0, 1.0)
        r2 = entropy_rate_cross_check(1.0, 1.0, 2.0)
        assert r2["entropy_rate"] < r1["entropy_rate"]

    def test_returns_floats_and_bools(self):
        result = entropy_rate_cross_check(1.0, 1.0, 1.0)
        assert isinstance(result["entropy_rate"], float)
        assert isinstance(result["is_positive"], bool)
        assert isinstance(result["holographic_check_passed"], bool)

    # Errors
    def test_raises_negative_B_site(self):
        with pytest.raises(ValueError, match="B_site"):
            entropy_rate_cross_check(-0.1, 1.0, 1.0)

    def test_raises_zero_V_site(self):
        with pytest.raises(ValueError, match="V_site"):
            entropy_rate_cross_check(1.0, 0.0, 1.0)

    def test_raises_negative_V_site(self):
        with pytest.raises(ValueError, match="V_site"):
            entropy_rate_cross_check(1.0, -1.0, 1.0)

    def test_raises_zero_phi_local(self):
        with pytest.raises(ValueError, match="phi_local"):
            entropy_rate_cross_check(1.0, 1.0, 0.0)

    def test_raises_negative_phi_local(self):
        with pytest.raises(ValueError, match="phi_local"):
            entropy_rate_cross_check(1.0, 1.0, -1.0)

    def test_holographic_check_passed_matches_is_positive(self):
        result = entropy_rate_cross_check(3.0, 2.0, 0.5)
        assert result["holographic_check_passed"] == result["is_positive"]


# ===========================================================================
# field_strength_scan
# ===========================================================================

class TestFieldStrengthScan:
    def test_returns_dict_with_required_keys(self):
        result = field_strength_scan()
        assert set(result.keys()) == {
            "rho_values", "B_kk", "B_lattice", "agreements", "all_consistent"
        }

    def test_default_scan_all_consistent(self):
        result = field_strength_scan()
        assert result["all_consistent"] is True

    def test_list_lengths_match(self):
        rhos = [0.6, 0.7, 0.8, 0.9]
        result = field_strength_scan(rho_values=rhos)
        assert len(result["rho_values"]) == 4
        assert len(result["B_kk"]) == 4
        assert len(result["B_lattice"]) == 4
        assert len(result["agreements"]) == 4

    def test_rho_values_preserved(self):
        rhos = [0.5, 1.0, 1.5]
        result = field_strength_scan(rho_values=rhos)
        assert result["rho_values"] == rhos

    def test_B_increases_with_rho(self):
        rhos = [0.5, 0.7, 0.9, 1.1]
        result = field_strength_scan(rho_values=rhos)
        # B_kk = B_ext · rho · phi_bulk · sqrt(rho/rho_ref) — monotone in rho
        for i in range(len(rhos) - 1):
            assert result["B_kk"][i] < result["B_kk"][i + 1]

    def test_custom_phi_bulk_and_B_external(self):
        result = field_strength_scan(phi_bulk=2.0, B_external=3.0)
        assert result["all_consistent"] is True

    def test_all_agreements_near_zero(self):
        result = field_strength_scan()
        for a in result["agreements"]:
            assert a < 1e-10

    def test_returns_correct_types(self):
        result = field_strength_scan()
        assert isinstance(result["rho_values"], list)
        assert isinstance(result["B_kk"], list)
        assert isinstance(result["B_lattice"], list)
        assert isinstance(result["agreements"], list)
        assert isinstance(result["all_consistent"], bool)

    # Errors
    def test_raises_zero_phi_bulk(self):
        with pytest.raises(ValueError, match="phi_bulk"):
            field_strength_scan(phi_bulk=0.0)

    def test_raises_negative_phi_bulk(self):
        with pytest.raises(ValueError, match="phi_bulk"):
            field_strength_scan(phi_bulk=-1.0)

    def test_raises_negative_B_external(self):
        with pytest.raises(ValueError, match="B_external"):
            field_strength_scan(B_external=-0.5)

    def test_raises_zero_rho_in_list(self):
        with pytest.raises(ValueError, match="rho_values"):
            field_strength_scan(rho_values=[0.5, 0.0, 0.9])

    def test_raises_negative_rho_in_list(self):
        with pytest.raises(ValueError, match="rho_values"):
            field_strength_scan(rho_values=[0.5, -0.1])

    def test_single_rho_value(self):
        result = field_strength_scan(rho_values=[0.8])
        assert len(result["B_kk"]) == 1
        assert result["all_consistent"] is True

    def test_zero_B_external_gives_all_zeros(self):
        result = field_strength_scan(B_external=0.0)
        assert all(b == 0.0 for b in result["B_kk"])
        assert result["all_consistent"] is True


# ===========================================================================
# gamow_from_field_strength
# ===========================================================================

class TestGamowFromFieldStrength:
    def test_returns_dict_with_required_keys(self):
        result = gamow_from_field_strength(1.0, 1.0)
        assert set(result.keys()) == {
            "G_from_field_strength", "G_from_lattice_phi", "consistency_check"
        }

    def test_consistency_check_passes(self):
        result = gamow_from_field_strength(1.0, 1.5)
        assert result["consistency_check"] is True

    def test_gamow_values_equal(self):
        result = gamow_from_field_strength(2.0, 1.0)
        assert result["G_from_field_strength"] == result["G_from_lattice_phi"]

    def test_higher_phi_local_increases_gamow(self):
        r1 = gamow_from_field_strength(1.0, 1.0)
        r2 = gamow_from_field_strength(1.0, 2.0)
        assert r2["G_from_field_strength"] > r1["G_from_field_strength"]

    def test_gamow_in_range_zero_one(self):
        for phi in [0.5, 1.0, 2.0, 5.0]:
            result = gamow_from_field_strength(1.0, phi)
            assert 0.0 <= result["G_from_field_strength"] <= 1.0

    def test_custom_charges_and_v_rel(self):
        result = gamow_from_field_strength(1.0, 1.0, Z1=2.0, Z2=2.0, v_rel=0.01)
        assert result["consistency_check"] is True
        assert 0.0 <= result["G_from_field_strength"] <= 1.0

    def test_returns_correct_types(self):
        result = gamow_from_field_strength(1.0, 1.0)
        assert isinstance(result["G_from_field_strength"], float)
        assert isinstance(result["G_from_lattice_phi"], float)
        assert isinstance(result["consistency_check"], bool)

    def test_zero_B_site_allowed(self):
        result = gamow_from_field_strength(0.0, 1.0)
        assert result["consistency_check"] is True

    # Errors
    def test_raises_negative_B_site(self):
        with pytest.raises(ValueError, match="B_site"):
            gamow_from_field_strength(-0.1, 1.0)

    def test_raises_zero_phi_local(self):
        with pytest.raises(ValueError, match="phi_local"):
            gamow_from_field_strength(1.0, 0.0)

    def test_raises_negative_phi_local(self):
        with pytest.raises(ValueError, match="phi_local"):
            gamow_from_field_strength(1.0, -1.0)

    def test_raises_zero_v_rel(self):
        with pytest.raises(ValueError, match="v_rel"):
            gamow_from_field_strength(1.0, 1.0, v_rel=0.0)

    def test_raises_negative_v_rel(self):
        with pytest.raises(ValueError, match="v_rel"):
            gamow_from_field_strength(1.0, 1.0, v_rel=-0.001)


# ===========================================================================
# field_strength_verification_report
# ===========================================================================

class TestFieldStrengthVerificationReport:
    def test_returns_dict_with_required_keys(self):
        report = field_strength_verification_report()
        assert set(report.keys()) == {
            "status", "paths_checked", "all_consistent",
            "kk_reduction", "scan_result", "entropy_check", "gamow_check",
        }

    def test_status_is_independently_verified(self):
        report = field_strength_verification_report()
        assert report["status"] == "INDEPENDENTLY_VERIFIED"

    def test_all_consistent_true(self):
        report = field_strength_verification_report()
        assert report["all_consistent"] is True

    def test_paths_checked_has_three_entries(self):
        report = field_strength_verification_report()
        assert len(report["paths_checked"]) == 3

    def test_kk_reduction_cross_check_passed(self):
        report = field_strength_verification_report()
        assert report["kk_reduction"]["cross_check_passed"] is True

    def test_scan_result_all_consistent(self):
        report = field_strength_verification_report()
        assert report["scan_result"]["all_consistent"] is True

    def test_entropy_check_holographic_passed(self):
        report = field_strength_verification_report()
        assert report["entropy_check"]["holographic_check_passed"] is True

    def test_gamow_check_consistency(self):
        report = field_strength_verification_report()
        assert report["gamow_check"]["consistency_check"] is True

    def test_paths_checked_is_list_of_strings(self):
        report = field_strength_verification_report()
        assert isinstance(report["paths_checked"], list)
        assert all(isinstance(p, str) for p in report["paths_checked"])

    def test_status_is_string(self):
        report = field_strength_verification_report()
        assert isinstance(report["status"], str)

    def test_all_consistent_is_bool(self):
        report = field_strength_verification_report()
        assert isinstance(report["all_consistent"], bool)
