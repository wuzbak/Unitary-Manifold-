# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
realworld/prediction_impact.py
===============================
Answers the question: **do real-world observed values change the Unitary
Manifold's initial predictions, and by how much?**

The framework's Earth-system functions are normalised to pre-industrial
reference conditions (CO₂ = 280 ppm, CH₄ = 722 ppb, ΔT = 0 °C above
14 °C baseline, neutral ENSO).  When April 2026 observed values are
substituted, the framework outputs shift.  This module quantifies those
shifts and classifies them as ``significant`` (|shift| > 10 % of the
reference-condition output magnitude, or a qualitative phase change) or
``negligible``.

Usage
-----
    from realworld.prediction_impact import impact_report, impact_summary
    report = impact_report()            # uses snapshot (offline-safe)
    print(impact_summary(report))

Or from the CLI::

    python realworld/live_report.py --impact

Theory and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""

from __future__ import annotations

import sys
import pathlib
from typing import Any

# Allow import when run as a script from any working directory
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

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
# Pre-industrial / reference baseline constants
# ---------------------------------------------------------------------------
_CO2_REF_PPM = 280.0      # ppm — IPCC AR6 pre-industrial
_CH4_REF_PPB = 722.0      # ppb — IPCC AR6 pre-industrial
_T_BASE_C = 14.0          # °C  — 1951-1980 global mean surface T
_DELTA_T_REF = 0.0        # °C  — no anomaly at reference epoch
_PHI_PACIFIC_REF = 1.0    # dimensionless — neutral ENSO
_B_IGRF_NT = 25_000.0     # nT  — IGRF-13 mean surface dipole field

# Physical constants
_SIGMA_CORE = 5e5          # S/m
_RHO_CORE = 1.1e4          # kg/m³
_OMEGA_EARTH = 7.29e-5     # rad/s

_SIGNIFICANCE_THRESHOLD = 0.10  # 10 %


def _significance(reference: float, shifted: float) -> str:
    """Classify the prediction shift as 'significant' or 'negligible'."""
    if abs(reference) < 1e-12:
        return "significant" if abs(shifted) > 1e-9 else "negligible"
    frac = abs(shifted - reference) / abs(reference)
    return "significant" if frac > _SIGNIFICANCE_THRESHOLD else "negligible"


def _impact_entry(
    metric: str,
    reference_val: float,
    observed_val: float,
    unit: str = "",
) -> dict[str, Any]:
    shift = observed_val - reference_val
    return {
        "metric": metric,
        "unit": unit,
        "reference_prediction": round(reference_val, 6),
        "april2026_prediction": round(observed_val, 6),
        "shift": round(shift, 6),
        "significance": _significance(reference_val, observed_val),
    }


def impact_report(live: bool = False) -> list[dict[str, Any]]:
    """Compute prediction shifts from pre-industrial → April 2026 observed.

    Each entry in the returned list describes one framework metric,
    containing:

    * ``metric``               — human-readable metric name
    * ``unit``                 — physical unit string
    * ``reference_prediction`` — framework output at pre-industrial baseline
    * ``april2026_prediction`` — framework output with April 2026 data
    * ``shift``                — ``april2026 − reference``
    * ``significance``         — ``"significant"`` or ``"negligible"``

    Parameters
    ----------
    live : bool
        When ``True`` attempt live API calls; falls back to snapshot.

    Returns
    -------
    list[dict]
    """
    entries: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Fetch April 2026 observed values
    # ------------------------------------------------------------------
    co2_data = _co2.fetch(live=live)
    co2_obs = co2_data["co2_ppm"]

    ch4_data = _ch4.fetch(live=live)
    ch4_obs = ch4_data["ch4_ppb"]

    met_data = _met.fetch(live=live)
    delta_T_obs = met_data["delta_T_C"]

    enso_data = _enso.fetch(live=live)
    nino34_obs = enso_data["nino34_anomaly_C"]

    swpc_data = _swpc.fetch(live=live)
    B_obs_nT = swpc_data["B_nT"]

    # ------------------------------------------------------------------
    # 1. CO₂ radiative forcing  (W m⁻²)
    # ------------------------------------------------------------------
    f_co2_ref = co2_forcing(0.0)
    f_co2_obs = co2_forcing(co2_obs - _CO2_REF_PPM)
    entries.append(_impact_entry(
        "co2_radiative_forcing", f_co2_ref, f_co2_obs, "W/m²"
    ))

    # ------------------------------------------------------------------
    # 2. CH₄ forcing  (W m⁻²)
    # ------------------------------------------------------------------
    f_ch4_ref = methane_phi_forcing(_CH4_REF_PPB)
    f_ch4_obs = methane_phi_forcing(ch4_obs)
    entries.append(_impact_entry(
        "ch4_forcing", f_ch4_ref, f_ch4_obs, "W/m²"
    ))

    # ------------------------------------------------------------------
    # 3. Committed equilibrium ΔT  (°C)
    # ------------------------------------------------------------------
    dT_ref = equilibrium_temperature_shift(f_co2_ref + f_ch4_ref)
    dT_obs_pred = equilibrium_temperature_shift(f_co2_obs + f_ch4_obs)
    entries.append(_impact_entry(
        "committed_equilibrium_delta_T", dT_ref, dT_obs_pred, "°C"
    ))

    # ------------------------------------------------------------------
    # 4. CO₂ φ — greenhouse forcing  (dimensionless)
    # ------------------------------------------------------------------
    phi_ghg_ref = greenhouse_forcing_phi(_CO2_REF_PPM)
    phi_ghg_obs = greenhouse_forcing_phi(co2_obs)
    entries.append(_impact_entry(
        "co2_greenhouse_phi", phi_ghg_ref, phi_ghg_obs, "φ"
    ))

    # ------------------------------------------------------------------
    # 5. CO₂ φ — atmospheric carbon  (dimensionless)
    # ------------------------------------------------------------------
    phi_co2atm_ref = atmospheric_co2_phi(_CO2_REF_PPM)
    phi_co2atm_obs = atmospheric_co2_phi(co2_obs)
    entries.append(_impact_entry(
        "co2_atmospheric_phi", phi_co2atm_ref, phi_co2atm_obs, "φ"
    ))

    # ------------------------------------------------------------------
    # 6. Surface temperature anomaly φ  (dimensionless)
    # ------------------------------------------------------------------
    phi_T_ref = temperature_phi_anomaly(_T_BASE_C + _DELTA_T_REF, _T_BASE_C)
    phi_T_obs = temperature_phi_anomaly(_T_BASE_C + delta_T_obs, _T_BASE_C)
    entries.append(_impact_entry(
        "surface_T_phi", phi_T_ref, phi_T_obs, "φ"
    ))

    # ------------------------------------------------------------------
    # 7. ENSO phase  (qualitative — separate entry)
    # ------------------------------------------------------------------
    enso_ref = enso_phase(_PHI_PACIFIC_REF)
    phi_pacific_obs = 1.0 + nino34_obs / 2.0
    enso_obs = enso_phase(phi_pacific_obs)
    phase_changed = enso_ref != enso_obs
    entries.append({
        "metric": "enso_phase",
        "unit": "phase",
        "reference_prediction": enso_ref,
        "april2026_prediction": enso_obs,
        "shift": "changed" if phase_changed else "unchanged",
        "significance": "significant" if phase_changed else "negligible",
    })

    # ------------------------------------------------------------------
    # 8. Elsasser number Λ  (dimensionless)
    # ------------------------------------------------------------------
    B_ref_T = _B_IGRF_NT * 1e-9
    B_obs_T = B_obs_nT * 1e-9
    lam_ref = elsasser_number(_SIGMA_CORE, B_ref_T, _RHO_CORE, _OMEGA_EARTH)
    lam_obs = elsasser_number(_SIGMA_CORE, B_obs_T, _RHO_CORE, _OMEGA_EARTH)
    entries.append(_impact_entry(
        "elsasser_lambda", lam_ref, lam_obs, "Λ"
    ))

    return entries


def impact_summary(entries: list[dict[str, Any]]) -> str:
    """Return a formatted table of prediction impact entries.

    Parameters
    ----------
    entries : list[dict] — output of ``impact_report()``

    Returns
    -------
    str — multi-line table
    """
    lines = [
        "=" * 80,
        "  PREDICTION IMPACT: Pre-industrial Reference → April 2026 Observed",
        "=" * 80,
        f"{'Metric':<35}{'Reference':>12}{'Apr 2026':>12}{'Shift':>12}{'Impact':>10}",
        "-" * 80,
    ]
    for e in entries:
        ref = e["reference_prediction"]
        apr = e["april2026_prediction"]
        shift = e["shift"]
        sig = e["significance"]

        if isinstance(ref, float):
            lines.append(
                f"{e['metric']:<35}"
                f"{ref:>12.4f}"
                f"{apr:>12.4f}"
                f"{shift:>+12.4f}"
                f"{sig:>10}"
            )
        else:
            lines.append(
                f"{e['metric']:<35}"
                f"{str(ref):>12}"
                f"{str(apr):>12}"
                f"{str(shift):>12}"
                f"{sig:>10}"
            )

    lines.append("=" * 80)

    sig_count = sum(1 for e in entries if e["significance"] == "significant")
    lines.append(
        f"\n  {sig_count}/{len(entries)} metrics show SIGNIFICANT shifts "
        f"(>10% change from pre-industrial baseline)."
    )

    return "\n".join(lines)
