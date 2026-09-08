# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1106 — Lane 3 PsiCat receipt completion board."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded
from src.core.pillar1103_sprint_cq_continuation_charter import SPRINT, VERSION, build_truth_surface_sync_status
from src.core.pillar1104_lane1_action_to_evolution_continuation import lane1_action_to_evolution_continuation
from src.core.pillar1105_lane2_touched_translation_gate import PILLAR_VALID as P1105_VALID, lane2_touched_translation_gate

PILLAR_NUMBER: int = 1106
PILLAR_GATE: str = 'LANE3_PSICAT_RECEIPT_COMPLETION'
PILLAR_STATUS: str = 'LANE3_PSICAT_RECEIPT_COMPLETION_COMPLETE'
NEXT_PILLAR_SLOT: int = 1107
_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / '12-AZ-IP' / '20-psicat-navigator'



def _load(module_name: str) -> Any:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module(module_name)



def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CQ continuation packet', 'P1106'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1106', 'receipt completion'],
    })



def lane3_psicat_receipt_completion() -> Dict[str, Any]:
    lane1 = lane1_action_to_evolution_continuation()
    lane2 = lane2_touched_translation_gate()
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
    reviewer_packets = list(lane1.get('reviewer_packets') or [])
    reviewer_packet_ingestion = {
        'new_packets': reviewer_packets,
        'all_present': all((_ROOT / packet).exists() for packet in reviewer_packets),
        'active_unit_ids': list(lane1.get('touched_unit_ids') or []),
    }
    stage_receipt_visibility = {
        'stage_a_receipts_doc': (_PRODUCT_ROOT / 'training' / 'training_jsonl' / 'benchmarks' / 'stage_a_parity_capture.jsonl').exists(),
        'stage_b_receipts_doc': (_PRODUCT_ROOT / 'training' / 'training_jsonl' / 'benchmarks' / 'stage_b_sovereign_takeover.jsonl').exists(),
        'stage_c_receipts_doc': (_PRODUCT_ROOT / 'training' / 'training_jsonl' / 'benchmarks' / 'stage_c_capability_expansion.jsonl').exists(),
    }
    failed_units = sorted({
        *list(lane1.get('lane1_evidence_board', {}).get('blocked', []) or []),
        *list(lane2.get('compartmentalized_harvest', {}).get('blocked_units', []) or []),
    })

    truth_sync = _truth_surface_sync_status()
    valid = (
        bool(P1105_VALID)
        and bool(truth_sync.get('all_pass'))
        and len(proof_items) >= 4
        and all(stage_receipt_visibility.values())
        and reviewer_packet_ingestion['all_present']
    )
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1105_valid': bool(P1105_VALID),
            'truth_surfaces_synchronized_to_v37_3': bool(truth_sync.get('all_pass')),
            'formal_proof_foundry_queue_items_present': len(proof_items) >= 4,
            'stage_receipt_visibility_present': all(stage_receipt_visibility.values()),
            'new_reviewer_packets_present': reviewer_packet_ingestion['all_present'],
        },
        'co_runner_mode': {
            'lane1_lane2_artifact_ingestion': True,
            'local_first_primary_runtime': True,
            'openrouter_compatibility_only': True,
        },
        'reviewer_packet_ingestion': reviewer_packet_ingestion,
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
        'retraining_queue_inputs': {
            'failed_units_retained_for_retraining': failed_units,
            'drop_policy': 'no_drop_no_delete_keep_for_retraining_and_review',
        },
        'benchmark_receipt_visibility': stage_receipt_visibility,
        'receipt_cycle': {
            'mode': 'local_first_explicit_receipts',
            'stage_receipts_complete': all(stage_receipt_visibility.values()),
            'receipt_count_visible': sum(1 for present in stage_receipt_visibility.values() if present),
        },
        'outcome': 'LANE3_PSICAT_RECEIPT_COMPLETION_READY' if valid else 'LANE3_PSICAT_RECEIPT_COMPLETION_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane3_psicat_receipt_completion().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
