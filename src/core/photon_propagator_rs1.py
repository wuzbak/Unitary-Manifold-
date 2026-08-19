# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 772 — Photon propagator in the RS1 warped background.

This module isolates the gauge-field zero mode in the Randall-Sundrum 1 metric

    ds² = e^{-2k|y|} η_{μν} dx^μ dx^ν + dy²,

and records the leading KK correction and the Chern-Simons overlap suppression
relevant for birefringence.  For a bulk U(1) gauge field with Neumann/Neumann
boundary conditions, the zero mode is exactly flat:

    f₀(y) = 1 / sqrt(2πR)  on the covering interval y ∈ [-πR, πR],

so the four-dimensional zero-mode propagator is the ordinary massless photon
propagator G₀(p²) = 1/p² in Euclidean momentum convention.

The KK tower obeys the standard RS1 Bessel equation with approximate masses
mₙ ≈ xₙ M_KK, where xₙ are the first J₀ zeros and
M_KK = M_Pl exp(-πkR).  The birefringent Chern-Simons overlap with the radion
profile Φ_CS(y) = exp(-3k|y|) is

    I_CS = ∫ dy f₀²(y) Φ_CS(y)
         = (1 - exp(-3πkR)) / (3πkR),

which for πkR = 37 gives ≈ 9.009×10⁻³ and therefore
sqrt(I_CS) ≈ 9.49×10⁻².
"""
from __future__ import annotations

import math
from typing import Dict, List

from scipy.special import j0, j1, jn_zeros, y0, y1

PILLAR: int = 772
N_W: int = 5
K_CS: int = 74
PI_K_R: float = 37.0
M_PL_GEV: float = 1.22e19
M_KK_GEV: float = M_PL_GEV * math.exp(-PI_K_R)
PHOTON_KK_ROOTS = tuple(float(x) for x in jn_zeros(0, 6))
PILLAR_STATUS: str = "PHOTON_PROPAGATOR_RS1_DERIVED"

__all__ = [
    "PILLAR",
    "PILLAR_STATUS",
    "N_W",
    "K_CS",
    "PI_K_R",
    "M_PL_GEV",
    "M_KK_GEV",
    "PHOTON_KK_ROOTS",
    "photon_zero_mode_wavefunction",
    "photon_kk_spectrum",
    "photon_propagator_zero_mode",
    "cs_photon_overlap_integral",
    "birefringence_warp_correction",
    "photon_propagator_rs1_report",
]


def _validate_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def photon_zero_mode_wavefunction(pi_kr: float = PI_K_R) -> Dict:
    """Return the flat RS1 photon zero-mode profile.

    For the Z₂-even gauge zero mode on the covering interval [-πR, πR],

        f₀(y) = 1 / sqrt(2πR),   R = (πkR)/(π k).

    We set k = M_Pl for the numerical radius estimate, matching the RS1 scale
    convention used elsewhere in the repository.
    """
    _validate_positive("pi_kr", pi_kr)
    k_gev = M_PL_GEV
    radius_gev_inv = pi_kr / (math.pi * k_gev)
    normalization_length_gev_inv = 2.0 * math.pi * radius_gev_inv
    f0 = 1.0 / math.sqrt(normalization_length_gev_inv)
    return {
        "status": "DERIVED",
        "value": f0,
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "wavefunction": "f0(y) = 1/sqrt(2*pi*R)",
        "z2_parity": "even",
        "massless": True,
        "radius_gev_inv": radius_gev_inv,
        "normalization_length_gev_inv": normalization_length_gev_inv,
        "normalization_check": f0**2 * normalization_length_gev_inv,
        "pi_kr": pi_kr,
        "k_gev": k_gev,
    }


def photon_kk_spectrum(n_modes: int = 3, pi_kr: float = PI_K_R) -> Dict:
    """Return the leading RS1 photon KK masses and profile coefficients.

    The gauge KK masses satisfy the Neumann-boundary Bessel condition, whose
    leading approximation is mₙ ≈ xₙ M_KK with xₙ the J₀ zeros.  The bulk
    wavefunction is recorded as

        fₙ(y) = Nₙ exp(ky) [J₁(x) + bₙ Y₁(x)],
        x = mₙ exp(ky)/k,

    with bₙ fixed by the UV Neumann boundary condition.
    """
    _validate_positive("n_modes", float(n_modes))
    _validate_positive("pi_kr", pi_kr)
    m_kk = M_PL_GEV * math.exp(-pi_kr)
    modes: List[Dict] = []
    for idx, root in enumerate(PHOTON_KK_ROOTS[:n_modes], start=1):
        x_uv = root * math.exp(-pi_kr)
        numerator = -j0(x_uv)
        denominator = y0(x_uv)
        b_n = numerator / denominator if abs(denominator) > 1e-300 else 0.0
        modes.append(
            {
                "n": idx,
                "bessel_root_j0": root,
                "m_n_gev": root * m_kk,
                "m_over_mkk": root,
                "uv_argument": x_uv,
                "b_n": b_n,
                "wavefunction": "N_n exp(k y) [J1(x) + b_n Y1(x)]",
                "ir_profile_unnormalized": j1(root) + b_n * y1(root),
            }
        )
    return {
        "status": "DERIVED",
        "value": modes,
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "n_modes": n_modes,
        "pi_kr": pi_kr,
        "m_kk_gev": m_kk,
        "first_mode_mass_gev": modes[0]["m_n_gev"],
        "modes": modes,
    }


def photon_propagator_zero_mode(p2_gev2: float) -> Dict:
    """Return the Euclidean zero-mode photon propagator G₀(p²) = 1/p²."""
    if p2_gev2 < 0:
        raise ValueError("p2_gev2 must be non-negative in Euclidean convention")
    value = math.inf if p2_gev2 == 0 else 1.0 / p2_gev2
    return {
        "status": "DERIVED",
        "value": value,
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "p2_gev2": p2_gev2,
        "propagator": "1/p^2",
        "mass_pole_gev": 0.0,
    }


def cs_photon_overlap_integral(
    pi_kr: float = PI_K_R,
    n_w: int = N_W,
    k_cs: int = K_CS,
) -> Dict:
    """Return the warped photon-radion Chern-Simons overlap integral.

    Using the normalized zero mode on [-πR, πR],

        I_CS = (1/(2πR)) * 2 ∫₀^{πR} dy exp(-3ky)
             = (1 - exp(-3πkR)) / (3πkR).
    """
    _validate_positive("pi_kr", pi_kr)
    overlap = (1.0 - math.exp(-3.0 * pi_kr)) / (3.0 * pi_kr)
    beta_factor = math.sqrt(overlap)
    return {
        "status": "DERIVED",
        "value": overlap,
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "n_w": n_w,
        "k_cs": k_cs,
        "pi_kr": pi_kr,
        "overlap_integral": overlap,
        "beta_correction_factor": beta_factor,
        "large_warp_limit": 1.0 / (3.0 * pi_kr),
        "radion_profile": "Phi_CS(y) = exp(-3 k |y|)",
    }


def birefringence_warp_correction(beta_bare_deg: float, pi_kr: float = PI_K_R) -> Dict:
    """Apply the RS1 overlap suppression to a bare birefringence angle."""
    if beta_bare_deg < 0:
        raise ValueError("beta_bare_deg must be non-negative")
    overlap = cs_photon_overlap_integral(pi_kr=pi_kr)
    factor = overlap["beta_correction_factor"]
    beta_corrected = beta_bare_deg * factor
    return {
        "status": "DERIVED",
        "value": beta_corrected,
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "beta_bare_deg": beta_bare_deg,
        "beta_corrected_deg": beta_corrected,
        "warp_correction_factor": factor,
        "overlap_integral": overlap["overlap_integral"],
        "interpretation": (
            "The RS1 radion overlap suppresses the bare A∧F∧F contribution. "
            "Any phenomenological recovery of the observed birefringence window "
            "must come from the geometric CS coefficient, not from bulk overlap alone."
        ),
    }


def photon_propagator_rs1_report() -> Dict:
    """Return the complete Pillar 772 summary."""
    zero_mode = photon_zero_mode_wavefunction()
    spectrum = photon_kk_spectrum()
    overlap = cs_photon_overlap_integral()
    beta = birefringence_warp_correction(beta_bare_deg=0.302)
    kk_correction_scale = sum(1.0 / mode["m_over_mkk"] ** 2 for mode in spectrum["modes"]) / M_KK_GEV**2
    return {
        "status": PILLAR_STATUS,
        "value": {
            "zero_mode_propagator": "1/p^2",
            "kk_correction_low_energy_scale_gev_minus2": kk_correction_scale,
        },
        "epistemic_status": "DERIVED",
        "pillar": PILLAR,
        "n_w": N_W,
        "k_cs": K_CS,
        "pi_kr": PI_K_R,
        "m_kk_gev": M_KK_GEV,
        "zero_mode": zero_mode,
        "kk_spectrum": spectrum,
        "cs_overlap": overlap,
        "beta_example": beta,
        "summary": (
            "Flat Z2-even photon zero mode stays exactly massless; KK photons start "
            "at x1 M_KK ≈ 2.5 TeV; the CS-radion overlap is suppressed by ~9.0e-3."
        ),
    }
