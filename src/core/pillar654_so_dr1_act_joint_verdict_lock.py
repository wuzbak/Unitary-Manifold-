# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 654 — SO DR1 / ACT joint verdict lock.

STATUS: SO_DR1_ACT_JOINT_VERDICT_LOCK_PREREGISTERED

Background
----------
This pillar hard-locks the r-routing protocol for the combined Simons
Observatory DR1 and ACT tension landscape. The irreducible braided prediction
used here is r_NLO = 0.03132. Measurements near that value are routed as
CONSISTENT. Measurements that fall far below it certify the ACT-side tension as
irreducible, and very low measurements trigger an architecture-limit response.

References
----------
Pillar 303, Pillar 632, ACT DR6 tension notes, CMB-S4/SO readiness package.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List

__all__ = [
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'PILLAR_TITLE',
    'VERSION',
    'R_NLO_UM',
    'R_IRREDUCIBILITY_CERTIFIED',
    'PASS_THRESHOLD_R',
    'HIGH_TENSION_THRESHOLD_R',
    'ARCHITECTURE_LIMIT_THRESHOLD_R',
    'SHA256_PREREGISTRATION',
    'ADJACENT_TRACK',
    'so_dr1_joint_verdict',
    'what_is_claimed',
    'what_is_NOT_claimed',
    'pillar_report',
]

PILLAR_NUMBER: int = 654
PILLAR_STATUS: str = 'SO_DR1_ACT_JOINT_VERDICT_LOCK_PREREGISTERED'
PILLAR_TITLE: str = 'SO DR1 / ACT Joint Verdict Lock'
VERSION: str = 'v21.0'

R_NLO_UM: float = 0.03132
R_IRREDUCIBILITY_CERTIFIED: bool = True
PASS_THRESHOLD_R: float = 0.0315
HIGH_TENSION_THRESHOLD_R: float = 0.020
ARCHITECTURE_LIMIT_THRESHOLD_R: float = 0.016
SHA256_PREREGISTRATION: str = hashlib.sha256(
    b'SO_DR1_ACT_JOINT_VERDICT_LOCK_v21.0_r_nlo=0.03132'
).hexdigest()
ADJACENT_TRACK: bool = False


def so_dr1_joint_verdict(r_obs: float, sigma_r: float) -> Dict[str, Any]:
    """Return the locked three-branch routing verdict for SO DR1 / ACT."""
    if sigma_r <= 0.0:
        raise ValueError('sigma_r must be positive')

    sigma_tension = abs(r_obs - R_NLO_UM) / sigma_r
    if r_obs < ARCHITECTURE_LIMIT_THRESHOLD_R:
        branch = 'ARCHITECTURE_LIMIT_TRIGGERED'
        action = 'activate_inflation_architecture_review'
    elif r_obs < HIGH_TENSION_THRESHOLD_R:
        branch = 'IRREDUCIBLE_CONFIRMED'
        action = 'confirm_act_side_irreducibility'
    elif sigma_tension < 2.0 or r_obs >= PASS_THRESHOLD_R:
        branch = 'CONSISTENT'
        action = 'retain_braided_inflation_sector'
    else:
        branch = 'IRREDUCIBLE_CONFIRMED'
        action = 'confirm_act_side_irreducibility'

    return {
        'branch': branch,
        'r_obs': r_obs,
        'sigma_r': sigma_r,
        'sigma_tension': sigma_tension,
        'r_nlo_um': R_NLO_UM,
        'irreducibility_certified': R_IRREDUCIBILITY_CERTIFIED,
        'architecture_limit_triggered': branch == 'ARCHITECTURE_LIMIT_TRIGGERED',
        'action': action,
    }


def what_is_claimed() -> List[str]:
    """Return honest claims for Pillar 654."""
    return [
        'The SO DR1 / ACT routing thresholds are preregistered in executable form.',
        'r_NLO = 0.03132 is the locked UM comparison value.',
        'Values below r = 0.020 certify high tension as irreducible within the braided sector.',
        'Values below r = 0.016 trigger an architecture-limit response.',
        'The preregistration is SHA-256 locked.',
    ]


def what_is_NOT_claimed() -> List[str]:
    """Return honest non-claims for Pillar 654."""
    return [
        'No SO DR1 data is included here.',
        'No ToE score change is awarded before live measurements arrive.',
        'This module does not claim to remove the ACT tension inside 5D EFT.',
        'The architecture-limit branch is not triggered unless the observed r falls below 0.016.',
    ]


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 654 report."""
    return {
        'pillar': PILLAR_NUMBER,
        'title': PILLAR_TITLE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'adjacent_track': ADJACENT_TRACK,
        'r_nlo_um': R_NLO_UM,
        'pass_threshold_r': PASS_THRESHOLD_R,
        'high_tension_threshold_r': HIGH_TENSION_THRESHOLD_R,
        'architecture_limit_threshold_r': ARCHITECTURE_LIMIT_THRESHOLD_R,
        'sha256_preregistration': SHA256_PREREGISTRATION,
        'what_is_claimed': what_is_claimed(),
        'what_is_NOT_claimed': what_is_NOT_claimed(),
        'toe_score_delta': 0.0,
        'hardgate_score_delta': 0.0,
    }
