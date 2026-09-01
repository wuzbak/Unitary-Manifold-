# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 869 — NGEN_6D_BUNDLE_DEGENERACY_COMPUTED

Degeneracy audit of the Pillar 868 admissible bundle set.

Two further physical filters are applied to the c₁ = 3 candidates:

    F1  Z₂ parity      — the T²/Z₂ projection keeps chiral zero modes only for
                         odd line-bundle flux m.
    F2  charge bound   — the U(1) charge must actually occur in the SU(5)
                         branching of the E₈ adjoint, i.e. 1 ≤ |q| ≤ 4.

The point of this pillar is the *negative* result: the filters do not reduce
the admissible set to a single bundle.  The residual degeneracy N is reported
verbatim, and N = 1 is explicitly not claimed.
"""
from __future__ import annotations

from typing import Any

from src.sixd.pillar868_ngen_e8_adjoint_restriction import (
    ADMISSIBLE_BUNDLES,
    N_ADMISSIBLE,
    TARGET_C1,
)

PILLAR_NUMBER: int = 869
PILLAR_GATE: str = "NGEN_6D_BUNDLE_DEGENERACY_COMPUTED"

LEAN4_THEOREM_COUNT: int = 20
LEAN4_TOTAL_BEFORE: int = 2386
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

MAX_U1_CHARGE: int = 4

FILTERS: tuple[str, ...] = (
    "F1_Z2_PARITY_ODD_FLUX",
    "F2_E8_CHARGE_BOUND",
)

REMAINING_OPEN: list[str] = [
    "NGEN_6D_BUNDLE_SPECIFICATION_OPEN: c₁ = 3 remains degenerate after the "
    "available 6D filters; a UV commitment is required to pick one bundle.",
    "NGEN_6D_STABILITY_OPEN: slope-stability (Donaldson-Uhlenbeck-Yau) of the "
    "surviving bundles is not verified here.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "MAX_U1_CHARGE",
    "FILTERS",
    "SURVIVING_BUNDLES",
    "DEGENERACY_N",
    "DEGENERACY_IS_ONE",
    "FILTER_REDUCTION",
    "REMAINING_OPEN",
    "z2_parity_filter",
    "charge_bound_filter",
    "apply_filters",
    "ngen_uniqueness_audit_summary",
]


def z2_parity_filter(bundle: dict[str, Any]) -> bool:
    """Return True when the flux is odd (Z₂-even chiral zero modes survive)."""
    return int(bundle["flux"]) % 2 == 1


def charge_bound_filter(bundle: dict[str, Any], max_charge: int = MAX_U1_CHARGE) -> bool:
    """Return True when |q| occurs in the E₈ adjoint branching."""
    return 1 <= abs(int(bundle["u1_charge"])) <= max_charge


def apply_filters(bundles: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Return the bundles surviving both physical filters."""
    source = ADMISSIBLE_BUNDLES if bundles is None else bundles
    return [b for b in source if z2_parity_filter(b) and charge_bound_filter(b)]


SURVIVING_BUNDLES: list[dict[str, Any]] = apply_filters()
DEGENERACY_N: int = len(SURVIVING_BUNDLES)
DEGENERACY_IS_ONE: bool = DEGENERACY_N == 1
FILTER_REDUCTION: int = N_ADMISSIBLE - DEGENERACY_N
ALL_SURVIVORS_HAVE_TARGET_C1: bool = all(int(b["c1"]) == TARGET_C1 for b in SURVIVING_BUNDLES)


def ngen_uniqueness_audit_summary() -> dict[str, Any]:
    """Return the machine-readable bundle degeneracy certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "target_c1": TARGET_C1,
        "n_admissible_before_filters": N_ADMISSIBLE,
        "filters": list(FILTERS),
        "surviving_bundles": SURVIVING_BUNDLES,
        "degeneracy_n": DEGENERACY_N,
        "degeneracy_is_one": DEGENERACY_IS_ONE,
        "filter_reduction": FILTER_REDUCTION,
        "all_survivors_have_target_c1": ALL_SURVIVORS_HAVE_TARGET_C1,
        "epistemic_status": (
            f"DEGENERACY_COMPUTED: N = {DEGENERACY_N} bundles reproduce c₁ = 3 after "
            "all available 6D filters. Uniqueness is not claimed and the gap stays open."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
