# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 560 — NP-BC-1 Sub-gap A: RS Warp Factor Geometry Kernel."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar560_np_bc1_subgap_a_rs_geometry import (
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PROVED_COMPONENTS,
    REMAINING_GAPS,
    SUBGAP_A_STATUS,
    VERSION,
    advancement_certificate,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_a_proof_state,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 560


def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC1_SUBGAP_A_RS_GEOMETRY_KERNEL_PROVED"


def test_version():
    assert VERSION == "v19.3"


# ─── Lean4 file ───────────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    assert path.exists(), f"NPBC1SubgapA.lean not found at {path}"


def test_lean4_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 12


def test_lean4_file_status():
    assert LEAN4_NEW_FILE["status"] == "RS_GEOMETRY_KERNEL_PROVED"


def test_lean4_file_content_rs():
    content = LEAN4_NEW_FILE["content"]
    assert "fixed point" in content.lower() or "Fixed" in content


def test_lean4_file_content_kcs():
    content = LEAN4_NEW_FILE["content"]
    assert "74" in content or "k_CS" in content.lower() or "k_cs" in content.lower()


def test_lean4_file_honest_status():
    assert "PARTIALLY_CLOSED" in LEAN4_NEW_FILE["honest_status"]


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorem_count():
    assert LEAN4_THEOREM_COUNT["total"] == 151


def test_new_theorems():
    assert LEAN4_THEOREM_COUNT["total_new"] == 12


def test_previous_total():
    assert LEAN4_THEOREM_COUNT["total_previous"] == 139


def test_subgap_a_entry():
    assert LEAN4_THEOREM_COUNT["NPBC1SubgapA.lean"] == 12


def test_npbc1_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC1Kernel.lean"] == 18


def test_npbc2_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC2Kernel.lean"] == 16


def test_npbc3_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC3Kernel.lean"] == 14


# ─── Sub-gap A status ─────────────────────────────────────────────────────────

def test_subgap_a_kernel_proved():
    assert SUBGAP_A_STATUS["kernel_proved"] is True


def test_subgap_a_full_closure_not_achieved():
    assert SUBGAP_A_STATUS["full_closure_achieved"] is False


def test_subgap_a_source():
    assert "549" in SUBGAP_A_STATUS["source"]


# ─── Proved components ───────────────────────────────────────────────────────

def test_proved_components_count():
    components = proved_components()
    assert len(components) >= 10


def test_proved_components_all_proved():
    for c in proved_components():
        assert c["status"] == "PROVED"


def test_proved_components_has_fixed_points():
    names = [c["name"] for c in proved_components()]
    assert any("fixed point" in n.lower() for n in names)


def test_proved_components_has_kk_levels():
    names = [c["name"] for c in proved_components()]
    assert any("kk" in n.lower() or "level" in n.lower() for n in names)


def test_proved_components_has_braid():
    names = [c["name"] for c in proved_components()]
    assert any("braid" in n.lower() for n in names)


def test_proved_components_has_summary():
    names = [c["name"] for c in proved_components()]
    assert any("kernel" in n.lower() or "summary" in n.lower() for n in names)


# ─── Remaining gaps ───────────────────────────────────────────────────────────

def test_remaining_gaps_not_empty():
    assert len(REMAINING_GAPS) >= 1


def test_remaining_gaps_has_bessel():
    names = [g["name"] for g in REMAINING_GAPS]
    assert any("bessel" in n.lower() for n in names)


def test_remaining_gaps_has_difficulty():
    for gap in REMAINING_GAPS:
        assert "difficulty" in gap


# ─── subgap_a_proof_state ────────────────────────────────────────────────────

def test_subgap_a_proof_state_subgap():
    state = subgap_a_proof_state()
    assert state["subgap"] == "A"


def test_subgap_a_proof_state_status():
    state = subgap_a_proof_state()
    assert state["status"] == "RS_GEOMETRY_KERNEL_PROVED"


def test_subgap_a_proof_state_theorems():
    state = subgap_a_proof_state()
    assert state["kernel_theorems"] == 12


def test_subgap_a_proof_state_not_closed():
    state = subgap_a_proof_state()
    assert state["full_closure_achieved"] is False


# ─── remaining_gap_assessment ────────────────────────────────────────────────

def test_gap_assessment_partial_closure():
    assessment = remaining_gap_assessment()
    assert assessment["partial_closure_achieved"] is True


def test_gap_assessment_fraction():
    assessment = remaining_gap_assessment()
    assert 0.0 < assessment["full_closure_fraction"] < 1.0


def test_gap_assessment_has_blocker():
    assessment = remaining_gap_assessment()
    assert assessment["primary_blocker"] is not None


# ─── advancement_certificate ─────────────────────────────────────────────────

def test_advancement_cert_pillar():
    cert = advancement_certificate()
    assert cert["pillar"] == 560


def test_advancement_cert_subgap():
    cert = advancement_certificate()
    assert cert["subgap"] == "A"


def test_advancement_cert_theorems():
    cert = advancement_certificate()
    assert cert["theorems_added"] == 12
    assert cert["total_lean4_theorems"] == 151


def test_advancement_cert_toe_zero():
    cert = advancement_certificate()
    assert cert["toe_score_delta"] == 0.0


def test_advancement_cert_has_claims():
    cert = advancement_certificate()
    assert len(cert["what_is_claimed"]) >= 4


def test_advancement_cert_has_anti_claims():
    cert = advancement_certificate()
    assert len(cert["what_is_NOT_claimed"]) >= 2


def test_advancement_cert_not_fully_closed():
    cert = advancement_certificate()
    not_claimed = " ".join(cert["what_is_NOT_claimed"])
    assert "NOT fully closed" in not_claimed or "NOT closed" in not_claimed


# ─── pillar_report ────────────────────────────────────────────────────────────

def test_pillar_report_complete():
    report = pillar_report()
    for key in ["pillar", "title", "status", "version",
                "lean4_new_file", "lean4_theorem_count", "toe_score_delta"]:
        assert key in report


def test_pillar_report_toe_zero():
    report = pillar_report()
    assert report["toe_score_delta"] == 0.0


def test_pillar_report_not_adjacent():
    report = pillar_report()
    assert report["adjacent_track"] is False


def test_pillar_report_parent():
    report = pillar_report()
    assert report["parent_pillar"] == 549
