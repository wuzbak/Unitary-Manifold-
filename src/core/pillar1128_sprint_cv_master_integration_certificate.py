# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1128 — Sprint CV master integration certificate.

Fail-closes Sprint CV validity unless charter + all three lanes +
documentation packet + status coherence remain simultaneously valid. This
certificate is the version-earning gate: v38.0 is only earned if this
pillar's ``valid`` field is True.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

from src.core.pillar1122_sprint_cv_master_charter import (
    PILLAR_VALID as P1122_VALID,
    SPRINT,
    VERSION,
    sprint_cv_master_charter,
)
from src.core.pillar1123_lane1_action_to_evolution_cv_attempt import (
    PILLAR_VALID as P1123_VALID,
    lane1_action_to_evolution_cv_attempt,
)
from src.core.pillar1124_lane2_psicat_spc_phase2_promotion_sprint import (
    PILLAR_VALID as P1124_VALID,
    lane2_psicat_spc_phase2_promotion_sprint,
)
from src.core.pillar1125_lane3_monorepo_health_audit import (
    PILLAR_VALID as P1125_VALID,
    lane3_monorepo_health_audit,
)
from src.core.pillar1126_sprint_cv_documentation_evidence_packet import (
    PILLAR_VALID as P1126_VALID,
    sprint_cv_documentation_evidence_packet,
)
from src.core.pillar1127_sprint_cv_status_coherence_certificate import (
    PILLAR_VALID as P1127_VALID,
    sprint_cv_status_coherence_certificate,
)

PILLAR_NUMBER: int = 1128
PILLAR_GATE: str = 'SPRINT_CV_MASTER_INTEGRATION_CERTIFICATE'
PILLAR_STATUS: str = 'SPRINT_CV_MASTER_INTEGRATION_CERTIFICATE_COMPLETE'
NEXT_PILLAR_SLOT: int = 1129


@lru_cache(maxsize=1)
def sprint_cv_master_integration_certificate() -> Dict[str, Any]:
    lane_packets = {
        'charter': sprint_cv_master_charter(),
        'lane1_action_to_evolution': lane1_action_to_evolution_cv_attempt(),
        'lane2_psicat_spc_phase2': lane2_psicat_spc_phase2_promotion_sprint(),
        'lane3_monorepo_health': lane3_monorepo_health_audit(),
        'documentation_evidence_packet': sprint_cv_documentation_evidence_packet(),
        'status_coherence': sprint_cv_status_coherence_certificate(),
    }
    dependencies = {
        'pillar1122_valid': bool(P1122_VALID),
        'pillar1123_valid': bool(P1123_VALID),
        'pillar1124_valid': bool(P1124_VALID),
        'pillar1125_valid': bool(P1125_VALID),
        'pillar1126_valid': bool(P1126_VALID),
        'pillar1127_valid': bool(P1127_VALID),
    }
    valid = all(dependencies.values()) and all(bool(packet.get('valid')) for packet in lane_packets.values())

    lane1 = lane_packets['lane1_action_to_evolution']
    lane2 = lane_packets['lane2_psicat_spc_phase2']
    lane3 = lane_packets['lane3_monorepo_health']

    version_earning_gate = {
        'lane1_gate_satisfied': bool(
            lane1.get('binary_outcome')
            in {'VERIFIED_ACTION_EQUATION_RESIDUAL_DOMAIN_PACKAGE', 'PRECISE_BLOCKER_CERTIFICATE_AND_STOP'}
        ),
        'lane2_gate_satisfied': bool(
            lane2.get('promotion_decision')
            in {'PROMOTED_PHASE2_APPLIED_PRESSURE', 'HELD_WITH_REMEDIATION_ROUTING'}
        ),
        'lane3_gate_satisfied': bool(lane3.get('valid')),
    }
    version_earned = valid and all(version_earning_gate.values())

    return {
        'pillar': PILLAR_NUMBER,
        'gate': PILLAR_GATE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'sprint': SPRINT,
        'next_pillar_slot': NEXT_PILLAR_SLOT,
        'dependencies': dependencies,
        'lane_packets': lane_packets,
        'version_earning_gate': version_earning_gate,
        'version_earned': version_earned,
        'version_certificate': (
            f'Version bump v37.7 -> {VERSION} is EARNED as a certificate: '
            'Lane 1 reported an honest binary physics outcome, Lane 2 reported a receipt-backed '
            'SPC Phase 2 verdict, and Lane 3 verified clean truth-surface sync plus zero-fail health checks.'
            if version_earned
            else f'Version bump to {VERSION} is NOT earned; at least one lane gate failed to certify.'
        ),
        'definition_of_done': [
            'Charter scope lock (Lane 1/2/3) remains valid.',
            'Lane 1 emits either verified closure or a precise blocker certificate — never partial-credit language.',
            'Lane 2 emits a receipt-backed clear/hold verdict — never an unconditional promotion claim.',
            'Lane 3 verifies truth-surface lockstep, CI/large-directory health, and reports honestly on any tracked-not-fixed findings.',
            'Documentation and status-coherence packets confirm lockstep sync across all canonical truth surfaces.',
        ],
        'outcome': (
            'SPRINT_CV_MASTER_INTEGRATION_CERTIFICATE_READY'
            if valid
            else 'SPRINT_CV_MASTER_INTEGRATION_CERTIFICATE_BLOCKED'
        ),
        'valid': valid,
    }


class _PillarValidProxy:
    def __bool__(self) -> bool:
        try:
            return bool(sprint_cv_master_integration_certificate().get('valid'))
        except Exception:
            return False


PILLAR_VALID = _PillarValidProxy()


def pillar1128_summary() -> Dict[str, Any]:
    report = sprint_cv_master_integration_certificate()
    return {
        'pillar': PILLAR_NUMBER,
        'title': 'Sprint CV Master Integration Certificate',
        'status': PILLAR_STATUS,
        'outcome': report['outcome'],
        'valid': report['valid'],
        'version_earned': report['version_earned'],
    }
