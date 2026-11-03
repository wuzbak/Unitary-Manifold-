# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Properties of the toroidal rotary encoding and the relative-bias index matrix."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from az_tori_transformer.positional import (
    rotation_orbit_periods,
    rotation_steps_for_dim,
    modular_alias_diagnostics,
    modular_alias_diagnostics,
    toroidal_relative_bias_indices,
    toroidal_rotation_table,
)
from az_tori_transformer.toroidal_geometry import HALF_TURN, LATTICE_ORDER


def test_rotation_steps_require_even_head_dim() -> None:
    with pytest.raises(ValueError):
        rotation_steps_for_dim(7)


def test_rotation_table_is_periodic_with_orbit_period() -> None:
    head_dim = 8
    periods = rotation_orbit_periods(head_dim)
    max_period = int(periods.max())
    cos, sin = toroidal_rotation_table(seq_len=2 * max_period, head_dim=head_dim)
    for k, period in enumerate(periods):
        assert np.allclose(cos[0, k], cos[period, k])
        assert np.allclose(sin[0, k], sin[period, k])


def test_rotation_table_unit_norm() -> None:
    cos, sin = toroidal_rotation_table(seq_len=20, head_dim=6)
    norm_sq = cos ** 2 + sin ** 2
    assert np.allclose(norm_sq, 1.0, atol=1e-10)


def test_rotation_preserves_relative_dot_product() -> None:
    """The RoPE invariant: rotating q at i and k at j by the same per-pair
    angle leaves ``q'_i . k'_j`` a function of ``i - j`` only (mod period)."""
    rng = np.random.default_rng(0)
    head_dim = 8
    seq_len = 12
    cos, sin = toroidal_rotation_table(seq_len, head_dim)

    def rotate(vec: np.ndarray, pos: int) -> np.ndarray:
        even, odd = vec[0::2], vec[1::2]
        c, s = cos[pos], sin[pos]
        out = np.empty_like(vec)
        out[0::2] = even * c - odd * s
        out[1::2] = even * s + odd * c
        return out

    q = rng.normal(size=head_dim)
    k = rng.normal(size=head_dim)
    dot_a = rotate(q, 2) @ rotate(k, 5)
    dot_b = rotate(q, 7) @ rotate(k, 10)  # both pairs share relative offset +3
    assert np.isclose(dot_a, dot_b, atol=1e-8)


def test_relative_bias_indices_shape_and_range() -> None:
    seq_len = 10
    idx = toroidal_relative_bias_indices(seq_len)
    assert idx.shape == (seq_len, seq_len)
    assert idx.min() >= 0
    assert idx.max() <= HALF_TURN


def test_relative_bias_indices_symmetric_and_zero_diagonal() -> None:
    seq_len = 9
    idx = toroidal_relative_bias_indices(seq_len)
    assert np.array_equal(idx, idx.T)
    assert np.all(np.diag(idx) == 0)


def test_relative_bias_allows_distant_positions_to_be_geometrically_close() -> None:
    """The namesake property: two positions far apart in raw sequence index
    can still land on a small circular-distance bucket via the bank map."""
    seq_len = LATTICE_ORDER
    idx = toroidal_relative_bias_indices(seq_len)
    far_apart_pairs = [(i, j) for i in range(seq_len) for j in range(seq_len) if abs(i - j) > seq_len // 2]
    assert any(idx[i, j] <= 2 for i, j in far_apart_pairs)


def test_modular_alias_diagnostics_report_phase_and_projection_collisions() -> None:
    report = modular_alias_diagnostics(seq_len=80, head_dim=8)
    assert [pair["orbit_period"] for pair in report["rotation_pairs"]] == [74, 37, 74, 37]
    assert report["rotation_pairs"][0]["first_collision_positions"] == [0, 74]
    assert report["rotation_pairs"][1]["first_collision_positions"] == [0, 37]
    code = report["two_coordinate_torus_code"]
    bank = report["scalar_bank_projection"]
    assert code["unique_values"] == bank["unique_values"] == 74
    assert code["first_collision_positions"] == bank["first_collision_positions"] == [0, 74]
    assert (bank["source_coordinate_count"], bank["output_coordinate_count"]) == (2, 1)


@pytest.mark.parametrize(("seq_len", "head_dim"), [(0, 8), (10, 7), (10, 0)])
def test_modular_alias_diagnostics_validate_inputs(seq_len: int, head_dim: int) -> None:
    with pytest.raises(ValueError):
        modular_alias_diagnostics(seq_len, head_dim)


def test_modular_alias_diagnostics_report_phase_and_projection_collisions() -> None:
    report = modular_alias_diagnostics(seq_len=80, head_dim=8)
    assert [pair["orbit_period"] for pair in report["rotation_pairs"]] == [74, 37, 74, 37]
    assert report["rotation_pairs"][0]["first_collision_positions"] == [0, 74]
    assert report["rotation_pairs"][1]["first_collision_positions"] == [0, 37]
    code = report["two_coordinate_torus_code"]
    bank = report["scalar_bank_projection"]
    assert code["unique_values"] == bank["unique_values"] == 74
    assert code["first_collision_positions"] == bank["first_collision_positions"] == [0, 74]
    assert (bank["source_coordinate_count"], bank["output_coordinate_count"]) == (2, 1)


@pytest.mark.parametrize(("seq_len", "head_dim"), [(0, 8), (10, 7), (10, 0)])
def test_modular_alias_diagnostics_validate_inputs(seq_len: int, head_dim: int) -> None:
    with pytest.raises(ValueError):
        modular_alias_diagnostics(seq_len, head_dim)
