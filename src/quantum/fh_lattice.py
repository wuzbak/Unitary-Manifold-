# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/fh_lattice.py
=========================
Geometry-aware Fermi–Hubbard lattice module supporting 1D chains,
2D square lattices, 3D cubic lattices, and the KK-natural (5,7) braid ring.

EPISTEMIC STATUS — ADJACENT ENGINEERING LANE (NON-HARDGATE)
------------------------------------------------------------
This module extends the FH adjacent research lane to multi-dimensional
geometries.  Results are NOT hardgate UM pillars and do NOT alter the
core ToE score.  All geometry labels carry explicit ADJACENT_TRACK markers.

Supported geometries
--------------------
chain_1d    — open or periodic 1D chain (wraps the existing 1D builder)
square_2d   — 2D n×m square lattice with nearest-neighbour hopping
cubic_3d    — 3D n×m×k cubic lattice (memory-bounded, uses sparse for large sizes)
braid_kk    — KK-natural (5,7) braid topology on a ring with N=5+7=12 sites
custom      — caller-supplied adjacency list

Memory guidance (complex128, full Hilbert space 2^(2·n_sites))
--------------------------------------------------------------
n_sites =  6 → 2^12 =   4 096 states  (ED trivial)
n_sites =  8 → 2^16 =  65 536 states  (ED fast)
n_sites = 10 → 2^20 =   1.0 M states  (ED moderate)
n_sites = 12 → 2^24 =  16.8 M states  (ED slow; prefer sparse or XDiag)
n_sites = 14 → 2^28 = 268.4 M states  (XDiag lane recommended)
n_sites = 16 → 2^32 =   4.3 G states  (XDiag-only; UM dense infeasible)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

from .fermi_hubbard import FermionTerm, FermiHubbardHamiltonian, build_fermi_hubbard_1d

__all__ = [
    # Geometry specifications
    "LatticeGeometry",
    "chain_1d_geometry",
    "square_2d_geometry",
    "cubic_3d_geometry",
    "braid_kk_geometry",
    "custom_geometry",
    # Main lattice model
    "FermiHubbardLattice",
    # Factories
    "build_fermi_hubbard_chain",
    "build_fermi_hubbard_square_2d",
    "build_fermi_hubbard_cubic_3d",
    "build_fermi_hubbard_braid_kk",
    # Helpers
    "memory_estimate_bytes",
    "memory_estimate_gb",
    "hilbert_space_dimension",
    "ADJACENCY_TRACK_LABEL",
    "UM_BRAID_SITES",
    "UM_BRAID_N1",
    "UM_BRAID_N2",
]

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

ADJACENCY_TRACK_LABEL: str = "ADJACENT_TRACK_FH_LATTICE — NOT a hardgate UM pillar"

#: KK braid integers determining the natural ring geometry
UM_BRAID_N1: int = 5
UM_BRAID_N2: int = 7
UM_BRAID_SITES: int = UM_BRAID_N1 + UM_BRAID_N2  # = 12


# ---------------------------------------------------------------------------
# LatticeGeometry — immutable specification of the adjacency graph
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LatticeGeometry:
    """Immutable adjacency-list description of a Fermi–Hubbard lattice.

    Attributes
    ----------
    n_sites:
        Total number of lattice sites.
    edges:
        Tuple of (i, j) directed nearest-neighbour edges (both i→j and j→i
        are included by convention so that ``fermionic_terms()`` sums over
        all bonds correctly).  Each undirected bond appears *once* — the
        FH Hamiltonian builder adds both hopping directions internally.
    geometry:
        One of ``"chain_1d"``, ``"square_2d"``, ``"cubic_3d"``,
        ``"braid_kk"``, or ``"custom"``.
    dims:
        Shape tuple.  For a 4×4 square lattice ``dims = (4, 4)``.
        Empty for 1D chains and custom geometries.
    periodic:
        Whether periodic boundary conditions are applied.
    """

    n_sites: int
    edges: tuple[tuple[int, int], ...]
    geometry: str
    dims: tuple[int, ...] = ()
    periodic: bool = False

    def __post_init__(self) -> None:
        if self.n_sites < 2:
            raise ValueError("n_sites must be ≥ 2")
        allowed = {"chain_1d", "square_2d", "cubic_3d", "braid_kk", "custom"}
        if self.geometry not in allowed:
            raise ValueError(f"geometry must be one of {sorted(allowed)}")
        for e in self.edges:
            if len(e) != 2:
                raise ValueError("Each edge must be a (i, j) pair")
            i, j = e
            if not (0 <= i < self.n_sites and 0 <= j < self.n_sites):
                raise ValueError(f"Edge ({i}, {j}) references site out of range [0, {self.n_sites})")
            if i == j:
                raise ValueError(f"Self-loop at site {i} is not allowed")

    @property
    def n_bonds(self) -> int:
        """Number of distinct undirected bonds."""
        return len(self.edges)

    @property
    def coordination_number_avg(self) -> float:
        """Average number of neighbours per site."""
        if self.n_sites == 0:
            return 0.0
        return 2.0 * self.n_bonds / self.n_sites


# ---------------------------------------------------------------------------
# Geometry factory helpers
# ---------------------------------------------------------------------------


def chain_1d_geometry(n_sites: int, periodic: bool = False) -> LatticeGeometry:
    """1D chain geometry (open or periodic boundary conditions)."""
    if n_sites < 2:
        raise ValueError("n_sites must be ≥ 2 for a chain")
    edges_list: list[tuple[int, int]] = [(i, i + 1) for i in range(n_sites - 1)]
    if periodic:
        edges_list.append((n_sites - 1, 0))
    return LatticeGeometry(
        n_sites=n_sites,
        edges=tuple(edges_list),
        geometry="chain_1d",
        dims=(n_sites,),
        periodic=periodic,
    )


def square_2d_geometry(n_rows: int, n_cols: int, periodic: bool = False) -> LatticeGeometry:
    """2D square lattice with nearest-neighbour hopping.

    Site numbering: site (r, c) → r * n_cols + c.
    Nearest neighbours are (right, below) with periodic wrapping if requested.

    Parameters
    ----------
    n_rows, n_cols:
        Lattice dimensions.  Both must be ≥ 2.
    periodic:
        Apply periodic boundary conditions in both directions.
    """
    if n_rows < 2 or n_cols < 2:
        raise ValueError("n_rows and n_cols must both be ≥ 2 for a 2D square lattice")

    n_sites = n_rows * n_cols
    edges_set: set[tuple[int, int]] = set()

    def idx(r: int, c: int) -> int:
        return r * n_cols + c

    for r in range(n_rows):
        for c in range(n_cols):
            site = idx(r, c)
            # Right neighbour
            if c + 1 < n_cols:
                edges_set.add((site, idx(r, c + 1)))
            elif periodic:
                edges_set.add((site, idx(r, 0)))
            # Lower neighbour
            if r + 1 < n_rows:
                edges_set.add((site, idx(r + 1, c)))
            elif periodic:
                edges_set.add((site, idx(0, c)))

    return LatticeGeometry(
        n_sites=n_sites,
        edges=tuple(sorted(edges_set)),
        geometry="square_2d",
        dims=(n_rows, n_cols),
        periodic=periodic,
    )


def cubic_3d_geometry(n_x: int, n_y: int, n_z: int, periodic: bool = False) -> LatticeGeometry:
    """3D cubic lattice with nearest-neighbour hopping.

    Site numbering: site (x, y, z) → x*n_y*n_z + y*n_z + z.

    Memory warning
    --------------
    The full Hilbert space scales as 2^(2·n_x·n_y·n_z).  For n_x=n_y=n_z=3
    (27 sites) this is 2^54 ≈ 1.8×10^16 states — far beyond any dense ED.
    Use this geometry only with the XDiag sparse engine (n_sites ≤ ~12)
    or for abstract connectivity tests.

    Parameters
    ----------
    n_x, n_y, n_z:
        Lattice dimensions.  All must be ≥ 2.
    periodic:
        Apply periodic boundary conditions in all three directions.
    """
    if n_x < 2 or n_y < 2 or n_z < 2:
        raise ValueError("All cubic dimensions must be ≥ 2")

    n_sites = n_x * n_y * n_z
    edges_set: set[tuple[int, int]] = set()

    def idx(x: int, y: int, z: int) -> int:
        return x * n_y * n_z + y * n_z + z

    for x in range(n_x):
        for y in range(n_y):
            for z in range(n_z):
                site = idx(x, y, z)
                for dx, dy, dz in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                    nx_, ny_, nz_ = x + dx, y + dy, z + dz
                    if nx_ < n_x and ny_ < n_y and nz_ < n_z:
                        edges_set.add((site, idx(nx_, ny_, nz_)))
                    elif periodic:
                        edges_set.add((site, idx(nx_ % n_x, ny_ % n_y, nz_ % n_z)))

    return LatticeGeometry(
        n_sites=n_sites,
        edges=tuple(sorted(edges_set)),
        geometry="cubic_3d",
        dims=(n_x, n_y, n_z),
        periodic=periodic,
    )


def braid_kk_geometry(periodic: bool = True) -> LatticeGeometry:
    """KK-natural (5,7) braid topology on a ring of 12 = 5+7 sites.

    The UM (5,7) braid pair determines N = 5+7 = 12 ring sites.
    This is the natural embedding of the KK winding lattice as an FH model.
    Connections follow the ring topology with an additional braid bond
    between sites 4 and 7 (the junction of the two braid groups).

    EPISTEMIC STATUS — ADJACENT TRACK only.
    """
    n_sites = UM_BRAID_SITES  # = 12
    # Primary ring bonds
    edges_set: set[tuple[int, int]] = set()
    for i in range(n_sites):
        edges_set.add((i, (i + 1) % n_sites))
    # Braid junction: site n1-1=4 connects to site n1=5 (standard ring) AND
    # across to site n1+n2-1=11 to capture the (5,7) winding interleaving
    if UM_BRAID_N1 > 0 and UM_BRAID_N2 > 0:
        edges_set.add((UM_BRAID_N1 - 1, UM_BRAID_SITES - 1))  # (4, 11)
    return LatticeGeometry(
        n_sites=n_sites,
        edges=tuple(sorted(edges_set)),
        geometry="braid_kk",
        dims=(UM_BRAID_N1, UM_BRAID_N2),
        periodic=periodic,
    )


def custom_geometry(
    n_sites: int, edges: Sequence[tuple[int, int]]
) -> LatticeGeometry:
    """User-supplied arbitrary adjacency list.

    Parameters
    ----------
    n_sites:
        Number of lattice sites.
    edges:
        Undirected bonds as (i, j) pairs.  Both i < j and i > j are
        accepted; duplicates are silently de-duplicated.
    """
    # Canonicalise: sort each edge so that i < j, then de-duplicate.
    canon: set[tuple[int, int]] = set()
    for i, j in edges:
        canon.add((min(i, j), max(i, j)))
    return LatticeGeometry(
        n_sites=n_sites,
        edges=tuple(sorted(canon)),
        geometry="custom",
    )


# ---------------------------------------------------------------------------
# FermiHubbardLattice — FH model on an arbitrary geometry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FermiHubbardLattice:
    """Fermi–Hubbard model on an arbitrary LatticeGeometry.

    This class mirrors the interface of ``FermiHubbardHamiltonian`` so that
    it can be passed to ``fh_solver.exact_diagonalize`` via duck typing.

    EPISTEMIC STATUS — ADJACENT ENGINEERING LANE (NON-HARDGATE).
    """

    geometry: LatticeGeometry
    hopping_t: float
    interaction_u: float
    chemical_potential: float = 0.0

    def __post_init__(self) -> None:
        if self.hopping_t < 0:
            raise ValueError("hopping_t must be ≥ 0")
        if self.interaction_u < 0:
            raise ValueError("interaction_u must be ≥ 0")

    # --- Compatibility interface (mirrors FermiHubbardHamiltonian) ----------

    @property
    def n_sites(self) -> int:
        return self.geometry.n_sites

    @property
    def n_modes(self) -> int:
        return 2 * self.geometry.n_sites

    @property
    def periodic(self) -> bool:
        return self.geometry.periodic

    def mode_index(self, site: int, spin: int) -> int:
        """Return orbital index for site and spin (0=up, 1=down)."""
        if not 0 <= site < self.n_sites:
            raise ValueError(f"site {site} out of range [0, {self.n_sites})")
        if spin not in (0, 1):
            raise ValueError("spin must be 0 (up) or 1 (down)")
        return 2 * site + spin

    def hopping_edges(self) -> list[tuple[int, int]]:
        """Return the list of undirected nearest-neighbour bonds."""
        return list(self.geometry.edges)

    def fermionic_terms(self) -> list[FermionTerm]:
        """Return normal-ordered second-quantized Hamiltonian terms.

        H = -t Σ_{<i,j>,σ} (c†_{iσ} c_{jσ} + c†_{jσ} c_{iσ})
            + U Σ_i n_{i↑} n_{i↓}
            - μ Σ_{i,σ} n_{iσ}
        """
        terms: list[FermionTerm] = []

        for i, j in self.hopping_edges():
            for spin in (0, 1):
                mi = self.mode_index(i, spin)
                mj = self.mode_index(j, spin)
                terms.append(FermionTerm(-self.hopping_t, ((mi, True), (mj, False))))
                terms.append(FermionTerm(-self.hopping_t, ((mj, True), (mi, False))))

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

    def adjacency_report(self) -> dict[str, object]:
        """Return a summary of the lattice geometry."""
        return {
            "geometry": self.geometry.geometry,
            "n_sites": self.n_sites,
            "n_modes": self.n_modes,
            "n_bonds": self.geometry.n_bonds,
            "coordination_number_avg": self.geometry.coordination_number_avg,
            "dims": self.geometry.dims,
            "periodic": self.periodic,
            "hopping_t": self.hopping_t,
            "interaction_u": self.interaction_u,
            "chemical_potential": self.chemical_potential,
            "hilbert_space_dim": hilbert_space_dimension(self.n_sites),
            "memory_estimate_gb": memory_estimate_gb(self.n_sites),
            "status": ADJACENCY_TRACK_LABEL,
        }


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------


def build_fermi_hubbard_chain(
    n_sites: int,
    hopping_t: float,
    interaction_u: float,
    chemical_potential: float = 0.0,
    periodic: bool = False,
) -> FermiHubbardLattice:
    """Build a 1D FH model wrapped in FermiHubbardLattice for geometry-aware routing."""
    return FermiHubbardLattice(
        geometry=chain_1d_geometry(n_sites, periodic=periodic),
        hopping_t=hopping_t,
        interaction_u=interaction_u,
        chemical_potential=chemical_potential,
    )


def build_fermi_hubbard_square_2d(
    n_rows: int,
    n_cols: int,
    hopping_t: float,
    interaction_u: float,
    chemical_potential: float = 0.0,
    periodic: bool = False,
) -> FermiHubbardLattice:
    """Build a 2D square-lattice FH model.

    EPISTEMIC STATUS — ADJACENT ENGINEERING LANE (NON-HARDGATE).

    Parameters
    ----------
    n_rows, n_cols:
        Lattice dimensions (both ≥ 2).  Total sites = n_rows * n_cols.
    hopping_t:
        Nearest-neighbour hopping amplitude (uniform isotropic).
    interaction_u:
        On-site Hubbard interaction strength.
    chemical_potential:
        Global chemical potential (default 0 = half-filling tuned externally).
    periodic:
        Apply periodic boundary conditions.
    """
    return FermiHubbardLattice(
        geometry=square_2d_geometry(n_rows, n_cols, periodic=periodic),
        hopping_t=hopping_t,
        interaction_u=interaction_u,
        chemical_potential=chemical_potential,
    )


def build_fermi_hubbard_cubic_3d(
    n_x: int,
    n_y: int,
    n_z: int,
    hopping_t: float,
    interaction_u: float,
    chemical_potential: float = 0.0,
    periodic: bool = False,
) -> FermiHubbardLattice:
    """Build a 3D cubic-lattice FH model (memory-bounded).

    EPISTEMIC STATUS — ADJACENT ENGINEERING LANE (NON-HARDGATE).

    ⚠ Memory warning: for n_x·n_y·n_z > 12 sites, use the XDiag sparse
    engine.  The UM exact-dense engine is infeasible above ~12 sites.
    """
    return FermiHubbardLattice(
        geometry=cubic_3d_geometry(n_x, n_y, n_z, periodic=periodic),
        hopping_t=hopping_t,
        interaction_u=interaction_u,
        chemical_potential=chemical_potential,
    )


def build_fermi_hubbard_braid_kk(
    hopping_t: float = 1.0,
    interaction_u: float | None = None,
    chemical_potential: float = 0.0,
) -> FermiHubbardLattice:
    """Build the KK-natural (5,7) braid-ring FH model.

    Uses KK_U_OVER_T ≈ 78.23 if interaction_u is not supplied.
    This places the system deep in the Mott insulating phase.

    EPISTEMIC STATUS — ADJACENT ENGINEERING LANE (NON-HARDGATE).
    """
    from .um_kk_fh_bridge import KK_U_OVER_T  # lazy import to avoid circularity

    if interaction_u is None:
        interaction_u = KK_U_OVER_T * hopping_t
    return FermiHubbardLattice(
        geometry=braid_kk_geometry(periodic=True),
        hopping_t=hopping_t,
        interaction_u=interaction_u,
        chemical_potential=chemical_potential,
    )


# ---------------------------------------------------------------------------
# Memory estimation helpers
# ---------------------------------------------------------------------------


def hilbert_space_dimension(n_sites: int) -> int:
    """Full Hilbert space dimension for n_sites spinful fermionic sites: 2^(2·n_sites)."""
    return 1 << (2 * n_sites)


def memory_estimate_bytes(n_sites: int, dtype_bytes: int = 16) -> int:
    """Estimate dense Hamiltonian memory in bytes.

    Parameters
    ----------
    n_sites:
        Number of spinful lattice sites.
    dtype_bytes:
        Bytes per element (default 16 = complex128).

    Returns
    -------
    Estimated memory in bytes for storing the full dense Hamiltonian matrix.
    """
    dim = hilbert_space_dimension(n_sites)
    return dtype_bytes * dim * dim


def memory_estimate_gb(n_sites: int) -> float:
    """Estimate dense Hamiltonian memory in gigabytes."""
    return memory_estimate_bytes(n_sites) / (1024 ** 3)
