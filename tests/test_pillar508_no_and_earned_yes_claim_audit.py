# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 508 no-claim / earned-yes audit."""

from src.core import pillar508_no_and_earned_yes_claim_audit as p508


def test_constants():
    assert p508.PILLAR_NUMBER == 508
    assert p508.PILLAR_STATUS == "NO_AND_EARNED_YES_AUDIT_COMPLETE"
    assert p508.VERSION == "v15.5"
    assert len(p508.NO_CLAIM_KEYS) == 6
    assert len(p508.EARNED_YES_KEYS) == 6


def test_no_claim_board_has_exact_required_keys():
    board = p508.no_claim_board()
    assert sorted(board) == sorted(p508.NO_CLAIM_KEYS)
    assert all(entry["status"].startswith("NO_CLAIM__") for entry in board.values())


def test_no_false_nonperturbative_5d_kk_quantum_gravity_closure():
    entry = p508.no_claim_board()["FULL_NONPERTURBATIVE_5D_KK_QUANTUM_GRAVITY_CLOSURE"]
    assert entry["claimed_as_closed"] is False
    assert entry["evidence_status"] == "ARCHITECTURE_LIMIT_CERTIFIED"
    assert "No full non-perturbative 5D-KK quantum-gravity closure" in entry["claim"]


def test_no_p8_full_functional_space_proof_claim():
    entry = p508.no_claim_board()["P8_FULL_FUNCTIONAL_SPACE_PROOF"]
    assert entry["claimed_as_closed"] is False
    assert entry["evidence_status"] == "NAMED_RESIDUAL"
    assert "No P8 full functional-space proof" in entry["claim"]


def test_no_external_l2_gamma_hmc_receipt_claim():
    entry = p508.no_claim_board()["EXTERNAL_L2_GAMMA_HMC_RECEIPT"]
    assert entry["claimed_as_closed"] is False
    assert entry["evidence_status"] == "EXTERNAL_CONFIRMATION_PACKET_READY__HMC_RECEIPT_PENDING"
    assert "No external L2/γ HMC receipt" in entry["claim"]


def test_no_lean4_build_receipt_claim():
    entry = p508.no_claim_board()["LEAN4_BUILD_RECEIPT"]
    assert entry["claimed_as_closed"] is False
    assert entry["evidence_status"] == "LOCAL_CERTIFICATE_MANIFEST_PRESENT__BUILD_RECEIPT_REQUIRED"
    assert "lake build" in entry["blocking_criterion"]


def test_ccr_and_er_epr_remain_conjectural_theorem_lanes():
    board = p508.no_claim_board()
    assert board["CCR_THEOREM_PROOF"]["claimed_as_closed"] is False
    assert board["ER_EPR_THEOREM_PROOF"]["claimed_as_closed"] is False
    assert board["CCR_THEOREM_PROOF"]["evidence_status"] == "CONJECTURAL"
    assert board["ER_EPR_THEOREM_PROOF"]["evidence_status"] == "CONJECTURAL"


def test_earned_yes_board_has_exact_required_keys():
    board = p508.earned_yes_board()
    assert sorted(board) == sorted(p508.EARNED_YES_KEYS)
    assert all(entry["earned"] is True for entry in board.values())


def test_earned_yes_scopes_are_limited_not_overclaimed():
    board = p508.earned_yes_board()
    assert board["P8_INTEGER_LATTICE_PROOF"]["scope"] == "integer winding lattice, not full functional space"
    assert board["FIVE_D_KK_STRUCTURAL_GAP_CERTIFIED"]["scope"] == "gap certification, not quantum-gravity closure"
    assert board["LEAN4_LOCAL_MANIFEST_PRESENT"]["scope"] == "local manifest only; no build receipt"
    assert board["CCR_ER_EPR_CONJECTURE_LANES_FORMALIZED"]["scope"] == "formal conjecture status, not theorem proof"


def test_claim_boundary_audit_verdict():
    audit = p508.claim_boundary_audit()
    assert audit["no_claim_count"] == 6
    assert audit["earned_yes_count"] == 6
    assert audit["no_claim_keys_match"] is True
    assert audit["earned_yes_keys_match"] is True
    assert audit["no_claims_clean"] is True
    assert audit["earned_yes_claims_earned"] is True
    assert audit["hardgate_score_delta"] == 0.0
    assert audit["verdict"] == "NO_FALSE_CLOSURE__YES_ONLY_WHEN_EARNED"


def test_pillar_report_contains_no_claims_yes_claims_and_audit():
    report = p508.pillar_report()
    assert report["pillar"] == 508
    assert report["status"] == p508.PILLAR_STATUS
    assert sorted(report["no_claims"]) == sorted(p508.NO_CLAIM_KEYS)
    assert sorted(report["earned_yes"]) == sorted(p508.EARNED_YES_KEYS)
    assert report["audit"]["verdict"] == "NO_FALSE_CLOSURE__YES_ONLY_WHEN_EARNED"
