# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
DESI DR3 preregistration tracking and dark energy falsification status.

Pillar P824: DESI_DR3_PREREGISTERED
The UM predicts w₀ = -1.0 (cosmological constant) and wₐ = 0.0.
DESI DR2 showed ~2.75σ tension. DR3 is the registered test.

Status: PREREGISTERED — awaiting DESI DR3 release.
"""
from __future__ import annotations

import math

DESI_DR3_PREREGISTRATION: dict = {
    "preregistration_date": "2026-08-29",
    "pillar": "P824",
    "w0_prediction": -1.0,
    "wa_prediction": 0.0,
    "w0_dr2_observed": -0.827,      # DESI DR2 best-fit approximate
    "wa_dr2_observed": -0.75,       # DESI DR2 approximate
    "dr2_tension_sigma": 2.75,
    "status": "PREREGISTERED",
    "decision_tree": (
        "If DR3 w0≈-1 and wa≈0: UM prediction consistent. "
        "If DR3 w0≠-1 at >3σ: breathing-mode quintessence interpretation activated (P808). "
        "If DR3 wa≠0 at >3σ: tension registered as open problem."
    ),
    "caveat": (
        "The CPL dark energy EoS tension (wₐ≠0 from DESI DR2) is documented as an open problem "
        "in FALLIBILITY.md. The UM breathing-mode leakage (P808) predicts wₐ≈0 at leading order. "
        "DR3 is the decisive test."
    ),
}

# Known open falsification claims
FALSIFICATION_REGISTRY: list[dict] = [
    {
        "id": "birefringence",
        "name": "CMB Birefringence β",
        "prediction": "β ∈ {0.273°, 0.331°}",
        "window": "[0.22°, 0.38°], gap [0.29°–0.31°]",
        "test_by": "LiteBIRD ~2032",
        "status": "PENDING",
        "pillar": "P001 + braided-winding",
    },
    {
        "id": "desi_dr3",
        "name": "DESI DR3 w₀/wₐ",
        "prediction": "w₀=-1.0, wₐ=0.0",
        "window": "DR3 data release",
        "test_by": "DESI collaboration ~2026-2027",
        "status": "PREREGISTERED (P824)",
        "pillar": "P808, P824",
    },
    {
        "id": "cmb_peak_amplitude",
        "name": "CMB Acoustic Peak Amplitude",
        "prediction": "Suppressed ×4–7 vs Planck (Admission 2, FALLIBILITY.md)",
        "window": "Architecture limit — NLO_OPEN",
        "test_by": "Ongoing (Planck data)",
        "status": "OPEN GAP — documented in FALLIBILITY.md",
        "pillar": "P057, P063",
    },
    {
        "id": "n_s_prediction",
        "name": "CMB Spectral Index nₛ",
        "prediction": "nₛ = 0.9635",
        "window": "Planck: 0.9649 ± 0.0042",
        "test_by": "Planck legacy (confirmed within 0.3σ)",
        "status": "CONSISTENT",
        "pillar": "P001",
    },
    {
        "id": "r_tensor",
        "name": "Tensor-to-Scalar Ratio r",
        "prediction": "r = 0.0315",
        "window": "BICEP/Keck: r < 0.036",
        "test_by": "BICEP/Keck (upper bound consistent)",
        "status": "CONSISTENT (upper bound)",
        "pillar": "P001",
    },
]


def check_desi_tension(w0_observed: float, wa_observed: float) -> dict:
    """
    Check the tension between an observed w₀/wₐ and the UM prediction.

    Parameters
    ----------
    w0_observed : float
        Observed CPL w₀ parameter.
    wa_observed : float
        Observed CPL wₐ parameter.

    Returns
    -------
    dict with tension analysis.
    """
    dw0 = w0_observed - DESI_DR3_PREREGISTRATION["w0_prediction"]
    dwa = wa_observed - DESI_DR3_PREREGISTRATION["wa_prediction"]

    # Rough tension estimate assuming ~0.05 uncertainty on each
    sigma_w0 = 0.05
    sigma_wa = 0.20
    tension_w0 = abs(dw0) / sigma_w0
    tension_wa = abs(dwa) / sigma_wa
    combined = math.sqrt(tension_w0**2 + tension_wa**2) / math.sqrt(2)

    if combined < 1.0:
        verdict = "CONSISTENT — within 1σ of UM prediction"
    elif combined < 2.0:
        verdict = "MILD TENSION — 1–2σ from UM prediction"
    elif combined < 3.0:
        verdict = "TENSION — 2–3σ from UM prediction (registered as open problem)"
    else:
        verdict = "STRONG TENSION — >3σ from UM prediction (serious challenge to wₐ=0)"

    return {
        "w0_observed": w0_observed,
        "wa_observed": wa_observed,
        "w0_predicted": DESI_DR3_PREREGISTRATION["w0_prediction"],
        "wa_predicted": DESI_DR3_PREREGISTRATION["wa_prediction"],
        "delta_w0": dw0,
        "delta_wa": dwa,
        "tension_sigma_w0": round(tension_w0, 2),
        "tension_sigma_wa": round(tension_wa, 2),
        "combined_tension_sigma": round(combined, 2),
        "consistent": combined < 2.0,
        "verdict": verdict,
        "epistemic_note": DESI_DR3_PREREGISTRATION["caveat"],
    }


def get_falsification_status() -> dict:
    """Return full falsification registry with current status."""
    open_count = sum(1 for c in FALSIFICATION_REGISTRY if c["status"] in ("PENDING", "PREREGISTERED (P824)"))
    consistent_count = sum(1 for c in FALSIFICATION_REGISTRY if "CONSISTENT" in c["status"])
    gap_count = sum(1 for c in FALSIFICATION_REGISTRY if "OPEN GAP" in c["status"])

    return {
        "total_claims": len(FALSIFICATION_REGISTRY),
        "pending_external_test": open_count,
        "consistent_with_data": consistent_count,
        "registered_open_gaps": gap_count,
        "claims": FALSIFICATION_REGISTRY,
        "primary_falsifier": "LiteBIRD birefringence measurement ~2032",
        "epistemic_note": (
            "All gaps are documented honestly. Green status means consistent with current data, "
            "not that the theory is proven. External experimental tests are the only valid final arbiter."
        ),
    }
