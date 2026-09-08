# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1094 — Enterprise runtime deployment hardening."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.pillar1093_validation_resilience_scoped_security import PILLAR_VALID as P1093_VALID
from src.core.pillar1089_sprint_co_master_evolution_matrix import SPRINT, VERSION, build_truth_surface_sync_status

PILLAR_NUMBER: int = 1094
PILLAR_GATE: str = 'ENTERPRISE_RUNTIME_DEPLOYMENT_HARDENING'
PILLAR_STATUS: str = 'ENTERPRISE_RUNTIME_DEPLOYMENT_HARDENING_COMPLETE'
NEXT_PILLAR_SLOT: int = 1095
_ROOT = Path(__file__).resolve().parents[2]

_RUNTIME_PATHS = {
    'live_status_generator': _ROOT / '9-INFRASTRUCTURE' / 'generate_live_status.py',
    'assistant_api': _ROOT / 'bot' / 'assistant_api.py',
    'psicat_readme': _ROOT / '12-AZ-IP' / '20-psicat-navigator' / 'README.md',
    'validation_packet': _ROOT / '12-AZ-IP' / '20-psicat-navigator' / 'PSICAT_VALIDATION_RESILIENCE_PACKET.md',
}


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['enterprise runtime hardening', 'P1094'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1094', 'enterprise runtime'],
    })


def enterprise_runtime_deployment_hardening() -> Dict[str, Any]:
    presence = {name: path.exists() for name, path in _RUNTIME_PATHS.items()}
    truth_sync = _truth_surface_sync_status()
    valid = bool(P1093_VALID) and bool(truth_sync.get('all_pass')) and all(presence.values())
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1093_valid': bool(P1093_VALID),
            'truth_surfaces_synchronized_to_v37_1': bool(truth_sync.get('all_pass')),
            'runtime_surfaces_present': all(presence.values()),
        },
        'runtime_surfaces': {name: path.resolve().as_posix() for name, path in _RUNTIME_PATHS.items()},
        'runtime_presence': presence,
        'risk_ledger': [
            'live_status_and_public_api_must_report_the_same_version_and next-slot reality',
            'review packets and training artifacts must remain available during runtime outages',
            'deployment language may harden, but honesty boundaries may not relax',
        ],
        'outcome': 'ENTERPRISE_RUNTIME_DEPLOYMENT_HARDENING_READY' if valid else 'ENTERPRISE_RUNTIME_DEPLOYMENT_HARDENING_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(enterprise_runtime_deployment_hardening().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
