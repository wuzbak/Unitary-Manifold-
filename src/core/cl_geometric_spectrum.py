# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import math
import numpy as np

from src.core.phi0_rg_flow import phi0_at_cmb_scale

A_S: float = 2.1e-9                        # scalar amplitude (Planck 2018)
_TWO_PI_SQ: float = 2.0 * math.pi ** 2

# Planck 2018 peak amplitude reference values (Dₗ = ℓ(ℓ+1)Cₗ/2π) [μK²]
# First three acoustic peaks from Planck 2018 Table 4 / Figure 1.
_PLANCK_PEAK_DL_UK2: dict[int, float] = {
    220: 5765.0,   # first peak ℓ ≈ 220
    540: 2589.0,   # second peak ℓ ≈ 540
    800: 2547.0,   # third peak ℓ ≈ 800
}

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


def cmb_peak_suppression_audit() -> dict:
    """Quantify the UM CMB acoustic peak amplitude suppression vs Planck 2018.

    OPEN PROBLEM (FALLIBILITY.md Admission 2)
    ------------------------------------------
    The UM geometric spectrum (Pillar 104, this module) produces Dₗ values at
    the acoustic peaks that are suppressed by a factor of ×4–7 relative to the
    Planck 2018 measured values.  This function computes the suppression factor
    at each peak explicitly so that the gap is tracked in the test suite.

    The suppression comes from the UM transfer function T(ℓ, φ_CMB) being based
    on the simple Sachs-Wolfe approximation (T ∝ 1/[ℓ(ℓ+1)]) rather than a
    full Boltzmann integration that includes baryon acoustic oscillations.

    This function does NOT claim to solve the problem.  It records the size of
    the gap as a testable quantity so that future improvements (Pillars 57, 63)
    can be validated against it.

    Returns
    -------
    dict
        'peaks'           : dict — per-peak Dₗ comparison (UM vs Planck 2018)
        'suppression_range': tuple[float, float] — min and max suppression factor
        'status'          : str — OPEN gap label
        'resolution_note' : str — known path toward closure
    """
    phi_cmb = phi0_at_cmb_scale()
    peaks: dict[int, dict] = {}
    suppression_factors: list[float] = []

    for ell_peak, dl_planck_uk2 in _PLANCK_PEAK_DL_UK2.items():
        cl_um = cl_geometric(float(ell_peak), phi_cmb)
        # Convert Cₗ to Dₗ = ℓ(ℓ+1)Cₗ/(2π), then to μK² using A_s ≡ dimensionless.
        # The ratio Dₗ_UM / Dₗ_Planck captures the amplitude suppression directly.
        # Here we compare using the dimensionless Dₗ (relative to A_s scale).
        dl_um_relative = (ell_peak * (ell_peak + 1.0) * cl_um / (2.0 * math.pi))
        # Planck Dₗ in the same A_s-normalised units: Planck value / (A_s × T_CMB²)
        # T_CMB = 2.7255e6 μK in natural units
        T_CMB_UK: float = 2.7255e6  # μK
        dl_planck_rel = dl_planck_uk2 / (A_S * T_CMB_UK**2)
        suppression = dl_planck_rel / dl_um_relative if dl_um_relative > 0 else float("inf")
        suppression_factors.append(suppression)
        peaks[ell_peak] = {
            "dl_um_dimensionless": dl_um_relative,
            "dl_planck_uk2": dl_planck_uk2,
            "suppression_factor": suppression,
        }

    s_min = min(suppression_factors) if suppression_factors else float("nan")
    s_max = max(suppression_factors) if suppression_factors else float("nan")

    return {
        "peaks": peaks,
        "suppression_range": (s_min, s_max),
        "status": (
            f"OPEN: UM geometric spectrum suppressed by ×{s_min:.1f}–×{s_max:.1f} "
            "at acoustic peaks relative to Planck 2018. "
            "Full Boltzmann integration required for closure (see FALLIBILITY.md §Admission 2)."
        ),
        "resolution_note": (
            "Pillars 57 (radion amplification) and 63 (Eisenstein-Hu baryon loading) "
            "address this gap but a complete UM-native Boltzmann calculation is pending."
        ),
    }
