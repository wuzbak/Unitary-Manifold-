# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 566 — NP-BC-2 Sub-gap F: UV-IR Consistency Kernel."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar566_np_bc2_subgap_f_uv_ir import (
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    NP_BC2_OVERALL_STATUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    REMAINING_GAPS,
    SUBGAP_F_STATUS,
    VERSION,
    advancement_certificate,
    np_bc2_subgap_summary,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_f_proof_state,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 566


def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC2_SUBGAP_F_UV_IR_CONSISTENCY_KERNEL_PROVED"


def test_pillar_title_contains_subgap_f():
    assert "F" in PILLAR_TITLE or "UV" in PILLAR_TITLE


def test_version():
    assert VERSION == "v19.4"


# ─── Lean4 file ───────────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    assert path.exists(), f"NPBC2SubgapF.lean not found at {path}"


def test_lean4_file_path_correct():
    assert "NPBC2SubgapF" in LEAN4_NEW_FILE["path"]


def test_lean4_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 11


def test_lean4_file_status():
    assert LEAN4_NEW_FILE["status"] == "UV_IR_CONSISTENCY_KERNEL_PROVED"


def test_lean4_file_content_uv_ir():
    content = LEAN4_NEW_FILE["content"]
    assert "UV" in content or "IR" in content or "brane" in content.lower()


def test_lean4_file_content_kcs():
    content = LEAN4_NEW_FILE["content"]
    assert "k_cs" in content.lower() or "k_CS" in content


def test_lean4_file_honest_status_partially_closed():
    assert "PARTIALLY_CLOSED" in LEAN4_NEW_FILE["honest_status"]


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorem_count():
    assert LEAN4_THEOREM_COUNT["total"] == 206


def test_new_theorems():
    assert LEAN4_THEOREM_COUNT["total_new"] == 11


def test_previous_total():
    assert LEAN4_THEOREM_COUNT["total_previous"] == 195


def test_subgap_f_entry():
    assert LEAN4_THEOREM_COUNT["NPBC2SubgapF.lean"] == 11


def test_subgap_d_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC2SubgapD.lean"] == 11


def test_subgap_e_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC2SubgapE.lean"] == 11


def test_theorem_count_arithmetic():
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_THEOREM_COUNT["total_new"] == LEAN4_THEOREM_COUNT["total"]


# ─── Sub-gap F status ─────────────────────────────────────────────────────────

def test_subgap_f_kernel_proved():
    assert SUBGAP_F_STATUS["kernel_proved"] is True


def test_subgap_f_full_closure_not_achieved():
    assert SUBGAP_F_STATUS["full_closure_achieved"] is False


def test_subgap_f_source_references_pillar_556():
    assert "556" in SUBGAP_F_STATUS["source"]


def test_subgap_f_advance_over_556():
    assert len(SUBGAP_F_STATUS["advance_over_pillar_556"]) > 20


# ─── NP-BC-2 overall status ──────────────────────────────────────────────────

def test_np_bc2_all_three_subgap_kernels_proved():
    assert NP_BC2_OVERALL_STATUS["all_three_subgaps_kernel_proved"] is True


def test_np_bc2_not_fully_closed():
    assert NP_BC2_OVERALL_STATUS["full_np_bc2_closed"] is False


def test_np_bc2_total_subgap_theorems():
    assert NP_BC2_OVERALL_STATUS["total_np_bc2_subgap_theorems"] == 33


def test_np_bc2_blocking_residuals():
    assert NP_BC2_OVERALL_STATUS["blocking_residuals_per_subgap"] == 3
    assert NP_BC2_OVERALL_STATUS["total_blocking_residuals"] == 9


def test_np_bc2_has_all_three_subgap_keys():
    assert "subgap_d_mixing_angle" in NP_BC2_OVERALL_STATUS
    assert "subgap_e_saddle_bound" in NP_BC2_OVERALL_STATUS
    assert "subgap_f_uv_ir_consistency" in NP_BC2_OVERALL_STATUS


def test_np_bc2_subgap_d_label():
    assert "MIXING_ANGLE_KERNEL_PROVED" in NP_BC2_OVERALL_STATUS["subgap_d_mixing_angle"]


def test_np_bc2_subgap_e_label():
    assert "SADDLE_BOUND_KERNEL_PROVED" in NP_BC2_OVERALL_STATUS["subgap_e_saddle_bound"]


def test_np_bc2_subgap_f_label():
    assert "UV_IR_CONSISTENCY_KERNEL_PROVED" in NP_BC2_OVERALL_STATUS["subgap_f_uv_ir_consistency"]


# ─── Proved components ───────────────────────────────────────────────────────

def test_proved_components_count():
    components = proved_components()
    assert len(components) >= 8


def test_proved_components_all_proved():
    for c in proved_components():
        assert c["status"] == "PROVED"


def test_proved_components_has_uv_brane():
    names = [c["name"] for c in proved_components()]
    assert any("uv" in n.lower() or "UV" in n for n in names)


def test_proved_components_has_ir_brane():
    names = [c["name"] for c in proved_components()]
    assert any("ir" in n.lower() or "IR" in n for n in names)


def test_proved_components_has_bc_distinct():
    names = [c["name"] for c in proved_components()]
    assert any("distinct" in n.lower() or "dirichlet" in n.lower() for n in names)


def test_proved_components_has_summary():
    names = [c["name"] for c in proved_components()]
    assert any("summary" in n.lower() or "kernel" in n.lower() for n in names)


def test_proved_components_kcs_content():
    contents = [c["content"] for c in proved_components()]
    assert any("74" in c for c in contents)


# ─── Remaining gaps ───────────────────────────────────────────────────────────

def test_remaining_gaps_not_empty():
    gaps = remaining_gap_assessment()
    assert len(gaps) >= 1


def test_remaining_gaps_all_open():
    for gap in remaining_gap_assessment():
        assert gap["status"] == "OPEN"


def test_remaining_gaps_has_curved_background():
    names = [g["name"] for g in remaining_gap_assessment()]
    assert any("curved" in n.lower() or "wormhole" in n.lower() or "background" in n.lower() for n in names)


def test_remaining_gaps_have_reason():
    for gap in remaining_gap_assessment():
        assert "reason" in gap


# ─── subgap_f_proof_state ────────────────────────────────────────────────────

def test_subgap_f_proof_state_subgap():
    state = subgap_f_proof_state()
    assert state["subgap"] == "F"


def test_subgap_f_proof_state_bc():
    state = subgap_f_proof_state()
    assert state["bc"] == "NP-BC-2"


def test_subgap_f_proof_state_status():
    state = subgap_f_proof_state()
    assert state["status"] == "NP_BC2_SUBGAP_F_UV_IR_CONSISTENCY_KERNEL_PROVED"


def test_subgap_f_proof_state_all_three_proved():
    state = subgap_f_proof_state()
    assert state["np_bc2_all_three_subgap_kernels_proved"] is True


def test_subgap_f_proof_state_not_closed():
    state = subgap_f_proof_state()
    assert state["full_closure"] is False


def test_subgap_f_proof_state_theorems():
    state = subgap_f_proof_state()
    assert state["lean4_theorems"] == 11


# ─── np_bc2_subgap_summary ────────────────────────────────────────────────────

def test_np_bc2_summary_has_all_subgaps():
    summary = np_bc2_subgap_summary()
    assert "subgap_D" in summary
    assert "subgap_E" in summary
    assert "subgap_F" in summary


def test_np_bc2_summary_subgap_d_pillar():
    summary = np_bc2_subgap_summary()
    assert summary["subgap_D"]["pillar"] == 564


def test_np_bc2_summary_subgap_e_pillar():
    summary = np_bc2_subgap_summary()
    assert summary["subgap_E"]["pillar"] == 565


def test_np_bc2_summary_subgap_f_pillar():
    summary = np_bc2_subgap_summary()
    assert summary["subgap_F"]["pillar"] == 566


def test_np_bc2_summary_total_theorems():
    summary = np_bc2_subgap_summary()
    assert summary["np_bc2_total_subgap_theorems"] == 33


def test_np_bc2_summary_not_full_proof():
    summary = np_bc2_subgap_summary()
    assert summary["np_bc2_full_proof"] is False


def test_np_bc2_summary_theorem_total():
    summary = np_bc2_subgap_summary()
    d = summary["subgap_D"]["theorems"]
    e = summary["subgap_E"]["theorems"]
    f = summary["subgap_F"]["theorems"]
    assert d + e + f == 33


# ─── advancement_certificate ─────────────────────────────────────────────────

def test_advancement_cert_pillar():
    cert = advancement_certificate()
    assert cert["pillar"] == 566


def test_advancement_cert_subgap():
    cert = advancement_certificate()
    assert cert["subgap"] == "F"


def test_advancement_cert_bc():
    cert = advancement_certificate()
    assert cert["bc"] == "NP-BC-2"


def test_advancement_cert_theorems_added():
    cert = advancement_certificate()
    assert cert["theorems_added"] == 11


def test_advancement_cert_total_theorems():
    cert = advancement_certificate()
    assert cert["total_lean4_theorems"] == 206


def test_advancement_cert_np_bc2_milestone():
    cert = advancement_certificate()
    assert "np_bc2_milestone" in cert
    assert "D/E/F" in cert["np_bc2_milestone"] or "D, E, F" in cert["np_bc2_milestone"]


def test_advancement_cert_not_closed():
    cert = advancement_certificate()
    not_claimed = " ".join(cert["what_is_NOT_claimed"])
    assert "NOT" in not_claimed


def test_advancement_cert_erepr_not_proved():
    cert = advancement_certificate()
    not_claimed = " ".join(cert["what_is_NOT_claimed"])
    assert "ER=EPR" in not_claimed


# ─── pillar_report ────────────────────────────────────────────────────────────

def test_pillar_report_complete():
    report = pillar_report()
    for key in ["pillar", "title", "status", "version", "lean4",
                "theorem_count", "subgap_f_status", "np_bc2_overall",
                "proved", "remaining", "certificate"]:
        assert key in report


def test_pillar_report_pillar_number():
    report = pillar_report()
    assert report["pillar"] == 566


def test_pillar_report_version():
    report = pillar_report()
    assert report["version"] == "v19.4"


def test_pillar_report_np_bc2_overall_in_report():
    report = pillar_report()
    assert report["np_bc2_overall"]["all_three_subgaps_kernel_proved"] is True


def test_pillar_report_np_bc2_summary():
    report = pillar_report()
    assert "np_bc2_summary" in report
    assert report["np_bc2_summary"]["np_bc2_full_proof"] is False


def test_pillar_report_proved_list():
    report = pillar_report()
    assert isinstance(report["proved"], list)


def test_pillar_report_theorem_count_total():
    report = pillar_report()
    assert report["theorem_count"]["total"] == 206
