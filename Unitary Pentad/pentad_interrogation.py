# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
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
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "_with_body_phi() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
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
    """Sweep initial φ_trust and test whether Φ_avg = (1/5) Σ φᵢ is invariant.

    Addresses Gemini Interrogation 2.1:

        "Calculate Φ_avg = (1/5) Σ Ψᵢ.  Does Φ_avg vary by 54%, or is it
        constant?  If Φ_avg is constant, the 'Fixed Point' is the centre of
        the pentagon, and the individual bodies are just orbiting it."

    All other bodies are held at their canonical defaults (from
    ``PentadSystem.default()``).  Only φ_trust is swept, because the Trust
    field is the "anchor" that couples at the bare birefringence constant β
    without trust modulation.

    Parameters
    ----------
    phi_trust_values : sequence of initial φ_trust values.
                       Default: 9 values uniformly in [0.2, 1.0].
    max_iter, tol, dt, G4, kappa, gamma
                     : forwarded to ``pentad_master_equation``.

    Returns
    -------
    PentadCOMResult
    """
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "pentad_com_sweep() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
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
    """Check whether pairwise Moiré phase offsets Δφ_{ij} → 0 at the fixed point.

    Addresses Gemini Interrogation 2.2:

        "Your README mentions that at the fixed point, 'All pairwise Moiré phase
        offsets → 0.'  Check if this holds true even when φ* varies.  If the
        *relative* phases are zero, the system is perfectly aligned (Unitary),
        even if the *absolute* scale is floating."

    Runs ``pentad_master_equation`` from ``n_runs`` independently perturbed
    initial conditions.  At convergence (or max_iter), records all C(5,2) = 10
    pairwise Moiré phase angles from ``pentad_pairwise_phases``.

    Parameters
    ----------
    n_runs                : number of perturbed initial conditions to test.
                            Default: 12.
    phi_perturbation_scale: std of Gaussian φ perturbation per body.
                            Default: 0.3 (30 % of canonical scale).
    phase_threshold       : Δφ < this (radians) is "near zero."
                            Default: PHASE_NEAR_ZERO_RAD = 0.05 rad ≈ 2.9°.
    max_iter, tol, dt, G4, kappa, gamma
                          : forwarded to ``pentad_master_equation``.
    rng                   : optional RNG (default seed 99 for reproducibility).

    Returns
    -------
    PentadPhaseAlignmentResult
    """
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "pentad_phase_alignment_check() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
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
    """Sweep initial φ_human (intent strength) and measure Time-to-Convergence.

    Addresses Gemini Interrogation 2.3:

        "The TTC=285 outliers are likely cases where the Autopilot Sentinel was
        stuck in AWAITING_SHIFT.  Check if these specific cases had a lower
        intent_delta."

    The Human Intent body (Ψ_human, Body 3) carries the φ_human radion that
    represents human intent strength.  A lower initial φ_human means weaker
    human intent at the start of iteration.  This function sweeps φ_human_init
    and measures TTC = number of iterations for ``pentad_master_equation`` to
    converge, testing whether intent-weak runs are the slow outliers.

    Parameters
    ----------
    phi_human_values : sequence of initial φ_human values.
                       Default: 9 values in [0.1, 1.5].
    max_iter, tol, dt, G4, kappa, gamma
                     : forwarded to ``pentad_master_equation``.

    Returns
    -------
    PentadTTCIntentResult

    Notes
    -----
    TTC is defined as ``len(history)`` returned by ``pentad_master_equation``:
    the iteration index at which defect < tol.  If the run did not converge,
    TTC = max_iter.
    """
    # -----------------------------------------------------------------------
    # PENTAD PRODUCT POLICY v1.0 — AxiomZero Technologies
    # The HILS Pentad is a protected AxiomZero product currently in active
    # development.  This function's implementation is held in a private
    # AxiomZero repository.  See PENTAD_PRODUCT_NOTICE.md for details and
    # instructions on how to obtain access.
    # -----------------------------------------------------------------------
    raise NotImplementedError(
        "pentad_ttc_intent_analysis() is part of the AxiomZero Pentad product layer, "
        "currently in active development.  "
        "See PENTAD_PRODUCT_NOTICE.md."
    )
