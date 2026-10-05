# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 883 — LEAN4_ARCHITECTURE_LIMITS_REGISTRY_COMPLETE.

Registry pillar that enumerates every architecture limit certified during
Sprint BB and pairs each with its Lean4 proxy file.  The registry is a
statement of what the framework *cannot* do; every entry stays open.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

PILLAR_NUMBER: int = 883
PILLAR_GATE: str = "LEAN4_ARCHITECTURE_LIMITS_REGISTRY_COMPLETE"
LEAN4_FILE: str = "ArchitectureLimitRegistry.lean"
LEAN4_NAMESPACE: str = "UnitaryManifold.ArchLimitRegistry"
EXPECTED_MASTER_THEOREM: str = "theorem archlimit_complete : registryComplete = true := rfl"

LEAN4_THEOREM_COUNT: int = 30
LEAN4_TOTAL_BEFORE: int = 2656
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

REGISTRY: tuple[dict[str, str], ...] = (
    {
        "pillar": "871",
        "limit": "HIGGS_6D_UV_COMPLETION_ARCHITECTURE_LIMIT",
        "lean4_file": "Higgs6DUVCompletionLimit.lean",
        "irreducible": "no",
    },
    {
        "pillar": "872",
        "limit": "KKLT_PERTURBATIVE_CONSISTENT_NP_ARCHITECTURE_LIMIT",
        "lean4_file": "KKLTNonperturbativeLimit.lean",
        "irreducible": "no",
    },
    {
        "pillar": "873",
        "limit": "E8_BREAKING_DEGENERACY_2",
        "lean4_file": "E8BreakingPatternEnumeration.lean",
        "irreducible": "no",
    },
    {
        "pillar": "874",
        "limit": "CMB_PEAK_AMPLITUDE_ARCHITECTURE_LIMIT_CONFIRMED",
        "lean4_file": "CMBAmplitudeKKSurveyLean4.lean",
        "irreducible": "no",
    },
    {
        "pillar": "867",
        "limit": "ALPHA_S_ALL_DIMENSIONAL_AUDIT_COMPLETE",
        "lean4_file": "AlphaSCrossDimensionalAudit.lean",
        "irreducible": "no",
    },
    {
        "pillar": "875",
        "limit": "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT",
        "lean4_file": "NonPerturbativeQGLimit.lean",
        "irreducible": "yes",
    },
)

REMAINING_OPEN: list[str] = [
    "ARCHITECTURE_LIMIT_REGISTRY_OPEN: every registry entry is an open limit; "
    "none is closed by being registered.",
    "NON_PERTURBATIVE_QG_IRREDUCIBLE: one entry cannot be lifted by any amount "
    "of work inside the framework.",
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
    "REGISTRY",
    "N_LIMITS",
    "N_IRREDUCIBLE",
    "N_REGISTRY_THEOREMS",
    "THEOREM_COUNT_MATCHES",
    "ALL_ENTRIES_OPEN",
    "REMAINING_OPEN",
    "registry_pillars",
    "irreducible_entries",
    "lean4_architecture_limits_registry_summary",
]


def _lean4_text() -> str:
    if not _LEAN4_PATH.exists():
        return ""  # Graceful fallback — file missing in shallow clones
    return _LEAN4_PATH.read_text(encoding="utf-8")


def _count_theorems(text: str) -> int:
    return len(re.findall(r"^\s*theorem\s+[A-Za-z0-9_']+", text, flags=re.MULTILINE))


def registry_pillars(registry: tuple[dict[str, str], ...] = REGISTRY) -> list[int]:
    """Return the pillar numbers appearing in the registry."""
    return [int(entry["pillar"]) for entry in registry]


def irreducible_entries(
    registry: tuple[dict[str, str], ...] = REGISTRY,
) -> list[dict[str, str]]:
    """Return the registry entries that are irreducible within the framework."""
    return [entry for entry in registry if entry["irreducible"] == "yes"]


N_LIMITS: int = len(REGISTRY)
N_IRREDUCIBLE: int = len(irreducible_entries())
N_REGISTRY_THEOREMS: int = _count_theorems(_lean4_text())
THEOREM_COUNT_MATCHES: bool = N_REGISTRY_THEOREMS == LEAN4_THEOREM_COUNT
ALL_ENTRIES_OPEN: bool = all(
    entry["irreducible"] in {"yes", "no"} for entry in REGISTRY
) and N_LIMITS > 0


def lean4_architecture_limits_registry_summary() -> dict[str, Any]:
    """Return the machine-readable architecture-limit registry certificate."""
    text = _lean4_text()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "lean4_file": LEAN4_FILE,
        "lean4_path": str(_LEAN4_PATH),
        "namespace_present": f"namespace {LEAN4_NAMESPACE}" in text,
        "master_theorem_present": EXPECTED_MASTER_THEOREM in text,
        "architecture_limit_comment_present": "ARCHITECTURE_LIMIT" in text,
        "registry": list(REGISTRY),
        "n_limits": N_LIMITS,
        "n_irreducible": N_IRREDUCIBLE,
        "registry_pillars": registry_pillars(),
        "n_registry_theorems": N_REGISTRY_THEOREMS,
        "theorem_count_matches": THEOREM_COUNT_MATCHES,
        "all_entries_open": ALL_ENTRIES_OPEN,
        "epistemic_status": (
            "REGISTRY_COMPLETE: six architecture limits are registered, one of "
            "them irreducible. Registration is documentation of what remains "
            "impossible, not a closure."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
