# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_lattice_boltzmann.py
================================
Pillar 15-C — Tests for src/core/lattice_boltzmann.py.

Verifies the Unitary Collision Integral for lattice heat transport in the
Pd-D system.  Two hard benchmarks that must pass with canonical UM parameters:

    1. Prompt gamma ratio  P_γ < 10⁻⁶
    2. Thermalization time τ_eff ∈ [0.1, 100] fs

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

import numpy as np
import pytest

from src.core.lattice_boltzmann import (
    # constants
    C_S,
    DD_GAMMA_STANDARD,
    DD_Q_GAMMA_MEV,
    DD_Q_HE3_MEV,
    DD_Q_T_MEV,
    FS_TO_S,
    H_MAX_CANONICAL,
    HBAR_J_S,
    K_B_J_PER_K,
    K_CS,
    MEV_TO_J,
    N_W,
    N_W_BRAID,
    OMEGA_DEBYE_PD,
    PHI_MEAN_CANONICAL,
    RADION_COUPLING_BRAID,
    RADION_COUPLING_CANON,
    T_DEBYE_PD_K,
    TAU_PHONON_PD_S,
    # functions
    bmu_relaxation_time,
    bose_einstein,
    braid_coupling_comparison,
    calculate_cop,
    energy_branching,
    gamma_breakeven_coupling,
    lattice_heat_power,
    phonon_distribution_evolution,
    prompt_gamma_ratio,
    radion_phonon_coupling,
    sensitivity_sweep,
    tau_breakeven_tau_bmu,
    thermalization_time,
    thermalization_time_fs,
    unitary_collision_integral,
    validate_um_predictions,
)


# ===========================================================================
# Constants
# ===========================================================================


class TestConstants:
    def test_nw_is_five(self):
        assert N_W == 5

    def test_kcs_is_74(self):
        assert K_CS == 74

    def test_kcs_is_sum_of_squares(self):
        assert K_CS == 5 ** 2 + 7 ** 2

    def test_cs_value(self):
        assert C_S == pytest.approx(12.0 / 37.0, rel=1e-10)

    def test_radion_coupling_canon_positive(self):
        assert RADION_COUPLING_CANON > 0.0

    def test_radion_coupling_canon_formula(self):
        expected = N_W * np.sqrt(K_CS) * C_S
        assert RADION_COUPLING_CANON == pytest.approx(expected, rel=1e-10)

    def test_radion_coupling_canon_approx_14(self):
        # g ≈ 13.95 for canonical parameters
        assert 13.0 < RADION_COUPLING_CANON < 15.0

    def test_g_squared_approx_194(self):
        g2 = RADION_COUPLING_CANON ** 2
        assert 190.0 < g2 < 200.0

    def test_dd_q_he3_positive(self):
        assert DD_Q_HE3_MEV > 0.0

    def test_dd_q_t_positive(self):
        assert DD_Q_T_MEV > 0.0

    def test_dd_q_he3_value(self):
        assert DD_Q_HE3_MEV == pytest.approx(3.27, rel=1e-6)

    def test_dd_q_t_value(self):
        assert DD_Q_T_MEV == pytest.approx(4.03, rel=1e-6)

    def test_dd_gamma_standard_small(self):
        assert 1e-8 < DD_GAMMA_STANDARD < 1e-4

    def test_debye_temp_pd(self):
        assert 250.0 < T_DEBYE_PD_K < 300.0

    def test_omega_debye_positive(self):
        assert OMEGA_DEBYE_PD > 0.0

    def test_tau_phonon_pd_scale(self):
        # Should be ~200 fs = 2×10⁻¹³ s
        assert 1e-14 < TAU_PHONON_PD_S < 1e-11

    def test_fs_to_s_value(self):
        assert FS_TO_S == pytest.approx(1e-15, rel=1e-10)

    # --- Braid coupling constants (Gemini analysis, April 2026) ---

    def test_nw_braid_is_12(self):
        assert N_W_BRAID == 12

    def test_nw_braid_is_n1_plus_n2(self):
        assert N_W_BRAID == 5 + 7

    def test_radion_coupling_braid_positive(self):
        assert RADION_COUPLING_BRAID > 0.0

    def test_radion_coupling_braid_formula(self):
        expected = N_W_BRAID * np.sqrt(K_CS) * C_S
        assert RADION_COUPLING_BRAID == pytest.approx(expected, rel=1e-10)

    def test_radion_coupling_braid_approx_33(self):
        # g_braid ≈ 33.48 for n_w=12
        assert 32.0 < RADION_COUPLING_BRAID < 35.0

    def test_braid_coupling_larger_than_canon(self):
        assert RADION_COUPLING_BRAID > RADION_COUPLING_CANON

    def test_braid_to_canon_ratio(self):
        # ratio = N_W_BRAID / N_W = 12/5 = 2.4
        ratio = RADION_COUPLING_BRAID / RADION_COUPLING_CANON
        assert ratio == pytest.approx(N_W_BRAID / N_W, rel=1e-10)


# ===========================================================================
# bose_einstein
# ===========================================================================


class TestBoseEinstein:
    def test_positive_for_positive_omega(self):
        f0 = bose_einstein(OMEGA_DEBYE_PD, 300.0)
        assert f0 > 0.0

    def test_increases_with_temperature(self):
        f_low = bose_einstein(OMEGA_DEBYE_PD, 100.0)
        f_high = bose_einstein(OMEGA_DEBYE_PD, 600.0)
        assert f_high > f_low

    def test_decreases_with_frequency(self):
        f_low_om = bose_einstein(OMEGA_DEBYE_PD * 0.1, 300.0)
        f_high_om = bose_einstein(OMEGA_DEBYE_PD, 300.0)
        assert f_low_om > f_high_om

    def test_array_input(self):
        omega_arr = np.linspace(1e11, OMEGA_DEBYE_PD, 20)
        f0 = bose_einstein(omega_arr, 300.0)
        assert f0.shape == (20,)
        assert np.all(f0 > 0.0)

    def test_invalid_temperature(self):
        with pytest.raises(ValueError):
            bose_einstein(OMEGA_DEBYE_PD, 0.0)
        with pytest.raises(ValueError):
            bose_einstein(OMEGA_DEBYE_PD, -10.0)

    def test_high_temperature_classical_limit(self):
        # For kT >> ℏω: f0 ≈ kT/(ℏω) >> 1
        omega_low = 1e10  # very low frequency
        T_high = 3000.0
        f0 = bose_einstein(omega_low, T_high)
        classical_approx = K_B_J_PER_K * T_high / (HBAR_J_S * omega_low)
        assert f0 == pytest.approx(classical_approx, rel=0.01)

    def test_finite_everywhere(self):
        omega_arr = np.geomspace(1e10, OMEGA_DEBYE_PD * 2, 50)
        f0 = bose_einstein(omega_arr, 300.0)
        assert np.all(np.isfinite(f0))


# ===========================================================================
# bmu_relaxation_time
# ===========================================================================


class TestBmuRelaxationTime:
    def test_canonical_positive(self):
        tau = bmu_relaxation_time()
        assert tau > 0.0

    def test_canonical_shorter_than_tau0(self):
        tau = bmu_relaxation_time()
        assert tau < TAU_PHONON_PD_S

    def test_decreases_with_H_max(self):
        tau1 = bmu_relaxation_time(H_max=1.0)
        tau2 = bmu_relaxation_time(H_max=2.0)
        assert tau2 < tau1

    def test_decreases_with_phi_mean(self):
        tau1 = bmu_relaxation_time(phi_mean=1.0)
        tau2 = bmu_relaxation_time(phi_mean=4.0)
        assert tau2 < tau1

    def test_formula(self):
        tau = bmu_relaxation_time(H_max=1.5, phi_mean=3.0, tau0=TAU_PHONON_PD_S)
        expected = TAU_PHONON_PD_S / (1.5 * 3.0)
        assert tau == pytest.approx(expected, rel=1e-10)

    def test_invalid_H_max(self):
        with pytest.raises(ValueError):
            bmu_relaxation_time(H_max=0.0)
        with pytest.raises(ValueError):
            bmu_relaxation_time(H_max=-1.0)

    def test_invalid_phi_mean(self):
        with pytest.raises(ValueError):
            bmu_relaxation_time(phi_mean=0.0)

    def test_invalid_tau0(self):
        with pytest.raises(ValueError):
            bmu_relaxation_time(tau0=0.0)

    def test_canonical_scale_order(self):
        # canonical τ_Bmu = 2e-13 / (1.0 × 2.0) = 1e-13 s (100 fs)
        tau = bmu_relaxation_time()
        assert 1e-14 < tau < 1e-11


# ===========================================================================
# radion_phonon_coupling
# ===========================================================================


class TestRadionPhononCoupling:
    def test_canonical_value(self):
        g = radion_phonon_coupling()
        assert g == pytest.approx(RADION_COUPLING_CANON, rel=1e-10)

    def test_positive(self):
        assert radion_phonon_coupling() > 0.0

    def test_formula(self):
        g = radion_phonon_coupling(n_w=5.0, k_cs=74.0, c_s=12.0 / 37.0)
        expected = 5.0 * np.sqrt(74.0) * (12.0 / 37.0)
        assert g == pytest.approx(expected, rel=1e-10)

    def test_increases_with_nw(self):
        g1 = radion_phonon_coupling(n_w=3.0)
        g2 = radion_phonon_coupling(n_w=7.0)
        assert g2 > g1

    def test_increases_with_kcs(self):
        g1 = radion_phonon_coupling(k_cs=50.0)
        g2 = radion_phonon_coupling(k_cs=100.0)
        assert g2 > g1

    def test_invalid_nw(self):
        with pytest.raises(ValueError):
            radion_phonon_coupling(n_w=0.0)

    def test_invalid_kcs(self):
        with pytest.raises(ValueError):
            radion_phonon_coupling(k_cs=0.0)

    def test_invalid_cs(self):
        with pytest.raises(ValueError):
            radion_phonon_coupling(c_s=0.0)


# ===========================================================================
# unitary_collision_integral
# ===========================================================================


class TestUnitaryCollisionIntegral:
    def test_drives_toward_equilibrium_above(self):
        # f > f0 → collision term is negative (pushes down)
        f = np.array([2.0, 3.0, 4.0])
        f0 = np.ones(3)
        tau = 1e-13
        g = RADION_COUPLING_CANON
        C = unitary_collision_integral(f, f0, tau, g)
        assert np.all(C < 0.0)

    def test_drives_toward_equilibrium_below(self):
        # f < f0 → collision term is positive (pushes up)
        f = np.array([0.1, 0.2, 0.1])
        f0 = np.ones(3)
        tau = 1e-13
        g = RADION_COUPLING_CANON
        C = unitary_collision_integral(f, f0, tau, g)
        assert np.all(C > 0.0)

    def test_zero_when_at_equilibrium(self):
        f = np.array([1.0, 2.0, 3.0])
        f0 = f.copy()
        tau = 1e-13
        C = unitary_collision_integral(f, f0, tau, RADION_COUPLING_CANON)
        assert np.allclose(C, 0.0, atol=1e-30)

    def test_enhancement_factor(self):
        # C_UM = C_RTA × (1 + g²)
        f = np.array([2.0])
        f0 = np.array([1.0])
        tau = 1e-13
        g = RADION_COUPLING_CANON
        C_um = unitary_collision_integral(f, f0, tau, g)
        C_rta = -(f - f0) / tau
        expected = C_rta * (1.0 + g ** 2)
        assert np.allclose(C_um, expected, rtol=1e-10)

    def test_scalar_input(self):
        C = unitary_collision_integral(2.0, 1.0, 1e-13, RADION_COUPLING_CANON)
        assert np.isfinite(C)
        assert C < 0.0

    def test_invalid_tau(self):
        with pytest.raises(ValueError):
            unitary_collision_integral(2.0, 1.0, 0.0, RADION_COUPLING_CANON)
        with pytest.raises(ValueError):
            unitary_collision_integral(2.0, 1.0, -1e-13, RADION_COUPLING_CANON)

    def test_larger_coupling_gives_larger_rate(self):
        f = 2.0
        f0 = 1.0
        tau = 1e-13
        C_small = unitary_collision_integral(f, f0, tau, 1.0)
        C_large = unitary_collision_integral(f, f0, tau, RADION_COUPLING_CANON)
        assert abs(C_large) > abs(C_small)

    def test_output_shape_matches_input(self):
        f = np.ones(10) * 2.0
        f0 = np.ones(10)
        C = unitary_collision_integral(f, f0, 1e-13, RADION_COUPLING_CANON)
        assert C.shape == (10,)


# ===========================================================================
# thermalization_time  /  thermalization_time_fs
# ===========================================================================


class TestThermalizationTime:
    def test_canonical_in_femtosecond_range(self):
        """PRIMARY BENCHMARK: thermalization time must be in [0.1, 100] fs."""
        tau_Bmu = bmu_relaxation_time()
        g = radion_phonon_coupling()
        tau_fs = thermalization_time_fs(tau_Bmu, g)
        assert 0.1 <= tau_fs <= 100.0, (
            f"τ_eff = {tau_fs:.4f} fs is outside [0.1, 100] fs"
        )

    def test_shorter_than_tau_Bmu(self):
        tau_Bmu = bmu_relaxation_time()
        g = radion_phonon_coupling()
        tau_eff = thermalization_time(tau_Bmu, g)
        assert tau_eff < tau_Bmu

    def test_formula(self):
        tau_Bmu = 1e-13
        g = RADION_COUPLING_CANON
        expected = tau_Bmu / (1.0 + g ** 2)
        assert thermalization_time(tau_Bmu, g) == pytest.approx(expected, rel=1e-10)

    def test_fs_is_seconds_over_1e15(self):
        tau_Bmu = 1e-13
        g = RADION_COUPLING_CANON
        t_s = thermalization_time(tau_Bmu, g)
        t_fs = thermalization_time_fs(tau_Bmu, g)
        assert t_fs == pytest.approx(t_s / FS_TO_S, rel=1e-10)

    def test_decreases_with_coupling(self):
        tau_Bmu = 1e-13
        t1 = thermalization_time(tau_Bmu, 1.0)
        t2 = thermalization_time(tau_Bmu, RADION_COUPLING_CANON)
        assert t2 < t1

    def test_invalid_tau(self):
        with pytest.raises(ValueError):
            thermalization_time(0.0, RADION_COUPLING_CANON)

    def test_zero_coupling_returns_tau_Bmu(self):
        tau_Bmu = 1e-13
        t = thermalization_time(tau_Bmu, 0.0)
        assert t == pytest.approx(tau_Bmu, rel=1e-10)

    def test_canonical_value_below_5fs(self):
        tau_Bmu = bmu_relaxation_time()
        g = radion_phonon_coupling()
        tau_fs = thermalization_time_fs(tau_Bmu, g)
        # With canonical params, τ_eff ≈ 0.5 fs — solidly sub-femtosecond
        assert tau_fs < 5.0


# ===========================================================================
# prompt_gamma_ratio
# ===========================================================================


class TestPromptGammaRatio:
    def test_canonical_below_1e6(self):
        """PRIMARY BENCHMARK: prompt gamma ratio must be < 10⁻⁶."""
        g = radion_phonon_coupling()
        P_gamma = prompt_gamma_ratio(g)
        assert P_gamma < 1e-6, (
            f"Prompt gamma ratio {P_gamma:.3e} ≥ 10⁻⁶ — benchmark failed"
        )

    def test_canonical_much_smaller_than_standard(self):
        g = radion_phonon_coupling()
        P_gamma = prompt_gamma_ratio(g)
        assert P_gamma < DD_GAMMA_STANDARD

    def test_quadratic_suppression_formula(self):
        g = RADION_COUPLING_CANON
        gamma_std = DD_GAMMA_STANDARD
        expected = gamma_std / (1.0 + g ** 2) ** 2
        assert prompt_gamma_ratio(g, gamma_std) == pytest.approx(expected, rel=1e-10)

    def test_zero_coupling_returns_standard(self):
        P = prompt_gamma_ratio(0.0, DD_GAMMA_STANDARD)
        assert P == pytest.approx(DD_GAMMA_STANDARD, rel=1e-10)

    def test_decreases_with_coupling(self):
        P1 = prompt_gamma_ratio(1.0)
        P2 = prompt_gamma_ratio(RADION_COUPLING_CANON)
        assert P2 < P1

    def test_in_unit_interval(self):
        P = prompt_gamma_ratio(RADION_COUPLING_CANON)
        assert 0.0 <= P <= 1.0

    def test_invalid_gamma_standard(self):
        with pytest.raises(ValueError):
            prompt_gamma_ratio(RADION_COUPLING_CANON, gamma_standard=-0.1)
        with pytest.raises(ValueError):
            prompt_gamma_ratio(RADION_COUPLING_CANON, gamma_standard=1.5)

    def test_canonical_order_of_magnitude(self):
        # With canonical g² ≈ 194.6, suppression ≈ (195.6)² ≈ 3.83×10⁴
        # P_γ ≈ 3×10⁻⁷ / 3.83×10⁴ ≈ 7.8×10⁻¹²
        g = radion_phonon_coupling()
        P = prompt_gamma_ratio(g)
        assert P < 1e-10  # solidly below 10⁻⁶


# ===========================================================================
# energy_branching
# ===========================================================================


class TestEnergyBranching:
    def test_returns_dict(self):
        branch = energy_branching()
        assert isinstance(branch, dict)

    def test_required_keys(self):
        branch = energy_branching()
        required = {
            "Q_MeV", "tau_Bmu_s", "radion_coupling", "g_squared",
            "enhancement_factor", "tau_eff_s", "tau_eff_fs",
            "prompt_gamma_ratio", "prompt_gamma_ratio_standard",
            "phonon_fraction", "Q_lattice_MeV", "Q_gamma_MeV",
            "gamma_ratio_lt_1e6", "tau_in_fs_range",
        }
        assert required <= set(branch.keys())

    def test_gamma_ratio_benchmark_passes(self):
        """canonical parameters must satisfy P_γ < 10⁻⁶."""
        branch = energy_branching()
        assert branch["gamma_ratio_lt_1e6"] is True

    def test_tau_in_fs_benchmark_passes(self):
        """canonical parameters must satisfy τ_eff ∈ [0.1, 100] fs."""
        branch = energy_branching()
        assert branch["tau_in_fs_range"] is True

    def test_phonon_fraction_close_to_unity(self):
        branch = energy_branching()
        assert branch["phonon_fraction"] > 0.999

    def test_energy_conservation(self):
        branch = energy_branching()
        total = branch["Q_lattice_MeV"] + branch["Q_gamma_MeV"]
        assert total == pytest.approx(branch["Q_MeV"], rel=1e-6)

    def test_q_value_defaults_to_he3_channel(self):
        branch = energy_branching()
        assert branch["Q_MeV"] == pytest.approx(DD_Q_HE3_MEV, rel=1e-10)

    def test_t_channel_q_value(self):
        branch = energy_branching(Q_MeV=DD_Q_T_MEV)
        assert branch["Q_MeV"] == pytest.approx(DD_Q_T_MEV, rel=1e-10)

    def test_radion_coupling_stored(self):
        branch = energy_branching()
        assert branch["radion_coupling"] == pytest.approx(
            radion_phonon_coupling(), rel=1e-10
        )

    def test_enhancement_factor_large(self):
        branch = energy_branching()
        assert branch["enhancement_factor"] > 100.0

    def test_all_floats_finite(self):
        branch = energy_branching()
        for key, val in branch.items():
            if isinstance(val, float):
                assert np.isfinite(val), f"Non-finite value for key {key!r}: {val}"


# ===========================================================================
# phonon_distribution_evolution
# ===========================================================================


class TestPhononDistributionEvolution:
    def _make_f0(self):
        return bose_einstein(OMEGA_DEBYE_PD, 300.0)

    def test_starts_at_f_init(self):
        f_init = 5.0
        f0 = self._make_f0()
        t_arr = np.array([0.0, 1e-15, 1e-14])
        result = phonon_distribution_evolution(
            f_init, f0, bmu_relaxation_time(), RADION_COUPLING_CANON, t_arr
        )
        assert result[0] == pytest.approx(f_init, rel=1e-8)

    def test_converges_to_f0(self):
        f_init = 10.0
        f0 = self._make_f0()
        tau_Bmu = bmu_relaxation_time()
        g = RADION_COUPLING_CANON
        tau_eff = thermalization_time(tau_Bmu, g)
        # at t = 50 × τ_eff the distribution should be within 1e-20 of f0
        t_arr = np.array([50.0 * tau_eff])
        result = phonon_distribution_evolution(f_init, f0, tau_Bmu, g, t_arr)
        assert result[0] == pytest.approx(f0, rel=1e-6)

    def test_monotone_decay_above_f0(self):
        f_init = 10.0
        f0 = self._make_f0()
        t_arr = np.linspace(0, 5e-15, 20)
        result = phonon_distribution_evolution(
            f_init, f0, bmu_relaxation_time(), RADION_COUPLING_CANON, t_arr
        )
        # distribution should decrease monotonically toward f0
        diffs = np.diff(result)
        assert np.all(diffs <= 0.0)

    def test_monotone_increase_below_f0(self):
        f_init = 0.0
        f0 = self._make_f0()
        t_arr = np.linspace(0, 5e-15, 20)
        result = phonon_distribution_evolution(
            f_init, f0, bmu_relaxation_time(), RADION_COUPLING_CANON, t_arr
        )
        diffs = np.diff(result)
        assert np.all(diffs >= 0.0)

    def test_array_f_input(self):
        omega_arr = np.geomspace(1e11, OMEGA_DEBYE_PD, 10)
        f0 = bose_einstein(omega_arr, 300.0)
        f_init = f0 * 3.0  # start at 3× equilibrium
        t_arr = np.linspace(0, 1e-14, 5)
        result = phonon_distribution_evolution(
            f_init, f0, bmu_relaxation_time(), RADION_COUPLING_CANON, t_arr
        )
        assert result.shape == (10, 5)

    def test_invalid_tau(self):
        with pytest.raises(ValueError):
            phonon_distribution_evolution(
                2.0, 1.0, 0.0, RADION_COUPLING_CANON, np.array([1e-15])
            )

    def test_faster_with_larger_coupling(self):
        f_init = 5.0
        f0 = 1.0
        tau_Bmu = 1e-13
        t_arr = np.array([5e-15])
        result_small_g = phonon_distribution_evolution(f_init, f0, tau_Bmu, 1.0, t_arr)
        result_large_g = phonon_distribution_evolution(
            f_init, f0, tau_Bmu, RADION_COUPLING_CANON, t_arr
        )
        # larger coupling → closer to f0 in same time
        assert abs(result_large_g[0] - f0) < abs(result_small_g[0] - f0)


# ===========================================================================
# validate_um_predictions
# ===========================================================================


class TestValidateUmPredictions:
    def test_canonical_passes_all_benchmarks(self):
        result = validate_um_predictions()
        assert result["passed"] is True

    def test_gamma_ratio_lt_1e6_true(self):
        result = validate_um_predictions()
        assert result["gamma_ratio_lt_1e6"] is True

    def test_tau_in_fs_range_true(self):
        result = validate_um_predictions()
        assert result["tau_in_fs_range"] is True

    def test_returns_dict_with_required_keys(self):
        result = validate_um_predictions()
        required = {
            "passed", "gamma_ratio_lt_1e6", "tau_in_fs_range",
            "prompt_gamma_ratio", "tau_eff_fs", "radion_coupling",
            "g_squared", "enhancement_factor", "tau_Bmu_s",
        }
        assert required <= set(result.keys())

    def test_prompt_gamma_below_1e6(self):
        result = validate_um_predictions()
        assert result["prompt_gamma_ratio"] < 1e-6

    def test_tau_eff_fs_in_range(self):
        result = validate_um_predictions()
        assert 0.1 <= result["tau_eff_fs"] <= 100.0

    def test_enhancement_factor_value(self):
        result = validate_um_predictions()
        g = result["radion_coupling"]
        expected_enh = 1.0 + g ** 2
        assert result["enhancement_factor"] == pytest.approx(expected_enh, rel=1e-10)

    def test_g_squared_consistent(self):
        result = validate_um_predictions()
        g = result["radion_coupling"]
        assert result["g_squared"] == pytest.approx(g ** 2, rel=1e-10)

    def test_weak_coupling_fails_gamma_benchmark(self):
        # With g = 0 and a gamma_standard above 10⁻⁶, the benchmark fails.
        # (DD_GAMMA_STANDARD is already 3×10⁻⁷ < 10⁻⁶ in Pd; we raise it to
        # 5×10⁻⁶ to verify that the suppression is truly needed.)
        result = validate_um_predictions(radion_coupling=0.0, gamma_standard=5e-6)
        assert result["gamma_ratio_lt_1e6"] is False

    def test_weak_coupling_fails_tau_benchmark(self):
        # With g = 0, τ_eff = τ_Bmu ≈ 100 fs — right at the edge.
        # Use a long τ_Bmu to ensure it exceeds 100 fs with g=0.
        result = validate_um_predictions(
            tau_Bmu=2.0e-11,  # 20 000 fs >> 100 fs
            radion_coupling=0.0,
        )
        assert result["tau_in_fs_range"] is False


# ===========================================================================
# lattice_heat_power
# ===========================================================================


class TestLatticeHeatPower:
    def test_zero_rate_gives_zero_power(self):
        P = lattice_heat_power(0.0)
        assert P == pytest.approx(0.0, abs=1e-40)

    def test_positive_rate_gives_positive_power(self):
        P = lattice_heat_power(1e12)
        assert P > 0.0

    def test_scales_linearly_with_rate(self):
        P1 = lattice_heat_power(1e12)
        P2 = lattice_heat_power(2e12)
        assert P2 == pytest.approx(2.0 * P1, rel=1e-10)

    def test_scales_with_q_value(self):
        P_he3 = lattice_heat_power(1e12, Q_MeV=DD_Q_HE3_MEV)
        P_t = lattice_heat_power(1e12, Q_MeV=DD_Q_T_MEV)
        assert P_t > P_he3

    def test_phonon_fraction_close_to_one(self):
        # nearly all energy goes to lattice heat
        rate = 1e12
        P_full = rate * DD_Q_HE3_MEV * MEV_TO_J  # if phonon_fraction = 1
        P_um = lattice_heat_power(rate, Q_MeV=DD_Q_HE3_MEV)
        assert P_um / P_full > 0.999

    def test_invalid_rate(self):
        with pytest.raises(ValueError):
            lattice_heat_power(-1.0)

    def test_invalid_q(self):
        with pytest.raises(ValueError):
            lattice_heat_power(1e12, Q_MeV=0.0)
        with pytest.raises(ValueError):
            lattice_heat_power(1e12, Q_MeV=-1.0)

    def test_units_joules_per_s_per_cc(self):
        # 1 event/s/cm³ × 3.27 MeV ≈ 5.24×10⁻¹³ W/cm³
        P = lattice_heat_power(1.0, Q_MeV=DD_Q_HE3_MEV)
        expected_max = DD_Q_HE3_MEV * MEV_TO_J
        assert 0.0 < P <= expected_max

    def test_finite(self):
        P = lattice_heat_power(1e15)
        assert np.isfinite(P)


# ===========================================================================
# calculate_cop
# ===========================================================================


class TestCalculateCop:
    """COP = Q_heat / W_input; break-even at COP ≥ 1.0."""

    def _cop_above_breakeven(self):
        """Scenario where COP > 1: high fusion rate, low work input."""
        # 1e15 fusions/cm³/s is an optimistic scenario for illustrative testing.
        # The UM does NOT assert this rate is achievable at room temperature;
        # it asserts that IF that rate occurs, the COP is as computed.
        return calculate_cop(
            n_DD_per_cc_s=1e15,
            W_input_W_per_cc=1.0,
        )

    def _cop_below_breakeven(self):
        """Scenario where COP < 1: low fusion rate, high work input."""
        return calculate_cop(
            n_DD_per_cc_s=1.0,
            W_input_W_per_cc=1.0,
        )

    def test_returns_dict(self):
        result = calculate_cop(1e10, 1.0)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = calculate_cop(1e10, 1.0)
        required = {
            "n_DD_per_cc_s", "W_input_W_per_cc", "volume_cc", "Q_MeV",
            "radion_coupling", "phonon_fraction", "Q_lattice_W_per_cc",
            "Q_lattice_W_total", "W_input_W_total", "COP", "break_even",
            "COP_margin", "prompt_gamma_ratio",
        }
        assert required <= set(result.keys())

    def test_cop_positive(self):
        result = calculate_cop(1e10, 1.0)
        assert result["COP"] > 0.0

    def test_cop_above_breakeven_scenario(self):
        result = self._cop_above_breakeven()
        assert result["COP"] > 1.0
        assert result["break_even"] is True
        assert result["COP_margin"] > 0.0

    def test_cop_below_breakeven_scenario(self):
        result = self._cop_below_breakeven()
        assert result["COP"] < 1.0
        assert result["break_even"] is False
        assert result["COP_margin"] < 0.0

    def test_cop_scales_with_fusion_rate(self):
        r1 = calculate_cop(1e12, 1.0)
        r2 = calculate_cop(2e12, 1.0)
        assert r2["COP"] == pytest.approx(2.0 * r1["COP"], rel=1e-8)

    def test_cop_inversely_scales_with_work(self):
        r1 = calculate_cop(1e12, 1.0)
        r2 = calculate_cop(1e12, 2.0)
        assert r2["COP"] == pytest.approx(r1["COP"] / 2.0, rel=1e-8)

    def test_volume_cancels_in_cop(self):
        r1 = calculate_cop(1e12, 1.0, volume_cc=1.0)
        r2 = calculate_cop(1e12, 1.0, volume_cc=10.0)
        assert r2["COP"] == pytest.approx(r1["COP"], rel=1e-10)

    def test_volume_affects_absolute_power(self):
        r1 = calculate_cop(1e12, 1.0, volume_cc=1.0)
        r2 = calculate_cop(1e12, 1.0, volume_cc=5.0)
        assert r2["Q_lattice_W_total"] == pytest.approx(
            5.0 * r1["Q_lattice_W_total"], rel=1e-10
        )

    def test_phonon_fraction_close_to_unity(self):
        result = calculate_cop(1e12, 1.0)
        assert result["phonon_fraction"] > 0.999

    def test_t_channel_higher_q(self):
        r_he3 = calculate_cop(1e12, 1.0, Q_MeV=DD_Q_HE3_MEV)
        r_t = calculate_cop(1e12, 1.0, Q_MeV=DD_Q_T_MEV)
        assert r_t["COP"] > r_he3["COP"]

    def test_invalid_work_input_zero(self):
        with pytest.raises(ValueError):
            calculate_cop(1e12, 0.0)

    def test_invalid_work_input_negative(self):
        with pytest.raises(ValueError):
            calculate_cop(1e12, -1.0)

    def test_invalid_volume(self):
        with pytest.raises(ValueError):
            calculate_cop(1e12, 1.0, volume_cc=0.0)
        with pytest.raises(ValueError):
            calculate_cop(1e12, 1.0, volume_cc=-1.0)

    def test_cop_margin_formula(self):
        result = calculate_cop(1e12, 1.0)
        assert result["COP_margin"] == pytest.approx(
            result["COP"] - 1.0, rel=1e-10
        )

    def test_zero_fusion_gives_zero_cop(self):
        result = calculate_cop(0.0, 1.0)
        assert result["COP"] == pytest.approx(0.0, abs=1e-40)
        assert result["break_even"] is False

    def test_all_floats_finite(self):
        result = calculate_cop(1e12, 1.0)
        for key, val in result.items():
            if isinstance(val, float):
                assert np.isfinite(val), f"Non-finite for key {key!r}: {val}"

    def test_prompt_gamma_ratio_matches_standalone(self):
        g = radion_phonon_coupling()
        result = calculate_cop(1e12, 1.0, radion_coupling=g)
        expected_pg = prompt_gamma_ratio(g)
        assert result["prompt_gamma_ratio"] == pytest.approx(expected_pg, rel=1e-10)

    def test_cop_consistency_with_heat_power(self):
        rate = 1e13
        W_in = 0.5
        result = calculate_cop(rate, W_in, volume_cc=2.0)
        expected_q = lattice_heat_power(rate) * 2.0
        assert result["Q_lattice_W_total"] == pytest.approx(expected_q, rel=1e-8)


# ===========================================================================
# sensitivity_sweep
# ===========================================================================


class TestSensitivitySweep:
    """Gemini's requested sweep: g from 10 to 40, gamma/tau breakeven."""

    def _default_sweep(self):
        return sensitivity_sweep()

    def test_returns_dict(self):
        assert isinstance(self._default_sweep(), dict)

    def test_required_keys(self):
        sw = self._default_sweep()
        required = {
            "g_arr", "P_gamma_arr", "tau_eff_fs_arr",
            "g_canon", "g_braid", "P_gamma_canon", "P_gamma_braid",
            "tau_eff_fs_canon", "tau_eff_fs_braid", "tau_Bmu_s",
            "g_tau_limit", "g_gamma_breakeven",
            "canon_tau_in_range", "braid_tau_in_range",
            "canon_gamma_safe", "braid_gamma_safe",
        }
        assert required <= set(sw.keys())

    def test_g_arr_shape(self):
        sw = sensitivity_sweep(g_min=10.0, g_max=40.0, n_points=61)
        assert len(sw["g_arr"]) == 61

    def test_g_arr_bounds(self):
        sw = sensitivity_sweep(g_min=10.0, g_max=40.0, n_points=31)
        assert sw["g_arr"][0] == pytest.approx(10.0, rel=1e-10)
        assert sw["g_arr"][-1] == pytest.approx(40.0, rel=1e-10)

    def test_P_gamma_decreasing(self):
        sw = self._default_sweep()
        # P_γ monotonically decreases as g increases
        assert np.all(np.diff(sw["P_gamma_arr"]) <= 0.0)

    def test_tau_eff_decreasing(self):
        sw = self._default_sweep()
        # τ_eff monotonically decreases as g increases
        assert np.all(np.diff(sw["tau_eff_fs_arr"]) <= 0.0)

    def test_all_P_gamma_positive(self):
        sw = self._default_sweep()
        assert np.all(sw["P_gamma_arr"] > 0.0)

    def test_all_tau_eff_positive(self):
        sw = self._default_sweep()
        assert np.all(sw["tau_eff_fs_arr"] > 0.0)

    def test_canon_gamma_safe(self):
        sw = self._default_sweep()
        assert sw["canon_gamma_safe"] is True

    def test_braid_gamma_safe(self):
        # g_braid ≈ 33.47 also gives P_γ << 1e-6
        sw = self._default_sweep()
        assert sw["braid_gamma_safe"] is True

    def test_canon_tau_in_range(self):
        # g_canon (n_w=5): τ_eff ≈ 0.51 fs ∈ [0.1, 100] fs
        sw = self._default_sweep()
        assert sw["canon_tau_in_range"] is True

    def test_braid_tau_not_in_range_at_canonical_tau_bmu(self):
        # g_braid (n_w=12): τ_eff ≈ 0.089 fs < 0.1 fs at canonical τ_Bmu
        sw = self._default_sweep()
        assert sw["braid_tau_in_range"] is False

    def test_g_tau_limit_formula(self):
        # g_max for τ_eff ≥ 0.1 fs: g ≤ sqrt(τ_Bmu/0.1fs - 1)
        tau_Bmu = bmu_relaxation_time()
        expected = np.sqrt(max(0.0, tau_Bmu / (0.1e-15) - 1.0))
        sw = sensitivity_sweep(tau_Bmu=tau_Bmu)
        assert sw["g_tau_limit"] == pytest.approx(expected, rel=1e-6)

    def test_g_tau_limit_is_31_approx(self):
        # With canonical τ_Bmu = 1e-13 s: g_limit ≈ sqrt(1000-1) ≈ 31.6
        sw = self._default_sweep()
        assert 30.0 < sw["g_tau_limit"] < 33.0

    def test_g_gamma_breakeven_zero_for_small_standard(self):
        # DD_GAMMA_STANDARD = 3e-7 < 1e-6 → breakeven g = 0
        sw = self._default_sweep()
        assert sw["g_gamma_breakeven"] == pytest.approx(0.0, abs=1e-10)

    def test_g_gamma_breakeven_positive_for_large_standard(self):
        sw = sensitivity_sweep(gamma_standard=5e-6)
        assert sw["g_gamma_breakeven"] > 0.0
        assert sw["g_gamma_breakeven"] < 5.0

    def test_canon_braid_values_stored(self):
        sw = self._default_sweep()
        assert sw["g_canon"] == pytest.approx(RADION_COUPLING_CANON, rel=1e-10)
        assert sw["g_braid"] == pytest.approx(RADION_COUPLING_BRAID, rel=1e-10)

    def test_P_gamma_at_canon_matches_standalone(self):
        sw = self._default_sweep()
        expected = prompt_gamma_ratio(RADION_COUPLING_CANON)
        assert sw["P_gamma_canon"] == pytest.approx(expected, rel=1e-10)

    def test_tau_eff_at_canon_matches_standalone(self):
        tau_Bmu = bmu_relaxation_time()
        sw = sensitivity_sweep(tau_Bmu=tau_Bmu)
        expected = thermalization_time_fs(tau_Bmu, RADION_COUPLING_CANON)
        assert sw["tau_eff_fs_canon"] == pytest.approx(expected, rel=1e-10)

    def test_braid_P_gamma_smaller_than_canon(self):
        sw = self._default_sweep()
        assert sw["P_gamma_braid"] < sw["P_gamma_canon"]

    def test_braid_tau_smaller_than_canon(self):
        sw = self._default_sweep()
        assert sw["tau_eff_fs_braid"] < sw["tau_eff_fs_canon"]

    def test_invalid_g_range(self):
        with pytest.raises(ValueError):
            sensitivity_sweep(g_min=40.0, g_max=10.0)

    def test_invalid_n_points(self):
        with pytest.raises(ValueError):
            sensitivity_sweep(n_points=1)

    def test_custom_tau_bmu(self):
        tau = 5e-13  # longer τ_Bmu → larger g_tau_limit
        sw1 = sensitivity_sweep(tau_Bmu=bmu_relaxation_time())
        sw2 = sensitivity_sweep(tau_Bmu=tau)
        assert sw2["g_tau_limit"] > sw1["g_tau_limit"]


# ===========================================================================
# gamma_breakeven_coupling
# ===========================================================================


class TestGammaBreakevenCoupling:

    def test_zero_for_standard_below_threshold(self):
        # DD_GAMMA_STANDARD = 3e-7 < 1e-6
        g = gamma_breakeven_coupling(1e-6, DD_GAMMA_STANDARD)
        assert g == pytest.approx(0.0, abs=1e-10)

    def test_positive_for_standard_above_threshold(self):
        g = gamma_breakeven_coupling(1e-6, 5e-6)
        assert g > 0.0

    def test_formula_above_threshold(self):
        gamma_std = 1e-4
        threshold = 1e-6
        expected = np.sqrt(max(0.0, np.sqrt(gamma_std / threshold) - 1.0))
        g = gamma_breakeven_coupling(threshold, gamma_std)
        assert g == pytest.approx(expected, rel=1e-10)

    def test_verification_at_breakeven(self):
        # At g = g_min, P_γ should be just below threshold
        gamma_std = 5e-6
        threshold = 1e-6
        g_min = gamma_breakeven_coupling(threshold, gamma_std)
        P = gamma_std / (1.0 + g_min ** 2) ** 2
        assert P <= threshold

    def test_decreases_with_higher_threshold(self):
        # Higher threshold → need less suppression → smaller g_min
        g1 = gamma_breakeven_coupling(1e-6, 5e-6)
        g2 = gamma_breakeven_coupling(1e-4, 5e-6)
        assert g2 < g1

    def test_increases_with_higher_standard(self):
        # Higher standard → need more suppression → larger g_min
        g1 = gamma_breakeven_coupling(1e-6, 5e-6)
        g2 = gamma_breakeven_coupling(1e-6, 1e-3)
        assert g2 > g1

    def test_invalid_threshold(self):
        with pytest.raises(ValueError):
            gamma_breakeven_coupling(0.0)
        with pytest.raises(ValueError):
            gamma_breakeven_coupling(-1e-6)

    def test_invalid_gamma_standard(self):
        with pytest.raises(ValueError):
            gamma_breakeven_coupling(1e-6, -1e-7)

    def test_canon_coupling_above_breakeven_for_any_reasonable_standard(self):
        # Even at gamma_std = 1e-4, g_min < 10 << g_canon ≈ 13.95
        g_min = gamma_breakeven_coupling(1e-6, 1e-4)
        assert RADION_COUPLING_CANON > g_min


# ===========================================================================
# tau_breakeven_tau_bmu
# ===========================================================================


class TestTauBreakevenTauBmu:

    def test_positive(self):
        t = tau_breakeven_tau_bmu(0.1, RADION_COUPLING_CANON)
        assert t > 0.0

    def test_formula(self):
        g = RADION_COUPLING_CANON
        tau_min_fs = 0.5
        expected = tau_min_fs * FS_TO_S * (1.0 + g ** 2)
        assert tau_breakeven_tau_bmu(tau_min_fs, g) == pytest.approx(expected, rel=1e-10)

    def test_canonical_coupling_gives_small_tau_Bmu(self):
        # For g_canon, 0.1 fs requires only a small τ_Bmu
        t = tau_breakeven_tau_bmu(0.1, RADION_COUPLING_CANON)
        # 0.1e-15 * (1 + 194.6) ≈ 1.956e-14 s << canonical τ_Bmu = 1e-13 s
        assert t < bmu_relaxation_time()

    def test_braid_coupling_needs_longer_tau_Bmu(self):
        # For g_braid, 0.1 fs requires longer τ_Bmu than canonical
        t_canon = tau_breakeven_tau_bmu(0.1, RADION_COUPLING_CANON)
        t_braid = tau_breakeven_tau_bmu(0.1, RADION_COUPLING_BRAID)
        assert t_braid > t_canon

    def test_braid_needs_tau_bmu_just_above_canonical(self):
        # At g_braid, need τ_Bmu ≈ 1.12e-13 s, canonical is 1e-13 s (12% short)
        canonical_tau = bmu_relaxation_time()
        needed = tau_breakeven_tau_bmu(0.1, RADION_COUPLING_BRAID)
        ratio = needed / canonical_tau
        # Should be between 1.0 and 1.5 (marginal deficit)
        assert 1.0 < ratio < 1.5

    def test_scales_with_tau_min(self):
        g = RADION_COUPLING_CANON
        t1 = tau_breakeven_tau_bmu(0.1, g)
        t2 = tau_breakeven_tau_bmu(0.2, g)
        assert t2 == pytest.approx(2.0 * t1, rel=1e-10)

    def test_defaults_to_canonical_coupling(self):
        t_explicit = tau_breakeven_tau_bmu(0.1, RADION_COUPLING_CANON)
        t_default = tau_breakeven_tau_bmu(0.1)
        assert t_default == pytest.approx(t_explicit, rel=1e-10)

    def test_invalid_tau_min(self):
        with pytest.raises(ValueError):
            tau_breakeven_tau_bmu(0.0)
        with pytest.raises(ValueError):
            tau_breakeven_tau_bmu(-1.0)


# ===========================================================================
# braid_coupling_comparison
# ===========================================================================


class TestBraidCouplingComparison:

    def test_returns_dict(self):
        cmp = braid_coupling_comparison()
        assert isinstance(cmp, dict)

    def test_required_keys(self):
        cmp = braid_coupling_comparison()
        required = {
            "g_canon", "g_braid", "n_w_canon", "n_w_braid",
            "g_squared_canon", "g_squared_braid",
            "enhancement_canon", "enhancement_braid",
            "P_gamma_canon", "P_gamma_braid",
            "tau_eff_fs_canon", "tau_eff_fs_braid",
            "tau_Bmu_s", "canon_gamma_safe", "braid_gamma_safe",
            "canon_tau_in_range", "braid_tau_in_range",
            "tau_Bmu_min_for_braid_fs", "braid_needs_weaker_field",
            "open_question",
        }
        assert required <= set(cmp.keys())

    def test_n_w_values(self):
        cmp = braid_coupling_comparison()
        assert cmp["n_w_canon"] == 5
        assert cmp["n_w_braid"] == 12

    def test_g_values_match_constants(self):
        cmp = braid_coupling_comparison()
        assert cmp["g_canon"] == pytest.approx(RADION_COUPLING_CANON, rel=1e-10)
        assert cmp["g_braid"] == pytest.approx(RADION_COUPLING_BRAID, rel=1e-10)

    def test_braid_larger_than_canon(self):
        cmp = braid_coupling_comparison()
        assert cmp["g_braid"] > cmp["g_canon"]
        assert cmp["g_squared_braid"] > cmp["g_squared_canon"]
        assert cmp["enhancement_braid"] > cmp["enhancement_canon"]

    def test_both_gamma_safe(self):
        cmp = braid_coupling_comparison()
        assert cmp["canon_gamma_safe"] is True
        assert cmp["braid_gamma_safe"] is True

    def test_braid_P_gamma_smaller(self):
        cmp = braid_coupling_comparison()
        assert cmp["P_gamma_braid"] < cmp["P_gamma_canon"]

    def test_canon_tau_in_range(self):
        cmp = braid_coupling_comparison()
        assert cmp["canon_tau_in_range"] is True

    def test_braid_tau_not_in_range_at_canonical_tau_bmu(self):
        # Key finding: g_braid pushes τ_eff below 0.1 fs at canonical B_μ
        cmp = braid_coupling_comparison()
        assert cmp["braid_tau_in_range"] is False
        assert cmp["braid_needs_weaker_field"] is True

    def test_braid_tau_eff_is_attosecond(self):
        # 0.089 fs: sub-femtosecond, attosecond regime
        cmp = braid_coupling_comparison()
        assert 0.0 < cmp["tau_eff_fs_braid"] < 0.1

    def test_tau_bmu_min_for_braid_fs(self):
        cmp = braid_coupling_comparison()
        # Minimum τ_Bmu for g_braid to give τ_eff ≥ 0.1 fs
        expected = tau_breakeven_tau_bmu(0.1, RADION_COUPLING_BRAID)
        assert cmp["tau_Bmu_min_for_braid_fs"] == pytest.approx(expected, rel=1e-10)

    def test_braid_tau_bmu_min_slightly_above_canonical(self):
        # 1.12e-13 > 1e-13: canonical B_μ is marginally too strong for g_braid
        canonical = bmu_relaxation_time()
        cmp = braid_coupling_comparison()
        assert cmp["tau_Bmu_min_for_braid_fs"] > canonical

    def test_open_question_is_string(self):
        cmp = braid_coupling_comparison()
        assert isinstance(cmp["open_question"], str)
        assert len(cmp["open_question"]) > 20

    def test_g_squared_formula(self):
        cmp = braid_coupling_comparison()
        assert cmp["g_squared_canon"] == pytest.approx(RADION_COUPLING_CANON**2, rel=1e-10)
        assert cmp["g_squared_braid"] == pytest.approx(RADION_COUPLING_BRAID**2, rel=1e-10)

    def test_enhancement_formula(self):
        cmp = braid_coupling_comparison()
        assert cmp["enhancement_canon"] == pytest.approx(1.0 + RADION_COUPLING_CANON**2, rel=1e-10)
        assert cmp["enhancement_braid"] == pytest.approx(1.0 + RADION_COUPLING_BRAID**2, rel=1e-10)

    def test_with_weaker_bmu_braid_enters_fs_range(self):
        # If we pass a longer τ_Bmu (weaker B_μ), braid coupling returns to fs range
        tau_needed = tau_breakeven_tau_bmu(0.2, RADION_COUPLING_BRAID)
        cmp = braid_coupling_comparison(tau_Bmu=tau_needed * 1.01)  # 1% margin
        assert cmp["braid_tau_in_range"] is True

    def test_braid_enhancement_approx_1122(self):
        cmp = braid_coupling_comparison()
        # (1 + 33.47²) ≈ 1121.9
        assert 1100.0 < cmp["enhancement_braid"] < 1150.0

    def test_canon_enhancement_approx_196(self):
        cmp = braid_coupling_comparison()
        # (1 + 13.95²) ≈ 195.6
        assert 190.0 < cmp["enhancement_canon"] < 200.0
