# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from src.core.yukawa_geometric import (
    default_sector_localization,
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


def test_hierarchy_ratios_finite():
    ratios = hierarchy_ratios_from_texture()
    assert ratios["mode2_over_mode1"] > 0.0
    assert ratios["mode3_over_mode2"] > 0.0
    assert ratios["mode3_over_mode1"] > 0.0


def test_report_is_honestly_labeled():
    report = yukawa_geometric_report()
    assert report["texture"]["status"] == "DERIVED"
    assert report["status"] == "FITTED"
