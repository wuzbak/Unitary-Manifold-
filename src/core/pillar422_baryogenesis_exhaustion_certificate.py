# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 422 — Baryogenesis Exhaustion Certificate.

══════════════════════════════════════════════════════════════════════════════
PHYSICAL MOTIVATION
══════════════════════════════════════════════════════════════════════════════

The observed baryon asymmetry is η_B = n_B / n_γ ≈ 6.1×10⁻¹⁰ (Planck 2018).
Generating this asymmetry requires satisfying the Sakharov conditions:
(1) baryon number violation, (2) C/CP violation, (3) departure from
thermal equilibrium.

Within the minimal Unitary Manifold 5D-EFT, five independent baryogenesis
pathways have been audited:

    Path 1 — Thermal leptogenesis (KK seesaw):
        Pillar 323 established that the KK seesaw scale M_R ~ M_KK^exp(πkR) >>
        10¹⁴ GeV; the washout factor is not resonant; leptogenesis efficiency
        is O(10⁻⁹). ARCHITECTURE_LIMIT.

    Path 2 — KK electroweak baryogenesis (sphaleron):
        Pillar 365 (honest reckoning) established the central estimate
        η_B^{KK} ~ 10⁻¹³, a factor ~2000× below the observed value.
        Even with O(30) systematic uncertainty: still 100× short.
        ARCHITECTURE_LIMIT.

    Path 3 — Affleck-Dine in KK geometry:
        Pillar 370 showed that the AD condensate decays at T_decay > T_EW;
        the CP phase O(1) is present but the condensate is diluted before
        baryogenesis can proceed. ARCHITECTURE_LIMIT.

    Path 4 — KK-EWPT baryogenesis:
        Pillar 371 showed KK modes are exponentially suppressed at T_EW;
        v/T_c ≈ 0.3 < 1 (insufficient first-order EW phase transition).
        ARCHITECTURE_LIMIT.

    Path 5 — Resonant leptogenesis:
        Pillar 409 showed the braid lattice produces ΔM_R/M_R ≈ 5.0,
        while resonant leptogenesis requires ΔM_R/M_R ~ 4×10⁻⁵;
        the ratio is 10⁵× wrong. ARCHITECTURE_LIMIT.

This pillar certifies the exhaustion: all known baryogenesis pathways within
the minimal 5D-EFT are ARCHITECTURE_LIMIT. Baryogenesis requires an extension
(6D UV completion or non-minimal sector).

Status:
    ALL_BARYOGENESIS_PATHS_EXHAUSTED

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

from typing import Dict, List

__all__ = [
    'PILLAR_STATUS',
    'ETA_B_OBSERVED',
    'N_PATHS_AUDITED',
    'baryogenesis_paths_registry',
    'all_paths_architecture_limit',
    'baryogenesis_exhaustion_verdict',
    'extension_requirements',
]

PILLAR_STATUS: str = 'ALL_BARYOGENESIS_PATHS_EXHAUSTED'
ETA_B_OBSERVED: float = 6.1e-10    # Planck 2018 baryon asymmetry
N_PATHS_AUDITED: int = 5


def baryogenesis_paths_registry() -> List[Dict]:
    """Return the full registry of all audited baryogenesis paths."""
    return [
        {
            'path': 1,
            'name': 'Thermal leptogenesis (KK seesaw)',
            'source_pillar': 'Pillar 323',
            'blocker': 'M_R >> 10¹⁴ GeV; washout not resonant; efficiency O(10⁻⁹)',
            'eta_b_estimate': 1.0e-19,
            'shortfall_factor': ETA_B_OBSERVED / 1.0e-19,
            'status': 'ARCHITECTURE_LIMIT',
            'closed_by': 'Pillar 323 (leptogenesis scale audit)',
        },
        {
            'path': 2,
            'name': 'KK electroweak baryogenesis (sphaleron)',
            'source_pillar': 'Pillar 365',
            'blocker': 'Central estimate η_B ~ 10⁻¹³; O(30) uncertainty insufficient',
            'eta_b_estimate': 1.0e-13,
            'shortfall_factor': ETA_B_OBSERVED / 1.0e-13,
            'status': 'ARCHITECTURE_LIMIT',
            'closed_by': 'Pillar 365 (honest reckoning)',
        },
        {
            'path': 3,
            'name': 'Affleck-Dine in KK geometry',
            'source_pillar': 'Pillar 370',
            'blocker': 'AD condensate decays before EW epoch; dilution before baryogenesis',
            'eta_b_estimate': 0.0,
            'shortfall_factor': float('inf'),
            'status': 'ARCHITECTURE_LIMIT',
            'closed_by': 'Pillar 370 (condensate decay timing)',
        },
        {
            'path': 4,
            'name': 'KK-EWPT baryogenesis',
            'source_pillar': 'Pillar 371',
            'blocker': 'KK modes exp-suppressed at T_EW; v/T_c = 0.3 < 1',
            'eta_b_estimate': 0.0,
            'shortfall_factor': float('inf'),
            'status': 'ARCHITECTURE_LIMIT',
            'closed_by': 'Pillar 371 (phase transition analysis)',
        },
        {
            'path': 5,
            'name': 'Resonant leptogenesis (braid lattice)',
            'source_pillar': 'Pillar 409',
            'blocker': 'ΔM_R/M_R ≈ 5.0 vs required ~4×10⁻⁵; ratio 10⁵× wrong',
            'eta_b_estimate': 0.0,
            'shortfall_factor': float('inf'),
            'status': 'ARCHITECTURE_LIMIT',
            'closed_by': 'Pillar 409 (resonant degeneracy analysis)',
        },
    ]


def all_paths_architecture_limit() -> bool:
    """Return True if all audited baryogenesis paths are ARCHITECTURE_LIMIT."""
    paths = baryogenesis_paths_registry()
    return all(p['status'] == 'ARCHITECTURE_LIMIT' for p in paths)


def extension_requirements() -> Dict:
    """Return the honest statement of what is required to close baryogenesis."""
    return {
        'status': 'EXTENSION_REQUIRED',
        'minimal_5d_eft': 'ALL_PATHS_EXHAUSTED',
        'possible_extensions': [
            '6D UV completion with additional flat dimension',
            'Non-minimal sector (e.g., additional gauge field, extra scalar)',
            'Pre-inflationary baryogenesis from UV physics above M_KK',
            'Spontaneous baryogenesis from time-varying CP-odd condensate',
        ],
        'honest_statement': (
            'The minimal 5D-EFT Unitary Manifold framework cannot explain the observed '
            'baryon asymmetry η_B ≈ 6.1×10⁻¹⁰. All five known baryogenesis pathways '
            '(thermal leptogenesis, KK sphaleron, Affleck-Dine, KK-EWPT, resonant '
            'leptogenesis) face genuine architecture limits. Extension to 6D UV completion '
            'or a non-minimal sector is required. This is not a theoretical oversight — it '
            'is a known, named, and measured architecture limit of the minimal framework.'
        ),
    }


def baryogenesis_exhaustion_verdict() -> Dict:
    """Return the complete baryogenesis exhaustion certificate."""
    paths = baryogenesis_paths_registry()
    exhausted = all_paths_architecture_limit()
    ext = extension_requirements()
    return {
        'status': PILLAR_STATUS,
        'n_paths_audited': N_PATHS_AUDITED,
        'all_exhausted': exhausted,
        'eta_b_observed': ETA_B_OBSERVED,
        'paths': paths,
        'extension': ext,
        'verdict': (
            f'All {N_PATHS_AUDITED} baryogenesis pathways within the minimal '
            f'5D-EFT are ARCHITECTURE_LIMIT. Baryogenesis requires a UV '
            f'extension beyond the current framework.'
        ),
    }
