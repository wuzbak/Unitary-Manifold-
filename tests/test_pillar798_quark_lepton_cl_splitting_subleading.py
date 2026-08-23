# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 798 — QUARK_LEPTON_CL_SPLITTING_SUBLEADING
~60 tests covering the Casimir CS splitting formula, per-generation
values, comparison with bisection, and literature validation.
"""
import math
import pytest
from src.core.pillar798_quark_lepton_cl_splitting_subleading import (
    N_C,
    K_CS,
    N_W,
    CASIMIR_QUARK,
    CASIMIR_LEPTON,
    CL_TOPO_BASE,
    ALPHA_GUT_GEO,
    DELTA_CL_QUARK,
    DELTA_CL_LEPTON,
    PILLAR_798_GATE,
    cl_lepton,
    cl_quark,
    splitting_delta_cl,
    casimir_cs_splitting_formula,
    comparison_with_bisection,
    literature_validation,
    remaining_open_items,
    pillar798_summary,
    PILLAR_798_SUMMARY,
)


class TestConstants:
    def test_gate(self):
        assert PILLAR_798_GATE == "QUARK_LEPTON_CL_REQUIRES_FN_CHARGE"

    def test_n_c(self):
        assert N_C == 3

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_casimir_quark_value(self):
        expected = (N_C**2 - 1) / (2 * N_C)
        assert abs(CASIMIR_QUARK - expected) < 1e-12

    def test_casimir_quark_is_four_thirds(self):
        assert abs(CASIMIR_QUARK - 4/3) < 1e-12

    def test_casimir_lepton_zero(self):
        assert CASIMIR_LEPTON == 0.0

    def test_alpha_gut_geo(self):
        assert abs(ALPHA_GUT_GEO - 3/74) < 1e-12

    def test_cl_topo_base(self):
        assert abs(CL_TOPO_BASE - 71/74) < 1e-12

    def test_delta_cl_quark_negative(self):
        assert DELTA_CL_QUARK < 0.0

    def test_delta_cl_lepton_zero(self):
        assert DELTA_CL_LEPTON == 0.0

    def test_delta_cl_quark_formula(self):
        expected = -CASIMIR_QUARK / K_CS
        assert abs(DELTA_CL_QUARK - expected) < 1e-12

    def test_delta_cl_magnitude(self):
        # Should be -4/(3×74) = -4/222 ≈ -0.01802
        assert abs(DELTA_CL_QUARK - (-4/222)) < 1e-12


class TestCLLepton:
    def test_gen1(self):
        expected = CL_TOPO_BASE
        assert abs(cl_lepton(1) - expected) < 1e-12

    def test_gen2(self):
        expected = CL_TOPO_BASE - 1/(2*K_CS)
        assert abs(cl_lepton(2) - expected) < 1e-12

    def test_gen3(self):
        expected = CL_TOPO_BASE - 2/(2*K_CS)
        assert abs(cl_lepton(3) - expected) < 1e-12

    def test_ladder_decreasing(self):
        assert cl_lepton(1) > cl_lepton(2) > cl_lepton(3)

    def test_all_positive(self):
        for g in (1, 2, 3):
            assert cl_lepton(g) > 0.0

    def test_invalid_gen_raises(self):
        with pytest.raises(AssertionError):
            cl_lepton(4)


class TestCLQuark:
    def test_quark_less_than_lepton_same_gen(self):
        for g in (1, 2, 3):
            assert cl_quark(g) < cl_lepton(g)

    def test_splitting_constant_across_gens(self):
        for g in (1, 2, 3):
            diff = cl_lepton(g) - cl_quark(g)
            assert abs(diff - (-DELTA_CL_QUARK)) < 1e-12

    def test_gen1_value(self):
        expected = CL_TOPO_BASE + DELTA_CL_QUARK
        assert abs(cl_quark(1) - expected) < 1e-12

    def test_all_positive(self):
        for g in (1, 2, 3):
            assert cl_quark(g) > 0.0

    def test_ladder_decreasing(self):
        assert cl_quark(1) > cl_quark(2) > cl_quark(3)

    def test_invalid_gen_raises(self):
        with pytest.raises(AssertionError):
            cl_quark(0)


class TestSplitting:
    def test_splitting_three_gens(self):
        s = splitting_delta_cl()
        assert len(s) == 3

    def test_splitting_all_gens_present(self):
        s = splitting_delta_cl()
        assert 1 in s and 2 in s and 3 in s

    def test_splitting_quark_less_than_lepton(self):
        s = splitting_delta_cl()
        for g in (1, 2, 3):
            assert s[g]['c_L_quark'] < s[g]['c_L_lepton']

    def test_splitting_constant_across_gens(self):
        s = splitting_delta_cl()
        deltas = [s[g]['delta_cl_quark_minus_lepton'] for g in (1, 2, 3)]
        for d in deltas:
            assert abs(d - deltas[0]) < 1e-12

    def test_splitting_sign_negative(self):
        s = splitting_delta_cl()
        for g in (1, 2, 3):
            assert s[g]['delta_cl_quark_minus_lepton'] < 0.0


class TestCasimirFormula:
    def test_formula_value(self):
        f = casimir_cs_splitting_formula()
        expected = -4/222
        assert abs(f['value'] - expected) < 1e-12

    def test_zero_free_parameters(self):
        f = casimir_cs_splitting_formula()
        assert f['free_parameters'] == 0

    def test_simplified_string(self):
        f = casimir_cs_splitting_formula()
        assert '222' in f['simplified']

    def test_formula_string_present(self):
        f = casimir_cs_splitting_formula()
        assert 'C_F' in f['formula']


class TestBisectionComparison:
    def test_topo_vs_bisection_keys(self):
        c = comparison_with_bisection()
        assert 'topological_cl_lepton_g1' in c
        assert 'bisection_cl_electron' in c

    def test_topo_lepton_g1_near_71over74(self):
        c = comparison_with_bisection()
        assert abs(c['topological_cl_lepton_g1'] - 71/74) < 1e-12

    def test_honest_status_in_result(self):
        c = comparison_with_bisection()
        assert c['honest_status'] == PILLAR_798_GATE

    def test_gap_between_topo_and_bisection(self):
        c = comparison_with_bisection()
        # topo lepton G1 ≈ 0.9595; bisection electron ≈ 0.7980 — significant gap
        assert c['topo_lepton_vs_bisection_electron_gap'] > 0.1


class TestLiteratureValidation:
    def test_reference_contains_arxiv(self):
        v = literature_validation()
        assert '2604.22403' in v['reference']

    def test_validation_status(self):
        v = literature_validation()
        assert 'VALIDATED' in v['validation']

    def test_parallel_explanation(self):
        v = literature_validation()
        assert len(v['um_parallel']) > 50


class TestRemainingOpen:
    def test_open_items_present(self):
        items = remaining_open_items()
        assert len(items) >= 2

    def test_aps_open(self):
        items = remaining_open_items()
        labels = [i['item'] for i in items]
        assert any('APS' in l for l in labels)

    def test_fn_open(self):
        items = remaining_open_items()
        labels = [i['item'] for i in items]
        assert any('FN' in l for l in labels)


class TestSummary:
    def test_summary_pillar(self):
        s = pillar798_summary()
        assert s['pillar'] == 798

    def test_summary_gate(self):
        s = pillar798_summary()
        assert s['gate'] == PILLAR_798_GATE

    def test_summary_has_honest(self):
        s = pillar798_summary()
        assert 'honest_summary' in s

    def test_summary_honest_mentions_mechanism(self):
        s = pillar798_summary()
        assert 'mechanism' in s['honest_summary'].lower()

    def test_summary_alias(self):
        s = PILLAR_798_SUMMARY()
        assert s['pillar'] == 798
