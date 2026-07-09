# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 556 — Lean4 NP-BC-2 IR-Brane Mixing Geometric Kernel."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar556_erepr_np_bc2_ir_brane import (
    GEOMETRIC_KERNEL_COMPONENTS,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    NP_BC2_STATUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    REMAINING_SUB_GAPS,
    VERSION,
    advancement_certificate,
    geometric_kernel_components,
    np_bc2_proof_state,
    pillar_report,
    sub_gap_decomposition,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 556


def test_pillar_status():
    assert PILLAR_STATUS == "LEAN4_NP_BC2_GEOMETRIC_KERNEL_PROVED"


def test_version():
    assert VERSION == "v19.2"


# ─── Lean4 new file ──────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    assert path.exists(), f"NPBC2Kernel.lean not found at {path}"


def test_lean4_new_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 16


def test_lean4_new_file_status():
    assert LEAN4_NEW_FILE["status"] == "GEOMETRIC_KERNEL_PROVED"


def test_lean4_file_content_robin():
    assert "Robin" in LEAN4_NEW_FILE["content"]


def test_lean4_file_content_uv_ir():
    content = LEAN4_NEW_FILE["content"]
    assert "UV" in content or "IR" in content


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorem_count():
    assert LEAN4_THEOREM_COUNT["total"] == 125


def test_new_theorems():
    assert LEAN4_THEOREM_COUNT["total_new"] == 16


def test_previous_total():
    assert LEAN4_THEOREM_COUNT["total_previous"] == 109


def test_npbc2_kernel_theorems():
    assert LEAN4_THEOREM_COUNT["NPBC2Kernel.lean"] == 16


def test_theorem_count_consistency():
    assert (LEAN4_THEOREM_COUNT["total_previous"] + LEAN4_THEOREM_COUNT["total_new"]
            == LEAN4_THEOREM_COUNT["total"])


# ─── NP-BC-2 status ──────────────────────────────────────────────────────────

def test_np_bc2_status_axiom():
    assert NP_BC2_STATUS["axiom_statement"] == "erepr_np_bc_2 : Prop"


def test_np_bc2_kernel_proved():
    assert NP_BC2_STATUS["kernel_proved"] is True


def test_np_bc2_full_proof_not_achieved():
    assert NP_BC2_STATUS["full_proof_achieved"] is False


def test_np_bc2_axiom_source():
    assert "ERWormhole.lean" in NP_BC2_STATUS["axiom_source"]


# ─── Geometric kernel components ─────────────────────────────────────────────

def test_kernel_components_count():
    """At least 5 components in the geometric kernel."""
    components = geometric_kernel_components()
    assert len(components) >= 5


def test_kernel_components_all_proved():
    """All geometric kernel components are PROVED."""
    for comp in geometric_kernel_components():
        assert comp["status"] == "PROVED", f"{comp['name']} not PROVED"


def test_kernel_contains_robin():
    names = [c["name"] for c in geometric_kernel_components()]
    assert any("Robin" in n for n in names)


def test_kernel_contains_mixing():
    names = [c["name"] for c in geometric_kernel_components()]
    assert any("Mixing" in n or "mixing" in n for n in names)


def test_kernel_contains_summary():
    """A joint summary theorem is present."""
    names = [c["name"] for c in geometric_kernel_components()]
    assert any("kernel" in n.lower() or "summary" in n.lower() for n in names)


# ─── Remaining sub-gaps ──────────────────────────────────────────────────────

def test_sub_gaps_count():
    """Exactly 3 sub-gaps for NP-BC-2."""
    assert len(sub_gap_decomposition()) == 3


def test_sub_gaps_all_blocking():
    for gap in sub_gap_decomposition():
        assert gap["blocking"] is True


def test_sub_gap_names_unique():
    names = [g["name"] for g in sub_gap_decomposition()]
    assert len(names) == len(set(names))


def test_sub_gap_D_present():
    names = [g["name"] for g in sub_gap_decomposition()]
    assert any("D" in n for n in names)


def test_sub_gap_E_present():
    names = [g["name"] for g in sub_gap_decomposition()]
    assert any("E" in n for n in names)


def test_sub_gap_F_present():
    names = [g["name"] for g in sub_gap_decomposition()]
    assert any("F" in n for n in names)


# ─── np_bc2_proof_state ──────────────────────────────────────────────────────

def test_proof_state_axiom():
    ps = np_bc2_proof_state()
    assert ps["axiom"] == "erepr_np_bc_2"


def test_proof_state_status():
    ps = np_bc2_proof_state()
    assert ps["status"] == "GEOMETRIC_KERNEL_PROVED"


def test_proof_state_kernel_theorems():
    ps = np_bc2_proof_state()
    assert ps["kernel_theorems"] == 16


def test_proof_state_not_full():
    ps = np_bc2_proof_state()
    assert ps["full_proof_achieved"] is False


# ─── Advancement certificate ─────────────────────────────────────────────────

def test_certificate_pillar():
    cert = advancement_certificate()
    assert cert["pillar"] == 556


def test_certificate_theorems_added():
    cert = advancement_certificate()
    assert cert["theorems_added"] == 16


def test_certificate_total_theorems():
    cert = advancement_certificate()
    assert cert["total_lean4_theorems"] == 125


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
    assert r["pillar"] == 556
    assert r["status"] == "LEAN4_NP_BC2_GEOMETRIC_KERNEL_PROVED"
    assert r["toe_score_delta"] == 0.0
    assert r["hardgate_score_delta"] == 0.0
    assert r["parent_pillar"] == 549


def test_pillar_report_no_adjacent_track():
    r = pillar_report()
    assert r["adjacent_track"] is False
