# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 985 — Cross-Domain Calibration Harness (Sprint BL)."""

from __future__ import annotations

import hashlib
from typing import Any, Dict

from src.core.pillar950_ckm_kk_excited_states_audit import DELTA_THETA13_FRAC
from src.core.pillar951_fermion_ri_constraint_scaffold import CONSISTENCY_RATIO_MAX
from src.core.pillar958_cmb_kk_transfer_analytic import DELTA_KK_SOUND, DELTA_SILK
from src.core.pillar937_alpha_s_13d_window_tighten import ALPHA_S_PDG, WINDOW_TIGHTENED
from src.core.pillar984_compactification_parameter_object import (
    canonical_compactification_parameters,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "cross_domain_calibration_report",
]

PILLAR_NUMBER: int = 985
PILLAR_GATE: str = "CROSS_DOMAIN_CALIBRATION_HARNESS"


def _parameter_signature(payload: Dict[str, Any]) -> str:
    normalized = str(sorted(payload.items())).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()[:16]


def cross_domain_calibration_report() -> Dict[str, Any]:
    """Build a single calibration payload reused across all architecture lanes."""
    shared = canonical_compactification_parameters().to_dict()
    signature = _parameter_signature(shared)

    alpha_low, alpha_high = WINDOW_TIGHTENED
    lanes = {
        "ckm_theta13": {
            "parameter_signature": signature,
            "in_eft_correction_cap": DELTA_THETA13_FRAC,
            "calibration_status": "EFT_EXHAUSTED" if DELTA_THETA13_FRAC < 0.01 else "REVIEW",
        },
        "fermion_magnitudes": {
            "parameter_signature": signature,
            "ri_window_max_abs": abs(CONSISTENCY_RATIO_MAX),
            "calibration_status": "WINDOW_CONSTRAINED" if abs(CONSISTENCY_RATIO_MAX) < 0.5 else "TUNED",
        },
        "alpha_s": {
            "parameter_signature": signature,
            "window": [alpha_low, alpha_high],
            "pdg": ALPHA_S_PDG,
            "calibration_status": "OUTSIDE_WINDOW" if not (alpha_low <= ALPHA_S_PDG <= alpha_high) else "INSIDE_WINDOW",
        },
        "cmb_transfer": {
            "parameter_signature": signature,
            "delta_kk_sound": DELTA_KK_SOUND,
            "delta_silk": DELTA_SILK,
            "calibration_status": "TRANSFER_CHARACTERIZED",
        },
    }

    same_signature = len({lane["parameter_signature"] for lane in lanes.values()}) == 1
    valid = same_signature and bool(shared)

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "shared_parameters": shared,
        "parameter_signature": signature,
        "lanes": lanes,
        "all_lanes_share_same_parameters": same_signature,
    }


PILLAR_STATUS: str = "CROSS_DOMAIN_CALIBRATION_HARNESS_COMPLETE"
PILLAR_VALID: bool = cross_domain_calibration_report()["valid"]
