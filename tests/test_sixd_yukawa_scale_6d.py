# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for 6D Yukawa scale bridge: src/sixd/yukawa_scale_6d.py"""

from __future__ import annotations

import pytest

from src.sixd.yukawa_scale_6d import (
    BOTTOM_YUKAWA_SM,
    DEFAULT_C_R,
    DEFAULT_G5,
    ELECTRON_YUKAWA_SM,
    TAU_YUKAWA_SM,
    TOP_YUKAWA_SM,
    TOP_YUKAWA_TOLERANCE,
    YUKAWA_HARDGATE_TOLERANCE,
    diagonal_yukawa_spectrum,
    fixed_point_overlap,
    parameter_gate_status,
    tier4_yukawa_hardgate_v1028,
    top_yukawa_kill_switch,
    yukawa_entry,
    yukawa_scale_bridge_summary,
    zero_mode_profile_amplitude,
)


def test_profile_amplitude_is_one_below_half():
    assert zero_mode_profile_amplitude(0.49) == pytest.approx(1.0)


def test_profile_amplitude_decays_above_half():
    assert zero_mode_profile_amplitude(0.70) < 1.0


def test_fixed_point_overlap_diagonal_dominates_off_diagonal():
    assert fixed_point_overlap(0, 0) > fixed_point_overlap(0, 1)


def test_yukawa_entry_positive():
    assert yukawa_entry(0, 0, g5=DEFAULT_G5, c_r=DEFAULT_C_R) > 0.0


def test_diagonal_spectrum_hierarchical():
    spec = diagonal_yukawa_spectrum()
    assert spec["hierarchy"] is True


def test_top_kill_switch_within_50_percent():
    ks = top_yukawa_kill_switch()
    assert ks["pass"] is True
    assert ks["residual"] <= TOP_YUKAWA_TOLERANCE


def test_parameter_gate_status_mapping():
    assert parameter_gate_status(0.25) == "CONSTRAINED"
    assert parameter_gate_status(0.75) == "FITTED"


def test_bridge_summary_promotes_p6_family_to_constrained():
    summary = yukawa_scale_bridge_summary()
    updates = summary["parameter_gate_updates"]
    assert updates["P6"] == "CONSTRAINED"
    assert updates["P7"] == "CONSTRAINED"
    assert updates["P8"] == "CONSTRAINED"
    assert updates["P16"] == "CONSTRAINED"


def test_top_reference_constant_positive():
    assert TOP_YUKAWA_SM > 0.0


def test_reference_constants_positive():
    assert BOTTOM_YUKAWA_SM > 0.0
    assert TAU_YUKAWA_SM > 0.0
    assert ELECTRON_YUKAWA_SM > 0.0


def test_tier4_hardgate_promotes_all_p7_to_p10():
    report = tier4_yukawa_hardgate_v1028()
    assert report["all_gates_pass"] is True
    assert report["gates"]["axiomzero_purity"] is True
    assert set(report["promoted_parameters"]) == {"P7", "P8", "P9", "P10"}
    assert report["constrained_parameters"] == []


def test_tier4_hardgate_residuals_lt_5pct():
    report = tier4_yukawa_hardgate_v1028()
    for pid in ("P7", "P8", "P9", "P10"):
        row = report["parameters"][pid]
        assert row["nominal_residual_lt_5pct"] is True
        assert row["residual_pct"] < YUKAWA_HARDGATE_TOLERANCE * 100.0
        assert row["status"] == "GEOMETRIC_PREDICTION"


def test_tier4_hardgate_toe_delta():
    report = tier4_yukawa_hardgate_v1028()
    expected_delta = 0.3 * len(report["promoted_parameters"])
    assert report["toe_delta"] == pytest.approx(expected_delta, abs=1e-12)
    assert report["toe_score_after"] == pytest.approx(
        report["toe_score_before"] + report["toe_delta"],
        abs=1e-12,
    )
