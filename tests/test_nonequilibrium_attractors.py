# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_nonequilibrium_attractors.py
========================================
Tests for src/core/nonequilibrium_attractors.py — Pillar 110.
"""

import cmath
import math
import pytest

from src.core.nonequilibrium_attractors import (
    K_CS,
    WINDING_NUMBER,
    attractor_zoo,
    dissipative_attractor_dimension,
    ftum_floquet_eigenvalue,
    lyapunov_exponent_periodic,
    nonequilibrium_summary,
    time_crystal_period,
)

# ── ftum_floquet_eigenvalue ───────────────────────────────────────────────────

class TestFTUMFloquetEigenvalue:

    def test_returns_complex(self):
        lam = ftum_floquet_eigenvalue(period_tau=1.0)
        assert isinstance(lam, complex)

    def test_modulus_is_one(self):
        for tau in (0.5, 1.0, 2.0, 10.0, 100.0):
            lam = ftum_floquet_eigenvalue(period_tau=tau)
            assert abs(abs(lam) - 1.0) < 1e-12, f"tau={tau}: |λ|={abs(lam)}"

    def test_modulus_one_different_phi0(self):
        for phi0 in (0.5, 1.0, 1.5, 2.0):
            lam = ftum_floquet_eigenvalue(period_tau=1.0, phi0=phi0)
            assert abs(abs(lam) - 1.0) < 1e-12

    def test_modulus_one_different_k_cs(self):
        for k in (10, 37, 74, 100):
            lam = ftum_floquet_eigenvalue(period_tau=1.0, k_cs=k)
            assert abs(abs(lam) - 1.0) < 1e-12

    def test_phase_formula(self):
        tau, phi0, k_cs = 2.0, 1.0, 74
        lam = ftum_floquet_eigenvalue(period_tau=tau, phi0=phi0, k_cs=k_cs)
        expected_phase = 2.0 * math.pi * phi0**2 / (k_cs * tau)
        assert abs(cmath.phase(lam) - expected_phase) < 1e-12

    def test_raises_for_zero_tau(self):
        with pytest.raises(ValueError):
            ftum_floquet_eigenvalue(period_tau=0.0)

    def test_raises_for_negative_tau(self):
        with pytest.raises(ValueError):
            ftum_floquet_eigenvalue(period_tau=-1.0)

    def test_raises_for_zero_k_cs(self):
        with pytest.raises(ValueError):
            ftum_floquet_eigenvalue(period_tau=1.0, k_cs=0)

    def test_raises_for_negative_k_cs(self):
        with pytest.raises(ValueError):
            ftum_floquet_eigenvalue(period_tau=1.0, k_cs=-1)

    def test_phi0_zero_gives_plus_one(self):
        lam = ftum_floquet_eigenvalue(period_tau=1.0, phi0=0.0)
        assert abs(lam - 1.0) < 1e-12

    def test_large_tau_approaches_plus_one(self):
        lam = ftum_floquet_eigenvalue(period_tau=1e10)
        assert abs(lam - 1.0) < 1e-5

    def test_modulus_one_for_default(self):
        lam = ftum_floquet_eigenvalue(period_tau=time_crystal_period())
        assert abs(abs(lam) - 1.0) < 1e-12


# ── time_crystal_period ───────────────────────────────────────────────────────

class TestTimeCrystalPeriod:

    def test_positive(self):
        assert time_crystal_period() > 0.0

    def test_default_value(self):
        expected = 2.0 * math.pi * 74 / (25 * 1.0)
        assert abs(time_crystal_period() - expected) < 1e-12

    def test_approx_18_59(self):
        t = time_crystal_period()
        assert 18.0 < t < 19.5

    def test_scales_with_k_cs(self):
        t1 = time_crystal_period(k_cs=74)
        t2 = time_crystal_period(k_cs=148)
        assert abs(t2 / t1 - 2.0) < 1e-12

    def test_decreases_with_n_w(self):
        t5 = time_crystal_period(n_w=5)
        t7 = time_crystal_period(n_w=7)
        assert t5 > t7

    def test_scales_inversely_with_n_w_squared(self):
        t5 = time_crystal_period(n_w=5)
        t10 = time_crystal_period(n_w=10)
        assert abs(t5 / t10 - 4.0) < 1e-10

    def test_raises_for_zero_n_w(self):
        with pytest.raises(ValueError):
            time_crystal_period(n_w=0)

    def test_raises_for_negative_n_w(self):
        with pytest.raises(ValueError):
            time_crystal_period(n_w=-1)

    def test_raises_for_zero_k_cs(self):
        with pytest.raises(ValueError):
            time_crystal_period(k_cs=0)

    def test_raises_for_zero_phi0(self):
        with pytest.raises(ValueError):
            time_crystal_period(phi0=0.0)

    def test_scales_inversely_with_phi0_squared(self):
        t1 = time_crystal_period(phi0=1.0)
        t2 = time_crystal_period(phi0=2.0)
        assert abs(t1 / t2 - 4.0) < 1e-10

    def test_returns_float(self):
        assert isinstance(time_crystal_period(), float)


# ── dissipative_attractor_dimension ──────────────────────────────────────────

class TestDissipativeAttractorDimension:

    def test_default_is_4(self):
        assert dissipative_attractor_dimension() == 4

    def test_equals_n_w_minus_1(self):
        for n in (1, 3, 5, 7, 10):
            assert dissipative_attractor_dimension(n_w=n) == n - 1

    def test_returns_int(self):
        assert isinstance(dissipative_attractor_dimension(), int)

    def test_minimum_is_zero(self):
        assert dissipative_attractor_dimension(n_w=1) == 0

    def test_raises_for_zero_n_w(self):
        with pytest.raises(ValueError):
            dissipative_attractor_dimension(n_w=0)

    def test_raises_for_negative_n_w(self):
        with pytest.raises(ValueError):
            dissipative_attractor_dimension(n_w=-1)

    def test_large_n_w(self):
        assert dissipative_attractor_dimension(n_w=100) == 99


# ── lyapunov_exponent_periodic ───────────────────────────────────────────────

class TestLyapunovExponentPeriodic:

    def test_zero_at_phi0_1(self):
        assert abs(lyapunov_exponent_periodic(phi0=1.0)) < 1e-15

    def test_negative_for_phi0_greater_1(self):
        for phi0 in (1.01, 1.1, 1.5, 2.0):
            assert lyapunov_exponent_periodic(phi0=phi0) < 0.0, f"phi0={phi0}"

    def test_positive_for_phi0_less_1(self):
        for phi0 in (0.01, 0.5, 0.9, 0.99):
            assert lyapunov_exponent_periodic(phi0=phi0) > 0.0, f"phi0={phi0}"

    def test_formula(self):
        phi0, k_cs = 1.5, 74
        expected = phi0**2 / k_cs * (1.0 - phi0)
        assert abs(lyapunov_exponent_periodic(phi0, k_cs) - expected) < 1e-15

    def test_raises_for_zero_k_cs(self):
        with pytest.raises(ValueError):
            lyapunov_exponent_periodic(k_cs=0)

    def test_raises_for_negative_k_cs(self):
        with pytest.raises(ValueError):
            lyapunov_exponent_periodic(k_cs=-1)

    def test_returns_float(self):
        assert isinstance(lyapunov_exponent_periodic(), float)

    def test_continuous_through_phi0_1(self):
        lam_low = lyapunov_exponent_periodic(phi0=0.999)
        lam_one = lyapunov_exponent_periodic(phi0=1.000)
        lam_high = lyapunov_exponent_periodic(phi0=1.001)
        # Should be small and sign should flip
        assert lam_low > 0
        assert abs(lam_one) < 1e-14
        assert lam_high < 0

    def test_scales_with_phi0_squared_near_zero(self):
        # φ₀ small: λ_L ≈ φ₀²/k_cs (1 - φ₀) ≈ φ₀²/k_cs
        phi0 = 0.1
        lam = lyapunov_exponent_periodic(phi0=phi0)
        approx = phi0**2 / K_CS
        assert abs(lam - approx * (1 - phi0)) < 1e-15


# ── attractor_zoo ─────────────────────────────────────────────────────────────

class TestAttractorZoo:

    def test_returns_list(self):
        assert isinstance(attractor_zoo(), list)

    def test_length_is_3(self):
        assert len(attractor_zoo()) == 3

    def test_all_dicts(self):
        for item in attractor_zoo():
            assert isinstance(item, dict)

    def test_required_keys(self):
        for item in attractor_zoo():
            for key in ("type", "period", "dimension"):
                assert key in item

    def test_fixed_point_entry(self):
        zoo = attractor_zoo()
        fp = next(x for x in zoo if x["type"] == "fixed_point")
        assert fp["period"] == 0
        assert fp["dimension"] == 0

    def test_limit_cycle_entry(self):
        zoo = attractor_zoo()
        lc = next(x for x in zoo if x["type"] == "limit_cycle")
        assert lc["period"] > 0
        assert lc["dimension"] == 1

    def test_quasi_periodic_entry(self):
        zoo = attractor_zoo()
        qp = next(x for x in zoo if x["type"] == "quasi_periodic")
        assert math.isinf(qp["period"])
        assert qp["dimension"] == 2

    def test_limit_cycle_period_matches_time_crystal(self):
        zoo = attractor_zoo()
        lc = next(x for x in zoo if x["type"] == "limit_cycle")
        assert abs(lc["period"] - time_crystal_period()) < 1e-12

    def test_types_are_strings(self):
        for item in attractor_zoo():
            assert isinstance(item["type"], str)

    def test_dimensions_are_non_negative(self):
        for item in attractor_zoo():
            assert item["dimension"] >= 0

    def test_dimensions_non_decreasing_by_type(self):
        zoo = attractor_zoo()
        dims = [x["dimension"] for x in zoo]
        assert dims == sorted(dims)


# ── nonequilibrium_summary ────────────────────────────────────────────────────

class TestNonequilibriumSummary:

    def test_returns_dict(self):
        assert isinstance(nonequilibrium_summary(), dict)

    def test_required_keys(self):
        s = nonequilibrium_summary()
        for key in ("time_crystal_period", "attractor_dimension",
                    "lyapunov_at_phi0_1", "n_attractor_types"):
            assert key in s

    def test_time_crystal_period_positive(self):
        assert nonequilibrium_summary()["time_crystal_period"] > 0.0

    def test_time_crystal_period_matches_function(self):
        s = nonequilibrium_summary()
        assert abs(s["time_crystal_period"] - time_crystal_period()) < 1e-12

    def test_attractor_dimension_is_4(self):
        assert nonequilibrium_summary()["attractor_dimension"] == 4

    def test_lyapunov_at_phi0_1_is_zero(self):
        assert abs(nonequilibrium_summary()["lyapunov_at_phi0_1"]) < 1e-15

    def test_n_attractor_types_is_3(self):
        assert nonequilibrium_summary()["n_attractor_types"] == 3

    def test_no_none_values(self):
        s = nonequilibrium_summary()
        for v in s.values():
            assert v is not None

    def test_attractor_dimension_returns_int(self):
        s = nonequilibrium_summary()
        assert isinstance(s["attractor_dimension"], int)

    def test_n_attractor_types_matches_zoo(self):
        s = nonequilibrium_summary()
        assert s["n_attractor_types"] == len(attractor_zoo())
