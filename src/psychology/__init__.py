# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""src/psychology — Pillar 24: Psychology & Cognition."""
from .cognition import (
    cognitive_phi_load, perception_snr_phi, attention_bandwidth_phi,
    memory_phi_trace, reasoning_phi, problem_solving_phi, creativity_phi,
    metacognition_phi, executive_phi_function, cognitive_phi_bias,
)
from .behavior import (
    motivation_phi_drive, reward_phi_signal, habit_phi_formation,
    decision_phi_threshold, risk_phi_tolerance, altruism_phi,
    aggression_phi_trigger, emotional_phi_regulation, behavioral_phi_flexibility,
    social_conformity_phi,
)
from .social_psychology import (
    group_phi_cohesion, social_phi_influence, prejudice_phi,
    conformity_phi_pressure, leadership_phi, trust_phi_network,
    crowd_phi_dynamics, social_identity_phi, cooperation_phi,
    social_phi_entropy,
)

__all__ = [
    "cognitive_phi_load", "perception_snr_phi", "attention_bandwidth_phi",
    "memory_phi_trace", "reasoning_phi", "problem_solving_phi",
    "creativity_phi", "metacognition_phi", "executive_phi_function",
    "cognitive_phi_bias",
    "motivation_phi_drive", "reward_phi_signal", "habit_phi_formation",
    "decision_phi_threshold", "risk_phi_tolerance", "altruism_phi",
    "aggression_phi_trigger", "emotional_phi_regulation",
    "behavioral_phi_flexibility", "social_conformity_phi",
    "group_phi_cohesion", "social_phi_influence", "prejudice_phi",
    "conformity_phi_pressure", "leadership_phi", "trust_phi_network",
    "crowd_phi_dynamics", "social_identity_phi", "cooperation_phi",
    "social_phi_entropy",
]
