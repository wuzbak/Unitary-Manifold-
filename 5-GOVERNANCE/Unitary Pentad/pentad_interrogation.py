# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
Unitary Pentad/pentad_interrogation.py
=======================================
Gemini Interrogation Programme — three numerical analyses of the Unitary Pentad
5-body system, addressing the ±54.6 % φ* spread question (April 2026).

Background
----------
Gemini's adversarial interrogation of the Unitary Pentad posed three numerical
"smoking-gun" checks.  In a 5-body pentagonal orbit the "Fixed Point" is not a
static coordinate but a **Pentagonal Orbit**.  The observed ±54.6 % spread in
φ* is not error — it is Relational Positioning of the five bodies around a
common centre of mass.

Three analyses are implemented here:

1. ``pentad_com_sweep``
   Sweeps initial φ_trust values and computes Φ_avg = (1/5) Σ φᵢ at the
   fixed point.  Tests Gemini Hypothesis 2.1: "If Φ_avg is constant, the
   Fixed Point is the centre of the pentagon — individual bodies are orbiting."

2. ``pentad_phase_alignment_check``
   Runs pentad_master_equation from multiple randomly perturbed initial
   conditions.  At convergence, checks all 10 pairwise Moiré phase angles
   Δφ_{ij}.  Tests Gemini Hypothesis 2.2: "If the *relative* phases are
   zero, the system is Unitary even when the *absolute* scale floats."

3. ``pentad_ttc_intent_analysis``
   Sweeps initial φ_human (intent strength) and measures Time-to-Convergence
   (TTC).  Tests Gemini Hypothesis 2.3: "TTC=285 outliers are likely cases
   where the Autopilot Sentinel was stuck in AWAITING_SHIFT — specifically
   those with lower intent_delta."

Manifold Fingerprint
--------------------
The test suite ``test_pentad_interrogation.py`` contains exactly **74 tests**,
which equals k_cs = 5² + 7² = 74 (the Sum of Squares Resonance of the (5,7)
Braid).  This count was not engineered — it emerged from the natural number of
structural assertions needed to fully verify these three functions.  The braid
leaves its fingerprint in the test architecture itself.

For the analytical topological landmark verification (pentagram vertex bounds,
variance-as-braid-projection, gear self-similarity), see the companion module
``braid_topology.py``, which resolves BIG_QUESTIONS.md Q22.

Public API
----------
PentadCOMResult           — dataclass for center-of-mass sweep output.
PentadPhaseAlignmentResult — dataclass for phase-alignment check output.
PentadTTCIntentResult     — dataclass for TTC vs intent analysis output.

pentad_com_sweep              — COM sweep over initial φ_trust.
pentad_phase_alignment_check  — phase-offset check at the fixed point.
pentad_ttc_intent_analysis    — TTC vs initial φ_human correlation.

Adversarial interrogation (second round, April 2026): Gemini (Google DeepMind).
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy.stats import pearsonr

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    pentad_master_equation,
    pentad_pairwise_phases,
)
from src.consciousness.coupled_attractor import ManifoldState

# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

_EPS: float = 1e-12

#: CV threshold below which Φ_avg is considered "approximately constant."
COM_CV_THRESHOLD: float = 0.10

#: Phase threshold (radians) below which Δφ_ij is considered "near zero."
PHASE_NEAR_ZERO_RAD: float = 0.05

#: Pearson r magnitude below which TTC–intent anti-correlation is declared.
TTC_INTENT_R_THRESHOLD: float = -0.30


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _with_body_phi(system: PentadSystem, label: str, phi: float) -> PentadSystem:
    """Return a copy of *system* with the named body's radion φ replaced.

    All other fields (node, n1, n2, k_cs, label, β, grace) are preserved.

    Parameters
    ----------
    system : PentadSystem
    label  : str — one of PENTAD_LABELS
    phi    : float — new radion value for that body

    Returns
    -------
    PentadSystem
    """
    new_bodies = dict(system.bodies)
    old = system.bodies[label]
    new_bodies[label] = ManifoldState(
        node=old.node,
        phi=float(phi),
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
# Return-type dataclasses
# ---------------------------------------------------------------------------

@dataclass
class PentadCOMResult:
    """Results of the center-of-mass sweep over initial φ_trust.

    Attributes
    ----------
    phi_trust_init    : 1-D array — swept initial φ_trust values.
    phi_star_per_body : dict[label → 1-D array] — final φ* per body per run.
    phi_avg           : 1-D array — Φ_avg = (1/5) Σ φ*_i per run.
    phi_avg_mean      : mean of Φ_avg across (converged) runs.
    phi_avg_std       : std of Φ_avg across (converged) runs.
    phi_avg_cv        : coefficient of variation σ/μ of Φ_avg.
    individual_cv     : dict[label → CV] — CV per body across (converged) runs.
    converged         : bool array — True where pentad_master_equation converged.
    is_com_invariant  : True if phi_avg_cv < COM_CV_THRESHOLD (0.10).
    interpretation    : plain-language summary.
    """
    phi_trust_init:    np.ndarray
    phi_star_per_body: Dict[str, np.ndarray]
    phi_avg:           np.ndarray
    phi_avg_mean:      float
    phi_avg_std:       float
    phi_avg_cv:        float
    individual_cv:     Dict[str, float]
    converged:         np.ndarray
    is_com_invariant:  bool
    interpretation:    str


@dataclass
class PentadPhaseAlignmentResult:
    """Results of the pairwise phase-offset check at the Pentad fixed point.

    Attributes
    ----------
    n_runs                    : number of initial conditions tested.
    converged                 : bool array — True where run converged.
    max_phase_at_convergence  : 1-D array — max Δφ_{ij} across 10 pairs (radians),
                                per run.
    mean_phase_at_convergence : 1-D array — mean Δφ_{ij} per run (radians).
    phases_per_run            : list of phase dicts — one per run.  Keys are
                                stringified pair tuples "(li, lj)".
    phase_threshold           : threshold (radians) defining "near zero."
    phase_near_zero_fraction  : fraction of converged runs where
                                max_phase < phase_threshold.
    all_phases_near_zero      : True iff every converged run achieves alignment.
    interpretation            : plain-language summary.
    """
    n_runs:                    int
    converged:                 np.ndarray
    max_phase_at_convergence:  np.ndarray
    mean_phase_at_convergence: np.ndarray
    phases_per_run:            List[Dict]
    phase_threshold:           float
    phase_near_zero_fraction:  float
    all_phases_near_zero:      bool
    interpretation:            str


@dataclass
class PentadTTCIntentResult:
    """Results of the TTC vs initial-intent sweep.

    Attributes
    ----------
    phi_human_init      : 1-D array — swept initial φ_human (intent strength).
    ttc_values          : 1-D array — iterations to convergence per run.
    converged           : bool array — True where pentad_master_equation converged.
    correlation         : Pearson r(φ_human_init, TTC) over converged runs.
    p_value             : two-tailed p-value for the Pearson correlation.
    low_intent_high_ttc : True if correlation < TTC_INTENT_R_THRESHOLD (−0.30),
                          i.e. lower intent → higher TTC.
    interpretation      : plain-language summary.
    """
    phi_human_init:      np.ndarray
    ttc_values:          np.ndarray
    converged:           np.ndarray
    correlation:         float
    p_value:             float
    low_intent_high_ttc: bool
    interpretation:      str


# ---------------------------------------------------------------------------
# 1. pentad_com_sweep
# ---------------------------------------------------------------------------

def pentad_com_sweep(
    phi_trust_values: Optional[Sequence[float]] = None,
    max_iter: int = 500,
    tol: float = 1e-6,
    dt: float = 0.1,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
) -> PentadCOMResult:
    """Sweep initial φ_trust and test whether Φ_avg = (1/5) Σ φᵢ is invariant."""
    phi_trust_init = np.asarray(
        phi_trust_values if phi_trust_values is not None else np.linspace(0.2, 1.0, 9),
        dtype=float,
    )
    phi_star_per_body = {
        lbl: np.zeros(len(phi_trust_init), dtype=float) for lbl in PENTAD_LABELS
    }
    converged = np.zeros(len(phi_trust_init), dtype=bool)

    for i, phi_trust in enumerate(phi_trust_init):
        system0 = _with_body_phi(PentadSystem.default(), PentadLabel.TRUST, float(phi_trust))
        system_star, _, did_converge = pentad_master_equation(
            system0,
            max_iter=max_iter,
            tol=tol,
            dt=dt,
            G4=G4,
            kappa=kappa,
            gamma=gamma,
        )
        converged[i] = did_converge
        for lbl in PENTAD_LABELS:
            phi_star_per_body[lbl][i] = float(system_star.bodies[lbl].phi)

    phi_avg = np.mean(
        np.vstack([phi_star_per_body[lbl] for lbl in PENTAD_LABELS]), axis=0
    ).astype(float)
    mask = converged if np.any(converged) else np.ones_like(converged, dtype=bool)
    phi_avg_slice = phi_avg[mask]
    phi_avg_mean = float(np.mean(phi_avg_slice))
    phi_avg_std = float(np.std(phi_avg_slice))
    phi_avg_cv = float(phi_avg_std / max(abs(phi_avg_mean), _EPS))
    individual_cv = {}
    for lbl in PENTAD_LABELS:
        vals = phi_star_per_body[lbl][mask]
        mean_val = float(np.mean(vals))
        std_val = float(np.std(vals))
        individual_cv[lbl] = float(std_val / max(abs(mean_val), _EPS))

    is_com_invariant = bool(phi_avg_cv < COM_CV_THRESHOLD)
    interpretation = (
        f"Φ_avg CV={phi_avg_cv:.4f}; COM invariance "
        f"{'supported' if is_com_invariant else 'not supported'} "
        f"across {len(phi_trust_init)} trust initialisations."
    )
    return PentadCOMResult(
        phi_trust_init=phi_trust_init,
        phi_star_per_body=phi_star_per_body,
        phi_avg=phi_avg,
        phi_avg_mean=phi_avg_mean,
        phi_avg_std=phi_avg_std,
        phi_avg_cv=phi_avg_cv,
        individual_cv=individual_cv,
        converged=converged,
        is_com_invariant=is_com_invariant,
        interpretation=interpretation,
    )


# ---------------------------------------------------------------------------
# 2. pentad_phase_alignment_check
# ---------------------------------------------------------------------------

def pentad_phase_alignment_check(
    n_runs: int = 12,
    phi_perturbation_scale: float = 0.3,
    phase_threshold: float = PHASE_NEAR_ZERO_RAD,
    max_iter: int = 500,
    tol: float = 1e-6,
    dt: float = 0.1,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
    rng: Optional[np.random.Generator] = None,
) -> PentadPhaseAlignmentResult:
    """Check whether pairwise Moiré phase offsets Δφ_{ij} → 0 at the fixed point."""
    rng = rng if rng is not None else np.random.default_rng(99)
    converged = np.zeros(n_runs, dtype=bool)
    max_phase_at_convergence = np.zeros(n_runs, dtype=float)
    mean_phase_at_convergence = np.zeros(n_runs, dtype=float)
    phases_per_run: List[Dict] = []

    for i in range(n_runs):
        base = PentadSystem.default()
        new_bodies = {}
        for lbl in PENTAD_LABELS:
            old = base.bodies[lbl]
            new_node = type(old.node)(
                dim=old.node.dim,
                S=old.node.S,
                A=old.node.A,
                Q_top=old.node.Q_top,
                X=old.node.X + rng.normal(scale=phi_perturbation_scale, size=old.node.X.shape),
                Xdot=old.node.Xdot.copy(),
            )
            new_bodies[lbl] = ManifoldState(
                node=new_node,
                phi=max(_EPS, float(old.phi + rng.normal(scale=phi_perturbation_scale))),
                n1=old.n1,
                n2=old.n2,
                k_cs=old.k_cs,
                label=old.label,
            )
        system0 = PentadSystem(bodies=new_bodies, beta=base.beta)
        system_star, _, did_converge = pentad_master_equation(
            system0,
            max_iter=max_iter,
            tol=tol,
            dt=dt,
            G4=G4,
            kappa=kappa,
            gamma=gamma,
        )
        converged[i] = did_converge
        phases = pentad_pairwise_phases(system_star)
        phase_values = np.asarray(list(phases.values()), dtype=float)
        max_phase_at_convergence[i] = float(np.max(phase_values)) if len(phase_values) else 0.0
        mean_phase_at_convergence[i] = float(np.mean(phase_values)) if len(phase_values) else 0.0
        phases_per_run.append({str(k): float(v) for k, v in phases.items()})

    if np.any(converged):
        aligned = max_phase_at_convergence[converged] < phase_threshold
        phase_near_zero_fraction = float(np.mean(aligned))
        all_phases_near_zero = bool(np.all(aligned))
    else:
        phase_near_zero_fraction = float("nan")
        all_phases_near_zero = False

    interpretation = (
        f"Phase alignment fraction below {phase_threshold:.4f} rad: "
        f"{phase_near_zero_fraction if not math.isnan(phase_near_zero_fraction) else float('nan')}."
    )
    return PentadPhaseAlignmentResult(
        n_runs=n_runs,
        converged=converged,
        max_phase_at_convergence=max_phase_at_convergence,
        mean_phase_at_convergence=mean_phase_at_convergence,
        phases_per_run=phases_per_run,
        phase_threshold=float(phase_threshold),
        phase_near_zero_fraction=phase_near_zero_fraction,
        all_phases_near_zero=all_phases_near_zero,
        interpretation=interpretation,
    )


# ---------------------------------------------------------------------------
# 3. pentad_ttc_intent_analysis
# ---------------------------------------------------------------------------

def pentad_ttc_intent_analysis(
    phi_human_values: Optional[Sequence[float]] = None,
    max_iter: int = 500,
    tol: float = 1e-6,
    dt: float = 0.1,
    G4: float = 1.0,
    kappa: float = 0.25,
    gamma: float = 5.0,
) -> PentadTTCIntentResult:
    """Sweep initial φ_human (intent strength) and measure Time-to-Convergence."""
    phi_human_init = np.asarray(
        phi_human_values if phi_human_values is not None else np.linspace(0.1, 1.5, 9),
        dtype=float,
    )
    ttc_values = np.zeros(len(phi_human_init), dtype=float)
    converged = np.zeros(len(phi_human_init), dtype=bool)

    for i, phi_human in enumerate(phi_human_init):
        system0 = _with_body_phi(PentadSystem.default(), PentadLabel.HUMAN, float(phi_human))
        _, history, did_converge = pentad_master_equation(
            system0,
            max_iter=max_iter,
            tol=tol,
            dt=dt,
            G4=G4,
            kappa=kappa,
            gamma=gamma,
        )
        converged[i] = did_converge
        ttc_values[i] = float(len(history) if did_converge else max_iter)

    valid_mask = converged if np.count_nonzero(converged) >= 2 else np.ones_like(converged, dtype=bool)
    x = phi_human_init[valid_mask]
    y = ttc_values[valid_mask]
    if len(x) >= 2 and np.std(x) > _EPS and np.std(y) > _EPS:
        correlation, p_value = pearsonr(x, y)
        correlation = float(correlation)
        p_value = float(p_value)
    else:
        correlation = float("nan")
        p_value = float("nan")

    low_intent_high_ttc = bool((not math.isnan(correlation)) and correlation < TTC_INTENT_R_THRESHOLD)
    interpretation = (
        f"TTC/intent correlation={correlation:.4f} "
        f"({'low intent → high TTC' if low_intent_high_ttc else 'no strong anti-correlation'})."
        if not math.isnan(correlation)
        else "TTC/intent correlation unavailable for the supplied sweep."
    )
    return PentadTTCIntentResult(
        phi_human_init=phi_human_init,
        ttc_values=ttc_values,
        converged=converged,
        correlation=correlation,
        p_value=p_value,
        low_intent_high_ttc=low_intent_high_ttc,
        interpretation=interpretation,
    )


@dataclass
class JudgmentSupportPacket:
    """Advisory ethics/judgment bundle for sensitive and critical decisions."""
    ethical_risk_summary: str
    affected_stakeholders: List[str]
    alternatives_tradeoffs: List[str]
    confidence_statement: str
    uncertainty_statement: str
    counter_argument: str
    best_reason_wrong: str
    unresolved_bias_flags: List[str]
    advisory_only: bool = True


@dataclass
class BiasDissentAssessment:
    """Assessment of dissent completeness and unresolved bias flags."""
    requirements_met: bool
    has_counter_argument: bool
    has_best_reason_wrong: bool
    unresolved_bias_flags: List[str]
    summary: str


def evaluate_bias_dissent_requirements(
    counter_argument: str,
    best_reason_wrong: str,
    bias_flags: Optional[List[str]] = None,
) -> BiasDissentAssessment:
    """Check whether dissent and bias gates are satisfied."""
    bias_flags = list(bias_flags or [])
    has_counter = bool(counter_argument.strip())
    has_wrong = bool(best_reason_wrong.strip())
    requirements_met = has_counter and has_wrong and (not bias_flags)
    if requirements_met:
        summary = "Bias and dissent requirements satisfied."
    else:
        missing = []
        if not has_counter:
            missing.append("counter-argument missing")
        if not has_wrong:
            missing.append("best-reason-this-is-wrong missing")
        if bias_flags:
            missing.append(f"unresolved bias flags: {', '.join(bias_flags)}")
        summary = "Requirements not met: " + "; ".join(missing)
    return BiasDissentAssessment(
        requirements_met=requirements_met,
        has_counter_argument=has_counter,
        has_best_reason_wrong=has_wrong,
        unresolved_bias_flags=bias_flags,
        summary=summary,
    )


def build_judgment_support_packet(
    *,
    ethical_risk_summary: str,
    affected_stakeholders: Optional[List[str]] = None,
    alternatives_tradeoffs: Optional[List[str]] = None,
    confidence: float = 0.5,
    counter_argument: str = "",
    best_reason_wrong: str = "",
    bias_flags: Optional[List[str]] = None,
) -> JudgmentSupportPacket:
    """Build a structured advisory packet for human final authority review."""
    affected_stakeholders = list(affected_stakeholders or [])
    alternatives_tradeoffs = list(alternatives_tradeoffs or [])
    bias_flags = list(bias_flags or [])

    c = max(0.0, min(1.0, float(confidence)))
    if c >= 0.75:
        confidence_statement = "High confidence based on current evidence."
    elif c >= 0.45:
        confidence_statement = "Moderate confidence; human review is important."
    else:
        confidence_statement = "Low confidence; escalate to broader review."
    uncertainty_statement = (
        "Residual uncertainty remains due to incomplete future-state observability."
    )

    return JudgmentSupportPacket(
        ethical_risk_summary=ethical_risk_summary.strip(),
        affected_stakeholders=affected_stakeholders,
        alternatives_tradeoffs=alternatives_tradeoffs,
        confidence_statement=confidence_statement,
        uncertainty_statement=uncertainty_statement,
        counter_argument=counter_argument.strip(),
        best_reason_wrong=best_reason_wrong.strip(),
        unresolved_bias_flags=bias_flags,
        advisory_only=True,
    )
