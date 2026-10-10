# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Feature-velocity extraction and comparison pipeline.

Takes a sequence of pump-probe frames (intensity, timestamp, wavefront
half-angle metadata) and extracts the measured feature velocity as a
function of half-angle, in the same v/c units that
`src/materials/polariton_vortex.py` uses for its prediction curve, then
compares the two curves.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence

from ._repo import ensure_repo_on_path

ensure_repo_on_path()

from src.materials.polariton_vortex import (  # noqa: E402
    C_S_CANONICAL,
    critical_angle_deg,
    vortex_speed_ratio,
)


@dataclass(frozen=True)
class PumpProbeFrame:
    """One captured pump-probe frame.

    position_um : position of the tracked feature (vortex crossing point)
        along the propagation axis, in micrometres.
    timestamp_fs : capture time, in femtoseconds.
    half_angle_deg : wavefront half-angle at which this frame was captured.
    """

    position_um: float
    timestamp_fs: float
    half_angle_deg: float


@dataclass(frozen=True)
class FeatureVelocityCurve:
    """Measured feature velocity (v/c) as a function of half-angle."""

    half_angles_deg: List[float]
    v_over_c: List[float]


_C_UM_PER_FS = 0.299792458  # speed of light in micrometres / femtosecond


def extract_feature_velocity_curve(frames: Sequence[PumpProbeFrame]) -> FeatureVelocityCurve:
    """Group frames by half-angle and compute the feature velocity (v/c) at
    each angle via a finite-difference slope of position vs. time.

    Requires at least two frames per distinct half-angle to compute a slope.
    """
    if len(frames) < 2:
        raise ValueError("at least two frames are required to extract a velocity")

    by_angle: dict[float, list[PumpProbeFrame]] = {}
    for frame in frames:
        by_angle.setdefault(round(frame.half_angle_deg, 6), []).append(frame)

    angles: List[float] = []
    speeds: List[float] = []
    for angle, group in sorted(by_angle.items()):
        if len(group) < 2:
            continue
        group = sorted(group, key=lambda f: f.timestamp_fs)
        t0, t1 = group[0].timestamp_fs, group[-1].timestamp_fs
        x0, x1 = group[0].position_um, group[-1].position_um
        dt = t1 - t0
        if dt <= 0:
            continue
        v_um_per_fs = (x1 - x0) / dt
        angles.append(angle)
        speeds.append(v_um_per_fs / _C_UM_PER_FS)

    if not angles:
        raise ValueError("no half-angle group had >= 2 time-ordered frames")

    return FeatureVelocityCurve(half_angles_deg=angles, v_over_c=speeds)


def compare_to_prediction(
    measured: FeatureVelocityCurve,
    c_s: float = C_S_CANONICAL,
) -> dict:
    """Compare a measured feature-velocity curve to the braided-winding
    prediction from `polariton_vortex.vortex_speed_ratio`, angle by angle.

    Returns residuals and whether the measured crossing point (v/c = 1) falls
    inside, outside, or exactly at the predicted critical half-angle.
    """
    predicted = [
        vortex_speed_ratio(math.radians(angle), c_s=c_s) for angle in measured.half_angles_deg
    ]
    residuals = [m - p for m, p in zip(measured.v_over_c, predicted)]
    theta_c_deg = critical_angle_deg(c_s=c_s)

    crossing_deg = None
    for i in range(len(measured.v_over_c) - 1):
        v0, v1 = measured.v_over_c[i], measured.v_over_c[i + 1]
        if (v0 - 1.0) * (v1 - 1.0) <= 0 and v1 != v0:
            a0, a1 = measured.half_angles_deg[i], measured.half_angles_deg[i + 1]
            frac = (1.0 - v0) / (v1 - v0)
            crossing_deg = a0 + frac * (a1 - a0)
            break

    return {
        "predicted_v_over_c": predicted,
        "residuals": residuals,
        "max_abs_residual": max(abs(r) for r in residuals),
        "predicted_critical_angle_deg": theta_c_deg,
        "measured_crossing_angle_deg": crossing_deg,
    }
