# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/fermi_hubbard.py
=============================
Dedicated adjacent-research Fermi–Hubbard model layer.

EPISTEMIC STATUS — PHENOMENOLOGICAL BRIDGE / ADJACENT RESEARCH
----------------------------------------------------------------
This module is an engineering research track adjacent to the Unitary Manifold.
It is not a Category-1 5D-geometry derivation and does not alter UM hardgates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class FermionTerm:
    """Normal-ordered fermionic operator term.

    Operators are encoded as a left-to-right product tuple of
    ``(mode_index, is_creation)`` entries.
    """

    coefficient: complex
    operators: tuple[tuple[int, bool], ...]


@dataclass(frozen=True)
class FermiHubbardHamiltonian:
    """1D spinful Fermi–Hubbard Hamiltonian specification."""

    n_sites: int
    hopping_t: float
    interaction_u: float
    chemical_potential: float = 0.0
    periodic: bool = False

    def __post_init__(self) -> None:
        if self.n_sites < 2:
            raise ValueError("n_sites must be >= 2 for a lattice model")
        if self.hopping_t < 0:
            raise ValueError("hopping_t must be >= 0")
        if self.interaction_u < 0:
            raise ValueError("interaction_u must be >= 0")

    @property
    def n_modes(self) -> int:
        return 2 * self.n_sites

    def mode_index(self, site: int, spin: int) -> int:
        """Return orbital index for site and spin (0=up, 1=down)."""
        if not 0 <= site < self.n_sites:
            raise ValueError("site out of bounds")
        if spin not in (0, 1):
            raise ValueError("spin must be 0 (up) or 1 (down)")
        return 2 * site + spin

    def hopping_edges(self) -> list[tuple[int, int]]:
        """Nearest-neighbour edges for 1D chain."""
        edges = [(i, i + 1) for i in range(self.n_sites - 1)]
        if self.periodic:
            edges.append((self.n_sites - 1, 0))
        return edges

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
                    terms.append(FermionTerm(-self.chemical_potential, ((m, True), (m, False))))

        return terms


def build_fermi_hubbard_1d(
    n_sites: int,
    hopping_t: float,
    interaction_u: float,
    chemical_potential: float = 0.0,
    periodic: bool = False,
) -> FermiHubbardHamiltonian:
    """Factory for the adjacent-track 1D Fermi–Hubbard Hamiltonian."""
    return FermiHubbardHamiltonian(
        n_sites=n_sites,
        hopping_t=hopping_t,
        interaction_u=interaction_u,
        chemical_potential=chemical_potential,
        periodic=periodic,
    )


def iter_mode_number_terms(model: FermiHubbardHamiltonian) -> Iterable[FermionTerm]:
    """Yield n_m terms for all modes."""
    for mode in range(model.n_modes):
        yield FermionTerm(1.0, ((mode, True), (mode, False)))
