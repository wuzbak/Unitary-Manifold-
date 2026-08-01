# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 624 — F-theory Rung 10 spectral cover global sections."""
import pytest
from src.core.pillar624_ftheory_rung10_spectral_cover_global import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SPECTRAL_COVER_SECTIONS_STATUS,
    K_CS,
    N_SHEETS,
    N_W,
    DEG_L1,
    GENUS_GUT_DIVISOR,
    GLOBAL_SECTIONS_EXIST,
    spectral_cover_sections,
    line_bundle_sections,
    global_section_certificate,
    pillar_report,
)

NUMERIC_CHECKS = [
    ("PILLAR_NUMBER", PILLAR_NUMBER, 624),
    ("K_CS", K_CS, 74),
    ("N_SHEETS", N_SHEETS, 5),
    ("N_W", N_W, 5),
    ("DEG_L1", DEG_L1, 74 / 5),
    ("GENUS_GUT_DIVISOR", GENUS_GUT_DIVISOR, 0),
]

STRING_CHECKS = [
    ("PILLAR_STATUS", PILLAR_STATUS, "FTHEORY_RUNG10_SPECTRAL_COVER_GLOBAL_SECTIONS_ADJACENT"),
    ("SPECTRAL_COVER_SECTIONS_STATUS", SPECTRAL_COVER_SECTIONS_STATUS, "GLOBAL_SECTIONS_PROVED_AT_REFERENCE_CY4"),
]


@pytest.mark.parametrize("name,actual,expected", NUMERIC_CHECKS)
def test_numeric_constant(name, actual, expected):
    assert actual == pytest.approx(expected, rel=1e-10), f"{name} mismatch"


@pytest.mark.parametrize("name,actual,expected", STRING_CHECKS)
def test_string_constant(name, actual, expected):
    assert actual == expected, f"{name} mismatch"


def test_global_sections_exist():
    assert GLOBAL_SECTIONS_EXIST is True


def test_spectral_cover_sections_structure():
    result = spectral_cover_sections()
    assert isinstance(result, dict)
    assert result["all_sections_exist"] is True
    assert len(result["sections"]) == N_SHEETS - 1  # b2 through b5
    assert result["genus_gut_divisor"] == 0


def test_line_bundle_sections_all_k():
    sections = line_bundle_sections()
    assert len(sections) == N_SHEETS - 1  # k=2..5
    for entry in sections:
        assert entry["h0_bound"] > 0, f"h0_bound positive for k={entry['k']}"
        assert entry["deg_lk"] > 0, f"deg_lk positive for k={entry['k']}"


def test_global_section_certificate_structure():
    cert = global_section_certificate()
    assert cert["blocking_residual_resolved"] is True
    assert cert["global_sections_exist"] is True
    assert cert["all_sections_exist"] is True


def test_pillar_report_structure():
    rpt = pillar_report()
    assert rpt["pillar"] == 624
    assert rpt["adjacent_track"] is True
    assert rpt["toe_score_delta"] == 0.0
    assert rpt["hardgate_score_delta"] == 0.0
    assert "spectral_cover_sections" in rpt
    assert "global_section_certificate" in rpt
    assert "line_bundle_sections" in rpt


def test_pillar_report_all_sections_exist():
    rpt = pillar_report()
    assert rpt["spectral_cover_sections"]["all_sections_exist"] is True
