# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 205 — Generation Quantization Audit."""

import math
import pytest

from src.core.pillar205_generation_quantization import (
    N_W, K_CS, N_C, PI_KR,
    CL_QUANTIZED_LEVELS,
    cl_quantized,
    yukawa_from_cl,
    generation_mass_table,
    quantization_audit,
    heaviest_two_assessment,
    axiom_zero_audit,
    pillar205_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_quantized_levels_count(self):
        assert len(CL_QUANTIZED_LEVELS) == N_W + 1  # 6 levels: 0,1,2,3,4,5

    def test_quantized_levels_values(self):
        expected = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        for got, exp in zip(CL_QUANTIZED_LEVELS, expected):
            assert got == pytest.approx(exp)

    def test_quantized_levels_start_at_0(self):
        assert CL_QUANTIZED_LEVELS[0] == pytest.approx(0.0)

    def test_quantized_levels_end_at_1(self):
        assert CL_QUANTIZED_LEVELS[-1] == pytest.approx(1.0)


class TestClQuantized:
    def test_returns_list(self):
        result = cl_quantized()
        assert isinstance(result, list)

    def test_length_n_w_plus_1(self):
        result = cl_quantized(5)
        assert len(result) == 6

    def test_first_level_m0_cl0(self):
        result = cl_quantized()
        assert result[0]["m"] == 0
        assert result[0]["c_L"] == pytest.approx(0.0)

    def test_last_level_m5_cl1(self):
        result = cl_quantized()
        assert result[-1]["m"] == 5
        assert result[-1]["c_L"] == pytest.approx(1.0)

    def test_m3_cl_06(self):
        result = cl_quantized()
        entry = result[3]
        assert entry["m"] == 3
        assert entry["c_L"] == pytest.approx(0.6)

    def test_m2_is_ir_localised(self):
        result = cl_quantized()
        assert "IR" in result[2]["localisation"]

    def test_m3_is_uv_localised(self):
        result = cl_quantized()
        assert "UV" in result[3]["localisation"]

    def test_fraction_string(self):
        result = cl_quantized()
        assert result[3]["c_L_fraction"] == "3/5"


class TestYukawaFromCl:
    def test_ir_localised_cl0(self):
        assert yukawa_from_cl(0.0) == pytest.approx(1.0)

    def test_ir_localised_cl04(self):
        assert yukawa_from_cl(0.4) == pytest.approx(1.0)

    def test_critical_cl05(self):
        assert yukawa_from_cl(0.5) == pytest.approx(1.0)

    def test_uv_localised_cl06(self):
        expected = math.exp(-0.1 * 37.0)
        assert yukawa_from_cl(0.6) == pytest.approx(expected, rel=1e-6)

    def test_uv_localised_cl08(self):
        expected = math.exp(-0.3 * 37.0)
        assert yukawa_from_cl(0.8) == pytest.approx(expected, rel=1e-6)

    def test_uv_localised_cl10(self):
        expected = math.exp(-0.5 * 37.0)
        assert yukawa_from_cl(1.0) == pytest.approx(expected, rel=1e-6)

    def test_decreasing_with_increasing_cl(self):
        y06 = yukawa_from_cl(0.6)
        y08 = yukawa_from_cl(0.8)
        y10 = yukawa_from_cl(1.0)
        assert y06 > y08 > y10

    def test_all_positive(self):
        for cl in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            assert yukawa_from_cl(cl) > 0


class TestGenerationMassTable:
    def setup_method(self):
        self.table = generation_mass_table()

    def test_length(self):
        assert len(self.table) == N_W + 1  # 6 entries

    def test_m2_mass_order_of_v(self):
        # c_L=0.4 is IR-localised, mass ≈ v
        entry = self.table[2]  # m=2, c_L=0.4
        assert entry["m_f_GeV"] > 200  # heavy, near v

    def test_m3_mass_few_gev(self):
        # c_L=0.6, Y_eff = exp(-3.7) ≈ 0.025, mass ≈ 6 GeV
        entry = self.table[3]  # m=3, c_L=0.6
        assert 3 < entry["m_f_GeV"] < 10

    def test_m5_mass_tiny(self):
        # c_L=1.0, Y_eff = exp(-18.5) ≈ 9.4e-9, mass ≈ 0.0024 MeV (well below lepton scale)
        entry = self.table[5]  # m=5, c_L=1.0
        assert entry["m_f_MeV"] < 0.01  # << electron mass (0.511 MeV)

    def test_all_masses_positive(self):
        for entry in self.table:
            assert entry["m_f_GeV"] > 0

    def test_decreasing_mass(self):
        masses = [e["m_f_GeV"] for e in self.table]
        # From m=2 onwards masses should decrease (UV-localised)
        assert masses[2] > masses[3] > masses[4] > masses[5]

    def test_yukawa_from_cl_0_is_1(self):
        entry = self.table[0]
        assert entry["Y_eff"] == pytest.approx(1.0)

    def test_suppression_exponent_zero_for_ir(self):
        for entry in self.table[:3]:  # m=0,1,2 all have c_L <= 0.5
            assert entry["suppression_exponent"] == pytest.approx(0.0)


class TestQuantizationAudit:
    def setup_method(self):
        self.result = quantization_audit()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_hypothesis_string(self):
        assert "c_L" in self.result["hypothesis"]

    def test_n_w_stored(self):
        assert self.result["n_w"] == N_W

    def test_mass_table_nonempty(self):
        assert len(self.result["mass_table"]) > 0

    def test_pdg_comparisons_nonempty(self):
        assert len(self.result["pdg_comparisons"]) > 0

    def test_verdict_not_confirmed(self):
        # Agent A's full claim should NOT be confirmed
        assert "NOT" in self.result["verdict"] or "not" in self.result["verdict"]

    def test_agent_a_verdict_partial(self):
        assert "PARTIAL" in self.result["agent_a_verdict"] or "not" in self.result["agent_a_verdict"].lower()

    def test_total_levels(self):
        assert self.result["total_levels"] == N_W + 1


class TestHeaviestTwoAssessment:
    def setup_method(self):
        self.result = heaviest_two_assessment()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_top_cl(self):
        assert self.result["top_quark"]["c_L"] == pytest.approx(0.4)

    def test_bot_cl(self):
        assert self.result["bottom_quark"]["c_L"] == pytest.approx(0.6)

    def test_top_cl_fraction(self):
        assert "2/5" in self.result["top_quark"]["c_L_fraction"]

    def test_bot_cl_fraction(self):
        assert "3/5" in self.result["bottom_quark"]["c_L_fraction"]

    def test_top_yukawa_is_1(self):
        assert self.result["top_quark"]["Y_eff"] == pytest.approx(1.0)

    def test_bot_yukawa_below_1(self):
        assert self.result["bottom_quark"]["Y_eff"] < 1.0

    def test_top_ratio_within_factor_2(self):
        # Top prediction: ~257 GeV vs PDG 173 GeV → factor 1.5
        assert 0.5 < self.result["top_quark"]["ratio"] < 2.0

    def test_bot_ratio_within_factor_2(self):
        # Bottom prediction: ~6 GeV vs PDG 4.2 GeV → factor 1.5
        assert 0.5 < self.result["bottom_quark"]["ratio"] < 2.0

    def test_status_qualitative(self):
        assert "QUALITATIVE" in self.result["status"]

    def test_combined_verdict_present(self):
        assert len(self.result["combined_verdict"]) > 20


class TestAxiomZeroAudit:
    def setup_method(self):
        self.result = axiom_zero_audit()

    def test_compliant(self):
        assert self.result["axiom_zero_compliant"] is True

    def test_zero_sm_anchors(self):
        assert self.result["sm_anchors_count"] == 0

    def test_pdg_role_comparison(self):
        assert "comparison" in self.result["pdg_masses_role"].lower()


class TestPillar205Summary:
    def setup_method(self):
        self.result = pillar205_summary()

    def test_pillar_tag(self):
        assert self.result["pillar"] == "205"

    def test_version(self):
        assert "v10" in self.result["version"]

    def test_conclusion_not_confirmed(self):
        assert "NOT confirmed" in self.result["conclusion"] or "NOT" in self.result["conclusion"]

    def test_toe_impact_fitted(self):
        assert "FITTED" in self.result["toe_impact"]

    def test_status_partial(self):
        assert "PARTIAL" in self.result["status"]

    def test_agent_a_hypothesis_present(self):
        assert len(self.result["agent_a_hypothesis"]) > 0
