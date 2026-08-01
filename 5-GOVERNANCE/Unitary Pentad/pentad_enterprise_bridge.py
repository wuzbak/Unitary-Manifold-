# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
Unitary Pentad/pentad_enterprise_bridge.py
===========================================
Ship-wide orchestration bridge from Unitary Pentad dynamics to practical
operator-facing task routing.

Purpose
-------
This module turns Pentad state variables into a governance protocol for an
"enterprise computer" style assistant: ship-wide management and expertise,
automatically tailored to user and task intent.

Core ideas
----------
1. Personalization is explicit: each user has domain expertise and autonomy
   preference, which modulate authority splits.
2. Routing is protocolized by domain: chores, engineering, navigation,
   piloting, and exotic propulsion implications.
3. Safety is trust-gated: low trust modulation forces hold/manual paths.
4. Exotic propulsion is treated as implication-only analysis in this public
   layer (non-actuating by construction).

Public API
----------
ShipDomain
    Domain constants for ship-wide tasks.

UserProfile
    Per-operator personalization profile.

TaskIntent
    Structured task request (domain, criticality, optional autonomy override).

DomainProtocol
    Domain-specific routing guardrails.

RoutedIntent
    Final route result: execution mode, authority split, guard decisions.

default_domain_protocols() -> dict[str, DomainProtocol]
    Canonical protocol map for all supported domains.

personalization_factor(profile, domain) -> float
    User-specific gain in [0, 1].

pentad_authority_weights(system, profile, intent) -> dict[str, float]
    Normalized per-body authority share over the 5 Pentad bodies.

shipwide_readiness(system, profile, intent) -> float
    Scalar readiness score in [0, 1].

route_task_intent(system, profile, intent, protocols=None) -> RoutedIntent
    Main entry point.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Tuple

import numpy as np

from unitary_pentad import (
    BRAIDED_SOUND_SPEED,
    PENTAD_LABELS,
    PentadLabel,
    PentadSystem,
    TRUST_PHI_MIN,
    pentad_defect,
    trust_modulation,
)


_EPS: float = 1e-12


class ShipDomain:
    """Domain constants for enterprise-style ship-wide operations."""

    CHORES = "chores"
    ENGINEERING = "engineering"
    NAVIGATION = "navigation"
    PILOTING = "piloting"
    EXOTIC_PROPULSION = "exotic_propulsion"


SHIP_DOMAINS: Tuple[str, ...] = (
    ShipDomain.CHORES,
    ShipDomain.ENGINEERING,
    ShipDomain.NAVIGATION,
    ShipDomain.PILOTING,
    ShipDomain.EXOTIC_PROPULSION,
)


@dataclass(frozen=True)
class UserProfile:
    """Per-operator personalization profile.

    Attributes
    ----------
    user_id : str
        Stable operator identifier.
    expertise_by_domain : dict[str, float]
        Domain expertise in [0,1].  Missing domains default to 0.5.
    autonomy_preference : float
        Preferred autonomy level in [0,1]:
        0.0 => strongly human-steered, 1.0 => strongly AI-steered.
    """

    user_id: str
    expertise_by_domain: Dict[str, float] = field(default_factory=dict)
    autonomy_preference: float = 0.5

    def __post_init__(self) -> None:
        if not (0.0 <= self.autonomy_preference <= 1.0):
            raise ValueError(
                f"autonomy_preference={self.autonomy_preference} must be in [0,1]."
            )
        for domain, value in self.expertise_by_domain.items():
            if not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"expertise_by_domain[{domain!r}]={value} must be in [0,1]."
                )


@dataclass(frozen=True)
class TaskIntent:
    """Structured user intent for ship-wide orchestration."""

    task_id: str
    user_id: str
    domain: str
    criticality: float = 0.5
    requested_autonomy: Optional[float] = None

    def __post_init__(self) -> None:
        if self.domain not in SHIP_DOMAINS:
            raise ValueError(f"Unsupported domain={self.domain!r}.")
        if not (0.0 <= self.criticality <= 1.0):
            raise ValueError(f"criticality={self.criticality} must be in [0,1].")
        if self.requested_autonomy is not None and not (0.0 <= self.requested_autonomy <= 1.0):
            raise ValueError(
                f"requested_autonomy={self.requested_autonomy} must be in [0,1]."
            )


@dataclass(frozen=True)
class DomainProtocol:
    """Domain-specific guardrails for routing."""

    min_trust: float
    human_confirmation_threshold: float
    implication_only: bool
    allowed_actions: Tuple[str, ...]

    def __post_init__(self) -> None:
        if not (0.0 <= self.min_trust <= 1.0):
            raise ValueError(f"min_trust={self.min_trust} must be in [0,1].")
        if not (0.0 <= self.human_confirmation_threshold <= 1.0):
            raise ValueError(
                "human_confirmation_threshold must be in [0,1]."
            )
        if len(self.allowed_actions) == 0:
            raise ValueError("allowed_actions must be non-empty.")


@dataclass(frozen=True)
class RoutedIntent:
    """Route result for one task intent."""

    execution_mode: str
    readiness: float
    authority_weights: Dict[str, float]
    requires_human_confirmation: bool
    implication_only: bool
    allowed_actions: Tuple[str, ...]
    rationale: str


def default_domain_protocols() -> Dict[str, DomainProtocol]:
    """Return canonical domain protocols for ship-wide operations."""

    return {
        ShipDomain.CHORES: DomainProtocol(
            min_trust=0.10,
            human_confirmation_threshold=0.85,
            implication_only=False,
            allowed_actions=("schedule", "execute", "verify"),
        ),
        ShipDomain.ENGINEERING: DomainProtocol(
            min_trust=0.20,
            human_confirmation_threshold=0.60,
            implication_only=False,
            allowed_actions=("diagnose", "simulate", "execute", "verify"),
        ),
        ShipDomain.NAVIGATION: DomainProtocol(
            min_trust=0.25,
            human_confirmation_threshold=0.55,
            implication_only=False,
            allowed_actions=("compute", "simulate", "execute", "verify"),
        ),
        ShipDomain.PILOTING: DomainProtocol(
            min_trust=0.30,
            human_confirmation_threshold=0.45,
            implication_only=False,
            allowed_actions=("assist", "simulate", "execute", "verify"),
        ),
        ShipDomain.EXOTIC_PROPULSION: DomainProtocol(
            min_trust=0.35,
            human_confirmation_threshold=0.00,
            implication_only=True,
            allowed_actions=("analyze", "simulate", "propose"),
        ),
    }


def _domain_expertise(profile: UserProfile, domain: str) -> float:
    return float(profile.expertise_by_domain.get(domain, 0.5))


def personalization_factor(profile: UserProfile, domain: str) -> float:
    """User-specific personalization gain in [0,1]."""

    expertise = _domain_expertise(profile, domain)
    return float(np.clip(0.35 + 0.65 * expertise, 0.0, 1.0))


def _effective_autonomy(profile: UserProfile, intent: TaskIntent) -> float:
    if intent.requested_autonomy is None:
        return profile.autonomy_preference
    return float(intent.requested_autonomy)


def pentad_authority_weights(
    system: PentadSystem,
    profile: UserProfile,
    intent: TaskIntent,
) -> Dict[str, float]:
    """Compute normalized authority split over the 5 Pentad bodies."""

    expertise = _domain_expertise(profile, intent.domain)
    autonomy = _effective_autonomy(profile, intent)
    trust = float(np.clip(trust_modulation(system), 0.0, 1.0))

    phi_univ = system.bodies[PentadLabel.UNIV].phi
    phi_brain = system.bodies[PentadLabel.BRAIN].phi
    phi_human = system.bodies[PentadLabel.HUMAN].phi
    phi_ai = system.bodies[PentadLabel.AI].phi
    phi_trust = system.bodies[PentadLabel.TRUST].phi

    raw = {
        PentadLabel.UNIV: phi_univ,
        PentadLabel.BRAIN: phi_brain * (0.50 + 0.50 * expertise),
        PentadLabel.HUMAN: phi_human * (0.55 + 0.45 * expertise) * (1.15 - 0.50 * autonomy),
        PentadLabel.AI: phi_ai * (0.55 + 0.45 * autonomy) * (1.00 + 0.25 * expertise),
        PentadLabel.TRUST: phi_trust * (0.75 + 0.25 * trust),
    }

    total = sum(max(0.0, float(v)) for v in raw.values())
    norm = max(total, _EPS)
    return {label: float(np.clip(raw[label] / norm, 0.0, 1.0)) for label in PENTAD_LABELS}


def shipwide_readiness(
    system: PentadSystem,
    profile: UserProfile,
    intent: TaskIntent,
) -> float:
    """Scalar readiness score in [0,1] for the task under current Pentad state."""

    trust = float(np.clip(trust_modulation(system), 0.0, 1.0))
    personalization = personalization_factor(profile, intent.domain)

    phi_univ = system.bodies[PentadLabel.UNIV].phi
    phi_brain = system.bodies[PentadLabel.BRAIN].phi
    phi_human = system.bodies[PentadLabel.HUMAN].phi
    phi_ai = system.bodies[PentadLabel.AI].phi
    phi_trust = system.bodies[PentadLabel.TRUST].phi

    coupling = (
        0.25 * phi_univ
        + 0.20 * phi_brain
        + 0.20 * phi_human
        + 0.20 * phi_ai
        + 0.15 * phi_trust
    )

    risk_damping = 1.0 - 0.6 * float(intent.criticality)

    readiness = trust * personalization * coupling * risk_damping
    return float(np.clip(readiness, 0.0, 1.0))


def route_task_intent(
    system: PentadSystem,
    profile: UserProfile,
    intent: TaskIntent,
    protocols: Optional[Mapping[str, DomainProtocol]] = None,
) -> RoutedIntent:
    """Route one task request into execution mode + guardrails."""

    protocol_map = dict(default_domain_protocols()) if protocols is None else dict(protocols)
    if intent.domain not in protocol_map:
        raise ValueError(f"No protocol configured for domain={intent.domain!r}.")

    protocol = protocol_map[intent.domain]
    trust = float(np.clip(trust_modulation(system), 0.0, 1.0))
    readiness = shipwide_readiness(system, profile, intent)
    weights = pentad_authority_weights(system, profile, intent)

    requires_human_confirmation = (
        intent.criticality >= protocol.human_confirmation_threshold
        or trust < protocol.min_trust
        or protocol.implication_only
    )

    if trust < protocol.min_trust:
        mode = "hold"
        allowed_actions = ("stabilize_trust", "diagnose", "escalate")
        rationale = "Trust below protocol floor; action held pending stabilization."
        return RoutedIntent(
            execution_mode=mode,
            readiness=readiness,
            authority_weights=weights,
            requires_human_confirmation=True,
            implication_only=protocol.implication_only,
            allowed_actions=allowed_actions,
            rationale=rationale,
        )

    if protocol.implication_only:
        mode = "analysis_only"
        rationale = "Domain is implication-only in public layer; no direct actuation."
        return RoutedIntent(
            execution_mode=mode,
            readiness=readiness,
            authority_weights=weights,
            requires_human_confirmation=True,
            implication_only=True,
            allowed_actions=protocol.allowed_actions,
            rationale=rationale,
        )

    if readiness >= 0.66 and not requires_human_confirmation:
        mode = "autonomous_assist"
        rationale = "High readiness and within protocol guardrails for autonomous assist."
    elif readiness >= 0.33:
        mode = "supervised_assist"
        rationale = "Moderate readiness; proceed with supervised assist."
    else:
        mode = "manual_guidance"
        rationale = "Low readiness; route to manual guidance with AI support."

    return RoutedIntent(
        execution_mode=mode,
        readiness=readiness,
        authority_weights=weights,
        requires_human_confirmation=requires_human_confirmation,
        implication_only=False,
        allowed_actions=protocol.allowed_actions,
        rationale=rationale,
    )


def _clone_with_body_phi(system: PentadSystem, label: str, phi: float) -> PentadSystem:
    """Return a copy of ``system`` with one body's φ value replaced."""

    bodies = dict(system.bodies)
    old = bodies[label]
    bodies[label] = type(old)(
        node=old.node,
        phi=float(np.clip(phi, 0.0, 1.0)),
        n1=old.n1,
        n2=old.n2,
        k_cs=old.k_cs,
        label=old.label,
    )
    return PentadSystem(
        bodies=bodies,
        beta=system.beta,
        grace_steps=system.grace_steps,
        grace_decay=system.grace_decay,
        _trust_reservoir=system._trust_reservoir,
        _grace_elapsed=system._grace_elapsed,
    )


class OrganizationPentad:
    """Multi-organization coupling state over a fleet of Pentad systems."""

    def __init__(self, organizations: Optional[Mapping[str, PentadSystem]] = None) -> None:
        self.organizations: Dict[str, PentadSystem] = dict(organizations or {})
        self._trust_links: Dict[str, set[str]] = {
            org_id: set() for org_id in self.organizations
        }

    def _ensure_org(self, org_id: str) -> PentadSystem:
        if org_id not in self.organizations:
            self.organizations[org_id] = PentadSystem.default()
            self._trust_links[org_id] = set()
        return self.organizations[org_id]

    def couple_organizations(self, org1_id: str, org2_id: str) -> Tuple[str, str]:
        """Bidirectionally couple two organizations through the trust field."""

        if org1_id == org2_id:
            self._ensure_org(org1_id)
            return (org1_id, org2_id)

        org1 = self._ensure_org(org1_id)
        org2 = self._ensure_org(org2_id)

        shared_trust = 0.5 * (
            trust_modulation(org1) + trust_modulation(org2)
        ) + 0.5 * BRAIDED_SOUND_SPEED
        shared_trust = float(np.clip(shared_trust, TRUST_PHI_MIN, 1.0))

        self.organizations[org1_id] = _clone_with_body_phi(
            org1, PentadLabel.TRUST, shared_trust
        )
        self.organizations[org2_id] = _clone_with_body_phi(
            org2, PentadLabel.TRUST, shared_trust
        )
        self._trust_links.setdefault(org1_id, set()).add(org2_id)
        self._trust_links.setdefault(org2_id, set()).add(org1_id)
        return (org1_id, org2_id)

    def get_stability_score(self) -> float:
        """Return an aggregate cross-organization stability score in [0, 1]."""

        if not self.organizations:
            return 0.0

        internal_scores = []
        for system in self.organizations.values():
            trust = float(np.clip(trust_modulation(system), 0.0, 1.0))
            defect = float(max(0.0, pentad_defect(system)))
            internal_scores.append(float(np.clip(0.65 * trust + 0.35 * (1.0 / (1.0 + defect)), 0.0, 1.0)))

        n_orgs = len(self.organizations)
        max_links = max(n_orgs * (n_orgs - 1), 1)
        link_count = sum(len(v) for v in self._trust_links.values())
        link_density = float(link_count / max_links)

        score = 0.8 * float(np.mean(internal_scores)) + 0.2 * link_density
        return float(np.clip(score, 0.0, 1.0))

    def detect_defection(self, org_id: str) -> bool:
        """Return True when an organization has decoupled from the shared braid."""

        system = self._ensure_org(org_id)
        trust = float(trust_modulation(system))
        links = len(self._trust_links.get(org_id, set()))
        defect = float(max(0.0, pentad_defect(system)))
        if trust < TRUST_PHI_MIN:
            return True
        if len(self.organizations) > 1 and links == 0:
            return True
        return bool(defect > 3.0)


class EnterpriseRoutingLayer:
    """Route enterprise decisions through the five-body Pentad hierarchy."""

    _DOMAIN_BODY_MAP: Dict[str, str] = {
        ShipDomain.CHORES: PentadLabel.UNIV,
        ShipDomain.ENGINEERING: PentadLabel.AI,
        ShipDomain.NAVIGATION: PentadLabel.UNIV,
        ShipDomain.PILOTING: PentadLabel.HUMAN,
        ShipDomain.EXOTIC_PROPULSION: PentadLabel.TRUST,
        "safety": PentadLabel.BRAIN,
        "biology": PentadLabel.BRAIN,
        "trust": PentadLabel.TRUST,
        "human": PentadLabel.HUMAN,
        "ai": PentadLabel.AI,
    }

    def __init__(self, organization_pentad: Optional[OrganizationPentad] = None) -> None:
        self.organization_pentad = (
            OrganizationPentad() if organization_pentad is None else organization_pentad
        )
        self._route_history: List[Dict[str, Any]] = []
        self._body_loads: Dict[str, float] = {label: 0.0 for label in PENTAD_LABELS}

    def route_decision(self, decision_id: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
        """Route a decision payload to the most appropriate Pentad body."""

        explicit_body = payload.get("body_id")
        if explicit_body in PENTAD_LABELS:
            body_id = str(explicit_body)
        else:
            domain = str(payload.get("domain", "")).lower()
            body_id = self._DOMAIN_BODY_MAP.get(domain, PentadLabel.HUMAN)

        entropy = float(payload.get("entropy", 1.0))
        criticality = float(np.clip(payload.get("criticality", 0.5), 0.0, 1.0))
        load = entropy * (1.0 + criticality)
        self._body_loads[body_id] += load

        route = {
            "decision_id": decision_id,
            "target_body": body_id,
            "payload": dict(payload),
            "load": load,
            "route_index": len(self._route_history),
        }
        self._route_history.append(route)
        return route

    def get_load_balance(self) -> Dict[str, Any]:
        """Return entropy-weighted load distribution across Pentad bodies."""

        total = float(sum(self._body_loads.values()))
        if total <= _EPS:
            distribution = {label: 0.0 for label in PENTAD_LABELS}
            entropy = 0.0
        else:
            distribution = {
                label: float(self._body_loads[label] / total) for label in PENTAD_LABELS
            }
            probs = np.array([p for p in distribution.values() if p > 0.0], dtype=float)
            entropy = float(-np.sum(probs * np.log2(probs)))
            entropy /= np.log2(len(PENTAD_LABELS))

        dominant_body = max(distribution, key=distribution.get)
        return {
            "distribution": distribution,
            "entropy": float(np.clip(entropy, 0.0, 1.0)),
            "dominant_body": dominant_body,
            "routes": len(self._route_history),
        }
