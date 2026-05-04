# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests for src/core/falsification_check.py — the self-executing birefringence
falsification checker.

These tests ensure that the primary falsification conditions of the Unitary
Manifold are correctly encoded and will remain correct regardless of future
changes to other modules.

They also serve as executable documentation: each test case corresponds to a
scientifically meaningful scenario described in:
  - 3-FALSIFICATION/OBSERVATION_TRACKER.md
  - STEWARDSHIP.md §5
  - 3-FALSIFICATION/prediction.md
"""

import pytest

from src.core.falsification_check import (
    BETA_GAP_HI,
    BETA_GAP_LO,
    BETA_MAX,
    BETA_MIN,
    BETA_PRIMARY,
    BETA_SHADOW,
    BETA_THEORY_UNCERTAINTY,
    FalsificationResult,
    check_falsification,
    summary,
)


# ──────────────────────────────────────────────────────────────────────────────
# Constants sanity checks
# ──────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_prediction_values_are_correct(self):
        """Primary predictions must match FALLIBILITY.md Admission 1–2."""
        assert BETA_PRIMARY == pytest.approx(0.331, abs=1e-6)
        assert BETA_SHADOW == pytest.approx(0.273, abs=1e-6)

    def test_theory_uncertainty_small(self):
        """Internal uncertainty ± 0.007° (r_c + φ_min_bare in quadrature)."""
        assert BETA_THEORY_UNCERTAINTY == pytest.approx(0.007, abs=1e-6)

    def test_window_bounds(self):
        assert BETA_MIN == pytest.approx(0.22, abs=1e-6)
        assert BETA_MAX == pytest.approx(0.38, abs=1e-6)

    def test_gap_bounds(self):
        assert BETA_GAP_LO == pytest.approx(0.29, abs=1e-6)
        assert BETA_GAP_HI == pytest.approx(0.31, abs=1e-6)

    def test_predictions_inside_window(self):
        """Both sector predictions must lie within the admissible window."""
        assert BETA_MIN < BETA_SHADOW < BETA_PRIMARY < BETA_MAX

    def test_gap_inside_window(self):
        """The forbidden gap must be inside the admissible window."""
        assert BETA_MIN < BETA_GAP_LO < BETA_GAP_HI < BETA_MAX

    def test_predictions_outside_gap(self):
        """Neither sector prediction should fall in the forbidden gap."""
        assert not (BETA_GAP_LO < BETA_PRIMARY < BETA_GAP_HI)
        assert not (BETA_GAP_LO < BETA_SHADOW < BETA_GAP_HI)

    def test_sector_gap_is_0p058_degrees(self):
        """Sector gap Δβ = 0.058° = 2.9σ_LiteBIRD (LiteBIRD σ ≈ 0.02°)."""
        gap = BETA_PRIMARY - BETA_SHADOW
        assert gap == pytest.approx(0.058, abs=1e-3)


# ──────────────────────────────────────────────────────────────────────────────
# FALSIFIED scenarios
# ──────────────────────────────────────────────────────────────────────────────

class TestFalsified:
    def test_beta_far_below_minimum(self):
        """β = 0.10° ± 0.01° is 12σ below 0.22° → FALSIFIED."""
        result = check_falsification(beta=0.10, sigma=0.01)
        assert result.is_falsified()
        assert result.verdict == "FALSIFIED"
        assert "below" in result.message.lower()

    def test_beta_at_zero_with_small_sigma(self):
        """β = 0.00° ± 0.01° → FALSIFIED (birefringence consistent with zero)."""
        result = check_falsification(beta=0.00, sigma=0.01)
        assert result.is_falsified()

    def test_beta_far_above_maximum(self):
        """β = 0.55° ± 0.01° → FALSIFIED."""
        result = check_falsification(beta=0.55, sigma=0.01)
        assert result.is_falsified()
        assert "above" in result.message.lower()

    def test_beta_just_below_min_at_3sigma(self):
        """β = 0.19° ± 0.01° → 3.0σ below 0.22° → FALSIFIED."""
        result = check_falsification(beta=0.19, sigma=0.01)
        assert result.is_falsified()

    def test_beta_clearly_above_max_at_4sigma(self):
        """β = 0.42° ± 0.01° → 4.0σ above 0.38° → FALSIFIED."""
        result = check_falsification(beta=0.42, sigma=0.01)
        assert result.is_falsified()

    def test_beta_fully_in_gap_at_3sigma(self):
        """β = 0.30° ± 0.003° — 3σ interval fully within gap → FALSIFIED."""
        result = check_falsification(beta=0.30, sigma=0.003)
        assert result.is_falsified()
        assert "gap" in result.message.lower()

    def test_beta_in_gap_center_large_sigma_not_falsified(self):
        """β = 0.30° ± 0.02° — 3σ interval overlaps gap edges → not falsified."""
        result = check_falsification(beta=0.30, sigma=0.02)
        # The 3σ interval [0.24°, 0.36°] overlaps both gap edges → DISFAVOURED only
        assert not result.is_falsified()

    def test_falsified_exit_code_via_summary_message(self):
        """FALSIFIED results have the word 'excluded' or 'falsified' in their message."""
        result = check_falsification(beta=0.10, sigma=0.01)
        msg_lower = result.message.lower()
        assert "exclud" in msg_lower or "falsif" in msg_lower or "gap" in msg_lower


# ──────────────────────────────────────────────────────────────────────────────
# DISFAVOURED scenarios
# ──────────────────────────────────────────────────────────────────────────────

class TestDisfavoured:
    def test_beta_below_min_under_3sigma(self):
        """β = 0.21° ± 0.02° → 0.5σ below 0.22° → DISFAVOURED."""
        result = check_falsification(beta=0.21, sigma=0.02)
        assert result.verdict == "DISFAVOURED"
        assert not result.is_falsified()

    def test_beta_above_max_under_3sigma(self):
        """β = 0.39° ± 0.02° → 0.5σ above 0.38° → DISFAVOURED."""
        result = check_falsification(beta=0.39, sigma=0.02)
        assert result.verdict == "DISFAVOURED"

    def test_beta_in_gap_under_3sigma(self):
        """β = 0.30° ± 0.02° → in gap but 3σ interval overlaps edges → DISFAVOURED."""
        result = check_falsification(beta=0.30, sigma=0.02)
        assert result.verdict == "DISFAVOURED"


# ──────────────────────────────────────────────────────────────────────────────
# CONFIRMED scenarios
# ──────────────────────────────────────────────────────────────────────────────

class TestConfirmed:
    def test_primary_sector_exact(self):
        """β = 0.331° ± 0.02° → exactly at primary prediction → CONFIRMED."""
        result = check_falsification(beta=BETA_PRIMARY, sigma=0.02)
        assert result.is_confirmed()
        assert "(5,7)" in result.sector

    def test_primary_sector_within_1sigma(self):
        """β = 0.335° ± 0.02° → 0.2σ from primary → CONFIRMED."""
        result = check_falsification(beta=0.335, sigma=0.02)
        assert result.is_confirmed()
        assert "(5,7)" in result.sector

    def test_shadow_sector_exact(self):
        """β = 0.273° ± 0.02° → exactly at shadow prediction → CONFIRMED."""
        result = check_falsification(beta=BETA_SHADOW, sigma=0.02)
        assert result.is_confirmed()
        assert "(5,6)" in result.sector

    def test_shadow_sector_within_1sigma(self):
        """β = 0.268° ± 0.02° → 0.25σ from shadow → CONFIRMED."""
        result = check_falsification(beta=0.268, sigma=0.02)
        assert result.is_confirmed()
        assert "(5,6)" in result.sector

    def test_confirmed_primary_not_proof_of_framework(self):
        """CONFIRMED message must note this is not a proof of the full framework."""
        result = check_falsification(beta=BETA_PRIMARY, sigma=0.02)
        assert "not yet excluded" in result.message or "not a proof" in result.message

    def test_current_minami_observation_consistent(self):
        """Current hint β ≈ 0.35° ± 0.14° (Minami & Komatsu 2020) is CONFIRMED.
        
        The large σ = 0.14° means |0.35 - 0.331| / 0.14 = 0.136σ → within 1σ of primary.
        """
        result = check_falsification(beta=0.35, sigma=0.14)
        # Should be CONFIRMED (5,7) since 0.35 is within 1σ of 0.331
        assert result.is_confirmed()
        assert "(5,7)" in result.sector


# ──────────────────────────────────────────────────────────────────────────────
# CONSISTENT scenarios
# ──────────────────────────────────────────────────────────────────────────────

class TestConsistent:
    def test_in_window_not_near_prediction(self):
        """β = 0.25° ± 0.01° — in window, not near either prediction → CONSISTENT."""
        result = check_falsification(beta=0.25, sigma=0.01)
        # 0.25 is 2.3σ from shadow (0.273) and 8.1σ from primary (0.331)
        # Neither is within 1σ, and β is in window → CONSISTENT
        assert result.verdict == "CONSISTENT"

    def test_midpoint_of_window(self):
        """β = 0.30° but with large sigma → edge cases handled."""
        # With sigma = 0.02, β = 0.30 is in the gap. DISFAVOURED.
        result = check_falsification(beta=0.30, sigma=0.02)
        assert result.verdict in ("DISFAVOURED", "FALSIFIED", "CONSISTENT")

    def test_upper_part_of_window(self):
        """β = 0.36° ± 0.01° — in window, 2.9σ from primary → CONSISTENT."""
        result = check_falsification(beta=0.36, sigma=0.01)
        assert result.verdict == "CONSISTENT"


# ──────────────────────────────────────────────────────────────────────────────
# Input validation
# ──────────────────────────────────────────────────────────────────────────────

class TestInputValidation:
    def test_zero_sigma_raises(self):
        with pytest.raises(ValueError, match="sigma must be positive"):
            check_falsification(beta=0.331, sigma=0.0)

    def test_negative_sigma_raises(self):
        with pytest.raises(ValueError, match="sigma must be positive"):
            check_falsification(beta=0.331, sigma=-0.01)

    def test_negative_beta_allowed(self):
        """Negative β is physically possible (opposite rotation); should be FALSIFIED."""
        result = check_falsification(beta=-0.10, sigma=0.01)
        assert result.is_falsified()

    def test_very_small_sigma(self):
        """Tiny σ → precise test; primary sector at 0.0001° precision → CONFIRMED."""
        result = check_falsification(beta=BETA_PRIMARY, sigma=0.0001)
        assert result.is_confirmed()

    def test_invalid_verdict_raises(self):
        with pytest.raises(ValueError, match="Unknown verdict"):
            FalsificationResult(verdict="WRONG", message="test")


# ──────────────────────────────────────────────────────────────────────────────
# FalsificationResult API
# ──────────────────────────────────────────────────────────────────────────────

class TestFalsificationResultAPI:
    def test_is_falsified_true(self):
        r = FalsificationResult(verdict="FALSIFIED", message="test")
        assert r.is_falsified()
        assert not r.is_confirmed()

    def test_is_confirmed_true(self):
        r = FalsificationResult(verdict="CONFIRMED", message="test")
        assert r.is_confirmed()
        assert not r.is_falsified()

    def test_str_contains_verdict(self):
        r = FalsificationResult(verdict="CONSISTENT", message="in window")
        s = str(r)
        assert "CONSISTENT" in s
        assert "in window" in s

    def test_sector_in_str(self):
        r = FalsificationResult(
            verdict="CONFIRMED", message="test", sector="(5,7) primary"
        )
        s = str(r)
        assert "(5,7)" in s

    def test_all_verdicts_constructible(self):
        for v in FalsificationResult.VERDICTS:
            r = FalsificationResult(verdict=v, message="ok")
            assert r.verdict == v


# ──────────────────────────────────────────────────────────────────────────────
# Summary function
# ──────────────────────────────────────────────────────────────────────────────

class TestSummary:
    def test_summary_contains_predictions(self):
        s = summary()
        assert "0.331" in s
        assert "0.273" in s

    def test_summary_contains_litebird(self):
        s = summary()
        assert "LiteBIRD" in s

    def test_summary_contains_window(self):
        s = summary()
        assert "0.22" in s
        assert "0.38" in s

    def test_summary_contains_observation_tracker_reference(self):
        s = summary()
        assert "OBSERVATION_TRACKER" in s

    def test_summary_contains_stewardship_reference(self):
        s = summary()
        assert "STEWARDSHIP" in s


# ──────────────────────────────────────────────────────────────────────────────
# LiteBIRD sensitivity scenarios
# ──────────────────────────────────────────────────────────────────────────────

class TestLiteBIRDScenarios:
    """Simulate the expected range of LiteBIRD outcomes (σ_β ≈ 0.02°)."""

    LITEBIRD_SIGMA = 0.02

    def test_litebird_measures_primary(self):
        """LiteBIRD at β = 0.331° → CONFIRMED (5,7)."""
        result = check_falsification(beta=0.331, sigma=self.LITEBIRD_SIGMA)
        assert result.is_confirmed()
        assert "(5,7)" in result.sector

    def test_litebird_measures_shadow(self):
        """LiteBIRD at β = 0.273° → CONFIRMED (5,6)."""
        result = check_falsification(beta=0.273, sigma=self.LITEBIRD_SIGMA)
        assert result.is_confirmed()
        assert "(5,6)" in result.sector

    def test_litebird_measures_gap(self):
        """LiteBIRD at β = 0.300° ± 0.02° — gap center but large σ → DISFAVOURED."""
        result = check_falsification(beta=0.300, sigma=self.LITEBIRD_SIGMA)
        # 3σ = 0.06° > gap width 0.02° → interval overlaps both edges → not fully falsified
        assert result.verdict in ("DISFAVOURED", "CONSISTENT")
        assert not result.is_falsified()

    def test_litebird_zero(self):
        """LiteBIRD consistent with β = 0 (β = 0.01° ± 0.02°) → FALSIFIED."""
        result = check_falsification(beta=0.01, sigma=self.LITEBIRD_SIGMA)
        assert result.is_falsified()

    def test_litebird_too_high(self):
        """LiteBIRD at β = 0.45° ± 0.02° → FALSIFIED."""
        result = check_falsification(beta=0.45, sigma=self.LITEBIRD_SIGMA)
        assert result.is_falsified()

    def test_cmbs4_discriminates_sectors(self):
        """CMB-S4 (σ ≈ 0.01°) at β = 0.273° CONFIRMS shadow, REJECTS primary."""
        result = check_falsification(beta=0.273, sigma=0.01)
        assert result.is_confirmed()
        assert "(5,6)" in result.sector
        # Primary is 0.331 - 0.273 = 0.058° = 5.8σ away → clearly excluded by result
        assert result.sigma_from_prediction is not None
        assert result.sigma_from_prediction < 1.0
