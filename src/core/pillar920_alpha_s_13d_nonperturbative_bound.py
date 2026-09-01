# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 920 — α_s 13D Non-Perturbative Instanton Bound.

🔵 ADJACENT TRACK — Non-hardgate.  Does not alter core 5D predictions.

═══════════════════════════════════════════════════════════════════════════
THE GAP THIS ADDRESSES
═══════════════════════════════════════════════════════════════════════════

Pillar 912 (Sprint BD) narrowed the 13D gauge-kinetic α_s window via T²
fiber and Kähler modulus corrections, but left ALPHA_S_ARCHITECTURE_LIMIT_OPEN:
the remaining gap requires a complete string-loop computation.

This pillar computes the non-perturbative correction from instanton
contributions in the 13D theory.  The key formulae:

  α_s^{NP} = α_s^{tree} · exp(−S_{inst})

where  S_{inst} = 2π / g_s^2  is the instanton action in the 7D orbifold,
and  g_s ≈ 0.72  (Pillar 854 HW vacuum selection).

The NP correction shifts α_s upward (since exp(−S) < 1 for the suppression
but the gauge-kinetic denominator shrinks), giving:

  δα_s^{NP} = α_s^{tree} · (1 − exp(−2π n_w / k_cs)) · C_NP

where C_NP is a loop coefficient estimated from 7D orbifold geometry.

HONEST RESULT
─────────────
ALPHA_S_13D_CLOSED if the corrected window [α_s_low, α_s_high] contains
the PDG value 0.1180.
ALPHA_S_13D_NP_IRREDUCIBLE otherwise.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Any, Dict, Tuple

__all__ = [
    "N_W",
    "K_CS",
    "G_S",
    "ALPHA_S_PDG",
    "ALPHA_S_ADS_5D",
    "ALPHA_S_13D_CENTRAL",
    "ALPHA_S_NP_CENTRAL",
    "ALPHA_S_NP_WINDOW",
    "INSTANTON_ACTION",
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "instanton_correction",
    "alpha_s_np_bound",
    "alpha_s_np_summary",
]

N_W: int = 5
K_CS: int = 74
PI: float = math.pi

# From Pillar 854 HW vacuum
G_S: float = 0.72

# PDG α_s(M_Z)
ALPHA_S_PDG: float = 0.1180

# 5D tree-level (Pillar 693)
ALPHA_S_ADS_5D: float = PI ** 2 / (2.0 * K_CS)   # ≈ 0.0666

# 13D central value from Pillar 912
ALPHA_S_13D_CENTRAL: float = ALPHA_S_ADS_5D + N_W / (2.0 * K_CS)   # ≈ 0.1004

# Instanton action in units of g_s
INSTANTON_ACTION: float = 2.0 * PI * N_W / (K_CS * G_S ** 2)

# NP loop coefficient from 7D orbifold (one-loop Bessel function estimate)
# C_NP = n_w / (2 * k_cs * g_s²) × 1/(2π)
C_NP: float = N_W / (2.0 * K_CS * G_S ** 2 * 2.0 * PI)

# Non-perturbative correction
_inst_suppress: float = 1.0 - math.exp(-INSTANTON_ACTION)
DELTA_NP: float = ALPHA_S_13D_CENTRAL * _inst_suppress * C_NP

ALPHA_S_NP_CENTRAL: float = ALPHA_S_13D_CENTRAL + DELTA_NP

# Window: ±30% of the NP correction
_uncert: float = 0.30 * abs(DELTA_NP)
ALPHA_S_NP_WINDOW: Tuple[float, float] = (
    max(0.0, ALPHA_S_NP_CENTRAL - _uncert),
    ALPHA_S_NP_CENTRAL + _uncert,
)

PILLAR_NUMBER: int = 920
PILLAR_GATE: str = "ALPHA_S_13D_NONPERTURBATIVE_BOUND"

# Honest status
_window_includes_pdg: bool = ALPHA_S_NP_WINDOW[0] <= ALPHA_S_PDG <= ALPHA_S_NP_WINDOW[1]
PILLAR_STATUS: str = (
    "ALPHA_S_13D_CLOSED" if _window_includes_pdg else "ALPHA_S_13D_NP_IRREDUCIBLE"
)


def instanton_correction() -> Dict[str, Any]:
    """Return full instanton correction computation."""
    return {
        "n_w": N_W,
        "k_cs": K_CS,
        "g_s": G_S,
        "instanton_action": INSTANTON_ACTION,
        "inst_suppression_factor": _inst_suppress,
        "c_np_loop_coeff": C_NP,
        "alpha_s_ads_5d": ALPHA_S_ADS_5D,
        "alpha_s_13d_central": ALPHA_S_13D_CENTRAL,
        "delta_np": DELTA_NP,
        "alpha_s_np_central": ALPHA_S_NP_CENTRAL,
        "alpha_s_np_window": ALPHA_S_NP_WINDOW,
        "alpha_s_pdg": ALPHA_S_PDG,
        "window_includes_pdg": _window_includes_pdg,
        "residual_pct_5d": abs(ALPHA_S_ADS_5D - ALPHA_S_PDG) / ALPHA_S_PDG * 100.0,
        "residual_pct_np": abs(ALPHA_S_NP_CENTRAL - ALPHA_S_PDG) / ALPHA_S_PDG * 100.0,
    }


def alpha_s_np_bound() -> Dict[str, Any]:
    """Full NP bound analysis with honest closure assessment."""
    corr = instanton_correction()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "instanton_correction": corr,
        "interpretation": (
            "The 13D instanton correction brings the NP window "
            f"[{ALPHA_S_NP_WINDOW[0]:.4f}, {ALPHA_S_NP_WINDOW[1]:.4f}] to "
            f"{'include' if _window_includes_pdg else 'not include'} the PDG value "
            f"{ALPHA_S_PDG}.  "
            + (
                "ALPHA_S_13D_CLOSED: PDG value falls inside the NP-corrected window — "
                "the gap is covered at the leading NP level."
                if _window_includes_pdg
                else
                "ALPHA_S_13D_NP_IRREDUCIBLE: even with NP instanton corrections, the "
                "window does not reach PDG.  Full string-loop computation required."
            )
        ),
        "open_item": (
            None
            if _window_includes_pdg
            else (
                "ALPHA_S_NP_IRREDUCIBLE: non-perturbative instanton correction does "
                "not bridge the remaining α_s gap.  Architecture limit confirmed."
            )
        ),
        "references": [
            "Pillar 912 — 13D gauge kinetic function (T² + Kähler corrections)",
            "Pillar 693 — α_s 13D moduli pathway (5D AdS tree level)",
            "Pillar 854 — HW UV vacuum g_s = 0.72",
            "Blumenhagen et al., D-Brane Instantons in Type II Orientifolds (2009)",
        ],
    }


def alpha_s_np_summary() -> Dict[str, Any]:
    r = alpha_s_np_bound()
    return {
        "pillar": r["pillar"],
        "gate": r["gate"],
        "status": r["status"],
        "alpha_s_np_central": ALPHA_S_NP_CENTRAL,
        "alpha_s_np_window": ALPHA_S_NP_WINDOW,
        "alpha_s_pdg": ALPHA_S_PDG,
        "window_includes_pdg": _window_includes_pdg,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(alpha_s_np_bound(), indent=2, default=str))
