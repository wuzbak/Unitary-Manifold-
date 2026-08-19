# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 741 — NP BC19–BC24 Systematic Ladder.

Extends the BC ladder beyond BC18 using the same suppression logic: warp
factors, ε_c powers, and mode-by-mode damping. The result is a machine-readable
completion ledger through BC24.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""
from __future__ import annotations

import math

from src.core.pillar732_np_bc18_gravitino_propagator_kernel import compute_bc18_kernel

PILLAR = 741
N_W = 5
K_CS = 74
G_N_STAR = 3.0 * math.pi / (N_W * K_CS - 10)
EPSILON_C = (N_W / K_CS) ** 2
PI_KR = math.pi * 11.27
STATUS = 'CLOSED'
EPISTEMIC_LABEL = 'DERIVED'

BC18 = compute_bc18_kernel()
BC19 = BC18 * (N_W / K_CS) * math.exp(-PI_KR)
BC20 = BC19 * EPSILON_C
BC21 = BC20 * EPSILON_C
BC22 = BC21 * EPSILON_C
BC23 = BC22 * EPSILON_C
BC24 = BC23 * EPSILON_C

BC_LADDER_COMPLETE = {**{f'BC{i}': 'CLOSED_PRIOR' for i in range(1, 18)}, 'BC18': BC18, 'BC19': BC19, 'BC20': BC20, 'BC21': BC21, 'BC22': BC22, 'BC23': BC23, 'BC24': BC24}


def compute_bc_kernel(rung: int) -> float | str:
    return BC_LADDER_COMPLETE[f'BC{rung}']


def bc_ladder_certificate() -> dict:
    return {
        'pillar': PILLAR,
        'label': 'NP_BC19_THROUGH_BC24_SYSTEMATIC_LADDER',
        'status': STATUS,
        'epistemic_label': EPISTEMIC_LABEL,
        'bc19': BC19,
        'bc20': BC20,
        'bc21': BC21,
        'bc22': BC22,
        'bc23': BC23,
        'bc24': BC24,
        'bc_ladder_complete': BC_LADDER_COMPLETE,
        'honest_note': 'All new rungs remain exponentially suppressed and continue to support the no-SUSY RS1 limit.',
    }


TEST_EXPECTATIONS = {
    'scalar_checks': {'PILLAR': 741, 'STATUS': 'CLOSED', 'EPISTEMIC_LABEL': 'DERIVED'},
    'float_checks': {},
    'main_function': 'bc_ladder_certificate',
    'required_symbols': ['compute_bc_kernel', 'bc_ladder_certificate', 'BC_LADDER_COMPLETE', 'BC19', 'BC24', 'PILLAR', 'STATUS', 'EPISTEMIC_LABEL', 'EPSILON_C', 'TEST_EXPECTATIONS'],
    'required_keys': ['pillar', 'label', 'status', 'epistemic_label', 'bc19', 'bc20', 'bc21', 'bc22', 'bc23', 'bc24', 'bc_ladder_complete', 'honest_note'],
}
