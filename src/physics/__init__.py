# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/physics
===========
Cross-cutting physics modules for the Unitary Manifold framework.

Modules
-------
lattice_dynamics    — Coherence-volume scaling, collective Gamow factor,
                      phonon-radion bridge, and B_μ time-arrow energy routing.

Public API
----------
Constants
~~~~~~~~~
N_W_DEFAULT             Winding number n_w = 5 (canonical)
K_CS_DEFAULT            CS resonance constant k_cs = 74 = 5² + 7²
C_S_DEFAULT             Braided sound speed c_s = 12/37
ALPHA_FS                Fine-structure constant α = 1/137.036
G_THRESHOLD_DEFAULT     Default Gamow ignition threshold G_coll > 10⁻²⁰
X_BRAID_CANONICAL       Canonical optimal loading x = 7/8 = 0.875

Functions
~~~~~~~~~
phi_effective_collective(N, phi_local, ...)
    Collective radion field φ_eff = φ_local × (1 + N_eff × N).

ignition_N(phi_local, eta, G_threshold, ...)
    [STUB — implementation withheld per AxiomZero dual-use policy v1.0;
    see DUAL_USE_NOTICE.md]  Minimum coherence-domain size N for Gamow
    factor above G_threshold.  Raises NotImplementedError in this repo.

braid_resonance_loading(n_w, k_cs, c_s)
    D/Pd loading ratios at primary and canonical (5,7) braid resonance.

lattice_coherence_gain(N_coherence, phi_local, ...)
    [STUB — implementation withheld per AxiomZero dual-use policy v1.0;
    see DUAL_USE_NOTICE.md]  Full coherence-volume analysis including
    G_collective and ignition condition.  Raises NotImplementedError in
    this repo.

phonon_radion_bridge(D_Pd_loading, debye_temp_K, lattice_temp_K, ...)
    Model the Pd-D lattice as a phonon-driven radion pump.  Returns the
    Bose-Einstein phonon occupation, braid commensurability factor, and
    local radion field enhancement at a loaded D-site.

bmu_time_arrow_lock(B_site, phi_site, Q_MeV, ...)
    Mathematical proof that B_μ field irreversibility forces fusion energy
    into lattice phonons.  Returns quadratic branching fractions f_phonon
    and f_gamma, and the human-readable proof statement.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
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

from src.physics.lattice_dynamics import (
    # Constants
    N_W_DEFAULT,
    K_CS_DEFAULT,
    C_S_DEFAULT,
    ALPHA_FS,
    G_THRESHOLD_DEFAULT,
    X_BRAID_CANONICAL,
    # Functions
    phi_effective_collective,
    ignition_N,
    braid_resonance_loading,
    lattice_coherence_gain,
    phonon_radion_bridge,
    bmu_time_arrow_lock,
)

__all__ = [
    # Constants
    "N_W_DEFAULT",
    "K_CS_DEFAULT",
    "C_S_DEFAULT",
    "ALPHA_FS",
    "G_THRESHOLD_DEFAULT",
    "X_BRAID_CANONICAL",
    # Functions
    "phi_effective_collective",
    "ignition_N",
    "braid_resonance_loading",
    "lattice_coherence_gain",
    "phonon_radion_bridge",
    "bmu_time_arrow_lock",
]
