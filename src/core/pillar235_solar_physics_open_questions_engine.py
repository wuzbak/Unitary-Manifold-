# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 235 — Solar Physics Open Questions Engine (2026).

Adjacent applied research track (non-hardgate): this module provides a
quantitative, falsifiable synthesis framework for 12 major open solar-physics
questions. It does not claim these questions are solved by theory alone; it
provides deterministic diagnostics, simulation hooks, and explicit falsification
conditions that can be tested against observations.

🔵 ADJACENT TRACK — This module does NOT affect the Unitary Manifold ToE score.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

__provenance__ = {
    "pillar": 235,
    "title": "Solar Physics Open Questions Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — quantitative diagnostics and simulations "
        "for 12 open solar-physics questions; no claim of final closure"
    ),
}

__all__ = [
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "SOLAR_CONSTANT_W_M2",
    "STEFAN_BOLTZMANN",
    "SolarObservables",
    "solar_observables_reference",
    "question_diagnostics",
    "solar_question_portfolio",
    "monte_carlo_question_stability",
    "pillar235_solar_open_questions_report",
]

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

SOLAR_CONSTANT_W_M2: float = 1361.0
STEFAN_BOLTZMANN: float = 5.670374419e-8
EPSILON_MINIMUM: float = 1e-12


@dataclass(frozen=True)
class SolarObservables:
    """Minimal observational profile used by Pillar 235 diagnostics."""

    photosphere_temp_k: float = 5772.0
    corona_temp_k: float = 1_200_000.0
    alfven_speed_kms: float = 800.0
    alfven_damping_fraction: float = 0.55

    magnetic_reynolds_number: float = 1.0e8
    tachocline_shear: float = 0.25

    slow_wind_speed_kms: float = 420.0
    fast_wind_speed_kms: float = 760.0

    reconnection_rate: float = 0.12

    north_pole_temp_k: float = 1_130_000.0
    south_pole_temp_k: float = 1_050_000.0

    core_rotation_uniformity: float = 0.85

    surface_metallicity_z: float = 0.0134
    helioseismic_metallicity_z: float = 0.0172

    young_sun_luminosity_fraction: float = 0.70
    greenhouse_forcing_wm2: float = 78.0

    sep_shock_mach: float = 3.5
    sep_observed_spectral_index: float = 2.35

    cycle_variability_index: float = 0.32

    ibex_ribbon_alignment_deg: float = 84.0
    interstellar_field_nt: float = 0.45


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _validate(obs: SolarObservables) -> None:
    if obs.photosphere_temp_k <= 0 or obs.corona_temp_k <= 0:
        raise ValueError("Temperatures must be positive.")
    if obs.fast_wind_speed_kms <= 0 or obs.slow_wind_speed_kms <= 0:
        raise ValueError("Wind speeds must be positive.")
    if obs.magnetic_reynolds_number <= 0:
        raise ValueError("magnetic_reynolds_number must be > 0.")
    if not (0 <= obs.alfven_damping_fraction <= 1):
        raise ValueError("alfven_damping_fraction must be in [0, 1].")
    if not (0 <= obs.reconnection_rate <= 1):
        raise ValueError("reconnection_rate must be in [0, 1].")
    if not (0 <= obs.core_rotation_uniformity <= 1):
        raise ValueError("core_rotation_uniformity must be in [0, 1].")
    if obs.young_sun_luminosity_fraction <= 0:
        raise ValueError("young_sun_luminosity_fraction must be > 0.")
    if obs.sep_shock_mach <= 1:
        raise ValueError("sep_shock_mach must be > 1 for shock acceleration.")


def solar_observables_reference() -> SolarObservables:
    """Return the canonical Pillar 235 baseline profile."""
    return SolarObservables()


def _coronal_heating(obs: SolarObservables) -> dict[str, Any]:
    temp_ratio = obs.corona_temp_k / obs.photosphere_temp_k
    boltzmann_flux_ratio = (obs.corona_temp_k / obs.photosphere_temp_k) ** 4
    transport_efficiency = _clamp01(
        obs.alfven_damping_fraction * (obs.alfven_speed_kms / 1000.0)
    )
    closure = _clamp01(transport_efficiency / max(math.log10(temp_ratio), 1e-9))
    return {
        "question": "Coronal heating problem",
        "diagnostic": {
            "temp_ratio": temp_ratio,
            "radiative_flux_ratio": boltzmann_flux_ratio,
            "alfven_transport_efficiency": transport_efficiency,
            "closure_score": closure,
        },
        "derived_solution": (
            "Combined Alfvén-wave damping + bursty reconnection heating can plausibly "
            "close the energy gap when transport efficiency exceeds log-temperature demand."
        ),
        "epistemic_status": "CALCULATED diagnostic; mechanism remains EMPIRICAL/SPECULATIVE.",
        "falsification_condition": (
            "If measured wave/reconnection energy deposition remains below required coronal "
            "heating flux across heliocentric radii, this pathway is rejected."
        ),
    }


def _solar_dynamo(obs: SolarObservables) -> dict[str, Any]:
    dynamo_number = obs.tachocline_shear * math.sqrt(obs.magnetic_reynolds_number)
    cycle_lock = _clamp01(math.tanh(dynamo_number / 2_000.0))
    closure = _clamp01(0.5 * cycle_lock + 0.5 * obs.core_rotation_uniformity)
    return {
        "question": "Internal mechanics of the solar dynamo",
        "diagnostic": {
            "dynamo_number": dynamo_number,
            "cycle_lock_index": cycle_lock,
            "closure_score": closure,
        },
        "derived_solution": (
            "A shear-amplified mean-field dynamo with tachocline memory can reproduce robust "
            "cycle locking when the effective dynamo number is sufficiently supercritical."
        ),
        "epistemic_status": "CALCULATED reduced-order diagnostic.",
        "falsification_condition": (
            "If observed cycle phase/amplitude evolution cannot be reproduced with measured "
            "tachocline shear and diffusivity constraints, this reduced model fails."
        ),
    }


def _slow_wind(obs: SolarObservables) -> dict[str, Any]:
    speed_contrast = _clamp01(1.0 - obs.slow_wind_speed_kms / obs.fast_wind_speed_kms)
    expansion_mixing = _clamp01(obs.tachocline_shear * obs.reconnection_rate * 4.0)
    closure = _clamp01(0.6 * speed_contrast + 0.4 * expansion_mixing)
    return {
        "question": "Origins of the slow solar wind",
        "diagnostic": {
            "slow_fast_speed_contrast": speed_contrast,
            "expansion_reconnection_mixing": expansion_mixing,
            "closure_score": closure,
        },
        "derived_solution": (
            "Slow wind is consistent with interchange-reconnection outflow from open-closed "
            "field boundaries plus super-radial expansion mixing."
        ),
        "epistemic_status": "CALCULATED routing metric; origin assignment remains EMPIRICAL.",
        "falsification_condition": (
            "If compositional and charge-state signatures exclude boundary-source plasma, "
            "the proposed source topology is incorrect."
        ),
    }


def _flare_cme_trigger(obs: SolarObservables) -> dict[str, Any]:
    nonpotential_index = _clamp01(obs.reconnection_rate * math.log10(obs.magnetic_reynolds_number) / 8.0)
    instability = _clamp01(nonpotential_index * (1.0 + obs.tachocline_shear))
    return {
        "question": "What triggers solar flares and CMEs",
        "diagnostic": {
            "nonpotential_index": nonpotential_index,
            "eruption_instability_index": instability,
            "closure_score": instability,
        },
        "derived_solution": (
            "Eruptions become likely when active-region free magnetic energy crosses a "
            "non-potentiality threshold and reconnection enters runaway topology change."
        ),
        "epistemic_status": "CALCULATED eruption-risk proxy.",
        "falsification_condition": (
            "If high-index regions systematically remain non-eruptive while low-index regions "
            "erupt, threshold reconnection trigger logic is invalid."
        ),
    }


def _polar_temperature(obs: SolarObservables) -> dict[str, Any]:
    delta = obs.north_pole_temp_k - obs.south_pole_temp_k
    asymmetry = abs(delta) / max((obs.north_pole_temp_k + obs.south_pole_temp_k) * 0.5, 1.0)
    persistent_asymmetry_index = _clamp01(asymmetry * (1.0 + 0.5 * obs.tachocline_shear))
    return {
        "question": "Why the solar poles have different temperatures",
        "diagnostic": {
            "north_minus_south_temp_k": delta,
            "fractional_polar_asymmetry": asymmetry,
            "closure_score": persistent_asymmetry_index,
        },
        "derived_solution": (
            "Long-lived hemispheric asymmetry is consistent with unequal meridional transport "
            "and asymmetric magnetic open-flux topology rather than cycle-phase noise alone."
        ),
        "epistemic_status": "CALCULATED asymmetry quantification.",
        "falsification_condition": (
            "If hemispheric asymmetry vanishes after robust instrument cross-calibration, "
            "the proposed physical asymmetry driver is unsupported."
        ),
    }


def _core_rotation(obs: SolarObservables) -> dict[str, Any]:
    tachocline_coupling = _clamp01(obs.core_rotation_uniformity * (1.0 - 0.5 * obs.tachocline_shear))
    neutrino_constraint = _clamp01(1.0 - abs(0.85 - obs.core_rotation_uniformity))
    closure = _clamp01(0.5 * tachocline_coupling + 0.5 * neutrino_constraint)
    return {
        "question": "Solar neutrino asymmetry and core rotation",
        "diagnostic": {
            "core_uniformity": obs.core_rotation_uniformity,
            "tachocline_coupling_index": tachocline_coupling,
            "closure_score": closure,
        },
        "derived_solution": (
            "A magneto-gravity-wave coupling channel can preserve near-solid-body core "
            "rotation while allowing differential rotation above the tachocline."
        ),
        "epistemic_status": "CALCULATED consistency metric.",
        "falsification_condition": (
            "If future helioseismic inversions require strong core differential rotation, "
            "this coupling explanation is rejected."
        ),
    }


def _metallicity(obs: SolarObservables) -> dict[str, Any]:
    frac_gap = abs(obs.surface_metallicity_z - obs.helioseismic_metallicity_z) / max(
        obs.helioseismic_metallicity_z, EPSILON_MINIMUM
    )
    diffusion_correction = _clamp01(1.0 - frac_gap)
    return {
        "question": "Solar abundance (metallicity) problem",
        "diagnostic": {
            "surface_z": obs.surface_metallicity_z,
            "helioseismic_z": obs.helioseismic_metallicity_z,
            "fractional_metallicity_gap": frac_gap,
            "closure_score": diffusion_correction,
        },
        "derived_solution": (
            "A combined opacity-revision + diffusion/mixing correction lane is favored when "
            "fractional metallicity gap is small enough for transport physics to close."
        ),
        "epistemic_status": "CALCULATED discrepancy metric.",
        "falsification_condition": (
            "If updated opacity and diffusion models still cannot reconcile surface and "
            "helioseismic constraints, an additional missing ingredient is required."
        ),
    }


def _faint_young_sun(obs: SolarObservables) -> dict[str, Any]:
    absorbed_today = SOLAR_CONSTANT_W_M2 * (1.0 - 0.3) / 4.0
    absorbed_then = absorbed_today * obs.young_sun_luminosity_fraction
    required_forcing = max(0.0, absorbed_today - absorbed_then)
    forcing_coverage = _clamp01(obs.greenhouse_forcing_wm2 / max(required_forcing, 1e-9))
    return {
        "question": "Faint young Sun paradox",
        "diagnostic": {
            "required_greenhouse_forcing_wm2": required_forcing,
            "provided_forcing_wm2": obs.greenhouse_forcing_wm2,
            "forcing_coverage_fraction": forcing_coverage,
            "closure_score": forcing_coverage,
        },
        "derived_solution": (
            "The paradox is closed only if greenhouse + cloud/albedo feedback forcing meets "
            "or exceeds the radiative deficit implied by reduced young-Sun luminosity."
        ),
        "epistemic_status": "CALCULATED energy-balance requirement.",
        "falsification_condition": (
            "If geochemical constraints cap forcing below required deficit compensation, "
            "the standard climate closure path is insufficient."
        ),
    }


def _alfven_acceleration(obs: SolarObservables) -> dict[str, Any]:
    acceleration_eff = _clamp01(obs.alfven_damping_fraction * obs.alfven_speed_kms / max(obs.fast_wind_speed_kms, 1e-9))
    closure = _clamp01(acceleration_eff)
    return {
        "question": "Mechanism behind Alfvén wave acceleration",
        "diagnostic": {
            "alfven_wave_acceleration_efficiency": acceleration_eff,
            "closure_score": closure,
        },
        "derived_solution": (
            "Wave-pressure plus turbulent cascade damping can explain substantial wind "
            "acceleration where measured dissipation efficiency is high."
        ),
        "epistemic_status": "CALCULATED acceleration proxy.",
        "falsification_condition": (
            "If in situ wave dissipation is too weak to account for observed momentum flux, "
            "Alfvén-dominant acceleration is incomplete."
        ),
    }


def _sep_acceleration(obs: SolarObservables) -> dict[str, Any]:
    gamma = 5.0 / 3.0
    m2 = obs.sep_shock_mach ** 2
    compression_ratio = ((gamma + 1.0) * m2) / ((gamma - 1.0) * m2 + 2.0)
    predicted_index = (compression_ratio + 2.0) / (compression_ratio - 1.0)
    mismatch = abs(predicted_index - obs.sep_observed_spectral_index)
    closure = _clamp01(1.0 - mismatch / 2.0)
    return {
        "question": "Particle acceleration in shock fronts (SEP events)",
        "diagnostic": {
            "shock_mach": obs.sep_shock_mach,
            "compression_ratio": compression_ratio,
            "predicted_spectral_index": predicted_index,
            "observed_spectral_index": obs.sep_observed_spectral_index,
            "spectral_mismatch": mismatch,
            "closure_score": closure,
        },
        "derived_solution": (
            "Diffusive shock acceleration remains viable when predicted and observed SEP "
            "spectral indices are close after transport corrections."
        ),
        "epistemic_status": "CALCULATED DSA consistency check.",
        "falsification_condition": (
            "If corrected spectra systematically disagree with DSA compression-ratio scaling, "
            "shock-only acceleration models are insufficient."
        ),
    }


def _grand_minima(obs: SolarObservables) -> dict[str, Any]:
    intermittency = _clamp01(obs.cycle_variability_index * (1.0 - obs.reconnection_rate + 0.5 * obs.tachocline_shear))
    grand_minimum_risk = _clamp01(intermittency)
    return {
        "question": "What causes grand minima (e.g., Maunder Minimum)",
        "diagnostic": {
            "cycle_variability_index": obs.cycle_variability_index,
            "intermittency_index": intermittency,
            "closure_score": grand_minimum_risk,
        },
        "derived_solution": (
            "Grand minima are consistent with intermittency in a near-threshold nonlinear dynamo "
            "where stochastic fluctuations can temporarily quench large-scale field regeneration."
        ),
        "epistemic_status": "CALCULATED dynamo-intermittency proxy.",
        "falsification_condition": (
            "If reconstructed activity records show minima inconsistent with stochastic-threshold "
            "dynamo statistics, this mechanism is incomplete."
        ),
    }


def _ibex_ribbon(obs: SolarObservables) -> dict[str, Any]:
    perpendicular_error = abs(90.0 - obs.ibex_ribbon_alignment_deg)
    geometry_match = _clamp01(1.0 - perpendicular_error / 45.0)
    b_field_plausibility = _clamp01(1.0 - abs(obs.interstellar_field_nt - 0.45) / 0.45)
    closure = _clamp01(0.7 * geometry_match + 0.3 * b_field_plausibility)
    return {
        "question": "Source of the IBEX ribbon",
        "diagnostic": {
            "alignment_to_perpendicular_deg": obs.ibex_ribbon_alignment_deg,
            "perpendicular_error_deg": perpendicular_error,
            "interstellar_field_nt": obs.interstellar_field_nt,
            "closure_score": closure,
        },
        "derived_solution": (
            "Ribbon emission is consistent with secondary ENA production organized by a local "
            "interstellar magnetic field nearly perpendicular to the heliocentric line of sight."
        ),
        "epistemic_status": "CALCULATED geometric consistency metric.",
        "falsification_condition": (
            "If future ENA maps break the perpendicularity relation to local interstellar B-field, "
            "the dominant ribbon-origin model must be revised."
        ),
    }


def question_diagnostics(observables: SolarObservables | None = None) -> list[dict[str, Any]]:
    """Return deterministic diagnostics for the 12 major solar open questions."""
    obs = observables if observables is not None else solar_observables_reference()
    _validate(obs)
    return [
        _coronal_heating(obs),
        _solar_dynamo(obs),
        _slow_wind(obs),
        _flare_cme_trigger(obs),
        _polar_temperature(obs),
        _core_rotation(obs),
        _metallicity(obs),
        _faint_young_sun(obs),
        _alfven_acceleration(obs),
        _sep_acceleration(obs),
        _grand_minima(obs),
        _ibex_ribbon(obs),
    ]


def solar_question_portfolio(observables: SolarObservables | None = None) -> dict[str, Any]:
    """Aggregate 12-question diagnostics into a summary portfolio."""
    rows = question_diagnostics(observables)
    scores = [float(r["diagnostic"]["closure_score"]) for r in rows]
    mean_score = float(np.mean(scores))
    median_score = float(np.median(scores))
    min_score = float(np.min(scores))
    weakest = rows[int(np.argmin(scores))]["question"]
    return {
        "n_questions": len(rows),
        "mean_closure_score": mean_score,
        "median_closure_score": median_score,
        "minimum_closure_score": min_score,
        "weakest_question": weakest,
        "status": "CALCULATED (deterministic multi-question aggregation)",
        "notes": (
            "Scores reflect model consistency with supplied observables; they are not claims "
            "that any solar mystery is fully solved."
        ),
    }


def monte_carlo_question_stability(
    observables: SolarObservables | None = None,
    samples: int = 250,
    relative_sigma: float = 0.05,
    seed: int = 235,
) -> dict[str, Any]:
    """Run uncertainty perturbation and report stability of closure scores."""
    if samples <= 0:
        raise ValueError("samples must be > 0")
    if relative_sigma < 0:
        raise ValueError("relative_sigma must be >= 0")

    base = observables if observables is not None else solar_observables_reference()
    _validate(base)

    rng = np.random.default_rng(seed)
    fields = list(base.__dataclass_fields__.keys())

    traces: dict[str, list[float]] = {}
    for _ in range(samples):
        values: dict[str, float] = {}
        for k in fields:
            v = float(getattr(base, k))
            sigma = max(abs(v) * relative_sigma, EPSILON_MINIMUM)
            sampled = float(rng.normal(v, sigma))
            if k in {"alfven_damping_fraction", "reconnection_rate", "core_rotation_uniformity"}:
                sampled = _clamp01(sampled)
            if k == "sep_shock_mach":
                sampled = max(sampled, 1.01)
            if k in {
                "photosphere_temp_k",
                "corona_temp_k",
                "alfven_speed_kms",
                "magnetic_reynolds_number",
                "slow_wind_speed_kms",
                "fast_wind_speed_kms",
                "north_pole_temp_k",
                "south_pole_temp_k",
                "surface_metallicity_z",
                "helioseismic_metallicity_z",
                "young_sun_luminosity_fraction",
                "cycle_variability_index",
                "interstellar_field_nt",
            }:
                sampled = max(sampled, 1e-9)
            values[k] = sampled

        obs_i = SolarObservables(**values)
        for row in question_diagnostics(obs_i):
            q = row["question"]
            traces.setdefault(q, []).append(float(row["diagnostic"]["closure_score"]))

    stability = {
        q: {
            "mean": float(np.mean(v)),
            "std": float(np.std(v)),
            "min": float(np.min(v)),
            "max": float(np.max(v)),
        }
        for q, v in traces.items()
    }

    return {
        "samples": samples,
        "relative_sigma": relative_sigma,
        "seed": seed,
        "per_question": stability,
        "status": "CALCULATED (Monte Carlo sensitivity on observational uncertainties)",
    }


def pillar235_solar_open_questions_report(
    observables: SolarObservables | None = None,
    samples: int = 250,
    relative_sigma: float = 0.05,
    seed: int = 235,
) -> dict[str, Any]:
    """Integrated Pillar 235 report: diagnostics + portfolio + uncertainty."""
    diagnostics = question_diagnostics(observables)
    portfolio = solar_question_portfolio(observables)
    stability = monte_carlo_question_stability(
        observables=observables,
        samples=samples,
        relative_sigma=relative_sigma,
        seed=seed,
    )
    return {
        "diagnostics": diagnostics,
        "portfolio": portfolio,
        "stability": stability,
        "status": (
            "ADJACENT-TRACK quantified synthesis for 12 solar open questions; "
            "falsifiable but not a claim of full closure"
        ),
        "falsification_condition": (
            "If diagnostics systematically fail against independent helioseismic, in-situ "
            "solar-wind, SEP, and ENA datasets, the proposed synthesis must be revised or rejected."
        ),
    }
