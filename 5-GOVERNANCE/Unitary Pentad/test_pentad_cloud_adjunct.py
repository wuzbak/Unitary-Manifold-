# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Unit tests for pentad_cloud_adjunct.py."""

import os
import sys

import pytest

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from pentad_cloud_adjunct import (
    CLOUD_ADJUNCT_ROLES,
    CloudAdjunctDecision,
    CloudAdjunctPolicy,
    CloudAdjunctRequest,
    CloudAdjunctRole,
    default_cloud_adjunct_policy,
    evaluate_cloud_adjunct,
)
from unitary_pentad import PENTAD_LABELS, PentadLabel, PentadSystem
from src.consciousness.coupled_attractor import ManifoldState


def _with_body_phi(system: PentadSystem, label: str, phi: float) -> PentadSystem:
    old = system.bodies[label]
    bodies = dict(system.bodies)
    bodies[label] = ManifoldState(
        node=old.node,
        phi=phi,
        n1=old.n1,
        n2=old.n2,
        k_cs=old.k_cs,
        label=old.label,
    )
    return PentadSystem(bodies=bodies, beta=system.beta)


@pytest.fixture
def default_system() -> PentadSystem:
    return PentadSystem.default()


class TestCloudAdjunctValidation:
    def test_supported_roles_are_fixed(self):
        assert CLOUD_ADJUNCT_ROLES == (
            CloudAdjunctRole.ARCHIVE,
            CloudAdjunctRole.BATCH_COMPUTE,
            CloudAdjunctRole.TRUTH_QUERY,
            CloudAdjunctRole.MODEL_HOST,
        )

    def test_request_rejects_unknown_role(self):
        with pytest.raises(ValueError):
            CloudAdjunctRequest("x", "sixth_body", 50.0)

    def test_request_rejects_negative_latency(self):
        with pytest.raises(ValueError):
            CloudAdjunctRequest("x", CloudAdjunctRole.ARCHIVE, -1.0)

    def test_policy_rejects_non_pentad_orbit(self):
        with pytest.raises(ValueError):
            CloudAdjunctPolicy(active_orbit_bodies=PENTAD_LABELS + ("cloud",))


class TestCloudAdjunctRouting:
    def test_default_policy_preserves_exactly_five_active_bodies(self):
        policy = default_cloud_adjunct_policy()
        assert policy.active_orbit_bodies == PENTAD_LABELS
        assert len(policy.active_orbit_bodies) == 5

    def test_archive_routes_as_mirror(self, default_system):
        request = CloudAdjunctRequest(
            request_id="archive-1",
            role=CloudAdjunctRole.ARCHIVE,
            estimated_roundtrip_ms=80.0,
            state_mutation="snapshot",
        )
        decision = evaluate_cloud_adjunct(default_system, request)
        assert decision.execution_path == "adjunct_mirror"
        assert decision.cloud_enabled is True
        assert decision.requires_local_verification is False
        assert decision.failover_mode == "queue_snapshot_locally"

    def test_batch_compute_routes_async(self, default_system):
        request = CloudAdjunctRequest(
            request_id="batch-1",
            role=CloudAdjunctRole.BATCH_COMPUTE,
            estimated_roundtrip_ms=90.0,
            state_mutation="advisory",
        )
        decision = evaluate_cloud_adjunct(default_system, request)
        assert decision.execution_path == "adjunct_async"
        assert decision.cloud_enabled is True
        assert decision.requires_local_verification is True
        assert "simulate" in decision.allowed_operations

    def test_truth_query_requires_confirmation_when_critical(self, default_system):
        request = CloudAdjunctRequest(
            request_id="truth-1",
            role=CloudAdjunctRole.TRUTH_QUERY,
            estimated_roundtrip_ms=45.0,
            criticality=0.95,
            state_mutation="advisory",
        )
        decision = evaluate_cloud_adjunct(default_system, request)
        assert decision.execution_path == "adjunct_async"
        assert decision.requires_human_confirmation is True
        assert decision.failover_mode == "degrade_to_local_truth_and_cached_sources"

    def test_low_trust_forces_confirmation_for_remote_truth(self, default_system):
        low_trust = _with_body_phi(default_system, PentadLabel.TRUST, 0.0)
        request = CloudAdjunctRequest(
            request_id="truth-2",
            role=CloudAdjunctRole.TRUTH_QUERY,
            estimated_roundtrip_ms=20.0,
            criticality=0.2,
            state_mutation="advisory",
        )
        decision = evaluate_cloud_adjunct(low_trust, request)
        assert decision.execution_path == "adjunct_async"
        assert decision.requires_human_confirmation is True

    def test_phase_lock_request_is_rejected_from_cloud(self, default_system):
        request = CloudAdjunctRequest(
            request_id="phase-1",
            role=CloudAdjunctRole.MODEL_HOST,
            estimated_roundtrip_ms=15.0,
            phase_lock_required=True,
        )
        decision = evaluate_cloud_adjunct(default_system, request)
        assert decision.execution_path == "local_only"
        assert decision.cloud_enabled is False
        assert "phase-locking" in decision.rationale

    def test_control_write_request_is_rejected_from_cloud(self, default_system):
        request = CloudAdjunctRequest(
            request_id="control-1",
            role=CloudAdjunctRole.MODEL_HOST,
            estimated_roundtrip_ms=15.0,
            control_write_requested=True,
        )
        decision = evaluate_cloud_adjunct(default_system, request)
        assert decision.execution_path == "local_only"
        assert decision.cloud_enabled is False

    def test_actuation_mutation_is_rejected_from_cloud(self, default_system):
        request = CloudAdjunctRequest(
            request_id="act-1",
            role=CloudAdjunctRole.BATCH_COMPUTE,
            estimated_roundtrip_ms=80.0,
            state_mutation="actuation",
        )
        decision = evaluate_cloud_adjunct(default_system, request)
        assert decision.execution_path == "local_only"
        assert decision.cloud_enabled is False
        assert "actuate" in decision.rationale

    def test_disabled_role_falls_back_to_local(self, default_system):
        policy = CloudAdjunctPolicy(allow_remote_model_hosts=False)
        request = CloudAdjunctRequest(
            request_id="model-1",
            role=CloudAdjunctRole.MODEL_HOST,
            estimated_roundtrip_ms=60.0,
        )
        decision = evaluate_cloud_adjunct(default_system, request, policy=policy)
        assert decision.execution_path == "local_only"
        assert decision.cloud_enabled is False

    def test_decision_never_adds_a_sixth_body(self, default_system):
        request = CloudAdjunctRequest(
            request_id="model-2",
            role=CloudAdjunctRole.MODEL_HOST,
            estimated_roundtrip_ms=30.0,
        )
        decision = evaluate_cloud_adjunct(default_system, request)
        assert isinstance(decision, CloudAdjunctDecision)
        assert decision.can_join_active_orbit is False
        assert decision.active_orbit_bodies == PENTAD_LABELS
        assert len(decision.active_orbit_bodies) == 5
