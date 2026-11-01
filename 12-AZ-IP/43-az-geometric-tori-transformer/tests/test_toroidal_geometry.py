# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Toroidal lattice invariants, and a cross-check against the Navigator's golden vectors."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from az_tori_transformer.toroidal_geometry import (
    BRAID_WINDINGS,
    HALF_TURN,
    K_CS,
    LATTICE_ORDER,
    braid_bank,
    circular_distance,
    orbifold_fold,
    orbit_period,
    position_bank,
    position_code,
    wrap,
)


def test_lattice_order_is_sum_of_braid_squares() -> None:
    assert K_CS == BRAID_WINDINGS[0] ** 2 + BRAID_WINDINGS[1] ** 2 == 74
    assert LATTICE_ORDER == 74
    assert HALF_TURN == 37


@pytest.mark.parametrize("a,b", [(0, 0), (5, 68), (37, 37), (73, 1), (10, 60)])
def test_circular_distance_bounds(a: int, b: int) -> None:
    d = circular_distance(a, b)
    assert 0 <= d <= HALF_TURN
    assert d == circular_distance(b, a)


def test_circular_distance_is_symmetric_and_zero_on_diagonal() -> None:
    for i in range(LATTICE_ORDER):
        assert circular_distance(i, i) == 0


def test_orbifold_fold_fixed_points() -> None:
    assert orbifold_fold(0) == 0
    assert orbifold_fold(37) == 37
    assert orbifold_fold(74) == 0  # wraps first


def test_orbifold_fold_is_the_circular_distance_to_zero() -> None:
    for i in range(LATTICE_ORDER):
        assert orbifold_fold(i) == circular_distance(i, 0)


def test_braid_bank_requires_two_coordinates() -> None:
    with pytest.raises(ValueError):
        braid_bank((1,))


def test_braid_bank_of_pure_braid_winding_code_collapses_to_zero() -> None:
    """Documents the degenerate case ``position_code`` deliberately avoids:

    5**2 + 7**2 == 74 == 0 (mod 74), so a code built purely from the (5, 7)
    braid windings has a constant bank address. ``position_code`` uses the
    independent tick-phase winding for the second coordinate instead.
    """
    for i in range(10):
        code = (wrap(5 * i), wrap(7 * i))
        assert braid_bank(code) == 0


def test_position_code_is_non_degenerate() -> None:
    banks = {position_bank(i) for i in range(LATTICE_ORDER)}
    assert len(banks) > 1


def test_orbit_period_divides_lattice_order() -> None:
    for step in range(LATTICE_ORDER):
        period = orbit_period(step)
        assert LATTICE_ORDER % period == 0


def test_wrap_is_idempotent_and_bounded() -> None:
    for i in [-100, -1, 0, 73, 74, 148, 1000]:
        w = wrap(i)
        assert 0 <= w < LATTICE_ORDER
        assert wrap(w) == w


def test_cross_check_against_navigator_golden_vectors() -> None:
    """When the sibling Navigator product is importable, this product's local
    Z_74 arithmetic must agree with its golden-vector export exactly, so the
    two copies of the same specification never silently drift apart."""
    repo_root = Path(__file__).resolve().parents[3]
    navigator_root = repo_root / "12-AZ-IP" / "20-psicat-navigator"
    if not navigator_root.is_dir():
        pytest.skip("sibling Navigator product not present in this checkout")
    sys.path.insert(0, str(repo_root))  # navigator engine imports top-level `src.*`
    sys.path.insert(0, str(navigator_root))
    try:
        from ox_navigator.engine.merlin_toroidal_geometry import export_golden_vectors
    except ImportError:
        pytest.skip("Navigator engine package is not importable in this environment")

    golden = export_golden_vectors()
    for a, b, expected in golden["vectors"]["PHDIST"]:
        assert circular_distance(a, b) == expected
    for a, expected in golden["vectors"]["PHFOLD"]:
        assert orbifold_fold(a) == expected
    for a, b, expected in golden["vectors"]["BANK"]:
        assert braid_bank((a, b)) == expected
