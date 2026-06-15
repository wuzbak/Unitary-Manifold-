# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 435 — HL-LHC KK Graviton Prediction Package."""
from __future__ import annotations

import hashlib
import math
import pytest

from src.core.pillar435_hllhc_kk_graviton import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    PI_KR,
    M_KK_BOUND_TEV,
    BESSEL_CORRECTION,
    K_TILDE_REFERENCE,
    ATLAS_RUN2_LIMIT_TEV,
    CMS_RUN2_LIMIT_TEV,
    HK_REACH_300_TEV,
    HL_LHC_REACH_3000_TEV,
    PREREGISTRATION_HASH,
    sigma_br_leptonic,
    exclusion_reach,
    current_limit_comparison,
    run4_prediction_table,
    preregistration_hash_verify,
    falsification_routing,
    hllhc_prediction_package,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'HLLHC_PREDICTION_PREREGISTERED'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 435

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_m_kk_bound(self):
        assert M_KK_BOUND_TEV == pytest.approx(5.0)

    def test_bessel_correction(self):
        assert abs(BESSEL_CORRECTION - 0.876) < 0.01

    def test_atlas_limit_above_cms(self):
        assert ATLAS_RUN2_LIMIT_TEV > CMS_RUN2_LIMIT_TEV

    def test_um_bound_above_limits(self):
        assert M_KK_BOUND_TEV > ATLAS_RUN2_LIMIT_TEV
        assert M_KK_BOUND_TEV > CMS_RUN2_LIMIT_TEV

    def test_hl_lhc_reach_larger_than_300(self):
        assert HL_LHC_REACH_3000_TEV > HK_REACH_300_TEV

    def test_hash_is_64_hex(self):
        assert len(PREREGISTRATION_HASH) == 64
        int(PREREGISTRATION_HASH, 16)


class TestSigmaBrLeptonic:
    def test_positive(self):
        assert sigma_br_leptonic(5.0) > 0.0

    def test_higher_mass_lower_xsec(self):
        assert sigma_br_leptonic(5.0) > sigma_br_leptonic(10.0)

    def test_higher_k_tilde_higher_xsec(self):
        assert sigma_br_leptonic(5.0, k_tilde=0.1) > sigma_br_leptonic(5.0, k_tilde=0.05)

    def test_k_tilde_scaling(self):
        # Should scale as (k_tilde/k_ref)^2
        s1 = sigma_br_leptonic(5.0, k_tilde=0.1)
        s2 = sigma_br_leptonic(5.0, k_tilde=0.05)
        ratio = s1 / s2
        assert abs(ratio - 4.0) < 0.1  # (0.1/0.05)^2 = 4

    def test_invalid_mass_raises(self):
        with pytest.raises(ValueError):
            sigma_br_leptonic(0.0)

    def test_bessel_correction_applied(self):
        s_with = sigma_br_leptonic(5.0, bessel_corr=0.876)
        s_without = sigma_br_leptonic(5.0, bessel_corr=1.0)
        assert s_with < s_without

    def test_at_ref_point(self):
        # At reference (k̃=0.1, M=2 TeV), should give ~A = 1.0 fb × bessel²
        s = sigma_br_leptonic(2.0, k_tilde=0.1)
        expected = 1.0 * (0.876 ** 2)
        assert abs(s - expected) < 0.01


class TestExclusionReach:
    def test_3000_fb_larger_than_300_fb(self):
        assert exclusion_reach(3000.0) > exclusion_reach(300.0)

    def test_positive_result(self):
        assert exclusion_reach(300.0) > 0.0

    def test_scales_with_luminosity(self):
        r1 = exclusion_reach(300.0)
        r2 = exclusion_reach(3000.0)
        # Higher luminosity → higher reach
        assert r2 > r1


class TestCurrentLimitComparison:
    def test_consistent_with_atlas(self):
        result = current_limit_comparison(M_KK_BOUND_TEV)
        assert result['consistent_with_atlas']

    def test_consistent_with_cms(self):
        result = current_limit_comparison(M_KK_BOUND_TEV)
        assert result['consistent_with_cms']

    def test_safety_margins_positive(self):
        result = current_limit_comparison(M_KK_BOUND_TEV)
        assert result['safety_margin_atlas_tev'] > 0.0
        assert result['safety_margin_cms_tev'] > 0.0

    def test_verdict_consistent(self):
        result = current_limit_comparison(M_KK_BOUND_TEV)
        assert result['verdict'] == 'CONSISTENT'

    def test_below_atlas_gives_tension(self):
        result = current_limit_comparison(1.5)
        assert result['verdict'] == 'IN_TENSION'


class TestRun4PredictionTable:
    def setup_method(self):
        self.table = run4_prediction_table()

    def test_returns_list(self):
        assert isinstance(self.table, list)

    def test_has_six_points(self):
        assert len(self.table) == 6

    def test_first_mass(self):
        assert self.table[0]['m_kk_tev'] == pytest.approx(5.0)

    def test_last_mass(self):
        assert self.table[-1]['m_kk_tev'] == pytest.approx(10.0)

    def test_xsec_decreasing(self):
        for i in range(len(self.table) - 1):
            k = 'sigma_br_fb_ktilde_0p10'
            assert self.table[i][k] > self.table[i+1][k]

    def test_row_has_all_k_tildes(self):
        row = self.table[0]
        for key_frag in ['0p01', '0p05', '0p10']:
            assert any(key_frag in k for k in row.keys())


class TestPreregistrationHashVerify:
    def test_returns_dict(self):
        result = preregistration_hash_verify()
        assert isinstance(result, dict)

    def test_verified(self):
        result = preregistration_hash_verify()
        assert result['status'] == 'VERIFIED'

    def test_hash_matches(self):
        result = preregistration_hash_verify()
        assert result['sha256_hash'] == PREREGISTRATION_HASH


class TestFalsificationRouting:
    def test_at_bound_is_pass(self):
        result = falsification_routing(M_KK_BOUND_TEV)
        assert result['verdict'] == 'PASS'

    def test_above_bound_is_pass(self):
        result = falsification_routing(6.0)
        assert result['verdict'] == 'PASS'

    def test_below_bound_is_tension(self):
        result = falsification_routing(4.0)
        assert result['verdict'] == 'TENSION'

    def test_well_below_atlas_is_falsified(self):
        result = falsification_routing(1.0)
        assert result['verdict'] == 'FALSIFIED'

    def test_required_keys(self):
        result = falsification_routing(5.0)
        for key in ['verdict', 'condition', 'm_kk_observed_tev', 'um_bound_tev']:
            assert key in result


class TestHllhcPredictionPackage:
    def setup_method(self):
        self.pkg = hllhc_prediction_package()

    def test_returns_dict(self):
        assert isinstance(self.pkg, dict)

    def test_pillar_number(self):
        assert self.pkg['pillar'] == 435

    def test_status(self):
        assert self.pkg['status'] == 'HLLHC_PREDICTION_PREREGISTERED'

    def test_um_bound(self):
        assert self.pkg['um_bound']['mass_tev'] == pytest.approx(5.0)

    def test_current_limits_consistent(self):
        assert self.pkg['current_limits']['verdict'] == 'CONSISTENT'

    def test_hl_lhc_reach(self):
        reach = self.pkg['hl_lhc_reach']
        assert reach['3000_fb'] > reach['300_fb']

    def test_table_not_empty(self):
        assert len(self.pkg['prediction_table']) > 0

    def test_preregistration_verified(self):
        assert self.pkg['preregistration']['status'] == 'VERIFIED'
