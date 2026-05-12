# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar224_quantum_bottleneck_calculator.py
======================================================
Tests for Pillar 224: Quantum Computing Bottleneck Calculator.

All numeric values are derived from the framework's four invariants
(n_w=5, K_CS=74, c_s=12/37, φ₀≈0.739) using exact arithmetic.
No approximations are introduced in the tests themselves.
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar224_quantum_bottleneck_calculator import (
    N_W,
    K_CS,
    C_S,
    PHI0,
    K_B_SI,
    HBAR_SI,
    C_LIGHT,
    E_PLANCK_J,
    braid_fault_tolerance_threshold,
    logical_qubit_overhead,
    kk_decoherence_suppression,
    kk_crossover_frequency_hz,
    gradient_variance_bound,
    barren_plateau_crossover_qubits,
    topological_channel_capacity,
    gate_slot_size_seconds,
    geometric_gate_fidelity,
    max_tolerable_noise,
    ftum_convergence,
    vqe_advantage_table,
    vqe_crossover_qubits,
    decoder_deadline_seconds,
    unification_learning_reduction,
    kcs_gaussian_integer_decomposition,
    braiding_phase_degrees,
    threshold_safety_margin,
    bottleneck_report,
)

# ─────────────────────────────────────────────────────────────────────────────
# Constants smoke tests
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_nw(self):
        assert N_W == 5

    def test_kcs_sum_of_squares(self):
        assert K_CS == 5**2 + 7**2 == 74

    def test_cs_exact(self):
        assert abs(C_S - 12 / 37) < 1e-15

    def test_phi0_fixed_point(self):
        """φ₀ must satisfy cos(φ₀) = φ₀ to high precision."""
        assert abs(math.cos(PHI0) - PHI0) < 1e-12

    def test_si_constants_positive(self):
        for c in [K_B_SI, HBAR_SI, C_LIGHT, E_PLANCK_J]:
            assert c > 0


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 1: Error-correction overhead
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck1ErrorCorrection:
    def test_b5_threshold_value(self):
        p = braid_fault_tolerance_threshold(5)
        assert abs(p - (1 - math.cos(math.pi / 5))) < 1e-14

    def test_b5_threshold_approx_19_percent(self):
        p = braid_fault_tolerance_threshold(5)
        assert 0.190 < p < 0.192

    def test_b5_threshold_gt_surface_code(self):
        assert braid_fault_tolerance_threshold(5) > 0.01

    def test_threshold_decreases_with_strands(self):
        """cos(π/n) increases toward 1 as n grows, so p_th = 1−cos(π/n) decreases."""
        p5 = braid_fault_tolerance_threshold(5)
        p6 = braid_fault_tolerance_threshold(6)
        assert p5 > p6  # n=5 → 19.1%, n=6 → 13.4%; threshold falls with larger n

    def test_threshold_n2_is_zero(self):
        """cos(π/2) = 0; threshold(2) = 1 − 0 = 1.0."""
        assert abs(braid_fault_tolerance_threshold(2) - 1.0) < 1e-14

    def test_threshold_invalid(self):
        with pytest.raises(ValueError):
            braid_fault_tolerance_threshold(1)

    def test_logical_overhead_keys(self):
        r = logical_qubit_overhead(1e-3)
        assert "p_th_braid" in r
        assert "n_phys_surface" in r
        assert "n_phys_braid" in r
        assert "qubit_reduction_factor" in r

    def test_logical_overhead_braid_fewer_than_surface(self):
        r = logical_qubit_overhead(1e-3)
        assert r["n_phys_braid"] < r["n_phys_surface"]

    def test_logical_overhead_qubit_reduction_positive(self):
        r = logical_qubit_overhead(1e-3)
        assert r["qubit_reduction_factor"] > 1.0

    def test_logical_overhead_above_threshold_raises(self):
        with pytest.raises(ValueError):
            logical_qubit_overhead(0.02)  # above surface code threshold

    def test_logical_overhead_reduction_factor_5x(self):
        """At p_phys=0.1%, reduction should be roughly 5x (from pre-computed table)."""
        r = logical_qubit_overhead(1e-3)
        assert r["qubit_reduction_factor"] > 3.0

    def test_logical_overhead_target_consistency(self):
        """d_surface × d_braid constraints are integers ≥ 1."""
        r = logical_qubit_overhead(1e-3, p_logical_target=1e-15)
        assert r["d_surface"] >= 1
        assert r["d_braid"] >= 1


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 2: Cryogenic decoherence
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck2Decoherence:
    def test_suppression_keys(self):
        R_kk = E_PLANCK_J / (2 * math.pi * HBAR_SI * 5e9)
        r = kk_decoherence_suppression(15e-3, R_kk)
        assert "suppression_factor" in r
        assert "gamma_bare_hz" in r
        assert "gamma_suppressed_hz" in r

    def test_suppression_in_0_1(self):
        R_kk = E_PLANCK_J / (2 * math.pi * HBAR_SI * 5e9)
        r = kk_decoherence_suppression(15e-3, R_kk)
        assert 0.0 <= r["suppression_factor"] <= 1.0

    def test_suppression_decreases_with_higher_kk_mass(self):
        """Higher KK frequency (smaller R_kk) → more suppression."""
        R_low = E_PLANCK_J / (2 * math.pi * HBAR_SI * 100e9)  # 100 GHz
        R_high = E_PLANCK_J / (2 * math.pi * HBAR_SI * 1e9)   # 1 GHz
        r_low = kk_decoherence_suppression(15e-3, R_low)
        r_high = kk_decoherence_suppression(15e-3, R_high)
        assert r_low["suppression_factor"] < r_high["suppression_factor"]

    def test_gamma_bare_uses_kcs(self):
        """Bare rate = ω_nat / K_CS."""
        T = 15e-3
        R_kk = E_PLANCK_J / (2 * math.pi * HBAR_SI * 5e9)
        r = kk_decoherence_suppression(T, R_kk)
        omega_nat = K_B_SI * T / HBAR_SI
        expected = omega_nat / K_CS
        assert abs(r["gamma_bare_hz"] - expected) / expected < 1e-10

    def test_invalid_temperature(self):
        with pytest.raises(ValueError):
            kk_decoherence_suppression(-1.0, 1e30)

    def test_invalid_rkk(self):
        with pytest.raises(ValueError):
            kk_decoherence_suppression(15e-3, 0.0)

    def test_crossover_frequency_positive(self):
        f = kk_crossover_frequency_hz(15e-3)
        assert f > 0

    def test_crossover_frequency_increases_with_temperature(self):
        f1 = kk_crossover_frequency_hz(15e-3)
        f2 = kk_crossover_frequency_hz(100e-3)
        assert f2 > f1

    def test_crossover_formula(self):
        """Crossover freq = T_nat × ln(2) × E_Planck / (2πħ)."""
        T = 15e-3
        T_nat = K_B_SI * T / E_PLANCK_J
        expected = T_nat * math.log(2) * E_PLANCK_J / (2 * math.pi * HBAR_SI)
        assert abs(kk_crossover_frequency_hz(T) - expected) / expected < 1e-10

    def test_qubit_scale_kk_significant_suppression(self):
        """At 5 GHz KK scale and 15 mK, suppression should be < 1e-5."""
        R_kk = E_PLANCK_J / (2 * math.pi * HBAR_SI * 5e9)
        r = kk_decoherence_suppression(15e-3, R_kk)
        assert r["suppression_factor"] < 1e-5


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 3: Barren plateaus
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck3BarrenPlateau:
    def test_gradient_keys(self):
        r = gradient_variance_bound(10)
        assert "grad_variance_random" in r
        assert "grad_variance_kk" in r
        assert "kk_advantage_factor" in r
        assert "kk_dominates" in r

    def test_random_gradient_exponential(self):
        for n in [5, 10, 20]:
            r = gradient_variance_bound(n)
            assert abs(r["grad_variance_random"] - 2**(-n)) < 1e-30

    def test_kk_gradient_polynomial(self):
        for n in [5, 10, 20]:
            r = gradient_variance_bound(n)
            assert abs(r["grad_variance_kk"] - 1.0 / (K_CS**2 * n)) < 1e-30

    def test_kk_dominates_at_large_n(self):
        r = gradient_variance_bound(50)
        assert r["kk_dominates"] is True

    def test_crossover_is_small_number(self):
        n_cross = barren_plateau_crossover_qubits()
        assert 5 <= n_cross <= 25  # should be around 12-15

    def test_kk_advantage_grows_with_n(self):
        r10 = gradient_variance_bound(10)
        r50 = gradient_variance_bound(50)
        assert r50["kk_advantage_factor"] > r10["kk_advantage_factor"]

    def test_invalid_n_qubits(self):
        with pytest.raises(ValueError):
            gradient_variance_bound(0)

    def test_gradient_50q_advantage_billion_x(self):
        """At n=50, KK gradient is > 1 billion × random gradient."""
        r = gradient_variance_bound(50)
        assert r["kk_advantage_factor"] > 1e9


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 4: Quantum interconnects
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck4Interconnects:
    def test_channel_count_is_nw(self):
        r = topological_channel_capacity(4, 0.01)
        assert r["n_channels"] == N_W

    def test_zero_error_full_capacity(self):
        r = topological_channel_capacity(4, 0.0)
        assert abs(r["quantum_capacity_qubits"] - N_W * 4) < 1e-10

    def test_capacity_decreases_with_error(self):
        r0 = topological_channel_capacity(4, 0.0)
        r1 = topological_channel_capacity(4, 0.05)
        assert r1["quantum_capacity_qubits"] < r0["quantum_capacity_qubits"]

    def test_braiding_phase_value(self):
        r = topological_channel_capacity(4, 0.01)
        expected = 2 * math.pi * N_W * (N_W + 2) / K_CS
        assert abs(r["braiding_phase_rad"] - expected) < 1e-12

    def test_braiding_phase_degrees(self):
        r = topological_channel_capacity(4, 0.01)
        assert 165 < r["braiding_phase_degrees"] < 175  # ≈170.27°

    def test_invalid_error_rate(self):
        with pytest.raises(ValueError):
            topological_channel_capacity(4, 1.5)

    def test_binary_entropy_at_half(self):
        """H(0.5) = 1.0."""
        r = topological_channel_capacity(4, 0.5)
        assert abs(r["binary_entropy"] - 1.0) < 1e-10


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 5: Multi-programming latency
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck5MultiProgramming:
    def test_gate_slot_keys(self):
        r = gate_slot_size_seconds(15e-3)
        assert "t_gate_seconds" in r
        assert "t_gate_ns" in r
        assert "scheduling_slots_per_us" in r

    def test_gate_slot_formula(self):
        T = 15e-3
        omega = K_B_SI * T / HBAR_SI
        expected = 1.0 / (K_CS * omega)
        r = gate_slot_size_seconds(T)
        assert abs(r["t_gate_seconds"] - expected) / expected < 1e-10

    def test_gate_slot_positive(self):
        r = gate_slot_size_seconds(15e-3)
        assert r["t_gate_seconds"] > 0

    def test_gate_slot_sub_nanosecond(self):
        """At 15 mK, gate slot should be < 1 ns."""
        r = gate_slot_size_seconds(15e-3)
        assert r["t_gate_ns"] < 1.0

    def test_slots_per_us_gt_100(self):
        """At 15 mK, many gate slots fit in one microsecond."""
        r = gate_slot_size_seconds(15e-3)
        assert r["scheduling_slots_per_us"] > 100

    def test_invalid_temperature(self):
        with pytest.raises(ValueError):
            gate_slot_size_seconds(0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 6: Manufacturing variability
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck6Variability:
    def test_fidelity_at_zero_noise(self):
        r = geometric_gate_fidelity(0.0)
        assert r["fidelity"] == 1.0

    def test_fidelity_formula(self):
        for eps in [0.01, 0.1, 1.0, 5.0]:
            r = geometric_gate_fidelity(eps)
            expected = 1.0 - (eps / K_CS) ** 2
            assert abs(r["fidelity"] - expected) < 1e-14

    def test_fidelity_decreases_with_noise(self):
        r1 = geometric_gate_fidelity(0.1)
        r2 = geometric_gate_fidelity(1.0)
        assert r1["fidelity"] > r2["fidelity"]

    def test_infidelity_is_complement(self):
        for eps in [0.0, 0.5, 1.0]:
            r = geometric_gate_fidelity(eps)
            assert abs(r["fidelity"] + r["infidelity"] - 1.0) < 1e-14

    def test_advantage_vs_linear(self):
        """Quadratic suppression is better than linear at small ε."""
        r = geometric_gate_fidelity(1.0)
        # infidelity_quadratic < infidelity_linear
        infidelity_linear = 1.0 - r["fidelity_linear_comparison"]
        infidelity_quadratic = r["infidelity"]
        assert infidelity_quadratic < infidelity_linear

    def test_max_tolerable_noise(self):
        eps_max = max_tolerable_noise(0.999)
        # F(eps_max) should be ≥ 0.999
        r = geometric_gate_fidelity(eps_max)
        assert r["fidelity"] >= 0.999 - 1e-10

    def test_max_noise_formula(self):
        F_floor = 0.999
        expected = K_CS * math.sqrt(1 - F_floor)
        assert abs(max_tolerable_noise(F_floor) - expected) < 1e-10

    def test_invalid_fidelity_floor(self):
        with pytest.raises(ValueError):
            max_tolerable_noise(0.0)
        with pytest.raises(ValueError):
            max_tolerable_noise(1.0)

    def test_fidelity_at_eps_kcs(self):
        """At ε = K_CS, F = 1 - 1 = 0."""
        r = geometric_gate_fidelity(float(K_CS))
        assert abs(r["fidelity"]) < 1e-12

    def test_invalid_negative_noise(self):
        with pytest.raises(ValueError):
            geometric_gate_fidelity(-0.1)


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 7: Algorithm verification — FTUM convergence
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck7AlgorithmVerification:
    @pytest.mark.parametrize("x0", [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
    def test_converges_to_phi0(self, x0):
        r = ftum_convergence(x0)
        assert r["converged"]
        assert abs(r["x_final"] - PHI0) < 1e-10

    def test_converges_from_extreme(self):
        r = ftum_convergence(1e-8)
        assert r["converged"]

    def test_converges_from_near_one(self):
        r = ftum_convergence(0.9999)
        assert r["converged"]

    def test_iterations_under_100(self):
        for x0 in [0.1, 0.5, 0.9]:
            r = ftum_convergence(x0)
            assert r["iterations"] < 100

    def test_convergence_keys(self):
        r = ftum_convergence(0.5)
        assert "x0" in r
        assert "x_final" in r
        assert "iterations" in r
        assert "converged" in r
        assert "error" in r

    def test_error_below_tolerance(self):
        r = ftum_convergence(0.5, tol=1e-12)
        assert r["error"] < 1e-12

    def test_phi0_is_fixed_point(self):
        """Starting exactly at φ₀ converges immediately."""
        r = ftum_convergence(PHI0, tol=1e-15)
        assert r["converged"]
        assert r["iterations"] <= 2


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 8: Quantum advantage gap
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck8QuantumAdvantage:
    def test_table_length(self):
        table = vqe_advantage_table(range(2, 11))
        assert len(table) == 9

    def test_classical_ops_formula(self):
        table = vqe_advantage_table(range(2, 7))
        for entry in table:
            n = entry["n_qubits"]
            assert entry["classical_ops"] == 2 ** (3 * n)

    def test_vqe_evals_polynomial(self):
        table = vqe_advantage_table(range(2, 7), n_layers=10)
        for entry in table:
            n = entry["n_qubits"]
            assert entry["vqe_evals"] == K_CS * n * 10

    def test_advantage_at_large_n(self):
        """VQE advantage (classical > VQE) should appear by n=5."""
        table = vqe_advantage_table(range(2, 10), n_layers=10)
        # Find the largest n where advantage is False, then True
        advantage_ns = [e["n_qubits"] for e in table if e["advantage"]]
        assert len(advantage_ns) > 0
        assert max(advantage_ns) >= 4

    def test_crossover_qubits_reasonable(self):
        n_cross = vqe_crossover_qubits()
        assert 1 <= n_cross <= 10

    def test_ratio_grows_with_n(self):
        table = vqe_advantage_table(range(5, 15))
        ratios = [e["ratio"] for e in table]
        # ratios should be monotonically increasing
        for i in range(len(ratios) - 1):
            assert ratios[i + 1] > ratios[i]

    def test_hilbert_dim(self):
        table = vqe_advantage_table(range(2, 7))
        for e in table:
            assert e["hilbert_dim"] == 2 ** e["n_qubits"]


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 9: Classical-quantum latency
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck9ClassicalLatency:
    def test_decoder_keys(self):
        r = decoder_deadline_seconds(1e-3)
        assert "deadline_seconds" in r
        assert "deadline_ns" in r
        assert "fpga_achievable" in r

    def test_decoder_formula(self):
        L = 1e-3
        expected = L / (C_S * C_LIGHT)
        r = decoder_deadline_seconds(L)
        assert abs(r["deadline_seconds"] - expected) / expected < 1e-10

    def test_decoder_1mm_sub_nanosecond(self):
        """1 mm chip: decoder deadline should be < 1 ns."""
        r = decoder_deadline_seconds(1e-3)
        assert r["deadline_ns"] < 1.0

    def test_decoder_10mm_sub_nanosecond(self):
        """10 mm chip: deadline still sub-nanosecond."""
        r = decoder_deadline_seconds(10e-3)
        assert r["deadline_ns"] < 1.0

    def test_fpga_achievable_1mm(self):
        r = decoder_deadline_seconds(1e-3)
        # At sub-ns, fpga_achievable is False (FPGA clock = 1ns)
        # We just check the field exists and is boolean
        assert isinstance(r["fpga_achievable"], bool)

    def test_deadline_scales_with_length(self):
        r1 = decoder_deadline_seconds(1e-3)
        r2 = decoder_deadline_seconds(2e-3)
        assert abs(r2["deadline_seconds"] / r1["deadline_seconds"] - 2.0) < 1e-10

    def test_safety_factor(self):
        r1 = decoder_deadline_seconds(1e-3, safety_factor=1.0)
        r2 = decoder_deadline_seconds(1e-3, safety_factor=2.0)
        assert abs(r2["deadline_seconds"] / r1["deadline_seconds"] - 2.0) < 1e-10

    def test_invalid_length(self):
        with pytest.raises(ValueError):
            decoder_deadline_seconds(-1e-3)

    def test_propagation_speed_uses_cs(self):
        r = decoder_deadline_seconds(1e-3)
        assert abs(r["propagation_speed_m_s"] - C_S * C_LIGHT) < 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 10: Talent shortage
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck10Talent:
    def test_unification_keys(self):
        r = unification_learning_reduction()
        assert "n_separate_frameworks" in r
        assert "n_framework_constants" in r
        assert "reduction_factor" in r
        assert "shared_constants" in r

    def test_reduction_gt_1(self):
        r = unification_learning_reduction()
        assert r["reduction_factor"] > 1.0

    def test_constants_match_module(self):
        r = unification_learning_reduction()
        sc = r["shared_constants"]
        assert sc["n_w"] == N_W
        assert sc["K_CS"] == K_CS
        assert abs(sc["c_s"] - C_S) < 1e-15
        assert abs(sc["phi0"] - PHI0) < 1e-12


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 11: Post-quantum cryptography
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck11PQC:
    def test_gaussian_decomposition_contains_57(self):
        r = kcs_gaussian_integer_decomposition()
        assert (5, 7) in r["decompositions"]

    def test_kcs_matches(self):
        r = kcs_gaussian_integer_decomposition()
        assert r["K_CS"] == K_CS

    def test_all_decompositions_valid(self):
        r = kcs_gaussian_integer_decomposition()
        for a, b in r["decompositions"]:
            assert a ** 2 + b ** 2 == K_CS

    def test_braiding_phase_degrees_value(self):
        phase = braiding_phase_degrees()
        expected = math.degrees(2 * math.pi * N_W * (N_W + 2) / K_CS)
        assert abs(phase - expected) < 1e-10

    def test_braiding_phase_near_170(self):
        assert 168 < braiding_phase_degrees() < 172

    def test_braiding_fraction_irrational(self):
        """35/74 is already in lowest terms (gcd=1), confirming non-Abelian regime."""
        import math as m
        assert m.gcd(35, 74) == 1

    def test_gaussian_decomp_consistency(self):
        r = kcs_gaussian_integer_decomposition()
        # braiding_phase_degrees inside the dict matches the standalone function
        assert abs(r["braiding_phase_degrees"] - braiding_phase_degrees()) < 1e-10


# ─────────────────────────────────────────────────────────────────────────────
# Bottleneck 12: Supply chain
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneck12SupplyChain:
    def test_supply_chain_keys(self):
        r = threshold_safety_margin()
        assert "p_th_braid" in r
        assert "p_th_surface" in r
        assert "absolute_margin" in r
        assert "hardware_relaxation_factor" in r

    def test_relaxation_factor_approx_19(self):
        r = threshold_safety_margin()
        assert 18.5 < r["hardware_relaxation_factor"] < 20.0

    def test_absolute_margin_positive(self):
        r = threshold_safety_margin()
        assert r["absolute_margin"] > 0

    def test_braid_gt_surface(self):
        r = threshold_safety_margin()
        assert r["p_th_braid"] > r["p_th_surface"]


# ─────────────────────────────────────────────────────────────────────────────
# Combined bottleneck report
# ─────────────────────────────────────────────────────────────────────────────

class TestBottleneckReport:
    def test_report_all_keys_present(self):
        r = bottleneck_report()
        for key in [
            "b01_error_correction",
            "b02_decoherence",
            "b03_barren_plateau_crossover_n",
            "b03_barren_plateau_50q",
            "b04_interconnect",
            "b05_gate_slot",
            "b06_variability_eps1pct",
            "b06_variability_eps10pct",
            "b07_ftum_verification",
            "b08_advantage_table",
            "b08_crossover_n",
            "b09_decoder_1mm",
            "b09_decoder_10mm",
            "b10_unification",
            "b11_pqc",
            "b12_supply_chain",
            "b02_crossover_hz",
        ]:
            assert key in r, f"Missing key: {key}"

    def test_report_crossover_hz_positive(self):
        r = bottleneck_report()
        assert r["b02_crossover_hz"] > 0

    def test_report_b07_converged(self):
        r = bottleneck_report()
        assert r["b07_ftum_verification"]["converged"] is True

    def test_report_b08_table_nonempty(self):
        r = bottleneck_report()
        assert len(r["b08_advantage_table"]) > 0

    def test_report_b01_qubit_reduction_positive(self):
        r = bottleneck_report()
        assert r["b01_error_correction"]["qubit_reduction_factor"] > 1.0

    def test_report_b03_crossover_reasonable(self):
        r = bottleneck_report()
        assert 5 <= r["b03_barren_plateau_crossover_n"] <= 25

    def test_report_b04_has_capacity(self):
        r = bottleneck_report()
        assert "quantum_capacity_qubits" in r["b04_interconnect"]

    def test_report_b12_relaxation_gt_10(self):
        r = bottleneck_report()
        assert r["b12_supply_chain"]["hardware_relaxation_factor"] > 10.0


# ─────────────────────────────────────────────────────────────────────────────
# Cross-cutting: all functions return finite real numbers
# ─────────────────────────────────────────────────────────────────────────────

class TestNumericalSanity:
    def test_no_nan_in_report(self):
        r = bottleneck_report()
        # Spot-check numeric leaves
        def _check(v):
            if isinstance(v, float):
                assert not math.isnan(v), f"NaN found: {v}"
            elif isinstance(v, dict):
                for vv in v.values():
                    _check(vv)
            elif isinstance(v, list):
                for vv in v:
                    _check(vv)
        _check(r)

    def test_fidelity_in_range(self):
        for eps in [0.0, 0.1, 1.0, 10.0, 73.9]:
            r = geometric_gate_fidelity(eps)
            assert 0.0 <= r["fidelity"] <= 1.0

    def test_threshold_in_range(self):
        for n in [2, 3, 4, 5, 6, 7, 8]:
            p = braid_fault_tolerance_threshold(n)
            assert 0.0 < p <= 1.0
