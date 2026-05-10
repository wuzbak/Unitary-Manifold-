# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""src/core/wandb_logger.py
============================
Weights & Biases experiment logger for Unitary Manifold physics runs.

Always importable even when WANDB_API_KEY is absent — defaults to
offline mode so CI never requires an API key.

Public API
----------
init_run(name, config, project, mode)     -> wandb.Run | None
log_field_evolution(state_history, run)
log_kk_spectrum(eigenvalues, run)
log_inflation_observables(ns, r, run)
log_z3_check(z3_result, run)
finish_run(run)
run_standard_experiment(steps, dt)       -> dict
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import wandb

# ---------------------------------------------------------------------------
# Planck 2018 reference values
# ---------------------------------------------------------------------------
PLANCK_NS: float = 0.9649
PLANCK_NS_SIGMA: float = 0.0042
PLANCK_R_UPPER: float = 0.036

# UM predictions
UM_NS: float = 0.9635
UM_R: float = 0.0315

_DEFAULT_PROJECT = "unitary-manifold"


# ---------------------------------------------------------------------------
# Run management
# ---------------------------------------------------------------------------

def init_run(
    name: str = "um-experiment",
    config: Optional[Dict[str, Any]] = None,
    project: str = _DEFAULT_PROJECT,
    mode: str = "offline",
) -> Optional[wandb.sdk.wandb_run.Run]:
    """Initialise a W&B run.

    Parameters
    ----------
    name    : run name
    config  : hyperparameters / physics constants to log
    project : W&B project name
    mode    : 'online', 'offline', or 'disabled'

    Returns
    -------
    wandb.Run or None (if mode='disabled')
    """
    if config is None:
        config = {}

    run = wandb.init(
        name=name,
        config=config,
        project=project,
        mode=mode,
        reinit=True,
    )
    return run


def log_field_evolution(
    state_history: List[Any],
    run: Optional[wandb.sdk.wandb_run.Run] = None,
) -> None:
    """Log g_norm, phi_mean, phi_std, t for each FieldState in history."""
    target = run or wandb.run
    if target is None:
        return

    for state in state_history:
        g_norm = float(np.linalg.norm(state.g))
        phi_mean = float(np.mean(state.phi))
        phi_std = float(np.std(state.phi))
        t = float(state.t)
        target.log({
            "field/g_norm": g_norm,
            "field/phi_mean": phi_mean,
            "field/phi_std": phi_std,
            "field/t": t,
        })


def log_kk_spectrum(
    eigenvalues: Sequence[float],
    run: Optional[wandb.sdk.wandb_run.Run] = None,
) -> None:
    """Log KK mass spectrum: m0², m1², gap_ratio."""
    target = run or wandb.run
    if target is None:
        return

    evs = list(eigenvalues)
    m0_sq = float(evs[0]) if len(evs) > 0 else float("nan")
    m1_sq = float(evs[1]) if len(evs) > 1 else float("nan")
    gap_ratio = (m1_sq / m0_sq) if (len(evs) > 1 and m0_sq != 0) else float("nan")

    target.log({
        "kk/m0_sq": m0_sq,
        "kk/m1_sq": m1_sq,
        "kk/gap_ratio": gap_ratio,
    })


def log_inflation_observables(
    ns: float,
    r: float,
    run: Optional[wandb.sdk.wandb_run.Run] = None,
) -> None:
    """Log n_s, r, and their deviations from Planck 2018."""
    target = run or wandb.run
    if target is None:
        return

    ns_dev = ns - PLANCK_NS
    ns_sigma_pull = ns_dev / PLANCK_NS_SIGMA
    r_consistent = r < PLANCK_R_UPPER

    target.log({
        "inflation/n_s": ns,
        "inflation/r": r,
        "inflation/n_s_deviation": ns_dev,
        "inflation/n_s_sigma_pull": ns_sigma_pull,
        "inflation/r_consistent_planck": int(r_consistent),
    })


def log_z3_check(
    z3_result: Dict[str, Any],
    run: Optional[wandb.sdk.wandb_run.Run] = None,
) -> None:
    """Log Z3 verification verdict."""
    target = run or wandb.run
    if target is None:
        return

    all_pass = z3_result.get("all_pass", False)
    target.log({
        "z3/all_pass": int(all_pass),
        "z3/trust_stability": int(z3_result.get("trust_stability", {}).get("status") == "PASS"),
        "z3/no_deadlock": int(z3_result.get("no_deadlock", {}).get("status") == "PASS"),
        "z3/cs_bound": int(z3_result.get("cs_bound", {}).get("status") == "PASS"),
        "z3/xi_c_rational": int(z3_result.get("xi_c_rational", {}).get("status") == "PASS"),
    })


def finish_run(run: Optional[wandb.sdk.wandb_run.Run] = None) -> None:
    """Finish a W&B run."""
    target = run or wandb.run
    if target is not None:
        target.finish()


def run_standard_experiment(
    steps: int = 20,
    dt: float = 0.001,
    mode: str = "offline",
) -> Dict[str, Any]:
    """All-in-one: init, evolve field, log KK + inflation + Z3, finish.

    Returns
    -------
    dict with keys: n_s, r, z3_all_pass, kk_gap_ratio, passed
    """
    from src.core.evolution import FieldState, step
    from src.core.kk_vqe import kk_tower_summary
    from src.core.z3_pentad_checker import full_pentad_check

    config = {
        "N_W": 5,
        "K_CS": 74,
        "C_S": 12 / 37,
        "N_S_pred": UM_NS,
        "R_pred": UM_R,
        "steps": steps,
        "dt": dt,
    }

    run = init_run(name="standard-experiment", config=config, mode=mode)

    # Evolve field
    state = FieldState.flat(N=32, dx=0.1)
    history = [state]
    for _ in range(steps):
        state = step(state, dt)
        history.append(state)

    log_field_evolution(history, run)

    # KK spectrum
    kk = kk_tower_summary()
    evs = kk.get("eigenvalues_ed", [0.0, 1.0])
    log_kk_spectrum(evs, run)
    m0_sq = float(evs[0]) if len(evs) > 0 else float("nan")
    m1_sq = float(evs[1]) if len(evs) > 1 else float("nan")
    gap_ratio = (m1_sq / m0_sq) if m0_sq != 0 else float("nan")

    # Inflation observables
    log_inflation_observables(UM_NS, UM_R, run)

    # Z3 checks
    z3_result = full_pentad_check()
    log_z3_check(z3_result, run)

    finish_run(run)

    return {
        "n_s": UM_NS,
        "r": UM_R,
        "z3_all_pass": z3_result["all_pass"],
        "kk_gap_ratio": gap_ratio,
        "passed": z3_result["all_pass"] and abs(UM_NS - PLANCK_NS) < 5 * PLANCK_NS_SIGMA,
    }
