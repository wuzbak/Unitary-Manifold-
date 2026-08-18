# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 653 — DESI DR3 live routing protocol.

STATUS: DESI_DR3_LIVE_ROUTING_PROTOCOL_PREREGISTERED

Background
----------
This pillar converts the DESI DR3 preregistration into a live executable
routing rule. The frozen-radion Unitary Manifold prediction remains
w_a = 0.0. Once the DESI DR3 central value and uncertainty are public, this
module returns the machine-readable verdict branch and whether the rolling-
radion extension pathway is triggered.

The routing is intentionally conservative and mirrors the already documented
response logic: PASS below 2 sigma, TENSION between 2 and 3 sigma, and
FALSIFIED at 3 sigma or above.

References
----------
Pillar 268, Pillar 631, FALLIBILITY.md section on DESI dark-energy tension.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List

__all__ = [
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'PILLAR_TITLE',
    'VERSION',
    'WA_FROZEN_RADION',
    'FALSIFICATION_THRESHOLD',
    'TENSION_THRESHOLD',
    'SHA256_PREREGISTRATION',
    'ADJACENT_TRACK',
    'PILLAR_631_LINK',
    'routing_hash',
    'desi_dr3_verdict',
    'what_is_claimed',
    'what_is_NOT_claimed',
    'pillar_report',
]

PILLAR_NUMBER: int = 653
PILLAR_STATUS: str = 'DESI_DR3_LIVE_ROUTING_PROTOCOL_PREREGISTERED'
PILLAR_TITLE: str = 'DESI DR3 Live Routing Protocol'
VERSION: str = 'v21.0'

WA_FROZEN_RADION: float = 0.0
FALSIFICATION_THRESHOLD: float = 3.0
TENSION_THRESHOLD: float = 2.0
SHA256_PREREGISTRATION: str = hashlib.sha256(
    b'DESI_DR3_LIVE_ROUTING_PROTOCOL_v21.0_wa=0_threshold=3.0'
).hexdigest()
ADJACENT_TRACK: bool = False
PILLAR_631_LINK: str = 'pillar631_desi_dr3_falsification_response'


def routing_hash() -> Dict[str, Any]:
    """Return the preregistration hash payload."""
    return {
        'pillar': PILLAR_NUMBER,
        'version': VERSION,
        'sha256_preregistration': SHA256_PREREGISTRATION,
        'payload': 'DESI_DR3_LIVE_ROUTING_PROTOCOL_v21.0_wa=0_threshold=3.0',
    }


def desi_dr3_verdict(wa_obs: float, sigma_wa: float) -> Dict[str, Any]:
    """Live verdict function for DESI DR3."""
    if sigma_wa <= 0.0:
        raise ValueError('sigma_wa must be positive')

    sigma_tension = abs(wa_obs - WA_FROZEN_RADION) / sigma_wa
    if sigma_tension < TENSION_THRESHOLD:
        branch = 'PASS'
        action = 'frozen_radion_retained'
        extension_triggered = False
        architecture_trigger = False
    elif sigma_tension < FALSIFICATION_THRESHOLD:
        branch = 'TENSION'
        action = 'rolling_radion_extension_scoped'
        extension_triggered = False
        architecture_trigger = False
    else:
        branch = 'FALSIFIED'
        action = 'rolling_radion_extension_activated'
        extension_triggered = True
        architecture_trigger = True

    return {
        'branch': branch,
        'sigma_tension': sigma_tension,
        'wa_obs': wa_obs,
        'sigma_wa': sigma_wa,
        'action': action,
        'extension_triggered': extension_triggered,
        'architecture_trigger': architecture_trigger,
        'rolling_radion_link': PILLAR_631_LINK,
    }


def what_is_claimed() -> List[str]:
    """Return honest claims for Pillar 653."""
    return [
        'The DESI DR3 routing protocol is pre-registered as executable code.',
        'The frozen-radion prediction is fixed at w_a = 0.0.',
        'The live branch cutoffs are PASS below 2 sigma, TENSION at 2-3 sigma, and FALSIFIED at 3 sigma or above.',
        'The rolling-radion pathway is only triggered after a live >=3 sigma falsification.',
        'The preregistration is hash-locked with SHA-256.',
    ]


def what_is_NOT_claimed() -> List[str]:
    """Return honest non-claims for Pillar 653."""
    return [
        'DESI DR3 data is not embedded here; this module only routes live inputs.',
        'No ToE score gain is claimed from preregistration alone.',
        'The rolling-radion extension is not activated unless the live verdict reaches FALSIFIED.',
        'This pillar does not soften the pre-registered 3 sigma falsification threshold.',
    ]


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 653 report."""
    return {
        'pillar': PILLAR_NUMBER,
        'title': PILLAR_TITLE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'adjacent_track': ADJACENT_TRACK,
        'wa_frozen_radion': WA_FROZEN_RADION,
        'falsification_threshold': FALSIFICATION_THRESHOLD,
        'tension_threshold': TENSION_THRESHOLD,
        'routing_hash': routing_hash(),
        'pillar_631_link': PILLAR_631_LINK,
        'what_is_claimed': what_is_claimed(),
        'what_is_NOT_claimed': what_is_NOT_claimed(),
        'toe_score_delta': 0.0,
        'hardgate_score_delta': 0.0,
    }
