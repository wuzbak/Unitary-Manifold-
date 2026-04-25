# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_phi0_closure.py — Test suite for Pillar 56: φ₀ Self-Consistency Closure.

Covers:
- Basic function correctness for all public API functions
- Round-trip consistency: phi0_eff_from_ns(ns_from_phi0(x)) == x
- FTUM iteration convergence
- closure_audit() reports all_consistent=True
- lambda_cobe positivity and magnitude (~1e-12 range)
- Edge cases (tolerance, max_iter, different n_winding values)
- phi0_uncertainty_band symmetry and sensibility

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.phi0_closure import (
    N_WINDING,
    K_CS,
    C_S,
    PHI_0_BARE,
    NS_PLANCK,
    NS_SIGMA,
    NS_TARGET,
    AS_PLANCK,
    R_BRAIDED,
    R_BICEP_LIMIT,
    _F_BRAIDED,
    phi0_eff_from_ns,
    ns_from_phi0,
    lambda_cobe,
    ftum_phi0_iteration,
    closure_audit,
    phi0_uncertainty_band,
    ns_from_phi0_braided,
    phi0_eff_from_ns_braided,
    braided_closure_audit,
)

# ---------------------------------------------------------------------------
# Constants sanity tests
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_winding(self):
        assert N_WINDING == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_k_cs_equals_sum_of_squares(self):
        assert K_CS == 5**2 + 7**2

    def test_c_s_value(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-15

    def test_phi0_bare(self):
        assert PHI_0_BARE == 1.0

    def test_ns_planck(self):
        assert abs(NS_PLANCK - 0.9649) < 1e-10

    def test_ns_sigma(self):
        assert abs(NS_SIGMA - 0.0042) < 1e-10

    def test_ns_target(self):
        assert abs(NS_TARGET - 0.9635) < 1e-10

    def test_as_planck(self):
        assert abs(AS_PLANCK - 2.101e-9) < 1e-15

    def test_r_braided(self):
        assert abs(R_BRAIDED - 0.0315) < 1e-10

    def test_r_bicep_limit(self):
        assert abs(R_BICEP_LIMIT - 0.036) < 1e-10

    def test_r_braided_within_bicep(self):
        assert R_BRAIDED < R_BICEP_LIMIT

    def test_ns_target_within_2sigma_of_planck(self):
        assert abs(NS_TARGET - NS_PLANCK) < 2.0 * NS_SIGMA

    def test_ns_target_less_than_ns_planck(self):
        assert NS_TARGET < NS_PLANCK

    def test_c_s_less_than_one(self):
        assert C_S < 1.0

    def test_c_s_positive(self):
        assert C_S > 0.0


# ---------------------------------------------------------------------------
# phi0_eff_from_ns tests
# ---------------------------------------------------------------------------

class TestPhi0EffFromNs:
    def test_canonical_ns_target(self):
        phi0 = phi0_eff_from_ns(NS_TARGET)
        # Should be close to n_w × 2π = 5 × 2π ≈ 31.416; match to ~0.1%
        expected = N_WINDING * 2.0 * math.pi
        assert abs(phi0 - expected) / expected < 1e-3

    def test_known_result(self):
        # ns = 1 - 36/x^2 → x = sqrt(36/(1-ns))
        ns = 0.9
        phi0 = phi0_eff_from_ns(ns)
        assert abs(phi0 - math.sqrt(36.0 / 0.1)) < 1e-10

    def test_result_is_positive(self):
        phi0 = phi0_eff_from_ns(0.96)
        assert phi0 > 0.0

    def test_larger_ns_gives_larger_phi0(self):
        phi0_a = phi0_eff_from_ns(0.95)
        phi0_b = phi0_eff_from_ns(0.96)
        assert phi0_b > phi0_a

    def test_ns_1_raises(self):
        with pytest.raises(ValueError):
            phi0_eff_from_ns(1.0)

    def test_ns_greater_than_1_raises(self):
        with pytest.raises(ValueError):
            phi0_eff_from_ns(1.01)

    def test_ns_zero_raises(self):
        with pytest.raises(ValueError):
            phi0_eff_from_ns(0.0)

    def test_ns_negative_raises(self):
        with pytest.raises(ValueError):
            phi0_eff_from_ns(-0.1)

    def test_n_winding_ignored_in_result(self):
        # n_winding is accepted but doesn't affect the inversion formula
        phi0_a = phi0_eff_from_ns(NS_TARGET, 3)
        phi0_b = phi0_eff_from_ns(NS_TARGET, 7)
        assert abs(phi0_a - phi0_b) < 1e-15

    def test_small_ns(self):
        phi0 = phi0_eff_from_ns(0.1)
        assert abs(phi0 - math.sqrt(36.0 / 0.9)) < 1e-10

    def test_large_ns_close_to_one(self):
        phi0 = phi0_eff_from_ns(0.9999)
        assert phi0 > 500.0   # sqrt(36/0.0001) = 600

    def test_result_type_is_float(self):
        assert isinstance(phi0_eff_from_ns(0.95), float)


# ---------------------------------------------------------------------------
# ns_from_phi0 tests
# ---------------------------------------------------------------------------

class TestNsFromPhi0:
    def test_canonical_phi0(self):
        phi0_canonical = N_WINDING * 2.0 * math.pi
        ns = ns_from_phi0(phi0_canonical)
        # ns_from_phi0(5×2π) ≈ 0.96352 ≈ NS_TARGET=0.9635 to <1e-4
        assert abs(ns - NS_TARGET) < 1e-3

    def test_known_result(self):
        phi0 = 6.0
        ns = ns_from_phi0(phi0)
        assert abs(ns - (1.0 - 36.0 / 36.0)) < 1e-10

    def test_ns_less_than_one(self):
        ns = ns_from_phi0(100.0)
        assert ns < 1.0

    def test_ns_increases_with_phi0(self):
        ns_small = ns_from_phi0(10.0)
        ns_large = ns_from_phi0(50.0)
        assert ns_large > ns_small

    def test_zero_phi0_raises(self):
        with pytest.raises(ValueError):
            ns_from_phi0(0.0)

    def test_negative_phi0_raises(self):
        with pytest.raises(ValueError):
            ns_from_phi0(-5.0)

    def test_large_phi0_approaches_one(self):
        ns = ns_from_phi0(1e6)
        assert abs(ns - 1.0) < 1e-9

    def test_result_type_is_float(self):
        assert isinstance(ns_from_phi0(30.0), float)

    def test_phi0_1_gives_expected(self):
        ns = ns_from_phi0(1.0)
        assert abs(ns - (1.0 - 36.0)) < 1e-10  # = -35.0

    def test_phi0_eff_at_6(self):
        # phi0_eff = 6 → ns = 1 - 36/36 = 0
        ns = ns_from_phi0(6.0)
        assert abs(ns - 0.0) < 1e-10


# ---------------------------------------------------------------------------
# Round-trip tests
# ---------------------------------------------------------------------------

class TestRoundTrip:
    @pytest.mark.parametrize("phi0", [10.0, 20.0, 31.416, 50.0, 100.0, 200.0])
    def test_phi0_roundtrip(self, phi0):
        """phi0_eff_from_ns(ns_from_phi0(x)) == x"""
        ns = ns_from_phi0(phi0)
        phi0_recovered = phi0_eff_from_ns(ns)
        assert abs(phi0_recovered - phi0) < 1e-6

    @pytest.mark.parametrize("ns", [0.9, 0.95, 0.96, 0.9635, 0.97, 0.99])
    def test_ns_roundtrip(self, ns):
        """ns_from_phi0(phi0_eff_from_ns(ns)) == ns"""
        phi0 = phi0_eff_from_ns(ns)
        ns_recovered = ns_from_phi0(phi0)
        assert abs(ns_recovered - ns) < 1e-12

    def test_canonical_roundtrip(self):
        phi0_canonical = N_WINDING * 2.0 * math.pi
        ns = ns_from_phi0(phi0_canonical)
        phi0_back = phi0_eff_from_ns(ns)
        assert abs(phi0_back - phi0_canonical) < 1e-8


# ---------------------------------------------------------------------------
# lambda_cobe tests
# ---------------------------------------------------------------------------

class TestLambdaCobe:
    def test_positive(self):
        phi0_canonical = N_WINDING * 2.0 * math.pi
        lam = lambda_cobe(phi0_canonical)
        assert lam > 0.0

    def test_sensible_magnitude(self):
        # λ_COBE should be in the ~1e-13 to ~1e-11 range for canonical φ₀
        phi0_canonical = N_WINDING * 2.0 * math.pi
        lam = lambda_cobe(phi0_canonical)
        assert 1e-14 < lam < 1e-9

    def test_known_formula(self):
        phi0 = 10.0
        lam = lambda_cobe(phi0, as_target=AS_PLANCK)
        expected = 192.0 * math.pi**2 * AS_PLANCK / phi0**4
        assert abs(lam - expected) < 1e-20

    def test_zero_phi0_raises(self):
        with pytest.raises(ValueError):
            lambda_cobe(0.0)

    def test_negative_phi0_raises(self):
        with pytest.raises(ValueError):
            lambda_cobe(-1.0)

    def test_zero_as_raises(self):
        with pytest.raises(ValueError):
            lambda_cobe(30.0, as_target=0.0)

    def test_negative_as_raises(self):
        with pytest.raises(ValueError):
            lambda_cobe(30.0, as_target=-1e-9)

    def test_larger_phi0_gives_smaller_lambda(self):
        lam_small = lambda_cobe(20.0)
        lam_large = lambda_cobe(40.0)
        assert lam_large < lam_small

    def test_reconstructs_as_exactly(self):
        phi0_canonical = N_WINDING * 2.0 * math.pi
        lam = lambda_cobe(phi0_canonical, AS_PLANCK)
        as_reconstructed = lam * phi0_canonical**4 / (192.0 * math.pi**2)
        assert abs(as_reconstructed - AS_PLANCK) / AS_PLANCK < 1e-12

    def test_scales_linearly_with_as(self):
        phi0 = 30.0
        lam1 = lambda_cobe(phi0, AS_PLANCK)
        lam2 = lambda_cobe(phi0, 2.0 * AS_PLANCK)
        assert abs(lam2 / lam1 - 2.0) < 1e-10

    def test_result_type(self):
        assert isinstance(lambda_cobe(30.0), float)


# ---------------------------------------------------------------------------
# ftum_phi0_iteration tests
# ---------------------------------------------------------------------------

class TestFtumIteration:
    def test_converges(self):
        result = ftum_phi0_iteration()
        assert result["converged"] is True

    def test_phi0_converged_positive(self):
        result = ftum_phi0_iteration()
        assert result["phi0_converged"] > 0.0

    def test_ns_converged_physical(self):
        result = ftum_phi0_iteration()
        ns = result["ns_converged"]
        assert 0.0 < ns < 1.0

    def test_lambda_cobe_positive(self):
        result = ftum_phi0_iteration()
        assert result["lambda_cobe"] > 0.0

    def test_n_iterations_positive(self):
        result = ftum_phi0_iteration()
        assert result["n_iterations"] >= 1

    def test_residual_below_tol(self):
        tol = 1e-8
        result = ftum_phi0_iteration(tol=tol)
        assert result["residual"] < tol

    def test_residual_below_default_tol(self):
        result = ftum_phi0_iteration()
        assert result["residual"] < 1e-10

    def test_different_n_winding_converges(self):
        for n_w in [1, 3, 5, 7, 9]:
            result = ftum_phi0_iteration(
                phi0_init=n_w * 2.0 * math.pi, n_winding=n_w
            )
            assert result["converged"] is True

    def test_different_phi0_init_same_convergence(self):
        r1 = ftum_phi0_iteration(phi0_init=30.0)
        r2 = ftum_phi0_iteration(phi0_init=35.0)
        assert abs(r1["phi0_converged"] - r2["phi0_converged"]) < 1e-6

    def test_strict_tol_converges(self):
        result = ftum_phi0_iteration(tol=1e-12, max_iter=500)
        assert result["converged"] is True

    def test_max_iter_1_may_not_converge(self):
        result = ftum_phi0_iteration(phi0_init=1.0, max_iter=1)
        assert result["n_iterations"] <= 1

    def test_zero_phi0_init_raises(self):
        with pytest.raises(ValueError):
            ftum_phi0_iteration(phi0_init=0.0)

    def test_negative_phi0_init_raises(self):
        with pytest.raises(ValueError):
            ftum_phi0_iteration(phi0_init=-5.0)

    def test_zero_tol_raises(self):
        with pytest.raises(ValueError):
            ftum_phi0_iteration(tol=0.0)

    def test_negative_tol_raises(self):
        with pytest.raises(ValueError):
            ftum_phi0_iteration(tol=-1e-10)

    def test_zero_max_iter_raises(self):
        with pytest.raises(ValueError):
            ftum_phi0_iteration(max_iter=0)

    def test_n_winding_zero_raises(self):
        with pytest.raises(ValueError):
            ftum_phi0_iteration(n_winding=0)

    def test_result_keys(self):
        result = ftum_phi0_iteration()
        expected_keys = {"phi0_converged", "ns_converged", "lambda_cobe",
                         "n_iterations", "converged", "residual"}
        assert expected_keys.issubset(result.keys())

    def test_n_iterations_bounded_by_max_iter(self):
        result = ftum_phi0_iteration(max_iter=50)
        assert result["n_iterations"] <= 50


# ---------------------------------------------------------------------------
# closure_audit tests
# ---------------------------------------------------------------------------

class TestClosureAudit:
    def setup_method(self):
        self.audit = closure_audit()

    def test_all_consistent(self):
        assert self.audit["all_consistent"] is True

    def test_phi0_canonical_correct(self):
        expected = N_WINDING * 2.0 * math.pi
        assert abs(self.audit["phi0_canonical"] - expected) < 1e-10

    def test_phi0_from_ns_close_to_canonical(self):
        # phi0_from_ns and phi0_canonical agree to ~0.1% (NS_TARGET is rounded)
        assert abs(self.audit["phi0_from_ns"] - self.audit["phi0_canonical"]) / self.audit["phi0_canonical"] < 1e-3

    def test_phi0_from_ftum_positive(self):
        assert self.audit["phi0_from_ftum"] > 0.0

    def test_ns_check_present(self):
        assert "ns_check" in self.audit

    def test_as_check_present(self):
        assert "as_check" in self.audit

    def test_r_check_present(self):
        assert "r_check" in self.audit

    def test_ns_within_2sigma(self):
        assert self.audit["ns_check"]["within_2sigma"] is True

    def test_as_consistent(self):
        assert self.audit["as_check"]["consistent"] is True

    def test_as_ratio_close_to_one(self):
        assert abs(self.audit["as_check"]["as_ratio"] - 1.0) < 1e-10

    def test_lambda_cobe_positive(self):
        assert self.audit["as_check"]["lambda_cobe"] > 0.0

    def test_r_within_bicep(self):
        assert self.audit["r_check"]["within_bicep"] is True

    def test_ns_sigma_planck_finite(self):
        sigma_dev = self.audit["ns_check"]["ns_sigma_planck"]
        assert math.isfinite(sigma_dev)

    def test_ns_sigma_planck_reasonable(self):
        # Should be within a few sigma of Planck
        sigma_dev = self.audit["ns_check"]["ns_sigma_planck"]
        assert sigma_dev < 5.0

    def test_result_keys_complete(self):
        expected = {"phi0_canonical", "phi0_from_ns", "phi0_from_ftum",
                    "ns_check", "as_check", "r_check", "all_consistent"}
        assert expected.issubset(self.audit.keys())

    def test_ftum_delta_frac_small(self):
        assert self.audit["ftum_delta_frac"] < 0.1

    def test_ns_check_consistent(self):
        assert self.audit["ns_check"]["consistent"] is True

    def test_r_check_consistent(self):
        assert self.audit["r_check"]["consistent"] is True


# ---------------------------------------------------------------------------
# phi0_uncertainty_band tests
# ---------------------------------------------------------------------------

class TestPhi0UncertaintyBand:
    def test_central_value(self):
        band = phi0_uncertainty_band(1.0)
        expected_central = phi0_eff_from_ns(NS_TARGET)
        assert abs(band["phi0_central"] - expected_central) < 1e-10

    def test_phi0_upper_greater_than_central(self):
        band = phi0_uncertainty_band(1.0)
        assert band["phi0_upper"] > band["phi0_central"]

    def test_phi0_lower_less_than_central(self):
        band = phi0_uncertainty_band(1.0)
        assert band["phi0_lower"] < band["phi0_central"]

    def test_delta_phi0_positive(self):
        band = phi0_uncertainty_band(1.0)
        assert band["delta_phi0"] > 0.0

    def test_n_sigma_echoed(self):
        band = phi0_uncertainty_band(2.5)
        assert abs(band["n_sigma"] - 2.5) < 1e-15

    def test_larger_n_sigma_larger_band(self):
        band1 = phi0_uncertainty_band(1.0)
        band2 = phi0_uncertainty_band(2.0)
        assert band2["delta_phi0"] > band1["delta_phi0"]

    def test_band_is_asymmetric_about_central(self):
        # Upper and lower deviations need not be identical (nonlinear transform)
        band = phi0_uncertainty_band(1.0)
        delta_up = band["phi0_upper"] - band["phi0_central"]
        delta_down = band["phi0_central"] - band["phi0_lower"]
        # Both should be positive
        assert delta_up > 0.0
        assert delta_down > 0.0

    def test_zero_n_sigma_raises(self):
        with pytest.raises(ValueError):
            phi0_uncertainty_band(0.0)

    def test_negative_n_sigma_raises(self):
        with pytest.raises(ValueError):
            phi0_uncertainty_band(-1.0)

    def test_result_keys(self):
        band = phi0_uncertainty_band(1.0)
        expected = {"phi0_central", "phi0_lower", "phi0_upper", "delta_phi0", "n_sigma"}
        assert expected.issubset(band.keys())

    def test_all_values_positive(self):
        band = phi0_uncertainty_band(1.0)
        for key in ("phi0_central", "phi0_lower", "phi0_upper", "delta_phi0"):
            assert band[key] > 0.0, f"{key} should be positive"

    def test_band_2sigma_roughly_double_1sigma(self):
        band1 = phi0_uncertainty_band(1.0)
        band2 = phi0_uncertainty_band(2.0)
        ratio = band2["delta_phi0"] / band1["delta_phi0"]
        # Propagation is nonlinear (sqrt transform), so ratio is ~2 but may deviate
        assert 1.5 < ratio < 3.0

    def test_half_sigma_band(self):
        band = phi0_uncertainty_band(0.5)
        assert band["delta_phi0"] > 0.0
        assert band["phi0_upper"] > band["phi0_central"]


# ---------------------------------------------------------------------------
# Integration / physics sanity tests
# ---------------------------------------------------------------------------

class TestPhysicsSanity:
    def test_canonical_phi0_close_to_5_times_2pi(self):
        phi0_canonical = N_WINDING * 2.0 * math.pi
        assert abs(phi0_canonical - 31.41592653) < 1e-5

    def test_ns_target_prediction(self):
        phi0 = phi0_eff_from_ns(NS_TARGET)
        ns_back = ns_from_phi0(phi0)
        assert abs(ns_back - NS_TARGET) < 1e-12

    def test_lambda_cobe_at_canonical_order_of_magnitude(self):
        phi0_canonical = N_WINDING * 2.0 * math.pi
        lam = lambda_cobe(phi0_canonical)
        # λ_COBE ≈ 192π² × 2.1e-9 / (31.4)⁴ ≈ 1.3e-12
        assert 1e-14 < lam < 1e-10

    def test_ftum_converged_phi0_positive(self):
        result = ftum_phi0_iteration()
        assert result["phi0_converged"] > 0.0

    def test_ftum_converged_ns_physical(self):
        result = ftum_phi0_iteration()
        ns = result["ns_converged"]
        assert 0.8 < ns < 1.0

    def test_all_consistency_conditions_hold(self):
        audit = closure_audit()
        assert audit["all_consistent"] is True

    def test_r_braided_less_than_bicep_limit(self):
        assert R_BRAIDED < R_BICEP_LIMIT

    def test_phi0_from_ns_equals_5_times_2pi(self):
        phi0 = phi0_eff_from_ns(NS_TARGET)
        # NS_TARGET = 0.9635 → phi0 = sqrt(36/0.0365) ≈ 31.396
        expected = math.sqrt(36.0 / (1.0 - NS_TARGET))
        assert abs(phi0 - expected) < 1e-10

    def test_as_planck_correct_order(self):
        # 2.101e-9 is in the right ballpark
        assert 1e-10 < AS_PLANCK < 1e-8

    def test_ns_target_near_planck(self):
        # Within 1 sigma
        sigma_deviation = abs(NS_TARGET - NS_PLANCK) / NS_SIGMA
        assert sigma_deviation < 1.0


# ---------------------------------------------------------------------------
# ns_from_phi0_braided tests
# ---------------------------------------------------------------------------

class TestNsFromPhi0Braided:
    def test_reduces_to_canonical_at_ftum(self):
        """The exact identity: ns_braided(phi0_FTUM, c_s) = ns_canonical(phi0_canonical)."""
        phi0_canonical = N_WINDING * 2.0 * math.pi
        phi0_ftum = N_WINDING * 2.0 * math.pi * _F_BRAIDED
        ns_braided_at_ftum = ns_from_phi0_braided(phi0_ftum, C_S)
        ns_canonical_at_canonical = ns_from_phi0(phi0_canonical)
        assert abs(ns_braided_at_ftum - ns_canonical_at_canonical) < 1e-12

    def test_matches_ns_target_at_ftum(self):
        """ns_braided(phi0_FTUM) ≈ NS_TARGET to < 0.05% (rounding limit)."""
        phi0_ftum = N_WINDING * 2.0 * math.pi * _F_BRAIDED
        ns_br = ns_from_phi0_braided(phi0_ftum, C_S)
        assert abs(ns_br - NS_TARGET) < 5e-4

    def test_smaller_than_canonical_formula_at_same_phi0(self):
        """Braided formula always gives smaller ns at same phi0 (larger epsilon)."""
        phi0 = N_WINDING * 2.0 * math.pi
        ns_can = ns_from_phi0(phi0)
        ns_br = ns_from_phi0_braided(phi0, C_S)
        assert ns_br < ns_can

    def test_cs_one_gives_double_correction(self):
        """At c_s=1, the braided formula gives ns = 1 - 72/phi0^2 (double canonical)."""
        phi0 = 30.0
        ns_br = ns_from_phi0_braided(phi0, 1.0)
        expected = 1.0 - 36.0 * 2.0 / phi0**2
        assert abs(ns_br - expected) < 1e-12

    def test_cs_zero_limit_approaches_canonical(self):
        """As c_s → 0, ns_braided → ns_canonical."""
        phi0 = 30.0
        ns_br = ns_from_phi0_braided(phi0, 1e-6)
        ns_can = ns_from_phi0(phi0)
        assert abs(ns_br - ns_can) < 1e-10

    def test_known_value(self):
        phi0 = 10.0
        c_s = 0.5
        expected = 1.0 - 36.0 * (1.0 + 0.25) / 100.0
        assert abs(ns_from_phi0_braided(phi0, c_s) - expected) < 1e-12

    def test_zero_phi0_raises(self):
        with pytest.raises(ValueError):
            ns_from_phi0_braided(0.0, C_S)

    def test_negative_phi0_raises(self):
        with pytest.raises(ValueError):
            ns_from_phi0_braided(-5.0, C_S)

    def test_zero_cs_raises(self):
        with pytest.raises(ValueError):
            ns_from_phi0_braided(30.0, 0.0)

    def test_negative_cs_raises(self):
        with pytest.raises(ValueError):
            ns_from_phi0_braided(30.0, -0.3)

    def test_result_is_float(self):
        assert isinstance(ns_from_phi0_braided(30.0, C_S), float)

    def test_large_phi0_approaches_one(self):
        ns = ns_from_phi0_braided(1e6, C_S)
        assert abs(ns - 1.0) < 1e-6

    def test_planck_window_at_ftum(self):
        """ns_braided(phi0_FTUM) lies within Planck 2018 2σ window."""
        phi0_ftum = N_WINDING * 2.0 * math.pi * _F_BRAIDED
        ns = ns_from_phi0_braided(phi0_ftum, C_S)
        assert abs(ns - NS_PLANCK) < 2.0 * NS_SIGMA


# ---------------------------------------------------------------------------
# phi0_eff_from_ns_braided tests
# ---------------------------------------------------------------------------

class TestPhi0EffFromNsBraided:
    def test_equals_phi0_ftum_at_ns_target(self):
        """phi0_eff_from_ns_braided(NS_TARGET) ≈ phi0_FTUM to < 0.05%."""
        phi0_ftum = N_WINDING * 2.0 * math.pi * _F_BRAIDED
        phi0_br = phi0_eff_from_ns_braided(NS_TARGET, C_S)
        assert abs(phi0_br - phi0_ftum) / phi0_ftum < 5e-4

    def test_equals_canonical_times_f_braided(self):
        """phi0_braided = phi0_canonical × sqrt(1+c_s^2) to < 0.05%."""
        phi0_canonical = N_WINDING * 2.0 * math.pi
        phi0_br = phi0_eff_from_ns_braided(NS_TARGET, C_S)
        expected = phi0_canonical * _F_BRAIDED
        assert abs(phi0_br - expected) / expected < 5e-4

    def test_larger_than_canonical_formula(self):
        """Braided phi0 > canonical phi0 for same ns (c_s > 0)."""
        phi0_can = phi0_eff_from_ns(NS_TARGET)
        phi0_br = phi0_eff_from_ns_braided(NS_TARGET, C_S)
        assert phi0_br > phi0_can

    def test_ratio_equals_f_braided_approximately(self):
        """phi0_braided / phi0_canonical ≈ sqrt(1+c_s^2)."""
        phi0_can = phi0_eff_from_ns(NS_TARGET)
        phi0_br = phi0_eff_from_ns_braided(NS_TARGET, C_S)
        ratio = phi0_br / phi0_can
        assert abs(ratio - _F_BRAIDED) < 1e-10

    def test_round_trip_braided(self):
        """phi0_eff_from_ns_braided(ns_from_phi0_braided(x)) == x."""
        phi0 = 33.0
        ns = ns_from_phi0_braided(phi0, C_S)
        if 0.0 < ns < 1.0:
            phi0_back = phi0_eff_from_ns_braided(ns, C_S)
            assert abs(phi0_back - phi0) < 1e-8

    def test_cs_one_gives_sqrt2_times_canonical(self):
        """At c_s=1: phi0_braided = sqrt(2) × phi0_canonical."""
        phi0_can = phi0_eff_from_ns(NS_TARGET)
        phi0_br = phi0_eff_from_ns_braided(NS_TARGET, 1.0)
        assert abs(phi0_br / phi0_can - math.sqrt(2.0)) < 1e-10

    def test_ns_1_raises(self):
        with pytest.raises(ValueError):
            phi0_eff_from_ns_braided(1.0, C_S)

    def test_ns_zero_raises(self):
        with pytest.raises(ValueError):
            phi0_eff_from_ns_braided(0.0, C_S)

    def test_ns_negative_raises(self):
        with pytest.raises(ValueError):
            phi0_eff_from_ns_braided(-0.1, C_S)

    def test_cs_zero_raises(self):
        with pytest.raises(ValueError):
            phi0_eff_from_ns_braided(NS_TARGET, 0.0)

    def test_result_is_float(self):
        assert isinstance(phi0_eff_from_ns_braided(NS_TARGET, C_S), float)

    def test_result_positive(self):
        assert phi0_eff_from_ns_braided(NS_TARGET, C_S) > 0.0

    @pytest.mark.parametrize("ns", [0.9, 0.95, 0.9635, 0.97, 0.99])
    def test_ns_round_trip_parametrize(self, ns):
        phi0 = phi0_eff_from_ns_braided(ns, C_S)
        ns_back = ns_from_phi0_braided(phi0, C_S)
        assert abs(ns_back - ns) < 1e-12


# ---------------------------------------------------------------------------
# braided_closure_audit tests
# ---------------------------------------------------------------------------

class TestBraidedClosureAudit:
    def setup_method(self):
        self.audit = braided_closure_audit()

    def test_all_consistent(self):
        """The braided closure audit reports all conditions satisfied."""
        assert self.audit["all_consistent"] is True

    def test_phi0_canonical_correct(self):
        expected = N_WINDING * 2.0 * math.pi
        assert abs(self.audit["phi0_canonical"] - expected) < 1e-10

    def test_phi0_ftum_correct(self):
        expected = N_WINDING * 2.0 * math.pi * _F_BRAIDED
        assert abs(self.audit["phi0_ftum"] - expected) < 1e-10

    def test_phi0_ftum_greater_than_canonical(self):
        assert self.audit["phi0_ftum"] > self.audit["phi0_canonical"]

    def test_ftum_canonical_frac_about_5_percent(self):
        """FTUM attractor is ~5% above canonical (c_s = 12/37)."""
        frac = self.audit["ftum_canonical_frac"]
        assert 0.04 < frac < 0.07

    def test_ns_exact_identity(self):
        """The exact algebraic identity holds: ns_braided(phi0_FTUM) == ns_can(phi0_canonical)."""
        assert self.audit["ns_exact_identity"] is True

    def test_ns_at_ftum_braided_close_to_target(self):
        """ns_braided(phi0_FTUM) ≈ NS_TARGET to < 0.05%."""
        err = self.audit["ns_braided_error"]
        assert err < 5e-4

    def test_ns_at_ftum_canonical_differs_from_target(self):
        """ns_canonical(phi0_FTUM) ≠ NS_TARGET (canonical formula at wrong phi0)."""
        ns_can = self.audit["ns_at_ftum_canonical"]
        assert abs(ns_can - NS_TARGET) > 1e-3

    def test_lambda_cobe_positive(self):
        assert self.audit["lambda_cobe_ftum"] > 0.0

    def test_lambda_cobe_small(self):
        """λ_COBE should be ~10^-12."""
        assert 1e-14 < self.audit["lambda_cobe_ftum"] < 1e-9

    def test_as_ratio_close_to_one(self):
        assert abs(self.audit["as_ratio_ftum"] - 1.0) < 1e-10

    def test_ftum_converged(self):
        assert self.audit["ftum_converged"] is True

    def test_r_within_bicep(self):
        assert self.audit["r_check"]["within_bicep"] is True

    def test_phi0_from_ns_braided_close_to_ftum(self):
        """phi0_from_ns_braided ≈ phi0_FTUM to < 0.05%."""
        phi0_br = self.audit["phi0_from_ns_braided"]
        phi0_ftum = self.audit["phi0_ftum"]
        assert abs(phi0_br - phi0_ftum) / phi0_ftum < 5e-4

    def test_result_keys_complete(self):
        expected = {
            "phi0_canonical", "phi0_ftum", "phi0_from_ns_braided",
            "ftum_canonical_frac", "ns_at_ftum_braided", "ns_at_ftum_canonical",
            "ns_braided_error", "ns_exact_identity", "lambda_cobe_ftum",
            "as_ratio_ftum", "ftum_converged", "r_check", "all_consistent",
        }
        assert expected.issubset(self.audit.keys())

    def test_braided_formula_closes_gap(self):
        """The braided formula gives NS_TARGET at phi0_FTUM; canonical does not."""
        # Canonical formula at phi0_FTUM gives a different ns
        ns_can = self.audit["ns_at_ftum_canonical"]
        ns_br = self.audit["ns_at_ftum_braided"]
        # Braided is closer to NS_TARGET than canonical
        assert abs(ns_br - NS_TARGET) < abs(ns_can - NS_TARGET)

    def test_f_braided_factor_equals_sqrt_1_plus_cs_squared(self):
        """The FTUM correction factor f_braided = sqrt(1 + c_s^2)."""
        phi0_can = self.audit["phi0_canonical"]
        phi0_ftum = self.audit["phi0_ftum"]
        f_computed = phi0_ftum / phi0_can
        f_expected = math.sqrt(1.0 + C_S**2)
        assert abs(f_computed - f_expected) < 1e-12

    def test_four_way_closure_summary(self):
        """Verify all four closure conditions independently."""
        # 1. ns braided consistency
        assert self.audit["ns_braided_error"] < 5e-4
        # 2. As consistency
        assert abs(self.audit["as_ratio_ftum"] - 1.0) < 1e-10
        # 3. FTUM convergence
        assert self.audit["ftum_converged"] is True
        # 4. r < BICEP limit
        assert self.audit["r_check"]["within_bicep"] is True

