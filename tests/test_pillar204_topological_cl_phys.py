# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 204 — Topological c_L^phys from Dirac Zero-Mode Complementarity."""

import math
import pytest

from src.core.pillar204_topological_cl_phys import (
    N_W, K_CS, N_C, PI_KR,
    ALPHA_GUT_GEO, CL_TOPO, CL_RGE, DELTA_CL,
    alpha_gut_geometric,
    cl_phys_topological,
    cl_comparison,
    neutrino_mass_sensitivity,
    dirac_zero_mode_condition,
    fermion_mass_from_cl,
    axiom_zero_audit,
    pillar204_summary,
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

    def test_alpha_gut_value(self):
        assert ALPHA_GUT_GEO == pytest.approx(3.0 / 74.0, rel=1e-6)

    def test_cl_topo_value(self):
        assert CL_TOPO == pytest.approx(71.0 / 74.0, rel=1e-6)

    def test_cl_topo_plus_alpha_gut_is_1(self):
        assert CL_TOPO + ALPHA_GUT_GEO == pytest.approx(1.0, abs=1e-12)

    def test_cl_topo_below_1(self):
        assert CL_TOPO < 1.0

    def test_cl_topo_above_half(self):
        assert CL_TOPO > 0.5

    def test_cl_rge_approx(self):
        assert 0.95 < CL_RGE < 0.97

    def test_delta_cl_small(self):
        assert DELTA_CL < 0.01

    def test_delta_cl_is_difference(self):
        assert DELTA_CL == pytest.approx(abs(CL_TOPO - CL_RGE), rel=1e-6)


class TestAlphaGutGeometric:
    def setup_method(self):
        self.result = alpha_gut_geometric()

    def test_value(self):
        assert self.result["alpha_gut_geo"] == pytest.approx(3.0 / 74.0, rel=1e-6)

    def test_fraction_string(self):
        assert "3/74" in self.result["alpha_gut_fraction"]

    def test_source_pillar(self):
        assert "189" in self.result["source"]

    def test_physical_meaning_present(self):
        assert len(self.result["physical_meaning"]) > 20


class TestClPhysTopological:
    def setup_method(self):
        self.result = cl_phys_topological()

    def test_value(self):
        assert self.result["cl_topo"] == pytest.approx(71.0 / 74.0, rel=1e-6)

    def test_fraction_string(self):
        assert "71/74" in self.result["cl_topo_fraction"]

    def test_alpha_gut_geo(self):
        assert self.result["alpha_gut_geo"] == pytest.approx(3.0 / 74.0, rel=1e-6)

    def test_no_sm_anchors(self):
        assert self.result["sm_anchors_used"] == []

    def test_status_derived(self):
        assert "DERIVED" in self.result["status"]

    def test_derivation_has_steps(self):
        assert "Step 1" in self.result["derivation"]

    def test_numerator_correct(self):
        assert self.result["cl_topo_fraction_simplified"].startswith("71")


class TestClComparison:
    def setup_method(self):
        self.result = cl_comparison()

    def test_cl_topo(self):
        assert self.result["cl_topo"] == pytest.approx(71.0 / 74.0, rel=1e-6)

    def test_cl_rge(self):
        assert self.result["cl_rge"] == pytest.approx(0.961)

    def test_delta_cl(self):
        assert self.result["delta_cl"] < 0.01

    def test_pi_kr(self):
        assert self.result["pi_kr"] == pytest.approx(37.0)

    def test_sum_mnu_rge_is_62pt5(self):
        assert self.result["sum_mnu_rge_mev"] == pytest.approx(62.5)

    def test_sum_mnu_topo_different(self):
        assert abs(self.result["sum_mnu_topo_mev"] - 62.5) > 1.0  # >1% shift

    def test_mnu_shift_above_5pct(self):
        # Exponential sensitivity gives >5% shift
        assert self.result["sum_mnu_shift_pct"] > 5.0

    def test_status_approximate(self):
        assert "APPROXIMATE" in self.result["status"]

    def test_exponential_sensitivity_positive(self):
        assert self.result["exponential_sensitivity_exponent"] > 0


class TestNeutrinoMassSensitivity:
    def setup_method(self):
        self.result = neutrino_mass_sensitivity()

    def test_cl_phys_stored(self):
        assert self.result["cl_phys"] == pytest.approx(CL_TOPO, rel=1e-6)

    def test_suppression_positive(self):
        assert self.result["suppression_factor"] > 0

    def test_suppression_less_than_1(self):
        assert self.result["suppression_factor"] < 1.0

    def test_sensitivity_derivative_value(self):
        # d(ln m_ν)/d(c_L) = -2πkR = -74
        assert self.result["sensitivity_d_ln_mnu_d_cl"] == pytest.approx(-74.0)

    def test_note_mentions_exponential(self):
        assert "exp" in self.result["note"].lower() or "exponential" in self.result["note"].lower()

    def test_sum_mnu_predicted_positive(self):
        assert self.result["sum_mnu_predicted_mev"] > 0


class TestDiracZeroModeCondition:
    def setup_method(self):
        self.result = dirac_zero_mode_condition()

    def test_condition_string(self):
        assert "c_L" in self.result["condition"]

    def test_proof_has_steps(self):
        assert len(self.result["proof_steps"]) >= 4

    def test_verification_satisfied(self):
        assert self.result["verification"]["condition_satisfied"] is True

    def test_sum_is_1(self):
        v = self.result["verification"]
        assert v["sum"] == pytest.approx(1.0, abs=1e-12)

    def test_cl_topo_value(self):
        assert self.result["verification"]["cl_topo"] == pytest.approx(71.0 / 74.0, rel=1e-6)

    def test_limitations_nonempty(self):
        assert len(self.result["limitations"]) > 0

    def test_status_approximate(self):
        assert "APPROXIMATE" in self.result["status"]


class TestFermionMassFromCl:
    def setup_method(self):
        self.result = fermion_mass_from_cl()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_results_nonempty(self):
        assert len(self.result["results"]) > 0

    def test_ir_localised_yukawa_is_1(self):
        for entry in self.result["results"]:
            if entry["localisation"] == "IR":
                assert entry["Y_eff"] == pytest.approx(1.0)

    def test_uv_localised_yukawa_below_1(self):
        for entry in self.result["results"]:
            if entry["localisation"] == "UV":
                assert entry["Y_eff"] < 1.0

    def test_mass_positive(self):
        for entry in self.result["results"]:
            assert entry["m_f_GeV"] > 0

    def test_formula_present(self):
        assert "exp" in self.result["formula"]


class TestAxiomZeroAudit:
    def setup_method(self):
        self.result = axiom_zero_audit()

    def test_compliant(self):
        assert self.result["axiom_zero_compliant"] is True

    def test_zero_sm_anchors(self):
        assert self.result["sm_anchors_count"] == 0

    def test_two_inputs(self):
        assert len(self.result["derivation_inputs"]) == 2

    def test_cl_rge_comparison_only(self):
        comp = " ".join(self.result["quantities_used_for_comparison_only"])
        assert "0.961" in comp or "RGE" in comp


class TestPillar204Summary:
    def setup_method(self):
        self.result = pillar204_summary()

    def test_pillar_tag(self):
        assert self.result["pillar"] == "204"

    def test_version(self):
        assert "v10" in self.result["version"]

    def test_cl_topo_in_result(self):
        assert self.result["key_result"]["cl_topo"] == pytest.approx(71.0 / 74.0, rel=1e-6)

    def test_fraction_in_result(self):
        assert "71/74" in self.result["key_result"]["cl_topo_fraction"]

    def test_toe_impact_constrained(self):
        assert "CONSTRAINED" in self.result["toe_impact"]

    def test_status_approximate(self):
        assert "APPROXIMATE" in self.result["status"]

    def test_delta_cl_pct_below_1(self):
        assert self.result["key_result"]["delta_cl_pct"] < 1.0
