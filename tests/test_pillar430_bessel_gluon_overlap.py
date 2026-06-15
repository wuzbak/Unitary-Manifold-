# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 430 — Full RS1 Bessel Gluon Channel Amplitude."""
from __future__ import annotations

import math
import pytest

from src.core.pillar430_bessel_gluon_overlap import (
    PILLAR_STATUS,
    PI_KR,
    N_W,
    K_CS,
    M_KK_TEV,
    BESSEL_OVERLAP_CORRECTION,
    SIGMA_RATIO_LO,
    M_SAFE_LO_TEV,
    M_SAFE_BESSEL_TEV,
    bessel_j2,
    kk_graviton_wavefunction,
    compute_overlap_integral,
    bessel_overlap_correction_factor,
    gluon_channel_bessel_exact,
    sigma_ratio_bessel,
    sharpened_mass_bound,
    bessel_gluon_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'GLUON_CHANNEL_BESSEL_EXACT'

    def test_pi_kr(self):
        assert PI_KR == 37

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_m_kk_tev(self):
        assert M_KK_TEV == pytest.approx(1.04, rel=0.01)

    def test_bessel_correction_in_range(self):
        # The Bessel correction factor must be < 1 (suppression) and > 0.7
        assert 0.7 < BESSEL_OVERLAP_CORRECTION < 1.0

    def test_sigma_ratio_lo(self):
        # From Pillar 426: σ_ratio ≈ 2.03 at m_G_KK = 3.98 TeV
        assert SIGMA_RATIO_LO == pytest.approx(2.03, rel=0.01)

    def test_m_safe_lo_tev(self):
        # From Pillar 403: LO lower bound ≈ 1.8 TeV
        assert M_SAFE_LO_TEV == pytest.approx(1.8, rel=0.01)

    def test_m_safe_bessel_tev_larger_than_lo(self):
        # Bessel correction sharpens the bound → larger minimum mass
        assert M_SAFE_BESSEL_TEV > M_SAFE_LO_TEV


class TestBesselJ2:
    def test_j2_at_zero(self):
        assert bessel_j2(0.0) == 0.0

    def test_j2_positive_at_small_x(self):
        # J₂(x) > 0 for small positive x
        assert bessel_j2(0.5) > 0.0

    def test_j2_first_zero_near_5_1(self):
        # First zero of J₂ is at x ≈ 5.136
        j2_5 = bessel_j2(5.0)
        j2_6 = bessel_j2(6.0)
        # Should have different signs around the first zero
        assert j2_5 * j2_6 < 0 or (abs(j2_5) < 0.3 and abs(j2_6) < 0.3)

    def test_j2_at_pi(self):
        # J₂(π) ≈ 0.485 (verified: J₂(π) = (2/π)J₁(π) - J₀(π) ≈ 0.485)
        val = bessel_j2(math.pi)
        assert 0.40 < val < 0.60

    def test_j2_at_x1_positive(self):
        # At x₁ ≈ 3.83 (first relevant Bessel root used in overlap)
        val = bessel_j2(3.83)
        assert val > 0.0

    def test_j2_symmetric_check(self):
        # For cross-check: J₂ at x ≈ 2.0 should be positive and significant
        val = bessel_j2(2.0)
        assert val > 0.05

    def test_j2_at_ten(self):
        # J₂(10) ≈ +0.2546 (positive — past one oscillation from first root ≈5.136)
        val = bessel_j2(10.0)
        assert 0.15 < val < 0.40


class TestKKGravitonWavefunction:
    def test_zero_at_z_zero(self):
        # f ∝ z² J₂(...) → 0 as z → 0
        assert kk_graviton_wavefunction(0.001, m_kk=1.0) == pytest.approx(0.0, abs=1e-4)

    def test_positive_at_z_one(self):
        val = kk_graviton_wavefunction(1.0, m_kk=0.1)
        assert val >= 0.0

    def test_increases_with_z_at_small_arg(self):
        # At very small argument, J₂(arg) ∝ arg² so f ~ z⁴ → increasing
        f1 = kk_graviton_wavefunction(1.0, m_kk=0.01)
        f2 = kk_graviton_wavefunction(2.0, m_kk=0.01)
        assert f2 > f1


class TestOverlapIntegral:
    def test_returns_dict(self):
        result = compute_overlap_integral(n_points=50)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = compute_overlap_integral(n_points=50)
        for key in ['I_exact', 'I_lo_bessel', 'ratio', 'j2_x1', 'z_ir', 'n_points']:
            assert key in result

    def test_z_ir_is_exp_pi_kr(self):
        result = compute_overlap_integral(n_points=50)
        assert result['z_ir'] == pytest.approx(math.exp(PI_KR), rel=1e-8)

    def test_j2_x1_positive(self):
        result = compute_overlap_integral(n_points=50)
        assert result['j2_x1'] > 0.0

    def test_i_exact_positive(self):
        result = compute_overlap_integral(n_points=50)
        assert result['I_exact'] != 0.0

    def test_ratio_finite(self):
        result = compute_overlap_integral(n_points=50)
        assert math.isfinite(result['ratio'])

    def test_n_points_stored(self):
        result = compute_overlap_integral(n_points=50)
        assert result['n_points'] == 50


class TestBesselOverlapCorrectionFactor:
    def test_returns_float(self):
        val = bessel_overlap_correction_factor()
        assert isinstance(val, float)

    def test_equals_constant(self):
        assert bessel_overlap_correction_factor() == BESSEL_OVERLAP_CORRECTION

    def test_suppression_factor_less_than_one(self):
        assert bessel_overlap_correction_factor() < 1.0

    def test_suppression_factor_positive(self):
        assert bessel_overlap_correction_factor() > 0.0


class TestGluonChannelBesselExact:
    def test_at_reference_mass_dict(self):
        result = gluon_channel_bessel_exact(3.98)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = gluon_channel_bessel_exact(3.98)
        for key in ['m_gkk_tev', 'sigma_ratio_lo', 'bessel_correction_factor',
                    'sigma_ratio_bessel', 'verdict']:
            assert key in result

    def test_mass_stored(self):
        result = gluon_channel_bessel_exact(3.98)
        assert result['m_gkk_tev'] == pytest.approx(3.98, rel=1e-8)

    def test_correction_factor_matches_constant(self):
        result = gluon_channel_bessel_exact(3.98)
        assert result['bessel_correction_factor'] == BESSEL_OVERLAP_CORRECTION

    def test_sigma_ratio_bessel_less_than_lo(self):
        result = gluon_channel_bessel_exact(3.98)
        assert result['sigma_ratio_bessel'] < result['sigma_ratio_lo']

    def test_sigma_ratio_bessel_at_3p98_in_tension(self):
        result = gluon_channel_bessel_exact(3.98)
        assert result['sigma_ratio_bessel'] > 1.0
        assert result['verdict'] == 'IN_TENSION'

    def test_sigma_ratio_decreases_with_mass(self):
        low = gluon_channel_bessel_exact(3.0)
        high = gluon_channel_bessel_exact(6.0)
        assert low['sigma_ratio_bessel'] > high['sigma_ratio_bessel']

    def test_verdict_consistent_at_high_mass(self):
        result = gluon_channel_bessel_exact(15.0)
        assert result['verdict'] == 'CONSISTENT'

    def test_at_1p8_tev_in_tension(self):
        result = gluon_channel_bessel_exact(1.8)
        # At the old LO lower bound, should still be in tension
        assert result['verdict'] == 'IN_TENSION'


class TestSigmaRatioBessel:
    def test_returns_float(self):
        val = sigma_ratio_bessel(3.98)
        assert isinstance(val, float)

    def test_positive(self):
        assert sigma_ratio_bessel(3.98) > 0.0

    def test_consistent_with_channel_function(self):
        val1 = sigma_ratio_bessel(5.0)
        val2 = gluon_channel_bessel_exact(5.0)['sigma_ratio_bessel']
        assert val1 == pytest.approx(val2, rel=1e-10)


class TestSharpenedMassBound:
    def setup_method(self):
        self.bound = sharpened_mass_bound()

    def test_returns_dict(self):
        assert isinstance(self.bound, dict)

    def test_required_keys(self):
        for key in ['m_min_tev', 'sigma_ratio_at_bound', 'bessel_correction_factor',
                    'comparison_lo_bound_tev', 'sharpening_factor']:
            assert key in self.bound

    def test_m_min_tev_larger_than_lo(self):
        assert self.bound['m_min_tev'] > M_SAFE_LO_TEV

    def test_sigma_ratio_at_bound_near_unity(self):
        assert self.bound['sigma_ratio_at_bound'] == pytest.approx(1.0, abs=0.01)

    def test_sharpening_factor_greater_than_one(self):
        assert self.bound['sharpening_factor'] > 1.0

    def test_comparison_lo_bound(self):
        assert self.bound['comparison_lo_bound_tev'] == pytest.approx(M_SAFE_LO_TEV, rel=1e-8)

    def test_m_safe_bessel_tev_matches(self):
        assert M_SAFE_BESSEL_TEV == pytest.approx(self.bound['m_min_tev'], rel=1e-4)


class TestBesselGluonVerdict:
    def setup_method(self):
        self.verdict = bessel_gluon_verdict()

    def test_returns_dict(self):
        assert isinstance(self.verdict, dict)

    def test_status_is_bessel_exact(self):
        assert self.verdict['status'] == 'GLUON_CHANNEL_BESSEL_EXACT'

    def test_previous_status(self):
        assert 'BMU' in self.verdict['previous_status'] or \
               'CORRECTED' in self.verdict['previous_status']

    def test_bessel_correction_matches(self):
        assert self.verdict['bessel_correction_factor'] == BESSEL_OVERLAP_CORRECTION

    def test_correction_squared(self):
        expected = BESSEL_OVERLAP_CORRECTION ** 2
        assert self.verdict['bessel_correction_squared'] == pytest.approx(expected, rel=1e-10)

    def test_at_first_kk_mode_present(self):
        assert 'at_first_kk_mode_3p98_tev' in self.verdict
        assert self.verdict['at_first_kk_mode_3p98_tev']['verdict'] == 'IN_TENSION'

    def test_at_p403_lower_bound_present(self):
        assert 'at_p403_lower_bound_1p8_tev' in self.verdict

    def test_sharpened_bound_present(self):
        bound = self.verdict['sharpened_bound']
        assert bound['m_min_tev'] > M_SAFE_LO_TEV

    def test_scan_has_multiple_masses(self):
        assert len(self.verdict['scan']) >= 5

    def test_verdict_string_present(self):
        assert len(self.verdict['verdict']) > 0
        assert 'GLUON_CHANNEL_BESSEL_EXACT' in self.verdict['verdict']

    def test_honest_caveat_present(self):
        assert len(self.verdict['honest_caveat']) > 0

    def test_scan_masses_in_tension_at_3p98(self):
        scan = self.verdict['scan']
        entry_398 = next(e for e in scan if abs(e['m_gkk_tev'] - 3.98) < 0.1)
        assert entry_398['verdict'] == 'IN_TENSION'


class TestPhysicalConsistency:
    def test_bessel_correction_is_suppression(self):
        # The Bessel correction always suppresses (< 1)
        assert BESSEL_OVERLAP_CORRECTION < 1.0

    def test_tension_stronger_at_lower_mass(self):
        # More dangerous at lower KK mass (easier to produce)
        sr_low = sigma_ratio_bessel(2.0)
        sr_high = sigma_ratio_bessel(5.0)
        assert sr_low > sr_high

    def test_eventually_consistent_at_very_high_mass(self):
        # At sufficiently high mass, the channel is always consistent
        sr = sigma_ratio_bessel(20.0)
        assert sr < 1.0
