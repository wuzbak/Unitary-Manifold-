# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar380_borel_pade_gamma_bound.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar380_borel_pade_gamma_bound import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    GAMMA_THEORY, GAMMA_FIT, GAMMA_DISCREPANCY, K_CS, ALPHA_GUT, C_S,
    separation_guard,
    borel_transform_analysis,
    large_k_expansion,
    zamolodchikov_c_theorem_bound,
    renormalon_estimate,
    finite_k_correction_coefficient,
    gamma_bound_synthesis,
    l2_bounded_certificate,
    pillar380_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 380
    def test_status(self): assert PILLAR_STATUS == "L2_BOUNDED_NON_PERTURBATIVE"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_gamma_theory(self): assert abs(GAMMA_THEORY - 0.242) < 1e-6
    def test_gamma_fit(self): assert abs(GAMMA_FIT - 0.273) < 1e-6
    def test_gamma_discrepancy_positive(self): assert GAMMA_DISCREPANCY > 0
    def test_gamma_discrepancy_13pct(self):
        assert abs(GAMMA_DISCREPANCY - (GAMMA_FIT - GAMMA_THEORY) / GAMMA_THEORY) < 1e-6
    def test_k_cs(self): assert K_CS == 74
    def test_alpha_gut(self): assert abs(ALPHA_GUT - 3.0/74.0) < 1e-10
    def test_c_s(self): assert abs(C_S - 12.0/37.0) < 1e-10


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_l2_bounded(self): assert "L2_BOUNDED" in separation_guard()


class TestBorelTransformAnalysis:
    def test_returns_dict(self): assert isinstance(borel_transform_analysis(), dict)

    def test_all_np_suppressed(self):
        r = borel_transform_analysis()
        assert r["all_np_contributions_negligible"] is True

    def test_np_ir_renormalon_tiny(self):
        r = borel_transform_analysis()
        assert r["np_contribution_ir_renormalon"] < 1e-100

    def test_np_uv_renormalon_tiny(self):
        r = borel_transform_analysis()
        assert r["np_contribution_uv_renormalon"] < 1e-100

    def test_np_instanton_tiny(self):
        r = borel_transform_analysis()
        assert r["np_contribution_instanton"] < 1e-100

    def test_t_ir_equals_k_cs(self):
        r = borel_transform_analysis()
        assert abs(r["t_ir_renormalon"] - K_CS) < 1e-10

    def test_t_uv_equals_2k_cs(self):
        r = borel_transform_analysis()
        assert abs(r["t_uv_renormalon"] - 2 * K_CS) < 1e-10

    def test_verdict_suppressed(self):
        r = borel_transform_analysis()
        assert "SUPPRESSED" in r["verdict"].upper()

    def test_s_instanton_large(self):
        r = borel_transform_analysis()
        assert r["s_instanton"] > 1000


class TestLargeKExpansion:
    def test_returns_dict(self): assert isinstance(large_k_expansion(), dict)

    def test_c1_positive(self):
        r = large_k_expansion()
        assert r["c1_coefficient"] > 0

    def test_c1_physically_reasonable(self):
        r = large_k_expansion()
        assert r["c1_physically_reasonable"] is True

    def test_c1_in_expected_range(self):
        r = large_k_expansion()
        c1 = r["c1_coefficient"]
        assert 0 < c1 <= K_CS

    def test_delta_gamma_correct(self):
        r = large_k_expansion()
        assert abs(r["delta_gamma"] - (GAMMA_FIT - GAMMA_THEORY)) < 1e-10

    def test_c1_from_k_delta_gamma(self):
        r = large_k_expansion()
        expected_c1 = K_CS * (GAMMA_FIT - GAMMA_THEORY)
        assert abs(r["c1_coefficient"] - expected_c1) < 1e-10

    def test_two_loop_tiny(self):
        r = large_k_expansion()
        assert r["delta_gamma_2loop"] < 1e-3

    def test_two_loop_ratio_small(self):
        r = large_k_expansion()
        assert r["two_loop_vs_gap_ratio"] < 0.01

    def test_gamma_large_k_limit(self):
        r = large_k_expansion()
        assert abs(r["gamma_large_k_limit"] - GAMMA_THEORY) < 1e-6


class TestZamolodchikovCTheoremBound:
    def test_returns_dict(self): assert isinstance(zamolodchikov_c_theorem_bound(), dict)

    def test_c_uv_positive(self):
        r = zamolodchikov_c_theorem_bound()
        assert r["c_uv"] > 0

    def test_c_uv_less_than_3(self):
        r = zamolodchikov_c_theorem_bound()
        assert r["c_uv"] < 3.0

    def test_c_uv_formula(self):
        r = zamolodchikov_c_theorem_bound()
        expected = 3.0 * K_CS / (K_CS + 2.0)
        assert abs(r["c_uv"] - expected) < 1e-10

    def test_bound_too_weak(self):
        r = zamolodchikov_c_theorem_bound()
        assert r["gamma_bound_vacuum_floor"] < GAMMA_FIT - GAMMA_THEORY

    def test_c_theorem_cannot_explain_gap(self):
        r = zamolodchikov_c_theorem_bound()
        assert r["c_theorem_explains_gap"] is False


class TestRenormalonEstimate:
    def test_returns_dict(self): assert isinstance(renormalon_estimate(), dict)
    def test_viable_route(self):
        r = renormalon_estimate()
        assert r["only_viable_route"] == "finite_k_correction"
    def test_gap_to_explain_correct(self):
        r = renormalon_estimate()
        assert abs(r["gap_to_explain"] - (GAMMA_FIT - GAMMA_THEORY)) < 1e-10
    def test_three_suppressed_routes(self):
        r = renormalon_estimate()
        suppressed = [v for k, v in r["all_routes"].items() if "SUPPRESSED" in v["verdict"]]
        assert len(suppressed) >= 3


class TestFiniteKCorrectionCoefficient:
    def test_returns_dict(self): assert isinstance(finite_k_correction_coefficient(), dict)
    def test_c1_in_wzw_range(self):
        r = finite_k_correction_coefficient()
        assert r["c1_in_wzw_range"] is True
    def test_verdict_present(self):
        r = finite_k_correction_coefficient()
        assert "verdict" in r
        assert len(r["verdict"]) > 20


class TestGammaBoundSynthesis:
    def test_returns_dict(self): assert isinstance(gamma_bound_synthesis(), dict)

    def test_new_status(self):
        r = gamma_bound_synthesis()
        assert r["new_status"] == "L2_BOUNDED_NON_PERTURBATIVE"

    def test_approach_a_np_suppressed(self):
        r = gamma_bound_synthesis()
        assert r["approach_a_borel"]["all_np_suppressed"] is True

    def test_approach_b_c1_reasonable(self):
        r = gamma_bound_synthesis()
        assert r["approach_b_large_k"]["physically_reasonable"] is True

    def test_approach_c_not_applicable(self):
        r = gamma_bound_synthesis()
        assert r["approach_c_c_theorem"]["applicable_to_gamma"] is False

    def test_gamma_values_correct(self):
        r = gamma_bound_synthesis()
        assert abs(r["gamma_theory"] - GAMMA_THEORY) < 1e-6
        assert abs(r["gamma_fit"] - GAMMA_FIT) < 1e-6


class TestL2BoundedCertificate:
    def test_returns_dict(self): assert isinstance(l2_bounded_certificate(), dict)

    def test_all_conditions_met(self):
        r = l2_bounded_certificate()
        assert r["all_conditions_met"] is True

    def test_previous_status(self):
        r = l2_bounded_certificate()
        assert r["previous_status"] == "L2_PARTIALLY_CLOSED"

    def test_new_status(self):
        r = l2_bounded_certificate()
        assert r["new_status"] == "L2_BOUNDED_NON_PERTURBATIVE"

    def test_certificate_status(self):
        r = l2_bounded_certificate()
        assert "L2_BOUNDED_NON_PERTURBATIVE" in r["certificate_status"]

    def test_gap_fraction(self):
        r = l2_bounded_certificate()
        assert abs(r["gap_fraction"] - GAMMA_DISCREPANCY) < 1e-10


class TestPillar380Summary:
    def test_returns_dict(self): assert isinstance(pillar380_summary(), dict)
    def test_pillar_number(self):
        r = pillar380_summary()
        assert r["pillar_number"] == PILLAR_NUMBER
    def test_status(self):
        r = pillar380_summary()
        assert r["status"] == "L2_BOUNDED_NON_PERTURBATIVE"
    def test_key_result(self):
        r = pillar380_summary()
        assert "key_result" in r
        assert "13%" in r["key_result"] or "0.242" in r["key_result"]
    def test_previous_status(self):
        r = pillar380_summary()
        assert r["previous_status"] == "L2_PARTIALLY_CLOSED"
