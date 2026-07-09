# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 562 — NP-BC-1 Sub-gap C: Curved-Background Orbifold Consistency."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar562_np_bc1_subgap_c_curved_orbifold import (
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    NP_BC1_OVERALL_STATUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PROVED_COMPONENTS,
    REMAINING_GAPS,
    SUBGAP_C_STATUS,
    VERSION,
    advancement_certificate,
    flat_limit_consistency_check,
    np_bc1_subgap_summary,
    pillar_report,
    subgap_c_proof_state,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 562


def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC1_SUBGAP_C_CURVED_ORBIFOLD_KERNEL_PROVED"


def test_version():
    assert VERSION == "v19.3"


# ─── Lean4 file ───────────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    assert path.exists(), f"NPBC1SubgapC.lean not found at {path}"


def test_lean4_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 11


def test_lean4_file_status():
    assert LEAN4_NEW_FILE["status"] == "CURVED_ORBIFOLD_KERNEL_PROVED"


def test_lean4_file_content_curved():
    content = LEAN4_NEW_FILE["content"]
    assert "warp" in content.lower() or "flat" in content.lower()


def test_lean4_file_honest_status():
    assert "PARTIALLY_CLOSED" in LEAN4_NEW_FILE["honest_status"]


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorem_count():
    assert LEAN4_THEOREM_COUNT["total"] == 173


def test_new_theorems():
    assert LEAN4_THEOREM_COUNT["total_new"] == 11


def test_previous_total():
    assert LEAN4_THEOREM_COUNT["total_previous"] == 162


def test_subgap_c_entry():
    assert LEAN4_THEOREM_COUNT["NPBC1SubgapC.lean"] == 11


def test_subgap_a_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC1SubgapA.lean"] == 12


def test_subgap_b_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC1SubgapB.lean"] == 11


# ─── Sub-gap C status ─────────────────────────────────────────────────────────

def test_subgap_c_kernel_proved():
    assert SUBGAP_C_STATUS["kernel_proved"] is True


def test_subgap_c_full_closure_not_achieved():
    assert SUBGAP_C_STATUS["full_closure_achieved"] is False


def test_subgap_c_has_bridge():
    assert "bridge" in SUBGAP_C_STATUS


# ─── Proved components ───────────────────────────────────────────────────────

def test_proved_components_count():
    assert len(PROVED_COMPONENTS) >= 9


def test_proved_components_all_proved():
    for c in PROVED_COMPONENTS:
        assert c["status"] == "PROVED"


def test_proved_components_has_warp_factor():
    names = [c["name"].lower() for c in PROVED_COMPONENTS]
    assert any("warp" in n for n in names)


def test_proved_components_has_z2():
    names = [c["name"].lower() for c in PROVED_COMPONENTS]
    assert any("z₂" in n or "z2" in n for n in names)


def test_proved_components_has_braid():
    names = [c["name"].lower() for c in PROVED_COMPONENTS]
    assert any("braid" in n or "topolog" in n for n in names)


# ─── NP-BC-1 overall status ──────────────────────────────────────────────────

def test_np_bc1_overall_total_theorems():
    # 18 + 12 + 11 + 11 = 52
    assert NP_BC1_OVERALL_STATUS["total_np_bc1_theorems"] == 52


def test_np_bc1_overall_not_proved():
    assert NP_BC1_OVERALL_STATUS["full_proof_achieved"] is False


def test_np_bc1_overall_remaining_gaps():
    assert len(NP_BC1_OVERALL_STATUS["remaining_hard_gaps"]) >= 3


# ─── flat_limit_consistency_check ────────────────────────────────────────────

def test_flat_limit_zero_mode_even():
    check = flat_limit_consistency_check()
    assert check["zero_mode_z2_even"] is True


def test_flat_limit_kk1_odd():
    check = flat_limit_consistency_check()
    assert check["kk1_z2_odd"] is True


def test_flat_limit_winding_odd():
    check = flat_limit_consistency_check()
    assert check["winding_z2_odd"] is True


def test_flat_limit_braid_pair():
    check = flat_limit_consistency_check()
    assert check["braid_pair"] is True


def test_flat_limit_kk_half_level():
    check = flat_limit_consistency_check()
    assert check["kk_half_level"] is True


def test_flat_limit_all_consistent():
    check = flat_limit_consistency_check()
    assert check["all_consistent"] is True


# ─── np_bc1_subgap_summary ───────────────────────────────────────────────────

def test_subgap_summary_has_all_three():
    summary = np_bc1_subgap_summary()
    assert "subgap_A" in summary
    assert "subgap_B" in summary
    assert "subgap_C" in summary


def test_subgap_summary_pillars():
    summary = np_bc1_subgap_summary()
    assert summary["subgap_A"]["pillar"] == 560
    assert summary["subgap_B"]["pillar"] == 561
    assert summary["subgap_C"]["pillar"] == 562


def test_subgap_summary_none_closed():
    summary = np_bc1_subgap_summary()
    assert summary["subgap_A"]["full_closure"] is False
    assert summary["subgap_B"]["full_closure"] is False
    assert summary["subgap_C"]["full_closure"] is False


def test_subgap_summary_np_bc1_total():
    summary = np_bc1_subgap_summary()
    assert summary["np_bc1_total_theorems"] == 52


def test_subgap_summary_no_full_proof():
    summary = np_bc1_subgap_summary()
    assert summary["np_bc1_full_proof"] is False


# ─── subgap_c_proof_state ────────────────────────────────────────────────────

def test_proof_state_subgap():
    state = subgap_c_proof_state()
    assert state["subgap"] == "C"


def test_proof_state_not_closed():
    state = subgap_c_proof_state()
    assert state["full_closure_achieved"] is False


def test_proof_state_flat_limit():
    state = subgap_c_proof_state()
    assert state["flat_limit_consistent"] is True


def test_proof_state_milestone():
    state = subgap_c_proof_state()
    assert state["np_bc1_all_three_subgap_kernels_proved"] is True


# ─── advancement_certificate ─────────────────────────────────────────────────

def test_advancement_cert_pillar():
    cert = advancement_certificate()
    assert cert["pillar"] == 562


def test_advancement_cert_subgap():
    cert = advancement_certificate()
    assert cert["subgap"] == "C"


def test_advancement_cert_theorems():
    cert = advancement_certificate()
    assert cert["theorems_added"] == 11
    assert cert["total_lean4_theorems"] == 173


def test_advancement_cert_sprint1_milestone():
    cert = advancement_certificate()
    assert "sprint_1_np_bc1_milestone" in cert
    assert "THREE" in cert["sprint_1_np_bc1_milestone"] or "three" in cert["sprint_1_np_bc1_milestone"].lower()


def test_advancement_cert_not_closed():
    cert = advancement_certificate()
    not_claimed = " ".join(cert["what_is_NOT_claimed"])
    assert "NOT fully closed" in not_claimed or "NOT closed" in not_claimed


def test_advancement_cert_has_subgap_summary():
    cert = advancement_certificate()
    assert "np_bc1_subgap_summary" in cert


# ─── pillar_report ────────────────────────────────────────────────────────────

def test_pillar_report_complete():
    report = pillar_report()
    for key in ["pillar", "title", "status", "version",
                "lean4_new_file", "lean4_theorem_count", "toe_score_delta"]:
        assert key in report


def test_pillar_report_has_overall_status():
    report = pillar_report()
    assert "np_bc1_overall_status" in report


def test_pillar_report_toe_zero():
    report = pillar_report()
    assert report["toe_score_delta"] == 0.0


def test_pillar_report_not_adjacent():
    report = pillar_report()
    assert report["adjacent_track"] is False
