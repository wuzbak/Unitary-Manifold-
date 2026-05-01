# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_precision_audit.py
==============================
Test suite for Pillar 45-B — Numerical Precision Audit
(src/core/precision_audit.py).

~60 tests verifying:
  - Constants
  - se_minimum_at_57_mpmath: (5,7) is the minimum at 64, 128, and 256-bit precision
  - loss_coefficient_stability: exp(-10×L) < 1e-4 for L ≥ 1 at high precision
  - se_identity_57: S_E(5,7) = 1/√74 holds to many significant figures
  - lossless_branch_set_stable: {(5,7)} is the minimum across all precision levels
  - full_precision_audit: integrated check passes

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
    DPS_64BIT,
    K_CS_CANONICAL,
    LOSS_COEFFICIENT,
    LOSSY_SUPPRESSION_THRESHOLD,
    N1_CANONICAL,
    N2_CANONICAL,
    N_MAX_DEFAULT,
    SE_57_FLOAT,
    full_precision_audit,
    lossless_branch_set_stable,
    loss_coefficient_stability,
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

    def test_dps_hierarchy(self):
        assert DPS_64BIT < DPS_128BIT < DPS_256BIT


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
