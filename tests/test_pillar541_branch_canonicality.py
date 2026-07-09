# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 541 — Branch Canonicality Certificate: (5,7) vs (5,6).

All tests enforce zero-failure requirement.
"""

import math
import pytest

from src.core.pillar541_branch_canonicality_certificate import (
    CANONICAL_BRANCH,
    SHADOW_BRANCH,
    CERTIFICATE,
    K_CS_CANONICAL,
    K_CS_SHADOW,
    N1_CANONICAL, N2_CANONICAL,
    N1_SHADOW, N2_SHADOW,
    R_CANONICAL,
    R_SHADOW,
    BETA_CANONICAL_DEG,
    BETA_SHADOW_DEG,
    LITEBIRD_SIGMA_DEG,
    LITEBIRD_DISCRIMINABILITY_SIGMA,
    NS_PLANCK,
    NS_PLANCK_UNC,
    PILLAR_STATUS,
    z2_odd_boundary_phase,
    ns_tension_sigma,
    r_braided_from_pair,
    birefringence_angle_deg,
    canonicality_certificate,
    BranchCanonicality,
)


# ──────────────────────────────────────────────────────────────────────────────
# Constant integrity tests
# ──────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_canonical_k_cs(self):
        """k_CS for canonical (5,7) = 5² + 7² = 74."""
        assert K_CS_CANONICAL == 74

    def test_shadow_k_cs(self):
        """k_CS for shadow (5,6) = 5² + 6² = 61."""
        assert K_CS_SHADOW == 61

    def test_canonical_pair(self):
        assert N1_CANONICAL == 5
        assert N2_CANONICAL == 7

    def test_shadow_pair(self):
        assert N1_SHADOW == 5
        assert N2_SHADOW == 6

    def test_canonical_r(self):
        """Canonical r = 0.0315."""
        assert abs(R_CANONICAL - 0.0315) < 1e-6

    def test_shadow_r(self):
        """Shadow r = 0.0175."""
        assert abs(R_SHADOW - 0.0175) < 1e-6

    def test_beta_canonical(self):
        """Canonical β = 0.331°."""
        assert abs(BETA_CANONICAL_DEG - 0.331) < 1e-3

    def test_beta_shadow(self):
        """Shadow β = 0.273°."""
        assert abs(BETA_SHADOW_DEG - 0.273) < 1e-3

    def test_litebird_sigma(self):
        """LiteBIRD σ = 0.01°."""
        assert abs(LITEBIRD_SIGMA_DEG - 0.01) < 1e-6

    def test_litebird_discriminability(self):
        """Sectors must be discriminable at ≥4σ by LiteBIRD."""
        assert LITEBIRD_DISCRIMINABILITY_SIGMA >= 4.0

    def test_beta_gap_consistent_with_discriminability(self):
        """Discriminability = gap / LiteBIRD σ."""
        gap = BETA_CANONICAL_DEG - BETA_SHADOW_DEG
        expected = gap / LITEBIRD_SIGMA_DEG
        assert abs(LITEBIRD_DISCRIMINABILITY_SIGMA - expected) < 0.01

    def test_planck_ns(self):
        """Planck 2018 nₛ = 0.9649 ± 0.0042."""
        assert abs(NS_PLANCK - 0.9649) < 1e-6
        assert abs(NS_PLANCK_UNC - 0.0042) < 1e-6

    def test_canonical_r_less_than_bicep_keck(self):
        """Canonical r < BICEP/Keck limit of 0.036."""
        assert R_CANONICAL < 0.036

    def test_shadow_r_less_than_bicep_keck(self):
        """Shadow r < BICEP/Keck limit of 0.036."""
        assert R_SHADOW < 0.036

    def test_shadow_r_near_act_dr6(self):
        """Shadow r = 0.0175 > ACT DR6 limit 0.016 — BOTH sectors in tension with ACT."""
        assert R_SHADOW > 0.016  # shadow sector also above ACT DR6 limit

    def test_canonical_r_exceeds_act_dr6(self):
        """Canonical r > ACT DR6 limit — genuine tension."""
        assert R_CANONICAL > 0.016

    def test_pillar_status_label(self):
        """Status label contains NON_CANONICAL_BRANCH_CERTIFIED."""
        assert "NON_CANONICAL_BRANCH_CERTIFIED" in PILLAR_STATUS
        assert "SHADOW_SECTOR_CLASSIFIED" in PILLAR_STATUS


# ──────────────────────────────────────────────────────────────────────────────
# Z₂-odd boundary phase tests
# ──────────────────────────────────────────────────────────────────────────────

class TestZ2OddBoundaryPhase:
    def test_canonical_satisfies_z2_odd(self):
        """(5,7) pair must satisfy Z₂-odd CS boundary condition."""
        result = z2_odd_boundary_phase(5, 7)
        assert result["is_z2_odd"] is True

    def test_shadow_does_not_satisfy_z2_odd(self):
        """(5,6) pair must NOT satisfy Z₂-odd CS boundary condition."""
        result = z2_odd_boundary_phase(5, 6)
        assert result["is_z2_odd"] is False

    def test_canonical_k_cs_correct(self):
        result = z2_odd_boundary_phase(5, 7)
        assert result["k_cs"] == 74

    def test_shadow_k_cs_correct(self):
        result = z2_odd_boundary_phase(5, 6)
        assert result["k_cs"] == 61

    def test_canonical_product_is_integer(self):
        """k_CS(5,7) × η̄(5) must yield an integer."""
        result = z2_odd_boundary_phase(5, 7)
        assert result["is_integer_product"] is True
        assert result["product_integer"] == 37

    def test_canonical_product_is_odd(self):
        """Product 37 is odd — this is what selects (5,7)."""
        result = z2_odd_boundary_phase(5, 7)
        assert result["product_integer"] % 2 == 1

    def test_shadow_product_is_non_integer(self):
        """k_CS(5,6) × η̄(5) does not yield an integer — boundary condition fails."""
        result = z2_odd_boundary_phase(5, 6)
        assert result["is_integer_product"] is False
        assert result["product_integer"] is None

    def test_z2_odd_returns_dict(self):
        result = z2_odd_boundary_phase(5, 7)
        for key in ["k_cs", "eta_bar", "is_z2_odd", "product_integer"]:
            assert key in result


# ──────────────────────────────────────────────────────────────────────────────
# nₛ tension tests
# ──────────────────────────────────────────────────────────────────────────────

class TestNsTension:
    def test_canonical_ns_tension(self):
        """Canonical nₛ = 0.9635 within 0.5σ of Planck."""
        sigma = ns_tension_sigma(0.9635)
        assert sigma < 0.5

    def test_shadow_ns_tension(self):
        """Shadow nₛ = 0.9610 within 1.5σ of Planck."""
        sigma = ns_tension_sigma(0.9610)
        assert sigma < 1.5

    def test_canonical_closer_than_shadow(self):
        """Canonical nₛ is closer to Planck than shadow nₛ."""
        canonical_sigma = ns_tension_sigma(0.9635)
        shadow_sigma = ns_tension_sigma(0.9610)
        assert canonical_sigma < shadow_sigma

    def test_exact_planck_zero_tension(self):
        sigma = ns_tension_sigma(NS_PLANCK)
        assert sigma == pytest.approx(0.0)

    def test_tension_is_symmetric(self):
        s1 = ns_tension_sigma(0.9649 + 0.01)
        s2 = ns_tension_sigma(0.9649 - 0.01)
        assert abs(s1 - s2) < 1e-10


# ──────────────────────────────────────────────────────────────────────────────
# r_braided computation tests
# ──────────────────────────────────────────────────────────────────────────────

class TestRBraided:
    def test_canonical_r_braided(self):
        """r_braided(5,7) ≈ 0.0315."""
        r = r_braided_from_pair(5, 7)
        assert abs(r - R_CANONICAL) < 1e-6

    def test_shadow_r_braided(self):
        """r_braided(5,6) ≈ 0.0175."""
        r = r_braided_from_pair(5, 6)
        assert abs(r - R_SHADOW) < 0.0002

    def test_canonical_r_greater_than_shadow(self):
        """Canonical r > shadow r (same r_bare, different c_s)."""
        r_c = r_braided_from_pair(5, 7)
        r_s = r_braided_from_pair(5, 6)
        assert r_c > r_s

    def test_r_formula_uses_cs_ratio(self):
        """Verify r_shadow / r_canonical = c_s(5,6) / c_s(5,7)."""
        r_c = r_braided_from_pair(5, 7)
        r_s = r_braided_from_pair(5, 6)
        cs_57 = (7**2 - 5**2) / (5**2 + 7**2)  # 24/74
        cs_56 = (6**2 - 5**2) / (5**2 + 6**2)  # 11/61
        expected_ratio = cs_56 / cs_57
        assert abs(r_s / r_c - expected_ratio) < 1e-6

    def test_r_positive(self):
        assert r_braided_from_pair(5, 7) > 0
        assert r_braided_from_pair(5, 6) > 0


# ──────────────────────────────────────────────────────────────────────────────
# Birefringence angle tests
# ──────────────────────────────────────────────────────────────────────────────

class TestBirefringenceAngle:
    def test_canonical_beta(self):
        """β(k_cs=74) = 0.331° (by definition/calibration)."""
        beta = birefringence_angle_deg(74)
        assert abs(beta - BETA_CANONICAL_DEG) < 1e-6

    def test_shadow_beta(self):
        """β(k_cs=61) ≈ 0.273°."""
        beta = birefringence_angle_deg(61)
        assert abs(beta - BETA_SHADOW_DEG) < 0.001

    def test_beta_increases_with_k_cs(self):
        """β ∝ k_cs — larger CS level → larger birefringence angle."""
        beta_61 = birefringence_angle_deg(61)
        beta_74 = birefringence_angle_deg(74)
        beta_80 = birefringence_angle_deg(80)
        assert beta_61 < beta_74 < beta_80

    def test_beta_positive(self):
        assert birefringence_angle_deg(74) > 0
        assert birefringence_angle_deg(61) > 0

    def test_litebird_discriminates_sectors(self):
        """LiteBIRD gap = β(5,7) − β(5,6) ≥ 4σ_LB."""
        gap = birefringence_angle_deg(74) - birefringence_angle_deg(61)
        assert gap > 0
        assert gap / LITEBIRD_SIGMA_DEG >= 4.0


# ──────────────────────────────────────────────────────────────────────────────
# BraidBranch data structure tests
# ──────────────────────────────────────────────────────────────────────────────

class TestBraidBranch:
    def test_canonical_branch_canonicality(self):
        assert CANONICAL_BRANCH.canonicality == "CANONICAL"

    def test_shadow_branch_canonicality(self):
        assert SHADOW_BRANCH.canonicality == "SHADOW"

    def test_canonical_branch_z2_odd(self):
        assert CANONICAL_BRANCH.z2_odd is True

    def test_shadow_branch_not_z2_odd(self):
        assert SHADOW_BRANCH.z2_odd is False

    def test_canonical_branch_r(self):
        assert abs(CANONICAL_BRANCH.r_braided - R_CANONICAL) < 1e-6

    def test_shadow_branch_r(self):
        assert abs(SHADOW_BRANCH.r_braided - R_SHADOW) < 1e-6

    def test_canonical_branch_beta(self):
        assert abs(CANONICAL_BRANCH.beta_deg - BETA_CANONICAL_DEG) < 1e-3

    def test_shadow_branch_beta(self):
        assert abs(SHADOW_BRANCH.beta_deg - BETA_SHADOW_DEG) < 1e-3

    def test_canonical_k_cs_squared(self):
        assert CANONICAL_BRANCH.k_cs == 5**2 + 7**2

    def test_shadow_k_cs_squared(self):
        assert SHADOW_BRANCH.k_cs == 5**2 + 6**2

    def test_branches_are_frozen(self):
        """BraidBranch is frozen (immutable)."""
        with pytest.raises(Exception):
            CANONICAL_BRANCH.r_braided = 0.99


# ──────────────────────────────────────────────────────────────────────────────
# Certificate tests
# ──────────────────────────────────────────────────────────────────────────────

class TestBranchCanonicality:
    def test_certificate_version(self):
        assert CERTIFICATE.version == "v18.5"

    def test_certificate_pillar(self):
        assert CERTIFICATE.pillar == 541

    def test_certificate_status_label(self):
        assert "NON_CANONICAL_BRANCH_CERTIFIED" in CERTIFICATE.status

    def test_certificate_canonical_r(self):
        assert abs(CERTIFICATE.canonical_r - R_CANONICAL) < 1e-6

    def test_certificate_shadow_r(self):
        assert abs(CERTIFICATE.shadow_r - R_SHADOW) < 1e-6

    def test_certificate_litebird_gap(self):
        assert abs(CERTIFICATE.litebird_gap_deg - 0.058) < 0.001

    def test_certificate_litebird_discriminability(self):
        assert CERTIFICATE.litebird_discriminability_sigma >= 4.0

    def test_certificate_external_reviewer_note(self):
        note = CERTIFICATE.external_reviewer_note
        assert "0.0175" in note
        assert "NOT a Unitary Manifold canonical prediction" in note
        assert "0.0315" in note
        assert "CMB-S4" in note

    def test_certificate_summary_contains_key_values(self):
        s = CERTIFICATE.summary()
        assert "0.0315" in s
        assert "0.0175" in s
        assert "0.331" in s
        assert "0.273" in s

    def test_canonicality_certificate_function(self):
        cert = canonicality_certificate()
        assert isinstance(cert, BranchCanonicality)
        assert cert.pillar == 541

    def test_certificate_canonical_z2_odd(self):
        assert CERTIFICATE.canonical_z2_odd is True

    def test_certificate_shadow_not_z2_odd(self):
        """Shadow sector does not satisfy Z₂-odd — confirmed in certificate."""
        assert "SHADOW_SECTOR" in CERTIFICATE.shadow_epistemic_status

    def test_certificate_canonical_bicep_pass(self):
        assert "PASS" in CERTIFICATE.canonical_bicep_keck_status

    def test_certificate_canonical_act_tension(self):
        assert "HIGH_TENSION" in CERTIFICATE.canonical_act_dr6_status

    def test_certificate_shadow_act_tension(self):
        """Shadow r=0.0175 also above ACT DR6 limit — documented correctly."""
        assert "TENSION" in CERTIFICATE.shadow_act_dr6_status

    def test_certificate_litebird_launch_year(self):
        assert "2032" in CERTIFICATE.litebird_launch


# ──────────────────────────────────────────────────────────────────────────────
# Cross-consistency tests
# ──────────────────────────────────────────────────────────────────────────────

class TestCrossConsistency:
    def test_canonical_r_consistent_with_braided_formula(self):
        """r_canonical from formula = 0.0315 exactly (by construction — R_CANONICAL sets the scale)."""
        r_formula = r_braided_from_pair(5, 7)
        assert abs(r_formula - R_CANONICAL) < 1e-6  # absolute; exact by definition

    def test_shadow_r_consistent_with_braided_formula(self):
        """r_shadow from formula ≈ 0.0175 within 0.5% (relative; R_SHADOW is rounded to 4 d.p.)."""
        r_formula = r_braided_from_pair(5, 6)
        # Relative tolerance because R_SHADOW = 0.0175 is a rounded nominal value;
        # the formula yields 0.0315 × (11/61) / (12/37) ≈ 0.017504... which rounds to 0.0175.
        assert abs(r_formula - R_SHADOW) / R_SHADOW < 0.005

    def test_canonical_ns_tension_consistent(self):
        """Canonical nₛ tension from formula matches CERTIFICATE."""
        sigma = ns_tension_sigma(CERTIFICATE.canonical_ns)
        assert abs(sigma - CERTIFICATE.canonical_ns_tension_sigma) < 0.01

    def test_shadow_ns_tension_consistent(self):
        """Shadow nₛ tension from formula matches CERTIFICATE."""
        sigma = ns_tension_sigma(CERTIFICATE.shadow_ns)
        assert abs(sigma - CERTIFICATE.shadow_ns_tension_sigma) < 0.01

    def test_canonical_ns_better_fit_than_shadow(self):
        """(5,7) nₛ fits Planck better than (5,6) — independent selection pressure."""
        assert CERTIFICATE.canonical_ns_tension_sigma < CERTIFICATE.shadow_ns_tension_sigma

    def test_litebird_gap_equals_beta_difference(self):
        gap = CERTIFICATE.canonical_beta_deg - CERTIFICATE.shadow_beta_deg
        assert abs(gap - CERTIFICATE.litebird_gap_deg) < 1e-6

    def test_three_independent_selection_grounds(self):
        """Verify the three selection mechanisms are all consistent."""
        # 1. Z₂-odd: canonical satisfies, shadow does not
        z2_c = z2_odd_boundary_phase(N1_CANONICAL, N2_CANONICAL)
        z2_s = z2_odd_boundary_phase(N1_SHADOW, N2_SHADOW)
        assert z2_c["is_z2_odd"] and not z2_s["is_z2_odd"]
        # 2. Planck nₛ: canonical closer
        assert ns_tension_sigma(0.9635) < ns_tension_sigma(0.9610)
        # 3. Observational: both pass BICEP; canonical has ACT tension (honest)
        assert R_CANONICAL < 0.036  # BICEP/Keck
        assert R_SHADOW < 0.036
        assert R_CANONICAL > 0.016  # ACT tension is real
