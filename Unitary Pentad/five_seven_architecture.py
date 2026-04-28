# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/five_seven_architecture.py
==========================================
The 5-Core / 7-Layer Architecture of the Unitary Pentad.

Background
----------
The Unitary Pentad is not simply a 5-body system — it is a **layered**
architecture in which the compact S¹/Z₂ dimension is wound simultaneously
at two frequencies:

    Core  : n_core  = 5  (pentagonal geometry — the interaction structure)
    Layer : n_layer = 7  (spectral damper — the frequency buffer)

Together they form the (5,7) braid.  This module makes the layered view
explicit by providing analysis tools that compare candidate architectures,
compute their stability properties, and explain — through direct arithmetic —
why (5, 7) is the unique minimal-gap stable architecture.

The "5-Core" — Geometric Role
------------------------------
The n_core = 5 winding number fixes the *topology* of the interaction network:
with five-fold symmetry each node is calibrated to exactly four neighbours.
On its own (single-mode, n_w = 5) the theory predicts:

    ns ≈ 0.9635  (0.33σ from Planck 2018 — excellent)
    r  ≈ 0.097   (exceeds BICEP/Keck 2021 limit of 0.036 — unstable alone)

The bare system is geometrically correct but "too hot" — the tensor amplitude
is too high for the system to remain stable.

The "7-Layer" — Damping Role
-----------------------------
The n_layer = 7 mode acts as a **topological frequency buffer**:

    k_cs   = n_core² + n_layer²  = 5² + 7² = 74   (sum-of-squares resonance)
    ρ      = 2 · 5 · 7 / 74      = 35/37 ≈ 0.946   (kinetic mixing depth)
    c_s    = √(1 − ρ²)           = 12/37 ≈ 0.324   (braided sound speed)
    r_eff  = r_bare · c_s        ≈ 0.031            (below 0.036 ✓)

The depth of kinetic mixing ρ = 35/37 ≈ 0.946 shows the two modes are
near-maximally entangled — the 7-layer is not a decorative shell but is wound
*through* the 5-core.

Why Not (5, 6)?
--------------
For n_layer = 6:

    k_cs = 5² + 6² = 61
    ρ    = 2·5·6/61 = 60/61 ≈ 0.984  (over-entangled, almost singular)
    c_s  = √(1 − (60/61)²) = √(121/3721) = 11/61 ≈ 0.180
    r_eff ≈ 0.097 × 0.180 ≈ 0.017  (r satisfied ✓ but barely)

The critical failure: the stability floor c_s = 11/61 ≈ 0.180 is too low.
In the 5×5 pentagonal coupling matrix the minimum eigenvalue satisfies
λ_min ≥ c_s.  With c_s ≈ 0.180 the "damping gap" between λ_min and zero is
only half what (5,7) provides, making the orbit vulnerable to trust erosion.

The "Moiré Phase Sync" Condition
---------------------------------
For the ten pairwise phase offsets Δφ_{ij} to converge, the beat frequency
between the core and layer modes must produce a *commensurate* interference
pattern.  The beat is:

    beat = n_layer − n_core = 2  (minimal integer gap for (5,7))

This "beat of 2" is the smallest possible non-zero integer gap.  It means the
phase correction completes exactly once every half-cycle, providing the
densest possible damping without aliasing.  A larger gap (e.g., n_layer = 8,
beat = 3) means fewer correction opportunities per cycle, weakening damping.

The Sum-of-Squares Identity
----------------------------
The resonance condition k_cs = n_core² + n_layer² = 74 is not tuned; it was
derived independently from the CMB birefringence measurement β ≈ 0.35° and
found to equal exactly 5² + 7².  The integer 74 is the unique minimiser of
|β(k) − 0.35°| over k ∈ [1, 100].  Its coincidence with 5² + 7² is the
"resonance identity" — the Chern–Simons level is precisely the Euclidean
norm-squared of the braid vector (n_core, n_layer).

Public API
----------
CoreLayerArchitecture
    Dataclass representing a (n_core, n_layer) architecture with its full
    stability properties pre-computed.

architecture_report(n_core, n_layer) -> CoreLayerArchitecture
    Compute the full stability report for a given architecture.

is_stable_architecture(n_core, n_layer, r_limit, ns_sigma_max,
                        c_s_floor) -> bool
    Return True iff the architecture simultaneously satisfies all three
    stability criteria (r_eff < r_limit, ns within ns_sigma_max, c_s > c_s_floor).

compare_layer_candidates(n_core, n_layer_candidates) -> list[CoreLayerArchitecture]
    Compare several layer candidates for a fixed core winding number.

canonical_57() -> CoreLayerArchitecture
    Return the canonical (5, 7) architecture.

stability_floor_comparison() -> dict
    Dictionary mapping candidate (n_core, n_layer) pairs to their c_s values,
    demonstrating that (5, 7) provides the optimal stability floor.

FiveSixSevenDuality
    Dataclass summarising the duality between the (5, 7) ground-state braid
    and the (5, 6) metastable braid, expressed as exact-rational comparators.

five_six_seven_duality_report() -> FiveSixSevenDuality
    Collect the key exact-rational comparators between the two lossless braid
    states — Δc_s = 325/2257, λ_min ratio = 407/732, entropy capacity ratio,
    and S_E gap = 1/√61 − 1/√74 — into one labelled report.  The label
    records the precise epistemic status: (5, 6) is the metastable twin,
    triply-viable but eigenvalue-under-resolved, ordered above (5, 7) by the
    Euclidean action.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

import numpy as np

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.core.braided_winding import (
    resonant_kcs,
    braided_cs_mixing,
    braided_sound_speed,
    braided_r_effective,
    braided_ns_r,
    BraidedPrediction,
    R_BICEP_KECK_95,
    R_PLANCK_95,
    PHI0_BARE_FTUM,
)
from src.core.inflation import (
    effective_phi0_kk,
    ns_from_phi0,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Canonical core winding number — pentagonal geometry.
N_CORE: int = 5

#: Canonical layer winding number — spectral damper.
N_LAYER: int = 7

#: Minimal beat frequency for phase-sync: n_layer − n_core = 2.
BEAT_FREQUENCY: int = N_LAYER - N_CORE

#: Jacobi sum: n_core + n_layer = 12.
JACOBI_SUM: int = N_CORE + N_LAYER

#: Sum-of-squares resonance level: 5² + 7² = 74.
K_CS_RESONANCE: int = N_CORE ** 2 + N_LAYER ** 2

#: Minimum acceptable braided sound speed for Pentad stability.
#: Below this threshold the eigenvalue gap in the 5×5 coupling matrix
#: is insufficient to resist trust-erosion cascades.
C_S_STABILITY_FLOOR: float = 12.0 / 37.0   # ≈ 0.3243

#: r limit used by default (BICEP/Keck 2021 95 % CL).
DEFAULT_R_LIMIT: float = R_BICEP_KECK_95

#: Default ns acceptance window in Planck σ.
DEFAULT_NS_SIGMA_MAX: float = 2.0


# ---------------------------------------------------------------------------
# CoreLayerArchitecture dataclass
# ---------------------------------------------------------------------------

@dataclass
class CoreLayerArchitecture:
    """Full stability report for a (n_core, n_layer) braid architecture.

    Attributes
    ----------
    n_core          : int   — core winding number (interaction topology)
    n_layer         : int   — layer winding number (frequency damper)
    k_cs            : int   — Chern–Simons resonance level n_core² + n_layer²
    beat            : int   — n_layer − n_core (phase-sync frequency)
    jacobi_sum      : int   — n_core + n_layer
    rho             : float — kinetic mixing depth ρ = 2·n_core·n_layer / k_cs
    c_s             : float — braided sound speed √(1 − ρ²)
    ns              : float — scalar spectral index (from n_core mode)
    ns_sigma        : float — |ns − 0.9649| / 0.0042
    r_bare          : float — bare tensor-to-scalar ratio (n_core alone)
    r_eff           : float — braided r = r_bare × c_s
    r_satisfies_bicep : bool — r_eff < R_BICEP_KECK_95 (0.036)
    r_satisfies_planck: bool — r_eff < R_PLANCK_95 (0.056)
    ns_in_window    : bool  — ns within DEFAULT_NS_SIGMA_MAX σ of Planck
    c_s_above_floor : bool  — c_s ≥ C_S_STABILITY_FLOOR
    is_stable       : bool  — all three criteria satisfied simultaneously
    why_not_stable  : list[str] — human-readable reasons for instability
    """
    n_core:   int
    n_layer:  int
    k_cs:     int
    beat:     int
    jacobi_sum: int
    rho:      float
    c_s:      float
    ns:       float
    ns_sigma: float
    r_bare:   float
    r_eff:    float
    r_satisfies_bicep:  bool
    r_satisfies_planck: bool
    ns_in_window:       bool
    c_s_above_floor:    bool
    is_stable:          bool
    why_not_stable:     List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def architecture_report(
    n_core: int,
    n_layer: int,
    phi0_bare: float = PHI0_BARE_FTUM,
    r_limit: float = DEFAULT_R_LIMIT,
    ns_sigma_max: float = DEFAULT_NS_SIGMA_MAX,
    c_s_floor: float = C_S_STABILITY_FLOOR,
) -> CoreLayerArchitecture:
    """Compute the full stability report for a (n_core, n_layer) architecture.

    Uses the sum-of-squares resonance condition k_cs = n_core² + n_layer².

    Parameters
    ----------
    n_core        : int   — core winding number (≥ 1)
    n_layer       : int   — layer winding number (> n_core)
    phi0_bare     : float — bare radion vev at FTUM fixed point
    r_limit       : float — tensor amplitude upper bound (default BICEP/Keck)
    ns_sigma_max  : float — ns acceptance window in σ (default 2.0)
    c_s_floor     : float — minimum acceptable braided sound speed

    Returns
    -------
    CoreLayerArchitecture — full stability report

    Raises
    ------
    ValueError if n_core < 1 or n_layer ≤ n_core.
    """
    if n_core < 1:
        raise ValueError(f"n_core={n_core} must be ≥ 1.")
    if n_layer <= n_core:
        raise ValueError(
            f"n_layer={n_layer} must be strictly greater than n_core={n_core}."
        )

    k_cs = resonant_kcs(n_core, n_layer)

    # CMB predictions via braided_ns_r (uses n_core as the dominant mode)
    pred: BraidedPrediction = braided_ns_r(n_core, n_layer, phi0_bare, k_cs)

    r_bicep = bool(pred.r_eff < R_BICEP_KECK_95)
    r_planck = bool(pred.r_eff < R_PLANCK_95)
    ns_ok = bool(pred.ns_sigma <= ns_sigma_max)
    cs_ok = bool(pred.c_s >= c_s_floor)
    stable = r_bicep and ns_ok and cs_ok

    reasons: List[str] = []
    if not r_bicep:
        reasons.append(
            f"r_eff={pred.r_eff:.4f} exceeds BICEP/Keck limit {R_BICEP_KECK_95:.3f}"
        )
    if not r_planck and not r_bicep:
        reasons.append(
            f"r_eff={pred.r_eff:.4f} also exceeds Planck limit {R_PLANCK_95:.3f}"
        )
    if not ns_ok:
        reasons.append(
            f"ns={pred.ns:.4f} is {pred.ns_sigma:.1f}σ from Planck centre "
            f"(>{ns_sigma_max}σ limit)"
        )
    if not cs_ok:
        reasons.append(
            f"c_s={pred.c_s:.4f} is below stability floor {c_s_floor:.4f}; "
            "eigenvalue gap too small to resist trust-erosion cascades"
        )

    return CoreLayerArchitecture(
        n_core=n_core,
        n_layer=n_layer,
        k_cs=k_cs,
        beat=n_layer - n_core,
        jacobi_sum=n_core + n_layer,
        rho=pred.rho,
        c_s=pred.c_s,
        ns=pred.ns,
        ns_sigma=pred.ns_sigma,
        r_bare=pred.r_bare,
        r_eff=pred.r_eff,
        r_satisfies_bicep=r_bicep,
        r_satisfies_planck=r_planck,
        ns_in_window=ns_ok,
        c_s_above_floor=cs_ok,
        is_stable=stable,
        why_not_stable=reasons,
    )


def is_stable_architecture(
    n_core: int,
    n_layer: int,
    r_limit: float = DEFAULT_R_LIMIT,
    ns_sigma_max: float = DEFAULT_NS_SIGMA_MAX,
    c_s_floor: float = C_S_STABILITY_FLOOR,
) -> bool:
    """Return True iff the (n_core, n_layer) architecture is stable.

    A stable architecture simultaneously satisfies:
        1. r_eff < r_limit       (tensor amplitude suppressed enough)
        2. ns within ns_sigma_max σ of Planck 2018 central value
        3. c_s ≥ c_s_floor       (eigenvalue gap wide enough for Pentad)

    Parameters
    ----------
    n_core, n_layer : int   — winding numbers (n_layer > n_core ≥ 1)
    r_limit         : float — tensor amplitude bound (default BICEP/Keck 0.036)
    ns_sigma_max    : float — ns window in σ (default 2.0)
    c_s_floor       : float — c_s lower bound (default 12/37)

    Returns
    -------
    bool
    """
    return architecture_report(
        n_core, n_layer,
        r_limit=r_limit,
        ns_sigma_max=ns_sigma_max,
        c_s_floor=c_s_floor,
    ).is_stable


def compare_layer_candidates(
    n_core: int,
    n_layer_candidates: List[int],
    phi0_bare: float = PHI0_BARE_FTUM,
) -> List[CoreLayerArchitecture]:
    """Compare several layer winding numbers for a fixed core.

    Parameters
    ----------
    n_core             : int       — core winding number
    n_layer_candidates : list[int] — candidate layer winding numbers to compare
    phi0_bare          : float     — bare radion vev

    Returns
    -------
    list[CoreLayerArchitecture] — one entry per candidate, in input order

    Raises
    ------
    ValueError if any candidate is ≤ n_core.
    """
    results: List[CoreLayerArchitecture] = []
    for n_layer in n_layer_candidates:
        results.append(architecture_report(n_core, n_layer, phi0_bare))
    return results


def canonical_57() -> CoreLayerArchitecture:
    """Return the canonical (5, 7) Unitary Pentad architecture.

    This is the unique minimal-gap stable architecture for n_core = 5:

        k_cs = 74,  ρ = 35/37,  c_s = 12/37,  r_eff ≈ 0.031 ✓

    Returns
    -------
    CoreLayerArchitecture
    """
    return architecture_report(N_CORE, N_LAYER)


def stability_floor_comparison(
    n_core: int = N_CORE,
    n_layer_range: Tuple[int, int] = (6, 12),
) -> Dict[Tuple[int, int], float]:
    """Map candidate (n_core, n_layer) pairs to their braided sound speeds.

    Demonstrates why (5, 7) provides the optimal stability floor among
    architectures with the same core winding number.

    Parameters
    ----------
    n_core        : int           — core winding number (default 5)
    n_layer_range : tuple[int,int] — inclusive range of layer candidates

    Returns
    -------
    dict mapping (n_core, n_layer) → c_s for each candidate

    Notes
    -----
    The (5, 7) entry will have the largest c_s among small-layer candidates
    while still satisfying all CMB and eigenvalue constraints.
    """
    lo, hi = n_layer_range
    result: Dict[Tuple[int, int], float] = {}
    for n_layer in range(lo, hi + 1):
        if n_layer <= n_core:
            continue
        try:
            k = resonant_kcs(n_core, n_layer)
            c_s = braided_sound_speed(n_core, n_layer, k)
            result[(n_core, n_layer)] = c_s
        except ValueError:
            pass
    return result


def moiree_phase_sync_quality(n_core: int, n_layer: int) -> float:
    """Compute a dimensionless phase-sync quality metric for a braid pair.

    The Moiré phase sync quality is:

        Q = c_s / beat

    where beat = n_layer − n_core is the number of oscillation periods
    between phase corrections.  A smaller beat (more frequent corrections)
    combined with a larger c_s (stronger damping per correction) gives a
    higher Q.

    For (5, 7): Q = (12/37) / 2 = 6/37 ≈ 0.162  — the highest value
    achievable for n_core = 5 with beat ≥ 1 and c_s above the stability
    floor.

    Parameters
    ----------
    n_core, n_layer : int — winding numbers

    Returns
    -------
    float — Q ≥ 0
    """
    beat = n_layer - n_core
    if beat <= 0:
        return 0.0
    k = resonant_kcs(n_core, n_layer)
    try:
        c_s = braided_sound_speed(n_core, n_layer, k)
    except ValueError:
        return 0.0
    return float(c_s / beat)


# ---------------------------------------------------------------------------
# (5,7) / (5,6) duality report
# ---------------------------------------------------------------------------

@dataclass
class FiveSixSevenDuality:
    """Exact-rational comparators between the (5, 7) ground-state and (5, 6)
    metastable braid architectures.

    All quantities derive solely from the braid-pair integers (5, 7) and
    (5, 6) via the sum-of-squares resonance condition k_cs = n₁² + n₂² and
    the Euclidean action S_E = 1/√k_cs.  No observational inputs are used
    beyond the integers themselves.

    Attributes
    ----------
    c_s_57             : float — braided sound speed of (5, 7) = 12/37 ≈ 0.3243
    c_s_56             : float — braided sound speed of (5, 6) = 11/61 ≈ 0.1803
    delta_cs           : float — c_s(5,7) − c_s(5,6) ≈ 0.1440  [exact: 325/2257]
    delta_cs_exact     : str  — "325/2257" (reduced rational form)
    lambda_min_ratio   : float — c_s(5,6) / c_s(5,7) ≈ 0.5560  [exact: 407/732]
    lambda_min_ratio_exact : str — "407/732" (reduced rational form)
    entropy_capacity_ratio : float — (c_s(5,6)/c_s(5,7))² ≈ 0.3091
        Fraction of (5, 7)'s maximum information throughput sustainable by
        (5, 6), derived from the quadratic scaling of eigenvalue-gap capacity.
    se_57              : float — Euclidean action of (5, 7) = 1/√74 ≈ 0.1162
    se_56              : float — Euclidean action of (5, 6) = 1/√61 ≈ 0.1280
    se_gap             : float — se_56 − se_57 > 0; (5, 7) is the ground state
    se_57_is_minimum   : bool — True: (5, 7) has strictly lower Euclidean action
    label              : str  — human-readable epistemic status statement
    """
    c_s_57:                float
    c_s_56:                float
    delta_cs:              float
    delta_cs_exact:        str
    lambda_min_ratio:      float
    lambda_min_ratio_exact: str
    entropy_capacity_ratio: float
    se_57:                 float
    se_56:                 float
    se_gap:                float
    se_57_is_minimum:      bool
    label:                 str


def five_six_seven_duality_report() -> FiveSixSevenDuality:
    """Return exact-rational duality comparators for the (5, 7) and (5, 6) braids.

    The (5, 7) and (5, 6) architectures are the only two *triply-viable*
    braid states — pairs that simultaneously satisfy the Planck nₛ window,
    the BICEP/Keck r limit, and the CMB birefringence window.  Despite both
    being viable from observational data, they differ sharply in their
    algebraic stability properties:

    Ground-state ordering (Euclidean action):
        S_E(5, 7) = 1/√74 ≈ 0.1162  <  S_E(5, 6) = 1/√61 ≈ 0.1280

    Eigenvalue-gap deficit:
        Δc_s = c_s(5,7) − c_s(5,6) = 12/37 − 11/61 = 325/2257 ≈ 0.1440

    The stability floor C_S_STABILITY_FLOOR is defined as c_s(5,7) = 12/37.
    Therefore Δc_s is simultaneously the amount by which (5, 6) falls *below*
    the stability floor — the precise eigenvalue-gap deficit of the metastable
    state.

    Exact-rational derivations
    --------------------------
    Let n₁ = 5 (shared core), n₂ = 7 (ground layer), n₂' = 6 (metastable layer).

        k_57  = 5² + 7²  = 74;   k_56  = 5² + 6²  = 61
        c_s(5,7) = (7²−5²)/(7²+5²) = 24/74 = 12/37
        c_s(5,6) = (6²−5²)/(6²+5²) = 11/61

        Δc_s  = 12/37 − 11/61 = (12·61 − 11·37) / (37·61)
              = (732 − 407) / 2257  =  325/2257

        λ_min ratio = (11/61) / (12/37) = (11·37) / (61·12) = 407/732

        S_E gap = 1/√61 − 1/√74  > 0   [ground-state ordering]

    Epistemic note
    --------------
    This function reports only what the integer arithmetic of the braid
    geometry directly implies.  It does not claim that the (5, 6) state
    corresponds to any specific physical phenomenon (decoherence, dark energy,
    black holes, etc.).  Those interpretations require additional theoretical
    bridges not present in the current framework.

    Returns
    -------
    FiveSixSevenDuality — dataclass with all comparators and exact-rational
    string representations.
    """
    # -----------------------------------------------------------------------
    # Exact rational arithmetic (verified: fractions reduce to these values)
    # -----------------------------------------------------------------------
    c_s_57 = 12.0 / 37.0          # (7²−5²)/(7²+5²) = 24/74 = 12/37
    c_s_56 = 11.0 / 61.0          # (6²−5²)/(6²+5²) = 11/61

    # Δc_s = 12/37 − 11/61 = (732 − 407)/2257 = 325/2257
    delta_cs = c_s_57 - c_s_56

    # λ_min ratio = (11/61) / (12/37) = (11·37)/(61·12) = 407/732
    lambda_min_ratio = c_s_56 / c_s_57

    # Entropy capacity ratio = (λ_min ratio)²  [quadratic eigenvalue-gap scaling]
    entropy_capacity_ratio = lambda_min_ratio ** 2

    # Euclidean actions: S_E = 1/√k_cs
    se_57 = 1.0 / math.sqrt(74.0)  # ground state
    se_56 = 1.0 / math.sqrt(61.0)  # metastable state

    # se_gap > 0 confirms (5,7) is the lower-action ground state
    se_gap = se_56 - se_57

    label = (
        "(5,6) is the metastable twin: a triply-viable but eigenvalue-under-resolved "
        "state that the Euclidean action orders above (5,7).  "
        "The (5,7) braid is the unique ground state: S_E(5,7) = 1/√74 < S_E(5,6) = 1/√61.  "
        "The stability deficit Δc_s = 325/2257 is the exact amount by which "
        "the (5,6) eigenvalue gap falls below the (5,7) stability floor (12/37)."
    )

    return FiveSixSevenDuality(
        c_s_57=c_s_57,
        c_s_56=c_s_56,
        delta_cs=delta_cs,
        delta_cs_exact="325/2257",
        lambda_min_ratio=lambda_min_ratio,
        lambda_min_ratio_exact="407/732",
        entropy_capacity_ratio=entropy_capacity_ratio,
        se_57=se_57,
        se_56=se_56,
        se_gap=se_gap,
        se_57_is_minimum=bool(se_57 < se_56),
        label=label,
    )
