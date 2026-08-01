# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 564 — NP-BC-2 Sub-gap D: Mixing Angle Algebraic Kernel."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar564_np_bc2_subgap_d_mixing_angle import (
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    REMAINING_GAPS,
    SUBGAP_D_STATUS,
    VERSION,
    advancement_certificate,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_d_proof_state,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 564


def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC2_SUBGAP_D_MIXING_ANGLE_KERNEL_PROVED"


def test_pillar_title_contains_subgap_d():
    assert "D" in PILLAR_TITLE or "Mixing" in PILLAR_TITLE


def test_version():
    assert VERSION == "v19.4"


# ─── Lean4 file ───────────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    assert path.exists(), f"NPBC2SubgapD.lean not found at {path}"


def test_lean4_file_path_correct():
    assert "NPBC2SubgapD" in LEAN4_NEW_FILE["path"]


def test_lean4_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 11


def test_lean4_file_status():
    assert LEAN4_NEW_FILE["status"] == "MIXING_ANGLE_KERNEL_PROVED"


def test_lean4_file_content_nw():
    content = LEAN4_NEW_FILE["content"]
    assert "n_w" in content or "5" in content


def test_lean4_file_content_kcs():
    content = LEAN4_NEW_FILE["content"]
    assert "74" in content or "k_CS" in content.lower()


def test_lean4_file_honest_status_partially_closed():
    assert "PARTIALLY_CLOSED" in LEAN4_NEW_FILE["honest_status"]


def test_lean4_file_honest_status_not_full_np():
    assert "saddle" in LEAN4_NEW_FILE["honest_status"].lower() or "non-perturbative" in LEAN4_NEW_FILE["honest_status"].lower()


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorem_count():
    assert LEAN4_THEOREM_COUNT["total"] == 184


def test_new_theorems():
    assert LEAN4_THEOREM_COUNT["total_new"] == 11


def test_previous_total():
    assert LEAN4_THEOREM_COUNT["total_previous"] == 173


def test_subgap_d_entry():
    assert LEAN4_THEOREM_COUNT["NPBC2SubgapD.lean"] == 11


def test_theorem_count_arithmetic():
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_THEOREM_COUNT["total_new"] == LEAN4_THEOREM_COUNT["total"]


# ─── Sub-gap D status ─────────────────────────────────────────────────────────

def test_subgap_d_kernel_proved():
    assert SUBGAP_D_STATUS["kernel_proved"] is True


def test_subgap_d_full_closure_not_achieved():
    assert SUBGAP_D_STATUS["full_closure_achieved"] is False


def test_subgap_d_mixing_is_fraction():
    stmt = SUBGAP_D_STATUS["physical_statement"]
    assert "5/74" in stmt or "n_w/k_CS" in stmt


def test_subgap_d_source_references_pillar_556():
    assert "556" in SUBGAP_D_STATUS["source"]


def test_subgap_d_advance_over_556_present():
    assert len(SUBGAP_D_STATUS["advance_over_pillar_556"]) > 20


# ─── Proved components ───────────────────────────────────────────────────────

def test_proved_components_count():
    components = proved_components()
    assert len(components) >= 9


def test_proved_components_all_proved():
    for c in proved_components():
        assert c["status"] == "PROVED"


def test_proved_components_has_nw_numerator():
    names = [c["name"] for c in proved_components()]
    assert any("numerator" in n.lower() or "n_w" in n.lower() for n in names)


def test_proved_components_has_kcs_denominator():
    names = [c["name"] for c in proved_components()]
    assert any("denominator" in n.lower() or "k_cs" in n.lower() or "k_CS" in n for n in names)


def test_proved_components_has_small_angle_bound():
    names = [c["name"] for c in proved_components()]
    assert any("angle" in n.lower() or "bound" in n.lower() for n in names)


def test_proved_components_has_mod_residue():
    names = [c["name"] for c in proved_components()]
    assert any("mod" in n.lower() or "residue" in n.lower() for n in names)


def test_proved_components_has_summary():
    names = [c["name"] for c in proved_components()]
    assert any("summary" in n.lower() or "kernel" in n.lower() for n in names)


def test_proved_components_mixing_product_345():
    contents = [c["content"] for c in proved_components()]
    assert any("345" in c for c in contents)


def test_proved_components_winding_mixing_84():
    contents = [c["content"] for c in proved_components()]
    assert any("84" in c for c in contents)


# ─── Remaining gaps ───────────────────────────────────────────────────────────

def test_remaining_gaps_not_empty():
    gaps = remaining_gap_assessment()
    assert len(gaps) >= 1


def test_remaining_gaps_all_open():
    for gap in remaining_gap_assessment():
        assert gap["status"] == "OPEN"


def test_remaining_gaps_has_saddle():
    names = [g["name"] for g in remaining_gap_assessment()]
    assert any("saddle" in n.lower() or "non-perturbative" in n.lower() for n in names)


def test_remaining_gaps_have_reason():
    for gap in remaining_gap_assessment():
        assert "reason" in gap
        assert len(gap["reason"]) > 5


# ─── subgap_d_proof_state ────────────────────────────────────────────────────

def test_subgap_d_proof_state_subgap():
    state = subgap_d_proof_state()
    assert state["subgap"] == "D"


def test_subgap_d_proof_state_bc():
    state = subgap_d_proof_state()
    assert state["bc"] == "NP-BC-2"


def test_subgap_d_proof_state_status():
    state = subgap_d_proof_state()
    assert state["status"] == "NP_BC2_SUBGAP_D_MIXING_ANGLE_KERNEL_PROVED"


def test_subgap_d_proof_state_kernel_proved():
    state = subgap_d_proof_state()
    assert state["kernel_proved"] is True


def test_subgap_d_proof_state_not_closed():
    state = subgap_d_proof_state()
    assert state["full_closure"] is False


def test_subgap_d_proof_state_theorems():
    state = subgap_d_proof_state()
    assert state["lean4_theorems"] == 11


# ─── advancement_certificate ─────────────────────────────────────────────────

def test_advancement_cert_pillar():
    cert = advancement_certificate()
    assert cert["pillar"] == 564


def test_advancement_cert_subgap():
    cert = advancement_certificate()
    assert cert["subgap"] == "D"


def test_advancement_cert_bc():
    cert = advancement_certificate()
    assert cert["bc"] == "NP-BC-2"


def test_advancement_cert_theorems_added():
    cert = advancement_certificate()
    assert cert["theorems_added"] == 11


def test_advancement_cert_total_theorems():
    cert = advancement_certificate()
    assert cert["total_lean4_theorems"] == 184


def test_advancement_cert_has_epistemic_delta():
    cert = advancement_certificate()
    assert "epistemic_delta" in cert
    assert "MIXING_ANGLE_KERNEL_PROVED" in cert["epistemic_delta"]


def test_advancement_cert_has_anti_claims():
    cert = advancement_certificate()
    assert "what_is_NOT_claimed" in cert
    assert len(cert["what_is_NOT_claimed"]) >= 2


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
                "theorem_count", "subgap_d_status", "proved", "remaining", "certificate"]:
        assert key in report


def test_pillar_report_pillar_number():
    report = pillar_report()
    assert report["pillar"] == 564


def test_pillar_report_version():
    report = pillar_report()
    assert report["version"] == "v19.4"


def test_pillar_report_lean4_matches_module():
    report = pillar_report()
    assert report["lean4"]["theorems"] == 11


def test_pillar_report_theorem_count_total():
    report = pillar_report()
    assert report["theorem_count"]["total"] == 184


def test_pillar_report_proved_list():
    report = pillar_report()
    assert isinstance(report["proved"], list)
    assert len(report["proved"]) >= 9


def test_pillar_report_remaining_list():
    report = pillar_report()
    assert isinstance(report["remaining"], list)
