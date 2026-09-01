# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""5D sensor fusion helpers for the Unitary Pentacorder."""

from __future__ import annotations

import math

SENSOR_DIMENSIONS = {
    "accelerometer": "dim_1_x",
    "magnetometer": "dim_2_y",
    "barometer": "dim_3_z",
    "gps": "dim_4_t",
    "microphone": "dim_5_compact",
}


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, float(value)))


def _norm3(vector: tuple) -> float:
    return math.sqrt(sum(float(component) ** 2 for component in vector[:3]))


def fuse_sensor_readings(accel: tuple, mag: tuple, baro: float, gps: tuple, mic_level: float) -> dict:
    """Map physical sensor readings into a compact 5D state vector."""
    accel_norm = _norm3(accel)
    mag_norm = _norm3(mag)
    gps_speed = float(gps[2]) if len(gps) >= 3 else 0.0
    dimensions = {
        "dim_1_x": round(_clamp(accel_norm / 20.0), 4),
        "dim_2_y": round(_clamp(mag_norm / 100.0), 4),
        "dim_3_z": round(_clamp(float(baro) / 1100.0), 4),
        "dim_4_t": round(_clamp(1.0 - min(abs(gps_speed) / 100.0, 1.0)), 4),
        "dim_5_compact": round(_clamp(float(mic_level)), 4),
    }
    metrics = {
        "motion_stability": round(_clamp(1.0 - min(accel_norm / 20.0, 1.0)), 4),
        "field_alignment": round(_clamp(1.0 - min(abs(mag_norm - 50.0) / 50.0, 1.0)), 4),
        "environmental_coherence": round(_clamp((1.0 - min(abs(float(baro) - 1013.25) / 100.0, 1.0) + (1.0 - _clamp(float(mic_level)))) / 2.0), 4),
        "location_stability": round(_clamp(1.0 - min(abs(gps_speed) / 50.0, 1.0)), 4),
    }
    return {
        "dimensions": dimensions,
        "state_vector": [dimensions[key] for key in ("dim_1_x", "dim_2_y", "dim_3_z", "dim_4_t", "dim_5_compact")],
        "metrics": metrics,
        "raw_inputs": {
            "accelerometer": accel,
            "magnetometer": mag,
            "barometer": float(baro),
            "gps": gps,
            "microphone": float(mic_level),
        },
    }


def compute_convergence_index(sensor_state: dict, weights: tuple = (0.5, 0.3, 0.2)) -> float:
    """Compute a weighted convergence index from fused sensor state."""
    if len(weights) != 3 or sum(weights) <= 0:
        raise ValueError("weights must be a 3-tuple with positive total weight")
    metrics = sensor_state.get("metrics") or {}
    dimensions = sensor_state.get("dimensions") or {}
    motion = float(metrics.get("motion_stability", 1.0 - float(dimensions.get("dim_1_x", 0.0))))
    field = float(metrics.get("field_alignment", 1.0 - abs(float(dimensions.get("dim_2_y", 0.0)) - 0.5)))
    environment = float(metrics.get("environmental_coherence", (float(dimensions.get("dim_3_z", 0.0)) + (1.0 - float(dimensions.get("dim_5_compact", 0.0)))) / 2.0))
    composite = (
        weights[0] * _clamp((motion + field) / 2.0) +
        weights[1] * _clamp(environment) +
        weights[2] * _clamp(float(metrics.get("location_stability", float(dimensions.get("dim_4_t", 0.0)))))
    ) / sum(weights)
    return round(_clamp(composite), 4)


def get_lean4_proof_suggestion(sensor_pattern: str) -> dict:
    """Suggest a Lean4 theorem stub based on the dominant sensor pattern."""
    pattern = sensor_pattern.lower()
    if "mag" in pattern:
        theorem_file = "Lean4/Pentacorder/MagnetometerAlignment.lean"
        theorem_name = "magnetometer_alignment_preserves_gauge_signal"
    elif "gps" in pattern or "geo" in pattern:
        theorem_file = "Lean4/Pentacorder/GeodesicStability.lean"
        theorem_name = "gps_fix_implies_geodesic_stability"
    elif "baro" in pattern or "pressure" in pattern:
        theorem_file = "Lean4/Pentacorder/PressureCompactification.lean"
        theorem_name = "barometric_shift_bounds_compact_dimension"
    else:
        theorem_file = "Lean4/Pentacorder/SensorFusion5D.lean"
        theorem_name = "sensor_fusion_produces_bounded_state_vector"
    return {
        "sensor_pattern": sensor_pattern,
        "theorem_file": theorem_file,
        "theorem_name": theorem_name,
        "confidence": 0.8,
    }
