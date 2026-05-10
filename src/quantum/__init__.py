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
"""
from .kk_vqe import (
    kk_hamiltonian,
    ansatz_circuit,
    vqe_kk,
    VQEResult,
)

__all__ = [
    "kk_hamiltonian",
    "ansatz_circuit",
    "vqe_kk",
    "VQEResult",
]
