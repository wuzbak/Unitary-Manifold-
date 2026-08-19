# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar770_su5_orbifold_closure.py
============================================
Test suite for Pillar 770 — SU(5) from KK Orbifold Honest Closure.

~45 tests covering:
  - KK zero-mode counting (Step 1)
  - Gauge algebra identification (Step 2, GEOMETRICALLY_MOTIVATED)
  - Orbifold projection (Step 3, DERIVED)
  - Rank-4 alternative analysis
  - gap3_closure_report structure and honest epistemic labels
  - pillar_report contract
"""
from __future__ import annotations

import pytest
from src.core.pillar770_su5_orbifold_closure import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    N_W,
    SU5_RANK,
    SU5_GENERATORS,
    SM_GAUGE_GROUP,
    SM_GENERATORS,
    RANK_4_ALTERNATIVES,
    kk_zero_mode_count,
    step1_kk_spectrum,
    step2_gauge_algebra_identification,
    step3_orbifold_projection,
    rank4_alternative_analysis,
    gap3_closure_report,
    pillar_report,
)


# ── Constants ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 770


def test_pillar_status():
    assert PILLAR_STATUS == "PARTIALLY_CLOSED"


def test_n_w():
    assert N_W == 5


def test_su5_rank():
    assert SU5_RANK == 4


def test_su5_generators():
    assert SU5_GENERATORS == 24   # 5² − 1


def test_sm_generators():
    assert SM_GENERATORS == 12   # 8+3+1


# ── KK zero-mode counting ─────────────────────────────────────────────────────

def test_kk_zero_mode_count_n5():
    counts = kk_zero_mode_count(5)
    assert counts["n_w"] == 5
    assert counts["total_generators"] == 24   # 5²−1
    assert counts["rank_of_massless_algebra"] == 4
    assert counts["status"] == "DERIVED"


def test_kk_zero_mode_even_odd_sum():
    counts = kk_zero_mode_count(5)
    assert (counts["z2_even_massless"] + counts["z2_odd_massive"]) == counts["total_generators"]


def test_kk_zero_mode_count_n3():
    counts = kk_zero_mode_count(3)
    assert counts["total_generators"] == 8   # 3²−1 = SU(3)


# ── Step 1 ────────────────────────────────────────────────────────────────────

def test_step1_derived():
    s1 = step1_kk_spectrum()
    assert s1["status"] == "DERIVED"
    assert s1["step"] == 1


def test_step1_rank():
    s1 = step1_kk_spectrum()
    assert s1["rank"] == 4


def test_step1_n_massless_generators():
    s1 = step1_kk_spectrum()
    assert s1["n_massless_generators"] > 0


# ── Step 2 ────────────────────────────────────────────────────────────────────

def test_step2_geometrically_motivated():
    s2 = step2_gauge_algebra_identification()
    assert s2["status"] == "GEOMETRICALLY_MOTIVATED"
    assert s2["step"] == 2


def test_step2_selected_algebra_is_su5():
    s2 = step2_gauge_algebra_identification()
    assert s2["selected_algebra"] == "SU(5)"


def test_step2_open_gap_documented():
    s2 = step2_gauge_algebra_identification()
    assert len(s2["open_gap"]) > 20


def test_step2_exclusion_table_populated():
    s2 = step2_gauge_algebra_identification()
    assert len(s2["exclusion_table"]) == len(RANK_4_ALTERNATIVES)


def test_step2_su5_selected_in_table():
    s2 = step2_gauge_algebra_identification()
    selected = [e for e in s2["exclusion_table"] if e["algebra"] == "A4 = SU(5)"]
    assert len(selected) == 1
    assert selected[0]["verdict"].startswith("SELECTED")


# ── Step 3 ────────────────────────────────────────────────────────────────────

def test_step3_derived():
    s3 = step3_orbifold_projection()
    assert s3["status"] == "DERIVED"
    assert s3["step"] == 3


def test_step3_output_group():
    s3 = step3_orbifold_projection()
    assert s3["output_group"] == SM_GAUGE_GROUP


def test_step3_references_pillar636():
    s3 = step3_orbifold_projection()
    assert s3["pillar_reference"] == 636


def test_step3_heavy_modes_listed():
    s3 = step3_orbifold_projection()
    assert len(s3["heavy_modes_decoupled"]) > 0


# ── rank4_alternative_analysis ────────────────────────────────────────────────

def test_rank4_alternatives_count():
    table = rank4_alternative_analysis()
    assert len(table) == len(RANK_4_ALTERNATIVES)


def test_rank4_all_have_algebra_key():
    for entry in rank4_alternative_analysis():
        assert "algebra" in entry
        assert "verdict" in entry
        assert "proof_status" in entry


# ── gap3_closure_report ───────────────────────────────────────────────────────

def test_gap3_closure_report_structure():
    report = gap3_closure_report()
    assert report["gap_id"] == "Gap_3"
    assert isinstance(report["is_fully_closed"], bool)


def test_gap3_not_fully_closed():
    report = gap3_closure_report()
    assert report["is_fully_closed"] is False


def test_gap3_weakest_link_is_step2():
    report = gap3_closure_report()
    assert report["weakest_link"] == "GEOMETRICALLY_MOTIVATED"


def test_gap3_path_to_closure_documented():
    report = gap3_closure_report()
    assert len(report["path_to_full_closure"]) > 30


def test_gap3_has_three_steps():
    report = gap3_closure_report()
    assert len(report["steps"]) == 3


def test_gap3_status_before():
    report = gap3_closure_report()
    assert "GEOMETRICALLY_MOTIVATED" in report["status_before"]


def test_gap3_downstream_upgrades_if_closed():
    report = gap3_closure_report()
    assert len(report["downstream_upgrades_if_closed"]) >= 2


# ── pillar_report ─────────────────────────────────────────────────────────────

def test_pillar_report_contract():
    report = pillar_report()
    assert report["pillar"] == PILLAR_NUMBER
    assert "gap3_closed" in report
    assert report["gap3_closed"] is False  # honest: not yet fully proved


def test_pillar_report_has_gap3_report():
    report = pillar_report()
    assert "gap3_report" in report
