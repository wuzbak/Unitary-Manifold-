# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 324 — EW Oblique Corrections S,T,U from KK Tower."""
import math
import pytest

from src.core.pillar324_ew_oblique_kk_tower import (
    N_W, N2, K_CS, PI_KR, C_S, M_KK_GEV,
    ALPHA_EM, SIN2_TW, M_W_GEV, M_Z_GEV, M_T_GEV,
    S_CENTRAL, T_CENTRAL, U_CENTRAL,
    S_UNC, T_UNC, U_UNC,
    FCCE_S_UNC, FCCE_T_UNC,
    separation_guard,
    braid_mixing_rho,
    kk_s_parameter,
    kk_t_parameter_braid,
    kk_u_parameter,
    oblique_params_full,
    fcc_ee_detectability,
    ew_oblique_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_n2(self):
        assert N2 == 7

    def test_k_cs(self):
        assert K_CS == 74

    def test_sin2_tw(self):
        assert 0.22 < SIN2_TW < 0.24

    def test_m_w_approx(self):
        assert 80.0 < M_W_GEV < 81.0

    def test_fcc_ee_much_better_than_lep(self):
        assert FCCE_S_UNC < S_UNC / 10


class TestSeparationGuard:
    def test_returns_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent(self):
        assert "ADJACENT" in separation_guard()


class TestBraidMixingRho:
    def test_canonical(self):
        rho = braid_mixing_rho(5, 7, 74)
        assert abs(rho - 70/74) < 1e-10

    def test_less_than_one(self):
        assert braid_mixing_rho() < 1.0

    def test_positive(self):
        assert braid_mixing_rho() > 0.0

    def test_large(self):
        # 70/74 ≈ 0.946
        assert braid_mixing_rho() > 0.9


class TestKkSParameter:
    def test_positive(self):
        assert kk_s_parameter() > 0.0

    def test_below_lep_3sigma(self):
        # S_KK ~ 0.22; LEP bound S = 0.02 ± 0.10.
        # RS1 models famously have large S; check within 3σ (|S| < 0.32)
        assert abs(kk_s_parameter() - S_CENTRAL) < 3.0 * S_UNC

    def test_small_but_nonzero(self):
        s = kk_s_parameter()
        assert 1e-4 < s < 1.0

    def test_decreases_with_heavier_kk(self):
        s1 = kk_s_parameter(m_kk_gev=1000.0)
        s2 = kk_s_parameter(m_kk_gev=3000.0)
        assert s1 > s2


class TestKkTParameter:
    def test_positive(self):
        t = kk_t_parameter_braid()
        assert t > 0.0

    def test_below_lep_bound(self):
        assert kk_t_parameter_braid() < T_UNC

    def test_small(self):
        t = kk_t_parameter_braid()
        assert 1e-4 < t < 0.1


class TestKkUParameter:
    def test_sign(self):
        s = kk_s_parameter()
        u = kk_u_parameter(s)
        # U is negative (opposite sign to S)
        assert u < 0.0

    def test_small(self):
        s = kk_s_parameter()
        u = kk_u_parameter(s)
        assert abs(u) < abs(s)


class TestObliqueParams:
    def test_returns_dict(self):
        r = oblique_params_full()
        assert isinstance(r, dict)

    def test_all_keys(self):
        r = oblique_params_full()
        for k in ["S_kk", "T_kk", "U_kk", "S_total_bsm", "T_total_bsm", "U_total_bsm"]:
            assert k in r

    def test_s_t_within_3sigma_lep(self):
        # S = 0.02 ± 0.10, T = 0.07 ± 0.12 (LEP global fit)
        # RS1 S parameter is large; test within 3σ
        r = oblique_params_full()
        assert abs(r["S_kk"] - S_CENTRAL) < 3.0 * S_UNC
        assert abs(r["T_kk"] - T_CENTRAL) < 3.0 * T_UNC


class TestFccEeDetectability:
    def test_returns_dict(self):
        r = oblique_params_full()
        det = fcc_ee_detectability(r["S_kk"], r["T_kk"], r["U_kk"])
        assert isinstance(det, dict)

    def test_significance_positive(self):
        r = oblique_params_full()
        det = fcc_ee_detectability(r["S_kk"], r["T_kk"], r["U_kk"])
        assert det["fcc_ee_s_significance"] >= 0.0
        assert det["fcc_ee_t_significance"] >= 0.0

    def test_lep_3sigma_consistent(self):
        # RS1 S parameter is large; check within 3σ of LEP central value
        r = oblique_params_full()
        det = fcc_ee_detectability(r["S_kk"], r["T_kk"], r["U_kk"])
        # S_KK ~ 0.22, LEP S = 0.02 ± 0.10 → ~2.0σ; within 3σ
        assert det["lep_s_significance"] < 3.0


class TestFullReport:
    def setup_method(self):
        self.r = ew_oblique_full_report()

    def test_pillar_number(self):
        assert self.r["pillar"] == 324

    def test_adjacency(self):
        assert self.r["adjacency"] == "NON_HARDGATE_ADJACENT"

    def test_m_kk_tev(self):
        assert 0.5 < self.r["m_kk_tev"] < 5.0

    def test_braid_rho(self):
        assert 0.9 < self.r["braid_rho"] < 1.0

    def test_current_consistency(self):
        # RS1 S parameter is known to be large; within 3σ of LEP
        s_kk = self.r["oblique_params"]["S_kk"]
        assert abs(s_kk - S_CENTRAL) < 3.0 * S_UNC

    def test_physics_summary_string(self):
        assert isinstance(self.r["physics_summary"], str)
        assert len(self.r["physics_summary"]) > 50

    def test_fcc_ee_opportunity(self):
        assert isinstance(self.r["opportunity"], str)

    def test_falsifier(self):
        assert isinstance(self.r["falsifier"], str)
