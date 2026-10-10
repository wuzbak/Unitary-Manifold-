# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Templated Z3 safety-property checker library — Phase 1 of article-354
direction #11 ("Z3 checker -> formal-verification-as-a-service").

`src/core/z3_pentad_checker.py` hard-codes four Pentad-specific checks
(`check_trust_stability`, `check_no_deadlock`, `check_cs_bound`,
`check_xi_c_rational`). This module extracts the *shape* those checks
share — declare real-valued variables, declare constraints, declare a
named safety property, ask Z3 sat/unsat, interpret the result as
PASS/FAIL — into a reusable, domain-agnostic template, so any project
can define its own checker without hand-rolling Z3 boilerplate.

JAX/Z3 pattern: Z3 is an optional dependency in this repository
(`src/core/z3_pentad_checker.py` imports it unconditionally, matching
that module's own convention); this module guards the import so callers
can detect its absence gracefully.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

try:
    import z3
    Z3_AVAILABLE = True
    _IMPORT_ERROR: Optional[str] = None
except Exception as exc:  # pragma: no cover - exercised only when z3 missing
    z3 = None
    Z3_AVAILABLE = False
    _IMPORT_ERROR = str(exc)


def require_z3() -> None:
    if not Z3_AVAILABLE:
        raise RuntimeError(
            "z3-solver is not available in this environment "
            f"(import failed with: {_IMPORT_ERROR}). "
            "Install the 'z3-solver' package to run formal checks."
        )


@dataclass
class SafetyProperty:
    """A named safety property: a set of Z3 constraints plus an
    expected satisfiability outcome that counts as PASS.

    Parameters
    ----------
    name : str
    build_constraints : Callable[[], tuple]
        Zero-argument callable returning ``(solver, expect_sat)`` where
        ``solver`` is a fully-populated ``z3.Solver`` and ``expect_sat``
        is ``True`` if the property should be checked by expecting
        ``sat`` (a model exists), or ``False`` if it should be checked by
        expecting ``unsat`` (no counterexample exists).
    description : str
    """

    name: str
    build_constraints: Callable[[], tuple]
    description: str = ""


@dataclass
class CheckResult:
    name: str
    status: str  # "PASS" | "FAIL"
    z3_result: str
    model: Dict[str, str] = field(default_factory=dict)
    description: str = ""


def run_property(prop: SafetyProperty) -> CheckResult:
    """Run one SafetyProperty through Z3 and interpret the result."""
    require_z3()
    solver, expect_sat = prop.build_constraints()
    result = solver.check()
    passed = (result == z3.sat) if expect_sat else (result == z3.unsat)
    model: Dict[str, str] = {}
    if result == z3.sat:
        m = solver.model()
        for d in m.decls():
            model[d.name()] = str(m[d])
    return CheckResult(
        name=prop.name,
        status="PASS" if passed else "FAIL",
        z3_result=str(result),
        model=model,
        description=prop.description,
    )


def run_suite(properties: List[SafetyProperty]) -> Dict[str, object]:
    """Run a suite of SafetyProperty checks and summarize pass/fail counts."""
    results = [run_property(p) for p in properties]
    n_pass = sum(1 for r in results if r.status == "PASS")
    return {
        "results": results,
        "n_total": len(results),
        "n_pass": n_pass,
        "n_fail": len(results) - n_pass,
        "all_passed": n_pass == len(results),
    }
