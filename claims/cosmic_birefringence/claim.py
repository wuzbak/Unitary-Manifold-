# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Cosmic Birefringence Falsification Claim.

═══════════════════════════════════════════════════════════════════════════
CLAIM
═══════════════════════════════════════════════════════════════════════════
The Unitary Manifold predicts that the CMB cosmic birefringence angle β
takes one of exactly TWO values, determined by the (n₁, n₂) braid pair:

  β_canonical = β((5,7) braid) ≈ 0.331°   [K_CS = 74]
  β_alternate  = β((5,6) braid) ≈ 0.273°   [K_CS = 61]

The gap between these two predictions [0.29°, 0.31°] contains ZERO viable
braid pairs.  Any measurement inside this gap falsifies the braid mechanism.

The admissible window is [0.223°, 0.381°].  Any β outside this window
falsifies the UM birefringence sector completely.

═══════════════════════════════════════════════════════════════════════════
DERIVATION CHAIN (AxiomZero compliant)
═══════════════════════════════════════════════════════════════════════════
  Input:  {K_CS = 74, n_w = 5}  (no measured SM values)

  Step 1: The CS axion-photon coupling is g_aγγ = α_em/(π f_a) × K_CS
          where α_em = 1/137.036 (UM-DERIVED, P1/Pillar 56: α = φ₀⁻²).

  Step 2: Birefringence angle β = g_aγγ × B_CMB × L_Hubble / 2
          integrated along the photon path.

  Step 3: The integer minimiser of |β(k) − β_geom| selects k = 74 for the
          (5,7) braid and k = 61 for the (5,6) braid.

  See: src/core/braided_winding.birefringence_scenario_scan()
       src/core/cmb_topology.beta_from_cs()

═══════════════════════════════════════════════════════════════════════════
EXPERIMENTAL TARGET
═══════════════════════════════════════════════════════════════════════════
  LiteBIRD (JAXA, launch ~2032): expected sensitivity σ(β) ≈ 0.05° at 95%CL.
  This is sufficient to resolve the two predicted values (separation ≈ 0.058°).

  Current hints: Minami & Komatsu 2020 / Diego-Palazuelos 2022 report β ≈ 0.30°
  at 2–3σ — within the admissible window but between the two predicted values.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

from typing import Dict

__all__ = [
    # Constants
    "BETA_CANONICAL_DEG",
    "BETA_ALTERNATE_DEG",
    "KILL_ZONE_LOW_DEG",
    "KILL_ZONE_HIGH_DEG",
    "ADMISSIBLE_LOW_DEG",
    "ADMISSIBLE_HIGH_DEG",
    "K_CS_CANONICAL",
    "K_CS_ALTERNATE",
    # Falsification condition dict
    "FALSIFICATION_CONDITION",
    # Functions
    "evaluate_measurement",
]

# ─────────────────────────────────────────────────────────────────────────────
# PREDICTED VALUES
# ─────────────────────────────────────────────────────────────────────────────

#: Canonical prediction β for the (5,7) braid, K_CS = 74.
BETA_CANONICAL_DEG: float = 0.331

#: Alternate prediction β for the (5,6) braid, K_CS = 61.
BETA_ALTERNATE_DEG: float = 0.273

#: Chern-Simons level for the canonical (5,7) state.
K_CS_CANONICAL: int = 74

#: Chern-Simons level for the alternate (5,6) state.
K_CS_ALTERNATE: int = 61

# ─────────────────────────────────────────────────────────────────────────────
# FALSIFICATION BOUNDARIES
# ─────────────────────────────────────────────────────────────────────────────

#: Lower edge of the "kill zone" — the gap between the two predicted values.
#: Any measurement strictly inside [KILL_ZONE_LOW_DEG, KILL_ZONE_HIGH_DEG]
#: corresponds to zero viable braid pairs and falsifies the mechanism.
KILL_ZONE_LOW_DEG: float = 0.290

#: Upper edge of the kill zone.
KILL_ZONE_HIGH_DEG: float = 0.310

#: Lower edge of the full admissible window.
#: Any β below this value falsifies the UM birefringence sector entirely.
ADMISSIBLE_LOW_DEG: float = 0.223

#: Upper edge of the full admissible window.
#: Any β above this value falsifies the UM birefringence sector entirely.
ADMISSIBLE_HIGH_DEG: float = 0.381

# ─────────────────────────────────────────────────────────────────────────────
# MACHINE-READABLE FALSIFICATION CONDITION
# ─────────────────────────────────────────────────────────────────────────────

#: The canonical falsification condition dict.
#: External tools should query this dict to evaluate experimental results.
FALSIFICATION_CONDITION: Dict[str, object] = {
    "claim": "Cosmic birefringence β takes one of two values from the (5,7) or (5,6) braid",
    "prediction": {
        "canonical_deg": BETA_CANONICAL_DEG,
        "alternate_deg": BETA_ALTERNATE_DEG,
        "source": "(5,7) braid: K_CS=74=5²+7²; (5,6) braid: K_CS=61=5²+6²",
        "derivation": "src/core/braided_winding.birefringence_scenario_scan()",
    },
    "experimental_target": {
        "measurement_hint_deg": 0.30,
        "hint_significance": "2-3σ (Minami & Komatsu 2020, Diego-Palazuelos 2022)",
        "definitive_experiment": "LiteBIRD",
        "experiment_launch": "~2032",
        "expected_sensitivity_deg": 0.05,
    },
    "kill_threshold": {
        "kill_zone_deg": [KILL_ZONE_LOW_DEG, KILL_ZONE_HIGH_DEG],
        "kill_zone_description": (
            f"β ∈ [{KILL_ZONE_LOW_DEG}°, {KILL_ZONE_HIGH_DEG}°] — "
            "zero viable braid pairs in this interval → braid mechanism falsified"
        ),
        "outside_admissible_window": (
            f"β < {ADMISSIBLE_LOW_DEG}° or β > {ADMISSIBLE_HIGH_DEG}° — "
            "no viable braid pair exists → full birefringence sector falsified"
        ),
    },
    "experiment": "LiteBIRD (JAXA, launch ~2032) — expected σ(β) ≈ 0.05°",
    "timeline": "LiteBIRD launch ~2032; definitive result expected ~2034–2036",
    "pillar": "58 (birefringence derivation), 208 (Braid-Lock PMNS complement)",
    "toe_relevance": (
        "β is the PRIMARY falsification target.  Failure here invalidates "
        "K_CS = 74 and all predictions derived from the braid geometry."
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# EVALUATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_measurement(
    beta_measured_deg: float,
    sigma_deg: float = 0.0,
) -> Dict[str, object]:
    """Evaluate an experimental β measurement against the UM prediction.

    Parameters
    ----------
    beta_measured_deg :
        Measured birefringence angle in degrees.
    sigma_deg :
        1σ uncertainty of the measurement in degrees (0 = assume exact).

    Returns
    -------
    result : dict with keys:
        ``verdict``            — "CONSISTENT", "FALSIFIED_KILL_ZONE",
                                 "FALSIFIED_OUTSIDE_WINDOW", or "AMBIGUOUS"
        ``nearest_prediction`` — "canonical", "alternate", or "none"
        ``residual_canonical_deg`` — |β_measured − β_canonical|
        ``residual_alternate_deg`` — |β_measured − β_alternate|
        ``in_kill_zone``       — True if measurement is in the kill zone
        ``in_admissible_window`` — True if measurement is in [0.223°, 0.381°]
        ``message``            — human-readable verdict
    """
    res_can = abs(beta_measured_deg - BETA_CANONICAL_DEG)
    res_alt = abs(beta_measured_deg - BETA_ALTERNATE_DEG)
    nearest = "canonical" if res_can <= res_alt else "alternate"
    nearest_res = min(res_can, res_alt)

    in_kill_zone = KILL_ZONE_LOW_DEG <= beta_measured_deg <= KILL_ZONE_HIGH_DEG
    in_window = ADMISSIBLE_LOW_DEG <= beta_measured_deg <= ADMISSIBLE_HIGH_DEG

    if not in_window:
        verdict = "FALSIFIED_OUTSIDE_WINDOW"
        message = (
            f"β = {beta_measured_deg:.4f}° is outside the admissible window "
            f"[{ADMISSIBLE_LOW_DEG}°, {ADMISSIBLE_HIGH_DEG}°]. "
            "The UM birefringence sector is FALSIFIED."
        )
    elif in_kill_zone:
        verdict = "FALSIFIED_KILL_ZONE"
        message = (
            f"β = {beta_measured_deg:.4f}° is inside the kill zone "
            f"[{KILL_ZONE_LOW_DEG}°, {KILL_ZONE_HIGH_DEG}°]. "
            "Zero viable braid pairs exist here — braid mechanism FALSIFIED."
        )
    elif sigma_deg > 0 and nearest_res < 3.0 * sigma_deg:
        verdict = "CONSISTENT"
        nearest_val = BETA_CANONICAL_DEG if nearest == "canonical" else BETA_ALTERNATE_DEG
        message = (
            f"β = {beta_measured_deg:.4f}° ± {sigma_deg:.4f}° is consistent "
            f"with the {nearest} prediction "
            f"({nearest_val:.3f}°) "
            f"at {nearest_res / sigma_deg:.1f}σ."
        )
    elif sigma_deg == 0 and nearest_res < 0.05:
        verdict = "CONSISTENT"
        nearest_val = BETA_CANONICAL_DEG if nearest == "canonical" else BETA_ALTERNATE_DEG
        message = (
            f"β = {beta_measured_deg:.4f}° is within 0.05° of the {nearest} "
            f"prediction ({nearest_val:.3f}°)."
        )
    else:
        verdict = "AMBIGUOUS"
        message = (
            f"β = {beta_measured_deg:.4f}° is in the admissible window but "
            f"{nearest_res:.4f}° from the nearest prediction. "
            "Result is ambiguous — may require higher precision."
        )

    return {
        "verdict": verdict,
        "nearest_prediction": nearest,
        "residual_canonical_deg": res_can,
        "residual_alternate_deg": res_alt,
        "in_kill_zone": in_kill_zone,
        "in_admissible_window": in_window,
        "message": message,
    }
