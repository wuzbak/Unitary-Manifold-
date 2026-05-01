# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/cold_fusion/lattice.py
==========================
Palladium lattice geometry and deuterium loading — Pillar 15.

In the Unitary Manifold the Pd host lattice is modelled as a KK-compactified
FCC crystal whose geometric parameters derive from the local radion field φ.
Deuterium occupies octahedral interstitial sites; the loading ratio ρ = N_D/N_Pd
controls how strongly φ concentrates at each site, thereby setting the
effective tunneling enhancement experienced by each D–D pair.

The B_μ irreversibility field drives coherent loading: as ρ increases, B_site
grows and constructively interferes with φ to further suppress the Coulomb
barrier.

Theory summary
--------------
Geometric lattice constant (KK compactification):
    a = 2π φ_mean / n_w

FCC site density (4 atoms per unit cell):
    n_sites = 4 / a³

Coherence volume:
    V_coh = (4π/3) ξ³

Local φ at an occupied site:
    φ_site = φ_bulk · (ρ / ρ_ref)^0.5

Lattice strain from over-loading:
    ε = (ρ − ρ₀) / ρ₀

Effective deuteron mass (φ-suppressed):
    m* = 2 / φ_local

B-field at site:
    B_site = B_external · ρ · φ_local

Public API
----------
pd_lattice_constant(phi_mean, n_w)
    a = 2π φ_mean / n_w.

deuterium_loading_ratio(N_D, N_Pd)
    ρ = N_D / N_Pd; raises ValueError if ρ > 2.0.

lattice_site_density(a_lattice)
    n = 4 / a³  (FCC).

octahedral_site_fraction(rho_loading)
    f = rho_loading (occupied fraction equals loading ratio).

coherence_volume(xi)
    V_coh = (4π/3) ξ³.

sites_in_coherence_volume(xi, a_lattice)
    N = V_coh / a³.

phi_at_lattice_site(phi_bulk, rho_loading, rho_ref)
    φ_site = φ_bulk · (ρ/ρ_ref)^0.5.

lattice_strain(rho_loading, rho_0)
    ε = (ρ − ρ₀) / ρ₀.

effective_mass_deuteron(phi_local)
    m* = 2.0 / φ_local.

b_field_at_site(B_external, rho_loading, phi_local)
    B_site = B_external · ρ · φ_local.

loading_threshold_for_fusion(phi_bulk, Z1, Z2, v_rel)
    Minimum ρ such that φ_site > 1 (barrier enters enhancement regime).

pd_shell_number()
    Returns 5 (Pd is in period 5, 5th KK shell).
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

import numpy as np


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_N_W_DEFAULT: int = 5
_RHO_MAX: float = 2.0          # physical upper bound on D/Pd loading ratio
_RHO_REF_DEFAULT: float = 0.75 # reference loading for φ-site enhancement
_RHO_0_DEFAULT: float = 0.68   # equilibrium loading (strain-free)
_NUMERICAL_EPSILON: float = 1e-30


# ---------------------------------------------------------------------------
# Lattice constant
# ---------------------------------------------------------------------------

def pd_lattice_constant(
    phi_mean: float = 1.0,
    n_w: int = _N_W_DEFAULT,
) -> float:
    """Geometric lattice constant from KK compactification.

    In the 5D Kaluza–Klein geometry the natural length scale for the Pd FCC
    lattice is set by the winding number and the mean radion field:

        a = 2π φ_mean / n_w

    For n_w = 5 (Pd sits in the 5th KK shell) and φ_mean = 1 (Planck units)
    this gives a = 2π/5 ≈ 1.257 (Planck units).

    Parameters
    ----------
    phi_mean : float — mean radion ⟨φ⟩ (must be > 0, default 1.0)
    n_w      : int   — winding number of the KK shell (must be > 0, default 5)

    Returns
    -------
    a : float — lattice constant in Planck units (> 0)

    Raises
    ------
    ValueError
        If phi_mean ≤ 0 or n_w ≤ 0.
    """
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    if n_w <= 0:
        raise ValueError(f"n_w must be > 0, got {n_w!r}")
    return float(2.0 * np.pi * phi_mean / n_w)


# ---------------------------------------------------------------------------
# Deuterium loading ratio
# ---------------------------------------------------------------------------

def deuterium_loading_ratio(
    N_D: float,
    N_Pd: float,
) -> float:
    """Deuterium-to-palladium loading ratio ρ = N_D / N_Pd.

    The loading ratio quantifies the occupancy of Pd interstitial sites by
    deuterium atoms.  Physical experiments achieve ρ ≈ 0.6–0.95 for active
    LENR samples; ρ cannot physically exceed 2.0 (two D per Pd is the
    saturation limit).

    Parameters
    ----------
    N_D  : float — number of deuterium atoms (must be ≥ 0)
    N_Pd : float — number of palladium atoms (must be > 0)

    Returns
    -------
    rho : float — loading ratio in [0, 2.0]

    Raises
    ------
    ValueError
        If N_Pd ≤ 0, N_D < 0, or the computed ratio exceeds 2.0.
    """
    if N_Pd <= 0.0:
        raise ValueError(f"N_Pd must be > 0, got {N_Pd!r}")
    if N_D < 0.0:
        raise ValueError(f"N_D must be ≥ 0, got {N_D!r}")
    rho = N_D / N_Pd
    if rho > _RHO_MAX:
        raise ValueError(
            f"Loading ratio {rho!r} exceeds physical maximum of {_RHO_MAX}; "
            f"got N_D={N_D!r}, N_Pd={N_Pd!r}"
        )
    return float(rho)


# ---------------------------------------------------------------------------
# Lattice site density
# ---------------------------------------------------------------------------

def lattice_site_density(
    a_lattice: float,
) -> float:
    """FCC lattice site density from the lattice constant.

    An FCC unit cell contains 4 atoms.  The volumetric density of lattice
    sites (and hence of potential D–D tunneling pairs) is:

        n_sites = 4 / a³

    Parameters
    ----------
    a_lattice : float — lattice constant in Planck units (must be > 0)

    Returns
    -------
    n : float — site density (sites per Planck volume)

    Raises
    ------
    ValueError
        If a_lattice ≤ 0.
    """
    if a_lattice <= 0.0:
        raise ValueError(f"a_lattice must be > 0, got {a_lattice!r}")
    return float(4.0 / a_lattice ** 3)


# ---------------------------------------------------------------------------
# Octahedral site fraction
# ---------------------------------------------------------------------------

def octahedral_site_fraction(
    rho_loading: float,
) -> float:
    """Fraction of octahedral interstitial sites occupied by deuterium.

    In a Pd FCC lattice there is one octahedral interstitial site per host
    atom.  The occupied fraction therefore equals the loading ratio directly:

        f = ρ_loading

    Parameters
    ----------
    rho_loading : float — D/Pd loading ratio in [0, 1] (clamped internally)

    Returns
    -------
    f : float — fractional site occupancy in [0, 1]
    """
    return float(np.clip(rho_loading, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Coherence volume
# ---------------------------------------------------------------------------

def coherence_volume(
    xi: float,
) -> float:
    """Volume of the tunneling coherence sphere of radius ξ.

    The spatial extent over which the φ-enhanced tunneling condensate is
    phase-coherent is modelled as a sphere of radius ξ:

        V_coh = (4π/3) ξ³

    Parameters
    ----------
    xi : float — coherence length in Planck units (must be > 0)

    Returns
    -------
    V_coh : float — coherence volume in Planck units³ (> 0)

    Raises
    ------
    ValueError
        If xi ≤ 0.
    """
    if xi <= 0.0:
        raise ValueError(f"xi must be > 0, got {xi!r}")
    return float(4.0 * np.pi / 3.0 * xi ** 3)


# ---------------------------------------------------------------------------
# Sites in coherence volume
# ---------------------------------------------------------------------------

def sites_in_coherence_volume(
    xi: float,
    a_lattice: float,
) -> float:
    """Number of Pd lattice sites within one coherence volume.

    Divides the coherence volume by the volume per unit cell (a³) to obtain
    the number of lattice sites participating in coherent tunneling:

        N = V_coh / a³

    Parameters
    ----------
    xi        : float — coherence length in Planck units (must be > 0)
    a_lattice : float — lattice constant in Planck units (must be > 0)

    Returns
    -------
    N_sites : float — number of sites within the coherence volume

    Raises
    ------
    ValueError
        If xi ≤ 0 or a_lattice ≤ 0.
    """
    V_coh = coherence_volume(xi)
    if a_lattice <= 0.0:
        raise ValueError(f"a_lattice must be > 0, got {a_lattice!r}")
    return float(V_coh / a_lattice ** 3)


# ---------------------------------------------------------------------------
# Local φ at lattice site
# ---------------------------------------------------------------------------

def phi_at_lattice_site(
    phi_bulk: float,
    rho_loading: float,
    rho_ref: float = _RHO_REF_DEFAULT,
) -> float:
    """Local φ at an occupied octahedral site as a function of loading.

    The radion field concentrates at high-occupancy sites.  The enhancement
    scales as the square root of the loading ratio relative to a reference:

        φ_site = φ_bulk · (ρ / ρ_ref)^0.5

    At ρ = ρ_ref the site φ equals the bulk value.  Above ρ_ref the field is
    enhanced; below it is suppressed.

    Parameters
    ----------
    phi_bulk    : float — bulk (average) φ value (must be > 0)
    rho_loading : float — D/Pd loading ratio (must be > 0)
    rho_ref     : float — reference loading ratio (default 0.75, must be > 0)

    Returns
    -------
    phi_site : float — local φ at the lattice site (> 0)

    Raises
    ------
    ValueError
        If phi_bulk ≤ 0, rho_loading ≤ 0, or rho_ref ≤ 0.
    """
    if phi_bulk <= 0.0:
        raise ValueError(f"phi_bulk must be > 0, got {phi_bulk!r}")
    if rho_loading <= 0.0:
        raise ValueError(f"rho_loading must be > 0, got {rho_loading!r}")
    if rho_ref <= 0.0:
        raise ValueError(f"rho_ref must be > 0, got {rho_ref!r}")
    return float(phi_bulk * np.sqrt(rho_loading / rho_ref))


# ---------------------------------------------------------------------------
# Lattice strain
# ---------------------------------------------------------------------------

def lattice_strain(
    rho_loading: float,
    rho_0: float = _RHO_0_DEFAULT,
) -> float:
    """Fractional lattice strain induced by deuterium over-loading.

    Excess deuterium beyond the strain-free loading ρ₀ expands the Pd
    lattice.  The fractional strain is:

        ε = (ρ − ρ₀) / ρ₀

    Negative ε means the lattice is under-loaded (compressed relative to
    the equilibrium configuration).

    Parameters
    ----------
    rho_loading : float — current D/Pd loading ratio
    rho_0       : float — strain-free (equilibrium) loading ratio (default 0.68,
                          must be > 0)

    Returns
    -------
    eps : float — fractional strain (dimensionless)

    Raises
    ------
    ValueError
        If rho_0 ≤ 0.
    """
    if rho_0 <= 0.0:
        raise ValueError(f"rho_0 must be > 0, got {rho_0!r}")
    return float((rho_loading - rho_0) / rho_0)


# ---------------------------------------------------------------------------
# Effective deuteron mass
# ---------------------------------------------------------------------------

def effective_mass_deuteron(
    phi_local: float,
) -> float:
    """Effective deuteron mass suppressed by the local φ field.

    The 5D compactification modifies the inertial mass of a deuteron
    confined to a lattice site.  Larger φ means the compactified dimension
    is more open, reducing the effective 4D mass:

        m* = 2.0 / φ_local

    For φ_local = 1 the bare deuteron mass is recovered (m* = 2 in Planck
    units); for φ_local > 1 the mass is suppressed, increasing the tunneling
    de Broglie wavelength.

    Parameters
    ----------
    phi_local : float — local φ at the lattice site (must be > 0)

    Returns
    -------
    m_star : float — effective mass in Planck units (> 0)

    Raises
    ------
    ValueError
        If phi_local ≤ 0.
    """
    if phi_local <= 0.0:
        raise ValueError(f"phi_local must be > 0, got {phi_local!r}")
    return float(2.0 / phi_local)


# ---------------------------------------------------------------------------
# B-field at site
# ---------------------------------------------------------------------------

def b_field_at_site(
    B_external: float,
    rho_loading: float,
    phi_local: float,
) -> float:
    """Effective B_μ irreversibility field at an occupied lattice site.

    The irreversibility field is amplified at heavily loaded sites because
    both the loading ratio and the local φ constructively focus the field:

        B_site = B_external · ρ · φ_local

    Parameters
    ----------
    B_external  : float — applied external B_μ field strength (≥ 0)
    rho_loading : float — D/Pd loading ratio (must be ≥ 0)
    phi_local   : float — local φ at the lattice site (must be > 0)

    Returns
    -------
    B_site : float — local field strength at the site (≥ 0)

    Raises
    ------
    ValueError
        If B_external < 0, rho_loading < 0, or phi_local ≤ 0.
    """
    if B_external < 0.0:
        raise ValueError(f"B_external must be ≥ 0, got {B_external!r}")
    if rho_loading < 0.0:
        raise ValueError(f"rho_loading must be ≥ 0, got {rho_loading!r}")
    if phi_local <= 0.0:
        raise ValueError(f"phi_local must be > 0, got {phi_local!r}")
    return float(B_external * rho_loading * phi_local)


# ---------------------------------------------------------------------------
# Loading threshold for fusion
# ---------------------------------------------------------------------------

def loading_threshold_for_fusion(
    phi_bulk: float,
    Z1: float = 1.0,
    Z2: float = 1.0,
    v_rel: float = 0.001,
) -> float:
    """Minimum loading ratio ρ such that the local φ exceeds 1.

    Fusion enhancement requires φ_site > 1 so that the Gamow exponent is
    actually divided by a number greater than unity.  Inverting
    phi_at_lattice_site gives:

        φ_site = φ_bulk · (ρ / ρ_ref)^0.5 = 1
        ⟹  ρ_min = ρ_ref / φ_bulk²

    Parameters
    ----------
    phi_bulk : float — bulk φ value (must be > 0)
    Z1       : float — charge number of first nucleus (unused, for API symmetry)
    Z2       : float — charge number of second nucleus (unused, for API symmetry)
    v_rel    : float — relative velocity (unused, for API symmetry)

    Returns
    -------
    rho_min : float — minimum loading ratio for φ_site ≥ 1

    Raises
    ------
    ValueError
        If phi_bulk ≤ 0.
    """
    if phi_bulk <= 0.0:
        raise ValueError(f"phi_bulk must be > 0, got {phi_bulk!r}")
    return float(_RHO_REF_DEFAULT / phi_bulk ** 2)


# ---------------------------------------------------------------------------
# Pd shell number
# ---------------------------------------------------------------------------

def pd_shell_number() -> int:
    """KK shell number for palladium.

    Palladium (Z = 46) is in period 5 of the periodic table, corresponding
    to the 5th Kaluza–Klein winding shell in the Unitary Manifold.  This is
    why n_w = 5 is the canonical winding number for the Pd lattice constant.

    Returns
    -------
    n : int — KK shell number for Pd (always 5)
    """
    return 5
