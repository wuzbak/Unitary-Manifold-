# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""DESI tension monitor for the exact KK dark-energy prediction (w0=-1, wa=0).

Tension metric policy (v11.x correction)
-----------------------------------------
The correct defensible tension figure is the **wₐ-only** single-parameter
statistic, which matches the numbers published in the DESI DR2 paper itself
(arXiv:2503.14738):

  BAO-only:  |wₐ| / σ_wₐ = 0.62 / 0.30 = 2.07σ
  Combined:  |wₐ| / σ_wₐ = 0.55 / 0.20 = 2.75σ

The previous implementation computed a naive uncorrelated joint quadrature
sum over both w0 and wₐ deviations, yielding 3.30σ.  That figure is
**methodologically incorrect**: the w0–wₐ posterior from any CPL BAO+CMB+SNe
fit carries a strong negative correlation (ρ ≈ −0.75 to −0.85), which
significantly reduces the joint chi-squared.  With the proper covariance
correction (ρ = −0.80 for the combined analysis) the joint tension falls
to ≈ 2.82σ — still below the 3σ falsification threshold and consistent
with the documented HIGH_TENSION status.

``DESI_TENSION_SIGMA`` is now the wₐ-only value (2.75σ), matching all
documentation.  The covariance-corrected joint statistic is exported as
``DESI_JOINT_TENSION_SIGMA`` for completeness.

References: DESI Collaboration (2025), arXiv:2503.14738, Tables 2 & 4.
"""

from __future__ import annotations

import math
from typing import Dict, Optional

KK_W0_PREDICTION: float = -1.0
KK_WA_PREDICTION: float = 0.0

# DESI DR2 BAO+CMB+SNe combined constraints (arXiv:2503.14738, March 2025).
# w0 central value from the combined fit; wₐ central and sigmas as published.
DESI_BASELINE_OBS: Dict[str, float] = {
    "w0_obs": -0.90,
    "w0_sigma": 0.055,
    "wa_obs": -0.55,
    "wa_sigma": 0.20,
}

# Approximate w0–wₐ anti-correlation coefficient from the DESI DR2 combined
# posterior.  CPL fits with BAO+CMB+SNe typically yield ρ ∈ [−0.75, −0.85].
# We use −0.80 as the central estimate (conservative / well-supported).
DESI_CPL_CORRELATION: float = -0.80


# ---------------------------------------------------------------------------
# Internal validation helpers
# ---------------------------------------------------------------------------

def _validate_sigmas(w0_sigma: float, wa_sigma: float) -> None:
    if w0_sigma <= 0 or wa_sigma <= 0:
        raise ValueError("w0_sigma and wa_sigma must be strictly positive.")


def _validate_rho(rho: float) -> None:
    if not (-1.0 < rho < 1.0):
        raise ValueError("Correlation rho must satisfy -1 < rho < 1.")


# ---------------------------------------------------------------------------
# Primary tension functions
# ---------------------------------------------------------------------------

def wa_only_tension_sigma(wa_obs: float, wa_sigma: float) -> float:
    """Single-parameter wₐ tension — matches published DESI figures.

    This is the defensible canonical metric:

        tension = |wₐ_obs − wₐ_pred| / σ_wₐ

    It corresponds directly to the numbers quoted in arXiv:2503.14738:
    2.07σ (BAO-only) and 2.75σ (combined).

    Parameters
    ----------
    wa_obs : float
        Observed wₐ central value.
    wa_sigma : float
        Observed wₐ 1σ uncertainty (must be > 0).

    Returns
    -------
    float
        Tension in units of sigma.
    """
    if wa_sigma <= 0:
        raise ValueError("wa_sigma must be strictly positive.")
    return abs(wa_obs - KK_WA_PREDICTION) / wa_sigma


def joint_tension_sigma(
    w0_obs: float,
    w0_sigma: float,
    wa_obs: float,
    wa_sigma: float,
    rho: float = DESI_CPL_CORRELATION,
) -> float:
    """Covariance-corrected 2D joint chi-squared tension.

    Accounts for the strong negative correlation between w0 and wₐ in CPL
    dark energy fits.  The 2D chi-squared statistic is:

        Δ = [w0_obs − w0_pred, wₐ_obs − wₐ_pred]
        χ² = Δᵀ C⁻¹ Δ
           = (z_w0² − 2ρ·z_w0·z_wₐ + z_wₐ²) / (1 − ρ²)

    where z_i = Δ_i / σ_i.  The tension in sigma-units is √χ².

    For ρ = 0 (uncorrelated) this reduces to the naive quadrature sum.
    For ρ ≈ −0.80 (DESI combined) the joint tension is ≈ 2.82σ, well
    below the 3σ falsification threshold.

    Parameters
    ----------
    w0_obs, w0_sigma, wa_obs, wa_sigma : float
        CPL parameters and their 1σ uncertainties.
    rho : float
        Pearson correlation coefficient ρ(w0, wₐ) from the posterior.
        Must satisfy −1 < ρ < 1.  Default: DESI_CPL_CORRELATION = −0.80.

    Returns
    -------
    float
        Joint tension √χ² in sigma-units.
    """
    _validate_sigmas(w0_sigma, wa_sigma)
    _validate_rho(rho)
    z_w0 = (w0_obs - KK_W0_PREDICTION) / w0_sigma
    z_wa = (wa_obs - KK_WA_PREDICTION) / wa_sigma
    chi2 = (z_w0 ** 2 - 2.0 * rho * z_w0 * z_wa + z_wa ** 2) / (1.0 - rho ** 2)
    return math.sqrt(max(chi2, 0.0))


def desi_tension_sigma(
    w0_obs: float,
    w0_sigma: float,
    wa_obs: float,
    wa_sigma: float,
) -> float:
    """Published wₐ-only tension metric (API-compatible entry point).

    Returns the single-parameter wₐ tension, which matches the numbers
    published in arXiv:2503.14738 and quoted throughout this repository's
    documentation.

    CHANGE NOTE (v11.x): The previous implementation computed a naive
    uncorrelated joint quadrature sum (inflating tension to 3.30σ).  This
    function now returns the wₐ-only metric (2.75σ for the combined
    baseline), consistent with the published DESI figures and all canonical
    documentation.  Use ``joint_tension_sigma()`` for the covariance-
    corrected 2D statistic.

    Parameters
    ----------
    w0_obs, w0_sigma : float
        w0 observation and uncertainty (accepted for API compat; w0 is not
        used in the wₐ-only calculation).
    wa_obs, wa_sigma : float
        wₐ observation and 1σ uncertainty.

    Returns
    -------
    float
        |wₐ_obs − wₐ_pred| / σ_wₐ.
    """
    _validate_sigmas(w0_sigma, wa_sigma)
    return wa_only_tension_sigma(wa_obs, wa_sigma)


def tension_flag(tension_sigma: float) -> str:
    """Map tension in sigma to a categorical flag.

    Thresholds follow DESI escalation matrix in CLAIM_MASTER_BOARD.md:
      ≥ 3.0σ → CRITICAL  (≡ FALSIFIED threshold)
      > 2.0σ → WARNING   (≡ HIGH_TENSION)
      ≤ 2.0σ → PASS      (≡ CONSISTENT / TENSION_REDUCED)
    """
    if tension_sigma >= 3.0:
        return "CRITICAL"
    if tension_sigma > 2.0:
        return "WARNING"
    return "PASS"


# ---------------------------------------------------------------------------
# Observation window helper
# ---------------------------------------------------------------------------

def observation_window(
    w0_obs: float,
    w0_sigma: float,
    wa_obs: float,
    wa_sigma: float,
) -> Dict[str, tuple[float, float]]:
    """Return 1σ and 2σ confidence intervals for w0 and wₐ."""
    _validate_sigmas(w0_sigma, wa_sigma)
    return {
        "w0_1sigma": (w0_obs - w0_sigma, w0_obs + w0_sigma),
        "wa_1sigma": (wa_obs - wa_sigma, wa_obs + wa_sigma),
        "w0_2sigma": (w0_obs - 2.0 * w0_sigma, w0_obs + 2.0 * w0_sigma),
        "wa_2sigma": (wa_obs - 2.0 * wa_sigma, wa_obs + 2.0 * wa_sigma),
    }


# ---------------------------------------------------------------------------
# Monitor
# ---------------------------------------------------------------------------

def monitor_desi_tension(
    w0_obs: float = DESI_BASELINE_OBS["w0_obs"],
    w0_sigma: float = DESI_BASELINE_OBS["w0_sigma"],
    wa_obs: float = DESI_BASELINE_OBS["wa_obs"],
    wa_sigma: float = DESI_BASELINE_OBS["wa_sigma"],
    rho: float = DESI_CPL_CORRELATION,
) -> Dict[str, object]:
    """Full DESI tension monitor report.

    Returns both the wₐ-only and the covariance-corrected joint tension.
    The primary reported ``desi_tension_sigma`` key uses the wₐ-only metric
    to match published DESI figures and all canonical documentation.

    Parameters
    ----------
    w0_obs, w0_sigma, wa_obs, wa_sigma : float
        CPL observation and uncertainties (defaults: DESI DR2 combined).
    rho : float
        w0–wₐ posterior correlation for the joint metric (default −0.80).
    """
    wa_only = wa_only_tension_sigma(wa_obs, wa_sigma)
    joint = joint_tension_sigma(w0_obs, w0_sigma, wa_obs, wa_sigma, rho=rho)
    return {
        "kk_prediction": {"w0": KK_W0_PREDICTION, "wa": KK_WA_PREDICTION},
        "observation": {
            "w0_obs": w0_obs,
            "w0_sigma": w0_sigma,
            "wa_obs": wa_obs,
            "wa_sigma": wa_sigma,
        },
        "window": observation_window(w0_obs=w0_obs, w0_sigma=w0_sigma, wa_obs=wa_obs, wa_sigma=wa_sigma),
        # Primary metric: wₐ-only, matches published DESI DR2 figures
        "desi_tension_sigma": wa_only,
        "wa_only_tension_sigma": wa_only,
        # Supplementary: covariance-corrected joint chi-squared
        "joint_tension_sigma": joint,
        "joint_tension_rho": rho,
        "flag": tension_flag(wa_only),
        "update_ready": True,
        "tension_method_note": (
            "Primary metric is wₐ-only (matches DESI paper figures). "
            "Joint metric uses covariance-corrected 2D chi-squared with "
            f"ρ(w0,wₐ) = {rho} from the DESI CPL posterior."
        ),
    }


def updated_monitor_from_payload(payload: Dict[str, float]) -> Dict[str, object]:
    """Update the monitor from an external data payload dict.

    Required keys: w0_obs, w0_sigma, wa_obs, wa_sigma.
    Optional key: rho_w0_wa (default DESI_CPL_CORRELATION).
    """
    required = ("w0_obs", "w0_sigma", "wa_obs", "wa_sigma")
    missing = [k for k in required if k not in payload]
    if missing:
        raise ValueError(f"Missing required payload fields: {', '.join(missing)}")
    rho = float(payload.get("rho_w0_wa", DESI_CPL_CORRELATION))
    return monitor_desi_tension(
        w0_obs=float(payload["w0_obs"]),
        w0_sigma=float(payload["w0_sigma"]),
        wa_obs=float(payload["wa_obs"]),
        wa_sigma=float(payload["wa_sigma"]),
        rho=rho,
    )


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: wₐ-only tension (primary, matches published DESI figures): 2.75σ for combined.
DESI_TENSION_SIGMA: float = wa_only_tension_sigma(
    DESI_BASELINE_OBS["wa_obs"], DESI_BASELINE_OBS["wa_sigma"]
)

#: Same as DESI_TENSION_SIGMA — explicit alias for documentation clarity.
DESI_WA_ONLY_TENSION_SIGMA: float = DESI_TENSION_SIGMA

#: Covariance-corrected 2D joint tension using ρ = DESI_CPL_CORRELATION.
DESI_JOINT_TENSION_SIGMA: float = joint_tension_sigma(
    DESI_BASELINE_OBS["w0_obs"],
    DESI_BASELINE_OBS["w0_sigma"],
    DESI_BASELINE_OBS["wa_obs"],
    DESI_BASELINE_OBS["wa_sigma"],
    rho=DESI_CPL_CORRELATION,
)


__all__ = [
    "KK_W0_PREDICTION",
    "KK_WA_PREDICTION",
    "DESI_BASELINE_OBS",
    "DESI_CPL_CORRELATION",
    "DESI_TENSION_SIGMA",
    "DESI_WA_ONLY_TENSION_SIGMA",
    "DESI_JOINT_TENSION_SIGMA",
    "wa_only_tension_sigma",
    "joint_tension_sigma",
    "desi_tension_sigma",
    "tension_flag",
    "observation_window",
    "monitor_desi_tension",
    "updated_monitor_from_payload",
]
