# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 545 — Lean4 CCR/ER=EPR Proof Advancement."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar545_lean4_proof_advancement import (
    CCR_STATUS,
    EREPR_STATUS,
    LEAN4_FILES,
    NO_CLAIM_RECORD,
    NP_BOUNDARY_CONDITIONS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    advancement_certificate,
    ccr_proof_state,
    erepr_proof_state,
    lean4_file_inventory,
    np_bc_decomposition,
    pillar_report,
)

REPO_ROOT = Path(__file__).parent.parent


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 545


def test_pillar_status():
    assert "LEAN4_PROOF_ADVANCEMENT" in PILLAR_STATUS


def test_version():
    assert VERSION == "v19.0"


# ─── Lean4 file inventory ─────────────────────────────────────────────────────

def test_lean4_file_count():
    assert len(LEAN4_FILES) == 8


def test_erwormhole_lean_is_new():
    assert "lean4/UnitaryManifold/ERWormhole.lean" in LEAN4_FILES
    f = LEAN4_FILES["lean4/UnitaryManifold/ERWormhole.lean"]
    assert f["status"] == "VERIFIED_NEW"


def test_erwormhole_lean_file_exists():
    lean_path = REPO_ROOT / "lean4/UnitaryManifold/ERWormhole.lean"
    assert lean_path.exists(), "ERWormhole.lean should exist on disk"


def test_ccrkernel_lean_still_present():
    assert "lean4/UnitaryManifold/CCRKernel.lean" in LEAN4_FILES


def test_lean4_inventory_total_theorems():
    inv = lean4_file_inventory()
    assert inv["total_theorems"] >= 90  # all prior + 13 new


def test_lean4_inventory_new_theorems():
    inv = lean4_file_inventory()
    assert inv["new_theorems_this_sprint"] == 13


# ─── CCR proof state ─────────────────────────────────────────────────────────

def test_ccr_still_conditional():
    assert CCR_STATUS["current_status"] == "CONDITIONAL_THEOREM_KERNEL"


def test_ccr_single_open_condition():
    assert len(CCR_STATUS["open_conditions"]) == 1
    assert "p8" in CCR_STATUS["open_conditions"][0].lower()


def test_ccr_kernel_theorems_count():
    assert len(CCR_STATUS["kernel_theorems_proved"]) >= 5


# ─── ER=EPR proof state ──────────────────────────────────────────────────────

def test_erepr_still_conditional():
    assert EREPR_STATUS["current_status"] == "CONDITIONAL_THEOREM_KERNEL"


def test_erepr_three_open_conditions_after():
    assert len(EREPR_STATUS["open_conditions_after"]) == 3


def test_erepr_one_open_condition_before():
    assert len(EREPR_STATUS["open_conditions_before"]) == 1


def test_erepr_pillar_6_connection():
    assert "Pillar 6" in EREPR_STATUS["pillar_6_connection"]
    assert "DERIVED_CONDITIONAL" in EREPR_STATUS["pillar_6_connection"]


# ─── NP boundary conditions ──────────────────────────────────────────────────

def test_three_np_bcs():
    assert len(NP_BOUNDARY_CONDITIONS) == 3


def test_np_bc_ids():
    ids = [bc["id"] for bc in NP_BOUNDARY_CONDITIONS]
    assert "NP-BC-1" in ids
    assert "NP-BC-2" in ids
    assert "NP-BC-3" in ids


def test_np_bc_all_block_pillar_6():
    for bc in NP_BOUNDARY_CONDITIONS:
        assert bc["blocks_pillar_6"] is True


def test_np_bc_lean4_axiom_names():
    axioms = [bc["lean4_axiom"] for bc in NP_BOUNDARY_CONDITIONS]
    assert "erepr_np_bc_1" in axioms
    assert "erepr_np_bc_2" in axioms
    assert "erepr_np_bc_3" in axioms


# ─── No-claim record ─────────────────────────────────────────────────────────

def test_no_unconditional_ccr():
    assert NO_CLAIM_RECORD["unconditional_ccr_proved"] is False


def test_no_unconditional_erepr():
    assert NO_CLAIM_RECORD["unconditional_erepr_proved"] is False


def test_no_lean4_build_receipt():
    assert NO_CLAIM_RECORD["lean4_build_receipt"] is False


def test_no_hardgate_change():
    assert NO_CLAIM_RECORD["hardgate_score_changed"] is False


# ─── Functions ───────────────────────────────────────────────────────────────

def test_np_bc_decomposition():
    decomp = np_bc_decomposition()
    assert decomp["before"].startswith("1 unnamed")
    assert "3 named" in decomp["after"]
    assert decomp["decomposition_is_exact"] is True


def test_advancement_certificate():
    cert = advancement_certificate()
    assert cert["new_lean4_file"] == "lean4/UnitaryManifold/ERWormhole.lean"
    assert cert["theorems_added"] == 13
    assert cert["hardgate_score_delta"] == 0.0


def test_pillar_report_complete():
    report = pillar_report()
    assert report["pillar"] == 545
    assert report["adjacent_track"] is False
    assert "ERWormhole" in report["epistemic_delta"]
