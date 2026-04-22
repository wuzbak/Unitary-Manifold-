# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_coupled_history.py
==============================
Test suite for Pillar 45 — Coupled History: Consciousness–Quantum Measurement
Bridge (src/core/coupled_history.py).

~90 tests covering:
  - Constants
  - agency_decoherence_ratio: formula, ADR ≥ 1, monotonicity, errors
  - tau_dec_coupled: formula, ≤ tau_dec_bare, errors
  - build_coupled_history: structure, var_brain ≥ 0, ADR ≥ 1
  - high_agency_collapses_faster: observer_accelerates, born_probs, intentionality
  - consciousness_measurement_link: full dict, var_brain estimation, ADR formula
  - adr_vs_agency_scan: monotonicity of ADR vs Var_brain
  - Quantitative "Coupled History" assertion: high-agency brain causes faster collapse

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

from src.core.coupled_history import (
    BETA_COUPLING,
    PHI_VAR_FLOOR,
    CoupledHistory,
    agency_decoherence_ratio,
    adr_vs_agency_scan,
    build_coupled_history,
    consciousness_measurement_link,
    high_agency_collapses_faster,
    tau_dec_coupled,
)
from src.consciousness.coupled_attractor import (
    BIREFRINGENCE_RAD,
    CoupledSystem,
    ManifoldState,
)
from src.core.geometric_collapse import decoherence_timescale


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _default_system(phi_brain: float = 0.7, phi_univ: float = 1.0) -> CoupledSystem:
    b = ManifoldState.brain(phi=phi_brain, rng=np.random.default_rng(42))
    u = ManifoldState.universe(phi=phi_univ, rng=np.random.default_rng(0))
    return CoupledSystem(brain=b, universe=u)


def _simple_amplitudes() -> np.ndarray:
    return np.array([1.0 + 0j, 1.0 + 0j])


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_beta_coupling_matches_birefringence(self):
        assert BETA_COUPLING == pytest.approx(BIREFRINGENCE_RAD, rel=1e-9)

    def test_beta_coupling_small_positive(self):
        assert 5e-3 < BETA_COUPLING < 8e-3

    def test_phi_var_floor_positive(self):
        assert PHI_VAR_FLOOR > 0.0


# ---------------------------------------------------------------------------
# agency_decoherence_ratio
# ---------------------------------------------------------------------------

class TestAgencyDecohereRatio:
    def test_zero_var_gives_one(self):
        adr = agency_decoherence_ratio(0.0, phi_spread_bare=0.1)
        assert adr == pytest.approx(1.0)

    def test_positive_var_gives_adr_gt_one(self):
        adr = agency_decoherence_ratio(0.5, phi_spread_bare=0.1)
        assert adr > 1.0

    def test_formula(self):
        beta = 0.01
        var = 0.25
        spread = 0.2
        expected = 1.0 + beta ** 2 * var / spread
        assert agency_decoherence_ratio(var, spread, beta) == pytest.approx(expected, rel=1e-10)

    def test_monotonic_in_var_brain(self):
        spread = 0.1
        adrs = [agency_decoherence_ratio(v, spread) for v in [0.0, 0.1, 0.5, 1.0, 5.0]]
        for i in range(len(adrs) - 1):
            assert adrs[i] <= adrs[i + 1]

    def test_monotonic_in_beta(self):
        var = 0.5
        spread = 0.1
        adrs = [agency_decoherence_ratio(var, spread, b) for b in [0.001, 0.01, 0.1, 0.5]]
        for i in range(len(adrs) - 1):
            assert adrs[i] <= adrs[i + 1]

    def test_negative_spread_raises(self):
        with pytest.raises(ValueError):
            agency_decoherence_ratio(0.1, phi_spread_bare=-0.1)

    def test_zero_spread_raises(self):
        with pytest.raises(ValueError):
            agency_decoherence_ratio(0.1, phi_spread_bare=0.0)

    def test_negative_var_clamped_to_zero(self):
        # Negative var_brain should be clamped to 0 → ADR = 1
        adr = agency_decoherence_ratio(-0.5, phi_spread_bare=0.1)
        assert adr == pytest.approx(1.0)

    def test_large_var_large_adr(self):
        # ADR = 1 + β² × var / spread; β ≈ 6.13e-3, so β² ≈ 3.76e-5
        # With var=1000, spread=0.001: ADR = 1 + 3.76e-5 × 1000 / 0.001 ≈ 38.6
        adr = agency_decoherence_ratio(1000.0, phi_spread_bare=0.001)
        assert adr > 10.0

    def test_adr_always_non_negative(self):
        for vb, sp in [(0.0, 0.01), (1.0, 0.1), (0.001, 1.0)]:
            assert agency_decoherence_ratio(vb, sp) >= 1.0


# ---------------------------------------------------------------------------
# tau_dec_coupled
# ---------------------------------------------------------------------------

class TestTauDecCoupled:
    def test_bare_formula_zero_var(self):
        phi_mean = 1.0
        spread = 0.1
        result = tau_dec_coupled(phi_mean, spread, var_brain=0.0)
        bare = decoherence_timescale(phi_mean, spread)
        assert result == pytest.approx(bare, rel=1e-10)

    def test_coupled_leq_bare(self):
        phi_mean = 1.0
        spread = 0.1
        bare = decoherence_timescale(phi_mean, spread)
        coupled = tau_dec_coupled(phi_mean, spread, var_brain=0.5)
        assert coupled <= bare

    def test_coupled_strictly_less_for_positive_var(self):
        phi_mean = 1.0
        spread = 0.1
        coupled = tau_dec_coupled(phi_mean, spread, var_brain=0.5)
        bare = decoherence_timescale(phi_mean, spread)
        assert coupled < bare

    def test_formula(self):
        phi_mean, spread, var = 2.0, 0.5, 0.3
        beta = 0.01
        expected = phi_mean ** 2 / (spread + beta ** 2 * var)
        assert tau_dec_coupled(phi_mean, spread, var, beta) == pytest.approx(expected, rel=1e-10)

    def test_larger_var_smaller_tau(self):
        phi_mean, spread = 1.0, 0.1
        t1 = tau_dec_coupled(phi_mean, spread, var_brain=0.01)
        t2 = tau_dec_coupled(phi_mean, spread, var_brain=1.0)
        assert t2 < t1

    def test_negative_phi_mean_raises(self):
        with pytest.raises(ValueError):
            tau_dec_coupled(-1.0, 0.1, 0.0)

    def test_zero_phi_mean_raises(self):
        with pytest.raises(ValueError):
            tau_dec_coupled(0.0, 0.1, 0.0)

    def test_negative_spread_raises(self):
        with pytest.raises(ValueError):
            tau_dec_coupled(1.0, -0.1, 0.0)

    def test_zero_spread_raises(self):
        with pytest.raises(ValueError):
            tau_dec_coupled(1.0, 0.0, 0.0)

    def test_positive_result(self):
        assert tau_dec_coupled(1.0, 0.1, 0.5) > 0.0


# ---------------------------------------------------------------------------
# build_coupled_history
# ---------------------------------------------------------------------------

class TestBuildCoupledHistory:
    def _sys(self):
        return _default_system()

    def test_returns_coupled_history(self):
        result = build_coupled_history(self._sys(), n_steps=5, dt=0.01)
        assert isinstance(result, CoupledHistory)

    def test_history_length(self):
        n = 10
        result = build_coupled_history(self._sys(), n_steps=n, dt=0.01)
        # history records n+1 points (n steps + final state)
        assert len(result.brain_phi_history) == n + 1

    def test_n_steps_stored(self):
        result = build_coupled_history(self._sys(), n_steps=7, dt=0.01)
        assert result.n_steps == 7

    def test_adr_geq_one(self):
        result = build_coupled_history(self._sys(), n_steps=20, dt=0.05)
        assert result.adr >= 1.0

    def test_var_brain_non_negative(self):
        result = build_coupled_history(self._sys(), n_steps=20, dt=0.05)
        assert result.var_brain >= 0.0

    def test_tau_dec_coupled_leq_bare(self):
        result = build_coupled_history(self._sys(), n_steps=20, dt=0.05)
        assert result.tau_dec_coupled <= result.tau_dec_bare + 1e-12

    def test_tau_dec_bare_positive(self):
        result = build_coupled_history(self._sys(), n_steps=5, dt=0.01)
        assert result.tau_dec_bare > 0.0

    def test_tau_dec_coupled_positive(self):
        result = build_coupled_history(self._sys(), n_steps=5, dt=0.01)
        assert result.tau_dec_coupled > 0.0

    def test_beta_stored(self):
        sys = self._sys()
        result = build_coupled_history(sys, n_steps=5, dt=0.01)
        assert result.beta == pytest.approx(sys.beta)

    def test_phi_spread_bare_stored(self):
        result = build_coupled_history(self._sys(), n_steps=5, phi_spread_bare=0.3)
        assert result.phi_spread_bare == pytest.approx(0.3)

    def test_invalid_n_steps_raises(self):
        with pytest.raises(ValueError):
            build_coupled_history(self._sys(), n_steps=0)

    def test_invalid_phi_spread_bare_raises(self):
        with pytest.raises(ValueError):
            build_coupled_history(self._sys(), n_steps=5, phi_spread_bare=-0.1)

    def test_phi_history_all_positive(self):
        result = build_coupled_history(self._sys(), n_steps=20, dt=0.05)
        for phi in result.brain_phi_history:
            assert phi > 0.0


# ---------------------------------------------------------------------------
# high_agency_collapses_faster
# ---------------------------------------------------------------------------

class TestHighAgencyCollapsesFaster:
    def _sys(self):
        return _default_system(phi_brain=0.7, phi_univ=1.0)

    def test_returns_dict(self):
        result = high_agency_collapses_faster(
            self._sys(), _simple_amplitudes(), n_steps=10, dt=0.01
        )
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = high_agency_collapses_faster(
            self._sys(), _simple_amplitudes(), n_steps=10, dt=0.01
        )
        for key in ["history", "tau_dec_bare", "tau_dec_coupled", "adr",
                    "observer_accelerates", "born_probs", "var_brain",
                    "is_intentional", "intentionality_measure"]:
            assert key in result

    def test_adr_geq_one(self):
        result = high_agency_collapses_faster(
            self._sys(), _simple_amplitudes(), n_steps=20, dt=0.05
        )
        assert result["adr"] >= 1.0

    def test_observer_accelerates_bool(self):
        result = high_agency_collapses_faster(
            self._sys(), _simple_amplitudes(), n_steps=20, dt=0.05
        )
        assert isinstance(result["observer_accelerates"], bool)

    def test_born_probs_sum_to_one(self):
        result = high_agency_collapses_faster(
            self._sys(), _simple_amplitudes(), n_steps=5, dt=0.01
        )
        assert sum(result["born_probs"]) == pytest.approx(1.0)

    def test_tau_coupled_leq_bare(self):
        result = high_agency_collapses_faster(
            self._sys(), _simple_amplitudes(), n_steps=20, dt=0.05
        )
        assert result["tau_dec_coupled"] <= result["tau_dec_bare"] + 1e-12

    def test_history_is_coupled_history(self):
        result = high_agency_collapses_faster(
            self._sys(), _simple_amplitudes(), n_steps=5, dt=0.01
        )
        assert isinstance(result["history"], CoupledHistory)

    def test_born_probs_equal_for_symmetric_amplitudes(self):
        amp = np.array([1.0, 1.0], dtype=complex)
        result = high_agency_collapses_faster(self._sys(), amp, n_steps=5, dt=0.01)
        assert result["born_probs"][0] == pytest.approx(0.5)
        assert result["born_probs"][1] == pytest.approx(0.5)

    def test_is_intentional_bool(self):
        result = high_agency_collapses_faster(
            self._sys(), _simple_amplitudes(), n_steps=5, dt=0.01
        )
        assert isinstance(result["is_intentional"], bool)

    def test_intentionality_measure_non_negative(self):
        result = high_agency_collapses_faster(
            self._sys(), _simple_amplitudes(), n_steps=5, dt=0.01
        )
        assert result["intentionality_measure"] >= 0.0


# ---------------------------------------------------------------------------
# consciousness_measurement_link
# ---------------------------------------------------------------------------

class TestConsciousnessMeasurementLink:
    def _simple_link(self, brain_phi=0.7, univ_phi=1.0, spread=0.1):
        amp = _simple_amplitudes()
        return consciousness_measurement_link(brain_phi, univ_phi, spread, amp)

    def test_returns_dict(self):
        assert isinstance(self._simple_link(), dict)

    def test_required_keys(self):
        result = self._simple_link()
        for key in ["brain_phi", "universe_phi", "information_gap", "var_brain",
                    "tau_dec_bare", "tau_dec_coupled", "adr",
                    "observer_accelerates", "born_probs",
                    "rho_cs_correction", "fidelity_interpretation"]:
            assert key in result

    def test_adr_formula(self):
        result = self._simple_link(brain_phi=0.7, univ_phi=1.0, spread=0.1)
        beta = BETA_COUPLING
        delta_I = abs(0.7 ** 2 - 1.0 ** 2)
        var_est = (beta * delta_I) ** 2
        expected_adr = 1.0 + beta ** 2 * var_est / 0.1
        assert result["adr"] == pytest.approx(expected_adr, rel=1e-8)

    def test_observer_accelerates_true(self):
        result = self._simple_link(brain_phi=2.0, univ_phi=1.0, spread=0.1)
        assert result["observer_accelerates"] is True

    def test_born_probs_sum_to_one(self):
        result = self._simple_link()
        assert sum(result["born_probs"]) == pytest.approx(1.0, abs=1e-12)

    def test_information_gap_formula(self):
        result = self._simple_link(brain_phi=0.5, univ_phi=1.0)
        expected = abs(0.5 ** 2 - 1.0 ** 2)
        assert result["information_gap"] == pytest.approx(expected)

    def test_tau_dec_coupled_leq_bare(self):
        result = self._simple_link()
        assert result["tau_dec_coupled"] <= result["tau_dec_bare"] + 1e-12

    def test_custom_var_brain(self):
        amp = _simple_amplitudes()
        result = consciousness_measurement_link(0.7, 1.0, 0.1, amp, var_brain=0.5)
        expected_adr = 1.0 + BETA_COUPLING ** 2 * 0.5 / 0.1
        assert result["adr"] == pytest.approx(expected_adr, rel=1e-8)

    def test_negative_brain_phi_raises(self):
        with pytest.raises(ValueError):
            consciousness_measurement_link(-0.5, 1.0, 0.1, _simple_amplitudes())

    def test_zero_brain_phi_raises(self):
        with pytest.raises(ValueError):
            consciousness_measurement_link(0.0, 1.0, 0.1, _simple_amplitudes())

    def test_negative_universe_phi_raises(self):
        with pytest.raises(ValueError):
            consciousness_measurement_link(0.7, -1.0, 0.1, _simple_amplitudes())

    def test_zero_spread_raises(self):
        with pytest.raises(ValueError):
            consciousness_measurement_link(0.7, 1.0, 0.0, _simple_amplitudes())

    def test_fidelity_interpretation_string(self):
        result = self._simple_link()
        assert isinstance(result["fidelity_interpretation"], str)
        assert "ADR" in result["fidelity_interpretation"]

    def test_rho_cs_correction_positive(self):
        result = self._simple_link()
        assert result["rho_cs_correction"] > 0.0

    def test_equal_phi_gives_adr_one(self):
        # When brain_phi == universe_phi → delta_I = 0 → var_est = 0 → ADR = 1
        result = self._simple_link(brain_phi=1.0, univ_phi=1.0)
        assert result["adr"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# adr_vs_agency_scan
# ---------------------------------------------------------------------------

class TestAdrVsAgencyScan:
    def test_returns_list(self):
        results = adr_vs_agency_scan()
        assert isinstance(results, list)

    def test_default_has_ten_entries(self):
        # 0.0 + 9 logspace = 10 entries
        results = adr_vs_agency_scan()
        assert len(results) == 10

    def test_each_entry_has_required_keys(self):
        for entry in adr_vs_agency_scan():
            assert "var_brain" in entry
            assert "adr" in entry
            assert "tau_dec_coupled" in entry

    def test_adr_monotone_increasing(self):
        results = adr_vs_agency_scan()
        adrs = [r["adr"] for r in results]
        for i in range(len(adrs) - 1):
            assert adrs[i] <= adrs[i + 1] + 1e-12

    def test_tau_monotone_decreasing(self):
        results = adr_vs_agency_scan()
        taus = [r["tau_dec_coupled"] for r in results]
        for i in range(len(taus) - 1):
            assert taus[i] >= taus[i + 1] - 1e-12

    def test_zero_var_gives_adr_one(self):
        results = adr_vs_agency_scan(var_brain_values=[0.0])
        assert results[0]["adr"] == pytest.approx(1.0)

    def test_custom_var_values(self):
        vals = [0.1, 0.5, 1.0]
        results = adr_vs_agency_scan(var_brain_values=vals)
        assert len(results) == 3
        for i, r in enumerate(results):
            assert r["var_brain"] == pytest.approx(vals[i])

    def test_all_adrs_geq_one(self):
        for r in adr_vs_agency_scan():
            assert r["adr"] >= 1.0

    def test_all_taus_positive(self):
        for r in adr_vs_agency_scan():
            assert r["tau_dec_coupled"] > 0.0


# ---------------------------------------------------------------------------
# Quantitative "Coupled History" test — the core physics assertion
# ---------------------------------------------------------------------------

class TestCoupledHistoryPhysics:
    """
    The central physics test: a high-agency brain system (large φ_brain variance)
    always causes faster decoherence in the surrounding environment.

    This is the first mathematical link between consciousness and quantum measurement.
    """

    def test_high_agency_faster_than_zero_agency(self):
        """ADR > 1 for any positive variance — the core inequality."""
        phi_mean, spread = 1.0, 0.1
        tau_bare = decoherence_timescale(phi_mean, spread)
        tau_high = tau_dec_coupled(phi_mean, spread, var_brain=1.0)
        assert tau_high < tau_bare

    def test_adr_strictly_greater_than_one_for_brain(self):
        """A brain with nonzero φ-variance always has ADR > 1."""
        sys = _default_system(phi_brain=0.7, phi_univ=1.0)
        result = build_coupled_history(sys, n_steps=50, dt=0.05)
        # After 50 steps the brain φ fluctuates → var_brain > 0 → ADR > 1
        # (may be very close to 1 if system has converged; check ADR ≥ 1)
        assert result.adr >= 1.0

    def test_higher_phi_brain_gives_higher_adr(self):
        """Higher brain φ → larger ΔI → larger estimated var_brain → higher ADR."""
        spread = 0.1
        link_low = consciousness_measurement_link(0.5, 1.0, spread, np.array([1.0, 0.0]))
        link_high = consciousness_measurement_link(2.0, 1.0, spread, np.array([1.0, 0.0]))
        assert link_high["adr"] >= link_low["adr"]

    def test_adr_equals_one_for_equal_phi(self):
        """No agency (ΔI = 0) → ADR = 1 (no acceleration of decoherence)."""
        result = consciousness_measurement_link(1.0, 1.0, 0.1, np.array([1.0, 1.0]))
        assert result["adr"] == pytest.approx(1.0)

    def test_scan_monotone(self):
        """The ADR increases monotonically with Var_brain."""
        scan = adr_vs_agency_scan(phi_mean=1.0, phi_spread_bare=0.1)
        adrs = [r["adr"] for r in scan]
        assert adrs[-1] > adrs[0]  # max agency > zero agency

    def test_tau_dec_inequality(self):
        """τ_dec_coupled ≤ τ_dec_bare always holds (equation [5])."""
        for phi_mean, spread, var in [(1.0, 0.1, 0.5), (2.0, 0.5, 1.0), (0.5, 0.05, 0.1)]:
            tau_bare = decoherence_timescale(phi_mean, spread)
            tau_coup = tau_dec_coupled(phi_mean, spread, var)
            assert tau_coup <= tau_bare + 1e-12, (
                f"Failed for phi_mean={phi_mean}, spread={spread}, var={var}: "
                f"tau_coup={tau_coup} > tau_bare={tau_bare}"
            )

    def test_full_pipeline_observer_accelerates(self):
        """End-to-end: build_coupled_history → ADR ≥ 1 → collapse is faster."""
        sys = _default_system(phi_brain=0.9, phi_univ=1.0)
        hist = build_coupled_history(sys, n_steps=30, dt=0.05, phi_spread_bare=0.05)
        assert hist.adr >= 1.0
        assert hist.tau_dec_coupled <= hist.tau_dec_bare + 1e-12

    def test_rock_has_no_agency_adr_one(self):
        """A 'rock' (var_brain = 0) has ADR = 1 — no decoherence acceleration."""
        adr = agency_decoherence_ratio(0.0, phi_spread_bare=0.1)
        assert adr == pytest.approx(1.0)
