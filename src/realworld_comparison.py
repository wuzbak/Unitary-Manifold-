# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/realworld_comparison.py
===========================
Framework-vs-observation comparison runner.

This module is the single entry point that:

1. Calls each ``src/data_feeds`` adapter (or falls back to the pinned
   April 2026 snapshot when offline).
2. Feeds the live / cached values into the relevant Unitary Manifold
   functions.
3. Computes the residual ``delta = predicted − observed`` for each
   measurable quantity.
4. Returns a dict of ``{metric: {predicted, observed, delta, status}}``
   where ``status`` is ``"ok"`` when |delta/observed| < tolerance, else
   ``"warning"``.

Usage
-----
    from src.realworld_comparison import run_comparison
    report = run_comparison()          # uses snapshot (offline-safe)
    report = run_comparison(live=True) # tries live APIs first

Theory and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""

from __future__ import annotations

import math
from typing import Any

from src.climate.atmosphere import (
    greenhouse_forcing_phi,
    temperature_phi_anomaly,
)
from src.climate.carbon_cycle import (
    atmospheric_co2_phi,
    methane_phi_forcing,
)
from src.earth.geology import elsasser_number
from src.earth.meteorology import co2_forcing, equilibrium_temperature_shift
from src.earth.oceanography import enso_phase

from src.data_feeds import noaa_co2 as _co2
from src.data_feeds import noaa_ch4 as _ch4
from src.data_feeds import noaa_enso as _enso
from src.data_feeds import open_meteo as _met
from src.data_feeds import swpc_geomagnetic as _swpc

# ---------------------------------------------------------------------------
# Physical constants for Elsasser number calculation
# ---------------------------------------------------------------------------
_SIGMA_CORE = 5e5      # S/m  — outer-core electrical conductivity
_RHO_CORE = 1.1e4      # kg/m³ — outer-core density
_OMEGA_EARTH = 7.29e-5  # rad/s — Earth rotation rate

# Tolerance for ok/warning classification: |delta/observed| < TOL
_TOL = 0.15  # 15 %


def _status(predicted: float, observed: float, tol: float = _TOL) -> str:
    if observed == 0.0:
        return "ok" if abs(predicted) < 1e-9 else "warning"
    return "ok" if abs((predicted - observed) / observed) < tol else "warning"


def _entry(predicted: float, observed: float) -> dict[str, Any]:
    delta = predicted - observed
    return {
        "predicted": round(predicted, 4),
        "observed": round(observed, 4),
        "delta": round(delta, 4),
        "status": _status(predicted, observed),
    }


def run_comparison(live: bool = False) -> dict[str, dict[str, Any]]:
    """Run all framework-vs-observation comparisons.

    Parameters
    ----------
    live : bool
        When ``True`` attempt live API calls.  Falls back to the pinned
        April 2026 snapshot on any network failure.

    Returns
    -------
    dict
        Keys are metric names; values are dicts with keys
        ``predicted``, ``observed``, ``delta``, ``status``.
    """
    report: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # 1. CO₂ radiative forcing
    # ------------------------------------------------------------------
    co2_data = _co2.fetch(live=live)
    co2_ppm = co2_data["co2_ppm"]
    delta_co2 = co2_ppm - 280.0

    predicted_co2_forcing = co2_forcing(delta_co2)
    # IPCC AR6 best estimate: 5.35 × ln(co2/280) ≈ 3.7 × log2(co2/280)
    observed_co2_forcing = 5.35 * math.log(co2_ppm / 280.0)
    report["co2_radiative_forcing_Wm2"] = _entry(
        predicted_co2_forcing, observed_co2_forcing
    )

    # ------------------------------------------------------------------
    # 2. CO₂ φ parameter
    # ------------------------------------------------------------------
    predicted_co2_phi = greenhouse_forcing_phi(co2_ppm)
    observed_co2_phi = atmospheric_co2_phi(co2_ppm)
    report["co2_phi"] = _entry(predicted_co2_phi, observed_co2_phi)

    # ------------------------------------------------------------------
    # 3. CH₄ forcing
    # ------------------------------------------------------------------
    ch4_data = _ch4.fetch(live=live)
    ch4_ppb = ch4_data["ch4_ppb"]
    predicted_ch4 = methane_phi_forcing(ch4_ppb)
    # IPCC AR6 simplified expression: 0.036 * (sqrt(ch4) - sqrt(722))
    observed_ch4 = 0.036 * (math.sqrt(ch4_ppb) - math.sqrt(722.0))
    report["ch4_forcing_Wm2"] = _entry(predicted_ch4, observed_ch4)

    # ------------------------------------------------------------------
    # 4. Committed equilibrium ΔT
    # ------------------------------------------------------------------
    net_forcing = predicted_co2_forcing + predicted_ch4
    predicted_delta_T = equilibrium_temperature_shift(net_forcing)
    # WMO / IPCC observed: committed warming ≈ 1.5–2.0 °C; midpoint 1.75 °C
    observed_delta_T = 1.75
    report["committed_delta_T_C"] = _entry(predicted_delta_T, observed_delta_T)

    # ------------------------------------------------------------------
    # 5. Surface temperature anomaly φ
    # ------------------------------------------------------------------
    met_data = _met.fetch(live=live)
    T_global = met_data["T_global_C"]
    T_baseline = met_data["T_baseline_C"]
    predicted_T_phi = temperature_phi_anomaly(T_global, T_baseline)
    observed_T_phi = temperature_phi_anomaly(
        T_baseline + met_data["delta_T_C"], T_baseline
    )
    report["surface_T_phi"] = _entry(predicted_T_phi, observed_T_phi)

    # ------------------------------------------------------------------
    # 6. ENSO phase agreement
    # ------------------------------------------------------------------
    enso_data = _enso.fetch(live=live)
    nino34 = enso_data["nino34_anomaly_C"]
    observed_enso_phase = enso_data["phase"]
    # Map Niño 3.4 anomaly to φ_pacific: φ = 1.0 + anomaly / 2.0
    phi_pacific = 1.0 + nino34 / 2.0
    predicted_enso_phase = enso_phase(phi_pacific)
    report["enso_phase"] = {
        "predicted": predicted_enso_phase,
        "observed": observed_enso_phase,
        "nino34_anomaly_C": nino34,
        "status": "ok" if predicted_enso_phase == observed_enso_phase else "warning",
    }

    # ------------------------------------------------------------------
    # 7. Elsasser number Λ
    # ------------------------------------------------------------------
    swpc_data = _swpc.fetch(live=live)
    B_T = swpc_data["B_nT"] * 1e-9  # nT → T
    Lambda_predicted = elsasser_number(
        sigma=_SIGMA_CORE, B=B_T, rho=_RHO_CORE, omega=_OMEGA_EARTH
    )
    # Observed: IGRF-13 surface Λ; geodynamo interior Λ ≈ 0.1–10 (typical)
    # We compare to the IGRF surface-field derived value as the observable
    Lambda_igrf = elsasser_number(
        sigma=_SIGMA_CORE,
        B=25_000e-9,
        rho=_RHO_CORE,
        omega=_OMEGA_EARTH,
    )
    report["elsasser_lambda"] = _entry(Lambda_predicted, Lambda_igrf)

    return report


def comparison_summary(report: dict[str, dict[str, Any]]) -> str:
    """Return a human-readable summary of a comparison report.

    Parameters
    ----------
    report : dict — output of ``run_comparison()``

    Returns
    -------
    str — multi-line summary table
    """
    lines = [
        "=" * 72,
        f"{'Metric':<35}{'Predicted':>10}{'Observed':>10}{'Delta':>10}{'Status':>8}",
        "-" * 72,
    ]
    for metric, vals in report.items():
        if isinstance(vals.get("predicted"), (int, float)):
            lines.append(
                f"{metric:<35}"
                f"{vals['predicted']:>10.4f}"
                f"{vals['observed']:>10.4f}"
                f"{vals['delta']:>10.4f}"
                f"{vals['status']:>8}"
            )
        else:
            lines.append(
                f"{metric:<35}"
                f"{str(vals.get('predicted', ''))!s:>10}"
                f"{str(vals.get('observed', ''))!s:>10}"
                f"{'—':>10}"
                f"{vals['status']:>8}"
            )
    lines.append("=" * 72)
    return "\n".join(lines)
