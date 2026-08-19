# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Pillar 747 — External Falsification Readiness Audit.

Collects active falsification windows and deterministic routing functions for
incoming observations.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""
from __future__ import annotations

PILLAR = 747
STATUS = 'READY'
EPISTEMIC_LABEL = 'DERIVED'
FALSIFICATION_WINDOWS = [
    {'id': 'litebird', 'prediction': (0.273, 0.331), 'window': (0.22, 0.38), 'gap': (0.29, 0.31)},
    {'id': 'cmbs4', 'prediction': 0.0315, 'limit': 0.01},
    {'id': 'spherex', 'prediction': -0.532, 'sigma': 1.6},
    {'id': 'desi_dr3', 'prediction': 0.0, 'sigma_threshold': 3.0},
    {'id': 'nedm', 'prediction': 7.76e-27, 'limit': 1.8e-26},
    {'id': 'hllhc', 'prediction': 5.0, 'limit': 5.0},
    {'id': 'juno', 'prediction': 2.4109e-3, 'window': (2.2e-3, 2.7e-3)},
]


def route_litebird(beta_obs: float) -> str:
    lo, hi = 0.22, 0.38
    gap_lo, gap_hi = 0.29, 0.31
    if beta_obs < lo or beta_obs > hi or gap_lo <= beta_obs <= gap_hi:
        return 'FALSIFIED'
    return 'PASS'


def route_cmbs4(r_obs: float) -> str:
    return 'FALSIFIED' if r_obs < 0.01 else 'PASS'


def route_spherex(fnl_obs: float) -> str:
    sigma = abs(fnl_obs + 0.532) / 1.6
    return 'TENSION' if sigma > 2.0 else 'PASS'


def route_desi_dr3(wa_sigma: float) -> str:
    return 'FALSIFIED' if wa_sigma >= 3.0 else 'TENSION' if wa_sigma >= 2.0 else 'PASS'


def route_nedm(dn_obs: float) -> str:
    return 'FALSIFIED' if abs(dn_obs) > 1.8e-26 else 'PASS'


def route_hllhc(m_gkk_tev: float) -> str:
    return 'FALSIFIED' if m_gkk_tev < 5.0 else 'PASS'


def route_juno(dm31_sq: float) -> str:
    return 'FALSIFIED' if not (2.2e-3 <= dm31_sq <= 2.7e-3) else 'PASS'


def audit_all_windows() -> dict:
    return {
        'pillar': PILLAR,
        'label': 'EXTERNAL_FALSIFICATION_READINESS_AUDIT',
        'status': STATUS,
        'epistemic_label': EPISTEMIC_LABEL,
        'window_count': len(FALSIFICATION_WINDOWS),
        'windows': FALSIFICATION_WINDOWS,
        'routes': ['route_litebird', 'route_cmbs4', 'route_spherex', 'route_desi_dr3', 'route_nedm', 'route_hllhc', 'route_juno'],
        'honest_note': 'These callables route observations only; they do not replace the underlying experimental analyses.',
    }


TEST_EXPECTATIONS = {
    'scalar_checks': {'PILLAR': 747, 'STATUS': 'READY', 'EPISTEMIC_LABEL': 'DERIVED'},
    'float_checks': {},
    'main_function': 'audit_all_windows',
    'required_symbols': ['route_litebird', 'route_cmbs4', 'route_spherex', 'route_desi_dr3', 'route_nedm', 'route_hllhc', 'route_juno', 'audit_all_windows', 'FALSIFICATION_WINDOWS', 'TEST_EXPECTATIONS'],
    'required_keys': ['pillar', 'label', 'status', 'epistemic_label', 'window_count', 'windows', 'routes', 'honest_note'],
}
