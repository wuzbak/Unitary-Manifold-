# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 325 — BBN N_eff Consistency from KK Degrees of Freedom."""
import math
import pytest

from src.core.pillar325_bbn_neff_kk_consistency import (
    N_W, K_CS, PI_KR, M_KK_GEV, M_KK_MEV,
    T_BBN_MIN_MEV, T_BBN_MAX_MEV,
    N_EFF_SM, N_EFF_PLANCK, N_EFF_UNC_PLANCK, N_EFF_CMBS4_UNC,
    Y_P_OBSERVED, Y_P_SM, Y_P_UNC,
    separation_guard,
    kk_boltzmann_suppression,
    delta_neff_kk_tower,
    radion_mass_estimate,
    delta_neff_radion,
    helium4_abundance_correction,
    cmbs4_sensitivity_check,
    bbn_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_m_kk_mev(self):
        # M_KK ~ 1 TeV = 10^6 MeV
        assert M_KK_MEV > 1e5

    def test_n_eff_sm(self):
        assert abs(N_EFF_SM - 3.044) < 0.01

    def test_y_p_observed(self):
        # He-4 mass fraction ~24.5%
        assert 0.23 < Y_P_OBSERVED < 0.26

    def test_bbn_temps(self):
        assert T_BBN_MIN_MEV < T_BBN_MAX_MEV

    def test_cmbs4_better_than_planck(self):
        assert N_EFF_CMBS4_UNC < N_EFF_UNC_PLANCK


class TestSeparationGuard:
    def test_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent(self):
        assert "ADJACENT" in separation_guard()


class TestBoltzmannSuppression:
    def test_zero_for_m_much_larger_than_t(self):
        # M_KK ~ 10^6 MeV, T ~ 1 MeV → exp(-10^6) = 0
        supp = kk_boltzmann_suppression(1e6, 1.0)
        assert supp == 0.0

    def test_one_for_m_equals_zero(self):
        # exp(-0) = 1
        supp = kk_boltzmann_suppression(0.0, 1.0)
        # With exponent = -0/1 = 0, result = 1
        assert supp == pytest.approx(1.0, rel=1e-6)

    def test_decreases_with_mass(self):
        s1 = kk_boltzmann_suppression(10.0, 5.0)
        s2 = kk_boltzmann_suppression(20.0, 5.0)
        assert s1 > s2

    def test_kk_mev_gives_zero(self):
        assert kk_boltzmann_suppression(M_KK_MEV, 1.0) == 0.0


class TestDeltaNeff:
    def test_kk_tower_zero_at_bbn(self):
        dn = delta_neff_kk_tower(M_KK_MEV, t_bbn_mev=1.0)
        assert dn == 0.0

    def test_kk_tower_positive_for_light_mass(self):
        # If KK mass ~ 1 MeV (much lighter), expect non-zero ΔN_eff
        dn = delta_neff_kk_tower(m_kk_mev=1.0, t_bbn_mev=1.0)
        assert dn > 0.0

    def test_increases_with_modes(self):
        d1 = delta_neff_kk_tower(m_kk_mev=1.0, t_bbn_mev=1.0, n_modes=1)
        d3 = delta_neff_kk_tower(m_kk_mev=1.0, t_bbn_mev=1.0, n_modes=3)
        assert d3 >= d1


class TestRadionMass:
    def test_positive(self):
        m = radion_mass_estimate()
        assert m > 0.0

    def test_geom_scale(self):
        # Radion mass ~ GeV to hundreds of GeV
        m = radion_mass_estimate()
        assert 0.1 < m < 1000.0  # GeV

    def test_increases_with_lambda(self):
        m_low = radion_mass_estimate(lambda_gw=0.1)
        m_high = radion_mass_estimate(lambda_gw=10.0)
        assert m_high > m_low


class TestDeltaNeffRadion:
    def test_zero_for_kk_mass(self):
        # Radion is also heavy (GeV scale >> MeV BBN temp)
        dn = delta_neff_radion(M_KK_GEV, t_bbn_mev=1.0)
        assert dn == 0.0


class TestHelium4:
    def test_zero_correction_for_zero_neff(self):
        assert helium4_abundance_correction(0.0) == 0.0

    def test_positive_for_positive_neff(self):
        assert helium4_abundance_correction(0.1) > 0.0

    def test_scale(self):
        # 0.013 per ΔN_eff = 1
        dy = helium4_abundance_correction(1.0)
        assert abs(dy - 0.013) < 1e-10


class TestCmbs4Check:
    def test_below_threshold(self):
        r = cmbs4_sensitivity_check(1e-30)
        assert r["verdict"] == "BELOW_CMBS4_THRESHOLD"
        assert r["detectable_by_cmbs4"] is False

    def test_above_threshold(self):
        r = cmbs4_sensitivity_check(1.0)
        assert r["detectable_by_cmbs4"] is True

    def test_zero_neff(self):
        r = cmbs4_sensitivity_check(0.0)
        assert r["n_sigma_significance"] == 0.0


class TestFullReport:
    def setup_method(self):
        self.r = bbn_full_report()

    def test_pillar_number(self):
        assert self.r["pillar"] == 325

    def test_adjacency(self):
        assert self.r["adjacency"] == "NON_HARDGATE_ADJACENT"

    def test_verdict_consistent(self):
        assert self.r["verdict"] == "BBN_CONSISTENT"

    def test_delta_neff_zero(self):
        assert self.r["delta_neff_kk_tower"] == 0.0

    def test_planck_consistent(self):
        assert self.r["planck_consistent"] is True

    def test_yp_consistent(self):
        assert self.r["yp_consistent"] is True

    def test_cmbs4_prediction(self):
        assert isinstance(self.r["cmbs4_prediction"], str)
        assert "CMBS4" in self.r["cmbs4_prediction"] or "CMB-S4" in self.r["cmbs4_prediction"]

    def test_boltzmann_suppression(self):
        assert self.r["boltzmann_suppression_at_1mev"] == 0.0

    def test_physics_summary(self):
        assert "CONSISTENT" in self.r["physics_summary"]
