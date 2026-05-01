# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
omega — The Omega Synthesis: Universal Mechanics Engine (Pillar Ω)

The capstone synthesis of the Unitary Manifold. 98 pillars unified into a
single, queryable engine that computes any observable from first principles.

Quick start::

    from omega.omega_synthesis import UniversalEngine

    engine = UniversalEngine()
    report = engine.compute_all()

    print(f"n_s  = {report.cosmology.n_s:.4f}")   # 0.9635
    print(f"β    = {report.cosmology.beta_57_deg:.3f}°")  # 0.331°
    print(f"Ξ_c  = {float(report.consciousness.xi_c):.6f}")  # 0.472972...

Implementation & Synthesis: GitHub Copilot (AI)
"""

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}


from .omega_synthesis import (
    UniversalEngine,
    OmegaReport,
    CosmologyReport,
    ParticlePhysicsReport,
    GeometryReport,
    ConsciousnessReport,
    HILSReport,
    FalsifiablePrediction,
    # Seed constants — the five generators
    N_W,
    N_2,
    K_CS,
    C_S,
    XI_C,
)

__all__ = [
    "UniversalEngine",
    "OmegaReport",
    "CosmologyReport",
    "ParticlePhysicsReport",
    "GeometryReport",
    "ConsciousnessReport",
    "HILSReport",
    "FalsifiablePrediction",
    "N_W",
    "N_2",
    "K_CS",
    "C_S",
    "XI_C",
]
