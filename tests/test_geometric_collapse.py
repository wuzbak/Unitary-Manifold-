# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
test_geometric_collapse.py — Test suite for Pillar 44: Geometric Wavefunction
Collapse (src/core/geometric_collapse.py).

~80 tests covering all public functions, Born rule derivation, decoherence
timescale, braided corrections, and measurement summary.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.geometric_collapse import (
    C_S_BRAIDED,
    K_CS_CANONICAL,
    N_W_CANONICAL,
    RHO_BRAIDED,
    RHO_CS_CORRECTION,
    born_rule_geometric,
    branch_collapse,
    collapse_fidelity,
    collapse_phase_transition,
    decoherence_timescale,
    geometric_born_correction,
    information_current_before_collapse,
    measurement_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_rho_braided(self):
        assert abs(RHO_BRAIDED - 35 / 37) < 1e-12

    def test_c_s_braided(self):
        assert abs(C_S_BRAIDED - 12 / 37) < 1e-12

    def test_rho_cs_product(self):
        expected = (35 / 37) * (12 / 37)
        assert abs(RHO_CS_CORRECTION - expected) < 1e-12


# ---------------------------------------------------------------------------
# born_rule_geometric
# ---------------------------------------------------------------------------

class TestBornRuleGeometric:
    def test_equal_amplitudes_uniform(self):
        amps = np.array([1.0, 1.0, 1.0, 1.0], dtype=complex)
        probs = born_rule_geometric(amps)
        assert np.allclose(probs, 0.25)

    def test_sums_to_one(self):
        amps = np.array([1.0, 2.0, 3.0], dtype=complex)
        probs = born_rule_geometric(amps)
        assert abs(probs.sum() - 1.0) < 1e-12

    def test_single_nonzero(self):
        amps = np.array([0.0, 1.0, 0.0], dtype=complex)
        probs = born_rule_geometric(amps)
        assert abs(probs[1] - 1.0) < 1e-12
        assert probs[0] == 0.0
        assert probs[2] == 0.0

    def test_complex_amplitudes(self):
        amps = np.array([1 + 1j, 0.0], dtype=complex)
        probs = born_rule_geometric(amps)
        assert abs(probs[0] - 1.0) < 1e-12

    def test_two_branch_equal(self):
        amps = np.array([1.0, 1.0]) / math.sqrt(2)
        probs = born_rule_geometric(amps)
        assert abs(probs[0] - 0.5) < 1e-12
        assert abs(probs[1] - 0.5) < 1e-12

    def test_two_branch_unequal(self):
        a = math.sqrt(0.3)
        b = math.sqrt(0.7)
        probs = born_rule_geometric(np.array([a, b]))
        assert abs(probs[0] - 0.3) < 1e-12
        assert abs(probs[1] - 0.7) < 1e-12

    def test_raises_empty(self):
        with pytest.raises(ValueError):
            born_rule_geometric(np.array([]))

    def test_raises_all_zero(self):
        with pytest.raises(ValueError):
            born_rule_geometric(np.array([0.0, 0.0]))

    def test_shape_preserved(self):
        amps = np.array([1.0, 2.0, 3.0, 4.0])
        probs = born_rule_geometric(amps)
        assert probs.shape == amps.shape

    def test_non_negative(self):
        amps = np.random.default_rng(42).standard_normal(5) + 0.01
        probs = born_rule_geometric(amps)
        assert np.all(probs >= 0.0)


# ---------------------------------------------------------------------------
# decoherence_timescale
# ---------------------------------------------------------------------------

class TestDecoherenceTimescale:
    def test_basic_formula(self):
        tau = decoherence_timescale(2.0, 1.0)
        assert abs(tau - 4.0) < 1e-12

    def test_formula_general(self):
        for phi_mean in [0.1, 1.0, 5.0]:
            for phi_spread in [0.1, 0.5, 2.0]:
                tau = decoherence_timescale(phi_mean, phi_spread)
                expected = phi_mean ** 2 / phi_spread
                assert abs(tau - expected) < 1e-12

    def test_larger_phi_means_longer_tau(self):
        tau1 = decoherence_timescale(1.0, 0.5)
        tau2 = decoherence_timescale(2.0, 0.5)
        assert tau2 > tau1

    def test_larger_spread_shorter_tau(self):
        tau1 = decoherence_timescale(1.0, 0.5)
        tau2 = decoherence_timescale(1.0, 2.0)
        assert tau2 < tau1

    def test_raises_zero_phi_mean(self):
        with pytest.raises(ValueError):
            decoherence_timescale(0.0, 1.0)

    def test_raises_negative_phi_mean(self):
        with pytest.raises(ValueError):
            decoherence_timescale(-1.0, 1.0)

    def test_raises_zero_phi_spread(self):
        with pytest.raises(ValueError):
            decoherence_timescale(1.0, 0.0)

    def test_positive(self):
        assert decoherence_timescale(1.0, 1.0) > 0.0


# ---------------------------------------------------------------------------
# collapse_phase_transition
# ---------------------------------------------------------------------------

class TestCollapsePhaseTransition:
    def test_collapsed_below_threshold(self):
        assert collapse_phase_transition(0.5, 1.0) is True

    def test_not_collapsed_above_threshold(self):
        assert collapse_phase_transition(2.0, 1.0) is False

    def test_exactly_at_threshold_not_collapsed(self):
        # phi < threshold required
        assert collapse_phase_transition(1.0, 1.0) is False

    def test_very_small_phi_collapsed(self):
        assert collapse_phase_transition(1e-10, 1.0) is True


# ---------------------------------------------------------------------------
# geometric_born_correction
# ---------------------------------------------------------------------------

class TestGeometricBornCorrection:
    def test_sums_to_one(self):
        probs = np.array([0.3, 0.7])
        corrected = geometric_born_correction(probs)
        assert abs(corrected.sum() - 1.0) < 1e-12

    def test_correction_pulls_toward_uniform(self):
        probs = np.array([0.9, 0.1])
        corrected = geometric_born_correction(probs)
        # Correction makes the distribution more uniform
        assert corrected[0] < probs[0]
        assert corrected[1] > probs[1]

    def test_uniform_input_unchanged(self):
        probs = np.array([0.25, 0.25, 0.25, 0.25])
        corrected = geometric_born_correction(probs)
        assert np.allclose(corrected, probs, atol=1e-12)

    def test_zero_weight_gives_born(self):
        probs = np.array([0.4, 0.6])
        corrected = geometric_born_correction(probs, rho=0.0, c_s=0.0)
        assert np.allclose(corrected, probs, atol=1e-12)

    def test_raises_empty(self):
        with pytest.raises(ValueError):
            geometric_born_correction(np.array([]))

    def test_raises_negative_prob(self):
        with pytest.raises(ValueError):
            geometric_born_correction(np.array([-0.1, 1.1]))

    def test_output_non_negative(self):
        probs = np.array([0.1, 0.4, 0.5])
        corrected = geometric_born_correction(probs)
        assert np.all(corrected >= 0.0)

    def test_canonical_rho_cs(self):
        """Test with canonical braided parameters."""
        probs = np.array([0.5, 0.5])
        corrected = geometric_born_correction(probs, RHO_BRAIDED, C_S_BRAIDED)
        assert abs(corrected.sum() - 1.0) < 1e-12


# ---------------------------------------------------------------------------
# information_current_before_collapse
# ---------------------------------------------------------------------------

class TestInformationCurrentBeforeCollapse:
    def test_formula(self):
        amps = np.array([1.0, 1.0]) / math.sqrt(2)
        phi = 2.0
        j0 = information_current_before_collapse(amps, phi)
        expected = phi ** 2 * np.abs(amps) ** 2
        assert np.allclose(j0, expected)

    def test_current_sums_to_phi_squared(self):
        amps = np.array([3.0, 4.0]) / 5.0  # normalised
        phi = 3.0
        j0 = information_current_before_collapse(amps, phi)
        assert abs(j0.sum() - phi ** 2) < 1e-10

    def test_scales_with_phi_squared(self):
        amps = np.array([1.0, 0.0])
        j1 = information_current_before_collapse(amps, 1.0)
        j2 = information_current_before_collapse(amps, 2.0)
        assert abs(j2[0] / j1[0] - 4.0) < 1e-12

    def test_raises_zero_phi(self):
        with pytest.raises(ValueError):
            information_current_before_collapse(np.array([1.0]), 0.0)


# ---------------------------------------------------------------------------
# branch_collapse
# ---------------------------------------------------------------------------

class TestBranchCollapse:
    def test_returns_tuple(self):
        amps = np.array([1.0, 0.0])
        result = branch_collapse(amps, 1.0, 0.5, np.random.default_rng(0))
        assert len(result) == 3

    def test_deterministic_collapse_to_branch_0(self):
        amps = np.array([1.0, 0.0])
        selected, probs, tau = branch_collapse(
            amps, 1.0, 0.5, np.random.default_rng(0)
        )
        assert selected == 0

    def test_probs_sum_to_one(self):
        amps = np.array([1.0, 1.0, 1.0]) / math.sqrt(3)
        _, probs, _ = branch_collapse(amps, 1.0, 0.5, np.random.default_rng(1))
        assert abs(probs.sum() - 1.0) < 1e-12

    def test_tau_dec_positive(self):
        amps = np.array([1.0, 0.0])
        _, _, tau = branch_collapse(amps, 2.0, 0.5, np.random.default_rng(2))
        assert tau > 0.0

    def test_selected_within_range(self):
        amps = np.array([1.0, 1.0, 1.0]) / math.sqrt(3)
        for seed in range(10):
            sel, _, _ = branch_collapse(amps, 1.0, 0.5, np.random.default_rng(seed))
            assert 0 <= sel < 3

    def test_raises_zero_phi_mean(self):
        with pytest.raises(ValueError):
            branch_collapse(np.array([1.0, 0.0]), 0.0, 0.5)

    def test_raises_zero_phi_dec(self):
        with pytest.raises(ValueError):
            branch_collapse(np.array([1.0, 0.0]), 1.0, 0.0)


# ---------------------------------------------------------------------------
# collapse_fidelity
# ---------------------------------------------------------------------------

class TestCollapseFidelity:
    def test_identical_gives_1(self):
        p = np.array([0.3, 0.7])
        assert abs(collapse_fidelity(p, p) - 1.0) < 1e-12

    def test_orthogonal_gives_zero(self):
        p1 = np.array([1.0, 0.0])
        p2 = np.array([0.0, 1.0])
        # max diff = 1.0, so fidelity = 0
        assert abs(collapse_fidelity(p1, p2) - 0.0) < 1e-12

    def test_bounded_in_01(self):
        p1 = np.array([0.4, 0.6])
        p2 = np.array([0.5, 0.5])
        f = collapse_fidelity(p1, p2)
        assert 0.0 <= f <= 1.0

    def test_raises_shape_mismatch(self):
        with pytest.raises(ValueError):
            collapse_fidelity(np.array([0.5, 0.5]), np.array([1.0 / 3] * 3))


# ---------------------------------------------------------------------------
# measurement_summary
# ---------------------------------------------------------------------------

class TestMeasurementSummary:
    def setup_method(self):
        self.amps = np.array([1.0, 1.0]) / math.sqrt(2)
        self.summary = measurement_summary(self.amps, 1.0, 0.5)

    def test_keys_present(self):
        for key in [
            "born_probs", "corrected_probs", "tau_dec",
            "collapsed", "information_current", "rho_cs_correction",
            "fidelity_to_born"
        ]:
            assert key in self.summary

    def test_born_probs_sum_to_1(self):
        assert abs(self.summary["born_probs"].sum() - 1.0) < 1e-12

    def test_corrected_probs_sum_to_1(self):
        assert abs(self.summary["corrected_probs"].sum() - 1.0) < 1e-12

    def test_tau_dec_positive(self):
        assert self.summary["tau_dec"] > 0.0

    def test_rho_cs_correction_value(self):
        assert abs(self.summary["rho_cs_correction"] - RHO_CS_CORRECTION) < 1e-12

    def test_fidelity_in_01(self):
        f = self.summary["fidelity_to_born"]
        assert 0.0 <= f <= 1.0

    def test_equal_superposition_born_half(self):
        assert np.allclose(self.summary["born_probs"], 0.5)

    def test_information_current_shape(self):
        assert self.summary["information_current"].shape == self.amps.shape
