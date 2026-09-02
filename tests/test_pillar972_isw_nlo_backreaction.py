# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 972 — ISW NLO Back-Reaction Bound."""

import math

from src.core.pillar972_isw_nlo_backreaction import (
    ALPHA_BR,
    DELTA_CL_THRESHOLD,
    K_CS,
    L_BINS,
    N_W,
    OMEGA_GAMMA_REC,
    PHI0,
    PILLAR_STATUS,
    PILLAR_VALID,
    delta_cl_isw,
    fallibility_update,
    isw_boltzmann_bound_certified,
    isw_nlo_amplitude,
    isw_nlo_table,
    pillar972_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "ISW_NLO_BOLTZMANN_BOUNDED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_basic_constants():
    assert N_W == 5
    assert K_CS == 74
    assert PHI0 == 1.0


def test_alpha_br_value():
    assert math.isclose(ALPHA_BR, 25.0 / 148.0, rel_tol=0.0, abs_tol=1e-15)


def test_omega_gamma_rec_value():
    assert OMEGA_GAMMA_REC == 0.07


def test_l_bins():
    assert L_BINS == [20, 100, 400]


def test_threshold_value():
    assert DELTA_CL_THRESHOLD == 1e-3


def test_amplitude_payload():
    result = isw_nlo_amplitude()
    assert result["alpha_BR"] == ALPHA_BR
    assert result["omega_gamma_rec"] == OMEGA_GAMMA_REC


def test_amplitude_nlo_scale():
    result = isw_nlo_amplitude()
    assert 1.3e-4 < result["A_NLO"] < 1.5e-4


def test_delta_cl_ell_20():
    result = delta_cl_isw(20)
    assert 5.8e-4 < result["delta_cl_over_cl"] < 6.0e-4
    assert result["below_threshold"] is True


def test_delta_cl_ell_100():
    result = delta_cl_isw(100)
    assert 1.1e-4 < result["delta_cl_over_cl"] < 1.2e-4


def test_delta_cl_ell_400():
    result = delta_cl_isw(400)
    assert 2.9e-5 < result["delta_cl_over_cl"] < 3.0e-5


def test_table_length():
    assert len(isw_nlo_table()) == 3


def test_table_is_monotone_decreasing():
    table = isw_nlo_table()
    deltas = [row["delta_cl_over_cl"] for row in table]
    assert deltas[0] > deltas[1] > deltas[2]


def test_boltzmann_bound_certified():
    result = isw_boltzmann_bound_certified()
    assert result["all_below_threshold"] is True
    assert result["max_delta_cl_over_cl"] < DELTA_CL_THRESHOLD


def test_fallibility_update():
    result = fallibility_update()
    assert result["previous_status"] == "OPEN"
    assert result["new_status"] == "CLOSED"
    assert result["pillar"] == 972


def test_summary_metadata():
    result = pillar972_summary()
    assert result["pillar"] == 972
    assert result["status"] == PILLAR_STATUS
    assert result["valid"] is True
