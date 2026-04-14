# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""src/materials — Pillar 26: Materials Science."""
from .condensed import (
    band_gap_phi, fermi_phi_level, phonon_phi_scattering,
    electron_phi_mobility, thermal_phi_conductivity, magnetic_phi_ordering,
    crystal_phi_defects, grain_boundary_phi, dislocation_phi_density,
    phase_transition_phi,
)
from .semiconductors import (
    carrier_phi_density, dopant_phi_concentration, pn_junction_phi,
    transistor_phi_gain, semiconductor_phi_noise, solar_cell_phi_efficiency,
    led_phi_efficiency, diode_phi_current, quantum_phi_dot,
    semiconductor_phi_bandgap,
)
from .metamaterials import (
    negative_phi_index, metamaterial_phi_resonance, photonic_phi_bandgap,
    acoustic_phi_metamaterial, cloaking_phi_efficiency, epsilon_phi_near_zero,
    hyperbolic_phi_dispersion, nonlinear_phi_metamaterial,
    topological_phi_insulator, phi_plasmon_resonance,
)

__all__ = [
    "band_gap_phi", "fermi_phi_level", "phonon_phi_scattering",
    "electron_phi_mobility", "thermal_phi_conductivity", "magnetic_phi_ordering",
    "crystal_phi_defects", "grain_boundary_phi", "dislocation_phi_density",
    "phase_transition_phi",
    "carrier_phi_density", "dopant_phi_concentration", "pn_junction_phi",
    "transistor_phi_gain", "semiconductor_phi_noise", "solar_cell_phi_efficiency",
    "led_phi_efficiency", "diode_phi_current", "quantum_phi_dot",
    "semiconductor_phi_bandgap",
    "negative_phi_index", "metamaterial_phi_resonance", "photonic_phi_bandgap",
    "acoustic_phi_metamaterial", "cloaking_phi_efficiency", "epsilon_phi_near_zero",
    "hyperbolic_phi_dispersion", "nonlinear_phi_metamaterial",
    "topological_phi_insulator", "phi_plasmon_resonance",
]
