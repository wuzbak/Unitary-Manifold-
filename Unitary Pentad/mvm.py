# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/mvm.py
=====================
Minimum Viable Manifold (MVM): Hardware-Constrained Architecture Search.

Background
----------
The canonical Unitary Pentad operates at the (5,7) braid fixed point.  In
practice — a DIY hardware setup, a resource-limited deployment, or an early
bootstrap phase before the full SATURATION_N validators are available — the
question arises: **what is the smallest (n_core, n_layer) configuration that
still satisfies all three stability criteria under given hardware constraints?**

This is a well-defined optimisation problem:

    Minimise  n_layer  subject to:
        architecture_report(n_core, n_layer).is_stable == True
        n_layer ≤ n_layer_max
        (n_core is fixed by the HILS framework to 5)

The answer for unconstrained search is trivially (5, 7) — the unique minimal
stable pair identified by ``five_seven_architecture.py``.  The MVM function
becomes non-trivial when hardware imposes a ceiling on n_layer (e.g., a
low-power embedded node cannot sustain the full spectral-damper complexity)
or when an operator is bootstrapping from a reduced n_core configuration.

MVMConstraints
--------------
    n_core     : int   — core winding number (default N_CORE = 5).
                         Fixed by the HILS pentagonal framework; change
                         only for sub-braid bootstrap scenarios.
    n_layer_max: int   — upper bound on layer winding number the hardware
                         can support (default 20).
    r_limit    : float — CMB tensor-to-scalar upper bound (default BICEP/Keck).
    ns_sigma_max: float — scalar spectral index acceptance window (default 2σ).
    c_s_floor  : float — minimum braided sound speed (default C_S_STABILITY_FLOOR).

MinimumViableManifold
---------------------
Result dataclass returned by ``minimum_viable_manifold``:

    architecture  : CoreLayerArchitecture | None — smallest viable pair,
                    or None if no stable pair exists within constraints.
    constraints   : MVMConstraints — the constraints used in the search.
    search_steps  : int — number of (n_core, n_layer) pairs examined.
    is_viable     : bool — True iff a stable architecture was found.
    reason        : str — human-readable outcome description.

Search Order
------------
The search increments n_layer from n_core + 1 to n_layer_max and returns
the FIRST stable architecture found.  Because stability at n_layer = 7
requires the c_s constraint (c_s ≥ 12/37), smaller n_layer values are
checked first and rejected for the right physical reason:

    n_layer = 6 → c_s = 11/61 ≈ 0.180 < 0.324  (stability floor too low)
    n_layer = 7 → c_s = 12/37 ≈ 0.324 ✓  (canonical MVM result)
    n_layer = 8 → r_eff ≈ 0.042 > 0.036  (tensor amplitude too high)

So the MVM is not just the first n_layer that satisfies r — it finds the
unique n_layer that simultaneously passes all three criteria.

Validators-to-Floor Utility
-----------------------------
``validators_to_reach_floor(target_floor)`` answers: how many aligned
validators are needed to raise the collective stability floor (from
``collective_braid.collective_stability_floor``) to ``target_floor``?
This is the inverse of ``collective_stability_floor`` and is useful for
planning the "bootstrapping" trajectory toward full SATURATION_N.

Hardware Profile Factory
------------------------
``hardware_profile(n_layer_max, n_core)`` creates an MVMConstraints with
all other fields at canonical defaults.  Useful for quick "what's the
smallest viable system for my hardware?" queries.

Public API
----------
MVM_N_LAYER_SEARCH_MAX : int = 20
    Default upper bound on the n_layer search.

MVMConstraints
    Dataclass: n_core, n_layer_max, r_limit, ns_sigma_max, c_s_floor.

MinimumViableManifold
    Dataclass: architecture, constraints, search_steps, is_viable, reason.

mvm_search(constraints) → tuple[CoreLayerArchitecture | None, int]
    Inner search: returns (first stable architecture, steps examined).

minimum_viable_manifold(constraints=None) → MinimumViableManifold
    Public entry point: find the smallest viable (n_core, n_layer) pair.

validators_to_reach_floor(target_floor, n_validators_max) → int
    Minimum number of aligned validators to reach a collective c_s floor.

hardware_profile(n_layer_max, n_core) → MVMConstraints
    Factory: canonical constraints with a custom n_layer ceiling.
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
from typing import Optional, Tuple

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from five_seven_architecture import (
    N_CORE,
    N_LAYER,
    C_S_STABILITY_FLOOR,
    DEFAULT_R_LIMIT,
    DEFAULT_NS_SIGMA_MAX,
    CoreLayerArchitecture,
    architecture_report,
)
from distributed_authority import SATURATION_N
from collective_braid import collective_stability_floor


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Default upper bound on the n_layer search dimension.
MVM_N_LAYER_SEARCH_MAX: int = 20

#: Default core winding number for MVM search (HILS pentagonal requirement).
MVM_N_CORE_DEFAULT: int = N_CORE  # 5

_EPS: float = 1e-12


# ---------------------------------------------------------------------------
# MVMConstraints
# ---------------------------------------------------------------------------

@dataclass
class MVMConstraints:
    """Hardware and physics constraints for the MVM search.

    Attributes
    ----------
    n_core       : int   — core winding number to search with (default 5).
                           The HILS pentagonal framework requires n_core = 5
                           for a full Unitary Pentad; lower values correspond
                           to sub-braid bootstrap configurations.
    n_layer_max  : int   — maximum layer winding number the hardware supports
                           (default MVM_N_LAYER_SEARCH_MAX = 20).
    r_limit      : float — upper bound on r_eff (default: BICEP/Keck 0.036).
    ns_sigma_max : float — acceptance window for ns in Planck σ (default 2.0).
    c_s_floor    : float — minimum acceptable braided sound speed
                           (default C_S_STABILITY_FLOOR = 12/37).
    """
    n_core:       int   = MVM_N_CORE_DEFAULT
    n_layer_max:  int   = MVM_N_LAYER_SEARCH_MAX
    r_limit:      float = DEFAULT_R_LIMIT
    ns_sigma_max: float = DEFAULT_NS_SIGMA_MAX
    c_s_floor:    float = C_S_STABILITY_FLOOR

    def __post_init__(self) -> None:
        if self.n_core < 1:
            raise ValueError(f"n_core={self.n_core} must be ≥ 1.")
        if self.n_layer_max <= self.n_core:
            raise ValueError(
                f"n_layer_max={self.n_layer_max} must be > n_core={self.n_core}."
            )
        if self.r_limit <= 0.0:
            raise ValueError(f"r_limit={self.r_limit} must be > 0.")
        if self.ns_sigma_max <= 0.0:
            raise ValueError(f"ns_sigma_max={self.ns_sigma_max} must be > 0.")
        if not (0.0 < self.c_s_floor < 1.0):
            raise ValueError(f"c_s_floor={self.c_s_floor} must be in (0, 1).")


# ---------------------------------------------------------------------------
# MinimumViableManifold
# ---------------------------------------------------------------------------

@dataclass
class MinimumViableManifold:
    """Result of the MVM search.

    Attributes
    ----------
    architecture  : CoreLayerArchitecture | None
        The smallest stable (n_core, n_layer) pair found, or None if no
        stable pair exists within the given constraints.
    constraints   : MVMConstraints
        The constraints used in the search.
    search_steps  : int
        Number of (n_core, n_layer) pairs examined before terminating.
    is_viable     : bool
        True iff a stable architecture was found.
    reason        : str
        Human-readable description of the outcome.
    """
    architecture:  Optional[CoreLayerArchitecture]
    constraints:   MVMConstraints
    search_steps:  int
    is_viable:     bool
    reason:        str


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def mvm_search(
    constraints: MVMConstraints,
) -> Tuple[Optional[CoreLayerArchitecture], int]:
    """Inner search: return the first stable architecture and steps examined.

    Iterates n_layer from (n_core + 1) to n_layer_max (inclusive), calling
    ``architecture_report`` at each step.  Returns on the first stable result.

    Parameters
    ----------
    constraints : MVMConstraints

    Returns
    -------
    tuple — (CoreLayerArchitecture | None, int)
        First element: the smallest stable architecture, or None.
        Second element: total number of candidate pairs examined.
    """
    steps = 0
    n_core = constraints.n_core
    for n_layer in range(n_core + 1, constraints.n_layer_max + 1):
        steps += 1
        try:
            arch = architecture_report(
                n_core,
                n_layer,
                r_limit=constraints.r_limit,
                ns_sigma_max=constraints.ns_sigma_max,
                c_s_floor=constraints.c_s_floor,
            )
        except ValueError:
            continue
        if arch.is_stable:
            return arch, steps
    return None, steps


def minimum_viable_manifold(
    constraints: Optional[MVMConstraints] = None,
) -> MinimumViableManifold:
    """Find the smallest (n_core, n_layer) architecture satisfying all constraints.

    The MVM is the minimum-complexity configuration that simultaneously
    passes three stability criteria:

        1. r_eff < r_limit        (tensor amplitude suppressed)
        2. ns within ns_sigma_max σ of Planck
        3. c_s ≥ c_s_floor        (eigenvalue gap adequate for Pentad)

    For canonical constraints (default), the result is the (5, 7) architecture
    with k_cs = 74, c_s = 12/37, r_eff ≈ 0.031.

    Parameters
    ----------
    constraints : MVMConstraints | None
        Search constraints.  If None, uses MVMConstraints() defaults
        (n_core = 5, n_layer_max = 20, canonical physics limits).

    Returns
    -------
    MinimumViableManifold — result with architecture (or None), search
    metadata, viability flag, and human-readable reason.
    """
    if constraints is None:
        constraints = MVMConstraints()

    arch, steps = mvm_search(constraints)

    if arch is not None:
        reason = (
            f"Smallest stable architecture: "
            f"(n_core={arch.n_core}, n_layer={arch.n_layer}), "
            f"k_cs={arch.k_cs}, c_s={arch.c_s:.6f}, r_eff={arch.r_eff:.4f}."
        )
        return MinimumViableManifold(
            architecture=arch,
            constraints=constraints,
            search_steps=steps,
            is_viable=True,
            reason=reason,
        )

    reason = (
        f"No stable architecture found for n_core={constraints.n_core}, "
        f"n_layer ∈ [{constraints.n_core + 1}, {constraints.n_layer_max}] "
        f"with r_limit={constraints.r_limit:.3f}, "
        f"c_s_floor={constraints.c_s_floor:.4f}."
    )
    return MinimumViableManifold(
        architecture=None,
        constraints=constraints,
        search_steps=steps,
        is_viable=False,
        reason=reason,
    )


def validators_to_reach_floor(
    target_floor: float,
    n_validators_max: int = SATURATION_N,
) -> int:
    """Minimum number of aligned validators to reach a target collective c_s floor.

    Uses ``collective_braid.collective_stability_floor(n)`` and finds the
    smallest n ∈ [0, n_validators_max] such that the collective floor is
    at or above ``target_floor``.

    This is the bootstrapping trajectory planner: given that you want the
    collective eigenvalue floor to reach some target (e.g., 0.5 for moderate
    resilience, 1.0 for perfect collective stability), how many aligned
    validators do you need?

    Parameters
    ----------
    target_floor     : float — desired collective stability floor ∈ (0, 1].
    n_validators_max : int   — maximum validators to check (default SATURATION_N).

    Returns
    -------
    int — minimum validators required; returns n_validators_max if the target
    is not reached within that range (i.e., returns the saturation count).

    Raises
    ------
    ValueError if target_floor ≤ 0 or target_floor > 1.
    """
    if target_floor <= 0.0:
        raise ValueError(f"target_floor={target_floor} must be > 0.")
    if target_floor > 1.0 + _EPS:
        raise ValueError(f"target_floor={target_floor} must be ≤ 1.")

    for n in range(0, n_validators_max + 1):
        if collective_stability_floor(n) >= target_floor - _EPS:
            return n

    return n_validators_max


def hardware_profile(
    n_layer_max: int,
    n_core: int = MVM_N_CORE_DEFAULT,
) -> MVMConstraints:
    """Factory: build a hardware-constrained MVMConstraints profile.

    All physics limits (r_limit, ns_sigma_max, c_s_floor) are kept at
    canonical defaults.  Only the hardware ceiling on n_layer is customised.

    Typical usage
    -------------
    To find the smallest viable (5, ?) architecture that a device supporting
    at most n_layer = 10 can run:

        profile = hardware_profile(n_layer_max=10)
        mvm = minimum_viable_manifold(profile)
        # mvm.architecture = (5, 7) — the MVM is the same as canonical

    If the device can only support n_layer ≤ 6:

        profile = hardware_profile(n_layer_max=6)
        mvm = minimum_viable_manifold(profile)
        # mvm.is_viable = False — (5, 6) fails the c_s floor

    Parameters
    ----------
    n_layer_max : int — maximum layer winding number for this hardware.
    n_core      : int — core winding number (default 5).

    Returns
    -------
    MVMConstraints with the specified ceiling and canonical physics limits.

    Raises
    ------
    ValueError (from MVMConstraints) if n_layer_max ≤ n_core.
    """
    return MVMConstraints(
        n_core=n_core,
        n_layer_max=n_layer_max,
    )
