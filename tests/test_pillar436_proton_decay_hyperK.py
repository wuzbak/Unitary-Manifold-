# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 436 — Hyper-K Proton Decay Prediction Package."""
from __future__ import annotations

import hashlib
import math
import pytest

from src.core.pillar436_proton_decay_hyperK import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    PI_KR,
    ALPHA_GUT,
    M_PROTON_GEV,
    M_KK_MIN_GEV,
    M_X_GEV,
    A_L_RENORM,
    F_ORB,
    SK_LIMIT_YR,
    HK_SENSITIVITY_YR,
    GEV_TO_YR,
    PREREGISTRATION_HASH,
    m_x_from_kk,
    f_orb_suppression,
    proton_lifetime_yr,
    hyperk_comparison,
    preregistration_hash_verify,
    proton_decay_package,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'PROTON_DECAY_BOUNDED_FROM_KK_GUT'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 436

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_alpha_gut(self):
        assert abs(ALPHA_GUT - 3.0 / 74.0) < 1e-12

    def test_m_proton_reasonable(self):
        assert abs(M_PROTON_GEV - 0.938272) < 1e-4

    def test_m_kk_min_in_gev(self):
        assert M_KK_MIN_GEV == pytest.approx(5.0e3)  # 5 TeV in GeV

    def test_m_x_large(self):
        # M_X = M_KK × exp(37) should be > M_Planck ~ 1.22e19 GeV
        assert M_X_GEV > 1.0e18

    def test_a_l_reasonable(self):
        assert 1.0 < A_L_RENORM < 2.0

    def test_f_orb_positive(self):
        assert F_ORB > 0.0

    def test_f_orb_less_than_one(self):
        assert F_ORB < 1.0

    def test_sk_limit_order(self):
        assert SK_LIMIT_YR > 1.0e33

    def test_hk_larger_than_sk(self):
        assert HK_SENSITIVITY_YR > SK_LIMIT_YR

    def test_gev_to_yr_positive(self):
        assert GEV_TO_YR > 0.0

    def test_preregistration_hash_length(self):
        assert len(PREREGISTRATION_HASH) == 64


class TestMxFromKK:
    def test_uses_exp_pikr(self):
        m_x = m_x_from_kk(5.0e3, 37.0)
        assert abs(m_x - 5.0e3 * math.exp(37.0)) < 1.0

    def test_scaling_with_m_kk(self):
        m1 = m_x_from_kk(5.0e3)
        m2 = m_x_from_kk(10.0e3)
        assert abs(m2 / m1 - 2.0) < 0.01

    def test_matches_constant(self):
        assert abs(m_x_from_kk() - M_X_GEV) < 1.0


class TestFOrbSuppression:
    def test_n_w_five(self):
        expected = (math.cos(math.pi / 5) ** 2) / 5.0
        assert abs(f_orb_suppression(5) - expected) < 1e-12

    def test_positive(self):
        assert f_orb_suppression(5) > 0.0

    def test_matches_constant(self):
        assert abs(f_orb_suppression(N_W) - F_ORB) < 1e-12

    def test_different_n_w(self):
        # Different winding numbers give different suppression
        assert f_orb_suppression(5) != f_orb_suppression(7)


class TestProtonLifetimeYr:
    def test_positive(self):
        tau = proton_lifetime_yr()
        assert tau > 0.0

    def test_far_above_sk(self):
        # UM predicts tau >> 10^34 yr (super-Planckian M_X)
        tau = proton_lifetime_yr()
        assert tau > SK_LIMIT_YR

    def test_far_above_hk(self):
        # UM prediction is not testable by Hyper-K
        tau = proton_lifetime_yr()
        assert tau > HK_SENSITIVITY_YR

    def test_scales_with_m_x_fourth(self):
        # tau ∝ M_X^4
        tau1 = proton_lifetime_yr(m_x_gev=1.0e19)
        tau2 = proton_lifetime_yr(m_x_gev=2.0e19)
        ratio = tau2 / tau1
        assert abs(ratio - 2.0 ** 4) < ratio * 0.01  # within 1%

    def test_larger_alpha_shorter_lifetime(self):
        tau1 = proton_lifetime_yr(alpha_gut=0.04)
        tau2 = proton_lifetime_yr(alpha_gut=0.08)
        assert tau1 > tau2


class TestHyperkComparison:
    def setup_method(self):
        self.tau = proton_lifetime_yr()
        self.result = hyperk_comparison(self.tau)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_above_sk_true(self):
        assert self.result['above_sk']

    def test_above_hk_true(self):
        assert self.result['above_hk']

    def test_verdict_not_testable(self):
        assert self.result['verdict'] == 'NOT_TESTABLE_HYPERK'

    def test_label_correct(self):
        assert self.result['label'] == 'PROTON_DECAY_BOUNDED_FROM_KK_GUT'

    def test_testable_if_short(self):
        result = hyperk_comparison(5.0e34)
        assert result['verdict'] == 'TESTABLE_HYPERK'

    def test_tension_if_below_sk(self):
        result = hyperk_comparison(1.0e33)
        assert result['verdict'] == 'IN_TENSION'


class TestPreregistrationHashVerify:
    def test_returns_dict(self):
        result = preregistration_hash_verify()
        assert isinstance(result, dict)

    def test_verified(self):
        result = preregistration_hash_verify()
        assert result['status'] == 'VERIFIED'

    def test_hash_matches_constant(self):
        result = preregistration_hash_verify()
        assert result['sha256_hash'] == PREREGISTRATION_HASH


class TestProtonDecayPackage:
    def setup_method(self):
        self.pkg = proton_decay_package()

    def test_returns_dict(self):
        assert isinstance(self.pkg, dict)

    def test_pillar_number(self):
        assert self.pkg['pillar'] == 436

    def test_status(self):
        assert self.pkg['status'] == 'PROTON_DECAY_BOUNDED_FROM_KK_GUT'

    def test_prediction_not_testable(self):
        assert self.pkg['prediction']['verdict'] == 'NOT_TESTABLE_HYPERK'

    def test_alpha_gut_in_derivation(self):
        assert abs(self.pkg['derivation']['alpha_gut'] - ALPHA_GUT) < 1e-12

    def test_m_x_large(self):
        assert self.pkg['derivation']['m_x_gev'] > 1.0e19

    def test_preregistration_verified(self):
        assert self.pkg['preregistration']['status'] == 'VERIFIED'

    def test_routing_keys(self):
        routing = self.pkg['routing']
        assert 'NOT_TESTABLE_HYPERK' in routing
        assert 'TESTABLE_HYPERK' in routing


class TestNumerics:
    def test_alpha_gut_exact(self):
        assert ALPHA_GUT == pytest.approx(3.0 / 74.0)

    def test_m_x_formula(self):
        expected = M_KK_MIN_GEV * math.exp(PI_KR)
        assert abs(M_X_GEV - expected) < 1.0

    def test_f_orb_formula(self):
        expected = (math.cos(math.pi / N_W) ** 2) / N_W
        assert abs(F_ORB - expected) < 1e-12
