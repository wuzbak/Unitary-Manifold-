# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Unit tests for pentad_enterprise_bridge.py."""

import math
import os
import sys

import pytest

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from pentad_enterprise_bridge import (
    SHIP_DOMAINS,
    ShipDomain,
    UserProfile,
    TaskIntent,
    DomainProtocol,
    default_domain_protocols,
    personalization_factor,
    pentad_authority_weights,
    shipwide_readiness,
    route_task_intent,
)
from unitary_pentad import PentadLabel, PentadSystem
from src.consciousness.coupled_attractor import ManifoldState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


@pytest.fixture
def profile() -> UserProfile:
    return UserProfile(
        user_id="captain",
        expertise_by_domain={
            ShipDomain.CHORES: 0.9,
            ShipDomain.NAVIGATION: 0.8,
            ShipDomain.PILOTING: 0.85,
            ShipDomain.ENGINEERING: 0.7,
            ShipDomain.EXOTIC_PROPULSION: 0.4,
        },
        autonomy_preference=0.6,
    )


# ---------------------------------------------------------------------------
# Basics
# ---------------------------------------------------------------------------

class TestDomainsAndProtocols:
    def test_ship_domains_has_five_entries(self):
        assert len(SHIP_DOMAINS) == 5

    def test_default_protocols_cover_all_domains(self):
        protocols = default_domain_protocols()
        assert set(protocols.keys()) == set(SHIP_DOMAINS)

    def test_exotic_propulsion_is_implication_only(self):
        protocols = default_domain_protocols()
        proto = protocols[ShipDomain.EXOTIC_PROPULSION]
        assert proto.implication_only is True
        assert "execute" not in proto.allowed_actions


class TestValidation:
    def test_user_profile_rejects_bad_autonomy(self):
        with pytest.raises(ValueError):
            UserProfile(user_id="u", autonomy_preference=1.1)

    def test_user_profile_rejects_bad_expertise(self):
        with pytest.raises(ValueError):
            UserProfile(user_id="u", expertise_by_domain={ShipDomain.CHORES: -0.01})

    def test_task_intent_rejects_unknown_domain(self):
        with pytest.raises(ValueError):
            TaskIntent(task_id="t", user_id="u", domain="unknown")

    def test_domain_protocol_rejects_empty_actions(self):
        with pytest.raises(ValueError):
            DomainProtocol(
                min_trust=0.1,
                human_confirmation_threshold=0.5,
                implication_only=False,
                allowed_actions=(),
            )


class TestPersonalizationAndMath:
    def test_personalization_factor_increases_with_expertise(self):
        low = UserProfile(user_id="u1", expertise_by_domain={ShipDomain.CHORES: 0.2})
        high = UserProfile(user_id="u2", expertise_by_domain={ShipDomain.CHORES: 0.9})
        assert personalization_factor(high, ShipDomain.CHORES) > personalization_factor(low, ShipDomain.CHORES)

    def test_authority_weights_sum_to_one(self, default_system, profile):
        intent = TaskIntent(task_id="t", user_id="captain", domain=ShipDomain.NAVIGATION)
        w = pentad_authority_weights(default_system, profile, intent)
        assert set(w.keys()) == {
            PentadLabel.UNIV,
            PentadLabel.BRAIN,
            PentadLabel.HUMAN,
            PentadLabel.AI,
            PentadLabel.TRUST,
        }
        assert math.isclose(sum(w.values()), 1.0, rel_tol=1e-9, abs_tol=1e-9)

    def test_requested_autonomy_biases_ai_weight(self, default_system, profile):
        low = TaskIntent(
            task_id="t1",
            user_id="captain",
            domain=ShipDomain.NAVIGATION,
            requested_autonomy=0.0,
        )
        high = TaskIntent(
            task_id="t2",
            user_id="captain",
            domain=ShipDomain.NAVIGATION,
            requested_autonomy=1.0,
        )
        w_low = pentad_authority_weights(default_system, profile, low)
        w_high = pentad_authority_weights(default_system, profile, high)
        assert w_high[PentadLabel.AI] > w_low[PentadLabel.AI]

    def test_readiness_in_unit_interval(self, default_system, profile):
        intent = TaskIntent(task_id="t", user_id="captain", domain=ShipDomain.CHORES, criticality=0.4)
        score = shipwide_readiness(default_system, profile, intent)
        assert 0.0 <= score <= 1.0

    def test_readiness_decreases_with_criticality(self, default_system, profile):
        low = TaskIntent(task_id="t1", user_id="captain", domain=ShipDomain.ENGINEERING, criticality=0.1)
        high = TaskIntent(task_id="t2", user_id="captain", domain=ShipDomain.ENGINEERING, criticality=0.9)
        assert shipwide_readiness(default_system, profile, high) < shipwide_readiness(default_system, profile, low)

    def test_readiness_drops_when_trust_drops(self, default_system, profile):
        intent = TaskIntent(task_id="t", user_id="captain", domain=ShipDomain.PILOTING)
        low_trust_system = _with_body_phi(default_system, PentadLabel.TRUST, 0.0)
        assert shipwide_readiness(low_trust_system, profile, intent) < shipwide_readiness(default_system, profile, intent)


class TestRouting:
    def test_low_trust_forces_hold(self, default_system, profile):
        low_trust = _with_body_phi(default_system, PentadLabel.TRUST, 0.0)
        intent = TaskIntent(task_id="t", user_id="captain", domain=ShipDomain.PILOTING, criticality=0.2)
        routed = route_task_intent(low_trust, profile, intent)
        assert routed.execution_mode == "hold"
        assert routed.requires_human_confirmation is True

    def test_exotic_propulsion_routes_to_analysis_only(self, default_system, profile):
        intent = TaskIntent(
            task_id="x",
            user_id="captain",
            domain=ShipDomain.EXOTIC_PROPULSION,
            criticality=0.9,
        )
        routed = route_task_intent(default_system, profile, intent)
        assert routed.execution_mode == "analysis_only"
        assert routed.implication_only is True
        assert routed.requires_human_confirmation is True
        assert "execute" not in routed.allowed_actions

    def test_high_critical_piloting_requires_confirmation(self, default_system, profile):
        intent = TaskIntent(
            task_id="p",
            user_id="captain",
            domain=ShipDomain.PILOTING,
            criticality=0.95,
        )
        routed = route_task_intent(default_system, profile, intent)
        assert routed.requires_human_confirmation is True

    def test_returns_valid_non_implication_route_for_chores(self, default_system, profile):
        intent = TaskIntent(
            task_id="c",
            user_id="captain",
            domain=ShipDomain.CHORES,
            criticality=0.1,
        )
        routed = route_task_intent(default_system, profile, intent)
        assert routed.implication_only is False
        assert routed.execution_mode in {"autonomous_assist", "supervised_assist", "manual_guidance"}

    def test_missing_protocol_raises(self, default_system, profile):
        intent = TaskIntent(task_id="t", user_id="captain", domain=ShipDomain.CHORES)
        with pytest.raises(ValueError):
            route_task_intent(default_system, profile, intent, protocols={})
