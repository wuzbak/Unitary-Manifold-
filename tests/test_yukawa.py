# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from src.core.yukawa_geometric import (
    default_sector_localization,
    zero_mode_overlap,
    yukawa_matrix_three_sector,
    hierarchy_ratios_from_texture,
    yukawa_geometric_report,
)


def test_localization_has_three_sectors():
    loc = default_sector_localization()
    assert set(loc.keys()) == {"uv", "bulk", "ir"}


def test_yukawa_matrix_is_3x3_positive():
    mat = yukawa_matrix_three_sector()["matrix"]
    assert len(mat) == 3
    assert all(len(row) == 3 for row in mat)
    assert all(cell > 0.0 for row in mat for cell in row)
    assert mat[0][1] != mat[0][0]
    for i in range(3):
        for j in range(3):
            assert mat[i][j] == mat[j][i]


def test_hierarchy_ratios_finite():
    ratios = hierarchy_ratios_from_texture()
    assert ratios["mode2_over_mode1"] > 1.0
    assert ratios["mode3_over_mode2"] > 1.0
    assert ratios["mode3_over_mode1"] > 1.0
    assert ratios["mode3_over_mode1"] >= ratios["mode2_over_mode1"]


def test_overlap_self_exceeds_cross_overlap():
    loc = default_sector_localization()
    self_overlap = zero_mode_overlap(loc["uv"], loc["uv"])
    cross_overlap = zero_mode_overlap(loc["uv"], loc["ir"])
    assert self_overlap > cross_overlap
    assert 0.9 <= self_overlap <= 1.01


def test_overlap_converges_with_grid_refinement():
    loc = default_sector_localization()
    coarse = zero_mode_overlap(loc["bulk"], loc["ir"], n_points=501)
    fine = zero_mode_overlap(loc["bulk"], loc["ir"], n_points=4001)
    assert abs(fine - coarse) < 1e-3


def test_report_is_honestly_labeled():
    report = yukawa_geometric_report()
    assert report["texture"]["status"] == "DERIVED"
    assert report["status"] == "FITTED"
    ratios = report["hierarchy_ratios"]
    assert "mode2_over_mode1" in ratios
    assert "mode3_over_mode2" in ratios
    assert "mode3_over_mode1" in ratios
    assert ratios["mode2_over_mode1"] > 1.0
