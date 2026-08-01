# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 635 — P19 lightest neutrino mass c_L bound."""
from __future__ import annotations

import math

from src.core.pillar635_p19_lightest_nu_cl_bound import (
    C_L_PHYS,
    C_R_PHYS,
    K_CS,
    KATRIN_SENSITIVITY_MEV,
    M_KK_GEV,
    M_NU1_MAX_MEV,
    M_NU1_SEESAW_GEV,
    M_R_GEV,
    N_W,
    P19_STATUS_AFTER,
    P19_STATUS_BEFORE,
    PI_KR,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PLANCK_SIGMA_MNU_MEV,
    VERSION,
    cl_topological_bound,
    experimental_comparison,
    p19_status,
    pillar_report,
    seesaw_mass_chain,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
BOUND = cl_topological_bound()
CHAIN = seesaw_mass_chain()
EXP = experimental_comparison()
STATUS = p19_status()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 635

    def test_status(self):
        assert PILLAR_STATUS == "P19_LIGHTEST_NU_CL_BOUND_TIGHTENED"

    def test_c_l_phys(self):
        assert abs(C_L_PHYS - 71.0 / 74.0) < 1e-12

    def test_c_r_phys(self):
        assert abs(C_R_PHYS - 0.50) < 1e-12

    def test_pi_kr(self):
        expected = (K_CS / N_W) * math.pi
        assert abs(PI_KR - expected) < 1e-10

    def test_m_r_gev(self):
        expected = M_KK_GEV * C_R_PHYS / C_L_PHYS
        assert abs(M_R_GEV - expected) < 1e-9

    def test_m_nu1_max_tighter_than_planck(self):
        assert M_NU1_MAX_MEV < PLANCK_SIGMA_MNU_MEV

    def test_m_nu1_max_below_katrin(self):
        # Below KATRIN sensitivity — not directly testable by KATRIN
        assert M_NU1_MAX_MEV < KATRIN_SENSITIVITY_MEV


class TestTopologicalBound:
    def test_tighter_than_planck(self):
        assert BOUND["tighter_than_planck"] is True

    def test_m_nu1_max_mev_positive(self):
        assert BOUND["m_nu1_max_mev_conservative"] > 0.0

    def test_c_l_range(self):
        assert BOUND["c_l_range"][0] < C_L_PHYS < BOUND["c_l_range"][1]


class TestSeesawChain:
    def test_formula(self):
        assert "mν₁" in CHAIN["formula"]

    def test_m_nu1_positive(self):
        assert M_NU1_SEESAW_GEV > 0.0

    def test_m_dirac_positive(self):
        assert CHAIN["m_dirac_gev"] > 0.0


class TestExperimentalComparison:
    def test_not_detectable_by_katrin(self):
        assert EXP["detectable_by_katrin"] is False


class TestStatusAdvance:
    def test_before(self):
        assert P19_STATUS_BEFORE == "OPEN"

    def test_after(self):
        assert "TIGHTENED" in P19_STATUS_AFTER


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 3
        assert len(what_is_NOT_claimed()) >= 3
