# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 585 — Δm²₂₁ quantified-residual certificate."""
from __future__ import annotations

import pytest

from src.core.pillar585_dm21_closure_certificate import (
    DM21_AFTER_STEP1,
    DM21_AFTER_STEP2,
    DM21_BASELINE_TENSION,
    DM21_CURRENT_TENSION,
    DM21_THRESHOLD_CLOSED,
    NAMED_RESIDUAL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    TOE_DELTA,
    VERSION,
    cascade_summary,
    closure_certificate,
    comparison_with_dm31,
    named_residual_assessment,
    p20_status_upgrade,
    pillar_report,
)


def test_pillar_identity():
    assert PILLAR_NUMBER == 585
    assert PILLAR_STATUS == "DM21_QUANTIFIED_RESIDUAL_CASCADE_COMPLETE"
    assert VERSION == "v20.1"


def test_certificate_constants():
    assert DM21_BASELINE_TENSION == pytest.approx(4.63)
    assert DM21_AFTER_STEP1 == pytest.approx(3.07)
    assert DM21_AFTER_STEP2 == pytest.approx(2.98)
    assert DM21_CURRENT_TENSION == pytest.approx(2.98)
    assert DM21_THRESHOLD_CLOSED == pytest.approx(1.0)
    # Retired by Pillar 772 (Lepton Jarlskog-Lattice Closure)
    assert NAMED_RESIDUAL == "DM21_LJL_1_16SIGMA_QUANTIFIED_RESIDUAL"
    assert TOE_DELTA == pytest.approx(0.0)


def test_cascade_summary_length():
    summary = cascade_summary()
    assert len(summary) == 3


def test_cascade_ordered_steps():
    summary = cascade_summary()
    assert [item["step"] for item in summary] == [0, 1, 2]


def test_cascade_tensions_decrease():
    summary = cascade_summary()
    tensions = [item["tension_sigma"] for item in summary]
    assert tensions[0] > tensions[1] > tensions[2]


def test_cascade_final_not_closed():
    summary = cascade_summary()
    assert summary[-1]["tension_sigma"] > DM21_THRESHOLD_CLOSED


def test_named_residual_keys():
    residual = named_residual_assessment()
    for key in [
        "named_residual",
        "ratio_um",
        "ratio_pdg",
        "ratio_error_percent",
        "obstruction",
        "needed_structure",
        "verdict",
    ]:
        assert key in residual


def test_named_residual_value():
    residual = named_residual_assessment()
    assert residual["named_residual"] == NAMED_RESIDUAL
    assert residual["verdict"] == "RESIDUAL_REMAINS"


def test_named_residual_ratio_error_about_ten_percent():
    residual = named_residual_assessment()
    assert 9.0 < residual["ratio_error_percent"] < 15.0


def test_named_residual_has_multiple_needs():
    residual = named_residual_assessment()
    assert len(residual["needed_structure"]) >= 3


def test_status_upgrade_honest():
    upgrade = p20_status_upgrade()
    assert upgrade["status_before"] == "GEOMETRIC_ESTIMATE"
    assert upgrade["status_after"] == "QUANTIFIED_RESIDUAL"
    assert upgrade["closed"] is False


def test_comparison_with_dm31():
    comparison = comparison_with_dm31()
    assert comparison["dm31_final_tension_sigma"] < 1.0
    assert comparison["dm21_final_tension_sigma"] > 1.0
    assert "not closed" in comparison["difference"].lower()


def test_closure_certificate_keys():
    cert = closure_certificate()
    for key in [
        "pillar",
        "certificate",
        "status_before",
        "status_after",
        "tension_before_sigma",
        "tension_after_step1_sigma",
        "tension_after_step2_sigma",
        "closure_threshold_sigma",
        "closed",
        "named_residual",
        "what_is_claimed",
        "what_is_NOT_claimed",
    ]:
        assert key in cert


def test_closure_certificate_not_closed():
    cert = closure_certificate()
    assert cert["closed"] is False
    assert cert["tension_after_step2_sigma"] > cert["closure_threshold_sigma"]


def test_closure_certificate_tensions_match_constants():
    cert = closure_certificate()
    assert cert["tension_before_sigma"] == pytest.approx(DM21_BASELINE_TENSION)
    assert cert["tension_after_step1_sigma"] == pytest.approx(DM21_AFTER_STEP1)
    assert cert["tension_after_step2_sigma"] == pytest.approx(DM21_AFTER_STEP2)


def test_closure_certificate_has_honest_anti_claims():
    cert = closure_certificate()
    assert any("not closed" in item.lower() for item in cert["what_is_NOT_claimed"])
    assert any("not within 1σ" in item.lower() or "not within 1" in item.lower()
               for item in cert["what_is_NOT_claimed"])


def test_closure_certificate_toe_delta_zero():
    cert = closure_certificate()
    assert cert["toe_score_delta"] == pytest.approx(0.0)


def test_report_structure():
    report = pillar_report()
    assert report["pillar"] == 585
    assert report["status"] == PILLAR_STATUS
    assert report["adjacent_track"] is False
    assert report["toe_score_delta"] == pytest.approx(0.0)
    assert report["hardgate_score_delta"] == pytest.approx(0.0)


def test_report_parent_pillars():
    report = pillar_report()
    assert report["parent_pillars"] == [583, 584]


def test_report_contains_certificate_and_residual():
    report = pillar_report()
    assert report["closure_certificate"]["named_residual"] == NAMED_RESIDUAL
    assert report["named_residual_assessment"]["verdict"] == "RESIDUAL_REMAINS"
