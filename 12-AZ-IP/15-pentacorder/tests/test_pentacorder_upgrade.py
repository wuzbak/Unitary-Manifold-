# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Upgrade tests for the Unitary Pentacorder app."""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pentacorder.engine.convergence_display import format_5d_display, get_alert_level
from pentacorder.engine.sensor_fusion_5d import (
    SENSOR_DIMENSIONS,
    compute_convergence_index,
    fuse_sensor_readings,
    get_lean4_proof_suggestion,
)


def test_sensor_dimensions_exact_mapping():
    assert SENSOR_DIMENSIONS == {
        "accelerometer": "dim_1_x",
        "magnetometer": "dim_2_y",
        "barometer": "dim_3_z",
        "gps": "dim_4_t",
        "microphone": "dim_5_compact",
    }


def test_fuse_sensor_readings_builds_state_vector():
    state = fuse_sensor_readings((1.0, 2.0, 3.0), (30.0, 0.0, 40.0), 1013.25, (47.6, -122.3, 12.0), 0.2)
    assert len(state["state_vector"]) == 5
    assert set(state["dimensions"]) == {"dim_1_x", "dim_2_y", "dim_3_z", "dim_4_t", "dim_5_compact"}


def test_fuse_sensor_readings_clamps_large_values():
    state = fuse_sensor_readings((100.0, 0.0, 0.0), (200.0, 0.0, 0.0), 5000.0, (0.0, 0.0, 999.0), 2.5)
    assert state["dimensions"]["dim_1_x"] == 1.0
    assert state["dimensions"]["dim_2_y"] == 1.0
    assert state["dimensions"]["dim_3_z"] == 1.0
    assert state["dimensions"]["dim_4_t"] == 0.0
    assert state["dimensions"]["dim_5_compact"] == 1.0


def test_fuse_sensor_readings_contains_metrics():
    state = fuse_sensor_readings((0.0, 0.0, 9.8), (25.0, 0.0, 0.0), 1000.0, (0.0, 0.0, 0.0), 0.1)
    assert set(state["metrics"]) == {"motion_stability", "field_alignment", "environmental_coherence", "location_stability"}


def test_compute_convergence_index_in_range():
    state = fuse_sensor_readings((1.0, 1.0, 1.0), (20.0, 20.0, 10.0), 1012.0, (0.0, 0.0, 5.0), 0.2)
    ci = compute_convergence_index(state)
    assert 0.0 <= ci <= 1.0


def test_compute_convergence_index_custom_weights():
    state = fuse_sensor_readings((0.1, 0.1, 0.1), (30.0, 40.0, 0.0), 1013.25, (0.0, 0.0, 1.0), 0.0)
    ci = compute_convergence_index(state, weights=(0.2, 0.5, 0.3))
    assert ci > 0.5


def test_compute_convergence_index_rejects_bad_weights():
    with pytest.raises(ValueError):
        compute_convergence_index({}, weights=(1.0, 0.0))


def test_compute_convergence_index_can_derive_from_dimensions_only():
    ci = compute_convergence_index({"dimensions": {"dim_1_x": 0.2, "dim_2_y": 0.5, "dim_3_z": 0.9, "dim_4_t": 0.8, "dim_5_compact": 0.1}})
    assert 0.0 <= ci <= 1.0


def test_get_lean4_proof_suggestion_for_magnetometer():
    suggestion = get_lean4_proof_suggestion("magnetometer drift")
    assert suggestion["theorem_file"].endswith("MagnetometerAlignment.lean")


def test_get_lean4_proof_suggestion_for_gps():
    suggestion = get_lean4_proof_suggestion("gps route")
    assert suggestion["theorem_name"] == "gps_fix_implies_geodesic_stability"


def test_get_lean4_proof_suggestion_for_barometer():
    suggestion = get_lean4_proof_suggestion("pressure anomaly")
    assert suggestion["theorem_file"].endswith("PressureCompactification.lean")


def test_get_lean4_proof_suggestion_default_case():
    suggestion = get_lean4_proof_suggestion("mixed sensor")
    assert suggestion["theorem_file"].endswith("SensorFusion5D.lean")


def test_format_5d_display_contains_all_dimensions():
    state = fuse_sensor_readings((1.0, 2.0, 3.0), (30.0, 0.0, 40.0), 1013.25, (47.6, -122.3, 12.0), 0.2)
    display = format_5d_display(state, 0.75)
    for label in ("dim_1_x", "dim_2_y", "dim_3_z", "dim_4_t", "dim_5_compact", "CI", "Alert"):
        assert label in display


@pytest.mark.parametrize(
    ("ci", "level"),
    [(0.85, "NOMINAL"), (0.7, "ELEVATED"), (0.5, "ALERT"), (0.2, "CRITICAL")],
)
def test_get_alert_level_thresholds(ci, level):
    assert get_alert_level(ci) == level


def test_display_alert_level_matches_threshold():
    state = {"dimensions": {"dim_1_x": 0.1, "dim_2_y": 0.2, "dim_3_z": 0.3, "dim_4_t": 0.4, "dim_5_compact": 0.5}}
    display = format_5d_display(state, 0.2)
    assert "CRITICAL" in display
