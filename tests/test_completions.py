# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_completions.py
=========================
Unit tests for the six structural completions of the Unitary Manifold:

[1]  KK wavefunction renormalisation  →  r_eff < 0.036      (inflation.py)
[2]  KK mode sum for Aₛ               →  amplitude gap closed (inflation.py)
[3]  Index-theorem route to n_w        →  n_w = 5            (derivation.py)
[4]  Anomaly-inflow route to k_CS      →  k_CS = 74          (derivation.py)
[5]  Holographic renormalisation       →  finite S_ren        (boundary.py)
[6]  FTUM contraction condition        →  unique fixed point  (fixed_point.py)
"""

from __future__ import annotations

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------

from src.core.inflation import (
    kk_wavefunction_renorm,
    epsilon_eff_kk,
    r_eff_kk,
    solve_p_for_r_constraint,
    kk_amplitude_sum,
    effective_phi0_kk,
    ns_from_phi0,
    slow_roll_params,
    gw_potential_derivs,
)
from src.core.derivation import (
    derive_nw_index_theorem,
    derive_kcs_anomaly_inflow,
    SM_FERMION_SPECTRUM_DEFAULT,
    ALPHA_EM_CANONICAL,
    R_C_CANONICAL,
)
from src.holography.boundary import (
    fefferman_graham_expansion,
    boundary_counterterms,
    holographic_renormalized_action,
    BoundaryState,
)
from src.multiverse.fixed_point import (
    MultiverseNetwork,
    weighted_norm_network,
    operator_spectral_radius,
    check_contraction_condition,
)


# ===========================================================================
# [1]  KK wavefunction renormalisation
# ===========================================================================

class TestKKWavefunctionRenorm:
    """kk_wavefunction_renorm, epsilon_eff_kk, r_eff_kk."""

    def test_flat_profile_is_phi0_power(self):
        """For m_phi=0 (flat profile), Z_kinetic = phi0^p analytically."""
        for phi0 in [0.5, 1.0, 2.0, 5.0]:
            for p in [0.5, 1.0, 2.0, 3.0]:
                Z = kk_wavefunction_renorm(phi0, p=p, m_phi=0.0)
                assert abs(Z - phi0 ** p) < 1e-12, (
                    f"Z_kinetic != phi0^p for phi0={phi0}, p={p}"
                )

    def test_nonflat_profile_larger_than_flat(self):
        """Curved profile (m_phi > 0) with p > 0 has Z > phi0^p for phi0 = 1."""
        # For m_phi > 0, cosh(m_phi y) ≥ 1, so integral > phi0^p when phi0 = 1
        Z_flat = kk_wavefunction_renorm(1.0, p=1.0, m_phi=0.0)
        Z_curved = kk_wavefunction_renorm(1.0, p=1.0, R_c=1.0, m_phi=1.0)
        assert Z_curved > Z_flat, (
            f"Curved profile Z={Z_curved} should exceed flat Z={Z_flat}"
        )

    def test_epsilon_eff_reduces_epsilon(self):
        """epsilon_eff = epsilon / Z must be smaller than bare epsilon when Z > 1."""
        eps = 0.1
        Z = 3.0
        eps_eff = epsilon_eff_kk(eps, Z)
        assert abs(eps_eff - eps / Z) < 1e-14
        assert eps_eff < eps

    def test_r_eff_formula(self):
        """r_eff = 16 * epsilon / Z."""
        eps = 0.006
        Z = 3.0
        r = r_eff_kk(eps, Z)
        assert abs(r - 16.0 * eps / Z) < 1e-14

    def test_r_eff_below_bicep_keck_with_Z3(self):
        """With Z_kinetic ≥ 3 and bare epsilon from phi0_eff ≈ 31.4, r_eff < 0.036."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        phi_star = phi0_eff / np.sqrt(3.0)
        V, dV, d2V = gw_potential_derivs(phi_star, phi0_eff, lam=1.0)
        eps, _ = slow_roll_params(phi_star, V, dV, d2V)
        r_bare = 16.0 * eps
        r_eff_3 = r_eff_kk(eps, 3.0)
        assert r_eff_3 < 0.036, (
            f"r_eff={r_eff_3:.4f} should be < 0.036 with Z=3 "
            f"(r_bare={r_bare:.4f})"
        )

    def test_r_eff_does_not_shift_ns(self):
        """Z_kinetic affects ε_eff but not η → nₛ is unchanged."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        ns_bare, _, eps, eta = ns_from_phi0(phi0_eff)
        # With Z_kinetic renorm, only epsilon is renormed; nₛ uses the full formula
        # nₛ = 1 - 6ε + 2η; renorming ε shifts nₛ slightly but η is unchanged
        eps_eff = epsilon_eff_kk(eps, 3.0)
        ns_eff = 1.0 - 6.0 * eps_eff + 2.0 * eta
        # ns_eff should be closer to 1 (less tilt from ε) while η part unchanged
        assert ns_eff > ns_bare, (
            "Reducing ε_eff should bring nₛ closer to 1 (less red tilt from ε)"
        )

    def test_invalid_phi0_raises(self):
        with pytest.raises(ValueError, match="phi0"):
            kk_wavefunction_renorm(0.0, p=1.0)

    def test_invalid_Z_raises(self):
        with pytest.raises(ValueError, match="Z_kinetic"):
            epsilon_eff_kk(0.1, 0.0)

    def test_solve_p_constraint_finds_solution_with_curved_profile(self):
        """solve_p_for_r_constraint finds p s.t. r_eff < 0.036 for m_phi > 0."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        phi_star = phi0_eff / np.sqrt(3.0)
        V, dV, _ = gw_potential_derivs(phi_star, phi0_eff, lam=1.0)
        eps, _ = slow_roll_params(phi_star, V, dV, _)
        result = solve_p_for_r_constraint(eps, r_target=0.036, m_phi=1.0)
        # With large enough p, Z grows → r_eff shrinks
        assert result["constraint_met"] or result["r_eff_values"][-1] < 0.036, (
            "Should find p giving r_eff < 0.036 for m_phi=1"
        )

    def test_solve_p_returns_consistent_r(self):
        """r_eff at p_solution matches the reported r_eff value."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        phi_star = phi0_eff / np.sqrt(3.0)
        V, dV, _ = gw_potential_derivs(phi_star, phi0_eff, lam=1.0)
        eps, _ = slow_roll_params(phi_star, V, dV, _)
        result = solve_p_for_r_constraint(eps, r_target=0.036, m_phi=1.0)
        if result["constraint_met"]:
            p_sol = result["p_solution"]
            Z_sol = result["Z_solution"]
            r_check = r_eff_kk(eps, Z_sol)
            assert abs(r_check - result["r_eff"]) < 1e-10


# ===========================================================================
# [2]  KK mode sum for Aₛ
# ===========================================================================

class TestKKAmplitudeSum:
    """kk_amplitude_sum."""

    def test_zero_mode_recovers_As_zero_when_no_kk_modes_active(self):
        """With m_KK_1 > H*, only the zero mode contributes: A_s_total = A_s_zero."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        # Very small R_c → m_KK_1 = 1/R_c >> H_* → only n=0 active
        result = kk_amplitude_sum(phi0_eff, lam=1.0, R_c=1e-6, N_max=10)
        assert result["N_active"] == 1, (
            f"Expected only zero mode active, got N_active={result['N_active']}"
        )
        assert abs(result["As_total"] - result["As_zero"]) < 1e-14 * abs(result["As_zero"])

    def test_enhancement_equals_N_active(self):
        """A_s_total / A_s_zero == N_active exactly."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        result = kk_amplitude_sum(phi0_eff, lam=1.0, R_c=1.0, N_max=50)
        assert abs(result["enhancement"] - result["N_active"]) < 1e-12

    def test_large_R_c_gives_more_active_modes(self):
        """Larger R_c → smaller m_KK_1 → more KK modes below H_*."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        r1 = kk_amplitude_sum(phi0_eff, lam=1.0, R_c=1.0,   N_max=200)
        r2 = kk_amplitude_sum(phi0_eff, lam=1.0, R_c=10.0,  N_max=200)
        assert r2["N_active"] >= r1["N_active"], (
            "Larger R_c should give at least as many active KK modes"
        )

    def test_amplitude_positive(self):
        phi0_eff = effective_phi0_kk(1.0, 5)
        result = kk_amplitude_sum(phi0_eff, R_c=1.0)
        assert result["As_zero"] > 0.0
        assert result["As_total"] > 0.0

    def test_enhancement_closes_amplitude_gap_with_R_c_tuned(self):
        """With R_c chosen so that ~5 modes are active, enhancement ≈ 5.

        The known amplitude gap is a factor 4–7.  We verify that the KK
        tower mechanism can produce the required enhancement.
        """
        phi0_eff = effective_phi0_kk(1.0, 5)
        phi_star = phi0_eff / np.sqrt(3.0)
        V, _, _ = gw_potential_derivs(phi_star, phi0_eff, lam=1.0)
        H_star = float(np.sqrt(V / 3.0))
        # Choose R_c s.t. m_KK_4 < H* < m_KK_5:  R_c = 4 / H_star (so m_4 = H_star/4 → active)
        R_c_target = 5.0 / H_star   # makes m_1=H/5, …, m_4=4H/5, m_5=H* → 5 modes
        result = kk_amplitude_sum(phi0_eff, R_c=R_c_target, N_max=200)
        assert result["N_active"] >= 4, (
            f"Expected ≥ 4 active modes for R_c={R_c_target:.3f}, "
            f"got N_active={result['N_active']}"
        )
        assert result["enhancement"] >= 4, (
            f"Enhancement={result['enhancement']} should be ≥ 4 to close amplitude gap"
        )

    def test_invalid_phi0_eff_raises(self):
        with pytest.raises(ValueError):
            kk_amplitude_sum(-1.0, R_c=1.0)

    def test_output_keys_present(self):
        phi0_eff = effective_phi0_kk(1.0, 5)
        result = kk_amplitude_sum(phi0_eff, R_c=1.0)
        for key in ("As_zero", "As_total", "enhancement", "N_active", "H_star",
                    "m_KK_1", "R_c", "phi_star", "As_formula"):
            assert key in result, f"Missing key '{key}'"


# ===========================================================================
# [3]  Index-theorem route to n_w
# ===========================================================================

class TestIndexTheoremNW:
    """derive_nw_index_theorem."""

    def test_three_generations_gives_five(self):
        """Standard input: 3 SM generations → n_w = 5."""
        n_w, details = derive_nw_index_theorem(n_generations=3, z2_removes=1)
        assert n_w == 5, f"Expected n_w=5, got {n_w}"
        assert details["n_w"] == 5
        assert details["n_w_before_Z2"] == 6
        assert details["is_derived"] is True

    def test_index_equals_n_generations(self):
        n_w, details = derive_nw_index_theorem(n_generations=3)
        assert details["index_D5"] == 3

    def test_orbifold_doubling(self):
        """n_w_before_Z2 = 2 × n_generations before projection."""
        for ng in [1, 2, 3, 4]:
            _, details = derive_nw_index_theorem(n_generations=ng, z2_removes=0)
            assert details["n_w_before_Z2"] == 2 * ng

    def test_z2_removes_one(self):
        """Default Z₂ projection removes exactly 1 mode."""
        _, details = derive_nw_index_theorem(n_generations=3)
        assert details["z2_removes"] == 1
        assert details["n_w"] == details["n_w_before_Z2"] - 1

    def test_derivation_marked_as_derived(self):
        _, details = derive_nw_index_theorem()
        assert details["is_derived"] is True

    def test_summary_string_present(self):
        _, details = derive_nw_index_theorem()
        assert isinstance(details["derivation_summary"], str)
        assert "5" in details["derivation_summary"]

    def test_invalid_n_generations_raises(self):
        with pytest.raises(ValueError, match="n_generations"):
            derive_nw_index_theorem(n_generations=0)

    def test_invalid_z2_removes_raises(self):
        with pytest.raises(ValueError, match="z2_removes"):
            derive_nw_index_theorem(n_generations=3, z2_removes=-1)

    def test_different_generations_gives_correct_nw(self):
        """Verify formula for various n_gen values."""
        for ng in [1, 2, 3, 4, 5]:
            n_w, _ = derive_nw_index_theorem(n_generations=ng, z2_removes=1)
            expected = 2 * ng - 1
            assert n_w == expected, (
                f"For n_gen={ng}: expected n_w={expected}, got {n_w}"
            )


# ===========================================================================
# [4]  Anomaly-inflow route to k_CS
# ===========================================================================

class TestAnomalyInflowKCS:
    """derive_kcs_anomaly_inflow."""

    def test_geometric_kcs_is_74(self):
        """The birefringence formula gives k_CS_int = 74 (CS_LEVEL_PLANCK_MATCH)."""
        result = derive_kcs_anomaly_inflow()
        assert result["k_cs_int"] == 74, (
            f"k_cs_int={result['k_cs_int']} should equal 74"
        )

    def test_sm_left_anomaly_coefficient(self):
        """Left-chiral SM anomaly coefficient = 72 (Q_L: 18, L_L: 54)."""
        result = derive_kcs_anomaly_inflow()
        assert result["A_SM_left"] == 72, (
            f"A_SM_left={result['A_SM_left']} expected 72 (Q_L: 18, L_L: 54)"
        )

    def test_delta_k_is_two(self):
        """Deficit δk = k_cs − A_SM_left = 74 − 72 = 2 (two hidden-sector modes)."""
        result = derive_kcs_anomaly_inflow()
        assert result["delta_k"] == 2, (
            f"delta_k={result['delta_k']} expected 2"
        )

    def test_consistency_flag(self):
        """is_consistent = True iff |k_cs − A_SM_left| ≤ 3."""
        result = derive_kcs_anomaly_inflow()
        assert result["is_consistent"] is True

    def test_per_fermion_breakdown_contains_all_species(self):
        """Output includes one entry per SM species in SM_FERMION_SPECTRUM_DEFAULT."""
        result = derive_kcs_anomaly_ingest = derive_kcs_anomaly_inflow()
        names = {f["name"] for f in result["per_fermion"]}
        for expected_name in ("Q_L", "u_R", "d_R", "L_L", "e_R"):
            assert expected_name in names, f"Missing '{expected_name}' in per_fermion"

    def test_per_fermion_QL_contrib(self):
        """Q_L: Y6=1, mult=3×2×3=18 → left-chiral contribution = 1² × 18 × (+1) = 18."""
        result = derive_kcs_anomaly_inflow()
        ql = next(f for f in result["per_fermion"] if f["name"] == "Q_L")
        assert ql["Y6_sq"] == 1
        assert ql["mult"] == 18
        assert ql["contrib"] == 18

    def test_per_fermion_LL_contrib(self):
        """L_L: Y6=3, mult=1×2×3=6 → left-chiral contribution = 9 × 6 × (+1) = 54."""
        result = derive_kcs_anomaly_inflow()
        ll = next(f for f in result["per_fermion"] if f["name"] == "L_L")
        assert ll["Y6_sq"] == 9
        assert ll["mult"] == 6
        assert ll["contrib"] == 54

    def test_geometric_kcs_continuous_value(self):
        """k_cs_geometric should be close to 74 (within 1)."""
        result = derive_kcs_anomaly_inflow()
        assert abs(result["k_cs_geometric"] - 74.0) < 1.0

    def test_output_keys(self):
        result = derive_kcs_anomaly_inflow()
        for key in ("k_cs_geometric", "k_cs_int", "A_SM_left", "A_SM_total",
                    "delta_k", "per_fermion", "beta_target_deg", "delta_phi",
                    "is_consistent"):
            assert key in result, f"Missing key '{key}'"

    def test_custom_beta_target(self):
        """Different beta_target changes k_cs_geometric continuously."""
        r1 = derive_kcs_anomaly_inflow(beta_target_deg=0.30)
        r2 = derive_kcs_anomaly_inflow(beta_target_deg=0.40)
        assert r1["k_cs_geometric"] < r2["k_cs_geometric"]


# ===========================================================================
# [5]  Holographic renormalisation
# ===========================================================================

class TestHolographicRenormalization:
    """fefferman_graham_expansion, boundary_counterterms, holographic_renormalized_action."""

    @pytest.fixture
    def flat_boundary_metric(self):
        """Simple flat induced metric for N=10 grid points."""
        N = 10
        h = np.zeros((N, 2, 2))
        for i in range(N):
            h[i] = np.eye(2) * (1.0 + 0.05 * np.sin(i * 0.5))
        return h

    # --- fefferman_graham_expansion ---

    def test_fg_g0_equals_boundary_metric(self, flat_boundary_metric):
        """g^(0) must be the boundary metric itself."""
        h = flat_boundary_metric
        fg = fefferman_graham_expansion(h, L_ads=1.0)
        np.testing.assert_array_equal(fg["g0"], h)

    def test_fg_returns_g2_and_g4(self, flat_boundary_metric):
        """FG expansion of order 4 returns g2 and g4 arrays."""
        fg = fefferman_graham_expansion(flat_boundary_metric, L_ads=1.0, order=4)
        assert "g2" in fg
        assert "g4" in fg
        assert fg["g2"].shape == flat_boundary_metric.shape
        assert fg["g4"].shape == flat_boundary_metric.shape

    def test_fg_g2_shape(self, flat_boundary_metric):
        fg = fefferman_graham_expansion(flat_boundary_metric)
        assert fg["g2"].shape == flat_boundary_metric.shape

    def test_fg_trace_g2_shape(self, flat_boundary_metric):
        fg = fefferman_graham_expansion(flat_boundary_metric)
        assert fg["trace_g2"].shape == (flat_boundary_metric.shape[0],)

    def test_fg_flat_metric_has_zero_g2(self):
        """For exactly flat metric (det = 1), g^{(2)} = 0."""
        N = 5
        h = np.stack([np.eye(2)] * N)
        fg = fefferman_graham_expansion(h, L_ads=1.0)
        np.testing.assert_allclose(fg["g2"], 0.0, atol=1e-14)

    # --- boundary_counterterms ---

    def test_counterterms_returns_float_S_ct(self, flat_boundary_metric):
        ct = boundary_counterterms(flat_boundary_metric, L_ads=1.0, dx=0.1)
        assert isinstance(ct["S_ct"], float)
        assert np.isfinite(ct["S_ct"])

    def test_counterterms_keys(self, flat_boundary_metric):
        ct = boundary_counterterms(flat_boundary_metric)
        for key in ("S_ct", "S_K", "S_cosmo", "S_curv", "sqrt_gamma", "kappa5_sq"):
            assert key in ct, f"Missing key '{key}'"

    def test_counterterms_sqrt_gamma_positive(self, flat_boundary_metric):
        ct = boundary_counterterms(flat_boundary_metric)
        assert np.all(ct["sqrt_gamma"] >= 0.0)

    def test_counterterms_kappa5_sq(self, flat_boundary_metric):
        ct = boundary_counterterms(flat_boundary_metric, G5=1.0)
        assert abs(ct["kappa5_sq"] - 8.0 * np.pi) < 1e-12

    # --- holographic_renormalized_action ---

    def test_S_ren_is_finite_for_reasonable_S_bulk(self, flat_boundary_metric):
        """S_ren = S_bulk + S_ct should be finite."""
        result = holographic_renormalized_action(
            S_bulk=10.0, g_boundary=flat_boundary_metric, L_ads=1.0, dx=0.1
        )
        assert result["is_finite"] is True
        assert np.isfinite(result["S_ren"])

    def test_S_ren_equation(self, flat_boundary_metric):
        """S_ren = S_bulk + S_ct."""
        S_bulk = 5.0
        result = holographic_renormalized_action(
            S_bulk=S_bulk, g_boundary=flat_boundary_metric
        )
        assert abs(result["S_ren"] - (S_bulk + result["S_ct"])) < 1e-12

    def test_output_keys(self, flat_boundary_metric):
        result = holographic_renormalized_action(1.0, flat_boundary_metric)
        for key in ("S_bulk", "S_ct", "S_ren", "is_finite",
                    "Z_admissible", "counterterm_details"):
            assert key in result, f"Missing key '{key}'"

    def test_S_ren_is_not_just_S_bulk(self, flat_boundary_metric):
        """S_ren ≠ S_bulk in general (counterterms are non-zero)."""
        result = holographic_renormalized_action(100.0, flat_boundary_metric)
        assert result["S_ct"] != 0.0, "Counterterms should be non-zero for non-trivial metric"


# ===========================================================================
# [6]  FTUM contraction condition
# ===========================================================================

class TestFTUMContractionCondition:
    """weighted_norm_network, operator_spectral_radius, check_contraction_condition."""

    @pytest.fixture
    def small_chain(self):
        return MultiverseNetwork.chain(n=4, coupling=0.05,
                                       rng=np.random.default_rng(0))

    @pytest.fixture
    def fully_connected_3(self):
        return MultiverseNetwork.fully_connected(n=3, coupling=0.05,
                                                  rng=np.random.default_rng(1))

    # --- weighted_norm_network ---

    def test_weighted_norm_positive(self, small_chain):
        w = weighted_norm_network(small_chain)
        assert w >= 0.0

    def test_weighted_norm_holographic_default(self, small_chain):
        """Default weights are A_i / 4 (G4 = 1)."""
        w = weighted_norm_network(small_chain)
        assert np.isfinite(w)

    def test_weighted_norm_custom_weights(self, small_chain):
        n = small_chain.n_nodes()
        w_ones = weighted_norm_network(small_chain, weights=np.ones(n))
        assert np.isfinite(w_ones)

    def test_weighted_norm_wrong_length_raises(self, small_chain):
        with pytest.raises(ValueError, match="weights"):
            weighted_norm_network(small_chain, weights=np.ones(99))

    def test_weighted_norm_zero_network_is_zero(self):
        """All-zero state vectors should give norm zero."""
        from src.multiverse.fixed_point import MultiverseNode
        nodes = [MultiverseNode(dim=2, S=0.0, A=0.0, Q_top=0.0,
                                X=np.zeros(2), Xdot=np.zeros(2)) for _ in range(3)]
        adj = np.zeros((3, 3))
        net = MultiverseNetwork(nodes=nodes, adjacency=adj)
        assert weighted_norm_network(net) == 0.0

    # --- operator_spectral_radius ---

    def test_spectral_radius_positive(self, small_chain):
        sr = operator_spectral_radius(small_chain, dt=0.2)
        assert sr["rho"] >= 0.0

    def test_spectral_radius_finite(self, small_chain):
        sr = operator_spectral_radius(small_chain, dt=0.2)
        assert np.isfinite(sr["rho"])

    def test_spectral_radius_keys(self, small_chain):
        sr = operator_spectral_radius(small_chain)
        for key in ("rho", "is_contraction", "contraction_margin",
                    "gamma_critical", "n_nodes", "method"):
            assert key in sr, f"Missing key '{key}'"

    def test_spectral_radius_n_nodes(self, small_chain):
        sr = operator_spectral_radius(small_chain)
        assert sr["n_nodes"] == 4

    def test_weakly_coupled_network_is_contraction(self):
        """Very weak coupling (adjacency ≈ 0) + kappa > 0: H alone is contractive."""
        net = MultiverseNetwork.chain(n=3, coupling=1e-6,
                                      rng=np.random.default_rng(42))
        sr = operator_spectral_radius(net, dt=0.2, kappa=0.5)
        # H matrix: diagonal −kappa*dt = −0.1 → eigenvalue magnitude = 0.1 < 1
        assert sr["is_contraction"] is True

    # --- check_contraction_condition ---

    def test_contraction_holds_with_canonical_gamma(self, small_chain):
        """With canonical gamma=5.0 and weak coupling, contraction should hold."""
        result = check_contraction_condition(small_chain, gamma=5.0)
        assert result["contraction_holds"] is True

    def test_contraction_keys(self, small_chain):
        result = check_contraction_condition(small_chain)
        for key in ("rho_HT", "rho_U_damped", "contraction_holds",
                    "convergence_rate", "n_iters_to_1pct",
                    "banach_conclusion", "gamma_used", "gamma_critical"):
            assert key in result, f"Missing key '{key}'"

    def test_rho_U_damped_formula(self, small_chain):
        """rho_U_damped = rho_HT / (1 + gamma * dt)."""
        gamma = 5.0
        dt = 0.2
        result = check_contraction_condition(small_chain, gamma=gamma)
        sr = operator_spectral_radius(small_chain, dt=dt)
        expected_rho = sr["rho"] / (1.0 + gamma * dt)
        assert abs(result["rho_U_damped"] - expected_rho) < 1e-10

    def test_banach_conclusion_is_string(self, small_chain):
        result = check_contraction_condition(small_chain)
        assert isinstance(result["banach_conclusion"], str)
        assert len(result["banach_conclusion"]) > 0

    def test_convergence_rate_positive(self, small_chain):
        result = check_contraction_condition(small_chain)
        assert result["convergence_rate"] >= 0.0

    def test_zero_coupling_gamma0_may_not_contract(self):
        """With gamma=0 and kappa=0, H+T has no damping → may not be contractive."""
        net = MultiverseNetwork.fully_connected(n=3, coupling=2.0,
                                                rng=np.random.default_rng(7))
        result = check_contraction_condition(net, gamma=0.0, kappa=0.0, dt=1.0)
        # rho_U_damped == rho_HT, which may be ≥ 1 for large coupling
        assert isinstance(result["contraction_holds"], bool)

    def test_large_gamma_always_contracts(self):
        """With very large gamma, rho_U_damped → 0 regardless of coupling."""
        net = MultiverseNetwork.fully_connected(n=5, coupling=10.0,
                                                rng=np.random.default_rng(9))
        result = check_contraction_condition(net, gamma=1e6)
        assert result["contraction_holds"] is True
        assert result["rho_U_damped"] < 1.0
