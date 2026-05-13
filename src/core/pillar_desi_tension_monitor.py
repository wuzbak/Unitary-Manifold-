# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""DESI tension monitor for the exact KK dark-energy prediction (w0=-1, wa=0)."""

from __future__ import annotations

import math
from typing import Dict

KK_W0_PREDICTION: float = -1.0
KK_WA_PREDICTION: float = 0.0

DESI_BASELINE_OBS: Dict[str, float] = {
    "w0_obs": -0.90,
    "w0_sigma": 0.055,
    "wa_obs": -0.55,
    "wa_sigma": 0.20,
}


def _validate_sigmas(w0_sigma: float, wa_sigma: float) -> None:
    if w0_sigma <= 0 or wa_sigma <= 0:
        raise ValueError("w0_sigma and wa_sigma must be strictly positive.")


def desi_tension_sigma(
    w0_obs: float,
    w0_sigma: float,
    wa_obs: float,
    wa_sigma: float,
) -> float:
    _validate_sigmas(w0_sigma, wa_sigma)
    z_w0 = (w0_obs - KK_W0_PREDICTION) / w0_sigma
    z_wa = (wa_obs - KK_WA_PREDICTION) / wa_sigma
    return math.sqrt(z_w0 * z_w0 + z_wa * z_wa)


def tension_flag(tension_sigma: float) -> str:
    if tension_sigma > 3.0:
        return "CRITICAL"
    if tension_sigma > 2.0:
        return "WARNING"
    return "PASS"


def observation_window(
    w0_obs: float,
    w0_sigma: float,
    wa_obs: float,
    wa_sigma: float,
) -> Dict[str, tuple[float, float]]:
    _validate_sigmas(w0_sigma, wa_sigma)
    return {
        "w0_1sigma": (w0_obs - w0_sigma, w0_obs + w0_sigma),
        "wa_1sigma": (wa_obs - wa_sigma, wa_obs + wa_sigma),
        "w0_2sigma": (w0_obs - 2.0 * w0_sigma, w0_obs + 2.0 * w0_sigma),
        "wa_2sigma": (wa_obs - 2.0 * wa_sigma, wa_obs + 2.0 * wa_sigma),
    }


def monitor_desi_tension(
    w0_obs: float = DESI_BASELINE_OBS["w0_obs"],
    w0_sigma: float = DESI_BASELINE_OBS["w0_sigma"],
    wa_obs: float = DESI_BASELINE_OBS["wa_obs"],
    wa_sigma: float = DESI_BASELINE_OBS["wa_sigma"],
) -> Dict[str, object]:
    sigma = desi_tension_sigma(w0_obs=w0_obs, w0_sigma=w0_sigma, wa_obs=wa_obs, wa_sigma=wa_sigma)
    return {
        "kk_prediction": {"w0": KK_W0_PREDICTION, "wa": KK_WA_PREDICTION},
        "observation": {
            "w0_obs": w0_obs,
            "w0_sigma": w0_sigma,
            "wa_obs": wa_obs,
            "wa_sigma": wa_sigma,
        },
        "window": observation_window(w0_obs=w0_obs, w0_sigma=w0_sigma, wa_obs=wa_obs, wa_sigma=wa_sigma),
        "desi_tension_sigma": sigma,
        "flag": tension_flag(sigma),
        "update_ready": True,
    }


def updated_monitor_from_payload(payload: Dict[str, float]) -> Dict[str, object]:
    required = ("w0_obs", "w0_sigma", "wa_obs", "wa_sigma")
    missing = [k for k in required if k not in payload]
    if missing:
        raise ValueError(f"Missing required payload fields: {', '.join(missing)}")
    return monitor_desi_tension(
        w0_obs=float(payload["w0_obs"]),
        w0_sigma=float(payload["w0_sigma"]),
        wa_obs=float(payload["wa_obs"]),
        wa_sigma=float(payload["wa_sigma"]),
    )


DESI_TENSION_SIGMA: float = monitor_desi_tension()["desi_tension_sigma"]


__all__ = [
    "KK_W0_PREDICTION",
    "KK_WA_PREDICTION",
    "DESI_BASELINE_OBS",
    "DESI_TENSION_SIGMA",
    "desi_tension_sigma",
    "tension_flag",
    "observation_window",
    "monitor_desi_tension",
    "updated_monitor_from_payload",
]
