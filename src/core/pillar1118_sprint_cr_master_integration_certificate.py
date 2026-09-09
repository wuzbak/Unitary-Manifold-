# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1118 — Sprint CR master integration certificate."""

from __future__ import annotations

from functools import lru_cache
from typing import Dict

from src.core.pillar1109_sprint_cr_master_charter import PILLAR_VALID as P1109_VALID, SPRINT, VERSION
from src.core.pillar1110_formal_burden_board import PILLAR_VALID as P1110_VALID, formal_burden_board
from src.core.pillar1111_lane1_action_to_evolution_closure_attempt import PILLAR_VALID as P1111_VALID, lane1_action_to_evolution_closure_attempt
from src.core.pillar1112_lane2_lean4_deterministic_proof import PILLAR_VALID as P1112_VALID, lane2_lean4_deterministic_proof
from src.core.pillar1113_lane3_python_lean_truth_equivalence import PILLAR_VALID as P1113_VALID, lane3_python_lean_truth_equivalence
from src.core.pillar1114_lane4_falsifier_tension_discipline import PILLAR_VALID as P1114_VALID, lane4_falsifier_tension_discipline
from src.core.pillar1115_lane5_verification_regression_discipline import PILLAR_VALID as P1115_VALID, lane5_verification_regression_discipline
from src.core.pillar1116_documentation_evidence_packet import PILLAR_VALID as P1116_VALID, sprint_cr_documentation_evidence_packet
from src.core.pillar1117_sprint_cr_status_coherence_certificate import PILLAR_VALID as P1117_VALID, sprint_cr_status_coherence_certificate

PILLAR_NUMBER: int = 1118
PILLAR_GATE: str = 'SPRINT_CR_MASTER_INTEGRATION_CERTIFICATE'
PILLAR_STATUS: str = 'SPRINT_CR_MASTER_INTEGRATION_CERTIFICATE_COMPLETE'
NEXT_PILLAR_SLOT: int = 1119


@lru_cache(maxsize=1)
def sprint_cr_master_integration_certificate() -> Dict[str, object]:
    lane_packets = {
        'formal_burden_board': formal_burden_board(),
        'lane1_action_to_evolution': lane1_action_to_evolution_closure_attempt(),
        'lane2_lean4_deterministic': lane2_lean4_deterministic_proof(),
        'lane3_truth_equivalence': lane3_python_lean_truth_equivalence(),
        'lane4_falsifier_tension': lane4_falsifier_tension_discipline(),
        'lane5_verification_regression': lane5_verification_regression_discipline(),
        'documentation_evidence_packet': sprint_cr_documentation_evidence_packet(),
        'status_coherence': sprint_cr_status_coherence_certificate(),
    }
    dependencies = {
        'pillar1109_valid': bool(P1109_VALID),
        'pillar1110_valid': bool(P1110_VALID),
        'pillar1111_valid': bool(P1111_VALID),
        'pillar1112_valid': bool(P1112_VALID),
        'pillar1113_valid': bool(P1113_VALID),
        'pillar1114_valid': bool(P1114_VALID),
        'pillar1115_valid': bool(P1115_VALID),
        'pillar1116_valid': bool(P1116_VALID),
        'pillar1117_valid': bool(P1117_VALID),
    }
    valid = all(dependencies.values()) and all(bool(packet.get('valid')) for packet in lane_packets.values())

    lane1_outcome = str(lane_packets['lane1_action_to_evolution'].get('unit_outcome') or 'TIGHTENED_WITH_EXPLICIT_BLOCKER')
    final_board = {
        'closed': ['none'] if lane1_outcome != 'CLOSED_NOW' else ['ACTION_TO_EVOLUTION_BOUNDARY'],
        'tightened': ['ACTION_TO_EVOLUTION_BOUNDARY', 'LANE2_LEAN4_DETERMINISTIC_PROOF', 'LANE3_PYTHON_LEAN_TRUTH_EQUIVALENCE'],
        'blocked_or_external_wait': ['DESI_DR3_MONITORING', 'LITEBIRD_BIREFRINGENCE', 'NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT'],
    }

    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': dependencies,
        'lane_packets': lane_packets,
        'final_board': final_board,
        'definition_of_done': [
            'scope lock remains action-to-evolution primary with support-only secondary units',
            'formal burden board and deterministic lane contracts are machine-readable',
            'falsifier windows stay explicit with external waits preserved',
            'targeted and full regression discipline is declared and reported',
            'truth surfaces stay synchronized and sprint fail-closes on drift',
        ],
        'outcome': 'SPRINT_CR_MASTER_INTEGRATION_CERTIFICATE_READY' if valid else 'SPRINT_CR_MASTER_INTEGRATION_CERTIFICATE_BLOCKED',
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cr_master_integration_certificate().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
