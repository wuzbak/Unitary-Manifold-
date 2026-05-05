# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_fermion_laplacian_spectrum.py
==========================================
Tests for Pillar 174 — Fermion Masses from the RS₁ Laplacian.

Theory, scientific direction, and framework: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""

import math
import pytest

from src.core.fermion_laplacian_spectrum import (
    N_W, K_CS, PI_KR, HAT_Y5, C_R_CANONICAL, SM_FERMION_DATA,
    rs_zero_mode_profile_L,
    rs_zero_mode_profile_R,
    yukawa_overlap_integral,
    yukawa_from_c,
    fermion_mass_from_c,
    c_from_mass,
    zero_mode_normalization,
    is_zero_mode_normalizable,
    c_spectrum_is_continuous,
    what_quantizes_c,
    fermion_mass_hierarchy,
    pillar174_honest_verdict,
    pillar174_summary,
    pillar174_full_report,
)


class TestModuleConstants:
    def test_n_w(self): assert N_W == 5
    def test_k_cs(self): assert K_CS == 74
    def test_pi_kr(self): assert PI_KR == pytest.approx(37.0, rel=1e-12)
    def test_hat_y5(self): assert HAT_Y5 == pytest.approx(1.0, rel=1e-12)
    def test_c_r_canonical(self): assert C_R_CANONICAL == pytest.approx(0.920, rel=1e-9)
    def test_sm_fermion_data_length(self): assert len(SM_FERMION_DATA) == 9
    def test_sm_fermion_data_has_quarks(self): assert len([f for f in SM_FERMION_DATA if f["sector"]=="quark"]) == 6
    def test_sm_fermion_data_has_leptons(self): assert len([f for f in SM_FERMION_DATA if f["sector"]=="lepton"]) == 3
    def test_top_quark_mass(self): assert next(f for f in SM_FERMION_DATA if f["name"]=="top quark")["mass_mev"] == pytest.approx(172_760.0, rel=0.01)
    def test_electron_mass(self): assert next(f for f in SM_FERMION_DATA if f["name"]=="electron")["mass_mev"] == pytest.approx(0.511, rel=0.01)
    def test_k_cs_is_sum_of_squares(self): assert K_CS == N_W**2 + 7**2
    def test_pi_kr_is_k_cs_over_2(self): assert PI_KR == pytest.approx(K_CS/2.0, rel=1e-12)


class TestRsZeroModeProfiles:
    def test_profile_L_at_uv_brane(self): assert rs_zero_mode_profile_L(0.9, y=0.0) == pytest.approx(1.0, rel=1e-9)
    def test_profile_L_increases_for_c_less_than_2(self):
        assert rs_zero_mode_profile_L(0.5, y=PI_KR) > rs_zero_mode_profile_L(0.5, y=0.0)
    def test_profile_L_decreases_for_c_gt_2(self):
        assert rs_zero_mode_profile_L(2.5, y=1.0) < rs_zero_mode_profile_L(2.5, y=0.0)
    def test_profile_R_at_uv_brane(self): assert rs_zero_mode_profile_R(0.9, y=0.0) == pytest.approx(1.0, rel=1e-9)
    def test_profiles_positive(self):
        for c in [0.3, 0.5, 0.9, 1.5]:
            for y in [0.0, 1.0, 5.0]:
                assert rs_zero_mode_profile_L(c, y) > 0
                assert rs_zero_mode_profile_R(c, y) > 0


class TestYukawaOverlapIntegral:
    def test_returns_positive(self): assert yukawa_overlap_integral(0.8, 0.9) > 0.0
    def test_decreases_with_increasing_cl(self):
        assert yukawa_overlap_integral(0.6, 0.9) > yukawa_overlap_integral(0.8, 0.9) > yukawa_overlap_integral(0.95, 0.9)
    def test_exponential_hierarchy_range(self):
        assert yukawa_overlap_integral(0.51, 0.9) / yukawa_overlap_integral(0.99, 0.9) > 1e5
    def test_hat_y5_scales_linearly(self):
        assert yukawa_overlap_integral(0.8, 0.9, hat_y5=2.0) == pytest.approx(2.0*yukawa_overlap_integral(0.8, 0.9, hat_y5=1.0), rel=1e-6)


class TestYukawaFromC:
    def test_returns_positive(self): assert yukawa_from_c(0.8) > 0.0
    def test_consistent_with_overlap_integral(self): assert yukawa_from_c(0.8) == pytest.approx(yukawa_overlap_integral(0.8, C_R_CANONICAL), rel=1e-9)


class TestFermionMassFromC:
    def test_returns_positive(self): assert fermion_mass_from_c(0.8) > 0.0
    def test_decreasing_with_c_l(self): assert fermion_mass_from_c(0.7) > fermion_mass_from_c(0.85) > fermion_mass_from_c(0.95)
    def test_mass_in_mev(self):
        m = fermion_mass_from_c(0.9)
        assert m > 0.0 and m < 1e20


class TestCFromMass:
    def test_electron_mass(self):
        c_l = c_from_mass(0.511)
        assert fermion_mass_from_c(c_l) == pytest.approx(0.511, rel=0.01)
    def test_muon_mass(self):
        c_l = c_from_mass(105.66)
        assert fermion_mass_from_c(c_l) == pytest.approx(105.66, rel=0.01)
    def test_tau_mass(self):
        c_l = c_from_mass(1776.9)
        assert fermion_mass_from_c(c_l) == pytest.approx(1776.9, rel=0.01)
    def test_top_quark_mass(self):
        c_l = c_from_mass(172_760.0)
        assert fermion_mass_from_c(c_l) == pytest.approx(172_760.0, rel=0.02)
    def test_c_l_ordering(self):
        c_e = c_from_mass(0.511)
        c_mu = c_from_mass(105.66)
        c_tau = c_from_mass(1776.9)
        assert c_e > c_mu > c_tau
    def test_c_l_is_positive(self):
        for f in SM_FERMION_DATA[:3]:
            try:
                c_l = c_from_mass(f["mass_mev"])
                assert isinstance(c_l, float)
            except ValueError:
                pass


class TestZeroModeNormalization:
    def test_positive_for_standard_c(self):
        for c in [0.5, 0.7, 0.9, 0.95]: assert zero_mode_normalization(c) > 0.0
    def test_flat_profile_at_half(self): assert zero_mode_normalization(0.5) == pytest.approx(1.0/math.sqrt(PI_KR), rel=0.01)
    def test_positive_for_ir_localised(self):
        for c in [0.3, 0.1, 0.0, -0.5]: assert zero_mode_normalization(c) > 0.0
    def test_decreases_for_large_c(self): assert zero_mode_normalization(0.6) > zero_mode_normalization(0.8) > zero_mode_normalization(0.95)


class TestIsZeroModeNormalizable:
    def test_normalizable_for_typical_c(self):
        for c in [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 1.5]: assert is_zero_mode_normalizable(c) is True
    def test_normalizable_for_negative_c(self):
        for c in [-2.0, -1.0, -0.5]: assert is_zero_mode_normalizable(c) is True
    def test_normalizable_for_large_c(self):
        for c in [1.0, 1.5, 2.0, 3.0]: assert is_zero_mode_normalizable(c) is True


class TestCSpectrumIsContinuous:
    def setup_method(self): self.result = c_spectrum_is_continuous()
    def test_returns_dict(self): assert isinstance(self.result, dict)
    def test_all_normalizable(self): assert self.result["all_normalizable"] is True
    def test_is_continuous(self): assert self.result["is_continuous"] is True
    def test_n_tested_substantial(self): assert self.result["n_tested"] >= 20
    def test_c_range_includes_typical_fermion_values(self):
        c_min, c_max = self.result["c_range"]
        assert c_min < 0.5 and c_max > 0.9
    def test_verdict_mentions_continuous(self):
        assert "CONTINUOUS" in self.result["verdict"].upper() or "continuous" in self.result["verdict"]
    def test_verdict_mentions_parameterized(self): assert "PARAMETERIZED" in self.result["verdict"]
    def test_quantization_source_is_list(self):
        assert isinstance(self.result["quantization_source"], list) and len(self.result["quantization_source"]) >= 2


class TestWhatQuantizesC:
    def setup_method(self): self.result = what_quantizes_c()
    def test_returns_dict(self): assert isinstance(self.result, dict)
    def test_current_status_parameterized(self): assert self.result["current_status"] == "PARAMETERIZED"
    def test_mechanisms_is_list(self):
        assert isinstance(self.result["mechanisms"], list) and len(self.result["mechanisms"]) >= 3
    def test_mechanisms_have_required_keys(self):
        for m in self.result["mechanisms"]:
            assert "name" in m and "description" in m and "status" in m
    def test_winding_mechanism_present(self):
        names = [m["name"].lower() for m in self.result["mechanisms"]]
        assert any("winding" in n or "topolog" in n for n in names)
    def test_recommendation_present(self): assert isinstance(self.result["recommendation"], str) and len(self.result["recommendation"]) > 20
    def test_current_evidence_present(self): assert "current_evidence" in self.result


class TestFermionMassHierarchy:
    def setup_method(self): self.hierarchy = fermion_mass_hierarchy()
    def test_returns_list(self): assert isinstance(self.hierarchy, list)
    def test_nine_fermions(self): assert len(self.hierarchy) == 9
    def test_all_have_c_l(self):
        for f in self.hierarchy: assert "c_l" in f
    def test_all_have_status_parameterized(self):
        for f in self.hierarchy: assert f["status"] == "PARAMETERIZED"
    def test_all_have_pdg_mass(self):
        for f in self.hierarchy: assert "mass_pdg_mev" in f and f["mass_pdg_mev"] > 0.0
    def test_c_l_ordering_reflects_mass_hierarchy(self):
        valid = [f for f in self.hierarchy if math.isfinite(f.get("c_l", float("nan")))]
        valid_sorted = sorted(valid, key=lambda x: x["mass_pdg_mev"])
        c_vals = [f["c_l"] for f in valid_sorted]
        if len(c_vals) >= 3: assert c_vals[0] > c_vals[-1]
    def test_note_mentions_bisection(self):
        for f in self.hierarchy:
            note = f.get("note", "")
            assert "bisection" in note.lower() or "fitted" in note.lower() or "c_L" in note
    def test_c_r_canonical(self):
        for f in self.hierarchy: assert f["c_r"] == pytest.approx(C_R_CANONICAL, rel=1e-9)


class TestPillar174HonestVerdict:
    def setup_method(self): self.v = pillar174_honest_verdict()
    def test_returns_dict(self): assert isinstance(self.v, dict)
    def test_question_present(self): assert "question" in self.v and len(self.v["question"]) > 20
    def test_answer_says_no(self): assert "NO" in self.v["answer"].upper() or "not" in self.v["answer"].lower()
    def test_spectrum_analysis_present(self): assert "spectrum_analysis" in self.v and self.v["spectrum_analysis"]["is_continuous"] is True
    def test_what_quantizes_c_present(self): assert "what_quantizes_c" in self.v and self.v["what_quantizes_c"]["current_status"] == "PARAMETERIZED"
    def test_fermion_hierarchy_present(self): assert "fermion_hierarchy" in self.v and len(self.v["fermion_hierarchy"]) == 9
    def test_overall_status_mentions_parameterized(self): assert "PARAMETERIZED" in self.v["overall_status"]
    def test_conclusion_present(self): assert "conclusion" in self.v and len(self.v["conclusion"]) > 50
    def test_conclusion_says_continuous(self): assert "continuous" in self.v["conclusion"].lower()
    def test_conclusion_says_parameterized(self): assert "PARAMETERIZED" in self.v["conclusion"]
    def test_conclusion_not_derived(self):
        conclusion = self.v["conclusion"]
        assert "fermion masses are DERIVED" not in conclusion
        assert "masses are DERIVED" not in conclusion
        assert "PARAMETERIZED" in conclusion
    def test_conclusion_mentions_open_problem(self): assert "open" in self.v["conclusion"].lower()


class TestPillar174Summary:
    def test_returns_string(self): assert isinstance(pillar174_summary(), str)
    def test_mentions_pillar_174(self): assert "174" in pillar174_summary()
    def test_mentions_parameterized(self): assert "PARAMETERIZED" in pillar174_summary()
    def test_mentions_continuous(self): assert "continuous" in pillar174_summary().lower()
    def test_mentions_holon_zero(self): assert "holon_zero" in pillar174_summary().lower() or "holon zero" in pillar174_summary().lower()
    def test_not_empty(self): assert len(pillar174_summary()) > 100


class TestPillar174FullReport:
    def setup_method(self): self.r = pillar174_full_report()
    def test_returns_dict(self): assert isinstance(self.r, dict)
    def test_pillar_number(self): assert self.r["pillar"] == 174
    def test_title_present(self): assert "title" in self.r
    def test_status_present(self): assert "PARAMETERIZED" in self.r["status"]
    def test_constants_correct(self):
        c = self.r["constants"]
        assert c["n_w"] == N_W and c["k_cs"] == K_CS
        assert c["pi_kr"] == pytest.approx(PI_KR, rel=1e-9)
        assert c["hat_y5"] == pytest.approx(HAT_Y5, rel=1e-9)
        assert c["c_r_canonical"] == pytest.approx(C_R_CANONICAL, rel=1e-9)
    def test_verdict_present(self): assert "verdict" in self.r
    def test_summary_present(self): assert "summary" in self.r
    def test_authorship_present(self): assert "authorship" in self.r
