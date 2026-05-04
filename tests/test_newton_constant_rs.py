# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 141: Newton Constant from RS Geometry (src/core/newton_constant_rs.py)."""

import math
import pytest

from src.core.newton_constant_rs import (
    newton_constant_from_rs,
    rs_planck_mass_relation,
    newton_constant_closure_status,
    m5_estimate_from_mkk,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def planck_rel():
    return rs_planck_mass_relation()


@pytest.fixture(scope="module")
def newton():
    return newton_constant_from_rs()


@pytest.fixture(scope="module")
def status():
    return newton_constant_closure_status()


@pytest.fixture(scope="module")
def m5_1040():
    return m5_estimate_from_mkk(1040)


# ---------------------------------------------------------------------------
# rs_planck_mass_relation — return type and keys
# ---------------------------------------------------------------------------

def test_planck_rel_is_dict(planck_rel):
    assert isinstance(planck_rel, dict)


def test_planck_rel_has_m_pl_gev(planck_rel):
    assert "M_Pl_gev" in planck_rel


def test_planck_rel_has_m5_gev(planck_rel):
    assert "M5_gev" in planck_rel


def test_planck_rel_has_k_gev(planck_rel):
    assert "k_gev" in planck_rel


def test_planck_rel_has_pi_kr(planck_rel):
    assert "pi_kr" in planck_rel


def test_planck_rel_has_relation_string(planck_rel):
    assert "relation" in planck_rel


# ---------------------------------------------------------------------------
# Planck mass values
# ---------------------------------------------------------------------------

def test_m_pl_in_physical_range(planck_rel):
    assert 1e18 < planck_rel["M_Pl_gev"] < 1.5e19


def test_m_pl_value(planck_rel):
    assert abs(planck_rel["M_Pl_gev"] - 1.2209e19) < 1e16


def test_m5_positive(planck_rel):
    assert planck_rel["M5_gev"] > 0


def test_m5_near_mpl(planck_rel):
    assert abs(planck_rel["M5_gev"] - planck_rel["M_Pl_gev"]) < 1e15


def test_pi_kr_is_37(planck_rel):
    assert abs(planck_rel["pi_kr"] - 37.0) < 0.01


def test_relation_string_non_empty(planck_rel):
    assert len(planck_rel["relation"]) > 0


# ---------------------------------------------------------------------------
# newton_constant_from_rs — return type and keys
# ---------------------------------------------------------------------------

def test_newton_is_dict(newton):
    assert isinstance(newton, dict)


def test_newton_has_g_n_nat(newton):
    assert "G_N_nat" in newton


def test_newton_has_m_pl_gev(newton):
    assert "M_Pl_gev" in newton


def test_newton_has_status(newton):
    assert "status" in newton


def test_newton_has_pi_kr(newton):
    assert "pi_kr" in newton


# ---------------------------------------------------------------------------
# G_N values
# ---------------------------------------------------------------------------

def test_g_n_positive(newton):
    assert newton["G_N_nat"] > 0


def test_g_n_value(newton):
    assert abs(newton["G_N_nat"] - 2.6693e-40) < 1e-43


def test_g_n_in_expected_range(newton):
    # G_N in natural units (GeV^-2) is about 6.7e-39 GeV^-2 — here in Planck units
    assert 1e-42 < newton["G_N_nat"] < 1e-37


def test_newton_m_pl_matches_planck_rel(newton, planck_rel):
    assert abs(newton["M_Pl_gev"] - planck_rel["M_Pl_gev"]) < 1e15


def test_newton_pi_kr_is_37(newton):
    assert abs(newton["pi_kr"] - 37.0) < 0.01


def test_newton_status_constrained(newton):
    assert "CONSTRAINED" in newton["status"]


# ---------------------------------------------------------------------------
# newton_constant_closure_status
# ---------------------------------------------------------------------------

def test_closure_status_is_dict(status):
    assert isinstance(status, dict)


def test_closure_status_pillar_141(status):
    assert status["pillar"] == 141


def test_closure_status_constrained(status):
    assert "CONSTRAINED" in status["status"]


def test_closure_status_has_g_n_nat(status):
    assert "G_N_nat" in status


def test_closure_status_has_m_pl(status):
    assert "M_Pl_gev" in status


def test_closure_status_closed_true(status):
    assert status.get("closed") is True


def test_closure_status_has_caveat(status):
    assert "caveat" in status


def test_closure_status_caveat_non_empty(status):
    assert len(status["caveat"]) > 0


def test_closure_status_caveat_mentions_m5(status):
    caveat = status["caveat"].lower()
    assert "m5" in caveat or "m₅" in caveat or "uv" in caveat


# ---------------------------------------------------------------------------
# m5_estimate_from_mkk
# ---------------------------------------------------------------------------

def test_m5_1040_is_dict(m5_1040):
    assert isinstance(m5_1040, dict)


def test_m5_1040_has_m5_gev(m5_1040):
    assert "m5_gev" in m5_1040


def test_m5_1040_positive(m5_1040):
    assert m5_1040["m5_gev"] > 0


def test_m5_1040_in_planck_range(m5_1040):
    assert 1e18 < m5_1040["m5_gev"] < 1.5e19


def test_m5_1040_value(m5_1040):
    assert abs(m5_1040["m5_gev"] - 1.22e19) < 1e17


def test_m5_1040_has_k_gev(m5_1040):
    assert "k_gev" in m5_1040


def test_m5_1040_k_positive(m5_1040):
    assert m5_1040["k_gev"] > 0


def test_m5_1040_has_m_kk_gev(m5_1040):
    assert "m_kk_gev" in m5_1040


def test_m5_1040_input_preserved(m5_1040):
    assert abs(m5_1040["m_kk_gev"] - 1040) < 1.0
