# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for RS1/5D Completeness Audit Certificate (Pillar 225, Track A Session 8)."""

import pytest

from src.core.rs1_5d_completeness_audit import (
    N_W, K_CS,
    N_DERIVED, N_CONSTRAINED, N_TOTAL,
    TOE_SCORE_5D,
    N_ARCHITECTURE_LIMITS,
    ARCHITECTURE_LIMIT_KEYS,
    derived_quantities_catalog,
    architecture_limits_catalog,
    toe_score_calculation,
    completeness_certificate,
    five_d_boundary_statement,
    rs1_completeness_audit,
    pillar225_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_derived_positive(self):
        assert N_DERIVED > 0

    def test_n_constrained_nonneg(self):
        assert N_CONSTRAINED >= 0

    def test_n_total_at_least_n_derived(self):
        assert N_TOTAL >= N_DERIVED

    def test_toe_score_between_0_and_1(self):
        assert 0 < TOE_SCORE_5D <= 1.0

    def test_toe_score_formula(self):
        expected = (N_DERIVED + N_CONSTRAINED * 0.5) / N_TOTAL
        assert TOE_SCORE_5D == pytest.approx(expected, rel=1e-6)

    def test_n_architecture_limits_positive(self):
        assert N_ARCHITECTURE_LIMITS > 0

    def test_architecture_limit_keys_tuple(self):
        assert isinstance(ARCHITECTURE_LIMIT_KEYS, tuple)
        assert len(ARCHITECTURE_LIMIT_KEYS) == N_ARCHITECTURE_LIMITS


class TestDerivedQuantitiesCatalog:
    def test_returns_list(self):
        result = derived_quantities_catalog()
        assert isinstance(result, list)

    def test_has_at_least_n_derived_plus_constrained(self):
        result = derived_quantities_catalog()
        assert len(result) >= N_DERIVED

    def test_all_have_id(self):
        for q in derived_quantities_catalog():
            assert "id" in q

    def test_all_have_status(self):
        for q in derived_quantities_catalog():
            assert "status" in q

    def test_all_have_quantity(self):
        for q in derived_quantities_catalog():
            assert "quantity" in q

    def test_all_have_value(self):
        for q in derived_quantities_catalog():
            assert "value" in q

    def test_has_ns_entry(self):
        quantities = [q["quantity"] for q in derived_quantities_catalog()]
        assert any("nₛ" in q or "spectral" in q.lower() for q in quantities)

    def test_has_higgs_vev_entry(self):
        quantities = [q["quantity"] for q in derived_quantities_catalog()]
        assert any("Higgs" in q or "higgs" in q.lower() or "VEV" in q for q in quantities)

    def test_has_n_gen_entry(self):
        quantities = [q["quantity"] for q in derived_quantities_catalog()]
        assert any("gen" in q.lower() or "N_gen" in q for q in quantities)

    def test_derived_count_matches_constant(self):
        result = derived_quantities_catalog()
        actual_derived = sum(1 for q in result if q["status"] != "CONSTRAINED")
        assert actual_derived == N_DERIVED


class TestArchitectureLimitsCatalog:
    def test_returns_list(self):
        result = architecture_limits_catalog()
        assert isinstance(result, list)

    def test_has_n_architecture_limits_entries(self):
        result = architecture_limits_catalog()
        assert len(result) == N_ARCHITECTURE_LIMITS

    def test_all_have_id(self):
        for entry in architecture_limits_catalog():
            assert "id" in entry

    def test_all_have_requires_dimension(self):
        for entry in architecture_limits_catalog():
            assert "requires_dimension" in entry

    def test_all_have_brief(self):
        for entry in architecture_limits_catalog():
            assert "brief" in entry

    def test_cc_is_in_catalog(self):
        ids = [e["id"] for e in architecture_limits_catalog()]
        assert "A-1_cosmological_constant" in ids

    def test_sugra_requires_11d(self):
        catalog = architecture_limits_catalog()
        sugra = next(e for e in catalog if "supersymmetry" in e["id"])
        assert sugra["requires_dimension"] == 11


class TestToEScoreCalculation:
    def test_returns_dict(self):
        result = toe_score_calculation()
        assert isinstance(result, dict)

    def test_has_n_derived(self):
        result = toe_score_calculation()
        assert result["n_derived"] == N_DERIVED

    def test_has_n_constrained(self):
        result = toe_score_calculation()
        assert result["n_constrained"] == N_CONSTRAINED

    def test_score_between_0_and_1(self):
        result = toe_score_calculation()
        assert 0 < result["toe_score_5d"] <= 1.0

    def test_score_percentage_string(self):
        result = toe_score_calculation()
        assert "%" in result["toe_score_percent"]

    def test_honest_statement_present(self):
        result = toe_score_calculation()
        assert len(result["honest_statement"]) > 50

    def test_next_rung_priority_present(self):
        result = toe_score_calculation()
        assert "next_rung_priority" in result

    def test_next_rung_mentions_6d(self):
        result = toe_score_calculation()
        assert "6D" in result["next_rung_priority"]


class TestCompletenessCertificate:
    def test_returns_dict(self):
        result = completeness_certificate()
        assert isinstance(result, dict)

    def test_version_present(self):
        result = completeness_certificate()
        assert "version" in result

    def test_pillar_225(self):
        result = completeness_certificate()
        assert result["pillar"] == 225

    def test_has_toe_score(self):
        result = completeness_certificate()
        assert "toe_score" in result

    def test_has_derived_quantities(self):
        result = completeness_certificate()
        assert "derived_quantities" in result

    def test_has_architecture_limits(self):
        result = completeness_certificate()
        assert "architecture_limits" in result

    def test_next_rung_mentions_6d(self):
        result = completeness_certificate()
        assert "6D" in result["next_dimensional_rung"]["target"]

    def test_next_rung_mechanism_t2z3(self):
        result = completeness_certificate()
        assert "T²/Z₃" in result["next_dimensional_rung"]["mechanism"] or \
               "T2" in result["next_dimensional_rung"]["mechanism"]


class TestFiveDeBoundaryStatement:
    def test_returns_string(self):
        stmt = five_d_boundary_statement()
        assert isinstance(stmt, str)

    def test_long_enough(self):
        stmt = five_d_boundary_statement()
        assert len(stmt) > 200

    def test_mentions_6d_transition(self):
        stmt = five_d_boundary_statement()
        assert "6D" in stmt

    def test_mentions_architecture_limit_or_boundary(self):
        stmt = five_d_boundary_statement()
        assert "ARCHITECTURE_LIMIT" in stmt or "boundary" in stmt.lower()


class TestRS1CompletenessAudit:
    def test_returns_dict(self):
        result = rs1_completeness_audit()
        assert isinstance(result, dict)

    def test_module_name(self):
        result = rs1_completeness_audit()
        assert result["module"] == "rs1_5d_completeness_audit"

    def test_pillar_225(self):
        result = rs1_completeness_audit()
        assert result["pillar"] == 225

    def test_has_certificate(self):
        result = rs1_completeness_audit()
        assert "certificate" in result

    def test_quick_summary_present(self):
        result = rs1_completeness_audit()
        assert "quick_summary" in result

    def test_toe_score_in_summary(self):
        result = rs1_completeness_audit()
        assert "toe_score_5d" in result["quick_summary"]

    def test_architecture_limits_by_dimension(self):
        result = rs1_completeness_audit()
        summary = result["quick_summary"]
        assert "architecture_limits_require" in summary
        dims = summary["architecture_limits_require"]
        assert "6D" in dims
        assert "10D" in dims
        assert "11D" in dims


class TestPillar225Summary:
    def test_returns_dict(self):
        s = pillar225_summary()
        assert isinstance(s, dict)

    def test_pillar_225(self):
        s = pillar225_summary()
        assert s["pillar"] == 225

    def test_toe_score_between_0_and_1(self):
        s = pillar225_summary()
        assert 0 < s["toe_score_5d"] <= 1.0

    def test_n_derived_matches(self):
        s = pillar225_summary()
        assert s["n_derived"] == N_DERIVED

    def test_next_rung_mentions_6d(self):
        s = pillar225_summary()
        assert "6D" in s["next_rung"]
