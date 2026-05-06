"""
test_claim.py — Tests validating the mp_me_ratio falsification claim.

Run from the repository root:
    python -m pytest claims/mp_me_ratio/test_claim.py -v
"""
import sys
sys.path.insert(0, ".")

import pytest
from claims.mp_me_ratio.claim import (
    C_LAT_CURRENT,
    FALSIFICATION_CONDITION,
    K_CS,
    KILL_THRESHOLD_PCT,
    MP_ME_GEO,
    MP_ME_PDG,
    MP_ME_RESIDUAL_PCT,
    N_C,
    N_W,
    evaluate_measurement,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────


class TestConstants:
    """Verify the fixed numerical values."""

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_mp_me_geo_formula(self):
        expected = 74 ** 2 / 3.0
        assert abs(MP_ME_GEO - expected) < 1e-9

    def test_mp_me_geo_value(self):
        assert abs(MP_ME_GEO - 1825.333_333) < 1e-3

    def test_mp_me_pdg_value(self):
        assert abs(MP_ME_PDG - 1836.15267) < 1e-5

    def test_residual_pct_approx_0p59(self):
        assert abs(MP_ME_RESIDUAL_PCT - 0.59) < 0.05

    def test_residual_pct_formula(self):
        expected = abs(MP_ME_GEO - MP_ME_PDG) / MP_ME_PDG * 100.0
        assert abs(MP_ME_RESIDUAL_PCT - expected) < 1e-9

    def test_kill_threshold_is_0p1pct(self):
        assert abs(KILL_THRESHOLD_PCT - 0.1) < 1e-9

    def test_c_lat_close_to_unity(self):
        """C_lat should be close to 1 (≈1.006 for 0.59% residual)."""
        assert 1.0 < C_LAT_CURRENT < 1.02

    def test_k_cs_identity_n1_sq_plus_n2_sq(self):
        """K_CS = 5² + 7² is the core algebraic identity."""
        assert K_CS == 5 ** 2 + 7 ** 2

    def test_n_c_equals_ceil_nw_over_2(self):
        import math
        assert N_C == math.ceil(N_W / 2)


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

    def test_prediction_value_matches_constant(self):
        pred = FALSIFICATION_CONDITION["prediction"]
        assert abs(pred["value"] - MP_ME_GEO) < 1e-9

    def test_prediction_is_axiomzero_compliant(self):
        assert FALSIFICATION_CONDITION["prediction"]["axiomzero_compliant"] is True

    def test_kill_threshold_matches_constant(self):
        kt = FALSIFICATION_CONDITION["kill_threshold"]
        assert abs(kt["threshold_pct"] - KILL_THRESHOLD_PCT) < 1e-9

    def test_experimental_target_pdg_correct(self):
        et = FALSIFICATION_CONDITION["experimental_target"]
        assert abs(et["pdg_value"] - MP_ME_PDG) < 1e-5


# ─────────────────────────────────────────────────────────────────────────────
# evaluate_measurement()
# ─────────────────────────────────────────────────────────────────────────────


class TestEvaluateMeasurement:
    """Test the evaluate_measurement() function."""

    def test_pdg_value_with_c_lat_is_consistent(self):
        """PDG value + current C_lat → CONSISTENT (by construction)."""
        result = evaluate_measurement(MP_ME_PDG, c_lat_derived=C_LAT_CURRENT)
        assert result["verdict"] == "CONSISTENT"
        assert result["residual_pct"] < 1e-6

    def test_pure_geo_with_c_lat_1_is_consistent(self):
        """Pure geometric value with C_lat=1.0 → CONSISTENT (residual=0)."""
        result = evaluate_measurement(MP_ME_GEO, c_lat_derived=1.0)
        assert result["verdict"] == "CONSISTENT"
        assert result["residual_pct"] < 1e-9

    def test_1pct_deviation_is_falsified(self):
        """A 1% deviation from the geometric prediction falsifies the claim."""
        mp_me_bad = MP_ME_GEO * 1.01  # 1% shift
        result = evaluate_measurement(mp_me_bad, c_lat_derived=1.0)
        assert result["verdict"] == "FALSIFIED"

    def test_0p05pct_deviation_is_consistent(self):
        """A 0.05% deviation is within the kill threshold."""
        mp_me_close = MP_ME_GEO * 1.0005
        result = evaluate_measurement(mp_me_close, c_lat_derived=1.0)
        assert result["verdict"] == "CONSISTENT"

    def test_0p3pct_deviation_is_tension(self):
        """A 0.3% deviation is between 1× and 5× the kill threshold."""
        mp_me_tension = MP_ME_GEO * 1.003
        result = evaluate_measurement(mp_me_tension, c_lat_derived=1.0)
        assert result["verdict"] == "TENSION"

    def test_residual_is_non_negative(self):
        for ratio in [1800.0, 1825.0, 1836.0, 1850.0]:
            result = evaluate_measurement(ratio)
            assert result["residual_pct"] >= 0.0

    def test_corrected_geo_uses_c_lat(self):
        result = evaluate_measurement(MP_ME_PDG, c_lat_derived=C_LAT_CURRENT)
        expected_geo = MP_ME_GEO * C_LAT_CURRENT
        assert abs(result["corrected_geo"] - expected_geo) < 1e-9

    def test_pure_geo_stored_correctly(self):
        result = evaluate_measurement(MP_ME_PDG)
        assert abs(result["mp_me_geo_pure"] - MP_ME_GEO) < 1e-9
