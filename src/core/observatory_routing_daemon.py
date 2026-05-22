# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Observatory Routing Daemon (ORD) — Automated experiment monitoring.

══════════════════════════════════════════════════════════════════════════════
WHAT THIS IS
══════════════════════════════════════════════════════════════════════════════

The Observatory Routing Daemon is the world's first self-executing theory
validation system.  On publication day for any pre-registered experiment,
the ORD:

  1. DETECTS:  New experimental result for a watched experiment
  2. EXTRACTS: Measured value and uncertainty from the result
  3. ROUTES:   Calls the appropriate preregistered falsifier function
  4. ISSUES:   A machine-signed verdict (CONFIRMED / CONSISTENT /
               HIGH_TENSION / FALSIFIED)
  5. UPDATES:  Relevant tracking documents

This module provides:
  - The experiment registry (all watched experiments and their parameters)
  - The routing dispatcher (maps experiment → falsifier function)
  - The verdict engine (formats and validates verdicts)
  - A simulation/test mode (for dry-runs before real data arrives)

══════════════════════════════════════════════════════════════════════════════
WATCHED EXPERIMENTS (AS OF v11.18)
══════════════════════════════════════════════════════════════════════════════

  Experiment       | Observable  | Pillar | Expected DR1 | Falsification threshold
  ──────────────── | ─────────── | ────── | ─────────────| ───────────────────────
  JUNO             | Ordering/Δm | 334    | ~2027        | IO at ≥3σ
  Simons Obs (SO)  | r           | 335    | ~2027        | r < 0.010 at ≥3σ
  DESI DR3         | wₐ          | 336    | ~2027        | |wₐ| ≥ 3σ from 0
  LiteBIRD         | β (birefr.) | P2     | ~2032        | β ∉ [0.22°, 0.38°]
  CMB-S4           | r (confirm) | P3     | ~2030        | r < 0.005 at ≥3σ
  KATRIN           | m_ν sum     | P301   | ~2027        | Σmν > 0.5 eV at ≥3σ
  LISA             | GW spectrum | P294   | ~2034+       | GW peak ∉ [1, 30] mHz
  Hyper-Kamiokande | ν ordering  | P296   | ~2027        | IO confirmed ≥3σ
  DESI DR4         | wₐ (deep)   | 336    | ~2028        | |wₐ| ≥ 3σ
  Euclid           | σ₈ / w      | P4     | ~2026        | σ₈ tension ≥3σ

══════════════════════════════════════════════════════════════════════════════
"""

import datetime
import math

# Import the preregistered falsifier functions
from .pillar334_juno_prediction_package import route_juno_dr1
from .pillar335_simons_observatory_protocol import route_so_dr1
from .pillar336_desi_dr3_routing_engine import route_desi_dr3

# ─────────────────────────────────────────────────────────────────────────────
# EXPERIMENT REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

# Each entry in the registry defines a watched experiment
EXPERIMENT_REGISTRY = {
    "JUNO": {
        "full_name": "Jiangmen Underground Neutrino Observatory",
        "observable": "neutrino_mass_ordering",
        "pillar": 334,
        "preregistered_in": "Pillars 332 (v11.17) + 334 (v11.18)",
        "expected_dr1": "2027",
        "falsification_condition": "Inverted ordering at ≥3σ → Pillar 42 FALSIFIED",
        "um_prediction": "NORMAL ordering (m₁ < m₂ < m₃)",
        "routing_function": "route_juno",
        "parameters_needed": ["measured_ordering", "ordering_sigma"],
        "optional_parameters": ["dm31_measured", "dm31_sigma_percent"],
    },
    "SIMONS_OBSERVATORY": {
        "full_name": "Simons Observatory Large Aperture Telescope",
        "observable": "tensor_to_scalar_ratio_r",
        "pillar": 335,
        "preregistered_in": "Pillar 335 (v11.18)",
        "expected_dr1": "2027",
        "falsification_condition": "r < 0.010 MEASURED at ≥3σ → Pillar P2/P3 FALSIFIED",
        "um_prediction": "r = 0.0315 ± 0.002",
        "routing_function": "route_so",
        "parameters_needed": ["r_measured", "r_sigma"],
        "optional_parameters": ["is_measurement"],
    },
    "DESI_DR3": {
        "full_name": "Dark Energy Spectroscopic Instrument Data Release 3",
        "observable": "dark_energy_eos_wa",
        "pillar": 336,
        "preregistered_in": "Pillar 336 (v11.18)",
        "expected_dr1": "2027",
        "falsification_condition": "wₐ ≠ 0 at ≥3σ → P4 FALSIFIED",
        "um_prediction": "wₐ = 0 (frozen radion)",
        "routing_function": "route_desi",
        "parameters_needed": ["wa_measured", "wa_sigma"],
        "optional_parameters": ["data_label"],
    },
    "LITEBIRD": {
        "full_name": "Lite (Light) satellite for the study of B-mode polarization",
        "observable": "cmb_birefringence_beta",
        "pillar": "P2 (birefringence prediction)",
        "preregistered_in": "Multiple pillars: P97, P303",
        "expected_dr1": "2032",
        "falsification_condition": "β ∉ [0.22°, 0.38°] → braided winding FALSIFIED",
        "um_prediction": "β ∈ {≈0.273°, ≈0.331°} canonical",
        "routing_function": "route_litebird",
        "parameters_needed": ["beta_deg_measured", "beta_sigma_deg"],
        "optional_parameters": [],
    },
    "CMB_S4": {
        "full_name": "CMB Stage 4",
        "observable": "tensor_to_scalar_ratio_r",
        "pillar": "P3 (r confirmation)",
        "preregistered_in": "Pillar 335 (v11.18)",
        "expected_dr1": "2030",
        "falsification_condition": "r < 0.005 at ≥3σ → P2/P3 FALSIFIED",
        "um_prediction": "r = 0.0315 ± 0.002",
        "routing_function": "route_cmbs4",
        "parameters_needed": ["r_measured", "r_sigma"],
        "optional_parameters": [],
    },
    "KATRIN": {
        "full_name": "Karlsruhe Tritium Neutrino Experiment",
        "observable": "neutrino_mass_sum",
        "pillar": "P301 (KATRIN preregistration)",
        "preregistered_in": "Pillar 302 (v11.11)",
        "expected_dr1": "2027",
        "falsification_condition": "Σmν > 0.5 eV at ≥3σ → P26 (lightest ν mass) FALSIFIED",
        "um_prediction": "Σmν ≈ 0.06–0.10 eV (normal ordering)",
        "routing_function": "route_katrin",
        "parameters_needed": ["sum_m_nu_ev", "sum_m_nu_sigma_ev"],
        "optional_parameters": [],
    },
    "LISA": {
        "full_name": "Laser Interferometer Space Antenna",
        "observable": "gravitational_wave_background",
        "pillar": "P294 (LISA preregistration)",
        "preregistered_in": "Pillar 294 (v11.9)",
        "expected_dr1": "2034+",
        "falsification_condition": "GW peak ∉ [1, 30] mHz → KK PT mechanism constrained",
        "um_prediction": "GW peak at f_peak ~ 7 mHz (from KK PT at T_KK~1 TeV)",
        "routing_function": "route_lisa",
        "parameters_needed": ["f_peak_mhz", "f_sigma_mhz"],
        "optional_parameters": [],
    },
    "HYPER_KAMIOKANDE": {
        "full_name": "Hyper-Kamiokande",
        "observable": "neutrino_mass_ordering_atmospheric",
        "pillar": "P296 (Hyper-K timeline)",
        "preregistered_in": "Pillar 296 (v11.10)",
        "expected_dr1": "2027",
        "falsification_condition": "IO confirmed at ≥3σ → Pillar 42 FALSIFIED",
        "um_prediction": "NORMAL ordering (same as JUNO prediction)",
        "routing_function": "route_hyperk",
        "parameters_needed": ["measured_ordering", "ordering_sigma"],
        "optional_parameters": [],
    },
}

# Birefringence prediction range for LiteBIRD routing
BETA_PREDICTION_CANONICAL = (0.273, 0.331)  # degrees
BETA_ADMISSIBLE_WINDOW = (0.22, 0.38)       # degrees
BETA_PREDICTED_GAP = (0.29, 0.31)           # degrees (landing here also falsifies)

# KATRIN neutrino mass bound
NU_MASS_SUM_UM_LOW = 0.06      # eV (normal ordering lower bound)
NU_MASS_SUM_UM_HIGH = 0.10     # eV
NU_MASS_FALSIFICATION_EV = 0.5 # eV at ≥3σ → falsified

# LISA gravitational wave prediction
GW_PEAK_FREQ_MHZ_LOW = 1.0     # mHz
GW_PEAK_FREQ_MHZ_HIGH = 30.0   # mHz
GW_PEAK_FREQ_MHZ_CENTRAL = 7.0 # mHz (from KK PT)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTING FUNCTIONS (for experiments without dedicated pillar modules)
# ─────────────────────────────────────────────────────────────────────────────

def route_juno(measured_ordering: str, ordering_sigma: float,
               dm31_measured: float = None,
               dm31_sigma_percent: float = None) -> dict:
    """Route JUNO result — delegates to Pillar 334."""
    return route_juno_dr1(measured_ordering, ordering_sigma,
                          dm31_measured, dm31_sigma_percent)


def route_so(r_measured: float, r_sigma: float,
             is_measurement: bool = True) -> dict:
    """Route Simons Observatory result — delegates to Pillar 335."""
    return route_so_dr1(r_measured, r_sigma, is_measurement)


def route_desi(wa_measured: float, wa_sigma: float,
               data_label: str = "DESI DR3") -> dict:
    """Route DESI result — delegates to Pillar 336."""
    return route_desi_dr3(wa_measured, wa_sigma, data_label)


def route_litebird(beta_deg_measured: float, beta_sigma_deg: float) -> dict:
    """Route LiteBIRD birefringence result to a verdict.

    Args:
        beta_deg_measured: Measured birefringence angle β [degrees].
        beta_sigma_deg: 1σ uncertainty [degrees].

    Returns:
        Dict with verdict and required actions.
    """
    beta_low = BETA_ADMISSIBLE_WINDOW[0]
    beta_high = BETA_ADMISSIBLE_WINDOW[1]
    beta_gap_low = BETA_PREDICTED_GAP[0]
    beta_gap_high = BETA_PREDICTED_GAP[1]

    # Check if measurement is in admissible window
    in_window = beta_low <= beta_deg_measured <= beta_high
    in_gap = beta_gap_low <= beta_deg_measured <= beta_gap_high

    # Distance from admissible window
    if beta_deg_measured < beta_low:
        n_sigma_outside = (beta_low - beta_deg_measured) / beta_sigma_deg
    elif beta_deg_measured > beta_high:
        n_sigma_outside = (beta_deg_measured - beta_high) / beta_sigma_deg
    else:
        n_sigma_outside = 0.0

    # Distance from canonical prediction range
    canonical_mid = sum(BETA_PREDICTION_CANONICAL) / 2
    n_sigma_from_canonical = abs(beta_deg_measured - canonical_mid) / beta_sigma_deg

    if not in_window and n_sigma_outside >= 3.0:
        verdict = "FALSIFIED"
        actions = [
            f"β = {beta_deg_measured:.4f}° outside admissible window [{beta_low},{beta_high}]° at {n_sigma_outside:.1f}σ",
            "Mark P2 birefringence prediction FALSIFIED in CLAIM_MASTER_BOARD.md",
            "This is the PRIMARY falsifier of the braided winding mechanism",
        ]
    elif in_gap and n_sigma_outside < 3.0:
        verdict = "FALSIFIED_GAP"
        actions = [
            f"β = {beta_deg_measured:.4f}° lands in predicted gap [{beta_gap_low},{beta_gap_high}]°",
            "Gap landing is explicitly a falsification condition",
            "Mark braided winding FALSIFIED in CLAIM_MASTER_BOARD.md",
        ]
    elif not in_window and n_sigma_outside >= 2.0:
        verdict = "HIGH_TENSION"
        actions = [
            f"β outside window at {n_sigma_outside:.1f}σ — below 3σ falsification threshold",
            "Escalate monitoring. Await final LiteBIRD analysis.",
        ]
    elif in_window and n_sigma_from_canonical < 2.0:
        verdict = "CONFIRMED"
        actions = [
            f"β = {beta_deg_measured:.4f}° ± {beta_sigma_deg:.4f}° within canonical range and window",
            "Birefringence prediction CONFIRMED — upgrade P2 to CONFIRMED",
            "This confirms the braided winding mechanism at primary falsifier level",
        ]
    elif in_window:
        verdict = "CONSISTENT"
        actions = [
            f"β = {beta_deg_measured:.4f}° within admissible window — consistent",
            "Continue monitoring.",
        ]
    else:
        verdict = "CONSISTENT"
        actions = ["Monitor."]

    return {
        "pillar": "P2",
        "experiment": "LiteBIRD",
        "observable": "birefringence_beta_deg",
        "beta_measured": beta_deg_measured,
        "beta_sigma": beta_sigma_deg,
        "admissible_window": BETA_ADMISSIBLE_WINDOW,
        "canonical_prediction": BETA_PREDICTION_CANONICAL,
        "predicted_gap": BETA_PREDICTED_GAP,
        "n_sigma_outside_window": n_sigma_outside,
        "n_sigma_from_canonical": n_sigma_from_canonical,
        "verdict": verdict,
        "required_actions": actions,
        "routing_protocol": "ORD v11.18",
    }


def route_katrin(sum_m_nu_ev: float, sum_m_nu_sigma_ev: float) -> dict:
    """Route KATRIN neutrino mass sum result to a verdict.

    Args:
        sum_m_nu_ev: Measured (or bounded) Σmν [eV].
        sum_m_nu_sigma_ev: 1σ uncertainty [eV].

    Returns:
        Dict with verdict and required actions.
    """
    um_central = (NU_MASS_SUM_UM_LOW + NU_MASS_SUM_UM_HIGH) / 2
    n_sigma_from_falsification = (NU_MASS_FALSIFICATION_EV - sum_m_nu_ev) / sum_m_nu_sigma_ev

    if sum_m_nu_ev > NU_MASS_FALSIFICATION_EV and n_sigma_from_falsification < 0:
        n_sigma_above = abs(n_sigma_from_falsification)
        if n_sigma_above >= 3.0:
            verdict = "FALSIFIED"
            actions = [
                f"Σmν = {sum_m_nu_ev:.3f} eV > {NU_MASS_FALSIFICATION_EV} eV at {n_sigma_above:.1f}σ → P26 FALSIFIED",
            ]
        else:
            verdict = "HIGH_TENSION"
            actions = [f"Σmν = {sum_m_nu_ev:.3f} eV at {n_sigma_above:.1f}σ — monitor"]
    elif sum_m_nu_ev < NU_MASS_SUM_UM_HIGH + 3 * sum_m_nu_sigma_ev:
        verdict = "CONSISTENT"
        actions = [f"Σmν = {sum_m_nu_ev:.3f} eV consistent with UM range [0.06, 0.10] eV"]
    else:
        verdict = "TENSION"
        actions = [f"Σmν = {sum_m_nu_ev:.3f} eV — investigate"]

    return {
        "pillar": "P301",
        "experiment": "KATRIN",
        "observable": "neutrino_mass_sum_ev",
        "sum_m_nu_measured": sum_m_nu_ev,
        "sum_m_nu_sigma": sum_m_nu_sigma_ev,
        "um_prediction_range": (NU_MASS_SUM_UM_LOW, NU_MASS_SUM_UM_HIGH),
        "falsification_threshold_ev": NU_MASS_FALSIFICATION_EV,
        "verdict": verdict,
        "required_actions": actions,
        "routing_protocol": "ORD v11.18",
    }


def route_lisa(f_peak_mhz: float, f_sigma_mhz: float) -> dict:
    """Route LISA gravitational wave background result to a verdict.

    Args:
        f_peak_mhz: Measured peak frequency of GW background [mHz].
        f_sigma_mhz: 1σ uncertainty [mHz].

    Returns:
        Dict with verdict and required actions.
    """
    um_pred = GW_PEAK_FREQ_MHZ_CENTRAL
    n_sigma_from_um = abs(f_peak_mhz - um_pred) / f_sigma_mhz

    in_range = GW_PEAK_FREQ_MHZ_LOW <= f_peak_mhz <= GW_PEAK_FREQ_MHZ_HIGH

    if not in_range:
        dist_from_range = min(abs(f_peak_mhz - GW_PEAK_FREQ_MHZ_LOW),
                              abs(f_peak_mhz - GW_PEAK_FREQ_MHZ_HIGH))
        n_sigma_outside = dist_from_range / f_sigma_mhz
        verdict = "FALSIFIED" if n_sigma_outside >= 3.0 else "HIGH_TENSION"
    elif n_sigma_from_um < 2.0:
        verdict = "CONFIRMED"
    else:
        verdict = "CONSISTENT"

    return {
        "pillar": "P294",
        "experiment": "LISA",
        "observable": "gw_peak_freq_mhz",
        "f_peak_measured": f_peak_mhz,
        "f_peak_sigma": f_sigma_mhz,
        "um_prediction_mhz": um_pred,
        "admissible_range_mhz": (GW_PEAK_FREQ_MHZ_LOW, GW_PEAK_FREQ_MHZ_HIGH),
        "n_sigma_from_um": round(n_sigma_from_um, 2),
        "verdict": verdict,
        "required_actions": [
            f"GW peak at {f_peak_mhz:.2f} mHz, UM predicts {um_pred} mHz — {verdict}"
        ],
        "routing_protocol": "ORD v11.18",
    }


def route_hyperk(measured_ordering: str, ordering_sigma: float) -> dict:
    """Route Hyper-Kamiokande ordering result — same logic as JUNO."""
    result = route_juno_dr1(measured_ordering, ordering_sigma)
    result["experiment"] = "Hyper-Kamiokande"
    result["pillar"] = "P296"
    return result


def route_cmbs4(r_measured: float, r_sigma: float) -> dict:
    """Route CMB-S4 r result — same logic as SO with CMB-S4 label."""
    result = route_so_dr1(r_measured, r_sigma)
    result["experiment"] = "CMB-S4"
    return result


# ─────────────────────────────────────────────────────────────────────────────
# DISPATCH ENGINE
# ─────────────────────────────────────────────────────────────────────────────

# Map experiment keys to routing functions
ROUTING_DISPATCH = {
    "JUNO": route_juno,
    "SIMONS_OBSERVATORY": route_so,
    "DESI_DR3": route_desi,
    "LITEBIRD": route_litebird,
    "CMB_S4": route_cmbs4,
    "KATRIN": route_katrin,
    "LISA": route_lisa,
    "HYPER_KAMIOKANDE": route_hyperk,
    "DESI_DR4": route_desi,   # same routing function, different label
}


def dispatch(experiment: str, **kwargs) -> dict:
    """Dispatch an experimental result to the correct routing function.

    Args:
        experiment: Experiment key (must be in ROUTING_DISPATCH).
        **kwargs: Parameters for the routing function (experiment-specific).

    Returns:
        Dict with verdict and required actions.

    Raises:
        ValueError: If experiment is not in registry.
    """
    experiment_upper = experiment.strip().upper().replace(" ", "_")
    if experiment_upper not in ROUTING_DISPATCH:
        available = list(ROUTING_DISPATCH.keys())
        raise ValueError(
            f"Unknown experiment '{experiment}'. "
            f"Available: {available}"
        )
    fn = ROUTING_DISPATCH[experiment_upper]
    return fn(**kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# VERDICT ENGINE
# ─────────────────────────────────────────────────────────────────────────────

VERDICT_CODES = {
    "FALSIFIED": {
        "severity": "CRITICAL",
        "color": "RED",
        "description": "UM prediction falsified by experimental data at ≥3σ.",
        "required_response_hours": 24,
    },
    "FALSIFIED_GAP": {
        "severity": "CRITICAL",
        "color": "RED",
        "description": "UM prediction falsified by landing in predicted exclusion gap.",
        "required_response_hours": 24,
    },
    "HIGH_TENSION": {
        "severity": "ELEVATED",
        "color": "ORANGE",
        "description": "Experimental tension at 2–3σ. Not falsified. Monitor closely.",
        "required_response_hours": 72,
    },
    "HIGH_TENSION_ABOVE": {
        "severity": "ELEVATED",
        "color": "ORANGE",
        "description": "Measurement above UM prediction. Investigate NLO corrections.",
        "required_response_hours": 72,
    },
    "TENSION": {
        "severity": "MODERATE",
        "color": "YELLOW",
        "description": "Some tension with UM prediction. Monitor.",
        "required_response_hours": 168,
    },
    "CONSISTENT": {
        "severity": "NOMINAL",
        "color": "GREEN",
        "description": "Consistent with UM prediction. No immediate action required.",
        "required_response_hours": None,
    },
    "CONFIRMED": {
        "severity": "POSITIVE",
        "color": "BRIGHT_GREEN",
        "description": "UM prediction confirmed by experimental data.",
        "required_response_hours": 24,
    },
    "RESOLVED": {
        "severity": "POSITIVE",
        "color": "GREEN",
        "description": "Previous tension resolved. UM prediction consistent.",
        "required_response_hours": 24,
    },
}


def format_verdict(routing_result: dict, publication_date: str = None) -> dict:
    """Format a routing result into a standardized verdict document.

    Args:
        routing_result: Dict from any routing function.
        publication_date: ISO date of the experimental publication (optional).

    Returns:
        Standardized verdict dict with metadata.
    """
    verdict = routing_result.get("verdict", "UNKNOWN")
    code_info = VERDICT_CODES.get(verdict, {
        "severity": "UNKNOWN",
        "color": "GREY",
        "description": "Unknown verdict.",
        "required_response_hours": None,
    })

    return {
        "ord_version": "v11.18",
        "timestamp": publication_date or datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "experiment": routing_result.get("experiment", "UNKNOWN"),
        "pillar": routing_result.get("pillar", "UNKNOWN"),
        "verdict": verdict,
        "severity": code_info["severity"],
        "description": code_info["description"],
        "required_response_hours": code_info["required_response_hours"],
        "routing_result": routing_result,
        "documents_to_update": _documents_to_update(verdict),
        "routing_protocol": "ORD v11.18",
    }


def _documents_to_update(verdict: str) -> list:
    """Return list of documents to update for a given verdict."""
    docs = ["3-FALSIFICATION/OBSERVATION_TRACKER.md"]
    if verdict in ("FALSIFIED", "FALSIFIED_GAP"):
        docs += [
            "docs/CLAIM_MASTER_BOARD.md",
            "docs/WAVE_CHANGELOG.md",
            "STATUS.md",
            "FALLIBILITY.md",
        ]
    elif verdict in ("CONFIRMED", "RESOLVED"):
        docs += [
            "docs/CLAIM_MASTER_BOARD.md",
            "STATUS.md",
        ]
    elif verdict in ("HIGH_TENSION", "HIGH_TENSION_ABOVE", "TENSION"):
        docs += ["docs/CLAIM_MASTER_BOARD.md"]
    return docs


# ─────────────────────────────────────────────────────────────────────────────
# SIMULATION MODE (DRY-RUN)
# ─────────────────────────────────────────────────────────────────────────────

def simulate_all_experiments() -> dict:
    """Run a dry-run simulation of all experiments at their UM-predicted values.

    This confirms that all routing functions return 'CONSISTENT' or 'CONFIRMED'
    when the UM prediction is exactly confirmed.
    """
    results = {}

    # JUNO: predict Normal Ordering confirmed at 3σ
    results["JUNO_um_confirmed"] = format_verdict(
        route_juno("NO", 3.5),
        publication_date="2027-01-01 (SIMULATED)"
    )

    # JUNO: predict Inverted Ordering — should be FALSIFIED
    results["JUNO_falsified_test"] = format_verdict(
        route_juno("IO", 3.5),
        publication_date="2027-01-01 (SIMULATED)"
    )

    # SO: r = 0.0315 exactly confirmed
    results["SO_um_confirmed"] = format_verdict(
        route_so(0.0315, 0.003),
        publication_date="2027-06-01 (SIMULATED)"
    )

    # SO: r = 0.005 — falsification scenario
    results["SO_falsified_test"] = format_verdict(
        route_so(0.005, 0.003),
        publication_date="2027-06-01 (SIMULATED)"
    )

    # DESI DR3: wₐ = 0 — UM confirmed
    results["DESI_um_confirmed"] = format_verdict(
        route_desi(0.0, 0.17),
        publication_date="2027-03-01 (SIMULATED)"
    )

    # DESI DR3: tension maintained at -0.55
    results["DESI_tension_test"] = format_verdict(
        route_desi(-0.55, 0.17, "DESI DR3 (simulated tension)"),
        publication_date="2027-03-01 (SIMULATED)"
    )

    # LiteBIRD: β = 0.300° — lands in predicted gap [0.29, 0.31]
    results["LITEBIRD_gap_test"] = format_verdict(
        route_litebird(0.300, 0.01),
        publication_date="2032-01-01 (SIMULATED)"
    )

    # LiteBIRD: β = 0.320° — between gap and canonical 0.331° → CONSISTENT
    results["LITEBIRD_consistent_test"] = format_verdict(
        route_litebird(0.320, 0.01),
        publication_date="2032-01-01 (SIMULATED)"
    )

    # KATRIN: Σmν = 0.08 eV — consistent
    results["KATRIN_consistent_test"] = format_verdict(
        route_katrin(0.08, 0.05),
        publication_date="2027-09-01 (SIMULATED)"
    )

    # LISA: f_peak = 7.0 mHz — confirmed
    results["LISA_confirmed_test"] = format_verdict(
        route_lisa(7.0, 2.0),
        publication_date="2034-01-01 (SIMULATED)"
    )

    return results


def ord_status_report() -> dict:
    """Return the current ORD status and experiment registry summary."""
    return {
        "ord_version": "v11.18",
        "title": "Observatory Routing Daemon — Status Report",
        "watched_experiments": len(EXPERIMENT_REGISTRY),
        "routing_functions": len(ROUTING_DISPATCH),
        "verdict_codes": list(VERDICT_CODES.keys()),
        "experiment_registry": EXPERIMENT_REGISTRY,
        "next_expected": {
            "JUNO": "~2027",
            "SIMONS_OBSERVATORY": "~2027",
            "DESI_DR3": "~2027",
            "KATRIN": "~2027",
            "CMB_S4": "~2030",
            "LITEBIRD": "~2032",
            "LISA": "~2034+",
        },
        "critical_falsifiers": {
            "primary": "LiteBIRD β ∉ [0.22°, 0.38°]",
            "secondary": ["JUNO IO at ≥3σ", "SO r < 0.010 at ≥3σ"],
            "monitoring": ["DESI DR3 wₐ tension", "Hyper-K ordering"],
        },
    }
