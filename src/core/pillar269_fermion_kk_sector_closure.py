# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 269 — Fermion KK sector closure packet.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

This packet consolidates the fermion-side KK reduction work:
- chiral zero mode and index theorem,
- orbifold chirality / Witten-obstruction resolution,
- 6D anchor elimination for c_L,
- explicit statement that the absolute light-generation hierarchy is still open.
"""
from __future__ import annotations

from typing import Dict

from src.core.chiral_fermion_orbifold import chiral_fermion_closure_status
from src.core.fermion_cL_spectrum_6d_audit import anchor_elimination_proof, wsa_gate_report
from src.core.fermion_cl_quantization import cl_constraints_from_braid
from src.core.fermion_emergence import PHI_0, dirac_kk_spectrum, index_theorem_check

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "fermion_zero_mode_gate",
    "fermion_anchor_elimination_gate",
    "fermion_kk_sector_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"


def fermion_zero_mode_gate(phi0: float = PHI_0) -> Dict[str, object]:
    """Check the executable zero-mode / KK-gap structure."""
    spectrum = dirac_kk_spectrum(phi0=phi0, n_modes=4)
    index = index_theorem_check()
    left_zero = spectrum["untwisted_L"][0]
    first_right = spectrum["untwisted_R"][0]
    first_twisted = spectrum["twisted"][0]
    gate_pass = (
        abs(left_zero) < 1e-15
        and first_right > 0.0
        and first_twisted > 0.0
        and bool(index["theorem_satisfied"])
    )
    return {
        "spectrum": spectrum,
        "index_theorem": index,
        "gate_pass": gate_pass,
        "evidence": (
            "Massless left-handed zero mode survives, right-handed zero mode is "
            "absent, twisted sector is gapped, and the index theorem is satisfied."
        ),
    }


def fermion_anchor_elimination_gate() -> Dict[str, object]:
    """Check how far the 6D c_L program removes fitted fermion anchors."""
    elimination = anchor_elimination_proof()
    free_before = elimination["before_6d"]["free_params"]
    free_after = elimination["after_6d"]["free_params"]
    return {
        "anchor_elimination": elimination,
        "gate_pass": free_after < free_before,
        "free_parameter_reduction": free_before - free_after,
    }


def fermion_kk_sector_report() -> Dict[str, object]:
    """Return the consolidated fermion-side KK reduction status."""
    zero_mode = fermion_zero_mode_gate()
    chiral = chiral_fermion_closure_status()
    braid_constraints = cl_constraints_from_braid()
    anchor_gate = fermion_anchor_elimination_gate()
    wsa = wsa_gate_report()

    substantially_closed = (
        bool(zero_mode["gate_pass"])
        and chiral["new_status"].startswith("✅ RESOLVED")
        and bool(anchor_gate["gate_pass"])
    )

    return {
        "pillar": 269,
        "title": "Fermion KK sector closure packet",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "zero_mode_gate": zero_mode,
        "chiral_orbifold_status": chiral,
        "braid_cL_constraints": braid_constraints,
        "anchor_elimination_gate": anchor_gate,
        "wsa_gate_report": wsa,
        "fermion_zero_mode_closed": bool(zero_mode["gate_pass"]),
        "fermion_hierarchy_fully_closed": bool(wsa["gate_passed"]),
        "status": (
            "BOSONIC_CLOSED_FERMION_ZERO_MODE_CLOSED_HIERARCHY_OPEN"
            if substantially_closed and not wsa["gate_passed"]
            else "FERMION_TRACK_OPEN"
        ),
        "remaining_open": (
            "Exact absolute fermion mass hierarchy and the final Yukawa-scale "
            "anchors remain open even though chirality, index, orbifold routing, "
            "and c_L anchor reduction are now executable."
        ),
    }
