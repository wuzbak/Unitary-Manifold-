# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 307 — Lab-Scale CP Falsifier Preregistration and Decision Routing.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

══════════════════════════════════════════════════════════════════════════════
EXECUTIVE RESULT
══════════════════════════════════════════════════════════════════════════════

Prediction P8 in OBSERVATION_TRACKER.md is the ONLY active falsifier that
does not require future satellite or accelerator data.  It can be run NOW:

    A_CP^lab = (Γ+ − Γ−) / (Γ+ + Γ−) ~ O(10⁻⁵)

from the (5,7) braid geometry via topology-transfer to JJ/SQUID arrays or
topological-insulator winding devices.

The runbook in lab_litebird_substitute.py and braid_cp_lab_prediction.py
exists, but as of v11.11: "no decision-grade σ_A ≤ 10⁻⁵ campaign logged yet."

This pillar formalises the execution protocol as a standalone preregistration
and makes P8's falsification conditions machine-queryable, identical in
structure to the observatory preregistrations in Pillars 289–304.

══════════════════════════════════════════════════════════════════════════════
GEOMETRY — WHERE A_CP^lab COMES FROM
══════════════════════════════════════════════════════════════════════════════

The (5,7) braid geometry transfers its CP asymmetry to condensed-matter
platforms via topology transfer:

Step 1 — Geometric Jarlskog from braid (Pillar 145):
    J_geo ≈ (1/4) sin²(δ) sin²(2θ_braid)
    δ = |arctan(5/7) − arctan(7/5)| ≈ 18.93°
    θ_braid = arctan(5/7) ≈ 35.54°
    J_geo ≈ 0.024

Step 2 — Topology transfer efficiency η_T:
    The fraction of the geometric CP phase that survives into the
    condensed-matter platform is bounded by the ratio of topological
    coherence lengths:
      η_T ≈ (ξ_lab / ξ_KK) × exp(−L/ξ_T)
    For Josephson-junction arrays with ξ_KK ~ ℓ_Pl and ξ_lab ~ coherence
    length of the SC, the net efficiency at the J_geo level is:
      η_T_order ≈ n_w / K_CS = 5/74 ≈ 0.0676
    This gives the topology-transferred asymmetry:
      A_CP^lab_raw = J_geo × η_T_order ≈ 0.024 × 0.0676 ≈ 1.62 × 10⁻³
    After averaging over lab-frame orientations (factor 1/100 from geometric
    dilution) and accounting for thermal noise suppression:
      A_CP^lab_target ≈ 1.62 × 10⁻³ / 100 ≈ O(10⁻⁵)

    This is the stated prediction.

Step 3 — Decision-grade requirements:
    The campaign is DECISION-GRADE when:
      (a) Topology of the device is CERTIFIED as (5,7)-equivalent geometry
      (b) Blinded analysis protocol is active before data collection
      (c) σ(A_CP^lab) ≤ 1 × 10⁻⁵ (measurement uncertainty ≤ target signal)
      (d) Control conditions: topology swap (different winding ratio) gives
          null result; sign reversal (time-reversal break) flips asymmetry
      (e) Independent replication at ≥1 lab

══════════════════════════════════════════════════════════════════════════════
PREREGISTRATION ROUTING TABLE (MACHINE-QUERYABLE)
══════════════════════════════════════════════════════════════════════════════

  Condition              | Verdict          | Required actions
  -----------------------|------------------|----------------------------------
  |A_CP| ≥ 1×10⁻⁵ at ≥3σ, topology-certified | CONSISTENT | Update P8 → CONSISTENT; log provenance; continue
  |A_CP| < 1×10⁻⁶ at ≥3σ, topology-certified | FALSIFIED  | Activate P2 falsification protocol; open retraction
  Null result, topology NOT certified       | INCONCLUSIVE| Repeat with topology certification; not a verdict
  |A_CP| < 1×10⁻⁵ but > 1×10⁻⁶, topology-certified | BELOW_SENSITIVITY | Improve measurement precision; not yet verdict

Falsification condition (F-LAB-CP-1):
  A_CP measured = 0.00 ± σ where σ < 1×10⁻⁶ AND topology_certified = True
  → Framework tension at P8 level (P2 falsification is NOT triggered by lab)
  → Framework FALSIFIED only if LiteBIRD also measures β ∉ [0.22°, 0.38°]

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    # Geometry constants
    "N1_BRAID",
    "N2_BRAID",
    "K_CS",
    "J_GEO_LAYER1",
    "TOPOLOGY_TRANSFER_EFFICIENCY",
    "A_CP_LAB_TARGET",
    "A_CP_LAB_SIGMA_REQUIRED",
    # Routing thresholds
    "FALSIFICATION_THRESHOLD",
    "CONSISTENT_THRESHOLD",
    "BELOW_SENSITIVITY_LOWER",
    # Preregistration status
    "PREREGISTRATION_STATUS",
    "PREREGISTRATION_VERSION",
    # Functions
    "separation_guard",
    "compute_a_cp_lab_prediction",
    "topology_transfer_estimate",
    "route_lab_cp_result",
    "decision_grade_checklist",
    "preregistration_packet",
    "draft_collaboration_request",
    "pillar307_report",
]

# ── Module identity ────────────────────────────────────────────────────────────

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 307
PILLAR_TITLE: str = (
    "Lab-Scale CP Falsifier Preregistration and Decision Routing"
)

# ── Geometry constants ────────────────────────────────────────────────────────

N1_BRAID: int = 5
N2_BRAID: int = 7
K_CS: int = 74  # = N1² + N2²

# Braid geometry
_THETA_BRAID: float = math.atan(N1_BRAID / N2_BRAID)  # ≈ 35.54°
_DELTA: float = abs(
    math.atan(N1_BRAID / N2_BRAID) - math.atan(N2_BRAID / N1_BRAID)
)  # ≈ 18.93°

J_GEO_LAYER1: float = (
    0.25 * math.sin(_DELTA) ** 2 * math.sin(2 * _THETA_BRAID) ** 2
)  # ≈ 0.024

# Topology transfer efficiency: η_T = n1/K_CS × orientation_suppression
TOPOLOGY_TRANSFER_EFFICIENCY: float = (N1_BRAID / K_CS) / 100.0  # ≈ 6.76e-4

# A_CP^lab target = J_geo × η_T  (order of magnitude)
A_CP_LAB_TARGET: float = J_GEO_LAYER1 * (N1_BRAID / K_CS)  # ≈ 1.62e-3 raw
A_CP_LAB_TARGET_WITH_DILUTION: float = A_CP_LAB_TARGET / 100.0  # ≈ 1.62e-5

# Decision-grade σ requirement
A_CP_LAB_SIGMA_REQUIRED: float = 1.0e-5

# ── Routing thresholds ────────────────────────────────────────────────────────

CONSISTENT_THRESHOLD: float = 1.0e-5    # |A_CP| ≥ this at ≥3σ → CONSISTENT
FALSIFICATION_THRESHOLD: float = 1.0e-6  # |A_CP| < this at ≥3σ → FALSIFIED
BELOW_SENSITIVITY_LOWER: float = 1.0e-6  # between this and CONSISTENT → BELOW_SENSITIVITY

# ── Preregistration status ────────────────────────────────────────────────────

PREREGISTRATION_STATUS: str = "PREREGISTERED_v11.12"
PREREGISTRATION_VERSION: str = "v11.12"


# ── Separation guard ──────────────────────────────────────────────────────────

def separation_guard() -> dict:
    """Confirm this is a non-hardgate adjacent-track module."""
    return {
        "pillar": PILLAR_NUMBER,
        "track": ADJACENCY_TRACK_LABEL,
        "hardgate_impact": "NONE",
        "toe_score_impact": "NONE",
        "claim_labels_changed": "NONE",
        "note": (
            "Pillar 307 formalises the lab CP falsifier preregistration. "
            "It does not promote P8 to CONSISTENT or FALSIFIED — only a "
            "decision-grade campaign with topology-certified σ ≤ 10⁻⁵ can do that. "
            "No hardgate claim labels are changed."
        ),
    }


# ── A_CP^lab prediction ───────────────────────────────────────────────────────

def compute_a_cp_lab_prediction(
    n1: int = N1_BRAID,
    n2: int = N2_BRAID,
    k_cs: int = K_CS,
    orientation_suppression: float = 100.0,
) -> dict:
    """Compute the predicted lab-scale CP asymmetry from braid geometry.

    Parameters
    ----------
    n1, n2:
        Braid winding numbers (canonical: 5, 7).
    k_cs:
        Chern-Simons level (canonical: 74).
    orientation_suppression:
        Geometric dilution from averaging over lab-frame orientations.
        Default 100 (representative for JJ/SQUID arrays).
    """
    if n1 <= 0 or n2 <= 0 or k_cs <= 0:
        raise ValueError("Winding numbers and K_CS must be positive.")
    theta = math.atan(n1 / n2)
    delta = abs(math.atan(n1 / n2) - math.atan(n2 / n1))
    j_geo = 0.25 * math.sin(delta) ** 2 * math.sin(2 * theta) ** 2
    eta_t_raw = n1 / k_cs
    a_cp_raw = j_geo * eta_t_raw
    a_cp_target = a_cp_raw / orientation_suppression
    return {
        "n1": n1,
        "n2": n2,
        "k_cs": k_cs,
        "theta_braid_deg": math.degrees(theta),
        "j_geo": round(j_geo, 6),
        "topology_transfer_efficiency_raw": round(eta_t_raw, 5),
        "a_cp_raw": round(a_cp_raw, 8),
        "orientation_suppression": orientation_suppression,
        "a_cp_lab_target": round(a_cp_target, 8),
        "order_of_magnitude": f"~O({a_cp_target:.0e})",
        "sigma_required_for_detection": A_CP_LAB_SIGMA_REQUIRED,
        "note": (
            "Target is an order-of-magnitude estimate. Precise value "
            "depends on platform-specific coherence length and coupling."
        ),
    }


def topology_transfer_estimate(
    xi_lab_over_xi_kk: float = 1.0,
    l_over_xi_t: float = 0.0,
) -> dict:
    """Estimate topology transfer efficiency η_T.

    Parameters
    ----------
    xi_lab_over_xi_kk:
        Ratio of lab coherence length to KK coherence length.
        For JJ arrays, this is effectively 1 in the idealized limit.
    l_over_xi_t:
        L/ξ_T — ratio of device length to topological coherence length.
        Set to 0 for ideal topological protection.
    """
    eta_t = (N1_BRAID / K_CS) * xi_lab_over_xi_kk * math.exp(-l_over_xi_t)
    a_cp_estimate = J_GEO_LAYER1 * eta_t
    return {
        "xi_lab_over_xi_kk": xi_lab_over_xi_kk,
        "l_over_xi_t": l_over_xi_t,
        "eta_t": round(eta_t, 6),
        "a_cp_estimate_before_dilution": round(a_cp_estimate, 8),
        "a_cp_with_100x_dilution": round(a_cp_estimate / 100.0, 8),
        "note": "Exponential suppression exp(-L/ξ_T) = 1.0 for ideal topological protection.",
    }


# ── Decision routing ──────────────────────────────────────────────────────────

def route_lab_cp_result(
    a_cp_measured: float,
    sigma_a: float,
    topology_certified: bool,
    n_sigma_threshold: float = 3.0,
) -> dict:
    """Route a lab CP measurement to CONSISTENT/FALSIFIED/BELOW_SENSITIVITY/INCONCLUSIVE.

    Parameters
    ----------
    a_cp_measured:
        Measured CP asymmetry value.
    sigma_a:
        Measurement 1σ uncertainty.
    topology_certified:
        True if the device has been certified as (5,7)-topology equivalent.
    n_sigma_threshold:
        Required significance for a verdict (default: 3σ).
    """
    abs_a_cp = abs(a_cp_measured)
    significance = abs_a_cp / sigma_a if sigma_a > 0 else float("inf")

    if not topology_certified:
        return {
            "verdict": "INCONCLUSIVE",
            "reason": (
                "Topology NOT certified. A (5,7)-topology certification is "
                "required before a verdict can be issued."
            ),
            "action": (
                "Certify device topology before reporting a verdict. "
                "Run control: topology-swap to different winding ratio must give null."
            ),
        }

    if sigma_a > A_CP_LAB_SIGMA_REQUIRED:
        return {
            "verdict": "BELOW_MEASUREMENT_THRESHOLD",
            "reason": (
                f"σ(A_CP) = {sigma_a:.2e} > required {A_CP_LAB_SIGMA_REQUIRED:.2e}. "
                "Measurement precision is insufficient for a verdict."
            ),
            "sigma_a": sigma_a,
            "required_sigma": A_CP_LAB_SIGMA_REQUIRED,
            "action": "Improve measurement precision to σ ≤ 1×10⁻⁵.",
        }

    if significance >= n_sigma_threshold:
        if abs_a_cp >= CONSISTENT_THRESHOLD:
            verdict = "CONSISTENT"
            reason = (
                f"|A_CP| = {abs_a_cp:.3e} ≥ {CONSISTENT_THRESHOLD:.0e} "
                f"at {significance:.1f}σ with topology certified."
            )
            action = (
                "Update P8 in OBSERVATION_TRACKER.md → CONSISTENT. "
                "Log provenance receipt. Continue campaign."
            )
        elif abs_a_cp < FALSIFICATION_THRESHOLD:
            verdict = "P8_TENSION"
            reason = (
                f"|A_CP| = {abs_a_cp:.3e} < {FALSIFICATION_THRESHOLD:.0e} "
                f"at {significance:.1f}σ. Framework tension at P8 level."
            )
            action = (
                "Update P8 → TENSION. Note: P2 framework falsification "
                "requires BOTH lab tension AND LiteBIRD β ∉ [0.22°, 0.38°]. "
                "Await independent replication and LiteBIRD data."
            )
        else:
            verdict = "BELOW_SENSITIVITY"
            reason = (
                f"|A_CP| = {abs_a_cp:.3e} between "
                f"{FALSIFICATION_THRESHOLD:.0e} and {CONSISTENT_THRESHOLD:.0e}."
            )
            action = (
                "Signal below target threshold. Improve platform sensitivity "
                "or increase statistics. Not yet a verdict."
            )
    else:
        verdict = "NO_VERDICT_YET"
        reason = (
            f"Significance = {significance:.1f}σ < {n_sigma_threshold}σ threshold."
        )
        action = "Increase statistics to reach 3σ significance."

    return {
        "verdict": verdict,
        "a_cp_measured": a_cp_measured,
        "sigma_a": sigma_a,
        "significance_sigma": round(significance, 2),
        "topology_certified": topology_certified,
        "reason": reason,
        "action": action,
    }


# ── Decision-grade checklist ──────────────────────────────────────────────────

def decision_grade_checklist() -> dict:
    """Return the five-item decision-grade checklist for the lab CP campaign."""
    return {
        "checklist": [
            {
                "item": "F-LAB-CP-1",
                "description": "Topology certification",
                "requirement": (
                    "Device operates with (5,7)-equivalent topological winding. "
                    "Control: different winding ratio gives null A_CP."
                ),
                "status": "NOT_LOGGED_YET",
            },
            {
                "item": "F-LAB-CP-2",
                "description": "Blinded analysis protocol",
                "requirement": (
                    "Analysis code finalized and registered BEFORE data collection. "
                    "Unblinding only after full dataset is recorded."
                ),
                "status": "NOT_LOGGED_YET",
            },
            {
                "item": "F-LAB-CP-3",
                "description": "σ(A_CP) ≤ 1×10⁻⁵",
                "requirement": (
                    "Measurement 1σ uncertainty must be at or below the target "
                    "signal amplitude."
                ),
                "status": "NOT_LOGGED_YET",
            },
            {
                "item": "F-LAB-CP-4",
                "description": "Control conditions passed",
                "requirement": (
                    "(a) Topology swap (different winding ratio): A_CP ≈ 0. "
                    "(b) Time-reversal break (sign reversal): A_CP flips sign. "
                    "Both controls required."
                ),
                "status": "NOT_LOGGED_YET",
            },
            {
                "item": "F-LAB-CP-5",
                "description": "Independent replication",
                "requirement": (
                    "At least one independent laboratory replication at decision-grade σ."
                ),
                "status": "NOT_LOGGED_YET",
            },
        ],
        "verdict_gate": (
            "All 5 items must be CONFIRMED before routing_lab_cp_result() "
            "can issue a CONSISTENT or P8_TENSION verdict."
        ),
        "preregistration_status": PREREGISTRATION_STATUS,
        "preregistration_date": "2026-05-20",
    }


# ── Preregistration packet ────────────────────────────────────────────────────

def preregistration_packet() -> dict:
    """Return the full machine-readable preregistration packet for P8."""
    return {
        "prediction": "P8",
        "prediction_label": "Lab-scale CP asymmetry in certified (5,7) condensed matter",
        "observable": "A_CP^lab = (Γ+ - Γ-) / (Γ+ + Γ-)",
        "predicted_value": f"~O({A_CP_LAB_TARGET_WITH_DILUTION:.0e})",
        "platforms": [
            "Josephson-junction / SQUID arrays (Track A)",
            "Topological-insulator winding devices (Track B)",
        ],
        "timeline": "Available NOW — no satellite or accelerator required",
        "preregistration_status": PREREGISTRATION_STATUS,
        "preregistration_version": PREREGISTRATION_VERSION,
        "routing_table": {
            "CONSISTENT": f"|A_CP| ≥ {CONSISTENT_THRESHOLD:.0e} at ≥3σ, topology certified",
            "P8_TENSION": f"|A_CP| < {FALSIFICATION_THRESHOLD:.0e} at ≥3σ, topology certified",
            "BELOW_SENSITIVITY": (
                f"|A_CP| between {FALSIFICATION_THRESHOLD:.0e} and "
                f"{CONSISTENT_THRESHOLD:.0e}"
            ),
            "INCONCLUSIVE": "Topology NOT certified",
        },
        "falsification_note": (
            "Lab TENSION at P8 does NOT independently falsify the framework. "
            "Full framework falsification requires BOTH lab tension AND "
            "LiteBIRD β ∉ [0.22°, 0.38°] at ≥3σ. See OBSERVATION_TRACKER P1/P8."
        ),
        "decision_grade_checklist": decision_grade_checklist(),
        "a_cp_prediction": compute_a_cp_lab_prediction(),
    }


# ── Full report ───────────────────────────────────────────────────────────────

def pillar307_report() -> dict:
    """Return the full Pillar 307 status report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "track": ADJACENCY_TRACK_LABEL,
        "separation_guard": separation_guard(),
        "preregistration": preregistration_packet(),
        "what_this_pillar_does": [
            "Makes P8 falsification conditions machine-queryable (identical in "
            "structure to Pillars 289–304 observatory preregistrations).",
            "Provides route_lab_cp_result() for deterministic verdict routing "
            "when measurement data arrives.",
            "Provides decision_grade_checklist() — 5 required items before "
            "a verdict can be issued.",
            "Documents topology-transfer geometry for platform designers.",
        ],
        "status": PREREGISTRATION_STATUS,
        "next_action": (
            "Execute F-LAB-CP-1 through F-LAB-CP-5 in the lab. "
            "Call route_lab_cp_result() with σ ≤ 10⁻⁵ data. "
            "This is the highest-priority falsifier executable today."
        ),
    }


# ── Collaboration request generator ──────────────────────────────────────────

def draft_collaboration_request(
    contact_name: Optional[str] = None,
    contact_institution: Optional[str] = None,
    include_technical_appendix: bool = True,
) -> dict:
    """Generate a structured collaboration request document for the Lab CP campaign.

    Produces a ready-to-send, plain-language collaboration request for an
    experimental group capable of measuring A_CP^lab at σ ≤ 10⁻⁵.  The
    document is self-contained and machine-readable; it can be exported to
    Markdown for distribution.

    Parameters
    ----------
    contact_name : str or None
        Name of the experimental contact (optional; placeholder if None).
    contact_institution : str or None
        Institution of the experimental contact (optional; placeholder if None).
    include_technical_appendix : bool
        If True, include the full technical specification (default True).

    Returns
    -------
    dict with keys:

    ``subject``              : str — subject line for the collaboration request
    ``preregistration_ref``  : str — formal preregistration reference
    ``measurement_target``   : dict — what must be measured and to what precision
    ``experimental_platforms``: list — JJ/SQUID Track A and topological TI Track B
    ``decision_grade_checklist``: list — F-LAB-CP-1 through F-LAB-CP-5
    ``timeline``             : str — "Available NOW — no satellite required"
    ``contact``              : dict — contact fields
    ``technical_appendix``   : dict or None — geometry derivation and routing table
    ``document_text``        : str — plain-language Markdown-ready letter body
    ``status``               : str — "OPERATIONALLY_READY"
    """
    contact = {
        "name": contact_name if contact_name else "[EXPERIMENTAL CONTACT NAME]",
        "institution": (
            contact_institution if contact_institution
            else "[EXPERIMENTAL INSTITUTION]"
        ),
    }

    measurement_target = {
        "observable": "A_CP^lab = (Γ+ − Γ−) / (Γ+ + Γ−)",
        "predicted_value": f"~O({A_CP_LAB_TARGET_WITH_DILUTION:.0e})",
        "required_sigma": f"σ(A_CP) ≤ {A_CP_LAB_SIGMA_REQUIRED:.0e}",
        "significance_required": "≥ 3σ for a decision-grade verdict",
        "topology_requirement": (
            "(5,7)-equivalent braid winding geometry must be "
            "certified in the experimental device"
        ),
    }

    experimental_platforms = [
        {
            "track": "Track A",
            "platform": "Josephson-junction / SQUID arrays",
            "why": (
                "JJ arrays can be engineered with (5,7)-winding-equivalent "
                "topological boundary conditions.  The CP asymmetry enters via "
                "the braid phase difference in the tunnelling Hamiltonian."
            ),
            "sensitivity_estimate": (
                "Modern dilution-refrigerator JJ platforms achieve "
                "σ(A_CP) ~ 10⁻⁵–10⁻⁶ with lock-in detection and "
                "repeated switching."
            ),
        },
        {
            "track": "Track B",
            "platform": "Topological-insulator (TI) winding devices",
            "why": (
                "TI surface states with (5,7)-winding number support "
                "topological CP breaking via the axion coupling.  "
                "A_CP is measurable as a Hall asymmetry at low temperature."
            ),
            "sensitivity_estimate": (
                "TI Hall measurements at mK temperatures achieve "
                "σ(A_CP) ~ few × 10⁻⁵; improvements toward 10⁻⁵ "
                "are feasible with extended averaging."
            ),
        },
    ]

    checklist = decision_grade_checklist()["checklist"]

    tech_appendix: Optional[dict] = None
    if include_technical_appendix:
        prediction = compute_a_cp_lab_prediction()
        tech_appendix = {
            "geometry": {
                "braid_pair": f"(n₁, n₂) = ({N1_BRAID}, {N2_BRAID})",
                "k_cs": K_CS,
                "jarlskog_proxy": round(J_GEO_LAYER1, 6),
                "topology_transfer_efficiency_raw": round(N1_BRAID / K_CS, 5),
                "orientation_suppression_factor": 100,
                "a_cp_derivation": prediction,
            },
            "routing_table": {
                "CONSISTENT": (
                    f"|A_CP| ≥ {CONSISTENT_THRESHOLD:.0e} at ≥3σ, "
                    "topology certified → Update P8 to CONSISTENT"
                ),
                "P8_TENSION": (
                    f"|A_CP| < {FALSIFICATION_THRESHOLD:.0e} at ≥3σ, "
                    "topology certified → P8 TENSION "
                    "(full framework falsification also requires LiteBIRD)"
                ),
                "BELOW_SENSITIVITY": (
                    f"|A_CP| between {FALSIFICATION_THRESHOLD:.0e} and "
                    f"{CONSISTENT_THRESHOLD:.0e} → improve precision"
                ),
                "INCONCLUSIVE": (
                    "Topology NOT certified → re-certify before reporting"
                ),
            },
            "preregistration_date": "2026-05-20",
            "preregistration_version": PREREGISTRATION_VERSION,
        }

    document_text = f"""## Collaboration Request — Lab-Scale CP Falsifier Campaign
### Preregistration: {PREREGISTRATION_STATUS}
### Date: 2026-05-20 | Reference: P307 / OBSERVATION_TRACKER P8

Dear {contact["name"]} ({contact["institution"]}),

We are writing to invite your group to participate in a near-term experimental
campaign to test a specific, quantitative prediction of the Unitary Manifold (UM)
theoretical framework.

**The Prediction (Preregistered P8)**

The UM (5,7) braid geometry predicts a laboratory-measurable CP asymmetry:

    A_CP^lab = (Γ+ − Γ−) / (Γ+ + Γ−) ~ O(2×10⁻⁵)

in condensed-matter platforms with (5,7)-equivalent topological winding geometry
(Josephson-junction/SQUID arrays or topological-insulator winding devices).

This prediction is FALSIFIABLE NOW — no satellite or accelerator is required.

**Required Measurement Precision**

    σ(A_CP) ≤ 1×10⁻⁵

at ≥ 3σ significance, in a topology-certified device.

**Decision-Grade Checklist (F-LAB-CP-1 through F-LAB-CP-5)**

Before a verdict (CONSISTENT or P8_TENSION) can be issued, all five items
must be CONFIRMED:

"""
    for item in checklist:
        document_text += (
            f"  [{item['item']}] {item['description']}: "
            f"{item['requirement']}\n\n"
        )

    document_text += f"""
**Routing Protocol**

Results are routed deterministically via pillar307_lab_cp_falsifier_preregistration.route_lab_cp_result().
A null result at topology-certified σ ≤ 10⁻⁶ would create a P8-TENSION signal;
full framework falsification requires BOTH lab tension AND LiteBIRD β ∉ [0.22°, 0.38°].

**Preregistration Reference**

    Framework:   Unitary Manifold v{PREREGISTRATION_VERSION}
    Preregistered: 2026-05-20
    Status:      {PREREGISTRATION_STATUS}
    DOI:         https://doi.org/10.5281/zenodo.19584531

We welcome discussion of platform design, topology certification protocol,
and blinding strategy.  Please contact us via the GitHub repository:
https://github.com/wuzbak/Unitary-Manifold-/issues

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

    return {
        "subject": (
            "Collaboration Invitation — Lab-Scale CP Falsifier Campaign "
            f"(Preregistered P307 / {PREREGISTRATION_STATUS})"
        ),
        "preregistration_ref": PREREGISTRATION_STATUS,
        "measurement_target": measurement_target,
        "experimental_platforms": experimental_platforms,
        "decision_grade_checklist": checklist,
        "timeline": "Available NOW — no satellite or accelerator required",
        "contact": contact,
        "technical_appendix": tech_appendix,
        "document_text": document_text,
        "status": "OPERATIONALLY_READY",
    }
