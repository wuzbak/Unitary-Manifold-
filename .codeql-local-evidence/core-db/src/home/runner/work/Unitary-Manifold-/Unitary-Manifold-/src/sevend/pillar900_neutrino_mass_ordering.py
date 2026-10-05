# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 900 — NEUTRINO_MASS_ORDERING_AUDIT.

A simple seesaw proxy uses the Pillar 887 neutrino FN charges to generate heavy
Majorana scales M_Σ^(i) = M_Σ ε^{-qᵢ}.  Light masses then follow as
m_ν^(i) ∝ 1/M_Σ^(i), normalised to a benchmark m₃ ≈ 0.05 eV.

Honest status
-------------
The goal is to test ordering, not to claim a precision neutrino spectrum.  The
returned summary reports the mass-squared splittings explicitly against the PDG
benchmarks.
"""
from __future__ import annotations

from typing import Any

from src.core.pillar841_6d_baryogenesis_dn_prediction import M_SIGMA_GEV
from src.sevend.pillar887_fn_charge_assignment import FN_CHARGES_NEUTRINO, FN_EPSILON

PILLAR_NUMBER: int = 900
PILLAR_GATE: str = "NEUTRINO_MASS_ORDERING_AUDIT"

PDG_DELTA_M21_SQ: float = 7.53e-5
PDG_DELTA_M31_SQ: float = 2.455e-3
PDG_PREFERENCE: str = "NORMAL"
M_NU3_TARGET_EV: float = 0.05

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "DELTA_M21_SQ",
    "DELTA_M31_SQ",
    "MASS_ORDERING",
    "PDG_PREFERENCE",
    "ORDERING_GATE",
    "STATUS_LABEL",
    "neutrino_ordering_summary",
]


def heavy_neutrino_scales_gev() -> tuple[float, float, float]:
    """Return the FN-weighted heavy neutrino scales."""
    return tuple(M_SIGMA_GEV * FN_EPSILON ** (-charge) for charge in FN_CHARGES_NEUTRINO)



def light_neutrino_masses_ev() -> tuple[float, float, float]:
    """Return benchmark FN-weighted light neutrino masses in eV."""
    q1, q2, q3 = FN_CHARGES_NEUTRINO
    return (
        M_NU3_TARGET_EV * FN_EPSILON ** q1,
        M_NU3_TARGET_EV * FN_EPSILON ** q2,
        M_NU3_TARGET_EV * FN_EPSILON ** q3,
    )


M_NU_EV = light_neutrino_masses_ev()
DELTA_M21_SQ: float = M_NU_EV[1] ** 2 - M_NU_EV[0] ** 2
DELTA_M31_SQ: float = M_NU_EV[2] ** 2 - M_NU_EV[0] ** 2
MASS_ORDERING: str = "NORMAL" if M_NU_EV[2] > M_NU_EV[1] > M_NU_EV[0] else "INVERTED"
ORDERING_GATE: str = "NORMAL_ORDERING_RECOVERED" if MASS_ORDERING == PDG_PREFERENCE else "ORDERING_TENSION"
STATUS_LABEL: str = "RESOLVED" if MASS_ORDERING == PDG_PREFERENCE else "TENSION_PERSISTS"


def neutrino_ordering_summary() -> dict[str, Any]:
    """Return the machine-readable neutrino ordering audit."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "result_gate": ORDERING_GATE,
        "heavy_neutrino_scales_gev": list(heavy_neutrino_scales_gev()),
        "light_neutrino_masses_ev": list(M_NU_EV),
        "delta_m21_sq": DELTA_M21_SQ,
        "delta_m31_sq": DELTA_M31_SQ,
        "pdg_delta_m21_sq": PDG_DELTA_M21_SQ,
        "pdg_delta_m31_sq": PDG_DELTA_M31_SQ,
        "mass_ordering": MASS_ORDERING,
        "pdg_preference": PDG_PREFERENCE,
        "epistemic_status": (
            "This seesaw proxy is used only to audit whether the geometry prefers normal ordering. "
            "The benchmark mass scale is explicit and not disguised as a full precision derivation."
        ),
    }
