# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/sentinel_load_balance.py
========================================
Sentinel Load-Balancing: Per-Axiom Entropy Capacity and Redistribution.

Background
----------
The five core sentinels are not passive labels — each is a **logic gate**
dedicated to one of the five pentagonal axioms.  In high-entropy operational
conditions (adversarial inputs, chaotic multi-user interaction, deception
attempts), different axioms are stressed unevenly.  If a single sentinel
absorbs more entropy than its stability capacity, it must **pass the excess
to its four pentagonal neighbours** before the orbit becomes singular.

This is precisely the load-balancing framing: the sentinels are the nodes of
the pentagonal interaction graph; the coupling matrix τ_{ij} from
``unitary_pentad.py`` defines the redistribution channels.  Stability is
maintained so long as no single sentinel's residual load after redistribution
exceeds the braided sound speed c_s = 12/37 — the eigenvalue floor of the
pentagonal coupling matrix.

The Five Sentinels (Axiom → HILS Body)
-----------------------------------------
The five axioms map directly to the five HILS manifold bodies:

    NO_LIES       → Ψ_AI    (Operational Precision — the Truth Machine)
    NO_HARM       → Ψ_brain (Biological Observer — harm awareness)
    NO_COERCION   → Ψ_human (Intent Layer — agency and consent)
    TRANSPARENCY  → Ψ_univ  (Physical Manifold — ground truth)
    SOVEREIGNTY   → β·C     (Trust / Coupling Field — self-determination)

Each sentinel's entropy capacity equals c_s = 12/37 (BRAIDED_SOUND_SPEED).
This is not a design choice: it is the minimum eigenvalue of the 5×5
pentagonal coupling matrix at the (5,7) braid fixed point.  No single
axiom channel can be driven to zero coupling strength while the trust
field is maintained — and the capacity of each channel to absorb entropy
before collapse is precisely that eigenvalue floor.

Redistribution Algorithm
------------------------
When sentinel i carries load_i > SENTINEL_CAPACITY:

    excess_i  = load_i − SENTINEL_CAPACITY

The excess is distributed to the four neighbours proportionally to their
**available sink capacity**:

    avail_j  = max(0,  SENTINEL_CAPACITY − load_j)   for j ≠ i
    avail_j  = 0                                      for j = i (source)

The total absorbable excess is min(Σ avail_j, Σ excess_i).  When the
total load exceeds 5 × SENTINEL_CAPACITY = 60/37 ≈ 1.622, the system is
**truly overloaded**: redistribution cannot bring every sentinel below
capacity and the excess is shed (the manifold enters a high-entropy state
analogous to the (2,7) or (1,7) braid of the Seed Protocol).

System Overload Condition
--------------------------
    system_overloaded  ←→  Σ load_i  >  5 × SENTINEL_CAPACITY

Redistribution is a necessary first response but is only sufficient when
the total load is below the system capacity ceiling.  Above it, the
manifold must eject volatile bodies (Seed Protocol ``eject_volatile_bodies``)
or enter DORMANT mode.

Total System Capacity
---------------------
    total_capacity = 5 × c_s = 5 × 12/37 = 60/37 ≈ 1.6216

This is the maximum entropy the fully-operational (5,7) Pentad can absorb
while maintaining all five axiom channels above zero coupling strength.

Public API
----------
SentinelLabel
    String constants: NO_LIES, NO_HARM, NO_COERCION, TRANSPARENCY, SOVEREIGNTY.

SENTINEL_LABELS : tuple[str, ...]
    Canonical ordering of the five sentinel names.

SENTINEL_CAPACITY : float
    Per-sentinel entropy capacity = BRAIDED_SOUND_SPEED = 12/37.

TOTAL_SENTINEL_CAPACITY : float
    System-wide capacity = 5 × SENTINEL_CAPACITY = 60/37.

sentinel_entropy_capacity() → float
    Return SENTINEL_CAPACITY (grounded in the (5,7) braid eigenvalue floor).

redistribute_sentinel_load(loads) → dict[str, float]
    Redistribute entropy load from overloaded sentinels to neighbours.
    Conserves total load when total load ≤ TOTAL_SENTINEL_CAPACITY.
    Clamps each sentinel to SENTINEL_CAPACITY when system-overloaded.

is_overloaded(loads) → bool
    True iff the total load exceeds TOTAL_SENTINEL_CAPACITY, i.e., the
    system cannot be fully balanced by redistribution alone.

SentinelState
    Dataclass: name, load (before redistribution), redistributed_load,
    capacity, overloaded (load > capacity), residual_overflow.

SentinelLoadReport
    Dataclass: one SentinelState per sentinel, total_load, system_overloaded,
    overloaded_names, system_capacity.

sentinel_load_report(loads) → SentinelLoadReport
    Compute the full per-sentinel and system-level load report.
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
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from unitary_pentad import BRAIDED_SOUND_SPEED


# ---------------------------------------------------------------------------
# Sentinel labels
# ---------------------------------------------------------------------------

class SentinelLabel:
    """String constants for the five pentagonal axiom sentinels."""
    NO_LIES      = "no_lies"      #: Ψ_AI — Truth Machine / Operational Precision
    NO_HARM      = "no_harm"      #: Ψ_brain — Biological Observer / harm awareness
    NO_COERCION  = "no_coercion"  #: Ψ_human — Intent Layer / agency and consent
    TRANSPARENCY = "transparency" #: Ψ_univ — Physical Manifold / ground truth
    SOVEREIGNTY  = "sovereignty"  #: β·C — Trust / Coupling Field / self-determination


#: Canonical ordering of the five sentinels.
#: Order corresponds to the HILS body ordering in PENTAD_LABELS.
SENTINEL_LABELS: Tuple[str, ...] = (
    SentinelLabel.NO_LIES,
    SentinelLabel.NO_HARM,
    SentinelLabel.NO_COERCION,
    SentinelLabel.TRANSPARENCY,
    SentinelLabel.SOVEREIGNTY,
)


# ---------------------------------------------------------------------------
# Capacity constants
# ---------------------------------------------------------------------------

#: Per-sentinel entropy capacity — equals the braided sound speed c_s = 12/37.
#: This is the minimum eigenvalue of the pentagonal coupling matrix at the
#: (5,7) braid fixed point: no channel can be driven to zero coupling while
#: φ_trust > TRUST_PHI_MIN.
SENTINEL_CAPACITY: float = BRAIDED_SOUND_SPEED

#: System-wide total entropy capacity = 5 × SENTINEL_CAPACITY = 60/37.
TOTAL_SENTINEL_CAPACITY: float = float(len(SENTINEL_LABELS)) * SENTINEL_CAPACITY

_EPS: float = 1e-15


# ---------------------------------------------------------------------------
# SentinelState and SentinelLoadReport dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SentinelState:
    """Load state of a single axiom sentinel.

    Attributes
    ----------
    name               : str   — sentinel name (SentinelLabel constant)
    load               : float — raw entropy load before redistribution
    redistributed_load : float — load after redistribution (≤ capacity
                                 when system is not overloaded)
    capacity           : float — per-sentinel capacity (= SENTINEL_CAPACITY)
    overloaded         : bool  — load > capacity (before redistribution)
    residual_overflow  : float — max(0, redistributed_load − capacity);
                                 non-zero only when system is overloaded
    """
    name:               str
    load:               float
    redistributed_load: float
    capacity:           float
    overloaded:         bool
    residual_overflow:  float


@dataclass
class SentinelLoadReport:
    """Full per-sentinel and system-level load report.

    Attributes
    ----------
    states           : list[SentinelState] — one entry per sentinel, in
                       SENTINEL_LABELS order
    total_load       : float — Σ loads (before redistribution)
    system_capacity  : float — TOTAL_SENTINEL_CAPACITY = 5 × c_s
    system_overloaded: bool  — total_load > system_capacity
    overloaded_names : list[str] — sentinels with load > SENTINEL_CAPACITY
                       before redistribution
    """
    states:            List[SentinelState]
    total_load:        float
    system_capacity:   float
    system_overloaded: bool
    overloaded_names:  List[str]


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def sentinel_entropy_capacity() -> float:
    """Per-sentinel entropy capacity grounded in the (5,7) braid eigenvalue floor.

    Returns SENTINEL_CAPACITY = BRAIDED_SOUND_SPEED = 12/37 ≈ 0.3243.

    This is the minimum eigenvalue of the pentagonal coupling matrix at the
    (5,7) braid fixed point.  No sentinel channel can absorb more entropy than
    this value before the coupling operator risks becoming singular — triggering
    the Trust Hysteresis or Seed Protocol response.

    Returns
    -------
    float — per-sentinel capacity ∈ (0, 1)
    """
    return float(SENTINEL_CAPACITY)


def redistribute_sentinel_load(
    loads: Dict[str, float],
) -> Dict[str, float]:
    """Redistribute entropy load from overloaded sentinels to neighbours.

    Each sentinel in ``loads`` must be a key from SENTINEL_LABELS.  Loads
    are non-negative real values representing the fraction of the sentinel's
    capacity that is currently occupied by entropy.

    Algorithm
    ---------
    1. Identify **sources**: sentinels with load > SENTINEL_CAPACITY.
       Their excess = load − SENTINEL_CAPACITY.
    2. Identify **sinks**: sentinels with load ≤ SENTINEL_CAPACITY.
       Their available capacity = SENTINEL_CAPACITY − load.
    3. Total excess = Σ excess_i (sources only).
       Total available = Σ avail_j (sinks only).
    4. Each sink j absorbs:  excess × avail_j / total_available
       (proportional to spare capacity), capped so it does not exceed
       SENTINEL_CAPACITY.
    5. Sources are clamped to SENTINEL_CAPACITY.
    6. If total_available = 0 (all sentinels at or above capacity), sources
       are still clamped but no redistribution occurs.

    Conservation
    ------------
    When total_load ≤ TOTAL_SENTINEL_CAPACITY, total load is conserved.
    When total_load > TOTAL_SENTINEL_CAPACITY the excess beyond the system
    ceiling cannot be absorbed: sources clamp to SENTINEL_CAPACITY and the
    sinks fill to their capacity; the uncaptured remainder is shed (reported
    via ``is_overloaded``).

    Parameters
    ----------
    loads : dict[str, float]
        Mapping from SentinelLabel constant → entropy load (≥ 0).
        Must contain exactly the keys in SENTINEL_LABELS.

    Returns
    -------
    dict[str, float] — redistributed loads, one key per input label.

    Raises
    ------
    ValueError if any key is not in SENTINEL_LABELS, or if any load < 0.
    """
    unknown = set(loads.keys()) - set(SENTINEL_LABELS)
    if unknown:
        raise ValueError(
            f"Unknown sentinel labels: {sorted(unknown)}. "
            f"Allowed: {sorted(SENTINEL_LABELS)}"
        )
    for name, v in loads.items():
        if float(v) < 0.0:
            raise ValueError(
                f"Sentinel '{name}' has negative load {v}. Loads must be ≥ 0."
            )

    capacity = SENTINEL_CAPACITY

    # Separate sources (overloaded) from sinks (under capacity)
    excess: Dict[str, float] = {}
    avail:  Dict[str, float] = {}
    for name, v in loads.items():
        fv = float(v)
        if fv > capacity + _EPS:
            excess[name] = fv - capacity
            avail[name]  = 0.0   # sources do not absorb
        else:
            excess[name] = 0.0
            avail[name]  = capacity - fv

    total_excess = sum(excess.values())
    total_avail  = sum(avail.values())

    result: Dict[str, float] = {}

    if total_excess < _EPS:
        # Nothing to redistribute
        return {k: float(v) for k, v in loads.items()}

    if total_avail < _EPS:
        # No sink capacity — clamp overloaded sources to SENTINEL_CAPACITY
        for name, v in loads.items():
            result[name] = min(float(v), capacity)
        return result

    # How much excess can actually be absorbed
    absorbed = min(total_excess, total_avail)

    for name, v in loads.items():
        fv = float(v)
        if excess[name] > _EPS:
            # Source: clamp to capacity
            result[name] = capacity
        else:
            # Sink: receive share of absorbed excess
            share = absorbed * avail[name] / total_avail
            result[name] = min(capacity, fv + share)

    return result


def is_overloaded(loads: Dict[str, float]) -> bool:
    """True iff the total load exceeds the system's total capacity.

    This is the irreducible overload condition: when the total entropy
    across all five sentinels exceeds TOTAL_SENTINEL_CAPACITY = 5 × c_s =
    60/37 ≈ 1.622, no redistribution scheme can bring every sentinel below
    its per-sentinel capacity.  The system must either enter the Seed
    Protocol (eject volatile bodies) or accept that some axiom channels
    remain above the eigenvalue floor.

    Parameters
    ----------
    loads : dict[str, float]
        Mapping from SentinelLabel constant → entropy load (≥ 0).

    Returns
    -------
    bool — True iff Σ loads > TOTAL_SENTINEL_CAPACITY.
    """
    return float(sum(loads.values())) > TOTAL_SENTINEL_CAPACITY + _EPS


def sentinel_load_report(
    loads: Dict[str, float],
) -> SentinelLoadReport:
    """Compute the full per-sentinel and system-level load report.

    Runs ``redistribute_sentinel_load`` internally and annotates each
    sentinel with its pre- and post-redistribution state.

    Parameters
    ----------
    loads : dict[str, float]
        Mapping from SentinelLabel constant → entropy load (≥ 0).
        Must contain exactly the keys in SENTINEL_LABELS.

    Returns
    -------
    SentinelLoadReport — complete diagnostic snapshot.

    Raises
    ------
    ValueError (propagated from ``redistribute_sentinel_load``) if any
    label is invalid or any load is negative.
    """
    # Validate via the redistribution function (raises on bad input)
    redistributed = redistribute_sentinel_load(loads)

    capacity     = SENTINEL_CAPACITY
    total_load   = float(sum(loads.values()))
    sys_cap      = TOTAL_SENTINEL_CAPACITY
    sys_overload = total_load > sys_cap + _EPS

    states:            List[SentinelState] = []
    overloaded_names:  List[str]           = []

    for name in SENTINEL_LABELS:
        raw_load  = float(loads[name])
        redist    = float(redistributed[name])
        over      = raw_load > capacity + _EPS
        residual  = float(max(0.0, redist - capacity))
        states.append(SentinelState(
            name=name,
            load=raw_load,
            redistributed_load=redist,
            capacity=capacity,
            overloaded=over,
            residual_overflow=residual,
        ))
        if over:
            overloaded_names.append(name)

    return SentinelLoadReport(
        states=states,
        total_load=total_load,
        system_capacity=sys_cap,
        system_overloaded=sys_overload,
        overloaded_names=overloaded_names,
    )
