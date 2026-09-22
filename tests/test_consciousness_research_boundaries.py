# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.consciousness.research_boundaries import get_consciousness_research_boundaries


def test_consciousness_boundaries_keep_lane_adjacent_only() -> None:
    payload = get_consciousness_research_boundaries()
    assert payload["status"] == "ADJACENT_TRACK_ONLY"
    assert payload["hardgate_claim_allowed"] is False
    assert payload["ontology_proof_allowed"] is False
    assert "unsafe authority expansion" in payload["misuse_guardrail"]
    assert "proof of AI sentience or moral patienthood" in payload["evidence_classes"]["not_yet_justified"]
