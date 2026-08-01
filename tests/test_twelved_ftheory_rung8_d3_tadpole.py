from __future__ import annotations

import pytest

from src.twelved.ftheory_rung8_d3_tadpole import (
    CY4_CHI,
    EPISTEMIC_STATUS,
    K_CS,
    N_D3,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    TADPOLE_RATIO,
    VERSION,
    braid_tadpole_consistency,
    g4_flux_bound,
    kill_switch_check,
    pillar_report,
    tadpole_cancellation_check,
)


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("PILLAR_NUMBER", PILLAR_NUMBER),
        ("PILLAR_STATUS", PILLAR_STATUS),
        ("EPISTEMIC_STATUS", EPISTEMIC_STATUS),
        ("VERSION", VERSION),
        ("CY4_CHI", CY4_CHI),
        ("N_D3", N_D3),
        ("K_CS", K_CS),
        ("TADPOLE_RATIO", TADPOLE_RATIO),
    ],
)
def test_constants_are_present(label, value):
    assert value is not None, label


def test_constant_values_are_exact():
    assert PILLAR_NUMBER == 578
    assert PILLAR_STATUS == "FTHEORY_RUNG8_D3_TADPOLE_CHARGE_CANCELLATION_ADJACENT"
    assert EPISTEMIC_STATUS == "ADJACENT_TRACK"
    assert VERSION == "v20.1"
    assert CY4_CHI == 1_820_160
    assert N_D3 == 75_840
    assert K_CS == 74
    assert TADPOLE_RATIO == pytest.approx(74.0 / 24.0)


@pytest.mark.parametrize(
    "key",
    [
        "check",
        "chi_over_24",
        "n_d3",
        "n_flux_units",
        "n_flux_proxy",
        "lhs",
        "residual",
        "exact_reference_identity",
        "pass",
        "honest_status",
    ],
)
def test_tadpole_cancellation_keys(key):
    result = tadpole_cancellation_check()
    assert key in result


def test_tadpole_cancellation_reference_identity():
    result = tadpole_cancellation_check()
    assert result["chi_over_24"] == pytest.approx(75_840.0)
    assert result["n_d3"] == 75_840
    assert result["n_flux_units"] == 0
    assert result["n_flux_proxy"] == pytest.approx(0.0)
    assert result["lhs"] == pytest.approx(75_840.0)
    assert result["residual"] == pytest.approx(0.0)
    assert result["exact_reference_identity"] is True
    assert result["pass"] is True


@pytest.mark.parametrize("n_flux_units", [1, 2, 10, 100])
def test_tadpole_cancellation_detects_positive_flux_residual(n_flux_units):
    result = tadpole_cancellation_check(n_flux_units=n_flux_units)
    assert result["n_flux_proxy"] == pytest.approx((n_flux_units**2) / 2.0)
    assert result["residual"] < 0.0
    assert result["pass"] is False


@pytest.mark.parametrize("kwargs", [{"n_d3": -1}, {"n_flux_units": -1}])
def test_tadpole_cancellation_rejects_negative_inputs(kwargs):
    with pytest.raises(ValueError):
        tadpole_cancellation_check(**kwargs)


@pytest.mark.parametrize(
    "key",
    [
        "check",
        "k_cs_times_nd3_over_chi",
        "expected_ratio",
        "ratio_equals_37_over_12",
        "pass",
        "honest_status",
    ],
)
def test_braid_tadpole_consistency_keys(key):
    result = braid_tadpole_consistency()
    assert key in result


def test_braid_tadpole_consistency_values():
    result = braid_tadpole_consistency()
    assert result["k_cs_times_nd3_over_chi"] == pytest.approx(37.0 / 12.0)
    assert result["expected_ratio"] == pytest.approx(74.0 / 24.0)
    assert result["ratio_equals_37_over_12"] is True
    assert result["pass"] is True
    assert "not derive k_CS" in result["honest_status"]


@pytest.mark.parametrize("n_flux_units", [0, 1, 10, 389])
def test_g4_flux_bound_allowed_cases(n_flux_units):
    result = g4_flux_bound(n_flux_units=n_flux_units)
    assert result["allowed"] is True
    assert result["pass"] is True
    assert result["remaining_capacity_for_d3"] >= 0.0


def test_g4_flux_bound_exact_reference_case():
    result = g4_flux_bound()
    assert result["n_flux_proxy"] == pytest.approx(0.0)
    assert result["tadpole_capacity"] == pytest.approx(75_840.0)
    assert result["max_flux_units_proxy"] == 389


def test_g4_flux_bound_overflow_case():
    result = g4_flux_bound(390)
    assert result["n_flux_proxy"] == pytest.approx((390**2) / 2.0)
    assert result["remaining_capacity_for_d3"] < 0.0
    assert result["allowed"] is False
    assert result["pass"] is False


def test_g4_flux_bound_rejects_negative_input():
    with pytest.raises(ValueError):
        g4_flux_bound(-1)


def test_kill_switch_passes():
    assert kill_switch_check() is True


@pytest.mark.parametrize(
    "key",
    [
        "pillar",
        "title",
        "status",
        "version",
        "epistemic_status",
        "constants",
        "tadpole_cancellation",
        "braid_tadpole_consistency",
        "g4_flux_bound",
        "kill_switch_pass",
    ],
)
def test_pillar_report_keys(key):
    report = pillar_report()
    assert key in report


def test_pillar_report_values():
    report = pillar_report()
    assert report["constants"]["cy4_chi"] == CY4_CHI
    assert report["constants"]["n_d3"] == N_D3
    assert report["tadpole_cancellation"]["exact_reference_identity"] is True
    assert report["braid_tadpole_consistency"]["pass"] is True
    assert report["kill_switch_pass"] is True
