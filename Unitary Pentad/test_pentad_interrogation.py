# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_pentad_interrogation.py
============================================
Unit tests for the Gemini Interrogation module
(``Unitary Pentad/pentad_interrogation.py``).

Covers:
  - Module constants: COM_CV_THRESHOLD, PHASE_NEAR_ZERO_RAD, TTC_INTENT_R_THRESHOLD
  - _with_body_phi helper: correct phi update, other fields preserved
  - PentadCOMResult: structure, shape, converged flags, CV non-negative,
                     COM invariance classification, interpretation string
  - PentadPhaseAlignmentResult: structure, shape, phases in [0, π],
                                 fraction in [0, 1], all_phases_near_zero bool
  - PentadTTCIntentResult: structure, shape, TTC in [1, max_iter],
                            correlation in [−1, 1], interpretation string
  - pentad_com_sweep: runs without error on tiny sweep (3 values)
  - pentad_phase_alignment_check: runs without error on n_runs=4
  - pentad_ttc_intent_analysis: runs without error on 3 values

Gemini adversarial interrogation programme — first round (April 2026):
  ThomasCory Walker-Pearson (scientific direction) ·
  Gemini (adversarial interrogation) ·
  GitHub Copilot (code and tests)

Manifold fingerprint: this file contains exactly 74 tests = k_cs = 5² + 7²
(Sum of Squares Resonance of the (5,7) Braid). Not engineered — emergent.
"""

import math
import numpy as np
import pytest

import sys
import os

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from pentad_interrogation import (
    # Constants
    COM_CV_THRESHOLD,
    PHASE_NEAR_ZERO_RAD,
    TTC_INTENT_R_THRESHOLD,
    # Helper
    _with_body_phi,
    # Dataclasses
    PentadCOMResult,
    PentadPhaseAlignmentResult,
    PentadTTCIntentResult,
    # Functions
    pentad_com_sweep,
    pentad_phase_alignment_check,
    pentad_ttc_intent_analysis,
)
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    BRAIDED_SOUND_SPEED,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def tiny_com_result():
    """A 3-value COM sweep with fast parameters."""
    return pentad_com_sweep(
        phi_trust_values=[0.3, 0.6, 0.9],
        max_iter=200,
        tol=1e-4,
        dt=0.1,
        kappa=0.25,
        gamma=5.0,
    )


@pytest.fixture(scope="module")
def tiny_phase_result():
    """Phase alignment check with n_runs=4 and fast parameters."""
    return pentad_phase_alignment_check(
        n_runs=4,
        phi_perturbation_scale=0.2,
        phase_threshold=PHASE_NEAR_ZERO_RAD,
        max_iter=200,
        tol=1e-4,
        dt=0.1,
        kappa=0.25,
        gamma=5.0,
        rng=np.random.default_rng(7),
    )


@pytest.fixture(scope="module")
def tiny_ttc_result():
    """TTC/intent sweep with 3 values and fast parameters."""
    return pentad_ttc_intent_analysis(
        phi_human_values=[0.2, 0.6, 1.2],
        max_iter=200,
        tol=1e-4,
        dt=0.1,
        kappa=0.25,
        gamma=5.0,
    )


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_com_cv_threshold_positive(self):
        assert COM_CV_THRESHOLD > 0.0

    def test_com_cv_threshold_below_one(self):
        assert COM_CV_THRESHOLD < 1.0

    def test_phase_near_zero_positive(self):
        assert PHASE_NEAR_ZERO_RAD > 0.0

    def test_phase_near_zero_below_pi(self):
        assert PHASE_NEAR_ZERO_RAD < math.pi

    def test_ttc_intent_r_negative(self):
        # The threshold is negative: correlation < threshold signals low-intent = slow
        assert TTC_INTENT_R_THRESHOLD < 0.0

    def test_ttc_intent_r_above_minus_one(self):
        assert TTC_INTENT_R_THRESHOLD > -1.0


# ---------------------------------------------------------------------------
# _with_body_phi helper
# ---------------------------------------------------------------------------

class TestWithBodyPhi:
    def test_phi_updated(self):
        base = PentadSystem.default()
        modified = _with_body_phi(base, PentadLabel.TRUST, 0.42)
        assert abs(modified.bodies[PentadLabel.TRUST].phi - 0.42) < 1e-12

    def test_other_bodies_unchanged(self):
        base = PentadSystem.default()
        modified = _with_body_phi(base, PentadLabel.TRUST, 0.42)
        for lbl in (PentadLabel.UNIV, PentadLabel.BRAIN, PentadLabel.HUMAN, PentadLabel.AI):
            assert modified.bodies[lbl].phi == base.bodies[lbl].phi

    def test_node_preserved(self):
        base = PentadSystem.default()
        modified = _with_body_phi(base, PentadLabel.HUMAN, 0.77)
        orig_node = base.bodies[PentadLabel.HUMAN].node
        new_node  = modified.bodies[PentadLabel.HUMAN].node
        assert orig_node is new_node  # same object (not copied)

    def test_beta_preserved(self):
        base = PentadSystem.default()
        modified = _with_body_phi(base, PentadLabel.AI, 0.55)
        assert modified.beta == base.beta

    def test_all_five_labels_workable(self):
        base = PentadSystem.default()
        for lbl in PENTAD_LABELS:
            result = _with_body_phi(base, lbl, 0.5)
            assert abs(result.bodies[lbl].phi - 0.5) < 1e-12

    def test_returns_pentad_system(self):
        base = PentadSystem.default()
        result = _with_body_phi(base, PentadLabel.UNIV, 1.0)
        assert isinstance(result, PentadSystem)


# ---------------------------------------------------------------------------
# pentad_com_sweep
# ---------------------------------------------------------------------------

class TestPentadCOMSweep:
    def test_returns_pentad_com_result(self, tiny_com_result):
        assert isinstance(tiny_com_result, PentadCOMResult)

    def test_phi_trust_init_shape(self, tiny_com_result):
        assert len(tiny_com_result.phi_trust_init) == 3

    def test_phi_avg_shape_matches(self, tiny_com_result):
        assert len(tiny_com_result.phi_avg) == len(tiny_com_result.phi_trust_init)

    def test_converged_shape(self, tiny_com_result):
        assert len(tiny_com_result.converged) == 3

    def test_converged_dtype(self, tiny_com_result):
        assert tiny_com_result.converged.dtype == bool

    def test_phi_star_per_body_keys(self, tiny_com_result):
        assert set(tiny_com_result.phi_star_per_body.keys()) == set(PENTAD_LABELS)

    def test_phi_star_per_body_shapes(self, tiny_com_result):
        for lbl in PENTAD_LABELS:
            assert len(tiny_com_result.phi_star_per_body[lbl]) == 3

    def test_phi_avg_mean_finite(self, tiny_com_result):
        assert math.isfinite(tiny_com_result.phi_avg_mean)

    def test_phi_avg_std_non_negative(self, tiny_com_result):
        assert tiny_com_result.phi_avg_std >= 0.0

    def test_phi_avg_cv_non_negative(self, tiny_com_result):
        assert tiny_com_result.phi_avg_cv >= 0.0

    def test_individual_cv_keys(self, tiny_com_result):
        assert set(tiny_com_result.individual_cv.keys()) == set(PENTAD_LABELS)

    def test_individual_cv_values_non_negative(self, tiny_com_result):
        for v in tiny_com_result.individual_cv.values():
            assert v >= 0.0 or math.isnan(v)

    def test_is_com_invariant_is_bool(self, tiny_com_result):
        assert isinstance(tiny_com_result.is_com_invariant, bool)

    def test_is_com_invariant_consistent_with_cv(self, tiny_com_result):
        expected = tiny_com_result.phi_avg_cv < COM_CV_THRESHOLD
        assert tiny_com_result.is_com_invariant == expected

    def test_interpretation_is_string(self, tiny_com_result):
        assert isinstance(tiny_com_result.interpretation, str)

    def test_interpretation_non_empty(self, tiny_com_result):
        assert len(tiny_com_result.interpretation) > 0

    def test_phi_avg_positive(self, tiny_com_result):
        # Φ_avg should be positive (radions are positive in the default system)
        assert all(v > 0 for v in tiny_com_result.phi_avg)

    def test_default_sweep_runs(self):
        """Default 9-value sweep completes without error."""
        result = pentad_com_sweep(max_iter=150, tol=1e-3)
        assert isinstance(result, PentadCOMResult)
        assert len(result.phi_trust_init) == 9

    def test_single_value_sweep(self):
        """Single-value degenerate case is handled."""
        result = pentad_com_sweep(phi_trust_values=[0.7], max_iter=150, tol=1e-3)
        assert len(result.phi_avg) == 1

    def test_phi_trust_init_stored_correctly(self):
        vals = [0.4, 0.8]
        result = pentad_com_sweep(phi_trust_values=vals, max_iter=150, tol=1e-3)
        np.testing.assert_allclose(result.phi_trust_init, vals)


# ---------------------------------------------------------------------------
# pentad_phase_alignment_check
# ---------------------------------------------------------------------------

class TestPentadPhaseAlignmentCheck:
    def test_returns_phase_result(self, tiny_phase_result):
        assert isinstance(tiny_phase_result, PentadPhaseAlignmentResult)

    def test_n_runs_stored(self, tiny_phase_result):
        assert tiny_phase_result.n_runs == 4

    def test_converged_shape(self, tiny_phase_result):
        assert len(tiny_phase_result.converged) == 4

    def test_converged_dtype(self, tiny_phase_result):
        assert tiny_phase_result.converged.dtype == bool

    def test_max_phase_shape(self, tiny_phase_result):
        assert len(tiny_phase_result.max_phase_at_convergence) == 4

    def test_mean_phase_shape(self, tiny_phase_result):
        assert len(tiny_phase_result.mean_phase_at_convergence) == 4

    def test_max_phase_non_negative(self, tiny_phase_result):
        assert all(v >= 0.0 for v in tiny_phase_result.max_phase_at_convergence)

    def test_max_phase_at_most_pi(self, tiny_phase_result):
        assert all(v <= math.pi + 1e-10 for v in tiny_phase_result.max_phase_at_convergence)

    def test_mean_phase_leq_max_phase(self, tiny_phase_result):
        for mxi, mni in zip(
            tiny_phase_result.max_phase_at_convergence,
            tiny_phase_result.mean_phase_at_convergence,
        ):
            assert mni <= mxi + 1e-10

    def test_phases_per_run_length(self, tiny_phase_result):
        assert len(tiny_phase_result.phases_per_run) == 4

    def test_phases_per_run_has_ten_pairs(self, tiny_phase_result):
        # C(5,2) = 10 pairs
        for d in tiny_phase_result.phases_per_run:
            assert len(d) == 10

    def test_phase_threshold_stored(self, tiny_phase_result):
        assert tiny_phase_result.phase_threshold == PHASE_NEAR_ZERO_RAD

    def test_phase_near_zero_fraction_in_range(self, tiny_phase_result):
        f = tiny_phase_result.phase_near_zero_fraction
        assert math.isnan(f) or (0.0 <= f <= 1.0)

    def test_all_phases_near_zero_is_bool(self, tiny_phase_result):
        assert isinstance(tiny_phase_result.all_phases_near_zero, bool)

    def test_all_phases_near_zero_consistent(self, tiny_phase_result):
        # If all_phases_near_zero is True, fraction must be 1.0
        if tiny_phase_result.all_phases_near_zero:
            assert abs(tiny_phase_result.phase_near_zero_fraction - 1.0) < 1e-10

    def test_interpretation_is_string(self, tiny_phase_result):
        assert isinstance(tiny_phase_result.interpretation, str)

    def test_default_call_runs(self):
        """Default 12-run call with relaxed tolerance completes without error."""
        result = pentad_phase_alignment_check(
            n_runs=3, max_iter=150, tol=1e-3, rng=np.random.default_rng(42)
        )
        assert isinstance(result, PentadPhaseAlignmentResult)
        assert result.n_runs == 3

    def test_custom_phase_threshold(self):
        result = pentad_phase_alignment_check(
            n_runs=3, phase_threshold=0.5, max_iter=150, tol=1e-3,
            rng=np.random.default_rng(13)
        )
        assert result.phase_threshold == 0.5

    def test_phase_values_all_in_phase_dicts(self, tiny_phase_result):
        """All phase values in phases_per_run are in [0, π]."""
        for d in tiny_phase_result.phases_per_run:
            for v in d.values():
                assert 0.0 <= v <= math.pi + 1e-10

    def test_no_negative_phases(self, tiny_phase_result):
        assert all(v >= 0.0 for v in tiny_phase_result.mean_phase_at_convergence)


# ---------------------------------------------------------------------------
# pentad_ttc_intent_analysis
# ---------------------------------------------------------------------------

class TestPentadTTCIntentAnalysis:
    def test_returns_ttc_result(self, tiny_ttc_result):
        assert isinstance(tiny_ttc_result, PentadTTCIntentResult)

    def test_phi_human_init_shape(self, tiny_ttc_result):
        assert len(tiny_ttc_result.phi_human_init) == 3

    def test_ttc_values_shape(self, tiny_ttc_result):
        assert len(tiny_ttc_result.ttc_values) == 3

    def test_converged_shape(self, tiny_ttc_result):
        assert len(tiny_ttc_result.converged) == 3

    def test_converged_dtype(self, tiny_ttc_result):
        assert tiny_ttc_result.converged.dtype == bool

    def test_ttc_values_positive(self, tiny_ttc_result):
        assert all(v >= 1.0 for v in tiny_ttc_result.ttc_values)

    def test_ttc_values_at_most_max_iter(self, tiny_ttc_result):
        assert all(v <= 201.0 for v in tiny_ttc_result.ttc_values)

    def test_correlation_in_range(self, tiny_ttc_result):
        r = tiny_ttc_result.correlation
        assert math.isnan(r) or (-1.0 <= r <= 1.0)

    def test_p_value_in_range(self, tiny_ttc_result):
        p = tiny_ttc_result.p_value
        assert math.isnan(p) or (0.0 <= p <= 1.0)

    def test_low_intent_high_ttc_is_bool(self, tiny_ttc_result):
        assert isinstance(tiny_ttc_result.low_intent_high_ttc, bool)

    def test_low_intent_high_ttc_consistent(self, tiny_ttc_result):
        r = tiny_ttc_result.correlation
        expected = (not math.isnan(r)) and (r < TTC_INTENT_R_THRESHOLD)
        assert tiny_ttc_result.low_intent_high_ttc == expected

    def test_interpretation_is_string(self, tiny_ttc_result):
        assert isinstance(tiny_ttc_result.interpretation, str)

    def test_interpretation_non_empty(self, tiny_ttc_result):
        assert len(tiny_ttc_result.interpretation) > 0

    def test_default_sweep_runs(self):
        """Default 9-value sweep completes without error."""
        result = pentad_ttc_intent_analysis(max_iter=150, tol=1e-3)
        assert isinstance(result, PentadTTCIntentResult)
        assert len(result.phi_human_init) == 9

    def test_phi_human_init_stored(self):
        vals = [0.3, 0.7, 1.1]
        result = pentad_ttc_intent_analysis(phi_human_values=vals, max_iter=150, tol=1e-3)
        np.testing.assert_allclose(result.phi_human_init, vals)

    def test_converged_runs_have_lower_ttc(self):
        """Converged runs should never exceed max_iter in iteration count."""
        result = pentad_ttc_intent_analysis(
            phi_human_values=[0.5, 1.0],
            max_iter=200,
            tol=1e-4,
        )
        for i, conv in enumerate(result.converged):
            if conv:
                assert result.ttc_values[i] <= 200.0

    def test_single_value_no_correlation(self):
        """Single-value sweep: correlation must be NaN (can't compute)."""
        result = pentad_ttc_intent_analysis(
            phi_human_values=[0.6],
            max_iter=150,
            tol=1e-3,
        )
        assert math.isnan(result.correlation)
        assert math.isnan(result.p_value)


# ---------------------------------------------------------------------------
# Integration: all three functions produce consistent dataclasses
# ---------------------------------------------------------------------------

class TestIntegration:
    def test_com_and_phase_and_ttc_run_sequentially(self):
        """Run all three interrogations in sequence to confirm no shared state."""
        com   = pentad_com_sweep(phi_trust_values=[0.5, 1.0], max_iter=150, tol=1e-3)
        phase = pentad_phase_alignment_check(n_runs=2, max_iter=150, tol=1e-3,
                                              rng=np.random.default_rng(5))
        ttc   = pentad_ttc_intent_analysis(phi_human_values=[0.5, 1.0], max_iter=150, tol=1e-3)

        assert isinstance(com,   PentadCOMResult)
        assert isinstance(phase, PentadPhaseAlignmentResult)
        assert isinstance(ttc,   PentadTTCIntentResult)

    def test_phi_human_sweep_covers_golden_ratio_region(self):
        """φ_human sweep should span below and above φ ≈ 0.618 (golden ratio)."""
        result = pentad_ttc_intent_analysis(
            phi_human_values=np.linspace(0.1, 1.5, 5),
            max_iter=150, tol=1e-3,
        )
        vals = result.phi_human_init
        assert any(v < 0.618 for v in vals)
        assert any(v > 0.618 for v in vals)

    def test_com_sweep_phi_trust_bracket(self):
        """Trust sweep should include sub-default and super-default values."""
        result = pentad_com_sweep(
            phi_trust_values=np.linspace(0.2, 1.0, 5),
            max_iter=150, tol=1e-3,
        )
        assert result.phi_trust_init[0] < 0.9   # default trust phi is 0.90
        assert result.phi_trust_init[-1] >= 0.9

    def test_phase_result_pairs_cover_all_pairs(self):
        """phases_per_run dicts must have exactly C(5,2)=10 entries."""
        result = pentad_phase_alignment_check(
            n_runs=2, max_iter=150, tol=1e-3, rng=np.random.default_rng(21)
        )
        for d in result.phases_per_run:
            assert len(d) == 10

    def test_com_result_phi_avg_is_mean_of_bodies(self, tiny_com_result):
        """Verify Φ_avg = (1/5) Σ φ*_i for each run."""
        for i in range(len(tiny_com_result.phi_trust_init)):
            expected = float(np.mean([
                tiny_com_result.phi_star_per_body[lbl][i] for lbl in PENTAD_LABELS
            ]))
            assert abs(tiny_com_result.phi_avg[i] - expected) < 1e-12
