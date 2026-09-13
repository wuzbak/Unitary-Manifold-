# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for provably safe neighborhood certification toolkit."""
from __future__ import annotations

import math
from types import MappingProxyType

import pytest

import src.core.provably_safe_neighborhood_certification as cert_mod
from src.core.provably_safe_neighborhood_certification import (
    FAIL_CLOSED_RULES,
    PosteriorNeighborhoodInput,
    SingularityRoutingInput,
    TruncationEnvelope,
    checkpointed_formal_bridge_packet,
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


def test_posterior_neighborhood_boundary_case_is_not_certified() -> None:
    # 2*alpha*beta == 1 boundary must fail closed.
    cert = posterior_neighborhood_certificate(
        PosteriorNeighborhoodInput(
            residual_bound=0.5,
            inverse_bound=1.0,
            lipschitz_bound=1.0,
        )
    )
    assert not cert["sufficient_condition"]


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


def test_posterior_neighborhood_beta_zero_with_positive_inverse_uses_affine_radius() -> None:
    cert = posterior_neighborhood_certificate(
        PosteriorNeighborhoodInput(
            residual_bound=0.1,
            inverse_bound=2.0,
            lipschitz_bound=0.0,
        )
    )
    assert cert["sufficient_condition"]
    assert cert["degenerate_affine_case"]
    assert cert["radius"] == pytest.approx(0.2)


def test_posterior_neighborhood_beta_zero_large_seed_fails_closed() -> None:
    cert = posterior_neighborhood_certificate(
        PosteriorNeighborhoodInput(
            residual_bound=1.0,
            inverse_bound=1.0,
            lipschitz_bound=0.0,
        )
    )
    assert not cert["sufficient_condition"]
    assert any("alpha < 1" in msg for msg in cert["residual_unknowns"])


def test_posterior_neighborhood_zero_inverse_bound_reports_inverse_degeneracy() -> None:
    cert = posterior_neighborhood_certificate(
        PosteriorNeighborhoodInput(
            residual_bound=0.1,
            inverse_bound=0.0,
            lipschitz_bound=0.1,
        )
    )
    assert not cert["sufficient_condition"]
    assert any("Inverse-bound degeneracy" in msg for msg in cert["residual_unknowns"])


def test_posterior_neighborhood_exact_affine_zero_residual_certified() -> None:
    cert = posterior_neighborhood_certificate(
        PosteriorNeighborhoodInput(
            residual_bound=0.0,
            inverse_bound=2.0,
            lipschitz_bound=0.0,
        )
    )
    assert cert["sufficient_condition"]
    assert cert["radius"] == pytest.approx(0.0, abs=1e-15)
    assert cert["residual_unknowns"] == []


def test_posterior_neighborhood_near_zero_lipschitz_is_stable() -> None:
    cert = posterior_neighborhood_certificate(
        PosteriorNeighborhoodInput(
            residual_bound=1.0e-6,
            inverse_bound=2.0,
            lipschitz_bound=1.0e-14,
        )
    )
    assert cert["sufficient_condition"]
    assert cert["radius"] >= 0.0


def test_posterior_neighborhood_rejects_negative_inputs() -> None:
    with pytest.raises(ValueError):
        posterior_neighborhood_certificate(
            PosteriorNeighborhoodInput(
                residual_bound=-0.1,
                inverse_bound=2.0,
                lipschitz_bound=0.1,
            )
        )


def test_posterior_neighborhood_rejects_nonfinite_inputs() -> None:
    with pytest.raises(ValueError):
        posterior_neighborhood_certificate(
            PosteriorNeighborhoodInput(
                residual_bound=float("nan"),
                inverse_bound=2.0,
                lipschitz_bound=0.1,
            )
        )


def test_truncation_envelope_aggregates_components() -> None:
    env = TruncationEnvelope(0.01, 0.02, 0.03)
    out = truncation_envelope(env)
    assert out["total_error"] == pytest.approx(0.06, rel=1e-9)
    assert out["monotone_components"]
    assert out["audit_ready"]


def test_truncation_envelope_rejects_nonfinite_components() -> None:
    with pytest.raises(ValueError):
        truncation_envelope(
            TruncationEnvelope(
                finite_mode_error=float("inf"),
                tail_bound=0.01,
                nonlinear_remainder=0.01,
            )
        )


def test_sobolev_localization_obligation_compatible() -> None:
    out = sobolev_localization_obligation(local_patch_radius=0.5)
    assert out["localized_contractive"]
    assert out["obligation"]["l_h1"] < 1.0
    assert out["obligation"]["epsilon_grad_max"] > 0.0


def test_sobolev_localization_obligation_radius_affects_bound() -> None:
    small = sobolev_localization_obligation(local_patch_radius=0.5)
    large = sobolev_localization_obligation(local_patch_radius=2.0)
    assert large["obligation"]["epsilon_grad_max"] < small["obligation"]["epsilon_grad_max"]


def test_sobolev_localization_obligation_rejects_nonpositive_radius() -> None:
    with pytest.raises(ValueError):
        sobolev_localization_obligation(local_patch_radius=0.0)
    with pytest.raises(ValueError):
        sobolev_localization_obligation(local_patch_radius=float("nan"))


def test_sobolev_localization_obligation_uses_patched_h1_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cert_mod, "h1_lipschitz_estimate", lambda: {"l_h1": 1.1})
    monkeypatch.setattr(cert_mod, "critical_gradient_bound", lambda: {"epsilon_grad_max": 0.1})
    out = cert_mod.sobolev_localization_obligation(local_patch_radius=1.0)
    assert not out["localized_contractive"]


def test_sobolev_localization_obligation_uses_patched_gradient_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cert_mod, "h1_lipschitz_estimate", lambda: {"l_h1": 0.8})
    monkeypatch.setattr(cert_mod, "critical_gradient_bound", lambda: {"epsilon_grad_max": 0.0})
    out = cert_mod.sobolev_localization_obligation(local_patch_radius=1.0)
    assert not out["localized_contractive"]


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
    assert not route["fail_closed"]


def test_singularity_routing_nonfinite_jacobian_is_input_fail_closed() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=float("nan"),
            invariant_curvature_norm=10.0,
            topological_index_delta=0,
        ),
    )
    assert route["route"] == "INVALID_NUMERIC_INPUT_FAIL_CLOSED"
    assert route["fail_closed"]


def test_singularity_routing_nonfinite_curvature_is_input_fail_closed() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=1.0,
            invariant_curvature_norm=float("inf"),
            topological_index_delta=0,
        ),
    )
    assert route["route"] == "INVALID_NUMERIC_INPUT_FAIL_CLOSED"
    assert route["fail_closed"]


def test_singularity_routing_negative_curvature_is_input_fail_closed() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=1.0,
            invariant_curvature_norm=-1.0,
            topological_index_delta=0,
        ),
    )
    assert route["route"] == "INVALID_NUMERIC_INPUT_FAIL_CLOSED"
    assert route["fail_closed"]


def test_singularity_routing_nonfinite_curvature_precedes_coordinate_breakdown() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=0.0,
            invariant_curvature_norm=float("inf"),
            topological_index_delta=0,
        ),
    )
    assert route["route"] == "INVALID_NUMERIC_INPUT_FAIL_CLOSED"


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


def test_singularity_routing_custom_threshold_flips_route() -> None:
    regular = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=0.9,
            invariant_curvature_norm=50.0,
            topological_index_delta=0,
        ),
        curvature_singularity_threshold=100.0,
    )
    flagged = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=0.9,
            invariant_curvature_norm=50.0,
            topological_index_delta=0,
        ),
        curvature_singularity_threshold=10.0,
    )
    assert regular["route"] == "REGULAR_REGION_CERTIFIABLE"
    assert flagged["route"] == "GEOMETRIC_SINGULAR_BEHAVIOR_CERTIFY_OR_REJECT"


def test_singularity_routing_threshold_boundary_is_regular() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=0.9,
            invariant_curvature_norm=10.0,
            topological_index_delta=0,
        ),
        curvature_singularity_threshold=10.0,
    )
    assert route["route"] == "REGULAR_REGION_CERTIFIABLE"


def test_singularity_routing_geometric_precedes_coordinate_breakdown() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=0.0,
            invariant_curvature_norm=1.0e7,
            topological_index_delta=0,
        ),
        curvature_singularity_threshold=1.0e6,
    )
    assert route["route"] == "GEOMETRIC_SINGULAR_BEHAVIOR_CERTIFY_OR_REJECT"


def test_singularity_routing_geometric_precedes_topology_signal() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=1.0,
            invariant_curvature_norm=1.0e7,
            topological_index_delta=1,
        ),
        curvature_singularity_threshold=1.0e6,
    )
    assert route["route"] == "GEOMETRIC_SINGULAR_BEHAVIOR_CERTIFY_OR_REJECT"


def test_singularity_routing_topology_precedes_coordinate_on_invalid_chart() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=0.0,
            invariant_curvature_norm=10.0,
            topological_index_delta=1,
        ),
        curvature_singularity_threshold=1.0e6,
    )
    assert route["route"] == "CONSTRUCTIVE_PROOF_REQUIRED_TOPOLOGICAL_TRANSITION"


def test_singularity_routing_negative_jacobian_is_rechart_required() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=-0.1,
            invariant_curvature_norm=10.0,
            topological_index_delta=0,
        ),
        curvature_singularity_threshold=1.0e6,
    )
    assert route["route"] == "COORDINATE_BREAKDOWN_RECHART_REQUIRED"


def test_singularity_routing_nonintegral_topology_delta_is_input_fail_closed() -> None:
    route = singularity_topology_route(
        SingularityRoutingInput(
            chart_jacobian_min=1.0,
            invariant_curvature_norm=10.0,
            topological_index_delta=1.5,  # type: ignore[arg-type]
        ),
        curvature_singularity_threshold=1.0e6,
    )
    assert route["route"] == "INVALID_NUMERIC_INPUT_FAIL_CLOSED"


def test_singularity_routing_rejects_invalid_threshold() -> None:
    with pytest.raises(ValueError):
        singularity_topology_route(
            SingularityRoutingInput(
                chart_jacobian_min=0.9,
                invariant_curvature_norm=50.0,
                topological_index_delta=0,
            ),
            curvature_singularity_threshold=float("nan"),
        )
    with pytest.raises(ValueError):
        singularity_topology_route(
            SingularityRoutingInput(
                chart_jacobian_min=0.9,
                invariant_curvature_norm=50.0,
                topological_index_delta=0,
            ),
            curvature_singularity_threshold=-1.0,
        )


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


def test_full_packet_coordinate_breakdown_requires_rechart_and_blocks_certification() -> None:
    packet = full_certification_packet(
        posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
        envelope=TruncationEnvelope(0.01, 0.02, 0.03),
        routing=SingularityRoutingInput(0.0, 10.0, 0),
        local_patch_radius=1.0,
    )
    assert not packet["all_certified"]
    assert any("COORDINATE_BREAKDOWN_RECHART_REQUIRED" in reason for reason in packet["residual_unknowns"])


def test_full_packet_propagates_custom_curvature_threshold() -> None:
    packet = full_certification_packet(
        posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
        envelope=TruncationEnvelope(0.01, 0.02, 0.03),
        routing=SingularityRoutingInput(1.0, 50.0, 0),
        local_patch_radius=1.0,
        curvature_singularity_threshold=10.0,
    )
    assert not packet["all_certified"]
    assert (
        packet["singularity_topology_routing"]["route"]
        == "GEOMETRIC_SINGULAR_BEHAVIOR_CERTIFY_OR_REJECT"
    )


def test_full_packet_fail_closed_when_truncation_not_audit_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    def _non_certifying_envelope(_env: TruncationEnvelope) -> dict:
        return {"audit_ready": False}

    monkeypatch.setattr(cert_mod, "truncation_envelope", _non_certifying_envelope)
    packet = cert_mod.full_certification_packet(
        posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
        envelope=TruncationEnvelope(0.01, 0.02, 0.03),
        routing=SingularityRoutingInput(1.0, 10.0, 0),
        local_patch_radius=1.0,
    )
    assert not packet["all_certified"]
    assert packet["verdict"] == "PARTIAL_PACKET_FAIL_CLOSED_WITH_EXPLICIT_UNKNOWNS"
    assert any("Truncation envelope" in reason for reason in packet["residual_unknowns"])


def test_full_packet_not_certified_when_posterior_unknowns_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cert_mod,
        "posterior_neighborhood_certificate",
        lambda _inp: {
            "sufficient_condition": True,
            "residual_unknowns": ["manual-proof-gap"],
        },
    )
    packet = cert_mod.full_certification_packet(
        posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
        envelope=TruncationEnvelope(0.01, 0.02, 0.03),
        routing=SingularityRoutingInput(1.0, 10.0, 0),
        local_patch_radius=1.0,
    )
    assert not packet["all_certified"]
    assert "manual-proof-gap" in packet["residual_unknowns"]


def test_full_packet_rejects_malformed_truncation_stage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cert_mod, "truncation_envelope", lambda _env: {})
    with pytest.raises(ValueError):
        cert_mod.full_certification_packet(
            posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
            envelope=TruncationEnvelope(0.01, 0.02, 0.03),
            routing=SingularityRoutingInput(1.0, 10.0, 0),
            local_patch_radius=1.0,
        )


def test_full_packet_rejects_malformed_posterior_stage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cert_mod, "posterior_neighborhood_certificate", lambda _inp: {})
    with pytest.raises(ValueError):
        cert_mod.full_certification_packet(
            posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
            envelope=TruncationEnvelope(0.01, 0.02, 0.03),
            routing=SingularityRoutingInput(1.0, 10.0, 0),
            local_patch_radius=1.0,
        )


def test_full_packet_rejects_posterior_stage_with_nonlist_unknowns(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cert_mod,
        "posterior_neighborhood_certificate",
        lambda _inp: {"sufficient_condition": True, "residual_unknowns": None},
    )
    with pytest.raises(ValueError):
        cert_mod.full_certification_packet(
            posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
            envelope=TruncationEnvelope(0.01, 0.02, 0.03),
            routing=SingularityRoutingInput(1.0, 10.0, 0),
            local_patch_radius=1.0,
        )


def test_full_packet_rejects_posterior_stage_with_nonbool_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cert_mod,
        "posterior_neighborhood_certificate",
        lambda _inp: {"sufficient_condition": "yes", "residual_unknowns": []},
    )
    with pytest.raises(ValueError):
        cert_mod.full_certification_packet(
            posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
            envelope=TruncationEnvelope(0.01, 0.02, 0.03),
            routing=SingularityRoutingInput(1.0, 10.0, 0),
            local_patch_radius=1.0,
        )


def test_full_packet_rejects_malformed_sobolev_stage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cert_mod, "sobolev_localization_obligation", lambda local_patch_radius: {})
    with pytest.raises(ValueError):
        cert_mod.full_certification_packet(
            posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
            envelope=TruncationEnvelope(0.01, 0.02, 0.03),
            routing=SingularityRoutingInput(1.0, 10.0, 0),
            local_patch_radius=1.0,
        )


def test_full_packet_rejects_nonbool_truncation_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cert_mod, "truncation_envelope", lambda _env: {"audit_ready": "false"})
    with pytest.raises(ValueError):
        cert_mod.full_certification_packet(
            posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
            envelope=TruncationEnvelope(0.01, 0.02, 0.03),
            routing=SingularityRoutingInput(1.0, 10.0, 0),
            local_patch_radius=1.0,
        )


def test_full_packet_rejects_nonbool_sobolev_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cert_mod,
        "sobolev_localization_obligation",
        lambda local_patch_radius: {"localized_contractive": 1},
    )
    with pytest.raises(ValueError):
        cert_mod.full_certification_packet(
            posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
            envelope=TruncationEnvelope(0.01, 0.02, 0.03),
            routing=SingularityRoutingInput(1.0, 10.0, 0),
            local_patch_radius=1.0,
        )


def test_full_packet_rejects_malformed_routing_stage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cert_mod, "singularity_topology_route", lambda _routing, **kwargs: {})
    with pytest.raises(ValueError):
        cert_mod.full_certification_packet(
            posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
            envelope=TruncationEnvelope(0.01, 0.02, 0.03),
            routing=SingularityRoutingInput(1.0, 10.0, 0),
            local_patch_radius=1.0,
        )


def test_full_packet_rejects_nonbool_routing_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cert_mod,
        "singularity_topology_route",
        lambda _routing, **kwargs: {"route": "REGULAR_REGION_CERTIFIABLE", "fail_closed": "no"},
    )
    with pytest.raises(ValueError):
        cert_mod.full_certification_packet(
            posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
            envelope=TruncationEnvelope(0.01, 0.02, 0.03),
            routing=SingularityRoutingInput(1.0, 10.0, 0),
            local_patch_radius=1.0,
        )


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


def test_formal_bridge_artifact_rejects_malformed_packet() -> None:
    with pytest.raises(ValueError):
        formal_bridge_artifact({"all_certified": True})


def test_formal_bridge_artifact_rejects_inconsistent_packet() -> None:
    with pytest.raises(ValueError):
        formal_bridge_artifact({"all_certified": True, "residual_unknowns": ["missing proof"]})


def test_formal_bridge_artifact_rejects_nonboolean_all_certified() -> None:
    with pytest.raises(ValueError):
        formal_bridge_artifact({"all_certified": "false", "residual_unknowns": []})


def test_formal_bridge_artifact_rejects_nonlist_unknowns() -> None:
    with pytest.raises(ValueError):
        formal_bridge_artifact({"all_certified": False, "residual_unknowns": "missing proof"})


def test_formal_bridge_artifact_rejects_set_unknowns_iterable() -> None:
    with pytest.raises(ValueError):
        formal_bridge_artifact({"all_certified": False, "residual_unknowns": {"b-proof", "a-proof"}})


def test_formal_bridge_artifact_rejects_frozenset_unknowns() -> None:
    with pytest.raises(ValueError):
        formal_bridge_artifact(
            {"all_certified": False, "residual_unknowns": frozenset({"b-proof", "a-proof"})}
        )


def test_formal_bridge_artifact_accepts_tuple_unknowns_sequence() -> None:
    artifact = formal_bridge_artifact({"all_certified": False, "residual_unknowns": ("missing proof",)})
    assert artifact["status"] == "BLOCKED_FAIL_CLOSED"
    assert artifact["residual_unknowns"] == ["missing proof"]


def test_formal_bridge_artifact_accepts_generator_unknowns_deterministically() -> None:
    with pytest.raises(ValueError):
        formal_bridge_artifact(
            {
                "all_certified": False,
                "residual_unknowns": (item for item in ["b-proof", "a-proof"]),
            }
        )


def test_formal_bridge_artifact_rejects_nonmapping_packet() -> None:
    with pytest.raises(ValueError):
        formal_bridge_artifact([])  # type: ignore[arg-type]


def test_formal_bridge_artifact_accepts_blocked_packet_without_unknowns() -> None:
    artifact = formal_bridge_artifact({"all_certified": False, "residual_unknowns": []})
    assert artifact["status"] == "BLOCKED_FAIL_CLOSED"
    assert artifact["residual_unknowns"] == []


def test_formal_bridge_artifact_rejects_mixed_type_unknowns_without_typeerror() -> None:
    with pytest.raises(ValueError):
        formal_bridge_artifact({"all_certified": False, "residual_unknowns": ["ok", 3]})


def test_formal_bridge_artifact_accepts_mappingproxy_input() -> None:
    packet = MappingProxyType({"all_certified": False, "residual_unknowns": ["missing proof"]})
    artifact = formal_bridge_artifact(packet)  # type: ignore[arg-type]
    assert artifact["status"] == "BLOCKED_FAIL_CLOSED"
    assert artifact["residual_unknowns"] == ["missing proof"]


def test_checkpointed_formal_bridge_packet_success() -> None:
    out = checkpointed_formal_bridge_packet(
        posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
        envelope=TruncationEnvelope(0.01, 0.02, 0.03),
        routing=SingularityRoutingInput(1.0, 10.0, 0),
        phase="Phase C",
        restart_pointer="src/core/provably_safe_neighborhood_certification.py:checkpointed_formal_bridge_packet",
    )
    assert out["packet"]["all_certified"] is True
    assert out["artifact"]["status"] == "READY_FOR_FORMALIZATION"
    assert out["checkpoint"]["resumable"] is True
    assert list(out["checkpoint"]["checkpoint"]["remaining_obligations"]) == []


def test_checkpointed_formal_bridge_packet_blocked_routes_unknowns_to_checkpoint() -> None:
    out = checkpointed_formal_bridge_packet(
        posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
        envelope=TruncationEnvelope(0.01, 0.02, 0.03),
        routing=SingularityRoutingInput(0.0, 10.0, 0),
        phase="Phase C",
        restart_pointer="src/core/provably_safe_neighborhood_certification.py:checkpointed_formal_bridge_packet",
    )
    assert out["packet"]["all_certified"] is False
    assert out["artifact"]["status"] == "BLOCKED_FAIL_CLOSED"
    assert out["checkpoint"]["checkpoint"]["remaining_obligations"]


def test_checkpointed_formal_bridge_packet_propagates_optional_params() -> None:
    out = checkpointed_formal_bridge_packet(
        posterior_input=PosteriorNeighborhoodInput(0.01, 2.0, 0.2),
        envelope=TruncationEnvelope(0.01, 0.02, 0.03),
        routing=SingularityRoutingInput(1.0, 50.0, 0),
        phase="Phase C",
        restart_pointer="src/core/provably_safe_neighborhood_certification.py:checkpointed_formal_bridge_packet",
        local_patch_radius=2.0,
        curvature_singularity_threshold=10.0,
    )
    assert out["packet"]["sobolev_localization"]["obligation"]["local_patch_radius"] == pytest.approx(2.0)
    assert (
        out["packet"]["singularity_topology_routing"]["curvature_singularity_threshold"]
        == pytest.approx(10.0)
    )
