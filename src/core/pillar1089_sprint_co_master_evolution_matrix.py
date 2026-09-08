# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1089 — Sprint CO master evolution matrix."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

PILLAR_NUMBER: int = 1089
PILLAR_GATE: str = "SPRINT_CO_MASTER_EVOLUTION_MATRIX"
PILLAR_STATUS: str = "SPRINT_CO_MASTER_EVOLUTION_MATRIX_COMPLETE"
VERSION: str = "v37.1"
SPRINT: str = "CO"
SPRINT_DATE: str = "2026-09-08"
NEXT_PILLAR_SLOT: int = 1090
FINAL_SPRINT_NEXT_SLOT: int = 1097

_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_SYNC_PATHS = [
    (_ROOT / 'STATUS.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(),
    (_ROOT / 'FALLIBILITY.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(),
    (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(),
    (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(),
]
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
MASTER_LANES = [
    {
        'lane_id': 'LANE_A_LEAN4_PROOF_CORE',
        'title': 'Lean4 proof-core strengthening',
        'goal': 'Keep the formal program narrower and stronger around named burden retirement.',
    },
    {
        'lane_id': 'LANE_B_LEAN_TO_PYTHON_BRIDGE',
        'title': 'Lean→Python executable bridge hardening',
        'goal': 'Make provenance explicit and keep manual-port boundaries honest.',
    },
    {
        'lane_id': 'LANE_C_PSICAT_CONTINUOUS_TRAINING',
        'title': 'PsiCat continuous training integration',
        'goal': 'Turn every proof packet and sprint receipt into governed training artifacts.',
    },
    {
        'lane_id': 'LANE_D_VALIDATION_RESILIENCE',
        'title': 'Validation / CI / security resilience',
        'goal': 'Preserve changed-surface-first validation, missing-signal honesty, and fail-closed review policy.',
    },
    {
        'lane_id': 'LANE_E_ENTERPRISE_RUNTIME',
        'title': 'Enterprise runtime hardening',
        'goal': 'Keep live runtime, status, and review packets operationally coherent.',
    },
]


def _json_safe(value: Any) -> Any:
    return deepcopy(value)


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def build_truth_surface_sync_status(required_fragments: dict[str, list[str]]) -> Dict[str, Any]:
    file_checks = []
    for file_path, fragments in required_fragments.items():
        candidate = Path(file_path)
        exists = candidate.is_file()
        read_ok = True
        content = ''
        if exists:
            try:
                content = candidate.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                read_ok = False
        file_checks.append({
            'path': file_path,
            'exists': exists,
            'read_ok': read_ok,
            'required_fragments': list(fragments),
            'pass': exists and read_ok and all(fragment in content for fragment in fragments),
        })
    return {'all_pass': all(item['pass'] for item in file_checks), 'files': file_checks}


def _truth_surface_sync_status() -> Dict[str, Any]:
    checks = {
        (_ROOT / 'STATUS.md').resolve().as_posix(): [f'{VERSION} Sprint {SPRINT}', 'Pillars 1089-1096', 'next slot 1097'],
        (_ROOT / 'docs' / 'mas_tracker.yml').resolve().as_posix(): ['v37_1_sprint_co:', '  pillars: 1089-1096', '  next_pillar_slot: 1097'],
        (_ROOT / 'FALLIBILITY.md').resolve().as_posix(): [f'Unitary Manifold {VERSION}', 'Sprint CO', 'Pillars 1089-1096'],
        (_ROOT / 'docs' / 'CLAIM_MASTER_BOARD.md').resolve().as_posix(): [f'*P{PILLAR_NUMBER} ({VERSION}):', PILLAR_STATUS],
        (_ROOT / 'docs' / 'GATEKEEPER_SUMMARY.md').resolve().as_posix(): [f'**Sprint {SPRINT} ({VERSION}', '1 sprint packet (1089-1096)', 'Next slot 1097'],
        (_ROOT / 'docs' / 'TRUTH_LAYER.md').resolve().as_posix(): ['### Sprint CO proof foundry hardening and governed evolution sprint', 'master evolution matrix'],
        (_ROOT / 'docs' / 'WAVE_CHANGELOG.md').resolve().as_posix(): [f'## {VERSION} ({SPRINT_DATE} — Sprint {SPRINT}: Pillars 1089-1096)', '**Next pillar slot:** 1097'],
        (_ROOT / 'docs' / 'SPRINT_PLAN.md').resolve().as_posix(): ['## SPRINT CO PROOF FOUNDRY HARDENING AND GOVERNED EVOLUTION PROTOCOL', 'Historical continuity: v37.1 Sprint CO'],
        (_ROOT / '9-INFRASTRUCTURE' / 'um_live_status.json').resolve().as_posix(): ['"version": "37.1"', '"sprint": "CO"', '"next_slot": 1097'],
    }
    return build_truth_surface_sync_status(checks)


def sprint_co_master_evolution_matrix() -> Dict[str, Any]:
    truth_sync = _truth_surface_sync_status()
    lane_rows = [
        {
            'lane_id': lane['lane_id'],
            'title': lane['title'],
            'goal': lane['goal'],
            'deliverable_pillar': pillar,
            'status': 'CHARTERED',
        }
        for lane, pillar in zip(MASTER_LANES, range(1090, 1095), strict=False)
    ]
    valid = bool(truth_sync.get('all_pass')) and len(lane_rows) == 5 and len(OPEN_LANES) == 9
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'master_packet_range': '1089-1096',
        'dependencies': {
            'truth_surfaces_synchronized_to_v37_1': bool(truth_sync.get('all_pass')),
            'lane_count_locked_to_five': len(lane_rows) == 5,
            'open_lane_inventory_retained': len(OPEN_LANES) == 9,
        },
        'lane_charter': lane_rows,
        'open_lanes_unchanged': list(OPEN_LANES),
        'integration_rules': [
            'no theorem-count growth without proof-distance accounting',
            'no direct Lean runtime claim unless artifact exchange exists',
            'every meaningful sprint advance must emit PsiCat training artifacts',
            'skipped or missing validation remains visible',
            'restart safety requires explicit receipts and next-action surfaces',
        ],
        'integrated_board': {
            'mode': 'all_hands_parallel_fail_closed',
            'truth_surface_sync_paths': list(CANONICAL_SYNC_PATHS),
            'closed_this_sprint': ['master_evolution_charter_is_now_machine_readable'],
            'tightened_or_corrected': [
                'lean_frontier_bridge_training_validation_and_runtime_work_are_separated_into_named lanes',
                'parallel deliverables now end in receipts rather than narrative-only advancement',
            ],
            'blocked_or_external_wait': ['all previously open scientific lanes remain explicit and unchanged'],
        },
        'outcome': 'SPRINT_CO_MASTER_EVOLUTION_MATRIX_READY' if valid else 'SPRINT_CO_MASTER_EVOLUTION_MATRIX_BLOCKED',
        'truth_surface_sync': truth_sync,
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_co_master_evolution_matrix().get('valid'))
        except Exception:
            return False

    def __repr__(self) -> str:
        return str(bool(self))


PILLAR_VALID = _PillarValidProxy()


def pillar1089_summary() -> Dict[str, Any]:
    report = sprint_co_master_evolution_matrix()
    return {
        'pillar': PILLAR_NUMBER,
        'title': 'Sprint CO Master Evolution Matrix',
        'status': PILLAR_STATUS,
        'outcome': report['outcome'],
        'valid': report['valid'],
    }
