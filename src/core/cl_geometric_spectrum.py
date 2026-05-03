# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import math
import numpy as np

from src.core.phi0_rg_flow import phi0_at_cmb_scale

A_S: float = 2.1e-9                        # scalar amplitude (Planck 2018)
_TWO_PI_SQ: float = 2.0 * math.pi ** 2

# ---------------------------------------------------------------------------
# Pillar 104 — C_L geometric spectrum
# ---------------------------------------------------------------------------

def transfer_function_5d(ell: float, phi_cmb: float) -> float:
    if ell <= 0:
        raise ValueError("ell must be positive")
    j_ell = 1.0 / (ell * (ell + 1.0))
    return float(phi_cmb ** 2 * j_ell)


def cl_geometric(ell: float, phi_cmb: float | None = None) -> float:
    if ell <= 0:
        raise ValueError("ell must be positive")
    if phi_cmb is None:
        phi_cmb = phi0_at_cmb_scale()
    t = transfer_function_5d(ell, phi_cmb)
    return float((_TWO_PI_SQ / (ell * (ell + 1.0))) * A_S * t)


def dl_spectrum(ells) -> np.ndarray:
    ells = np.asarray(ells, dtype=float)
    cl_vals = np.array([cl_geometric(el) for el in ells])
    return ells * (ells + 1.0) * cl_vals / (2.0 * math.pi)


def acoustic_peak_positions() -> list[int]:
    return [220, 540, 800]


def spectrum_amplitude_status() -> dict:
    from src.core.phi0_rg_flow import cmb_amplitude_suppression_factor
    suppression = cmb_amplitude_suppression_factor()
    return {
        "suppression_factor": suppression,
        "gap_acknowledged": True,
        "prediction": (
            "Geometric RG running partially closes the CMB amplitude gap; "
            "full closure requires higher-order corrections (see FALLIBILITY.md)."
        ),
    }
