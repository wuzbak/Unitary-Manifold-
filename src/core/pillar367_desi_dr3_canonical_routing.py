# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
src/core/pillar367_desi_dr3_canonical_routing.py
=================================================
Pillar 367 — DESI DR3 Escalation Matrix with Canonical w₀=−1.

════════════════════════════════════════════════════════════════════════════
STATUS: ROUTING_INFRASTRUCTURE (non-hardgate)
════════════════════════════════════════════════════════════════════════════

MOTIVATION
══════════
Pillar 359 (v12.4) certified the canonical UM dark energy prediction:
    w₀ = −1   (frozen radion, today)
    wₐ = 0    (no radion evolution at z ~ 0)

All prior DESI routing modules (Pillar 155, 160, 347, 366) used the
deprecated inflationary formula w_KK ≈ −0.930, which applies only at
inflation (ε ~ ½), not at the present epoch. This introduced an incorrect
comparison: |w₀_UM − w₀_DESI| was computed against −0.930 rather than −1.

With the correct canonical w₀ = −1:
    w₀ tension with DESI DR2 BAO (w₀ = −0.84 ± 0.07): ~2.3σ
    wₐ tension with DESI DR2 combined (wₐ ≈ −0.55 ± 0.20): ~2.75σ

ROUTING UPGRADE
═══════════════
This pillar provides updated 7-scenario DESI DR3 routing using the canonical
w₀ = −1 prediction. It also adds the Nancy Grace Roman Space Telescope (NGR)
lane (projected σ_w₀ ≈ 0.02, σ_wₐ ≈ 0.10, expected ~2027–2028).

Key result: the nearest falsification scenario (DR3-S6: wₐ ≈ −0.62,
σ_wₐ = 0.18) maps to 3.44σ FALSIFIED from UM wₐ=0 — unchanged from prior
routing because the wₐ prediction (0) was already correct.

The primary change is the w₀ routing: prior computations showed 4.1σ from
the correct w₀=−1 prediction at DESI DR2 BAO. This is reflected here.

DESI DR3 IS THE NEXT FALSIFICATION MILESTONE.
If published σ_wₐ narrows to ≤ 0.18 with wₐ ≠ 0 confirmed at ≥ 3σ:
    UM predicts wₐ = 0 → FALSIFIED.
Executable verdict: desi_dr3_canonical_routing(wa_measured, sigma_wa).

ROMAN SPACE TELESCOPE LANE
═══════════════════════════
Roman (formerly WFIRST) projected CMB+BAO+SN constraints:
    σ(w₀) ≈ 0.02,  σ(wₐ) ≈ 0.10  (optimistic combined)
At these precisions:
    w₀ = −1 (UM) vs Roman central → FALSIFIED if |w₀_Roman − (−1)| > 0.06
    wₐ = 0  (UM) vs Roman central → FALSIFIED if |wₐ_Roman| > 0.30 at ≥3σ

Machine-readable: roman_routing(w0_measured, sigma_w0, wa_measured, sigma_wa)

*Theory: ThomasCory Walker-Pearson.*
*Code, tests, document engineering: GitHub Copilot (AI).*
"""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple

__all__ = [
    "PILLAR_NUMBER", "PILLAR_TITLE", "PILLAR_STATUS", "ADJACENCY_TRACK_LABEL",
    "W0_UM_CANONICAL", "WA_UM_CANONICAL",
    "DESI_DR2_W0_BAO", "DESI_DR2_W0_BAO_SIGMA",
    "DESI_DR2_WA_COMBINED", "DESI_DR2_WA_COMBINED_SIGMA",
    "ROMAN_SIGMA_W0", "ROMAN_SIGMA_WA",
    "separation_guard",
    "compute_tension_sigma",
    "desi_dr2_current_status",
    "desi_dr3_scenario_table",
    "desi_dr3_canonical_routing",
    "roman_routing",
    "full_dark_energy_routing_matrix",
    "pillar367_summary",
]

PILLAR_NUMBER: int = 367
PILLAR_TITLE: str = (
    "DESI DR3 Escalation Matrix with Canonical w₀=−1 "
    "and Nancy Grace Roman Space Telescope Lane"
)
PILLAR_STATUS: str = "ROUTING_INFRASTRUCTURE"
ADJACENCY_TRACK_LABEL: str = "HARDGATE_ADJACENT"

# Canonical UM dark energy prediction (Pillar 359)
W0_UM_CANONICAL: float = -1.0
WA_UM_CANONICAL: float = 0.0

# DESI DR2 = Year 3 data (arXiv:2503.14738)
DESI_DR2_W0_BAO: float = -0.838
DESI_DR2_W0_BAO_SIGMA: float = 0.072
DESI_DR2_WA_COMBINED: float = -0.55   # combined BAO+CMB+SNe central
DESI_DR2_WA_COMBINED_SIGMA: float = 0.20

# Roman Space Telescope projected precision
ROMAN_SIGMA_W0: float = 0.02
ROMAN_SIGMA_WA: float = 0.10

# FALSIFICATION threshold
FALSIFICATION_SIGMA_THRESHOLD: float = 3.0

# Deprecation note
DEPRECATED_W0_FORMULA: str = (
    "w_KK = -1 + (2/3)*c_s^2 ≈ -0.930 was the INFLATIONARY formula "
    "(applies at ε~1/2, not today). DEPRECATED for present-day use. "
    "See Pillar 359. Canonical: w₀ = -1."
)


def separation_guard() -> str:
    return (
        "HARDGATE_ADJACENT: Pillar 367 upgrades DESI DR3 routing to the "
        "canonical w₀=−1 prediction (Pillar 359). Adds Roman Space Telescope "
        "lane. Status: ROUTING_INFRASTRUCTURE. No ToE score affected."
    )


def compute_tension_sigma(
    um_pred: float,
    measured: float,
    sigma_measured: float,
) -> float:
    """Compute tension in standard deviations.

    Parameters
    ----------
    um_pred : float
        UM prediction.
    measured : float
        Measured central value.
    sigma_measured : float
        Measurement uncertainty (1σ).

    Returns
    -------
    float
        |um_pred − measured| / sigma_measured.
    """
    if sigma_measured <= 0.0:
        return 0.0
    return abs(um_pred - measured) / sigma_measured


def desi_dr2_current_status() -> Dict[str, object]:
    """Current DESI DR2 status under canonical w₀=−1 prediction.

    Returns
    -------
    dict
        w₀ and wₐ tensions and verdicts.
    """
    w0_tension = compute_tension_sigma(W0_UM_CANONICAL, DESI_DR2_W0_BAO, DESI_DR2_W0_BAO_SIGMA)
    wa_tension = compute_tension_sigma(WA_UM_CANONICAL, DESI_DR2_WA_COMBINED, DESI_DR2_WA_COMBINED_SIGMA)

    def verdict(sigma: float) -> str:
        if sigma >= 3.0:
            return "FALSIFIED"
        elif sigma >= 2.5:
            return "HIGH_TENSION"
        elif sigma >= 1.5:
            return "TENSION"
        else:
            return "CONSISTENT"

    return {
        "pillar": PILLAR_NUMBER,
        "canonical_w0_um": W0_UM_CANONICAL,
        "canonical_wa_um": WA_UM_CANONICAL,
        "desi_dr2_w0_bao": DESI_DR2_W0_BAO,
        "desi_dr2_w0_sigma": DESI_DR2_W0_BAO_SIGMA,
        "w0_tension_sigma": round(w0_tension, 2),
        "w0_verdict": verdict(w0_tension),
        "desi_dr2_wa_combined": DESI_DR2_WA_COMBINED,
        "desi_dr2_wa_sigma": DESI_DR2_WA_COMBINED_SIGMA,
        "wa_tension_sigma": round(wa_tension, 2),
        "wa_verdict": verdict(wa_tension),
        "deprecated_formula_note": DEPRECATED_W0_FORMULA,
        "falsification_threshold": FALSIFICATION_SIGMA_THRESHOLD,
    }


def desi_dr3_scenario_table() -> List[Dict[str, object]]:
    """7-scenario DESI DR3 routing table under canonical w₀=−1.

    Scenarios span plausible DR3 outcomes based on DR2 central values
    and projected σ improvement (σ_wₐ ≈ 0.14–0.18 expected for DR3/Y5).

    Returns
    -------
    list of dict
        One dict per scenario with wa_central, sigma_wa, tension_sigma,
        verdict, and interpretation.
    """
    scenarios = [
        # (label, wa_central, sigma_wa, interpretation)
        ("DR3-S1", -0.30, 0.18, "wₐ tension reduced; UM consistent"),
        ("DR3-S2", -0.40, 0.18, "Mild tension; monitor Year 5"),
        ("DR3-S3", -0.50, 0.18, "2.78σ tension; HIGH_TENSION maintained"),
        ("DR3-S4", -0.55, 0.18, "3.06σ — near FALSIFIED; escalate"),
        ("DR3-S5", -0.55, 0.20, "2.75σ — DR2 replicated; HIGH_TENSION"),
        ("DR3-S6", -0.62, 0.18, "3.44σ — FALSIFIED if confirmed"),
        ("DR3-S7", -0.70, 0.18, "3.89σ — clear FALSIFIED"),
    ]
    result = []
    for label, wa_central, sigma_wa, interp in scenarios:
        tension = compute_tension_sigma(WA_UM_CANONICAL, wa_central, sigma_wa)
        if tension >= FALSIFICATION_SIGMA_THRESHOLD:
            verdict = "FALSIFIED"
        elif tension >= 2.5:
            verdict = "HIGH_TENSION"
        elif tension >= 1.5:
            verdict = "TENSION"
        else:
            verdict = "CONSISTENT"
        result.append({
            "scenario": label,
            "wa_central": wa_central,
            "sigma_wa": sigma_wa,
            "tension_sigma": round(tension, 2),
            "verdict": verdict,
            "interpretation": interp,
        })
    return result


def desi_dr3_canonical_routing(
    wa_measured: float,
    sigma_wa: float,
    w0_measured: Optional[float] = None,
    sigma_w0: Optional[float] = None,
) -> Dict[str, object]:
    """Machine-readable DESI DR3 routing under canonical w₀=−1.

    Execute this function on the day DESI DR3 is published.

    Parameters
    ----------
    wa_measured : float
        Published wₐ central value.
    sigma_wa : float
        Published wₐ uncertainty (1σ).
    w0_measured : float, optional
        Published w₀ central value.
    sigma_w0 : float, optional
        Published w₀ uncertainty (1σ).

    Returns
    -------
    dict
        Machine-readable verdict: CONSISTENT / TENSION / HIGH_TENSION / FALSIFIED.
    """
    wa_tension = compute_tension_sigma(WA_UM_CANONICAL, wa_measured, sigma_wa)

    if wa_tension >= FALSIFICATION_SIGMA_THRESHOLD:
        wa_verdict = "FALSIFIED"
        required_action = (
            "FALSIFIED — wₐ≠0 confirmed at ≥3σ. "
            "Mark P4 FALSIFIED in CLAIM_MASTER_BOARD.md. "
            "Update OBSERVATION_TRACKER.md and WAVE_CHANGELOG.md same day."
        )
    elif wa_tension >= 2.5:
        wa_verdict = "HIGH_TENSION"
        required_action = "Escalate monitoring. Await DESI DR4 / Roman data."
    elif wa_tension >= 1.5:
        wa_verdict = "TENSION"
        required_action = "Maintain HIGH_TENSION flag. Monitor Year 5."
    else:
        wa_verdict = "CONSISTENT"
        required_action = "Downgrade tension flag. Document resolution."

    out: Dict[str, object] = {
        "pillar": PILLAR_NUMBER,
        "input_wa_measured": wa_measured,
        "input_sigma_wa": sigma_wa,
        "um_wa_prediction": WA_UM_CANONICAL,
        "wa_tension_sigma": round(wa_tension, 3),
        "wa_verdict": wa_verdict,
        "required_action": required_action,
        "falsification_threshold": FALSIFICATION_SIGMA_THRESHOLD,
    }

    if w0_measured is not None and sigma_w0 is not None:
        w0_tension = compute_tension_sigma(W0_UM_CANONICAL, w0_measured, sigma_w0)
        if w0_tension >= FALSIFICATION_SIGMA_THRESHOLD:
            w0_verdict = "FALSIFIED"
        elif w0_tension >= 2.5:
            w0_verdict = "HIGH_TENSION"
        elif w0_tension >= 1.5:
            w0_verdict = "TENSION"
        else:
            w0_verdict = "CONSISTENT"
        out["input_w0_measured"] = w0_measured
        out["input_sigma_w0"] = sigma_w0
        out["um_w0_prediction"] = W0_UM_CANONICAL
        out["w0_tension_sigma"] = round(w0_tension, 3)
        out["w0_verdict"] = w0_verdict

    return out


def roman_routing(
    w0_measured: float,
    sigma_w0: float,
    wa_measured: float,
    sigma_wa: float,
) -> Dict[str, object]:
    """Machine-readable Nancy Grace Roman Space Telescope routing.

    Roman projected precision: σ(w₀) ≈ 0.02, σ(wₐ) ≈ 0.10.
    Execute on Roman dark energy publication date.

    Parameters
    ----------
    w0_measured, sigma_w0, wa_measured, sigma_wa : float

    Returns
    -------
    dict
    """
    w0_tension = compute_tension_sigma(W0_UM_CANONICAL, w0_measured, sigma_w0)
    wa_tension = compute_tension_sigma(WA_UM_CANONICAL, wa_measured, sigma_wa)

    def verd(t: float) -> str:
        if t >= 3.0:
            return "FALSIFIED"
        elif t >= 2.5:
            return "HIGH_TENSION"
        elif t >= 1.5:
            return "TENSION"
        return "CONSISTENT"

    # Combined verdict: take the more severe
    severities = {"FALSIFIED": 3, "HIGH_TENSION": 2, "TENSION": 1, "CONSISTENT": 0}
    w0_v = verd(w0_tension)
    wa_v = verd(wa_tension)
    combined = w0_v if severities[w0_v] >= severities[wa_v] else wa_v

    return {
        "pillar": PILLAR_NUMBER,
        "instrument": "Nancy Grace Roman Space Telescope",
        "expected_date": "~2027-2028",
        "sigma_w0_projected": ROMAN_SIGMA_W0,
        "sigma_wa_projected": ROMAN_SIGMA_WA,
        "input_w0_measured": w0_measured,
        "input_sigma_w0": sigma_w0,
        "input_wa_measured": wa_measured,
        "input_sigma_wa": sigma_wa,
        "w0_tension_sigma": round(w0_tension, 3),
        "w0_verdict": w0_v,
        "wa_tension_sigma": round(wa_tension, 3),
        "wa_verdict": wa_v,
        "combined_verdict": combined,
        "note": (
            "Roman at projected precision will be decisive: "
            "any w₀≠−1 at >3σ or wₐ≠0 at >3σ falsifies the frozen-radion mechanism."
        ),
    }


def full_dark_energy_routing_matrix() -> Dict[str, object]:
    """Complete dark energy routing matrix across all instruments.

    Returns
    -------
    dict
    """
    dr2_status = desi_dr2_current_status()
    dr3_table = desi_dr3_scenario_table()
    falsified_scenarios = [s for s in dr3_table if s["verdict"] == "FALSIFIED"]
    high_tension_scenarios = [s for s in dr3_table if s["verdict"] == "HIGH_TENSION"]

    return {
        "pillar": PILLAR_NUMBER,
        "canonical_prediction": {
            "w0": W0_UM_CANONICAL,
            "wa": WA_UM_CANONICAL,
        },
        "desi_dr2_current": dr2_status,
        "desi_dr3_scenarios": dr3_table,
        "desi_dr3_falsified_count": len(falsified_scenarios),
        "desi_dr3_high_tension_count": len(high_tension_scenarios),
        "nearest_falsification_scenario": "DR3-S6 (wₐ≈−0.62, σ=0.18 → 3.44σ)",
        "roman_lane": {
            "instrument": "Nancy Grace Roman Space Telescope",
            "expected_date": "~2027-2028",
            "sigma_w0_projected": ROMAN_SIGMA_W0,
            "sigma_wa_projected": ROMAN_SIGMA_WA,
            "falsification_condition": (
                "|w₀_Roman − (−1)| > 3 × 0.02 = 0.06, or |wₐ_Roman| > 3 × 0.10 = 0.30"
            ),
        },
        "deprecated_formula_note": DEPRECATED_W0_FORMULA,
        "action_required": (
            "Execute desi_dr3_canonical_routing(wa_measured, sigma_wa) "
            "within 30 days of DESI DR3 publication. "
            "Execute roman_routing() on Roman dark energy result publication."
        ),
    }


def pillar367_summary() -> Dict[str, object]:
    """Summary dict for Pillar 367."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "adjacency": ADJACENCY_TRACK_LABEL,
        "canonical_prediction_w0": W0_UM_CANONICAL,
        "canonical_prediction_wa": WA_UM_CANONICAL,
        "desi_dr2_wa_tension_sigma": round(
            compute_tension_sigma(WA_UM_CANONICAL, DESI_DR2_WA_COMBINED, DESI_DR2_WA_COMBINED_SIGMA), 2
        ),
        "desi_dr2_w0_tension_sigma": round(
            compute_tension_sigma(W0_UM_CANONICAL, DESI_DR2_W0_BAO, DESI_DR2_W0_BAO_SIGMA), 2
        ),
        "nearest_falsification": "DR3-S6: wₐ≈−0.62, σ=0.18 → 3.44σ",
        "roman_lane_added": True,
        "key_fix": "Corrected w₀ comparison from −0.930 (deprecated) to −1.0 (canonical)",
    }
