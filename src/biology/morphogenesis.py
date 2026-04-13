# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/biology/morphogenesis.py
==============================
Morphogenesis as Spontaneous Symmetry Breaking in the φ Field — Pillar: Biology.

Turing patterns = spontaneous symmetry breaking in φ
-----------------------------------------------------
Embryonic development begins from a near-uniform φ field.  The FTUM
amplifies small φ fluctuations through a Turing instability: the activator
(u) and inhibitor (v) correspond to two coupled φ modes.  When the
inhibitor diffuses much faster than the activator, the uniform state
becomes linearly unstable and spatial patterns (stripes, spots) form
spontaneously — the embryo differentiates.

Turing instability condition
-----------------------------
For the classic activator–inhibitor system the uniform state is destabilised
if and only if:

    D_v / D_u > (1 + sqrt(b/a))²,   a > 0,  b > 0

where D_u is the activator diffusivity, D_v the inhibitor diffusivity,
a the activator self-activation rate, and b the inhibitor cross-activation
rate.  The FTUM amplifies the most unstable wavenumber k_max.

Morphogen gradient
------------------
A source cell secretes a morphogen (φ) that diffuses and degrades,
establishing an exponential positional gradient:

    φ(x) = φ₀ exp(−x / λ_m),   λ_m = sqrt(D / k_deg)

where D is the morphogen diffusivity and k_deg is the degradation rate.
Cells read their position by reading their local φ value.

Segment formation from winding numbers
---------------------------------------
The compact 5th dimension carries topological winding numbers n_w.
Each full winding maps to two body segments (one anterior, one posterior):

    n_seg = 2 n_w

This topological constraint predicts the even-numbered Hox gene cluster
patterning observed in bilaterian metazoans.

Positional information
----------------------
Shannon (1948) positional information quantifies how precisely a cell can
determine its position from its morphogen concentration:

    H_pos = −∑ p_i log₂ p_i

where p_i is the probability of cell type i at a given position.  We
discretise φ_field into n_types bins and compute H_pos.

Gray-Scott reaction-diffusion
------------------------------
The canonical numerical model of Turing morphogenesis.  One Euler step:

    du/dt = D_u ∇²u − uv² + f(1 − u)
    dv/dt = D_v ∇²v + uv² − (f + k) v

∇² is computed via finite differences with periodic (np.roll) boundaries.

Public API
----------
turing_instability_condition(D_u, D_v, a, b)
    True iff the Turing condition D_v/D_u > (1 + sqrt(b/a))² is satisfied.

morphogen_gradient(x, phi0, lam_m)
    Exponential morphogen profile φ(x) = phi0 exp(−x / lam_m).

morphogen_length_scale(D, k_deg)
    λ_m = sqrt(D / k_deg).

turing_wavelength(D_u, D_v, a, b)
    Characteristic Turing pattern wavelength λ_T = 2π / k_max.

segment_count(n_w)
    n_seg = 2 n_w (topological winding → body-segment count).

positional_information(phi_field, n_types)
    Shannon entropy of discretised cell-type distribution.

reaction_diffusion_step(u, v, Du, Dv, f, k, dt, dx)
    One Euler step of the Gray-Scott reaction-diffusion system.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_ENTROPY_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Turing instability
# ---------------------------------------------------------------------------

def turing_instability_condition(
    D_u: float,
    D_v: float,
    a: float,
    b: float,
) -> bool:
    """Test the Turing diffusion-driven instability condition.

    For an activator–inhibitor system, the homogeneous steady state is
    linearly unstable if the inhibitor diffuses sufficiently faster than
    the activator:

        D_v / D_u > (1 + sqrt(b/a))²

    This is a necessary and sufficient condition for spontaneous pattern
    formation (Turing, 1952).

    Parameters
    ----------
    D_u : float — activator diffusivity (must be > 0)
    D_v : float — inhibitor diffusivity (must be > 0)
    a   : float — activator self-activation rate (must be > 0)
    b   : float — inhibitor cross-activation rate (must be > 0)

    Returns
    -------
    bool — True iff the Turing condition is satisfied

    Raises
    ------
    ValueError
        If D_u ≤ 0 or D_v ≤ 0.
    """
    if D_u <= 0.0:
        raise ValueError(f"D_u must be > 0, got {D_u!r}")
    if D_v <= 0.0:
        raise ValueError(f"D_v must be > 0, got {D_v!r}")
    if a <= 0.0 or b <= 0.0:
        return False
    threshold = (1.0 + np.sqrt(b / a)) ** 2
    return bool((D_v / D_u) > threshold)


def morphogen_gradient(
    x: np.ndarray,
    phi0: float,
    lam_m: float,
) -> np.ndarray:
    """Exponential morphogen gradient from a localised source.

    A morphogen diffuses from a point source at x = 0 and degrades at
    rate k_deg.  At steady state the profile is exponential:

        φ(x) = phi0 · exp(−x / lam_m)

    Cells read their position from the local φ value.

    Parameters
    ----------
    x     : ndarray — spatial coordinate array (arbitrary shape)
    phi0  : float   — morphogen concentration at the source (must be > 0)
    lam_m : float   — morphogen decay length λ_m = sqrt(D / k_deg) (must be > 0)

    Returns
    -------
    phi : ndarray, same shape as x — morphogen concentration

    Raises
    ------
    ValueError
        If phi0 ≤ 0 or lam_m ≤ 0.
    """
    if phi0 <= 0.0:
        raise ValueError(f"phi0 must be > 0, got {phi0!r}")
    if lam_m <= 0.0:
        raise ValueError(f"lam_m must be > 0, got {lam_m!r}")
    x_arr = np.asarray(x, dtype=float)
    return phi0 * np.exp(-x_arr / lam_m)


def morphogen_length_scale(D: float, k_deg: float) -> float:
    """Morphogen length scale from diffusivity and degradation rate.

    The characteristic spatial range over which a morphogen persists is
    set by the competition between diffusion (D) and degradation (k_deg):

        λ_m = sqrt(D / k_deg)

    Parameters
    ----------
    D     : float — morphogen diffusivity (must be > 0)
    k_deg : float — first-order degradation rate (must be > 0)

    Returns
    -------
    lam_m : float — morphogen length scale λ_m (> 0)

    Raises
    ------
    ValueError
        If D ≤ 0 or k_deg ≤ 0.
    """
    if D <= 0.0:
        raise ValueError(f"D must be > 0, got {D!r}")
    if k_deg <= 0.0:
        raise ValueError(f"k_deg must be > 0, got {k_deg!r}")
    return float(np.sqrt(D / k_deg))


def turing_wavelength(
    D_u: float,
    D_v: float,
    a: float,
    b: float,
) -> float:
    """Characteristic Turing pattern wavelength.

    In the unstable regime the most amplified wavenumber is:

        k²_max = sqrt(a b / (D_u D_v))

    which gives the Turing wavelength:

        λ_T = 2π / k_max

    Returns ``np.inf`` if the system is not in the Turing-unstable regime
    (i.e., if the Turing instability condition is not satisfied).

    Parameters
    ----------
    D_u : float — activator diffusivity (must be > 0)
    D_v : float — inhibitor diffusivity (must be > 0)
    a   : float — activator self-activation rate
    b   : float — inhibitor cross-activation rate

    Returns
    -------
    lam_T : float — Turing wavelength (> 0) or np.inf
    """
    if not turing_instability_condition(D_u, D_v, a, b):
        return float(np.inf)
    # k²_max = sqrt(ab / (D_u D_v)) is the geometric-mean wavenumber of the
    # most-amplified Turing mode (always positive in the unstable regime).
    k_sq = float(np.sqrt(a * b / (D_u * D_v)))
    if k_sq <= 0.0:
        return float(np.inf)
    return float(2.0 * np.pi / np.sqrt(k_sq))


def segment_count(n_w: int) -> int:
    """Body-segment count from topological winding number.

    Each full winding of the compact 5th dimension maps to two body
    segments (anterior + posterior pair), reproducing the bilaterian
    Hox cluster constraint:

        n_seg = 2 n_w

    Parameters
    ----------
    n_w : int — winding number (must be ≥ 1)

    Returns
    -------
    n_seg : int — number of body segments

    Raises
    ------
    ValueError
        If n_w < 1.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    return 2 * int(n_w)


def positional_information(
    phi_field: np.ndarray,
    n_types: int = 4,
) -> float:
    """Shannon positional information from the cell-type distribution.

    Bins phi_field into n_types equal-width bins and computes the
    Shannon entropy:

        H_pos = −∑ p_i log₂ p_i

    where p_i is the fraction of cells assigned to each bin.  Maximum
    positional information (all types equally likely) is log₂(n_types).

    Parameters
    ----------
    phi_field : ndarray — φ values of individual cells
    n_types   : int     — number of discrete cell types / bins (default 4)

    Returns
    -------
    H_pos : float — Shannon entropy in bits (≥ 0)
    """
    phi_arr = np.asarray(phi_field, dtype=float)
    counts, _ = np.histogram(phi_arr, bins=n_types)
    total = counts.sum() + _ENTROPY_EPSILON
    p = counts / total
    p = np.clip(p, _ENTROPY_EPSILON, None)
    return float(-np.sum(p * np.log2(p)))


def reaction_diffusion_step(
    u: np.ndarray,
    v: np.ndarray,
    Du: float,
    Dv: float,
    f: float,
    k: float,
    dt: float = 0.01,
    dx: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """One Euler step of the Gray-Scott reaction-diffusion system.

    Updates the activator (u) and inhibitor (v) fields by one explicit
    Euler time step using the Gray-Scott kinetics:

        du/dt = D_u ∇²u − u v² + f (1 − u)
        dv/dt = D_v ∇²v + u v² − (f + k) v

    The Laplacian ∇² is computed via second-order finite differences with
    periodic boundary conditions (using ``np.roll``):

        ∇²u_i ≈ (u_{i+1} − 2u_i + u_{i−1}) / dx²

    Parameters
    ----------
    u  : ndarray, shape (N,) — activator field
    v  : ndarray, shape (N,) — inhibitor field
    Du : float — activator diffusivity (must be > 0)
    Dv : float — inhibitor diffusivity (must be > 0)
    f  : float — feed rate
    k  : float — kill rate
    dt : float — time step (must be > 0, default 0.01)
    dx : float — spatial grid spacing (default 1.0)

    Returns
    -------
    (u_new, v_new) : tuple of ndarray, same shape as (u, v)

    Raises
    ------
    ValueError
        If Du ≤ 0, Dv ≤ 0, or dt ≤ 0.
    """
    if Du <= 0.0:
        raise ValueError(f"Du must be > 0, got {Du!r}")
    if Dv <= 0.0:
        raise ValueError(f"Dv must be > 0, got {Dv!r}")
    if dt <= 0.0:
        raise ValueError(f"dt must be > 0, got {dt!r}")
    u_arr = np.asarray(u, dtype=float)
    v_arr = np.asarray(v, dtype=float)

    def laplacian(field: np.ndarray) -> np.ndarray:
        return (np.roll(field, 1) - 2.0 * field + np.roll(field, -1)) / dx**2

    uvv = u_arr * v_arr**2
    u_new = u_arr + dt * (Du * laplacian(u_arr) - uvv + f * (1.0 - u_arr))
    v_new = v_arr + dt * (Dv * laplacian(v_arr) + uvv - (f + k) * v_arr)
    return u_new, v_new
