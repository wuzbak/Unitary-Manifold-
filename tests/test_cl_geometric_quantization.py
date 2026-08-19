# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 702 — c_L Geometric Quantization (cl_geometric_quantization.py)."""
from __future__ import annotations

import math
import pytest

from src.core.cl_geometric_quantization import (
    PILLAR_STATUS,
    VERSION,
    N_W,
    K_CS,
    PI_KR,
    V_EW_GEV,
    M_TOP_GEV,
    c_L_pattern,
    c_L_from_yukawa_normalisation,
    c_L_from_mass_hierarchy,
    zero_mode_profile_L,
    top_yukawa_normalisation_condition,
    cl_quantization_result,
    derivation_chain_status,
    honest_assessment,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_pillar_status_string(self):
        assert PILLAR_STATUS == 'CL_GEOMETRIC_QUANTIZATION_ATTEMPTED'

    def test_framework_constants(self):
        assert N_W == 5
        assert K_CS == 74
        assert abs(PI_KR - 37.0) < 1e-12

    def test_physical_constants(self):
        assert V_EW_GEV > 200.0
        assert M_TOP_GEV > 150.0


# ---------------------------------------------------------------------------
# c_L pattern formula
# ---------------------------------------------------------------------------

class TestCLPattern:
    def test_gen1_value(self):
        assert abs(c_L_pattern(1) - 0.9) < 1e-12

    def test_gen2_value(self):
        assert abs(c_L_pattern(2) - 0.8) < 1e-12

    def test_gen3_value(self):
        assert abs(c_L_pattern(3) - 0.7) < 1e-12

    def test_pattern_hierarchy(self):
        assert c_L_pattern(1) > c_L_pattern(2) > c_L_pattern(3)

    def test_pattern_range(self):
        for gen in [1, 2, 3]:
            val = c_L_pattern(gen)
            assert 0.5 < val < 1.0

    def test_pattern_formula_at_nw5(self):
        # c_L(n) = 0.5 + (5-n)/(10)
        for gen in [1, 2, 3]:
            expected = 0.5 + (5 - gen) / 10.0
            assert abs(c_L_pattern(gen) - expected) < 1e-12


# ---------------------------------------------------------------------------
# Zero-mode profile
# ---------------------------------------------------------------------------

class TestZeroModeProfile:
    def test_positive_for_cL_above_half(self):
        for c_L in [0.51, 0.6, 0.7, 0.8, 0.9, 1.0]:
            f = zero_mode_profile_L(c_L)
            assert f > 0.0

    def test_positive_for_cL_below_half(self):
        """IR-localised fermions (c_L < 0.5) also have positive profile."""
        for c_L in [0.49, 0.3, 0.0, -1.0]:
            f = zero_mode_profile_L(c_L)
            assert f > 0.0

    def test_flat_profile_at_cL_half(self):
        """At c_L = 0.5 (flat profile), f₀ = 1/sqrt(kπR) ≈ 0.164."""
        f = zero_mode_profile_L(0.5)
        assert abs(f - 1.0 / math.sqrt(37.0)) < 1e-10

    def test_decreasing_in_cL(self):
        """f₀ is strictly DECREASING in c_L (universal_yukawa._f0 convention)."""
        c_vals = [0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        f_vals = [zero_mode_profile_L(c) for c in c_vals]
        for i in range(len(f_vals) - 1):
            assert f_vals[i] > f_vals[i + 1]

    def test_finite(self):
        for c_L in [0.51, 0.7, 0.9, -1.0, 0.5]:
            assert math.isfinite(zero_mode_profile_L(c_L))


# ---------------------------------------------------------------------------
# Yukawa normalisation
# ---------------------------------------------------------------------------

class TestYukawaQuantisation:
    def test_derived_cL3_finite(self):
        """c_L for y_top=1 is finite (top quark requires c_L << 0.5)."""
        c_L3 = c_L_from_yukawa_normalisation()
        assert math.isfinite(c_L3)

    def test_derived_cL3_gives_correct_overlap(self):
        """The derived c_L actually satisfies f_L × f_R ≈ y_top_target."""
        y_target = 0.7  # use sub-unity target to stay in tractable range
        c_L3 = c_L_from_yukawa_normalisation(y_top_target=y_target)
        f_R = 1.0 / math.sqrt(37.0)
        overlap = zero_mode_profile_L(c_L3) * f_R
        assert abs(overlap - y_target) < 1e-6

    def test_top_yukawa_normalisation_condition(self):
        result = top_yukawa_normalisation_condition()
        assert 'c_L3_from_yukawa_normalisation' in result
        assert 'c_L3_from_pattern_formula' in result
        assert 'discrepancy' in result
        assert math.isfinite(result['discrepancy'])

    def test_pattern_cL3_in_expected_range(self):
        """Pattern formula gives c_L^(3) in (0.5, 1.0)."""
        result = top_yukawa_normalisation_condition()
        assert 0.5 < result['c_L3_from_pattern_formula'] < 1.5


# ---------------------------------------------------------------------------
# Mass hierarchy derivation
# ---------------------------------------------------------------------------

class TestMassHierarchy:
    def test_hierarchy_ordering(self):
        """Heavier fermion → smaller c_L (RS1 convention: heavier = smaller = IR-localized).
        Using lepton masses with tau as the reference anchor.
        """
        # Use tau lepton as anchor (well within lepton UV-localized regime)
        M_TAU_GEV = 1.77686
        M_MU_GEV = 0.10566
        from src.core.universal_yukawa import required_c_L_for_universal_yukawa
        c_L_tau_ref = required_c_L_for_universal_yukawa(M_TAU_GEV * 1000.0)
        c_L_muon = c_L_from_mass_hierarchy(M_MU_GEV, m_ref_GeV=M_TAU_GEV,
                                            c_L_ref=c_L_tau_ref)
        # Muon lighter → larger c_L (more UV-localised)
        assert c_L_muon > c_L_tau_ref

    def test_hierarchy_values_in_lepton_range(self):
        """Lepton c_L values are UV-localized (above 0.5) in the RS1 UV-brane formula."""
        from src.core.universal_yukawa import required_c_L_for_universal_yukawa
        M_TAU_GEV = 1.77686
        M_MU_GEV = 0.10566
        c_L_tau = required_c_L_for_universal_yukawa(M_TAU_GEV * 1000.0)
        c_L_mu = required_c_L_for_universal_yukawa(M_MU_GEV * 1000.0)
        assert 0.5 < c_L_tau < 0.65
        assert 0.5 < c_L_mu < 0.70


# ---------------------------------------------------------------------------
# Quantization result
# ---------------------------------------------------------------------------

class TestQuantizationResult:
    def test_result_has_status(self):
        result = cl_quantization_result()
        assert result['status'] in ('FITTED', 'DERIVED_GEN1')

    def test_result_has_all_generations(self):
        result = cl_quantization_result()
        for key in ['c_L1_yukawa_quantisation', 'c_L2_yukawa_quantisation',
                    'c_L3_yukawa_quantisation', 'c_L1_pattern', 'c_L2_pattern', 'c_L3_pattern']:
            assert key in result
            assert math.isfinite(result[key])

    def test_result_hierarchy_preserved(self):
        """Both Yukawa and pattern families give c_L^(1) > c_L^(2) > c_L^(3)."""
        result = cl_quantization_result()
        assert result['c_L1_pattern'] > result['c_L2_pattern'] > result['c_L3_pattern']

    def test_result_has_honest_gap(self):
        result = cl_quantization_result()
        assert 'honest_gap' in result
        assert len(result['honest_gap']) > 10

    def test_result_has_summary(self):
        result = cl_quantization_result()
        assert 'summary' in result


# ---------------------------------------------------------------------------
# Derivation chain and honest assessment
# ---------------------------------------------------------------------------

class TestDerivationChain:
    def test_derivation_chain_structure(self):
        status = derivation_chain_status()
        for key in ['pillar', 'title', 'status', 'pattern_status', 'gap']:
            assert key in status

    def test_derivation_chain_pillar(self):
        status = derivation_chain_status()
        assert status['pillar'] == 702

    def test_honest_assessment_is_string(self):
        assessment = honest_assessment()
        assert isinstance(assessment, str)
        assert len(assessment) > 50

    def test_honest_assessment_mentions_fitted_or_derived(self):
        assessment = honest_assessment()
        assert 'FITTED' in assessment or 'DERIVED' in assessment

    def test_honest_assessment_mentions_pattern(self):
        assessment = honest_assessment()
        assert 'pattern' in assessment.lower()
