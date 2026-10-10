# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch — Phase 2 of article-354 direction #2.

Wraps `pipeline.py` for live HTTP access. No real pump-probe dataset is
bundled; `/api/demo-comparison` builds synthetic frames from the prediction
curve itself as a self-consistency smoke test, not as evidence of anything.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping

from ._repo import ensure_repo_on_path

ensure_repo_on_path()

from src.materials.polariton_vortex import C_S_CANONICAL, critical_angle_deg  # noqa: E402

from .pipeline import (
    PumpProbeFrame,
    compare_to_prediction,
    extract_feature_velocity_curve,
    vortex_speed_ratio,
)

API_ENDPOINTS = ("/api/status", "/api/prediction", "/api/demo-comparison")


def _first(query: Mapping[str, List[str]], key: str, default: str | None = None) -> str | None:
    values = query.get(key)
    return values[0] if values else default


def _synthetic_frames(c_s: float, angles: List[float]) -> List[PumpProbeFrame]:
    """Two frames per angle, built exactly on the prediction curve itself."""
    frames: List[PumpProbeFrame] = []
    for angle in angles:
        v_over_c = vortex_speed_ratio(math.radians(angle), c_s=c_s)
        v_um_per_fs = v_over_c * 0.299792458
        frames.append(PumpProbeFrame(position_um=0.0, timestamp_fs=0.0, half_angle_deg=angle))
        frames.append(PumpProbeFrame(position_um=v_um_per_fs * 10.0, timestamp_fs=10.0, half_angle_deg=angle))
    return frames


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {"product": "AZ Polariton Vortex Analyzer", "endpoints": list(API_ENDPOINTS)}

    if path == "/api/prediction":
        c_s = float(_first(query, "c_s", str(C_S_CANONICAL)))
        return {"c_s": c_s, "predicted_critical_angle_deg": critical_angle_deg(c_s=c_s)}

    if path == "/api/demo-comparison":
        c_s = float(_first(query, "c_s", str(C_S_CANONICAL)))
        angles = [5.0, 10.0, 15.0, 18.93, 25.0, 35.0]
        frames = _synthetic_frames(c_s, angles)
        measured = extract_feature_velocity_curve(frames)
        result = compare_to_prediction(measured, c_s=c_s)
        result["note"] = "synthetic self-consistency demo, not a real experimental dataset"
        return result

    raise KeyError(f"unknown API endpoint: {path}")
