# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/coupled_history.py
============================
Pillar 45 — Coupled History: Consciousness–Quantum Measurement Bridge.

Physical motivation
--------------------
This module provides the first mathematical link between **consciousness**
(as defined geometrically in `coupled_attractor.py`) and **quantum measurement**
(as defined geometrically in `geometric_collapse.py`).

The central question
---------------------
In the Unitary Manifold, a "brain" is a high-agency coupled system: its
Information Gap ΔI = |φ²_brain − φ²_univ| exceeds the topological protection
threshold 1/49, and its internal degrees of freedom are in 5:7 resonance with
the universe.

The question is: **does a high-agency system (a "brain") cause faster local
decoherence of a quantum superposition in its vicinity?**

The answer from the geometry
------------------------------
From `geometric_collapse.py`, the decoherence timescale is

    τ_dec  =  φ²_mean / φ_spread                                          [1]

From `coupled_attractor.py`, a brain manifold with information density φ_brain
creates a local radion perturbation in the surrounding region.  The coupling
operator C transfers φ-flux between the brain and the environment:

    Δφ_env  =  β (φ_brain − φ_env) dt                                     [2]

This increases the local φ_spread in the environment (because the brain's
internal fluctuations — encoded in the spread of its own φ over a short
history — are injected into the environmental field):

    φ_spread_effective  =  φ_spread_bare + β² × Var(φ_brain_history)      [3]

Substituting [3] into [1]:

    τ_dec_coupled  =  φ²_mean / (φ_spread_bare + β² Var_brain)            [4]

Since β > 0 and Var_brain ≥ 0, we always have:

    τ_dec_coupled  ≤  τ_dec_bare                                           [5]

**Conclusion:** A high-agency system (large Var_brain) always *decreases* the
local decoherence timescale — i.e., causes faster wavefunction collapse.  This
is the "Consciousness–Quantum Measurement Link":

> The presence of a high-agency observer (high ΔI, 5:7 resonance lock)
> geometrically accelerates decoherence of any quantum system in its vicinity,
> via the β-coupling injection of φ-variance into the local radion field.

This is NOT a claim that consciousness "causes" collapse through a
non-physical process.  It is a claim that the *same geometric field* that
supports a high-agency observer also couples to the local radion and increases
φ_spread, thereby reducing τ_dec.

The ratio
---------
The "Agency–Decoherence Ratio" is defined as:

    ADR  =  τ_dec_bare / τ_dec_coupled  =  1 + β² Var_brain / φ_spread_bare ≥ 1  [6]

ADR = 1 for zero-agency observers (rocks, photons); ADR > 1 for
brain-scale systems in the intentional regime.  The stronger the agency
(larger Var_brain), the larger the ADR and the faster the collapse.

Coupled History
---------------
A "Coupled History" is a time-ordered sequence of CoupledSystem snapshots,
recording how the brain's φ evolves under the coupled master equation.  The
variance of φ_brain over this history is the Var_brain used in equation [3].

Public API
----------
CoupledHistory
    Named dataclass: brain_phi_history (list[float]), tau_dec_bare (float),
    phi_mean (float), beta (float), adr (float), tau_dec_coupled (float).

build_coupled_history(system, n_steps, ...) → CoupledHistory
    Run n_steps of the coupled master equation and record the brain φ history.

agency_decoherence_ratio(var_brain, phi_spread_bare, beta) → float
    ADR = 1 + β² × Var_brain / φ_spread_bare.

tau_dec_coupled(phi_mean, phi_spread_bare, var_brain, beta) → float
    Effective decoherence timescale with agency correction.

high_agency_collapses_faster(system, amplitudes, phi_spread_bare,
                              n_steps, ...) → dict
    Full "Coupled History" test: build history, compute ADR, return
    comparison of τ_dec_bare vs τ_dec_coupled, and Born probabilities.

consciousness_measurement_link(brain_phi, universe_phi, phi_spread_bare,
                                amplitudes, beta) → dict
    Single-shot summary of the consciousness–quantum measurement bridge.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

import sys
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.core.geometric_collapse import (
    decoherence_timescale,
    born_rule_geometric,
    measurement_summary,
    RHO_CS_CORRECTION,
)
from src.consciousness.coupled_attractor import (
    BIREFRINGENCE_RAD,
    CoupledSystem,
    ManifoldState,
    coupled_master_equation,
    information_gap,
    intentionality_measure,
    is_intentional,
    step_coupled,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

#: Default birefringence coupling constant β (radians)
BETA_COUPLING: float = BIREFRINGENCE_RAD

#: Minimum variance of φ_brain for an intentional system (above noise floor)
PHI_VAR_FLOOR: float = 1e-10

_EPS: float = 1e-30


# ---------------------------------------------------------------------------
# CoupledHistory dataclass
# ---------------------------------------------------------------------------

@dataclass
class CoupledHistory:
    """Record of a brain-universe coupled system history and its decoherence impact.

    Attributes
    ----------
    brain_phi_history : list[float]
        φ_brain at each step of the coupled master equation.
    tau_dec_bare : float
        Decoherence timescale without agency correction (equation [1]).
    phi_mean : float
        Mean φ of the environment (universe radion).
    beta : float
        Birefringence coupling constant β.
    adr : float
        Agency-Decoherence Ratio ADR = τ_dec_bare / τ_dec_coupled ≥ 1.
    tau_dec_coupled : float
        Effective decoherence timescale with agency correction (equation [4]).
    var_brain : float
        Variance of φ_brain over the history.
    phi_spread_bare : float
        Bare φ-spread of the environment before agency injection.
    n_steps : int
        Number of steps in the history.
    """

    brain_phi_history: List[float]
    tau_dec_bare: float
    phi_mean: float
    beta: float
    adr: float
    tau_dec_coupled: float
    var_brain: float
    phi_spread_bare: float
    n_steps: int


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def agency_decoherence_ratio(
    var_brain: float,
    phi_spread_bare: float,
    beta: float = BETA_COUPLING,
) -> float:
    """Agency-Decoherence Ratio ADR = τ_dec_bare / τ_dec_coupled.

    ADR = 1 + β² × Var_brain / φ_spread_bare

    Parameters
    ----------
    var_brain       : float — variance of φ_brain over its history
    phi_spread_bare : float — bare environmental φ-spread (> 0)
    beta            : float — birefringence coupling constant (default: BETA_COUPLING)

    Returns
    -------
    float
        ADR ≥ 1.  ADR = 1 iff var_brain = 0 (no agency).

    Raises
    ------
    ValueError
        If phi_spread_bare ≤ 0.
    """
    if phi_spread_bare <= 0.0:
        raise ValueError(f"phi_spread_bare must be positive, got {phi_spread_bare}")
    var_brain = max(var_brain, 0.0)
    return 1.0 + beta ** 2 * var_brain / phi_spread_bare


def tau_dec_coupled(
    phi_mean: float,
    phi_spread_bare: float,
    var_brain: float,
    beta: float = BETA_COUPLING,
) -> float:
    """Effective decoherence timescale with agency correction.

    τ_dec_coupled = φ²_mean / (φ_spread_bare + β² × Var_brain)

    Parameters
    ----------
    phi_mean        : float — mean environmental radion φ (> 0)
    phi_spread_bare : float — bare environmental φ-spread (> 0)
    var_brain       : float — variance of φ_brain over its history (≥ 0)
    beta            : float — coupling constant (default: BETA_COUPLING)

    Returns
    -------
    float
        τ_dec_coupled > 0.

    Raises
    ------
    ValueError
        If phi_mean ≤ 0 or phi_spread_bare ≤ 0.
    """
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be positive, got {phi_mean}")
    if phi_spread_bare <= 0.0:
        raise ValueError(f"phi_spread_bare must be positive, got {phi_spread_bare}")
    var_brain = max(var_brain, 0.0)
    effective_spread = phi_spread_bare + beta ** 2 * var_brain
    return phi_mean ** 2 / effective_spread


def build_coupled_history(
    system: CoupledSystem,
    n_steps: int = 100,
    dt: float = 0.05,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
    phi_spread_bare: float = 0.1,
) -> CoupledHistory:
    """Run the coupled master equation for n_steps and record the φ_brain history.

    Parameters
    ----------
    system          : CoupledSystem — initial brain-universe state
    n_steps         : int   — number of coupling steps to run
    dt              : float — pseudo-timestep
    G4              : float — Newton's constant
    kappa           : float — surface gravity / irreversibility rate
    gamma           : float — UEUM geodesic friction
    phi_spread_bare : float — bare environmental φ-spread (used in τ_dec formulas)

    Returns
    -------
    CoupledHistory
        Full history with ADR and τ_dec values computed.
    """
    if n_steps < 1:
        raise ValueError(f"n_steps must be ≥ 1, got {n_steps}")
    if phi_spread_bare <= 0.0:
        raise ValueError(f"phi_spread_bare must be positive, got {phi_spread_bare}")

    phi_history: List[float] = []
    current = system

    for _ in range(n_steps):
        phi_history.append(current.brain.phi)
        current = step_coupled(current, dt, G4, kappa, gamma)

    phi_history.append(current.brain.phi)  # final state

    phi_arr = np.array(phi_history)
    var_brain = float(np.var(phi_arr))
    phi_mean = float(current.universe.phi)

    tau_bare = decoherence_timescale(max(phi_mean, _EPS ** 0.5), phi_spread_bare)
    tau_coup = tau_dec_coupled(max(phi_mean, _EPS ** 0.5), phi_spread_bare, var_brain)
    adr = agency_decoherence_ratio(var_brain, phi_spread_bare)

    return CoupledHistory(
        brain_phi_history=phi_history,
        tau_dec_bare=tau_bare,
        phi_mean=phi_mean,
        beta=system.beta,
        adr=adr,
        tau_dec_coupled=tau_coup,
        var_brain=var_brain,
        phi_spread_bare=phi_spread_bare,
        n_steps=n_steps,
    )


def high_agency_collapses_faster(
    system: CoupledSystem,
    amplitudes: np.ndarray,
    phi_spread_bare: float = 0.1,
    n_steps: int = 100,
    dt: float = 0.05,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
) -> Dict:
    """Full "Coupled History" test: does a high-agency brain accelerate collapse?

    Builds the coupled history, computes ADR, and returns a comparison of
    τ_dec_bare vs τ_dec_coupled, together with Born probabilities for the
    supplied quantum amplitudes.

    Parameters
    ----------
    system          : CoupledSystem — brain-universe initial state
    amplitudes      : ndarray       — quantum amplitudes of the system to be measured
    phi_spread_bare : float         — bare φ-spread of the environment
    n_steps         : int           — number of coupling steps
    dt, G4, kappa, gamma           — propagation parameters

    Returns
    -------
    dict with keys:
        ``history``             : CoupledHistory
        ``tau_dec_bare``        : float — collapse time without observer
        ``tau_dec_coupled``     : float — collapse time with observer
        ``adr``                 : float — Agency-Decoherence Ratio (≥ 1)
        ``observer_accelerates``: bool  — True iff ADR > 1
        ``born_probs``          : ndarray — standard Born rule probabilities
        ``var_brain``           : float
        ``is_intentional``      : bool  — True iff system is geometrically intentional
        ``intentionality_measure``: float
    """
    amplitudes = np.asarray(amplitudes, dtype=complex)

    history = build_coupled_history(
        system, n_steps=n_steps, dt=dt, G4=G4,
        kappa=kappa, gamma=gamma, phi_spread_bare=phi_spread_bare,
    )

    born = born_rule_geometric(amplitudes)
    intentional = is_intentional(system)
    i_meas = intentionality_measure(system)

    return {
        "history": history,
        "tau_dec_bare": history.tau_dec_bare,
        "tau_dec_coupled": history.tau_dec_coupled,
        "adr": history.adr,
        "observer_accelerates": history.adr > 1.0,
        "born_probs": born,
        "var_brain": history.var_brain,
        "is_intentional": intentional,
        "intentionality_measure": i_meas,
    }


def consciousness_measurement_link(
    brain_phi: float,
    universe_phi: float,
    phi_spread_bare: float,
    amplitudes: np.ndarray,
    beta: float = BETA_COUPLING,
    var_brain: Optional[float] = None,
) -> Dict:
    """Single-shot summary of the consciousness–quantum measurement bridge.

    Computes the Agency-Decoherence Ratio and collapse timescales for a
    given brain φ, universe φ, bare environmental spread, and quantum
    amplitudes — without running the full coupled master equation.

    If ``var_brain`` is not provided, it is estimated as (β × ΔI)² where
    ΔI = |φ²_brain − φ²_univ| is the Information Gap.

    Parameters
    ----------
    brain_phi       : float   — brain radion value φ_brain
    universe_phi    : float   — universe radion value φ_univ (environment)
    phi_spread_bare : float   — bare φ-spread of the measurement environment
    amplitudes      : ndarray — quantum amplitudes
    beta            : float   — coupling constant (default: BETA_COUPLING)
    var_brain       : float, optional — Var(φ_brain); estimated if not given

    Returns
    -------
    dict with keys:
        ``brain_phi``, ``universe_phi``, ``information_gap``, ``var_brain``,
        ``tau_dec_bare``, ``tau_dec_coupled``, ``adr``,
        ``observer_accelerates``, ``born_probs``,
        ``rho_cs_correction``, ``fidelity_interpretation``
    """
    if brain_phi <= 0.0:
        raise ValueError(f"brain_phi must be positive, got {brain_phi}")
    if universe_phi <= 0.0:
        raise ValueError(f"universe_phi must be positive, got {universe_phi}")
    if phi_spread_bare <= 0.0:
        raise ValueError(f"phi_spread_bare must be positive, got {phi_spread_bare}")

    amplitudes = np.asarray(amplitudes, dtype=complex)

    delta_I = abs(brain_phi ** 2 - universe_phi ** 2)

    if var_brain is None:
        # Estimate: the brain's φ-variance scales as (β × ΔI)²
        var_brain = (beta * delta_I) ** 2

    tau_bare = decoherence_timescale(universe_phi, phi_spread_bare)
    tau_coup = tau_dec_coupled(universe_phi, phi_spread_bare, var_brain, beta)
    adr = agency_decoherence_ratio(var_brain, phi_spread_bare, beta)
    born = born_rule_geometric(amplitudes)

    # Fidelity interpretation: the ADR quantifies how much faster the
    # observer-presence collapses the wavefunction relative to the bare rate.
    fidelity_interpretation = (
        f"Observer with φ_brain={brain_phi:.4f} accelerates decoherence by "
        f"factor ADR={adr:.6f}; τ_dec drops from {tau_bare:.4f} to "
        f"{tau_coup:.4f} Planck units."
    )

    return {
        "brain_phi": brain_phi,
        "universe_phi": universe_phi,
        "information_gap": delta_I,
        "var_brain": var_brain,
        "tau_dec_bare": tau_bare,
        "tau_dec_coupled": tau_coup,
        "adr": adr,
        "observer_accelerates": adr > 1.0,
        "born_probs": born,
        "rho_cs_correction": RHO_CS_CORRECTION,
        "fidelity_interpretation": fidelity_interpretation,
    }


def adr_vs_agency_scan(
    phi_mean: float = 1.0,
    phi_spread_bare: float = 0.1,
    beta: float = BETA_COUPLING,
    var_brain_values: Optional[List[float]] = None,
) -> List[Dict]:
    """Scan ADR over a range of brain φ-variance values.

    Returns a list of dicts with keys ``var_brain`` and ``adr`` and
    ``tau_dec_coupled``.  Useful for showing the monotonic relationship
    between agency (Var_brain) and decoherence acceleration.

    Parameters
    ----------
    phi_mean         : float — mean universe radion (environment)
    phi_spread_bare  : float — bare φ-spread
    beta             : float — coupling constant
    var_brain_values : list[float], optional — Var_brain scan values
                       (default: 10 log-spaced values from 0 to 1)

    Returns
    -------
    list of dicts, one per Var_brain value
    """
    if var_brain_values is None:
        var_brain_values = [0.0] + list(np.logspace(-4, 0, 9))

    results = []
    for vb in var_brain_values:
        adr = agency_decoherence_ratio(vb, phi_spread_bare, beta)
        tau = tau_dec_coupled(phi_mean, phi_spread_bare, vb, beta)
        results.append({
            "var_brain": vb,
            "adr": adr,
            "tau_dec_coupled": tau,
        })
    return results
