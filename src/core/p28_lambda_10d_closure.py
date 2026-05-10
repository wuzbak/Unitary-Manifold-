# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""P28 10D closure package: flux sufficiency + explicit vacuum selection."""
from __future__ import annotations

import math
from typing import Dict

from src.core.p28_lambda_first_principles import p28_first_principles_report
from src.eleventd.g4_flux_vacuum_link import g4_flux_selection_summary
from src.tend.cc_architecture_limit import LAMBDA_OBS_MPLANCK4, N_FLUX

__all__ = [
    "BASE_N_FLUX",
    "DUAL_FLUX_MULTIPLICITY",
    "REQUIRED_N_FLUX_MIN",
    "effective_flux_sufficiency",
    "explicit_vacuum_selection",
    "p28_10d_closure_report",
]

BASE_N_FLUX: int = N_FLUX
DUAL_FLUX_MULTIPLICITY: int = 2
REQUIRED_N_FLUX_MIN: int = 61


def _all_closure_gates_satisfied(
    flux: Dict[str, object],
    selection: Dict[str, object],
    first_principles: Dict[str, object],
) -> bool:
    """Return True only when flux sufficiency and explicit selection gates all pass."""
    return bool(
        flux["meets_bp_threshold"]
        and flux["spacing_below_lambda_obs"]
        and selection["explicit_selection_pass"]
        and first_principles["derivation_pass"]
    )


def effective_flux_sufficiency(
    base_n_flux: int = BASE_N_FLUX,
    dual_flux_multiplicity: int = DUAL_FLUX_MULTIPLICITY,
) -> Dict[str, object]:
    """Compute effective BP channel count and spacing sufficiency in the 10D closure branch."""
    if base_n_flux <= 0:
        raise ValueError(f"base_n_flux must be positive, got {base_n_flux}")
    if dual_flux_multiplicity <= 0:
        raise ValueError(f"dual_flux_multiplicity must be positive, got {dual_flux_multiplicity}")

    effective_n_flux = base_n_flux * dual_flux_multiplicity
    # Naive BP (Bousso-Polchinski) discretuum spacing scales as ε ~ 10^{-2 N_flux}; therefore
    # log10(ε / M_Pl^4) = -2 * N_flux.
    spacing_log10 = -2.0 * float(effective_n_flux)
    lambda_obs_log10 = math.log10(LAMBDA_OBS_MPLANCK4)
    spacing_below_lambda_obs = spacing_log10 < lambda_obs_log10
    meets_bp_threshold = effective_n_flux >= REQUIRED_N_FLUX_MIN

    return {
        "base_n_flux": int(base_n_flux),
        "dual_flux_multiplicity": int(dual_flux_multiplicity),
        "effective_n_flux": effective_n_flux,
        "required_n_flux_min": REQUIRED_N_FLUX_MIN,
        "meets_bp_threshold": meets_bp_threshold,
        "spacing_log10": spacing_log10,
        "lambda_obs_log10": lambda_obs_log10,
        "spacing_below_lambda_obs": spacing_below_lambda_obs,
        "status": (
            "SUFFICIENT_10D_CLOSURE_CHANNEL_COUNT"
            if meets_bp_threshold and spacing_below_lambda_obs
            else "INSUFFICIENT_10D_CLOSURE_CHANNEL_COUNT"
        ),
    }


def explicit_vacuum_selection() -> Dict[str, object]:
    """Provide explicit UV vacuum-selection evidence used by the P28 hardgate."""
    selection = g4_flux_selection_summary()
    selected_n_w = selection.get("unique_flux_selected_n_w")
    explicit_selection_pass = (
        selection["status"] == "UNIQUE_UV_FLUX_SELECTION"
        and selected_n_w == 5
        and len(selection["surviving_candidates"]) == 1
    )
    return {
        "selection_summary": selection,
        "explicit_selection_pass": explicit_selection_pass,
        "status": "EXPLICIT_SELECTION_PROVED" if explicit_selection_pass else "EXPLICIT_SELECTION_BLOCKED",
    }


def p28_10d_closure_report() -> Dict[str, object]:
    """Return consolidated 10D closure evidence for P28 promotion gates."""
    flux = effective_flux_sufficiency()
    selection = explicit_vacuum_selection()
    first_principles = p28_first_principles_report()
    closure_pass = _all_closure_gates_satisfied(flux, selection, first_principles)
    return {
        "parameter": "P28",
        "closure_dimension": "10D",
        "effective_n_flux": flux["effective_n_flux"],
        "required_n_flux_min": flux["required_n_flux_min"],
        "meets_bp_threshold": flux["meets_bp_threshold"],
        "spacing_log10": flux["spacing_log10"],
        "lambda_obs_log10": flux["lambda_obs_log10"],
        "spacing_below_lambda_obs": flux["spacing_below_lambda_obs"],
        "explicit_selection_pass": selection["explicit_selection_pass"],
        "selection_winner_n_w": selection["selection_summary"].get("unique_flux_selected_n_w"),
        "first_principles_derivation_pass": first_principles["derivation_pass"],
        "first_principles_lambda_pred_mplanck4": first_principles["components"]["lambda_pred_mplanck4"],
        "first_principles_lambda_pred_log10": first_principles["components"]["lambda_pred_log10"],
        "first_principles_topological_partition": first_principles["components"]["topological_partition"],
        "first_principles_status": first_principles["status"],
        "all_closure_gates_pass": closure_pass,
        "promotion_ready": closure_pass,
        "status": "P28_10D_CLOSURE_READY" if closure_pass else "P28_10D_CLOSURE_BLOCKED",
    }
