# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Focused formal-invariant registry for non-regression proof checks."""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List

from src.core.aps_spin_structure import eta_bar_from_cs_inflow
from src.core.braided_winding import braided_sound_speed, resonant_kcs
from src.core.completeness_theorem import kcs_seven_closure_conditions

CANONICAL_N1 = 5
CANONICAL_N2 = 7
CANONICAL_K_CS = 74
CANONICAL_SOUND_SPEED = Fraction(12, 37)


def _optional_z3_status() -> Dict[str, Any]:
    try:  # pragma: no cover - optional dependency
        import z3  # type: ignore
    except Exception:
        return {
            "available": False,
            "solver": "z3",
            "status": "UNAVAILABLE",
            "reason": "Optional dependency not installed in the current environment.",
        }
    return {
        "available": True,
        "solver": "z3",
        "status": "AVAILABLE",
        "version": getattr(z3, "get_version_string", lambda: "unknown")(),
    }


def formal_invariant_registry() -> Dict[str, Any]:
    """Return the canonical registry describing which invariants live where."""
    return {
        "status": "FORMAL_INVARIANT_REGISTRY_READY",
        "scope_note": (
            "This registry covers a small high-leverage invariant set for non-regression checking. "
            "It is not a claim that the whole theory has been formalized."
        ),
        "interface_standard": {
            "lean4": {
                "role": "Full theorem statements and proof artifacts where already available or promoted later.",
                "required_fields": ["artifact_path", "claim_class", "regression_gate"],
            },
            "z3": {
                "role": "Constraint consistency and satisfiability checks for discrete/integer claims.",
                "required_fields": ["solver", "available", "status"],
            },
            "python": {
                "role": "Deterministic executable truth-audits for arithmetic and structural invariants.",
                "required_fields": ["callable", "pass"],
            },
        },
        "optional_solver": _optional_z3_status(),
        "invariants": [
            {
                "id": "canonical_resonant_kcs",
                "claim": "The canonical braid pair (5,7) yields k_CS = 74.",
                "claim_class": "discrete_winding_invariant",
                "verification_surface": ["python", "z3"],
                "artifact_path": "src/core/braided_winding.py",
                "regression_gate": "required",
            },
            {
                "id": "canonical_braided_sound_speed",
                "claim": "The canonical braided sound speed is exactly 12/37.",
                "claim_class": "braid_integer_invariant",
                "verification_surface": ["python", "lean4"],
                "artifact_path": "src/core/braided_winding.py",
                "regression_gate": "required",
            },
            {
                "id": "aps_half_class_for_nw5",
                "claim": "The APS η̄ spin-structure value for n_w=5 is 1/2.",
                "claim_class": "spin_structure_invariant",
                "verification_surface": ["python", "lean4"],
                "artifact_path": "src/core/aps_spin_structure.py",
                "regression_gate": "required",
            },
            {
                "id": "kcs_seven_condition_closure",
                "claim": "The completeness surface still reports all seven closure conditions at k_CS = 74.",
                "claim_class": "closure_surface_invariant",
                "verification_surface": ["python"],
                "artifact_path": "src/core/completeness_theorem.py",
                "regression_gate": "required",
            },
        ],
    }


def evaluate_formal_invariants() -> Dict[str, Any]:
    """Execute the focused non-regression invariant checks."""
    results: List[Dict[str, Any]] = []

    k_cs = resonant_kcs(CANONICAL_N1, CANONICAL_N2)
    results.append(
        {
            "id": "canonical_resonant_kcs",
            "verification_surface": "python",
            "observed": k_cs,
            "expected": CANONICAL_K_CS,
            "pass": k_cs == CANONICAL_K_CS,
        }
    )

    sound_speed_value = braided_sound_speed(CANONICAL_N1, CANONICAL_N2, k_cs)
    sound_speed_expected = float(CANONICAL_SOUND_SPEED)
    results.append(
        {
            "id": "canonical_braided_sound_speed",
            "verification_surface": "python",
            "observed": sound_speed_value,
            "expected_fraction": f"{CANONICAL_SOUND_SPEED.numerator}/{CANONICAL_SOUND_SPEED.denominator}",
            "pass": abs(sound_speed_value - sound_speed_expected) < 1e-12,
        }
    )

    eta_value = eta_bar_from_cs_inflow(CANONICAL_N1)
    results.append(
        {
            "id": "aps_half_class_for_nw5",
            "verification_surface": "python",
            "observed": eta_value,
            "expected": 0.5,
            "pass": abs(float(eta_value) - 0.5) < 1e-12,
        }
    )

    closure = kcs_seven_closure_conditions()
    closure_pass = len(closure) == 7 and all(int(item.get("k_cs_value", -1)) == CANONICAL_K_CS for item in closure)
    results.append(
        {
            "id": "kcs_seven_condition_closure",
            "verification_surface": "python",
            "observed": {"condition_count": len(closure), "all_equal_74": closure_pass},
            "expected": True,
            "pass": closure_pass,
        }
    )

    passed = all(bool(item.get("pass")) for item in results)
    return {
        "status": "FORMAL_INVARIANTS_PASS" if passed else "FORMAL_INVARIANTS_FAIL",
        "registry": formal_invariant_registry(),
        "results": results,
        "summary": {
            "checked_count": len(results),
            "pass_count": sum(1 for item in results if bool(item.get("pass"))),
            "all_pass": passed,
        },
        "guardrail": (
            "Passing this focused registry means the selected invariants did not regress. "
            "It does not imply total formal closure of the repository."
        ),
    }


__all__ = [
    "evaluate_formal_invariants",
    "formal_invariant_registry",
]
