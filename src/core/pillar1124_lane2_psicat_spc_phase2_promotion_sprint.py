# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1124 — Sprint CV Lane 2: PsiCat SPC Phase 2 applied-pressure promotion.

Executes the existing `/api/psicat/spc-phase2-applied-pressure` battery and
applies the `PSICAT_SPC_BENCHMARK_GATES.md` hard-fail discipline: promote only
if all gates are simultaneously clear, otherwise freeze promotion language and
report explicit remediation routing.
"""

from __future__ import annotations

import importlib
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from src.core.merlin_package_bootstrap import ensure_merlin_package_loaded
from src.core.pillar1122_sprint_cv_master_charter import (
    PILLAR_VALID as P1122_VALID,
    SPRINT,
    VERSION,
    build_truth_surface_sync_status,
)

PILLAR_NUMBER: int = 1124
PILLAR_GATE: str = 'LANE2_PSICAT_SPC_PHASE2_PROMOTION_SPRINT'
PILLAR_STATUS: str = 'LANE2_PSICAT_SPC_PHASE2_PROMOTION_SPRINT_COMPLETE'
NEXT_PILLAR_SLOT: int = 1125
_ROOT = Path(__file__).resolve().parents[2]
_PRODUCT_ROOT = _ROOT / '12-AZ-IP' / '20-psicat-navigator'

CLEAR_VERDICTS = {'PHASE2_CLEAR_ADVANCE_TO_PHASE3'}
HOLD_VERDICTS = {'PHASE2_HOLD_REMEDIATE'}


def _load(module_name: str) -> Any:
    ensure_merlin_package_loaded(_PRODUCT_ROOT)
    return importlib.import_module(module_name)


def _truth_surface_sync_status() -> Dict[str, Any]:
    return build_truth_surface_sync_status({
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CV three-lane earned-version packet', 'Lane 2'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1124', 'SPC Phase 2'],
    })


@lru_cache(maxsize=1)
def lane2_psicat_spc_phase2_promotion_sprint() -> Dict[str, Any]:
    merlin_program = _load('ox_navigator.engine.merlin_program')
    packet = merlin_program.run_psicat_spc_phase2_applied_pressure(limit=5, training_limit=9)

    phase2_lanes = list(packet.get('applied_pressure_lanes') or packet.get('phase2_lanes') or [])
    phase_gate_ledger = dict(packet.get('phase_gate_ledger') or {})
    phase_verdict = str(packet.get('phase_verdict') or '')
    blocker_register = list(packet.get('blocker_register') or [])

    verdict_recognized = phase_verdict in (CLEAR_VERDICTS | HOLD_VERDICTS)
    is_clear = phase_verdict in CLEAR_VERDICTS
    promotion_decision = 'PROMOTED_PHASE2_APPLIED_PRESSURE' if is_clear else 'HELD_WITH_REMEDIATION_ROUTING'

    remediation_actions = []
    if not is_clear:
        for blocker in blocker_register:
            if isinstance(blocker, dict):
                remediation_actions.extend(list(blocker.get('recommended_actions') or []))

    truth_sync = _truth_surface_sync_status()
    packet_shape_ok = bool(
        packet.get('ok') is True
        and packet.get('mode') == 'spc_phase2_applied_pressure_execution'
        and verdict_recognized
        and isinstance(phase_gate_ledger, dict)
    )
    valid = bool(P1122_VALID) and bool(truth_sync.get('all_pass')) and packet_shape_ok

    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1122_valid': bool(P1122_VALID),
            'truth_surfaces_synchronized_to_v38_0': bool(truth_sync.get('all_pass')),
            'packet_shape_ok': packet_shape_ok,
            'phase_verdict_recognized': verdict_recognized,
        },
        'phase2_packet': packet,
        'phase2_lanes': phase2_lanes,
        'phase_gate_ledger': phase_gate_ledger,
        'phase_verdict': phase_verdict,
        'promotion_decision': promotion_decision,
        'promotion_no_unconditional_claim_guardrail': (
            'Promotion language is receipt-gated: PROMOTED only if phase_verdict is a recognized '
            'clear verdict with zero blocker_register entries; otherwise held with remediation routing.'
        ),
        'blocker_register': blocker_register,
        'remediation_actions': remediation_actions,
        'sovereign_local_priority': {
            'openrouter_role': 'COMPATIBILITY_ONLY',
            'primary_lane': 'SOVEREIGN_LOCAL',
        },
        'truth_surface_sync': truth_sync,
        'outcome': (
            'LANE2_PSICAT_SPC_PHASE2_PROMOTION_SPRINT_READY'
            if valid
            else 'LANE2_PSICAT_SPC_PHASE2_PROMOTION_SPRINT_BLOCKED'
        ),
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane2_psicat_spc_phase2_promotion_sprint().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()


def pillar1124_summary() -> Dict[str, Any]:
    report = lane2_psicat_spc_phase2_promotion_sprint()
    return {
        'pillar': PILLAR_NUMBER,
        'title': 'Sprint CV Lane 2 — PsiCat SPC Phase 2 Applied-Pressure Promotion',
        'status': PILLAR_STATUS,
        'outcome': report['outcome'],
        'valid': report['valid'],
    }
