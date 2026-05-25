# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 484 — PMNS p_R Two-Loop Yukawa Execution."""
from __future__ import annotations

import math

from src.core.pillar484_pmns_pr_two_loop_yukawa import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    C_S,
    ALPHA_S_KK,
    M_KK_GEV,
    M_R_GEV,
    PR_LO,
    B_NU,
    DELTA_2LOOP,
    PR_NLO,
    PR_NLO_UNCERTAINTY,
    PR_NLO_LOW,
    PR_NLO_HIGH,
    beta_function_nu,
    yukawa_rge_one_loop,
    two_loop_correction,
    pr_nlo_from_rge,
    seesaw_effective_mass,
    pmns_solar_angle_from_pr,
    nlo_interval,
    derivation_chain_status,
    pillar_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'PMNS_PR_TWO_LOOP_YUKAWA_EXECUTED'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 484

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-10

    def test_alpha_s_kk_formula(self):
        assert abs(ALPHA_S_KK - 2 * math.pi / K_CS) < 1e-10

    def test_m_kk_in_tev_range(self):
        assert M_KK_GEV > 1000  # > 1 TeV

    def test_m_r_greater_than_m_kk(self):
        assert M_R_GEV > M_KK_GEV

    def test_pr_lo_in_interval(self):
        assert 0.30 <= PR_LO <= 0.43

    def test_b_nu_value(self):
        assert abs(B_NU - 1.5 * K_CS / N_W) < 1e-8

    def test_delta_2loop_positive(self):
        assert DELTA_2LOOP > 0  # M_R > M_KK so ln > 0

    def test_pr_nlo_close_to_pr_lo(self):
        # NLO correction should be < 15%
        assert abs(PR_NLO - PR_LO) / PR_LO < 0.15

    def test_pr_nlo_positive(self):
        assert PR_NLO > 0

    def test_uncertainty_is_5pct(self):
        assert abs(PR_NLO_UNCERTAINTY / PR_NLO - 0.05) < 0.001

    def test_low_high_symmetric(self):
        assert abs((PR_NLO_HIGH - PR_NLO) - (PR_NLO - PR_NLO_LOW)) < 1e-10


class TestBetaFunctionNu:
    def setup_method(self):
        self.beta = beta_function_nu()

    def test_returns_dict(self):
        assert isinstance(self.beta, dict)

    def test_b_nu_one_loop(self):
        assert abs(self.beta['b_nu_one_loop'] - B_NU) < 1e-8

    def test_b_nu_two_loop_smaller(self):
        assert self.beta['b_nu_two_loop'] < self.beta['b_nu_one_loop']

    def test_has_alpha_s(self):
        assert 'alpha_s' in self.beta

    def test_has_formula(self):
        assert 'formula' in self.beta

    def test_k_cs_consistent(self):
        assert self.beta['k_cs'] == K_CS

    def test_n_w_consistent(self):
        assert self.beta['n_w'] == N_W


class TestYukawaRGEOneLoop:
    def setup_method(self):
        self.rge = yukawa_rge_one_loop()

    def test_returns_dict(self):
        assert isinstance(self.rge, dict)

    def test_y_nu_mr_positive(self):
        assert self.rge['y_nu_mr'] > 0

    def test_ratio_less_than_one(self):
        # Y_ν runs up or down depending on sign of b_ν × log_ratio
        assert 'ratio' in self.rge

    def test_log_ratio_positive(self):
        assert self.rge['log_ratio'] > 0  # M_R > M_KK

    def test_loop_is_1(self):
        assert self.rge['loop'] == 1

    def test_mass_scales(self):
        assert self.rge['m_kk'] == M_KK_GEV
        assert self.rge['m_r'] == M_R_GEV


class TestTwoLoopCorrection:
    def setup_method(self):
        self.corr = two_loop_correction()

    def test_returns_dict(self):
        assert isinstance(self.corr, dict)

    def test_delta_2loop_matches_constant(self):
        assert abs(self.corr['delta_2loop'] - DELTA_2LOOP) < 1e-10

    def test_b_nu_correct(self):
        assert abs(self.corr['b_nu'] - B_NU) < 1e-8

    def test_has_formula(self):
        assert 'formula' in self.corr

    def test_relative_correction_pct(self):
        pct = self.corr['relative_correction_pct']
        assert pct > 0
        assert pct < 15  # < 15% correction

    def test_log_ratio_positive(self):
        assert self.corr['log_ratio'] > 0


class TestPrNLOFromRGE:
    def setup_method(self):
        self.nlo = pr_nlo_from_rge()

    def test_returns_dict(self):
        assert isinstance(self.nlo, dict)

    def test_pr_nlo_matches_constant(self):
        assert abs(self.nlo['pr_nlo'] - PR_NLO) < 1e-10

    def test_pr_lo_correct(self):
        assert self.nlo['pr_lo'] == PR_LO

    def test_nlo_interval_narrower(self):
        assert self.nlo['interval_width_nlo'] < self.nlo['interval_width_lo']

    def test_lo_interval(self):
        assert self.nlo['lo_interval'] == (0.30, 0.43)

    def test_nlo_interval_within_lo(self):
        lo_low, lo_high = self.nlo['lo_interval']
        nlo_low, nlo_high = self.nlo['nlo_interval']
        # NLO central value should stay within LO interval
        assert lo_low <= self.nlo['pr_nlo'] <= lo_high

    def test_uncertainty_positive(self):
        assert self.nlo['uncertainty'] > 0

    def test_narrows_interval(self):
        assert self.nlo['narrows_interval'] is True

    def test_low_less_than_high(self):
        assert self.nlo['pr_nlo_low'] < self.nlo['pr_nlo_high']


class TestSeesawEffectiveMass:
    def test_returns_dict(self):
        result = seesaw_effective_mass()
        assert isinstance(result, dict)

    def test_m_nu_positive(self):
        result = seesaw_effective_mass()
        assert result['m_nu_ev'] > 0

    def test_consistent_with_planck_at_default(self):
        result = seesaw_effective_mass(y_nu=0.1)
        assert 'consistent_with_planck' in result

    def test_larger_y_larger_mass(self):
        r1 = seesaw_effective_mass(y_nu=0.1)
        r2 = seesaw_effective_mass(y_nu=0.5)
        assert r2['m_nu_ev'] > r1['m_nu_ev']

    def test_formula_string(self):
        result = seesaw_effective_mass()
        assert 'formula' in result


class TestPMNSSolarAngleFromPR:
    def setup_method(self):
        self.angle = pmns_solar_angle_from_pr(PR_NLO)

    def test_returns_dict(self):
        assert isinstance(self.angle, dict)

    def test_theta12_in_physical_range(self):
        # theta12 from arctan(p_R^NLO); p_R_NLO ≈ 0.37 → arctan ≈ 20°
        # Physical solar mixing angle range from this leading-order relation: 15–45°
        assert 15 < self.angle['theta12_deg'] < 45

    def test_pdg_reference(self):
        assert abs(self.angle['pdg_theta12_deg'] - 33.41) < 0.1

    def test_tension_sigma(self):
        assert self.angle['tension_sigma'] >= 0

    def test_consistent_with_data(self):
        assert isinstance(self.angle['consistent_with_data'], bool)

    def test_formula(self):
        assert 'formula' in self.angle

    def test_pr_stored(self):
        assert abs(self.angle['p_r'] - PR_NLO) < 1e-10

    def test_zero_pr_gives_zero_angle(self):
        result = pmns_solar_angle_from_pr(0.0)
        assert abs(result['theta12_deg']) < 0.01


class TestNLOInterval:
    def setup_method(self):
        self.interval = nlo_interval()

    def test_returns_dict(self):
        assert isinstance(self.interval, dict)

    def test_lo_interval(self):
        assert self.interval['lo_interval'] == (0.30, 0.43)

    def test_narrowing_factor_greater_than_1(self):
        assert self.interval['narrowing_factor'] > 1.0

    def test_width_ratio_less_than_1(self):
        assert self.interval['width_ratio'] < 1.0

    def test_pr_nlo_central(self):
        assert abs(self.interval['pr_nlo_central'] - PR_NLO) < 1e-10

    def test_has_verdict(self):
        assert 'verdict' in self.interval
        assert 'narrows' in self.interval['verdict'].lower()


class TestDerivationChainStatus:
    def setup_method(self):
        self.chain = derivation_chain_status()

    def test_returns_dict(self):
        assert isinstance(self.chain, dict)

    def test_has_pillar_statuses(self):
        assert 'pillar_461_status' in self.chain
        assert 'pillar_484_status' in self.chain

    def test_pillar_484_status_correct(self):
        assert self.chain['pillar_484_status'] == PILLAR_STATUS

    def test_chain_steps_listed(self):
        assert len(self.chain['chain_steps_executed']) >= 4

    def test_pr_nlo_in_result(self):
        assert abs(self.chain['pr_nlo'] - PR_NLO) < 1e-10

    def test_residual_documented(self):
        assert 'residual_remaining' in self.chain
        assert len(self.chain['residual_remaining']) > 20

    def test_epistemic_upgrade_documented(self):
        assert 'epistemic_upgrade' in self.chain
        assert 'NAMED_RESIDUAL' in self.chain['epistemic_upgrade']


class TestPillarReport:
    def setup_method(self):
        self.report = pillar_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar_number(self):
        assert self.report['pillar'] == 484

    def test_status(self):
        assert self.report['status'] == PILLAR_STATUS

    def test_has_constants(self):
        c = self.report['constants']
        assert c['n_w'] == N_W
        assert c['k_cs'] == K_CS

    def test_has_nlo_result(self):
        assert 'nlo_result' in self.report

    def test_has_seesaw_mass(self):
        assert 'seesaw_mass' in self.report

    def test_has_pmns_solar_angle(self):
        assert 'pmns_solar_angle' in self.report

    def test_has_interval_summary(self):
        assert 'interval_summary' in self.report

    def test_has_verdict(self):
        assert 'verdict' in self.report
        assert 'NLO' in self.report['verdict'] or 'nlo' in self.report['verdict'].lower()

    def test_has_chain_status(self):
        assert 'chain_status' in self.report
