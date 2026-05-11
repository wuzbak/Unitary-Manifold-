# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/__init__.py
=======================
Quantum-circuit layer of the Unitary Manifold.

Current modules
---------------
kk_vqe
    Variational Quantum Eigensolver formulation of the Kaluza–Klein mass
    eigenvalue problem on the compact S¹ dimension with (5,7,74) braid
    corrections.
fermi_hubbard
    Adjacent-track Fermi–Hubbard model and mappings (JW/BK), execution,
    observables, and benchmark utilities.
"""
from .kk_vqe import (
    kk_hamiltonian,
    ansatz_circuit,
    vqe_kk,
    VQEResult,
)
from .fermi_hubbard import (
    FermionTerm,
    FermiHubbardHamiltonian,
    build_fermi_hubbard_1d,
)
from .fermion_mapping import (
    PauliTerm,
    fermion_terms_to_qubit_terms,
    pauli_terms_to_matrix,
)
from .execution import (
    ExecutionConfig,
    ExecutionResult,
    MockHardwareAdapter,
    RunManifest,
    run_time_evolution,
    save_run_artifact,
)
from .benchmarks import (
    TDVPReference,
    TDVPParityReport,
    ScalingCurve,
    ScalingPoint,
    build_scaling_curve,
    run_observable_benchmark,
    tdvp_parity_report,
)

__all__ = [
    "kk_hamiltonian",
    "ansatz_circuit",
    "vqe_kk",
    "VQEResult",
    "FermionTerm",
    "FermiHubbardHamiltonian",
    "build_fermi_hubbard_1d",
    "PauliTerm",
    "fermion_terms_to_qubit_terms",
    "pauli_terms_to_matrix",
    "ExecutionConfig",
    "ExecutionResult",
    "MockHardwareAdapter",
    "RunManifest",
    "run_time_evolution",
    "save_run_artifact",
    "TDVPReference",
    "TDVPParityReport",
    "ScalingCurve",
    "ScalingPoint",
    "build_scaling_curve",
    "run_observable_benchmark",
    "tdvp_parity_report",
]
