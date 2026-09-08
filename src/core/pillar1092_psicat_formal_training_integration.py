# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1092 — PsiCat formal training integration."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded
from src.core.pillar1091_lean_python_bridge_hardening import PILLAR_VALID as P1091_VALID
from src.core.pillar1089_sprint_co_master_evolution_matrix import SPRINT, VERSION, build_truth_surface_sync_status

PILLAR_NUMBER: int = 1092
PILLAR_GATE: str = 'PSICAT_FORMAL_TRAINING_INTEGRATION'
PILLAR_STATUS: str = 'PSICAT_FORMAL_TRAINING_INTEGRATION_COMPLETE'
NEXT_PILLAR_SLOT: int = 1093
_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / '12-AZ-IP' / '20-psicat-navigator'


def _load(module_name: str) -> Any:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module(module_name)


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['PsiCat formal training integration', 'P1092'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1092', 'PsiCat formal training'],
    })


def psicat_formal_training_integration() -> Dict[str, Any]:
    merlin_program = _load('ox_navigator.engine.merlin_program')
    merlin_memory = _load('ox_navigator.engine.merlin_memory')
    merlin_training_execution = _load('ox_navigator.engine.merlin_training_execution')
    architecture = merlin_program.get_training_architecture(limit=12)
    bundle = merlin_program.build_training_artifact_bundle(limit=6)
    session = merlin_memory.MerlinSession()
    queue = merlin_training_execution.build_merlin_training_execution_queue(session=session, limit=20)
    queue_items = [item for item in list(queue.get('items') or []) if str(item.get('lane_id') or '') == 'lane_d_formal_proof_foundry']
    truth_sync = _truth_surface_sync_status()
    valid = bool(P1091_VALID) and bool(truth_sync.get('all_pass')) and bool(queue_items)
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1091_valid': bool(P1091_VALID),
            'truth_surfaces_synchronized_to_v37_1': bool(truth_sync.get('all_pass')),
            'formal_proof_foundry_family_present': any(item.get('family') == 'formal_proof_foundry' for item in architecture.get('dataset_families', [])),
            'proof_foundry_queue_items_present': len(queue_items) >= 4,
        },
        'training_architecture': {
            'formal_proof_foundry': dict(architecture.get('formal_proof_foundry') or {}),
            'dataset_families': [item for item in architecture.get('dataset_families', []) if item.get('family') == 'formal_proof_foundry'],
            'active_surface': architecture.get('active_training_surfaces', {}).get('formal_proof_foundry_bundle'),
        },
        'artifact_bundle': {
            'formal_proof_foundry_bundle': dict(((bundle.get('artifact_bundle') or {}).get('formal_proof_foundry_bundle') or {})),
        },
        'training_execution_queue': {
            'lane_id': 'lane_d_formal_proof_foundry',
            'queue_item_count': len(queue_items),
            'queue_items': queue_items[:8],
        },
        'outcome': 'PSICAT_FORMAL_TRAINING_INTEGRATION_READY' if valid else 'PSICAT_FORMAL_TRAINING_INTEGRATION_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(psicat_formal_training_integration().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
