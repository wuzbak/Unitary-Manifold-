# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Lean4 theorem index helpers for OX Navigator."""
from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_LIVE_STATUS_PATH = _REPO_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"


def _load_live_status_theorem_count() -> int:
    try:
        payload = json.loads(_LIVE_STATUS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 2186
    lean4 = payload.get("lean4") if isinstance(payload, dict) else {}
    count = lean4.get("theorem_count") if isinstance(lean4, dict) else None
    return count if isinstance(count, int) and count >= 0 else 2186


LEAN4_THEOREM_COUNT = _load_live_status_theorem_count()
LEAN4_THEOREM_SAMPLE = [
    'APS_T2Z2_NgenBridge',
    'APSEtaInvariantBridge',
    'APSEtaInvariantScaffold',
    'AlphaSNLOWindingAudit',
    'AlphaSNSVZClosure',
    'BirefringenceACTDR6',
    'BraidUniqueness',
    'BraidUniquenessAlgebraic',
    'CKM7DMixingAngles',
    'CKMFullUnitarityMatrix',
    'CKMRhoBarClosure',
    'CKMVubNLO',
    'CosmologicalConstantKK',
    'DESIWaNogo',
    'DesiDR2FalsificationBoundary',
    'DesiDR3PreRegistration',
    'DimensionalChainClosure',
    'DimensionalChainUniqueness',
    'DiracOrbifoldSpectrum',
    'MasterTheoremDimensionalChain',
]

PILLAR_THEOREM_INDEX: dict[int, list[str]] = {
    837: ['DiracOrbifoldSpectrum', 'NgenKawamuraBridge'],
    838: ['HiggsArchitectureLimit', 'HiggsCW5DClosure', 'HiggsGHUNLOBound'],
    839: ['APS_T2Z2_NgenBridge', 'APSEtaInvariantBridge', 'APSEtaInvariantScaffold'],
    840: ['DimensionalChainClosure', 'DimensionalChainUniqueness'],
    841: [],
    842: ['DiracOrbifoldSpectrum', 'APS_T2Z2_NgenBridge', 'DimensionalChainClosure'],
    843: ['CKM7DMixingAngles', 'CKMFullUnitarityMatrix', 'CKMRhoBarClosure', 'CKMVubNLO'],
    844: ['AlphaSNSVZClosure', 'AlphaSNLOWindingAudit'],
    845: [],
    846: ['CKM7DMixingAngles', 'AlphaSNSVZClosure'],
    847: [],
    848: [],
    849: ['GS9DAnomalyBridge'],
    850: ['PMNSDeltaCPNLO', 'PMNSSolarAngleBound', 'PMNSRationalBounds'],
    851: [],
    852: ['GS9DAnomalyBridge', 'PMNSDeltaCPNLO'],
    853: [],
    854: [],
    855: ['SwamplandAxiom', 'SwamplandConsistencyAudit'],
    856: ['SwamplandConsistencyAudit'],
    857: [],
    858: ['DimensionalChainClosure', 'DimensionalChainUniqueness'],
    859: ['MasterTheoremDimensionalChain'],
    860: ['DimensionalChainClosure', 'MasterTheoremDimensionalChain'],
}

__all__ = [
    'LEAN4_THEOREM_COUNT',
    'LEAN4_THEOREM_SAMPLE',
    'search_theorems',
    'get_theorem_count',
    'get_theorems_by_pillar',
]


def search_theorems(query: str, theorems: list[str] | None = None) -> list[str]:
    """Return simple case-insensitive substring matches."""
    haystack = list(theorems) if theorems is not None else list(LEAN4_THEOREM_SAMPLE)
    needle = (query or '').strip().lower()
    if not needle:
        return haystack
    return [theorem for theorem in haystack if needle in theorem.lower()]


def get_theorem_count() -> int:
    """Return the registered Lean4 theorem total."""
    return LEAN4_THEOREM_COUNT


def get_theorems_by_pillar(pillar_id: int) -> list[str]:
    """Return theorem names associated with a pillar in the lightweight index."""
    return list(PILLAR_THEOREM_INDEX.get(pillar_id, []))
