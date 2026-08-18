# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 674 — NP-BC-7 Sub-gap T."""
from __future__ import annotations

import pytest

from src.core.pillar674_np_bc7_subgap_t_adm_path_integral_measure import (
    ADM_MEASURE_OBSTRUCTION_TYPE,
    ADJACENT_TRACK,
    DEWITT_METRIC_FORMULA,
    FULL_3METRIC_SECTOR_OBSTRUCTION,
    LEAN4_NEW_FILE,
    LEAN4_THEOREM_COUNT,
    M_PHI_GEV,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PROVED_COMPONENTS,
    RADION_SECTOR_GAUSSIAN,
    SUBGAP_T_STATUS,
    UV_REGULATOR_OPTIONS,
    VERSION,
    Z_PHI_ONE_LOOP_FORMULA,
    dewitt_metric_orbifold,
    full_3metric_obstruction,
    lean4_certificate,
    pillar_report,
    proved_components,
    radion_partition_function,
    remaining_gap_assessment,
)


class TestPillar674Constants:
    @pytest.mark.parametrize(
        ("actual", "expected"),
        [
            (PILLAR_NUMBER, 674),
            (VERSION, "v21.0"),
            (LEAN4_NEW_FILE["theorems"], 11),
            (LEAN4_THEOREM_COUNT["total_previous"], 354),
            (LEAN4_THEOREM_COUNT["total"], 365),
            (M_PHI_GEV, 765.0),
            (len(UV_REGULATOR_OPTIONS), 2),
            (len(PROVED_COMPONENTS), 11),
        ],
    )
    def test_exact_constants(self, actual, expected) -> None:
        assert actual == expected

    def test_boolean_constants(self) -> None:
        assert ADJACENT_TRACK is False
        assert RADION_SECTOR_GAUSSIAN is True
        assert FULL_3METRIC_SECTOR_OBSTRUCTION is True

    def test_string_constants(self) -> None:
        assert PILLAR_STATUS == "NP_BC7_SUBGAP_T_ADM_PATH_INTEGRAL_MEASURE_OBSTRUCTION_FORMALISED"
        assert SUBGAP_T_STATUS == "ADM_PATH_INTEGRAL_MEASURE_OBSTRUCTION_FORMALISED"
        assert ADM_MEASURE_OBSTRUCTION_TYPE == "ADM_MEASURE_OBSTRUCTION"
        assert DEWITT_METRIC_FORMULA.startswith("G^{ijkl}")
        assert Z_PHI_ONE_LOOP_FORMULA == "(m_phi / (2*pi))**(1/2)"
        assert "Sub-gap T" in PILLAR_TITLE


class TestPillar674Functions:
    def test_proved_components_length(self) -> None:
        assert len(proved_components()) == 11
        assert proved_components() == PROVED_COMPONENTS

    def test_dewitt_metric_orbifold(self) -> None:
        result = dewitt_metric_orbifold()
        assert result["formula"] == DEWITT_METRIC_FORMULA
        assert result["kk_adds_radion_sector"] is True
        assert "Riem(S1/Z2)" in result["sectors"]

    def test_radion_partition_function(self) -> None:
        result = radion_partition_function()
        assert result["m_phi_gev"] == pytest.approx(765.0, rel=1e-12)
        assert result["sector_gaussian"] is True
        assert result["z_phi_value"] > 0.0

    def test_full_3metric_obstruction(self) -> None:
        result = full_3metric_obstruction()
        assert result["obstruction_type"] == "ADM_MEASURE_OBSTRUCTION"
        assert result["obstruction_formalised"] is True
        assert result["community_level_open_problem"] is True
        assert result["uv_regulator_options"] == UV_REGULATOR_OPTIONS

    def test_remaining_gap_assessment(self) -> None:
        result = remaining_gap_assessment()
        assert result["full_path_integral_claimed"] is False
        assert result["radion_sector_gaussian"] is True
        assert result["full_3metric_sector_obstruction"] is True

    def test_lean4_certificate(self) -> None:
        result = lean4_certificate()
        assert result["new_theorems"] == 11
        assert result["lean4_total_after"] == 365
        assert result["proved_components"] == 11


class TestPillar674Report:
    def test_report_shape(self) -> None:
        report = pillar_report()
        for key in (
            "pillar",
            "title",
            "status",
            "version",
            "adjacent_track",
            "dewitt_metric_orbifold",
            "radion_partition_function",
            "full_3metric_obstruction",
            "proved_components",
            "remaining_gap_assessment",
            "lean4_certificate",
        ):
            assert key in report

    def test_report_values(self) -> None:
        report = pillar_report()
        assert report["pillar"] == 674
        assert report["adjacent_track"] is False
        assert report["toe_score_delta"] == 0.0
        assert report["hardgate_score_delta"] == 0.0
