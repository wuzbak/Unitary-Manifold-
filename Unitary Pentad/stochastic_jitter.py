# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/stochastic_jitter.py
=====================================
Observer-Induced Jitter: Langevin Phase-Noise Extension to the Master Equation.

Background
----------
The Unitary Pentad's (5,7) braid provides a *deterministic* stability bound:
the minimum eigenvalue of the pentagonal coupling matrix is bounded from below
by c_s = 12/37 ≈ 0.324.  But the "Human" and "AI" bodies are not silent
oscillators — they inject **operational noise** at every tick:

    Human body (Ψ_human) — **cognitive jitter**:
        The human operator's intent vector is subject to sampling noise,
        attentional drift, and cognitive bias.  Each time the human "reads" the
        pentad state they introduce a perturbation proportional to their
        operating temperature σ_human (units: radion noise per tick).

    AI body (Ψ_AI) — **hallucination jitter**:
        The AI inference engine has a temperature parameter T_AI that controls
        the magnitude of stochastic excursions from the computed mean.  This
        maps directly to the AI body's phase-noise amplitude σ_AI.

Langevin Extension
------------------
The noisy Master Equation adds a Langevin noise term to the deterministic
``step_pentad`` update:

    φᵢ(t + dt) = φᵢ_deterministic(t + dt) + σᵢ · η_i · √dt

where η_i ~ N(0, 1) is independent white noise and σᵢ is body i's noise
amplitude.  The noise is **additive** (Itô convention) so it does not alter
the equilibrium distribution of the deterministic fixed points — it only
broadens them.

(5,7) Braid Jitter Suppression
-------------------------------
The braid acts as a low-pass filter for phase noise.  The *braid suppression
factor* quantifies how much the coupling operator damps a unit of injected
jitter in one step:

    suppression_factor = 1 − β_eff · dt

where β_eff = β × φ_trust × c_s is the effective coupling at the stability
floor.  For the default parameters this gives ≈ 0.98 — meaning 2 % of any
noise amplitude is damped per step.

The **noise tolerance** is the maximum σ (equal noise on all noisy bodies)
the system can sustain while keeping the mean pairwise phase offset below
the collapse threshold (π/2):

    σ_max ≈ (π/2) × β_eff × dt × √(n_steps)   (diffusion limit)

Phase-Lock Margin
-----------------
After n_steps of noisy evolution the *phase-lock margin* is the gap between
the empirical 95th-percentile maximum phase offset and the π/2 reversal
threshold.  A positive margin means the braid is still suppressing noise
effectively; a negative margin signals that cognitive/operational jitter has
driven the system past the phase-reversal point.

Public API
----------
JitterProfile
    Dataclass: per-body noise amplitudes σ for the 5 Pentad bodies.
    Factory: JitterProfile.default(sigma_human, sigma_ai) — only Human and AI
    bodies carry noise by default; the physical/brain/trust bodies are silent.

JitterReport
    Dataclass: results of a Monte-Carlo jitter stress test.
    Fields: n_trials, n_steps, sigma_human, sigma_ai, mean_max_phase,
    std_max_phase, p95_max_phase, phase_lock_margin, suppression_factor,
    braid_holds.

inject_phase_noise(system, profile, rng) -> PentadSystem
    Apply one Langevin noise step: add σᵢ · η_i · √dt to each body's φ.
    Returns a new PentadSystem (pure function).

noisy_step(system, profile, dt, G4, kappa, gamma, rng) -> PentadSystem
    One combined step: deterministic step_pentad + Langevin noise injection.

braid_suppression_factor(system, dt) -> float
    Effective one-step jitter suppression factor for the current state.

noise_tolerance(system, dt, n_steps) -> float
    Maximum equal noise amplitude σ the system can sustain before reaching
    the phase-reversal threshold in the diffusion limit.

jitter_stress_test(system, profile, n_trials, n_steps, dt, seed) -> JitterReport
    Monte-Carlo stress test: simulate n_trials independent noisy runs of
    n_steps each, recording the maximum pairwise phase offset per run.
    Returns a JitterReport with statistics and a braid_holds flag.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Optional

import numpy as np

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    BRAIDED_SOUND_SPEED,
    TRUST_PHI_MIN,
    trust_modulation,
    pentad_pairwise_phases,
    step_pentad,
)
from src.consciousness.coupled_attractor import ManifoldState

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Phase reversal threshold (π/2): beyond this the coupling amplifies divergence.
PHASE_REVERSAL_THRESHOLD: float = math.pi / 2

#: Default cognitive jitter amplitude for the Human body (σ_human).
DEFAULT_SIGMA_HUMAN: float = 0.02

#: Default hallucination jitter amplitude for the AI body (σ_AI).
DEFAULT_SIGMA_AI: float = 0.01

#: Floor on noise amplitudes to prevent division issues.
_SIGMA_EPS: float = 1e-14


# ---------------------------------------------------------------------------
# JitterProfile
# ---------------------------------------------------------------------------

@dataclass
class JitterProfile:
    """Per-body noise amplitudes σᵢ for the 5 Pentad bodies.

    By convention the Physical Manifold (univ), Brain, and Trust bodies are
    treated as *silent* (σ = 0) — their dynamics are governed by deterministic
    physics.  Only the Human and AI bodies carry operational noise.

    Attributes
    ----------
    sigma : dict[str, float]
        Mapping from PentadLabel → noise amplitude σᵢ ≥ 0.
        Default: only HUMAN and AI have non-zero σ.
    """
    sigma: Dict[str, float]

    def __post_init__(self) -> None:
        # Ensure all 5 bodies have an entry; missing ones default to 0.
        for lbl in PENTAD_LABELS:
            self.sigma.setdefault(lbl, 0.0)
        # Clamp to non-negative
        for lbl in PENTAD_LABELS:
            self.sigma[lbl] = max(0.0, self.sigma[lbl])

    @classmethod
    def default(
        cls,
        sigma_human: float = DEFAULT_SIGMA_HUMAN,
        sigma_ai: float = DEFAULT_SIGMA_AI,
    ) -> "JitterProfile":
        """Create a profile with noise only on the Human and AI bodies.

        Parameters
        ----------
        sigma_human : float — cognitive jitter amplitude (default 0.02)
        sigma_ai    : float — hallucination jitter amplitude (default 0.01)
        """
        return cls(sigma={
            PentadLabel.UNIV:  0.0,
            PentadLabel.BRAIN: 0.0,
            PentadLabel.HUMAN: float(sigma_human),
            PentadLabel.AI:    float(sigma_ai),
            PentadLabel.TRUST: 0.0,
        })

    @classmethod
    def symmetric(cls, sigma: float) -> "JitterProfile":
        """Equal noise amplitude on all five bodies.

        Parameters
        ----------
        sigma : float — noise amplitude for every body
        """
        return cls(sigma={lbl: float(sigma) for lbl in PENTAD_LABELS})


# ---------------------------------------------------------------------------
# JitterReport
# ---------------------------------------------------------------------------

@dataclass
class JitterReport:
    """Results of a Monte-Carlo jitter stress test.

    Attributes
    ----------
    n_trials          : int   — number of independent Monte-Carlo runs
    n_steps           : int   — steps per run
    sigma_human       : float — Human body noise amplitude used
    sigma_ai          : float — AI body noise amplitude used
    mean_max_phase    : float — mean of (max pairwise phase per run)
    std_max_phase     : float — standard deviation of max phase across runs
    p95_max_phase     : float — 95th-percentile max phase across runs
    phase_lock_margin : float — PHASE_REVERSAL_THRESHOLD − p95_max_phase
                                positive → braid holds; negative → phase lock lost
    suppression_factor : float — β_eff × dt evaluated at the initial state
    braid_holds        : bool  — True iff phase_lock_margin > 0
    """
    n_trials:           int
    n_steps:            int
    sigma_human:        float
    sigma_ai:           float
    mean_max_phase:     float
    std_max_phase:      float
    p95_max_phase:      float
    phase_lock_margin:  float
    suppression_factor: float
    braid_holds:        bool


# ---------------------------------------------------------------------------
# inject_phase_noise
# ---------------------------------------------------------------------------

def inject_phase_noise(
    system: PentadSystem,
    profile: JitterProfile,
    dt: float,
    rng: np.random.Generator,
) -> PentadSystem:
    """Apply one Langevin noise step to the system's radion values.

    Each body i receives an additive perturbation:

        φᵢ → φᵢ + σᵢ · η_i · √dt,   η_i ~ N(0, 1)

    The perturbation is additive (Itô convention) and acts only on the radion φ.
    The entropy S and state vector X are unperturbed by the noise step.

    Parameters
    ----------
    system  : PentadSystem — current state
    profile : JitterProfile — per-body noise amplitudes
    dt      : float — pseudo-timestep (scales noise as √dt)
    rng     : numpy Generator — source of randomness

    Returns
    -------
    PentadSystem — copy with perturbed φ values
    """
    sqrt_dt = math.sqrt(max(dt, 0.0))
    new_bodies = {}
    for lbl in PENTAD_LABELS:
        old = system.bodies[lbl]
        sigma = profile.sigma.get(lbl, 0.0)
        if sigma > _SIGMA_EPS:
            eta = float(rng.standard_normal())
            new_phi = old.phi + sigma * eta * sqrt_dt
        else:
            new_phi = old.phi
        new_bodies[lbl] = ManifoldState(
            node=old.node,
            phi=new_phi,
            n1=old.n1,
            n2=old.n2,
            k_cs=old.k_cs,
            label=old.label,
        )
    return PentadSystem(
        bodies=new_bodies,
        beta=system.beta,
        grace_steps=system.grace_steps,
        grace_decay=system.grace_decay,
        _trust_reservoir=system._trust_reservoir,
        _grace_elapsed=system._grace_elapsed,
    )


# ---------------------------------------------------------------------------
# noisy_step
# ---------------------------------------------------------------------------

def noisy_step(
    system: PentadSystem,
    profile: JitterProfile,
    dt: float,
    rng: np.random.Generator,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
) -> PentadSystem:
    """One combined noisy step: deterministic U_pentad + Langevin noise.

    Order: deterministic step first, then noise injection.  This ordering
    ensures that the braid's damping operator acts *before* the noise is
    added, which is the standard Itô discretisation:

        system(t+dt) = step_pentad(system(t)) + noise(dt)

    Parameters
    ----------
    system  : PentadSystem
    profile : JitterProfile
    dt      : float — pseudo-timestep
    rng     : numpy Generator
    G4      : float — Newton's constant (default 1)
    kappa   : float — FTUM curvature constant (default 1)
    gamma   : float — FTUM damping constant (default 1)

    Returns
    -------
    PentadSystem
    """
    det = step_pentad(system, dt=dt, G4=G4, kappa=kappa, gamma=gamma)
    return inject_phase_noise(det, profile, dt=dt, rng=rng)


# ---------------------------------------------------------------------------
# braid_suppression_factor
# ---------------------------------------------------------------------------

def braid_suppression_factor(system: PentadSystem, dt: float) -> float:
    """One-step jitter suppression factor for the (5,7) braid.

    The coupling operator damps a noise amplitude by a factor

        suppression = β_eff × dt

    per step, where β_eff = β × φ_trust × c_s is the effective coupling at
    the braided stability floor.  Values close to 1 mean strong suppression;
    values near 0 mean the braid is ineffective (either trust has collapsed
    or dt is tiny).

    Parameters
    ----------
    system : PentadSystem
    dt     : float — pseudo-timestep

    Returns
    -------
    float — suppression factor ∈ [0, 1]
    """
    tau = trust_modulation(system)
    beta_eff = system.beta * tau * BRAIDED_SOUND_SPEED
    return float(np.clip(beta_eff * dt, 0.0, 1.0))


# ---------------------------------------------------------------------------
# noise_tolerance
# ---------------------------------------------------------------------------

def noise_tolerance(
    system: PentadSystem,
    dt: float,
    n_steps: int,
) -> float:
    """Maximum equal noise amplitude before phase-reversal in the diffusion limit.

    In the diffusion limit (many independent noise steps) the RMS phase drift
    after n_steps grows as σ × √n_steps × √dt.  The system reaches the
    phase-reversal threshold when:

        σ × √(n_steps × dt) = PHASE_REVERSAL_THRESHOLD × suppression_factor

    Solving for σ:

        σ_max = PHASE_REVERSAL_THRESHOLD × suppression_factor / √(n_steps × dt)

    This gives a conservative (lower-bound) estimate of the noise tolerance.

    Parameters
    ----------
    system  : PentadSystem — current state (used for suppression_factor)
    dt      : float — pseudo-timestep
    n_steps : int — number of steps to tolerate noise over

    Returns
    -------
    float — σ_max ≥ 0
    """
    sf = braid_suppression_factor(system, dt)
    denom = math.sqrt(max(n_steps * dt, 1e-30))
    return float(PHASE_REVERSAL_THRESHOLD * sf / denom)


# ---------------------------------------------------------------------------
# jitter_stress_test
# ---------------------------------------------------------------------------

def jitter_stress_test(
    system: PentadSystem,
    profile: JitterProfile,
    n_trials: int = 200,
    n_steps: int = 50,
    dt: float = 0.05,
    seed: Optional[int] = 42,
) -> JitterReport:
    """Monte-Carlo stress test: can the (5,7) braid suppress the jitter?

    For each of n_trials independent runs:

        1. Start from the provided system state.
        2. Apply n_steps of noisy_step.
        3. Record max_phase = max pairwise Moiré phase offset at the end.

    Then compute statistics across runs and report whether phase lock was
    maintained (braid_holds = p95_max_phase < PHASE_REVERSAL_THRESHOLD).

    Parameters
    ----------
    system   : PentadSystem — initial state (same for all trials)
    profile  : JitterProfile — per-body noise amplitudes
    n_trials : int   — number of Monte-Carlo trials (default 200)
    n_steps  : int   — steps per trial (default 50)
    dt       : float — pseudo-timestep (default 0.05)
    seed     : int or None — master RNG seed (default 42)

    Returns
    -------
    JitterReport
    """
    rng_master = np.random.default_rng(seed)
    max_phases = np.empty(n_trials)

    sf = braid_suppression_factor(system, dt)

    for trial in range(n_trials):
        trial_rng = np.random.default_rng(rng_master.integers(0, 2**32))
        current = system
        for _ in range(n_steps):
            current = noisy_step(current, profile, dt=dt, rng=trial_rng)
        phases = pentad_pairwise_phases(current)
        max_phases[trial] = float(max(phases.values()))

    mean_mp = float(np.mean(max_phases))
    std_mp  = float(np.std(max_phases))
    p95_mp  = float(np.percentile(max_phases, 95))
    margin  = float(PHASE_REVERSAL_THRESHOLD - p95_mp)

    return JitterReport(
        n_trials=n_trials,
        n_steps=n_steps,
        sigma_human=profile.sigma.get(PentadLabel.HUMAN, 0.0),
        sigma_ai=profile.sigma.get(PentadLabel.AI, 0.0),
        mean_max_phase=mean_mp,
        std_max_phase=std_mp,
        p95_max_phase=p95_mp,
        phase_lock_margin=margin,
        suppression_factor=sf,
        braid_holds=(margin > 0.0),
    )
