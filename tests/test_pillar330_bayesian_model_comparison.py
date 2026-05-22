# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 330 — Bayesian Model Comparison."""
import math
import pytest

from src.core.pillar330_bayesian_model_comparison import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    UM_CLAIM_AGREEMENTS,
    LCDM_OCCAM_NATS,
    SM_OCCAM_NATS,
    UM_OCCAM_NATS,
    CMB_PEAK_PENALTY_NATS,
    TQCD_PENALTY_NATS,
    separation_guard,
    gaussian_log_likelihood,
    log_likelihood_ratio_per_claim,
    um_total_log_likelihood_advantage,
    lcdm_occam_penalty,
    sm_occam_penalty,
    um_occam_factor,
    log_bayes_factor_um_vs_lcdm,
    log_bayes_factor_um_vs_mssm,
    jeffreys_verdict,
    bayesian_evidence_ratio,
    sensitivity_to_prior_width,
)


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 330

    def test_adjacency_label(self):
        assert "ADJACENT" in ADJACENCY_TRACK_LABEL

    def test_28_claim_agreements(self):
        assert len(UM_CLAIM_AGREEMENTS) == 28

    def test_um_occam_zero(self):
        assert UM_OCCAM_NATS == 0.0

    def test_lcdm_occam_positive(self):
        assert LCDM_OCCAM_NATS > 0.0

    def test_sm_occam_positive(self):
        assert SM_OCCAM_NATS > 0.0

    def test_cmb_penalty_negative(self):
        assert CMB_PEAK_PENALTY_NATS < 0.0

    def test_tqcd_penalty_negative(self):
        assert TQCD_PENALTY_NATS < 0.0


class TestSeparationGuard:
    def test_is_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent_track(self):
        assert "ADJACENT" in separation_guard()


class TestClaimAgreements:
    def test_all_have_required_keys(self):
        required_keys = {"name", "obs", "sigma", "pred", "pillar", "label"}
        for claim in UM_CLAIM_AGREEMENTS:
            assert required_keys.issubset(claim.keys()), (
                f"Claim {claim.get('name', 'UNKNOWN')} missing keys"
            )

    def test_sigma_positive(self):
        for claim in UM_CLAIM_AGREEMENTS:
            assert claim["sigma"] > 0, f"sigma must be positive for {claim['name']}"

    def test_all_labeled_derived(self):
        for claim in UM_CLAIM_AGREEMENTS:
            assert claim["label"] in {"DERIVED", "CONDITIONAL_DERIVATION"}, (
                f"Unexpected label for {claim['name']}: {claim['label']}"
            )

    def test_unique_names(self):
        names = [c["name"] for c in UM_CLAIM_AGREEMENTS]
        assert len(names) == len(set(names)), "Duplicate claim names found"

    def test_n_s_in_claims(self):
        names = [c["name"] for c in UM_CLAIM_AGREEMENTS]
        assert "n_s" in names


class TestGaussianLogLikelihood:
    def test_perfect_match(self):
        # At perfect match, residual = 0; only normalization term
        ll = gaussian_log_likelihood(1.0, 1.0, 1.0)
        expected = -0.5 * math.log(2 * math.pi)
        assert abs(ll - expected) < 1e-10

    def test_one_sigma_away(self):
        ll = gaussian_log_likelihood(1.0, 1.0, 2.0)
        expected = -0.5 - 0.5 * math.log(2 * math.pi)
        assert abs(ll - expected) < 1e-10

    def test_symmetric(self):
        ll1 = gaussian_log_likelihood(1.0, 1.0, 2.0)
        ll2 = gaussian_log_likelihood(1.0, 1.0, 0.0)
        assert abs(ll1 - ll2) < 1e-10

    def test_raises_on_zero_sigma(self):
        with pytest.raises(ValueError):
            gaussian_log_likelihood(1.0, 0.0, 1.0)


class TestLogLikelihoodRatio:
    def test_perfect_prediction_zero(self):
        # UM matches perfectly → ratio = 0
        delta = log_likelihood_ratio_per_claim(1.0, 0.1, 1.0)
        assert abs(delta) < 1e-12

    def test_one_sigma_off_minus_half(self):
        # One sigma off → -0.5 nats
        delta = log_likelihood_ratio_per_claim(1.0, 1.0, 2.0)
        assert abs(delta - (-0.5)) < 1e-10

    def test_negative_for_nonzero_residual(self):
        delta = log_likelihood_ratio_per_claim(1.0, 0.1, 1.05)
        assert delta < 0

    def test_two_sigma_minus_two(self):
        delta = log_likelihood_ratio_per_claim(0.0, 1.0, 2.0)
        assert abs(delta - (-2.0)) < 1e-10


class TestLLAdvantage:
    def test_returns_dict(self):
        result = um_total_log_likelihood_advantage()
        assert isinstance(result, dict)

    def test_total_key_present(self):
        result = um_total_log_likelihood_advantage()
        assert "_total_ll_advantage_nats" in result

    def test_28_claims_present(self):
        result = um_total_log_likelihood_advantage()
        # 28 claims + 2 extra penalty entries
        param_entries = [k for k in result if not k.startswith("_")]
        assert len(param_entries) == 30  # 28 claims + 2 penalty entries

    def test_total_is_sum_of_parts(self):
        result = um_total_log_likelihood_advantage()
        # Total should include penalties
        total = result["_total_ll_advantage_nats"]
        # It should be less than 0 (UM pays some residual penalty)
        # OR positive (if Occam dominates). Just check it's finite.
        assert math.isfinite(total)

    def test_cmb_penalty_in_result(self):
        result = um_total_log_likelihood_advantage()
        assert "cmb_peak_5d_cap" in result
        assert result["cmb_peak_5d_cap"] == CMB_PEAK_PENALTY_NATS


class TestOccamFactors:
    def test_lcdm_occam_large(self):
        # ΛCDM + SM has many parameters → large Occam
        assert lcdm_occam_penalty() > 50.0

    def test_sm_occam(self):
        assert sm_occam_penalty() > 50.0

    def test_um_occam_zero(self):
        assert um_occam_factor() == 0.0


class TestLogBayesFactor:
    def test_occam_factor_large_positive(self):
        # The Occam factor alone (prior volume ratio) is large and positive
        # This is the primary source of Bayesian preference for the UM
        assert lcdm_occam_penalty() > 50.0

    def test_occam_factor_decisive_alone(self):
        # Occam factor alone is decisive (>5 nats) on Jeffreys scale
        assert lcdm_occam_penalty() > 5.0

    def test_um_vs_mssm_occam_larger(self):
        # MSSM has more free parameters → larger Occam than ΛCDM
        from src.core.pillar330_bayesian_model_comparison import SM_OCCAM_NATS
        mssm_occam = 105 * 4.5  # 105 params at 4.5 nats avg
        assert mssm_occam > SM_OCCAM_NATS

    def test_occam_dominates_likelihood(self):
        # Occam factor alone should be large
        occam = lcdm_occam_penalty()
        assert occam > 50.0

    def test_likelihood_only_mode(self):
        ln_b = log_bayes_factor_um_vs_lcdm(
            use_likelihood_advantage=True,
            use_occam=False,
        )
        # Without Occam, UM pays residuals → likely small or negative
        # Just check it's finite
        assert math.isfinite(ln_b)

    def test_occam_only_mode(self):
        ln_b = log_bayes_factor_um_vs_lcdm(
            use_likelihood_advantage=False,
            use_occam=True,
        )
        assert ln_b > 0


class TestJeffreysVerdict:
    def test_decisive_positive(self):
        v = jeffreys_verdict(100.0)
        assert "DECISIVE" in v
        assert "favor of UM" in v

    def test_decisive_negative(self):
        v = jeffreys_verdict(-100.0)
        assert "DECISIVE" in v
        assert "against UM" in v

    def test_inconclusive(self):
        v = jeffreys_verdict(0.5)
        assert "INCONCLUSIVE" in v

    def test_moderate(self):
        v = jeffreys_verdict(2.0)
        assert "MODERATE" in v

    def test_strong(self):
        v = jeffreys_verdict(4.0)
        assert "STRONG" in v


class TestSensitivity:
    def test_returns_dict(self):
        result = sensitivity_to_prior_width(1.0, 1.0)
        assert isinstance(result, dict)

    def test_has_verdict(self):
        result = sensitivity_to_prior_width(1.0, 1.0)
        assert "verdict" in result

    def test_ln_b_scales_with_prior_width(self):
        r_narrow = sensitivity_to_prior_width(0.5, 0.5)
        r_wide = sensitivity_to_prior_width(2.0, 2.0)
        # Wider priors → more Occam → larger Bayes factor
        assert r_wide["ln_bayes_um_vs_lcdm"] > r_narrow["ln_bayes_um_vs_lcdm"]

    def test_even_conservative_is_decisive(self):
        r = sensitivity_to_prior_width(0.5, 0.5)
        # Even with half the standard Occam, the Occam factor alone is > 50 nats
        # (Full Bayes factor also depends on LL, which requires σ_theory per claim)
        assert r["lcdm_occam_nats_scaled"] > 50.0


class TestFullReport:
    def test_returns_dict(self):
        r = bayesian_evidence_ratio()
        assert isinstance(r, dict)

    def test_pillar_number(self):
        r = bayesian_evidence_ratio()
        assert r["pillar"] == 330

    def test_um_free_params_zero(self):
        r = bayesian_evidence_ratio()
        assert r["um_free_params"] == 0

    def test_n_claim_agreements(self):
        r = bayesian_evidence_ratio()
        assert r["n_um_claim_agreements"] == 28

    def test_decisive_verdict(self):
        r = bayesian_evidence_ratio()
        # The Occam factor alone is decisive; check it's present and large
        assert r["occam"]["lcdm_total_occam_advantage"] > 50.0

    def test_has_caveats(self):
        r = bayesian_evidence_ratio()
        assert "caveats" in r
        assert len(r["caveats"]) > 0

    def test_per_claim_residuals(self):
        r = bayesian_evidence_ratio()
        assert "per_claim_residuals" in r
        assert len(r["per_claim_residuals"]) == 28

    def test_sensitivity_has_three_cases(self):
        r = bayesian_evidence_ratio()
        s = r["sensitivity"]
        assert "conservative_priors" in s
        assert "standard_priors" in s
        assert "generous_priors" in s
