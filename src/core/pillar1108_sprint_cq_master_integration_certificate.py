# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1108 — Sprint CQ master integration certificate."""

from __future__ import annotations

from typing import Dict

from src.core.pillar1103_sprint_cq_continuation_charter import PILLAR_VALID as P1103_VALID, SPRINT, VERSION
from src.core.pillar1104_lane1_action_to_evolution_continuation import PILLAR_VALID as P1104_VALID, lane1_action_to_evolution_continuation
from src.core.pillar1105_lane2_touched_translation_gate import PILLAR_VALID as P1105_VALID, lane2_touched_translation_gate
from src.core.pillar1106_lane3_psicat_receipt_completion import PILLAR_VALID as P1106_VALID, lane3_psicat_receipt_completion
from src.core.pillar1107_sprint_cq_status_coherence_certificate import PILLAR_VALID as P1107_VALID, sprint_cq_status_coherence_certificate

PILLAR_NUMBER: int = 1108
PILLAR_GATE: str = 'SPRINT_CQ_MASTER_INTEGRATION_CERTIFICATE'
PILLAR_STATUS: str = 'SPRINT_CQ_MASTER_INTEGRATION_CERTIFICATE_COMPLETE'
NEXT_PILLAR_SLOT: int = 1109



def sprint_cq_master_integration_certificate() -> Dict[str, object]:
    lane_packets = {
        'lane1_action_to_evolution': lane1_action_to_evolution_continuation(),
        'lane2_touched_translation': lane2_touched_translation_gate(),
        'lane3_psicat_receipt_completion': lane3_psicat_receipt_completion(),
        'status_coherence': sprint_cq_status_coherence_certificate(),
    }
    dependencies = {
        'pillar1103_valid': bool(P1103_VALID),
        'pillar1104_valid': bool(P1104_VALID),
        'pillar1105_valid': bool(P1105_VALID),
        'pillar1106_valid': bool(P1106_VALID),
        'pillar1107_valid': bool(P1107_VALID),
    }
    valid = all(dependencies.values()) and all(bool(packet.get('valid')) for packet in lane_packets.values())
    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': dependencies,
        'lane_packets': lane_packets,
        'definition_of_done': [
            'lane 1 keeps action-to-evolution primary and shrinks the blocker surface if closure is not earned',
            'lane 2 audits only touched units and preserves the strict master-theorem ready/blocked gate',
            'lane 3 ingests the new reviewer packets, preserves failed units, and exposes a fresh receipt cycle',
            'truth surfaces remain synchronized and fail closed on drift',
            'no widened claim scope or over-claiming of hardgate closure while open lanes remain unresolved',
        ],
        'outcome': 'SPRINT_CQ_MASTER_INTEGRATION_CERTIFICATE_READY' if valid else 'SPRINT_CQ_MASTER_INTEGRATION_CERTIFICATE_BLOCKED',
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cq_master_integration_certificate().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()
