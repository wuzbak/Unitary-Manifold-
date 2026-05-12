# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/test_realtime_sciences_core.py
==========================================
Unit tests for the Real-Time Sciences Core.

Covers:
  - Constants: C_S, DEFAULT_N_HYPOTHESES, QUERY_READY_THRESHOLD, DEFAULT_DOMAINS
  - DataDomain constants
  - Observation: construction, likelihood normalisation
  - RealTimeSciencesCore: factory (NumPy and JAX paths), add_domain,
    ingest, readiness, system_readiness, query, tick
  - Bayesian update: monotone readiness increase after concentrated likelihood
  - System readiness: geometric mean with trust weighting
  - JAX/NumPy equivalence (when JAX available)
  - Edge cases: empty domain list, uniform belief, unknown domain query
"""

import math
import sys
import os

import pytest
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_PENTAD = os.path.dirname(_HERE)
_ROOT = os.path.dirname(_PENTAD)
for _p in [_HERE, _PENTAD, _ROOT]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from five_cores.realtime_sciences_core import (
    C_S,
    DEFAULT_N_HYPOTHESES,
    QUERY_READY_THRESHOLD,
    DEFAULT_DOMAINS,
    DataDomain,
    Observation,
    SciencesState,
    RealTimeSciencesCore,
    _JAX_AVAILABLE,
)

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def concentrated_likelihood(k: int, peak_idx: int, sharpness: float = 10.0) -> np.ndarray:
    """Return likelihood array peaked at peak_idx with given sharpness."""
    x = np.zeros(k)
    x[peak_idx] = sharpness
    x += 1.0  # smooth floor
    return x / x.sum()


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_c_s_value(self):
        assert math.isclose(C_S, 12 / 37, rel_tol=1e-12)

    def test_default_hypotheses_positive(self):
        assert DEFAULT_N_HYPOTHESES > 1

    def test_query_ready_threshold_in_range(self):
        assert 0 < QUERY_READY_THRESHOLD < 1

    def test_default_domains_not_empty(self):
        assert len(DEFAULT_DOMAINS) > 0

    def test_data_domain_constants_strings(self):
        for attr in ["ASTROPHYSICS", "NAVIGATION", "BIOLOGY"]:
            assert isinstance(getattr(DataDomain, attr), str)


# ===========================================================================
# Observation
# ===========================================================================

class TestObservation:
    def test_likelihood_normalised(self):
        obs = Observation("ASTROPHYSICS", np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
        assert math.isclose(obs.likelihood_ratios.sum(), 1.0, abs_tol=1e-10)

    def test_all_nonnegative_after_construction(self):
        obs = Observation("NAVIGATION", np.array([0.0, 1.0, 0.0, 0.0, 2.0]))
        assert np.all(obs.likelihood_ratios >= 0)

    def test_uniform_likelihood_stays_uniform(self):
        k = DEFAULT_N_HYPOTHESES
        obs = Observation("BIOLOGY", np.ones(k))
        assert np.allclose(obs.likelihood_ratios, 1 / k)


# ===========================================================================
# Factory
# ===========================================================================

class TestFactory:
    def test_default_factory(self):
        sc = RealTimeSciencesCore.default()
        assert sc._phi_trust == 1.0
        assert len(sc._beliefs) == len(DEFAULT_DOMAINS)

    def test_numpy_factory(self):
        sc = RealTimeSciencesCore(use_jax=False)
        assert not sc._use_jax

    def test_jax_factory(self):
        if not _JAX_AVAILABLE:
            pytest.skip("JAX not installed")
        sc = RealTimeSciencesCore(use_jax=True)
        assert sc._use_jax

    def test_jax_require_raises_without_jax(self):
        if _JAX_AVAILABLE:
            pytest.skip("JAX is available — can't test this path")
        with pytest.raises(ImportError):
            RealTimeSciencesCore(use_jax=True)

    def test_custom_domains(self):
        sc = RealTimeSciencesCore(domains=["ALPHA", "BETA"])
        assert set(sc._beliefs.keys()) == {"ALPHA", "BETA"}

    def test_custom_n_hypotheses(self):
        sc = RealTimeSciencesCore(n_hypotheses=8)
        for b in sc._beliefs.values():
            assert len(b) == 8


# ===========================================================================
# Add Domain
# ===========================================================================

class TestAddDomain:
    def test_add_new_domain(self):
        sc = RealTimeSciencesCore(domains=[])
        sc.add_domain("NEW_DOMAIN")
        assert "NEW_DOMAIN" in sc._beliefs

    def test_add_domain_idempotent(self):
        sc = RealTimeSciencesCore.default()
        b_before = sc._beliefs[DataDomain.ASTROPHYSICS].copy()
        sc.add_domain(DataDomain.ASTROPHYSICS)
        assert np.allclose(sc._beliefs[DataDomain.ASTROPHYSICS], b_before)


# ===========================================================================
# Ingest and Bayesian Update
# ===========================================================================

class TestIngest:
    def _core(self) -> RealTimeSciencesCore:
        return RealTimeSciencesCore(use_jax=False, n_hypotheses=5)

    def test_ingest_increments_count(self):
        sc = self._core()
        obs = Observation(DataDomain.ASTROPHYSICS, concentrated_likelihood(5, 0))
        sc.ingest(obs)
        assert sc._ingestion_count == 1

    def test_ingest_unknown_domain_creates_it(self):
        sc = self._core()
        sc.ingest(Observation("EXOTIC_DOMAIN", np.ones(5)))
        assert "EXOTIC_DOMAIN" in sc._beliefs

    def test_readiness_increases_after_concentrated_ingest(self):
        sc = self._core()
        r_before = sc.readiness(DataDomain.ASTROPHYSICS)
        for _ in range(20):
            obs = Observation(DataDomain.ASTROPHYSICS, concentrated_likelihood(5, 2))
            sc.ingest(obs)
        r_after = sc.readiness(DataDomain.ASTROPHYSICS)
        assert r_after > r_before

    def test_readiness_zero_at_uniform(self):
        sc = self._core()
        r = sc.readiness(DataDomain.ASTROPHYSICS)
        # Uniform belief → H = log(K) → R = 0
        assert math.isclose(r, 0.0, abs_tol=1e-10)

    def test_readiness_one_at_degenerate(self):
        sc = self._core()
        # Force degenerate belief
        sc._beliefs[DataDomain.ASTROPHYSICS] = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
        r = sc.readiness(DataDomain.ASTROPHYSICS)
        assert math.isclose(r, 1.0, abs_tol=1e-10)

    def test_readiness_bounded(self):
        sc = self._core()
        for _ in range(50):
            obs = Observation(DataDomain.BIOLOGY, concentrated_likelihood(5, 1))
            sc.ingest(obs)
        assert 0.0 <= sc.readiness(DataDomain.BIOLOGY) <= 1.0


# ===========================================================================
# System Readiness
# ===========================================================================

class TestSystemReadiness:
    def test_system_readiness_in_unit_interval(self):
        sc = RealTimeSciencesCore.default()
        sr = sc.system_readiness()
        assert 0.0 <= sr <= 1.0

    def test_system_readiness_one_when_all_domains_degenerate(self):
        # With R_i = 1 for all domains, geometric mean must be 1 regardless of trust.
        k = DEFAULT_N_HYPOTHESES
        sc = RealTimeSciencesCore(phi_trust=0.5, use_jax=False, n_hypotheses=k)
        degenerate = np.zeros(k)
        degenerate[0] = 1.0
        for d in sc._beliefs:
            sc._beliefs[d] = degenerate.copy()
        assert math.isclose(sc.system_readiness(), 1.0, abs_tol=1e-8)

    def test_system_readiness_non_negative(self):
        sc = RealTimeSciencesCore(phi_trust=0.1, use_jax=False)
        assert sc.system_readiness() >= 0.0


# ===========================================================================
# Query
# ===========================================================================

class TestQuery:
    def test_query_returns_dict(self):
        sc = RealTimeSciencesCore.default()
        result = sc.query(DataDomain.ASTROPHYSICS, "What is the CMB temperature?")
        assert isinstance(result, dict)
        assert "readiness" in result
        assert "dominant_hypothesis" in result
        assert "belief" in result

    def test_query_ready_flag(self):
        sc = RealTimeSciencesCore(use_jax=False, n_hypotheses=5)
        # Force high readiness
        sc._beliefs[DataDomain.ASTROPHYSICS] = np.array([0.9, 0.025, 0.025, 0.025, 0.025])
        result = sc.query(DataDomain.ASTROPHYSICS)
        assert result["query_ready"]

    def test_query_unknown_domain(self):
        sc = RealTimeSciencesCore.default()
        result = sc.query("UNKNOWN_DOMAIN")
        assert "readiness" in result


# ===========================================================================
# Tick
# ===========================================================================

class TestTick:
    def test_tick_returns_state(self):
        sc = RealTimeSciencesCore.default()
        state = sc.tick()
        assert isinstance(state, SciencesState)

    def test_jax_active_flag(self):
        sc = RealTimeSciencesCore(use_jax=False)
        state = sc.tick()
        assert not state.jax_active

    def test_tick_with_observations(self):
        sc = RealTimeSciencesCore(use_jax=False, n_hypotheses=5)
        obs = [Observation(DataDomain.NAVIGATION, concentrated_likelihood(5, 0))]
        state = sc.tick(observations=obs)
        assert state.recent_ingestion_count == 1

    def test_step_count_increments(self):
        sc = RealTimeSciencesCore.default()
        sc.tick()
        sc.tick()
        assert sc._step_count == 2


# ===========================================================================
# JAX / NumPy equivalence
# ===========================================================================

@pytest.mark.skipif(not _JAX_AVAILABLE, reason="JAX not installed")
class TestJAXNumPyEquivalence:
    def test_same_belief_update(self):
        k = 5
        b = np.ones(k) / k
        likelihood = concentrated_likelihood(k, 2)

        sc_np = RealTimeSciencesCore(use_jax=False, domains=["X"], n_hypotheses=k)
        sc_jx = RealTimeSciencesCore(use_jax=True, domains=["X"], n_hypotheses=k)
        sc_np._beliefs["X"] = b.copy()
        sc_jx._beliefs["X"] = b.copy()

        sc_np.ingest(Observation("X", likelihood))
        sc_jx.ingest(Observation("X", likelihood))

        assert np.allclose(sc_np._beliefs["X"], sc_jx._beliefs["X"], atol=1e-6)

    def test_same_readiness(self):
        k = 5
        b = concentrated_likelihood(k, 1)
        sc_np = RealTimeSciencesCore(use_jax=False, domains=["X"], n_hypotheses=k)
        sc_jx = RealTimeSciencesCore(use_jax=True, domains=["X"], n_hypotheses=k)
        sc_np._beliefs["X"] = b.copy()
        sc_jx._beliefs["X"] = b.copy()
        assert math.isclose(
            sc_np.readiness("X"), sc_jx.readiness("X"), abs_tol=1e-5
        )
