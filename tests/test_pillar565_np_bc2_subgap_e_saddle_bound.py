# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 565 — NP-BC-2 Sub-gap E: Saddle-Point Expansion Bound Kernel."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar565_np_bc2_subgap_e_saddle_bound import (
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    NP_PERT_RATIO,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    REMAINING_GAPS,
    SUBGAP_E_STATUS,
    VERSION,
    advancement_certificate,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_e_proof_state,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 565


def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC2_SUBGAP_E_SADDLE_BOUND_KERNEL_PROVED"


def test_pillar_title_contains_subgap_e():
    assert "E" in PILLAR_TITLE or "Saddle" in PILLAR_TITLE


def test_version():
    assert VERSION == "v19.4"


def test_np_pert_ratio():
    assert NP_PERT_RATIO == 14  # 74 // 5


def test_np_pert_ratio_arithmetic():
    assert NP_PERT_RATIO == 74 // 5


# ─── Lean4 file ───────────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    assert path.exists(), f"NPBC2SubgapE.lean not found at {path}"


def test_lean4_file_path_correct():
    assert "NPBC2SubgapE" in LEAN4_NEW_FILE["path"]


def test_lean4_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 11


def test_lean4_file_status():
    assert LEAN4_NEW_FILE["status"] == "SADDLE_BOUND_KERNEL_PROVED"


def test_lean4_file_content_kcs():
    content = LEAN4_NEW_FILE["content"]
    assert "74" in content or "k_CS" in content.lower()


def test_lean4_file_content_positivity():
    content = LEAN4_NEW_FILE["content"]
    assert "bound" in content.lower() or "positiv" in content.lower()


def test_lean4_file_honest_status_partially_closed():
    assert "PARTIALLY_CLOSED" in LEAN4_NEW_FILE["honest_status"]


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorem_count():
    assert LEAN4_THEOREM_COUNT["total"] == 195


def test_new_theorems():
    assert LEAN4_THEOREM_COUNT["total_new"] == 11


def test_previous_total():
    assert LEAN4_THEOREM_COUNT["total_previous"] == 184


def test_subgap_e_entry():
    assert LEAN4_THEOREM_COUNT["NPBC2SubgapE.lean"] == 11


def test_subgap_d_entry_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC2SubgapD.lean"] == 11


def test_theorem_count_arithmetic():
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_THEOREM_COUNT["total_new"] == LEAN4_THEOREM_COUNT["total"]


# ─── Sub-gap E status ─────────────────────────────────────────────────────────

def test_subgap_e_kernel_proved():
    assert SUBGAP_E_STATUS["kernel_proved"] is True


def test_subgap_e_full_closure_not_achieved():
    assert SUBGAP_E_STATUS["full_closure_achieved"] is False


def test_subgap_e_np_pert_ratio_integer():
    assert SUBGAP_E_STATUS["np_pert_ratio_integer"] == 14


def test_subgap_e_source_references_pillar_556():
    assert "556" in SUBGAP_E_STATUS["source"]


def test_subgap_e_advance_over_556():
    assert len(SUBGAP_E_STATUS["advance_over_pillar_556"]) > 20


# ─── Proved components ───────────────────────────────────────────────────────

def test_proved_components_count():
    components = proved_components()
    assert len(components) >= 8


def test_proved_components_all_proved():
    for c in proved_components():
        assert c["status"] == "PROVED"


def test_proved_components_has_positivity():
    names = [c["name"] for c in proved_components()]
    assert any("positiv" in n.lower() or "bound" in n.lower() for n in names)


def test_proved_components_has_kcs_lower_bound():
    names = [c["name"] for c in proved_components()]
    assert any("k_cs" in n.lower() or "74" in n or "lower" in n.lower() for n in names)


def test_proved_components_has_monotone():
    names = [c["name"] for c in proved_components()]
    assert any("monotone" in n.lower() or "tower" in n.lower() for n in names)


def test_proved_components_has_summary():
    names = [c["name"] for c in proved_components()]
    assert any("summary" in n.lower() or "kernel" in n.lower() for n in names)


def test_proved_components_superadditivity():
    names = [c["name"] for c in proved_components()]
    assert any("superadd" in n.lower() or "additiv" in n.lower() for n in names)


def test_proved_components_first_excitation():
    contents = [c["content"] for c in proved_components()]
    assert any("74" in c for c in contents)


# ─── Remaining gaps ───────────────────────────────────────────────────────────

def test_remaining_gaps_not_empty():
    gaps = remaining_gap_assessment()
    assert len(gaps) >= 1


def test_remaining_gaps_all_open():
    for gap in remaining_gap_assessment():
        assert gap["status"] == "OPEN"


def test_remaining_gaps_has_non_linear():
    names = [g["name"] for g in remaining_gap_assessment()]
    assert any("saddle" in n.lower() or "non-linear" in n.lower() or "nonlinear" in n.lower() for n in names)


def test_remaining_gaps_have_reason():
    for gap in remaining_gap_assessment():
        assert "reason" in gap
        assert len(gap["reason"]) > 5


# ─── subgap_e_proof_state ────────────────────────────────────────────────────

def test_subgap_e_proof_state_subgap():
    state = subgap_e_proof_state()
    assert state["subgap"] == "E"


def test_subgap_e_proof_state_bc():
    state = subgap_e_proof_state()
    assert state["bc"] == "NP-BC-2"


def test_subgap_e_proof_state_status():
    state = subgap_e_proof_state()
    assert state["status"] == "NP_BC2_SUBGAP_E_SADDLE_BOUND_KERNEL_PROVED"


def test_subgap_e_proof_state_kernel_proved():
    state = subgap_e_proof_state()
    assert state["kernel_proved"] is True


def test_subgap_e_proof_state_not_closed():
    state = subgap_e_proof_state()
    assert state["full_closure"] is False


def test_subgap_e_proof_state_theorems():
    state = subgap_e_proof_state()
    assert state["lean4_theorems"] == 11


def test_subgap_e_proof_state_np_pert_ratio():
    state = subgap_e_proof_state()
    assert state["np_pert_ratio"] == 14


# ─── advancement_certificate ─────────────────────────────────────────────────

def test_advancement_cert_pillar():
    cert = advancement_certificate()
    assert cert["pillar"] == 565


def test_advancement_cert_subgap():
    cert = advancement_certificate()
    assert cert["subgap"] == "E"


def test_advancement_cert_bc():
    cert = advancement_certificate()
    assert cert["bc"] == "NP-BC-2"


def test_advancement_cert_theorems_added():
    cert = advancement_certificate()
    assert cert["theorems_added"] == 11


def test_advancement_cert_total_theorems():
    cert = advancement_certificate()
    assert cert["total_lean4_theorems"] == 195


def test_advancement_cert_epistemic_delta_mentions_saddle():
    cert = advancement_certificate()
    assert "SADDLE_BOUND_KERNEL_PROVED" in cert["epistemic_delta"]


def test_advancement_cert_epistemic_delta_mentions_ratio():
    cert = advancement_certificate()
    assert "14" in cert["epistemic_delta"]


def test_advancement_cert_has_anti_claims():
    cert = advancement_certificate()
    assert "what_is_NOT_claimed" in cert
    assert len(cert["what_is_NOT_claimed"]) >= 2


def test_advancement_cert_erepr_not_proved():
    cert = advancement_certificate()
    not_claimed = " ".join(cert["what_is_NOT_claimed"])
    assert "ER=EPR" in not_claimed


# ─── pillar_report ────────────────────────────────────────────────────────────

def test_pillar_report_complete():
    report = pillar_report()
    for key in ["pillar", "title", "status", "version", "lean4",
                "theorem_count", "subgap_e_status", "proved", "remaining", "certificate"]:
        assert key in report


def test_pillar_report_pillar_number():
    report = pillar_report()
    assert report["pillar"] == 565


def test_pillar_report_version():
    report = pillar_report()
    assert report["version"] == "v19.4"


def test_pillar_report_lean4_theorems():
    report = pillar_report()
    assert report["lean4"]["theorems"] == 11


def test_pillar_report_theorem_count_total():
    report = pillar_report()
    assert report["theorem_count"]["total"] == 195


def test_pillar_report_proved_list():
    report = pillar_report()
    assert isinstance(report["proved"], list)
    assert len(report["proved"]) >= 8


def test_pillar_report_remaining_list():
    report = pillar_report()
    assert isinstance(report["remaining"], list)
