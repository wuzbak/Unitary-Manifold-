# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 509 earned proof-advancement kernels."""

from src.core import pillar509_earned_proof_advancement as p509


def test_constants():
    assert p509.PILLAR_NUMBER == 509
    assert p509.PILLAR_STATUS == "EARNED_PROOF_ADVANCEMENT_KERNELS_CERTIFIED"
    assert p509.VERSION == "v15.6"
    assert len(p509.PROOF_KERNEL_KEYS) == 2
    assert len(p509.REMAINING_FULL_CLOSURE_KEYS) == 6


def test_earned_kernel_board_has_exact_keys():
    board = p509.earned_proof_kernel_board()
    assert sorted(board) == sorted(p509.PROOF_KERNEL_KEYS)
    assert all(entry["earned"] is True for entry in board.values())
    assert all(entry["promotion"] == "CONJECTURAL -> CONDITIONAL_THEOREM_KERNEL_PROVED" for entry in board.values())


def test_ccr_advances_to_conditional_theorem_kernel_without_full_closure():
    ccr = p509.earned_proof_kernel_board()["CCR_CONDITIONAL_WEYL_LIMIT_KERNEL"]
    assert ccr["source_lane_status"] == "CONJECTURAL"
    assert ccr["earned"] is True
    assert ccr["full_theorem_closed"] is False
    assert len(ccr["hypotheses"]) == 4
    assert len(ccr["proof_steps"]) == 4
    assert "Weyl phase commutator" in ccr["proved_claim"]
    assert "star product" in ccr["remaining_full_closure_residual"]


def test_er_epr_advances_to_conditional_theorem_kernel_without_full_closure():
    er_epr = p509.earned_proof_kernel_board()["ER_EPR_CONDITIONAL_HOMOLOGY_KERNEL"]
    assert er_epr["source_lane_status"] == "CONJECTURAL"
    assert er_epr["earned"] is True
    assert er_epr["full_theorem_closed"] is False
    assert len(er_epr["hypotheses"]) == 4
    assert len(er_epr["proof_steps"]) == 4
    assert "bijection" in er_epr["proved_claim"]
    assert "RT formula" in er_epr["remaining_full_closure_residual"]


def test_remaining_full_closure_board_keeps_external_and_full_proof_blocks():
    board = p509.remaining_full_closure_board()
    assert sorted(board) == sorted(p509.REMAINING_FULL_CLOSURE_KEYS)
    assert all(entry["claimed_as_closed"] is False for entry in board.values())
    assert board["FULL_NONPERTURBATIVE_5D_KK_QUANTUM_GRAVITY_CLOSURE"]["status"].startswith("NO_CLAIM__")
    assert board["P8_FULL_FUNCTIONAL_SPACE_PROOF"]["status"].startswith("NO_CLAIM__")
    assert board["EXTERNAL_L2_GAMMA_HMC_RECEIPT"]["status"].startswith("NO_CLAIM__")
    assert board["LEAN4_BUILD_RECEIPT"]["status"].startswith("NO_CLAIM__")
    assert board["CCR_UNCONDITIONAL_RS1_STAR_PRODUCT_THEOREM"]["status"] == "CONDITIONAL_THEOREM_KERNEL_PROVED__FULL_RS1_STAR_PRODUCT_PENDING"
    assert board["ER_EPR_UNCONDITIONAL_KK_RT_THEOREM"]["status"] == "CONDITIONAL_THEOREM_KERNEL_PROVED__FULL_KK_RT_DERIVATION_PENDING"


def test_proof_advancement_certificate_verdict():
    cert = p509.proof_advancement_certificate()
    assert cert["kernel_count"] == 2
    assert cert["remaining_full_closure_count"] == 6
    assert cert["kernel_keys_match"] is True
    assert cert["remaining_keys_match"] is True
    assert cert["all_kernels_earned"] is True
    assert cert["no_full_closure_overclaim"] is True
    assert cert["hardgate_score_delta"] == 0.0
    assert cert["verdict"] == "EARNED_CONDITIONAL_PROOF_ADVANCEMENT__FULL_CLOSURE_STILL_EVIDENCE_GATED"


def test_pillar_report_contains_kernels_remaining_closure_and_certificate():
    report = p509.pillar_report()
    assert report["pillar"] == 509
    assert report["status"] == p509.PILLAR_STATUS
    assert sorted(report["earned_proof_kernels"]) == sorted(p509.PROOF_KERNEL_KEYS)
    assert sorted(report["remaining_full_closure"]) == sorted(p509.REMAINING_FULL_CLOSURE_KEYS)
    assert report["certificate"]["verdict"] == "EARNED_CONDITIONAL_PROOF_ADVANCEMENT__FULL_CLOSURE_STILL_EVIDENCE_GATED"

