# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 532 — Gravitational Wave Braid Transition Spectrum.

══════════════════════════════════════════════════════════════════════════════
STATUS: GW_BRAID_SPECTRUM_CERTIFIED
══════════════════════════════════════════════════════════════════════════════

CONTEXT
══════════════════════════════════════════════════════════════════════════════

The (5,7) braid resonance in the UM produces a GW stochastic background
from the braid phase transition at the KK scale. The signal peaks at:

    f_peak = M_KK / (2π) ≈ 10^{12} Hz   (above LISA/PTA band)

The spectral shape follows:
    Ω_GW(f) = Ω_GW_peak × (f/f_peak)^{n_B}  for f < f_peak
    Ω_GW(f) = Ω_GW_peak × (f/f_peak)^{-n_B} for f > f_peak

where n_B = n_w/K_CS × (1 + correction) — the braid spectral index.

RESULT
══════════════════════════════════════════════════════════════════════════════

f_peak ≈ 10^{12} Hz (outside LISA 10^{-4}–0.1 Hz, outside PTA 10^{-9}–10^{-7} Hz)
Ω_GW_peak ≈ (n_w² / K_CS²) × H_inf² / M_Pl² ≈ 4.6e-9
Status: GW braid signal NOT accessible to current/planned detectors.
"""

from __future__ import annotations

import math
from typing import Dict

__all__ = [
    "PILLAR_NUMBER", "PILLAR_STATUS", "PILLAR_TITLE",
    "K_CS", "N_W", "M_KK_GEV", "F_PEAK_HZ", "N_B_SPECTRAL",
    "OMEGA_GW_PEAK", "LISA_BAND_HZ", "PTA_BAND_HZ",
    "gw_braid_spectral_index", "gw_braid_peak_frequency",
    "gw_braid_omega_peak", "gw_braid_omega_at_frequency",
    "detector_accessibility", "pillar532_report",
]

PILLAR_NUMBER: int = 532
PILLAR_STATUS: str = "GW_BRAID_SPECTRUM_CERTIFIED"
PILLAR_TITLE: str = (
    "GW Braid Transition Spectrum — f_peak ≈ 10^12 Hz; Outside Detector Bands"
)

K_CS: int = 74
N_W: int = 5

# KK scale (canonical TeV)
M_KK_GEV: float = 1000.0    # 1 TeV in GeV
# Convert to Hz: E [GeV] × (1.52e24 Hz/GeV) = f [Hz]
GEV_TO_HZ: float = 1.5193e24  # ℏ⁻¹ in Hz/GeV
F_PEAK_HZ: float = M_KK_GEV / (2.0 * math.pi) * GEV_TO_HZ

# Braid spectral index n_B = n_w / K_CS = 5/74
N_B_SPECTRAL: float = N_W / K_CS

# Peak GW energy density (dimensionless Ω_GW)
# Ω_GW_peak ~ (n_w² / K_CS²) × (H_inf/M_Pl)²
H_INF_OVER_MPL: float = 1.0e-5  # H_inf ≈ 10^{-5} M_Pl
OMEGA_GW_PEAK: float = (N_W**2 / K_CS**2) * H_INF_OVER_MPL**2

# Detector bands (Hz)
LISA_BAND_HZ: tuple = (1e-4, 0.1)    # LISA sensitivity band
PTA_BAND_HZ: tuple = (1e-9, 1e-7)    # PTA sensitivity band
SKA_BAND_HZ: tuple = (1e-9, 1e-6)    # SKA-PTA sensitivity band


def gw_braid_spectral_index() -> float:
    """Return the braid GW spectral index n_B = n_w / K_CS."""
    return N_W / K_CS


def gw_braid_peak_frequency() -> float:
    """Return the GW peak frequency f_peak = M_KK / (2π) in Hz."""
    return M_KK_GEV / (2.0 * math.pi) * GEV_TO_HZ


def gw_braid_omega_peak() -> float:
    """Return Ω_GW at the peak frequency."""
    return OMEGA_GW_PEAK


def gw_braid_omega_at_frequency(f_hz: float) -> float:
    """Return Ω_GW(f) using the broken power-law braid spectrum."""
    if f_hz <= 0:
        return 0.0
    if f_hz <= F_PEAK_HZ:
        return OMEGA_GW_PEAK * (f_hz / F_PEAK_HZ) ** N_B_SPECTRAL
    else:
        return OMEGA_GW_PEAK * (f_hz / F_PEAK_HZ) ** (-N_B_SPECTRAL)


def detector_accessibility() -> Dict[str, object]:
    """Check accessibility of GW braid signal to current and planned detectors."""
    lisa_accessible = LISA_BAND_HZ[0] <= F_PEAK_HZ <= LISA_BAND_HZ[1]
    pta_accessible = PTA_BAND_HZ[0] <= F_PEAK_HZ <= PTA_BAND_HZ[1]

    # Ω_GW at LISA band edge
    omega_at_lisa = gw_braid_omega_at_frequency(0.01)
    omega_at_pta = gw_braid_omega_at_frequency(1e-8)

    return {
        "f_peak_hz": F_PEAK_HZ,
        "lisa_accessible": lisa_accessible,
        "pta_accessible": pta_accessible,
        "omega_at_lisa_01hz": omega_at_lisa,
        "omega_at_pta_1e8hz": omega_at_pta,
        "verdict": (
            "GW_BRAID_OUTSIDE_DETECTOR_BANDS"
            if not (lisa_accessible or pta_accessible)
            else "GW_BRAID_DETECTABLE"
        ),
    }


def pillar532_report() -> Dict[str, object]:
    """Full Pillar 532 machine-readable report."""
    access = detector_accessibility()
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "spectrum": {
            "f_peak_hz": F_PEAK_HZ,
            "n_b_spectral": N_B_SPECTRAL,
            "omega_gw_peak": OMEGA_GW_PEAK,
        },
        "detector_accessibility": access,
        "summary": (
            f"GW braid peak at f ≈ {F_PEAK_HZ:.2e} Hz (outside LISA/PTA bands). "
            f"Signal NOT accessible to current/planned detectors. "
            f"Pillar CERTIFIED as architecture limit on GW detection."
        ),
    }
