"""
test_claim.py — Tests that MUST PASS to validate the k_CS=74 derivation claim,
and MUST FAIL if the claim's key assumption is removed.

Run from the repository root:
    python -m pytest claims/integer_derivation/test_claim.py -v
"""
import math
import sys
sys.path.insert(0, ".")

import pytest
from src.core.inflation import (
    cs_level_for_birefringence,
    cs_axion_photon_coupling,
    birefringence_angle,
    CS_LEVEL_PLANCK_MATCH,
)

# Physical constants used in the derivation
BETA_TARGET_DEG = 0.35
ALPHA_EM        = 1 / 137.036
R_C             = 12.0
DELTA_PHI       = 5.38


class TestIntegerDerivation:
    """k_CS = 74 is derived from β = 0.35°, not adjusted post-hoc."""

    def test_continuous_level_near_74(self):
        """The exact (non-integer) k_CS from the formula rounds to 74."""
        k_float = cs_level_for_birefringence(BETA_TARGET_DEG, ALPHA_EM, R_C, DELTA_PHI)
        assert 73.0 < k_float < 74.5, (
            f"Expected k_CS ≈ 73.7, got {k_float:.4f}. "
            "The derivation no longer points to 74."
        )

    def test_rounded_level_equals_constant(self):
        """round(k_continuous) matches CS_LEVEL_PLANCK_MATCH = 74."""
        k_float = cs_level_for_birefringence(BETA_TARGET_DEG, ALPHA_EM, R_C, DELTA_PHI)
        assert round(k_float) == CS_LEVEL_PLANCK_MATCH, (
            f"round({k_float:.4f}) = {round(k_float)}, "
            f"but CS_LEVEL_PLANCK_MATCH = {CS_LEVEL_PLANCK_MATCH}. "
            "Constant or formula has changed."
        )

    def test_cs_level_is_unique_minimiser(self):
        """k=74 uniquely minimises |β(k)−0.35°| over all integers k ∈ [1, 100].

        DELETE-POWER TEST: change CS_LEVEL_PLANCK_MATCH to any other integer,
        or alter cs_axion_photon_coupling(), and this test fails.
        """
        g_74     = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        beta_74  = math.degrees(birefringence_angle(g_74, DELTA_PHI))
        resid_74 = abs(beta_74 - BETA_TARGET_DEG)

        for k in range(1, 101):
            if k == CS_LEVEL_PLANCK_MATCH:
                continue
            g = cs_axion_photon_coupling(k, ALPHA_EM, R_C)
            b = math.degrees(birefringence_angle(g, DELTA_PHI))
            r = abs(b - BETA_TARGET_DEG)
            assert r >= resid_74, (
                f"k={k} gives |β−0.35°| = {r:.6f}° < {resid_74:.6f}° (k=74). "
                "k=74 is NO LONGER the unique minimiser — claim broken."
            )

    def test_back_computed_beta_matches_target(self):
        """β(k=74) ≈ 0.35° to within the observational uncertainty (0.14°)."""
        g_agg    = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        beta_deg = math.degrees(birefringence_angle(g_agg, DELTA_PHI))
        assert abs(beta_deg - BETA_TARGET_DEG) < 0.14, (
            f"β(k=74) = {beta_deg:.4f}° differs from target {BETA_TARGET_DEG}° "
            "by more than the 1-σ observational window (0.14°)."
        )

    def test_neighbouring_integers_give_larger_residual(self):
        """k=73 and k=75 both produce a larger |β−0.35°| than k=74."""
        g_74  = cs_axion_photon_coupling(74, ALPHA_EM, R_C)
        resid_74 = abs(math.degrees(birefringence_angle(g_74, DELTA_PHI)) - BETA_TARGET_DEG)

        for k_neighbour in (73, 75):
            g = cs_axion_photon_coupling(k_neighbour, ALPHA_EM, R_C)
            b = math.degrees(birefringence_angle(g, DELTA_PHI))
            resid = abs(b - BETA_TARGET_DEG)
            assert resid > resid_74, (
                f"k={k_neighbour} residual {resid:.6f}° ≤ k=74 residual "
                f"{resid_74:.6f}°. Uniqueness is not robust."
            )

    def test_wrong_k_fails_beta_match(self):
        """k=1 (no coupling) does not reproduce the birefringence signal."""
        g_k1     = cs_axion_photon_coupling(1, ALPHA_EM, R_C)
        beta_deg = math.degrees(birefringence_angle(g_k1, DELTA_PHI))
        assert abs(beta_deg - BETA_TARGET_DEG) > 0.14, (
            "k=1 unexpectedly reproduces β ≈ 0.35°. The derivation is not constraining."
        )
