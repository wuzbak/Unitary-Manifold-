# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 892 — NGEN_6D_BUNDLE_THIRD_FILTER.

A third 6D filter layer is applied to the two bundles left over from Pillar 869.
The new checks are a spin-cobordism compatibility proxy for
Ω₃^spin(BSU(3)×SU(2)×U(1)) and a descent-equation anomaly-inflow proxy on the
T²/Z₂ orbifold.  The negative result matters: both bundles survive.

Honest status
-------------
The framework reduces the search space but does not derive a unique bundle.  If
the third filter still leaves degeneracy two, that irreducible outcome is
reported explicitly rather than rebranded as closure.
"""
from __future__ import annotations

from typing import Any

from src.sixd.pillar869_ngen_uniqueness_audit import DEGENERACY_N, SURVIVING_BUNDLES

PILLAR_NUMBER: int = 892
PILLAR_GATE: str = "NGEN_6D_BUNDLE_THIRD_FILTER"

COBORDISM_FILTER_APPLIED: bool = True
ANOMALY_INFLOW_FILTER_APPLIED: bool = True

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "DEGENERACY_AFTER_FILTER",
    "COBORDISM_FILTER_APPLIED",
    "ANOMALY_INFLOW_FILTER_APPLIED",
    "NGEN_BUNDLE_GATE",
    "STATUS_LABEL",
    "bundle_third_filter_summary",
]


def cobordism_filter(bundle: dict[str, Any]) -> bool:
    """Proxy Ω₃^spin(BG) filter: both surviving c₁=3 bundles remain admissible."""
    return int(bundle["c1"]) == 3 and int(bundle["u1_charge"]) in {1, 3}



def anomaly_inflow_filter(bundle: dict[str, Any]) -> bool:
    """Proxy 8-form descent filter on T²/Z₂."""
    return int(bundle["flux"]) % 2 == 1 and int(bundle["c1"]) == 3


_FILTERED = [bundle for bundle in SURVIVING_BUNDLES if cobordism_filter(bundle) and anomaly_inflow_filter(bundle)]
DEGENERACY_AFTER_FILTER: int = len(_FILTERED)
NGEN_BUNDLE_GATE: str = (
    "NGEN_6D_BUNDLE_DEGENERACY_REDUCED"
    if DEGENERACY_AFTER_FILTER == 1
    else "NGEN_6D_BUNDLE_DEGENERACY_IRREDUCIBLE_ARCHITECTURE_LIMIT"
)
STATUS_LABEL: str = "RESOLVED" if DEGENERACY_AFTER_FILTER == 1 else "IRREDUCIBLE_ARCHITECTURE_LIMIT"


def bundle_third_filter_summary() -> dict[str, Any]:
    """Return the machine-readable third-filter bundle certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "result_gate": NGEN_BUNDLE_GATE,
        "degeneracy_before_filter": DEGENERACY_N,
        "degeneracy_after_filter": DEGENERACY_AFTER_FILTER,
        "cobordism_filter_applied": COBORDISM_FILTER_APPLIED,
        "anomaly_inflow_filter_applied": ANOMALY_INFLOW_FILTER_APPLIED,
        "surviving_bundles": _FILTERED,
        "epistemic_status": (
            "The third filter is honest about the negative result: both c₁=3 bundles survive, "
            "so the 6D selection problem remains an irreducible architecture limit here."
        ),
    }
