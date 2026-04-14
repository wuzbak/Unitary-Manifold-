# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
recycling/entropy_ledger.py
============================
Lifecycle S_U accounting and alignment — Pillar 16c.

The Unitary Manifold provides a universal entropy ledger for material
lifecycles.  Every step — from raw-material extraction through manufacturing,
use, and end-of-life — generates entropy in the unitary action S_U.  The
ledger quantifies exactly what recycling recovers and what is irreversibly lost.

The central discovery: humans measure recycling success by mass recovered,
but the manifold shows that mass is the wrong metric.  The correct metric
is φ-alignment — how closely does the recovered material's φ-field match
the virgin material's φ-field?  A 100 % mass recovery at 30 % φ-alignment
is not recycling; it is φ-entropy laundering.

What humans get wrong
---------------------
1. Mass metric ≠ quality metric.  Recovering 90 % by mass but at φ = 0.4φ_virgin
   means 60 % of the material's information value is lost — effectively
   downcycling, not recycling.
2. Single-cycle thinking.  The standard "recycled content" label ignores
   cumulative quality loss.  After five mechanical cycles at α = 0.15 per
   cycle, φ_5 = 0.47 φ_0 — less than half the original quality.
3. Entropy blindness.  Industry reports "diverted from landfill" as a
   success metric.  The manifold shows that diverting to an inefficient
   process (COP < 1) increases global S_U more than landfilling.
4. Alignment gap.  Blending recycled and virgin material hides the alignment
   gap but does not fix it.  The blend φ lies between the two, and
   subsequent cycles degrade it further.

Theory summary
--------------
Production entropy (S_U generated in n manufacturing steps):
    S_prod = n · k_B · ln(φ_product / φ_raw)   [if φ_product > φ_raw]

Use-phase entropy (exponential decay of φ during product lifetime):
    S_use = φ_product · (1 − exp(−decay_rate · t_use)) / decay_rate
    φ_end = φ_product · exp(−decay_rate · t_use)

Recycling entropy cost (work done to recover φ):
    S_recycle = k_B · |ln(φ_recycled / φ_waste)|

Landfill entropy rate (ongoing S_U generation):
    dS/dt_landfill = k_degrade · φ_waste

True recycling efficiency (net φ saved vs. virgin production):
    η_true = (φ_recycled − φ_waste) / (φ_virgin − φ_waste)

φ lifecycle trace (raw → product → use → waste → recycled):
    Computed step-by-step with per-step decay coefficients.

Alignment score (how close is recycled to virgin):
    A_score = min(φ_recycled / φ_virgin, 1)   ∈ [0, 1]

Material entropy debt (φ lost per cycle):
    D_cycle = φ_in − φ_out

Information loss per cycle:
    IL_n = φ_0 · (1 − exp(−α · n))

Closed-loop criterion:
    closed = φ_recycled ≥ φ_virgin · (1 − tol)

Open-loop total entropy budget:
    S_open = sum of entropy debt across all steps in the chain

Downcycling depth:
    DD = (φ_virgin − φ_recycled) / (φ_virgin − φ_landfill)   ∈ [0, 1]
         DD = 0 → true closed loop; DD = 1 → equivalent to landfill

Public API
----------
production_entropy(phi_raw, phi_product, n_steps, k_B)
    S_U generated manufacturing the product from raw materials.

use_phase_phi(phi_product, t_use, decay_rate)
    φ remaining at end of use phase.

recycling_entropy_cost(phi_waste, phi_recycled, k_B)
    Entropy cost of the recycling step itself.

landfill_entropy_rate(phi_waste, k_degrade)
    dS/dt in landfill.

true_recycling_efficiency(phi_recycled, phi_waste, phi_virgin)
    Net φ efficiency of the recycling process.

lifecycle_phi_trace(phi_raw, steps)
    φ at each lifecycle stage given a list of (type, param) steps.

alignment_score(phi_recycled, phi_virgin)
    How well does recycled φ match virgin φ?

material_entropy_debt(phi_in, phi_out)
    φ lost (entropy debt) in a single processing step.

information_loss_per_cycle(phi_0, n_cycles, alpha)
    Cumulative φ lost after n cycles.

closed_loop_criterion(phi_recycled, phi_virgin, tol)
    True if recycled material is within tol of virgin φ.

open_loop_entropy_budget(phi_sequence)
    Total entropy debt across an open-loop chain.

downcycling_depth(phi_recycled, phi_virgin, phi_landfill)
    Normalised depth of downcycling: 0 = closed loop, 1 = landfill.
"""

from __future__ import annotations

import numpy as np
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Production entropy
# ---------------------------------------------------------------------------

def production_entropy(
    phi_raw: float,
    phi_product: float,
    n_steps: int = 1,
    k_B: float = 1.0,
) -> float:
    """S_U generated in manufacturing the product from raw materials.

    Each manufacturing step rearranges the φ field, and the total entropy
    generated scales with the log-ratio of product to raw-material φ times
    the number of processing steps:

        S_prod = n_steps · k_B · ln(φ_product / φ_raw)

    This is positive when φ_product > φ_raw (manufacturing increases
    structural order by consuming free energy).

    Parameters
    ----------
    phi_raw     : float — φ of the raw material input (> 0)
    phi_product : float — φ of the finished product (> 0)
    n_steps     : int   — number of manufacturing steps (≥ 1)
    k_B         : float — Boltzmann constant (default 1, Planck units)

    Returns
    -------
    S_prod : float — production entropy (≥ 0 when φ_product ≥ φ_raw)

    Raises
    ------
    ValueError
        If phi_raw ≤ 0, phi_product ≤ 0, or n_steps < 1.
    """
    if phi_raw <= 0.0:
        raise ValueError(f"phi_raw must be > 0, got {phi_raw!r}")
    if phi_product <= 0.0:
        raise ValueError(f"phi_product must be > 0, got {phi_product!r}")
    if n_steps < 1:
        raise ValueError(f"n_steps must be ≥ 1, got {n_steps!r}")
    return float(n_steps * k_B * np.log(phi_product / phi_raw))


# ---------------------------------------------------------------------------
# Use-phase φ
# ---------------------------------------------------------------------------

def use_phase_phi(
    phi_product: float,
    t_use: float,
    decay_rate: float,
) -> float:
    """φ remaining in the product at the end of its use phase.

    During use the product experiences mechanical stress, UV, oxidation, and
    contamination — all of which lower the local φ exponentially:

        φ_end = φ_product · exp(−decay_rate · t_use)

    Parameters
    ----------
    phi_product : float — φ at start of use phase (> 0)
    t_use       : float — duration of use phase (≥ 0)
    decay_rate  : float — φ decay rate during use (> 0)

    Returns
    -------
    phi_end : float — φ at end of use (> 0)

    Raises
    ------
    ValueError
        If phi_product ≤ 0, t_use < 0, or decay_rate ≤ 0.
    """
    if phi_product <= 0.0:
        raise ValueError(f"phi_product must be > 0, got {phi_product!r}")
    if t_use < 0.0:
        raise ValueError(f"t_use must be ≥ 0, got {t_use!r}")
    if decay_rate <= 0.0:
        raise ValueError(f"decay_rate must be > 0, got {decay_rate!r}")
    return float(phi_product * np.exp(-decay_rate * t_use))


# ---------------------------------------------------------------------------
# Recycling entropy cost
# ---------------------------------------------------------------------------

def recycling_entropy_cost(
    phi_waste: float,
    phi_recycled: float,
    k_B: float = 1.0,
) -> float:
    """Entropy cost of the recycling process itself.

    Recovering φ_recycled from a waste stream at φ_waste requires an
    entropy expenditure proportional to the log-ratio:

        S_recycle = k_B · |ln(φ_recycled / φ_waste)|

    When φ_recycled < φ_waste the process is purely dissipative (it
    lowers quality).  When φ_recycled > φ_waste the process upgrades the
    material — this costs positive entropy elsewhere (energy input).

    Parameters
    ----------
    phi_waste    : float — φ of the waste stream entering recycling (> 0)
    phi_recycled : float — φ of the recovered material (> 0)
    k_B          : float — Boltzmann constant (default 1)

    Returns
    -------
    S_recycle : float — entropy cost (≥ 0)

    Raises
    ------
    ValueError
        If phi_waste ≤ 0 or phi_recycled ≤ 0.
    """
    if phi_waste <= 0.0:
        raise ValueError(f"phi_waste must be > 0, got {phi_waste!r}")
    if phi_recycled <= 0.0:
        raise ValueError(f"phi_recycled must be > 0, got {phi_recycled!r}")
    return float(k_B * abs(np.log(phi_recycled / phi_waste)))


# ---------------------------------------------------------------------------
# Landfill entropy rate
# ---------------------------------------------------------------------------

def landfill_entropy_rate(
    phi_waste: float,
    k_degrade: float,
) -> float:
    """Ongoing S_U generation rate in a landfill.

    Landfilled material continues to generate entropy as it slowly degrades
    under microbial action and environmental exposure.  The rate is
    proportional to the remaining φ (higher-quality material = faster
    entropy generation when it degrades):

        dS/dt_landfill = k_degrade · φ_waste

    Parameters
    ----------
    phi_waste  : float — φ of the landfilled material (> 0)
    k_degrade  : float — landfill degradation rate coefficient (> 0)

    Returns
    -------
    dS_dt : float — entropy generation rate (> 0)

    Raises
    ------
    ValueError
        If phi_waste ≤ 0 or k_degrade ≤ 0.
    """
    if phi_waste <= 0.0:
        raise ValueError(f"phi_waste must be > 0, got {phi_waste!r}")
    if k_degrade <= 0.0:
        raise ValueError(f"k_degrade must be > 0, got {k_degrade!r}")
    return float(k_degrade * phi_waste)


# ---------------------------------------------------------------------------
# True recycling efficiency
# ---------------------------------------------------------------------------

def true_recycling_efficiency(
    phi_recycled: float,
    phi_waste: float,
    phi_virgin: float,
) -> float:
    """Net φ efficiency of the recycling process.

    Measures what fraction of the φ-gap between waste and virgin quality
    is bridged by the recycling process:

        η_true = (φ_recycled − φ_waste) / (φ_virgin − φ_waste)

    η_true = 1.0 → perfect closed loop (recycled = virgin quality).
    η_true = 0.0 → no improvement (recycled = waste quality, i.e. pointless).
    η_true < 0.0 → the process degrades the material further.

    Parameters
    ----------
    phi_recycled : float — φ of the recycled material output (≥ 0)
    phi_waste    : float — φ of the waste stream input (≥ 0)
    phi_virgin   : float — φ of the equivalent virgin material (> phi_waste)

    Returns
    -------
    eta : float — true recycling efficiency (real-valued; 1.0 is ideal)

    Raises
    ------
    ValueError
        If phi_virgin ≤ phi_waste.
    """
    if phi_virgin <= phi_waste:
        raise ValueError(
            f"phi_virgin must be > phi_waste; got {phi_virgin!r} ≤ {phi_waste!r}"
        )
    return float((phi_recycled - phi_waste) / (phi_virgin - phi_waste))


# ---------------------------------------------------------------------------
# Lifecycle φ trace
# ---------------------------------------------------------------------------

def lifecycle_phi_trace(
    phi_raw: float,
    steps: List[Tuple[str, float]],
) -> List[float]:
    """Trace φ through each stage of the material lifecycle.

    Each step is a (type, param) tuple:
      - ("mfg",   ratio)       → φ *= ratio   (manufacturing step; ratio > 0)
      - ("use",   decay_rate)  → φ *= exp(−decay_rate)   (one unit of use time)
      - ("recycle", ratio)     → φ *= ratio   (mechanical recycling step)
      - ("chem_recycle", ratio)→ φ *= ratio   (chemical recycling — can be ≥ 1)

    Returns the φ value after each step (including the initial value at
    index 0).

    Parameters
    ----------
    phi_raw : float — φ of the raw material (> 0)
    steps   : list of (str, float) — ordered lifecycle steps

    Returns
    -------
    trace : list of float — φ at each stage (length = len(steps) + 1)

    Raises
    ------
    ValueError
        If phi_raw ≤ 0 or any step ratio ≤ 0.
    """
    if phi_raw <= 0.0:
        raise ValueError(f"phi_raw must be > 0, got {phi_raw!r}")
    phi = phi_raw
    trace = [phi]
    for step_type, param in steps:
        if param <= 0.0:
            raise ValueError(
                f"Step param must be > 0 for step '{step_type}', got {param!r}"
            )
        if step_type == "use":
            phi = phi * np.exp(-param)
        else:
            phi = phi * param
        trace.append(float(phi))
    return trace


# ---------------------------------------------------------------------------
# Alignment score
# ---------------------------------------------------------------------------

def alignment_score(
    phi_recycled: float,
    phi_virgin: float,
) -> float:
    """Manifold alignment score: how closely does recycled φ match virgin φ?

    The alignment score is the core metric the manifold introduces for
    material recovery.  It replaces the misleading mass-recovery rate:

        A_score = min(φ_recycled / φ_virgin, 1)   ∈ [0, 1]

    A_score = 1.0 → the recycled material is geometrically equivalent to
    virgin material in the 5D sense — true closed-loop recycling.
    A_score = 0.5 → half the φ-content is recovered — marginal recycling.
    A_score < 0.2 → the process is more accurately described as
    energy recovery or downcycling.

    Parameters
    ----------
    phi_recycled : float — φ of the recycled output (≥ 0)
    phi_virgin   : float — φ of the virgin reference (> 0)

    Returns
    -------
    score : float — alignment score ∈ [0, 1]

    Raises
    ------
    ValueError
        If phi_virgin ≤ 0 or phi_recycled < 0.
    """
    if phi_virgin <= 0.0:
        raise ValueError(f"phi_virgin must be > 0, got {phi_virgin!r}")
    if phi_recycled < 0.0:
        raise ValueError(f"phi_recycled must be ≥ 0, got {phi_recycled!r}")
    return float(np.clip(phi_recycled / phi_virgin, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Material entropy debt
# ---------------------------------------------------------------------------

def material_entropy_debt(
    phi_in: float,
    phi_out: float,
) -> float:
    """φ lost (entropy debt) in a single processing step.

    The entropy debt measures how much φ-content is destroyed by a single
    processing step — the amount of information/quality that cannot be
    recovered without additional energy input:

        D = φ_in − φ_out

    D > 0 → quality degraded (normal for mechanical processing).
    D = 0 → quality-neutral step (ideal limit).
    D < 0 → quality improvement (chemical recycling back to monomers).

    Parameters
    ----------
    phi_in  : float — φ entering the step (> 0)
    phi_out : float — φ leaving the step (≥ 0)

    Returns
    -------
    D : float — entropy debt (real-valued)

    Raises
    ------
    ValueError
        If phi_in ≤ 0 or phi_out < 0.
    """
    if phi_in <= 0.0:
        raise ValueError(f"phi_in must be > 0, got {phi_in!r}")
    if phi_out < 0.0:
        raise ValueError(f"phi_out must be ≥ 0, got {phi_out!r}")
    return float(phi_in - phi_out)


# ---------------------------------------------------------------------------
# Information loss per cycle
# ---------------------------------------------------------------------------

def information_loss_per_cycle(
    phi_0: float,
    n_cycles: int,
    alpha: float,
) -> float:
    """Cumulative φ lost after n recycling cycles.

    The φ decay is exponential (see polymers.cycle_quality_loss), so the
    cumulative information lost after n cycles is:

        IL_n = φ_0 · (1 − exp(−α · n))

    Parameters
    ----------
    phi_0    : float — initial φ of the virgin material (> 0)
    n_cycles : int   — number of recycling cycles (≥ 0)
    alpha    : float — per-cycle decay coefficient (> 0)

    Returns
    -------
    IL : float — cumulative φ lost ∈ [0, phi_0)

    Raises
    ------
    ValueError
        If phi_0 ≤ 0, n_cycles < 0, or alpha ≤ 0.
    """
    if phi_0 <= 0.0:
        raise ValueError(f"phi_0 must be > 0, got {phi_0!r}")
    if n_cycles < 0:
        raise ValueError(f"n_cycles must be ≥ 0, got {n_cycles!r}")
    if alpha <= 0.0:
        raise ValueError(f"alpha must be > 0, got {alpha!r}")
    return float(phi_0 * (1.0 - np.exp(-alpha * n_cycles)))


# ---------------------------------------------------------------------------
# Closed-loop criterion
# ---------------------------------------------------------------------------

def closed_loop_criterion(
    phi_recycled: float,
    phi_virgin: float,
    tol: float = 0.05,
) -> bool:
    """True if the recycled material meets the closed-loop quality criterion.

    A process qualifies as genuinely closed-loop if the recycled φ is within
    tolerance tol of the virgin φ:

        closed = φ_recycled ≥ φ_virgin · (1 − tol)

    The default tolerance of 5 % corresponds to the manifold prediction that
    below 95 % φ-alignment, the polymer's mechanical and optical properties
    fall outside virgin specification, requiring blending.

    Parameters
    ----------
    phi_recycled : float — φ of the recycled output (≥ 0)
    phi_virgin   : float — φ of the virgin reference (> 0)
    tol          : float — fractional tolerance (default 0.05)

    Returns
    -------
    closed : bool — True if the closed-loop criterion is met

    Raises
    ------
    ValueError
        If phi_virgin ≤ 0, phi_recycled < 0, or tol not in [0, 1].
    """
    if phi_virgin <= 0.0:
        raise ValueError(f"phi_virgin must be > 0, got {phi_virgin!r}")
    if phi_recycled < 0.0:
        raise ValueError(f"phi_recycled must be ≥ 0, got {phi_recycled!r}")
    if not (0.0 <= tol <= 1.0):
        raise ValueError(f"tol must be ∈ [0, 1], got {tol!r}")
    return bool(phi_recycled >= phi_virgin * (1.0 - tol))


# ---------------------------------------------------------------------------
# Open-loop entropy budget
# ---------------------------------------------------------------------------

def open_loop_entropy_budget(
    phi_sequence: List[float],
) -> float:
    """Total entropy debt accumulated across an open-loop recycling chain.

    An open-loop chain passes the material through multiple transformations,
    each of which may lower φ.  The total entropy debt is:

        S_open = Σ_i max(φ_i − φ_{i+1}, 0)

    (Only downward steps are counted as entropy; upward steps are handled
    separately as recycling entropy cost.)

    Parameters
    ----------
    phi_sequence : list of float — φ at each stage (≥ 2 values, all > 0)

    Returns
    -------
    S_open : float — total entropy debt across the chain (≥ 0)

    Raises
    ------
    ValueError
        If phi_sequence has fewer than 2 elements or any value is ≤ 0.
    """
    if len(phi_sequence) < 2:
        raise ValueError("phi_sequence must have at least 2 elements")
    phi_arr = np.asarray(phi_sequence, dtype=float)
    if np.any(phi_arr <= 0.0):
        raise ValueError("All phi values must be > 0")
    deltas = phi_arr[:-1] - phi_arr[1:]
    return float(np.sum(np.maximum(deltas, 0.0)))


# ---------------------------------------------------------------------------
# Downcycling depth
# ---------------------------------------------------------------------------

def downcycling_depth(
    phi_recycled: float,
    phi_virgin: float,
    phi_landfill: float,
) -> float:
    """Normalised downcycling depth: 0 = closed loop, 1 = landfill equivalent.

    Positions the recycled material on a linear scale between the ideal
    (closed-loop) and the worst case (landfilled):

        DD = (φ_virgin − φ_recycled) / (φ_virgin − φ_landfill)

    DD = 0.0 → φ_recycled = φ_virgin  (perfect closed loop)
    DD = 1.0 → φ_recycled = φ_landfill  (process adds no value over landfill)
    DD > 1.0 → the process degrades material below landfill φ (destruction)

    Parameters
    ----------
    phi_recycled : float — φ of the recycled output (≥ 0)
    phi_virgin   : float — φ of the virgin reference (> phi_landfill)
    phi_landfill : float — φ of the material if landfilled (≥ 0)

    Returns
    -------
    DD : float — downcycling depth (real-valued; 0 = ideal, 1 = no value)

    Raises
    ------
    ValueError
        If phi_virgin ≤ phi_landfill.
    """
    if phi_virgin <= phi_landfill:
        raise ValueError(
            f"phi_virgin must be > phi_landfill; got {phi_virgin!r} ≤ {phi_landfill!r}"
        )
    return float((phi_virgin - phi_recycled) / (phi_virgin - phi_landfill))
