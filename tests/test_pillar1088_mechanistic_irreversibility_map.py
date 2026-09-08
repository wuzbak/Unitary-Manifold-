# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 1088 — mechanistic irreversibility map."""

from __future__ import annotations

import math

import pytest

from src.core.pillar1088_mechanistic_irreversibility_map import (
    ADJACENCY_LABEL,
    MAX_EXACT_ORDER,
    NEXT_PILLAR_SLOT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SPRINT,
    TRACK_LABEL,
    VERSION,
    benchmark_cases,
    build_mechanistic_irreversibility_map,
    compare_mechanistic_maps,
    exact_subset_contributions,
    forward_reverse_irreversibility,
    interaction_order_totals,
    pillar1088_mechanistic_irreversibility_report,
    psicat_assist_packet,
)


def _case(case_id: str):
    return next(case for case in benchmark_cases() if case.case_id == case_id)


def _case_report(case_id: str):
    case = _case(case_id)
    return build_mechanistic_irreversibility_map(
        trajectory=case.trajectory,
        component_names=case.component_names,
        case_label=case.label,
        externally_driven_components=case.externally_driven_components,
        purpose=case.purpose,
    )


def test_identity_contract() -> None:
    assert PILLAR_NUMBER == 1088
    assert PILLAR_TITLE == "Mechanistic Irreversibility Map"
    assert PILLAR_STATUS == "ADJACENT_MECHANISTIC_IRREVERSIBILITY_MAP_READY"
    assert VERSION == "v37.0"
    assert SPRINT == "CN"
    assert NEXT_PILLAR_SLOT == 1089
    assert TRACK_LABEL == "MECHANISTIC_IRREVERSIBILITY_DIAGNOSTICS"
    assert ADJACENCY_LABEL == "ADJACENT_RESEARCH_TRACK"
    assert MAX_EXACT_ORDER == 3


def test_benchmark_suite_contract() -> None:
    cases = benchmark_cases()
    assert len(cases) == 4
    assert [case.case_id for case in cases] == [
        "reversible_control",
        "single_component_drive",
        "pair_coupled_cycle",
        "triplet_only_cycle",
    ]


def test_invalid_component_names_raise() -> None:
    with pytest.raises(ValueError):
        build_mechanistic_irreversibility_map(
            trajectory=[(0,), (1,), (0,)],
            component_names=("alpha",),
            case_label="bad",
        )


def test_invalid_trajectory_width_raises() -> None:
    with pytest.raises(ValueError):
        build_mechanistic_irreversibility_map(
            trajectory=[(0, 0), (1, 1), (0, 0)],
            component_names=("alpha", "beta", "gamma"),
            case_label="bad",
        )


def test_invalid_subset_raises() -> None:
    case = _case("pair_coupled_cycle")
    with pytest.raises(ValueError):
        forward_reverse_irreversibility(case.trajectory, case.component_names, subset=(3,))


def test_exact_contributions_reconstruct_full_score_pair_case() -> None:
    case = _case("pair_coupled_cycle")
    exact = exact_subset_contributions(case.trajectory, case.component_names)
    full = forward_reverse_irreversibility(case.trajectory, case.component_names)
    totals = interaction_order_totals(exact, len(case.component_names), full)
    assert math.isclose(totals["reconstructed_total"], full, rel_tol=0.0, abs_tol=1e-12)


def test_reversible_control_scores_zero() -> None:
    report = _case_report("reversible_control")
    assert report["dominant_order"] == "none"
    assert report["total_local_irreversibility"] == pytest.approx(0.0, abs=1e-12)
    assert all(value == pytest.approx(0.0, abs=1e-12) for value in report["order_totals"].values())


def test_single_component_case_is_singleton_dominated() -> None:
    report = _case_report("single_component_drive")
    assert report["dominant_order"] == "singleton"
    assert report["questions_answered"]["mostly_intrinsic"] is True
    assert report["order_fractions"]["singleton"] > 0.99
    assert report["external_internal_balance"]["verdict"] == "EXTERNALLY_DRIVEN_DOMINANT"
    assert report["top_interaction"]["subset_label"] == "alpha"


def test_pair_case_is_pairwise_dominated() -> None:
    report = _case_report("pair_coupled_cycle")
    assert report["dominant_order"] == "pairwise"
    assert report["questions_answered"]["pairwise_explains_majority"] is True
    assert report["questions_answered"]["triplet_required"] is False
    assert report["order_fractions"]["pairwise"] > 0.99
    assert report["top_interaction"]["subset_label"] == "alpha × beta"


def test_triplet_case_requires_collective_structure() -> None:
    report = _case_report("triplet_only_cycle")
    assert report["dominant_order"] == "triplet"
    assert report["questions_answered"]["triplet_required"] is True
    assert report["questions_answered"]["pairwise_explains_majority"] is False
    assert report["order_fractions"]["triplet"] > 0.99
    assert report["top_interaction"]["subset_label"] == "alpha × beta × gamma"


def test_ranked_interactions_are_sorted_deterministically() -> None:
    report = _case_report("pair_coupled_cycle")
    ranked = report["ranked_interactions"]
    scores = [row["exact_contribution"] for row in ranked]
    assert scores == sorted(scores, reverse=True)
    assert ranked[0]["subset_label"] == "alpha × beta"
    assert ranked[-1]["subset_label"] == "gamma"


def test_report_schema_stability() -> None:
    report = _case_report("pair_coupled_cycle")
    assert set(report.keys()) == {
        "case_label",
        "purpose",
        "component_names",
        "trajectory_length",
        "transition_count",
        "total_local_irreversibility",
        "exact_subset_contributions",
        "order_totals",
        "order_fractions",
        "dominant_order",
        "top_interaction",
        "ranked_interactions",
        "external_internal_balance",
        "questions_answered",
        "interpretation",
    }


def test_psicat_packet_contract() -> None:
    report = _case_report("triplet_only_cycle")
    packet = psicat_assist_packet(report)
    assert packet["consumer"] == "PsiCat"
    assert packet["case_label"] == report["case_label"]
    assert packet["dominant_order"] == "triplet"
    assert "pair projection loses the arrow" in packet["recommended_next_question"]


def test_comparison_surface_detects_order_shift() -> None:
    pair = _case_report("pair_coupled_cycle")
    triplet = _case_report("triplet_only_cycle")
    comparison = compare_mechanistic_maps(pair, triplet)
    assert comparison["dominant_order_shift"] == ["pairwise", "triplet"]
    assert comparison["fraction_deltas"]["pairwise"] < 0.0
    assert comparison["fraction_deltas"]["triplet"] > 0.0


def test_full_pillar_report_contract() -> None:
    report = pillar1088_mechanistic_irreversibility_report()
    assert report["pillar"] == 1088
    assert report["status"] == PILLAR_STATUS
    assert report["version"] == VERSION
    assert report["sprint"] == SPRINT
    assert report["next_pillar_slot"] == 1089
    assert report["adjacency_label"] == ADJACENCY_LABEL
    assert len(report["benchmark_suite"]) == 4
    assert report["anchors"]["pillar471_monotonicity_requirement"]["canonical_candidate"] == "B_mu"
    assert report["anchors"]["dissipation_geometry_anchor"]["second_law_satisfied"] is True
    assert report["pair_vs_triplet_comparison"]["dominant_order_shift"] == ["pairwise", "triplet"]


def test_all_exact_contributions_non_negative_in_benchmarks() -> None:
    for case in benchmark_cases():
        report = _case_report(case.case_id)
        for row in report["exact_subset_contributions"]:
            assert row["exact_contribution"] >= -1e-12
