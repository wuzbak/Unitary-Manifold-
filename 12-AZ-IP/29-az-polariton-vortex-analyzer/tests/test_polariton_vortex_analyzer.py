# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import math
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_polariton_vortex_analyzer import (
    PumpProbeFrame,
    extract_feature_velocity_curve,
    compare_to_prediction,
)
from az_polariton_vortex_analyzer.pipeline import _C_UM_PER_FS


def _synthetic_frames_matching_prediction():
    """Build synthetic frames whose finite-difference velocity exactly
    reproduces polariton_vortex.vortex_speed_ratio at each angle — the
    sanity check that the extraction math is self-consistent."""
    from az_polariton_vortex_analyzer._repo import ensure_repo_on_path

    ensure_repo_on_path()
    from src.materials.polariton_vortex import vortex_speed_ratio

    frames = []
    for angle_deg in [5.0, 10.0, 15.0, 18.93, 25.0]:
        v_over_c = vortex_speed_ratio(math.radians(angle_deg))
        v_um_per_fs = v_over_c * _C_UM_PER_FS
        frames.append(PumpProbeFrame(position_um=0.0, timestamp_fs=0.0, half_angle_deg=angle_deg))
        frames.append(
            PumpProbeFrame(position_um=v_um_per_fs * 10.0, timestamp_fs=10.0, half_angle_deg=angle_deg)
        )
    return frames


def test_extract_feature_velocity_curve_requires_two_frames():
    with pytest.raises(ValueError):
        extract_feature_velocity_curve([PumpProbeFrame(0.0, 0.0, 10.0)])


def test_extract_feature_velocity_curve_basic_slope():
    frames = [
        PumpProbeFrame(position_um=0.0, timestamp_fs=0.0, half_angle_deg=10.0),
        PumpProbeFrame(position_um=2.0, timestamp_fs=1.0, half_angle_deg=10.0),
    ]
    curve = extract_feature_velocity_curve(frames)
    assert curve.half_angles_deg == [10.0]
    assert curve.v_over_c[0] == pytest.approx(2.0 / _C_UM_PER_FS)


def test_compare_to_prediction_zero_residual_for_self_consistent_data():
    frames = _synthetic_frames_matching_prediction()
    curve = extract_feature_velocity_curve(frames)
    result = compare_to_prediction(curve)
    assert result["max_abs_residual"] < 1e-9
    assert result["predicted_critical_angle_deg"] == pytest.approx(18.924644416051237)


def test_compare_to_prediction_finds_crossing_angle_near_theta_c():
    frames = _synthetic_frames_matching_prediction()
    curve = extract_feature_velocity_curve(frames)
    result = compare_to_prediction(curve)
    assert result["measured_crossing_angle_deg"] == pytest.approx(18.93, abs=0.5)


def test_extract_feature_velocity_curve_ignores_single_sample_angles():
    frames = [
        PumpProbeFrame(position_um=0.0, timestamp_fs=0.0, half_angle_deg=5.0),
        PumpProbeFrame(position_um=0.0, timestamp_fs=0.0, half_angle_deg=10.0),
        PumpProbeFrame(position_um=1.0, timestamp_fs=1.0, half_angle_deg=10.0),
    ]
    curve = extract_feature_velocity_curve(frames)
    assert curve.half_angles_deg == [10.0]
