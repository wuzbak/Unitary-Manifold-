# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
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
from typing import Dict, Mapping, Optional, Tuple

import numpy as np

from unitary_pentad import (
    PENTAD_LABELS,
    PentadLabel,
    PentadSystem,
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
