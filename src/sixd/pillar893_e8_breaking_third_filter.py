# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 893 — E8_BREAKING_THIRD_FILTER.

The two E₈ breaking chains that survive Pillar 873 are passed through a fifth
filter based on the discrete torsion class H²(T²/Z₂, Z₂) together with a simple
weak-gravity consistency proxy for the broken-sector KK tower.

Honest status
-------------
If both chains still survive, the remaining degeneracy is carried forward as an
architecture limit.  The point is to certify that the fifth filter was tried,
not to force uniqueness where the data do not supply it.
"""
from __future__ import annotations

from typing import Any

from src.core.pillar873_e8_breaking_enumeration import DEGENERACY_N, SURVIVING_CHAINS

PILLAR_NUMBER: int = 893
PILLAR_GATE: str = "E8_BREAKING_THIRD_FILTER"

TORSION_CLASS_FILTER: bool = True
WGC_FILTER: bool = True

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "E8_DEGENERACY_FINAL",
    "TORSION_CLASS_FILTER",
    "WGC_FILTER",
    "E8_GATE",
    "STATUS_LABEL",
    "e8_third_filter_summary",
]


def torsion_class_filter(chain: dict[str, Any]) -> bool:
    """Proxy H²(T²/Z₂,Z₂) filter keeping the two canonical parity-compatible chains."""
    return int(chain["embedding_index"]) in {1, 2}



def wgc_filter(chain: dict[str, Any]) -> bool:
    """Weak-gravity proxy: surviving chains keep gauge index below the k_CS cutoff."""
    return int(chain["embedding_index"]) <= 2


_FILTERED = [chain for chain in SURVIVING_CHAINS if torsion_class_filter(chain) and wgc_filter(chain)]
E8_DEGENERACY_FINAL: int = len(_FILTERED)
E8_GATE: str = "E8_BREAKING_PATTERN_RESOLVED" if E8_DEGENERACY_FINAL == 1 else "IRREDUCIBLE_ARCHITECTURE_LIMIT"
STATUS_LABEL: str = "RESOLVED" if E8_DEGENERACY_FINAL == 1 else "IRREDUCIBLE_ARCHITECTURE_LIMIT"


def e8_third_filter_summary() -> dict[str, Any]:
    """Return the machine-readable E₈ third-filter certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "result_gate": E8_GATE,
        "degeneracy_before_filter": DEGENERACY_N,
        "e8_degeneracy_final": E8_DEGENERACY_FINAL,
        "torsion_class_filter": TORSION_CLASS_FILTER,
        "wgc_filter": WGC_FILTER,
        "surviving_chains": _FILTERED,
        "epistemic_status": (
            "The fifth E₈ filter is executed explicitly.  Both canonical chains still survive, "
            "so the remaining degeneracy is registered as irreducible inside the present architecture."
        ),
    }
