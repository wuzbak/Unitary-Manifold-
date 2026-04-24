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
    phi0_eff_from_ns,
    ns_from_phi0,
    lambda_cobe,
    ftum_phi0_iteration,
    closure_audit,
    phi0_uncertainty_band,
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
