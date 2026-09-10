# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1120 — PsiCat training, benchmarking, and promotion sprint packet."""

from __future__ import annotations

import importlib
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded
from src.core.pillar1109_sprint_cr_master_charter import build_truth_surface_sync_status

PILLAR_NUMBER: int = 1120
PILLAR_GATE: str = 'PSICAT_TRAINING_BENCHMARKING_PROMOTION_SPRINT'
PILLAR_STATUS: str = 'PSICAT_TRAINING_BENCHMARKING_PROMOTION_SPRINT_COMPLETE'
VERSION: str = 'v37.6'
SPRINT: str = 'CT'
SPRINT_DATE: str = '2026-09-10'
NEXT_PILLAR_SLOT: int = 1121
_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / '12-AZ-IP' / '20-psicat-navigator'


def _load(module_name: str) -> Any:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module(module_name)


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', f'Pillar {PILLAR_NUMBER}', 'next slot 1121'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v37_6_sprint_ct:', '  pillars: 1120-1120', '  next_pillar_slot: 1121'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): [f'Unitary Manifold {VERSION}', 'Sprint CT', 'Pillars 1120-1120'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): [f'**Sprint {SPRINT} ({VERSION}', f'P{PILLAR_NUMBER}', 'Next slot 1121'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['### Sprint CT PsiCat training, benchmarking, and promotion sprint', 'training-benchmarking-promotion packet'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} ({SPRINT_DATE} — Sprint {SPRINT}: Pillar {PILLAR_NUMBER})', '**Next pillar slot:** 1121'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): ['## SPRINT CT PSICAT TRAINING BENCHMARKING PROMOTION PROTOCOL', 'Historical continuity: v37.6 Sprint CT', 'Historical continuity: v37.5 Sprint CS'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): ['"version": "37.6"', '"sprint": "CT"', '"next_slot": 1121', '"historical_continuity"', '"version": "37.5"', '"sprint": "CS"', '"next_slot": 1120'],
    })


def _truth_surface_file_pass(truth_sync: Dict[str, Any], relative_path: str) -> bool:
    expected_path = (_ROOT / relative_path).resolve().as_posix()
    for file_check in truth_sync.get('files') or []:
        if file_check.get('path') == expected_path:
            return bool(file_check.get('pass'))
    return False


@lru_cache(maxsize=1)
def psicat_training_benchmarking_promotion_sprint() -> Dict[str, Any]:
    merlin_program = _load('ox_navigator.engine.merlin_program')
    packet = merlin_program.get_psicat_training_benchmarking_promotion_sprint(limit=2, training_limit=4)
    truth_sync = _truth_surface_sync_status()

    training_board = list(packet.get('training_board') or [])
    benchmark_board = dict(packet.get('benchmark_board') or {})
    promotion_readiness = dict(packet.get('promotion_readiness') or {})
    next_sprint = dict(packet.get('appropriate_promotion_sprint') or {})
    historical_continuity_declared = (
        _truth_surface_file_pass(truth_sync, 'docs/SPRINT_PLAN.md')
        and _truth_surface_file_pass(truth_sync, '9-INFRASTRUCTURE/um_live_status.json')
    )

    valid = bool(
        bool(truth_sync.get('all_pass'))
        and packet.get('mode') == 'training_benchmarking_promotion_sprint'
        and len(training_board) >= 4
        and len(list(benchmark_board.get('stage_gate_summary') or [])) == 5
        and len(list(benchmark_board.get('spc_phase1_lane_receipts') or [])) == 3
        and str(next_sprint.get('sprint_id') or '')
        and str(promotion_readiness.get('promotion_language') or '')
        and historical_continuity_declared
    )
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'training_packet_mode_ok': packet.get('mode') == 'training_benchmarking_promotion_sprint',
            'training_board_complete': len(training_board) >= 4,
            'benchmark_stage_coverage_complete': len(list(benchmark_board.get('stage_gate_summary') or [])) == 5,
            'spc_lane_coverage_complete': len(list(benchmark_board.get('spc_phase1_lane_receipts') or [])) == 3,
            'truth_surfaces_synchronized_to_v37_6': bool(truth_sync.get('all_pass')),
            'historical_continuity_declared_from_sprint_cs': historical_continuity_declared,
        },
        'packet': packet,
        'training_board': training_board,
        'benchmark_board': benchmark_board,
        'promotion_readiness': promotion_readiness,
        'appropriate_promotion_sprint': next_sprint,
        'truth_surface_sync': truth_sync,
        'outcome': (
            'PSICAT_TRAINING_BENCHMARKING_PROMOTION_SPRINT_READY'
            if valid
            else 'PSICAT_TRAINING_BENCHMARKING_PROMOTION_SPRINT_BLOCKED'
        ),
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(psicat_training_benchmarking_promotion_sprint().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()


def pillar1120_summary() -> Dict[str, Any]:
    report = psicat_training_benchmarking_promotion_sprint()
    return {
        'pillar': PILLAR_NUMBER,
        'title': 'PsiCat Training Benchmarking Promotion Sprint',
        'status': PILLAR_STATUS,
        'outcome': report['outcome'],
        'valid': report['valid'],
    }
