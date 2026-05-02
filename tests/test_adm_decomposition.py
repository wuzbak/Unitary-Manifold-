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
        g_bad = np.eye(4)  # all positive (Riemannian, not Lorentzian)
        with pytest.raises(ValueError, match="g_\\{tt\\}"):
            extract_induced_metric(g_bad)

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
