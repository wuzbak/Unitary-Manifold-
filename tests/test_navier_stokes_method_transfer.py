# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.navier_stokes_method_transfer import (
    BRAID_AUDIT_ANCHOR,
    CURRICULUM_PACKET_PATH,
    INTAKE_PACKET_PATH,
    OPEN_OBLIGATION_MAPPING,
    navier_stokes_method_transfer_packet,
)


def test_packet_identity_and_paths() -> None:
    packet = navier_stokes_method_transfer_packet()
    assert packet["program"] == "NAVIER_STOKES_METHOD_TRANSFER"
    assert packet["local_artifacts"]["intake_packet"] == INTAKE_PACKET_PATH
    assert packet["local_artifacts"]["curriculum_packet"] == CURRICULUM_PACKET_PATH
    assert packet["source_basis"]["primary_basis"] == "user_problem_statement_summary"


def test_packet_has_non_transfer_guardrails() -> None:
    packet = navier_stokes_method_transfer_packet()
    assert "foundational obligation" in packet["source_basis"]["non_transfer_clause"]
    assert "do_not_promote_new_physics_closure_from_this_packet" in packet["guardrails"]
    assert "ACTION_TO_EVOLUTION_EQUIVALENCE" == packet["um_open_obligation_mapping"][0]["obligation_id"]


def test_action_and_braid_audits_are_explicit() -> None:
    packet = navier_stokes_method_transfer_packet()
    checklist = packet["action_to_evolution_sharpening"]["deliverable_checklist"]
    assert checklist == [
        "checkable action functional",
        "explicit Euler-Lagrange equations",
        "fixed variable/time-identification map",
        "residual comparison against implemented flow",
        "promotion-boundary note with exact verified perimeter",
    ]
    assert packet["braided_winding_audit"]["anchor_path"] == BRAID_AUDIT_ANCHOR
    assert len(packet["braided_winding_audit"]["structurally_conjectural_now"]) >= 1


def test_psicat_training_questions_match_plan() -> None:
    packet = navier_stokes_method_transfer_packet()
    assert packet["crosswalk_questions"] == [
        "what_is_structurally_analogous",
        "what_is_only_metaphorically_similar",
        "what_is_mathematically_reusable",
        "what_is_completely_non_transferable",
    ]
    assert len(packet["adversarial_review_questions"]) == 6
    assert len(OPEN_OBLIGATION_MAPPING) == 4
