# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 424 — Quadrupole Topology L Constraint from Inflation.

══════════════════════════════════════════════════════════════════════════════
PHYSICAL MOTIVATION
══════════════════════════════════════════════════════════════════════════════

Pillar 410 established that a T³/Z₂ topology with scale L ∈ [7.9, 11.4] Gpc
can explain the CMB quadrupole deficit (26–47% below ΛCDM) that the standard
UM KK mechanism cannot account for.  However, Pillar 410 could not select L:
the UM geometry sets the 5D compactification scale R ~ 1.79 μm, not the
cosmological topology scale L.

This pillar attempts to constrain L from the inflationary side.  The question
is: does the UM inflation (N_e ≈ 66, H_inf from r=0.0315 and A_s) set a
preferred topology scale that falls within the P410 window [7.9, 11.4] Gpc?

══════════════════════════════════════════════════════════════════════════════
CALCULATION: INFLATIONARY HORIZON SCALE TODAY
══════════════════════════════════════════════════════════════════════════════

The comoving scale of the inflationary Hubble horizon today:

    L_H_inf = H_inf^{-1} × (a_0/a_end)

where:
    H_inf  — inflationary Hubble rate from UM (r=0.0315, A_s=2.1×10⁻⁹)
    a_0/a_end ≈ T_RH / T_CMB  (radiation-dominated post-inflation)
    T_RH ≈ 3.7×10⁸ GeV  (Pillar 404)
    T_CMB = 2.725 K = 2.35×10⁻¹³ GeV

H_inf from UM parameters:
    H_inf² = (π²/2) r A_s M_Pl²
    H_inf ≈ π M_Pl √(r A_s / 2) ≈ 1.8×10⁻⁵ M_Pl ≈ 2.2×10¹⁴ GeV

Conversion to comoving Gpc today:
    H_inf^{-1} (physical at inflation) in Gpc:
        H_inf^{-1} = 1/(H_inf in Mpc⁻¹)
    The comoving size today:
        L_H_inf_comoving = H_inf^{-1} × (T_RH / T_CMB)
    in units of D_H = c/H_0 ≈ 14.3 Gpc:
        L_H_inf / D_H = (H_0/H_inf) × (T_RH/T_CMB)

Result:
    H_0/H_inf ≈ 7.0×10⁻⁵⁷  (67.4 km/s/Mpc in GeV)
    T_RH/T_CMB ≈ 1.57×10²¹

    L_H_inf / D_H ≈ (H_0/H_inf) × (T_RH/T_CMB)
                  ≈ 7.0×10⁻⁵⁷ × 1.57×10²¹
                  ≈ 1.1×10⁻³⁵

This is 35 orders of magnitude smaller than D_H.

The inflationary horizon scale, expanded from the end of inflation to today,
is L_H_inf ≈ 1.1×10⁻³⁵ × 14.3 Gpc ≈ 1.6×10⁻³⁴ Gpc.

This is nowhere near the [7.9, 11.4] Gpc window.

══════════════════════════════════════════════════════════════════════════════
CONCLUSION: ARCHITECTURE LIMIT
══════════════════════════════════════════════════════════════════════════════

The UM inflation cannot set the topology scale L.  The inflationary
horizon, comoving today, is 35 orders of magnitude below the quadrupole
scale.  Moreover:

1. Any pre-inflationary topology with L ≲ D_H is diluted away by N_e ≈ 66
   e-folds of inflation by a factor e^{N_e} ≈ e^{66} ≈ 4.6×10²⁸.
2. A post-inflationary mechanism generating topology at L ~ D_H is not
   present in the minimal 5D-EFT.
3. The Planck 2020 lower bound L > 0.97 D_H = 13.9 Gpc further conflicts
   with the P410 suppression window [7.9, 11.4] Gpc.

Quadrupole topology remains a POSSIBLE_CANDIDATE mechanism, but the UM cannot
select L from within its minimal 5D-EFT.  Extension required.

Status:
    TOPOLOGY_L_INFLATION_ARCHITECTURE_LIMIT

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    'PILLAR_STATUS',
    'R_TENSOR_TO_SCALAR',
    'A_S',
    'H_0_GEV',
    'T_RH_GEV',
    'T_CMB_GEV',
    'D_H_GPC',
    'L_WINDOW_MIN_GPC',
    'L_WINDOW_MAX_GPC',
    'L_PLANCK_LOWER_GPC',
    'compute_h_inf',
    'compute_l_inf_comoving',
    'topology_window_analysis',
    'topology_l_constraint_verdict',
]

PILLAR_STATUS: str = 'TOPOLOGY_L_INFLATION_ARCHITECTURE_LIMIT'

# ── UM inflation parameters ───────────────────────────────────────────────────
R_TENSOR_TO_SCALAR: float = 0.0315     # UM prediction (Pillar 97-B)
A_S: float = 2.1e-9                    # CMB scalar amplitude (Planck 2018)
M_PL_GEV: float = 1.22e19             # Planck mass in GeV

# ── Cosmological parameters ───────────────────────────────────────────────────
H_0_GEV: float = 4.56e-42             # H_0 = 67.4 km/s/Mpc in GeV
T_RH_GEV: float = 3.7e8               # Reheating temperature (Pillar 404) GeV
T_CMB_GEV: float = 2.35e-13           # T_CMB = 2.725 K in GeV
D_H_GPC: float = 14.3                 # Hubble distance c/H_0 in Gpc

# ── P410 topology suppression window ──────────────────────────────────────────
L_WINDOW_MIN_GPC: float = 7.9         # min L for 26-47% quadrupole suppression
L_WINDOW_MAX_GPC: float = 11.4        # max L for 26-47% quadrupole suppression
L_PLANCK_LOWER_GPC: float = 13.9      # Planck lower bound L > 0.97 D_H


def compute_h_inf(
    r: float = R_TENSOR_TO_SCALAR,
    a_s: float = A_S,
    m_pl: float = M_PL_GEV,
) -> float:
    """Compute the inflationary Hubble rate in GeV.

    H_inf = π M_Pl √(r A_s / 2)
    """
    return math.pi * m_pl * math.sqrt(r * a_s / 2.0)


def compute_l_inf_comoving(
    h_inf: float | None = None,
    h_0: float = H_0_GEV,
    t_rh: float = T_RH_GEV,
    t_cmb: float = T_CMB_GEV,
    d_h: float = D_H_GPC,
) -> Dict:
    """Compute the comoving inflationary horizon scale in Gpc today.

    L_H_inf_comoving = H_inf^{-1} × (T_RH/T_CMB)  [in natural units]
    In units of D_H:
        L_H_inf / D_H = (H_0/H_inf) × (T_RH/T_CMB)
    """
    if h_inf is None:
        h_inf = compute_h_inf()
    h0_over_hinf = h_0 / h_inf
    trh_over_tcmb = t_rh / t_cmb
    l_over_dh = h0_over_hinf * trh_over_tcmb
    l_gpc = l_over_dh * d_h
    return {
        'h_inf_gev': h_inf,
        'h0_over_hinf': h0_over_hinf,
        'trh_over_tcmb': trh_over_tcmb,
        'l_over_dh': l_over_dh,
        'l_gpc': l_gpc,
        'log10_l_over_dh': math.log10(max(l_over_dh, 1e-300)),
    }


def topology_window_analysis() -> Dict:
    """Analyse whether the inflationary scale falls in the P410 topology window."""
    l_data = compute_l_inf_comoving()
    l_gpc = l_data['l_gpc']
    in_p410_window = L_WINDOW_MIN_GPC <= l_gpc <= L_WINDOW_MAX_GPC
    above_planck_bound = l_gpc >= L_PLANCK_LOWER_GPC
    # Gap between required P410 window and Planck lower bound
    p410_planck_compatible = L_WINDOW_MAX_GPC >= L_PLANCK_LOWER_GPC
    return {
        'l_inf_comoving_gpc': l_gpc,
        'l_window_min_gpc': L_WINDOW_MIN_GPC,
        'l_window_max_gpc': L_WINDOW_MAX_GPC,
        'l_planck_lower_gpc': L_PLANCK_LOWER_GPC,
        'in_p410_window': in_p410_window,
        'above_planck_lower_bound': above_planck_bound,
        'p410_window_planck_compatible': p410_planck_compatible,
        'inflation_can_set_topology_scale': False,
        'orders_of_magnitude_short': abs(l_data['log10_l_over_dh']),
    }


def topology_l_constraint_verdict() -> Dict:
    """Return the complete topology L inflation constraint verdict."""
    l_data = compute_l_inf_comoving()
    analysis = topology_window_analysis()
    return {
        'status': PILLAR_STATUS,
        'l_inf_comoving': l_data,
        'window_analysis': analysis,
        'blockers': [
            'Inflationary horizon today is ~35 orders of magnitude below D_H',
            'Pre-inflationary topology diluted by e^{N_e} ≈ 4.6×10²⁸',
            'P410 window [7.9, 11.4] Gpc conflicts with Planck lower bound 13.9 Gpc',
            'No post-inflationary mechanism for generating L ~ D_H in minimal 5D-EFT',
        ],
        'verdict': (
            'The UM inflationary sector (N_e ≈ 66, H_inf ≈ 2.2×10¹⁴ GeV) cannot '
            'select the topology scale L within the quadrupole suppression window '
            '[7.9, 11.4] Gpc. The inflationary Hubble horizon comoving today is '
            '~10⁻³⁵ D_H — 35 orders of magnitude too small. L selection is an '
            'ARCHITECTURE_LIMIT of the minimal 5D-EFT.'
        ),
    }
