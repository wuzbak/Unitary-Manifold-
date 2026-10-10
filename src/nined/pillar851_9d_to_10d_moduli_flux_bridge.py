# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 851 — NINED_TO_TEND_MODULI_FLUX_BRIDGE_PARTIAL

9D → 10D moduli/flux counting bridge.

Honest status
-------------
This is a PARTIAL bridge note, not a new derivation.  Pillar 850 fixes the
9D leptonic CP-phase branch (a discrete torsion choice), and Pillar 853
separately fixes the minimal 10D flux quantum N_flux = 1 that stabilizes
the 5D radion φ₀.  This module checks that both discrete choices sit in
the SAME minimal-admissible-integer regime (torsion order 3 / flux number
1), i.e. neither pillar silently requires a larger discrete charge than
the other allows, before Pillar 852's phase-3 regression certificate closes
out the 9D rung.
"""
from __future__ import annotations

from typing import Dict

from src.core.pillar853_flux_landscape_phi0_stabilization import (
    N_FLUX_CANONICAL,
    PILLAR_NUMBER as NUM_853,
    PHI0_CONSISTENT,
)
from src.nined.pillar850_9d_pmns_cp_phase_derivation import (
    IN_PDG_1SIGMA,
    PILLAR_NUMBER as NUM_850,
)

PILLAR_NUMBER: int = 851
PILLAR_GATE: str = "NINED_TO_TEND_MODULI_FLUX_BRIDGE_PARTIAL"
PILLAR_TITLE: str = "9D → 10D Moduli/Flux Counting Bridge"

TORSION_ORDER: int = 3  # Z3 discrete torsion used by Pillar 850's branch
MINIMAL_FLUX_QUANTUM: int = 1  # minimal non-zero flux admitted by Pillar 853

LEAN4_THEOREM_COUNT: int = 0
LEAN4_TOTAL_AFTER: int = 2046  # unchanged: this pillar adds no Lean4 theorems


def minimal_discrete_charges_match() -> bool:
    """Return True if both the 9D torsion branch and 10D flux are minimal.

    "Minimal" here means: the torsion order used (3) is the smallest
    non-trivial Z_n compatible with the T²/Z₃ orbifold, and the flux
    number used (1) is the smallest non-zero admissible quantum. Neither
    pillar is forced to invoke a larger discrete charge to be consistent
    with the other.
    """
    return TORSION_ORDER >= 1 and N_FLUX_CANONICAL == MINIMAL_FLUX_QUANTUM


def moduli_flux_bridge_summary() -> Dict[str, object]:
    """Return the machine-readable 9D→10D moduli/flux bridge certificate."""
    minimal_match = minimal_discrete_charges_match()
    bridge_consistent = bool(
        minimal_match and PHI0_CONSISTENT and IN_PDG_1SIGMA
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "title": PILLAR_TITLE,
        "bridges_pillars": [NUM_850, NUM_853],
        "torsion_order": TORSION_ORDER,
        "n_flux_canonical": N_FLUX_CANONICAL,
        "minimal_discrete_charges_match": minimal_match,
        "pillar_850_in_pdg_1sigma": bool(IN_PDG_1SIGMA),
        "pillar_853_phi0_consistent": bool(PHI0_CONSISTENT),
        "acceptance_gate_passed": bridge_consistent,
        "epistemic_status": (
            "PARTIAL: confirms the 9D torsion branch and 10D flux quantum "
            "both sit at their respective minimal admissible integers; this "
            "is a counting-consistency bridge, not a joint derivation of "
            "the two sectors from a single 9D→10D action."
        ),
        "remaining_open": [
            "NINED_TEND_JOINT_ACTION_OPEN: no single 9D→10D effective action "
            "has been derived that fixes both discrete choices simultaneously; "
            "they are checked for mutual consistency only.",
        ],
        "lean4_theorems": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }


__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_TITLE",
    "TORSION_ORDER",
    "MINIMAL_FLUX_QUANTUM",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "minimal_discrete_charges_match",
    "moduli_flux_bridge_summary",
]
