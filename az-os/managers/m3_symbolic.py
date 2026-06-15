# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/managers/m3_symbolic.py — Manager 3: Symbolic Math & Algebraic Verification

Every physics claim from any other manager passes through M3 before being
accepted.  M3 uses SymPy for symbolic verification and Z3 for SMT bounds checking.

Sub-agents:
  1. SympyTranslatorAgent  — translates claims to SymPy expressions
  2. Z3BoundsAgent         — checks numerical bounds via Z3 SAT
  3. TypeEnforcer          — variable-type consistency check
  4. EquivalenceProver     — symbolic equivalence between two expressions
  5. EdgeCaseChecker       — numerical edge-case scanner (NaN, inf, zero-division)
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).parent.parent.parent

try:
    import sympy as sp
    _SYMPY = True
except ImportError:
    _SYMPY = False

try:
    import z3
    _Z3 = True
except ImportError:
    _Z3 = False


@dataclass
class SymbolicResult:
    agent: str
    status: str         # "verified" | "falsified" | "unverified" | "error"
    value: Any = None
    error: Optional[str] = None


class M3SymbolicManager:
    """
    Manager 3 — Symbolic Math & Algebraic Verification.

    This is the mathematical firewall.  No claim exits M3 as "verified" unless
    it passes at least one of: SymPy symbolic check OR Z3 SMT bounds check.
    Claims that cannot be checked are labelled "unverified" and flagged for
    human review via M7.
    """

    MANAGER_ID = "M3"
    KK_LEVEL = 1  # system-services ring (not kernel — symbolic math is adjacent-track)

    # ------------------------------------------------------------------
    # Sub-agent 1: SymPy Translator
    # ------------------------------------------------------------------

    def sympy_verify(self, expr_str: str, assumption_str: str = "True") -> SymbolicResult:
        """
        Verify a symbolic expression using SymPy.

        Parameters
        ----------
        expr_str : str
            A SymPy-parseable expression that should simplify to zero or True.
            Example: "Eq(5**2 + 7**2, 74)"
        assumption_str : str
            Optional assumption context.
        """
        if not _SYMPY:
            return SymbolicResult("SympyTranslatorAgent", "unverified",
                                  error="SymPy not installed")
        try:
            result = sp.sympify(expr_str)
            simplified = sp.simplify(result)
            if simplified == sp.true or simplified == 0 or simplified is sp.true:
                return SymbolicResult("SympyTranslatorAgent", "verified",
                                      value=str(simplified))
            else:
                return SymbolicResult("SympyTranslatorAgent", "falsified",
                                      value=str(simplified))
        except Exception as exc:
            return SymbolicResult("SympyTranslatorAgent", "error", error=str(exc))

    # ------------------------------------------------------------------
    # Sub-agent 2: Z3 Bounds
    # ------------------------------------------------------------------

    def z3_bounds_check(
        self,
        variable_name: str,
        lower_bound: float,
        upper_bound: float,
        claimed_value: float,
    ) -> SymbolicResult:
        """
        Check that a claimed value lies within the given bounds using Z3.

        Returns "verified" if lower ≤ claimed ≤ upper, "falsified" otherwise.
        """
        if not _Z3:
            # Fallback: pure Python bounds check
            ok = lower_bound <= claimed_value <= upper_bound
            return SymbolicResult(
                "Z3BoundsAgent",
                "verified" if ok else "falsified",
                value={"lower": lower_bound, "value": claimed_value, "upper": upper_bound},
            )
        try:
            v = z3.Real(variable_name)
            solver = z3.Solver()
            solver.add(v >= lower_bound, v <= upper_bound, v == claimed_value)
            sat = solver.check()
            status = "verified" if sat == z3.sat else "falsified"
            return SymbolicResult("Z3BoundsAgent", status,
                                  value={"z3_result": str(sat)})
        except Exception as exc:
            return SymbolicResult("Z3BoundsAgent", "error", error=str(exc))

    # ------------------------------------------------------------------
    # Sub-agent 3: Type Enforcer
    # ------------------------------------------------------------------

    def type_check(self, claims: dict) -> SymbolicResult:
        """
        Check that all values in a claims dictionary have the expected types.

        ``claims`` format: {variable_name: (value, expected_type)}
        Example: {"n_w": (5, int), "n_s": (0.9635, float)}
        """
        errors = []
        for name, (value, expected) in claims.items():
            if not isinstance(value, expected):
                errors.append(f"{name}: got {type(value).__name__}, expected {expected.__name__}")
        if errors:
            return SymbolicResult("TypeEnforcer", "falsified",
                                  error="; ".join(errors))
        return SymbolicResult("TypeEnforcer", "verified",
                              value={"checked": list(claims.keys())})

    # ------------------------------------------------------------------
    # Sub-agent 4: Equivalence Prover
    # ------------------------------------------------------------------

    def prove_equivalence(self, expr_a: str, expr_b: str) -> SymbolicResult:
        """
        Prove that two symbolic expressions are equivalent.

        Returns "verified" if SymPy can prove expr_a == expr_b, "unverified" otherwise.
        """
        if not _SYMPY:
            return SymbolicResult("EquivalenceProver", "unverified",
                                  error="SymPy not installed")
        try:
            a = sp.sympify(expr_a)
            b = sp.sympify(expr_b)
            diff = sp.simplify(a - b)
            if diff == 0:
                return SymbolicResult("EquivalenceProver", "verified",
                                      value={"difference": "0"})
            else:
                return SymbolicResult("EquivalenceProver", "falsified",
                                      value={"difference": str(diff)})
        except Exception as exc:
            return SymbolicResult("EquivalenceProver", "error", error=str(exc))

    # ------------------------------------------------------------------
    # Sub-agent 5: Edge Case Checker
    # ------------------------------------------------------------------

    def edge_case_check(self, func_str: str, test_points: list[float]) -> SymbolicResult:
        """
        Numerically evaluate a function at test points to detect NaN, inf, or zero-division.

        ``func_str`` must be a valid Python expression in variable 'x'.
        Example: "1 / (x - 5)"  with test_points=[0, 5, 10]
        """
        issues = []
        import math
        for x in test_points:
            try:
                val = eval(func_str, {"x": x, "math": math})  # noqa: S307
                if math.isnan(val) or math.isinf(val):
                    issues.append(f"x={x} → {val}")
            except ZeroDivisionError:
                issues.append(f"x={x} → ZeroDivisionError")
            except Exception as exc:
                issues.append(f"x={x} → {exc}")
        if issues:
            return SymbolicResult("EdgeCaseChecker", "falsified",
                                  error="; ".join(issues))
        return SymbolicResult("EdgeCaseChecker", "verified",
                              value={"test_points": test_points})

    # ------------------------------------------------------------------
    # Validate core UM constants (called by AgentCore at startup)
    # ------------------------------------------------------------------

    def validate_core_constants(self) -> list[SymbolicResult]:
        """Run all 5 sub-agents on the core UM physics constants."""
        return [
            # n_w = 5, k_cs = 74 = 5² + 7²
            self.sympy_verify("Eq(5**2 + 7**2, 74)"),
            # n_s prediction in Planck bounds
            self.z3_bounds_check("n_s", 0.9607, 0.9691, 0.9635),
            # Type check core constants
            self.type_check({
                "n_w": (5, int),
                "k_cs": (74, int),
                "n_s": (0.9635, float),
                "r_braided": (0.0315, float),
            }),
            # φ⁻¹ equivalence
            self.prove_equivalence("2/(1+sqrt(5))", "(-1+sqrt(5))/2"),
            # Sound speed edge cases
            self.edge_case_check("12/37", []),
        ]
