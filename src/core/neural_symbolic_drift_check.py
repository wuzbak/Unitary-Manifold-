# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Post-MAS Track 3: neural-symbolic drift checks for core equations."""

from __future__ import annotations

from typing import Callable, Dict, List

import sympy as sp

from src.core.sensitivity_analysis import (
    C_S_BRAIDED,
    PHI0_CANONICAL,
    cs_from_phi0,
    ns_from_phi0,
    r_from_phi0,
    w_kk_from_phi0,
)

__all__ = [
    "equation_family_report",
    "track3_drift_artifact",
]


def _sample_phi0() -> List[float]:
    base = PHI0_CANONICAL
    return [base * 0.95, base, base * 1.05]


def _equation_specs() -> List[Dict[str, object]]:
    phi0 = sp.Symbol("phi0", positive=True, real=True)
    n_w = sp.Integer(5)
    c_s = sp.Rational(12, 37)
    return [
        {
            "family": "inflation_observables",
            "name": "n_s(phi0)",
            "symbolic": 1 - 8 * n_w / phi0**2,
            "numeric": ns_from_phi0,
            "vars": [phi0],
        },
        {
            "family": "inflation_observables",
            "name": "r_braided(phi0)",
            "symbolic": (32 * n_w / phi0**2) * c_s,
            "numeric": r_from_phi0,
            "vars": [phi0],
        },
        {
            "family": "dark_energy_sector",
            "name": "c_s(phi0)",
            "symbolic": c_s,
            "numeric": cs_from_phi0,
            "vars": [phi0],
        },
        {
            "family": "dark_energy_sector",
            "name": "w_KK(phi0)",
            "symbolic": -1 + sp.Rational(2, 3) * c_s**2,
            "numeric": w_kk_from_phi0,
            "vars": [phi0],
        },
    ]


def equation_family_report(tolerance: float = 1e-12) -> Dict[str, object]:
    """Return per-family pass/fail drift report from symbolic reverse-mapping."""
    specs = _equation_specs()
    by_family: Dict[str, Dict[str, object]] = {}
    for spec in specs:
        family = spec["family"]
        if family not in by_family:
            by_family[family] = {"equations": [], "status": "PASS"}

        fn: Callable[[float], float] = spec["numeric"]
        sym_expr = spec["symbolic"]
        phi0 = spec["vars"][0]
        sym_fn = sp.lambdify(phi0, sym_expr, "numpy")

        diffs = []
        for x in _sample_phi0():
            symbolic_val = float(sym_fn(x))
            numeric_val = float(fn(float(x)))
            diffs.append(abs(symbolic_val - numeric_val))
        max_diff = max(diffs)
        passed = bool(max_diff <= tolerance)
        if not passed:
            by_family[family]["status"] = "FAIL"

        by_family[family]["equations"].append(
            {
                "name": spec["name"],
                "max_abs_diff": max_diff,
                "tolerance": tolerance,
                "status": "PASS" if passed else "FAIL",
            }
        )

    overall = "PASS" if all(v["status"] == "PASS" for v in by_family.values()) else "FAIL"
    return {
        "families": by_family,
        "overall_status": overall,
    }


def track3_drift_artifact(tolerance: float = 1e-12) -> Dict[str, object]:
    """Return complete Track 3 artifact."""
    report = equation_family_report(tolerance=tolerance)
    return {
        "track": "T3",
        "title": "Neural-symbolic drift check",
        "drift_report": report["families"],
        "status": report["overall_status"],
        "tolerance": tolerance,
    }

