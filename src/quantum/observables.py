# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/observables.py
==========================
Spin/charge observables for Fermi–Hubbard benchmark reporting.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .fermi_hubbard import FermionTerm, FermiHubbardHamiltonian
from .fermion_mapping import MappingName, PauliTerm, fermion_terms_to_qubit_terms, pauli_terms_to_matrix


@dataclass(frozen=True)
class ObservableSnapshot:
    charge_density: np.ndarray
    spin_density: np.ndarray
    double_occupancy: np.ndarray
    staggered_magnetization: float


def expectation_pauli_sum(state: np.ndarray, terms: list[PauliTerm], n_qubits: int) -> complex:
    h = pauli_terms_to_matrix(terms, n_qubits=n_qubits)
    return np.vdot(state, h @ state)


def _number_operator(mode: int) -> FermionTerm:
    return FermionTerm(1.0, ((mode, True), (mode, False)))


def _double_occupancy_operator(up_mode: int, dn_mode: int) -> FermionTerm:
    return FermionTerm(1.0, ((up_mode, True), (up_mode, False), (dn_mode, True), (dn_mode, False)))


def snapshot_observables(
    state: np.ndarray,
    model: FermiHubbardHamiltonian,
    mapping: MappingName = "jw",
) -> ObservableSnapshot:
    charge = np.zeros(model.n_sites, dtype=float)
    spin = np.zeros(model.n_sites, dtype=float)
    doublon = np.zeros(model.n_sites, dtype=float)

    for i in range(model.n_sites):
        up = model.mode_index(i, 0)
        dn = model.mode_index(i, 1)

        n_up = expectation_pauli_sum(
            state,
            fermion_terms_to_qubit_terms([_number_operator(up)], model.n_modes, mapping=mapping),
            model.n_modes,
        ).real
        n_dn = expectation_pauli_sum(
            state,
            fermion_terms_to_qubit_terms([_number_operator(dn)], model.n_modes, mapping=mapping),
            model.n_modes,
        ).real
        n_d = expectation_pauli_sum(
            state,
            fermion_terms_to_qubit_terms([_double_occupancy_operator(up, dn)], model.n_modes, mapping=mapping),
            model.n_modes,
        ).real

        charge[i] = n_up + n_dn
        spin[i] = n_up - n_dn
        doublon[i] = n_d

    # Antiferromagnetic order parameter: <Σ_i (-1)^i S^z_i> / N
    staggered = float(np.mean(((-1) ** np.arange(model.n_sites)) * spin))
    return ObservableSnapshot(
        charge_density=charge,
        spin_density=spin,
        double_occupancy=doublon,
        staggered_magnetization=staggered,
    )
