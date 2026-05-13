# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 183 sub-leading c_L spectrum expansion."""

from __future__ import annotations

import pytest

from src.core.pillar183_cl_spectrum_subleading import cl_spectrum


@pytest.mark.parametrize(
    "k_cs,n_w",
    [
        (74, 5),
        (74, 7),
        (61, 5),
        (130, 7),
        (100, 5),
        (150, 5),
        (256, 9),
        (512, 11),
        (1000, 5),
        (4096, 13),
    ],
)
def test_leading_matches_baseline(k_cs: int, n_w: int) -> None:
    result = cl_spectrum(k_cs=k_cs, n_w=n_w, order=2)
    expected = 0.5 + (n_w / k_cs)
    assert result["leading"]["value"] == pytest.approx(expected, abs=1e-15)


@pytest.mark.parametrize(
    "k_cs,n_w",
    [
        (74, 5),
        (74, 7),
        (74, 9),
        (80, 5),
        (96, 7),
        (128, 5),
        (256, 9),
        (512, 11),
    ],
)
def test_subleading_order_1_bounded(k_cs: int, n_w: int) -> None:
    result = cl_spectrum(k_cs=k_cs, n_w=n_w, order=2)
    rel_pct = result["subleading"]["order_1"]["relative_pct"]
    assert rel_pct <= 1.4


@pytest.mark.parametrize(
    "k_cs,n_w,tol",
    [
        (10_000, 5, 2.0e-3),
        (20_000, 5, 1.0e-3),
        (50_000, 5, 5.0e-4),
        (100_000, 5, 2.5e-4),
        (100_000, 7, 2.5e-4),
        (200_000, 9, 1.5e-4),
        (500_000, 11, 6.0e-5),
        (1_000_000, 13, 3.0e-5),
    ],
)
def test_large_kcs_limit_tends_to_one(k_cs: int, n_w: int, tol: float) -> None:
    result = cl_spectrum(k_cs=k_cs, n_w=n_w, order=2)
    assert abs(result["total"]["value"] - 1.0) <= tol


def test_api_shape_and_uncertainties_present() -> None:
    result = cl_spectrum(k_cs=74, n_w=5, order=2)
    assert set(result.keys()) == {"inputs", "leading", "subleading", "total"}
    assert "uncertainty" in result["leading"]
    assert "order_1" in result["subleading"]
    assert "order_2" in result["subleading"]
    assert "uncertainty" in result["subleading"]["order_1"]
    assert "uncertainty" in result["subleading"]["order_2"]
    assert "uncertainty" in result["total"]


def test_invalid_order_raises() -> None:
    with pytest.raises(ValueError):
        cl_spectrum(k_cs=74, n_w=5, order=1)
