# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 673 — NP-BC-7 Sub-gap S."""
from __future__ import annotations

import pytest

from src.core.pillar673_np_bc7_subgap_s_wdw_functional_determinant import (
    ADJACENT_TRACK,
    BRAIDED_SOUND_SPEED,
    FULL_FUNCTIONAL_INTEGRAL_DIVERGES,
    K_CS,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    MINISUPERSPACE_TRACTABLE,
    N_W,
    OBSTRUCTION_TYPE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    SEELEY_DEWITT_COEFFICIENTS,
    SUBGAP_S_STATUS,
    VERSION,
    lean4_certificate,
    pillar_report,
    proved_components,
    remaining_gap_assessment,
    seeley_dewitt_heat_kernel,
    z2_projection_effect,
)


class TestPillar673Constants:
    @pytest.mark.parametrize(
        ("actual", "expected"),
        [
            (PILLAR_NUMBER, 673),
            (VERSION, "v21.0"),
            (K_CS, 74),
            (N_W, 5),
            (LEAN4_NEW_FILE["theorems"], 12),
            (LEAN4_THEOREM_COUNT["total_previous"], 342),
            (LEAN4_THEOREM_COUNT["total"], 354),
            (len(PROVED_COMPONENTS), 12),
        ],
    )
    def test_exact_constants(self, actual, expected) -> None:
        assert actual == expected

    def test_boolean_constants(self) -> None:
        assert ADJACENT_TRACK is False
        assert MINISUPERSPACE_TRACTABLE is True
        assert FULL_FUNCTIONAL_INTEGRAL_DIVERGES is True

    def test_string_constants(self) -> None:
        assert PILLAR_STATUS == "NP_BC7_SUBGAP_S_WDW_FUNCTIONAL_DETERMINANT_OBSTRUCTION_FORMALISED"
        assert SUBGAP_S_STATUS == "WDW_FUNCTIONAL_DETERMINANT_OBSTRUCTION_FORMALISED"
        assert "SEELEY_DEWITT" in OBSTRUCTION_TYPE
        assert "Sub-gap S" in PILLAR_TITLE

    def test_core_coefficients(self) -> None:
        assert SEELEY_DEWITT_COEFFICIENTS["a0"] == "Vol(M)"
        assert SEELEY_DEWITT_COEFFICIENTS["a2"] == "integral_R_over_6"
        assert SEELEY_DEWITT_COEFFICIENTS["a4"] == "curvature_squared_integral"
        assert BRAIDED_SOUND_SPEED == pytest.approx(12.0 / 37.0, rel=1e-12)


class TestPillar673Functions:
    def test_proved_components_length(self) -> None:
        assert len(proved_components()) == 12
        assert proved_components() == PROVED_COMPONENTS

    def test_heat_kernel(self) -> None:
        result = seeley_dewitt_heat_kernel()
        assert result["a0_coeff"] == "Vol(M)"
        assert result["a4_coeff"] == "curvature_squared_integral"
        assert result["minisuperspace_tractable"] is True
        assert result["full_functional_diverges"] is True
        assert result["divergence_structure_named"] is True

    def test_z2_projection_effect(self) -> None:
        result = z2_projection_effect()
        assert result["z2_eliminates_odd_modes"] is True
        assert result["kk_correction_coefficient_numeric"] == N_W**2 * K_CS
        assert "curvature_squared_prefactor" in result["kk_correction_coefficient"]

    def test_remaining_gap_assessment(self) -> None:
        result = remaining_gap_assessment()
        assert result["full_quantization_claimed"] is False
        assert result["obstruction_formalised"] is True
        assert result["community_level_open_problem"] is True

    def test_lean4_certificate(self) -> None:
        result = lean4_certificate()
        assert result["lean4_total_after"] == 354
        assert result["new_theorems"] == 12
        assert result["proved_components"] == 12


class TestPillar673Report:
    def test_report_shape(self) -> None:
        report = pillar_report()
        for key in (
            "pillar",
            "title",
            "status",
            "version",
            "adjacent_track",
            "seeley_dewitt_heat_kernel",
            "z2_projection_effect",
            "proved_components",
            "remaining_gap_assessment",
            "lean4_certificate",
            "toe_score_delta",
            "hardgate_score_delta",
        ):
            assert key in report

    def test_report_values(self) -> None:
        report = pillar_report()
        assert report["pillar"] == 673
        assert report["adjacent_track"] is False
        assert report["toe_score_delta"] == 0.0
        assert report["hardgate_score_delta"] == 0.0
