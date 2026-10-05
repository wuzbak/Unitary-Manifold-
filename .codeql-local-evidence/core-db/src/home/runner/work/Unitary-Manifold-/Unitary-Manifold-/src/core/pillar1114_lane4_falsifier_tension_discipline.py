# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1114 — Lane 4 falsifier and tension discipline."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

from src.core.observational_lane_freeze_registry import observational_lane_freeze_registry
from src.core.pillar1109_sprint_cr_master_charter import SPRINT, VERSION, build_truth_surface_sync_status
from src.core.pillar1113_lane3_python_lean_truth_equivalence import PILLAR_VALID as P1113_VALID

PILLAR_NUMBER: int = 1114
PILLAR_GATE: str = 'LANE4_FALSIFIER_TENSION_DISCIPLINE'
PILLAR_STATUS: str = 'LANE4_FALSIFIER_TENSION_DISCIPLINE_COMPLETE'
NEXT_PILLAR_SLOT: int = 1115

OPEN_LANES = [
    'CMB_AMP_CONFIRMED_IRREDUCIBLE',
    'ALPHA_S_TYPE_B_FLOOR',
    'HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW',
    'CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED',
    'FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED',
    'JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED',
    'DESI_DR3_MONITORING',
    'LITEBIRD_BIREFRINGENCE',
    'NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT',
]


def _truth_surface_sync_status() -> Dict[str, Any]:
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    return build_truth_surface_sync_status({
        (root / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['Sprint CR master implementation packet', 'Lane 4'],
        (root / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (root / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): ['P1114', 'falsifier and tension discipline'],
    })


@lru_cache(maxsize=1)
def lane4_falsifier_tension_discipline() -> Dict[str, Any]:
    freeze_registry = observational_lane_freeze_registry()
    lanes = dict(freeze_registry.get('lanes') or {})
    external_wait_only = {
        lane_id: lane for lane_id, lane in lanes.items() if str(lane.get('treatment') or '') == 'FROZEN_UNTIL_NEW_DATA'
    }

    truth_sync = _truth_surface_sync_status()
    valid = bool(P1113_VALID) and bool(truth_sync.get('all_pass')) and len(OPEN_LANES) == 9 and len(external_wait_only) >= 2
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': {
            'pillar1113_valid': bool(P1113_VALID),
            'truth_surfaces_synchronized_to_v37_4': bool(truth_sync.get('all_pass')),
            'open_lane_inventory_retained': len(OPEN_LANES) == 9,
            'external_wait_registry_present': len(external_wait_only) >= 2,
        },
        'open_lanes_unchanged': list(OPEN_LANES),
        'falsifier_windows': {
            'DESI_DR3_MONITORING': 'EXTERNAL_WAIT_ONLY',
            'LITEBIRD_BIREFRINGENCE': 'EXTERNAL_WAIT_ONLY',
            'CMB_S4_R': 'EXTERNAL_WAIT_ONLY',
        },
        'freeze_registry_snapshot': lanes,
        'label_flip_policy': 'No label flip unless new evidence is earned and documented.',
        'outcome': 'LANE4_FALSIFIER_TENSION_DISCIPLINE_READY' if valid else 'LANE4_FALSIFIER_TENSION_DISCIPLINE_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(lane4_falsifier_tension_discipline().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
