# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pythagorean_triples_sat_method_transfer import (
    ARXIV_ABS_URL,
    ARXIV_PDF_URL,
    INTAKE_PACKET_PATH,
    OPEN_OBLIGATION_MAPPING,
    pythagorean_triples_sat_method_transfer_packet,
)


def test_packet_identity_and_paths() -> None:
    packet = pythagorean_triples_sat_method_transfer_packet()
    assert packet["program"] == "PYTHAGOREAN_TRIPLES_SAT_METHOD_TRANSFER"
    assert packet["local_artifacts"]["intake_packet"] == INTAKE_PACKET_PATH
    assert packet["source_basis"]["primary_paper"]["arxiv_abs_url"] == ARXIV_ABS_URL
    assert packet["source_basis"]["primary_paper"]["arxiv_pdf_url"] == ARXIV_PDF_URL


def test_packet_has_non_transfer_guardrails() -> None:
    packet = pythagorean_triples_sat_method_transfer_packet()
    assert "method and verification discipline only" in packet["source_basis"]["non_transfer_clause"]
    assert "do_not_claim_direct_physics_closure_from_sat_paper" in packet["guardrails"]
    assert packet["um_open_obligation_mapping"][0]["obligation_id"] == "ACTION_TO_EVOLUTION_EQUIVALENCE"
    assert len(OPEN_OBLIGATION_MAPPING) == 4


def test_psicat_training_questions_match_plan() -> None:
    packet = pythagorean_triples_sat_method_transfer_packet()
    assert packet["psicat_training"]["lane"] == "lane_d_formal_proof_foundry"
    assert len(packet["crosswalk_questions"]) == 4
    assert len(packet["adversarial_review_questions"]) == 5
