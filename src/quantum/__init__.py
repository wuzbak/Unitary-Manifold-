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
xdiag_bridge
    Adjacent UM↔XDiag compatibility bridge for schema contracts, bidirectional
    artifact conversion, parity gates, and deterministic routing.
fh_solver
    Adjacent-track exact diagonalization (ED) solver for the 1D Fermi–Hubbard
    model with sector decomposition and Bethe Ansatz validation.
um_kk_fh_bridge
    Formal adjacent-track bridge mapping UM KK braid constants (5, 7, 74) to
    Fermi–Hubbard parameters; confirms the Mott insulating phase at U/t ≈ 78.
"""
from .fh_solver import (
    FHSectorResult,
    FHEdResult,
    solve_sector,
    exact_diagonalize,
    BETHE_ANSATZ_2SITE,
    validate_bethe_ansatz,
    um_kk_natural_parameters,
)
from .um_kk_fh_bridge import (
    KKFHBridgeResult,
    kk_to_fh_parameters,
    run_kk_fh_bridge,
    mott_insulator_verdict,
    BRIDGE_STATUS,
    KK_U_OVER_T,
    KK_PHASE,
)
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
from .xdiag_bridge import (
    XDIAG_UM_SCHEMA_VERSION,
    CouplingSpec,
    EvolutionSpec,
    LatticeSpec,
    ObservableSpec,
    ParityDelta,
    ParityReport,
    ParityTolerance,
    ProvenanceSpec,
    RoutingDecision,
    RoutingThresholds,
    SectorSpec,
    XDiagBridgeArtifact,
    XDiagBridgeSpec,
    XDiagExportPayload,
    assert_parity,
    build_xdiag_bridge_spec,
    choose_route,
    export_um_to_xdiag,
    ingest_xdiag_to_um_artifact,
    parity_report,
    save_bridge_artifact,
    spec_from_dict,
)

__all__ = [
    "kk_hamiltonian",
    "ansatz_circuit",
    "vqe_kk",
    "VQEResult",
    "FHSectorResult",
    "FHEdResult",
    "solve_sector",
    "exact_diagonalize",
    "BETHE_ANSATZ_2SITE",
    "validate_bethe_ansatz",
    "um_kk_natural_parameters",
    "KKFHBridgeResult",
    "kk_to_fh_parameters",
    "run_kk_fh_bridge",
    "mott_insulator_verdict",
    "BRIDGE_STATUS",
    "KK_U_OVER_T",
    "KK_PHASE",
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
    "XDIAG_UM_SCHEMA_VERSION",
    "LatticeSpec",
    "CouplingSpec",
    "SectorSpec",
    "ObservableSpec",
    "EvolutionSpec",
    "ProvenanceSpec",
    "XDiagBridgeSpec",
    "build_xdiag_bridge_spec",
    "spec_from_dict",
    "XDiagExportPayload",
    "XDiagBridgeArtifact",
    "export_um_to_xdiag",
    "ingest_xdiag_to_um_artifact",
    "save_bridge_artifact",
    "ParityTolerance",
    "ParityDelta",
    "ParityReport",
    "parity_report",
    "assert_parity",
    "RoutingThresholds",
    "RoutingDecision",
    "choose_route",
]
