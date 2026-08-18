# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 656 — SPHEREx f_NL preregistration lock.

STATUS: SPHEREX_FNL_PREREGISTRATION_LOCKED

Background
----------
This pillar converts the sharpened SPHEREx equilateral non-Gaussianity target
into a live routing lock. The UM+KK target remains centered near f_NL = -1.93,
with the sharpened theory band [-3.0, -1.9] adopted from the preceding
analysis. The verdict compares a live observation band against this locked
interval and returns PASS, TENSION, or FALSIFIED.

References
----------
Pillar 375, Pillar 645, SPHEREx sensitivity notes.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List

__all__ = [
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'PILLAR_TITLE',
    'VERSION',
    'FNL_UM_KK',
    'FNL_BAND_LOW',
    'FNL_BAND_HIGH',
    'FNL_DBI_RAW',
    'SPHEREX_SNR',
    'SHA256_PREREGISTRATION',
    'ADJACENT_TRACK',
    'spherex_verdict',
    'what_is_claimed',
    'what_is_NOT_claimed',
    'pillar_report',
]

PILLAR_NUMBER: int = 656
PILLAR_STATUS: str = 'SPHEREX_FNL_PREREGISTRATION_LOCKED'
PILLAR_TITLE: str = 'SPHEREx f_NL Preregistration Lock'
VERSION: str = 'v21.0'

FNL_UM_KK: float = -1.93
FNL_BAND_LOW: float = -3.0
FNL_BAND_HIGH: float = -1.9
FNL_DBI_RAW: float = -2.76
SPHEREX_SNR: float = 1.2
SHA256_PREREGISTRATION: str = hashlib.sha256(
    b'SPHEREX_FNL_LOCK_v21.0_fnl=-1.93_band=[-3,-1.9]'
).hexdigest()
ADJACENT_TRACK: bool = False


def spherex_verdict(f_nl_obs: float, sigma: float) -> Dict[str, Any]:
    """Return the live verdict for a SPHEREx f_NL measurement."""
    if sigma <= 0.0:
        raise ValueError('sigma must be positive')

    obs_low = f_nl_obs - 2.0 * sigma
    obs_high = f_nl_obs + 2.0 * sigma
    no_overlap = obs_high < FNL_BAND_LOW or obs_low > FNL_BAND_HIGH
    central_in_band = FNL_BAND_LOW <= f_nl_obs <= FNL_BAND_HIGH

    if no_overlap:
        branch = 'FALSIFIED'
        action = 'reject_locked_fnl_band'
    elif central_in_band:
        branch = 'PASS'
        action = 'retain_sharpened_fnl_prediction'
    else:
        branch = 'TENSION'
        action = 'await_joint_shape_cross_check'

    overlap_low = max(obs_low, FNL_BAND_LOW)
    overlap_high = min(obs_high, FNL_BAND_HIGH)
    overlap_width = max(0.0, overlap_high - overlap_low)

    return {
        'branch': branch,
        'f_nl_obs': f_nl_obs,
        'sigma': sigma,
        'obs_low_2sigma': obs_low,
        'obs_high_2sigma': obs_high,
        'overlap_width': overlap_width,
        'action': action,
        'sha256_preregistration': SHA256_PREREGISTRATION,
    }


def what_is_claimed() -> List[str]:
    """Return honest claims for Pillar 656."""
    return [
        'The sharpened SPHEREx band [-3.0, -1.9] is preregistration-locked.',
        'The KK-centered target remains f_NL = -1.93.',
        'PASS, TENSION, and FALSIFIED are decided from 2 sigma interval overlap with the locked band.',
        'The lock is hash-committed with SHA-256.',
        'No ToE score change is claimed without live SPHEREx data.',
    ]


def what_is_NOT_claimed() -> List[str]:
    """Return honest non-claims for Pillar 656."""
    return [
        'This module does not report a real SPHEREx measurement.',
        'The DBI raw value is not substituted for the locked KK-centered target.',
        'A no-overlap verdict is required for falsification; mere offset is not enough.',
        'No hardgate score increase is granted for preregistration alone.',
    ]


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 656 report."""
    return {
        'pillar': PILLAR_NUMBER,
        'title': PILLAR_TITLE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'adjacent_track': ADJACENT_TRACK,
        'fnl_um_kk': FNL_UM_KK,
        'fnl_band_low': FNL_BAND_LOW,
        'fnl_band_high': FNL_BAND_HIGH,
        'fnl_dbi_raw': FNL_DBI_RAW,
        'spherex_snr': SPHEREX_SNR,
        'sha256_preregistration': SHA256_PREREGISTRATION,
        'what_is_claimed': what_is_claimed(),
        'what_is_NOT_claimed': what_is_NOT_claimed(),
        'toe_score_delta': 0.0,
        'hardgate_score_delta': 0.0,
    }
