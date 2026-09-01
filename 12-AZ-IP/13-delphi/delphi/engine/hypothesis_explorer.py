# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Multi-Modal Hypothesis Explorer for DelPhi."""
from __future__ import annotations

ORACLE_CHANNELS = [
    {
        'id': 'birefringence',
        'name': 'CMB Birefringence Oracle',
        'pillar': 'P001',
        'prediction': 'β ∈ [0.22°, 0.38°]',
        'falsifier': 'LiteBIRD 2032',
    },
    {
        'id': 'desi',
        'name': 'DESI Dark-Energy Oracle',
        'pillar': 'P063',
        'prediction': 'w_a = 0 remains the registered KK route prediction',
        'falsifier': 'DESI DR3 and successor equation-of-state analyses',
    },
    {
        'id': 'cmb',
        'name': 'CMB Amplitude Audit Oracle',
        'pillar': 'P057',
        'prediction': 'acoustic-peak amplitude still requires KK-tower completion',
        'falsifier': 'A transfer-chain derivation that closes the ×4–7 peak gap',
    },
    {
        'id': 'yukawa',
        'name': 'Yukawa Texture Oracle',
        'pillar': 'P067',
        'prediction': 'n_w = 5 remains the selected winding after quantitative filters',
        'falsifier': 'A first-principles derivation or data update that excludes n_w = 5',
    },
    {
        'id': 'geo',
        'name': 'Geometric Closure Oracle',
        'pillar': 'P858',
        'prediction': 'the dimensional chain remains registered from 11D to 4D',
        'falsifier': 'A broken reduction link in the registered dimensional chain',
    },
]

_CHANNEL_DETAILS: dict[str, dict[str, object]] = {
    'birefringence': {
        'supporting_pillars': ['P001', 'P057', 'P063'],
        'contradicting_pillars': ['P860'],
        'confidence_interval': 'β ∈ [0.22°, 0.38°]',
        'status': 'HARDGATE',
    },
    'desi': {
        'supporting_pillars': ['P063', 'P067'],
        'contradicting_pillars': ['P860'],
        'confidence_interval': 'w_a = 0 ± observational error bars',
        'status': 'OPEN',
    },
    'cmb': {
        'supporting_pillars': ['P057', 'P063'],
        'contradicting_pillars': ['P860'],
        'confidence_interval': 'acoustic-peak amplitude remains under-resolved by roughly ×4–7',
        'status': 'OPEN',
    },
    'yukawa': {
        'supporting_pillars': ['P067', 'P837', 'P843'],
        'contradicting_pillars': ['P860'],
        'confidence_interval': 'hierarchical Yukawa textures stay within order-of-magnitude routing bounds',
        'status': 'ADJACENT',
    },
    'geo': {
        'supporting_pillars': ['P001', 'P004', 'P858', 'P859'],
        'contradicting_pillars': [],
        'confidence_interval': '11D→10D→9D→7D→6D→5D→4D registration remains intact',
        'status': 'HARDGATE',
    },
}

_PILLAR_STATUS_OVERRIDES: dict[int, tuple[str, float, str]] = {
    57: ('PARTIAL', 0.61, 'The amplitude suppression remains openly documented in FALLIBILITY.md.'),
    63: ('PARTIAL', 0.68, 'Dark-energy routing remains test-bound against DESI updates.'),
    67: ('PARTIAL', 0.72, 'The final n_w = 5 selection still relies on the quantitative data filter.'),
    837: ('PARTIAL', 0.66, 'The 6D generation bridge is conditional on c₁ = 3.'),
    838: ('PARTIAL', 0.58, 'The Hosotani Higgs estimate is ballpark-valid but UV-sensitive.'),
    839: ('PARTIAL', 0.74, 'The Lean4 bridge is a proxy formalisation, not the full analytic APS theorem.'),
    840: ('CLOSED', 0.83, 'The zero-mode reduction closes, while KK backreaction remains higher-order.'),
    841: ('OPEN', 0.49, 'The benchmark remains testable, but collider confirmation is still absent.'),
    843: ('PARTIAL', 0.69, 'The CKM hierarchy closes structurally, not at exact PDG central values.'),
    844: ('PARTIAL', 0.65, 'The 7D α_s route still depends on an open volume ratio.'),
    849: ('CLOSED', 0.86, 'The 9D anomaly bridge fixes k_CS = 74 at the bridge level.'),
    850: ('PARTIAL', 0.67, 'The PMNS phase route remains model-dependent beyond the current proxy.'),
    853: ('PARTIAL', 0.63, 'Flux stabilization is registered, but the non-perturbative completion stays open.'),
    854: ('PARTIAL', 0.64, 'The visible-sector selection is registered, while detailed E8 breaking remains open.'),
    855: ('PARTIAL', 0.71, 'The audit passes cross-dimensionally but preserves explicit swampland caveats.'),
    858: ('CLOSED', 0.84, 'The chain is fully registered without erasing partial links.'),
    859: ('CLOSED', 0.88, 'The master theorem file is registered at the architecture-summary level.'),
    860: ('PARTIAL', 0.79, 'The sprint certificate closes bookkeeping while preserving remaining open items.'),
}

__all__ = [
    'ORACLE_CHANNELS',
    'explore_hypothesis',
    'get_uncertainty_quantification',
]


def _channel_map() -> dict[str, dict[str, str]]:
    return {channel['id']: channel for channel in ORACLE_CHANNELS}


def explore_hypothesis(hypothesis: str, channel_id: str) -> dict[str, object]:
    """Explore a hypothesis against one registered DelPhi channel."""
    channel_lookup = _channel_map()
    if channel_id not in channel_lookup:
        raise ValueError(f'Unknown channel_id: {channel_id}')

    channel = channel_lookup[channel_id]
    detail = _CHANNEL_DETAILS[channel_id]
    lowered = hypothesis.lower()
    stressed = any(token in lowered for token in ('falsif', 'contradict', 'outside', 'fail', 'tension'))
    status = 'OPEN' if stressed and detail['status'] != 'OPEN' else detail['status']
    contradicting = list(detail['contradicting_pillars'])
    if stressed and channel['pillar'] not in contradicting:
        contradicting.append(channel['pillar'])

    return {
        'hypothesis': hypothesis,
        'channel': channel_id,
        'supporting_pillars': list(detail['supporting_pillars']),
        'contradicting_pillars': contradicting,
        'confidence_interval': str(detail['confidence_interval']),
        'status': status,
    }


def get_uncertainty_quantification(pillar_id: int) -> dict[str, object]:
    """Return a lightweight uncertainty record for a pillar."""
    if pillar_id in _PILLAR_STATUS_OVERRIDES:
        status, confidence, caveat = _PILLAR_STATUS_OVERRIDES[pillar_id]
    elif 1 <= pillar_id <= 208:
        status, confidence, caveat = (
            'CLOSED',
            0.91,
            'Hardgate pillar registration is closed, but external falsifiers and empirical audits still apply.',
        )
    elif 209 <= pillar_id <= 785:
        status, confidence, caveat = (
            'PARTIAL',
            0.62,
            'Adjacent-track pillars remain informative but are not part of the closed hardgate claim set.',
        )
    else:
        status, confidence, caveat = (
            'OPEN',
            0.35,
            'No closed registry entry was identified for this pillar id.',
        )
    return {
        'pillar': pillar_id,
        'status': status,
        'confidence': confidence,
        'caveat': caveat,
    }
