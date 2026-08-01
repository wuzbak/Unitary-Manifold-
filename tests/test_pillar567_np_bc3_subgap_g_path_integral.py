# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 567 — NP-BC-3 Sub-gap G: Path Integral Topology Kernel."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar567_np_bc3_subgap_g_path_integral import (
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    REMAINING_GAPS,
    SUBGAP_G_STATUS,
    VERSION,
    WINDING_BOUND,
    advancement_certificate,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    subgap_g_proof_state,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 567


def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC3_SUBGAP_G_PATH_INTEGRAL_TOPOLOGY_KERNEL_PROVED"


def test_pillar_title_contains_subgap_g():
    assert "G" in PILLAR_TITLE or "Path" in PILLAR_TITLE


def test_version():
    assert VERSION == "v19.4"


def test_winding_bound():
    assert WINDING_BOUND == 370  # 5 × 74


def test_winding_bound_arithmetic():
    assert WINDING_BOUND == 5 * 74


# ─── Lean4 file ───────────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    assert path.exists(), f"NPBC3SubgapG.lean not found at {path}"


def test_lean4_file_path_correct():
    assert "NPBC3SubgapG" in LEAN4_NEW_FILE["path"]


def test_lean4_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 11


def test_lean4_file_status():
    assert LEAN4_NEW_FILE["status"] == "PATH_INTEGRAL_TOPOLOGY_KERNEL_PROVED"


def test_lean4_file_content_vacuum():
    content = LEAN4_NEW_FILE["content"]
    assert "vacuum" in content.lower() or "S(0)" in content


def test_lean4_file_content_kcs():
    content = LEAN4_NEW_FILE["content"]
    assert "74" in content or "k_CS" in content.lower()


def test_lean4_file_content_winding_bound():
    content = LEAN4_NEW_FILE["content"]
    assert "370" in content or "winding" in content.lower()


def test_lean4_file_honest_status_partially_closed():
    assert "PARTIALLY_CLOSED" in LEAN4_NEW_FILE["honest_status"]


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorem_count():
    assert LEAN4_THEOREM_COUNT["total"] == 217


def test_new_theorems():
    assert LEAN4_THEOREM_COUNT["total_new"] == 11


def test_previous_total():
    assert LEAN4_THEOREM_COUNT["total_previous"] == 206


def test_subgap_g_entry():
    assert LEAN4_THEOREM_COUNT["NPBC3SubgapG.lean"] == 11


def test_subgap_d_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC2SubgapD.lean"] == 11


def test_subgap_e_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC2SubgapE.lean"] == 11


def test_subgap_f_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC2SubgapF.lean"] == 11


def test_theorem_count_arithmetic():
    assert LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_THEOREM_COUNT["total_new"] == LEAN4_THEOREM_COUNT["total"]


# ─── Sub-gap G status ─────────────────────────────────────────────────────────

def test_subgap_g_kernel_proved():
    assert SUBGAP_G_STATUS["kernel_proved"] is True


def test_subgap_g_full_closure_not_achieved():
    assert SUBGAP_G_STATUS["full_closure_achieved"] is False


def test_subgap_g_winding_bound_370():
    assert SUBGAP_G_STATUS["winding_bound_370"] == 370


def test_subgap_g_source_references_pillar_557():
    assert "557" in SUBGAP_G_STATUS["source"]


def test_subgap_g_advance_over_557():
    assert len(SUBGAP_G_STATUS["advance_over_pillar_557"]) > 20


# ─── Proved components ───────────────────────────────────────────────────────

def test_proved_components_count():
    components = proved_components()
    assert len(components) >= 9


def test_proved_components_all_proved():
    for c in proved_components():
        assert c["status"] == "PROVED"


def test_proved_components_has_vacuum():
    names = [c["name"] for c in proved_components()]
    assert any("vacuum" in n.lower() for n in names)


def test_proved_components_has_action_factorization():
    names = [c["name"] for c in proved_components()]
    assert any("factori" in n.lower() or "factor" in n.lower() for n in names)


def test_proved_components_has_monotone():
    names = [c["name"] for c in proved_components()]
    assert any("monotone" in n.lower() or "ordering" in n.lower() for n in names)


def test_proved_components_has_winding_bound():
    names = [c["name"] for c in proved_components()]
    assert any("bound" in n.lower() or "370" in n for n in names)


def test_proved_components_has_summary():
    names = [c["name"] for c in proved_components()]
    assert any("summary" in n.lower() or "kernel" in n.lower() for n in names)


def test_proved_components_kcs_recovery():
    names = [c["name"] for c in proved_components()]
    assert any("recovery" in n.lower() or "cs level" in n.lower() for n in names)


def test_proved_components_vacuum_zero():
    contents = [c["content"] for c in proved_components()]
    assert any("S(0) = 0" in c or "zero action" in c.lower() for c in contents)


# ─── Remaining gaps ───────────────────────────────────────────────────────────

def test_remaining_gaps_not_empty():
    gaps = remaining_gap_assessment()
    assert len(gaps) >= 1


def test_remaining_gaps_all_open():
    for gap in remaining_gap_assessment():
        assert gap["status"] == "OPEN"


def test_remaining_gaps_has_operator_insertions():
    names = [g["name"] for g in remaining_gap_assessment()]
    assert any("operator" in n.lower() or "insertion" in n.lower() or "path integral" in n.lower() for n in names)


def test_remaining_gaps_have_reason():
    for gap in remaining_gap_assessment():
        assert "reason" in gap


# ─── subgap_g_proof_state ────────────────────────────────────────────────────

def test_subgap_g_proof_state_subgap():
    state = subgap_g_proof_state()
    assert state["subgap"] == "G"


def test_subgap_g_proof_state_bc():
    state = subgap_g_proof_state()
    assert state["bc"] == "NP-BC-3"


def test_subgap_g_proof_state_status():
    state = subgap_g_proof_state()
    assert state["status"] == "NP_BC3_SUBGAP_G_PATH_INTEGRAL_TOPOLOGY_KERNEL_PROVED"


def test_subgap_g_proof_state_kernel_proved():
    state = subgap_g_proof_state()
    assert state["kernel_proved"] is True


def test_subgap_g_proof_state_not_closed():
    state = subgap_g_proof_state()
    assert state["full_closure"] is False


def test_subgap_g_proof_state_theorems():
    state = subgap_g_proof_state()
    assert state["lean4_theorems"] == 11


def test_subgap_g_proof_state_winding_bound():
    state = subgap_g_proof_state()
    assert state["winding_bound"] == 370


# ─── advancement_certificate ─────────────────────────────────────────────────

def test_advancement_cert_pillar():
    cert = advancement_certificate()
    assert cert["pillar"] == 567


def test_advancement_cert_subgap():
    cert = advancement_certificate()
    assert cert["subgap"] == "G"


def test_advancement_cert_bc():
    cert = advancement_certificate()
    assert cert["bc"] == "NP-BC-3"


def test_advancement_cert_theorems_added():
    cert = advancement_certificate()
    assert cert["theorems_added"] == 11


def test_advancement_cert_total_theorems():
    cert = advancement_certificate()
    assert cert["total_lean4_theorems"] == 217


def test_advancement_cert_epistemic_delta_mentions_g():
    cert = advancement_certificate()
    assert "PATH_INTEGRAL_TOPOLOGY_KERNEL_PROVED" in cert["epistemic_delta"]


def test_advancement_cert_epistemic_delta_mentions_370():
    cert = advancement_certificate()
    assert "370" in cert["epistemic_delta"]


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
                "theorem_count", "subgap_g_status", "proved", "remaining", "certificate"]:
        assert key in report


def test_pillar_report_pillar_number():
    report = pillar_report()
    assert report["pillar"] == 567


def test_pillar_report_version():
    report = pillar_report()
    assert report["version"] == "v19.4"


def test_pillar_report_lean4_theorems():
    report = pillar_report()
    assert report["lean4"]["theorems"] == 11


def test_pillar_report_theorem_count_total():
    report = pillar_report()
    assert report["theorem_count"]["total"] == 217


def test_pillar_report_proved_list():
    report = pillar_report()
    assert isinstance(report["proved"], list)
    assert len(report["proved"]) >= 9


def test_pillar_report_remaining_list():
    report = pillar_report()
    assert isinstance(report["remaining"], list)
