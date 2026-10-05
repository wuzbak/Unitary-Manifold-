# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 882 — LEAN4_CKM_PMNS_UNIFIED_THEOREM.

Consolidation pillar for the unified quark (7D) and lepton (9D) flavour
sectors.  The Lean4 proxy file records the shared discrete-torsion origin of
both CP phases together with the honest status of each sector: the PMNS phase
agrees with the global fit within 1σ, while the CKM mixing angles remain in
tension.  No agreement is asserted that the numerics do not support.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

PILLAR_NUMBER: int = 882
PILLAR_GATE: str = "LEAN4_CKM_PMNS_UNIFIED_THEOREM"
LEAN4_FILE: str = "CKMPMNSUnifiedDerivation.lean"
LEAN4_NAMESPACE: str = "UnitaryManifold.CKMPMNSUnified"
EXPECTED_MASTER_THEOREM: str = "theorem ckmpmns_unified : unified = true := rfl"

LEAN4_THEOREM_COUNT: int = 50
LEAN4_TOTAL_BEFORE: int = 2606
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

QUARK_SECTOR_DIMENSION: int = 7
LEPTON_SECTOR_DIMENSION: int = 9
N_SECTORS: int = 2

REMAINING_OPEN: list[str] = [
    "CKM_ANGLE_TENSION_OPEN: the geometric CKM angles do not reproduce the PDG "
    "ordering; the unification is structural, not numerical.",
    "FLAVOUR_SUBLEADING_CHARGE_OPEN: sub-leading bulk charge data is unknown in "
    "both the quark and lepton sectors.",
]

_LEAN4_PATH = Path(__file__).resolve().parents[2] / "lean4" / "UnitaryManifold" / LEAN4_FILE

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_FILE",
    "LEAN4_NAMESPACE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "N_UNIFIED_THEOREMS",
    "THEOREM_COUNT_MATCHES",
    "QUARK_SECTOR_DIMENSION",
    "LEPTON_SECTOR_DIMENSION",
    "N_SECTORS",
    "REMAINING_OPEN",
    "lean4_ckm_pmns_unified_summary",
]


def _lean4_text() -> str:
    if not _LEAN4_PATH.exists():
        return ""  # Graceful fallback — file missing in shallow clones
    return _LEAN4_PATH.read_text(encoding="utf-8")


def _count_theorems(text: str) -> int:
    return len(re.findall(r"^\s*theorem\s+[A-Za-z0-9_']+", text, flags=re.MULTILINE))


N_UNIFIED_THEOREMS: int = _count_theorems(_lean4_text())
THEOREM_COUNT_MATCHES: bool = N_UNIFIED_THEOREMS == LEAN4_THEOREM_COUNT


def lean4_ckm_pmns_unified_summary() -> dict[str, Any]:
    """Return the machine-readable unified CKM/PMNS Lean4 certificate."""
    text = _lean4_text()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "lean4_file": LEAN4_FILE,
        "lean4_path": str(_LEAN4_PATH),
        "namespace_present": f"namespace {LEAN4_NAMESPACE}" in text,
        "master_theorem_present": EXPECTED_MASTER_THEOREM in text,
        "architecture_limit_comment_present": "ARCHITECTURE_LIMIT" in text,
        "n_unified_theorems": N_UNIFIED_THEOREMS,
        "theorem_count_matches": THEOREM_COUNT_MATCHES,
        "quark_sector_dimension": QUARK_SECTOR_DIMENSION,
        "lepton_sector_dimension": LEPTON_SECTOR_DIMENSION,
        "n_sectors": N_SECTORS,
        "epistemic_status": (
            "PARTIAL_CLOSURE: the two flavour sectors share one discrete-torsion "
            "origin, but only the leptonic CP phase agrees with data; the CKM "
            "angle tension is carried forward unresolved."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
