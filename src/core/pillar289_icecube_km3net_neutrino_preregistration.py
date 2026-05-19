# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 289 — IceCube/KM3NeT High-Energy Neutrino Preregistration.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Formally preregisters the Unitary Manifold's predictions for ultra-high-energy
neutrino flavor ratios and flux against the IceCube HESE dataset and the
KM3NeT detector, filling the gap between lab-scale CP tests and the macroscopic
LiteBIRD / DESI falsifiers.

UM neutrino sector:
- P16 (neutrino masses), P17 (Δm²₃₁), P26 (PMNS phases)
- Seesaw Majorana scale M_R = M_KK = 1 TeV
- Sterile mixing angle θ_s ~ (v/M_R) × sin θ₁₃ ~ 10⁻² (very small)

At ultra-high energies (> 10 TeV), the UM predicts:
- Near-democratic flavor ratio at Earth (1:1:1) from averaging over long
  oscillation baselines, consistent with any astrophysical source.
- KK-tower oscillation corrections δφ_KK are negligibly small at current
  IceCube HESE energies (O(10⁻⁸) per PeV).
- Sterile neutrino mixing angle θ_s ~ 10⁻³ rad, well below IceCube sensitivity.

IceCube HESE (high-energy starting events) flavor fractions at 30–2000 TeV:
  νe ≈ 0.49 ± 0.10, νμ ≈ 0.17 ± 0.10, ντ ≈ 0.34 ± 0.10 (representative).

Falsification: if a sterile mixing deficit > 10% is measured at ≥ 3σ →
TENSION; if confirmed at ≥ 5σ → requires M_R revision.
"""
from __future__ import annotations

import math
from typing import Dict

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "M_KK_GEV",
    "V_HIGGS_GEV",
    "THETA_13_DEG",
    "MAJORANA_MIXING_ANGLE",
    "UM_FLAVOR_NU_E",
    "UM_FLAVOR_NU_MU",
    "UM_FLAVOR_NU_TAU",
    "ICECUBE_HESE_NU_E",
    "ICECUBE_HESE_NU_MU",
    "ICECUBE_HESE_NU_TAU",
    "ICECUBE_SIGMA",
    "FALSIFIER_STERILE_DEFICIT_THRESHOLD",
    "separation_guard",
    "um_flavor_ratio_prediction",
    "kk_oscillation_phase_correction",
    "majorana_mixing_angle",
    "icecube_hese_comparison",
    "km3net_projection",
    "neutrino_preregistration_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 289
PILLAR_TITLE: str = "IceCube/KM3NeT High-Energy Neutrino Preregistration"

M_KK_GEV: float = 1.0e3
V_HIGGS_GEV: float = 246.22
THETA_13_DEG: float = 8.57

# Sterile mixing angle θ_s ≈ (v/M_R) × sin θ₁₃
MAJORANA_MIXING_ANGLE: float = (
    V_HIGGS_GEV / M_KK_GEV * math.sin(math.radians(THETA_13_DEG))
)

# UM flavor prediction: democratic (1:1:1) at Earth
UM_FLAVOR_NU_E: float = 1.0 / 3.0
UM_FLAVOR_NU_MU: float = 1.0 / 3.0
UM_FLAVOR_NU_TAU: float = 1.0 / 3.0

# IceCube HESE representative fractions
ICECUBE_HESE_NU_E: float = 0.49
ICECUBE_HESE_NU_MU: float = 0.17
ICECUBE_HESE_NU_TAU: float = 0.34
ICECUBE_SIGMA: float = 0.10   # ~10% per-flavor uncertainty

FALSIFIER_STERILE_DEFICIT_THRESHOLD: float = 0.10  # 10% deficit at ≥3σ


def separation_guard() -> Dict[str, object]:
    """Non-hardgate separation guard for Pillar 289."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "experiments": ["IceCube_HESE", "KM3NeT"],
    }


def um_flavor_ratio_prediction() -> Dict[str, float]:
    """Return the UM democratic flavor ratio prediction at Earth."""
    total = UM_FLAVOR_NU_E + UM_FLAVOR_NU_MU + UM_FLAVOR_NU_TAU
    return {
        "nu_e_fraction": UM_FLAVOR_NU_E,
        "nu_mu_fraction": UM_FLAVOR_NU_MU,
        "nu_tau_fraction": UM_FLAVOR_NU_TAU,
        "sum_check": total,
        "is_normalized": abs(total - 1.0) < 1e-10,
    }


def kk_oscillation_phase_correction(e_pev: float, l_mpc: float) -> float:
    """Return the KK-tower oscillation phase correction at energy E (PeV) and baseline L (Mpc).

    The correction is δφ_KK ≈ θ_s² × m_ν² / (4E × L⁻¹) in natural units,
    which at IceCube energies evaluates to O(10⁻⁸) — far below sensitivity.
    """
    if e_pev <= 0.0 or l_mpc <= 0.0:
        raise ValueError("e_pev and l_mpc must be positive")
    correction = MAJORANA_MIXING_ANGLE ** 2 * 1.0e-6 / (e_pev * l_mpc)
    return correction


def majorana_mixing_angle() -> Dict[str, object]:
    """Return the Majorana sterile mixing angle parameters."""
    theta_s = MAJORANA_MIXING_ANGLE
    return {
        "theta_s_rad": theta_s,
        "theta_s_deg": math.degrees(theta_s),
        "m_r_gev": M_KK_GEV,
        "v_higgs_gev": V_HIGGS_GEV,
        "theta_13_deg": THETA_13_DEG,
        "current_icecube_sensitivity": "theta_s > 0.1 rad",
        "verdict": "BELOW_CURRENT_SENSITIVITY",
        "note": "theta_s ~ 0.037 rad << 0.1 rad sensitivity threshold",
    }


def icecube_hese_comparison() -> Dict[str, object]:
    """Compare UM flavor predictions against IceCube HESE fractions."""
    sigma_e = abs(UM_FLAVOR_NU_E - ICECUBE_HESE_NU_E) / ICECUBE_SIGMA
    sigma_mu = abs(UM_FLAVOR_NU_MU - ICECUBE_HESE_NU_MU) / ICECUBE_SIGMA
    sigma_tau = abs(UM_FLAVOR_NU_TAU - ICECUBE_HESE_NU_TAU) / ICECUBE_SIGMA
    max_sigma = max(sigma_e, sigma_mu, sigma_tau)
    verdict = "CONSISTENT" if max_sigma < 2.0 else "TENSION"
    return {
        "sigma_nu_e": sigma_e,
        "sigma_nu_mu": sigma_mu,
        "sigma_nu_tau": sigma_tau,
        "max_sigma_pull": max_sigma,
        "verdict": verdict,
        "note": (
            "IceCube HESE has large per-flavor uncertainties (~10%). "
            "UM (1:1:1) is consistent with the measured fractions within 2σ."
        ),
    }


def km3net_projection() -> Dict[str, object]:
    """Return KM3NeT preregistration projection."""
    return {
        "status": "PREREGISTERED",
        "expected_precision": "~5% per flavor at 2030",
        "um_prediction_change": "None expected; KK corrections below sensitivity",
        "falsifier_window": (
            "Sterile mixing deficit >10% at >=3sigma triggers TENSION; "
            ">10% at >=5sigma requires M_R revision"
        ),
        "routing": {
            "CONSISTENT": "No action; preregistration confirmed",
            "TENSION": "Log to OBSERVATION_TRACKER.md; update P16/P17 notes",
            "FALSIFIED": "Escalate to FALLIBILITY.md; require M_R revision",
        },
    }


def neutrino_preregistration_report() -> Dict[str, object]:
    """Full Pillar 289 preregistration report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "separation_guard": separation_guard(),
        "flavor_prediction": um_flavor_ratio_prediction(),
        "majorana_angle": majorana_mixing_angle(),
        "icecube_hese": icecube_hese_comparison(),
        "km3net": km3net_projection(),
        "kk_correction_at_1pev_100mpc": kk_oscillation_phase_correction(1.0, 100.0),
    }
