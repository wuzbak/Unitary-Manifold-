# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 788 — v23 Sprint Regression Certificate.

Locks the v23 sprint state: test count, Lean4 theorem count, pillar slots,
and all new pillar epistemic gates introduced in this sprint.

Epistemic gate: V23_REGRESSION_CERTIFICATE_ISSUED
This module cannot import from Pillars 786 or 787 to avoid circular deps;
it holds snapshot constants only.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR",
    "VERSION",
    "STATUS",
    "SPRINT_NAME",
    "SPRINT_DATE",
    "TESTS_PASSED_FLOOR",
    "LEAN4_THEOREMS_FLOOR",
    "NEXT_PILLAR_SLOT",
    "V23_PILLARS",
    "V23_EPISTEMIC_GATES",
    "regression_certificate_summary",
    "TEST_EXPECTATIONS",
]

PILLAR: int = 788
VERSION: str = "v23.0"
STATUS: str = "V23_REGRESSION_CERTIFICATE_ISSUED"
SPRINT_NAME: str = "v23 — The Living Theory"
SPRINT_DATE: str = "2026-08-20"

# ── Regression floor constants ─────────────────────────────────────────────
# These are the *minimum acceptable* values — actual counts may be higher
# because other v23 work (application tests, subtrack tests) adds to them.
TESTS_PASSED_FLOOR: int = 57_124   # from STATUS.md v23.0 baseline
LEAN4_THEOREMS_FLOOR: int = 1006   # from STATUS.md v23.0 baseline
NEXT_PILLAR_SLOT: int = 789

# ── v23 pillar inventory ───────────────────────────────────────────────────
V23_PILLARS: List[Dict[str, Any]] = [
    {
        "pillar": 786,
        "name": "Winding Resonance Stability Basin",
        "gate": "WINDING_BASIN_CLOSED",
        "result": "n_w=5 is the unique winding number in [1,15] satisfying all observational constraints",
    },
    {
        "pillar": 787,
        "name": "Falsification Boundary Map",
        "gate": "FALSIFICATION_MAP_REGISTERED",
        "result": "7 experiments pre-registered with locked verdict thresholds",
    },
    {
        "pillar": 788,
        "name": "v23 Sprint Regression Certificate",
        "gate": "V23_REGRESSION_CERTIFICATE_ISSUED",
        "result": "Sprint locked: tests ≥57,124, Lean4 ≥1006, next slot 789",
    },
]

# ── Epistemic gate snapshot ────────────────────────────────────────────────
V23_EPISTEMIC_GATES: Dict[str, str] = {
    "P786_STABILITY_BASIN": "WINDING_BASIN_CLOSED",
    "P787_FALSIFICATION_MAP": "FALSIFICATION_MAP_REGISTERED",
    "P788_REGRESSION": "V23_REGRESSION_CERTIFICATE_ISSUED",
    # Carried forward from v22.11
    "P785_G4_CRITERION2": "G4_CRITERION2_HIGGS_CMB_CROSS_SECTOR_CORRELATION",
    "P784_TYPE_AB": "TYPE_AB_CLASSIFICATION_COMPLETE",
    "P782_ALPHA_S": "ALPHA_S_NSVZ_KK_DERIVED",
    "P781_FN_CHARGES": "FN_CHARGE_GEOMETRIC_REDUCTION_QUANTIFIED",
    "P773_DM21_NLO": "DM21_NLO_PARTIAL_CLOSURE",
    "P772_LEPTON_JL": "LEPTON_JARLSKOG_LATTICE_DERIVED",
}

# ── v23 Application deliverable ────────────────────────────────────────────
V23_APPLICATION: Dict[str, Any] = {
    "name": "Axiom Zero Interrogator",
    "product_id": "18",
    "html": "public-site/az-apps/18-interrogator.html",
    "js": "public-site/js/18-interrogator.js",
    "kb": "public-site/data/interrogator-kb.json",
    "kb_builder": "TOOLS/build_interrogator_kb.py",
    "tests": "tests/test_interrogator.py",
    "description": (
        "A fully offline, self-contained Theory Interrogation Engine. "
        "Three modes: Challenge (claim → epistemic status + falsification condition), "
        "Experiment (experiment → all pillars it tests), "
        "Tension Map (interactive canvas of all open tensions). "
        "No server, no API keys. Single HTML+JS app."
    ),
}


def regression_certificate_summary() -> Dict[str, Any]:
    """Return the full v23 regression certificate."""
    return {
        "pillar": PILLAR,
        "version": VERSION,
        "status": STATUS,
        "sprint_name": SPRINT_NAME,
        "sprint_date": SPRINT_DATE,
        "tests_passed_floor": TESTS_PASSED_FLOOR,
        "lean4_theorems_floor": LEAN4_THEOREMS_FLOOR,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "v23_pillars": V23_PILLARS,
        "v23_epistemic_gates": V23_EPISTEMIC_GATES,
        "v23_application": V23_APPLICATION,
        "invariant": "0 test failures is a hard requirement at all times.",
    }


TEST_EXPECTATIONS: Dict[str, Any] = {
    "pillar": 788,
    "status": "V23_REGRESSION_CERTIFICATE_ISSUED",
    "tests_passed_floor": 57124,
    "lean4_floor": 1006,
    "next_slot": 789,
    "v23_pillar_count": 3,
    "all_gates_present": True,
}
