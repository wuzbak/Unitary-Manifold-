# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_adm_decomposition.py
================================
Test suite for src/core/adm_decomposition.py — Pillar 100.

Covers:
  a. Induced-metric extraction (gamma, N, beta from g_{μν})
  b. Extrinsic curvature K_{ij} in Gaussian normal gauge and general case
  c. Hamiltonian constraint residual for flat/vacuum initial data
  d. ADM vs Ricci-flow comparison — the UM uses coordinate time
  e. Arrow-of-time ADM link — structured derivation
  f. Pillar 100 summary
"""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.adm_decomposition import (
    extract_induced_metric,
    extrinsic_curvature,
    hamiltonian_constraint,
    adm_vs_ricci_flow_comparison,
    arrow_of_time_adm_link,
    adm_lapse_deviation,
    adm_time_lapse_bridge,
    frw_adm_exact_lapse,
    pillar_100_summary,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def flat_minkowski_4d():
    """Flat Minkowski metric g_{μν} = diag(−1, 1, 1, 1)."""
    return np.diag([-1.0, 1.0, 1.0, 1.0])


@pytest.fixture
def perturbed_4d():
    """Slightly perturbed Minkowski metric (still Lorentzian)."""
    g = np.diag([-1.0, 1.0, 1.0, 1.0])
    g[0, 0] = -1.04  # lapse perturbation
    g[1, 1] = 1.02
    return g


@pytest.fixture
def flat_3d_metric():
    """Flat induced 3-metric δ_{ij}."""
    return np.eye(3)


@pytest.fixture
def zero_K(flat_3d_metric):
    """Zero extrinsic curvature (flat initial data)."""
    return np.zeros((3, 3))


# ---------------------------------------------------------------------------
# a. Induced-metric extraction
# ---------------------------------------------------------------------------

class TestExtractInducedMetric:
    """Tests for extract_induced_metric()."""

    def test_flat_gamma_is_identity(self, flat_minkowski_4d):
        gamma, N, beta = extract_induced_metric(flat_minkowski_4d)
        assert gamma.shape == (3, 3)
        np.testing.assert_allclose(gamma, np.eye(3), atol=1e-12)

    def test_lapse_is_one_for_flat(self, flat_minkowski_4d):
        _, N, _ = extract_induced_metric(flat_minkowski_4d)
        assert abs(N - 1.0) < 1e-12

    def test_shift_is_zero_for_diagonal(self, flat_minkowski_4d):
        _, _, beta = extract_induced_metric(flat_minkowski_4d)
        np.testing.assert_allclose(beta, np.zeros(3), atol=1e-12)

    def test_lapse_from_perturbed_metric(self, perturbed_4d):
        _, N, _ = extract_induced_metric(perturbed_4d)
        expected_N = np.sqrt(1.04)
        assert abs(N - expected_N) < 1e-10

    def test_induced_metric_3x3(self, perturbed_4d):
        gamma, _, _ = extract_induced_metric(perturbed_4d)
        assert gamma.shape == (3, 3)

    def test_induced_metric_is_spatial_block(self, perturbed_4d):
        gamma, _, _ = extract_induced_metric(perturbed_4d)
        np.testing.assert_allclose(gamma, perturbed_4d[1:, 1:], atol=1e-12)

    def test_raises_for_non_lorentzian(self):
        non_lorentzian_metric = np.eye(4)  # all positive — Riemannian, not Lorentzian
        with pytest.raises(ValueError, match="g_\\{tt\\}"):
            extract_induced_metric(non_lorentzian_metric)

    def test_raises_for_wrong_dimension(self):
        g_5d = np.eye(5)
        with pytest.raises(ValueError, match="Expected 4×4"):
            extract_induced_metric(g_5d)

    def test_symmetry_preserved(self, perturbed_4d):
        """Induced metric must be symmetric."""
        gamma, _, _ = extract_induced_metric(perturbed_4d)
        np.testing.assert_allclose(gamma, gamma.T, atol=1e-12)


# ---------------------------------------------------------------------------
# b. Extrinsic curvature
# ---------------------------------------------------------------------------

class TestExtrinsicCurvature:
    """Tests for extrinsic_curvature()."""

    def test_zero_K_for_static_metric(self, flat_3d_metric):
        """Static metric (γ̇ = 0) in GN gauge gives K_{ij} = 0."""
        gamma_dot = np.zeros((3, 3))
        K = extrinsic_curvature(flat_3d_metric, gamma_dot, N=1.0,
                                beta=np.zeros(3), dx=0.1)
        np.testing.assert_allclose(K, np.zeros((3, 3)), atol=1e-12)

    def test_K_shape_is_3x3(self, flat_3d_metric):
        gamma_dot = np.eye(3) * 0.01
        K = extrinsic_curvature(flat_3d_metric, gamma_dot, N=1.0,
                                beta=np.zeros(3), dx=0.1)
        assert K.shape == (3, 3)

    def test_K_proportional_to_gamma_dot_in_gn_gauge(self, flat_3d_metric):
        """In GN gauge (N=1, β=0): K_{ij} = (1/2) γ̇_{ij}."""
        gamma_dot = np.diag([0.02, 0.01, 0.04])
        K = extrinsic_curvature(flat_3d_metric, gamma_dot, N=1.0,
                                beta=np.zeros(3), dx=0.1)
        np.testing.assert_allclose(K, 0.5 * gamma_dot, atol=1e-12)

    def test_K_scaled_by_lapse(self, flat_3d_metric):
        """Doubling N halves K_{ij} (for zero shift)."""
        gamma_dot = np.eye(3) * 0.1
        K1 = extrinsic_curvature(flat_3d_metric, gamma_dot, N=1.0,
                                 beta=np.zeros(3), dx=0.1)
        K2 = extrinsic_curvature(flat_3d_metric, gamma_dot, N=2.0,
                                 beta=np.zeros(3), dx=0.1)
        np.testing.assert_allclose(K2, K1 / 2.0, atol=1e-12)

    def test_K_is_symmetric(self, flat_3d_metric):
        """K_{ij} must be symmetric."""
        rng = np.random.default_rng(42)
        gamma_dot = rng.standard_normal((3, 3))
        gamma_dot = 0.5 * (gamma_dot + gamma_dot.T)
        K = extrinsic_curvature(flat_3d_metric, gamma_dot, N=1.0,
                                beta=np.zeros(3), dx=0.1)
        np.testing.assert_allclose(K, K.T, atol=1e-12)

    def test_K_nonzero_for_expanding_universe(self, flat_3d_metric):
        """Expanding universe: γ̇_{ij} = 2H γ_{ij} gives K = H δ_{ij}."""
        H = 0.5
        gamma_dot = 2.0 * H * flat_3d_metric
        K = extrinsic_curvature(flat_3d_metric, gamma_dot, N=1.0,
                                beta=np.zeros(3), dx=0.1)
        expected = H * np.eye(3)
        np.testing.assert_allclose(K, expected, atol=1e-12)


# ---------------------------------------------------------------------------
# c. Hamiltonian constraint
# ---------------------------------------------------------------------------

class TestHamiltonianConstraint:
    """Tests for hamiltonian_constraint()."""

    def test_flat_vacuum_residual_is_zero(self, flat_3d_metric, zero_K):
        """Flat 3-metric + zero K + zero matter = constraint exactly satisfied."""
        H = hamiltonian_constraint(flat_3d_metric, zero_K, rho_m=0.0)
        assert abs(H) < 1e-12

    def test_returns_float(self, flat_3d_metric, zero_K):
        H = hamiltonian_constraint(flat_3d_metric, zero_K)
        assert isinstance(H, float)

    def test_matter_source_breaks_vacuum(self, flat_3d_metric, zero_K):
        """Non-zero matter density gives non-zero residual."""
        H = hamiltonian_constraint(flat_3d_metric, zero_K, rho_m=1.0)
        assert H != 0.0
        assert H < 0.0  # ρ_m > 0 shifts H negative

    def test_nonzero_K_trace_contributes(self, flat_3d_metric):
        """Non-zero K_trace gives K² contribution to H."""
        K_expand = 0.1 * np.eye(3)  # uniform expansion
        H = hamiltonian_constraint(flat_3d_metric, K_expand, rho_m=0.0)
        # K_trace = 0.3, K_sq = 0.03, H = 0 + 0.09 − 0.03 = 0.06
        assert abs(H - 0.06) < 1e-10

    def test_traceless_K_reduces_H(self, flat_3d_metric):
        """Traceless K_{ij} contributes −K^{ij}K_{ij} to H (negative)."""
        K_shear = np.array([[0.1, 0.0, 0.0],
                            [0.0, -0.1, 0.0],
                            [0.0, 0.0, 0.0]])
        H = hamiltonian_constraint(flat_3d_metric, K_shear, rho_m=0.0)
        # K_trace = 0, K_sq = 0.01 + 0.01 = 0.02, H = 0 + 0 − 0.02 = −0.02
        assert abs(H - (-0.02)) < 1e-10


# ---------------------------------------------------------------------------
# d. ADM vs Ricci-flow comparison
# ---------------------------------------------------------------------------

class TestAdmVsRicciFlow:
    """Tests for adm_vs_ricci_flow_comparison()."""

    def setup_method(self):
        self.gamma = np.eye(3)
        self.K = 0.05 * np.eye(3)
        self.N = 1.0
        self.beta = np.zeros(3)
        self.R_ij = np.zeros((3, 3))  # flat 3D curvature
        self.R4 = 0.0
        self.result = adm_vs_ricci_flow_comparison(
            self.gamma, self.K, self.N, self.beta, self.R_ij, self.R4, dt=0.01
        )

    def test_returns_dict_with_expected_keys(self):
        required = {
            "gamma_dot_adm", "gamma_dot_ricci", "difference",
            "max_difference", "flows_agree", "R4_is_source_not_flow_rhs",
            "conclusion",
        }
        assert required.issubset(self.result.keys())

    def test_adm_gamma_dot_shape(self):
        assert self.result["gamma_dot_adm"].shape == (3, 3)

    def test_ricci_gamma_dot_shape(self):
        assert self.result["gamma_dot_ricci"].shape == (3, 3)

    def test_adm_gives_minus_2NK_in_gn_gauge(self):
        """In GN gauge (β=0, flat R_{ij}=0): γ̇ = −2 N K."""
        expected = -2.0 * self.N * self.K
        np.testing.assert_allclose(
            self.result["gamma_dot_adm"], expected, atol=1e-12
        )

    def test_ricci_flow_gives_zero_for_flat(self):
        """R_{ij} = 0 (flat) → Ricci flow gives γ̇ = 0."""
        np.testing.assert_allclose(
            self.result["gamma_dot_ricci"], np.zeros((3, 3)), atol=1e-12
        )

    def test_flows_disagree_when_K_nonzero(self):
        """ADM and Ricci flow are different when K ≠ 0 and R_{ij} = 0."""
        assert not self.result["flows_agree"]

    def test_R4_is_always_source(self):
        assert self.result["R4_is_source_not_flow_rhs"] is True

    def test_conclusion_mentions_coordinate_time(self):
        assert "COORDINATE TIME" in self.result["conclusion"]

    def test_conclusion_mentions_pillar_100(self):
        assert "100" in self.result["conclusion"]

    def test_flows_agree_for_trivial_case(self):
        """Both flows agree when K = 0 AND R_{ij} = 0 (trivial)."""
        result_trivial = adm_vs_ricci_flow_comparison(
            np.eye(3), np.zeros((3, 3)), 1.0, np.zeros(3),
            np.zeros((3, 3)), 0.0, dt=0.01
        )
        assert result_trivial["flows_agree"]


# ---------------------------------------------------------------------------
# e. Arrow-of-time ADM link
# ---------------------------------------------------------------------------

class TestArrowOfTimeAdmLink:
    """Tests for arrow_of_time_adm_link()."""

    def setup_method(self):
        self.result = arrow_of_time_adm_link()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_100(self):
        assert self.result["pillar"] == 100

    def test_status_is_derived(self):
        assert self.result["status"] == "DERIVED"

    def test_has_four_steps(self):
        for key in ["step1_dec", "step2_hc", "step3_entropy", "step4_geometric_arrow"]:
            assert key in self.result

    def test_flow_parameter_is_coordinate_time(self):
        assert self.result["flow_parameter_is_coordinate_time"] is True

    def test_ricci_flow_not_used(self):
        assert self.result["ricci_flow_is_not_used"] is True

    def test_links_to_earlier_pillars(self):
        assert 53 in self.result["link_to_pillars"]
        assert 88 in self.result["link_to_pillars"]

    def test_step1_mentions_nec(self):
        assert "NEC" in self.result["step1_dec"] or "DEC" in self.result["step1_dec"]

    def test_step2_mentions_hamiltonian_constraint(self):
        assert "Hamiltonian" in self.result["step2_hc"] or "constraint" in self.result["step2_hc"]

    def test_step3_mentions_entropy(self):
        assert "entropy" in self.result["step3_entropy"].lower() or "S =" in self.result["step3_entropy"]

    def test_step4_mentions_kk_field(self):
        assert "KK" in self.result["step4_geometric_arrow"] or "B_μ" in self.result["step4_geometric_arrow"]

    def test_falsification_condition_present(self):
        assert "falsification" in self.result
        assert len(self.result["falsification"]) > 10


# ---------------------------------------------------------------------------
# f. Pillar 100 summary
# ---------------------------------------------------------------------------

class TestPillar100Summary:
    """Tests for pillar_100_summary()."""

    def setup_method(self):
        self.result = pillar_100_summary()

    def test_pillar_number_is_100(self):
        assert self.result["pillar"] == 100

    def test_status_is_derived(self):
        assert self.result["status"] == "DERIVED"

    def test_title_mentions_adm(self):
        assert "ADM" in self.result["label"]

    def test_key_result_mentions_coordinate_time(self):
        assert "COORDINATE TIME" in self.result["key_result"]

    def test_honest_gaps_present(self):
        assert isinstance(self.result["honest_gaps"], list)
        assert len(self.result["honest_gaps"]) >= 1

    def test_citations_present(self):
        assert isinstance(self.result["citations"], list)
        assert len(self.result["citations"]) >= 3

    def test_new_modules_list_has_five_functions(self):
        assert len(self.result["new_modules"]) == 5

    def test_provenance_has_pillar_100(self):
        assert self.result["provenance"]["pillar"] == 100

    def test_description_mentions_ricci_flow(self):
        assert "Ricci" in self.result["description"]


# ---------------------------------------------------------------------------
# §XIV.3 — ADM lapse deviation (adm_lapse_deviation)
# ---------------------------------------------------------------------------

class TestADMLapseDeviation:
    """Verify that the UM background lapse deviation from N=1 is < 1% (§XIV.3)."""

    @pytest.fixture(autouse=True)
    def result(self):
        self.result = adm_lapse_deviation()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_required_keys(self):
        required = {
            "lapse_N", "delta_lapse", "deviation_fractional",
            "deviation_percent", "ratio_sq", "below_threshold",
            "verdict", "status", "derivation",
        }
        assert required.issubset(self.result.keys())

    def test_lapse_close_to_one(self):
        """N_phys must be within floating-point distance of 1.0."""
        assert abs(self.result["lapse_N"] - 1.0) < 1e-50

    def test_deviation_fractional_positive(self):
        assert self.result["deviation_fractional"] > 0.0

    def test_deviation_below_one_percent(self):
        """Core §XIV.3 claim: deviation < 1%."""
        assert self.result["deviation_percent"] < 1.0

    def test_below_threshold_flag(self):
        assert self.result["below_threshold"] is True

    def test_status_quantified(self):
        assert self.result["status"] == "QUANTIFIED"

    def test_verdict_mentions_adm(self):
        assert "ADM" in self.result["verdict"]

    def test_custom_masses(self):
        """Custom M_KK and M_Pl values should still return < 1% for UM scales."""
        r = adm_lapse_deviation(M_KK_meV=200.0, M_Pl_meV=1.2209e31)
        assert r["deviation_percent"] < 1.0
        assert r["below_threshold"] is True


# ---------------------------------------------------------------------------
# ADM time-parameterization gap: lapse-function bridge
# ---------------------------------------------------------------------------

class TestADMTimeLapseBridge:
    """Tests for adm_time_lapse_bridge() — ADM gap quantification."""

    @classmethod
    def setup_class(cls):
        cls.result = adm_time_lapse_bridge()

    # ---- return structure ----

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_epsilon_sr(self):
        assert "epsilon_sr" in self.result

    def test_has_lapse_deviation_estimate(self):
        assert "lapse_deviation_estimate" in self.result

    def test_has_lapse_pct_error(self):
        assert "lapse_pct_error" in self.result

    def test_has_gaussian_normal_ok(self):
        assert "gaussian_normal_ok" in self.result

    def test_has_gap_status(self):
        assert "gap_status" in self.result

    def test_has_gap_description(self):
        assert "gap_description" in self.result

    def test_has_mitigation(self):
        assert "mitigation" in self.result

    def test_has_remaining_open(self):
        assert "remaining_open" in self.result

    # ---- physical content ----

    def test_default_epsilon_is_small(self):
        assert self.result["epsilon_sr"] < 0.01

    def test_lapse_deviation_equals_epsilon(self):
        assert abs(self.result["lapse_deviation_estimate"] - self.result["epsilon_sr"]) < 1e-12

    def test_lapse_pct_below_five_percent(self):
        assert self.result["lapse_pct_error"] < 5.0

    def test_gaussian_normal_ok_for_slow_roll(self):
        assert self.result["gaussian_normal_ok"] is True

    def test_gap_status_mentions_BACKGROUND_CLOSED(self):
        assert "BACKGROUND CLOSED" in self.result["gap_status"]

    def test_gap_status_references_frw_exact_lapse(self):
        assert "frw_adm_exact_lapse" in self.result["gap_status"]

    def test_gap_description_mentions_Ricci(self):
        assert "Ricci" in self.result["gap_description"]

    def test_gap_description_mentions_lapse(self):
        assert "lapse" in self.result["gap_description"].lower()

    def test_mitigation_mentions_pillar_41(self):
        assert "41" in self.result["mitigation"]

    def test_remaining_open_mentions_Hamiltonian(self):
        assert "Hamiltonian" in self.result["remaining_open"]

    # ---- phi0_eff override ----

    def test_phi0_eff_overrides_epsilon(self):
        phi0 = 31.416
        expected_eps = 6.0 / phi0 ** 2
        res = adm_time_lapse_bridge(phi0_eff=phi0)
        assert abs(res["epsilon_sr"] - expected_eps) < 1e-12

    def test_higher_epsilon_gives_larger_lapse_error(self):
        res_high = adm_time_lapse_bridge(epsilon_sr=0.05)
        res_low = adm_time_lapse_bridge(epsilon_sr=0.001)
        assert res_high["lapse_deviation_estimate"] > res_low["lapse_deviation_estimate"]

    def test_near_unity_epsilon_gaussian_not_ok(self):
        res = adm_time_lapse_bridge(epsilon_sr=0.1)
        assert res["gaussian_normal_ok"] is False


# ---------------------------------------------------------------------------
# FRW exact lapse — closes the ADM lapse gap for the cosmological background
# ---------------------------------------------------------------------------

class TestFRWAdmExactLapse:
    """Tests for frw_adm_exact_lapse() — Pillar 100 background gap closure."""

    @classmethod
    def setup_class(cls):
        cls.result = frw_adm_exact_lapse()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_N_exact_is_one(self):
        """Lapse N=1 is the exact GNC gauge choice for FRW."""
        assert self.result["N_exact"] == 1.0

    def test_lapse_deviation_background_is_zero(self):
        """Background lapse deviation is exactly zero (gauge choice, not approximation)."""
        assert self.result["lapse_deviation_background"] == 0.0

    def test_hamiltonian_constraint_numerically_satisfied(self):
        """3H² = 8πGρ must hold to < 1e-10 in Planck units."""
        assert self.result["hamiltonian_constraint_frw"] < 1e-10

    def test_hamiltonian_constraint_satisfied_flag(self):
        assert self.result["hamiltonian_constraint_satisfied"] is True

    def test_background_status_contains_CLOSED(self):
        assert "CLOSED" in self.result["background_status"]

    def test_background_status_mentions_exact(self):
        assert "exact" in self.result["background_status"].lower()

    def test_gap_status_contains_CLOSED(self):
        assert "CLOSED" in self.result["gap_status"]

    def test_perturbation_status_contains_OPEN(self):
        assert "OPEN" in self.result["perturbation_status"]

    def test_perturbation_status_mentions_elliptic(self):
        assert "elliptic" in self.result["perturbation_status"].lower()

    def test_gap_upgraded_from_contains_PARTIALLY_MITIGATED(self):
        assert "PARTIALLY MITIGATED" in self.result["gap_upgraded_from"]

    def test_gauge_choice_mentions_GNC(self):
        assert "GNC" in self.result["gauge_choice"] or "Gaussian" in self.result["gauge_choice"]

    def test_closure_statement_present(self):
        assert "closure_statement" in self.result
        assert len(self.result["closure_statement"]) > 50

    def test_closure_statement_mentions_Friedmann(self):
        assert "Friedmann" in self.result["closure_statement"]

    def test_n_w_default_is_5(self):
        assert self.result["n_w"] == 5

    def test_k_cs_default_is_74(self):
        assert self.result["k_cs"] == 74

    def test_slow_roll_epsilon_is_on_H_not_N(self):
        """ε = 6/n_w² = 0.24 for n_w=5; this is on H, not on N."""
        import math
        expected = 6.0 / 5 ** 2
        assert abs(self.result["slow_roll_epsilon"] - expected) < 1e-12

    def test_custom_n_w_changes_epsilon(self):
        res = frw_adm_exact_lapse(n_w=7)
        expected = 6.0 / 7 ** 2
        assert abs(res["slow_roll_epsilon"] - expected) < 1e-12

    def test_N_exact_unchanged_for_custom_n_w(self):
        """Winding number has no effect on N — N=1 is always exact."""
        res = frw_adm_exact_lapse(n_w=7)
        assert res["N_exact"] == 1.0

    def test_lapse_deviation_background_unchanged_for_any_epsilon(self):
        """Background lapse deviation is zero regardless of slow-roll regime."""
        res = frw_adm_exact_lapse(n_w=3)
        assert res["lapse_deviation_background"] == 0.0
