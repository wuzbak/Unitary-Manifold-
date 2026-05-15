"""
test_claim.py — Tests validating the k_CS=74 integer derivation claim.

Run from the repository root:
    python -m pytest claims/integer_derivation/test_claim.py -v
"""
import math
import sys

import pytest

sys.path.insert(0, ".")

from src.core.inflation import (
    CS_LEVEL_PLANCK_MATCH,
    birefringence_angle,
    cs_axion_photon_coupling,
    cs_level_for_birefringence,
)

BETA_TARGET_DEG = 0.35
ALPHA_EM = 1 / 137.036
R_C = 12.0
DELTA_PHI = 5.38


class TestIntegerDerivationIdentityRegression:
    """Identity/regression tests for canonical derivation path."""

    def test_continuous_level_near_74(self):
        k_float = cs_level_for_birefringence(BETA_TARGET_DEG, ALPHA_EM, R_C, DELTA_PHI)
        assert 73.0 < k_float < 74.5

    def test_round_level_matches_constant(self):
        k_float = cs_level_for_birefringence(BETA_TARGET_DEG, ALPHA_EM, R_C, DELTA_PHI)
        assert round(k_float) == CS_LEVEL_PLANCK_MATCH

    def test_k74_back_computed_beta_matches_target(self):
        g_agg = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        beta_deg = math.degrees(birefringence_angle(g_agg, DELTA_PHI))
        assert abs(beta_deg - BETA_TARGET_DEG) < 0.14


class TestIntegerDerivationFalsificationExternalDiscrimination:
    """Falsification and external discrimination tests."""

    def test_k74_unique_minimiser_global_scan(self):
        g_74 = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        beta_74 = math.degrees(birefringence_angle(g_74, DELTA_PHI))
        resid_74 = abs(beta_74 - BETA_TARGET_DEG)

        for k in range(1, 101):
            if k == CS_LEVEL_PLANCK_MATCH:
                continue
            g = cs_axion_photon_coupling(k, ALPHA_EM, R_C)
            b = math.degrees(birefringence_angle(g, DELTA_PHI))
            r = abs(b - BETA_TARGET_DEG)
            assert r >= resid_74

    def test_wrong_k_fails_beta_match(self):
        g_k1 = cs_axion_photon_coupling(1, ALPHA_EM, R_C)
        beta_deg = math.degrees(birefringence_angle(g_k1, DELTA_PHI))
        assert abs(beta_deg - BETA_TARGET_DEG) > 0.14

    def test_neighbouring_integers_have_larger_residual(self):
        g_74 = cs_axion_photon_coupling(74, ALPHA_EM, R_C)
        resid_74 = abs(math.degrees(birefringence_angle(g_74, DELTA_PHI)) - BETA_TARGET_DEG)
        for k_neighbour in (73, 75):
            g = cs_axion_photon_coupling(k_neighbour, ALPHA_EM, R_C)
            b = math.degrees(birefringence_angle(g, DELTA_PHI))
            resid = abs(b - BETA_TARGET_DEG)
            assert resid > resid_74


class TestIntegerDerivationOracleAndPerturbation:
    """Independent-oracle and perturbation sweeps."""

    def test_oracle_forward_path_local_minimiser(self):
        residuals = {}
        for k in range(70, 79):
            g = cs_axion_photon_coupling(k, ALPHA_EM, R_C)
            beta = math.degrees(birefringence_angle(g, DELTA_PHI))
            residuals[k] = abs(beta - BETA_TARGET_DEG)
        assert min(residuals, key=residuals.get) == 74

    @pytest.mark.parametrize("k", [73, 74, 75])
    def test_perturbation_k_triplet_positive_beta(self, k):
        g = cs_axion_photon_coupling(k, ALPHA_EM, R_C)
        b = math.degrees(birefringence_angle(g, DELTA_PHI))
        assert b > 0.0

    def test_perturbation_k_triplet_v_shape(self):
        residuals = []
        for k in (73, 74, 75):
            g = cs_axion_photon_coupling(k, ALPHA_EM, R_C)
            b = math.degrees(birefringence_angle(g, DELTA_PHI))
            residuals.append(abs(b - BETA_TARGET_DEG))
        assert residuals[1] < residuals[0]
        assert residuals[1] < residuals[2]

    @pytest.mark.parametrize("r_c_test", [10.0, 12.0, 14.0])
    def test_perturbation_rc_sweep_k74_local_best(self, r_c_test):
        residuals = {}
        for k in (73, 74, 75):
            g = cs_axion_photon_coupling(k, ALPHA_EM, r_c_test)
            b = math.degrees(birefringence_angle(g, DELTA_PHI))
            residuals[k] = abs(b - BETA_TARGET_DEG)
        assert residuals[74] < residuals[73]
        assert residuals[74] < residuals[75]
