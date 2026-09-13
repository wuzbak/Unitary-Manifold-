# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for provably safe neighborhood certification toolkit."""
from __future__ import annotations

import math

import pytest

from src.core.provably_safe_neighborhood_certification import (
    FAIL_CLOSED_RULES,
    PosteriorNeighborhoodInput,
    SingularityRoutingInput,
    TruncationEnvelope,
    full_certification_packet,
    formal_bridge_artifact,
    obligation_split,
    phase_checkpoint,
    posterior_neighborhood_certificate,
    singularity_topology_route,
    sobolev_localization_obligation,
    truncation_envelope,
)


def test_fail_closed_rules_present() -> None:
    assert FAIL_CLOSED_RULES["no_unverifiable_claims"]
    assert FAIL_CLOSED_RULES["explicit_residual_unknowns"]


def test_posterior_neighborhood_success_case() -> None:
    inp = PosteriorNeighborhoodInput(
        residual_bound=0.01,
        inverse_bound=2.0,
        lipschitz_bound=0.2,
    )
    cert = posterior_neighborhood_certificate(inp)
    assert cert["sufficient_condition"]
    assert cert["radius"] > 0.0
    assert cert["verdict"] == "POSTERIOR_NEIGHBORHOOD_CERTIFIED_UNIQUE"


def test_posterior_neighborhood_fail_closed_case() -> None:
    inp = PosteriorNeighborhoodInput(
        residual_bound=1.0,
        inverse_bound=3.0,
        lipschitz_bound=1.0,
    )
    cert = posterior_neighborhood_certificate(inp)
    assert not cert["sufficient_condition"]
    assert math.isnan(cert["radius"])
    assert cert["residual_unknowns"]


def test_truncation_envelope_aggregates_components() -> None:
    env = TruncationEnvelope(0.01, 0.02, 0.03)
    out = truncation_envelope(env)
    assert out["total_error"] == pytest.approx(0.06, rel=1e-9)
    assert out["monotone_components"]
    assert out["audit_ready"]


def test_sobolev_localization_obligation_compatible() -> None:
    out = sobolev_localization_obligation(local_patch_radius=0.5)
    assert out["localized_contractive"]
    assert out["obligation"]["l_h1"] < 1.0
    assert out["obligation"]["epsilon_grad_max"] > 0.0


def test_singularity_routing_regular() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=0.5,
            invariant_curvature_norm=10.0,
            topological_index_delta=0,
        ),
    )
    assert route["route"] == "REGULAR_REGION_CERTIFIABLE"
    assert not route["fail_closed"]


def test_singularity_routing_coordinate_breakdown() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=0.0,
            invariant_curvature_norm=10.0,
            topological_index_delta=0,
        ),
    )
    assert route["route"] == "COORDINATE_BREAKDOWN_RECHART_REQUIRED"
    assert route["fail_closed"]


def test_singularity_routing_topology_transition_fail_closed() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=0.9,
            invariant_curvature_norm=10.0,
            topological_index_delta=1,
        ),
    )
    assert route["route"] == "CONSTRUCTIVE_PROOF_REQUIRED_TOPOLOGICAL_TRANSITION"
    assert route["fail_closed"]


def test_obligation_split_nonempty_and_disjoint_roles() -> None:
    split = obligation_split()
    assert split["interval_obligations"]
    assert split["analytic_obligations"]
    assert any("finite-dimensional" in s for s in split["interval_obligations"])
    assert any("infinite-dimensional" in s for s in split["analytic_obligations"])


def test_phase_checkpoint_resumable() -> None:
    ckpt = phase_checkpoint(
        phase="Phase B",
        completed_invariants=["posterior kernel"],
        remaining_obligations=["tail bound"],
        restart_pointer="src/core/provably_safe_neighborhood_certification.py:full_certification_packet",
    )
    assert ckpt["resumable"]
    assert ckpt["checkpoint"]["phase"] == "Phase B"


def test_full_packet_success() -> None:
    packet = full_certification_packet(
        posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
        envelope=TruncationEnvelope(0.01, 0.02, 0.03),
        routing=SingularityRoutingInput(1.0, 10.0, 0),
        local_patch_radius=1.0,
    )
    assert packet["all_certified"]
    assert packet["verdict"] == "CERTIFIED_PACKET_READY_FOR_FORMAL_BRIDGE"
    assert packet["residual_unknowns"] == []


def test_full_packet_fail_closed_with_unknowns() -> None:
    packet = full_certification_packet(
        posterior_input=PosteriorNeighborhoodInput(1.0, 3.0, 1.0),
        envelope=TruncationEnvelope(0.01, 0.02, 0.03),
        routing=SingularityRoutingInput(0.0, 10.0, 0),
        local_patch_radius=1.0,
    )
    assert not packet["all_certified"]
    assert packet["verdict"] == "PARTIAL_PACKET_FAIL_CLOSED_WITH_EXPLICIT_UNKNOWNS"
    assert packet["residual_unknowns"]


def test_formal_bridge_artifact_ready_and_blocked() -> None:
    success_packet = full_certification_packet(
        posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
        envelope=TruncationEnvelope(0.01, 0.02, 0.03),
        routing=SingularityRoutingInput(1.0, 10.0, 0),
        local_patch_radius=1.0,
    )
    blocked_packet = full_certification_packet(
        posterior_input=PosteriorNeighborhoodInput(1.0, 3.0, 1.0),
        envelope=TruncationEnvelope(0.01, 0.02, 0.03),
        routing=SingularityRoutingInput(0.0, 10.0, 0),
        local_patch_radius=1.0,
    )
    ready = formal_bridge_artifact(success_packet)
    blocked = formal_bridge_artifact(blocked_packet)

    assert ready["status"] == "READY_FOR_FORMALIZATION"
    assert blocked["status"] == "BLOCKED_FAIL_CLOSED"
    assert blocked["residual_unknowns"]
