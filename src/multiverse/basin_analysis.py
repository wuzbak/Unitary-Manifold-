# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/multiverse/basin_analysis.py
=================================
Basin-of-attraction analysis tools for the FTUM fixed-point iteration.

Addresses Q19 in BIG_QUESTIONS.md: the 82.8% convergence rate and ±54.8%
spread in φ* reveal that the FTUM fixed point is not globally unique.
This module provides four complementary diagnostics to characterise the
structure of that non-universality, following the programme outlined by
Gemini's analysis (April 2026):

1. ``basin_of_attraction_sweep``
   Systematic grid sweep over (S₀, A₀, Q_top) initial conditions.
   Records φ* (mean entropy at the fixed point), convergence flag, iteration
   count, and residual history for every starting point.

2. ``classify_non_convergent``
   Classifies a residual history as one of three failure modes:
   - ``"limit_cycle"``  — oscillates without decaying (possible period-2+ orbit)
   - ``"divergent"``    — residual grows without bound
   - ``"slow"``         — monotonically decreasing but stalls above tolerance

3. ``sensitivity_sweep``
   Micro-perturbs a given initial condition by ±ε and records what fraction
   of those perturbed runs flip between convergent and non-convergent.
   A high flip fraction signals a **fractal basin boundary** at that point.

4. ``bifurcation_scan``
   Scans a secondary parameter (``"coupling"``, ``"kappa"``, ``"dt"``, or
   ``"Q_top"``) while holding others fixed and records φ* at each value.
   A discontinuous jump in φ* marks a **bifurcation point**.

5. ``topological_invariant_check``
   Given a completed ``BasinSweepResult``, computes the coefficient of
   variation (CV = σ/μ) of several candidate invariant quantities across all
   converged cases and returns the candidate with the smallest CV.  A CV ≪ 1
   would constitute a **relative fixed point** (something that stays constant
   while φ* itself varies).

6. ``near_miss_analysis``
   Given a list of residual histories (one per initial condition), identifies
   cases where the residual oscillates persistently near the tolerance without
   converging — the "near-miss" signature of a marginal attractor.

Public API
----------
BasinSweepResult            — dataclass for sweep output
SensitivityResult           — dataclass for sensitivity sweep output
BifurcationResult           — dataclass for bifurcation scan output
InvariantResult             — dataclass for invariant check output
NearMissResult              — dataclass for near-miss analysis output

basin_of_attraction_sweep   — grid sweep
classify_non_convergent     — residual history classifier
sensitivity_sweep           — fractal boundary detector
bifurcation_scan            — bifurcation mapper
topological_invariant_check — invariant finder
near_miss_analysis          — near-miss oscillation detector

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .fixed_point import (
    MultiverseNetwork,
    MultiverseNode,
    fixed_point_iteration,
)

# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

_EPS = 1e-30   # guard against division by zero

# Canonical default network parameters used by Q19
_DEFAULT_N_NODES = 3
_DEFAULT_COUPLING = 0.1
_DEFAULT_MAX_ITER = 300
_DEFAULT_TOL = 1e-6
_DEFAULT_DT = 0.2
_DEFAULT_KAPPA = 0.25
_DEFAULT_GAMMA = 5.0
_DEFAULT_G4 = 1.0


# ---------------------------------------------------------------------------
# Return-type dataclasses
# ---------------------------------------------------------------------------

@dataclass
class BasinSweepResult:
    """Results of a basin-of-attraction grid sweep.

    Attributes
    ----------
    S_values, A_values, Q_values : 1-D arrays of the swept parameter grids.
    phi_star       : 3-D array, shape (n_S, n_A, n_Q).  Mean node entropy at
                     the fixed point for each (S₀, A₀, Q_top) triple; NaN for
                     non-convergent cases.
    converged      : bool array, same shape — True where iteration converged.
    n_iters        : int array — iterations used (max_iter for non-convergent).
    residual_histories : list of (n_S × n_A × n_Q) residual history arrays.
    convergence_rate   : float — fraction of cases that converged.
    phi_star_mean  : float — mean φ* across converged cases.
    phi_star_std   : float — standard deviation.
    phi_star_min   : float — minimum.
    phi_star_max   : float — maximum.
    phi_star_spread_pct : float — 100 × σ / μ (coefficient of variation %).
    edge_failure_fraction : float — fraction of non-convergent cases that lie
                     on the boundary of the swept grid (sensitivity indicator).
    """
    S_values: np.ndarray
    A_values: np.ndarray
    Q_values: np.ndarray
    phi_star: np.ndarray        # shape (n_S, n_A, n_Q)
    converged: np.ndarray       # bool, same shape
    n_iters: np.ndarray         # int, same shape
    residual_histories: List    # flat list, row-major over (S, A, Q)
    convergence_rate: float
    phi_star_mean: float
    phi_star_std: float
    phi_star_min: float
    phi_star_max: float
    phi_star_spread_pct: float
    edge_failure_fraction: float


@dataclass
class SensitivityResult:
    """Results of a micro-perturbation sensitivity sweep around one point.

    Attributes
    ----------
    S0, A0, Q_top  : the nominal initial condition.
    nominal_converged : bool — does the unperturbed run converge?
    nominal_phi_star  : float — φ* of the unperturbed run (NaN if not converged).
    flip_fraction  : float — fraction of perturbed runs that differ in convergence
                     outcome from the nominal run.  High value → fractal boundary.
    is_fractal_boundary : bool — True if flip_fraction > 0.2 (20 % threshold).
    phi_star_perturbed  : 1-D array of φ* values for each perturbation.
    stability_class : str — "stable", "marginal", or "fractal".
    """
    S0: float
    A0: float
    Q_top: float
    nominal_converged: bool
    nominal_phi_star: float
    flip_fraction: float
    is_fractal_boundary: bool
    phi_star_perturbed: np.ndarray
    stability_class: str


@dataclass
class BifurcationResult:
    """Results of a secondary-parameter bifurcation scan.

    Attributes
    ----------
    param_name   : name of the scanned parameter.
    param_values : 1-D array of scanned values.
    phi_star     : 1-D array of φ* at each value (NaN if not converged).
    converged    : bool array, same length.
    bifurcation_indices : list of indices where |φ*(i+1) − φ*(i)| is
                  anomalously large (> 3× median absolute difference).
    bifurcation_values  : parameter values at those indices.
    n_bifurcations      : int — count of detected bifurcations.
    """
    param_name: str
    param_values: np.ndarray
    phi_star: np.ndarray
    converged: np.ndarray
    bifurcation_indices: List[int]
    bifurcation_values: List[float]
    n_bifurcations: int


@dataclass
class InvariantResult:
    """Results of a topological invariant search.

    Attributes
    ----------
    candidate_names : list of candidate quantity names.
    cv_values       : dict mapping name → coefficient of variation (σ/μ).
    best_candidate  : name of the quantity with the smallest CV.
    best_cv         : its CV value.
    invariant_found : bool — True if best_cv < 0.1 (within 10 % of constant).
    interpretation  : plain-language summary.
    """
    candidate_names: List[str]
    cv_values: Dict[str, float]
    best_candidate: str
    best_cv: float
    invariant_found: bool
    interpretation: str


@dataclass
class NearMissResult:
    """Results of near-miss oscillation analysis.

    Attributes
    ----------
    n_total              : total residual histories analysed.
    n_near_miss          : count of near-miss cases (oscillates near tolerance).
    near_miss_fraction   : n_near_miss / n_total.
    n_limit_cycle        : count classified as ``"limit_cycle"``.
    n_divergent          : count classified as ``"divergent"``.
    n_slow               : count classified as ``"slow"``.
    classifications      : list of classification strings, one per history.
    median_oscillation_amplitude : median peak-to-trough amplitude of oscillating
                           residuals, as a multiple of tol.
    """
    n_total: int
    n_near_miss: int
    near_miss_fraction: float
    n_limit_cycle: int
    n_divergent: int
    n_slow: int
    classifications: List[str]
    median_oscillation_amplitude: float


# ---------------------------------------------------------------------------
# 1. basin_of_attraction_sweep
# ---------------------------------------------------------------------------

def basin_of_attraction_sweep(
    S_values: Optional[Sequence[float]] = None,
    A_values: Optional[Sequence[float]] = None,
    Q_values: Optional[Sequence[float]] = None,
    n_nodes: int = _DEFAULT_N_NODES,
    coupling: float = _DEFAULT_COUPLING,
    max_iter: int = _DEFAULT_MAX_ITER,
    tol: float = _DEFAULT_TOL,
    dt: float = _DEFAULT_DT,
    kappa: float = _DEFAULT_KAPPA,
    gamma: float = _DEFAULT_GAMMA,
    G4: float = _DEFAULT_G4,
    rng: Optional[np.random.Generator] = None,
) -> BasinSweepResult:
    """Sweep a grid of initial conditions and map the FTUM basin of attraction.

    Replicates and extends the 192-case sweep documented in Q19 of
    BIG_QUESTIONS.md.  For each (S₀, A₀, Q_top) triple a fresh ``n_nodes``-node
    chain network is constructed, all nodes initialised to the same (S₀, A₀,
    Q_top), and ``fixed_point_iteration`` is run.

    Parameters
    ----------
    S_values : sequence of floats — initial entropy values to sweep.
               Default: 8 log-spaced values in [0.10, 5.10].
    A_values : sequence of floats — initial area values to sweep.
               Default: 8 log-spaced values in [0.50, 5.50].
    Q_values : sequence of floats — topological charge values.
               Default: [0.0, 0.5, 1.0] (3 values, as in Q19).
    n_nodes, coupling, max_iter, tol, dt, kappa, gamma, G4
               — passed directly to ``fixed_point_iteration``.
    rng        — optional RNG for reproducible X / Xdot initialisation.

    Returns
    -------
    BasinSweepResult
    """
    if S_values is None:
        S_values = np.linspace(0.10, 5.10, 8)
    if A_values is None:
        A_values = np.linspace(0.50, 5.50, 8)
    if Q_values is None:
        Q_values = np.array([0.0, 0.5, 1.0])
    if rng is None:
        rng = np.random.default_rng(42)

    S_arr = np.asarray(S_values, dtype=float)
    A_arr = np.asarray(A_values, dtype=float)
    Q_arr = np.asarray(Q_values, dtype=float)

    nS, nA, nQ = len(S_arr), len(A_arr), len(Q_arr)
    phi_star_arr = np.full((nS, nA, nQ), np.nan)
    converged_arr = np.zeros((nS, nA, nQ), dtype=bool)
    n_iters_arr = np.zeros((nS, nA, nQ), dtype=int)
    residual_histories: List = []

    for si, S0 in enumerate(S_arr):
        for ai, A0 in enumerate(A_arr):
            for qi, Q0 in enumerate(Q_arr):
                # Build a fresh network with all nodes at (S0, A0, Q0)
                nodes = [
                    MultiverseNode(
                        dim=4,
                        S=float(S0),
                        A=float(A0),
                        Q_top=float(Q0),
                        X=1e-2 * rng.standard_normal(4),
                        Xdot=np.zeros(4),
                    )
                    for _ in range(n_nodes)
                ]
                adj = np.zeros((n_nodes, n_nodes))
                for k in range(n_nodes - 1):
                    adj[k, k + 1] = adj[k + 1, k] = coupling
                net = MultiverseNetwork(nodes=nodes, adjacency=adj)

                final_net, history, conv = fixed_point_iteration(
                    net,
                    max_iter=max_iter,
                    tol=tol,
                    dt=dt,
                    G4=G4,
                    kappa=kappa,
                    gamma=gamma,
                )

                residual_histories.append(history)
                converged_arr[si, ai, qi] = conv
                n_iters_arr[si, ai, qi] = len(history)
                if conv:
                    phi_star_arr[si, ai, qi] = float(
                        np.mean([nd.S for nd in final_net.nodes])
                    )

    # Summary statistics over converged cases
    converged_vals = phi_star_arr[converged_arr]
    n_total = nS * nA * nQ
    n_conv = int(converged_arr.sum())
    conv_rate = n_conv / n_total if n_total > 0 else 0.0

    if n_conv > 0:
        mu = float(np.mean(converged_vals))
        sigma = float(np.std(converged_vals))
        pmin = float(np.min(converged_vals))
        pmax = float(np.max(converged_vals))
        spread_pct = 100.0 * sigma / (mu + _EPS)
    else:
        mu = sigma = pmin = pmax = spread_pct = float("nan")

    # Edge-failure fraction: non-convergent cases at the grid boundary
    edge_mask = _edge_mask(nS, nA, nQ)
    non_conv_mask = ~converged_arr
    n_non_conv = int(non_conv_mask.sum())
    edge_failures = int((non_conv_mask & edge_mask).sum())
    edge_fail_frac = edge_failures / (n_non_conv + _EPS) if n_non_conv > 0 else 0.0

    return BasinSweepResult(
        S_values=S_arr,
        A_values=A_arr,
        Q_values=Q_arr,
        phi_star=phi_star_arr,
        converged=converged_arr,
        n_iters=n_iters_arr,
        residual_histories=residual_histories,
        convergence_rate=conv_rate,
        phi_star_mean=mu,
        phi_star_std=sigma,
        phi_star_min=pmin,
        phi_star_max=pmax,
        phi_star_spread_pct=spread_pct,
        edge_failure_fraction=edge_fail_frac,
    )


def _edge_mask(nS: int, nA: int, nQ: int) -> np.ndarray:
    """Return a bool array (nS, nA, nQ) that is True at grid boundary cells."""
    mask = np.zeros((nS, nA, nQ), dtype=bool)
    if nS > 0:
        mask[0, :, :] = True
        mask[-1, :, :] = True
    if nA > 0:
        mask[:, 0, :] = True
        mask[:, -1, :] = True
    if nQ > 0:
        mask[:, :, 0] = True
        mask[:, :, -1] = True
    return mask


# ---------------------------------------------------------------------------
# 2. classify_non_convergent
# ---------------------------------------------------------------------------

def classify_non_convergent(
    residuals: Sequence[float],
    tol: float = _DEFAULT_TOL,
    oscillation_window: int = 10,
    divergence_ratio: float = 2.0,
) -> str:
    """Classify a non-convergent residual history into a failure mode.

    Parameters
    ----------
    residuals         : sequence of per-iteration defect values.
    tol               : convergence tolerance (same as fixed_point_iteration).
    oscillation_window: number of tail iterations to examine for oscillation.
    divergence_ratio  : if final/initial residual exceeds this, classify as
                        divergent.

    Returns
    -------
    str: one of ``"limit_cycle"``, ``"divergent"``, or ``"slow"``.
    """
    r = np.asarray(residuals, dtype=float)
    if len(r) == 0:
        return "slow"

    # Divergence: final residual substantially larger than initial
    if r[-1] > divergence_ratio * (r[0] + _EPS):
        return "divergent"

    # Limit cycle: tail oscillates (alternating sign of differences)
    if len(r) >= oscillation_window:
        tail = r[-oscillation_window:]
        diffs = np.diff(tail)
        sign_changes = int(np.sum(np.diff(np.sign(diffs)) != 0))
        # If more than half the tail differences alternate sign → oscillation
        if sign_changes >= oscillation_window // 2:
            return "limit_cycle"

    # Default: residual is decreasing but slowly
    return "slow"


# ---------------------------------------------------------------------------
# 3. sensitivity_sweep
# ---------------------------------------------------------------------------

def sensitivity_sweep(
    S0: float,
    A0: float,
    Q_top: float = 0.0,
    eps: float = 1e-3,
    n_perturbations: int = 50,
    fractal_threshold: float = 0.20,
    n_nodes: int = _DEFAULT_N_NODES,
    coupling: float = _DEFAULT_COUPLING,
    max_iter: int = _DEFAULT_MAX_ITER,
    tol: float = _DEFAULT_TOL,
    dt: float = _DEFAULT_DT,
    kappa: float = _DEFAULT_KAPPA,
    gamma: float = _DEFAULT_GAMMA,
    G4: float = _DEFAULT_G4,
    rng: Optional[np.random.Generator] = None,
) -> SensitivityResult:
    """Test for fractal basin boundaries around a given initial condition.

    Runs the nominal initial condition and ``n_perturbations`` micro-perturbed
    variants (each perturbed by at most ±ε in S₀ and A₀).  A high fraction of
    perturbed runs that *flip* between convergent and non-convergent compared to
    the nominal run signals that the initial condition lies near a fractal basin
    boundary.

    Parameters
    ----------
    S0, A0, Q_top    : nominal initial condition.
    eps              : maximum absolute perturbation applied to S₀ and A₀.
    n_perturbations  : number of perturbed runs to perform.
    fractal_threshold: flip_fraction above this value → classified as fractal.
    n_nodes, coupling, max_iter, tol, dt, kappa, gamma, G4 : FTUM parameters.
    rng              : optional RNG.

    Returns
    -------
    SensitivityResult
    """
    if rng is None:
        rng = np.random.default_rng(0)

    def _run(S_init: float, A_init: float) -> Tuple[bool, float]:
        """Return (converged, phi_star) for given init."""
        nodes = [
            MultiverseNode(
                dim=4,
                S=max(S_init, _EPS),
                A=max(A_init, _EPS),
                Q_top=float(Q_top),
                X=np.zeros(4),
                Xdot=np.zeros(4),
            )
            for _ in range(n_nodes)
        ]
        adj = np.zeros((n_nodes, n_nodes))
        for k in range(n_nodes - 1):
            adj[k, k + 1] = adj[k + 1, k] = coupling
        net = MultiverseNetwork(nodes=nodes, adjacency=adj)
        final_net, _, conv = fixed_point_iteration(
            net, max_iter=max_iter, tol=tol, dt=dt,
            G4=G4, kappa=kappa, gamma=gamma,
        )
        phi = float(np.mean([nd.S for nd in final_net.nodes])) if conv else float("nan")
        return conv, phi

    # Nominal run
    nom_conv, nom_phi = _run(S0, A0)

    # Perturbed runs
    phi_star_list: List[float] = []
    flip_count = 0
    for _ in range(n_perturbations):
        dS = rng.uniform(-eps, eps)
        dA = rng.uniform(-eps, eps)
        conv_p, phi_p = _run(S0 + dS, A0 + dA)
        phi_star_list.append(phi_p)
        if conv_p != nom_conv:
            flip_count += 1

    flip_fraction = flip_count / (n_perturbations + _EPS)
    is_fractal = flip_fraction > fractal_threshold

    if is_fractal:
        stability_class = "fractal"
    elif flip_fraction > 0.05:
        stability_class = "marginal"
    else:
        stability_class = "stable"

    return SensitivityResult(
        S0=float(S0),
        A0=float(A0),
        Q_top=float(Q_top),
        nominal_converged=nom_conv,
        nominal_phi_star=nom_phi,
        flip_fraction=float(flip_fraction),
        is_fractal_boundary=is_fractal,
        phi_star_perturbed=np.array(phi_star_list),
        stability_class=stability_class,
    )


# ---------------------------------------------------------------------------
# 4. bifurcation_scan
# ---------------------------------------------------------------------------

def bifurcation_scan(
    param_name: str,
    param_values: Sequence[float],
    S0: float = 1.0,
    A0: float = 1.0,
    Q_top: float = 0.0,
    n_nodes: int = _DEFAULT_N_NODES,
    max_iter: int = _DEFAULT_MAX_ITER,
    tol: float = _DEFAULT_TOL,
    dt: float = _DEFAULT_DT,
    kappa: float = _DEFAULT_KAPPA,
    gamma: float = _DEFAULT_GAMMA,
    coupling: float = _DEFAULT_COUPLING,
    G4: float = _DEFAULT_G4,
) -> BifurcationResult:
    """Scan a secondary parameter and detect bifurcation points in φ*.

    At each value of ``param_name`` the other parameters are held fixed.
    Supported parameters: ``"coupling"``, ``"kappa"``, ``"dt"``, ``"Q_top"``.

    A **bifurcation point** is detected where the absolute jump in φ* between
    consecutive parameter values exceeds 3× the median absolute difference
    (MAD) across the scan.

    Parameters
    ----------
    param_name   : one of ``"coupling"``, ``"kappa"``, ``"dt"``, ``"Q_top"``.
    param_values : 1-D sequence of parameter values to scan.
    S0, A0, Q_top: base initial condition (Q_top is overridden if scanned).
    n_nodes, max_iter, tol, dt, kappa, gamma, coupling, G4 : base FTUM params.

    Returns
    -------
    BifurcationResult
    """
    supported = {"coupling", "kappa", "dt", "Q_top"}
    if param_name not in supported:
        raise ValueError(
            f"param_name must be one of {supported}; got {param_name!r}."
        )

    pv = np.asarray(param_values, dtype=float)
    phi_arr = np.full(len(pv), np.nan)
    conv_arr = np.zeros(len(pv), dtype=bool)

    for pi, pval in enumerate(pv):
        # Override the scanned parameter
        run_coupling = pval if param_name == "coupling" else coupling
        run_kappa = pval if param_name == "kappa" else kappa
        run_dt = pval if param_name == "dt" else dt
        run_Q_top = pval if param_name == "Q_top" else Q_top

        n = n_nodes
        nodes = [
            MultiverseNode(
                dim=4,
                S=float(S0),
                A=float(A0),
                Q_top=float(run_Q_top),
                X=np.zeros(4),
                Xdot=np.zeros(4),
            )
            for _ in range(n)
        ]
        adj = np.zeros((n, n))
        for k in range(n - 1):
            adj[k, k + 1] = adj[k + 1, k] = run_coupling
        net = MultiverseNetwork(nodes=nodes, adjacency=adj)

        final_net, _, conv = fixed_point_iteration(
            net, max_iter=max_iter, tol=tol, dt=run_dt,
            G4=G4, kappa=run_kappa, gamma=gamma,
        )
        conv_arr[pi] = conv
        if conv:
            phi_arr[pi] = float(np.mean([nd.S for nd in final_net.nodes]))

    # Detect bifurcation points: large jumps in φ*
    valid = ~np.isnan(phi_arr)
    bif_indices: List[int] = []
    bif_values: List[float] = []

    if valid.sum() >= 2:
        diffs = np.abs(np.diff(phi_arr[valid]))
        mad = float(np.median(diffs)) if len(diffs) > 0 else 0.0
        threshold = 3.0 * mad if mad > 0 else (np.max(diffs) * 0.5 if len(diffs) > 0 else 0.0)
        # Map back to original indices
        valid_indices = np.where(valid)[0]
        for j, d in enumerate(diffs):
            if d > threshold:
                idx = int(valid_indices[j])
                bif_indices.append(idx)
                bif_values.append(float(pv[idx]))

    return BifurcationResult(
        param_name=param_name,
        param_values=pv,
        phi_star=phi_arr,
        converged=conv_arr,
        bifurcation_indices=bif_indices,
        bifurcation_values=bif_values,
        n_bifurcations=len(bif_indices),
    )


# ---------------------------------------------------------------------------
# 5. topological_invariant_check
# ---------------------------------------------------------------------------

def topological_invariant_check(
    sweep: BasinSweepResult,
) -> InvariantResult:
    """Search for quantities that remain constant across different φ* values.

    For each converged initial condition (S₀, A₀, Q_top) and its associated
    φ* (mean converged entropy), computes several candidate invariant
    quantities and reports the coefficient of variation (CV = σ/|μ|) for each.
    A low CV indicates a quantity that barely changes even as φ* varies widely.

    Candidates tested
    -----------------
    ``phi_star / A0``          — φ* normalised by initial area
    ``phi_star * A0``          — product
    ``phi_star / S0``          — φ* normalised by initial entropy
    ``phi_star / (S0 + A0)``   — normalised by initial sum
    ``phi_star * S0 / A0``     — weighted ratio
    ``(phi_star - S0) / A0``   — entropy excess relative to area

    Parameters
    ----------
    sweep : BasinSweepResult from ``basin_of_attraction_sweep``.

    Returns
    -------
    InvariantResult
    """
    # Collect (S0, A0, phi*) for each converged case
    S_arr, A_arr, Q_arr = sweep.S_values, sweep.A_values, sweep.Q_values
    nS, nA, nQ = len(S_arr), len(A_arr), len(Q_arr)

    S0_list: List[float] = []
    A0_list: List[float] = []
    phi_list: List[float] = []

    for si, S0 in enumerate(S_arr):
        for ai, A0 in enumerate(A_arr):
            for qi in range(nQ):
                if sweep.converged[si, ai, qi]:
                    S0_list.append(float(S0))
                    A0_list.append(float(A0))
                    phi_list.append(float(sweep.phi_star[si, ai, qi]))

    if len(phi_list) < 2:
        return InvariantResult(
            candidate_names=[],
            cv_values={},
            best_candidate="(none — insufficient converged cases)",
            best_cv=float("nan"),
            invariant_found=False,
            interpretation="Fewer than 2 converged cases; cannot assess invariants.",
        )

    S0_arr = np.array(S0_list)
    A0_arr = np.array(A0_list)
    phi_arr = np.array(phi_list)

    candidates: Dict[str, np.ndarray] = {
        "phi_star / A0":          phi_arr / (A0_arr + _EPS),
        "phi_star * A0":          phi_arr * A0_arr,
        "phi_star / S0":          phi_arr / (S0_arr + _EPS),
        "phi_star / (S0 + A0)":   phi_arr / (S0_arr + A0_arr + _EPS),
        "phi_star * S0 / A0":     phi_arr * S0_arr / (A0_arr + _EPS),
        "(phi_star - S0) / A0":   (phi_arr - S0_arr) / (A0_arr + _EPS),
    }

    cv_values: Dict[str, float] = {}
    for name, vals in candidates.items():
        mu = float(np.mean(vals))
        sigma = float(np.std(vals))
        cv_values[name] = sigma / (abs(mu) + _EPS)

    best_name = min(cv_values, key=lambda k: cv_values[k])
    best_cv = cv_values[best_name]
    found = best_cv < 0.10   # within 10 %

    if found:
        interp = (
            f"Relative fixed point found: '{best_name}' has CV = {best_cv:.4f} "
            f"(< 10 %).  φ* varies by ±{100*float(np.std(phi_arr)/np.mean(phi_arr)):.1f}% "
            f"in absolute value, but this ratio stays nearly constant — consistent "
            f"with a geometric constraint selecting a relative, not absolute, "
            f"fixed point."
        )
    else:
        interp = (
            f"No strong relative fixed point found (best CV = {best_cv:.4f} "
            f"for '{best_name}', threshold 0.10).  The geometry is not "
            f"selecting a conserved ratio across initial conditions; the "
            f"fixed-point attractor is path-dependent."
        )

    return InvariantResult(
        candidate_names=list(candidates.keys()),
        cv_values=cv_values,
        best_candidate=best_name,
        best_cv=best_cv,
        invariant_found=found,
        interpretation=interp,
    )


# ---------------------------------------------------------------------------
# 6. near_miss_analysis
# ---------------------------------------------------------------------------

def near_miss_analysis(
    residual_histories: Sequence[Sequence[float]],
    tol: float = _DEFAULT_TOL,
    near_miss_band: float = 10.0,
    oscillation_window: int = 10,
) -> NearMissResult:
    """Detect near-miss oscillation in a collection of residual histories.

    A history is classified as a **near miss** if its final residual lies in
    the band (tol, near_miss_band × tol) — i.e., it almost converged but
    didn't, and the tail is oscillating rather than monotonically decreasing.

    Parameters
    ----------
    residual_histories : list of per-run residual lists.
    tol               : convergence tolerance (histories that end below this
                        are treated as converged and excluded from analysis).
    near_miss_band    : multiplier; histories ending below ``near_miss_band×tol``
                        but above ``tol`` are "near misses".
    oscillation_window: number of tail iterations to examine for oscillation.

    Returns
    -------
    NearMissResult
    """
    classifications: List[str] = []
    near_miss_count = 0
    limit_cycle_count = 0
    divergent_count = 0
    slow_count = 0
    oscillation_amplitudes: List[float] = []

    for hist in residual_histories:
        r = np.asarray(hist, dtype=float)
        if len(r) == 0:
            classifications.append("slow")
            slow_count += 1
            continue

        final = r[-1]
        if final <= tol:
            classifications.append("converged")
            continue

        cls = classify_non_convergent(r, tol=tol, oscillation_window=oscillation_window)
        classifications.append(cls)

        if cls == "limit_cycle":
            limit_cycle_count += 1
        elif cls == "divergent":
            divergent_count += 1
        else:
            slow_count += 1

        # Near-miss: ended close to tolerance
        if tol < final <= near_miss_band * tol:
            near_miss_count += 1

        # Oscillation amplitude in the tail
        if len(r) >= oscillation_window:
            tail = r[-oscillation_window:]
            amplitudes = np.abs(np.diff(tail))
            if len(amplitudes) > 0:
                oscillation_amplitudes.append(float(np.max(amplitudes)) / (tol + _EPS))

    n_total = len(residual_histories)
    near_miss_frac = near_miss_count / (n_total + _EPS)
    med_amp = float(np.median(oscillation_amplitudes)) if oscillation_amplitudes else 0.0

    return NearMissResult(
        n_total=n_total,
        n_near_miss=near_miss_count,
        near_miss_fraction=near_miss_frac,
        n_limit_cycle=limit_cycle_count,
        n_divergent=divergent_count,
        n_slow=slow_count,
        classifications=classifications,
        median_oscillation_amplitude=med_amp,
    )


# ---------------------------------------------------------------------------
# 7. convergence_time_analysis
# ---------------------------------------------------------------------------

@dataclass
class ConvergenceTimeResult:
    """Results of time-to-convergence (TTC) analysis.

    Distinguishes "hard fail" (system structurally cannot converge) from
    "slow crawl" (system would converge given more iterations).

    Attributes
    ----------
    n_converged        : number of cases that converged.
    n_hard_fail        : non-convergent cases classified as divergent or
                         limit_cycle — structural failures.
    n_slow_crawl       : non-convergent cases classified as slow — likely
                         convergent given more iterations.
    hard_fail_fraction : n_hard_fail / n_non_convergent.
    slow_crawl_fraction: n_slow_crawl / n_non_convergent.
    ttc_converged      : 1-D array of iteration counts for converged cases.
    ttc_mean           : mean iterations-to-convergence.
    ttc_median         : median iterations-to-convergence.
    ttc_max            : maximum (slowest converged case).
    ttc_boundary_mean  : mean TTC for converged cells adjacent to a
                         non-convergent cell (boundary cells).
    ttc_interior_mean  : mean TTC for converged cells not adjacent to any
                         non-convergent cell (interior cells).
    critical_slowing   : bool — True if boundary TTC > 2× interior TTC,
                         indicating critical slowing down near the boundary.
    power_law_exponent : float — exponent α of the best-fit power law
                         n_iters ∝ distance^{-α} near the boundary, or NaN
                         if there are fewer than 3 boundary points.
    power_law_r2       : float — R² of that fit (0–1; higher = better fit).
    non_convergent_classes : dict mapping classification → count for all
                         non-convergent cases.
    """
    n_converged: int
    n_hard_fail: int
    n_slow_crawl: int
    hard_fail_fraction: float
    slow_crawl_fraction: float
    ttc_converged: np.ndarray
    ttc_mean: float
    ttc_median: float
    ttc_max: int
    ttc_boundary_mean: float
    ttc_interior_mean: float
    critical_slowing: bool
    power_law_exponent: float
    power_law_r2: float
    non_convergent_classes: Dict[str, int]


def convergence_time_analysis(
    sweep: BasinSweepResult,
    tol: float = _DEFAULT_TOL,
    boundary_ttc_ratio: float = 2.0,
) -> ConvergenceTimeResult:
    """Analyse the distribution of iterations-to-convergence across a sweep.

    Separates the 17.2 % non-convergent cases into **hard fails** (divergent
    or limit-cycle — structurally unable to converge) and **slow crawls**
    (monotone decrease that merely ran out of iterations — would likely
    converge with a larger ``max_iter`` budget).

    Also tests for **critical slowing down** near the basin boundary: if
    converged cells adjacent to non-convergent cells take significantly more
    iterations than interior converged cells, the system exhibits the
    divergence of relaxation time characteristic of a continuous phase
    transition or fractal basin boundary.

    A power-law fit  n_iters ∝ d^{-α}  (where d is the Euclidean distance
    in (S₀, A₀) space to the nearest non-convergent cell) is performed on
    boundary-adjacent converged cells.  An exponent α > 0 and R² > 0.5
    strongly suggests a **critical transition point** rather than a simple
    domain wall.

    Parameters
    ----------
    sweep              : BasinSweepResult from ``basin_of_attraction_sweep``.
    tol                : convergence tolerance (for classify_non_convergent).
    boundary_ttc_ratio : threshold ratio boundary_mean / interior_mean above
                         which ``critical_slowing`` is flagged (default 2.0).

    Returns
    -------
    ConvergenceTimeResult
    """
    S_arr, A_arr, Q_arr = sweep.S_values, sweep.A_values, sweep.Q_values
    nS, nA, nQ = len(S_arr), len(A_arr), len(Q_arr)
    conv = sweep.converged
    n_iters = sweep.n_iters

    # ----- classify non-convergent histories --------------------------------
    non_conv_classes: Dict[str, int] = {"divergent": 0, "limit_cycle": 0, "slow": 0}
    flat_idx = 0
    hard_fail_mask = np.zeros((nS, nA, nQ), dtype=bool)
    slow_crawl_mask = np.zeros((nS, nA, nQ), dtype=bool)

    for si in range(nS):
        for ai in range(nA):
            for qi in range(nQ):
                hist = sweep.residual_histories[flat_idx]
                flat_idx += 1
                if conv[si, ai, qi]:
                    continue
                cls = classify_non_convergent(hist, tol=tol)
                non_conv_classes[cls] = non_conv_classes.get(cls, 0) + 1
                if cls in ("divergent", "limit_cycle"):
                    hard_fail_mask[si, ai, qi] = True
                else:
                    slow_crawl_mask[si, ai, qi] = True

    n_non_conv = int((~conv).sum())
    n_hard = int(hard_fail_mask.sum())
    n_slow = int(slow_crawl_mask.sum())
    hard_frac = n_hard / (n_non_conv + _EPS)
    slow_frac = n_slow / (n_non_conv + _EPS)

    # ----- TTC statistics for converged cases --------------------------------
    ttc_conv = n_iters[conv].astype(int)
    n_converged = int(conv.sum())

    if n_converged > 0:
        ttc_mean = float(np.mean(ttc_conv))
        ttc_median = float(np.median(ttc_conv))
        ttc_max = int(np.max(ttc_conv))
    else:
        ttc_mean = ttc_median = float("nan")
        ttc_max = 0

    # ----- boundary vs interior TTC -----------------------------------------
    # A converged cell is "boundary-adjacent" if any of its 6-connected
    # neighbours in (si, ai, qi) space is non-convergent.
    boundary_ttc: List[float] = []
    interior_ttc: List[float] = []
    boundary_dist: List[float] = []   # distance to nearest non-convergent cell
    boundary_ttc_vals: List[float] = []

    # Precompute (S, A) coordinates for distance calculation
    coords_SA = {}
    for si, S0 in enumerate(S_arr):
        for ai, A0 in enumerate(A_arr):
            for qi in range(nQ):
                coords_SA[(si, ai, qi)] = np.array([float(S0), float(A0)])

    for si in range(nS):
        for ai in range(nA):
            for qi in range(nQ):
                if not conv[si, ai, qi]:
                    continue
                # Check 6-connected neighbours
                neighbours = [
                    (si - 1, ai, qi), (si + 1, ai, qi),
                    (ai - 1, si, qi), (ai + 1, si, qi),
                    (si, ai, qi - 1), (si, ai, qi + 1),
                ]
                is_boundary = False
                for ns, na, nq in [(si-1,ai,qi),(si+1,ai,qi),
                                   (si,ai-1,qi),(si,ai+1,qi),
                                   (si,ai,qi-1),(si,ai,qi+1)]:
                    if 0 <= ns < nS and 0 <= na < nA and 0 <= nq < nQ:
                        if not conv[ns, na, nq]:
                            is_boundary = True
                            break
                t = float(n_iters[si, ai, qi])
                if is_boundary:
                    boundary_ttc.append(t)
                    # Distance to nearest non-convergent cell centre in (S,A) space
                    my_coord = coords_SA[(si, ai, qi)]
                    dists = []
                    for ns2 in range(nS):
                        for na2 in range(nA):
                            for nq2 in range(nQ):
                                if not conv[ns2, na2, nq2]:
                                    dists.append(float(np.linalg.norm(
                                        my_coord - coords_SA[(ns2, na2, nq2)]
                                    )))
                    if dists:
                        d = min(dists)
                        boundary_dist.append(d)
                        boundary_ttc_vals.append(t)
                else:
                    interior_ttc.append(t)

    bnd_mean = float(np.mean(boundary_ttc)) if boundary_ttc else float("nan")
    int_mean = float(np.mean(interior_ttc)) if interior_ttc else float("nan")
    critical = (
        (bnd_mean > boundary_ttc_ratio * int_mean)
        if (np.isfinite(bnd_mean) and np.isfinite(int_mean) and int_mean > 0)
        else False
    )

    # ----- power-law fit: n_iters ∝ d^{-α} ---------------------------------
    # Linearise: log(n_iters) = -α log(d) + const → OLS on (log d, log n)
    pl_exp = float("nan")
    pl_r2 = float("nan")
    if len(boundary_dist) >= 3:
        log_d = np.log(np.array(boundary_dist) + _EPS)
        log_t = np.log(np.array(boundary_ttc_vals) + _EPS)
        # OLS: log_t = a * log_d + b
        A_mat = np.column_stack([log_d, np.ones(len(log_d))])
        try:
            coeffs, *_ = np.linalg.lstsq(A_mat, log_t, rcond=None)
            a_coef = float(coeffs[0])
            pl_exp = -a_coef   # n ∝ d^{a} → power-law exponent is -a
            # R²
            log_t_pred = A_mat @ coeffs
            ss_res = float(np.sum((log_t - log_t_pred) ** 2))
            ss_tot = float(np.sum((log_t - np.mean(log_t)) ** 2))
            pl_r2 = 1.0 - ss_res / (ss_tot + _EPS)
        except np.linalg.LinAlgError:
            pass

    return ConvergenceTimeResult(
        n_converged=n_converged,
        n_hard_fail=n_hard,
        n_slow_crawl=n_slow,
        hard_fail_fraction=hard_frac,
        slow_crawl_fraction=slow_frac,
        ttc_converged=ttc_conv,
        ttc_mean=ttc_mean,
        ttc_median=ttc_median,
        ttc_max=ttc_max,
        ttc_boundary_mean=bnd_mean,
        ttc_interior_mean=int_mean,
        critical_slowing=critical,
        power_law_exponent=pl_exp,
        power_law_r2=pl_r2,
        non_convergent_classes=non_conv_classes,
    )


# ---------------------------------------------------------------------------
# 8. boundary_zoom_sweep
# ---------------------------------------------------------------------------

@dataclass
class BoundaryZoomResult:
    """Results of a recursive high-resolution boundary zoom sweep.

    Attributes
    ----------
    coarse_sweep   : the original ``BasinSweepResult`` passed in.
    zoom_sweep     : the high-resolution ``BasinSweepResult`` around the
                     boundary region.
    S_zoom_range   : (S_min, S_max) of the zoomed grid.
    A_zoom_range   : (A_min, A_max) of the zoomed grid.
    boundary_cells : list of (si, ai, qi) index triples in the coarse sweep
                     that were identified as boundary-adjacent.
    n_boundary_cells : number of coarse boundary cells found.
    zoom_convergence_rate : convergence rate of the zoom sweep.
    zoom_phi_star_spread_pct : φ* spread in the zoomed region.
    boundary_is_smooth : bool — True if the zoom sweep shows a clean
                     monotone transition (no interleaved convergent/
                     non-convergent cells), False if it is fractal-like.
    """
    coarse_sweep: BasinSweepResult
    zoom_sweep: BasinSweepResult
    S_zoom_range: Tuple[float, float]
    A_zoom_range: Tuple[float, float]
    boundary_cells: List[Tuple[int, int, int]]
    n_boundary_cells: int
    zoom_convergence_rate: float
    zoom_phi_star_spread_pct: float
    boundary_is_smooth: bool


def boundary_zoom_sweep(
    coarse_sweep: BasinSweepResult,
    zoom_resolution: int = 12,
    padding_fraction: float = 0.25,
    max_iter: int = _DEFAULT_MAX_ITER,
    tol: float = _DEFAULT_TOL,
    dt: float = _DEFAULT_DT,
    kappa: float = _DEFAULT_KAPPA,
    gamma: float = _DEFAULT_GAMMA,
    n_nodes: int = _DEFAULT_N_NODES,
    coupling: float = _DEFAULT_COUPLING,
    G4: float = _DEFAULT_G4,
    rng: Optional[np.random.Generator] = None,
) -> BoundaryZoomResult:
    """Recursively zoom into the convergence/divergence boundary region.

    Identifies all boundary-adjacent cells in ``coarse_sweep`` (converged
    cells with at least one non-convergent neighbour, or vice-versa),
    computes the bounding box of those cells in (S₀, A₀) space, pads it
    by ``padding_fraction``, then runs a new higher-resolution sweep
    (``zoom_resolution × zoom_resolution`` grid) within that box.

    This directly answers the architecture question: **yes, the existing
    ``basin_of_attraction_sweep`` naturally supports recursive zooming**
    because it accepts arbitrary (S_values, A_values) grids.  This function
    is the thin wrapper that computes the zoom box automatically.

    The boundary smoothness test checks whether the zoomed grid contains any
    "checkerboard" pattern — a converged cell immediately adjacent to a
    non-convergent cell in the same row or column.  A smooth boundary would
    show a clean half-plane split; a fractal boundary shows interleaving.

    Parameters
    ----------
    coarse_sweep      : a completed ``BasinSweepResult``.
    zoom_resolution   : number of grid points per axis in the zoom sweep.
    padding_fraction  : fractional padding added around the boundary bounding
                        box (default 0.25 = 25 %).
    max_iter, tol, dt, kappa, gamma, n_nodes, coupling, G4
                      : FTUM parameters forwarded to the zoom sweep.
    rng               : optional RNG.

    Returns
    -------
    BoundaryZoomResult
    """
    if rng is None:
        rng = np.random.default_rng(42)

    S_arr = coarse_sweep.S_values
    A_arr = coarse_sweep.A_values
    conv = coarse_sweep.converged
    nS, nA, nQ = conv.shape

    # ----- find boundary cells in coarse sweep ------------------------------
    boundary_cells: List[Tuple[int, int, int]] = []
    for si in range(nS):
        for ai in range(nA):
            for qi in range(nQ):
                this_conv = conv[si, ai, qi]
                for ns, na, nq in [(si-1,ai,qi),(si+1,ai,qi),
                                   (si,ai-1,qi),(si,ai+1,qi),
                                   (si,ai,qi-1),(si,ai,qi+1)]:
                    if 0 <= ns < nS and 0 <= na < nA and 0 <= nq < nQ:
                        if conv[ns, na, nq] != this_conv:
                            boundary_cells.append((si, ai, qi))
                            break

    if not boundary_cells:
        # No boundary found — use full coarse extent as fallback
        S_min, S_max = float(S_arr[0]), float(S_arr[-1])
        A_min, A_max = float(A_arr[0]), float(A_arr[-1])
    else:
        S_boundary = [float(S_arr[si]) for si, ai, qi in boundary_cells]
        A_boundary = [float(A_arr[ai]) for si, ai, qi in boundary_cells]
        S_min, S_max = min(S_boundary), max(S_boundary)
        A_min, A_max = min(A_boundary), max(A_boundary)

    # Add padding
    S_range = max(S_max - S_min, float(np.diff(S_arr).mean()) if len(S_arr) > 1 else 1.0)
    A_range = max(A_max - A_min, float(np.diff(A_arr).mean()) if len(A_arr) > 1 else 1.0)
    pad_S = padding_fraction * S_range
    pad_A = padding_fraction * A_range
    S_min_zoom = max(float(S_arr[0]), S_min - pad_S)
    S_max_zoom = min(float(S_arr[-1]), S_max + pad_S)
    A_min_zoom = max(float(A_arr[0]), A_min - pad_A)
    A_max_zoom = min(float(A_arr[-1]), A_max + pad_A)

    # Ensure range is non-degenerate
    if S_max_zoom <= S_min_zoom:
        S_min_zoom = float(S_arr[0])
        S_max_zoom = float(S_arr[-1])
    if A_max_zoom <= A_min_zoom:
        A_min_zoom = float(A_arr[0])
        A_max_zoom = float(A_arr[-1])

    S_zoom = np.linspace(S_min_zoom, S_max_zoom, zoom_resolution)
    A_zoom = np.linspace(A_min_zoom, A_max_zoom, zoom_resolution)

    zoom = basin_of_attraction_sweep(
        S_values=S_zoom,
        A_values=A_zoom,
        Q_values=coarse_sweep.Q_values,
        n_nodes=n_nodes,
        coupling=coupling,
        max_iter=max_iter,
        tol=tol,
        dt=dt,
        kappa=kappa,
        gamma=gamma,
        G4=G4,
        rng=rng,
    )

    # ----- boundary smoothness test -----------------------------------------
    # Smooth: in every row (fixed A) and column (fixed S), convergence flips
    # at most once. Fractal: multiple flips occur.
    nSz, nAz, nQz = zoom.converged.shape
    max_flips_per_line = 0
    for ai in range(nAz):
        for qi in range(nQz):
            row = zoom.converged[:, ai, qi].astype(int)
            flips = int(np.sum(np.abs(np.diff(row))))
            max_flips_per_line = max(max_flips_per_line, flips)
    for si in range(nSz):
        for qi in range(nQz):
            col = zoom.converged[si, :, qi].astype(int)
            flips = int(np.sum(np.abs(np.diff(col))))
            max_flips_per_line = max(max_flips_per_line, flips)

    boundary_is_smooth = max_flips_per_line <= 1

    return BoundaryZoomResult(
        coarse_sweep=coarse_sweep,
        zoom_sweep=zoom,
        S_zoom_range=(S_min_zoom, S_max_zoom),
        A_zoom_range=(A_min_zoom, A_max_zoom),
        boundary_cells=boundary_cells,
        n_boundary_cells=len(boundary_cells),
        zoom_convergence_rate=zoom.convergence_rate,
        zoom_phi_star_spread_pct=zoom.phi_star_spread_pct,
        boundary_is_smooth=boundary_is_smooth,
    )
