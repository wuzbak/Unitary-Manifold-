# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/fh_curved.py
========================
Curved-space Fermi–Hubbard extension scaffolding for the UM adjacent quantum lane.

EPISTEMIC STATUS — ADJACENT ENGINEERING LANE (NON-HARDGATE)
------------------------------------------------------------
This module provides the geometry-aware interface for Fermi–Hubbard models
on curved lattices, specifically those coupled to the Unitary Manifold
Kaluza–Klein radion field.

Physics context
---------------
In the Unitary Manifold the 5th (compact) dimension is parameterised by
a radion field φ(x).  When the KK geometry is mapped to a condensed-matter
lattice, the radion modulates the local hopping amplitude:

    t_{ij} = t₀ · f(φᵢ, φⱼ)    with  f(φᵢ, φⱼ) = exp[−λ·|φᵢ − φⱼ|]

where λ is the radion coupling (KK_RADION_COUPLING below) and φᵢ is the
radion field value at site i.

For a uniform radion background φᵢ = φ₀ the coupling reduces to f = 1
(standard flat-space FH).  Non-uniform backgrounds encode the geometry of
the compact dimension as a site-dependent hopping modulation.

IMPORTANT: This is an ADJACENT TRACK connection — the existence of such a
coupling does NOT constitute a hardgate UM pillar and does NOT alter the
core ToE score.  The separation is enforced explicitly by ``separation_guard()``.

KK-natural coupling
-------------------
The canonical radion coupling follows from the (5,7) braid pair:

    λ = c_s / n_w = (12/37) / 5 = 12/185 ≈ 0.064865…

where c_s = 12/37 is the braided sound speed and n_w = 5 is the winding number.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Sequence

from .fermi_hubbard import FermionTerm
from .fh_lattice import (
    FermiHubbardLattice,
    LatticeGeometry,
    ADJACENCY_TRACK_LABEL,
    UM_BRAID_N1,
    UM_BRAID_N2,
)

__all__ = [
    # Constants
    "KK_RADION_COUPLING",
    "KK_BRAIDED_SOUND_SPEED",
    "KK_WINDING_NUMBER",
    "CURVED_TRACK_LABEL",
    # Specs
    "RadionField",
    "CurvedSpaceFHSpec",
    "KKCurvedGeometrySpec",
    # Functions
    "radion_hopping_factor",
    "curved_hopping_coefficient",
    "build_radion_field_uniform",
    "build_radion_field_sinusoidal",
    "build_radion_field_kk_natural",
    "build_fermi_hubbard_curved",
    "kk_curved_spec",
    "separation_guard",
    "curved_adjacency_report",
]

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

KK_BRAIDED_SOUND_SPEED: float = 12.0 / 37.0   # c_s from (5,7) braid resonance
KK_WINDING_NUMBER: int = UM_BRAID_N1           # n_w = 5
KK_RADION_COUPLING: float = KK_BRAIDED_SOUND_SPEED / KK_WINDING_NUMBER
# = (12/37) / 5 = 12/185 ≈ 0.064865…

CURVED_TRACK_LABEL: str = (
    "ADJACENT_TRACK_FH_CURVED — NOT a hardgate UM pillar; "
    "radion coupling is an exploratory adjacent-lane connection only"
)


# ---------------------------------------------------------------------------
# Radion field specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RadionField:
    """Site-resolved radion field configuration φᵢ for a Fermi–Hubbard lattice.

    Attributes
    ----------
    values:
        Tuple of length n_sites with φᵢ for each site.
    profile:
        Human-readable profile name (e.g. ``"uniform"``, ``"sinusoidal"``,
        ``"kk_natural"``).
    coupling:
        Radion–hopping coupling constant λ (default: KK_RADION_COUPLING).
    """

    values: tuple[float, ...]
    profile: str
    coupling: float = KK_RADION_COUPLING

    def __post_init__(self) -> None:
        if len(self.values) < 2:
            raise ValueError("RadionField must have at least 2 site values")
        if self.coupling < 0:
            raise ValueError("coupling λ must be ≥ 0")

    @property
    def n_sites(self) -> int:
        return len(self.values)

    @property
    def phi_min(self) -> float:
        return min(self.values)

    @property
    def phi_max(self) -> float:
        return max(self.values)

    @property
    def phi_spread(self) -> float:
        return self.phi_max - self.phi_min


# ---------------------------------------------------------------------------
# Curved-space FH specification dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CurvedSpaceFHSpec:
    """Full specification of a curved-space Fermi–Hubbard model.

    Attributes
    ----------
    base_lattice:
        The underlying FermiHubbardLattice (flat-space geometry).
    radion:
        The site-resolved radion field modulating hopping.
    hopping_factor_fn:
        Function (phi_i, phi_j, coupling) → float describing the bond
        hopping modulation.  Defaults to ``radion_hopping_factor``.
    notes:
        Free-text annotation.
    """

    base_lattice: FermiHubbardLattice
    radion: RadionField
    notes: str = ""

    def __post_init__(self) -> None:
        if self.radion.n_sites != self.base_lattice.n_sites:
            raise ValueError(
                f"RadionField has {self.radion.n_sites} sites but "
                f"base_lattice has {self.base_lattice.n_sites} sites"
            )

    @property
    def n_sites(self) -> int:
        return self.base_lattice.n_sites

    @property
    def n_modes(self) -> int:
        return self.base_lattice.n_modes

    @property
    def geometry(self) -> LatticeGeometry:
        return self.base_lattice.geometry


@dataclass(frozen=True)
class KKCurvedGeometrySpec:
    """KK-specific curved geometry coupling parameters.

    Attributes
    ----------
    n1, n2:
        KK braid winding integers (canonical: 5, 7).
    k_cs:
        Chern–Simons level = n1² + n2² (canonical: 74).
    radion_amplitude:
        Maximum radion field variation Δφ across the ring.
    n_sites:
        Number of lattice sites (default: n1 + n2 = 12).
    """

    n1: int = UM_BRAID_N1
    n2: int = UM_BRAID_N2
    k_cs: int = 74
    radion_amplitude: float = 0.1
    n_sites: int = UM_BRAID_N1 + UM_BRAID_N2

    def __post_init__(self) -> None:
        if self.n1 <= 0 or self.n2 <= 0:
            raise ValueError("n1 and n2 must be positive")
        if self.k_cs != self.n1 ** 2 + self.n2 ** 2:
            raise ValueError(f"k_cs must equal n1²+n2² = {self.n1**2+self.n2**2}")
        if self.radion_amplitude < 0:
            raise ValueError("radion_amplitude must be ≥ 0")
        if self.n_sites < 2:
            raise ValueError("n_sites must be ≥ 2")

    @property
    def coupling(self) -> float:
        """KK-natural radion coupling λ = c_s / n_w."""
        return KK_RADION_COUPLING

    @property
    def flat_limit(self) -> bool:
        """True when radion_amplitude ≈ 0 (flat-space limit)."""
        return self.radion_amplitude < 1e-12


# ---------------------------------------------------------------------------
# Radion hopping functions
# ---------------------------------------------------------------------------


def radion_hopping_factor(phi_i: float, phi_j: float, coupling: float) -> float:
    """Compute bond hopping modulation factor for a radion field.

    f(φᵢ, φⱼ) = exp[−λ · |φᵢ − φⱼ|]

    Parameters
    ----------
    phi_i, phi_j:
        Radion field values at the two sites of the bond.
    coupling:
        Radion–hopping coupling constant λ (≥ 0).

    Returns
    -------
    float in (0, 1] giving the hopping suppression factor.
    """
    if coupling < 0:
        raise ValueError("coupling λ must be ≥ 0")
    return math.exp(-coupling * abs(phi_i - phi_j))


def curved_hopping_coefficient(
    base_t: float,
    phi_i: float,
    phi_j: float,
    coupling: float,
) -> float:
    """Compute the radion-modulated hopping coefficient t_{ij}.

    t_{ij} = t₀ · f(φᵢ, φⱼ) = t₀ · exp[−λ · |φᵢ − φⱼ|]

    Parameters
    ----------
    base_t:
        Bare hopping amplitude t₀ (≥ 0).
    phi_i, phi_j:
        Radion field values at the two sites.
    coupling:
        Radion coupling λ.

    Returns
    -------
    Effective hopping coefficient t_{ij} ≥ 0.
    """
    if base_t < 0:
        raise ValueError("base_t must be ≥ 0")
    return base_t * radion_hopping_factor(phi_i, phi_j, coupling)


# ---------------------------------------------------------------------------
# Radion field builders
# ---------------------------------------------------------------------------


def build_radion_field_uniform(
    n_sites: int,
    phi0: float = 0.0,
    coupling: float = KK_RADION_COUPLING,
) -> RadionField:
    """Uniform radion background φᵢ = φ₀ for all sites (flat-space limit)."""
    return RadionField(
        values=tuple(phi0 for _ in range(n_sites)),
        profile="uniform",
        coupling=coupling,
    )


def build_radion_field_sinusoidal(
    n_sites: int,
    amplitude: float = 0.1,
    phase: float = 0.0,
    coupling: float = KK_RADION_COUPLING,
) -> RadionField:
    """Sinusoidal radion profile φᵢ = A · sin(2π·i/N + φ₀).

    Parameters
    ----------
    n_sites:
        Number of lattice sites.
    amplitude:
        Amplitude A of the sinusoidal modulation.
    phase:
        Phase offset φ₀ in radians.
    coupling:
        Radion coupling λ.
    """
    values = tuple(
        amplitude * math.sin(2.0 * math.pi * i / n_sites + phase)
        for i in range(n_sites)
    )
    return RadionField(values=values, profile="sinusoidal", coupling=coupling)


def build_radion_field_kk_natural(
    kk_spec: KKCurvedGeometrySpec,
) -> RadionField:
    """Build the KK-natural radion field for a (n1, n2) braid ring.

    The KK radion profile is set by the winding-number-weighted sinusoid:

        φᵢ = A · [n1·sin(2π·i/N) − n2·cos(2π·i/N)] / K_CS

    where A = kk_spec.radion_amplitude, N = kk_spec.n_sites.

    EPISTEMIC STATUS — ADJACENT TRACK only.
    """
    n = kk_spec.n_sites
    A = kk_spec.radion_amplitude
    n1, n2, k_cs = kk_spec.n1, kk_spec.n2, kk_spec.k_cs

    values = tuple(
        A * (n1 * math.sin(2.0 * math.pi * i / n) - n2 * math.cos(2.0 * math.pi * i / n)) / k_cs
        for i in range(n)
    )
    return RadionField(
        values=values,
        profile="kk_natural",
        coupling=kk_spec.coupling,
    )


# ---------------------------------------------------------------------------
# Curved FH model builder
# ---------------------------------------------------------------------------


def build_fermi_hubbard_curved(
    spec: CurvedSpaceFHSpec,
) -> "CurvedFermiHubbardLattice":
    """Construct a curved-space FH model from a CurvedSpaceFHSpec.

    Returns a ``CurvedFermiHubbardLattice`` whose ``fermionic_terms()``
    produces bond-dependent hopping coefficients t_{ij} modulated by the
    radion field.

    EPISTEMIC STATUS — ADJACENT TRACK only.
    """
    return CurvedFermiHubbardLattice(spec=spec)


# ---------------------------------------------------------------------------
# CurvedFermiHubbardLattice — FH model with geometry-aware hopping
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CurvedFermiHubbardLattice:
    """Fermi–Hubbard model with radion-modulated site-dependent hopping.

    Mirrors the duck-typing interface of ``FermiHubbardLattice`` so that
    the UM ED solver and XDiag bridge can accept it.

    EPISTEMIC STATUS — ADJACENT ENGINEERING LANE (NON-HARDGATE).
    """

    spec: CurvedSpaceFHSpec

    # --- Compatibility interface ----------------------------------------

    @property
    def n_sites(self) -> int:
        return self.spec.n_sites

    @property
    def n_modes(self) -> int:
        return self.spec.n_modes

    @property
    def periodic(self) -> bool:
        return self.spec.geometry.periodic

    @property
    def hopping_t(self) -> float:
        return self.spec.base_lattice.hopping_t

    @property
    def interaction_u(self) -> float:
        return self.spec.base_lattice.interaction_u

    @property
    def chemical_potential(self) -> float:
        return self.spec.base_lattice.chemical_potential

    def mode_index(self, site: int, spin: int) -> int:
        return self.spec.base_lattice.mode_index(site, spin)

    def hopping_edges(self) -> list[tuple[int, int]]:
        return self.spec.base_lattice.hopping_edges()

    def effective_hopping(self, i: int, j: int) -> float:
        """Bond-specific hopping coefficient t_{ij} after radion modulation."""
        phi_i = self.spec.radion.values[i]
        phi_j = self.spec.radion.values[j]
        return curved_hopping_coefficient(
            self.hopping_t, phi_i, phi_j, self.spec.radion.coupling
        )

    def fermionic_terms(self) -> list[FermionTerm]:
        """Return FH Hamiltonian terms with radion-modulated hopping.

        H_curved = -Σ_{<i,j>,σ} t_{ij} (c†_{iσ} c_{jσ} + h.c.)
                 + U Σ_i n_{i↑} n_{i↓}
                 - μ Σ_{i,σ} n_{iσ}

        where t_{ij} = t₀ · exp[−λ · |φᵢ − φⱼ|].
        """
        terms: list[FermionTerm] = []

        for i, j in self.hopping_edges():
            t_ij = self.effective_hopping(i, j)
            for spin in (0, 1):
                mi = self.mode_index(i, spin)
                mj = self.mode_index(j, spin)
                terms.append(FermionTerm(-t_ij, ((mi, True), (mj, False))))
                terms.append(FermionTerm(-t_ij, ((mj, True), (mi, False))))

        if self.interaction_u:
            for i in range(self.n_sites):
                up = self.mode_index(i, 0)
                dn = self.mode_index(i, 1)
                terms.append(
                    FermionTerm(
                        self.interaction_u,
                        ((up, True), (up, False), (dn, True), (dn, False)),
                    )
                )

        if self.chemical_potential:
            for i in range(self.n_sites):
                for spin in (0, 1):
                    m = self.mode_index(i, spin)
                    terms.append(
                        FermionTerm(-self.chemical_potential, ((m, True), (m, False)))
                    )

        return terms


# ---------------------------------------------------------------------------
# KK curved spec convenience constructor
# ---------------------------------------------------------------------------


def kk_curved_spec(
    hopping_t: float = 1.0,
    interaction_u: float | None = None,
    radion_amplitude: float = 0.1,
) -> CurvedSpaceFHSpec:
    """Build the canonical KK-natural curved FH spec for a 12-site braid ring.

    EPISTEMIC STATUS — ADJACENT TRACK only.

    Parameters
    ----------
    hopping_t:
        Bare hopping amplitude t₀.
    interaction_u:
        On-site interaction U.  Defaults to KK_U_OVER_T ≈ 78.23 (Mott regime).
    radion_amplitude:
        Radion modulation amplitude.  Set to 0 for the flat-space limit.
    """
    from .fh_lattice import build_fermi_hubbard_braid_kk  # avoid circular

    base = build_fermi_hubbard_braid_kk(
        hopping_t=hopping_t,
        interaction_u=interaction_u,
    )
    kk_spec = KKCurvedGeometrySpec(radion_amplitude=radion_amplitude)
    radion = build_radion_field_kk_natural(kk_spec)
    return CurvedSpaceFHSpec(
        base_lattice=base,
        radion=radion,
        notes=(
            "KK-natural curved FH spec: (5,7) braid ring with sinusoidal "
            "radion modulation. ADJACENT TRACK — not a hardgate UM pillar."
        ),
    )


# ---------------------------------------------------------------------------
# Separation guard
# ---------------------------------------------------------------------------


def separation_guard() -> dict[str, str]:
    """Hard assertion that this module is non-hardgate adjacent track.

    Returns a dict confirming the epistemic status.  Any caller requiring
    physics-grade hardgate claims should use the core src/core/ modules.
    """
    return {
        "status": CURVED_TRACK_LABEL,
        "toe_score_impact": "NONE",
        "hardgate": "FALSE",
        "physics_claim": "NONE",
        "message": (
            "fh_curved.py is an adjacent engineering lane exploring the "
            "connection between KK radion geometry and FH hopping modulation. "
            "It does NOT constitute a hardgate UM pillar and does NOT alter "
            "the core ToE score.  See docs/CLAIM_MASTER_BOARD.md §Lane F."
        ),
    }


# ---------------------------------------------------------------------------
# Adjacency report helper
# ---------------------------------------------------------------------------


def curved_adjacency_report(model: CurvedFermiHubbardLattice) -> dict[str, object]:
    """Return a geometry and coupling summary for a curved FH model."""
    phi = model.spec.radion.values
    bond_hoppings = {
        (i, j): model.effective_hopping(i, j) for i, j in model.hopping_edges()
    }
    return {
        "geometry": model.spec.geometry.geometry,
        "n_sites": model.n_sites,
        "n_modes": model.n_modes,
        "radion_profile": model.spec.radion.profile,
        "radion_coupling": model.spec.radion.coupling,
        "phi_min": min(phi),
        "phi_max": max(phi),
        "phi_spread": max(phi) - min(phi),
        "base_hopping_t": model.hopping_t,
        "interaction_u": model.interaction_u,
        "n_bonds": len(bond_hoppings),
        "min_effective_hopping": min(bond_hoppings.values()) if bond_hoppings else 0.0,
        "max_effective_hopping": max(bond_hoppings.values()) if bond_hoppings else 0.0,
        "flat_limit": model.spec.radion.phi_spread < 1e-12,
        "status": CURVED_TRACK_LABEL,
        "separation_guard": separation_guard(),
    }
