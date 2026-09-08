# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1088 — mechanistic irreversibility map.

Adjacent research track (non-hardgate): this module turns abstract arrow-of-time
language into a machine-readable interaction map. It does not claim a final
ontological derivation of time's arrow. Its job is narrower and practical:
locate where irreversibility lives inside an interacting system and identify
whether the dominant carrier is intrinsic, pairwise, triplet, or genuinely
collective.

The implementation is intentionally benchmark-first. It uses controlled
synthetic trajectories so the decomposition can be checked against known
interaction structure before any biological or observational extension.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
import math
from typing import Any, Iterable, Sequence

from src.core.adm_entropy_production_rate import adm_entropy_rate
from src.core.dissipation_geometry import (
    GAMMA_CANONICAL,
    lindblad_entropy_production,
    second_law_check,
)
from src.core.pillar471_irreversibility_uniqueness import monotonicity_requirement

PILLAR_NUMBER = 1088
PILLAR_TITLE = "Mechanistic Irreversibility Map"
PILLAR_STATUS = "ADJACENT_MECHANISTIC_IRREVERSIBILITY_MAP_READY"
VERSION = "v37.0"
SPRINT = "CN"
NEXT_PILLAR_SLOT = 1089
ADJACENCY_LABEL = "ADJACENT_RESEARCH_TRACK"
TRACK_LABEL = "MECHANISTIC_IRREVERSIBILITY_DIAGNOSTICS"
MAX_EXACT_ORDER = 3
EPSILON = 1e-12

__all__ = [
    "ADJACENCY_LABEL",
    "BenchmarkCase",
    "EPSILON",
    "MAX_EXACT_ORDER",
    "NEXT_PILLAR_SLOT",
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "SPRINT",
    "TRACK_LABEL",
    "VERSION",
    "benchmark_cases",
    "build_mechanistic_irreversibility_map",
    "compare_mechanistic_maps",
    "exact_subset_contributions",
    "forward_reverse_irreversibility",
    "interaction_order_totals",
    "pillar1088_mechanistic_irreversibility_report",
    "psicat_assist_packet",
]


@dataclass(frozen=True)
class BenchmarkCase:
    """Controlled benchmark for irreversibility decomposition."""

    case_id: str
    label: str
    component_names: tuple[str, ...]
    trajectory: tuple[tuple[int, ...], ...]
    expected_dominant_order: str
    purpose: str
    externally_driven_components: tuple[str, ...] = ()


def _validate_component_names(component_names: Sequence[str]) -> tuple[str, ...]:
    names = tuple(str(name) for name in component_names)
    if len(names) < 2:
        raise ValueError("Need at least two components for an interaction map")
    if len(set(names)) != len(names):
        raise ValueError("Component names must be unique")
    if any(not name for name in names):
        raise ValueError("Component names must be non-empty")
    return names


def _validate_trajectory(
    trajectory: Sequence[Sequence[int]],
    component_names: Sequence[str],
) -> tuple[tuple[int, ...], ...]:
    names = _validate_component_names(component_names)
    states = tuple(tuple(int(value) for value in state) for state in trajectory)
    if len(states) < 3:
        raise ValueError("Need at least three time points")
    width = len(names)
    if any(len(state) != width for state in states):
        raise ValueError("Every trajectory state must match component count")
    return states


def _subset_label(indices: Iterable[int], component_names: Sequence[str]) -> str:
    return " × ".join(component_names[index] for index in indices)


def _project_state(state: Sequence[int], subset: Sequence[int]) -> tuple[int, ...]:
    return tuple(state[index] for index in subset)


def _transition_counts(
    trajectory: Sequence[Sequence[int]],
    subset: Sequence[int],
) -> Counter[tuple[tuple[int, ...], tuple[int, ...]]]:
    projected = [_project_state(state, subset) for state in trajectory]
    return Counter(zip(projected[:-1], projected[1:]))


def _kl_from_forward_reverse(
    counts: Counter[tuple[tuple[int, ...], tuple[int, ...]]],
) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    keys = set(counts) | {(dst, src) for (src, dst) in counts}
    score = 0.0
    for edge in keys:
        p = counts.get(edge, 0) / total
        q = counts.get((edge[1], edge[0]), 0) / total
        if p > 0.0:
            score += p * math.log(p / max(q, EPSILON))
    return float(score)


def forward_reverse_irreversibility(
    trajectory: Sequence[Sequence[int]],
    component_names: Sequence[str],
    subset: Sequence[int] | None = None,
) -> float:
    """Return forward-vs-reverse irreversibility for a subset trajectory."""

    names = _validate_component_names(component_names)
    states = _validate_trajectory(trajectory, names)
    chosen_subset = tuple(range(len(names))) if subset is None else tuple(subset)
    if not chosen_subset:
        raise ValueError("Subset must be non-empty")
    if any(index < 0 or index >= len(names) for index in chosen_subset):
        raise ValueError("Subset index out of range")
    counts = _transition_counts(states, chosen_subset)
    return _kl_from_forward_reverse(counts)


def exact_subset_contributions(
    trajectory: Sequence[Sequence[int]],
    component_names: Sequence[str],
    max_exact_order: int = MAX_EXACT_ORDER,
) -> dict[tuple[int, ...], float]:
    """Möbius-style exact contributions for subsets up to max_exact_order."""

    names = _validate_component_names(component_names)
    states = _validate_trajectory(trajectory, names)
    max_order = min(int(max_exact_order), len(names))
    if max_order < 1:
        raise ValueError("max_exact_order must be positive")

    subset_scores: dict[tuple[int, ...], float] = {}
    exact: dict[tuple[int, ...], float] = {}
    for order in range(1, max_order + 1):
        for subset in combinations(range(len(names)), order):
            score = forward_reverse_irreversibility(states, names, subset=subset)
            subset_scores[subset] = score
            contribution = score
            for sub_order in range(1, order):
                for smaller in combinations(subset, sub_order):
                    contribution -= exact[smaller]
            if abs(contribution) < 1e-12:
                contribution = 0.0
            exact[subset] = float(contribution)
    return exact


def interaction_order_totals(
    exact_contributions: dict[tuple[int, ...], float],
    component_count: int,
    full_system_score: float,
) -> dict[str, float]:
    """Aggregate singleton/pairwise/triplet/higher-order totals."""

    singleton = sum(value for key, value in exact_contributions.items() if len(key) == 1)
    pairwise = sum(value for key, value in exact_contributions.items() if len(key) == 2)
    triplet = sum(value for key, value in exact_contributions.items() if len(key) == 3)
    covered = singleton + pairwise + triplet
    higher = 0.0 if component_count <= 3 else full_system_score - covered
    if abs(higher) < 1e-12:
        higher = 0.0
    return {
        "singleton": float(singleton),
        "pairwise": float(pairwise),
        "triplet": float(triplet),
        "higher_order_residual": float(higher),
        "reconstructed_total": float(covered + higher),
    }


def _fractions(order_totals: dict[str, float], total: float) -> dict[str, float]:
    if total <= 0.0:
        return {key: 0.0 for key in order_totals if key != "reconstructed_total"}
    return {
        key: float(value / total)
        for key, value in order_totals.items()
        if key != "reconstructed_total"
    }


def _dominant_order(order_totals: dict[str, float]) -> str:
    candidates = {
        "singleton": order_totals["singleton"],
        "pairwise": order_totals["pairwise"],
        "triplet": order_totals["triplet"],
        "higher_order_residual": order_totals["higher_order_residual"],
    }
    best = max(candidates.items(), key=lambda item: (item[1], item[0]))
    return "none" if best[1] <= 1e-12 else best[0]


def _ranking_rows(
    exact_contributions: dict[tuple[int, ...], float],
    component_names: Sequence[str],
) -> list[dict[str, Any]]:
    rows = []
    for subset, value in exact_contributions.items():
        rows.append(
            {
                "subset": list(subset),
                "subset_label": _subset_label(subset, component_names),
                "order": len(subset),
                "exact_contribution": float(value),
            }
        )
    rows.sort(key=lambda row: (-row["exact_contribution"], row["order"], row["subset_label"]))
    return rows


def _external_internal_split(
    exact_contributions: dict[tuple[int, ...], float],
    component_names: Sequence[str],
    externally_driven_components: Sequence[str],
) -> dict[str, Any]:
    driven = set(externally_driven_components)
    total = sum(exact_contributions.values())
    if not driven:
        intrinsic = sum(value for key, value in exact_contributions.items() if len(key) == 1)
        coupling = total - intrinsic
        verdict = (
            "INTERNAL_COUPLING_DOMINATED"
            if coupling > intrinsic + 1e-12
            else "COMPONENT_INTRINSIC_DOMINATED"
        )
        return {
            "externally_driven_components": [],
            "externally_driven_share": 0.0,
            "internally_generated_share": 1.0 if total > 0.0 else 0.0,
            "verdict": verdict if total > 0.0 else "NO_IRREVERSIBILITY_DETECTED",
        }

    driven_indices = {index for index, name in enumerate(component_names) if name in driven}
    driven_mass = sum(
        value
        for subset, value in exact_contributions.items()
        if any(index in driven_indices for index in subset)
    )
    internal_mass = max(total - driven_mass, 0.0)
    if total <= 0.0:
        verdict = "NO_IRREVERSIBILITY_DETECTED"
    elif driven_mass >= internal_mass:
        verdict = "EXTERNALLY_DRIVEN_DOMINANT"
    else:
        verdict = "INTERNALLY_GENERATED_DOMINANT"
    return {
        "externally_driven_components": list(externally_driven_components),
        "externally_driven_share": 0.0 if total <= 0.0 else float(driven_mass / total),
        "internally_generated_share": 0.0 if total <= 0.0 else float(internal_mass / total),
        "verdict": verdict,
    }


def _interpretation(
    dominant_order: str,
    total: float,
    external_internal: dict[str, Any],
    top_ranking: list[dict[str, Any]],
) -> str:
    if total <= 1e-12:
        return "No measurable forward-vs-reverse asymmetry is detected in this control trajectory."
    leader = top_ranking[0]["subset_label"] if top_ranking else "none"
    if dominant_order == "singleton":
        return (
            "Irreversibility is concentrated in single-component dynamics, so the"
            f" main arrow carrier is intrinsic/local rather than distributed coupling; top carrier: {leader}."
        )
    if dominant_order == "pairwise":
        return (
            "Pairwise couplings carry most of the arrow, indicating that ordinary"
            f" two-body interaction structure is sufficient to explain the observed asymmetry; top carrier: {leader}."
        )
    if dominant_order == "triplet":
        return (
            "The arrow survives only at genuine three-body level, so pair reductions"
            f" would miss the mechanism; top collective carrier: {leader}."
        )
    if dominant_order == "higher_order_residual":
        return (
            "Irreversibility remains after singleton/pair/triplet accounting, so the"
            " system likely contains larger collective structure not reducible to low-order maps."
        )
    return f"Dominant source classification is {external_internal['verdict']}."


def build_mechanistic_irreversibility_map(
    trajectory: Sequence[Sequence[int]],
    component_names: Sequence[str],
    case_label: str,
    externally_driven_components: Sequence[str] = (),
    purpose: str = "",
) -> dict[str, Any]:
    """Build a machine-readable irreversibility map for one system."""

    names = _validate_component_names(component_names)
    states = _validate_trajectory(trajectory, names)
    exact = exact_subset_contributions(states, names)
    full_score = forward_reverse_irreversibility(states, names)
    order_totals = interaction_order_totals(exact, len(names), full_score)
    fractions = _fractions(order_totals, full_score)
    ranking = _ranking_rows(exact, names)
    dominant_order = _dominant_order(order_totals)
    external_internal = _external_internal_split(exact, names, externally_driven_components)
    top_subset = ranking[0] if ranking else None

    return {
        "case_label": case_label,
        "purpose": purpose,
        "component_names": list(names),
        "trajectory_length": len(states),
        "transition_count": len(states) - 1,
        "total_local_irreversibility": float(full_score),
        "exact_subset_contributions": [
            {
                "subset": list(subset),
                "subset_label": _subset_label(subset, names),
                "order": len(subset),
                "exact_contribution": float(value),
            }
            for subset, value in sorted(exact.items(), key=lambda item: (len(item[0]), item[0]))
        ],
        "order_totals": order_totals,
        "order_fractions": fractions,
        "dominant_order": dominant_order,
        "top_interaction": top_subset,
        "ranked_interactions": ranking,
        "external_internal_balance": external_internal,
        "questions_answered": {
            "mostly_intrinsic": order_totals["singleton"] > (order_totals["pairwise"] + order_totals["triplet"] + order_totals["higher_order_residual"]),
            "pairwise_explains_majority": fractions["pairwise"] > 0.5,
            "triplet_required": fractions["triplet"] > 0.5,
            "higher_order_collective_evidence": fractions["higher_order_residual"] > 0.05,
        },
        "interpretation": _interpretation(dominant_order, full_score, external_internal, ranking),
    }


def compare_mechanistic_maps(
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any]:
    """Compare two mechanistic maps for PsiCat-style analysis."""

    deltas = {}
    for key in ("singleton", "pairwise", "triplet", "higher_order_residual"):
        deltas[key] = float(right["order_fractions"][key] - left["order_fractions"][key])
    return {
        "left_case": left["case_label"],
        "right_case": right["case_label"],
        "dominant_order_shift": [left["dominant_order"], right["dominant_order"]],
        "fraction_deltas": deltas,
        "total_irreversibility_delta": float(
            right["total_local_irreversibility"] - left["total_local_irreversibility"]
        ),
    }


def psicat_assist_packet(case_report: dict[str, Any]) -> dict[str, Any]:
    """Return a concise packet suitable for PsiCat training/assist flows."""

    dominant = case_report["dominant_order"]
    verdict = case_report["external_internal_balance"]["verdict"]
    top = case_report["top_interaction"]["subset_label"] if case_report["top_interaction"] else "none"
    if dominant == "pairwise":
        next_question = "Audit whether the top ranked coupling is sufficient to reproduce most of the full-system arrow."
    elif dominant == "triplet":
        next_question = "Test whether any pair projection loses the arrow, confirming irreducible collective mechanics."
    elif dominant == "singleton":
        next_question = "Separate intrinsic dissipation from coupling-induced asymmetry by perturbing the dominant component."
    else:
        next_question = "Expand the tracked subset size because the residual collective contribution may hide larger-group structure."
    return {
        "consumer": "PsiCat",
        "case_label": case_report["case_label"],
        "dominant_order": dominant,
        "top_interaction": top,
        "source_balance_verdict": verdict,
        "pairwise_fraction": case_report["order_fractions"]["pairwise"],
        "triplet_fraction": case_report["order_fractions"]["triplet"],
        "higher_order_fraction": case_report["order_fractions"]["higher_order_residual"],
        "narrative_summary": case_report["interpretation"],
        "recommended_next_question": next_question,
    }


def benchmark_cases() -> tuple[BenchmarkCase, ...]:
    """Return the benchmark suite used by Pillar 1088."""

    names = ("alpha", "beta", "gamma")
    return (
        BenchmarkCase(
            case_id="reversible_control",
            label="Reversible control",
            component_names=names,
            trajectory=(
                (0, 0, 0),
                (1, 1, 0),
                (0, 0, 0),
                (1, 1, 0),
                (0, 0, 0),
            ),
            expected_dominant_order="none",
            purpose="Control case: forward and reverse transition statistics match.",
        ),
        BenchmarkCase(
            case_id="single_component_drive",
            label="Single-component dissipative drive",
            component_names=names,
            trajectory=(
                (1, 0, 0),
                (1, 0, 0),
                (0, 0, 0),
                (0, 0, 0),
            )
            * 10,
            expected_dominant_order="singleton",
            purpose="Arrow is carried by one component with no genuine coupling requirement.",
            externally_driven_components=("alpha",),
        ),
        BenchmarkCase(
            case_id="pair_coupled_cycle",
            label="Pair-coupled irreversible cycle",
            component_names=names,
            trajectory=(
                (0, 0, 0),
                (1, 0, 0),
                (1, 1, 0),
                (0, 1, 0),
                (0, 0, 0),
            )
            * 5,
            expected_dominant_order="pairwise",
            purpose="Arrow is carried by a directed two-component coupling while singleton projections stay reversible.",
        ),
        BenchmarkCase(
            case_id="triplet_only_cycle",
            label="Triplet-only collective cycle",
            component_names=names,
            trajectory=(
                (0, 1, 0),
                (0, 1, 0),
                (0, 0, 0),
                (1, 1, 0),
                (1, 1, 1),
                (1, 1, 1),
                (0, 0, 0),
                (0, 1, 1),
                (0, 1, 0),
                (1, 1, 1),
                (1, 1, 0),
                (0, 1, 0),
            )
            * 5,
            expected_dominant_order="triplet",
            purpose="Pairwise views erase the arrow, so the mechanism is genuinely collective at third order.",
        ),
    )


def pillar1088_mechanistic_irreversibility_report() -> dict[str, Any]:
    """Return the full Pillar 1088 report."""

    benchmark_reports = []
    for case in benchmark_cases():
        case_report = build_mechanistic_irreversibility_map(
            trajectory=case.trajectory,
            component_names=case.component_names,
            case_label=case.label,
            externally_driven_components=case.externally_driven_components,
            purpose=case.purpose,
        )
        benchmark_reports.append(
            {
                "case_id": case.case_id,
                "expected_dominant_order": case.expected_dominant_order,
                "report": case_report,
                "psicat_assist": psicat_assist_packet(case_report),
            }
        )

    pair_report = next(row["report"] for row in benchmark_reports if row["case_id"] == "pair_coupled_cycle")
    triplet_report = next(row["report"] for row in benchmark_reports if row["case_id"] == "triplet_only_cycle")
    comparison = compare_mechanistic_maps(pair_report, triplet_report)

    anchor_sigma = lindblad_entropy_production(GAMMA_CANONICAL, S_von_neumann=1.0)
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "track_label": TRACK_LABEL,
        "adjacency_label": ADJACENCY_LABEL,
        "boundary_statement": (
            "This is an adjacent mechanistic map of irreversibility. It is a"
            " diagnostic decomposition layer, not a final ontological derivation"
            " of time's arrow and not a new hardgate physics closure."
        ),
        "anchors": {
            "pillar471_monotonicity_requirement": monotonicity_requirement(),
            "adm_entropy_rate_anchor": {
                "example_dS_dt": adm_entropy_rate(phi=1.0, K_trace=1.0, A_horizon=4.0),
                "interpretation": "Positive geometric entropy production remains the repo-level second-law anchor.",
            },
            "dissipation_geometry_anchor": {
                "gamma_canonical": GAMMA_CANONICAL,
                "sigma_example": anchor_sigma,
                "second_law_satisfied": second_law_check(anchor_sigma),
            },
        },
        "practical_questions": [
            "Is irreversibility mostly intrinsic or coupling-generated?",
            "Do pairwise interactions explain most of the arrow?",
            "Is a triplet or larger collective mechanism required?",
            "Which component or coupling is the dominant arrow carrier?",
        ],
        "benchmark_suite": benchmark_reports,
        "pair_vs_triplet_comparison": comparison,
    }
