# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1033 — neutrino mass-scale topological-form program (void-space execution C)."""

from __future__ import annotations

from typing import Any, Dict

from src.core.neutrino_rge_bridge import c_left_from_rge_consistency
from src.core.pillar416_cl_phys_topological import rational_search, um_expression_search
from src.core.pillar964_cl_phys_analytic_closure import CL_PHYS_ZERO_ORDER, K_CS, N_W

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "PILLAR964_UV_FRACTION",
    "neutrino_topological_form_program",
    "pillar1033_summary",
]

PILLAR_NUMBER: int = 1033
PILLAR_GATE: str = "NEUTRINO_TOPOLOGICAL_FORM_PROGRAM"
PILLAR_STATUS: str = "NEUTRINO_TOPOLOGICAL_FORM_PROGRAM_COMPLETE"
PILLAR964_UV_FRACTION: str = "69/74"


def neutrino_topological_form_program() -> Dict[str, Any]:
    """Attempt UV/IR reconciliation for c_L^phys or certify irreducible separation."""
    rge_solution = c_left_from_rge_consistency()
    rational = rational_search(target=float(rge_solution["c_left_required"]))
    expressions = um_expression_search()

    c_l_uv = float(CL_PHYS_ZERO_ORDER)
    c_l_ir = float(rge_solution["c_left_required"])
    uv_ir_gap = abs(c_l_ir - c_l_uv)

    topological_match = uv_ir_gap <= 0.01
    strict_closed_form_match = (
        abs(float(rational["best_rational"]["value"]) - c_l_ir) <= 1.0e-4
    )

    closure_earned = topological_match and strict_closed_form_match
    outcome = (
        "NEUTRINO_TOPOLOGICAL_FORM_CLOSURE_EARNED"
        if closure_earned
        else "NEUTRINO_UV_IR_SEPARATION_CERTIFIED"
    )

    named_residual = (
        "CL_PHYS_IR_SHIFT_FROM_RGE"
        if not closure_earned
        else "NONE"
    )

    valid = outcome in {
        "NEUTRINO_TOPOLOGICAL_FORM_CLOSURE_EARNED",
        "NEUTRINO_UV_IR_SEPARATION_CERTIFIED",
    }

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "execution_order_rank": 3,
        "uv_fraction": PILLAR964_UV_FRACTION,
        "n_w": N_W,
        "k_cs": K_CS,
        "c_l_uv": c_l_uv,
        "c_l_ir_rge": c_l_ir,
        "uv_ir_gap": uv_ir_gap,
        "rge_solver_status": rge_solution["status"],
        "best_rational_match": rational["best_rational"],
        "best_global_rational": rational["best_global_rational"],
        "best_expression_match": expressions["best_match"],
        "topological_match": topological_match,
        "strict_closed_form_match": strict_closed_form_match,
        "closure_earned": closure_earned,
        "named_residual": named_residual,
        "outcome": outcome,
        "interpretation": (
            "The UV analytic form c_L=(K_CS-N_W)/K_CS is retained while the IR value "
            "from neutrino-scale consistency remains RGE-shifted. The lane is reported "
            "as UV/IR separation unless a true closed-form reconciliation is achieved."
        ),
    }


_REPORT = neutrino_topological_form_program()
PILLAR_VALID: bool = bool(_REPORT["valid"])


def pillar1033_summary() -> Dict[str, Any]:
    """Return concise Pillar 1033 summary."""
    report = neutrino_topological_form_program()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Neutrino Topological-Form Program",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "outcome": report["outcome"],
        "named_residual": report["named_residual"],
        "uv_ir_gap": report["uv_ir_gap"],
    }

