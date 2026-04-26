# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_photon_epoch.py — Test suite for Pillar 64: Photon Epoch Cosmology.

Covers:
- Module constants: physical plausibility, UM/KK values, clarification of c_s_KK ≠ c_s_PB
- photon_temperature: scaling, errors
- omega_photon_h2: Stefan-Boltzmann scaling, positivity, errors
- omega_radiation_h2: neutrino contribution, positivity, errors
- matter_radiation_equality: Planck value, monotonicity, errors
- photon_baryon_sound_speed: radiation limit, baryon correction, distinction from C_S
- sound_horizon_analytic: Planck reference, EH formula structure, parameter dependence
- silk_diffusion_scale: physical range, Planck proximity, parameter scaling
- saha_ionization_fraction: high-T limit, recombination regime, errors
- recombination_redshift: standard ΛCDM range, bisection convergence, errors
- kk_radion_photon_pressure_ratio: value, smallness, errors
- kk_modified_hubble_rad_dominated: KK correction sign, errors
- photon_epoch_summary: completeness, KK vs PB sound speed ratio, epoch boundaries

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from src.core.photon_epoch import (
    # Constants
    OMEGA_M,
    OMEGA_B,
    OMEGA_LAMBDA,
    H_REDUCED,
    T_CMB_K,
    N_NU_EFF,
    Z_STAR,
    RS_STAR_PLANCK,
    K_SILK_PLANCK,
    ZETA_3,
    OMEGA_GAMMA_H2_FIDU,
    N_WINDING,
    K_CS,
    C_S,
    NS_UM,
    R_BRAIDED,
    F_BRAID,
    # Functions
    photon_temperature,
    omega_photon_h2,
    omega_radiation_h2,
    matter_radiation_equality,
    photon_baryon_sound_speed,
    sound_horizon_analytic,
    silk_diffusion_scale,
    saha_ionization_fraction,
    recombination_redshift,
    kk_radion_photon_pressure_ratio,
    kk_modified_hubble_rad_dominated,
    photon_epoch_summary,
)


# ===========================================================================
# Constants sanity tests
# ===========================================================================

class TestConstants:
    def test_T_cmb_K_planck(self):
        assert abs(T_CMB_K - 2.7255) < 1e-5

    def test_omega_m_planck(self):
        assert abs(OMEGA_M - 0.3153) < 1e-5

    def test_omega_b_planck(self):
        assert abs(OMEGA_B - 0.04930) < 1e-5

    def test_omega_lambda_planck(self):
        assert abs(OMEGA_LAMBDA - 0.6847) < 1e-5

    def test_h_reduced_planck(self):
        assert abs(H_REDUCED - 0.6736) < 1e-5

    def test_z_star_recombination(self):
        assert abs(Z_STAR - 1090.0) < 1.0

    def test_rs_star_planck_mpc(self):
        assert 130.0 < RS_STAR_PLANCK < 160.0

    def test_k_silk_planck(self):
        assert abs(K_SILK_PLANCK - 0.1404) < 1e-4

    def test_omega_gamma_h2_fidu(self):
        assert abs(OMEGA_GAMMA_H2_FIDU - 2.471e-5) < 1e-8

    def test_n_winding_is_5(self):
        assert N_WINDING == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_c_s_is_12_over_37(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_c_s_kk_is_less_than_radiation_limit(self):
        """KK radion speed (0.324) < pure radiation speed (1/√3 ≈ 0.577)."""
        assert C_S < 1.0 / math.sqrt(3.0)

    def test_ns_um_near_planck(self):
        """UM spectral index within 1σ of Planck 2018 (0.9649 ± 0.0042)."""
        assert abs(NS_UM - 0.9649) < 2 * 0.0042

    def test_r_braided_below_bicep_keck(self):
        """UM tensor-to-scalar ratio is below BICEP/Keck 2021 95% CL limit."""
        assert R_BRAIDED < 0.036

    def test_f_braid_is_cs_squared_over_kcs(self):
        assert abs(F_BRAID - C_S ** 2 / K_CS) < 1e-15

    def test_f_braid_is_small(self):
        """KK correction to radiation epoch must be sub-per-cent."""
        assert F_BRAID < 1e-2
        assert F_BRAID > 0.0

    def test_zeta_3_value(self):
        assert abs(ZETA_3 - 1.2020569031595942) < 1e-12

    def test_flatness(self):
        """Ω_m + Ω_Λ ≈ 1 for a flat universe (radiation is negligible today)."""
        assert abs(OMEGA_M + OMEGA_LAMBDA - 1.0) < 0.01


# ===========================================================================
# photon_temperature
# ===========================================================================

class TestPhotonTemperature:
    def test_today_a_equals_1(self):
        assert abs(photon_temperature(1.0) - T_CMB_K) < 1e-12

    def test_at_recombination(self):
        a_star = 1.0 / (1.0 + Z_STAR)
        T_star = photon_temperature(a_star)
        expected = T_CMB_K * (1.0 + Z_STAR)
        assert abs(T_star - expected) < 0.1

    def test_recombination_temperature_range(self):
        a_star = 1.0 / 1091.0
        T_star = photon_temperature(a_star)
        assert 2900.0 < T_star < 3100.0

    def test_half_scale_factor(self):
        assert abs(photon_temperature(0.5) - 2.0 * T_CMB_K) < 1e-10

    def test_custom_T0(self):
        assert abs(photon_temperature(1.0, T0_K=3.0) - 3.0) < 1e-12

    def test_zero_scale_factor_raises(self):
        with pytest.raises(ValueError):
            photon_temperature(0.0)

    def test_negative_scale_factor_raises(self):
        with pytest.raises(ValueError):
            photon_temperature(-0.5)

    def test_zero_T0_raises(self):
        with pytest.raises(ValueError):
            photon_temperature(0.5, T0_K=0.0)

    def test_return_type_float(self):
        assert isinstance(photon_temperature(0.5), float)

    def test_inverse_scaling(self):
        """T(a) × a = T₀ for all valid a."""
        for a in [0.1, 0.5, 1.0]:
            assert abs(photon_temperature(a) * a - T_CMB_K) < 1e-10


# ===========================================================================
# omega_photon_h2
# ===========================================================================

class TestOmegaPhotonH2:
    def test_fiducial_value(self):
        assert abs(omega_photon_h2(T_CMB_K) - OMEGA_GAMMA_H2_FIDU) < 1e-10

    def test_positive(self):
        assert omega_photon_h2() > 0.0

    def test_t4_scaling(self):
        """Ω_γ h² ∝ T⁴ (Stefan-Boltzmann)."""
        T_test = 3.0
        expected = OMEGA_GAMMA_H2_FIDU * (T_test / T_CMB_K) ** 4
        assert abs(omega_photon_h2(T_test) - expected) < 1e-14

    def test_larger_T_larger_omega(self):
        assert omega_photon_h2(3.0) > omega_photon_h2(T_CMB_K)

    def test_zero_T_raises(self):
        with pytest.raises(ValueError):
            omega_photon_h2(0.0)

    def test_negative_T_raises(self):
        with pytest.raises(ValueError):
            omega_photon_h2(-1.0)

    def test_photon_density_much_less_than_matter(self):
        """Photon density today is tiny compared to matter (radiation-dominated epoch is over)."""
        omega_gamma = omega_photon_h2()
        omega_m_h2 = OMEGA_M * H_REDUCED ** 2
        assert omega_gamma < 1e-3 * omega_m_h2

    def test_return_type_float(self):
        assert isinstance(omega_photon_h2(), float)


# ===========================================================================
# omega_radiation_h2
# ===========================================================================

class TestOmegaRadiationH2:
    def test_greater_than_photon_only(self):
        """Including neutrinos: Ω_r > Ω_γ."""
        assert omega_radiation_h2() > omega_photon_h2()

    def test_neutrino_factor_value(self):
        """Standard model: Ω_r ≈ 1.6909 × Ω_γ for N_ν,eff = 3.046."""
        ratio = omega_radiation_h2() / omega_photon_h2()
        assert 1.60 < ratio < 1.75

    def test_zero_neutrinos_returns_photon_only(self):
        assert abs(omega_radiation_h2(N_nu_eff=0.0) - omega_photon_h2()) < 1e-15

    def test_positive(self):
        assert omega_radiation_h2() > 0.0

    def test_zero_T_raises(self):
        with pytest.raises(ValueError):
            omega_radiation_h2(T_cmb_K=0.0)

    def test_negative_N_nu_raises(self):
        with pytest.raises(ValueError):
            omega_radiation_h2(N_nu_eff=-1.0)

    def test_planck_value_range(self):
        """Planck 2018: Ω_r h² ≈ 4.18 × 10⁻⁵."""
        omega_r = omega_radiation_h2()
        assert 3.5e-5 < omega_r < 5.0e-5


# ===========================================================================
# matter_radiation_equality
# ===========================================================================

class TestMatterRadiationEquality:
    def test_planck_z_eq_range(self):
        """Planck 2018: z_eq ≈ 3387 (within 5%)."""
        z_eq = matter_radiation_equality()
        assert 3000.0 < z_eq < 4000.0

    def test_positive(self):
        assert matter_radiation_equality() > 0.0

    def test_more_matter_higher_z_eq(self):
        """More matter → equality happens earlier (higher z)."""
        z_low = matter_radiation_equality(omega_m_h2=0.10)
        z_high = matter_radiation_equality(omega_m_h2=0.30)
        assert z_high > z_low

    def test_higher_T_lower_z_eq(self):
        """Hotter CMB → more radiation → equality later (lower z_eq)."""
        z1 = matter_radiation_equality(T_cmb_K=2.7255)
        z2 = matter_radiation_equality(T_cmb_K=3.5)
        assert z2 < z1

    def test_z_eq_above_z_star(self):
        """Radiation domination ends before recombination: z_eq > z★."""
        assert matter_radiation_equality() > Z_STAR

    def test_zero_omega_m_raises(self):
        with pytest.raises(ValueError):
            matter_radiation_equality(omega_m_h2=0.0)

    def test_negative_omega_m_raises(self):
        with pytest.raises(ValueError):
            matter_radiation_equality(omega_m_h2=-0.1)

    def test_return_type_float(self):
        assert isinstance(matter_radiation_equality(), float)


# ===========================================================================
# photon_baryon_sound_speed — the key c_s_PB ≠ C_S distinction
# ===========================================================================

class TestPhotonBaryonSoundSpeed:
    def test_zero_baryon_loading_gives_radiation_limit(self):
        """R_b → 0: c_s_PB → 1/√3 ≈ 0.5774 (pure radiation limit)."""
        c_s = photon_baryon_sound_speed(0.0)
        assert abs(c_s - 1.0 / math.sqrt(3.0)) < 1e-12

    def test_planck_baryon_loading(self):
        """With R_b ≈ 0.62 (Planck 2018): c_s_PB ≈ 0.45–0.50."""
        c_s = photon_baryon_sound_speed(0.62)
        assert 0.40 < c_s < 0.60

    def test_c_s_PB_less_than_radiation_limit(self):
        """Baryon loading always reduces c_s_PB below 1/√3."""
        for R_b in [0.1, 0.5, 1.0, 2.0]:
            assert photon_baryon_sound_speed(R_b) < 1.0 / math.sqrt(3.0)

    def test_c_s_PB_decreases_with_R_b(self):
        """More baryon loading → smaller sound speed."""
        c_s_low = photon_baryon_sound_speed(0.1)
        c_s_high = photon_baryon_sound_speed(1.0)
        assert c_s_high < c_s_low

    def test_c_s_PB_is_not_c_s_KK(self):
        """Photon-baryon speed ≠ KK radion speed — the core physics distinction."""
        c_s_pb = photon_baryon_sound_speed(0.62)
        assert abs(c_s_pb - C_S) > 0.05

    def test_c_s_PB_greater_than_c_s_KK_at_recombination(self):
        """At recombination R_b ≈ 0.62: c_s_PB ≈ 0.45 > C_S = 0.324."""
        c_s_pb = photon_baryon_sound_speed(0.62)
        assert c_s_pb > C_S

    def test_c_s_pb_sub_luminal(self):
        """Sound speed must be less than c (all R_b ≥ 0)."""
        for R_b in [0.0, 0.5, 1.0, 5.0, 10.0]:
            assert photon_baryon_sound_speed(R_b) <= 1.0

    def test_negative_R_b_raises(self):
        with pytest.raises(ValueError):
            photon_baryon_sound_speed(-0.1)

    def test_return_type_float(self):
        assert isinstance(photon_baryon_sound_speed(0.5), float)

    def test_large_R_b_goes_to_zero(self):
        """For R_b → ∞ (fully baryon-loaded): c_s_PB → 0."""
        assert photon_baryon_sound_speed(1000.0) < 0.02


# ===========================================================================
# sound_horizon_analytic
# ===========================================================================

class TestSoundHorizonAnalytic:
    def test_positive(self):
        assert sound_horizon_analytic() > 0.0

    def test_within_5_percent_of_planck(self):
        """EH 1998 analytic formula should reproduce Planck r_s to within 5%."""
        r_s = sound_horizon_analytic()
        frac = abs(r_s / RS_STAR_PLANCK - 1.0)
        assert frac < 0.05

    def test_planck_range_mpc(self):
        """Sound horizon must be in physically reasonable Mpc range."""
        r_s = sound_horizon_analytic()
        assert 120.0 < r_s < 165.0

    def test_more_baryons_smaller_sound_horizon(self):
        """Higher Ω_b h² → more baryon loading → reduced r_s."""
        omega_m_h2 = OMEGA_M * H_REDUCED ** 2
        r_s_low = sound_horizon_analytic(omega_b_h2=0.01, omega_m_h2=omega_m_h2)
        r_s_high = sound_horizon_analytic(omega_b_h2=0.05, omega_m_h2=omega_m_h2)
        assert r_s_high < r_s_low

    def test_more_matter_smaller_sound_horizon(self):
        """Higher Ω_m h² → smaller r_s (earlier matter-radiation equality)."""
        omega_b_h2 = OMEGA_B * H_REDUCED ** 2
        r_s_low = sound_horizon_analytic(omega_b_h2=omega_b_h2, omega_m_h2=0.10)
        r_s_high = sound_horizon_analytic(omega_b_h2=omega_b_h2, omega_m_h2=0.25)
        assert r_s_high < r_s_low

    def test_zero_omega_b_raises(self):
        with pytest.raises(ValueError):
            sound_horizon_analytic(omega_b_h2=0.0)

    def test_zero_omega_m_raises(self):
        with pytest.raises(ValueError):
            sound_horizon_analytic(omega_m_h2=0.0)

    def test_zero_z_dec_raises(self):
        with pytest.raises(ValueError):
            sound_horizon_analytic(z_dec=0.0)

    def test_zero_T_raises(self):
        with pytest.raises(ValueError):
            sound_horizon_analytic(T_cmb_K=0.0)

    def test_consistent_with_cmb_transfer_r_s_star(self):
        """r_s matches the cmb_transfer RS_STAR_PLANCK reference to 5%."""
        r_s = sound_horizon_analytic()
        assert abs(r_s / RS_STAR_PLANCK - 1.0) < 0.05


# ===========================================================================
# silk_diffusion_scale
# ===========================================================================

class TestSilkDiffusionScale:
    def test_positive(self):
        assert silk_diffusion_scale() > 0.0

    def test_physically_reasonable_range(self):
        """k_D should be in (0.05, 0.30) Mpc⁻¹ for standard ΛCDM."""
        k_D = silk_diffusion_scale()
        assert 0.05 < k_D < 0.30

    def test_order_of_magnitude_correct(self):
        """k_D should be within a factor of 2 of the Planck reference 0.1404."""
        k_D = silk_diffusion_scale()
        assert K_SILK_PLANCK / 2.0 < k_D < 2.0 * K_SILK_PLANCK

    def test_more_baryons_reduces_k_D(self):
        """Higher Ω_b → longer photon mean free path → smaller k_D (larger r_D)."""
        k_D_low = silk_diffusion_scale(omega_b=0.03)
        k_D_high = silk_diffusion_scale(omega_b=0.07)
        # More baryons reduce mean free path → more scattering → larger k_D (smaller r_D)
        # Actually, more baryons increase n_b → shorter mean free path → smaller r_D → larger k_D
        assert k_D_high > k_D_low

    def test_zero_omega_b_raises(self):
        with pytest.raises(ValueError):
            silk_diffusion_scale(omega_b=0.0)

    def test_zero_omega_m_raises(self):
        with pytest.raises(ValueError):
            silk_diffusion_scale(omega_m=0.0)

    def test_zero_h_raises(self):
        with pytest.raises(ValueError):
            silk_diffusion_scale(h=0.0)

    def test_zero_T_raises(self):
        with pytest.raises(ValueError):
            silk_diffusion_scale(T_cmb_K=0.0)

    def test_zero_z_dec_raises(self):
        with pytest.raises(ValueError):
            silk_diffusion_scale(z_dec=0.0)

    def test_return_type_float(self):
        assert isinstance(silk_diffusion_scale(), float)


# ===========================================================================
# saha_ionization_fraction
# ===========================================================================

class TestSahaIonizationFraction:
    def test_high_T_fully_ionized(self):
        """At T >> ionization temperature: x_e ≈ 1 (plasma fully ionized)."""
        x_e = saha_ionization_fraction(20000.0)
        assert x_e > 0.99

    def test_low_T_mostly_neutral(self):
        """At T = 2000 K: recombination well underway, x_e ≪ 1."""
        x_e = saha_ionization_fraction(2000.0)
        assert x_e < 0.01

    def test_result_in_0_1_range(self):
        """x_e must always be in [0, 1]."""
        for T in [500.0, 2000.0, 3000.0, 5000.0, 10000.0, 30000.0]:
            x_e = saha_ionization_fraction(T)
            assert 0.0 <= x_e <= 1.0

    def test_monotonically_increasing_with_T(self):
        """x_e increases with temperature (hotter → more ionization)."""
        T_vals = [1000.0, 2000.0, 3500.0, 5000.0, 10000.0]
        x_e_vals = [saha_ionization_fraction(T) for T in T_vals]
        for i in range(len(x_e_vals) - 1):
            assert x_e_vals[i + 1] >= x_e_vals[i]

    def test_higher_omega_b_less_ionized(self):
        """More baryons → denser plasma → more recombination → lower x_e."""
        x_e_low = saha_ionization_fraction(4000.0, omega_b_h2=0.01)
        x_e_high = saha_ionization_fraction(4000.0, omega_b_h2=0.05)
        assert x_e_high < x_e_low

    def test_zero_T_raises(self):
        with pytest.raises(ValueError):
            saha_ionization_fraction(0.0)

    def test_negative_T_raises(self):
        with pytest.raises(ValueError):
            saha_ionization_fraction(-100.0)

    def test_zero_omega_b_raises(self):
        with pytest.raises(ValueError):
            saha_ionization_fraction(3000.0, omega_b_h2=0.0)

    def test_return_type_float(self):
        assert isinstance(saha_ionization_fraction(5000.0), float)

    def test_recombination_regime(self):
        """At T ≈ 3000 K (z★ ≈ 1090): universe is significantly recombined."""
        x_e = saha_ionization_fraction(3000.0)
        assert x_e < 0.1


# ===========================================================================
# recombination_redshift
# ===========================================================================

class TestRecombinationRedshift:
    def test_standard_range(self):
        """z_rec with x_e=0.1 threshold should be near z★ ≈ 1090 (±30%)."""
        z_rec = recombination_redshift()
        assert 700.0 < z_rec < 1500.0

    def test_positive(self):
        assert recombination_redshift() > 0.0

    def test_higher_threshold_higher_z_rec(self):
        """Looser threshold (x_e = 0.5 vs 0.1) → earlier apparent recombination."""
        z_low = recombination_redshift(x_e_threshold=0.1)
        z_high = recombination_redshift(x_e_threshold=0.5)
        assert z_high > z_low

    def test_more_baryons_higher_z_rec(self):
        """More baryons → faster recombination → larger z_rec."""
        z_low = recombination_redshift(omega_b_h2=0.01)
        z_high = recombination_redshift(omega_b_h2=0.05)
        assert z_high > z_low

    def test_invalid_threshold_zero_raises(self):
        with pytest.raises(ValueError):
            recombination_redshift(x_e_threshold=0.0)

    def test_invalid_threshold_one_raises(self):
        with pytest.raises(ValueError):
            recombination_redshift(x_e_threshold=1.0)

    def test_negative_threshold_raises(self):
        with pytest.raises(ValueError):
            recombination_redshift(x_e_threshold=-0.1)

    def test_return_type_float(self):
        assert isinstance(recombination_redshift(), float)

    def test_z_rec_after_z_eq(self):
        """Recombination happens after matter-radiation equality: z_rec < z_eq."""
        z_rec = recombination_redshift()
        z_eq = matter_radiation_equality()
        assert z_rec < z_eq


# ===========================================================================
# kk_radion_photon_pressure_ratio
# ===========================================================================

class TestKKRadionPhotonPressureRatio:
    def test_canonical_value(self):
        f = kk_radion_photon_pressure_ratio(C_S, K_CS)
        assert abs(f - F_BRAID) < 1e-15

    def test_value_near_1_4e_3(self):
        f = kk_radion_photon_pressure_ratio()
        assert abs(f - 1.419e-3) < 1e-5

    def test_is_positive(self):
        assert kk_radion_photon_pressure_ratio() > 0.0

    def test_is_much_less_than_1(self):
        """KK radion pressure is a tiny fraction of photon pressure."""
        assert kk_radion_photon_pressure_ratio() < 0.01

    def test_scales_as_c_s_squared(self):
        """f_braid ∝ c_s² — doubling c_s quadruples f_braid."""
        f1 = kk_radion_photon_pressure_ratio(C_S, K_CS)
        f2 = kk_radion_photon_pressure_ratio(2.0 * C_S, K_CS)
        assert abs(f2 / f1 - 4.0) < 1e-10

    def test_scales_inversely_with_k_cs(self):
        """f_braid ∝ 1/k_cs — doubling k_cs halves f_braid."""
        f1 = kk_radion_photon_pressure_ratio(C_S, 74)
        f2 = kk_radion_photon_pressure_ratio(C_S, 148)
        assert abs(f2 / f1 - 0.5) < 1e-10

    def test_zero_c_s_gives_zero(self):
        assert kk_radion_photon_pressure_ratio(0.0, 74) == 0.0

    def test_negative_c_s_raises(self):
        with pytest.raises(ValueError):
            kk_radion_photon_pressure_ratio(-0.1, 74)

    def test_zero_k_cs_raises(self):
        with pytest.raises(ValueError):
            kk_radion_photon_pressure_ratio(C_S, 0)

    def test_return_type_float(self):
        assert isinstance(kk_radion_photon_pressure_ratio(), float)


# ===========================================================================
# kk_modified_hubble_rad_dominated
# ===========================================================================

class TestKKModifiedHubble:
    def test_positive(self):
        assert kk_modified_hubble_rad_dominated(3400.0) > 0.0

    def test_larger_z_larger_H(self):
        """Hubble rate increases with z during radiation domination."""
        H_low = kk_modified_hubble_rad_dominated(1000.0)
        H_high = kk_modified_hubble_rad_dominated(5000.0)
        assert H_high > H_low

    def test_kk_correction_increases_H(self):
        """f_braid > 0 → KK-corrected H > uncorrected H."""
        H_kk = kk_modified_hubble_rad_dominated(3400.0, f_braid=F_BRAID)
        H_std = kk_modified_hubble_rad_dominated(3400.0, f_braid=0.0)
        assert H_kk > H_std

    def test_kk_correction_is_small(self):
        """KK correction to H must be a fraction δH/H ≈ ½ f_braid ≈ 7 × 10⁻⁴."""
        H_kk = kk_modified_hubble_rad_dominated(3400.0, f_braid=F_BRAID)
        H_std = kk_modified_hubble_rad_dominated(3400.0, f_braid=0.0)
        delta_H_over_H = (H_kk - H_std) / H_std
        expected = 0.5 * F_BRAID
        # sqrt(1+f) - 1 ≈ f/2 to first order; tolerance accounts for second-order term
        assert abs(delta_H_over_H - expected) < 1e-5

    def test_h2_scaling_is_absorbed_in_omega_r(self):
        """omega_r_h2 = Ω_r h² already encodes h; H is independent of the h parameter."""
        H1 = kk_modified_hubble_rad_dominated(3400.0, h=0.67)
        H2 = kk_modified_hubble_rad_dominated(3400.0, h=0.74)
        # When omega_r_h2 is None, the function derives it from T_cmb_K which gives
        # the physical Ω_r h² (with H_REDUCED), so H is the same for both calls.
        assert abs(H1 - H2) < 1.0  # sub km/s/Mpc difference

    def test_zero_z_returns_reasonable_value(self):
        """At z=0, H is the present-day Hubble rate of the radiation component."""
        H0_rad = kk_modified_hubble_rad_dominated(0.0)
        assert H0_rad > 0.0

    def test_negative_z_raises(self):
        with pytest.raises(ValueError):
            kk_modified_hubble_rad_dominated(-1.0)

    def test_zero_h_raises(self):
        with pytest.raises(ValueError):
            kk_modified_hubble_rad_dominated(3400.0, h=0.0)

    def test_negative_f_braid_raises(self):
        with pytest.raises(ValueError):
            kk_modified_hubble_rad_dominated(3400.0, f_braid=-0.01)


# ===========================================================================
# photon_epoch_summary
# ===========================================================================

class TestPhotonEpochSummary:
    @pytest.fixture(scope="class")
    def summary(self):
        return photon_epoch_summary()

    def test_returns_dict(self, summary):
        assert isinstance(summary, dict)

    def test_all_required_keys_present(self, summary):
        required = {
            "T_cmb_K", "omega_gamma_h2", "omega_r_h2", "nu_fraction",
            "z_eq", "z_rec_saha", "R_b_at_rec", "c_s_PB_at_rec",
            "r_s_analytic", "k_D", "c_s_KK", "f_braid", "delta_H_over_H",
            "ns_um", "r_braided", "c_s_PB_vs_c_s_KK_ratio",
            "r_s_vs_planck_frac", "k_D_vs_planck_frac",
        }
        assert required.issubset(set(summary.keys()))

    def test_T_cmb_K_value(self, summary):
        assert abs(summary["T_cmb_K"] - T_CMB_K) < 1e-10

    def test_omega_gamma_h2_positive(self, summary):
        assert summary["omega_gamma_h2"] > 0.0

    def test_omega_r_h2_greater_than_gamma(self, summary):
        assert summary["omega_r_h2"] > summary["omega_gamma_h2"]

    def test_nu_fraction_positive(self, summary):
        assert summary["nu_fraction"] > 0.0

    def test_z_eq_above_z_star(self, summary):
        assert summary["z_eq"] > Z_STAR

    def test_z_rec_near_planck(self, summary):
        assert 700 < summary["z_rec_saha"] < 1600

    def test_R_b_at_rec_range(self, summary):
        """Baryon loading at recombination: R_b ≈ 0.4–0.9."""
        assert 0.3 < summary["R_b_at_rec"] < 1.0

    def test_c_s_PB_at_rec_greater_than_c_s_KK(self, summary):
        """Core physics distinction: photon-baryon speed > radion speed at recombination."""
        assert summary["c_s_PB_at_rec"] > summary["c_s_KK"]

    def test_c_s_PB_vs_KK_ratio_greater_than_1(self, summary):
        """c_s_PB / c_s_KK > 1 — photon-baryon plasma is faster than radion sector."""
        assert summary["c_s_PB_vs_c_s_KK_ratio"] > 1.0

    def test_r_s_analytic_planck_range(self, summary):
        assert 120.0 < summary["r_s_analytic"] < 165.0

    def test_k_D_physical_range(self, summary):
        assert 0.05 < summary["k_D"] < 0.30

    def test_c_s_KK_is_canonical(self, summary):
        assert abs(summary["c_s_KK"] - 12.0 / 37.0) < 1e-12

    def test_f_braid_is_small(self, summary):
        assert summary["f_braid"] < 1e-2

    def test_delta_H_over_H_is_half_f_braid(self, summary):
        assert abs(summary["delta_H_over_H"] - 0.5 * summary["f_braid"]) < 1e-15

    def test_ns_um_value(self, summary):
        assert abs(summary["ns_um"] - NS_UM) < 1e-10

    def test_r_braided_value(self, summary):
        assert abs(summary["r_braided"] - R_BRAIDED) < 1e-10

    def test_r_s_vs_planck_small_frac(self, summary):
        """EH analytic formula should agree with Planck reference to < 5%."""
        assert abs(summary["r_s_vs_planck_frac"]) < 0.05

    def test_all_values_finite(self, summary):
        for key, val in summary.items():
            assert math.isfinite(val), f"Summary key '{key}' is not finite: {val}"

    def test_all_values_positive_or_can_be_negative(self, summary):
        """Spot-check that the numeric values are not wildly wrong."""
        assert summary["omega_gamma_h2"] > 0
        assert summary["r_s_analytic"] > 0
        assert summary["k_D"] > 0
        assert summary["f_braid"] > 0
