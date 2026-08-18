# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 675 — NP-BC-7 synthesis certificate."""
from __future__ import annotations

from src.core.pillar675_np_bc7_synthesis_wdw_adm_obstruction_certificate import (
    ADJACENT_TRACK,
    ADVANCEMENT_OVER_DEFERMENT,
    COMMUNITY_LEVEL_OPEN_PROBLEM,
    FULL_QUANTIZATION_CLAIMED,
    LEAN4_TOTAL_NP_BC7,
    MINISUPERSPACE_TRACTABLE,
    NP_BC7_PILLARS,
    OBSTRUCTION_STATUS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SUBGAPS_S_T_PROVED,
    VERSION,
    np_bc7_synthesis_certificate,
    pillar_report,
    what_is_NOT_claimed,
    what_is_claimed,
)


class TestPillar675Constants:
    def test_constant_values(self) -> None:
        assert PILLAR_NUMBER == 675
        assert VERSION == "v21.0"
        assert PILLAR_STATUS == "WDW_ADM_OBSTRUCTION_PRECISELY_CHARACTERISED"
        assert OBSTRUCTION_STATUS == "WDW_ADM_OBSTRUCTION_PRECISELY_CHARACTERISED"
        assert LEAN4_TOTAL_NP_BC7 == 365
        assert len(SUBGAPS_S_T_PROVED) == 2
        assert NP_BC7_PILLARS == [673, 674]

    def test_boolean_constants(self) -> None:
        assert ADJACENT_TRACK is False
        assert MINISUPERSPACE_TRACTABLE is True
        assert FULL_QUANTIZATION_CLAIMED is False
        assert COMMUNITY_LEVEL_OPEN_PROBLEM is True


class TestPillar675Functions:
    def test_np_bc7_synthesis_certificate(self) -> None:
        result = np_bc7_synthesis_certificate()
        assert result["lean4_total"] == 365
        assert result["minisuperspace_tractable"] is True
        assert result["full_quantization_claimed"] is False
        assert result["community_level_open_problem"] is True
        assert result["advancement_over_deferment"] == ADVANCEMENT_OVER_DEFERMENT

    def test_claim_lists(self) -> None:
        claims = what_is_claimed()
        non_claims = what_is_NOT_claimed()
        assert len(claims) == 6
        assert len(non_claims) >= 3
        assert any("community-level open problem" in item for item in claims)
        assert any("No full inhomogeneous Wheeler-DeWitt quantization" in item for item in non_claims)


class TestPillar675Report:
    def test_report_shape(self) -> None:
        report = pillar_report()
        for key in (
            "pillar",
            "title",
            "status",
            "version",
            "adjacent_track",
            "np_bc7_synthesis_certificate",
            "what_is_claimed",
            "what_is_NOT_claimed",
            "toe_score_delta",
            "hardgate_score_delta",
        ):
            assert key in report

    def test_report_values(self) -> None:
        report = pillar_report()
        assert report["pillar"] == 675
        assert report["adjacent_track"] is False
        assert report["toe_score_delta"] == 0.0
        assert report["hardgate_score_delta"] == 0.0
