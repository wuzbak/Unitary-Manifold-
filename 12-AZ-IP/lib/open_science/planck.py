# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
Planck CMB reference data for the Unitary Manifold.

These are public values from the Planck 2018 legacy release
(Planck Collaboration 2020, A&A 641, A6).

No network calls — all values are hardcoded from the public data release.
"""
from __future__ import annotations

# Planck 2018 TT,TE,EE+lowE+lensing best-fit values
PLANCK_N_S: float       = 0.9649   # spectral index (±0.0042)
PLANCK_N_S_ERR: float   = 0.0042
PLANCK_R_UPPER: float   = 0.036    # BICEP/Keck 95% CL upper bound
PLANCK_H0: float        = 67.36    # km/s/Mpc (±0.54)
PLANCK_OMEGA_B: float   = 0.02237  # baryon density (±0.00015)
PLANCK_OMEGA_CDM: float = 0.1200   # CDM density (±0.0012)
PLANCK_TAU: float       = 0.0544   # optical depth (±0.0073)
PLANCK_A_S: float       = 2.100e-9  # scalar amplitude at k=0.05 Mpc⁻¹

# UM predictions for comparison
UM_N_S: float  = 0.9635   # 0.3σ from Planck — consistent
UM_R:   float  = 0.0315   # within BICEP/Keck bound — consistent


def get_planck_cmb_reference() -> dict:
    """Return Planck 2018 CMB reference parameters with UM comparison."""
    tension_ns = abs(UM_N_S - PLANCK_N_S) / PLANCK_N_S_ERR

    return {
        "source": "Planck 2018 (Planck Collaboration 2020, A&A 641, A6)",
        "doi": "10.1051/0004-6361/201833910",
        "parameters": {
            "n_s":        {"planck": PLANCK_N_S,       "planck_err": PLANCK_N_S_ERR,  "um": UM_N_S,  "tension_sigma": round(tension_ns, 2)},
            "r_upper":    {"planck_upper": PLANCK_R_UPPER,                             "um": UM_R,    "status": "CONSISTENT (below upper bound)"},
            "H0_km_s_Mpc":{"planck": PLANCK_H0,        "um": None,                    "status": "KK tower not directly constrained"},
            "omega_b":    {"planck": PLANCK_OMEGA_B,   "um": None,                    "status": "Input parameter"},
            "omega_cdm":  {"planck": PLANCK_OMEGA_CDM, "um": None,                    "status": "KK dark matter candidate — adjacent track"},
            "A_s":        {"planck": PLANCK_A_S,       "um": None,                    "status": "CMB amplitude — open gap (×4–7 suppressed, Admission 2)"},
        },
        "um_status": {
            "n_s": f"CONSISTENT — {tension_ns:.2f}σ from Planck",
            "r": "CONSISTENT — below BICEP/Keck 95% upper bound",
            "A_s": "OPEN GAP — CMB acoustic peak amplitude suppressed ×4–7 (documented FALLIBILITY.md Admission 2)",
        },
        "caveat": (
            "UM predictions are internal model outputs. Consistency with Planck data is "
            "necessary but not sufficient for the theory to be correct."
        ),
    }
