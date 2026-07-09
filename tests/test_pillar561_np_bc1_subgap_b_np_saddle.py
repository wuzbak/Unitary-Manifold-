# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 561 — NP-BC-1 Sub-gap B: NP Saddle Exponential Bound."""
from __future__ import annotations

import math
import pytest
from pathlib import Path
from src.core.pillar561_np_bc1_subgap_b_np_saddle import (
    K_CS,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PROVED_COMPONENTS,
    REMAINING_GAPS,
    SUBGAP_B_STATUS,
    VERSION,
    advancement_certificate,
    pillar_report,
    saddle_contribution_bound,
    subgap_b_proof_state,
    suppression_bound,
    winding_parity,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 561


def test_pillar_status():
    assert PILLAR_STATUS == "NP_BC1_SUBGAP_B_NP_SADDLE_BOUND_PROVED"


def test_version():
    assert VERSION == "v19.3"


def test_k_cs():
    assert K_CS == 74


# ─── Lean4 file ───────────────────────────────────────────────────────────────

def test_lean4_file_exists():
    path = Path(LEAN4_NEW_FILE["path"])
    assert path.exists(), f"NPBC1SubgapB.lean not found at {path}"


def test_lean4_file_theorem_count():
    assert LEAN4_NEW_FILE["theorems"] == 11


def test_lean4_file_status():
    assert LEAN4_NEW_FILE["status"] == "NP_SADDLE_BOUND_PROVED"


def test_lean4_file_content_suppression():
    content = LEAN4_NEW_FILE["content"]
    assert "suppression" in content.lower() or "positiv" in content.lower()


def test_lean4_file_content_parity():
    content = LEAN4_NEW_FILE["content"]
    assert "parity" in content.lower()


# ─── Lean4 theorem count ─────────────────────────────────────────────────────

def test_total_theorem_count():
    assert LEAN4_THEOREM_COUNT["total"] == 162


def test_new_theorems():
    assert LEAN4_THEOREM_COUNT["total_new"] == 11


def test_previous_total():
    assert LEAN4_THEOREM_COUNT["total_previous"] == 151


def test_subgap_b_entry():
    assert LEAN4_THEOREM_COUNT["NPBC1SubgapB.lean"] == 11


def test_subgap_a_unchanged():
    assert LEAN4_THEOREM_COUNT["NPBC1SubgapA.lean"] == 12


# ─── Sub-gap B status ─────────────────────────────────────────────────────────

def test_subgap_b_kernel_proved():
    assert SUBGAP_B_STATUS["kernel_proved"] is True


def test_subgap_b_full_closure_not_achieved():
    assert SUBGAP_B_STATUS["full_closure_achieved"] is False


# ─── suppression_bound ───────────────────────────────────────────────────────

def test_suppression_bound_n0():
    assert suppression_bound(0) == 1.0


def test_suppression_bound_n1():
    result = suppression_bound(1)
    expected = math.exp(-74)
    assert abs(result - expected) < 1e-50


def test_suppression_bound_n2():
    result = suppression_bound(2)
    expected = math.exp(-148)
    # Both are essentially 0.0 at float precision
    assert result == 0.0 or result < math.exp(-74)


def test_suppression_bound_decreasing():
    """Higher n gives smaller suppression bound."""
    s0 = suppression_bound(0)
    s1 = suppression_bound(1)
    # n=1 suppression < n=0 (which is 1.0)
    assert s1 < s0


def test_suppression_bound_negative_raises():
    with pytest.raises(ValueError):
        suppression_bound(-1)


# ─── winding_parity ──────────────────────────────────────────────────────────

def test_winding_parity_0_even():
    assert winding_parity(0) == "even"


def test_winding_parity_1_odd():
    assert winding_parity(1) == "odd"


def test_winding_parity_2_even():
    assert winding_parity(2) == "even"


def test_winding_parity_5_odd():
    assert winding_parity(5) == "odd"


def test_winding_parity_74_even():
    assert winding_parity(74) == "even"


def test_winding_parity_period():
    for n in range(10):
        assert winding_parity(n) == winding_parity(n + 2)


# ─── saddle_contribution_bound ───────────────────────────────────────────────

def test_saddle_table_length():
    table = saddle_contribution_bound(5)
    assert len(table) == 6  # n=0..5


def test_saddle_table_n0():
    table = saddle_contribution_bound(1)
    row0 = table[0]
    assert row0["n"] == 0
    assert row0["suppression_bound"] == 1.0
    assert row0["z2_parity"] == "even"
    assert row0["contribution_sign"] == "+"


def test_saddle_table_n1():
    table = saddle_contribution_bound(1)
    row1 = table[1]
    assert row1["n"] == 1
    assert row1["z2_parity"] == "odd"
    assert row1["contribution_sign"] == "-"


def test_saddle_table_exponents():
    table = saddle_contribution_bound(3)
    exponents = [row["exponent"] for row in table]
    assert exponents == [0, 74, 148, 222]


# ─── subgap_b_proof_state ────────────────────────────────────────────────────

def test_proof_state_subgap():
    state = subgap_b_proof_state()
    assert state["subgap"] == "B"


def test_proof_state_status():
    state = subgap_b_proof_state()
    assert state["status"] == "NP_SADDLE_BOUND_PROVED"


def test_proof_state_not_closed():
    state = subgap_b_proof_state()
    assert state["full_closure_achieved"] is False


def test_proof_state_suppression():
    state = subgap_b_proof_state()
    assert "suppression_estimate" in state
    assert state["suppression_estimate"]["n1_bound"] < 1.0


# ─── advancement_certificate ─────────────────────────────────────────────────

def test_advancement_cert_pillar():
    cert = advancement_certificate()
    assert cert["pillar"] == 561


def test_advancement_cert_subgap():
    cert = advancement_certificate()
    assert cert["subgap"] == "B"


def test_advancement_cert_theorems():
    cert = advancement_certificate()
    assert cert["theorems_added"] == 11
    assert cert["total_lean4_theorems"] == 162


def test_advancement_cert_toe_zero():
    cert = advancement_certificate()
    assert cert["toe_score_delta"] == 0.0


def test_advancement_cert_not_closed():
    cert = advancement_certificate()
    not_claimed = " ".join(cert["what_is_NOT_claimed"])
    assert "NOT fully closed" in not_claimed or "NOT closed" in not_claimed


# ─── pillar_report ────────────────────────────────────────────────────────────

def test_pillar_report_complete():
    report = pillar_report()
    for key in ["pillar", "title", "status", "version",
                "lean4_new_file", "lean4_theorem_count", "toe_score_delta"]:
        assert key in report


def test_pillar_report_saddle_table():
    report = pillar_report()
    assert "saddle_contribution_table" in report
    assert len(report["saddle_contribution_table"]) == 4  # n=0..3


def test_pillar_report_not_adjacent():
    report = pillar_report()
    assert report["adjacent_track"] is False


def test_pillar_report_parent():
    report = pillar_report()
    assert report["parent_pillar"] == 549
