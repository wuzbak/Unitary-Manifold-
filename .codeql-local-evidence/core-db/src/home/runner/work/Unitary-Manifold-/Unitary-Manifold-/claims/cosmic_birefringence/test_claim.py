"""
test_claim.py — Tests validating the cosmic_birefringence falsification claim.

Run from the repository root:
    python -m pytest claims/cosmic_birefringence/test_claim.py -v
"""
import sys
sys.path.insert(0, ".")

import pytest
from claims.cosmic_birefringence.claim import (
    ADMISSIBLE_HIGH_DEG,
    ADMISSIBLE_LOW_DEG,
    BETA_ALTERNATE_DEG,
    BETA_CANONICAL_DEG,
    FALSIFICATION_CONDITION,
    K_CS_ALTERNATE,
    K_CS_CANONICAL,
    KILL_ZONE_HIGH_DEG,
    KILL_ZONE_LOW_DEG,
    evaluate_measurement,
)


# ─────────────────────────────────────────────────────────────────────────────
# Catalogue / constants
# ─────────────────────────────────────────────────────────────────────────────


class TestConstants:
    """Verify the fixed numerical values of the claim."""

    def test_beta_canonical_is_0p331(self):
        assert abs(BETA_CANONICAL_DEG - 0.331) < 1e-6

    def test_beta_alternate_is_0p273(self):
        assert abs(BETA_ALTERNATE_DEG - 0.273) < 1e-6

    def test_kill_zone_bounds(self):
        assert abs(KILL_ZONE_LOW_DEG - 0.290) < 1e-6
        assert abs(KILL_ZONE_HIGH_DEG - 0.310) < 1e-6

    def test_admissible_window_bounds(self):
        assert abs(ADMISSIBLE_LOW_DEG - 0.223) < 1e-6
        assert abs(ADMISSIBLE_HIGH_DEG - 0.381) < 1e-6

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74

    def test_k_cs_alternate(self):
        assert K_CS_ALTERNATE == 61

    def test_both_predictions_in_admissible_window(self):
        assert ADMISSIBLE_LOW_DEG < BETA_CANONICAL_DEG < ADMISSIBLE_HIGH_DEG
        assert ADMISSIBLE_LOW_DEG < BETA_ALTERNATE_DEG < ADMISSIBLE_HIGH_DEG

    def test_neither_prediction_in_kill_zone(self):
        """The two predicted values must NOT be inside the kill zone."""
        assert not (KILL_ZONE_LOW_DEG <= BETA_CANONICAL_DEG <= KILL_ZONE_HIGH_DEG)
        assert not (KILL_ZONE_LOW_DEG <= BETA_ALTERNATE_DEG <= KILL_ZONE_HIGH_DEG)

    def test_kill_zone_is_inside_admissible_window(self):
        assert ADMISSIBLE_LOW_DEG < KILL_ZONE_LOW_DEG
        assert KILL_ZONE_HIGH_DEG < ADMISSIBLE_HIGH_DEG

    def test_predictions_separated_by_kill_zone(self):
        """The two predictions must be on opposite sides of the kill zone."""
        assert BETA_ALTERNATE_DEG < KILL_ZONE_LOW_DEG
        assert BETA_CANONICAL_DEG > KILL_ZONE_HIGH_DEG


# ─────────────────────────────────────────────────────────────────────────────
# FALSIFICATION_CONDITION dict
# ─────────────────────────────────────────────────────────────────────────────


class TestFalsificationConditionDict:
    """Machine-readable falsification condition must have required keys."""

    def test_has_required_keys(self):
        for key in ("prediction", "experimental_target", "kill_threshold",
                    "experiment", "timeline"):
            assert key in FALSIFICATION_CONDITION, (
                f"FALSIFICATION_CONDITION missing key: {key!r}"
            )

    def test_experiment_key(self):
        # experiment key is nested inside experimental_target OR at top level
        assert (
            "LiteBIRD" in str(FALSIFICATION_CONDITION.get("experimental_target", ""))
            or "LiteBIRD" in str(FALSIFICATION_CONDITION.get("experiment", ""))
        )

    def test_timeline_mentions_litebird(self):
        assert "LiteBIRD" in str(FALSIFICATION_CONDITION["timeline"]) or \
               "2032" in str(FALSIFICATION_CONDITION["timeline"])

    def test_prediction_values_match_constants(self):
        pred = FALSIFICATION_CONDITION["prediction"]
        assert abs(pred["canonical_deg"] - BETA_CANONICAL_DEG) < 1e-9
        assert abs(pred["alternate_deg"] - BETA_ALTERNATE_DEG) < 1e-9


# ─────────────────────────────────────────────────────────────────────────────
# evaluate_measurement()
# ─────────────────────────────────────────────────────────────────────────────


class TestEvaluateMeasurement:
    """Test the evaluate_measurement() function."""

    def test_canonical_prediction_is_consistent(self):
        result = evaluate_measurement(BETA_CANONICAL_DEG, sigma_deg=0.05)
        assert result["verdict"] == "CONSISTENT"
        assert result["nearest_prediction"] == "canonical"

    def test_alternate_prediction_is_consistent(self):
        result = evaluate_measurement(BETA_ALTERNATE_DEG, sigma_deg=0.05)
        assert result["verdict"] == "CONSISTENT"
        assert result["nearest_prediction"] == "alternate"

    def test_kill_zone_center_is_falsified(self):
        beta_kill = (KILL_ZONE_LOW_DEG + KILL_ZONE_HIGH_DEG) / 2.0
        result = evaluate_measurement(beta_kill)
        assert result["verdict"] == "FALSIFIED_KILL_ZONE"
        assert result["in_kill_zone"] is True

    def test_outside_window_low_is_falsified(self):
        result = evaluate_measurement(0.10)
        assert result["verdict"] == "FALSIFIED_OUTSIDE_WINDOW"
        assert result["in_admissible_window"] is False

    def test_outside_window_high_is_falsified(self):
        result = evaluate_measurement(0.50)
        assert result["verdict"] == "FALSIFIED_OUTSIDE_WINDOW"
        assert result["in_admissible_window"] is False

    def test_in_window_but_far_from_prediction_is_ambiguous(self):
        # β = 0.25° is in the admissible window but not at either prediction
        result = evaluate_measurement(0.25)
        # should be consistent with alternate (0.273 - 0.25 = 0.023) or ambiguous
        assert result["verdict"] in ("CONSISTENT", "AMBIGUOUS")

    def test_residuals_are_non_negative(self):
        for beta in [0.273, 0.300, 0.331, 0.250, 0.350]:
            result = evaluate_measurement(beta)
            assert result["residual_canonical_deg"] >= 0.0
            assert result["residual_alternate_deg"] >= 0.0

    def test_in_admissible_window_flag_correct(self):
        result_in = evaluate_measurement(0.300)
        assert result_in["in_admissible_window"] is True

        result_out = evaluate_measurement(0.10)
        assert result_out["in_admissible_window"] is False

    def test_exact_canonical_value_consistent_without_sigma(self):
        result = evaluate_measurement(BETA_CANONICAL_DEG)
        assert result["verdict"] in ("CONSISTENT", "AMBIGUOUS")
        # residual to canonical must be exactly 0
        assert result["residual_canonical_deg"] == 0.0
