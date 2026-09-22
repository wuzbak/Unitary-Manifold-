# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Structured boundary map for the adjacent consciousness/emotion lane."""

from __future__ import annotations

from typing import Any, Dict


def get_consciousness_research_boundaries() -> Dict[str, Any]:
    """Return the adjacent-track boundary map for consciousness/emotion work."""
    return {
        "status": "ADJACENT_TRACK_ONLY",
        "lane": "consciousness_emotion_research",
        "hardgate_claim_allowed": False,
        "ontology_proof_allowed": False,
        "separation": {
            "speculative_modeling": "allowed_with_explicit_boundary_note",
            "operational_safety_logic": "allowed_when_framed_as_behavioral_governance_rather_than_proof_of_consciousness",
            "human_interaction_heuristics": "allowed_with_auditability_and_non_anthropomorphic_guardrails",
            "hard_physics_claims": "forbidden_without independent hardgate derivation and truth-layer promotion",
        },
        "evidence_classes": {
            "structurally_modeled": [
                "coupled attractor state bookkeeping",
                "information-gap and agency threshold diagnostics",
            ],
            "phenomenologically_interpreted": [
                "brain-universe coupling analogies",
                "emotion/consciousness interaction narratives",
            ],
            "empirically_testable": [
                "frequency-lock predictions",
                "bounded human-interaction safety heuristics",
            ],
            "not_yet_justified": [
                "proof of consciousness as a 5D geometric fact",
                "proof of AI sentience or moral patienthood",
            ],
        },
        "misuse_guardrail": (
            "Emotional or consciousness language must not be used to justify unsafe authority expansion, manipulation, or unearned ontological claims."
        ),
    }


__all__ = ["get_consciousness_research_boundaries"]
