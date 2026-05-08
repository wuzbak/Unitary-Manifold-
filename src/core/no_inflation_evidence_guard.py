# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""No-inflation evidence governance guard for status promotions."""
from __future__ import annotations

from typing import Dict, Iterable

__all__ = [
    "REQUIRED_PROMOTION_GATES",
    "evaluate_promotion_guard",
]

REQUIRED_PROMOTION_GATES = (
    "nominal_residual",
    "robustness",
    "axiomzero_purity",
)


def evaluate_promotion_guard(gates: Dict[str, bool], required: Iterable[str] = REQUIRED_PROMOTION_GATES) -> Dict:
    """Evaluate whether a status promotion is allowed.

    A promotion is allowed only if all required gates are present and True.
    """
    required = tuple(required)
    missing = [name for name in required if name not in gates]
    present = [name for name in required if name in gates]
    failing = [name for name in present if not bool(gates[name])]
    allow = (len(missing) == 0) and (len(failing) == 0)

    return {
        "allow_promotion": allow,
        "required_gates": list(required),
        "missing_required_gates": missing,
        "failing_required_gates": failing,
        "no_inflation_policy": "promotion_blocked_unless_all_required_gates_pass",
    }
