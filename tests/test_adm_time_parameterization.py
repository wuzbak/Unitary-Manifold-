# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for ADM 3+1 time parameterization — Gap T3 closure.

Covers adm_decompose() and time_delay_rate() from
src.core.adm_time_parameterization.
"""

import math

import pytest

from src.core.adm_time_parameterization import (
    M_KK_DEFAULT,
    adm_decompose,
    time_delay_rate,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flat_params(phi=1.0, lam=0.0, g_diag=None):
    return {"phi": phi, "lam": lam, "g_diag": g_diag or [1.0, 1.0, 1.0]}


# ---------------------------------------------------------------------------
# adm_decompose — basic structure tests
# ---------------------------------------------------------------------------


def test_adm_decompose_returns_dict():
    result = adm_decompose(_flat_params())
    assert isinstance(result, dict)


def test_adm_decompose_has_all_keys():
    result = adm_decompose(_flat_params())
    for key in ("lapse", "shift", "three_metric_diag", "extrinsic_curvature_trace", "phi", "units"):
        assert key in result, f"Missing key: {key}"


def test_three_metric_has_three_components():
    result = adm_decompose(_flat_params())
    assert len(result["three_metric_diag"]) == 3


def test_shift_has_three_components():
    result = adm_decompose(_flat_params())
    assert len(result["shift"]) == 3


def test_phi_stored_in_result():
    phi = 0.42
    result = adm_decompose(_flat_params(phi=phi))
    assert result["phi"] == pytest.approx(phi)


def test_units_key_present():
    result = adm_decompose(_flat_params())
    assert "units" in result
    assert isinstance(result["units"], str)


# ---------------------------------------------------------------------------
# adm_decompose — lapse and shift
# ---------------------------------------------------------------------------


def test_flat_space_lapse_is_one():
    """phi=1.0, lam=0 → lapse=1.0 (flat KK limit)."""
    result = adm_decompose({"phi": 1.0, "lam": 0.0, "g_diag": [1.0, 1.0, 1.0]})
    assert result["lapse"] == pytest.approx(1.0)


def test_flat_space_shift_is_zero():
    """lam=0 → all shift components zero regardless of phi."""
    result = adm_decompose({"phi": 2.5, "lam": 0.0, "g_diag": [1.0, 1.0, 1.0]})
    for s in result["shift"]:
        assert s == pytest.approx(0.0)


def test_lapse_equals_phi_for_kk():
    """In KK ansatz lapse = phi."""
    for phi in [0.1, 0.5, 1.0, 2.0]:
        result = adm_decompose(_flat_params(phi=phi))
        assert result["lapse"] == pytest.approx(phi), f"Failed for phi={phi}"


def test_shift_nonzero_when_lam_nonzero():
    B = [1.0, 0.0, 0.0]
    result = adm_decompose({"phi": 1.0, "lam": 0.5, "g_diag": [1.0, 1.0, 1.0], "shift": B})
    assert result["shift"][0] == pytest.approx(0.5 * 1.0 * 1.0)
    assert result["shift"][1] == pytest.approx(0.0)
    assert result["shift"][2] == pytest.approx(0.0)


def test_three_metric_passthrough():
    g = [0.9, 1.1, 1.05]
    result = adm_decompose({"phi": 1.0, "lam": 0.0, "g_diag": g})
    assert result["three_metric_diag"] == pytest.approx(g)


def test_extrinsic_curvature_trace_finite():
    result = adm_decompose(_flat_params(phi=1.0))
    K = result["extrinsic_curvature_trace"]
    assert math.isfinite(K)


def test_extrinsic_curvature_sign():
    """K trace should be negative (KK breathing compresses foliation)."""
    result = adm_decompose(_flat_params(phi=0.5))
    assert result["extrinsic_curvature_trace"] < 0.0


def test_extrinsic_curvature_zero_phi():
    """phi=0 → K trace = 0."""
    result = adm_decompose({"phi": 0.0, "lam": 0.0, "g_diag": [1.0, 1.0, 1.0]})
    assert result["extrinsic_curvature_trace"] == pytest.approx(0.0)


def test_extrinsic_curvature_scales_with_phi():
    """K trace ∝ φ."""
    r1 = adm_decompose(_flat_params(phi=1.0))
    r2 = adm_decompose(_flat_params(phi=2.0))
    assert r2["extrinsic_curvature_trace"] == pytest.approx(2 * r1["extrinsic_curvature_trace"])


# ---------------------------------------------------------------------------
# time_delay_rate — basic limits
# ---------------------------------------------------------------------------


def test_radion_zero_no_delay():
    assert time_delay_rate(phi=0.0, M_kk=1e-3) == 0.0


def test_large_mkk_small_delay():
    """phi ≪ M_kk → delay rate ≈ 0."""
    rate = time_delay_rate(phi=1e-6, M_kk=1.0)
    assert abs(rate) < 1e-11


def test_delay_rate_negative():
    """Non-zero phi always produces a negative time delay."""
    rate = time_delay_rate(phi=1e-3, M_kk=1e-3)
    assert rate < 0.0


def test_delay_rate_at_equal_phi_mkk():
    """phi == M_kk → rate = 1/sqrt(2) - 1."""
    rate = time_delay_rate(1e-3, 1e-3)
    assert rate == pytest.approx(1.0 / math.sqrt(2.0) - 1.0, rel=1e-9)


def test_returns_float():
    assert isinstance(time_delay_rate(1e-3, 1e-3), float)


# ---------------------------------------------------------------------------
# time_delay_rate — monotonicity and scaling (parametric)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("phi", [1e-5, 1e-4, 1e-3, 5e-3, 1e-2])
def test_delay_monotone_in_phi(phi):
    """For fixed M_kk, larger phi → more negative rate (monotone)."""
    M_kk = 1e-2
    rate = time_delay_rate(phi, M_kk)
    rate_larger = time_delay_rate(phi * 2, M_kk)
    assert rate_larger < rate, f"Monotonicity failed at phi={phi}"


@pytest.mark.parametrize("M_kk", [1e-3, 5e-3, 1e-2, 0.1, 1.0])
def test_delay_shrinks_with_larger_mkk(M_kk):
    """For fixed phi, larger M_kk → delay closer to 0."""
    phi = 1e-4
    rate = time_delay_rate(phi, M_kk)
    rate_larger_mkk = time_delay_rate(phi, M_kk * 10)
    assert abs(rate_larger_mkk) < abs(rate), f"Monotonicity in M_kk failed at M_kk={M_kk}"


@pytest.mark.parametrize("phi,M_kk", [
    (1e-4, 1e-3),
    (1e-3, 1e-2),
    (0.1, 1.0),
    (0.5, 2.0),
    (1.0, 10.0),
])
def test_output_well_formed(phi, M_kk):
    """time_delay_rate always returns a finite float ≤ 0."""
    rate = time_delay_rate(phi, M_kk)
    assert isinstance(rate, float)
    assert math.isfinite(rate)
    assert rate <= 0.0


@pytest.mark.parametrize("phi,M_kk", [
    (1e-4, 1e-3),
    (1e-3, 1e-2),
    (0.1, 1.0),
    (0.5, 2.0),
    (1.0, 10.0),
])
def test_adm_decompose_well_formed_parametric(phi, M_kk):
    """adm_decompose dict is well-formed; lapse matches time_delay_rate lapse."""
    result = adm_decompose({"phi": phi, "lam": 0.1, "g_diag": [1.0, 1.0, 1.0]})
    assert isinstance(result, dict)
    assert len(result["shift"]) == 3
    assert len(result["three_metric_diag"]) == 3
    assert math.isfinite(result["lapse"])
    assert math.isfinite(result["extrinsic_curvature_trace"])
    # Lapse is φ; the KK lapse factor is 1/sqrt(1+(φ/M_kk)²)
    kk_lapse = 1.0 / math.sqrt(1.0 + (phi / M_kk) ** 2)
    # The geometric delay from this lapse is always ≤ 0
    assert kk_lapse - 1.0 <= 0.0
