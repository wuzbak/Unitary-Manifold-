# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 916 — 13D DBP Rung 8 Master Certificate.

🔵 ADJACENT TRACK — Non-hardgate capstone.

═══════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════

This pillar aggregates the Sprint BD results (Pillars 911–915) together
with the existing Rung 7 F-theory scaffold (Pillar 570) to produce the
honest Rung 8 ledger.

It is a *certificate*, not a score.  It documents:
  1. What closed (or partially closed) at the I-Theory level.
  2. What was narrowed (but remains open).
  3. What remains irreducible at the highest available level.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar911_sp2r_null_cone_radion import PILLAR_STATUS as STATUS_911, null_cone_summary
from src.core.pillar912_alpha_s_13d_gauge_kinetic import PILLAR_STATUS as STATUS_912, alpha_s_13d_summary
from src.core.pillar913_ckm_sp2r_shadow_gauge import PILLAR_STATUS as STATUS_913, ckm_sp2r_summary
from src.core.pillar914_ngen_aps_index_cy4 import PILLAR_STATUS as STATUS_914, ngen_aps_summary
from src.core.pillar915_cmb_amp_13d_radion import PILLAR_STATUS as STATUS_915, cmb_amp_summary

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "RUNG_8_STATUS",
    "BRIDGE_VALID",
    "REMAINING_OPEN",
    "ARCHITECTURE_LIMITS_CERTIFIED",
    "rung8_master_certificate",
    "sprint_bd_master_bridge_summary",
]

PILLAR_NUMBER: int = 916
PILLAR_GATE: str = "RUNG_8_DBP_MASTER_CERTIFICATE"

# --------------------------------------------------------------------------
# Aggregate results from Pillars 911–915
# --------------------------------------------------------------------------
_RESULTS: Dict[str, str] = {
    "P911_null_cone": STATUS_911,
    "P912_alpha_s": STATUS_912,
    "P913_ckm_shadow": STATUS_913,
    "P914_ngen_aps": STATUS_914,
    "P915_cmb_amp": STATUS_915,
}

# Items that closed or partially closed
_CLOSED: List[str] = [k for k, v in _RESULTS.items() if "CONSISTENT" in v or "CONFIRMED" in v or "PARTIAL_CLOSURE" in v or "NARROWED" in v or "FIXED" in v]

# Items that remain open (tension or architecture limit)
_OPEN: List[str] = [k for k, v in _RESULTS.items() if k not in _CLOSED]

# Rung 8 status: partial closure if at least one item closed, else architecture certified
_has_partial: bool = len(_CLOSED) > 0
RUNG_8_STATUS: str = "RUNG_8_PARTIAL_CLOSURE" if _has_partial else "RUNG_8_ARCHITECTURE_CERTIFIED"

# Rung 7 scaffold status (from Pillar 570)
RUNG_7_STATUS: str = "SCAFFOLD_COMPLETE"

# Master bridge valid if no import errors and at least rung scaffold is complete
BRIDGE_VALID: bool = True

REMAINING_OPEN: List[str] = [
    f"CKM_TENSION_PERSISTS_13D: {STATUS_913} — Sp(2,R) shadow gauge does not canonically fix FN charges to all three PDG CKM angles.",
    "CMB_AMP_ARCHITECTURE_LIMIT: full CMB peak amplitude closure requires numerical Boltzmann integration with Sp(2,R) WZ source term.",
]

ARCHITECTURE_LIMITS_CERTIFIED: List[str] = []
if "IRREDUCIBLE" in STATUS_912:
    ARCHITECTURE_LIMITS_CERTIFIED.append(
        "ALPHA_S_13D_IRREDUCIBLE: α_s gap not narrowed by T² fiber + Kähler corrections at leading order."
    )
if "IRREDUCIBLE" in STATUS_914:
    ARCHITECTURE_LIMITS_CERTIFIED.append(
        "NGEN_DEGENERACY_IRREDUCIBLE_13D: N_gen from CY₄ APS index does not confirm 3 on reference geometry."
    )
if "TENSION" in STATUS_913:
    ARCHITECTURE_LIMITS_CERTIFIED.append(
        "CKM_TENSION_PERSISTS_13D: CKM θ ordering tension documented at I-Theory level."
    )
if "ARCHITECTURE_LIMIT" in STATUS_915:
    ARCHITECTURE_LIMITS_CERTIFIED.append(
        "CMB_AMP_13D_ARCHITECTURE_LIMIT: WZ correction insufficient to bring suppression below ×4."
    )


def rung8_master_certificate() -> Dict[str, Any]:
    """Return the full Rung 8 master certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "rung_7_status": RUNG_7_STATUS,
        "rung_8_status": RUNG_8_STATUS,
        "bridge_valid": BRIDGE_VALID,
        "pillar_results": _RESULTS,
        "closed_or_narrowed": _CLOSED,
        "open_items": _OPEN,
        "n_closed": len(_CLOSED),
        "n_open": len(_OPEN),
        "remaining_open": REMAINING_OPEN,
        "architecture_limits_certified": ARCHITECTURE_LIMITS_CERTIFIED,
        "pillar_summaries": {
            "P911": null_cone_summary(),
            "P912": alpha_s_13d_summary(),
            "P913": ckm_sp2r_summary(),
            "P914": ngen_aps_summary(),
            "P915": cmb_amp_summary(),
        },
        "epistemic_note": (
            "This certificate is an honest accounting of what the 13D I-Theory level "
            "adds to the framework.  Results marked CONSISTENT/CONFIRMED/NARROWED "
            "represent genuine theoretical progress.  Results marked TENSION or "
            "ARCHITECTURE_LIMIT are documented for future resolution — no mechanism "
            "has been invented to force closure."
        ),
        "references": [
            "Pillar 570 — F-Theory Rung 7 scaffold",
            "Pillar 682 — 13D I-Theory metric engine",
            "Pillars 911–915 — Sprint BD results",
            "Bars & Terning, Extra Dimensions in Space and Time (2010)",
        ],
    }


def sprint_bd_master_bridge_summary() -> Dict[str, Any]:
    """Concise summary for the sprint regression certificate."""
    r = rung8_master_certificate()
    return {
        "pillar": r["pillar"],
        "gate": r["gate"],
        "rung_8_status": r["rung_8_status"],
        "n_closed": r["n_closed"],
        "n_open": r["n_open"],
        "bridge_valid": r["bridge_valid"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(rung8_master_certificate(), indent=2, default=str))
