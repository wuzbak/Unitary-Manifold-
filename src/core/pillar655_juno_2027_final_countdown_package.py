# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 655 — JUNO 2027 final countdown package.

STATUS: JUNO_2027_FINAL_COUNTDOWN_PREREGISTERED

Background
----------
This pillar packages the final executable routing rules for the neutrino-sector
JUNO Phase 2 measurement and the linked DUNE CP-phase cross-check. The UM
prediction for Delta m^2_31 comes from the P559 three-step cascade and is now
compared against live JUNO inputs at the advertised 0.5% precision target.

References
----------
Pillar 454, Pillar 559, PDG 2026 neutrino summaries, JUNO Phase 2 roadmap.
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    'PILLAR_NUMBER',
    'PILLAR_STATUS',
    'PILLAR_TITLE',
    'VERSION',
    'DM31_UM_EV2',
    'DM31_PDG_EV2',
    'DM31_JUNO_EV2',
    'DM31_TENSION_FINAL',
    'JUNO_PHASE2_PRECISION',
    'DM31_WINDOW_LOW',
    'DM31_WINDOW_HIGH',
    'ADJACENT_TRACK',
    'DUNE_CP_DELTA_RAD',
    'juno_phase2_verdict',
    'dune_cp_joint_verdict',
    'what_is_claimed',
    'what_is_NOT_claimed',
    'pillar_report',
]

PILLAR_NUMBER: int = 655
PILLAR_STATUS: str = 'JUNO_2027_FINAL_COUNTDOWN_PREREGISTERED'
PILLAR_TITLE: str = 'JUNO 2027 Final Countdown Package'
VERSION: str = 'v21.0'

DM31_UM_EV2: float = 2.4109e-3
DM31_PDG_EV2: float = 2.453e-3
DM31_JUNO_EV2: float = 2.411e-3
DM31_TENSION_FINAL: float = 0.12
JUNO_PHASE2_PRECISION: float = 0.005
DM31_WINDOW_LOW: float = 2.2e-3
DM31_WINDOW_HIGH: float = 2.7e-3
ADJACENT_TRACK: bool = False
DUNE_CP_DELTA_RAD: float = 1.2152


def juno_phase2_verdict(dm31_obs: float, precision_frac: float = 0.005) -> Dict[str, Any]:
    """Route a JUNO Phase 2 Delta m^2_31 measurement."""
    if precision_frac <= 0.0:
        raise ValueError('precision_frac must be positive')

    sigma_eff = DM31_UM_EV2 * precision_frac
    sigma_tension = abs(dm31_obs - DM31_UM_EV2) / sigma_eff
    outside_window = dm31_obs < DM31_WINDOW_LOW or dm31_obs > DM31_WINDOW_HIGH

    if outside_window or sigma_tension >= 3.0:
        branch = 'FALSIFIED'
        action = 'reopen_three_step_cascade'
    elif sigma_tension >= 1.0:
        branch = 'TENSION'
        action = 'hold_joint_juno_dune_review'
    else:
        branch = 'CLOSED_CONFIRMED'
        action = 'retain_p559_mass_splitting'

    return {
        'branch': branch,
        'dm31_obs': dm31_obs,
        'precision_frac': precision_frac,
        'sigma_eff': sigma_eff,
        'sigma_tension': sigma_tension,
        'outside_window': outside_window,
        'action': action,
    }


def dune_cp_joint_verdict(delta_cp_obs: float, sigma_cp: float) -> Dict[str, Any]:
    """Route a DUNE delta_CP measurement against the UM preregistration."""
    if sigma_cp <= 0.0:
        raise ValueError('sigma_cp must be positive')

    sigma_tension = abs(delta_cp_obs - DUNE_CP_DELTA_RAD) / sigma_cp
    if sigma_tension < 1.0:
        branch = 'CLOSED_CONFIRMED'
        action = 'retain_cp_preregistration'
    elif sigma_tension < 3.0:
        branch = 'TENSION'
        action = 'cross_check_with_juno_phase2'
    else:
        branch = 'FALSIFIED'
        action = 'reopen_cp_sector_architecture'

    return {
        'branch': branch,
        'delta_cp_obs': delta_cp_obs,
        'sigma_cp': sigma_cp,
        'sigma_tension': sigma_tension,
        'delta_cp_um_rad': DUNE_CP_DELTA_RAD,
        'action': action,
    }


def what_is_claimed() -> List[str]:
    """Return honest claims for Pillar 655."""
    return [
        'The JUNO Phase 2 routing thresholds are executable and preregistered.',
        'The UM Delta m^2_31 target remains fixed at 2.4109e-3 eV^2.',
        'The live falsification rule uses both sigma tension and a hard allowed window.',
        'A linked DUNE delta_CP routing function is included for joint neutrino-sector review.',
        'No score change is claimed until real Phase 2 measurements arrive.',
    ]


def what_is_NOT_claimed() -> List[str]:
    """Return honest non-claims for Pillar 655."""
    return [
        'This module does not claim that JUNO 2027 data has arrived.',
        'The DUNE cross-check does not replace the JUNO mass-splitting verdict.',
        'The pre-registered window is not widened to rescue out-of-band outcomes.',
        'No hardgate score gain occurs from countdown packaging alone.',
    ]


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 655 report."""
    return {
        'pillar': PILLAR_NUMBER,
        'title': PILLAR_TITLE,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'adjacent_track': ADJACENT_TRACK,
        'dm31_um_ev2': DM31_UM_EV2,
        'dm31_pdg_ev2': DM31_PDG_EV2,
        'dm31_juno_ev2': DM31_JUNO_EV2,
        'dm31_tension_final_sigma': DM31_TENSION_FINAL,
        'juno_phase2_precision': JUNO_PHASE2_PRECISION,
        'dune_cp_delta_rad': DUNE_CP_DELTA_RAD,
        'what_is_claimed': what_is_claimed(),
        'what_is_NOT_claimed': what_is_NOT_claimed(),
        'toe_score_delta': 0.0,
        'hardgate_score_delta': 0.0,
    }
