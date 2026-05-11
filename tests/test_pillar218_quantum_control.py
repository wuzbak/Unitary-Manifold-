# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar218_quantum_control.py — Pillar 218 test suite."""
import math
import pytest
from src.core.pillar218_quantum_control import (
    N_W,
    K_CS,
    BRAIDED_SOUND_SPEED,
    PHI0,
    SURFACE_CODE_THRESHOLD,
    K_B_SI,
    HBAR_SI,
    decoherence_rate_from_kk,
    braid_error_threshold,
    kk_gate_fidelity,
    control_hamiltonian_from_kk,
    topological_code_distance,
    quantum_capacity_bound,
    pillar218_summary,
)


# ---------------------------------------------------------------------------
# TestConstants
# ---------------------------------------------------------------------------
class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_k_cs_is_sum_of_squares(self):
        assert K_CS == 5**2 + 7**2

    def test_braided_sound_speed(self):
        assert abs(BRAIDED_SOUND_SPEED - 12 / 37) < 1e-15

    def test_phi0_approx(self):
        assert abs(PHI0 - 0.7390851) < 1e-6

    def test_phi0_is_dottie(self):
        # φ₀ satisfies cos(φ₀) = φ₀ to within 1e-6
        assert abs(math.cos(PHI0) - PHI0) < 1e-6

    def test_surface_code_threshold(self):
        assert abs(SURFACE_CODE_THRESHOLD - 0.01) < 1e-12

    def test_k_b_si(self):
        assert abs(K_B_SI - 1.380649e-23) < 1e-30

    def test_hbar_si(self):
        assert abs(HBAR_SI - 1.054571817e-34) < 1e-42


# ---------------------------------------------------------------------------
# TestDecoherence
# ---------------------------------------------------------------------------
class TestDecoherence:
    def test_returns_dict(self):
        r = decoherence_rate_from_kk(1.0, 1e-32)
        assert isinstance(r, dict)

    def test_has_required_keys(self):
        r = decoherence_rate_from_kk(1.0, 1e-32)
        for key in ("gamma_bare_hz", "suppression_factor", "gamma_suppressed_hz",
                    "coupling_alpha", "notes"):
            assert key in r

    def test_coupling_alpha(self):
        r = decoherence_rate_from_kk(300.0, 1e-32)
        assert abs(r["coupling_alpha"] - 1.0 / 74) < 1e-15

    def test_bare_rate_positive(self):
        r = decoherence_rate_from_kk(300.0, 1e-32)
        assert r["gamma_bare_hz"] > 0

    def test_suppression_in_unit_interval(self):
        r = decoherence_rate_from_kk(300.0, 1e-32)
        assert 0.0 <= r["suppression_factor"] <= 1.0

    def test_suppressed_le_bare(self):
        r = decoherence_rate_from_kk(300.0, 1e-32)
        assert r["gamma_suppressed_hz"] <= r["gamma_bare_hz"]

    def test_higher_temp_higher_bare_rate(self):
        r1 = decoherence_rate_from_kk(100.0, 1e-32)
        r2 = decoherence_rate_from_kk(300.0, 1e-32)
        assert r2["gamma_bare_hz"] > r1["gamma_bare_hz"]

    def test_larger_R_smaller_suppression(self):
        # Larger R → smaller m_KK → less suppression
        r1 = decoherence_rate_from_kk(300.0, 1e-10)
        r2 = decoherence_rate_from_kk(300.0, 1e-32)
        assert r1["suppression_factor"] >= r2["suppression_factor"]

    def test_notes_is_string(self):
        r = decoherence_rate_from_kk(300.0, 1e-32)
        assert isinstance(r["notes"], str)

    def test_raises_on_zero_temperature(self):
        with pytest.raises(ValueError):
            decoherence_rate_from_kk(0.0, 1e-32)

    def test_raises_on_negative_temperature(self):
        with pytest.raises(ValueError):
            decoherence_rate_from_kk(-1.0, 1e-32)

    def test_raises_on_zero_R(self):
        with pytest.raises(ValueError):
            decoherence_rate_from_kk(300.0, 0.0)

    @pytest.mark.parametrize("T", [0.01, 1.0, 77.0, 300.0, 1e4])
    def test_parametrized_temperatures(self, T):
        r = decoherence_rate_from_kk(T, 1e-32)
        assert r["gamma_bare_hz"] > 0
        assert 0.0 <= r["suppression_factor"] <= 1.0


# ---------------------------------------------------------------------------
# TestBraidThreshold
# ---------------------------------------------------------------------------
class TestBraidThreshold:
    def test_returns_dict(self):
        assert isinstance(braid_error_threshold(), dict)

    def test_has_required_keys(self):
        r = braid_error_threshold()
        for key in ("n_strands", "threshold_heuristic", "surface_code_threshold",
                    "ratio_vs_surface", "phi0_attractor", "notes"):
            assert key in r

    def test_threshold_positive(self):
        assert braid_error_threshold()["threshold_heuristic"] > 0

    def test_threshold_less_than_one(self):
        assert braid_error_threshold()["threshold_heuristic"] < 1.0

    def test_threshold_n5_value(self):
        r = braid_error_threshold(5)
        expected = 1.0 - math.cos(math.pi / 5)
        assert abs(r["threshold_heuristic"] - expected) < 1e-12

    def test_ratio_greater_than_one_for_n5(self):
        # B_5 heuristic threshold should exceed surface-code 1 %
        assert braid_error_threshold(5)["ratio_vs_surface"] > 1.0

    def test_phi0_attractor_consistent(self):
        assert abs(braid_error_threshold()["phi0_attractor"] - PHI0) < 1e-10

    def test_raises_on_n_strands_one(self):
        with pytest.raises(ValueError):
            braid_error_threshold(1)

    def test_n_strands_two(self):
        r = braid_error_threshold(2)
        expected = 1.0 - math.cos(math.pi / 2)
        assert abs(r["threshold_heuristic"] - expected) < 1e-12


# ---------------------------------------------------------------------------
# TestGateFidelity
# ---------------------------------------------------------------------------
class TestGateFidelity:
    def test_returns_dict(self):
        assert isinstance(kk_gate_fidelity(0.0), dict)

    def test_has_required_keys(self):
        r = kk_gate_fidelity(0.5)
        for key in ("fidelity", "infidelity", "epsilon_noise", "K_cs", "notes"):
            assert key in r

    def test_zero_noise_gives_unit_fidelity(self):
        r = kk_gate_fidelity(0.0)
        assert abs(r["fidelity"] - 1.0) < 1e-15

    def test_zero_noise_zero_infidelity(self):
        r = kk_gate_fidelity(0.0)
        assert r["infidelity"] == 0.0

    def test_fidelity_decreases_with_noise(self):
        f1 = kk_gate_fidelity(1.0)["fidelity"]
        f2 = kk_gate_fidelity(5.0)["fidelity"]
        assert f2 < f1

    def test_fidelity_at_eps_K_is_zero(self):
        # ε = K_CS → infidelity = 1 → fidelity = 0
        r = kk_gate_fidelity(float(K_CS))
        assert abs(r["fidelity"]) < 1e-12

    def test_infidelity_formula(self):
        eps = 3.7
        r = kk_gate_fidelity(eps, K_CS)
        assert abs(r["infidelity"] - (eps / K_CS) ** 2) < 1e-15

    def test_raises_on_negative_noise(self):
        with pytest.raises(ValueError):
            kk_gate_fidelity(-0.1)


# ---------------------------------------------------------------------------
# TestControlHamiltonian
# ---------------------------------------------------------------------------
class TestControlHamiltonian:
    def test_returns_dict(self):
        assert isinstance(control_hamiltonian_from_kk(1.0), dict)

    def test_has_required_keys(self):
        r = control_hamiltonian_from_kk(1.0)
        for key in ("H_x", "H_z", "omega_drive", "phi0", "H_norm",
                    "attractor_angle_deg", "notes"):
            assert key in r

    def test_H_x_equals_cos_phi0(self):
        r = control_hamiltonian_from_kk(1.0, PHI0)
        assert abs(r["H_x"] - math.cos(PHI0)) < 1e-12

    def test_H_z_equals_sin_phi0(self):
        r = control_hamiltonian_from_kk(1.0, PHI0)
        assert abs(r["H_z"] - math.sin(PHI0)) < 1e-12

    def test_H_norm_is_one(self):
        r = control_hamiltonian_from_kk(2.5, PHI0)
        assert abs(r["H_norm"] - 1.0) < 1e-12

    def test_omega_drive_stored(self):
        r = control_hamiltonian_from_kk(3.14)
        assert abs(r["omega_drive"] - 3.14) < 1e-12

    def test_raises_on_zero_omega(self):
        with pytest.raises(ValueError):
            control_hamiltonian_from_kk(0.0)

    def test_angle_deg_consistent(self):
        r = control_hamiltonian_from_kk(1.0, PHI0)
        assert abs(r["attractor_angle_deg"] - math.degrees(PHI0)) < 1e-10


# ---------------------------------------------------------------------------
# TestCodeDistance
# ---------------------------------------------------------------------------
class TestCodeDistance:
    def test_returns_dict(self):
        assert isinstance(topological_code_distance(), dict)

    def test_has_required_keys(self):
        r = topological_code_distance()
        for key in ("code_distance", "n_w", "K_cs", "corrects_errors",
                    "detects_errors", "notes"):
            assert key in r

    def test_default_distance_is_2(self):
        r = topological_code_distance(5, 74)
        assert r["code_distance"] == 2

    def test_distance_at_least_1(self):
        assert topological_code_distance()["code_distance"] >= 1

    def test_default_distance_ge_2(self):
        assert topological_code_distance()["code_distance"] >= 2

    def test_corrects_errors_nonneg(self):
        assert topological_code_distance()["corrects_errors"] >= 0

    def test_detects_errors_nonneg(self):
        assert topological_code_distance()["detects_errors"] >= 0

    def test_raises_on_zero_n_w(self):
        with pytest.raises(ValueError):
            topological_code_distance(0, 74)

    def test_larger_K_cs_larger_distance(self):
        d1 = topological_code_distance(5, 74)["code_distance"]
        d2 = topological_code_distance(5, 100)["code_distance"]
        assert d2 >= d1


# ---------------------------------------------------------------------------
# TestCapacityBound
# ---------------------------------------------------------------------------
class TestCapacityBound:
    def test_returns_dict(self):
        assert isinstance(quantum_capacity_bound(10, 0.01, 1e-32), dict)

    def test_has_required_keys(self):
        r = quantum_capacity_bound(10, 0.01, 1e-32)
        for key in ("n_qubits", "T_kelvin", "p_error_per_qubit",
                    "capacity_upper_bound", "gamma_suppressed_hz",
                    "t_gate_s", "notes"):
            assert key in r

    def test_capacity_le_n_qubits(self):
        r = quantum_capacity_bound(20, 0.01, 1e-32)
        assert r["capacity_upper_bound"] <= 20

    def test_capacity_nonneg(self):
        r = quantum_capacity_bound(10, 300.0, 1e-32)
        assert r["capacity_upper_bound"] >= 0.0

    def test_p_error_in_unit_interval(self):
        r = quantum_capacity_bound(10, 300.0, 1e-32)
        assert 0.0 <= r["p_error_per_qubit"] <= 1.0

    def test_raises_on_zero_qubits(self):
        with pytest.raises(ValueError):
            quantum_capacity_bound(0, 300.0)

    def test_raises_on_negative_temperature(self):
        with pytest.raises(ValueError):
            quantum_capacity_bound(10, -1.0)

    def test_notes_is_string(self):
        r = quantum_capacity_bound(5, 1.0, 1e-32)
        assert isinstance(r["notes"], str)


# ---------------------------------------------------------------------------
# TestSummary
# ---------------------------------------------------------------------------
class TestSummary:
    def setup_method(self):
        self.r = pillar218_summary()

    def test_returns_dict(self):
        assert isinstance(self.r, dict)

    def test_has_status_key(self):
        assert "status" in self.r

    def test_status_is_string(self):
        assert isinstance(self.r["status"], str)

    def test_pillar_number(self):
        assert self.r["pillar"] == 218

    def test_n_w(self):
        assert self.r["n_w"] == N_W

    def test_K_cs(self):
        assert self.r["K_cs"] == K_CS

    def test_phi0(self):
        assert abs(self.r["phi0"] - PHI0) < 1e-10

    def test_code_distance_default(self):
        assert self.r["code_distance_default"] == 2

    def test_braid_threshold_in_unit_interval(self):
        assert 0.0 < self.r["braid_threshold_n5"] < 1.0

    def test_ratio_vs_surface_positive(self):
        assert self.r["ratio_vs_surface"] > 0.0

    def test_gate_fidelity_at_eps1(self):
        expected = 1.0 - (1.0 / K_CS) ** 2
        assert abs(self.r["gate_fidelity_at_eps1"] - expected) < 1e-12

    def test_has_notes(self):
        assert "notes" in self.r
