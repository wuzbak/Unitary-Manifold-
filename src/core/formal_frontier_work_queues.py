# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Dedicated work-queue builders for the current formal frontier."""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.action_to_evolution_retirement_units import (
    build_action_to_evolution_retirement_units,
)

_LANE_A_WORK_QUEUES: Dict[str, List[Dict[str, Any]]] = {
    "APS_ETA_AXIOM_HALF_CLASS": [
        {
            "claim_id": "APS_HALF_CLASS_VALUE",
            "title": "η-class value classification",
            "lean_target": "UnitaryManifold.NWUniquenessHonest",
            "status": "CONDITIONAL_ONLY",
            "retirement_condition": "Replace the named APS axiom with a genuine formalized boundary-operator statement or keep it explicit as external frontier.",
            "current_reason": "The half-class selection is named honestly, but APS index theory is not yet formalized in Mathlib.",
        },
        {
            "claim_id": "APS_ZERO_CLASS_EXCLUSION",
            "title": "η = 0 exclusion branch",
            "lean_target": "UnitaryManifold.NWUniquenessHonest",
            "status": "CONDITIONAL_ONLY",
            "retirement_condition": "Show why the excluded η-class follows from the stated boundary machinery rather than from an arithmetic proxy.",
            "current_reason": "The current Lean surface keeps the class split explicit but still axiom-level.",
        },
    ],
    "APS_MATHLIB_FORMALIZATION_GAP": [
        {
            "claim_id": "APS_BOUNDARY_OPERATOR_SURFACE",
            "title": "Boundary operator surface",
            "lean_target": "UnitaryManifold.NWUniquenessHonest",
            "status": "BLOCKED_NOT_YET_DERIVABLE",
            "retirement_condition": "Define the manifolds-with-boundary and Dirac spectral objects needed for APS statements.",
            "current_reason": "This remains a Mathlib frontier, not a hidden local failure.",
        },
        {
            "claim_id": "NGEN_DEPENDENCY_BOUNDARY",
            "title": "N_gen dependency boundary",
            "lean_target": "UnitaryManifold.NWUniquenessHonest",
            "status": "BLOCKED_NOT_YET_DERIVABLE",
            "retirement_condition": "Either derive N_gen = 3 from admissible geometry or keep it isolated as external input.",
            "current_reason": "The repository is already honest that N_gen = 3 is not derived from first principles here.",
        },
    ],
    "DIRAC_ORBIFOLD_PROXY_BOUNDARY": [
        {
            "claim_id": "ORBIFOLD_PARITY_FACTS",
            "title": "Orbifold parity facts",
            "lean_target": "UnitaryManifold.DiracOrbifoldSpectrum",
            "status": "CONDITIONAL_ONLY",
            "retirement_condition": "Promote only the parity facts that can be stated independently of the full spectral proof.",
            "current_reason": "Some parity structure is isolatable even while the analytic boundary-value proof remains absent.",
        },
        {
            "claim_id": "DIRAC_SPECTRUM_STRUCTURAL_LEMMAS",
            "title": "Dirac-spectrum structural lemmas",
            "lean_target": "UnitaryManifold.DiracOrbifoldSpectrum",
            "status": "BLOCKED_NOT_YET_DERIVABLE",
            "retirement_condition": "Separate genuine operator/spectrum lemmas from arithmetic stand-ins and promote only the former.",
            "current_reason": "The file is still explicitly classified as arithmetic proxy only.",
        },
    ],
}


def build_frontier_work_queue(row_id: str) -> List[Dict[str, Any]]:
    """Return the work queue for a traceability row."""
    if row_id == "ACTION_TO_EVOLUTION_BOUNDARY":
        return build_action_to_evolution_retirement_units()
    return [dict(item) for item in _LANE_A_WORK_QUEUES.get(row_id, [])]


__all__ = ["build_frontier_work_queue"]
