# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 289 — IceCube/KM3NeT Neutrino Preregistration."""
import math
import pytest
from src.core.pillar289_icecube_km3net_neutrino_preregistration import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    MAJORANA_MIXING_ANGLE,
    UM_FLAVOR_NU_E,
    UM_FLAVOR_NU_MU,
    UM_FLAVOR_NU_TAU,
    ICECUBE_SIGMA,
    separation_guard,
    um_flavor_ratio_prediction,
    kk_oscillation_phase_correction,
    majorana_mixing_angle,
    icecube_hese_comparison,
    km3net_projection,
    neutrino_preregistration_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 289


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard_keys():
    g = separation_guard()
    assert g["pillar"] == 289
    assert g["is_hardgate"] is False
    assert g["experiments"] == ["IceCube_HESE", "KM3NeT"]


def test_flavor_fractions_democratic():
    assert abs(UM_FLAVOR_NU_E - 1/3) < 1e-10
    assert abs(UM_FLAVOR_NU_MU - 1/3) < 1e-10
    assert abs(UM_FLAVOR_NU_TAU - 1/3) < 1e-10


def test_um_flavor_ratio_prediction_sum():
    p = um_flavor_ratio_prediction()
    assert abs(p["sum_check"] - 1.0) < 1e-10


def test_um_flavor_ratio_normalized():
    p = um_flavor_ratio_prediction()
    assert p["is_normalized"] is True


def test_um_flavor_ratio_fractions_positive():
    p = um_flavor_ratio_prediction()
    assert p["nu_e_fraction"] > 0
    assert p["nu_mu_fraction"] > 0
    assert p["nu_tau_fraction"] > 0


def test_kk_phase_correction_positive():
    c = kk_oscillation_phase_correction(1.0, 100.0)
    assert c > 0.0


def test_kk_phase_correction_finite():
    c = kk_oscillation_phase_correction(1.0, 100.0)
    assert math.isfinite(c)


def test_kk_phase_correction_tiny():
    # Should be negligibly small at IceCube energies
    c = kk_oscillation_phase_correction(1.0, 100.0)
    assert c < 1e-4


def test_kk_phase_correction_raises_non_positive_energy():
    with pytest.raises(ValueError):
        kk_oscillation_phase_correction(0.0, 100.0)


def test_kk_phase_correction_raises_non_positive_baseline():
    with pytest.raises(ValueError):
        kk_oscillation_phase_correction(1.0, 0.0)


def test_majorana_mixing_angle_positive():
    m = majorana_mixing_angle()
    assert m["theta_s_rad"] > 0.0


def test_majorana_mixing_angle_below_sensitivity():
    m = majorana_mixing_angle()
    # theta_s << 0.1 rad
    assert m["theta_s_rad"] < 0.1
    assert m["verdict"] == "BELOW_CURRENT_SENSITIVITY"


def test_majorana_mixing_angle_keys():
    m = majorana_mixing_angle()
    for key in ("theta_s_rad", "theta_s_deg", "verdict"):
        assert key in m


def test_icecube_hese_verdict_consistent():
    v = icecube_hese_comparison()
    assert v["verdict"] == "CONSISTENT"


def test_icecube_hese_sigma_pulls_positive():
    v = icecube_hese_comparison()
    assert v["sigma_nu_e"] >= 0.0
    assert v["sigma_nu_mu"] >= 0.0
    assert v["sigma_nu_tau"] >= 0.0


def test_icecube_hese_keys():
    v = icecube_hese_comparison()
    for key in ("sigma_nu_e", "sigma_nu_mu", "sigma_nu_tau", "max_sigma_pull", "verdict"):
        assert key in v


def test_km3net_projection_preregistered():
    p = km3net_projection()
    assert p["status"] == "PREREGISTERED"


def test_km3net_projection_has_routing():
    p = km3net_projection()
    assert "routing" in p
    assert "falsifier_window" in p


def test_neutrino_report_pillar():
    r = neutrino_preregistration_report()
    assert r["pillar"] == 289


def test_neutrino_report_has_sections():
    r = neutrino_preregistration_report()
    for key in ("flavor_prediction", "majorana_angle", "icecube_hese", "km3net"):
        assert key in r
