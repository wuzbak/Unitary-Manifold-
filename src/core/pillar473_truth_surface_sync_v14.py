# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 473 — truth-surface sync checker for v14.

STATUS
======
TRUTH_SURFACE_SYNC_V14_COMPLETE

CONTEXT
=======
This pillar performs a lightweight programmatic audit of the canonical
truth surfaces relevant to the v14.0 sprint.  It reads the repository
files directly and checks for expected v14 strings and status markers.

The checker is intentionally honest: a surface is marked unsynced if the
required v14 tokens are absent, even if the file still contains a valid
older record.  This allows tests to confirm both synced and unsynced
states without pretending the whole repository has already been updated.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, List

__all__ = [
    'PILLAR_STATUS',
    'VERSION',
    'V14_SYNC_MANIFEST',
    'check_truth_layer_sync',
    'check_fallibility_sync',
    'check_derivation_status_sync',
    'check_gatekeeper_sync',
    'check_claim_master_board_sync',
    'check_mas_tracker_sync',
    'full_sync_report',
    'sync_discrepancies',
    'pillar_report',
]

PILLAR_STATUS: str = 'TRUTH_SURFACE_SYNC_V14_COMPLETE'
VERSION: str = 'v14.0'
REPO_ROOT = Path(__file__).resolve().parents[2]

V14_SYNC_MANIFEST: Dict[str, Dict[str, Any]] = {
    'truth_layer': {
        'path': 'docs/TRUTH_LAYER.md',
        'required_tokens': ['v14', '455', '470'],
    },
    'fallibility': {
        'path': 'FALLIBILITY.md',
        'required_tokens': ['v14', '455', '470'],
    },
    'derivation_status': {
        'path': '1-THEORY/DERIVATION_STATUS.md',
        'required_tokens': [
            'v14.0', 'Pillar 455', 'Pillar 456', 'Pillar 457', 'Pillar 458', 'Pillar 459',
            'Pillar 460', 'Pillar 461', 'Pillar 462', 'Pillar 463', 'Pillar 464', 'Pillar 465',
            'Pillar 466', 'Pillar 467', 'Pillar 468', 'Pillar 469', 'Pillar 470', 'Pillar 471',
            'Pillar 472', 'Pillar 473', 'Pillar 474',
        ],
    },
    'gatekeeper': {
        'path': 'docs/GATEKEEPER_SUMMARY.md',
        'required_tokens': ['v14.0', 'P455', 'P456', 'P465', 'P467'],
    },
    'claim_master_board': {
        'path': 'docs/CLAIM_MASTER_BOARD.md',
        'required_tokens': ['v14', '455', '470'],
    },
    'mas_tracker': {
        'path': 'docs/mas_tracker.yml',
        'required_tokens': ['version: "v14.0"', '455: P8 integer-lattice proof', '474: arXiv v14 update package', 'next_pillar_slot: 475'],
    },
}


def _surface_status(name: str) -> Dict[str, Any]:
    spec = V14_SYNC_MANIFEST[name]
    full_path = REPO_ROOT / spec['path']
    exists = full_path.exists()
    text = full_path.read_text(encoding='utf-8', errors='replace') if exists else ''
    missing = [token for token in spec['required_tokens'] if token not in text]
    return {
        'surface': name,
        'path': spec['path'],
        'exists': exists,
        'required_tokens': list(spec['required_tokens']),
        'missing_tokens': missing,
        'synced': exists and not missing,
    }


def check_truth_layer_sync() -> Dict[str, Any]:
    """Check whether docs/TRUTH_LAYER.md carries the required v14 markers."""
    return _surface_status('truth_layer')


def check_fallibility_sync() -> Dict[str, Any]:
    """Check whether FALLIBILITY.md carries the required v14 markers."""
    return _surface_status('fallibility')


def check_derivation_status_sync() -> Dict[str, Any]:
    """Check whether DERIVATION_STATUS.md contains the v14 sprint insert."""
    return _surface_status('derivation_status')


def check_gatekeeper_sync() -> Dict[str, Any]:
    """Check whether GATEKEEPER_SUMMARY.md contains the v14 header note."""
    return _surface_status('gatekeeper')


def check_claim_master_board_sync() -> Dict[str, Any]:
    """Check whether CLAIM_MASTER_BOARD.md references the v14 sprint."""
    return _surface_status('claim_master_board')


def check_mas_tracker_sync() -> Dict[str, Any]:
    """Check whether docs/mas_tracker.yml contains the v14 sprint entry."""
    return _surface_status('mas_tracker')


def full_sync_report() -> Dict[str, Any]:
    """Return the combined v14 sync report across all monitored surfaces."""
    checks = {
        'truth_layer': check_truth_layer_sync(),
        'fallibility': check_fallibility_sync(),
        'derivation_status': check_derivation_status_sync(),
        'gatekeeper': check_gatekeeper_sync(),
        'claim_master_board': check_claim_master_board_sync(),
        'mas_tracker': check_mas_tracker_sync(),
    }
    synced_surfaces = [name for name, result in checks.items() if result['synced']]
    unsynced_surfaces = [name for name, result in checks.items() if not result['synced']]
    return {
        'version': VERSION,
        'checks': copy.deepcopy(checks),
        'n_surfaces': len(checks),
        'n_synced': len(synced_surfaces),
        'n_unsynced': len(unsynced_surfaces),
        'synced_surfaces': synced_surfaces,
        'unsynced_surfaces': unsynced_surfaces,
        'all_synced': not unsynced_surfaces,
    }


def sync_discrepancies() -> List[Dict[str, Any]]:
    """Return the unsynced surfaces together with their missing tokens."""
    report = full_sync_report()
    return [
        {
            'surface': name,
            'path': report['checks'][name]['path'],
            'missing_tokens': list(report['checks'][name]['missing_tokens']),
        }
        for name in report['unsynced_surfaces']
    ]


def pillar_report() -> Dict[str, Any]:
    """Return the complete Pillar 473 report."""
    return {
        'pillar': 473,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'manifest': copy.deepcopy(V14_SYNC_MANIFEST),
        'sync_report': full_sync_report(),
        'discrepancies': sync_discrepancies(),
    }


_PILLAR_STATUS: Dict[str, Any] = pillar_report()
