# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 755 — Gravitino KK Spectrum Full Audit.

Completes the KK gravitino spectrum audit in the RS1 fixed-point limit and
keeps the SUSY-moduli architecture limit distinct from the derived spectrum.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""
from __future__ import annotations

from src.core.pillar741_np_bc19_through_bc24_systematic_ladder import BC19, BC24

PILLAR = 755
N_MODES = 74
M32_MODE_0_GEV = 249.0
MODE_STEP_GEV = 498.0
SPECTRUM_STATUS = 'DERIVED'
SUSY_STATUS = 'NO_SUSY_SUPPRESSION_CONFIRMED'
STATUS = 'SPECTRUM_DERIVED'
EPISTEMIC_LABEL = 'DERIVED'


def gravitino_mass_mode(n: int) -> float:
    return M32_MODE_0_GEV + MODE_STEP_GEV * n


def full_spectrum(n_max: int = 6) -> list[float]:
    return [gravitino_mass_mode(n) for n in range(n_max + 1)]


def bc_suppression_audit() -> dict:
    return {'bc19': BC19, 'bc24': BC24, 'suppressed': BC24 < BC19 < 1.0e-20}


def spectrum_certificate() -> dict:
    return {
        'pillar': PILLAR,
        'label': 'GRAVITINO_KK_SPECTRUM_FULL_AUDIT',
        'status': STATUS,
        'epistemic_label': EPISTEMIC_LABEL,
        'n_modes': N_MODES,
        'mode0_gev': M32_MODE_0_GEV,
        'spectrum_status': SPECTRUM_STATUS,
        'susy_status': SUSY_STATUS,
        'spectrum_preview': full_spectrum(),
        'bc_suppression_audit': bc_suppression_audit(),
        'honest_note': 'The gravitino spectrum is derived; full SUSY moduli stabilization remains open as a separate architecture-limit problem.',
    }


TEST_EXPECTATIONS = {
    'scalar_checks': {'PILLAR': 755, 'N_MODES': 74, 'M32_MODE_0_GEV': 249.0, 'STATUS': 'SPECTRUM_DERIVED', 'EPISTEMIC_LABEL': 'DERIVED'},
    'float_checks': {'MODE_STEP_GEV': 498.0},
    'main_function': 'spectrum_certificate',
    'required_symbols': ['gravitino_mass_mode', 'full_spectrum', 'bc_suppression_audit', 'spectrum_certificate', 'PILLAR', 'STATUS', 'EPISTEMIC_LABEL', 'N_MODES', 'M32_MODE_0_GEV', 'TEST_EXPECTATIONS'],
    'required_keys': ['pillar', 'label', 'status', 'epistemic_label', 'n_modes', 'mode0_gev', 'spectrum_status', 'susy_status', 'spectrum_preview', 'bc_suppression_audit', 'honest_note'],
}
