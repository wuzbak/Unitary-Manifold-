# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 426 — B_μ Gluon Channel Exact Amplitude."""
import math
import pytest

from src.core.pillar426_bmu_gluon_amplitude import (
    PILLAR_STATUS,
    C1_BARE,
    C1_BENCHMARK,
    M_KK_TEV,
    PHI_STAR,
    SIGMA_RATIO_BARE,
    compute_z_gg,
    compute_c1_eff,
    compute_sigma_ratio,
    gluon_channel_at_mass,
    gluon_channel_scan,
    bmu_gluon_verdict,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'GLUON_CHANNEL_BMU_CORRECTED_EXACT'

    def test_c1_bare_positive(self):
        assert C1_BARE > 0.0

    def test_c1_bare_value(self):
        assert abs(C1_BARE - 1.31) < 0.01

    def test_c1_benchmark(self):
        assert abs(C1_BENCHMARK - 0.1) < 1e-6

    def test_m_kk_tev(self):
        assert 0.5 < M_KK_TEV < 2.0

    def test_phi_star_approx(self):
        assert abs(PHI_STAR - 2.0 * math.pi * 5) < 1e-8

    def test_sigma_ratio_bare_large(self):
        assert SIGMA_RATIO_BARE > 10.0


class TestComputeZGg:
    def test_returns_at_least_one(self):
        assert compute_z_gg(M_KK_TEV) >= 1.0

    def test_increases_with_mass(self):
        z1 = compute_z_gg(1.8)
        z2 = compute_z_gg(3.98)
        assert z2 > z1

    def test_at_first_kk_mode(self):
        # Z_gg should be >> 1 for m_G_KK = 3.98 TeV
        z = compute_z_gg(3.98)
        assert z > 1000

    def test_explicit_value_at_kk_scale(self):
        # At m_G_KK = M_KK: Z_gg = 1 + φ*² * (1.0)²
        z = compute_z_gg(M_KK_TEV, m_kk_tev=M_KK_TEV)
        assert abs(z - (1 + PHI_STAR**2)) < 1.0


class TestComputeC1Eff:
    def test_returns_positive(self):
        assert compute_c1_eff(3.98) > 0.0

    def test_smaller_than_bare(self):
        # B_μ correction always suppresses
        assert compute_c1_eff(3.98) < C1_BARE

    def test_suppression_increases_with_mass(self):
        c1_low = compute_c1_eff(1.8)
        c1_high = compute_c1_eff(3.98)
        assert c1_low > c1_high

    def test_value_at_first_kk_mode(self):
        c1 = compute_c1_eff(3.98)
        # Should be order 0.01
        assert 0.001 < c1 < 0.1


class TestComputeSigmaRatio:
    def test_returns_positive(self):
        assert compute_sigma_ratio(3.98) > 0.0

    def test_above_unity_at_first_kk_mode(self):
        # gluon channel is still in tension
        sigma = compute_sigma_ratio(3.98)
        assert sigma > 1.0

    def test_smaller_than_bare(self):
        # B_μ correction reduces cross-section ratio
        assert compute_sigma_ratio(3.98) < SIGMA_RATIO_BARE

    def test_larger_at_lower_mass(self):
        # Lower mass → smaller Z_gg → larger sigma_ratio
        # Wait, lower mass → smaller mass_ratio_sq → smaller Z_gg → larger c1_eff → larger sigma_ratio
        s_low = compute_sigma_ratio(1.8)
        s_high = compute_sigma_ratio(3.98)
        # At lower mass: less suppression → larger sigma_ratio
        # But sigma_ratio = (c1_eff/c1_benchmark)^2 * sigma_bare
        # c1_eff at lower mass is larger → larger sigma_ratio
        assert s_low > s_high


class TestGluonChannelAtMass:
    def test_returns_dict(self):
        assert isinstance(gluon_channel_at_mass(3.98), dict)

    @pytest.mark.parametrize('key', ['m_gkk_tev', 'z_gg', 'c1_bare', 'c1_eff',
                                     'c1_benchmark', 'sigma_ratio', 'above_lhc_benchmark', 'verdict'])
    def test_expected_keys(self, key):
        assert key in gluon_channel_at_mass(3.98)

    def test_at_3p98_tev_in_tension(self):
        result = gluon_channel_at_mass(3.98)
        assert result['verdict'] == 'IN_TENSION'

    def test_at_3p98_above_benchmark(self):
        result = gluon_channel_at_mass(3.98)
        assert result['above_lhc_benchmark'] is True

    def test_z_gg_large_at_3p98(self):
        result = gluon_channel_at_mass(3.98)
        assert result['z_gg'] > 1000


class TestGluonChannelScan:
    def test_returns_list(self):
        assert isinstance(gluon_channel_scan(), list)

    def test_returns_at_least_four_entries(self):
        assert len(gluon_channel_scan()) >= 4

    @pytest.mark.parametrize('idx', [0, 1, 2])
    def test_each_has_sigma_ratio(self, idx):
        scan = gluon_channel_scan()
        assert 'sigma_ratio' in scan[idx]

    def test_sigma_ratio_decreasing_with_mass(self):
        scan = gluon_channel_scan()
        # Higher mass → more suppression → smaller sigma_ratio
        # sigma ratios should decrease as mass increases
        ratios = [e['sigma_ratio'] for e in scan]
        # This should be monotonically... wait:
        # At higher mass: larger Z_gg → smaller c1_eff → smaller sigma_ratio
        # Actually at lower mass: smaller Z_gg → larger c1_eff → larger sigma_ratio
        assert ratios[0] > ratios[-1]


class TestBmuGluonVerdict:
    def test_returns_dict(self):
        assert isinstance(bmu_gluon_verdict(), dict)

    def test_status(self):
        assert bmu_gluon_verdict()['status'] == 'GLUON_CHANNEL_BMU_CORRECTED_EXACT'

    @pytest.mark.parametrize('key', ['at_first_kk_mode', 'at_lhc_lower_bound',
                                     'scan', 'c1_bare', 'verdict', 'honest_caveat'])
    def test_expected_keys(self, key):
        assert key in bmu_gluon_verdict()

    def test_first_kk_mode_in_tension(self):
        verdict = bmu_gluon_verdict()
        assert verdict['at_first_kk_mode']['verdict'] == 'IN_TENSION'

    def test_verdict_is_string(self):
        assert isinstance(bmu_gluon_verdict()['verdict'], str)

    def test_honest_caveat_present(self):
        caveat = bmu_gluon_verdict()['honest_caveat']
        assert len(caveat) > 50
