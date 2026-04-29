# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_aps_analytic_proof.py
=================================
Test suite for src/core/aps_analytic_proof.py (Pillar 80).

Coverage (~50 tests):
  - TestConstants: module constants exist and have expected values
  - TestTriangularNumber: exact integer values for n_w = 0..10
  - TestTriangularNumberParity: parity patterns for all residues mod 4
  - TestEtaBarFromTriangularParity: η̄ ∈ {0.0, 0.5} for canonical cases
  - TestHolonomyParameter: α ∈ {0.0, 0.5} consistent with η̄
  - TestWindingModeEtaSum: numerical η̄ matches analytic result
  - TestPontryaginNumberRS: p₁ = 0.0 for RS metric
  - TestAhatGenusModule1: ∫ Â mod 1 = 0.0
  - TestCS3FormIntegral: CS₃(n_w) mod 1 reproduces canonical values
  - TestStep3AnalyticTheorem: complete theorem dict for n_w = 5, 7
  - TestStep3UniquenessReport: n_w=5 selected, n_w=7 excluded
  - TestStep3StatusUpgrade: status strings and gap description
"""
from __future__ import annotations

import math
import pytest

from src.core.aps_analytic_proof import (
    N_W_CANONICAL,
    K_CS,
    PHI0,
    PI_KR_CANONICAL,
    ETA_BAR_NW5,
    ETA_BAR_NW7,
    triangular_number,
    triangular_number_parity,
    eta_bar_from_triangular_parity,
    holonomy_parameter,
    winding_mode_eta_sum,
    pontryagin_number_rs_metric,
    ahat_genus_mod1,
    cs_three_form_integral,
    step3_analytic_theorem,
    step3_uniqueness_report,
    step3_status_upgrade,
)


# ---------------------------------------------------------------------------
# TestConstants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi0(self):
        assert PHI0 == 1.0

    def test_pi_kr_canonical(self):
        assert PI_KR_CANONICAL == 37.0

    def test_eta_bar_nw5(self):
        assert ETA_BAR_NW5 == 0.5

    def test_eta_bar_nw7(self):
        assert ETA_BAR_NW7 == 0.0


# ---------------------------------------------------------------------------
# TestTriangularNumber
# ---------------------------------------------------------------------------

class TestTriangularNumber:
    """T(n_w) = n_w*(n_w+1)//2 — exact integers."""

    @pytest.mark.parametrize("n_w,expected", [
        (0, 0),
        (1, 1),
        (2, 3),
        (3, 6),
        (4, 10),
        (5, 15),
        (6, 21),
        (7, 28),
        (8, 36),
        (9, 45),
        (10, 55),
    ])
    def test_exact_values(self, n_w, expected):
        assert triangular_number(n_w) == expected

    def test_returns_int(self):
        assert isinstance(triangular_number(5), int)

    def test_zero(self):
        assert triangular_number(0) == 0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            triangular_number(-1)

    def test_large_value(self):
        # T(100) = 5050
        assert triangular_number(100) == 5050


# ---------------------------------------------------------------------------
# TestTriangularNumberParity
# ---------------------------------------------------------------------------

class TestTriangularNumberParity:
    """T(n_w) mod 2: odd iff n_w ≡ 1 or 2 (mod 4)."""

    @pytest.mark.parametrize("n_w,expected_parity", [
        (0, 0),   # T=0 even
        (1, 1),   # T=1 odd
        (2, 1),   # T=3 odd
        (3, 0),   # T=6 even
        (4, 0),   # T=10 even
        (5, 1),   # T=15 odd
        (6, 1),   # T=21 odd
        (7, 0),   # T=28 even
        (8, 0),   # T=36 even
        (9, 1),   # T=45 odd
        (10, 1),  # T=55 odd
        (11, 0),  # T=66 even
        (12, 0),  # T=78 even
    ])
    def test_parity_values(self, n_w, expected_parity):
        assert triangular_number_parity(n_w) == expected_parity

    def test_returns_int_0_or_1(self):
        for n_w in range(20):
            p = triangular_number_parity(n_w)
            assert p in (0, 1)

    def test_consistent_with_triangular_number(self):
        for n_w in range(30):
            assert triangular_number_parity(n_w) == triangular_number(n_w) % 2

    def test_period_4(self):
        """Parity is periodic with period 4: (1,1,0,0) starting at n_w=1."""
        pattern = [triangular_number_parity(n_w) for n_w in range(1, 5)]
        assert pattern == [1, 1, 0, 0]
        for offset in range(0, 20, 4):
            for k in range(4):
                assert triangular_number_parity(1 + offset + k) == pattern[k]


# ---------------------------------------------------------------------------
# TestEtaBarFromTriangularParity
# ---------------------------------------------------------------------------

class TestEtaBarFromTriangularParity:
    """η̄ ∈ {0.0, 0.5} from triangular parity."""

    def test_nw5_half(self):
        assert eta_bar_from_triangular_parity(5) == pytest.approx(0.5, abs=1e-12)

    def test_nw7_zero(self):
        assert eta_bar_from_triangular_parity(7) == pytest.approx(0.0, abs=1e-12)

    def test_nw1_half(self):
        assert eta_bar_from_triangular_parity(1) == pytest.approx(0.5, abs=1e-12)

    def test_nw3_zero(self):
        assert eta_bar_from_triangular_parity(3) == pytest.approx(0.0, abs=1e-12)

    def test_nw0_zero(self):
        assert eta_bar_from_triangular_parity(0) == pytest.approx(0.0, abs=1e-12)

    def test_nw2_half(self):
        # T(2) = 3 (odd) → η̄ = 0.5
        assert eta_bar_from_triangular_parity(2) == pytest.approx(0.5, abs=1e-12)

    def test_nw4_zero(self):
        # T(4) = 10 (even) → η̄ = 0.0
        assert eta_bar_from_triangular_parity(4) == pytest.approx(0.0, abs=1e-12)

    def test_returns_float(self):
        assert isinstance(eta_bar_from_triangular_parity(5), float)

    def test_range_zero_to_half(self):
        for n_w in range(20):
            eta = eta_bar_from_triangular_parity(n_w)
            assert eta in (0.0, 0.5)


# ---------------------------------------------------------------------------
# TestHolonomyParameter
# ---------------------------------------------------------------------------

class TestHolonomyParameter:
    """α ∈ {0.0, 0.5}; α = 0 when T(n_w) odd (zero mode present)."""

    def test_nw5_alpha_zero(self):
        # T(5) = 15 odd → zero mode present → α = 0
        assert holonomy_parameter(5) == pytest.approx(0.0, abs=1e-12)

    def test_nw7_alpha_half(self):
        # T(7) = 28 even → no zero mode → α = 0.5
        assert holonomy_parameter(7) == pytest.approx(0.5, abs=1e-12)

    def test_nw1_alpha_zero(self):
        assert holonomy_parameter(1) == pytest.approx(0.0, abs=1e-12)

    def test_nw3_alpha_half(self):
        assert holonomy_parameter(3) == pytest.approx(0.5, abs=1e-12)

    def test_returns_float(self):
        assert isinstance(holonomy_parameter(5), float)

    def test_range_zero_or_half(self):
        for n_w in range(15):
            alpha = holonomy_parameter(n_w)
            assert alpha in (0.0, 0.5)

    def test_anti_correlated_with_eta_bar(self):
        """α = 0 ↔ η̄ = 0.5; α = 0.5 ↔ η̄ = 0."""
        for n_w in range(15):
            alpha = holonomy_parameter(n_w)
            eta = eta_bar_from_triangular_parity(n_w)
            assert abs(alpha + eta - 0.5) < 1e-12


# ---------------------------------------------------------------------------
# TestWindingModeEtaSum
# ---------------------------------------------------------------------------

class TestWindingModeEtaSum:
    """Numerical η̄ from Dirac mode sum matches analytic result."""

    def test_nw5_gives_half(self):
        assert winding_mode_eta_sum(5) == pytest.approx(0.5, abs=1e-12)

    def test_nw7_gives_zero(self):
        assert winding_mode_eta_sum(7) == pytest.approx(0.0, abs=1e-12)

    def test_nw1_gives_half(self):
        assert winding_mode_eta_sum(1) == pytest.approx(0.5, abs=1e-12)

    def test_nw3_gives_zero(self):
        assert winding_mode_eta_sum(3) == pytest.approx(0.0, abs=1e-12)

    def test_matches_analytic_for_range(self):
        for n_w in range(10):
            numerical = winding_mode_eta_sum(n_w)
            analytic = eta_bar_from_triangular_parity(n_w)
            assert numerical == pytest.approx(analytic, abs=1e-12)

    def test_n_modes_parameter(self):
        # Result should be the same for different n_modes
        assert winding_mode_eta_sum(5, n_modes=50) == pytest.approx(
            winding_mode_eta_sum(5, n_modes=200), abs=1e-12
        )


# ---------------------------------------------------------------------------
# TestPontryaginNumberRS
# ---------------------------------------------------------------------------

class TestPontryaginNumberRS:
    """p₁ = 0 for RS warped product metric (Theorem 3)."""

    def test_default_returns_zero(self):
        assert pontryagin_number_rs_metric() == pytest.approx(0.0, abs=1e-12)

    def test_custom_parameters_still_zero(self):
        assert pontryagin_number_rs_metric(k_eff=2.0, R_KK=5.0) == pytest.approx(
            0.0, abs=1e-12
        )

    def test_returns_float(self):
        assert isinstance(pontryagin_number_rs_metric(), float)


# ---------------------------------------------------------------------------
# TestAhatGenusModule1
# ---------------------------------------------------------------------------

class TestAhatGenusModule1:
    """∫ Â mod 1 = 0.0 by Theorem 3."""

    def test_nw5_returns_zero(self):
        assert ahat_genus_mod1(5) == pytest.approx(0.0, abs=1e-12)

    def test_nw7_returns_zero(self):
        assert ahat_genus_mod1(7) == pytest.approx(0.0, abs=1e-12)

    def test_always_zero(self):
        for n_w in range(10):
            assert ahat_genus_mod1(n_w) == pytest.approx(0.0, abs=1e-12)

    def test_returns_float(self):
        assert isinstance(ahat_genus_mod1(5), float)


# ---------------------------------------------------------------------------
# TestCS3FormIntegral
# ---------------------------------------------------------------------------

class TestCS3FormIntegral:
    """CS₃(n_w) = T(n_w)/2 mod 1."""

    def test_nw5_half(self):
        # T(5) = 15 → 15/2 = 7.5 → mod 1 = 0.5
        assert cs_three_form_integral(5) == pytest.approx(0.5, abs=1e-12)

    def test_nw7_zero(self):
        # T(7) = 28 → 28/2 = 14.0 → mod 1 = 0.0
        assert cs_three_form_integral(7) == pytest.approx(0.0, abs=1e-12)

    def test_nw1_half(self):
        # T(1) = 1 → 0.5 → mod 1 = 0.5
        assert cs_three_form_integral(1) == pytest.approx(0.5, abs=1e-12)

    def test_nw3_zero(self):
        # T(3) = 6 → 3.0 → mod 1 = 0.0
        assert cs_three_form_integral(3) == pytest.approx(0.0, abs=1e-12)

    def test_nw0_zero(self):
        # T(0) = 0 → 0.0
        assert cs_three_form_integral(0) == pytest.approx(0.0, abs=1e-12)

    def test_matches_eta_bar(self):
        """CS₃ mod 1 should equal η̄."""
        for n_w in range(15):
            cs3 = cs_three_form_integral(n_w)
            eta = eta_bar_from_triangular_parity(n_w)
            assert cs3 == pytest.approx(eta, abs=1e-12)

    def test_range_zero_to_one(self):
        for n_w in range(15):
            cs3 = cs_three_form_integral(n_w)
            assert 0.0 <= cs3 < 1.0


# ---------------------------------------------------------------------------
# TestStep3AnalyticTheorem
# ---------------------------------------------------------------------------

class TestStep3AnalyticTheorem:
    """Full theorem dict for canonical winding numbers."""

    def setup_method(self):
        self.r5 = step3_analytic_theorem(5)
        self.r7 = step3_analytic_theorem(7)

    def test_nw5_keys_present(self):
        keys = [
            "n_w", "T_nw", "T_nw_parity", "eta_bar_exact",
            "eta_bar_winding_sum", "cs3_mod1", "p1_rs", "ahat_mod1",
            "selected_by_geometry", "proof_status", "remaining_gap",
        ]
        for k in keys:
            assert k in self.r5

    def test_nw5_T(self):
        assert self.r5["T_nw"] == 15

    def test_nw5_parity(self):
        assert self.r5["T_nw_parity"] == 1

    def test_nw5_eta_exact(self):
        assert self.r5["eta_bar_exact"] == pytest.approx(0.5, abs=1e-12)

    def test_nw5_eta_winding_sum(self):
        assert self.r5["eta_bar_winding_sum"] == pytest.approx(0.5, abs=1e-12)

    def test_nw5_cs3(self):
        assert self.r5["cs3_mod1"] == pytest.approx(0.5, abs=1e-12)

    def test_nw5_p1(self):
        assert self.r5["p1_rs"] == pytest.approx(0.0, abs=1e-12)

    def test_nw5_ahat(self):
        assert self.r5["ahat_mod1"] == pytest.approx(0.0, abs=1e-12)

    def test_nw5_selected_by_geometry(self):
        assert self.r5["selected_by_geometry"] is True

    def test_nw5_proof_status(self):
        assert self.r5["proof_status"] == "TOPOLOGICALLY PROVED"

    def test_nw5_remaining_gap_nonempty(self):
        assert len(self.r5["remaining_gap"]) > 10

    # n_w = 7 tests
    def test_nw7_T(self):
        assert self.r7["T_nw"] == 28

    def test_nw7_parity(self):
        assert self.r7["T_nw_parity"] == 0

    def test_nw7_eta_exact(self):
        assert self.r7["eta_bar_exact"] == pytest.approx(0.0, abs=1e-12)

    def test_nw7_selected_false(self):
        assert self.r7["selected_by_geometry"] is False

    def test_nw7_proof_status(self):
        assert self.r7["proof_status"] == "TOPOLOGICALLY EXCLUDED"


# ---------------------------------------------------------------------------
# TestStep3UniquenessReport
# ---------------------------------------------------------------------------

class TestStep3UniquenessReport:
    def setup_method(self):
        self.report = step3_uniqueness_report()

    def test_keys_present(self):
        for k in ["n_w_selected", "n_w_excluded", "eta_bar_5", "eta_bar_7",
                  "T_5", "T_7", "selection_criterion", "previous_status",
                  "new_status", "remaining_gap", "theorem_applied"]:
            assert k in self.report

    def test_nw5_selected(self):
        assert self.report["n_w_selected"] == 5

    def test_nw7_excluded(self):
        assert self.report["n_w_excluded"] == 7

    def test_eta_bar_5(self):
        assert self.report["eta_bar_5"] == pytest.approx(0.5, abs=1e-12)

    def test_eta_bar_7(self):
        assert self.report["eta_bar_7"] == pytest.approx(0.0, abs=1e-12)

    def test_T_5(self):
        assert self.report["T_5"] == 15

    def test_T_7(self):
        assert self.report["T_7"] == 28

    def test_previous_status_string(self):
        assert "PHYSICALLY-MOTIVATED" in self.report["previous_status"]

    def test_new_status_string(self):
        assert "TOPOLOGICALLY DERIVED" in self.report["new_status"]

    def test_remaining_gap_mentions_vacuum(self):
        assert "VACUUM" in self.report["remaining_gap"].upper() or \
               "vacuum" in self.report["remaining_gap"]

    def test_proof_status_5_selected(self):
        assert "PROVED" in self.report["proof_status_5"]

    def test_proof_status_7_excluded(self):
        assert "EXCLUDED" in self.report["proof_status_7"]


# ---------------------------------------------------------------------------
# TestStep3StatusUpgrade
# ---------------------------------------------------------------------------

class TestStep3StatusUpgrade:
    def setup_method(self):
        self.upgrade = step3_status_upgrade()

    def test_keys_present(self):
        for k in ["pillar", "title", "previous_status", "new_status",
                  "mechanism", "key_identity", "n_w_5_result", "n_w_7_result",
                  "remaining_gap", "future_direction"]:
            assert k in self.upgrade

    def test_pillar_number(self):
        assert self.upgrade["pillar"] == 80

    def test_previous_status_physically_motivated(self):
        assert "PHYSICALLY-MOTIVATED" in self.upgrade["previous_status"]

    def test_new_status_topologically_derived(self):
        assert "TOPOLOGICALLY DERIVED" in self.upgrade["new_status"]

    def test_key_identity_contains_T(self):
        assert "T" in self.upgrade["key_identity"] or "η̄" in self.upgrade["key_identity"]

    def test_nw5_result_is_dict(self):
        assert isinstance(self.upgrade["n_w_5_result"], dict)

    def test_nw7_result_is_dict(self):
        assert isinstance(self.upgrade["n_w_7_result"], dict)

    def test_nw5_selected_in_result(self):
        assert self.upgrade["n_w_5_result"]["selected_by_geometry"] is True

    def test_nw7_excluded_in_result(self):
        assert self.upgrade["n_w_7_result"]["selected_by_geometry"] is False

    def test_remaining_gap_nonempty(self):
        assert len(self.upgrade["remaining_gap"]) > 20

    def test_future_direction_nonempty(self):
        assert len(self.upgrade["future_direction"]) > 20
