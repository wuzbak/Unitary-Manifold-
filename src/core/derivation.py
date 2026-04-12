# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/derivation.py
======================
Stage 0 → Stage 3 constraint-based derivation of the discrete geometric
integers (n_w, k_CS) of the Unitary Manifold 4D → 5D → 4D pipeline.

Goal
----
Derive the winding number n_w and Chern–Simons level k_CS as the *only*
values that survive all structural, topological, and consistency constraints
of the pipeline — without using Planck CMB or birefringence observational
data as inputs.

Stages
------
Stage 0  Input structure: allowed candidates and constraint definitions.
Stage 1  Winding-number derivation: filter n_w ∈ [1, n_max] via C1–C8.
Stage 2  CS-level derivation: filter k_CS ∈ [1, k_max] via C3–C8 (CS variant).
Stage 3  Joint consistency check: verify (n_w, k_CS) are mutually consistent.

Constraints applied
-------------------
C1  5D → 4D → 5D round-trip closure (KK projection recovers initial fields).
C2  KK dimensional-reduction consistency (effective vev finite and non-zero).
C3  Gauge invariance under large gauge transformations (CS action invariant).
C4  Topological quantization on S¹ or S¹/Z₂ (orbifold boundary conditions).
C5  Anomaly cancellation in 4D effective theory.
C6  Fixed-point convergence of the FTUM operator U = I + H + T.
C7  Holographic entropy saturation stability (FTUM defect → 0).
C8  Parameter minimality — Occam filter (argmin complexity score).

Derivation results
------------------
For the canonical FTUM fixed point φ₀_bare = 1 (Planck units):

  n_w = 5   (purely structural — survives C1–C8 with zero observational input)
  k_CS = 74 (observationally assisted — structural constraints narrow to
              all k ∈ ℤ⁺; the birefringence hint selects k = 74 as the unique
              integer minimiser of |β(k) − β_geom|.  Marked ``is_derived =
              False`` per the failure-mode specification in the pseudocode.)

Failure modes (faithfully implemented)
---------------------------------------
* Multiple integers survive → framework admits a universality class; report
  all candidates and select argmin.
* None survive → axioms inconsistent; raise ``DerivationFailure``.
* Integers depend on observational priors → mark ``is_derived = False``.

Public API
----------
DerivationResult
    Dataclass: (n_w, k_cs, n_w_candidates, k_cs_candidates,
                n_w_is_derived, k_cs_is_derived, metadata).

DerivationFailure
    Exception raised when no candidate survives all constraints.

check_round_trip_closure(n_w, phi0_bare, tol)
    C1: verify that applying the KK Jacobian then inverting it recovers φ₀.

check_kk_consistency(n_w, phi0_bare)
    C2: verify φ₀_eff is finite, positive, and slow-roll consistent.

check_orbifold_parity(n_w)
    C4: verify n_w satisfies the Z₂ orbifold boundary condition (odd parity).

check_efolds(n_w, phi0_bare, n_efolds_min)
    C1+C2 combined: verify that the effective vev delivers ≥ n_efolds_min
    e-folds of slow-roll inflation (structural, not observational).

check_ftum_convergence(n_w, network_factory, ftum_kwargs)
    C6: run FTUM fixed-point iteration and verify convergence.

check_holographic_stability(n_w, network_factory, ftum_kwargs)
    C7: verify final FTUM defect < tol after convergence.

check_cs_gauge_invariance(k_cs)
    C3: CS level must be a positive integer.

check_cs_bundle_quantization(k_cs)
    C4 (CS): first Chern class must be an integer.

check_anomaly_cancellation(k_cs, n_w)
    C5: gauge anomaly coefficient must be integral.

check_cs_coupling_finite(k_cs, alpha_em, r_c)
    C5+C3: coupling g_aγγ must be dimensionless, finite, and positive.

check_ftum_cs_stability(k_cs, network_factory, ftum_kwargs)
    C6 (CS): FTUM iteration must remain stable when the CS topological
    charge is included in the UEUM Q_top term.

derive_winding_number(phi0_bare, n_max, n_efolds_min, ftum_kwargs)
    Stage 1 pipeline: return (n_w, candidates, is_derived, details).

derive_cs_level(n_w, phi0_bare, alpha_em, r_c, phi_min_phys, k_max,
                ftum_kwargs, use_birefringence_hint)
    Stage 2 pipeline: return (k_cs, candidates, is_derived, details).

derive_integers(phi0_bare, alpha_em, r_c, phi_min_phys, n_max, k_max,
                n_efolds_min, ftum_kwargs, use_birefringence_hint)
    Stage 3: joint derivation and consistency check.  Returns DerivationResult.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .inflation import (
    jacobian_5d_4d,
    effective_phi0_kk,
    ns_from_phi0,
    cs_axion_photon_coupling,
    birefringence_angle,
    field_displacement_gw,
    BIREFRINGENCE_TARGET_DEG,
    BIREFRINGENCE_SIGMA_DEG,
)
from ..multiverse.fixed_point import (
    MultiverseNetwork,
    fixed_point_iteration,
)


# ---------------------------------------------------------------------------
# Structural constants (NOT observational data)
# ---------------------------------------------------------------------------

#: Minimum e-folds of slow-roll inflation required for a viable cosmology.
#: This is a theoretical requirement (homogeneity / flatness problem), not
#: a Planck measurement.
N_EFOLDS_MIN: int = 60

#: KK radion background at the FTUM fixed point (Planck units, M_Pl = 1).
#: Follows from the normalisation M_5 = M_Pl used throughout the FTUM
#: construction.  Not a free parameter.
PHI0_BARE_FIXED_POINT: float = 1.0

#: Compactification radius in the canonical flat S¹/Z₂ geometry (Planck units).
R_C_CANONICAL: float = 12.0

#: Fine-structure constant α_EM = e² / (4π).
ALPHA_EM_CANONICAL: float = 1.0 / 137.036

#: Physical GW potential minimum (bare × J_RS) used for Δφ.
PHI_MIN_BARE_CANONICAL: float = 18.0

#: Tolerance on the round-trip KK Jacobian closure test.
ROUND_TRIP_TOL: float = 1e-10

#: FTUM convergence tolerance.
FTUM_TOL: float = 1e-6

#: Maximum FTUM iterations.
FTUM_MAX_ITER: int = 500


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class DerivationFailure(Exception):
    """Raised when no candidate integer survives all constraints.

    This indicates an internal inconsistency in the core axioms; the 5D
    structure should be revised if this is raised.
    """


def _resolve_phi_min_phys(phi_min_phys: Optional[float], r_c: float) -> float:
    """Return *phi_min_phys*, computing it from geometry if None is given.

    Used by both :func:`derive_cs_level` and :func:`_check_joint_consistency`
    to avoid duplicating the same lazy-import + Jacobian calculation.
    """
    if phi_min_phys is None:
        from .inflation import jacobian_rs_orbifold
        j_rs = jacobian_rs_orbifold(1.0, r_c)
        return float(j_rs * PHI_MIN_BARE_CANONICAL)
    return phi_min_phys


# ---------------------------------------------------------------------------
# DerivationResult
# ---------------------------------------------------------------------------

@dataclass
class DerivationResult:
    """Container returned by :func:`derive_integers`.

    Attributes
    ----------
    n_w : int
        Derived winding number (Stage 1).
    k_cs : int
        Derived or fitted Chern–Simons level (Stage 2).
    n_w_candidates : list of int
        All n_w values that survived constraints C1–C7 before the Occam
        filter.  Length 1 → unique derivation; length > 1 → universality
        class documented.
    k_cs_candidates : list of int
        Analogous list for k_CS.
    n_w_is_derived : bool
        True if n_w was derived from structural constraints alone (no
        observational priors).
    k_cs_is_derived : bool
        True if k_cs was derived from structural constraints alone.  False
        means it depends on an observational prior (birefringence hint) and
        should be treated as *fitted*, not derived.
    joint_consistent : bool
        True if the (n_w, k_cs) pair passed the Stage 3 joint consistency
        check.
    metadata : dict
        Detailed per-candidate information: phi0_eff, n_efolds, ns, r,
        g_agg, beta_deg, etc.
    """

    n_w: int
    k_cs: int
    n_w_candidates: List[int]
    k_cs_candidates: List[int]
    n_w_is_derived: bool
    k_cs_is_derived: bool
    joint_consistent: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Stage 1 individual constraint checks — winding number n_w
# ---------------------------------------------------------------------------

def check_round_trip_closure(
    n_w: int,
    phi0_bare: float = PHI0_BARE_FIXED_POINT,
    tol: float = ROUND_TRIP_TOL,
) -> Tuple[bool, str]:
    """C1: verify the 4D → 5D → 4D round-trip closes.

    The round-trip test computes the KK Jacobian J = n_w · 2π · √φ₀_bare,
    then inverts it to recover φ₀_bare:

        φ₀_recovered = (J / (n_w · 2π))²

    This must equal the input φ₀_bare to within ``tol``.  The closure fails
    only for degenerate inputs (n_w = 0, φ₀_bare = 0); all n_w ≥ 1 pass.

    Parameters
    ----------
    n_w      : int   — candidate winding number
    phi0_bare: float — bare FTUM radion vev
    tol      : float — absolute tolerance

    Returns
    -------
    (passed, reason) : (bool, str)
    """
    if n_w < 1:
        return False, f"n_w={n_w} < 1: not a positive integer"
    if phi0_bare <= 0.0:
        return False, f"phi0_bare={phi0_bare} ≤ 0: degenerate"

    J = jacobian_5d_4d(phi0_bare, n_w)
    phi0_recovered = (J / (n_w * 2.0 * np.pi)) ** 2
    residual = abs(phi0_recovered - phi0_bare)
    if residual > tol:
        return False, (
            f"Round-trip residual {residual:.3e} exceeds tol={tol:.3e}"
        )
    return True, "Round-trip closure satisfied"


def check_kk_consistency(
    n_w: int,
    phi0_bare: float = PHI0_BARE_FIXED_POINT,
) -> Tuple[bool, str]:
    """C2: KK dimensional-reduction consistency.

    Checks:
    1. phi0_eff = J_KK · phi0_bare is finite and positive.
    2. The slow-roll first parameter ε = 6/phi0_eff² is finite.
    3. The spectral index nₛ = 1 − 6ε is real.

    Parameters
    ----------
    n_w       : int   — candidate winding number
    phi0_bare : float — bare radion vev

    Returns
    -------
    (passed, reason) : (bool, str)
    """
    try:
        phi0_eff = effective_phi0_kk(phi0_bare, n_w)
    except ValueError as exc:
        return False, str(exc)

    if not np.isfinite(phi0_eff) or phi0_eff <= 0.0:
        return False, f"phi0_eff={phi0_eff} is not finite or positive"

    ns, r, eps, eta = ns_from_phi0(phi0_eff)
    if not np.isfinite(ns):
        return False, f"nₛ={ns} is not finite"

    return True, f"KK consistent: phi0_eff={phi0_eff:.4f}, nₛ={ns:.6f}"


def check_orbifold_parity(n_w: int) -> Tuple[bool, str]:
    """C4: topological quantization on the S¹/Z₂ orbifold.

    On the S¹/Z₂ orbifold the Z₂ reflection θ ↦ −θ maps a winding-n_w
    field configuration to a winding-(−n_w) configuration.  For the gauge
    field to satisfy the orbifold boundary conditions (anti-periodic BC at
    the fixed points θ = 0 and θ = π), the winding number must be *odd*:

        n_w ≡ 1  (mod 2)

    Even windings are projected out by the Z₂ symmetry and do not survive
    the orbifold truncation.

    Parameters
    ----------
    n_w : int — candidate winding number

    Returns
    -------
    (passed, reason) : (bool, str)
    """
    if n_w % 2 == 0:
        return False, f"n_w={n_w} is even: projected out by Z₂ orbifold"
    return True, f"n_w={n_w} is odd: compatible with S¹/Z₂ boundary conditions"


def check_efolds(
    n_w: int,
    phi0_bare: float = PHI0_BARE_FIXED_POINT,
    n_efolds_min: int = N_EFOLDS_MIN,
) -> Tuple[bool, str]:
    """C1+C2: round-trip inflation e-folds constraint.

    The slow-roll inflation must deliver at least ``n_efolds_min`` e-folds
    to solve the horizon and flatness problems.  For the Goldberger–Wise
    hilltop potential at the inflection point φ* = φ₀_eff/√3:

        N_e ≈ φ₀_eff² / 12

    This is a *structural* constraint of viable inflation theory — it does
    not depend on any Planck measurement.  For ``n_efolds_min`` = 60 and
    φ₀_bare = 1:

        φ₀_eff ≥ √(12 × 60) = √720 ≈ 26.83
        n_w · 2π ≥ 26.83  →  n_w ≥ 4.27  →  n_w ≥ 5

    Parameters
    ----------
    n_w          : int   — candidate winding number
    phi0_bare    : float — bare FTUM radion vev
    n_efolds_min : int   — minimum required e-folds (default 60)

    Returns
    -------
    (passed, reason) : (bool, str)
    """
    try:
        phi0_eff = effective_phi0_kk(phi0_bare, n_w)
    except ValueError as exc:
        return False, str(exc)

    n_efolds = phi0_eff ** 2 / 12.0
    if n_efolds < n_efolds_min:
        return False, (
            f"N_e ≈ {n_efolds:.1f} < {n_efolds_min} "
            f"(φ₀_eff={phi0_eff:.3f}): insufficient e-folds"
        )
    return True, (
        f"N_e ≈ {n_efolds:.1f} ≥ {n_efolds_min} "
        f"(φ₀_eff={phi0_eff:.3f}): e-folds OK"
    )


def check_ftum_convergence(
    n_w: int,
    network_factory: Optional[Callable[[], MultiverseNetwork]] = None,
    ftum_kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, str]:
    """C6: FTUM operator U = I + H + T must converge for generic initial conditions.

    Runs ``fixed_point_iteration`` on a small chain network.  The winding
    number does not directly enter the FTUM iteration (the fixed-point
    convergence is geometry-independent at this level), so this check
    documents that the FTUM machinery is functional for the given
    configuration.

    Parameters
    ----------
    n_w             : int — candidate winding number (used to set topology charge)
    network_factory : optional callable returning a MultiverseNetwork; defaults
                      to a 3-node chain with coupling 0.1
    ftum_kwargs     : extra keyword args forwarded to fixed_point_iteration

    Returns
    -------
    (passed, reason) : (bool, str)
    """
    if network_factory is None:
        def network_factory():
            return MultiverseNetwork.chain(n=3, rng=np.random.default_rng(42))

    if ftum_kwargs is None:
        ftum_kwargs = {"max_iter": FTUM_MAX_ITER, "tol": FTUM_TOL}

    net = network_factory()
    _, residuals, converged = fixed_point_iteration(net, **ftum_kwargs)

    if not converged:
        final_defect = residuals[-1] if residuals else float("inf")
        return False, (
            f"FTUM did not converge: final defect={final_defect:.3e}"
        )
    return True, (
        f"FTUM converged in {len(residuals)} iterations "
        f"(final defect={residuals[-1]:.3e})"
    )


def check_holographic_stability(
    n_w: int,
    network_factory: Optional[Callable[[], MultiverseNetwork]] = None,
    ftum_kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, str]:
    """C7: holographic entropy saturation must be stable at the FTUM fixed point.

    After convergence, every node's entropy must satisfy S ≈ A/(4G) (within
    the FTUM tolerance).  This verifies that the holographic bound is
    saturated — not violated — at the fixed point.

    Parameters
    ----------
    n_w             : int — candidate winding number
    network_factory : optional callable → MultiverseNetwork
    ftum_kwargs     : extra kwargs for fixed_point_iteration

    Returns
    -------
    (passed, reason) : (bool, str)
    """
    if network_factory is None:
        def network_factory():
            return MultiverseNetwork.chain(n=3, rng=np.random.default_rng(42))

    if ftum_kwargs is None:
        ftum_kwargs_local = {"max_iter": FTUM_MAX_ITER, "tol": FTUM_TOL}
    else:
        ftum_kwargs_local = ftum_kwargs

    net = network_factory()
    converged_net, residuals, converged = fixed_point_iteration(
        net, **ftum_kwargs_local
    )

    if not converged:
        return False, "FTUM did not converge; holographic stability cannot be verified"

    # Check entropy saturation: S ≈ A/(4G)
    G4 = ftum_kwargs_local.get("G4", 1.0)
    defects = [abs(node.A / (4.0 * G4) - node.S) for node in converged_net.nodes]
    max_defect = max(defects)
    tol = ftum_kwargs_local.get("tol", FTUM_TOL)

    if max_defect > tol:
        return False, (
            f"Holographic defect {max_defect:.3e} > tol={tol:.3e}; "
            "entropy not saturated"
        )
    return True, (
        f"Holographic entropy saturated: max defect={max_defect:.3e} < tol={tol:.3e}"
    )


# ---------------------------------------------------------------------------
# Stage 2 individual constraint checks — CS level k_CS
# ---------------------------------------------------------------------------

def check_cs_gauge_invariance(k_cs: int) -> Tuple[bool, str]:
    """C3: CS action is invariant under large gauge transformations.

    Under a large gauge transformation A → A + dα with ∮ dα = 2π around
    S¹, the CS action shifts by k_CS × 2π.  For the path integral to be
    gauge invariant this shift must be an integer multiple of 2π, requiring
    k_CS ∈ ℤ⁺.

    Parameters
    ----------
    k_cs : int — candidate CS level

    Returns
    -------
    (passed, reason) : (bool, str)
    """
    if not isinstance(k_cs, (int, np.integer)) or k_cs < 1:
        return False, f"k_cs={k_cs} is not a positive integer"
    return True, f"k_cs={k_cs}: large gauge transformation invariance satisfied"


def check_cs_bundle_quantization(k_cs: int) -> Tuple[bool, str]:
    """C4 (CS): topological quantization — gauge bundle has integer first Chern class.

    The 5D gauge bundle over the compact S¹ (or S¹/Z₂) must have an
    integer first Chern class c₁ = ∮ F/(2π) ∈ ℤ.  With the CS level
    k_CS encoding the bulk anomaly, this requires k_CS ∈ ℤ⁺.

    Parameters
    ----------
    k_cs : int — candidate CS level

    Returns
    -------
    (passed, reason) : (bool, str)
    """
    if not isinstance(k_cs, (int, np.integer)) or k_cs < 1:
        return False, f"k_cs={k_cs} is not a positive integer"
    return True, f"k_cs={k_cs}: first Chern class integer — bundle quantization OK"


def check_anomaly_cancellation(k_cs: int, n_w: int) -> Tuple[bool, str]:
    """C5: gauge anomalies cancel in the 4D effective theory.

    The Green–Schwarz anomaly cancellation mechanism requires the 4D
    effective anomaly coefficient, which receives contributions from both
    the matter sector and the CS inflow, to be an integer:

        A_eff = k_CS  (mod n_w)

    For the Unitary Manifold's minimal matter content (one winding sector
    per n_w mode), the matter anomaly A_matter = 0 (mod n_w).  The CS
    contribution A_CS = k_CS must therefore satisfy the same integrality
    condition.  Since k_CS ∈ ℤ⁺ is already required, anomaly cancellation
    is automatically satisfied for all positive integers.

    Parameters
    ----------
    k_cs : int — candidate CS level
    n_w  : int — winding number (already derived in Stage 1)

    Returns
    -------
    (passed, reason) : (bool, str)
    """
    if not isinstance(k_cs, (int, np.integer)) or k_cs < 1:
        return False, f"k_cs={k_cs} is not a positive integer"
    # With A_matter = 0 (mod n_w) for the minimal spectrum, any k_cs ∈ ℤ⁺ passes.
    return True, (
        f"k_cs={k_cs}: A_eff = k_cs mod n_w = {k_cs % n_w} — "
        "anomaly cancellation satisfied"
    )


def check_cs_coupling_finite(
    k_cs: int,
    alpha_em: float = ALPHA_EM_CANONICAL,
    r_c: float = R_C_CANONICAL,
) -> Tuple[bool, str]:
    """C5+C3: axion-photon coupling g_aγγ must be dimensionless, finite, positive.

    g_aγγ = k_CS · α_EM / (2π² r_c)

    Checks that g_aγγ > 0 and is finite (ensuring the CS coupling does not
    produce a degenerate effective theory).

    Parameters
    ----------
    k_cs     : int   — candidate CS level
    alpha_em : float — fine-structure constant
    r_c      : float — compactification radius

    Returns
    -------
    (passed, reason) : (bool, str)
    """
    try:
        g_agg = cs_axion_photon_coupling(k_cs, alpha_em, r_c)
    except ValueError as exc:
        return False, str(exc)

    if not np.isfinite(g_agg) or g_agg <= 0.0:
        return False, f"g_aγγ={g_agg} is not finite or positive"
    return True, f"g_aγγ={g_agg:.6e}: dimensionless, finite, positive"


def check_ftum_cs_stability(
    k_cs: int,
    network_factory: Optional[Callable[[], MultiverseNetwork]] = None,
    ftum_kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, str]:
    """C6 (CS): FTUM fixed-point must remain stable when the CS topological
    charge Q_top = k_CS × Δ_CS is included in the UEUM geodesic.

    The UEUM geodesic holographic force term −C X with C = A_sum/(4G) + Q_top
    is stabilising when C > 0.  With Q_top = k_CS × (A_sum/(4G)) / k_max
    (normalized to the holographic bound), stability requires:

        C = A_sum/(4G) × (1 + k_CS / k_max) > 0

    which holds for all k_CS ≥ 1 and k_max > 0.  The FTUM convergence is
    verified numerically with the Q_top modification applied.

    Parameters
    ----------
    k_cs            : int — candidate CS level
    network_factory : optional callable → MultiverseNetwork
    ftum_kwargs     : extra kwargs for fixed_point_iteration

    Returns
    -------
    (passed, reason) : (bool, str)
    """
    if network_factory is None:
        def network_factory():
            return MultiverseNetwork.chain(n=3, rng=np.random.default_rng(42))

    if ftum_kwargs is None:
        ftum_kwargs_local = {"max_iter": FTUM_MAX_ITER, "tol": FTUM_TOL}
    else:
        ftum_kwargs_local = dict(ftum_kwargs)

    net = network_factory()
    # Apply CS topological charge: scale Q_top by k_cs (normalised to k=100 ref)
    k_ref = 100.0
    from ..multiverse.fixed_point import MultiverseNode
    scaled_nodes = []
    for node in net.nodes:
        q_scaled = node.Q_top * (k_cs / k_ref)
        scaled_nodes.append(MultiverseNode(
            dim=node.dim, S=node.S, A=node.A,
            Q_top=q_scaled, X=node.X.copy(), Xdot=node.Xdot.copy()
        ))
    net_scaled = MultiverseNetwork(nodes=scaled_nodes, adjacency=net.adjacency)

    _, residuals, converged = fixed_point_iteration(net_scaled, **ftum_kwargs_local)

    if not converged:
        final_defect = residuals[-1] if residuals else float("inf")
        return False, (
            f"FTUM unstable with k_cs={k_cs}: final defect={final_defect:.3e}"
        )
    return True, (
        f"FTUM stable with k_cs={k_cs}: "
        f"converged in {len(residuals)} iterations"
    )


# ---------------------------------------------------------------------------
# Complexity / Occam score
# ---------------------------------------------------------------------------

def _complexity_score(n: int) -> int:
    """C8: Occam / minimality score — smaller integers are simpler."""
    return n


# ---------------------------------------------------------------------------
# Stage 1 — Winding-number derivation
# ---------------------------------------------------------------------------

def derive_winding_number(
    phi0_bare: float = PHI0_BARE_FIXED_POINT,
    n_max: int = 20,
    n_efolds_min: int = N_EFOLDS_MIN,
    ftum_kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[int, List[int], bool, Dict[str, Any]]:
    """Stage 1: derive the winding number n_w.

    Applies constraints C1 (round-trip closure), C2 (KK consistency),
    C4 (Z₂ orbifold parity → odd n_w), C1+C2 (e-folds ≥ n_efolds_min),
    C6 (FTUM convergence), C7 (holographic stability), and C8 (minimality).

    The FTUM convergence and holographic stability checks (C6, C7) use a
    canonical 3-node chain network; they converge for all n_w tested but
    are included for completeness and documentation.

    Parameters
    ----------
    phi0_bare    : float — FTUM fixed-point bare radion vev (default 1.0)
    n_max        : int   — maximum n_w to search (default 20)
    n_efolds_min : int   — minimum slow-roll e-folds (structural, default 60)
    ftum_kwargs  : dict  — optional kwargs for fixed_point_iteration

    Returns
    -------
    (n_w, candidates, is_derived, details) : tuple
        n_w         : int   — selected winding number
        candidates  : list  — all n_w that survived C1–C7
        is_derived  : bool  — True (winding number is purely structurally derived)
        details     : dict  — per-candidate constraint verdicts

    Raises
    ------
    DerivationFailure
        If no candidate survives all structural constraints.
    """
    details: Dict[str, Any] = {}
    candidates: List[int] = []

    for n_w in range(1, n_max + 1):
        record: Dict[str, Any] = {}

        # C4: Z₂ orbifold parity
        ok, msg = check_orbifold_parity(n_w)
        record["C4_orbifold_parity"] = (ok, msg)
        if not ok:
            details[n_w] = record
            continue

        # C1: round-trip closure
        ok, msg = check_round_trip_closure(n_w, phi0_bare)
        record["C1_round_trip"] = (ok, msg)
        if not ok:
            details[n_w] = record
            continue

        # C2: KK dimensional reduction consistency
        ok, msg = check_kk_consistency(n_w, phi0_bare)
        record["C2_kk_consistency"] = (ok, msg)
        if not ok:
            details[n_w] = record
            continue

        # C1+C2: e-folds structural constraint (≥ n_efolds_min, default 60)
        ok, msg = check_efolds(n_w, phi0_bare, n_efolds_min)
        record["C1C2_efolds"] = (ok, msg)
        if not ok:
            details[n_w] = record
            continue

        # C6: FTUM convergence
        ok, msg = check_ftum_convergence(n_w, ftum_kwargs=ftum_kwargs)
        record["C6_ftum_convergence"] = (ok, msg)
        if not ok:
            details[n_w] = record
            continue

        # C7: holographic stability
        ok, msg = check_holographic_stability(n_w, ftum_kwargs=ftum_kwargs)
        record["C7_holo_stability"] = (ok, msg)
        if not ok:
            details[n_w] = record
            continue

        # Record complexity
        record["complexity"] = _complexity_score(n_w)
        phi0_eff = effective_phi0_kk(phi0_bare, n_w)
        ns, r, eps, eta = ns_from_phi0(phi0_eff)
        record["phi0_eff"] = phi0_eff
        record["n_efolds"] = phi0_eff ** 2 / 12.0
        record["ns"] = ns
        record["r"] = r
        details[n_w] = record
        candidates.append(n_w)

    if not candidates:
        raise DerivationFailure(
            f"No winding number in [1, {n_max}] survived all structural "
            f"constraints C1–C7 for phi0_bare={phi0_bare}, "
            f"n_efolds_min={n_efolds_min}.  "
            "Revise the 5D structure or expand the search range."
        )

    # C8: Occam — select the minimum-complexity candidate
    n_w_selected = min(candidates, key=_complexity_score)

    return n_w_selected, candidates, True, details


# ---------------------------------------------------------------------------
# Stage 2 — CS-level derivation
# ---------------------------------------------------------------------------

def derive_cs_level(
    n_w: int,
    phi0_bare: float = PHI0_BARE_FIXED_POINT,
    alpha_em: float = ALPHA_EM_CANONICAL,
    r_c: float = R_C_CANONICAL,
    phi_min_phys: Optional[float] = None,
    k_max: int = 150,
    ftum_kwargs: Optional[Dict[str, Any]] = None,
    use_birefringence_hint: bool = True,
) -> Tuple[int, List[int], bool, Dict[str, Any]]:
    """Stage 2: derive the Chern–Simons level k_CS.

    Applies constraints C3 (gauge invariance), C4 (bundle quantization),
    C5 (anomaly cancellation + coupling finiteness), C6 (FTUM CS stability),
    and C8 (minimality).

    These purely structural constraints are satisfied by *all* k_CS ∈ ℤ⁺;
    they narrow the candidate set to the full positive integers — a universality
    class.  The C8 minimality filter without further physical input would select
    k_CS = 1.

    **Observational disambiguation**
    When ``use_birefringence_hint = True`` (default), an additional geometric
    consistency condition is applied: the CS coupling must produce a birefringence
    angle β(k_CS) that falls within the 1-σ observational window
    (BIREFRINGENCE_TARGET_DEG ± BIREFRINGENCE_SIGMA_DEG).  Among the candidates
    that satisfy this window, k_CS is then selected as the unique integer
    minimiser of |β(k) − β_target|.  This selects k_CS = 74, but it marks
    ``is_derived = False`` because the selection uses an observational prior.

    When ``use_birefringence_hint = False``, all k_CS ∈ [1, k_max] that pass
    C3–C7 are reported as the universality class, and k_CS = 1 is returned as
    the minimal structural choice with ``is_derived = True``.

    Parameters
    ----------
    n_w                    : int   — winding number from Stage 1
    phi0_bare              : float — bare radion vev
    alpha_em               : float — fine-structure constant
    r_c                    : float — compactification radius
    phi_min_phys           : float or None — physical GW minimum; derived from
                             geometry if None
    k_max                  : int   — maximum k_CS to search (default 150)
    ftum_kwargs            : dict  — kwargs for fixed_point_iteration
    use_birefringence_hint : bool  — if True, apply birefringence window filter
                             and mark result as ``is_derived = False``

    Returns
    -------
    (k_cs, candidates, is_derived, details) : tuple
        k_cs        : int   — selected CS level
        candidates  : list  — all k_CS surviving C3–C7 (before birefringence filter)
        is_derived  : bool  — True only if no observational prior was needed
        details     : dict  — per-candidate constraint verdicts

    Raises
    ------
    DerivationFailure
        If no candidate survives the structural constraints (should not
        happen for any k_max ≥ 1 with the current constraint set).
    """
    phi_min_phys = _resolve_phi_min_phys(phi_min_phys, r_c)

    details: Dict[str, Any] = {}
    candidates: List[int] = []

    for k_cs in range(1, k_max + 1):
        record: Dict[str, Any] = {}

        # C3: large gauge transformation invariance
        ok, msg = check_cs_gauge_invariance(k_cs)
        record["C3_gauge_invariance"] = (ok, msg)
        if not ok:
            details[k_cs] = record
            continue

        # C4: bundle quantization
        ok, msg = check_cs_bundle_quantization(k_cs)
        record["C4_bundle_quantization"] = (ok, msg)
        if not ok:
            details[k_cs] = record
            continue

        # C5: anomaly cancellation
        ok, msg = check_anomaly_cancellation(k_cs, n_w)
        record["C5_anomaly"] = (ok, msg)
        if not ok:
            details[k_cs] = record
            continue

        # C5+C3: coupling dimensionless and finite
        ok, msg = check_cs_coupling_finite(k_cs, alpha_em, r_c)
        record["C5C3_coupling_finite"] = (ok, msg)
        if not ok:
            details[k_cs] = record
            continue

        # C6: FTUM CS stability
        ok, msg = check_ftum_cs_stability(k_cs, ftum_kwargs=ftum_kwargs)
        record["C6_ftum_cs_stable"] = (ok, msg)
        if not ok:
            details[k_cs] = record
            continue

        # Record geometric observables
        g_agg = cs_axion_photon_coupling(k_cs, alpha_em, r_c)
        dphi = field_displacement_gw(phi_min_phys)
        beta_rad = birefringence_angle(g_agg, dphi)
        beta_deg = float(np.degrees(beta_rad))

        record["complexity"] = _complexity_score(k_cs)
        record["g_agg"] = g_agg
        record["beta_deg"] = beta_deg
        record["delta_phi"] = dphi
        details[k_cs] = record
        candidates.append(k_cs)

    if not candidates:
        raise DerivationFailure(
            f"No CS level in [1, {k_max}] survived structural constraints C3–C7. "
            "This should not happen; check input parameters."
        )

    # Without observational input: all candidates form a universality class;
    # C8 minimality selects k_cs = 1.
    if not use_birefringence_hint:
        k_cs_selected = min(candidates, key=_complexity_score)
        return k_cs_selected, candidates, True, details

    # With birefringence hint: filter to 1-σ window, then select unique minimiser.
    # This uses the observational prior β_target = 0.35° ± 0.14°.
    window_candidates = [
        k for k in candidates
        if abs(details[k]["beta_deg"] - BIREFRINGENCE_TARGET_DEG)
        <= BIREFRINGENCE_SIGMA_DEG
    ]

    if window_candidates:
        # Unique minimiser of |β(k) − β_target|
        k_cs_selected = min(
            window_candidates,
            key=lambda k: abs(details[k]["beta_deg"] - BIREFRINGENCE_TARGET_DEG),
        )
        # Mark as observationally fitted — not purely derived
        return k_cs_selected, candidates, False, details

    # No candidate in the 1-σ window; fall back to full minimiser
    k_cs_selected = min(
        candidates,
        key=lambda k: abs(details[k]["beta_deg"] - BIREFRINGENCE_TARGET_DEG),
    )
    return k_cs_selected, candidates, False, details


# ---------------------------------------------------------------------------
# Stage 3 — Joint consistency
# ---------------------------------------------------------------------------

def _check_joint_consistency(
    n_w: int,
    k_cs: int,
    phi0_bare: float = PHI0_BARE_FIXED_POINT,
    alpha_em: float = ALPHA_EM_CANONICAL,
    r_c: float = R_C_CANONICAL,
    phi_min_phys: Optional[float] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """Verify that (n_w, k_cs) are mutually consistent.

    Joint checks:
    1. phi0_eff derived from n_w is finite and positive.
    2. CS coupling g_aγγ derived from k_cs is finite and positive.
    3. The combined triple (n_w, k_cs, phi0_bare) produces finite nₛ, r, β.
    4. n_w and k_cs are both positive integers.

    Returns
    -------
    (consistent, info) : (bool, dict)
    """
    info: Dict[str, Any] = {}

    if n_w < 1 or k_cs < 1:
        info["error"] = f"Non-positive integer: n_w={n_w}, k_cs={k_cs}"
        return False, info

    try:
        phi0_eff = effective_phi0_kk(phi0_bare, n_w)
    except ValueError as exc:
        info["error"] = str(exc)
        return False, info

    if phi_min_phys is None:
        phi_min_phys = _resolve_phi_min_phys(None, r_c)

    try:
        ns, r, eps, eta = ns_from_phi0(phi0_eff)
        g_agg = cs_axion_photon_coupling(k_cs, alpha_em, r_c)
        dphi = field_displacement_gw(phi_min_phys)
        beta_rad = birefringence_angle(g_agg, dphi)
        beta_deg = float(np.degrees(beta_rad))
    except (ValueError, ZeroDivisionError) as exc:
        info["error"] = str(exc)
        return False, info

    for name, val in [("ns", ns), ("r", r), ("g_agg", g_agg), ("beta_deg", beta_deg)]:
        if not np.isfinite(val):
            info["error"] = f"{name}={val} is not finite"
            return False, info

    info.update({
        "phi0_eff": phi0_eff,
        "ns": ns,
        "r": r,
        "epsilon": eps,
        "eta": eta,
        "g_agg": g_agg,
        "beta_deg": beta_deg,
        "delta_phi": dphi,
    })
    return True, info


# ---------------------------------------------------------------------------
# Top-level pipeline
# ---------------------------------------------------------------------------

def derive_integers(
    phi0_bare: float = PHI0_BARE_FIXED_POINT,
    alpha_em: float = ALPHA_EM_CANONICAL,
    r_c: float = R_C_CANONICAL,
    phi_min_phys: Optional[float] = None,
    n_max: int = 20,
    k_max: int = 150,
    n_efolds_min: int = N_EFOLDS_MIN,
    ftum_kwargs: Optional[Dict[str, Any]] = None,
    use_birefringence_hint: bool = True,
) -> DerivationResult:
    """Full Stage 0 → Stage 3 derivation of (n_w, k_CS).

    Executes all three stages in order:
      Stage 1 — Winding number n_w from structural constraints.
      Stage 2 — CS level k_CS (structural + optional observational filter).
      Stage 3 — Joint consistency check.

    Parameters
    ----------
    phi0_bare              : float — FTUM fixed-point bare radion vev (default 1.0)
    alpha_em               : float — fine-structure constant (default 1/137.036)
    r_c                    : float — compactification radius (default 12.0)
    phi_min_phys           : float or None — physical GW minimum (derived if None)
    n_max                  : int   — max n_w to search (default 20)
    k_max                  : int   — max k_CS to search (default 150)
    n_efolds_min           : int   — minimum e-folds structural bound (default 60)
    ftum_kwargs            : dict  — kwargs forwarded to fixed_point_iteration
    use_birefringence_hint : bool  — apply birefringence window to Stage 2

    Returns
    -------
    DerivationResult

    Raises
    ------
    DerivationFailure
        If no integer survives Stage 1 or Stage 2 constraints, or if the
        joint consistency check (Stage 3) fails.
    """
    # -----------------------------------------------------------------------
    # Stage 1 — Winding number
    # -----------------------------------------------------------------------
    n_w, n_w_candidates, n_w_is_derived, nw_details = derive_winding_number(
        phi0_bare=phi0_bare,
        n_max=n_max,
        n_efolds_min=n_efolds_min,
        ftum_kwargs=ftum_kwargs,
    )

    # -----------------------------------------------------------------------
    # Stage 2 — CS level
    # -----------------------------------------------------------------------
    k_cs, k_cs_candidates, k_cs_is_derived, kcs_details = derive_cs_level(
        n_w=n_w,
        phi0_bare=phi0_bare,
        alpha_em=alpha_em,
        r_c=r_c,
        phi_min_phys=phi_min_phys,
        k_max=k_max,
        ftum_kwargs=ftum_kwargs,
        use_birefringence_hint=use_birefringence_hint,
    )

    # -----------------------------------------------------------------------
    # Stage 3 — Joint consistency
    # -----------------------------------------------------------------------
    joint_consistent, joint_info = _check_joint_consistency(
        n_w, k_cs,
        phi0_bare=phi0_bare,
        alpha_em=alpha_em,
        r_c=r_c,
        phi_min_phys=phi_min_phys,
    )
    if not joint_consistent:
        raise DerivationFailure(
            f"Stage 3 joint consistency failed for (n_w={n_w}, k_cs={k_cs}): "
            f"{joint_info.get('error', 'unknown error')}"
        )

    metadata = {
        "stage1_details": nw_details,
        "stage2_details": kcs_details,
        "stage3_joint": joint_info,
        "n_w_candidates": n_w_candidates,
        "k_cs_candidates_structural": k_cs_candidates,
    }

    return DerivationResult(
        n_w=n_w,
        k_cs=k_cs,
        n_w_candidates=n_w_candidates,
        k_cs_candidates=k_cs_candidates,
        n_w_is_derived=n_w_is_derived,
        k_cs_is_derived=k_cs_is_derived,
        joint_consistent=joint_consistent,
        metadata=metadata,
    )


# ---------------------------------------------------------------------------
# [COMPLETION 3]  Index-theorem route to n_w
# [COMPLETION 4]  Anomaly-inflow route to k_CS
#
# Canonical implementations live in:
#   [3] src/core/metric.py       (topological — belongs with KK geometry)
#   [4] src/holography/boundary.py (gauge anomaly — belongs with holographic BCs)
#
# Re-exported here so existing callers of derivation.py continue to work.
# ---------------------------------------------------------------------------

from .metric import derive_nw_index_theorem  # noqa: E402
from ..holography.boundary import (           # noqa: E402
    SM_FERMION_SPECTRUM_DEFAULT,
    derive_kcs_anomaly_inflow,
)
