# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_neuroscience.py
===========================
Unit tests for the src/neuroscience package — Pillar 20: Neuroscience.

Covers:
  - neurons.py  : action_potential_threshold, spike_frequency, refractory_period,
                   membrane_phi_potential, neural_noise_floor, adaptation_current,
                   hodgkin_huxley_phi, axon_phi_velocity, synaptic_phi_weight,
                   neural_phi_gain
  - synaptic.py : synaptic_transmission_phi, neurotransmitter_decay,
                   receptor_saturation_phi, long_term_potentiation_phi,
                   long_term_depression_phi, dopamine_phi_modulation,
                   serotonin_phi, glutamate_snr, gaba_inhibition_phi,
                   synaptic_phi_delay
  - cognition.py: working_memory_phi, attention_phi_focus, cognitive_load_phi,
                   decision_entropy_phi, learning_rate_phi,
                   memory_consolidation_phi, neural_phi_coherence,
                   arousal_phi_modulation, cognitive_flexibility_phi,
                   information_integration_phi
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import math
import numpy as np
import pytest

from src.neuroscience.neurons import (
    action_potential_threshold, spike_frequency, refractory_period,
    membrane_phi_potential, neural_noise_floor, adaptation_current,
    hodgkin_huxley_phi, axon_phi_velocity, synaptic_phi_weight, neural_phi_gain,
)
from src.neuroscience.synaptic import (
    synaptic_transmission_phi, neurotransmitter_decay, receptor_saturation_phi,
    long_term_potentiation_phi, long_term_depression_phi, dopamine_phi_modulation,
    serotonin_phi, glutamate_snr, gaba_inhibition_phi, synaptic_phi_delay,
)
from src.neuroscience.cognition import (
    working_memory_phi, attention_phi_focus, cognitive_load_phi,
    decision_entropy_phi, learning_rate_phi, memory_consolidation_phi,
    neural_phi_coherence, arousal_phi_modulation, cognitive_flexibility_phi,
    information_integration_phi,
)


# ---------------------------------------------------------------------------
# neurons.py
# ---------------------------------------------------------------------------

class TestActionPotentialThreshold:
    def test_basic(self):
        assert action_potential_threshold(0.0, 1.0) == pytest.approx(1.0)

    def test_zero_noise(self):
        assert action_potential_threshold(2.0, 0.0) == pytest.approx(2.0)

    def test_k_B_scaling(self):
        result = action_potential_threshold(0.0, 1.0, k_B=2.0)
        assert result == pytest.approx(2.0)

    def test_negative_B_raises(self):
        with pytest.raises(ValueError):
            action_potential_threshold(0.0, -1.0)

    def test_zero_k_B_raises(self):
        with pytest.raises(ValueError):
            action_potential_threshold(0.0, 1.0, k_B=0.0)


class TestSpikeFrequency:
    def test_above_threshold(self):
        f = spike_frequency(2.0, 1.0, 0.5)
        assert f == pytest.approx(2.0)

    def test_below_threshold_zero(self):
        assert spike_frequency(0.5, 1.0, 0.5) == pytest.approx(0.0)

    def test_tau_raises(self):
        with pytest.raises(ValueError):
            spike_frequency(2.0, 1.0, 0.0)


class TestRefractoryPeriod:
    def test_no_noise(self):
        assert refractory_period(1.0, 0.0) == pytest.approx(1.0)

    def test_noise_extends(self):
        assert refractory_period(1.0, 0.5) == pytest.approx(1.5)

    def test_raises_negative_tau(self):
        with pytest.raises(ValueError):
            refractory_period(-1.0, 0.0)

    def test_raises_negative_noise(self):
        with pytest.raises(ValueError):
            refractory_period(1.0, -0.1)


class TestMembranePhiPotential:
    def test_basic(self):
        assert membrane_phi_potential(-70.0, 1.0, 10.0) == pytest.approx(-60.0)

    def test_zero_current(self):
        assert membrane_phi_potential(-70.0, 0.0, 10.0) == pytest.approx(-70.0)

    def test_raises_zero_R(self):
        with pytest.raises(ValueError):
            membrane_phi_potential(-70.0, 1.0, 0.0)


class TestNeuralNoiseFloor:
    def test_positive(self):
        sigma = neural_noise_floor(kT=1e-20, C_mem=1e-12)
        assert sigma > 0.0

    def test_formula(self):
        sigma = neural_noise_floor(kT=4.0, C_mem=1.0)
        assert sigma == pytest.approx(2.0)

    def test_raises_kT_zero(self):
        with pytest.raises(ValueError):
            neural_noise_floor(0.0, 1e-12)


class TestAdaptationCurrent:
    def test_t_zero(self):
        assert adaptation_current(2.0, 5.0, 0.0) == pytest.approx(2.0)

    def test_decay(self):
        v = adaptation_current(1.0, 1.0, 1.0)
        assert v == pytest.approx(math.exp(-1.0))

    def test_raises_negative_tau(self):
        with pytest.raises(ValueError):
            adaptation_current(1.0, -1.0, 0.0)


class TestHodgkinHuxleyPhi:
    def test_at_rest(self):
        # At rest potentials the current should be near zero
        I = hodgkin_huxley_phi(V=-65.0, V_Na=50.0, V_K=-77.0,
                                g_Na=120.0, g_K=36.0, g_L=0.3, V_L=-54.0)
        assert isinstance(I, float)

    def test_raises_negative_g(self):
        with pytest.raises(ValueError):
            hodgkin_huxley_phi(0.0, 50.0, -77.0, -1.0, 36.0, 0.3, -54.0)


class TestAxonPhiVelocity:
    def test_myelinated_faster(self):
        v_m = axon_phi_velocity(2e-6, myelinated=True)
        v_u = axon_phi_velocity(2e-6, myelinated=False)
        assert v_m > v_u

    def test_positive(self):
        assert axon_phi_velocity(1e-6) > 0.0

    def test_raises_zero_diameter(self):
        with pytest.raises(ValueError):
            axon_phi_velocity(0.0)


class TestSynapticPhiWeight:
    def test_basic(self):
        assert synaptic_phi_weight(1.0, 0.2, 0.0) == pytest.approx(1.2)

    def test_floored_at_zero(self):
        assert synaptic_phi_weight(1.0, 0.0, 2.0) == pytest.approx(0.0)

    def test_raises_negative_base(self):
        with pytest.raises(ValueError):
            synaptic_phi_weight(-0.1, 0.0, 0.0)


class TestNeuralPhiGain:
    def test_midpoint(self):
        v = neural_phi_gain(1.0, 1.0, 1.0)
        assert v == pytest.approx(0.5)

    def test_range(self):
        for phi in [-5.0, 0.0, 5.0]:
            v = neural_phi_gain(phi, 0.0, 1.0)
            assert 0.0 < v < 1.0

    def test_raises_zero_slope(self):
        with pytest.raises(ValueError):
            neural_phi_gain(1.0, 0.0, 0.0)


# ---------------------------------------------------------------------------
# synaptic.py
# ---------------------------------------------------------------------------

class TestSynapticTransmissionPhi:
    def test_basic(self):
        assert synaptic_transmission_phi(1.0, 10.0, 0.0) == pytest.approx(10.0)

    def test_full_saturation(self):
        assert synaptic_transmission_phi(1.0, 10.0, 1.0) == pytest.approx(0.0)

    def test_raises_negative_q(self):
        with pytest.raises(ValueError):
            synaptic_transmission_phi(-1.0, 10.0, 0.0)

    def test_raises_bad_saturation(self):
        with pytest.raises(ValueError):
            synaptic_transmission_phi(1.0, 10.0, 1.5)


class TestNeurotransmitterDecay:
    def test_t_zero(self):
        assert neurotransmitter_decay(5.0, 0.0, 1.0) == pytest.approx(5.0)

    def test_decay(self):
        v = neurotransmitter_decay(1.0, 1.0, 1.0)
        assert v == pytest.approx(math.exp(-1.0))

    def test_raises_negative_NT(self):
        with pytest.raises(ValueError):
            neurotransmitter_decay(-1.0, 0.0, 1.0)


class TestReceptorSaturationPhi:
    def test_half_saturation(self):
        assert receptor_saturation_phi(1.0, 1.0) == pytest.approx(0.5)

    def test_zero_NT(self):
        assert receptor_saturation_phi(0.0, 1.0) == pytest.approx(0.0)

    def test_raises_zero_Kd(self):
        with pytest.raises(ValueError):
            receptor_saturation_phi(1.0, 0.0)


class TestLongTermPotentiationPhi:
    def test_positive_ltp(self):
        w = long_term_potentiation_phi(1.0, 0.5, 0.1)
        assert w == pytest.approx(1.05)

    def test_floored(self):
        w = long_term_potentiation_phi(0.0, -5.0, 0.1)
        assert w == pytest.approx(0.0)

    def test_raises_eta_zero(self):
        with pytest.raises(ValueError):
            long_term_potentiation_phi(1.0, 0.5, 0.0)


class TestLongTermDepressionPhi:
    def test_basic(self):
        assert long_term_depression_phi(1.0, 0.2) == pytest.approx(0.8)

    def test_full_depression(self):
        assert long_term_depression_phi(1.0, 1.0) == pytest.approx(0.0)

    def test_raises_bad_rate(self):
        with pytest.raises(ValueError):
            long_term_depression_phi(1.0, 1.5)


class TestDopaminePhiModulation:
    def test_zero_dopamine(self):
        assert dopamine_phi_modulation(1.0, 0.0) == pytest.approx(1.0)

    def test_max_dopamine(self):
        v = dopamine_phi_modulation(1.0, 1.0, d1_gain=1.0)
        assert v == pytest.approx(2.0)

    def test_raises_bad_level(self):
        with pytest.raises(ValueError):
            dopamine_phi_modulation(1.0, 1.5)


class TestSerotoninPhi:
    def test_neutral(self):
        assert serotonin_phi(1.0, 0.5) == pytest.approx(1.0)

    def test_high_serotonin(self):
        assert serotonin_phi(1.0, 1.0, 0.5) > 1.0

    def test_raises_bad_level(self):
        with pytest.raises(ValueError):
            serotonin_phi(1.0, -0.1)


class TestGlutamateSNR:
    def test_positive(self):
        assert glutamate_snr(2.0, 1.0) > 0.0

    def test_raises_negative_J(self):
        with pytest.raises(ValueError):
            glutamate_snr(-1.0, 1.0)


class TestGabaInhibitionPhi:
    def test_full_inhibition(self):
        assert gaba_inhibition_phi(1.0, 1.0) == pytest.approx(0.0)

    def test_no_inhibition(self):
        assert gaba_inhibition_phi(1.0, 0.0) == pytest.approx(1.0)

    def test_raises_bad_fraction(self):
        with pytest.raises(ValueError):
            gaba_inhibition_phi(1.0, 1.5)


class TestSynapticPhiDelay:
    def test_basic(self):
        assert synaptic_phi_delay(0.1, 10.0) == pytest.approx(0.01)

    def test_raises_zero_velocity(self):
        with pytest.raises(ValueError):
            synaptic_phi_delay(0.1, 0.0)


# ---------------------------------------------------------------------------
# cognition.py
# ---------------------------------------------------------------------------

class TestWorkingMemoryPhi:
    def test_basic(self):
        assert working_memory_phi(10.0, 0.0) > 0.0

    def test_raises_negative_phi(self):
        with pytest.raises(ValueError):
            working_memory_phi(-1.0, 0.0)

    def test_raises_negative_noise(self):
        with pytest.raises(ValueError):
            working_memory_phi(1.0, -0.1)


class TestAttentionPhiFocus:
    def test_full_focus(self):
        assert attention_phi_focus(1.0, 1.0) == pytest.approx(1.0)

    def test_half_focus(self):
        assert attention_phi_focus(0.5, 1.0) == pytest.approx(0.5)

    def test_clipped(self):
        assert attention_phi_focus(2.0, 1.0) == pytest.approx(1.0)

    def test_raises_zero_total(self):
        with pytest.raises(ValueError):
            attention_phi_focus(1.0, 0.0)


class TestCognitiveLoadPhi:
    def test_underload(self):
        assert cognitive_load_phi(2, 1.0, 10.0) == pytest.approx(0.2)

    def test_overload(self):
        assert cognitive_load_phi(20, 1.0, 10.0) > 1.0

    def test_raises_zero_capacity(self):
        with pytest.raises(ValueError):
            cognitive_load_phi(1, 1.0, 0.0)


class TestDecisionEntropyPhi:
    def test_uniform_two(self):
        H = decision_entropy_phi([0.5, 0.5])
        assert H == pytest.approx(math.log(2.0), rel=1e-3)

    def test_certain(self):
        H = decision_entropy_phi([1.0, 0.0, 0.0])
        assert H == pytest.approx(0.0, abs=1e-6)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            decision_entropy_phi([-0.1, 1.1])


class TestLearningRatePhi:
    def test_positive_error(self):
        assert learning_rate_phi(2.0, 1.0, 0.5) == pytest.approx(0.5)

    def test_zero_error(self):
        assert learning_rate_phi(1.0, 1.0) == pytest.approx(0.0)

    def test_raises_bad_alpha(self):
        with pytest.raises(ValueError):
            learning_rate_phi(1.0, 0.0, 0.0)


class TestMemoryConsolidationPhi:
    def test_t_zero(self):
        assert memory_consolidation_phi(1.0, 0.0, 1.0) == pytest.approx(0.0)

    def test_long_time(self):
        v = memory_consolidation_phi(1.0, 1000.0, 1.0)
        assert v == pytest.approx(1.0, abs=1e-6)

    def test_raises_negative_tau(self):
        with pytest.raises(ValueError):
            memory_consolidation_phi(1.0, 1.0, 0.0)


class TestNeuralPhiCoherence:
    def test_uniform_zero_coherence(self):
        v = neural_phi_coherence([1.0, 1.0, 1.0])
        assert v == pytest.approx(0.0, abs=1e-6)

    def test_positive_result(self):
        v = neural_phi_coherence([1.0, 2.0, 3.0])
        assert v > 0.0

    def test_raises_empty(self):
        with pytest.raises(ValueError):
            neural_phi_coherence([])


class TestArousalPhiModulation:
    def test_peak_optimal(self):
        # At peak_arousal, factor = 1
        v = arousal_phi_modulation(1.0, 0.5, 0.5)
        assert v == pytest.approx(1.0)

    def test_extremes_lower(self):
        v = arousal_phi_modulation(1.0, 0.0, 0.5)
        assert v < 1.0

    def test_raises_bad_arousal(self):
        with pytest.raises(ValueError):
            arousal_phi_modulation(1.0, 1.5)


class TestCognitiveFlexibilityPhi:
    def test_no_switches(self):
        assert cognitive_flexibility_phi(0, 1.0, 5.0) == pytest.approx(5.0)

    def test_floored(self):
        assert cognitive_flexibility_phi(10, 1.0, 5.0) == pytest.approx(0.0)

    def test_raises_negative_n(self):
        with pytest.raises(ValueError):
            cognitive_flexibility_phi(-1, 1.0, 5.0)


class TestInformationIntegrationPhi:
    def test_positive_integration(self):
        assert information_integration_phi(5.0, 3.0) == pytest.approx(2.0)

    def test_zero_integration(self):
        assert information_integration_phi(3.0, 3.0) == pytest.approx(0.0)

    def test_negative_integration(self):
        assert information_integration_phi(1.0, 3.0) == pytest.approx(-2.0)
