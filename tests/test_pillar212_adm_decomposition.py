# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar212_adm_decomposition.py
==========================================
Tests for Pillar 212 — ADM 3+1+1 Decomposition.

Covers:
  - adm_5d_metric
  - hamiltonian_constraint
  - momentum_constraint
  - ricci_to_adm_time_coincidence
  - entropy_production_rate_adm
  - adm_consistency_check
  - pillar212_summary
  - Input validation and physical properties
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar212_adm_decomposition import (
    adm_5d_metric,
    hamiltonian_constraint,
    momentum_constraint,
    ricci_to_adm_time_coincidence,
    entropy_production_rate_adm,
    adm_consistency_check,
    pillar212_summary,
    PHI_0_FTUM,
    _TOL,
)

# ---------------------------------------------------------------------------
# adm_5d_metric — basic interface
# ---------------------------------------------------------------------------

class TestAdm5dMetric:

    def test_returns_dict(self):
        result = adm_5d_metric()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = adm_5d_metric()
        for key in ("lapse_N", "shift_N_i", "gamma_3metric",
                    "G_55_radion", "phi", "lapse_at_ftum",
                    "time_coincidence", "metric_signature"):
            assert key in result

    # phi = 1 (FTUM fixed point)

    def test_lapse_at_phi1_is_unity(self):
        r = adm_5d_metric(phi=1.0)
        assert abs(r["lapse_N"] - 1.0) < _TOL

    def test_G55_at_phi1(self):
        r = adm_5d_metric(phi=1.0)
        assert abs(r["G_55_radion"] - 1.0) < _TOL

    def test_time_coincidence_at_phi1(self):
        r = adm_5d_metric(phi=1.0)
        assert r["time_coincidence"] is True

    def test_lapse_at_ftum_is_unity(self):
        r = adm_5d_metric(phi=2.0)
        assert abs(r["lapse_at_ftum"] - 1.0) < _TOL

    # phi = 4 → N = 0.5

    def test_lapse_at_phi4(self):
        r = adm_5d_metric(phi=4.0)
        assert abs(r["lapse_N"] - 0.5) < _TOL

    def test_G55_at_phi4(self):
        r = adm_5d_metric(phi=4.0)
        assert abs(r["G_55_radion"] - 16.0) < _TOL

    def test_shift_is_zero(self):
        r = adm_5d_metric()
        assert r["shift_N_i"] == [0.0, 0.0, 0.0]

    def test_gamma_3metric_label(self):
        r = adm_5d_metric()
        assert r["gamma_3metric"] == "flat_isotropic"

    def test_metric_signature(self):
        r = adm_5d_metric()
        assert r["metric_signature"] == "-+++++"

    def test_phi_echoed(self):
        r = adm_5d_metric(phi=3.0)
        assert abs(r["phi"] - 3.0) < _TOL

    # lapse formula N = phi^{-1/2}

    def test_lapse_formula_various(self):
        for phi in [0.25, 0.5, 2.0, 9.0]:
            r = adm_5d_metric(phi=phi)
            expected = phi ** (-0.5)
            assert abs(r["lapse_N"] - expected) < 1e-12, (
                f"phi={phi}: expected N={expected}, got {r['lapse_N']}"
            )

    # Input validation

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            adm_5d_metric(phi=0.0)

    def test_phi_negative_raises(self):
        with pytest.raises(ValueError):
            adm_5d_metric(phi=-1.0)

    def test_lapse_positive_for_positive_phi(self):
        for phi in [0.01, 0.5, 1.0, 2.0, 100.0]:
            r = adm_5d_metric(phi=phi)
            assert r["lapse_N"] > 0.0


# ---------------------------------------------------------------------------
# hamiltonian_constraint
# ---------------------------------------------------------------------------

class TestHamiltonianConstraint:

    def test_returns_dict(self):
        r = hamiltonian_constraint()
        assert isinstance(r, dict)

    def test_required_keys(self):
        r = hamiltonian_constraint()
        for key in ("K_trace", "K_squared", "R_3d",
                    "hamiltonian_value", "constraint_satisfied",
                    "hubble_rate", "phi"):
            assert key in r

    # H = 0 vacuum: constraint satisfied

    def test_vacuum_constraint_satisfied(self):
        r = hamiltonian_constraint(phi=1.0, H_hubble=0.0)
        assert r["constraint_satisfied"] is True

    def test_vacuum_hamiltonian_value_zero(self):
        r = hamiltonian_constraint(phi=1.0, H_hubble=0.0)
        assert abs(r["hamiltonian_value"]) < _TOL

    def test_vacuum_K_trace_zero(self):
        r = hamiltonian_constraint(phi=1.0, H_hubble=0.0)
        assert abs(r["K_trace"]) < _TOL

    def test_vacuum_K_squared_zero(self):
        r = hamiltonian_constraint(phi=1.0, H_hubble=0.0)
        assert abs(r["K_squared"]) < _TOL

    def test_R_3d_is_zero(self):
        r = hamiltonian_constraint(phi=1.0, H_hubble=0.1)
        assert r["R_3d"] == 0.0

    # H = 0.1

    def test_K_trace_at_H01(self):
        r = hamiltonian_constraint(phi=1.0, H_hubble=0.1)
        assert abs(r["K_trace"] - (-0.3)) < 1e-12

    def test_K_squared_at_H01(self):
        r = hamiltonian_constraint(phi=1.0, H_hubble=0.1)
        assert abs(r["K_squared"] - 0.03) < 1e-12

    def test_hubble_rate_echoed(self):
        r = hamiltonian_constraint(phi=1.0, H_hubble=0.1)
        assert abs(r["hubble_rate"] - 0.1) < _TOL

    # phi validation

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            hamiltonian_constraint(phi=0.0)

    def test_phi_negative_raises(self):
        with pytest.raises(ValueError):
            hamiltonian_constraint(phi=-2.0)


# ---------------------------------------------------------------------------
# momentum_constraint
# ---------------------------------------------------------------------------

class TestMomentumConstraint:

    def test_value_is_zero(self):
        r = momentum_constraint()
        assert r["momentum_constraint_value"] == 0.0

    def test_satisfied_true(self):
        r = momentum_constraint()
        assert r["satisfied"] is True

    def test_reason_non_empty(self):
        r = momentum_constraint()
        assert isinstance(r["reason"], str) and len(r["reason"]) > 10

    def test_satisfied_for_various_phi(self):
        for phi in [0.1, 0.5, 1.0, 2.0, 10.0]:
            r = momentum_constraint(phi=phi)
            assert r["satisfied"] is True

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            momentum_constraint(phi=0.0)

    def test_phi_negative_raises(self):
        with pytest.raises(ValueError):
            momentum_constraint(phi=-0.5)


# ---------------------------------------------------------------------------
# ricci_to_adm_time_coincidence
# ---------------------------------------------------------------------------

class TestRicciToAdmTimeCoincidence:

    def test_returns_dict(self):
        r = ricci_to_adm_time_coincidence()
        assert isinstance(r, dict)

    def test_required_keys(self):
        r = ricci_to_adm_time_coincidence()
        for key in ("phi_0", "lapse_at_phi0", "omega_at_phi0",
                    "dt_coord_equals_dt_ricci", "gap_closed",
                    "proof_statement", "caveat"):
            assert key in r

    # phi_0 = 1 (FTUM fixed point)

    def test_lapse_at_phi0_1(self):
        r = ricci_to_adm_time_coincidence(phi_0=1.0)
        assert abs(r["lapse_at_phi0"] - 1.0) < _TOL

    def test_omega_at_phi0_1(self):
        r = ricci_to_adm_time_coincidence(phi_0=1.0)
        assert abs(r["omega_at_phi0"] - 1.0) < _TOL

    def test_dt_coord_equals_dt_ricci_at_phi0_1(self):
        r = ricci_to_adm_time_coincidence(phi_0=1.0)
        assert r["dt_coord_equals_dt_ricci"] is True

    def test_gap_closed_at_phi0_1(self):
        r = ricci_to_adm_time_coincidence(phi_0=1.0)
        assert r["gap_closed"] is True

    # phi_0 = 2 (off attractor)

    def test_lapse_at_phi0_2(self):
        r = ricci_to_adm_time_coincidence(phi_0=2.0)
        assert abs(r["lapse_at_phi0"] - 2.0 ** (-0.5)) < _TOL

    def test_gap_not_closed_at_phi0_2(self):
        r = ricci_to_adm_time_coincidence(phi_0=2.0)
        assert r["gap_closed"] is False

    def test_dt_not_equal_at_phi0_2(self):
        r = ricci_to_adm_time_coincidence(phi_0=2.0)
        assert r["dt_coord_equals_dt_ricci"] is False

    def test_proof_statement_non_empty(self):
        r = ricci_to_adm_time_coincidence()
        assert isinstance(r["proof_statement"], str) and len(r["proof_statement"]) > 20

    def test_caveat_mentions_quantization(self):
        r = ricci_to_adm_time_coincidence()
        assert "quantization" in r["caveat"].lower() or "open" in r["caveat"].lower()

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            ricci_to_adm_time_coincidence(phi_0=0.0)

    def test_phi_negative_raises(self):
        with pytest.raises(ValueError):
            ricci_to_adm_time_coincidence(phi_0=-1.0)


# ---------------------------------------------------------------------------
# entropy_production_rate_adm
# ---------------------------------------------------------------------------

class TestEntropyProductionRateAdm:

    def test_returns_dict(self):
        r = entropy_production_rate_adm()
        assert isinstance(r, dict)

    def test_required_keys(self):
        r = entropy_production_rate_adm()
        for key in ("phi", "phi_dot", "lapse_N", "dS_dt_ricci",
                    "dS_dt_adm", "equals_ricci_at_attractor", "status"):
            assert key in r

    # At attractor phi=1

    def test_lapse_at_phi1(self):
        r = entropy_production_rate_adm(phi=1.0, phi_dot=1.0)
        assert abs(r["lapse_N"] - 1.0) < _TOL

    def test_dS_adm_equals_dS_ricci_at_phi1(self):
        r = entropy_production_rate_adm(phi=1.0, phi_dot=1.0)
        assert abs(r["dS_dt_adm"] - r["dS_dt_ricci"]) < _TOL

    def test_equals_ricci_at_attractor_true(self):
        r = entropy_production_rate_adm(phi=1.0, phi_dot=0.5)
        assert r["equals_ricci_at_attractor"] is True

    def test_zero_phi_dot_gives_zero_dS(self):
        r = entropy_production_rate_adm(phi=1.0, phi_dot=0.0)
        assert abs(r["dS_dt_ricci"]) < _TOL
        assert abs(r["dS_dt_adm"]) < _TOL

    # Off attractor phi=0.5 → N = sqrt(2)

    def test_lapse_at_phi_half(self):
        r = entropy_production_rate_adm(phi=0.5, phi_dot=1.0)
        expected_N = 0.5 ** (-0.5)   # = sqrt(2)
        assert abs(r["lapse_N"] - expected_N) < 1e-12

    def test_dS_adm_ne_dS_ricci_at_phi_half(self):
        r = entropy_production_rate_adm(phi=0.5, phi_dot=1.0)
        # N != 1 → ADM rate != Ricci rate
        assert abs(r["dS_dt_adm"] - r["dS_dt_ricci"]) > 1e-8

    # ADM rate = N * Ricci rate (general)

    def test_adm_equals_N_times_ricci(self):
        for phi, phi_dot in [(0.25, 2.0), (2.0, -1.0), (1.5, 0.3)]:
            r = entropy_production_rate_adm(phi=phi, phi_dot=phi_dot)
            expected = r["lapse_N"] * r["dS_dt_ricci"]
            assert abs(r["dS_dt_adm"] - expected) < 1e-12

    # Input validation

    def test_phi_zero_raises(self):
        with pytest.raises(ValueError):
            entropy_production_rate_adm(phi=0.0)

    def test_phi_negative_raises(self):
        with pytest.raises(ValueError):
            entropy_production_rate_adm(phi=-1.0)


# ---------------------------------------------------------------------------
# adm_consistency_check
# ---------------------------------------------------------------------------

class TestAdmConsistencyCheck:

    def test_returns_dict(self):
        r = adm_consistency_check()
        assert isinstance(r, dict)

    def test_all_passed(self):
        r = adm_consistency_check(n_samples=20)
        assert r["all_passed"] is True

    def test_attractor_rates_equal(self):
        r = adm_consistency_check()
        assert r["attractor_rates_equal"] is True

    def test_lapse_monotone_decreasing(self):
        r = adm_consistency_check()
        assert r["lapse_monotone_decreasing"] is True

    def test_hamiltonian_vacuum_satisfied(self):
        r = adm_consistency_check()
        assert r["hamiltonian_vacuum_satisfied"] is True

    def test_momentum_satisfied(self):
        r = adm_consistency_check()
        assert r["momentum_satisfied"] is True

    def test_n_samples_echoed(self):
        r = adm_consistency_check(n_samples=15)
        assert r["n_samples"] == 15


# ---------------------------------------------------------------------------
# pillar212_summary
# ---------------------------------------------------------------------------

class TestPillar212Summary:

    def test_returns_dict(self):
        r = pillar212_summary()
        assert isinstance(r, dict)

    def test_pillar_number(self):
        r = pillar212_summary()
        assert r["pillar"] == 212

    def test_gap_closed(self):
        r = pillar212_summary()
        assert r["gap_closed"] is True

    def test_time_coincidence(self):
        r = pillar212_summary()
        assert r["time_coincidence"] is True

    def test_hamiltonian_satisfied(self):
        r = pillar212_summary()
        assert r["hamiltonian_satisfied"] is True

    def test_momentum_satisfied(self):
        r = pillar212_summary()
        assert r["momentum_satisfied"] is True

    def test_consistency_all_passed(self):
        r = pillar212_summary()
        assert r["consistency_all_passed"] is True

    def test_lapse_at_ftum(self):
        r = pillar212_summary()
        assert abs(r["lapse_at_ftum"] - 1.0) < _TOL

    def test_dS_rates_equal(self):
        r = pillar212_summary()
        assert r["dS_rates_equal_at_attractor"] is True


# ---------------------------------------------------------------------------
# Physical properties
# ---------------------------------------------------------------------------

class TestPhysicalProperties:

    def test_lapse_positive_all_phi(self):
        """N = phi^{-1/2} > 0 for all phi > 0."""
        for phi in [0.001, 0.1, 1.0, 5.0, 100.0]:
            r = adm_5d_metric(phi=phi)
            assert r["lapse_N"] > 0.0

    def test_lapse_monotone_decreasing(self):
        """N decreases strictly as phi increases."""
        phis = [0.5, 1.0, 2.0, 4.0, 8.0]
        lapses = [adm_5d_metric(phi=p)["lapse_N"] for p in phis]
        for i in range(len(lapses) - 1):
            assert lapses[i] > lapses[i + 1], (
                f"N not decreasing: N({phis[i]})={lapses[i]} "
                f"vs N({phis[i+1]})={lapses[i+1]}"
            )

    def test_hamiltonian_vacuum_across_phi(self):
        """Vacuum Hamiltonian constraint satisfied for all phi > 0."""
        for phi in [0.1, 0.5, 1.0, 2.0, 10.0]:
            r = hamiltonian_constraint(phi=phi, H_hubble=0.0)
            assert r["constraint_satisfied"] is True

    def test_provenance_dict_present(self):
        from src.core.pillar212_adm_decomposition import __provenance__
        assert __provenance__["pillar"] == 212
        assert "closes_gap" in __provenance__
