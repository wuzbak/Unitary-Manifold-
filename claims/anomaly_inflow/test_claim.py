"""
test_claim.py — Tests validating the anomaly inflow claim.

Run from the repository root:
    python -m pytest claims/anomaly_inflow/test_claim.py -v
"""
import math
import sys

import pytest

sys.path.insert(0, ".")

from src.core.inflation import (
    CS_LEVEL_PLANCK_MATCH,
    birefringence_angle,
    cs_axion_photon_coupling,
)

ALPHA_EM = 1 / 137.036
R_C = 12.0
DELTA_PHI = 5.38
BETA_TARGET = 0.35
BETA_1SIGMA = 0.14


class TestAnomalyInflowIdentityRegression:
    """Identity/regression tests for formula and canonical values."""

    def test_identity_coupling_formula(self):
        g_agg = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        expected = CS_LEVEL_PLANCK_MATCH * ALPHA_EM / (2.0 * math.pi**2 * R_C)
        assert abs(g_agg - expected) / expected < 1e-12

    def test_regression_k74_coupling_value(self):
        g_agg = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        assert abs(g_agg - 2.280e-3) / 2.280e-3 < 0.01

    def test_regression_k74_beta_within_observation(self):
        g_agg = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        beta_deg = math.degrees(birefringence_angle(g_agg, DELTA_PHI))
        assert abs(beta_deg - BETA_TARGET) <= BETA_1SIGMA


class TestAnomalyInflowFalsification:
    """Falsification/discrimination tests."""

    def test_falsification_k1_does_not_match_signal(self):
        g_k1 = cs_axion_photon_coupling(1, ALPHA_EM, R_C)
        beta_k1 = math.degrees(birefringence_angle(g_k1, DELTA_PHI))
        assert abs(beta_k1 - BETA_TARGET) > BETA_1SIGMA

    def test_discrimination_k74_beats_73_and_75(self):
        resid = {}
        for k in (73, 74, 75):
            g = cs_axion_photon_coupling(k, ALPHA_EM, R_C)
            b = math.degrees(birefringence_angle(g, DELTA_PHI))
            resid[k] = abs(b - BETA_TARGET)
        assert resid[74] < resid[73]
        assert resid[74] < resid[75]


class TestAnomalyInflowOracleAndPerturbation:
    """Independent oracles and parameter perturbation sweeps."""

    def test_oracle_beta_bilinear_symmetry(self):
        # β ∝ g * Δφ, so doubling g and halving Δφ preserves β.
        beta_1 = birefringence_angle(0.002, 5.0)
        beta_2 = birefringence_angle(0.004, 2.5)
        assert beta_1 == pytest.approx(beta_2, rel=1e-12)

    def test_oracle_inverse_rc_scaling(self):
        g_6 = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, 6.0)
        g_12 = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, 12.0)
        g_24 = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, 24.0)
        assert g_6 / g_12 == pytest.approx(2.0, rel=1e-12)
        assert g_12 / g_24 == pytest.approx(2.0, rel=1e-12)

    @pytest.mark.parametrize("k", [73, 74, 75])
    def test_perturbation_k_triplet_beta_positive(self, k):
        g = cs_axion_photon_coupling(k, ALPHA_EM, R_C)
        beta = math.degrees(birefringence_angle(g, DELTA_PHI))
        assert beta > 0.0

    @pytest.mark.parametrize("alpha", [1 / 137.0, 1 / 137.036, 1 / 137.1])
    def test_perturbation_alpha_produces_positive_coupling(self, alpha):
        g = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, alpha, R_C)
        assert g > 0.0

    @pytest.mark.parametrize("delta_phi", [4.5, 5.38, 6.2])
    def test_perturbation_delta_phi_preserves_beta_linearity(self, delta_phi):
        g = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        beta = birefringence_angle(g, delta_phi)
        expected = 0.5 * g * abs(delta_phi)
        assert beta == pytest.approx(expected, rel=1e-12)
