# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 875 — NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT

Certification that the non-perturbative quantum-gravity sector is an
*irreducible* limit of the Unitary Manifold architecture, not a gap that more
work inside the framework can close.

The framework is a classical 5D Kaluza-Klein geometry with a one-loop
effective description.  Four independent obstructions are registered:

    O1 PERTURBATIVE_EFT_ONLY   — the action is a two-derivative EFT; the
                                 curvature expansion is truncated.
    O2 NO_UV_MEASURE           — no path-integral measure over 5D metrics is
                                 defined.
    O3 NO_BACKGROUND_INDEPENDENCE — the KK ansatz fixes the topology S¹ × M₄.
    O4 NO_TRANSPLANCKIAN_STATES — states above M_pl are outside the EFT.

Each obstruction is paired with the external programme that would be required
to lift it (lattice quantum gravity, loop quantum gravity, asymptotic safety,
or a full string/M-theory UV completion).  None of these are supplied here.

Honest status
-------------
IRREDUCIBLE.  This pillar closes nothing.  It states precisely what the
framework cannot do and what external input would be needed.
"""
from __future__ import annotations

from typing import Any

PILLAR_NUMBER: int = 875
PILLAR_GATE: str = "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT"
LIMIT_CERTIFICATE: str = "IRREDUCIBLE_ARCHITECTURE_LIMIT"

LEAN4_THEOREM_COUNT: int = 15
LEAN4_TOTAL_BEFORE: int = 2516
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

OBSTRUCTIONS: tuple[dict[str, str], ...] = (
    {
        "code": "O1_PERTURBATIVE_EFT_ONLY",
        "statement": "The 5D action is a truncated two-derivative EFT; higher "
        "curvature operators are not resummed.",
        "required_external_programme": "ASYMPTOTIC_SAFETY",
        "reducible_within_framework": "no",
    },
    {
        "code": "O2_NO_UV_MEASURE",
        "statement": "No path-integral measure over 5D metrics is defined, so "
        "the gravitational partition function is not computable.",
        "required_external_programme": "LATTICE_QUANTUM_GRAVITY",
        "reducible_within_framework": "no",
    },
    {
        "code": "O3_NO_BACKGROUND_INDEPENDENCE",
        "statement": "The KK ansatz fixes the topology S¹ × M₄; topology change "
        "and spin-foam sums are excluded by construction.",
        "required_external_programme": "LOOP_QUANTUM_GRAVITY",
        "reducible_within_framework": "no",
    },
    {
        "code": "O4_NO_TRANSPLANCKIAN_STATES",
        "statement": "States above M_pl (including black-hole microstates) lie "
        "outside the effective description.",
        "required_external_programme": "STRING_M_THEORY_UV_COMPLETION",
        "reducible_within_framework": "no",
    },
)

EXTERNAL_PROGRAMMES: tuple[str, ...] = (
    "ASYMPTOTIC_SAFETY",
    "LATTICE_QUANTUM_GRAVITY",
    "LOOP_QUANTUM_GRAVITY",
    "STRING_M_THEORY_UV_COMPLETION",
)

REMAINING_OPEN: list[str] = [
    "NON_PERTURBATIVE_QG_OPEN: irreducible within this framework; requires an "
    "external UV-complete quantum-gravity programme.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LIMIT_CERTIFICATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "OBSTRUCTIONS",
    "EXTERNAL_PROGRAMMES",
    "N_OBSTRUCTIONS",
    "ALL_IRREDUCIBLE",
    "PROGRAMMES_DISTINCT",
    "REMAINING_OPEN",
    "obstruction_codes",
    "is_reducible",
    "required_programmes",
    "nonperturbative_qg_limit_summary",
]


def obstruction_codes(
    obstructions: tuple[dict[str, str], ...] = OBSTRUCTIONS,
) -> list[str]:
    """Return the ordered obstruction codes."""
    return [entry["code"] for entry in obstructions]


def is_reducible(obstruction: dict[str, str]) -> bool:
    """Return True only if an obstruction is reducible inside the framework."""
    return obstruction["reducible_within_framework"] == "yes"


def required_programmes(
    obstructions: tuple[dict[str, str], ...] = OBSTRUCTIONS,
) -> list[str]:
    """Return the external programmes required to lift each obstruction."""
    return [entry["required_external_programme"] for entry in obstructions]


N_OBSTRUCTIONS: int = len(OBSTRUCTIONS)
ALL_IRREDUCIBLE: bool = not any(is_reducible(entry) for entry in OBSTRUCTIONS)
PROGRAMMES_DISTINCT: bool = len(set(required_programmes())) == N_OBSTRUCTIONS


def nonperturbative_qg_limit_summary() -> dict[str, Any]:
    """Return the machine-readable irreducible quantum-gravity certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "limit_certificate": LIMIT_CERTIFICATE,
        "obstructions": list(OBSTRUCTIONS),
        "n_obstructions": N_OBSTRUCTIONS,
        "external_programmes": list(EXTERNAL_PROGRAMMES),
        "all_irreducible": ALL_IRREDUCIBLE,
        "programmes_distinct": PROGRAMMES_DISTINCT,
        "epistemic_status": (
            "IRREDUCIBLE: four independent obstructions place the "
            "non-perturbative quantum-gravity sector permanently outside the "
            "Unitary Manifold architecture. No internal work can close it."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
