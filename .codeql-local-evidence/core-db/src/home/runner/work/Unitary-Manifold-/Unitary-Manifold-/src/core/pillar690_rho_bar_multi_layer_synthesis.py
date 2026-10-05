# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar690_rho_bar_multi_layer_synthesis.py
==========================
Pillar 690 — Rho-Bar Multi-Layer Synthesis

Combines the LO, subleading, and FN Layer 2 rho-bar estimates into a single
closure ledger.  The key honest result is that Layer 1 is the best of the three
implemented layers, while the requested Layer 2 FN correction worsens the PDG
gap to ~39.6%.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
from typing import Any, Dict, List

__all__ = [
    "N_W",
    "K_CS",
    "N1",
    "N2",
    "W_RHOBAR_PDG",
    "LAYER0_RHO_BAR",
    "LAYER1_RHO_BAR",
    "layer_improvement_table",
    "multi_layer_synthesis",
    "final_rho_bar_status",
]

N_W = 5
K_CS = 74
N1 = 5
N2 = 7
W_RHOBAR_PDG = 0.159
W_LAMBDA_PDG = 0.225
M_U_MEV = 2.16
M_T_MEV = 172760.0
EPSILON_FN = N_W / K_CS
LAYER0_RHO_BAR = 0.113
LAYER1_RHO_BAR = 0.119


def _r_b() -> float:
    vub_geo = math.sqrt(M_U_MEV / M_T_MEV)
    a_geo = math.sqrt(N1 / N2)
    return vub_geo / (a_geo * W_LAMBDA_PDG**3)


def _layer2_rho_bar() -> float:
    delta_sub = 2.0 * math.atan2(N1, N2)
    harmonic = 2.0 * math.pi / N_W
    delta_fn = math.atan2(EPSILON_FN * math.sin(harmonic), 1.0 - EPSILON_FN * math.cos(harmonic))
    return _r_b() * math.cos(delta_sub + delta_fn)


def _gap_percent(rho_bar: float) -> float:
    return abs(rho_bar - W_RHOBAR_PDG) / W_RHOBAR_PDG * 100.0


def layer_improvement_table() -> List[Dict[str, Any]]:
    """Return the three-layer rho-bar closure table."""
    layer2 = _layer2_rho_bar()
    rows = [
        {"layer": 0, "label": "LO", "rho_bar": LAYER0_RHO_BAR},
        {"layer": 1, "label": "Subleading", "rho_bar": LAYER1_RHO_BAR},
        {"layer": 2, "label": "FN", "rho_bar": layer2},
    ]
    for row in rows:
        row["gap_percent"] = _gap_percent(row["rho_bar"])
    baseline_gap = rows[0]["gap_percent"]
    for row in rows:
        row["improvement_vs_layer0_percent_points"] = baseline_gap - row["gap_percent"]
    return rows


def final_rho_bar_status() -> Dict[str, Any]:
    """Return the final rho-bar verdict after all implemented layers."""
    table = layer_improvement_table()
    final_gap = table[-1]["gap_percent"]
    best_row = min(table, key=lambda item: item["gap_percent"])
    status = "HARDGATE_CANDIDATE" if final_gap < 5.0 else "ARCHITECTURE_LIMIT_CERTIFIED"
    return {
        "pillar": 690,
        "status": status,
        "final_layer": table[-1],
        "best_layer": best_row,
        "final_gap_percent": final_gap,
        "passes_10_percent": final_gap < 10.0,
        "passes_5_percent": final_gap < 5.0,
        "honest_note": (
            "The synthesized chain does not monotonically improve: Layer 1 is best, "
            "while the requested FN Layer 2 phase shift over-rotates the triangle."
        ),
    }


def multi_layer_synthesis() -> Dict[str, Any]:
    """Return the full multi-layer synthesis record."""
    table = layer_improvement_table()
    return {
        "pillar": 690,
        "status": final_rho_bar_status()["status"],
        "rho_bar_pdg": W_RHOBAR_PDG,
        "layers": table,
        "final_status": final_rho_bar_status(),
    }
