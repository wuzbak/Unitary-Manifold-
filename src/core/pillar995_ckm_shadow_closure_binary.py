# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 995 — CKM shadow closure binary decision."""

from __future__ import annotations

import math
from typing import Any, Dict

from src.core.pillar994_unified_13d_compactification_state import (
    unified_13d_compactification_state,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "ckm_shadow_closure_binary",
]

PILLAR_NUMBER: int = 995
PILLAR_GATE: str = "CKM_SHADOW_CLOSURE_BINARY"

_THETA13_PDG_DEG = 0.201
_VUB_PDG = 3.82e-3
_JARLSKOG_PDG = 3.18e-5


def ckm_shadow_closure_binary() -> Dict[str, Any]:
    """Return binary CKM closure outcome from unified parent state only."""
    state = unified_13d_compactification_state()
    shared = state["shared_parent_state"]
    ckm = state["ckm_inputs"]

    theta13_deg = (
        ckm["theta13_base_deg"]
        + ckm["theta13_sin_weight"] * abs(math.sin(shared["torsion_phase"]))
        + ckm["theta13_tau_weight"] * (shared["tau"] - 1.0)
        + ckm["theta13_rho_weight"] * (shared["rho"] - 0.8)
    )
    vub = math.sin(math.radians(theta13_deg)) * ckm["vub_scale"]
    jarlskog = (
        math.sin(math.radians(theta13_deg))
        * math.sin(shared["torsion_phase"])
        * ckm["jarlskog_scale"]
    )

    theta13_rel_error = abs(theta13_deg - _THETA13_PDG_DEG) / _THETA13_PDG_DEG
    vub_rel_error = abs(vub - _VUB_PDG) / _VUB_PDG
    jarlskog_rel_error = abs(jarlskog - _JARLSKOG_PDG) / _JARLSKOG_PDG

    closed = (
        theta13_rel_error < 0.35
        and vub_rel_error < 0.35
        and jarlskog_rel_error < 0.35
    )
    runtime_status = (
        "CKM_SHADOW_CLOSED_FROM_PARENT_13D"
        if closed
        else "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED"
    )

    missing_object = (
        "NONE"
        if closed
        else "GLOBAL_FLAVOR_BUNDLE_WITH_NONLOCAL_OVERLAP_TENSOR"
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "runtime_status": runtime_status,
        "theta13_deg": theta13_deg,
        "vub": vub,
        "jarlskog_proxy": jarlskog,
        "theta13_rel_error": theta13_rel_error,
        "vub_rel_error": vub_rel_error,
        "jarlskog_rel_error": jarlskog_rel_error,
        "closed": closed,
        "named_missing_object": missing_object,
        "input_source": "PILLAR_994_UNIFIED_13D_COMPACTIFICATION_STATE",
    }


PILLAR_STATUS: str = "CKM_SHADOW_CLOSURE_BINARY_COMPLETE"
PILLAR_VALID: bool = True
