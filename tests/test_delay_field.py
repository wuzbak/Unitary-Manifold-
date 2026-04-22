# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
test_delay_field.py — Tests for Pillar 41: 5D Delay Field Model (DFM)

~90 tests covering all public functions in src/core/delay_field.py.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.delay_field import (
    C_S_CANONICAL,
    K_CS_CANONICAL,
    N1_CANONICAL,
    N2_CANONICAL,
    PHI_0_FTUM,
    PHI_STAR,
    braided_delay_spectrum,
    causal_arrow_of_time,
    coord_time_from_ricci,
    decoherence_time,
    delay_from_phi,
    dfm_summary,
    dfm_um_consistency_check,
    entanglement_capacity,
    entropy_production_rate,
    gemini_issue4_correction,
    irreversibility_measure,
    phi_from_delay,
    quantum_delay_variance,
    ricci_flow_time_factor,
    ricci_from_coord_time,
)


# ---------------------------------------------------------------------------
# TestModuleConstants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_phi_0_ftum_is_one(self):
        assert PHI_0_FTUM == 1.0

    def test_phi_star_is_one(self):
        assert PHI_STAR == 1.0

    def test_canonical_braid_n1(self):
        assert N1_CANONICAL == 5

    def test_canonical_braid_n2(self):
        assert N2_CANONICAL == 7

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_c_s_canonical(self):
        assert math.isclose(C_S_CANONICAL, 12.0 / 37.0, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# TestDelayPhiBridge
# ---------------------------------------------------------------------------

class TestDelayPhiBridge:
    def test_delay_from_phi_unity(self):
        assert delay_from_phi(1.0) == 1.0

    def test_delay_from_phi_two(self):
        assert delay_from_phi(2.0) == 4.0

    def test_phi_from_delay_four(self):
        assert math.isclose(phi_from_delay(4.0), 2.0, rel_tol=1e-12)

    def test_round_trip_phi_to_delay_and_back(self):
        for phi in (0.5, 1.0, 1.618, 3.14):
            assert math.isclose(phi_from_delay(delay_from_phi(phi)), phi, rel_tol=1e-12)

    def test_phi_from_delay_zero(self):
        assert phi_from_delay(0.0) == 0.0

    def test_phi_from_delay_negative_raises(self):
        with pytest.raises(ValueError):
            phi_from_delay(-1.0)


# ---------------------------------------------------------------------------
# TestEntanglementCapacity
# ---------------------------------------------------------------------------

class TestEntanglementCapacity:
    def test_entanglement_capacity_equals_phi_squared(self):
        for phi in (0.1, 1.0, 2.5, 10.0):
            assert math.isclose(entanglement_capacity(phi), phi ** 2, rel_tol=1e-12)

    def test_entanglement_capacity_unity(self):
        assert entanglement_capacity(1.0) == 1.0

    def test_entanglement_capacity_positive(self):
        for phi in (0.01, 0.5, 3.0):
            assert entanglement_capacity(phi) > 0

    def test_entanglement_capacity_matches_delay_from_phi(self):
        for phi in (0.7, 1.0, 2.0, 5.0):
            assert entanglement_capacity(phi) == delay_from_phi(phi)


# ---------------------------------------------------------------------------
# TestRicciFlowTimeFactor
# ---------------------------------------------------------------------------

class TestRicciFlowTimeFactor:
    def test_omega_is_reciprocal_of_phi(self):
        for phi in (0.5, 1.0, 2.0, 4.0):
            assert math.isclose(ricci_flow_time_factor(phi), 1.0 / phi, rel_tol=1e-12)

    def test_omega_at_phi_one(self):
        assert ricci_flow_time_factor(1.0) == 1.0

    def test_omega_at_phi_two(self):
        assert math.isclose(ricci_flow_time_factor(2.0), 0.5, rel_tol=1e-12)

    def test_omega_raises_for_zero_phi(self):
        with pytest.raises(ValueError):
            ricci_flow_time_factor(0.0)

    def test_omega_raises_for_negative_phi(self):
        with pytest.raises(ValueError):
            ricci_flow_time_factor(-1.0)


# ---------------------------------------------------------------------------
# TestCoordTimeFromRicci
# ---------------------------------------------------------------------------

class TestCoordTimeFromRicci:
    def test_coord_time_formula(self):
        assert math.isclose(coord_time_from_ricci(2.0, 2.0), 1.0, rel_tol=1e-12)

    def test_coord_time_at_phi_one_equals_t_ricci(self):
        for t in (0.0, 1.0, 5.0):
            assert math.isclose(coord_time_from_ricci(t, 1.0), t, rel_tol=1e-12)

    def test_coord_time_inverse_of_ricci_from_coord(self):
        for t_r, phi in ((2.0, 1.5), (3.0, 2.0), (0.5, 0.5)):
            t_c = coord_time_from_ricci(t_r, phi)
            assert math.isclose(ricci_from_coord_time(t_c, phi), t_r, rel_tol=1e-12)

    def test_coord_time_raises_for_non_positive_phi(self):
        with pytest.raises(ValueError):
            coord_time_from_ricci(1.0, 0.0)


# ---------------------------------------------------------------------------
# TestRicciFromCoordTime
# ---------------------------------------------------------------------------

class TestRicciFromCoordTime:
    def test_ricci_from_coord_formula(self):
        assert math.isclose(ricci_from_coord_time(1.0, 2.0), 2.0, rel_tol=1e-12)

    def test_ricci_from_coord_at_phi_one(self):
        for t in (0.0, 1.0, 7.0):
            assert math.isclose(ricci_from_coord_time(t, 1.0), t, rel_tol=1e-12)

    def test_ricci_from_coord_raises_for_non_positive_phi(self):
        with pytest.raises(ValueError):
            ricci_from_coord_time(1.0, -0.5)


# ---------------------------------------------------------------------------
# TestGeminiIssue4Correction
# ---------------------------------------------------------------------------

class TestGeminiIssue4Correction:
    def test_at_phi_one_discrepancy_is_zero(self):
        result = gemini_issue4_correction(1.0, 5.0)
        assert math.isclose(result["discrepancy"], 0.0, abs_tol=1e-12)

    def test_at_phi_two_discrepancy_positive(self):
        result = gemini_issue4_correction(2.0, 1.0)
        assert result["discrepancy"] > 0

    def test_at_phi_half_discrepancy_positive(self):
        result = gemini_issue4_correction(0.5, 1.0)
        assert result["discrepancy"] > 0

    def test_correct_keys_present(self):
        result = gemini_issue4_correction(1.0, 1.0)
        for key in ("t_coord", "t_ricci", "omega", "discrepancy"):
            assert key in result

    def test_omega_equals_one_over_phi(self):
        for phi in (0.5, 1.0, 3.0):
            result = gemini_issue4_correction(phi, 1.0)
            assert math.isclose(result["omega"], 1.0 / phi, rel_tol=1e-12)

    def test_discrepancy_formula_at_phi_two(self):
        result = gemini_issue4_correction(2.0, 1.0)
        expected = abs(1.0 / 2.0 - 1.0)
        assert math.isclose(result["discrepancy"], expected, rel_tol=1e-12)

    def test_t_coord_echoed_correctly(self):
        result = gemini_issue4_correction(2.0, 4.0)
        assert math.isclose(result["t_coord"], 4.0 / 2.0, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# TestQuantumDelayVariance
# ---------------------------------------------------------------------------

class TestQuantumDelayVariance:
    def test_variance_non_negative(self):
        for pm, ps in ((1.0, 0.1), (2.0, 0.5), (0.5, 0.01)):
            assert quantum_delay_variance(pm, ps) >= 0

    def test_variance_zero_at_zero_spread(self):
        assert quantum_delay_variance(1.0, 0.0) == 0.0

    def test_variance_formula(self):
        pm, ps = 2.0, 0.3
        expected = 4.0 * pm ** 2 * ps ** 2
        assert math.isclose(quantum_delay_variance(pm, ps), expected, rel_tol=1e-12)

    def test_variance_increases_with_phi_mean(self):
        ps = 0.1
        v1 = quantum_delay_variance(1.0, ps)
        v2 = quantum_delay_variance(2.0, ps)
        assert v2 > v1

    def test_variance_increases_with_phi_spread(self):
        pm = 1.0
        v1 = quantum_delay_variance(pm, 0.1)
        v2 = quantum_delay_variance(pm, 0.2)
        assert v2 > v1


# ---------------------------------------------------------------------------
# TestDecoherenceTime
# ---------------------------------------------------------------------------

class TestDecoherenceTime:
    def test_decoherence_time_positive(self):
        assert decoherence_time(1.0, 0.5) > 0

    def test_decoherence_time_increases_with_phi_mean(self):
        ps = 0.5
        assert decoherence_time(2.0, ps) > decoherence_time(1.0, ps)

    def test_decoherence_time_decreases_with_phi_spread(self):
        pm = 1.0
        assert decoherence_time(pm, 0.1) > decoherence_time(pm, 0.5)

    def test_decoherence_time_formula(self):
        pm, ps = 3.0, 0.5
        assert math.isclose(decoherence_time(pm, ps), pm ** 2 / ps, rel_tol=1e-12)

    def test_decoherence_time_raises_for_zero_spread(self):
        with pytest.raises(ValueError):
            decoherence_time(1.0, 0.0)

    def test_decoherence_time_raises_for_negative_spread(self):
        with pytest.raises(ValueError):
            decoherence_time(1.0, -0.1)


# ---------------------------------------------------------------------------
# TestIrreversibilityMeasure
# ---------------------------------------------------------------------------

class TestIrreversibilityMeasure:
    def test_unity_at_phi_equals_phi_0(self):
        assert irreversibility_measure(1.0, 1.0) == 1.0

    def test_greater_than_one_for_phi_above_phi_0(self):
        assert irreversibility_measure(2.0, 1.0) > 1.0

    def test_less_than_one_for_phi_below_phi_0(self):
        assert irreversibility_measure(0.5, 1.0) < 1.0

    def test_formula(self):
        phi, phi_0 = 3.0, 2.0
        expected = (phi / phi_0) ** 2
        assert math.isclose(irreversibility_measure(phi, phi_0), expected, rel_tol=1e-12)

    def test_default_phi_0_is_one(self):
        assert math.isclose(irreversibility_measure(2.0), 4.0, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# TestEntropyProductionRate
# ---------------------------------------------------------------------------

class TestEntropyProductionRate:
    def test_zero_when_phi_dot_zero(self):
        assert entropy_production_rate(1.0, 0.0) == 0.0

    def test_positive_when_phi_dot_positive(self):
        assert entropy_production_rate(1.0, 1.0) > 0

    def test_negative_when_phi_dot_negative(self):
        assert entropy_production_rate(1.0, -1.0) < 0

    def test_formula(self):
        phi, phi_dot, phi_0 = 2.0, 0.5, 1.0
        expected = 2.0 * phi * phi_dot / phi_0 ** 2
        assert math.isclose(
            entropy_production_rate(phi, phi_dot, phi_0), expected, rel_tol=1e-12
        )

    def test_default_phi_0(self):
        phi, phi_dot = 3.0, 0.2
        assert math.isclose(
            entropy_production_rate(phi, phi_dot),
            2.0 * phi * phi_dot,
            rel_tol=1e-12,
        )


# ---------------------------------------------------------------------------
# TestDfmUmConsistency
# ---------------------------------------------------------------------------

class TestDfmUmConsistency:
    def test_true_when_consistent(self):
        phi = 2.0
        assert dfm_um_consistency_check(phi, phi ** 2)

    def test_false_when_not_consistent(self):
        assert not dfm_um_consistency_check(2.0, 3.0)

    def test_exact_at_phi_one(self):
        assert dfm_um_consistency_check(1.0, 1.0)

    def test_false_for_large_discrepancy(self):
        assert not dfm_um_consistency_check(1.0, 100.0)


# ---------------------------------------------------------------------------
# TestBraidedDelaySpectrum
# ---------------------------------------------------------------------------

class TestBraidedDelaySpectrum:
    def test_canonical_c_s(self):
        result = braided_delay_spectrum(N1_CANONICAL, N2_CANONICAL, K_CS_CANONICAL)
        assert math.isclose(result["c_s"], C_S_CANONICAL, rel_tol=1e-12)

    def test_dict_keys_present(self):
        result = braided_delay_spectrum(5, 7, 74)
        for key in ("c_s", "delta_tau_1", "delta_tau_2", "phi_1", "phi_2"):
            assert key in result

    def test_phi_1_is_sqrt_delta_tau_1(self):
        result = braided_delay_spectrum(5, 7, 74)
        assert math.isclose(result["phi_1"] ** 2, abs(result["delta_tau_1"]), rel_tol=1e-12)

    def test_phi_2_is_sqrt_delta_tau_2(self):
        result = braided_delay_spectrum(5, 7, 74)
        assert math.isclose(result["phi_2"] ** 2, abs(result["delta_tau_2"]), rel_tol=1e-12)

    def test_canonical_delta_tau_1(self):
        result = braided_delay_spectrum(5, 7, 74)
        expected = 5 * C_S_CANONICAL
        assert math.isclose(result["delta_tau_1"], expected, rel_tol=1e-12)

    def test_canonical_delta_tau_2(self):
        result = braided_delay_spectrum(5, 7, 74)
        expected = 7 * C_S_CANONICAL
        assert math.isclose(result["delta_tau_2"], expected, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# TestCausalArrowOfTime
# ---------------------------------------------------------------------------

class TestCausalArrowOfTime:
    def test_forward(self):
        assert causal_arrow_of_time(1.0, 2.0) == "forward"

    def test_backward(self):
        assert causal_arrow_of_time(2.0, 1.0) == "backward"

    def test_equilibrium(self):
        assert causal_arrow_of_time(1.0, 1.0) == "equilibrium"

    def test_forward_small_increment(self):
        assert causal_arrow_of_time(1.0, 1.0 + 1e-15) == "forward"


# ---------------------------------------------------------------------------
# TestDfmSummary
# ---------------------------------------------------------------------------

class TestDfmSummary:
    def test_all_keys_present(self):
        result = dfm_summary(1.0, 1.0)
        expected_keys = {
            "phi",
            "delta_tau",
            "entanglement_capacity",
            "omega",
            "t_coord",
            "t_ricci",
            "discrepancy",
            "irreversibility",
            "entropy_production_rate_unit",
        }
        assert expected_keys.issubset(result.keys())

    def test_at_phi_one_discrepancy_zero(self):
        result = dfm_summary(1.0, 1.0)
        assert math.isclose(result["discrepancy"], 0.0, abs_tol=1e-12)

    def test_delta_tau_equals_phi_squared(self):
        for phi in (0.5, 1.0, 2.0):
            result = dfm_summary(phi, 1.0)
            assert math.isclose(result["delta_tau"], phi ** 2, rel_tol=1e-12)

    def test_omega_is_one_over_phi(self):
        for phi in (0.5, 1.0, 3.0):
            result = dfm_summary(phi, 1.0)
            assert math.isclose(result["omega"], 1.0 / phi, rel_tol=1e-12)

    def test_irreversibility_at_phi_one(self):
        result = dfm_summary(1.0, 1.0)
        assert math.isclose(result["irreversibility"], 1.0, rel_tol=1e-12)
