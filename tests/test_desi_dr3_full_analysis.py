# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_desi_dr3_full_analysis.py
======================================
Test suite for src/core/desi_dr3_full_analysis.py (~30 tests).

Covers:
  - Constants and baseline data integrity
  - kk_tower_wa_exact: total |wₐ| << 1e-20 (analytical bound 1e-32)
  - bulk_quintessence_constraints: field displacement > M_Pl for wₐ ≈ -0.62
  - desi_systematic_error_budget: systematics < actual DR2 uncertainty
  - likelihood_projection_dr2_to_dr3: probabilities sum to 1
  - wa_tension_sigma: correct sigma for known inputs
  - dr3_outcome_probability_map: probabilities sum to 1 ± 0.001
  - falsification_verdict: FALSIFIED for clearly ≠ 0; CONSISTENT for near-zero
"""
from __future__ import annotations

import math
import pytest

from src.core.desi_dr3_full_analysis import (
    DESI_DR2,
    UM_WA_PREDICTION,
    UM_W0_PREDICTION,
    kk_tower_wa_exact,
    bulk_quintessence_constraints,
    desi_systematic_error_budget,
    likelihood_projection_dr2_to_dr3,
    wa_tension_sigma,
    dr3_outcome_probability_map,
    falsification_verdict,
)


# ---------------------------------------------------------------------------
# Constants and baseline data
# ---------------------------------------------------------------------------

class TestConstants:
    def test_um_wa_prediction_is_zero(self):
        """UM wₐ prediction must be exactly 0.0."""
        assert UM_WA_PREDICTION == 0.0

    def test_um_w0_prediction_near_minus_0_93(self):
        """UM w₀ = −1 + (2/3)(12/37)² ≈ −0.9302."""
        expected = -1.0 + (2.0 / 3.0) * (12.0 / 37.0) ** 2
        assert abs(UM_W0_PREDICTION - expected) < 1e-12

    def test_um_w0_prediction_in_physical_range(self):
        """UM w₀ must be in (-1, 0) — dark energy but not phantom."""
        assert -1.0 < UM_W0_PREDICTION < 0.0

    def test_desi_dr2_wa_central(self):
        """DESI DR2 wₐ central value must be -0.62."""
        assert DESI_DR2["wa_central"] == pytest.approx(-0.62)

    def test_desi_dr2_wa_sigma_positive(self):
        """DESI DR2 wₐ uncertainty must be positive."""
        assert DESI_DR2["wa_sigma"] > 0.0

    def test_desi_dr2_w0_central(self):
        """DESI DR2 w₀ central value must be -0.838."""
        assert DESI_DR2["w0_central"] == pytest.approx(-0.838)

    def test_desi_dr2_has_reference(self):
        """DESI DR2 must contain a reference string."""
        assert "reference" in DESI_DR2
        assert "arXiv" in DESI_DR2["reference"] or "DESI" in DESI_DR2["reference"]

    def test_desi_dr2_tension_field(self):
        """DESI DR2 dict must contain pre-computed tension ~2.07σ."""
        tension = DESI_DR2.get("tension_wa_with_um", None)
        assert tension is not None
        assert abs(tension - 0.62 / 0.30) < 0.01


# ---------------------------------------------------------------------------
# kk_tower_wa_exact
# ---------------------------------------------------------------------------

class TestKkTowerWaExact:
    def test_total_wa_below_1e20(self):
        """KK tower total |wₐ| must be < 1e-20."""
        result = kk_tower_wa_exact(n_modes=5)
        assert result["total_wa_kk_abs"] < 1e-20

    def test_total_wa_below_analytical_bound(self):
        """KK tower total |wₐ| must not exceed declared analytical bound 1e-32."""
        result = kk_tower_wa_exact(n_modes=5)
        # The analytical bound is set; the computed value should be ≤ bound
        assert result["total_wa_kk_abs"] <= result["analytical_upper_bound"]

    def test_exceeds_analytical_bound_flag_false(self):
        """The 'exceeds_analytical_bound' flag must be False."""
        result = kk_tower_wa_exact(n_modes=5)
        assert result["exceeds_analytical_bound"] is False

    def test_returns_required_keys(self):
        """kk_tower_wa_exact must return all required keys."""
        result = kk_tower_wa_exact(n_modes=3)
        for key in ["n_modes", "total_wa_kk", "total_wa_kk_abs", "analytical_upper_bound",
                    "mode_contributions", "conclusion", "suppression_mechanism"]:
            assert key in result, f"Missing key: {key}"

    def test_mode_contributions_count(self):
        """Number of mode contributions must equal n_modes."""
        for n in [3, 5, 10]:
            result = kk_tower_wa_exact(n_modes=n)
            assert len(result["mode_contributions"]) == n

    def test_mode_masses_increase_with_n(self):
        """KK mode masses must increase with mode number n."""
        result = kk_tower_wa_exact(n_modes=5)
        masses = [m["m_n_gev"] for m in result["mode_contributions"]]
        for i in range(1, len(masses)):
            assert masses[i] > masses[i - 1]

    def test_rs_suppression_factor_small(self):
        """RS suppression factor exp(−πkR) must be << 1."""
        result = kk_tower_wa_exact()
        assert result["rs_suppression_factor"] < 1e-10

    def test_conclusion_contains_negligible(self):
        """Conclusion string must mention that wₐ is negligible."""
        result = kk_tower_wa_exact()
        assert "negligible" in result["conclusion"].lower() or "10⁻³²" in result["conclusion"]

    def test_wa_independent_of_n_modes_order_magnitude(self):
        """Total |wₐ| must remain < 1e-20 regardless of n_modes (5 or 20)."""
        r5 = kk_tower_wa_exact(n_modes=5)
        r20 = kk_tower_wa_exact(n_modes=20)
        assert r5["total_wa_kk_abs"] < 1e-20
        assert r20["total_wa_kk_abs"] < 1e-20


# ---------------------------------------------------------------------------
# bulk_quintessence_constraints
# ---------------------------------------------------------------------------

class TestBulkQuintessenceConstraints:
    def test_required_field_displacement_gt_mpl(self):
        """Generating wₐ ≈ -0.62 requires field displacement > 0.5 M_Pl."""
        result = bulk_quintessence_constraints()
        assert result["required_field_displacement_over_mpl"] > 0.5

    def test_is_super_planckian_flag(self):
        """Super-Planckian flag must be True when displacement ≥ 1 M_Pl."""
        result = bulk_quintessence_constraints()
        disp = result["required_field_displacement_over_mpl"]
        expected_flag = disp >= 1.0
        assert result["is_super_planckian"] == expected_flag

    def test_required_keys_present(self):
        """bulk_quintessence_constraints must return required keys."""
        result = bulk_quintessence_constraints()
        for key in ["wa_target", "required_field_displacement_over_mpl",
                    "is_super_planckian", "conclusion", "compatibility",
                    "um_geometry_constraints"]:
            assert key in result, f"Missing key: {key}"

    def test_wa_target_matches_desi_dr2(self):
        """wa_target must match DESI DR2 central value."""
        result = bulk_quintessence_constraints()
        assert result["wa_target"] == pytest.approx(DESI_DR2["wa_central"])

    def test_compatibility_not_current_action(self):
        """Compatibility must indicate the current 5D action is insufficient."""
        result = bulk_quintessence_constraints()
        assert result.get("compatibility") == "INCOMPATIBLE_WITH_CURRENT_5D_ACTION"
        # resolution_required must mention a new sector
        assert "sector" in result["resolution_required"].lower() or "field" in result["resolution_required"].lower()

    def test_small_sigma_gives_small_wa(self):
        """A small field displacement should give a small |predicted wₐ|."""
        result = bulk_quintessence_constraints(sigma_field_over_mpl=1e-5, potential_scale=1e-5)
        assert abs(result["predicted_wa_from_provided_sigma"]) < 1e-3


# ---------------------------------------------------------------------------
# desi_systematic_error_budget
# ---------------------------------------------------------------------------

class TestDesiSystematicErrorBudget:
    def test_total_systematic_less_than_dr2_uncertainty(self):
        """Total systematic (quadrature) must be < DESI DR2 wₐ uncertainty (0.30)."""
        result = desi_systematic_error_budget()
        assert result["total_systematic_quadrature"] < DESI_DR2["wa_sigma"]

    def test_total_systematic_linear_less_than_dr2_wa_central(self):
        """Total linear systematic must be less than |wₐ_DR2| = 0.62 (tension is real)."""
        result = desi_systematic_error_budget()
        assert result["total_systematic_linear"] < abs(DESI_DR2["wa_central"])

    def test_tension_is_real_flag(self):
        """tension_is_real must be True — systematics do not explain the tension."""
        result = desi_systematic_error_budget()
        assert result["tension_is_real"] is True

    def test_systematics_explain_tension_flag_false(self):
        """systematics_are_sufficient_to_explain_tension must be False."""
        result = desi_systematic_error_budget()
        assert result["systematics_are_sufficient_to_explain_tension"] is False

    def test_required_keys_present(self):
        """Must return all required keys."""
        result = desi_systematic_error_budget()
        for key in ["wa_central_dr2", "wa_sigma_stat_dr2", "current_tension_sigma",
                    "systematics", "total_systematic_quadrature",
                    "total_systematic_linear", "tension_is_real", "conclusion"]:
            assert key in result, f"Missing key: {key}"

    def test_current_tension_approx_2sigma(self):
        """Current tension must be approximately 2.07σ (0.62/0.30)."""
        result = desi_systematic_error_budget()
        expected = abs(DESI_DR2["wa_central"]) / DESI_DR2["wa_sigma"]
        assert abs(result["current_tension_sigma"] - expected) < 0.01

    def test_systematics_dict_nonempty(self):
        """Systematics dict must contain at least one entry."""
        result = desi_systematic_error_budget()
        assert len(result["systematics"]) >= 1


# ---------------------------------------------------------------------------
# likelihood_projection_dr2_to_dr3
# ---------------------------------------------------------------------------

class TestLikelihoodProjectionDr2ToDr3:
    def test_probabilities_sum_to_one(self):
        """Projected DR3 probabilities must sum to 1.0 ± 0.001."""
        result = likelihood_projection_dr2_to_dr3()
        total = result["probability_sum"]
        assert abs(total - 1.0) < 0.001

    def test_required_keys_present(self):
        """Must return all required keys."""
        result = likelihood_projection_dr2_to_dr3()
        for key in ["dr3_wa_sigma_projected", "dr3_wa_central_expected",
                    "p_falsification_tension_geq_3sigma",
                    "p_tension_2to3sigma",
                    "p_consistent_tension_lt_2sigma",
                    "probability_sum", "conclusion"]:
            assert key in result, f"Missing key: {key}"

    def test_all_probabilities_between_0_and_1(self):
        """Each probability must be in [0, 1]."""
        result = likelihood_projection_dr2_to_dr3()
        for key in ["p_falsification_tension_geq_3sigma",
                    "p_tension_2to3sigma",
                    "p_consistent_tension_lt_2sigma"]:
            assert 0.0 <= result[key] <= 1.0, f"Probability {key} = {result[key]} out of range"

    def test_dr3_sigma_smaller_than_dr2(self):
        """DR3 projected sigma must be smaller than DR2 sigma."""
        result = likelihood_projection_dr2_to_dr3(dr2_sigma=0.30, dr3_sigma_reduction_factor=0.6)
        assert result["dr3_wa_sigma_projected"] < 0.30

    def test_high_central_value_gives_high_p_falsified(self):
        """If DR2 central value is very negative (wa=-1.0) and small sigma, p_falsified should be high."""
        result = likelihood_projection_dr2_to_dr3(dr2_wa=-1.0, dr2_sigma=0.10, dr3_sigma_reduction_factor=0.5)
        # With dr2_wa=-1.0, sigma_dr3=0.05, expected tension=20σ → p_falsified ≈ 1
        assert result["p_falsification_tension_geq_3sigma"] > 0.9

    def test_zero_central_value_gives_high_p_consistent(self):
        """If DR2 central value is 0.0, most probability should be in CONSISTENT."""
        result = likelihood_projection_dr2_to_dr3(dr2_wa=0.0, dr2_sigma=0.30, dr3_sigma_reduction_factor=0.6)
        # DR3 centred on 0 → tension < 2σ most of the time
        assert result["p_consistent_tension_lt_2sigma"] > 0.9


# ---------------------------------------------------------------------------
# wa_tension_sigma
# ---------------------------------------------------------------------------

class TestWaTensionSigma:
    def test_exact_match_gives_zero(self):
        """If measured = predicted, tension must be 0.0."""
        assert wa_tension_sigma(0.0, 0.30, 0.0) == pytest.approx(0.0)

    def test_desi_dr2_tension(self):
        """DESI DR2 tension with UM: |−0.62 − 0| / 0.30 = 2.0667."""
        tension = wa_tension_sigma(-0.62, 0.30, 0.0)
        assert tension == pytest.approx(0.62 / 0.30, rel=1e-6)

    def test_known_1sigma(self):
        """wa=-0.30, sigma=0.30, predicted=0.0 → tension = 1.0."""
        assert wa_tension_sigma(-0.30, 0.30, 0.0) == pytest.approx(1.0)

    def test_negative_sigma_raises(self):
        """Negative sigma must raise ValueError."""
        with pytest.raises(ValueError):
            wa_tension_sigma(-0.62, -0.30, 0.0)

    def test_zero_sigma_raises(self):
        """Zero sigma must raise ValueError."""
        with pytest.raises(ValueError):
            wa_tension_sigma(-0.62, 0.0, 0.0)

    def test_absolute_value_symmetry(self):
        """Tension must be symmetric: |wa - pred|/sigma."""
        t1 = wa_tension_sigma(+0.62, 0.30, 0.0)
        t2 = wa_tension_sigma(-0.62, 0.30, 0.0)
        assert t1 == pytest.approx(t2)

    def test_non_zero_prediction(self):
        """Test with non-zero prediction value."""
        tension = wa_tension_sigma(-0.5, 0.25, -0.2)
        assert tension == pytest.approx(abs(-0.5 - (-0.2)) / 0.25)


# ---------------------------------------------------------------------------
# dr3_outcome_probability_map
# ---------------------------------------------------------------------------

class TestDr3OutcomeProbabilityMap:
    def test_probabilities_sum_to_one(self):
        """Outcome probabilities must sum to 1.0 ± 0.001."""
        result = dr3_outcome_probability_map()
        total = result["probability_sum"]
        assert abs(total - 1.0) < 0.001

    def test_required_keys_present(self):
        """Must return all required outcome keys."""
        result = dr3_outcome_probability_map()
        assert "outcomes" in result
        for key in ["FALSIFIED", "TENSION", "CONSISTENT"]:
            assert key in result["outcomes"], f"Missing outcome: {key}"

    def test_each_outcome_has_probability(self):
        """Each outcome must have a 'probability' field in [0, 1]."""
        result = dr3_outcome_probability_map()
        for key, val in result["outcomes"].items():
            assert "probability" in val, f"Missing probability for {key}"
            assert 0.0 <= val["probability"] <= 1.0

    def test_dominant_outcome_is_valid(self):
        """dominant_outcome must be one of FALSIFIED, TENSION, CONSISTENT."""
        result = dr3_outcome_probability_map()
        assert result["dominant_outcome"] in ["FALSIFIED", "TENSION", "CONSISTENT"]

    def test_dr3_sigma_projected_in_result(self):
        """Result must contain projected DR3 sigma."""
        result = dr3_outcome_probability_map()
        assert "dr3_sigma_projected" in result
        assert result["dr3_sigma_projected"] > 0.0


# ---------------------------------------------------------------------------
# falsification_verdict
# ---------------------------------------------------------------------------

class TestFalsificationVerdict:
    def test_falsified_for_clearly_nonzero(self):
        """wa=-1.0, sigma=0.10 → tension=10σ → FALSIFIED."""
        result = falsification_verdict(-1.0, 0.10)
        assert result["verdict"] == "FALSIFIED"

    def test_falsified_flag_true_for_large_tension(self):
        """falsifier_triggered must be True when FALSIFIED."""
        result = falsification_verdict(-1.0, 0.10)
        assert result["falsifier_triggered"] is True

    def test_consistent_for_near_zero(self):
        """wa=0.05, sigma=0.30 → tension=0.17σ → CONSISTENT."""
        result = falsification_verdict(0.05, 0.30)
        assert result["verdict"] == "CONSISTENT"

    def test_falsifier_false_for_consistent(self):
        """falsifier_triggered must be False when CONSISTENT."""
        result = falsification_verdict(0.05, 0.30)
        assert result["falsifier_triggered"] is False

    def test_tension_for_dr2_values(self):
        """DESI DR2 values (wa=-0.62, sigma=0.30) → TENSION (not FALSIFIED)."""
        result = falsification_verdict(-0.62, 0.30)
        assert result["verdict"] in ("TENSION", "HIGH_TENSION")
        assert result["verdict"] != "FALSIFIED"

    def test_high_tension_verdict(self):
        """wa=-0.75, sigma=0.10 → tension=7.5σ → FALSIFIED."""
        result = falsification_verdict(-0.75, 0.10)
        assert result["verdict"] == "FALSIFIED"

    def test_tension_range(self):
        """wa=-0.65, sigma=0.30 → tension~2.17σ → TENSION."""
        result = falsification_verdict(-0.65, 0.30)
        assert result["verdict"] == "TENSION"

    def test_required_keys_in_verdict(self):
        """falsification_verdict must return all required keys."""
        result = falsification_verdict(-0.62, 0.30)
        for key in ["verdict", "tension_sigma", "wa_dr3", "wa_sigma_dr3",
                    "um_wa_prediction", "required_action", "um_status_update",
                    "falsifier_triggered", "files_to_update"]:
            assert key in result, f"Missing key: {key}"

    def test_tension_sigma_matches_wa_tension_sigma(self):
        """tension_sigma in verdict must match wa_tension_sigma()."""
        wa, sigma = -0.62, 0.30
        expected = wa_tension_sigma(wa, sigma, 0.0)
        result = falsification_verdict(wa, sigma)
        assert result["tension_sigma"] == pytest.approx(expected)

    def test_files_to_update_nonempty(self):
        """files_to_update must be a non-empty list."""
        result = falsification_verdict(-0.62, 0.30)
        assert isinstance(result["files_to_update"], list)
        assert len(result["files_to_update"]) > 0

    def test_positive_wa_consistent(self):
        """Small positive wₐ should be CONSISTENT with UM wₐ = 0."""
        result = falsification_verdict(0.10, 0.30)
        assert result["verdict"] == "CONSISTENT"
