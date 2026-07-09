# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 549 — Lean4 NP-BC-1 Geometric Kernel Proof."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar549_lean4_np_bc1 import (
    GEOMETRIC_KERNEL_COMPONENTS,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    NP_BC1_STATUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REMAINING_SUB_GAPS,
    VERSION,
    advancement_certificate,
    geometric_kernel_components,
    np_bc1_proof_state,
    pillar_report,
    sub_gap_decomposition,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 549


def test_pillar_status():
    assert PILLAR_STATUS == "LEAN4_NP_BC1_GEOMETRIC_KERNEL_PROVED"


def test_version():
    assert VERSION == "v19.1"


# ─── Lean4 new file ──────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    # File must exist in repo
    assert path.exists(), f"NPBC1Kernel.lean not found at {path}"


def test_lean4_new_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 18


def test_lean4_new_file_status():
    assert LEAN4_NEW_FILE["status"] == "GEOMETRIC_KERNEL_PROVED"


def test_lean4_file_content_description():
    assert "Z₂" in LEAN4_NEW_FILE["content"]
    assert "UV-brane" in LEAN4_NEW_FILE["content"]


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorems_increased():
    assert LEAN4_THEOREM_COUNT["total"] > LEAN4_THEOREM_COUNT["total_previous"]


def test_total_theorems_value():
    assert LEAN4_THEOREM_COUNT["total"] == 109


def test_new_theorems_count():
    assert LEAN4_THEOREM_COUNT["total_new"] == 18


def test_npbc1_file_in_count():
    assert "NPBC1Kernel.lean" in LEAN4_THEOREM_COUNT
    assert LEAN4_THEOREM_COUNT["NPBC1Kernel.lean"] == 18


def test_previous_files_unchanged():
    assert LEAN4_THEOREM_COUNT["CCRKernel.lean"] == 18
    assert LEAN4_THEOREM_COUNT["ERWormhole.lean"] == 13


# ─── NP-BC-1 status ──────────────────────────────────────────────────────────

def test_np_bc1_kernel_proved():
    assert NP_BC1_STATUS["kernel_proved"] is True


def test_np_bc1_full_proof_not_achieved():
    assert NP_BC1_STATUS["full_proof_achieved"] is False


def test_np_bc1_blocking_reason_nonempty():
    assert len(NP_BC1_STATUS["blocking_reason"]) > 20


# ─── Geometric kernel components ─────────────────────────────────────────────

def test_geometric_kernel_count():
    components = geometric_kernel_components()
    assert len(components) >= 10


def test_all_kernel_components_proved():
    for comp in geometric_kernel_components():
        assert comp["status"] == "PROVED", f"{comp['name']} is not PROVED"


def test_z2_involution_in_kernel():
    names = [c["name"] for c in geometric_kernel_components()]
    assert any("involution" in n.lower() or "Z₂" in n for n in names)


def test_np_bc1_summary_in_kernel():
    names = [c["name"] for c in geometric_kernel_components()]
    assert any("geometric kernel" in n.lower() or "summary" in n.lower() for n in names)


def test_kernel_theorems_nonempty():
    for comp in geometric_kernel_components():
        assert comp["theorem"]


# ─── Remaining sub-gaps ───────────────────────────────────────────────────────

def test_sub_gap_count():
    gaps = sub_gap_decomposition()
    assert len(gaps) == 3


def test_all_sub_gaps_blocking():
    for gap in sub_gap_decomposition():
        assert gap["blocking"] is True


def test_sub_gap_a_rs_geometry():
    gaps = sub_gap_decomposition()
    assert any("RS" in g["name"] or "warped" in g["name"] or "Randall" in g["description"]
               for g in gaps)


def test_sub_gap_b_path_integral():
    gaps = sub_gap_decomposition()
    assert any("path" in g["description"].lower() or "saddle" in g["description"].lower()
               for g in gaps)


def test_sub_gap_c_curved_background():
    gaps = sub_gap_decomposition()
    assert any("curved" in g["description"].lower() or "Riemannian" in g["description"]
               for g in gaps)


def test_sub_gaps_have_difficulty():
    for gap in sub_gap_decomposition():
        assert "difficulty" in gap


# ─── NP-BC-1 proof state ─────────────────────────────────────────────────────

def test_proof_state_keys():
    state = np_bc1_proof_state()
    for key in ["axiom", "status", "kernel_file", "kernel_theorems",
                "full_proof_achieved", "remaining_sub_gaps"]:
        assert key in state


def test_proof_state_axiom():
    state = np_bc1_proof_state()
    assert state["axiom"] == "erepr_np_bc_1"


def test_proof_state_remaining_sub_gaps():
    state = np_bc1_proof_state()
    assert state["remaining_sub_gaps"] == 3


def test_proof_state_not_full():
    state = np_bc1_proof_state()
    assert state["full_proof_achieved"] is False


# ─── Advancement certificate ─────────────────────────────────────────────────

def test_advancement_certificate_keys():
    cert = advancement_certificate()
    for key in ["pillar", "status", "new_lean4_file", "theorems_added",
                "total_lean4_theorems", "epistemic_delta",
                "what_is_claimed", "what_is_NOT_claimed", "toe_score_delta"]:
        assert key in cert


def test_toe_score_unchanged():
    cert = advancement_certificate()
    assert cert["toe_score_delta"] == pytest.approx(0.0)


def test_total_lean4_theorems_in_cert():
    cert = advancement_certificate()
    assert cert["total_lean4_theorems"] == 109


def test_not_claimed_full_proof():
    cert = advancement_certificate()
    not_claimed_text = " ".join(cert["what_is_NOT_claimed"])
    assert "NOT" in not_claimed_text or "not" in not_claimed_text


def test_erepr_not_proved():
    cert = advancement_certificate()
    not_claimed = " ".join(cert["what_is_NOT_claimed"])
    assert "ER=EPR" in not_claimed or "NP-BC" in not_claimed


# ─── Full report ─────────────────────────────────────────────────────────────

def test_pillar_report_structure():
    report = pillar_report()
    assert report["pillar"] == 549
    assert report["parent_pillar"] == 545
    assert report["toe_score_delta"] == pytest.approx(0.0)
    assert report["adjacent_track"] is False
