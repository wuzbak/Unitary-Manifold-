# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 503 PMNS p_R full-chain synchronization."""

import math

import pytest

from src.core import pillar503_pmns_pr_full_chain as p503


def test_constants():
    assert p503.PILLAR_NUMBER == 503
    assert p503.PILLAR_STATUS == "PMNS_PR_FULL_CHAIN_SYNCHRONIZED"
    assert p503.TARGET_SOLAR_DEG > 30
    assert p503.SOLAR_TOLERANCE_DEG == 1.0


@pytest.mark.parametrize("pr", [0.352, 0.357, 0.370, 0.388])
def test_texture_profile_normalized(pr):
    profile = p503.texture_profile(pr)
    norm = math.sqrt(profile["left"] ** 2 + profile["middle"] ** 2 + profile["right"] ** 2)
    assert norm == pytest.approx(1.0)
    assert profile["p_r"] == pr


@pytest.mark.parametrize("pr", [0.352, 0.370, 0.388])
def test_texture_is_symmetric(pr):
    matrix = p503.coupled_seesaw_texture(pr)
    assert len(matrix) == 3
    for i in range(3):
        for j in range(3):
            assert matrix[i][j] == pytest.approx(matrix[j][i])


@pytest.mark.parametrize("pr", [0.352, 0.370, 0.388])
def test_row_norms_positive(pr):
    norms = p503.texture_row_norms(pr)
    assert len(norms) == 3
    assert all(value > 0 for value in norms)
    assert norms[0] > norms[1] > norms[2]


@pytest.mark.parametrize("pr", [0.352, 0.370, 0.388])
def test_effective_pr_is_stable(pr):
    result = p503.effective_pr_from_texture(pr)
    assert result["effective_p_r"] > 0
    assert abs(result["texture_correction"]) < 0.25


def test_effective_pr_texture_correction_bounded_for_canonical():
    result = p503.effective_pr_from_texture()
    assert abs(result["texture_correction"]) < 0.08


def test_solar_angle_window_ordered():
    window = p503.solar_angle_window()
    assert window["theta12_low_deg"] < window["theta12_center_deg"] < window["theta12_high_deg"]


def test_solar_angle_window_retains_pdg_gap():
    assert p503.solar_angle_window()["target_in_window"] is False


def test_solar_residual_named_not_hidden():
    assert p503.solar_angle_window()["center_residual_deg"] > 10.0


def test_full_chain_consistency_synchronized():
    result = p503.full_chain_consistency()
    assert result["synchronized"] is True
    assert result["pdg_gap_retained"] is True
    assert result["hardgate_score_delta"] == 0.0


def test_residual_retained():
    result = p503.full_chain_consistency()
    assert "THREE_GENERATION" in result["residual_name"]


def test_report_shape():
    report = p503.pillar_report()
    assert report["pillar"] == 503
    assert report["claim_label"] == "FULL_CHAIN_SYNCHRONIZED"
    assert "full_chain_consistency" in report
