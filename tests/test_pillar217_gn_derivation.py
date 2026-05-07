# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar217_gn_derivation.py — Pillar 217 test suite."""
import math
import pytest
from src.core.pillar217_gn_derivation import (
    N_W,
    K_CS,
    PI_K_R,
    M_PL_GEV,
    V_EW_GEV,
    G_N_SI,
    m5_from_rs1,
    gn_in_planck_units,
    mkk_from_m5,
    dimensional_argument,
    pillar217_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_k_r(self):
        assert abs(PI_K_R - 37.0) < 1e-10

    def test_m_pl_gev(self):
        assert abs(M_PL_GEV - 1.22089e19) / M_PL_GEV < 1e-4

    def test_v_ew_gev(self):
        assert abs(V_EW_GEV - 246.22) < 0.01

    def test_g_n_si_positive(self):
        assert G_N_SI > 0


# ---------------------------------------------------------------------------
# m5_from_rs1
# ---------------------------------------------------------------------------
class TestM5FromRS1:
    def setup_method(self):
        self.result = m5_from_rs1()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_m5_planck(self):
        assert "m5_planck_units" in self.result

    def test_m5_planck_value(self):
        expected = (2.0 / 74) ** (1.0 / 3.0)
        assert abs(self.result["m5_planck_units"] - expected) < 1e-10

    def test_m5_planck_approx_0_300(self):
        assert abs(self.result["m5_planck_units"] - 0.300) < 0.005

    def test_m5_formula_assertion(self):
        expected = (2.0 / K_CS) ** (1.0 / 3.0)
        assert abs(self.result["m5_planck_units"] - expected) < 1e-6

    def test_has_m5_gev(self):
        assert "m5_gev" in self.result

    def test_m5_gev_gt_1e18(self):
        assert self.result["m5_gev"] > 1e18

    def test_m5_gev_lt_m_pl(self):
        assert self.result["m5_gev"] < M_PL_GEV

    def test_m5_gev_consistent_with_planck(self):
        assert abs(self.result["m5_gev"] - self.result["m5_planck_units"] * M_PL_GEV) < 1e10

    def test_has_derivation(self):
        assert "derivation" in self.result

    def test_derivation_nonempty(self):
        assert len(self.result["derivation"]) > 5

    def test_custom_k_cs(self):
        r = m5_from_rs1(K_cs=100)
        expected = (2.0 / 100) ** (1.0 / 3.0)
        assert abs(r["m5_planck_units"] - expected) < 1e-10

    def test_m5_increases_with_smaller_k_cs(self):
        r50 = m5_from_rs1(K_cs=50)
        r100 = m5_from_rs1(K_cs=100)
        assert r50["m5_planck_units"] > r100["m5_planck_units"]


# ---------------------------------------------------------------------------
# gn_in_planck_units
# ---------------------------------------------------------------------------
class TestGNInPlanckUnits:
    def setup_method(self):
        self.result = gn_in_planck_units()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_gn_planck(self):
        assert "gn_planck" in self.result

    def test_gn_planck_approx(self):
        assert abs(self.result["gn_planck"] - 1.0 / (8.0 * math.pi)) < 1e-10

    def test_gn_planck_range(self):
        assert 0.038 < self.result["gn_planck"] < 0.042

    def test_has_gn_si(self):
        assert "gn_si" in self.result

    def test_gn_si_positive(self):
        assert self.result["gn_si"] > 0

    def test_gn_si_matches_constant(self):
        assert abs(self.result["gn_si"] - G_N_SI) < 1e-15

    def test_has_status(self):
        assert "status" in self.result

    def test_status_contains_dimensional_scale(self):
        assert "DIMENSIONAL SCALE" in self.result["status"]


# ---------------------------------------------------------------------------
# mkk_from_m5
# ---------------------------------------------------------------------------
class TestMKKFromM5:
    def setup_method(self):
        self.result = mkk_from_m5()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_m_kk_planck(self):
        assert "m_kk_planck" in self.result

    def test_m_kk_planck_value(self):
        expected = math.exp(-37.0)
        assert abs(self.result["m_kk_planck"] - expected) < 1e-20

    def test_has_m_kk_gev(self):
        assert "m_kk_gev" in self.result

    def test_m_kk_gev_positive(self):
        assert self.result["m_kk_gev"] > 0

    def test_has_m_kk_tev(self):
        assert "m_kk_tev" in self.result

    def test_m_kk_tev_between_0_1_and_100(self):
        assert 0.1 < self.result["m_kk_tev"] < 100.0

    def test_m_kk_tev_approx_1(self):
        assert 0.5 < self.result["m_kk_tev"] < 5.0

    def test_has_consistency(self):
        assert "consistency_with_v_ew" in self.result

    def test_consistency_true(self):
        assert self.result["consistency_with_v_ew"] is True

    def test_m_kk_gev_consistent_with_tev(self):
        assert abs(self.result["m_kk_gev"] / 1000.0 - self.result["m_kk_tev"]) < 1e-10

    def test_custom_pi_k_r(self):
        r = mkk_from_m5(pi_k_r=30.0)
        expected = math.exp(-30.0) * M_PL_GEV
        assert abs(r["m_kk_gev"] - expected) / expected < 1e-6


# ---------------------------------------------------------------------------
# dimensional_argument
# ---------------------------------------------------------------------------
class TestDimensionalArgument:
    def setup_method(self):
        self.result = dimensional_argument()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_n_free(self):
        assert "n_free_dimensionful" in self.result

    def test_n_free_is_1(self):
        assert self.result["n_free_dimensionful"] == 1

    def test_has_argument(self):
        assert "argument" in self.result

    def test_argument_nonempty(self):
        assert len(self.result["argument"]) > 10

    def test_has_buckingham_pi(self):
        assert "buckingham_pi_statement" in self.result

    def test_buckingham_nonempty(self):
        assert len(self.result["buckingham_pi_statement"]) > 10

    def test_buckingham_mentions_dimensional_scale(self):
        assert "DIMENSIONAL SCALE" in self.result["buckingham_pi_statement"]


# ---------------------------------------------------------------------------
# pillar217_summary
# ---------------------------------------------------------------------------
class TestPillar217Summary:
    def setup_method(self):
        self.result = pillar217_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 217

    def test_has_m5_derivation(self):
        assert "m5_derivation" in self.result
        assert isinstance(self.result["m5_derivation"], dict)

    def test_gn_status_contains_dimensional_scale(self):
        assert "DIMENSIONAL SCALE" in self.result["gn_status"]

    def test_m_kk_tev_range(self):
        assert 0.1 < self.result["m_kk_tev"] < 100.0

    def test_p28_reclassification_contains_dimensional_scale(self):
        assert "DIMENSIONAL SCALE" in self.result["p28_reclassification"]

    def test_rs1_consistency_true(self):
        assert self.result["rs1_consistency"] is True

    def test_toe_delta_zero(self):
        assert self.result["toe_delta"] == 0

    def test_honest_note_nonempty(self):
        assert len(self.result["honest_note"]) > 10

    def test_honest_note_mentions_m_pl(self):
        assert "M_Pl" in self.result["honest_note"] or "Planck" in self.result["honest_note"]

    def test_has_dimensional_argument(self):
        assert "dimensional_argument" in self.result

    def test_gn_planck_value(self):
        assert abs(self.result["gn_planck"] - 1.0 / (8.0 * math.pi)) < 1e-10

    def test_m5_planck_approx_0_300(self):
        m5 = self.result["m5_derivation"]["m5_planck_units"]
        assert abs(m5 - 0.300) < 0.005

    def test_m5_formula(self):
        m5 = self.result["m5_derivation"]["m5_planck_units"]
        expected = (2.0 / K_CS) ** (1.0 / 3.0)
        assert abs(m5 - expected) < 1e-6
