# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Worked example: re-express `src/core/z3_pentad_checker.py`'s four
hard-coded Pentad checks as `SafetyProperty` instances built from the
generic template, to prove the generalization is faithful."""

from __future__ import annotations

from .checker import SafetyProperty, Z3_AVAILABLE

if Z3_AVAILABLE:
    import z3

TRUST_PHI_MIN: float = 0.1
XI_C_NUM: int = 35
XI_C_DEN: int = 74
CS_NUM: int = 12
CS_DEN: int = 37
BODIES = ("univ", "brain", "human", "ai", "trust")


def _trust_stability_constraints():
    solver = z3.Solver()
    phi_trust = z3.Real("phi_trust")
    c_s = z3.Real("c_s")
    solver.add(phi_trust >= z3.RealVal(TRUST_PHI_MIN))
    solver.add(c_s == z3.RealVal(CS_NUM) / z3.RealVal(CS_DEN))
    solver.add(c_s > 0)
    return solver, True  # expect sat


def _no_deadlock_constraints():
    solver = z3.Solver()
    phis = {b: z3.Real(f"phi_{b}") for b in BODIES}
    solver.add(phis["univ"] >= z3.RealVal(TRUST_PHI_MIN))
    for b in BODIES:
        solver.add(phis[b] < z3.RealVal(TRUST_PHI_MIN))
    return solver, False  # expect unsat (deadlock impossible)


def _cs_bound_constraints():
    solver = z3.Solver()
    c_s = z3.Real("c_s")
    solver.add(c_s == z3.RealVal(CS_NUM) / z3.RealVal(CS_DEN))
    solver.add(z3.Or(c_s <= 0, c_s >= 1))
    return solver, False  # expect unsat (c_s always in bounds)


def _xi_c_rational_constraints():
    solver = z3.Solver()
    xi_c = z3.Real("xi_c")
    solver.add(xi_c == z3.RealVal(XI_C_NUM) / z3.RealVal(XI_C_DEN))
    solver.add(xi_c >= z3.RealVal(1) / z3.RealVal(2))
    return solver, False  # expect unsat (xi_c = 35/74 < 1/2)


PENTAD_SAFETY_PROPERTIES = [
    SafetyProperty(
        "trust_stability",
        _trust_stability_constraints,
        "phi_trust >= 0.1 AND c_s = 12/37 > 0 is satisfiable",
    ),
    SafetyProperty(
        "no_deadlock",
        _no_deadlock_constraints,
        "A total 5-body deadlock from a healthy start is unsatisfiable",
    ),
    SafetyProperty(
        "cs_bound",
        _cs_bound_constraints,
        "c_s = 12/37 is in (0, 1)",
    ),
    SafetyProperty(
        "xi_c_rational",
        _xi_c_rational_constraints,
        "xi_c = 35/74 is below the 1/2 symmetry point",
    ),
]
