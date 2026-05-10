# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_precision_audit.py
==============================
Test suite for Pillar 45-B — Numerical Precision Audit
(src/core/precision_audit.py).

~100 tests verifying:
  - Constants (including DPS_512BIT and PRECISION_LANES)
  - se_minimum_at_57_mpmath: (5,7) is the minimum at 64, 128, 256, and 512-bit precision
  - loss_coefficient_stability: exp(-10×L) < 1e-4 for L ≥ 1 at all precision levels
  - se_identity_57: S_E(5,7) = 1/√74 holds at all precision levels
  - lossless_branch_set_stable: {(5,7)} is the minimum across all precision levels
  - full_precision_audit: integrated check passes, optional 512-bit lane
  - precision_stability_256_vs_512: drift between 256-bit and 512-bit lanes
  - four_lane_precision_certificate: consolidated 64/128/256/512 certificate

"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Skip entire module if mpmath not available
mpmath = pytest.importorskip("mpmath", reason="mpmath not installed")

from src.core.precision_audit import (
    DPS_128BIT,
    DPS_256BIT,
    DPS_512BIT,
    DPS_64BIT,
    K_CS_CANONICAL,
    LOSS_COEFFICIENT,
    LOSSY_SUPPRESSION_THRESHOLD,
    N1_CANONICAL,
    N2_CANONICAL,
    N_MAX_DEFAULT,
    PRECISION_LANE_NAMES,
    PRECISION_LANES,
    SE_57_FLOAT,
    four_lane_precision_certificate,
    full_precision_audit,
    lossless_branch_set_stable,
    loss_coefficient_stability,
    precision_stability_256_vs_512,
    se_identity_57,
    se_minimum_at_57_mpmath,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n1_canonical(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical(self):
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_se_57_float_formula(self):
        assert SE_57_FLOAT == pytest.approx(1.0 / math.sqrt(74.0), rel=1e-14)

    def test_loss_coefficient(self):
        assert LOSS_COEFFICIENT == pytest.approx(10.0)

    def test_lossy_threshold(self):
        assert LOSSY_SUPPRESSION_THRESHOLD == pytest.approx(1e-4)

    def test_dps_128bit(self):
        assert DPS_128BIT >= 30  # at least 30 decimal places

    def test_dps_256bit(self):
        assert DPS_256BIT >= 70  # at least 70 decimal places

    def test_dps_512bit(self):
        assert DPS_512BIT >= 150  # at least 150 decimal places

    def test_dps_hierarchy(self):
        assert DPS_64BIT < DPS_128BIT < DPS_256BIT < DPS_512BIT

    def test_precision_lanes_tuple(self):
        assert PRECISION_LANES == (DPS_64BIT, DPS_128BIT, DPS_256BIT, DPS_512BIT)

    def test_precision_lane_names_length(self):
        assert len(PRECISION_LANE_NAMES) == len(PRECISION_LANES)

    def test_precision_lane_names_content(self):
        names_joined = " ".join(PRECISION_LANE_NAMES)
        assert "256" in names_joined
        assert "512" in names_joined


# ---------------------------------------------------------------------------
# se_minimum_at_57_mpmath
# ---------------------------------------------------------------------------

class TestSeMinimumAt57:
    def _check(self, dps):
        return se_minimum_at_57_mpmath(dps=dps, n_max=15)

    def test_returns_dict(self):
        r = self._check(DPS_128BIT)
        assert isinstance(r, dict)

    def test_required_keys(self):
        r = self._check(DPS_128BIT)
        for k in ["dps", "se_57", "se_57_exact", "minimum_pair", "minimum_se",
                  "57_is_minimum", "n_pairs_checked", "max_error_vs_64bit"]:
            assert k in r

    def test_57_is_minimum_at_128bit(self):
        r = se_minimum_at_57_mpmath(dps=DPS_128BIT)
        assert r["57_is_minimum"] is True

    def test_57_is_minimum_at_256bit(self):
        r = se_minimum_at_57_mpmath(dps=DPS_256BIT)
        assert r["57_is_minimum"] is True

    def test_57_is_minimum_at_64bit(self):
        r = se_minimum_at_57_mpmath(dps=DPS_64BIT)
        assert r["57_is_minimum"] is True

    def test_minimum_se_matches_se_57(self):
        r = se_minimum_at_57_mpmath(dps=DPS_128BIT)
        assert r["minimum_se"] == pytest.approx(r["se_57"], rel=1e-12)

    def test_se_57_close_to_reference(self):
        r = se_minimum_at_57_mpmath(dps=DPS_128BIT)
        assert r["se_57"] == pytest.approx(SE_57_FLOAT, rel=1e-12)

    def test_n_pairs_positive(self):
        r = self._check(DPS_128BIT)
        assert r["n_pairs_checked"] > 0

    def test_max_error_tiny(self):
        # Error between mpmath and 64-bit should be < 1e-14 for 128-bit
        r = se_minimum_at_57_mpmath(dps=DPS_128BIT)
        assert r["max_error_vs_64bit"] < 1e-12

    def test_dps_stored(self):
        r = self._check(DPS_128BIT)
        assert r["dps"] == DPS_128BIT

    def test_minimum_pair_is_5_7(self):
        r = se_minimum_at_57_mpmath(dps=DPS_256BIT)
        assert r["minimum_pair"] == (5, 7)


# ---------------------------------------------------------------------------
# loss_coefficient_stability
# ---------------------------------------------------------------------------

class TestLossCoefficientStability:
    def test_returns_dict(self):
        r = loss_coefficient_stability(dps=DPS_128BIT)
        assert isinstance(r, dict)

    def test_required_keys(self):
        r = loss_coefficient_stability(dps=DPS_128BIT)
        for k in ["dps", "loss_coefficient", "threshold", "results", "all_pass"]:
            assert k in r

    def test_all_pass_128bit(self):
        r = loss_coefficient_stability(dps=DPS_128BIT)
        assert r["all_pass"] is True

    def test_all_pass_256bit(self):
        r = loss_coefficient_stability(dps=DPS_256BIT)
        assert r["all_pass"] is True

    def test_L1_amplitude_below_threshold(self):
        r = loss_coefficient_stability(dps=DPS_128BIT, L_values=[1.0])
        assert r["results"][0]["amplitude_mpmath"] < LOSSY_SUPPRESSION_THRESHOLD

    def test_L1_amplitude_known_value(self):
        # exp(-10) ≈ 4.540e-5
        r = loss_coefficient_stability(dps=DPS_256BIT, L_values=[1.0])
        assert r["results"][0]["amplitude_mpmath"] == pytest.approx(
            math.exp(-10.0), rel=1e-10
        )

    def test_amplitudes_decrease_with_L(self):
        r = loss_coefficient_stability(dps=DPS_128BIT, L_values=[1.0, 2.0, 5.0])
        amps = [x["amplitude_mpmath"] for x in r["results"]]
        for i in range(len(amps) - 1):
            assert amps[i] > amps[i + 1]

    def test_mpmath_matches_64bit(self):
        r = loss_coefficient_stability(dps=DPS_128BIT, L_values=[1.0, 2.0])
        for entry in r["results"]:
            assert entry["amplitude_mpmath"] == pytest.approx(
                entry["amplitude_64bit"], rel=1e-12
            )

    def test_loss_coefficient_stored(self):
        r = loss_coefficient_stability(dps=DPS_128BIT)
        assert r["loss_coefficient"] == pytest.approx(LOSS_COEFFICIENT)

    def test_each_result_has_required_keys(self):
        r = loss_coefficient_stability(dps=DPS_128BIT)
        for entry in r["results"]:
            assert "L" in entry
            assert "amplitude_mpmath" in entry
            assert "amplitude_64bit" in entry
            assert "passes" in entry


# ---------------------------------------------------------------------------
# se_identity_57
# ---------------------------------------------------------------------------

class TestSeIdentity57:
    def test_returns_dict(self):
        r = se_identity_57(dps=DPS_128BIT)
        assert isinstance(r, dict)

    def test_required_keys(self):
        r = se_identity_57(dps=DPS_128BIT)
        for k in ["dps", "se_57_mpmath", "one_over_sqrt74_mpmath",
                  "absolute_error", "passes"]:
            assert k in r

    def test_passes_at_128bit(self):
        r = se_identity_57(dps=DPS_128BIT)
        assert r["passes"] is True

    def test_passes_at_256bit(self):
        r = se_identity_57(dps=DPS_256BIT)
        assert r["passes"] is True

    def test_absolute_error_tiny(self):
        r = se_identity_57(dps=DPS_256BIT)
        assert r["absolute_error"] < 1e-70

    def test_se_57_close_to_reference_float(self):
        r = se_identity_57(dps=DPS_128BIT)
        assert r["se_57_mpmath"] == pytest.approx(SE_57_FLOAT, rel=1e-13)

    def test_one_over_sqrt74_close_to_reference(self):
        r = se_identity_57(dps=DPS_128BIT)
        assert r["one_over_sqrt74_mpmath"] == pytest.approx(
            1.0 / math.sqrt(74.0), rel=1e-13
        )


# ---------------------------------------------------------------------------
# lossless_branch_set_stable
# ---------------------------------------------------------------------------

class TestLosslessBranchSetStable:
    def test_returns_dict(self):
        r = lossless_branch_set_stable(dps_list=[DPS_128BIT, DPS_256BIT])
        assert isinstance(r, dict)

    def test_required_keys(self):
        r = lossless_branch_set_stable(dps_list=[DPS_128BIT])
        for k in ["dps_list", "minimum_pairs", "all_consistent", "precision_results"]:
            assert k in r

    def test_all_consistent_true(self):
        r = lossless_branch_set_stable(dps_list=[DPS_64BIT, DPS_128BIT, DPS_256BIT])
        assert r["all_consistent"] is True

    def test_all_minimum_pairs_are_57(self):
        r = lossless_branch_set_stable(dps_list=[DPS_128BIT, DPS_256BIT])
        for pair in r["minimum_pairs"]:
            assert pair == (5, 7)

    def test_length_matches_dps_list(self):
        dps_list = [DPS_64BIT, DPS_128BIT]
        r = lossless_branch_set_stable(dps_list=dps_list)
        assert len(r["minimum_pairs"]) == len(dps_list)
        assert len(r["precision_results"]) == len(dps_list)


# ---------------------------------------------------------------------------
# full_precision_audit
# ---------------------------------------------------------------------------

class TestFullPrecisionAudit:
    def test_returns_dict(self):
        r = full_precision_audit(dps_low=DPS_64BIT, dps_high=DPS_128BIT)
        assert isinstance(r, dict)

    def test_required_keys(self):
        r = full_precision_audit(dps_low=DPS_64BIT, dps_high=DPS_128BIT)
        for k in ["check_1_se_minimum_128bit", "check_2_se_minimum_256bit",
                  "check_3_loss_coefficient", "check_4_se_identity",
                  "check_5_branch_set_stable", "all_pass", "summary"]:
            assert k in r

    def test_all_pass(self):
        r = full_precision_audit(dps_low=DPS_128BIT, dps_high=DPS_256BIT)
        assert r["all_pass"] is True

    def test_summary_is_string(self):
        r = full_precision_audit(dps_low=DPS_64BIT, dps_high=DPS_128BIT)
        assert isinstance(r["summary"], str)

    def test_summary_contains_pass(self):
        r = full_precision_audit(dps_low=DPS_128BIT, dps_high=DPS_256BIT)
        assert "PASS" in r["summary"]

    def test_check_4_se_identity_passes(self):
        r = full_precision_audit(dps_low=DPS_128BIT, dps_high=DPS_256BIT)
        assert r["check_4_se_identity"]["passes"] is True

    def test_check_5_branch_stable(self):
        r = full_precision_audit(dps_low=DPS_128BIT, dps_high=DPS_256BIT)
        assert r["check_5_branch_set_stable"]["all_consistent"] is True

    def test_with_512bit_ultra_lane_all_pass(self):
        r = full_precision_audit(dps_low=DPS_128BIT, dps_high=DPS_256BIT, dps_ultra=DPS_512BIT)
        assert r["all_pass"] is True

    def test_with_512bit_ultra_lane_has_check6(self):
        r = full_precision_audit(dps_low=DPS_128BIT, dps_high=DPS_256BIT, dps_ultra=DPS_512BIT)
        assert "check_6_se_minimum_512bit" in r

    def test_with_512bit_ultra_lane_check6_passes(self):
        r = full_precision_audit(dps_low=DPS_128BIT, dps_high=DPS_256BIT, dps_ultra=DPS_512BIT)
        assert r["check_6_se_minimum_512bit"]["57_is_minimum"] is True

    def test_without_ultra_lane_no_check6(self):
        r = full_precision_audit(dps_low=DPS_128BIT, dps_high=DPS_256BIT)
        assert "check_6_se_minimum_512bit" not in r


# ---------------------------------------------------------------------------
# 512-bit lane: se_minimum_at_57_mpmath at 512-bit
# ---------------------------------------------------------------------------

class TestSeMinimumAt512Bit:
    def test_57_is_minimum_at_512bit(self):
        r = se_minimum_at_57_mpmath(dps=DPS_512BIT)
        assert r["57_is_minimum"] is True

    def test_minimum_pair_is_5_7_at_512bit(self):
        r = se_minimum_at_57_mpmath(dps=DPS_512BIT)
        assert r["minimum_pair"] == (5, 7)

    def test_se_57_close_to_reference_at_512bit(self):
        r = se_minimum_at_57_mpmath(dps=DPS_512BIT)
        assert r["se_57"] == pytest.approx(SE_57_FLOAT, rel=1e-12)

    def test_max_error_tiny_at_512bit(self):
        r = se_minimum_at_57_mpmath(dps=DPS_512BIT)
        assert r["max_error_vs_64bit"] < 1e-12


# ---------------------------------------------------------------------------
# 512-bit lane: loss_coefficient_stability at 512-bit
# ---------------------------------------------------------------------------

class TestLossCoefficientStability512Bit:
    def test_all_pass_at_512bit(self):
        r = loss_coefficient_stability(dps=DPS_512BIT)
        assert r["all_pass"] is True

    def test_L1_amplitude_below_threshold_at_512bit(self):
        r = loss_coefficient_stability(dps=DPS_512BIT, L_values=[1.0])
        assert r["results"][0]["amplitude_mpmath"] < LOSSY_SUPPRESSION_THRESHOLD

    def test_mpmath_matches_64bit_at_512bit(self):
        r = loss_coefficient_stability(dps=DPS_512BIT, L_values=[1.0, 2.0])
        for entry in r["results"]:
            assert entry["amplitude_mpmath"] == pytest.approx(
                entry["amplitude_64bit"], rel=1e-12
            )


# ---------------------------------------------------------------------------
# 512-bit lane: se_identity_57 at 512-bit
# ---------------------------------------------------------------------------

class TestSeIdentity57At512Bit:
    def test_passes_at_512bit(self):
        r = se_identity_57(dps=DPS_512BIT)
        assert r["passes"] is True

    def test_absolute_error_tiny_at_512bit(self):
        r = se_identity_57(dps=DPS_512BIT)
        assert r["absolute_error"] < 1e-140  # well within 512-bit tolerance

    def test_se_57_close_to_reference_at_512bit(self):
        r = se_identity_57(dps=DPS_512BIT)
        assert r["se_57_mpmath"] == pytest.approx(SE_57_FLOAT, rel=1e-13)


# ---------------------------------------------------------------------------
# lossless_branch_set_stable (all four lanes)
# ---------------------------------------------------------------------------

class TestLosslessBranchSetStableAllLanes:
    def test_all_consistent_four_lanes(self):
        r = lossless_branch_set_stable(
            dps_list=[DPS_64BIT, DPS_128BIT, DPS_256BIT, DPS_512BIT]
        )
        assert r["all_consistent"] is True

    def test_all_minimum_pairs_are_57_four_lanes(self):
        r = lossless_branch_set_stable(
            dps_list=[DPS_64BIT, DPS_128BIT, DPS_256BIT, DPS_512BIT]
        )
        for pair in r["minimum_pairs"]:
            assert pair == (5, 7)

    def test_default_dps_list_includes_512bit(self):
        r = lossless_branch_set_stable()
        assert DPS_512BIT in r["dps_list"]

    def test_default_dps_list_length_is_four(self):
        r = lossless_branch_set_stable()
        assert len(r["dps_list"]) == 4


# ---------------------------------------------------------------------------
# precision_stability_256_vs_512
# ---------------------------------------------------------------------------

class TestPrecisionStability256Vs512:
    def _run(self, n_max=15):
        return precision_stability_256_vs_512(n_max=n_max)

    def test_returns_dict(self):
        assert isinstance(self._run(), dict)

    def test_required_keys(self):
        r = self._run()
        for k in [
            "dps_256", "dps_512", "minimum_pair_256", "minimum_pair_512",
            "minimum_pair_stable", "max_drift", "lossless_set_stable",
            "precision_stable", "verdict",
        ]:
            assert k in r

    def test_dps_values_correct(self):
        r = self._run()
        assert r["dps_256"] == DPS_256BIT
        assert r["dps_512"] == DPS_512BIT

    def test_minimum_pair_stable_true(self):
        r = self._run()
        assert r["minimum_pair_stable"] is True

    def test_lossless_set_stable_true(self):
        r = self._run()
        assert r["lossless_set_stable"] is True

    def test_precision_stable_true(self):
        r = self._run()
        assert r["precision_stable"] is True

    def test_minimum_pair_256_is_5_7(self):
        r = self._run()
        assert r["minimum_pair_256"] == (5, 7)

    def test_minimum_pair_512_is_5_7(self):
        r = self._run()
        assert r["minimum_pair_512"] == (5, 7)

    def test_max_drift_tiny(self):
        r = self._run()
        assert r["max_drift"] < 1e-70  # should be essentially machine zero

    def test_verdict_mentions_stable(self):
        r = self._run()
        assert "STABLE" in r["verdict"].upper()

    def test_verdict_is_string(self):
        r = self._run()
        assert isinstance(r["verdict"], str)
        assert len(r["verdict"]) > 20


# ---------------------------------------------------------------------------
# four_lane_precision_certificate
# ---------------------------------------------------------------------------

class TestFourLanePrecisionCertificate:
    def _run(self, n_max=15):
        return four_lane_precision_certificate(n_max=n_max)

    def test_returns_dict(self):
        assert isinstance(self._run(), dict)

    def test_required_keys(self):
        r = self._run()
        for k in [
            "lanes", "lane_names", "overall_pass", "precision_stable",
            "stability_256_vs_512", "branch_set_stable",
            "hardgate_256_status", "ultra_512_status", "certificate_summary",
        ]:
            assert k in r

    def test_four_lanes_present(self):
        r = self._run()
        assert len(r["lanes"]) == 4

    def test_all_lanes_have_required_keys(self):
        r = self._run()
        for lane in r["lanes"]:
            for k in [
                "lane_name", "dps", "se_minimum_57_is_min", "se_minimum_pair",
                "loss_coeff_all_pass", "identity_passes", "identity_absolute_error",
                "lane_pass",
            ]:
                assert k in lane, f"Key {k!r} missing from lane {lane.get('lane_name')}"

    def test_overall_pass_true(self):
        r = self._run()
        assert r["overall_pass"] is True

    def test_precision_stable_true(self):
        r = self._run()
        assert r["precision_stable"] is True

    def test_hardgate_256_pass(self):
        r = self._run()
        assert r["hardgate_256_status"] == "PASS"

    def test_ultra_512_pass(self):
        r = self._run()
        assert r["ultra_512_status"] == "PASS"

    def test_all_individual_lanes_pass(self):
        r = self._run()
        for lane in r["lanes"]:
            assert lane["lane_pass"] is True, (
                f"Lane {lane['lane_name']} failed"
            )

    def test_all_lanes_57_is_minimum(self):
        r = self._run()
        for lane in r["lanes"]:
            assert lane["se_minimum_57_is_min"] is True

    def test_all_lanes_loss_coeff_pass(self):
        r = self._run()
        for lane in r["lanes"]:
            assert lane["loss_coeff_all_pass"] is True

    def test_all_lanes_identity_passes(self):
        r = self._run()
        for lane in r["lanes"]:
            assert lane["identity_passes"] is True

    def test_identity_error_decreases_with_precision(self):
        r = self._run()
        errors = [l["identity_absolute_error"] for l in r["lanes"]]
        # Higher precision lanes should have smaller errors
        assert errors[2] <= errors[1] or errors[2] < 1e-70  # 256-bit tighter than 128-bit
        assert errors[3] <= errors[2] or errors[3] < 1e-140  # 512-bit tighter than 256-bit

    def test_certificate_summary_is_string(self):
        r = self._run()
        assert isinstance(r["certificate_summary"], str)
        assert len(r["certificate_summary"]) > 50

    def test_certificate_summary_contains_pass_verdict(self):
        r = self._run()
        assert "PASS" in r["certificate_summary"]

    def test_certificate_summary_mentions_256_and_512(self):
        r = self._run()
        summary = r["certificate_summary"]
        assert "256" in summary
        assert "512" in summary

    def test_lane_names_count(self):
        r = self._run()
        assert len(r["lane_names"]) == 4

    def test_stability_256_vs_512_embedded(self):
        r = self._run()
        stab = r["stability_256_vs_512"]
        assert stab["precision_stable"] is True
        assert stab["minimum_pair_512"] == (5, 7)

