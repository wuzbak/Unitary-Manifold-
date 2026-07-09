# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 557 — Lean4 NP-BC-3 KK CS Path Integral Geometric Kernel."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar557_erepr_np_bc3_kk_cs import (
    GEOMETRIC_KERNEL_COMPONENTS,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    NP_BC3_STATUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REMAINING_SUB_GAPS,
    VERSION,
    advancement_certificate,
    erepr_axiom_status_summary,
    geometric_kernel_components,
    np_bc3_proof_state,
    pillar_report,
    sub_gap_decomposition,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 557


def test_pillar_status():
    assert PILLAR_STATUS == "LEAN4_NP_BC3_GEOMETRIC_KERNEL_PROVED"


def test_version():
    assert VERSION == "v19.2"


# ─── Lean4 new file ──────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    assert path.exists(), f"NPBC3Kernel.lean not found at {path}"


def test_lean4_new_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 14


def test_lean4_new_file_status():
    assert LEAN4_NEW_FILE["status"] == "GEOMETRIC_KERNEL_PROVED"


def test_lean4_file_content_has_kcs():
    content = LEAN4_NEW_FILE["content"]
    assert "k_CS" in content or "CS" in content


def test_lean4_file_content_has_vacuum():
    content = LEAN4_NEW_FILE["content"]
    assert "vacuum" in content.lower() or "zero action" in content.lower()


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorem_count():
    assert LEAN4_THEOREM_COUNT["total"] == 139


def test_new_theorems():
    assert LEAN4_THEOREM_COUNT["total_new"] == 14


def test_previous_total():
    assert LEAN4_THEOREM_COUNT["total_previous"] == 125


def test_npbc3_kernel_theorems():
    assert LEAN4_THEOREM_COUNT["NPBC3Kernel.lean"] == 14


def test_theorem_count_consistency():
    assert (LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_THEOREM_COUNT["total_new"]
            == LEAN4_THEOREM_COUNT["total"])


def test_npbc2_theorem_count_unchanged():
    """Pillar 556 count not modified."""
    assert LEAN4_THEOREM_COUNT["NPBC2Kernel.lean"] == 16


def test_npbc1_theorem_count_unchanged():
    """Pillar 549 count not modified."""
    assert LEAN4_THEOREM_COUNT["NPBC1Kernel.lean"] == 18


# ─── NP-BC-3 status ──────────────────────────────────────────────────────────

def test_np_bc3_status_axiom():
    assert NP_BC3_STATUS["axiom_statement"] == "erepr_np_bc_3 : Prop"


def test_np_bc3_kernel_proved():
    assert NP_BC3_STATUS["kernel_proved"] is True


def test_np_bc3_full_proof_not_achieved():
    assert NP_BC3_STATUS["full_proof_achieved"] is False


def test_np_bc3_axiom_source():
    assert "ERWormhole.lean" in NP_BC3_STATUS["axiom_source"]


def test_np_bc3_cs_physics():
    phys = NP_BC3_STATUS["physical_meaning"]
    assert "Chern-Simons" in phys or "CS" in phys


# ─── Geometric kernel components ─────────────────────────────────────────────

def test_kernel_components_count():
    """At least 10 components in the geometric kernel."""
    components = geometric_kernel_components()
    assert len(components) >= 10


def test_kernel_components_all_proved():
    """All geometric kernel components are PROVED."""
    for comp in geometric_kernel_components():
        assert comp["status"] == "PROVED", f"{comp['name']} not PROVED"


def test_kernel_contains_kcs_positive():
    names = [c["name"] for c in geometric_kernel_components()]
    assert any("positive" in n.lower() or "positiv" in n.lower() for n in names)


def test_kernel_contains_vacuum():
    names = [c["name"] for c in geometric_kernel_components()]
    assert any("vacuum" in n.lower() or "zero" in n.lower() for n in names)


def test_kernel_contains_factorization():
    names = [c["name"] for c in geometric_kernel_components()]
    assert any("factorize" in n.lower() or "factor" in n.lower() for n in names)


def test_kernel_contains_braid_pair():
    names = [c["name"] for c in geometric_kernel_components()]
    assert any("braid" in n.lower() or "5²" in n or "7²" in n for n in names)


# ─── Remaining sub-gaps ──────────────────────────────────────────────────────

def test_sub_gaps_count():
    """Exactly 3 sub-gaps for NP-BC-3."""
    assert len(sub_gap_decomposition()) == 3


def test_sub_gaps_all_blocking():
    for gap in sub_gap_decomposition():
        assert gap["blocking"] is True


def test_sub_gap_names_unique():
    names = [g["name"] for g in sub_gap_decomposition()]
    assert len(names) == len(set(names))


def test_sub_gap_G_present():
    names = [g["name"] for g in sub_gap_decomposition()]
    assert any("G" in n for n in names)


def test_sub_gap_H_present():
    names = [g["name"] for g in sub_gap_decomposition()]
    assert any("H" in n for n in names)


def test_sub_gap_I_present():
    names = [g["name"] for g in sub_gap_decomposition()]
    assert any("I" in n for n in names)


# ─── np_bc3_proof_state ──────────────────────────────────────────────────────

def test_proof_state_axiom():
    ps = np_bc3_proof_state()
    assert ps["axiom"] == "erepr_np_bc_3"


def test_proof_state_status():
    ps = np_bc3_proof_state()
    assert ps["status"] == "GEOMETRIC_KERNEL_PROVED"


def test_proof_state_kernel_theorems():
    ps = np_bc3_proof_state()
    assert ps["kernel_theorems"] == 14


def test_proof_state_not_full():
    ps = np_bc3_proof_state()
    assert ps["full_proof_achieved"] is False


def test_proof_state_remaining_sub_gaps():
    ps = np_bc3_proof_state()
    assert ps["remaining_sub_gaps"] == 3


# ─── ER=EPR axiom status summary ─────────────────────────────────────────────

def test_erepr_summary_all_three_attempted():
    s = erepr_axiom_status_summary()
    assert s["erepr_overall"]["all_three_attempted"] is True


def test_erepr_summary_not_fully_proved():
    s = erepr_axiom_status_summary()
    assert s["erepr_overall"]["full_proof_achieved"] is False


def test_erepr_summary_9_sub_gaps():
    s = erepr_axiom_status_summary()
    assert s["erepr_overall"]["total_named_sub_gaps"] == 9


def test_erepr_np_bc1_status():
    s = erepr_axiom_status_summary()
    assert s["NP-BC-1"]["pillar"] == 549
    assert s["NP-BC-1"]["theorems"] == 18


def test_erepr_np_bc2_status():
    s = erepr_axiom_status_summary()
    assert s["NP-BC-2"]["pillar"] == 556
    assert s["NP-BC-2"]["theorems"] == 16


def test_erepr_np_bc3_status():
    s = erepr_axiom_status_summary()
    assert s["NP-BC-3"]["pillar"] == 557
    assert s["NP-BC-3"]["theorems"] == 14


def test_erepr_total_theorems_across_np_bcs():
    s = erepr_axiom_status_summary()
    assert s["erepr_overall"]["total_theorems_across_np_bcs"] == 18 + 16 + 14  # 48


# ─── Advancement certificate ─────────────────────────────────────────────────

def test_certificate_pillar():
    cert = advancement_certificate()
    assert cert["pillar"] == 557


def test_certificate_theorems_added():
    cert = advancement_certificate()
    assert cert["theorems_added"] == 14


def test_certificate_total_theorems():
    cert = advancement_certificate()
    assert cert["total_lean4_theorems"] == 139


def test_certificate_toe_delta():
    cert = advancement_certificate()
    assert cert["toe_score_delta"] == 0.0


def test_certificate_not_closed():
    cert = advancement_certificate()
    not_claimed = cert["what_is_NOT_claimed"]
    assert any("NOT closed" in s or "not closed" in s.lower() for s in not_claimed)


def test_certificate_erepr_not_proved():
    cert = advancement_certificate()
    not_claimed = cert["what_is_NOT_claimed"]
    assert any("ER=EPR" in s for s in not_claimed)


# ─── Pillar report ───────────────────────────────────────────────────────────

def test_pillar_report_keys():
    r = pillar_report()
    assert r["pillar"] == 557
    assert r["status"] == "LEAN4_NP_BC3_GEOMETRIC_KERNEL_PROVED"
    assert r["toe_score_delta"] == 0.0
    assert r["hardgate_score_delta"] == 0.0
    assert r["parent_pillar"] == 556


def test_pillar_report_no_adjacent_track():
    r = pillar_report()
    assert r["adjacent_track"] is False


def test_pillar_report_all_kernels_proved():
    r = pillar_report()
    assert r["erepr_np_bc_closure_status"] == "ALL_THREE_KERNELS_PROVED"
