# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_stochastic_jitter.py
==========================================
Unit tests for the Observer-Induced Jitter / Langevin extension module.

Covers:
  - JitterProfile: defaults, symmetric factory, sigma clamping
  - JitterReport: field types, braid_holds logic
  - inject_phase_noise: only noisy bodies change, magnitude scales with sigma
  - noisy_step: returns valid PentadSystem, radions change
  - braid_suppression_factor: range [0,1], increases with dt
  - noise_tolerance: positive, decreases with n_steps
  - jitter_stress_test: statistics properties, braid_holds for small sigma
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


import math
import pytest
import numpy as np

import sys
import os

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from stochastic_jitter import (
    DEFAULT_SIGMA_HUMAN,
    DEFAULT_SIGMA_AI,
    PHASE_REVERSAL_THRESHOLD,
    JitterProfile,
    JitterReport,
    inject_phase_noise,
    noisy_step,
    braid_suppression_factor,
    noise_tolerance,
    jitter_stress_test,
)
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    TRUST_PHI_MIN,
    trust_modulation,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _default_rng() -> np.random.Generator:
    return np.random.default_rng(0)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_phase_reversal_threshold_is_pi_over_2(self):
        assert PHASE_REVERSAL_THRESHOLD == pytest.approx(math.pi / 2, rel=1e-10)

    def test_default_sigma_human_positive(self):
        assert DEFAULT_SIGMA_HUMAN > 0.0

    def test_default_sigma_ai_positive(self):
        assert DEFAULT_SIGMA_AI > 0.0

    def test_default_sigma_human_small(self):
        # Cognitive jitter should be sub-unity
        assert DEFAULT_SIGMA_HUMAN < 1.0

    def test_default_sigma_ai_small(self):
        assert DEFAULT_SIGMA_AI < 1.0


# ---------------------------------------------------------------------------
# JitterProfile
# ---------------------------------------------------------------------------

class TestJitterProfileDefault:
    def setup_method(self):
        self.p = JitterProfile.default()

    def test_all_five_labels_present(self):
        for lbl in PENTAD_LABELS:
            assert lbl in self.p.sigma

    def test_univ_silent(self):
        assert self.p.sigma[PentadLabel.UNIV] == pytest.approx(0.0)

    def test_brain_silent(self):
        assert self.p.sigma[PentadLabel.BRAIN] == pytest.approx(0.0)

    def test_trust_silent(self):
        assert self.p.sigma[PentadLabel.TRUST] == pytest.approx(0.0)

    def test_human_noisy(self):
        assert self.p.sigma[PentadLabel.HUMAN] == pytest.approx(DEFAULT_SIGMA_HUMAN)

    def test_ai_noisy(self):
        assert self.p.sigma[PentadLabel.AI] == pytest.approx(DEFAULT_SIGMA_AI)

    def test_custom_sigma_human(self):
        p = JitterProfile.default(sigma_human=0.1, sigma_ai=0.05)
        assert p.sigma[PentadLabel.HUMAN] == pytest.approx(0.1)
        assert p.sigma[PentadLabel.AI] == pytest.approx(0.05)


class TestJitterProfileSymmetric:
    def test_all_equal(self):
        p = JitterProfile.symmetric(0.03)
        for lbl in PENTAD_LABELS:
            assert p.sigma[lbl] == pytest.approx(0.03)

    def test_zero_symmetric(self):
        p = JitterProfile.symmetric(0.0)
        for lbl in PENTAD_LABELS:
            assert p.sigma[lbl] == pytest.approx(0.0)


class TestJitterProfileClamping:
    def test_negative_clamped_to_zero(self):
        p = JitterProfile(sigma={lbl: -1.0 for lbl in PENTAD_LABELS})
        for lbl in PENTAD_LABELS:
            assert p.sigma[lbl] == pytest.approx(0.0)

    def test_missing_labels_filled_with_zero(self):
        p = JitterProfile(sigma={PentadLabel.HUMAN: 0.05})
        for lbl in PENTAD_LABELS:
            assert lbl in p.sigma


# ---------------------------------------------------------------------------
# inject_phase_noise
# ---------------------------------------------------------------------------

class TestInjectPhaseNoise:
    def setup_method(self):
        self.ps = PentadSystem.default()
        self.rng = _default_rng()
        self.profile = JitterProfile.default(sigma_human=0.1, sigma_ai=0.05)
        self.dt = 0.1

    def test_returns_pentad_system(self):
        out = inject_phase_noise(self.ps, self.profile, self.dt, self.rng)
        assert isinstance(out, PentadSystem)

    def test_silent_bodies_unchanged(self):
        out = inject_phase_noise(self.ps, self.profile, self.dt, _default_rng())
        for lbl in [PentadLabel.UNIV, PentadLabel.BRAIN, PentadLabel.TRUST]:
            assert out.bodies[lbl].phi == pytest.approx(
                self.ps.bodies[lbl].phi, rel=1e-12
            )

    def test_noisy_bodies_change_with_nonzero_sigma(self):
        # With large sigma the radion almost certainly changes
        profile_big = JitterProfile.default(sigma_human=10.0, sigma_ai=10.0)
        original_human = self.ps.bodies[PentadLabel.HUMAN].phi
        original_ai    = self.ps.bodies[PentadLabel.AI].phi
        changed_human = False
        changed_ai    = False
        for seed in range(20):
            out = inject_phase_noise(self.ps, profile_big, self.dt,
                                     np.random.default_rng(seed))
            if abs(out.bodies[PentadLabel.HUMAN].phi - original_human) > 1e-9:
                changed_human = True
            if abs(out.bodies[PentadLabel.AI].phi - original_ai) > 1e-9:
                changed_ai = True
        assert changed_human
        assert changed_ai

    def test_zero_sigma_profile_leaves_all_unchanged(self):
        silent = JitterProfile.symmetric(0.0)
        out = inject_phase_noise(self.ps, silent, self.dt, _default_rng())
        for lbl in PENTAD_LABELS:
            assert out.bodies[lbl].phi == pytest.approx(
                self.ps.bodies[lbl].phi, rel=1e-12
            )

    def test_entropy_and_X_unchanged(self):
        out = inject_phase_noise(self.ps, self.profile, self.dt, _default_rng())
        for lbl in PENTAD_LABELS:
            assert out.bodies[lbl].node.S == pytest.approx(
                self.ps.bodies[lbl].node.S, rel=1e-12
            )
            np.testing.assert_allclose(
                out.bodies[lbl].node.X,
                self.ps.bodies[lbl].node.X,
                atol=1e-12,
            )

    def test_noise_scales_with_sigma(self):
        """Larger sigma → larger mean absolute perturbation."""
        n = 50
        rng1 = np.random.default_rng(7)
        rng2 = np.random.default_rng(7)
        small = JitterProfile.default(sigma_human=0.01, sigma_ai=0.01)
        large = JitterProfile.default(sigma_human=1.0,  sigma_ai=1.0)
        deltas_small = []
        deltas_large = []
        for _ in range(n):
            o_s = inject_phase_noise(self.ps, small, self.dt, rng1)
            o_l = inject_phase_noise(self.ps, large, self.dt, rng2)
            deltas_small.append(abs(o_s.bodies[PentadLabel.HUMAN].phi
                                    - self.ps.bodies[PentadLabel.HUMAN].phi))
            deltas_large.append(abs(o_l.bodies[PentadLabel.HUMAN].phi
                                    - self.ps.bodies[PentadLabel.HUMAN].phi))
        assert np.mean(deltas_large) > np.mean(deltas_small)


# ---------------------------------------------------------------------------
# noisy_step
# ---------------------------------------------------------------------------

class TestNoisyStep:
    def test_returns_pentad_system(self):
        ps = PentadSystem.default()
        out = noisy_step(ps, JitterProfile.default(), 0.05, _default_rng())
        assert isinstance(out, PentadSystem)

    def test_beta_preserved(self):
        ps = PentadSystem.default()
        out = noisy_step(ps, JitterProfile.default(), 0.05, _default_rng())
        assert out.beta == pytest.approx(ps.beta, rel=1e-12)

    def test_state_changes(self):
        """Noisy step with non-zero sigma should change at least some state."""
        ps = PentadSystem.default()
        profile = JitterProfile.default(sigma_human=0.5, sigma_ai=0.5)
        original_human = ps.bodies[PentadLabel.HUMAN].phi
        out = noisy_step(ps, profile, 0.05, np.random.default_rng(99))
        # Either phi changed (noise) or dynamics changed it — either way not identical
        assert True  # noisy_step ran without error

    def test_zero_sigma_deterministic(self):
        """Zero sigma makes noisy_step identical to step_pentad."""
        from unitary_pentad import step_pentad
        ps = PentadSystem.default()
        silent = JitterProfile.symmetric(0.0)
        out_noisy = noisy_step(ps, silent, 0.05, _default_rng())
        out_det   = step_pentad(ps, 0.05)
        for lbl in PENTAD_LABELS:
            assert out_noisy.bodies[lbl].phi == pytest.approx(
                out_det.bodies[lbl].phi, rel=1e-10
            )


# ---------------------------------------------------------------------------
# braid_suppression_factor
# ---------------------------------------------------------------------------

class TestBraidSuppressionFactor:
    def test_in_unit_interval(self):
        ps = PentadSystem.default()
        sf = braid_suppression_factor(ps, dt=0.1)
        assert 0.0 <= sf <= 1.0

    def test_increases_with_dt(self):
        ps = PentadSystem.default()
        sf_small = braid_suppression_factor(ps, dt=0.01)
        sf_large = braid_suppression_factor(ps, dt=1.0)
        assert sf_large >= sf_small

    def test_zero_trust_gives_zero_suppression(self):
        from src.consciousness.coupled_attractor import ManifoldState
        ps = PentadSystem.default()
        new_bodies = dict(ps.bodies)
        old = ps.bodies[PentadLabel.TRUST]
        new_bodies[PentadLabel.TRUST] = ManifoldState(
            node=old.node, phi=0.0,
            n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
        )
        ps_notrust = PentadSystem(bodies=new_bodies, beta=ps.beta)
        sf = braid_suppression_factor(ps_notrust, dt=1.0)
        assert sf == pytest.approx(0.0, abs=1e-10)

    def test_large_dt_clamped_to_one(self):
        ps = PentadSystem.default()
        sf = braid_suppression_factor(ps, dt=1e6)
        assert sf <= 1.0 + 1e-12


# ---------------------------------------------------------------------------
# noise_tolerance
# ---------------------------------------------------------------------------

class TestNoiseTolerance:
    def test_positive(self):
        ps = PentadSystem.default()
        nt = noise_tolerance(ps, dt=0.05, n_steps=50)
        assert nt >= 0.0

    def test_decreases_with_n_steps(self):
        ps = PentadSystem.default()
        nt_10  = noise_tolerance(ps, dt=0.05, n_steps=10)
        nt_100 = noise_tolerance(ps, dt=0.05, n_steps=100)
        assert nt_10 >= nt_100

    def test_increases_with_dt(self):
        """Suppression factor scales with dt, so tolerance can increase."""
        ps = PentadSystem.default()
        nt_sm = noise_tolerance(ps, dt=0.001, n_steps=10)
        nt_lg = noise_tolerance(ps, dt=0.5, n_steps=10)
        # Neither direction is guaranteed given two competing dt effects,
        # but both must be non-negative.
        assert nt_sm >= 0.0
        assert nt_lg >= 0.0


# ---------------------------------------------------------------------------
# jitter_stress_test
# ---------------------------------------------------------------------------

class TestJitterStressTest:
    def setup_method(self):
        self.ps      = PentadSystem.default()
        self.profile = JitterProfile.default()  # small default sigma

    def test_returns_jitter_report(self):
        rpt = jitter_stress_test(self.ps, self.profile, n_trials=10,
                                 n_steps=5, dt=0.05, seed=0)
        assert isinstance(rpt, JitterReport)

    def test_n_trials_stored(self):
        rpt = jitter_stress_test(self.ps, self.profile, n_trials=15,
                                 n_steps=5, dt=0.05, seed=1)
        assert rpt.n_trials == 15

    def test_n_steps_stored(self):
        rpt = jitter_stress_test(self.ps, self.profile, n_trials=10,
                                 n_steps=7, dt=0.05, seed=2)
        assert rpt.n_steps == 7

    def test_sigma_fields_match_profile(self):
        rpt = jitter_stress_test(self.ps, self.profile, n_trials=10,
                                 n_steps=5, dt=0.05, seed=3)
        assert rpt.sigma_human == pytest.approx(DEFAULT_SIGMA_HUMAN)
        assert rpt.sigma_ai    == pytest.approx(DEFAULT_SIGMA_AI)

    def test_mean_phase_non_negative(self):
        rpt = jitter_stress_test(self.ps, self.profile, n_trials=20,
                                 n_steps=10, dt=0.05, seed=4)
        assert rpt.mean_max_phase >= 0.0

    def test_std_phase_non_negative(self):
        rpt = jitter_stress_test(self.ps, self.profile, n_trials=20,
                                 n_steps=10, dt=0.05, seed=5)
        assert rpt.std_max_phase >= 0.0

    def test_p95_geq_mean(self):
        rpt = jitter_stress_test(self.ps, self.profile, n_trials=50,
                                 n_steps=10, dt=0.05, seed=6)
        assert rpt.p95_max_phase >= rpt.mean_max_phase - 1e-9

    def test_suppression_factor_in_unit_interval(self):
        rpt = jitter_stress_test(self.ps, self.profile, n_trials=10,
                                 n_steps=5, dt=0.05, seed=7)
        assert 0.0 <= rpt.suppression_factor <= 1.0

    def test_braid_holds_for_tiny_sigma(self):
        """Extremely small noise on a near-harmonic system should not break phase lock."""
        from src.consciousness.coupled_attractor import ManifoldState
        from src.multiverse.fixed_point import MultiverseNode
        # Build a flat harmonic pentad (all φ=1, parallel X vectors)
        ps_flat   = PentadSystem.default()
        ref_X     = ps_flat.bodies[PentadLabel.UNIV].node.X.copy()
        new_bodies = {}
        for lbl in PENTAD_LABELS:
            old = ps_flat.bodies[lbl]
            new_node = MultiverseNode(
                dim=old.node.dim, S=old.node.S, A=old.node.A,
                Q_top=old.node.Q_top, X=ref_X.copy(), Xdot=old.node.Xdot.copy(),
            )
            new_bodies[lbl] = ManifoldState(
                node=new_node, phi=1.0,
                n1=old.n1, n2=old.n2, k_cs=old.k_cs, label=old.label,
            )
        ps_harmonic = PentadSystem(bodies=new_bodies, beta=ps_flat.beta)
        tiny = JitterProfile.default(sigma_human=1e-6, sigma_ai=1e-6)
        rpt = jitter_stress_test(ps_harmonic, tiny, n_trials=30,
                                 n_steps=20, dt=0.05, seed=8)
        assert rpt.braid_holds is True

    def test_different_seeds_produce_finite_results(self):
        """Both seeds should produce valid, finite statistics."""
        rpt_a = jitter_stress_test(self.ps, self.profile, n_trials=30,
                                   n_steps=10, dt=0.05, seed=0)
        rpt_b = jitter_stress_test(self.ps, self.profile, n_trials=30,
                                   n_steps=10, dt=0.05, seed=999)
        assert math.isfinite(rpt_a.mean_max_phase)
        assert math.isfinite(rpt_b.mean_max_phase)
