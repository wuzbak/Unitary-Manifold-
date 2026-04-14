# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
recycling/polymers.py
=====================
Plastics and polymers as φ-chain topology — Pillar 16a.

In the Unitary Manifold a polymer chain is not merely a sequence of covalent
bonds; it is a topological object whose winding number N_w encodes its
configuration entropy, recyclability, and degradation pathway.

The entanglement-capacity scalar φ develops a series of shallow minima along
the backbone — one per repeat unit.  The total depth of those minima is the
formation energy; the height of the barrier from the product well back to
the monomer well is the depolymerization barrier.  Recycling is the process
of surmounting that barrier and restoring the monomer φ-well.

What humans get wrong
---------------------
1. Linear thinking — recycling is treated as a simple material loop, but
   each mechanical or thermal cycle lowers φ (the winding-number topology
   degrades) so the recovered material is always of lower quality unless
   chemical recycling restores the monomers.
2. Contamination blindness — even a small B_μ noise field from mixed-stream
   contamination can broaden the φ-minima of each polymer type until they
   overlap, making sorting impossible.
3. Microplastic underestimation — the information-current gradient at polymer
   surfaces drives continuous fragmentation; suppressing this flux requires
   raising the local φ, not just mechanical shredding.

Theory summary
--------------
Polymer φ-well (Gaussian-well per bond):
    φ(r) = φ_∞ - (φ_∞ - φ_min) · exp(−a²(r − r₀)²)

Recyclability index:
    RI = φ_recovery / φ_formation   ∈ [0, 1]

Depolymerization barrier (B_μ activation):
    E_depoly = λ² φ_mean² H_max² / 2

Sorting discriminability (normalised φ-contrast):
    Δ = |φ_a − φ_b| / (φ_a + φ_b)    ∈ [0, 1]

Contamination tolerance:
    contaminated = |B_field| ≥ B_threshold

Thermal degradation rate (Arrhenius + φ suppression):
    k_deg(T) = A · exp(−E_a / (φ_chain · k_B · T))

Cycle quality loss (φ decay per recycle):
    φ_n = φ_0 · exp(−α · n)

Microplastic flux (information-current fragmentation):
    J_micro = D · φ · ∇φ

Polymer winding number (Kuhn-segment topology):
    N_w = round(backbone_length / kuhn_length)

Chain entanglement density:
    ρ_ent = n_chains · φ_mean / volume

Public API
----------
polymer_bond_phi(r, r0, phi_inf, phi_min, a)
    Gaussian-well φ profile across a single backbone bond.

recyclability_index(phi_recovery, phi_formation)
    RI = phi_recovery / phi_formation.

depolymerization_barrier(H_max, phi_mean, lam)
    E_depoly = λ² φ² H_max² / 2.

sorting_discriminability(phi_a, phi_b)
    Normalised φ-contrast |φ_a − φ_b| / (φ_a + φ_b).

is_contaminated(B_field, B_threshold)
    True where |B_field| ≥ B_threshold.

degradation_rate(T, phi_chain, A, E_a, k_B)
    Arrhenius rate suppressed by φ_chain.

cycle_quality_loss(phi_0, n_cycles, alpha)
    φ_n = φ_0 · exp(−α · n).

microplastic_flux(phi, D, dx)
    J_micro = D · φ · ∇φ  (information-current fragmentation flux).

polymer_winding_number(backbone_length, kuhn_length)
    N_w = round(backbone_length / kuhn_length).

chain_entanglement_density(n_chains, phi_mean, volume)
    ρ_ent = n_chains · φ_mean / volume.

phi_from_recyclate_density(rho_kg_m3, rho_ref, phi_ref)
    Scale φ linearly with material density relative to a reference.

sorting_purity(phi_stream, phi_target, sigma_noise)
    Gaussian-model purity of a sorted stream.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_LAM_DEFAULT: float = 1.0
_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Polymer φ-bond well
# ---------------------------------------------------------------------------

def polymer_bond_phi(
    r: np.ndarray,
    r0: float,
    phi_inf: float,
    phi_min: float,
    a: float,
) -> np.ndarray:
    """Gaussian-well φ profile across a single polymer backbone bond.

    Each covalent bond in the polymer backbone localises the entanglement-
    capacity scalar into a Gaussian well centred on the equilibrium bond
    length r₀:

        φ(r) = φ_∞ − (φ_∞ − φ_min) · exp(−a²(r − r₀)²)

    Parameters
    ----------
    r       : ndarray, shape (N,) — radial grid
    r0      : float — equilibrium bond length
    phi_inf : float — asymptotic φ as r → ∞
    phi_min : float — minimum φ at the bond centre (must be ≤ phi_inf)
    a       : float — inverse well-width parameter (a > 0)

    Returns
    -------
    phi : ndarray, shape (N,) — φ profile
    """
    r_arr = np.asarray(r, dtype=float)
    depth = phi_inf - phi_min
    return phi_inf - depth * np.exp(-(a ** 2) * (r_arr - r0) ** 2)


# ---------------------------------------------------------------------------
# Recyclability index
# ---------------------------------------------------------------------------

def recyclability_index(
    phi_recovery: float,
    phi_formation: float,
) -> float:
    """Recyclability index: fraction of the formation φ restored by recycling.

    A perfect closed-loop process would restore φ_recovery = φ_formation,
    giving RI = 1.0.  Downcycling yields RI < 1.  Landfilling = RI → 0.

        RI = φ_recovery / φ_formation

    Parameters
    ----------
    phi_recovery  : float — φ of the recovered/recycled material (≥ 0)
    phi_formation : float — φ of the virgin/formed material (> 0)

    Returns
    -------
    RI : float — recyclability index clamped to [0, 1]

    Raises
    ------
    ValueError
        If phi_formation ≤ 0.
    """
    if phi_formation <= 0.0:
        raise ValueError(f"phi_formation must be > 0, got {phi_formation!r}")
    return float(np.clip(phi_recovery / phi_formation, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Depolymerization barrier
# ---------------------------------------------------------------------------

def depolymerization_barrier(
    H_max: float,
    phi_mean: float,
    lam: float = _LAM_DEFAULT,
) -> float:
    """Activation energy for depolymerizing a polymer back to monomers.

    The B_μ field-strength tensor peak H_max sets the height of the barrier
    that must be surmounted to break every repeat-unit bond and recover the
    monomer φ-well:

        E_depoly = λ² φ_mean² H_max² / 2

    Higher H_max (steeper φ gradient along the chain) means a larger barrier —
    the polymer is harder to depolymerize, as observed for cross-linked
    thermosets vs. linear thermoplastics.

    Parameters
    ----------
    H_max    : float — peak B_μ field-strength magnitude (≥ 0)
    phi_mean : float — mean radion ⟨φ⟩ along the chain (> 0)
    lam      : float — KK coupling λ (default 1)

    Returns
    -------
    E_depoly : float — depolymerization barrier in Planck units (≥ 0)

    Raises
    ------
    ValueError
        If phi_mean ≤ 0 or lam ≤ 0.
    """
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    if lam <= 0.0:
        raise ValueError(f"lam must be > 0, got {lam!r}")
    return float(0.5 * lam ** 2 * phi_mean ** 2 * H_max ** 2)


# ---------------------------------------------------------------------------
# Sorting discriminability
# ---------------------------------------------------------------------------

def sorting_discriminability(
    phi_a: float,
    phi_b: float,
) -> float:
    """Normalised φ-contrast between two polymer types.

    Sorting by polymer type is only physically possible when the two φ-field
    signatures are sufficiently distinct.  The discriminability Δ measures
    this contrast:

        Δ = |φ_a − φ_b| / (φ_a + φ_b)    ∈ [0, 1)

    Δ → 0 means the two polymers are indistinguishable to the sorting
    process; Δ → 1 means they are maximally discriminable.  In practice
    Δ < 0.05 makes automated near-IR sorting unreliable.

    Parameters
    ----------
    phi_a : float — φ of polymer type A (> 0)
    phi_b : float — φ of polymer type B (> 0)

    Returns
    -------
    delta : float — discriminability ∈ [0, 1)

    Raises
    ------
    ValueError
        If phi_a ≤ 0 or phi_b ≤ 0.
    """
    if phi_a <= 0.0:
        raise ValueError(f"phi_a must be > 0, got {phi_a!r}")
    if phi_b <= 0.0:
        raise ValueError(f"phi_b must be > 0, got {phi_b!r}")
    return float(abs(phi_a - phi_b) / (phi_a + phi_b))


# ---------------------------------------------------------------------------
# Contamination check
# ---------------------------------------------------------------------------

def is_contaminated(
    B_field: np.ndarray,
    B_threshold: float,
) -> np.ndarray:
    """Identify contaminated sites where B_μ noise exceeds the sorting threshold.

    A mixed-stream recycling batch contains multiple polymer types whose
    φ-minima are distinct when pure, but B_μ noise from contamination
    broadens those minima.  When the local field strength exceeds B_threshold
    the φ-signature is effectively washed out:

        contaminated ↔ |B_field(x)| ≥ B_threshold

    Parameters
    ----------
    B_field     : array-like — local B_μ field strength at each point
    B_threshold : float — contamination threshold (> 0)

    Returns
    -------
    mask : ndarray of bool — True where contamination is present

    Raises
    ------
    ValueError
        If B_threshold ≤ 0.
    """
    if B_threshold <= 0.0:
        raise ValueError(f"B_threshold must be > 0, got {B_threshold!r}")
    return np.abs(np.asarray(B_field, dtype=float)) >= B_threshold


# ---------------------------------------------------------------------------
# Thermal degradation rate
# ---------------------------------------------------------------------------

def degradation_rate(
    T: float,
    phi_chain: float,
    A: float = 1.0,
    E_a: float = 1.0,
    k_B: float = 1.0,
) -> float:
    """Thermal degradation rate of a polymer, suppressed by chain φ.

    The local φ field along the polymer backbone suppresses the thermal
    degradation rate by effectively raising the barrier per unit of thermal
    energy:

        k_deg(T) = A · exp(−φ_chain · E_a / (k_B · T))

    Higher φ_chain (more entangled, more topologically complex chain) raises
    the effective barrier φ·E_a, leading to a slower degradation rate —
    the manifold predicts that high-molecular-weight, entangled polymers
    degrade more slowly, consistent with observation.

    Parameters
    ----------
    T         : float — temperature (must be > 0)
    phi_chain : float — mean φ along the polymer chain (must be > 0)
    A         : float — pre-exponential frequency factor (default 1)
    E_a       : float — bare activation energy (default 1)
    k_B       : float — Boltzmann constant (default 1, Planck units)

    Returns
    -------
    k_deg : float — degradation rate (≥ 0)

    Raises
    ------
    ValueError
        If T ≤ 0 or phi_chain ≤ 0.
    """
    if T <= 0.0:
        raise ValueError(f"T must be > 0, got {T!r}")
    if phi_chain <= 0.0:
        raise ValueError(f"phi_chain must be > 0, got {phi_chain!r}")
    return float(A * np.exp(-phi_chain * E_a / (k_B * T)))


# ---------------------------------------------------------------------------
# Cycle quality loss
# ---------------------------------------------------------------------------

def cycle_quality_loss(
    phi_0: float,
    n_cycles: int,
    alpha: float,
) -> float:
    """φ of the polymer after n mechanical/thermal recycling cycles.

    Every recycling pass applies mechanical shear or thermal stress that
    reduces chain length, breaks cross-links, and partially collapses the
    winding-number topology.  The result is an exponential decay of φ:

        φ_n = φ_0 · exp(−α · n)

    α is the per-cycle degradation coefficient — higher for aggressive
    processes (extrusion at high temperature) and lower for mild solvolysis.
    This is the manifold explanation for why mechanically recycled plastic
    downcycles: the winding number N_w decreases irreversibly with each pass.

    Parameters
    ----------
    phi_0    : float — initial φ of virgin/pristine polymer (> 0)
    n_cycles : int   — number of recycling cycles (≥ 0)
    alpha    : float — per-cycle φ decay coefficient (> 0)

    Returns
    -------
    phi_n : float — φ after n cycles (> 0)

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
    return float(phi_0 * np.exp(-alpha * n_cycles))


# ---------------------------------------------------------------------------
# Microplastic flux
# ---------------------------------------------------------------------------

def microplastic_flux(
    phi: np.ndarray,
    D: float = 1.0,
    dx: float = 1.0,
) -> np.ndarray:
    """Information-current fragmentation flux that generates microplastics.

    At polymer surfaces the φ field has a steep gradient.  The information
    current drives material from high-φ (intact polymer) to low-φ
    (fragmented particle) regions:

        J_micro = D · φ · ∇φ

    Regions of large |J_micro| correspond to surfaces where microplastic
    generation is highest.  Suppressing this flux requires elevating the
    local φ (e.g., via surface coatings that increase entanglement) or
    removing the gradient (uniform φ throughout the bulk).

    Parameters
    ----------
    phi : ndarray, shape (N,) — φ field across the polymer body
    D   : float — diffusion-transport coefficient (default 1)
    dx  : float — grid spacing (default 1)

    Returns
    -------
    J_micro : ndarray, shape (N,) — fragmentation flux at each grid point
    """
    phi_arr = np.asarray(phi, dtype=float)
    grad_phi = np.gradient(phi_arr, dx, edge_order=2)
    return D * phi_arr * grad_phi


# ---------------------------------------------------------------------------
# Polymer winding number
# ---------------------------------------------------------------------------

def polymer_winding_number(
    backbone_length: float,
    kuhn_length: float,
) -> int:
    """Topological winding number of a polymer chain.

    In the 5D geometry, a linear polymer of contour length L_backbone
    wound on the compactified S¹ with Kuhn segment length b has winding
    number:

        N_w = round(L_backbone / b)

    This is the number of times the chain "wraps" the compact dimension.
    Higher N_w → higher topological entanglement → higher φ_mean → harder
    to depolymerize (larger E_depoly) and slower degradation.

    Parameters
    ----------
    backbone_length : float — contour length of the polymer backbone (> 0)
    kuhn_length     : float — Kuhn statistical segment length (> 0)

    Returns
    -------
    N_w : int — topological winding number (≥ 1)

    Raises
    ------
    ValueError
        If backbone_length ≤ 0 or kuhn_length ≤ 0.
    """
    if backbone_length <= 0.0:
        raise ValueError(f"backbone_length must be > 0, got {backbone_length!r}")
    if kuhn_length <= 0.0:
        raise ValueError(f"kuhn_length must be > 0, got {kuhn_length!r}")
    return max(1, round(backbone_length / kuhn_length))


# ---------------------------------------------------------------------------
# Chain entanglement density
# ---------------------------------------------------------------------------

def chain_entanglement_density(
    n_chains: float,
    phi_mean: float,
    volume: float,
) -> float:
    """Volumetric φ-entanglement density of a polymer melt or solid.

    The collective φ-density from all entangled chains in a volume element:

        ρ_ent = n_chains · φ_mean / volume

    Higher ρ_ent correlates with better mechanical properties and — crucially —
    with a higher depolymerization barrier.  Materials with low ρ_ent
    (degraded, low-MW recyclate) are easier to depolymerize via pyrolysis
    but also easier to fragment into microplastics.

    Parameters
    ----------
    n_chains  : float — number of polymer chains in the volume (> 0)
    phi_mean  : float — mean φ per chain (> 0)
    volume    : float — volume of the sample (> 0)

    Returns
    -------
    rho_ent : float — entanglement density (Planck units⁻³)

    Raises
    ------
    ValueError
        If n_chains ≤ 0, phi_mean ≤ 0, or volume ≤ 0.
    """
    if n_chains <= 0.0:
        raise ValueError(f"n_chains must be > 0, got {n_chains!r}")
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    if volume <= 0.0:
        raise ValueError(f"volume must be > 0, got {volume!r}")
    return float(n_chains * phi_mean / volume)


# ---------------------------------------------------------------------------
# φ from recyclate density
# ---------------------------------------------------------------------------

def phi_from_recyclate_density(
    rho_kg_m3: float,
    rho_ref: float = 1000.0,
    phi_ref: float = 1.0,
) -> float:
    """Estimate the φ signature of a recyclate from its bulk density.

    More compact, higher-density materials have more atoms per unit volume,
    hence more KK winding modes and higher φ.  A linear scaling with
    respect to a reference material (default: water, ρ_ref = 1000 kg/m³,
    φ_ref = 1.0) gives a practical first estimate:

        φ = φ_ref · (ρ / ρ_ref)

    Parameters
    ----------
    rho_kg_m3 : float — bulk density of the recyclate (kg/m³, > 0)
    rho_ref   : float — reference density (default 1000 kg/m³)
    phi_ref   : float — reference φ (default 1.0)

    Returns
    -------
    phi : float — estimated φ (> 0)

    Raises
    ------
    ValueError
        If rho_kg_m3 ≤ 0, rho_ref ≤ 0, or phi_ref ≤ 0.
    """
    if rho_kg_m3 <= 0.0:
        raise ValueError(f"rho_kg_m3 must be > 0, got {rho_kg_m3!r}")
    if rho_ref <= 0.0:
        raise ValueError(f"rho_ref must be > 0, got {rho_ref!r}")
    if phi_ref <= 0.0:
        raise ValueError(f"phi_ref must be > 0, got {phi_ref!r}")
    return float(phi_ref * rho_kg_m3 / rho_ref)


# ---------------------------------------------------------------------------
# Sorting purity
# ---------------------------------------------------------------------------

def sorting_purity(
    phi_stream: float,
    phi_target: float,
    sigma_noise: float,
) -> float:
    """Gaussian-model purity of a sorted polymer stream.

    The sorting process selects material whose φ falls within one σ_noise
    of the target φ.  Modelling the φ distribution in the stream as a
    Gaussian, the fraction of correctly sorted material is:

        purity = exp(−(φ_stream − φ_target)² / (2 σ_noise²))

    purity = 1.0 when φ_stream = φ_target (perfect sort);
    purity → 0 when the stream is far off-target.

    Parameters
    ----------
    phi_stream  : float — mean φ of the incoming stream (> 0)
    phi_target  : float — target φ of the desired polymer (> 0)
    sigma_noise : float — φ-noise width of the sorting sensor (> 0)

    Returns
    -------
    purity : float — sorting purity ∈ (0, 1]

    Raises
    ------
    ValueError
        If sigma_noise ≤ 0.
    """
    if sigma_noise <= 0.0:
        raise ValueError(f"sigma_noise must be > 0, got {sigma_noise!r}")
    return float(np.exp(-((phi_stream - phi_target) ** 2) / (2.0 * sigma_noise ** 2)))
