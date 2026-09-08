# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1100 — Lane 3 PsiCat continuous training execution board."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded
from src.core.pillar1099_lane2_python_lean_translation_audit import PILLAR_VALID as P1099_VALID
from src.core.pillar1097_sprint_cp_three_lane_charter import SPRINT, VERSION, build_truth_surface_sync_status

PILLAR_NUMBER: int = 1100
PILLAR_GATE: str = 'LANE3_PSICAT_CONTINUOUS_TRAINING_EXECUTION'
PILLAR_STATUS: str = 'LANE3_PSICAT_CONTINUOUS_TRAINING_EXECUTION_COMPLETE'
NEXT_PILLAR_SLOT: int = 1101
_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / '12-AZ-IP' / '20-psicat-navigator'


def _load(module_name: str) -> Any:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module(module_name)


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Lane 3', 'P1100'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1100', 'PsiCat'],
    })


def lane3_psicat_continuous_training_execution() -> Dict[str, Any]:
    merlin_program = _load('ox_navigator.engine.merlin_program')
    merlin_memory = _load('ox_navigator.engine.merlin_memory')
    merlin_training_execution = _load('ox_navigator.engine.merlin_training_execution')

    architecture = merlin_program.get_training_architecture(limit=12)
    bundle = merlin_program.build_training_artifact_bundle(limit=6)
    session = merlin_memory.MerlinSession()
    queue = merlin_training_execution.build_merlin_training_execution_queue(session=session, limit=32)
    ledgers = merlin_training_execution.get_merlin_lane_progress_ledgers(session=session, limit=6)

    queue_items = list(queue.get('items') or [])
    proof_items = [item for item in queue_items if str(item.get('lane_id') or '') == 'lane_d_formal_proof_foundry']
    stage_receipt_visibility = {
        'stage_a_receipts_doc': (_PRODUCT_ROOT / 'training' / 'training_jsonl' / 'benchmarks' / 'stage_a_parity_capture.jsonl').exists(),
        'stage_b_receipts_doc': (_PRODUCT_ROOT / 'training' / 'training_jsonl' / 'benchmarks' / 'stage_b_sovereign_takeover.jsonl').exists(),
        'stage_c_receipts_doc': (_PRODUCT_ROOT / 'training' / 'training_jsonl' / 'benchmarks' / 'stage_c_capability_expansion.jsonl').exists(),
    }

    truth_sync = _truth_surface_sync_status()
    valid = bool(P1099_VALID) and bool(truth_sync.get('all_pass')) and len(proof_items) >= 4 and all(stage_receipt_visibility.values())
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1099_valid': bool(P1099_VALID),
            'truth_surfaces_synchronized_to_v37_2': bool(truth_sync.get('all_pass')),
            'formal_proof_foundry_queue_items_present': len(proof_items) >= 4,
            'stage_receipt_visibility_present': all(stage_receipt_visibility.values()),
        },
        'co_runner_mode': {
            'lane1_lane2_artifact_ingestion': True,
            'local_first_primary_runtime': True,
            'openrouter_compatibility_only': True,
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
            'total_queue_items': int(queue.get('total_queue_items') or 0),
            'proof_lane_queue_items': len(proof_items),
            'proof_lane_samples': proof_items[:8],
        },
        'lane_progress_ledgers': {
            'overall': dict(ledgers.get('overall') or {}),
            'lane_count': len(list(ledgers.get('lane_ledgers') or [])),
        },
        'benchmark_receipt_visibility': stage_receipt_visibility,
        'readiness_packet': {
            'go_hold_demote_mode': 'FAIL_CLOSED',
            'unresolved_blockers': [
                'proof_foundry_promotion_still_requires_completed_receipt_cycles',
                'sovereign_replacement_decisions_remain_benchmark_gated',
            ],
        },
        'outcome': 'LANE3_PSICAT_CONTINUOUS_TRAINING_READY' if valid else 'LANE3_PSICAT_CONTINUOUS_TRAINING_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane3_psicat_continuous_training_execution().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
