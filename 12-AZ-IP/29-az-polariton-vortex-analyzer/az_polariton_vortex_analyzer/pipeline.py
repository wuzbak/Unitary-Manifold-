# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Feature-velocity extraction and comparison pipeline.

Takes a sequence of tracked pump-probe features (position, timestamp, wavefront
half-angle metadata) and extracts the measured feature velocity as a
function of half-angle, in the same v/c units that
`src/materials/polariton_vortex.py` uses for its prediction curve, then
compares the two curves.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
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
    fit_diagnostics: list[dict] = field(default_factory=list)


_C_UM_PER_FS = 0.299792458  # speed of light in micrometres / femtosecond


def finite_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


def validate_c_s(c_s: float) -> float:
    c_s = finite_number(c_s, "c_s")
    if not 0 < c_s < 1:
        raise ValueError("c_s must be strictly between 0 and 1")
    return c_s


def extract_feature_velocity_curve(frames: Sequence[PumpProbeFrame]) -> FeatureVelocityCurve:
    """Group frames by half-angle and compute the feature velocity (v/c) at
    each angle via an ordinary least-squares fit of position vs. time.

    Uses every sample, preserving signed velocity. Requires at least two
    distinct timestamps per exact half-angle; invalid groups are never dropped.
    """
    if len(frames) < 2:
        raise ValueError("at least two frames are required to extract a velocity")

    by_angle: dict[float, list[PumpProbeFrame]] = {}
    for index, frame in enumerate(frames):
        position = finite_number(frame.position_um, f"frame {index + 1} position_um")
        timestamp = finite_number(frame.timestamp_fs, f"frame {index + 1} timestamp_fs")
        angle = finite_number(frame.half_angle_deg, f"frame {index + 1} half_angle_deg")
        if not 0 < angle < 90:
            raise ValueError(f"frame {index + 1} half_angle_deg must be between 0 and 90 (exclusive)")
        by_angle.setdefault(angle, []).append(PumpProbeFrame(position, timestamp, angle))

    angles: List[float] = []
    speeds: List[float] = []
    diagnostics: list[dict] = []
    for angle, group in sorted(by_angle.items()):
        if len(group) < 2:
            raise ValueError(f"half-angle {angle} requires at least two frames")
        group = sorted(group, key=lambda f: f.timestamp_fs)
        if len({f.timestamp_fs for f in group}) != len(group):
            raise ValueError(f"half-angle {angle} has duplicate timestamps")
        t0, t1 = group[0].timestamp_fs, group[-1].timestamp_fs
        dt = t1 - t0
        try:
            # Normalize time to avoid squaring very small or very large delays.
            times = [(f.timestamp_fs - t0) / dt for f in group]
            positions = [f.position_um - group[0].position_um for f in group]
            mean_t = math.fsum(times) / len(group)
            mean_x = math.fsum(positions) / len(group)
            centered_t = [t - mean_t for t in times]
            s_tt = math.fsum(t * t for t in centered_t)
            slope = math.fsum(t * (x - mean_x) for t, x in zip(centered_t, positions)) / s_tt
            v_um_per_fs = slope / dt
            residuals = [x - mean_x - slope * t for t, x in zip(centered_t, positions)]
            rmse = math.hypot(*residuals) / math.sqrt(len(group))
            speed = v_um_per_fs / _C_UM_PER_FS
            if not all(math.isfinite(v) for v in (dt, speed, rmse)):
                raise ValueError("nonfinite derived feature")
        except (OverflowError, ZeroDivisionError, ValueError) as exc:
            raise ValueError(f"half-angle {angle} has an unrepresentable fit; check units/range") from exc
        angles.append(angle)
        speeds.append(speed)
        diagnostics.append({
            "half_angle_deg": angle,
            "frame_count": len(group),
            "time_span_fs": dt,
            "position_fit_rmse_um": rmse,
        })

    return FeatureVelocityCurve(half_angles_deg=angles, v_over_c=speeds, fit_diagnostics=diagnostics)


def compare_to_prediction(
    measured: FeatureVelocityCurve,
    c_s: float = C_S_CANONICAL,
) -> dict:
    """Compare a measured feature-velocity curve to the braided-winding
    prediction from `polariton_vortex.vortex_speed_ratio`, angle by angle.

    Returns descriptive residuals and interpolated crossings of v/c = 1.
    Neither agreement nor disagreement establishes a hardgate physics claim.
    """
    c_s = validate_c_s(c_s)
    if not measured.half_angles_deg or len(measured.half_angles_deg) != len(measured.v_over_c):
        raise ValueError("measured curve must have equal, nonempty angle and velocity lists")
    angles = [finite_number(a, "half_angle_deg") for a in measured.half_angles_deg]
    speeds = [finite_number(v, "v_over_c") for v in measured.v_over_c]
    if any(not 0 < a < 90 for a in angles) or any(a >= b for a, b in zip(angles, angles[1:])):
        raise ValueError("curve half-angles must be unique, increasing and between 0 and 90")
    try:
        predicted = [
            vortex_speed_ratio(math.radians(angle), c_s=c_s) for angle in angles
        ]
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("prediction is not representable; check half-angle range") from exc
    residuals = [m - p for m, p in zip(speeds, predicted)]
    if not all(math.isfinite(v) for v in predicted + residuals):
        raise ValueError("comparison is not finite; check angle/velocity range")
    theta_c_deg = critical_angle_deg(c_s=c_s)

    crossings = []
    for i, (angle, speed) in enumerate(zip(angles, speeds)):
        if speed == 1.0:
            crossings.append(angle)
        if i + 1 < len(speeds) and (speed < 1 < speeds[i + 1] or speed > 1 > speeds[i + 1]):
            v0, v1 = speed, speeds[i + 1]
            a0, a1 = angle, angles[i + 1]
            velocity_scale = max(abs(v0), abs(v1), 1.0)
            frac = ((1.0 - v0) / velocity_scale) / (v1 / velocity_scale - v0 / velocity_scale)
            crossings.append(a0 + frac * (a1 - a0))
    crossing_deg = crossings[0] if crossings else None
    scale = max(abs(r) for r in residuals)
    rmse = scale * math.sqrt(math.fsum((r / scale) ** 2 for r in residuals) / len(residuals)) if scale else 0.0

    return {
        "predicted_v_over_c": predicted,
        "residuals": residuals,
        "max_abs_residual": scale,
        "mean_abs_residual": math.fsum(abs(r) / len(residuals) for r in residuals),
        "rmse_v_over_c": rmse,
        "predicted_critical_angle_deg": theta_c_deg,
        "measured_crossing_angle_deg": crossing_deg,
        "measured_crossing_angles_deg": crossings,
        "crossing_status": "not_bracketed" if not crossings else "multiple" if len(crossings) > 1 else "single",
    }
