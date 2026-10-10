# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Braided Qubit Ansatz Studio — Product 31.

Phase-0 "small-qubit ansatz" tool for article-354 direction #4: extends
`src/quantum/kk_vqe.py`'s existing hardware-efficient ansatz (Ry layers +
CNOT ladder) into an explicit, exportable gate list for an eight-qubit
braided-lattice instance, and validates that the gate list reproduces the
same unitary as `kk_vqe.ansatz_circuit()` via an independent, from-scratch
statevector simulator — before anyone submits a job to real quantum
hardware.

Epistemic status: this product runs no real quantum hardware and claims no
hardware result. It is the simulation-validated circuit-export step that
Phase 1 (an actual cloud quantum-hardware run) and Phase 2 (comparison
against XDiag exact diagonalization) would build on.
"""

from .circuit_export import (
    Gate,
    BraidedAnsatzCircuit,
    build_braided_ansatz_circuit,
    simulate_circuit,
    validate_against_kk_vqe,
)

__all__ = [
    "Gate",
    "BraidedAnsatzCircuit",
    "build_braided_ansatz_circuit",
    "simulate_circuit",
    "validate_against_kk_vqe",
]

__version__ = "1.0.0"
