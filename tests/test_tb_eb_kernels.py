# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_tb_eb_kernels.py
============================
Test suite for Pillar 119 — TB/EB Correlation Kernels (src/core/tb_eb_kernels.py).

~50 tests organised in 6 classes covering all six public API functions.
"""

from __future__ import annotations

import math

import pytest

from src.core.tb_eb_kernels import (
    C_L_REF,
    LITEBIRD_NOISE,
    R_BRAIDED,
    TWIST_ANGLE_E2_DEG,
    TWIST_ANGLE_E3_DEG,
    correlation_summary,
    distinguish_from_inflation,
    inflation_bmode_tb_kernel,
    litebird_detectability,
    topology_eb_kernel,
    topology_tb_kernel,
)


class TestTopologyTbKernel:
    """10 tests for topology_tb_kernel."""

    def test_zero_twist_returns_zero(self):
        assert topology_tb_kernel(2, 0.0) == 0.0

    def test_zero_twist_any_ell_returns_zero(self):
        for ell in [1, 10, 100]:
            assert topology_tb_kernel(ell, 0.0) == 0.0

    def test_e2_twist_ell2_positive(self):
        assert topology_tb_kernel(2, TWIST_ANGLE_E2_DEG) > 0.0

    def test_e3_twist_ell2_positive(self):
        assert topology_tb_kernel(2, TWIST_ANGLE_E3_DEG) > 0.0

    def test_returns_float(self):
        result = topology_tb_kernel(5, 90.0)
        assert isinstance(result, float)

    def test_value_error_ell_zero(self):
        with pytest.raises(ValueError):
            topology_tb_kernel(0, 90.0)

    def test_value_error_ell_negative(self):
        with pytest.raises(ValueError):
            topology_tb_kernel(-1, 90.0)

    def test_decreasing_with_ell_for_e2(self):
        # For E2 (180°), cos(180°) = -1 → exp factor = exp(-ell*2/10), strongly decreasing
        k1 = topology_tb_kernel(1, TWIST_ANGLE_E2_DEG)
        k100 = topology_tb_kernel(100, TWIST_ANGLE_E2_DEG)
        assert k1 >= k100

    def test_e2_and_e3_both_positive(self):
        assert topology_tb_kernel(5, TWIST_ANGLE_E2_DEG) > 0.0
        assert topology_tb_kernel(5, TWIST_ANGLE_E3_DEG) > 0.0

    def test_kernel_positive_for_small_twist(self):
        assert topology_tb_kernel(10, 45.0) > 0.0


class TestTopologyEbKernel:
    """8 tests for topology_eb_kernel."""

    def test_zero_twist_returns_zero(self):
        assert topology_eb_kernel(2, 0.0) == 0.0

    def test_e2_twist_positive(self):
        assert topology_eb_kernel(2, TWIST_ANGLE_E2_DEG) > 0.0

    def test_e3_twist_positive(self):
        assert topology_eb_kernel(2, TWIST_ANGLE_E3_DEG) > 0.0

    def test_returns_float(self):
        result = topology_eb_kernel(5, 90.0)
        assert isinstance(result, float)

    def test_value_error_ell_zero(self):
        with pytest.raises(ValueError):
            topology_eb_kernel(0, 90.0)

    def test_value_error_ell_negative(self):
        with pytest.raises(ValueError):
            topology_eb_kernel(-5, 90.0)

    def test_kernel_positive_for_twist(self):
        assert topology_eb_kernel(10, 45.0) > 0.0

    def test_monotonically_decreasing_with_ell(self):
        # exp(-ell/20) is strictly decreasing; sin² factor is constant w.r.t. ell
        twist = TWIST_ANGLE_E2_DEG
        vals = [topology_eb_kernel(ell, twist) for ell in [1, 5, 20, 80]]
        assert all(vals[i] > vals[i + 1] for i in range(len(vals) - 1))


class TestInflationBmodeTbKernel:
    """8 tests for inflation_bmode_tb_kernel."""

    def test_returns_float(self):
        result = inflation_bmode_tb_kernel(5, 0.03)
        assert isinstance(result, float)

    def test_r_zero_returns_zero(self):
        assert inflation_bmode_tb_kernel(2, 0.0) == 0.0

    def test_r_positive_returns_positive(self):
        assert inflation_bmode_tb_kernel(10, 0.05) > 0.0

    def test_value_error_ell_zero(self):
        with pytest.raises(ValueError):
            inflation_bmode_tb_kernel(0, 0.03)

    def test_value_error_ell_negative(self):
        with pytest.raises(ValueError):
            inflation_bmode_tb_kernel(-2, 0.03)

    def test_value_error_r_negative(self):
        with pytest.raises(ValueError):
            inflation_bmode_tb_kernel(10, -0.01)

    def test_r_braided_value_less_than_c_l_ref(self):
        # r = 0.0315 < 1, so C_L_REF * r * exp(-...) < C_L_REF
        val = inflation_bmode_tb_kernel(10, R_BRAIDED)
        assert val < C_L_REF

    def test_peaks_at_low_ell(self):
        # Gaussian peaks at ℓ → 0; value at ℓ=1 > value at ℓ=200
        v_low = inflation_bmode_tb_kernel(1, R_BRAIDED)
        v_high = inflation_bmode_tb_kernel(200, R_BRAIDED)
        assert v_low > v_high


class TestDistinguishFromInflation:
    """10 tests for distinguish_from_inflation."""

    def test_returns_dict(self):
        result = distinguish_from_inflation(10)
        assert isinstance(result, dict)

    def test_has_ell_key(self):
        result = distinguish_from_inflation(10)
        assert "ell" in result

    def test_has_all_required_keys(self):
        required = {
            "ell", "topology_tb", "inflation_tb", "ratio",
            "distinguishable", "l_dependence_topology", "l_dependence_inflation",
        }
        result = distinguish_from_inflation(10)
        assert required.issubset(result.keys())

    def test_distinguishable_is_true(self):
        result = distinguish_from_inflation(2)
        assert result["distinguishable"] is True

    def test_ratio_not_one_for_e2(self):
        result = distinguish_from_inflation(10)
        assert result["ratio"] != 1.0

    def test_ratio_is_float(self):
        result = distinguish_from_inflation(10)
        assert isinstance(result["ratio"], float)

    def test_topology_tb_positive(self):
        # E2 (180°) with non-zero twist → topology_tb > 0
        result = distinguish_from_inflation(10)
        assert result["topology_tb"] > 0.0

    def test_inflation_tb_positive_for_r_braided(self):
        result = distinguish_from_inflation(10)
        assert result["inflation_tb"] > 0.0

    def test_ell2_result(self):
        result = distinguish_from_inflation(2)
        assert result["ell"] == 2
        assert result["topology_tb"] > 0.0

    def test_ell50_result(self):
        result = distinguish_from_inflation(50)
        assert result["ell"] == 50
        assert isinstance(result["ratio"], float)


class TestCorrelationSummary:
    """8 tests for correlation_summary."""

    def test_returns_dict_e2(self):
        result = correlation_summary("E2")
        assert isinstance(result, dict)

    def test_returns_dict_e3(self):
        result = correlation_summary("E3")
        assert isinstance(result, dict)

    def test_has_all_required_keys(self):
        required = {
            "topology", "twist_angle_deg", "tb_kernels", "eb_kernels",
            "tb_nonzero", "eb_nonzero", "parity_violation", "distinguishable_from_lcdm",
        }
        for topo in ("E2", "E3"):
            result = correlation_summary(topo)
            assert required.issubset(result.keys())

    def test_tb_nonzero_true(self):
        for topo in ("E2", "E3"):
            assert correlation_summary(topo)["tb_nonzero"] is True

    def test_eb_nonzero_true(self):
        for topo in ("E2", "E3"):
            assert correlation_summary(topo)["eb_nonzero"] is True

    def test_parity_violation_true(self):
        for topo in ("E2", "E3"):
            assert correlation_summary(topo)["parity_violation"] is True

    def test_distinguishable_from_lcdm_true(self):
        for topo in ("E2", "E3"):
            assert correlation_summary(topo)["distinguishable_from_lcdm"] is True

    def test_value_error_unknown_topology(self):
        with pytest.raises(ValueError):
            correlation_summary("E99")

    def test_tb_kernels_has_four_entries(self):
        result = correlation_summary("E2")
        assert len(result["tb_kernels"]) == 4

    def test_eb_kernels_is_dict(self):
        result = correlation_summary("E3")
        assert isinstance(result["eb_kernels"], dict)


class TestLitebirdDetectability:
    """6 tests for litebird_detectability."""

    def test_returns_dict_e2(self):
        result = litebird_detectability("E2")
        assert isinstance(result, dict)

    def test_returns_dict_e3(self):
        result = litebird_detectability("E3")
        assert isinstance(result, dict)

    def test_has_all_required_keys(self):
        required = {
            "topology", "snr_tb", "snr_eb", "detectable_tb",
            "detectable_eb", "instrument", "reference",
        }
        for topo in ("E2", "E3"):
            result = litebird_detectability(topo)
            assert required.issubset(result.keys())

    def test_instrument_is_litebird(self):
        assert litebird_detectability("E2")["instrument"] == "LiteBIRD"
        assert litebird_detectability("E3")["instrument"] == "LiteBIRD"

    def test_snr_tb_positive(self):
        for topo in ("E2", "E3"):
            assert litebird_detectability(topo)["snr_tb"] > 0.0

    def test_snr_eb_positive(self):
        for topo in ("E2", "E3"):
            assert litebird_detectability(topo)["snr_eb"] > 0.0

    def test_value_error_unknown_topology(self):
        with pytest.raises(ValueError):
            litebird_detectability("E1")

    def test_reference_field_present(self):
        result = litebird_detectability("E2")
        assert "reference" in result
        assert isinstance(result["reference"], str)
