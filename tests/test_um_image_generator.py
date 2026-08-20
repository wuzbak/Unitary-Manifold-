# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for the public-site UM physics image generator constants."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.core import litebird_boundary
from src.core.pillar585_dm21_closure_certificate import DM21_CURRENT_TENSION
from src.core.pillar712_tensor_spectral_index_tightening import N_S as SOURCE_N_S
from src.core.pillar712_tensor_spectral_index_tightening import R_BRAIDED as SOURCE_R_BRAIDED
from src.core.pillar772_lepton_jarlskog_lattice_closure import TENSION_AFTER_LJL
from src.core.pillar773_dm21_nlo_lattice_correction import TENSION_AFTER_NLO
from src.core.pillar784_type_ab_gap_classification import K_CS as SOURCE_K_CS
from src.core.pillar784_type_ab_gap_classification import LEAN4_NEW_TOTAL
from src.core.pillar784_type_ab_gap_classification import N_W as SOURCE_N_W

REPO_ROOT = Path(__file__).resolve().parents[1]
JS_PATH = REPO_ROOT / "public-site" / "js" / "um-image-generator.js"
HTML_PATH = REPO_ROOT / "public-site" / "az-apps" / "um-image-generator.html"
STATUS_PATH = REPO_ROOT / "STATUS.md"
JS_TEXT = JS_PATH.read_text(encoding="utf-8")
HTML_TEXT = HTML_PATH.read_text(encoding="utf-8")
STATUS_TEXT = STATUS_PATH.read_text(encoding="utf-8")


def js_number(name: str) -> float:
    match = re.search(rf"export const {name} = ([0-9.]+);", JS_TEXT)
    assert match, f"Missing JS numeric constant: {name}"
    return float(match.group(1))


def js_int(name: str) -> int:
    return int(js_number(name))


def js_array(name: str) -> list[float]:
    match = re.search(rf"export const {name} = Object\.freeze\(\[(.*?)\]\);", JS_TEXT)
    assert match, f"Missing JS array constant: {name}"
    return [float(part.strip()) for part in match.group(1).split(",")]


def status_test_count() -> int:
    match = re.search(r"56,747 passed", STATUS_TEXT)
    assert match, "STATUS.md no longer reports the expected regression test count"
    return 56747


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("N_S", 0.9635),
        ("R_BRAIDED", 0.0315),
        ("BETA_LOW", 0.273),
        ("BETA_HIGH", 0.331),
        ("BETA_FLOOR", 0.22),
        ("BETA_CEILING", 0.38),
        ("WINDING_NUMBER", 5),
        ("K_CS", 74),
        ("LEAN4_THEOREMS", 976),
        ("TEST_COUNT", 56747),
    ],
)
def test_js_scalar_literals(name: str, expected: float) -> None:
    assert js_number(name) == pytest.approx(expected)


@pytest.mark.parametrize("index, expected", [(0, 2.98), (1, 1.16), (2, 1.07)])
def test_js_dm21_array_literals(index: int, expected: float) -> None:
    assert js_array("DM21_TENSIONS")[index] == pytest.approx(expected)


def test_html_page_exists() -> None:
    assert HTML_PATH.exists()


def test_html_title_present() -> None:
    assert "UM Physics Image Generator" in HTML_TEXT


def test_html_has_download_button() -> None:
    assert "Download PNG" in HTML_TEXT


@pytest.mark.parametrize(
    ("function_name",),
    [
        ("drawCmbParameterPlane",),
        ("drawBirefringenceWindow",),
        ("drawKkMassTower",),
        ("drawBraidTopology",),
        ("drawMetricStructure",),
        ("drawDm21Timeline",),
        ("drawPillarDomainPieChart",),
        ("drawFalsificationCalendar",),
    ],
)
def test_js_exports_each_renderer(function_name: str) -> None:
    assert f"export function {function_name}(canvas" in JS_TEXT


def test_ns_matches_source_constant() -> None:
    assert js_number("N_S") == pytest.approx(SOURCE_N_S)


def test_r_matches_source_constant() -> None:
    assert js_number("R_BRAIDED") == pytest.approx(SOURCE_R_BRAIDED)


def test_beta_low_matches_source_constant() -> None:
    assert js_number("BETA_LOW") == pytest.approx(litebird_boundary.BETA_CANONICAL)


def test_beta_high_matches_source_constant() -> None:
    assert js_number("BETA_HIGH") == pytest.approx(litebird_boundary.BETA_DERIVED)


def test_beta_floor_matches_source_constant() -> None:
    assert js_number("BETA_FLOOR") == pytest.approx(litebird_boundary.ADMISSIBLE_LOWER)


def test_beta_ceiling_matches_source_constant() -> None:
    assert js_number("BETA_CEILING") == pytest.approx(litebird_boundary.ADMISSIBLE_UPPER)


def test_winding_matches_source_constant() -> None:
    assert js_int("WINDING_NUMBER") == SOURCE_N_W


def test_kcs_matches_source_constant() -> None:
    assert js_int("K_CS") == SOURCE_K_CS


def test_dm21_step2_matches_source_constant() -> None:
    assert js_array("DM21_TENSIONS")[0] == pytest.approx(DM21_CURRENT_TENSION)


def test_dm21_ljl_matches_rounded_source_constant() -> None:
    assert js_array("DM21_TENSIONS")[1] == pytest.approx(round(TENSION_AFTER_LJL, 2))


def test_dm21_nlo_matches_rounded_source_constant() -> None:
    assert js_array("DM21_TENSIONS")[2] == pytest.approx(round(TENSION_AFTER_NLO, 2))


def test_lean4_total_matches_source_constant() -> None:
    assert js_int("LEAN4_THEOREMS") == LEAN4_NEW_TOTAL


def test_status_test_count_matches_literal() -> None:
    assert js_int("TEST_COUNT") == status_test_count()


def test_kcs_is_sum_of_squares() -> None:
    assert js_int("K_CS") == 5 ** 2 + 7 ** 2


def test_dm21_tensions_are_monotone_nonincreasing() -> None:
    tensions = js_array("DM21_TENSIONS")
    assert tensions[0] >= tensions[1] >= tensions[2]


def test_visualization_metadata_has_eight_entries() -> None:
    assert JS_TEXT.count("filename:") == 8


def test_footer_liability_notice_present() -> None:
    assert "Open science artifact for human review, use at your own liability" in HTML_TEXT
