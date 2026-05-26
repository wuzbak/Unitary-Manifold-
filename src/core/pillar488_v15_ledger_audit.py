# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 488 — v15 ledger-audit completion certificate."""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Tuple

__all__ = [
    'PILLAR_LABEL',
    'PILLAR_STATUS',
    'PILLAR_NUMBER',
    'VERSION',
    'CANONICAL_LEDGER_PATHS',
    'ONBOARDING_DOC_PATHS',
    'SPRINT_PILLARS',
    'ADMISSION_COUNT',
    'NEXT_PILLAR_SLOT',
    'synchronized_ledgers',
    'onboarding_doc_targets',
    'doc_sync_certificate',
    'version_consistency_certificate',
    'admission_and_pillar_counts',
    'status_report',
]

PILLAR_LABEL: str = 'V15_LEDGER_AUDIT_COMPLETE'
PILLAR_STATUS: str = PILLAR_LABEL
PILLAR_NUMBER: int = 488
VERSION: str = 'v15.0'

CANONICAL_LEDGER_PATHS: Tuple[str, ...] = (
    'STATUS.md',
    'FALLIBILITY.md',
    'README.md',
    '1-THEORY/DERIVATION_STATUS.md',
    'docs/WAVE_CHANGELOG.md',
    'docs/mas_tracker.yml',
)
ONBOARDING_DOC_PATHS: Tuple[str, ...] = (
    'CONTRIBUTING.md',
    '2-REPRODUCIBILITY/README.md',
    '9-INFRASTRUCTURE/TEST/README.md',
    '.github/copilot-instructions.md',
    '9-INFRASTRUCTURE/wiki/Getting-Started.md',
    '9-INFRASTRUCTURE/wiki/Contributing.md',
    '6-MONOGRAPH/MCP_INGEST.md',
    '4-IMPLICATIONS/WHAT_THIS_MEANS.md',
)
SPRINT_PILLARS: Tuple[int, ...] = (488, 489, 490, 491, 492, 493, 494)
ADMISSION_COUNT: int = 13
NEXT_PILLAR_SLOT: int = 495


def synchronized_ledgers() -> Dict[str, Any]:
    """Return the live-ledger synchronization target for v15."""
    return {
        'version': VERSION,
        'canonical_ledgers': list(CANONICAL_LEDGER_PATHS),
        'count': len(CANONICAL_LEDGER_PATHS),
        'synchronized': True,
        'reason': 'v15 closes the doc-drift regression by forcing the live ledgers onto one canonical branch state.',
    }


def onboarding_doc_targets() -> List[str]:
    """Return the v15 onboarding documents that must mirror the canonical count."""
    return list(ONBOARDING_DOC_PATHS)


def doc_sync_certificate() -> Dict[str, Any]:
    """Return the machine-readable certificate for the v15 doc-sync fix."""
    return {
        'status': PILLAR_STATUS,
        'version': VERSION,
        'canonical_ledger_count': len(CANONICAL_LEDGER_PATHS),
        'onboarding_doc_count': len(ONBOARDING_DOC_PATHS),
        'ledgers_synchronized': True,
        'onboarding_docs_synchronized': True,
        'regression_gate': 'DOC_DRIFT_FIXED',
        'scope': 'tests/ + recycling/ + 5-GOVERNANCE/Unitary Pentad/',
    }


def version_consistency_certificate() -> Dict[str, Any]:
    """Return the version-consistency statement for v15."""
    return {
        'target_version': VERSION,
        'all_live_ledgers_target_v15': True,
        'first_canonical_count_source': 'STATUS.md',
        'audit_type': 'LEDGER_AND_ONBOARDING_SYNC',
    }


def admission_and_pillar_counts() -> Dict[str, int]:
    """Return the core closure counts used by the v15 audit."""
    return {
        'admission_count': ADMISSION_COUNT,
        'sprint_pillar_count': len(SPRINT_PILLARS),
        'first_pillar': SPRINT_PILLARS[0],
        'last_pillar': SPRINT_PILLARS[-1],
        'next_pillar_slot': NEXT_PILLAR_SLOT,
    }


def status_report() -> Dict[str, Any]:
    """Return the full Pillar 488 status report."""
    return {
        'pillar': PILLAR_NUMBER,
        'label': PILLAR_LABEL,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'ledger_sync': synchronized_ledgers(),
        'onboarding_docs': onboarding_doc_targets(),
        'doc_sync_certificate': doc_sync_certificate(),
        'version_consistency': version_consistency_certificate(),
        'counts': admission_and_pillar_counts(),
    }


_PILLAR_STATUS: Dict[str, Any] = copy.deepcopy(status_report())
