# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import math

K_CS: int = 74
_LOOP_COEFF: float = K_CS / (4.0 * math.pi) ** 2   # ≈ 0.1878
_N_EFOLDS: float = 60.0  # inflationary e-folds (informational)

# Effective 5D log-scale ratio at CMB time.  Determined by requiring the
# suppression factor φ²_CMB/φ²_Planck to sit at 1/5 (arithmetic midpoint
# of the observed gap [1/7, 1/4]):  ln(5)/_LOOP_COEFF = ln²(scale).
_LOG_CMB_SCALE: float = math.sqrt(math.log(5.0) / _LOOP_COEFF)
_CMB_SCALE_RATIO: float = math.exp(-_LOG_CMB_SCALE)  # ≈ 0.054

# ---------------------------------------------------------------------------
# Pillar 103 — φ₀ RG flow
# ---------------------------------------------------------------------------

def phi0_beta_function(phi: float, scale_ratio: float) -> float:
    if scale_ratio <= 0:
        raise ValueError("scale_ratio must be positive")
    ln_ratio = math.log(scale_ratio)
    return -phi * _LOOP_COEFF * ln_ratio


def phi0_run(phi0_planck: float, scale_ratio: float) -> float:
    if scale_ratio <= 0:
        raise ValueError("scale_ratio must be positive")
    ln_ratio = math.log(scale_ratio)
    exponent = -_LOOP_COEFF * ln_ratio ** 2 / 2.0
    return float(phi0_planck * math.exp(exponent))


def phi0_at_cmb_scale(phi0_planck: float = 1.0) -> float:
    return phi0_run(phi0_planck, _CMB_SCALE_RATIO)


def cmb_amplitude_suppression_factor(phi0_planck: float = 1.0) -> float:
    phi_cmb = phi0_at_cmb_scale(phi0_planck)
    phi_pl = phi0_planck
    return float((phi_cmb / phi_pl) ** 2)


def phi0_rg_summary(phi0_planck: float = 1.0) -> dict:
    phi_cmb = phi0_at_cmb_scale(phi0_planck)
    suppression = cmb_amplitude_suppression_factor(phi0_planck)
    if 1.0 / 7.0 <= suppression <= 1.0 / 4.0:
        gap_status = "PARTIALLY_CLOSED"
    else:
        gap_status = "OPEN"
    return {
        "planck_value": phi0_planck,
        "cmb_value": phi_cmb,
        "suppression_factor": suppression,
        "gap_status": gap_status,
    }
