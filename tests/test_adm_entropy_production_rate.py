# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 107 — ADM 3+1 Quantitative Entropy Production Rate."""

import numpy as np
import pytest
from src.core.adm_entropy_production_rate import (
    adm_entropy_rate,
    adm_K_trace_from_evolution,
    adm_entropy_rate_cosmological,
    adm_second_law_check,
    adm_entropy_production_tensor,
    quantitative_aot_closure,
    PHI_0, H_0_PLANCK, G_NEWTON,
)


# ---------------------------------------------------------------------------
# adm_entropy_rate — core formula
# ---------------------------------------------------------------------------

class TestAdmEntropyRate:
    def test_positive_for_expanding(self):
        """dS/dt > 0 for expanding universe (K > 0, phi > 0)."""
        assert adm_entropy_rate(1.0, 1.0, 1.0) > 0.0

    def test_zero_when_K_zero(self):
        """dS/dt = 0 in flat static space (K = 0)."""
        assert adm_entropy_rate(31.4, 0.0, 100.0) == 0.0

    def test_zero_when_phi_zero(self):
        """dS/dt = 0 when dilaton vanishes."""
        assert adm_entropy_rate(0.0, 1.0, 100.0) == 0.0

    def test_formula_exact(self):
        """dS/dt = phi * K * A / (4G)."""
        phi, K, A, G = 2.0, 3.0, 5.0, 1.0
        expected = phi * K * A / (4.0 * G)
        assert abs(adm_entropy_rate(phi, K, A, G) - expected) < 1e-14

    def test_proportional_to_phi(self):
        r1 = adm_entropy_rate(1.0, 2.0, 10.0)
        r2 = adm_entropy_rate(3.0, 2.0, 10.0)
        assert abs(r2 / r1 - 3.0) < 1e-12

    def test_proportional_to_K(self):
        r1 = adm_entropy_rate(5.0, 1.0, 10.0)
        r2 = adm_entropy_rate(5.0, 4.0, 10.0)
        assert abs(r2 / r1 - 4.0) < 1e-12

    def test_proportional_to_area(self):
        r1 = adm_entropy_rate(5.0, 2.0, 1.0)
        r2 = adm_entropy_rate(5.0, 2.0, 7.0)
        assert abs(r2 / r1 - 7.0) < 1e-12

    def test_inverse_proportional_to_G(self):
        r1 = adm_entropy_rate(5.0, 2.0, 10.0, G_4=1.0)
        r2 = adm_entropy_rate(5.0, 2.0, 10.0, G_4=2.0)
        assert abs(r1 / r2 - 2.0) < 1e-12

    def test_phi0_canonical(self):
        """With phi_0 = 10pi, K=1, A=1, G=1: rate = phi_0/4."""
        rate = adm_entropy_rate(PHI_0, 1.0, 1.0, 1.0)
        assert abs(rate - PHI_0 / 4.0) < 1e-12

    def test_negative_K_contracting(self):
        """Contracting space (K < 0) gives negative rate — entropy decreases."""
        rate = adm_entropy_rate(1.0, -1.0, 100.0)
        assert rate < 0.0


# ---------------------------------------------------------------------------
# adm_K_trace_from_evolution
# ---------------------------------------------------------------------------

class TestAdmKTrace:
    def test_constant_phi_K_zero(self):
        """K = 0 for constant phi (static field)."""
        t = np.linspace(0, 1, 50)
        phi = np.ones(50) * 31.4
        K = adm_K_trace_from_evolution(phi, t)
        assert abs(K) < 1e-8

    def test_exponential_growth(self):
        """phi = A exp(a t) => K = -3 * d/dt ln(phi) = -3a (returned as 3a for expanding)."""
        t = np.linspace(0, 1, 200)
        a = 0.5
        phi = np.exp(a * t)
        K = adm_K_trace_from_evolution(phi, t)
        # K_trace = -3 * a (in this convention: K ~ -3 * d_t ln phi)
        # For growing phi, d_t ln phi = a > 0, so K = -3a < 0
        assert abs(K - (-3.0 * a)) < 0.05  # allow 5% numerical gradient error

    def test_needs_two_points(self):
        with pytest.raises(ValueError):
            adm_K_trace_from_evolution([1.0], [0.0])

    def test_returns_float(self):
        t = np.linspace(0, 1, 10)
        phi = np.ones(10)
        assert isinstance(adm_K_trace_from_evolution(phi, t), float)


# ---------------------------------------------------------------------------
# adm_entropy_rate_cosmological
# ---------------------------------------------------------------------------

class TestAdmEntropyRateCosmological:
    def setup_method(self):
        self.result = adm_entropy_rate_cosmological()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_positive_dS_dt(self):
        assert self.result['dS_dt'] > 0.0

    def test_positive_S_current(self):
        assert self.result['S_current'] > 0.0

    def test_positive_entropy_increase_per_Gyr(self):
        assert self.result['entropy_increase_per_Gyr'] > 0.0

    def test_K_trace_is_3H(self):
        assert abs(self.result['K_trace'] - 3.0 * H_0_PLANCK) < 1e-30

    def test_A_horizon_formula(self):
        expected_A = 4.0 * np.pi / H_0_PLANCK**2
        assert abs(self.result['A_horizon'] - expected_A) / expected_A < 1e-10

    def test_dS_dt_formula(self):
        """dS/dt = phi_0 * 3H * A / 4G = 3pi*phi_0 / (G*H_0)."""
        expected = 3.0 * np.pi * PHI_0 / (G_NEWTON * H_0_PLANCK)
        assert abs(self.result['dS_dt'] - expected) / expected < 1e-10

    def test_has_all_keys(self):
        for key in ('dS_dt', 'S_current', 'entropy_increase_per_Gyr', 'K_trace', 'A_horizon'):
            assert key in self.result

    def test_custom_phi(self):
        r = adm_entropy_rate_cosmological(phi_0=10.0)
        assert r['dS_dt'] > 0.0

    def test_larger_phi_larger_rate(self):
        r1 = adm_entropy_rate_cosmological(phi_0=1.0)
        r2 = adm_entropy_rate_cosmological(phi_0=2.0)
        assert r2['dS_dt'] > r1['dS_dt']


# ---------------------------------------------------------------------------
# adm_second_law_check
# ---------------------------------------------------------------------------

class TestAdmSecondLawCheck:
    def test_constant_phi_second_law(self):
        """Static phi => K≈0 => dS/dt≈0; second law holds (within numerical noise)."""
        t = np.linspace(0, 2, 50)
        phi = np.ones(50) * 5.0
        result = adm_second_law_check(phi, t)
        # Rates should be ≈0; allow tiny float noise from np.gradient
        assert abs(result['mean_rate']) < 1e-6

    def test_returns_rates_array(self):
        t = np.linspace(0, 1, 20)
        phi = np.ones(20) * 3.0
        result = adm_second_law_check(phi, t)
        assert isinstance(result['rates'], np.ndarray)
        assert len(result['rates']) == 20

    def test_has_keys(self):
        t = np.linspace(0, 1, 10)
        phi = np.ones(10)
        result = adm_second_law_check(phi, t)
        for key in ('all_positive', 'min_rate', 'mean_rate', 'rates'):
            assert key in result


# ---------------------------------------------------------------------------
# adm_entropy_production_tensor
# ---------------------------------------------------------------------------

class TestAdmEntropyProductionTensor:
    def test_shape(self):
        gamma = np.eye(3)
        K_ij = np.eye(3)
        T = adm_entropy_production_tensor(gamma, K_ij, 1.0, 1.0)
        assert T.shape == (3, 3)

    def test_scalar_rate_consistency(self):
        """Trace of T * A ~ scalar rate (up to normalisation)."""
        gamma = np.eye(3)
        K_trace = 1.5
        K_ij = np.eye(3) * (K_trace / 3.0)
        N, phi = 1.0, 2.0
        T = adm_entropy_production_tensor(gamma, K_ij, N, phi)
        trace_T = np.trace(T)
        # trace = N * phi * K_trace / (4G)
        expected = N * phi * K_trace / 4.0
        assert abs(trace_T - expected) < 1e-12

    def test_proportional_to_N_phi(self):
        gamma = np.eye(3)
        K_ij = np.eye(3)
        T1 = adm_entropy_production_tensor(gamma, K_ij, 1.0, 1.0)
        T2 = adm_entropy_production_tensor(gamma, K_ij, 2.0, 3.0)
        # T2 = 6 * T1
        assert np.allclose(T2, 6.0 * T1)

    def test_zero_K_zero_T(self):
        gamma = np.eye(3)
        K_ij = np.zeros((3, 3))
        T = adm_entropy_production_tensor(gamma, K_ij, 1.0, 1.0)
        assert np.allclose(T, 0.0)


# ---------------------------------------------------------------------------
# quantitative_aot_closure — G1 closure
# ---------------------------------------------------------------------------

class TestQuantitativeAotClosure:
    def setup_method(self):
        self.result = quantitative_aot_closure()

    def test_gap_closed(self):
        assert self.result['gap_closed'] is True

    def test_status(self):
        assert self.result['status'] == 'QUANTITATIVE_CLOSURE'

    def test_pillar(self):
        assert self.result['pillar'] == 107

    def test_gap_id(self):
        assert self.result['gap_id'] == 'G1'

    def test_rate_positive(self):
        assert self.result['rate'] > 0.0

    def test_has_formula(self):
        assert 'dS/dt' in self.result['formula']

    def test_has_description(self):
        assert 'ADM' in self.result['description']

    def test_S_current_positive(self):
        assert self.result['S_current'] > 0.0

    def test_entropy_increase_positive(self):
        assert self.result['entropy_increase_per_Gyr'] > 0.0
