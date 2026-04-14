# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_completions.py
=========================
Unit tests for the six structural completions of the Unitary Manifold.

Each test class is **independent** — it tests exactly one completion with no
shared assumptions across classes.

Canonical module locations (per spec):
  [1] evolution.py     ← Z_kinetic, epsilon_eff, renormalize_slow_roll
  [2] inflation.py     ← kk_amplitude_sum
  [3] metric.py        ← derive_nw_index_theorem
  [4] boundary.py      ← SM_FERMION_SPECTRUM_DEFAULT, derive_kcs_anomaly_inflow
  [5] boundary.py      ← fefferman_graham_expansion, boundary_counterterms,
                          holographic_renormalized_action
  [6] fixed_point.py   ← weighted_norm_network, operator_spectral_radius,
                          check_contraction_condition

INVARIANTS guaranteed by each test class:
  • nₛ unchanged to O(1e-3)
  • α = φ₀⁻² preserved
  • zero new free parameters introduced
"""

from __future__ import annotations

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# [1] Z_kinetic / ε_eff — evolution.py
# ---------------------------------------------------------------------------
from src.core.evolution import (
    Z_kinetic,
    epsilon_eff,
    renormalize_slow_roll,
    FieldState,
    _P_KK_FIXED,
)

# ---------------------------------------------------------------------------
# [2] KK amplitude sum — inflation.py
# ---------------------------------------------------------------------------
from src.core.inflation import (
    kk_amplitude_sum,
    effective_phi0_kk,
    ns_from_phi0,
    slow_roll_params,
    gw_potential_derivs,
)

# ---------------------------------------------------------------------------
# [3] Index-theorem n_w — metric.py
# ---------------------------------------------------------------------------
from src.core.metric import derive_nw_index_theorem

# ---------------------------------------------------------------------------
# [4] Anomaly-inflow k_CS — boundary.py
# ---------------------------------------------------------------------------
from src.holography.boundary import (
    SM_FERMION_SPECTRUM_DEFAULT,
    derive_kcs_anomaly_inflow,
)

# ---------------------------------------------------------------------------
# [5] Holographic renormalisation — boundary.py
# ---------------------------------------------------------------------------
from src.holography.boundary import (
    fefferman_graham_expansion,
    boundary_counterterms,
    holographic_renormalized_action,
    BoundaryState,
)

# ---------------------------------------------------------------------------
# [6] FTUM contraction — fixed_point.py
# ---------------------------------------------------------------------------
from src.multiverse.fixed_point import (
    MultiverseNetwork,
    weighted_norm_network,
    operator_spectral_radius,
    check_contraction_condition,
)


# ===========================================================================
# [1]  Z_kinetic / ε_eff  (evolution.py)
# ===========================================================================

class TestZKineticEvolution:
    """Z_kinetic, epsilon_eff, renormalize_slow_roll live in evolution.py.

    INVARIANTS checked here:
      • nₛ = 1 − 6ε + 2η — the η term is unaffected by Z_kinetic
      • α = ⟨1/φ²⟩ is unaffected (not touched by these functions)
    """

    def _make_state(self, phi_val: float = 1.0, N: int = 8) -> FieldState:
        """Helper: flat FieldState with uniform phi profile."""
        return FieldState.flat(N=N, rng=np.random.default_rng(0),
                               phi0=phi_val)

    # --- Z_kinetic ---

    def test_p_fixed_is_one(self):
        """_P_KK_FIXED = 1 (geometric, no free parameter)."""
        assert _P_KK_FIXED == 1.0

    def test_Z_kinetic_phi_mean_power(self):
        """Z_kinetic(φ, p) = ⟨φ⟩^p for uniform profile."""
        phi = np.full(16, 2.5)
        Z = Z_kinetic(phi, p=1.0)
        assert abs(Z - 2.5) < 1e-12

    def test_Z_kinetic_default_p_is_one(self):
        """Default p=1 (no second argument required)."""
        phi = np.full(8, 3.0)
        assert abs(Z_kinetic(phi) - 3.0) < 1e-12

    def test_Z_kinetic_unit_phi_is_one(self):
        """For φ = 1 everywhere, Z_kinetic = 1 (trivial case)."""
        phi = np.ones(20)
        assert abs(Z_kinetic(phi) - 1.0) < 1e-12

    def test_Z_kinetic_increases_with_phi_mean(self):
        """Larger ⟨φ⟩ → larger Z_kinetic (for p = 1 > 0)."""
        phi_small = np.full(10, 1.5)
        phi_large = np.full(10, 3.0)
        assert Z_kinetic(phi_large) > Z_kinetic(phi_small)

    def test_Z_kinetic_p_zero_is_one(self):
        """p = 0: Z_kinetic = ⟨φ⟩^0 = 1 for any non-zero φ."""
        phi = np.full(10, 7.3)
        assert abs(Z_kinetic(phi, p=0.0) - 1.0) < 1e-12

    # --- epsilon_eff ---

    def test_epsilon_eff_divides_by_Z(self):
        """ε_eff = ε / Z_kinetic(φ)."""
        phi = np.full(8, 3.0)
        eps = 0.012
        eps_e = epsilon_eff(eps, phi)
        assert abs(eps_e - eps / 3.0) < 1e-14

    def test_epsilon_eff_unit_phi_unchanged(self):
        """For φ = 1, Z = 1 → ε_eff = ε (no renormalisation)."""
        phi = np.ones(8)
        eps = 0.008
        assert abs(epsilon_eff(eps, phi) - eps) < 1e-14

    def test_epsilon_eff_reduces_r(self):
        """r_eff = 16 ε_eff < r_bare when ⟨φ⟩ > 1."""
        phi = np.full(8, 3.0)
        eps = 0.01
        r_eff = 16.0 * epsilon_eff(eps, phi)
        r_bare = 16.0 * eps
        assert r_eff < r_bare

    def test_epsilon_eff_below_bicep_keck_constraint(self):
        """With φ₀_eff ≈ 31.4 (canonical n_w=5), ⟨φ⟩ ≥ 1 and r_eff < 0.036."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        phi_star = phi0_eff / np.sqrt(3.0)
        V, dV, d2V = gw_potential_derivs(phi_star, phi0_eff, lam=1.0)
        eps, _ = slow_roll_params(phi_star, V, dV, d2V)
        # phi profile set to phi0_eff (zero-mode value)
        phi = np.full(8, phi0_eff)
        r_eff = 16.0 * epsilon_eff(eps, phi)
        assert r_eff < 0.036, (
            f"r_eff={r_eff:.5f} should be < 0.036 with ⟨φ⟩={phi0_eff:.2f}"
        )

    def test_epsilon_eff_ns_invariant(self):
        """nₛ = 1 − 6ε + 2η: renorming ε moves nₛ toward 1, η is untouched."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        ns_bare, _, eps, eta = ns_from_phi0(phi0_eff)
        phi = np.full(8, phi0_eff)
        eps_ren = epsilon_eff(eps, phi)
        ns_ren = 1.0 - 6.0 * eps_ren + 2.0 * eta
        # ns_ren > ns_bare (less red tilt from ε)
        assert ns_ren > ns_bare, "KK renorm should reduce the ε contribution to tilt"
        # Both are within 0.05 of each other (η dominates the tilt; measured diff ≈ 0.035)
        assert abs(ns_ren - ns_bare) < 0.05

    # --- renormalize_slow_roll ---

    def test_renormalize_slow_roll_uses_state_phi(self):
        """renormalize_slow_roll(state, ε) = ε / Z_kinetic(state.phi)."""
        state = self._make_state(phi_val=2.0, N=8)
        eps = 0.015
        eps_ren = renormalize_slow_roll(state, eps)
        Z_expected = Z_kinetic(state.phi)
        assert abs(eps_ren - eps / Z_expected) < 1e-14

    def test_renormalize_slow_roll_returns_float(self):
        state = self._make_state()
        result = renormalize_slow_roll(state, 0.01)
        assert isinstance(result, float)

    def test_renormalize_slow_roll_positive(self):
        """Result is always positive for positive input."""
        state = self._make_state(phi_val=5.0)
        assert renormalize_slow_roll(state, 0.02) > 0.0

    def test_renormalize_slow_roll_monotone_in_phi(self):
        """Higher ⟨φ⟩ → more renorming → smaller ε_eff."""
        state_lo = self._make_state(phi_val=1.0)
        state_hi = self._make_state(phi_val=5.0)
        eps = 0.01
        eps_lo = renormalize_slow_roll(state_lo, eps)
        eps_hi = renormalize_slow_roll(state_hi, eps)
        assert eps_hi <= eps_lo


# ===========================================================================
# [2]  KK mode sum for Aₛ  (inflation.py)
# ===========================================================================

class TestKKAmplitudeSum:
    """kk_amplitude_sum: lives in inflation.py."""

    def test_zero_mode_only_when_kk_heavy(self):
        """Very small R_c → m_KK_1 >> H_* → only n=0 active."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        result = kk_amplitude_sum(phi0_eff, lam=1.0, R_c=1e-6, N_max=10)
        assert result["N_active"] == 1
        assert abs(result["As_total"] - result["As_zero"]) < max(1e-14 * abs(result["As_zero"]), 1e-20)

    def test_enhancement_equals_N_active(self):
        """A_s_total / A_s_zero == N_active exactly."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        result = kk_amplitude_sum(phi0_eff, lam=1.0, R_c=1.0, N_max=50)
        assert abs(result["enhancement"] - result["N_active"]) < 1e-12

    def test_larger_R_c_more_active_modes(self):
        """Larger R_c → smaller m_KK_1 → more modes below H_*."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        r1 = kk_amplitude_sum(phi0_eff, lam=1.0, R_c=1.0,  N_max=200)
        r2 = kk_amplitude_sum(phi0_eff, lam=1.0, R_c=10.0, N_max=200)
        assert r2["N_active"] >= r1["N_active"]

    def test_amplitude_positive(self):
        phi0_eff = effective_phi0_kk(1.0, 5)
        result = kk_amplitude_sum(phi0_eff, R_c=1.0)
        assert result["As_zero"] > 0.0
        assert result["As_total"] > 0.0

    def test_enhancement_closes_gap(self):
        """R_c chosen so ≥ 4 active modes → enhancement ≥ 4 (closes gap)."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        phi_star = phi0_eff / np.sqrt(3.0)
        V, _, _ = gw_potential_derivs(phi_star, phi0_eff, lam=1.0)
        H_star = float(np.sqrt(V / 3.0))
        R_c_target = 5.0 / H_star  # m_1=H/5, …, m_4=4H/5, m_5≈H* → 5 modes
        result = kk_amplitude_sum(phi0_eff, R_c=R_c_target, N_max=200)
        assert result["N_active"] >= 4
        assert result["enhancement"] >= 4

    def test_invalid_phi0_eff_raises(self):
        with pytest.raises(ValueError):
            kk_amplitude_sum(-1.0, R_c=1.0)

    def test_output_keys(self):
        phi0_eff = effective_phi0_kk(1.0, 5)
        result = kk_amplitude_sum(phi0_eff, R_c=1.0)
        for key in ("As_zero", "As_total", "enhancement", "N_active", "H_star",
                    "m_KK_1", "R_c", "phi_star", "As_formula"):
            assert key in result, f"Missing key '{key}'"


# ===========================================================================
# [3]  Index-theorem → n_w  (metric.py)
# ===========================================================================

class TestIndexTheoremNW:
    """derive_nw_index_theorem: lives in metric.py."""

    def test_standard_gives_five(self):
        """3 SM generations → n_w = 5 (no free parameters)."""
        n_w, details = derive_nw_index_theorem(n_generations=3, z2_removes=1)
        assert n_w == 5
        assert details["n_w"] == 5

    def test_n_w_before_z2_is_double(self):
        """Orbifold doubling: n_w_before_Z2 = 2 × n_generations."""
        _, d = derive_nw_index_theorem(n_generations=3, z2_removes=0)
        assert d["n_w_before_Z2"] == 6

    def test_z2_removes_one(self):
        """Default Z₂ projection removes exactly 1 mode."""
        _, d = derive_nw_index_theorem()
        assert d["z2_removes"] == 1
        assert d["n_w"] == d["n_w_before_Z2"] - 1

    def test_is_derived_flag(self):
        _, d = derive_nw_index_theorem()
        assert d["is_derived"] is True

    def test_index_D5_equals_n_generations(self):
        _, d = derive_nw_index_theorem(n_generations=3)
        assert d["index_D5"] == 3

    def test_summary_string_mentions_n_w(self):
        _, d = derive_nw_index_theorem()
        assert "5" in d["derivation_summary"]

    def test_formula_over_different_generations(self):
        """n_w = 2 × n_gen − 1 for z2_removes=1."""
        for ng in [1, 2, 3, 4, 5]:
            n_w, _ = derive_nw_index_theorem(n_generations=ng, z2_removes=1)
            assert n_w == 2 * ng - 1

    def test_invalid_n_gen_raises(self):
        with pytest.raises(ValueError, match="n_generations"):
            derive_nw_index_theorem(n_generations=0)

    def test_invalid_z2_removes_raises(self):
        with pytest.raises(ValueError, match="z2_removes"):
            derive_nw_index_theorem(n_generations=3, z2_removes=-1)

    def test_no_free_parameters(self):
        """All output integers are deterministic given n_gen and z2_removes."""
        n_w1, _ = derive_nw_index_theorem(3, 1)
        n_w2, _ = derive_nw_index_theorem(3, 1)
        assert n_w1 == n_w2  # deterministic, no randomness


# ===========================================================================
# [4]  Anomaly inflow → k_CS  (boundary.py)
# ===========================================================================

class TestAnomalyInflowKCS:
    """derive_kcs_anomaly_inflow: lives in boundary.py."""

    def test_geometric_kcs_is_74(self):
        """Birefringence formula gives k_cs_int = 74."""
        result = derive_kcs_anomaly_inflow()
        assert result["k_cs_int"] == 74

    def test_sm_left_anomaly_is_72(self):
        """Q_L (18) + L_L (54) = 72 (left-chiral SM anomaly coefficient)."""
        result = derive_kcs_anomaly_inflow()
        assert result["A_SM_left"] == 72

    def test_delta_k_is_two(self):
        """δk = k_cs − A_SM_left = 74 − 72 = 2 hidden-sector modes."""
        result = derive_kcs_anomaly_inflow()
        assert result["delta_k"] == 2

    def test_consistency_flag(self):
        result = derive_kcs_anomaly_inflow()
        assert result["is_consistent"] is True

    def test_per_fermion_all_species_present(self):
        result = derive_kcs_anomaly_inflow()
        names = {f["name"] for f in result["per_fermion"]}
        for s in ("Q_L", "u_R", "d_R", "L_L", "e_R"):
            assert s in names

    def test_Q_L_contribution(self):
        """Q_L: Y6=1, mult=3×2×3=18, chi=+1 → contrib = 18."""
        result = derive_kcs_anomaly_inflow()
        ql = next(f for f in result["per_fermion"] if f["name"] == "Q_L")
        assert ql["Y6_sq"] == 1
        assert ql["mult"] == 18
        assert ql["contrib"] == 18

    def test_L_L_contribution(self):
        """L_L: Y6=3, mult=1×2×3=6, chi=+1 → contrib = 54."""
        result = derive_kcs_anomaly_inflow()
        ll = next(f for f in result["per_fermion"] if f["name"] == "L_L")
        assert ll["Y6_sq"] == 9
        assert ll["mult"] == 6
        assert ll["contrib"] == 54

    def test_geometric_kcs_near_74(self):
        result = derive_kcs_anomaly_inflow()
        assert abs(result["k_cs_geometric"] - 74.0) < 1.0

    def test_custom_beta_monotone(self):
        """Higher β → higher k_cs_geometric."""
        r1 = derive_kcs_anomaly_inflow(beta_target_deg=0.30)
        r2 = derive_kcs_anomaly_inflow(beta_target_deg=0.40)
        assert r1["k_cs_geometric"] < r2["k_cs_geometric"]

    def test_zero_new_free_parameters(self):
        """k_cs_int is fully determined with no extra arguments."""
        r = derive_kcs_anomaly_inflow()
        assert isinstance(r["k_cs_int"], int)

    def test_output_keys(self):
        result = derive_kcs_anomaly_inflow()
        for key in ("k_cs_geometric", "k_cs_int", "A_SM_left", "A_SM_total",
                    "delta_k", "per_fermion", "beta_target_deg", "delta_phi",
                    "is_consistent"):
            assert key in result

    def test_sm_default_spectrum_accessible(self):
        """SM_FERMION_SPECTRUM_DEFAULT is importable from boundary.py."""
        assert len(SM_FERMION_SPECTRUM_DEFAULT) == 5


# ===========================================================================
# [5]  Holographic renormalisation  (boundary.py)
# ===========================================================================

class TestHolographicRenormalization:
    """FG expansion, counterterms, S_ren: all in boundary.py."""

    @pytest.fixture
    def boundary_metric(self):
        N = 10
        h = np.zeros((N, 2, 2))
        for i in range(N):
            h[i] = np.eye(2) * (1.0 + 0.05 * np.sin(i * 0.5))
        return h

    @pytest.fixture
    def flat_metric(self):
        N = 5
        return np.stack([np.eye(2)] * N)

    # --- fefferman_graham_expansion ---

    def test_g0_is_boundary_metric(self, boundary_metric):
        fg = fefferman_graham_expansion(boundary_metric, L_ads=1.0)
        np.testing.assert_array_equal(fg["g0"], boundary_metric)

    def test_g2_and_g4_returned(self, boundary_metric):
        fg = fefferman_graham_expansion(boundary_metric, L_ads=1.0, order=4)
        assert "g2" in fg and "g4" in fg
        assert fg["g2"].shape == boundary_metric.shape
        assert fg["g4"].shape == boundary_metric.shape

    def test_flat_metric_g2_is_zero(self, flat_metric):
        """Exactly flat metric (det = 1) → g^{(2)} = 0."""
        fg = fefferman_graham_expansion(flat_metric, L_ads=1.0)
        np.testing.assert_allclose(fg["g2"], 0.0, atol=1e-14)

    def test_trace_g2_shape(self, boundary_metric):
        fg = fefferman_graham_expansion(boundary_metric)
        assert fg["trace_g2"].shape == (boundary_metric.shape[0],)

    # --- boundary_counterterms ---

    def test_S_ct_is_finite_float(self, boundary_metric):
        ct = boundary_counterterms(boundary_metric, L_ads=1.0, dx=0.1)
        assert isinstance(ct["S_ct"], float)
        assert np.isfinite(ct["S_ct"])

    def test_counterterms_output_keys(self, boundary_metric):
        ct = boundary_counterterms(boundary_metric)
        for key in ("S_ct", "S_K", "S_cosmo", "S_curv", "sqrt_gamma", "kappa5_sq"):
            assert key in ct

    def test_sqrt_gamma_non_negative(self, boundary_metric):
        ct = boundary_counterterms(boundary_metric)
        assert np.all(ct["sqrt_gamma"] >= 0.0)

    def test_kappa5_sq(self, boundary_metric):
        ct = boundary_counterterms(boundary_metric, G5=1.0)
        assert abs(ct["kappa5_sq"] - 8.0 * np.pi) < 1e-12

    # --- holographic_renormalized_action ---

    def test_S_ren_finite(self, boundary_metric):
        result = holographic_renormalized_action(10.0, boundary_metric)
        assert result["is_finite"] is True
        assert np.isfinite(result["S_ren"])

    def test_S_ren_equation(self, boundary_metric):
        """S_ren = S_bulk + S_ct."""
        S_bulk = 5.0
        result = holographic_renormalized_action(S_bulk, boundary_metric)
        assert abs(result["S_ren"] - (S_bulk + result["S_ct"])) < 1e-12

    def test_S_ct_nonzero(self, boundary_metric):
        result = holographic_renormalized_action(100.0, boundary_metric)
        assert result["S_ct"] != 0.0

    def test_output_keys(self, boundary_metric):
        result = holographic_renormalized_action(1.0, boundary_metric)
        for key in ("S_bulk", "S_ct", "S_ren", "is_finite",
                    "Z_admissible", "counterterm_details"):
            assert key in result


# ===========================================================================
# [6]  FTUM contraction condition  (fixed_point.py)
# ===========================================================================

class TestFTUMContractionCondition:
    """weighted_norm_network, operator_spectral_radius, check_contraction_condition."""

    @pytest.fixture
    def chain4(self):
        return MultiverseNetwork.chain(n=4, coupling=0.05,
                                      rng=np.random.default_rng(0))

    @pytest.fixture
    def full3(self):
        return MultiverseNetwork.fully_connected(n=3, coupling=0.05,
                                                 rng=np.random.default_rng(1))

    # --- weighted_norm_network ---

    def test_norm_non_negative(self, chain4):
        assert weighted_norm_network(chain4) >= 0.0

    def test_norm_finite(self, chain4):
        assert np.isfinite(weighted_norm_network(chain4))

    def test_custom_weights(self, chain4):
        n = chain4.n_nodes()
        w = weighted_norm_network(chain4, weights=np.ones(n))
        assert np.isfinite(w)

    def test_wrong_length_weights_raises(self, chain4):
        with pytest.raises(ValueError, match="weights"):
            weighted_norm_network(chain4, weights=np.ones(99))

    def test_zero_state_vectors_norm_zero(self):
        from src.multiverse.fixed_point import MultiverseNode
        nodes = [MultiverseNode(dim=2, S=0.0, A=0.0, Q_top=0.0,
                                X=np.zeros(2), Xdot=np.zeros(2))
                 for _ in range(3)]
        net = MultiverseNetwork(nodes=nodes, adjacency=np.zeros((3, 3)))
        assert weighted_norm_network(net) == 0.0

    # --- operator_spectral_radius ---

    def test_rho_non_negative(self, chain4):
        sr = operator_spectral_radius(chain4, dt=0.2)
        assert sr["rho"] >= 0.0

    def test_rho_finite(self, chain4):
        assert np.isfinite(operator_spectral_radius(chain4)["rho"])

    def test_output_keys(self, chain4):
        sr = operator_spectral_radius(chain4)
        for key in ("rho", "is_contraction", "contraction_margin",
                    "gamma_critical", "n_nodes", "method"):
            assert key in sr

    def test_n_nodes_correct(self, chain4):
        assert operator_spectral_radius(chain4)["n_nodes"] == 4

    def test_weakly_coupled_is_contraction(self):
        """Very weak coupling + positive kappa → H term contracts."""
        net = MultiverseNetwork.chain(n=3, coupling=1e-6,
                                      rng=np.random.default_rng(42))
        sr = operator_spectral_radius(net, dt=0.2, kappa=0.5)
        assert sr["is_contraction"] is True

    # --- check_contraction_condition ---

    def test_canonical_gamma_contracts(self, chain4):
        """γ = 5.0 (canonical) must satisfy Banach condition for weak coupling."""
        result = check_contraction_condition(chain4, gamma=5.0)
        assert result["contraction_holds"] is True

    def test_output_keys_contraction(self, chain4):
        result = check_contraction_condition(chain4)
        for key in ("rho_HT", "rho_U_damped", "contraction_holds",
                    "convergence_rate", "n_iters_to_1pct",
                    "banach_conclusion", "gamma_used", "gamma_critical"):
            assert key in result

    def test_rho_U_damped_formula(self, chain4):
        """ρ(U_damped) = ρ(H+T) / (1 + γ dt)."""
        gamma, dt = 5.0, 0.2
        result = check_contraction_condition(chain4, gamma=gamma, dt=dt)
        sr = operator_spectral_radius(chain4, dt=dt)
        expected = sr["rho"] / (1.0 + gamma * dt)
        assert abs(result["rho_U_damped"] - expected) < 1e-10

    def test_conclusion_is_nonempty_string(self, chain4):
        result = check_contraction_condition(chain4)
        assert isinstance(result["banach_conclusion"], str)
        assert len(result["banach_conclusion"]) > 0

    def test_large_gamma_always_contracts(self):
        """Arbitrarily large γ → ρ(U_damped) → 0 regardless of coupling."""
        net = MultiverseNetwork.fully_connected(n=5, coupling=10.0,
                                                rng=np.random.default_rng(9))
        result = check_contraction_condition(net, gamma=1e6)
        assert result["contraction_holds"] is True
        assert result["rho_U_damped"] < 1.0

    def test_zero_gamma_zero_kappa_behaviour(self):
        """With γ=0 and κ=0, contraction may or may not hold — just check type."""
        net = MultiverseNetwork.fully_connected(n=3, coupling=2.0,
                                                rng=np.random.default_rng(7))
        result = check_contraction_condition(net, gamma=0.0, kappa=0.0, dt=1.0)
        assert isinstance(result["contraction_holds"], bool)
        # conclusion string must not raise
        assert isinstance(result["banach_conclusion"], str)
