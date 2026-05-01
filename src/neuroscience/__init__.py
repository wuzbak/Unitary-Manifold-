# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""src/neuroscience — Pillar 20: Neuroscience & Brain Dynamics."""

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}

from .neurons import (
    action_potential_threshold, spike_frequency, refractory_period,
    membrane_phi_potential, neural_noise_floor, adaptation_current,
    hodgkin_huxley_phi, axon_phi_velocity, synaptic_phi_weight, neural_phi_gain,
)
from .synaptic import (
    synaptic_transmission_phi, neurotransmitter_decay, receptor_saturation_phi,
    long_term_potentiation_phi, long_term_depression_phi, dopamine_phi_modulation,
    serotonin_phi, glutamate_snr, gaba_inhibition_phi, synaptic_phi_delay,
)
from .cognition import (
    working_memory_phi, attention_phi_focus, cognitive_load_phi,
    decision_entropy_phi, learning_rate_phi, memory_consolidation_phi,
    neural_phi_coherence, arousal_phi_modulation, cognitive_flexibility_phi,
    information_integration_phi,
)

__all__ = [
    "action_potential_threshold", "spike_frequency", "refractory_period",
    "membrane_phi_potential", "neural_noise_floor", "adaptation_current",
    "hodgkin_huxley_phi", "axon_phi_velocity", "synaptic_phi_weight",
    "neural_phi_gain",
    "synaptic_transmission_phi", "neurotransmitter_decay",
    "receptor_saturation_phi", "long_term_potentiation_phi",
    "long_term_depression_phi", "dopamine_phi_modulation", "serotonin_phi",
    "glutamate_snr", "gaba_inhibition_phi", "synaptic_phi_delay",
    "working_memory_phi", "attention_phi_focus", "cognitive_load_phi",
    "decision_entropy_phi", "learning_rate_phi", "memory_consolidation_phi",
    "neural_phi_coherence", "arousal_phi_modulation",
    "cognitive_flexibility_phi", "information_integration_phi",
]
