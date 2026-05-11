# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
desi_year3_monitor.py — DESI Year 3 / wₐ tension monitoring harness.

═══════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════
The Pillar 155 module (kk_de_wa_cpl.py) documents the 2.1σ wₐ tension
between the UM prediction (wₐ = 0) and DESI DR2 (wₐ = −0.62 ± 0.30).

This monitoring harness:
  1. Stores the current observational state (DESI DR2 baseline).
  2. Provides a structured comparison framework for DESI Year 3 results
     (~2026) when they become available.
  3. Tracks the tension evolution as a function of the wₐ central value
     and uncertainty.
  4. Documents the UM falsification condition for the wₐ parameter.

═══════════════════════════════════════════════════════════════════════════
DESI YEAR 3 FALSIFICATION CONDITIONS
═══════════════════════════════════════════════════════════════════════════
The UM predicts wₐ = 0 exactly (frozen GW radion).

  • If DESI Year 3 gives wₐ = 0 consistent at < 1σ → UM consistent ✅
  • If DESI Year 3 gives wₐ ≠ 0 at > 3σ → UM predicts wₐ = 0 is excluded:
      Tension documented as HONEST_OPEN_PROBLEM.
      Resolution requires either:
        (a) A new geometric sector in the UM beyond the radion, or
        (b) Systematic effects in DESI (lensing, CMB cross-calibration).

CURRENT STATUS (DESI DR2, arXiv:2503.14738):
  w₀ = −0.838 ± 0.072  →  UM w₀ = −0.9302 at 1.3σ  ✅ CONSISTENT
  wₐ = −0.62 ± 0.30   →  UM wₐ = 0 at 2.1σ        ⚠️ OPEN TENSION

═══════════════════════════════════════════════════════════════════════════

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

__all__ = [
    # Baseline data
    "DESI_DR2",
    "UM_PREDICTION",
    "MONITOR_INTEGRATION_TARGETS",
    "REQUIRED_RELEASE_FIELDS",
    # Functions
    "tension_from_measurement",
    "routing_decision",
    "route_desi_y3",
    "update_with_new_data",
    "validate_release_payload",
    "strict_release_ingest",
    "falsification_verdict",
    "monitoring_report",
    "desi_year3_placeholder",
]

# ---------------------------------------------------------------------------
# Baseline observational data (DESI DR2)
# ---------------------------------------------------------------------------

#: DESI DR2 CPL constraints (arXiv:2503.14738, 2025)
DESI_DR2: Dict = {
    "release": "DESI DR2",
    "year": 2025,
    "reference": "DESI Collaboration (2025), arXiv:2503.14738",
    "w0_central": -0.838,
    "w0_sigma": 0.072,
    "wa_central": -0.62,
    "wa_sigma": 0.30,
    "datasets": "BAO + CMB + SNe Ia",
    "status": "CURRENT_BASELINE",
}

MONITOR_INTEGRATION_TARGETS: List[str] = [
    "src/core/kk_de_wa_cpl.py",
    "3-FALSIFICATION/OBSERVATION_TRACKER.md",
    "src/core/canonical_falsifier_evidence_feed.py",
]

REQUIRED_RELEASE_FIELDS: List[str] = [
    "release_name",
    "year",
    "w0_central",
    "w0_sigma",
    "wa_central",
    "wa_sigma",
    "reference",
    "datasets",
]
_PAYLOAD_ALIASES = {
    "release": "release_name",
    "w0": "w0_central",
    "w0_err": "w0_sigma",
    "wa": "wa_central",
    "wa_err": "wa_sigma",
    "citation": "reference",
    "data": "datasets",
}


def _validate_positive_sigmas(w0_sigma: float, wa_sigma: float) -> None:
    """Shared strict-ingest sigma positivity guard."""
    if w0_sigma <= 0 or wa_sigma <= 0:
        raise ValueError("w0_sigma and wa_sigma must be strictly positive.")

#: UM predictions for w₀ and wₐ
UM_PREDICTION: Dict = {
    "w0": -1.0 + (2.0 / 3.0) * (12.0 / 37.0) ** 2,  # = W_KK ≈ −0.9302
    "wa": 0.0,
    "mechanism_w0": "w₀ = −1 + (2/3)c_s² with c_s = 12/37 (braided KK zero-mode)",
    "mechanism_wa": "wₐ = 0 (GW-stabilised radion frozen at m_r >> H₀)",
    "falsification_wa": "wₐ ≠ 0 at > 3σ would require new geometric sector",
    "module": "src/core/kk_de_wa_cpl.py (Pillar 155)",
}


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def tension_from_measurement(
    w0_obs: float,
    w0_sigma: float,
    wa_obs: float,
    wa_sigma: float,
    release_name: str = "custom",
) -> Dict:
    """Compute UM tension vs an observed CPL measurement.

    Parameters
    ----------
    w0_obs : float   Observed w₀ central value.
    w0_sigma : float Observed w₀ uncertainty (1σ).
    wa_obs : float   Observed wₐ central value.
    wa_sigma : float Observed wₐ uncertainty (1σ).
    release_name : str  Name of the data release.

    Returns
    -------
    dict with tension analysis and consistency verdict.
    """
    w0_um = UM_PREDICTION["w0"]
    wa_um = UM_PREDICTION["wa"]

    tension_w0 = abs(w0_um - w0_obs) / w0_sigma if w0_sigma > 0 else float("inf")
    tension_wa = abs(wa_um - wa_obs) / wa_sigma if wa_sigma > 0 else float("inf")

    consistent_w0 = tension_w0 < 2.0
    consistent_wa = tension_wa < 2.0
    tension_combined = math.sqrt(tension_w0**2 + tension_wa**2)

    return {
        "release": release_name,
        "um_w0": w0_um,
        "obs_w0": w0_obs,
        "obs_w0_sigma": w0_sigma,
        "tension_w0_sigma": tension_w0,
        "consistent_w0": consistent_w0,
        "um_wa": wa_um,
        "obs_wa": wa_obs,
        "obs_wa_sigma": wa_sigma,
        "tension_wa_sigma": tension_wa,
        "consistent_wa": consistent_wa,
        "tension_combined_sigma": tension_combined,
        "overall_consistent": consistent_w0 and consistent_wa,
        "verdict": (
            "CONSISTENT ✅" if (consistent_w0 and consistent_wa)
            else f"PARTIAL_TENSION ⚠️ (w₀: {tension_w0:.1f}σ, wₐ: {tension_wa:.1f}σ)"
        ),
    }


def routing_decision(
    w0_tension_sigma: float,
    wa_tension_sigma: float,
    release_name: str,
    year: int,
) -> Dict[str, object]:
    """Route a new dark-energy release into PASS/TENSION/FALSIFIED buckets."""
    if wa_tension_sigma >= 3.0:
        route = "FALSIFIED"
        status = "❌ FALSIFIED"
        action = (
            "Update kk_de_wa_cpl.py, OBSERVATION_TRACKER.md, and the canonical "
            "falsifier feed immediately; record the ≥3σ Year-3 exclusion."
        )
    elif wa_tension_sigma >= 1.0 or w0_tension_sigma >= 2.0:
        route = "TENSION"
        status = "🟠 TENSION"
        action = (
            "Record the release as monitored tension; keep the gap open and do "
            "not claim any rescue without a new geometric sector."
        )
    else:
        route = "PASS"
        status = "🟢 PASS"
        action = (
            "Record the release as consistent in the tracker, sync the canonical "
            "feed, and preserve wₐ = 0 as unfalsified."
        )

    return {
        "route": route,
        "status": status,
        "release": release_name,
        "year": year,
        "integration_targets": list(MONITOR_INTEGRATION_TARGETS),
        "action": action,
    }


def route_desi_y3(wa: float, sigma: float) -> Dict[str, object]:
    """Route DESI Year 3 using explicit PASS/TENSION/FALSIFIED policy.

    Parameters
    ----------
    wa : float
        DESI Year 3 wₐ central value.
    sigma : float
        DESI Year 3 wₐ uncertainty (1σ).
    """
    wa_tension_sigma = abs(wa - UM_PREDICTION["wa"]) / sigma if sigma > 0 else float("inf")
    # Keep w0 routing anchored to current baseline unless explicit Y3 w0 is provided.
    w0_tension_sigma = abs(UM_PREDICTION["w0"] - DESI_DR2["w0_central"]) / DESI_DR2["w0_sigma"]
    route = routing_decision(
        w0_tension_sigma=w0_tension_sigma,
        wa_tension_sigma=wa_tension_sigma,
        release_name="DESI Year 3",
        year=2026,
    )
    route.update(
        {
            "wa_input": wa,
            "sigma_input": sigma,
            "wa_tension_sigma": wa_tension_sigma,
        }
    )
    return route


def update_with_new_data(
    release_name: str,
    year: int,
    w0_central: float,
    w0_sigma: float,
    wa_central: float,
    wa_sigma: float,
    reference: str = "",
    datasets: str = "",
) -> Dict:
    """Process new observational data and compare with UM prediction.

    This function is designed to be called when new DESI (or other)
    results become available.  It returns a full comparison report.

    Parameters
    ----------
    release_name : str  Name of the data release (e.g. "DESI Year 3").
    year : int          Year of the release.
    w0_central : float  Observed w₀ central value.
    w0_sigma : float    Observed w₀ uncertainty.
    wa_central : float  Observed wₐ central value.
    wa_sigma : float    Observed wₐ uncertainty.
    reference : str     Reference (arXiv or journal).
    datasets : str      Datasets used (e.g. "BAO + CMB + SNe Ia").

    Returns
    -------
    dict with full comparison vs DESI DR2 baseline and UM prediction.
    """
    # Keep direct-call safety even though strict_release_ingest() also validates.
    _validate_positive_sigmas(w0_sigma, wa_sigma)

    new_tension = tension_from_measurement(
        w0_central, w0_sigma, wa_central, wa_sigma, release_name
    )
    dr2_tension = tension_from_measurement(
        DESI_DR2["w0_central"],
        DESI_DR2["w0_sigma"],
        DESI_DR2["wa_central"],
        DESI_DR2["wa_sigma"],
        "DESI DR2 baseline",
    )

    # Compute improvement vs DESI DR2 baseline
    wa_tension_dr2 = dr2_tension["tension_wa_sigma"]
    wa_tension_new = new_tension["tension_wa_sigma"]
    wa_improvement = wa_tension_dr2 - wa_tension_new
    routing = routing_decision(
        new_tension["tension_w0_sigma"],
        new_tension["tension_wa_sigma"],
        release_name,
        year,
    )

    return {
        "release": release_name,
        "year": year,
        "reference": reference,
        "datasets": datasets,
        "new_data": {
            "w0_central": w0_central,
            "w0_sigma": w0_sigma,
            "wa_central": wa_central,
            "wa_sigma": wa_sigma,
        },
        "um_tension": new_tension,
        "baseline_tension": dr2_tension,
        "routing": routing,
        "wa_tension_improvement_sigma": wa_improvement,
        "wording": (
            f"{release_name} ({year}): wₐ = {wa_central:.2f} ± {wa_sigma:.2f}. "
            f"UM tension: {wa_tension_new:.1f}σ (vs {wa_tension_dr2:.1f}σ at DESI DR2). "
            f"{'Tension reduced ✅' if wa_improvement > 0 else 'Tension increased ⚠️'}."
        ),
    }


def validate_release_payload(payload: Dict) -> Dict:
    """Validate and normalise a strict DESI-style release payload."""
    normalized_payload = dict(payload)
    for alias, canonical in _PAYLOAD_ALIASES.items():
        if canonical not in normalized_payload and alias in normalized_payload:
            normalized_payload[canonical] = normalized_payload[alias]

    missing = [key for key in REQUIRED_RELEASE_FIELDS if key not in normalized_payload]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    release_name = str(normalized_payload["release_name"]).strip()
    reference = str(normalized_payload["reference"]).strip()
    datasets = str(normalized_payload["datasets"]).strip()
    year = int(normalized_payload["year"])
    w0_central = float(normalized_payload["w0_central"])
    w0_sigma = float(normalized_payload["w0_sigma"])
    wa_central = float(normalized_payload["wa_central"])
    wa_sigma = float(normalized_payload["wa_sigma"])

    if year < int(DESI_DR2["year"]):
        raise ValueError(f"year must be >= {DESI_DR2['year']} for this monitoring pipeline.")
    if year > 2100:
        raise ValueError("year must be <= 2100 for this monitoring pipeline.")
    if not release_name:
        raise ValueError("release_name must be non-empty.")
    _validate_positive_sigmas(w0_sigma, wa_sigma)
    numeric_fields = {
        "w0_central": w0_central,
        "w0_sigma": w0_sigma,
        "wa_central": wa_central,
        "wa_sigma": wa_sigma,
    }
    for name, value in numeric_fields.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite, got {value!r}")
    # Broad ingest guardrails for physical plausibility / typo resistance:
    #   w0 is expected near O(1) around -1 and wa in an O(1) dynamical range,
    #   so we keep a conservative superset envelope for CPL-like posteriors.
    # These are not hard cosmology priors, only strict-ingest safety bounds.
    if not (-3.0 <= w0_central <= 1.0):
        raise ValueError("w0_central outside physics-safe ingest bounds [-3, 1].")
    if not (-5.0 <= wa_central <= 5.0):
        raise ValueError("wa_central outside physics-safe ingest bounds [-5, 5].")
    if not (0.0 < w0_sigma <= 2.0):
        raise ValueError("w0_sigma outside physics-safe ingest bounds (0, 2].")
    if not (0.0 < wa_sigma <= 2.0):
        raise ValueError("wa_sigma outside physics-safe ingest bounds (0, 2].")
    if not reference:
        raise ValueError("reference must be non-empty.")
    if not datasets:
        raise ValueError("datasets must be non-empty.")

    return {
        "release_name": release_name,
        "year": year,
        "w0_central": w0_central,
        "w0_sigma": w0_sigma,
        "wa_central": wa_central,
        "wa_sigma": wa_sigma,
        "reference": reference,
        "datasets": datasets,
    }


def strict_release_ingest(payload: Dict) -> Dict:
    """Strict release-ingest entrypoint for DESI Year-3 readiness."""
    valid = validate_release_payload(payload)
    analysis = update_with_new_data(
        release_name=valid["release_name"],
        year=valid["year"],
        w0_central=valid["w0_central"],
        w0_sigma=valid["w0_sigma"],
        wa_central=valid["wa_central"],
        wa_sigma=valid["wa_sigma"],
        reference=valid["reference"],
        datasets=valid["datasets"],
    )

    return {
        "pipeline": "DESI_Y3_STRICT_INGEST",
        "validated_payload": valid,
        "normalization": "alias-aware",
        "analysis": analysis,
        "route": analysis["routing"]["route"],
        "integration_targets": list(MONITOR_INTEGRATION_TARGETS),
        "ready_for_release_day": True,
    }


def falsification_verdict(wa_obs: float, wa_sigma: float) -> Dict:
    """Return falsification verdict for the UM wₐ = 0 prediction.

    Parameters
    ----------
    wa_obs : float   Observed wₐ central value.
    wa_sigma : float Observed wₐ uncertainty (1σ).

    Returns
    -------
    dict with falsification assessment.
    """
    wa_um = 0.0
    tension = abs(wa_um - wa_obs) / wa_sigma if wa_sigma > 0 else float("inf")

    if tension < 1.0:
        verdict = "CONSISTENT — UM wₐ=0 within 1σ ✅"
        level = "CONSISTENT"
    elif tension < 2.0:
        verdict = f"MARGINAL — UM wₐ=0 at {tension:.1f}σ; monitoring required ⚠️"
        level = "MARGINAL"
    elif tension < 3.0:
        verdict = f"TENSION — UM wₐ=0 at {tension:.1f}σ; HONEST_OPEN_PROBLEM ⚠️"
        level = "TENSION"
    else:
        verdict = f"EXCLUDED — UM wₐ=0 at {tension:.1f}σ; requires new geometric sector 🔴"
        level = "EXCLUDED"

    return {
        "wa_um_prediction": wa_um,
        "wa_observed": wa_obs,
        "wa_sigma": wa_sigma,
        "tension_sigma": tension,
        "verdict": verdict,
        "level": level,
        "action_required": (
            "Document as HONEST_OPEN_PROBLEM in FALLIBILITY.md"
            if level in ("TENSION", "EXCLUDED")
            else "No action — within observational uncertainty"
        ),
    }


def monitoring_report() -> Dict:
    """Generate current monitoring report vs DESI DR2 baseline.

    Returns
    -------
    dict with full monitoring state.
    """
    dr2 = tension_from_measurement(
        DESI_DR2["w0_central"],
        DESI_DR2["w0_sigma"],
        DESI_DR2["wa_central"],
        DESI_DR2["wa_sigma"],
        "DESI DR2",
    )
    verdict = falsification_verdict(DESI_DR2["wa_central"], DESI_DR2["wa_sigma"])
    routing = routing_decision(
        dr2["tension_w0_sigma"],
        dr2["tension_wa_sigma"],
        DESI_DR2["release"],
        DESI_DR2["year"],
    )

    return {
        "version": "v10.26",
        "current_baseline": DESI_DR2,
        "um_prediction": UM_PREDICTION,
        "current_tension": dr2,
        "falsification_verdict": verdict,
        "routing": routing,
        "next_milestone": {
            "release": "DESI Year 3",
            "expected_year": 2026,
            "expected_wa_sigma": 0.20,
            "note": (
                "DESI Year 3 (~2026) is expected to reduce wₐ uncertainty "
                "to ~0.20. If wₐ remains at −0.62 with σ=0.20, tension rises "
                "to ~3.1σ — potential falsification of UM wₐ=0."
            ),
        },
        "update_instructions": (
            "When DESI Year 3 results are available, call strict_release_ingest(payload) "
            "with required fields from REQUIRED_RELEASE_FIELDS."
        ),
    }


def desi_year3_placeholder() -> Dict:
    """Placeholder for DESI Year 3 data (to be filled when available).

    Returns
    -------
    dict with placeholder status.
    """
    return {
        "release": "DESI Year 3",
        "year": 2026,
        "status": "READY_FOR_STRICT_INGEST",
        "required_fields": list(REQUIRED_RELEASE_FIELDS),
        "example_payload": {
            "release_name": "DESI Year 3",
            "year": 2026,
            "w0_central": -0.84,
            "w0_sigma": 0.06,
            "wa_central": -0.40,
            "wa_sigma": 0.20,
            "reference": "DESI Collaboration (2026), preprint",
            "datasets": "BAO Year 3 + CMB + SNe Ia",
        },
        "expected_datasets": "BAO Year 3 + CMB (ACT DR6 / Planck PR4) + DESY5 SNe",
        "expected_improvement": "~2× improvement in wₐ precision (σ_wₐ ≈ 0.15–0.20)",
        "um_falsification_threshold": (
            "If wₐ ≠ 0 at > 3σ with Year 3 data → UM wₐ=0 excluded; "
            "requires new geometric sector (quintessence or bulk field)."
        ),
        "action_on_release": (
            "Validate payload with validate_release_payload() and ingest via "
            "strict_release_ingest() to route and publish integration targets."
        ),
        "integration_targets": list(MONITOR_INTEGRATION_TARGETS),
    }
