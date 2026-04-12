"""
test_claim.py — Tests validating the anomaly_inflow claim: the 5D bulk CS term
uniquely generates the axion-photon coupling g_aγγ that reproduces β ≈ 0.35°.

Run from the repository root:
    python -m pytest claims/anomaly_inflow/test_claim.py -v
"""
import math
import sys
sys.path.insert(0, ".")

import pytest
from src.core.inflation import (
    cs_axion_photon_coupling,
    birefringence_angle,
    CS_LEVEL_PLANCK_MATCH,
)

ALPHA_EM    = 1 / 137.036
R_C         = 12.0
DELTA_PHI   = 5.38
BETA_TARGET = 0.35   # degrees, Minami & Komatsu / Diego-Palazuelos
BETA_1SIGMA = 0.14   # degrees, 1σ observational uncertainty


class TestAnomalyInflow:
    """5D bulk CS anomaly inflow chain: k_CS → g_aγγ → β."""

    def test_coupling_formula_correct(self):
        """g_aγγ = k_CS · α_EM / (2π² r_c) — the formula is correctly coded.

        DELETE-POWER TEST: change the volume factor (2π²) and this fails.
        """
        g_agg    = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        expected = CS_LEVEL_PLANCK_MATCH * ALPHA_EM / (2.0 * math.pi**2 * R_C)
        assert abs(g_agg - expected) / expected < 1e-10, (
            f"g_aγγ = {g_agg:.8e}, expected {expected:.8e}. Formula changed."
        )

    def test_coupling_value_stable(self):
        """g_aγγ(k=74) ≈ 2.28 × 10⁻³ (code-verified)."""
        g_agg = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        assert abs(g_agg - 2.280e-3) / 2.280e-3 < 0.01, (
            f"g_aγγ = {g_agg:.4e}, expected ≈ 2.280e-3. Code changed — update claim."
        )

    def test_beta_within_observational_window(self):
        """β(k=74) is within the 1σ observational window (0.35 ± 0.14°).

        DELETE-POWER TEST: alter cs_axion_photon_coupling() or birefringence_angle()
        and this fails.
        """
        g_agg    = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        beta_deg = math.degrees(birefringence_angle(g_agg, DELTA_PHI))
        assert abs(beta_deg - BETA_TARGET) <= BETA_1SIGMA, (
            f"β(k=74) = {beta_deg:.4f}°, which is outside the 1σ window "
            f"[{BETA_TARGET - BETA_1SIGMA:.2f}°, {BETA_TARGET + BETA_1SIGMA:.2f}°]."
        )

    def test_zero_anomaly_gives_wrong_beta(self):
        """k_CS = 1 (no anomaly inflow) does not reproduce β ≈ 0.35°.

        DELETE-POWER TEST: if the formula degenerates so that k_CS=1 gives β≈0.35°,
        the integer derivation is not constraining.
        """
        g_k1     = cs_axion_photon_coupling(1, ALPHA_EM, R_C)
        beta_k1  = math.degrees(birefringence_angle(g_k1, DELTA_PHI))
        assert abs(beta_k1 - BETA_TARGET) > BETA_1SIGMA, (
            f"k_CS=1 unexpectedly gives β = {beta_k1:.4f}° ≈ {BETA_TARGET}°. "
            "The coupling formula is not constraining — anomaly inflow claim broken."
        )

    def test_coupling_scales_linearly_with_k(self):
        """g_aγγ ∝ k_CS — the coupling is linear in the CS charge.

        DELETE-POWER TEST: add a k-independent additive constant and this fails.
        """
        g_74 = cs_axion_photon_coupling(74, ALPHA_EM, R_C)
        g_37 = cs_axion_photon_coupling(37, ALPHA_EM, R_C)
        ratio = g_74 / g_37
        assert abs(ratio - 2.0) < 1e-8, (
            f"g(74)/g(37) = {ratio:.8f}, expected 2.0 exactly. "
            "Linear k-scaling broken — anomaly inflow is not topological."
        )

    def test_coupling_scales_inversely_with_rc(self):
        """g_aγγ ∝ 1/r_c — doubling r_c halves the coupling."""
        g_rc1  = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
        g_rc2  = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, 2 * R_C)
        assert abs(g_rc1 / g_rc2 - 2.0) < 1e-8, (
            f"g(r_c)/g(2r_c) = {g_rc1/g_rc2:.8f}, expected 2.0."
        )
