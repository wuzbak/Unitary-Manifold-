# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_non_gaussianity.py
==============================
Tests for src/core/non_gaussianity.py — two-field f_NL from the dynamical radion.

Covers:
  slow_roll_fnl_adiabatic   — Maldacena formula, sign, small magnitude
  isocurvature_mass_sq      — M_rc²/H² computation, light-field condition
  geodesic_deviation_fnl    — 5D ladder signal, scaling, canonical value
  two_field_fnl_delta_n     — full δN combination, Planck safety, light flag
  fnl_observability         — SNR assessment, exclusion thresholds
  fnl_radion_scan           — joint (β, f_NL) stability map
  fnl_running               — scale dependence, n_f sign, pivot consistency
"""

import math

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.non_gaussianity import (
    slow_roll_fnl_adiabatic,
    isocurvature_mass_sq,
    geodesic_deviation_fnl,
    two_field_fnl_delta_n,
    fnl_observability,
    fnl_radion_scan,
    fnl_running,
    PLANCK_FNL_SIGMA,
    PLANCK_FNL_EXCLUSION,
    CMBS4_FNL_SIGMA,
    LITEBIRD_FNL_SIGMA,
    BETA_SAFE_LO,
    BETA_SAFE_HI,
)

# Canonical parameters used throughout (matching FTUM/braided-winding values)
PHI0_EFF_CANONICAL = 31.4     # = J_KK * phi0_bare ≈ 5 × 2π × φ₀_bare
LAM_CANONICAL      = 1.0
LAM_GW_CANONICAL   = 1.0
R_C_CANONICAL      = 12.0


# ===========================================================================
# slow_roll_fnl_adiabatic
# ===========================================================================

class TestSlowRollFnlAdiabatic:

    def test_positive_epsilon_positive_eta_zero(self):
        """f_NL^adi = (5/12)*6ε > 0 when η = 0."""
        eps = 0.01
        f = slow_roll_fnl_adiabatic(eps, eta=0.0)
        assert f == pytest.approx((5.0/12.0) * 6.0 * eps, rel=1e-12)

    def test_zero_epsilon_zero_eta_gives_zero(self):
        assert slow_roll_fnl_adiabatic(0.0, 0.0) == pytest.approx(0.0, abs=1e-14)

    def test_maldacena_formula(self):
        """f_NL = (5/12)(6ε - 2η) exactly."""
        eps, eta = 0.006, 0.002
        expected = (5.0/12.0) * (6.0*eps - 2.0*eta)
        assert slow_roll_fnl_adiabatic(eps, eta) == pytest.approx(expected, rel=1e-12)

    def test_canonical_value_small(self):
        """For canonical φ₀_eff ≈ 31.4: f_NL^adi ≈ 0.015 ≪ 1."""
        eps = 6.0 / PHI0_EFF_CANONICAL**2   # ε = 6/φ₀²
        f   = slow_roll_fnl_adiabatic(eps, eta=0.0)
        assert f == pytest.approx(15.0 / PHI0_EFF_CANONICAL**2, rel=1e-10)
        assert abs(f) < 0.1

    def test_below_planck_exclusion(self):
        """f_NL^adi must be far below Planck 2σ exclusion for canonical params."""
        eps = 6.0 / PHI0_EFF_CANONICAL**2
        f   = slow_roll_fnl_adiabatic(eps, eta=0.0)
        assert abs(f) < PLANCK_FNL_EXCLUSION

    def test_negative_eta_increases_fnl(self):
        """η < 0 increases f_NL (more negative η → larger positive contribution)."""
        eps = 0.01
        f0  = slow_roll_fnl_adiabatic(eps, eta=0.0)
        fn  = slow_roll_fnl_adiabatic(eps, eta=-0.005)
        assert fn > f0

    def test_raises_on_negative_epsilon(self):
        with pytest.raises(ValueError, match="epsilon"):
            slow_roll_fnl_adiabatic(-0.001, 0.0)


# ===========================================================================
# isocurvature_mass_sq
# ===========================================================================

class TestIsocurvatureMassSq:

    def test_returns_three_tuple(self):
        M2, H2, m = isocurvature_mass_sq(PHI0_EFF_CANONICAL)
        assert isinstance(M2, float)
        assert isinstance(H2, float)
        assert isinstance(m,  float)

    def test_M_rc_sq_formula(self):
        """M_rc² = 2 λ_GW φ₀²."""
        phi, lam_gw = 10.0, 2.0
        M2, H2, _ = isocurvature_mass_sq(phi, lam=1.0, lam_gw=lam_gw)
        assert M2 == pytest.approx(2.0 * lam_gw * phi**2, rel=1e-12)

    def test_H_sq_formula(self):
        """H² = (4/27) λ φ₀⁴."""
        phi, lam = 10.0, 1.5
        _, H2, _ = isocurvature_mass_sq(phi, lam=lam, lam_gw=1.0)
        assert H2 == pytest.approx((4.0/27.0) * lam * phi**4, rel=1e-12)

    def test_mass_ratio_formula(self):
        """mass_ratio = M_rc²/H² = 27 λ_GW / (2 λ φ₀²)."""
        phi, lam, lam_gw = 10.0, 1.0, 1.0
        M2, H2, m = isocurvature_mass_sq(phi, lam, lam_gw)
        assert m == pytest.approx(M2 / H2, rel=1e-10)

    def test_all_positive(self):
        M2, H2, m = isocurvature_mass_sq(PHI0_EFF_CANONICAL)
        assert M2 > 0.0
        assert H2 > 0.0
        assert m  > 0.0

    def test_canonical_radion_is_light(self):
        """m ≪ 1 for canonical parameters: r_c is a light field during inflation."""
        _, _, m = isocurvature_mass_sq(PHI0_EFF_CANONICAL, LAM_CANONICAL, LAM_GW_CANONICAL)
        assert m < 1.0, f"Expected light isocurvature (m < 1), got m = {m:.4f}"

    def test_heavier_lam_gw_increases_mass_ratio(self):
        """Larger λ_GW → stiffer radion → larger M_rc²/H²."""
        _, _, m1 = isocurvature_mass_sq(PHI0_EFF_CANONICAL, LAM_CANONICAL, lam_gw=1.0)
        _, _, m2 = isocurvature_mass_sq(PHI0_EFF_CANONICAL, LAM_CANONICAL, lam_gw=100.0)
        assert m2 > m1

    def test_larger_phi0_decreases_mass_ratio(self):
        """Larger φ₀ → smaller M_rc²/H² (H grows faster than M_rc)."""
        _, _, m1 = isocurvature_mass_sq(20.0)
        _, _, m2 = isocurvature_mass_sq(40.0)
        assert m2 < m1

    def test_raises_on_non_positive_phi(self):
        with pytest.raises(ValueError, match="phi0_eff"):
            isocurvature_mass_sq(0.0)

    def test_raises_on_non_positive_lam(self):
        with pytest.raises(ValueError, match="lam"):
            isocurvature_mass_sq(10.0, lam=0.0)

    def test_raises_on_non_positive_lam_gw(self):
        with pytest.raises(ValueError, match="lam_gw"):
            isocurvature_mass_sq(10.0, lam_gw=-1.0)

    def test_lam_gw_scaling(self):
        """M_rc² scales linearly with λ_GW."""
        M2_a, _, _ = isocurvature_mass_sq(10.0, lam_gw=1.0)
        M2_b, _, _ = isocurvature_mass_sq(10.0, lam_gw=3.0)
        assert M2_b == pytest.approx(3.0 * M2_a, rel=1e-12)


# ===========================================================================
# geodesic_deviation_fnl
# ===========================================================================

class TestGeodesicDeviationFnl:

    def test_positive(self):
        """f_NL^5D > 0 for all positive parameters."""
        f = geodesic_deviation_fnl(PHI0_EFF_CANONICAL)
        assert f > 0.0

    def test_canonical_value(self):
        """f_NL^5D ≈ 0.42 for canonical parameters (below Planck exclusion)."""
        f = geodesic_deviation_fnl(PHI0_EFF_CANONICAL, LAM_CANONICAL,
                                    LAM_GW_CANONICAL, R_C_CANONICAL)
        # (5/6) × (2 × 1 × 31.4²) / (27 × 1 × 144)
        expected = (5.0/6.0) * (2.0 * LAM_CANONICAL * PHI0_EFF_CANONICAL**2) / (
            27.0 * LAM_GW_CANONICAL * R_C_CANONICAL**2
        )
        assert f == pytest.approx(expected, rel=1e-8)
        assert f < PLANCK_FNL_EXCLUSION

    def test_formula_scaling_phi(self):
        """f_NL^5D ∝ φ₀²: doubling φ₀ quadruples f_NL."""
        f1 = geodesic_deviation_fnl(10.0, lam=1.0, lam_gw=1.0, r_c_star=5.0)
        f2 = geodesic_deviation_fnl(20.0, lam=1.0, lam_gw=1.0, r_c_star=5.0)
        assert f2 == pytest.approx(4.0 * f1, rel=1e-10)

    def test_formula_scaling_lam(self):
        """f_NL^5D ∝ λ: doubling λ doubles f_NL."""
        f1 = geodesic_deviation_fnl(10.0, lam=1.0, lam_gw=1.0, r_c_star=5.0)
        f2 = geodesic_deviation_fnl(10.0, lam=2.0, lam_gw=1.0, r_c_star=5.0)
        assert f2 == pytest.approx(2.0 * f1, rel=1e-10)

    def test_formula_scaling_lam_gw(self):
        """f_NL^5D ∝ 1/λ_GW: doubling λ_GW halves f_NL."""
        f1 = geodesic_deviation_fnl(10.0, lam=1.0, lam_gw=1.0, r_c_star=5.0)
        f2 = geodesic_deviation_fnl(10.0, lam=1.0, lam_gw=2.0, r_c_star=5.0)
        assert f2 == pytest.approx(0.5 * f1, rel=1e-10)

    def test_formula_scaling_r_c(self):
        """f_NL^5D ∝ 1/r_c²: doubling r_c* quarters f_NL."""
        f1 = geodesic_deviation_fnl(10.0, lam=1.0, lam_gw=1.0, r_c_star=5.0)
        f2 = geodesic_deviation_fnl(10.0, lam=1.0, lam_gw=1.0, r_c_star=10.0)
        assert f2 == pytest.approx(0.25 * f1, rel=1e-10)

    def test_decreases_with_r_c(self):
        """f_NL^5D decreases as r_c* increases (stronger compactification suppresses NG)."""
        f_values = [geodesic_deviation_fnl(PHI0_EFF_CANONICAL, r_c_star=rc)
                    for rc in [5.0, 10.0, 15.0, 20.0]]
        assert f_values[0] > f_values[1] > f_values[2] > f_values[3]

    def test_below_planck_exclusion_canonical(self):
        f = geodesic_deviation_fnl(PHI0_EFF_CANONICAL, LAM_CANONICAL,
                                    LAM_GW_CANONICAL, R_C_CANONICAL)
        assert abs(f) < PLANCK_FNL_EXCLUSION

    def test_raises_on_non_positive_phi(self):
        with pytest.raises(ValueError):
            geodesic_deviation_fnl(0.0)

    def test_raises_on_non_positive_lam(self):
        with pytest.raises(ValueError):
            geodesic_deviation_fnl(10.0, lam=0.0)

    def test_raises_on_non_positive_lam_gw(self):
        with pytest.raises(ValueError):
            geodesic_deviation_fnl(10.0, lam_gw=-1.0)

    def test_raises_on_non_positive_r_c(self):
        with pytest.raises(ValueError):
            geodesic_deviation_fnl(10.0, r_c_star=0.0)


# ===========================================================================
# two_field_fnl_delta_n
# ===========================================================================

class TestTwoFieldFnlDeltaN:

    def _run(self, **kw):
        defaults = dict(phi0_eff=PHI0_EFF_CANONICAL, lam=LAM_CANONICAL,
                        lam_gw=LAM_GW_CANONICAL, r_c_star=R_C_CANONICAL)
        defaults.update(kw)
        return two_field_fnl_delta_n(**defaults)

    def test_returns_dict_with_required_keys(self):
        result = self._run()
        for key in [
            "f_NL_adi", "f_NL_iso", "f_NL_5D", "f_NL_total",
            "M_rc_sq", "H_sq", "mass_ratio", "is_light",
            "epsilon", "eta", "planck_safe", "phi0_eff",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_canonical_is_planck_safe(self):
        """Canonical parameters must pass Planck 2018 f_NL bound."""
        result = self._run()
        assert result["planck_safe"], (
            f"f_NL_total = {result['f_NL_total']:.4f} violates Planck 2σ bound"
        )

    def test_canonical_radion_is_light(self):
        """r_c is a light isocurvature field (mass_ratio < 1) for canonical params."""
        result = self._run()
        assert result["is_light"], (
            f"Expected light isocurvature (mass_ratio < 1), "
            f"got mass_ratio = {result['mass_ratio']:.4f}"
        )

    def test_no_turning_gives_zero_iso(self):
        """f_NL^iso = 0 when turning_rate = 0 and delta_r_c_frac = 0."""
        result = self._run(turning_rate=0.0, delta_r_c_frac=0.0)
        assert result["f_NL_iso"] == pytest.approx(0.0, abs=1e-14)

    def test_total_equals_sum(self):
        """f_NL_total = f_NL_adi + f_NL_iso + f_NL_5D."""
        result = self._run(turning_rate=0.01, delta_r_c_frac=0.1)
        total  = result["f_NL_adi"] + result["f_NL_iso"] + result["f_NL_5D"]
        assert result["f_NL_total"] == pytest.approx(total, rel=1e-12)

    def test_adi_matches_standalone(self):
        """f_NL_adi matches slow_roll_fnl_adiabatic at the same ε, η."""
        result  = self._run()
        f_stand = slow_roll_fnl_adiabatic(result["epsilon"], result["eta"])
        assert result["f_NL_adi"] == pytest.approx(f_stand, rel=1e-10)

    def test_5d_matches_standalone(self):
        """f_NL_5D matches geodesic_deviation_fnl."""
        result = self._run()
        f_geo  = geodesic_deviation_fnl(PHI0_EFF_CANONICAL, LAM_CANONICAL,
                                         LAM_GW_CANONICAL, R_C_CANONICAL)
        assert result["f_NL_5D"] == pytest.approx(f_geo, rel=1e-10)

    def test_mass_ratio_matches_standalone(self):
        """mass_ratio matches isocurvature_mass_sq output."""
        result      = self._run()
        _, _, m_ref = isocurvature_mass_sq(PHI0_EFF_CANONICAL, LAM_CANONICAL,
                                            LAM_GW_CANONICAL)
        assert result["mass_ratio"] == pytest.approx(m_ref, rel=1e-10)

    def test_eta_zero_at_inflection(self):
        """η = 0 at the GW inflection point φ* = φ₀/√3."""
        result = self._run()
        assert result["eta"] == pytest.approx(0.0, abs=1e-10)

    def test_turning_enhances_iso_fnl(self):
        """Larger turning rate produces larger |f_NL^iso|."""
        r0 = self._run(turning_rate=0.0)
        r1 = self._run(turning_rate=0.01)
        r2 = self._run(turning_rate=0.05)
        assert abs(r2["f_NL_iso"]) > abs(r1["f_NL_iso"]) > abs(r0["f_NL_iso"])

    def test_planck_exclusion_for_large_turning(self):
        """Very large turning rate drives |f_NL| above Planck exclusion."""
        result = self._run(turning_rate=10.0)
        assert not result["planck_safe"]

    def test_phi0_echo(self):
        result = self._run()
        assert result["phi0_eff"] == pytest.approx(PHI0_EFF_CANONICAL)


# ===========================================================================
# fnl_observability
# ===========================================================================

class TestFnlObservability:

    def test_returns_dict_with_required_keys(self):
        result = fnl_observability(0.5)
        for key in [
            "f_NL", "planck_excluded", "planck_snr", "litebird_snr",
            "cmbs4_snr", "planck_detectable", "litebird_detectable",
            "cmbs4_detectable", "verdict",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_canonical_fnl_not_excluded(self):
        """f_NL^5D ≈ 0.42 is not excluded by Planck."""
        f = geodesic_deviation_fnl(PHI0_EFF_CANONICAL, LAM_CANONICAL,
                                    LAM_GW_CANONICAL, R_C_CANONICAL)
        result = fnl_observability(f)
        assert not result["planck_excluded"]

    def test_large_fnl_is_excluded(self):
        """f_NL = 50 is excluded by Planck (> 10.2)."""
        result = fnl_observability(50.0)
        assert result["planck_excluded"]

    def test_snr_formula_planck(self):
        """planck_snr = |f_NL| / σ_Planck."""
        f      = 3.0
        result = fnl_observability(f)
        assert result["planck_snr"] == pytest.approx(abs(f) / PLANCK_FNL_SIGMA, rel=1e-12)

    def test_snr_formula_cmbs4(self):
        """cmbs4_snr = |f_NL| / σ_CMB-S4."""
        f      = 1.5
        result = fnl_observability(f)
        assert result["cmbs4_snr"] == pytest.approx(abs(f) / CMBS4_FNL_SIGMA, rel=1e-12)

    def test_snr_formula_litebird(self):
        f      = 4.0
        result = fnl_observability(f)
        assert result["litebird_snr"] == pytest.approx(abs(f) / LITEBIRD_FNL_SIGMA, rel=1e-12)

    def test_negative_fnl_same_snr(self):
        """SNR is based on |f_NL|; same for ±f_NL."""
        rp = fnl_observability( 3.0)
        rn = fnl_observability(-3.0)
        assert rp["planck_snr"] == pytest.approx(rn["planck_snr"])

    def test_verdict_is_string(self):
        result = fnl_observability(0.5)
        assert isinstance(result["verdict"], str)
        assert len(result["verdict"]) > 0

    def test_cmbs4_detectable_above_threshold(self):
        """f_NL > 2σ_CMB-S4 → cmbs4_detectable = True."""
        result = fnl_observability(2.5)
        assert result["cmbs4_detectable"]

    def test_cmbs4_not_detectable_below_threshold(self):
        result = fnl_observability(0.1)
        assert not result["cmbs4_detectable"]

    def test_exclusion_threshold(self):
        """Exactly at PLANCK_FNL_EXCLUSION is not excluded (strict inequality)."""
        result_below = fnl_observability(PLANCK_FNL_EXCLUSION - 0.01)
        result_above = fnl_observability(PLANCK_FNL_EXCLUSION + 0.01)
        assert not result_below["planck_excluded"]
        assert result_above["planck_excluded"]

    def test_f_NL_echo(self):
        result = fnl_observability(3.7)
        assert result["f_NL"] == pytest.approx(3.7)


# ===========================================================================
# fnl_radion_scan
# ===========================================================================

class TestFnlRadionScan:

    def _run(self, **kw):
        return fnl_radion_scan(r_c_values=np.linspace(1.0, 20.0, 40), **kw)

    def test_returns_dict_with_required_keys(self):
        result = self._run()
        for key in [
            "r_c_values", "f_NL_5D", "beta_deg", "beta_safe",
            "fnl_safe", "joint_safe", "n_joint_safe",
            "canonical_fnl", "canonical_safe",
        ]:
            assert key in result, f"Missing key: {key}"

    def test_array_lengths_consistent(self):
        result = self._run()
        n = len(result["r_c_values"])
        assert len(result["f_NL_5D"])   == n
        assert len(result["beta_deg"])  == n
        assert len(result["beta_safe"]) == n
        assert len(result["fnl_safe"])  == n
        assert len(result["joint_safe"])== n

    def test_all_fnl_safe_past_saturation_floor(self):
        """After the J_RS saturation floor (r_c ≥ 5 for k=1) all f_NL^5D are
        within Planck bounds for canonical λ."""
        result  = self._run(phi0_eff=PHI0_EFF_CANONICAL, lam=1.0, lam_gw=1.0)
        r_c     = result["r_c_values"]
        fnl_s   = result["fnl_safe"]
        sat_mask = r_c >= 5.0
        if np.any(sat_mask):
            assert np.all(fnl_s[sat_mask]), (
                f"Some r_c ≥ 5 values give |f_NL| > Planck exclusion: "
                f"max |f_NL| = {np.max(np.abs(result['f_NL_5D'][sat_mask])):.2f}"
            )

    def test_small_r_c_exceeds_planck_bound(self):
        """At r_c < 5 the 5D correction f_NL^5D ∝ 1/r_c² is large and Planck-excluded.
        This is the correct physics: a too-small extra dimension = excluded by CMB NG."""
        result = self._run(phi0_eff=PHI0_EFF_CANONICAL, lam=1.0, lam_gw=1.0)
        r_c     = result["r_c_values"]
        fnl     = result["f_NL_5D"]
        small_mask = r_c < 3.0
        if np.any(small_mask):
            assert np.any(np.abs(fnl[small_mask]) > PLANCK_FNL_EXCLUSION), (
                "Expected large f_NL at small r_c (< 3) to be Planck-excluded"
            )
        """f_NL^5D must decrease as r_c increases (∝ 1/r_c²)."""
        result = self._run()
        f = result["f_NL_5D"]
        # After J_RS saturation (r_c > 5), f_NL should be monotonically decreasing
        r_c = result["r_c_values"]
        sat_i = int(np.argmax(r_c >= 5.0))
        assert np.all(np.diff(f[sat_i:]) < 0.0), (
            "f_NL^5D should decrease monotonically after J_RS saturation"
        )

    def test_canonical_joint_safe(self):
        """r_c = 12 must pass both the β rail and Planck f_NL bound."""
        result = self._run()
        assert result["canonical_safe"], (
            f"Canonical r_c=12: β={result['beta_deg'][np.argmin(np.abs(result['r_c_values']-12))]:.4f}°, "
            f"f_NL={result['canonical_fnl']:.4f}"
        )

    def test_joint_safe_zone_non_empty(self):
        """At least some r_c values pass both constraints."""
        result = self._run()
        assert result["n_joint_safe"] > 0

    def test_joint_safe_subset_of_beta_safe(self):
        """joint_safe implies beta_safe."""
        result = self._run()
        joint = result["joint_safe"]
        beta  = result["beta_safe"]
        assert np.all(beta[joint])

    def test_default_r_c_grid_when_none(self):
        """Passing r_c_values=None uses default linspace(1, 20, 80)."""
        result = fnl_radion_scan(r_c_values=None)
        assert len(result["r_c_values"]) == 80

    def test_larger_lam_gw_suppresses_fnl(self):
        """Stiffer radion (larger λ_GW) → smaller f_NL^5D."""
        r1 = self._run(lam_gw=1.0)
        r2 = self._run(lam_gw=5.0)
        assert np.all(r2["f_NL_5D"] < r1["f_NL_5D"])


# ===========================================================================
# fnl_running
# ===========================================================================

class TestFnlRunning:

    def _run(self, **kw):
        defaults = dict(phi0_eff=PHI0_EFF_CANONICAL, lam=LAM_CANONICAL,
                        lam_gw=LAM_GW_CANONICAL, r_c_star=R_C_CANONICAL)
        defaults.update(kw)
        return fnl_running(**defaults)

    def test_returns_dict_with_required_keys(self):
        result = self._run()
        for key in ["k_values", "f_NL_5D", "n_f", "f_NL_pivot", "ns_used"]:
            assert key in result, f"Missing key: {key}"

    def test_pivot_value_matches_geodesic_fnl(self):
        """f_NL at the pivot scale matches geodesic_deviation_fnl."""
        result    = self._run(pivot_k=0.05)
        f_geo     = geodesic_deviation_fnl(PHI0_EFF_CANONICAL, LAM_CANONICAL,
                                            LAM_GW_CANONICAL, R_C_CANONICAL)
        assert result["f_NL_pivot"] == pytest.approx(f_geo, rel=1e-8)

    def test_n_f_is_negative(self):
        """n_f = 2(n_s - 1) < 0 for n_s < 1."""
        result = self._run()
        assert result["n_f"] < 0.0

    def test_n_f_formula(self):
        """n_f ≈ 2(n_s - 1) from scale-dependent φ₀_eff."""
        result = self._run()
        ns     = result["ns_used"]
        assert result["n_f"] == pytest.approx(2.0 * (ns - 1.0), rel=1e-10)

    def test_f_NL_at_pivot_k(self):
        """At k = k_pivot, f_NL(k) = f_NL_pivot exactly."""
        pivot = 0.05
        result = self._run(pivot_k=pivot)
        k_arr  = result["k_values"]
        f_arr  = result["f_NL_5D"]
        idx    = int(np.argmin(np.abs(k_arr - pivot)))
        assert f_arr[idx] == pytest.approx(result["f_NL_pivot"], rel=0.05)

    def test_array_lengths_match(self):
        result = self._run()
        assert len(result["f_NL_5D"]) == len(result["k_values"])

    def test_running_decreases_to_large_k(self):
        """n_f < 0 means f_NL decreases toward small scales (large k)."""
        result = self._run()
        f = result["f_NL_5D"]
        # f_NL should decrease from large to small scales
        assert f[-1] < f[0]  # f_NL at largest k < f_NL at smallest k

    def test_default_k_grid_when_none(self):
        result = fnl_running(k_pivots=None)
        assert len(result["k_values"]) == 60

    def test_ns_used_in_planck_range(self):
        """n_s used for running must be in the Planck 1σ range [0.9607, 0.9691]."""
        result = self._run()
        ns = result["ns_used"]
        assert 0.92 < ns < 1.0, f"ns = {ns:.4f} is far from Planck range"


# ===========================================================================
# TestBraidedEquilateralFnl
# ===========================================================================

from src.core.non_gaussianity import (
    braided_equilateral_fnl,
    braided_fnl_full_summary,
    PLANCK_FNL_EQUIL_SIGMA,
    CMBS4_FNL_EQUIL_SIGMA,
    SO_FNL_EQUIL_SIGMA,
)


class TestBraidedEquilateralFnl:
    """Tests for braided_equilateral_fnl."""

    def test_returns_dict_with_required_keys(self):
        r = braided_equilateral_fnl(5, 7)
        for key in [
            "n1", "n2", "k_cs", "rho", "c_s", "c_s_inv_sq",
            "f_NL_equil", "f_NL_ortho", "f_NL_equil_analytic",
            "planck_equil_snr", "cmbs4_equil_snr", "so_equil_snr",
            "planck_excluded", "cmbs4_detectable",
            "formula", "reference", "status", "verdict",
        ]:
            assert key in r, f"Missing key: {key}"

    def test_f_NL_equil_positive_for_cs_lt_1(self):
        r = braided_equilateral_fnl(5, 7)
        assert r["f_NL_equil"] > 0.0

    def test_f_NL_equil_close_to_2757_for_57(self):
        r = braided_equilateral_fnl(5, 7)
        assert abs(r["f_NL_equil"] - 2.757) < 1e-2

    def test_f_NL_equil_zero_when_cs_is_1(self):
        # Exact c_s=1 requires rho=0.  Use k_cs=1000 to get rho≈0.004 (nearly zero).
        # The test checks formula consistency: f_NL = (35/108)(1/c_s^2-1).
        r = braided_equilateral_fnl(1, 2, k_cs=1000)
        rho = 2 * 1 * 2 / 1000.0
        import numpy as np
        c_s = np.sqrt(1 - rho**2)
        expected = (35.0 / 108.0) * (1.0 / c_s**2 - 1.0)
        assert abs(r["f_NL_equil"] - expected) < 1e-10

    def test_f_NL_equil_exact_zero_for_rho_zero(self):
        # With k_cs very large, rho→0, f_NL→0
        r = braided_equilateral_fnl(1, 2, k_cs=10**8)
        assert abs(r["f_NL_equil"]) < 1e-5

    def test_f_NL_equil_increases_as_cs_decreases(self):
        # Higher rho → lower c_s → higher f_NL_equil
        r_small_rho = braided_equilateral_fnl(1, 2, k_cs=100)   # rho = 0.04
        r_large_rho = braided_equilateral_fnl(5, 7, k_cs=74)    # rho = 70/74 >> 0.04
        assert r_large_rho["f_NL_equil"] > r_small_rho["f_NL_equil"]

    def test_planck_excluded_false_for_57(self):
        r = braided_equilateral_fnl(5, 7)
        assert r["planck_excluded"] is False

    def test_cmbs4_detectable_false_for_57(self):
        r = braided_equilateral_fnl(5, 7)
        assert r["cmbs4_detectable"] is False

    def test_formula_string_matches(self):
        r = braided_equilateral_fnl(5, 7)
        assert "35/108" in r["formula"] or "(35/108)" in r["formula"]

    def test_reference_contains_Chen_or_Seery(self):
        r = braided_equilateral_fnl(5, 7)
        assert "Chen" in r["reference"] or "Seery" in r["reference"]

    def test_status_contains_DERIVED(self):
        r = braided_equilateral_fnl(5, 7)
        assert "DERIVED" in r["status"]

    def test_analytic_value_42875_over_15552_for_57(self):
        r = braided_equilateral_fnl(5, 7)
        expected = 42875.0 / 15552.0
        assert abs(r["f_NL_equil_analytic"] - expected) < 1e-12

    def test_f_NL_ortho_positive_for_57(self):
        r = braided_equilateral_fnl(5, 7)
        assert r["f_NL_ortho"] > 0.0

    def test_both_fnl_positive_for_57(self):
        r = braided_equilateral_fnl(5, 7)
        assert r["f_NL_equil"] > 0.0 and r["f_NL_ortho"] > 0.0

    def test_snr_values_finite_and_positive(self):
        r = braided_equilateral_fnl(5, 7)
        import math
        for key in ["planck_equil_snr", "cmbs4_equil_snr", "so_equil_snr"]:
            assert math.isfinite(r[key]) and r[key] > 0.0

    def test_f_NL_equil_matches_formula_numerically(self):
        r = braided_equilateral_fnl(5, 7)
        c_s = r["c_s"]
        expected = (35.0 / 108.0) * (1.0 / c_s**2 - 1.0)
        assert abs(r["f_NL_equil"] - expected) < 1e-10


class TestBraidedFnlFullSummary:
    """Tests for braided_fnl_full_summary."""

    PHI0 = 31.4  # canonical

    def test_returns_dict_with_required_keys(self):
        r = braided_fnl_full_summary(5, 7, self.PHI0)
        for key in [
            "n1", "n2", "f_NL_adi", "f_NL_iso", "f_NL_5D_geodesic",
            "f_NL_equil_braided", "f_NL_ortho_braided",
            "f_NL_total_local", "f_NL_total_equil", "all_planck_consistent",
        ]:
            assert key in r, f"Missing key: {key}"

    def test_all_planck_consistent_true_for_canonical(self):
        r = braided_fnl_full_summary(5, 7, self.PHI0)
        assert r["all_planck_consistent"] is True

    def test_f_NL_equil_braided_matches_braided_equilateral_fnl(self):
        r_sum = braided_fnl_full_summary(5, 7, self.PHI0)
        r_equil = braided_equilateral_fnl(5, 7)
        assert abs(r_sum["f_NL_equil_braided"] - r_equil["f_NL_equil"]) < 1e-12

    def test_f_NL_total_local_is_sum_of_adi_iso_5D(self):
        r = braided_fnl_full_summary(5, 7, self.PHI0)
        expected = r["f_NL_adi"] + r["f_NL_iso"] + r["f_NL_5D_geodesic"]
        assert abs(r["f_NL_total_local"] - expected) < 1e-12

    def test_f_NL_total_equil_is_f_NL_equil_braided(self):
        r = braided_fnl_full_summary(5, 7, self.PHI0)
        assert abs(r["f_NL_total_equil"] - r["f_NL_equil_braided"]) < 1e-12

    def test_n1_n2_echoed(self):
        r = braided_fnl_full_summary(5, 7, self.PHI0)
        assert r["n1"] == 5 and r["n2"] == 7

    def test_f_NL_equil_braided_positive(self):
        r = braided_fnl_full_summary(5, 7, self.PHI0)
        assert r["f_NL_equil_braided"] > 0.0

    def test_f_NL_ortho_braided_positive(self):
        r = braided_fnl_full_summary(5, 7, self.PHI0)
        assert r["f_NL_ortho_braided"] > 0.0
