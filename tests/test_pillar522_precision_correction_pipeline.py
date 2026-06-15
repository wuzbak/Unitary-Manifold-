# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 522 — 11D precision observable corrections pipeline.

Status: FRONTIER_COMPUTATION (🔵 ADJACENT TRACK)
"""

from __future__ import annotations

import math
import pytest

from src.eleventd.precision_correction_pipeline import (
    CMBS4_AMP_SENSITIVITY,
    CMBS4_R_SENSITIVITY,
    LITEBIRD_BETA_SENSITIVITY_DEG,
    SPHEREX_FNL_SENSITIVITY,
    cmb_amplitude_chain,
    falsifier_map,
    nlo_seed_chain,
    nlo_zphi_chain,
    p_r_chain,
    pipeline_consistency_checks,
    precision_correction_pipeline,
)


# ── Module constants ───────────────────────────────────────────────────────────


class TestModuleConstants:
    def test_litebird_sensitivity(self):
        assert LITEBIRD_BETA_SENSITIVITY_DEG > 0

    def test_cmbs4_r_sensitivity(self):
        assert CMBS4_R_SENSITIVITY > 0

    def test_spherex_fnl_sensitivity(self):
        assert SPHEREX_FNL_SENSITIVITY > 0

    def test_cmbs4_amp_sensitivity(self):
        assert CMBS4_AMP_SENSITIVITY > 0


# ── nlo_zphi_chain ────────────────────────────────────────────────────────────


class TestNloZphiChain:
    @pytest.fixture(scope="class")
    def chain(self):
        return nlo_zphi_chain()

    def test_required_keys(self, chain):
        for k in ("zphi_0", "delta_zphi_g4", "zphi_nlo",
                  "cmb_pct_resolved", "sigma_residual_nlo_pct",
                  "architecture_limit_status"):
            assert k in chain

    def test_zphi_nlo_greater_than_zphi_0(self, chain):
        assert chain["zphi_nlo"] > chain["zphi_0"]

    def test_delta_positive(self, chain):
        assert chain["delta_zphi_g4"] > 0

    def test_cmb_pct_resolved_positive(self, chain):
        assert chain["cmb_pct_resolved"] > 0

    def test_architecture_limit_status(self, chain):
        assert "PARTIALLY_RESOLVED" in chain["architecture_limit_status"]

    def test_deterministic(self):
        c1 = nlo_zphi_chain()
        c2 = nlo_zphi_chain()
        assert c1["zphi_nlo"] == pytest.approx(c2["zphi_nlo"])


# ── cmb_amplitude_chain ───────────────────────────────────────────────────────


class TestCmbAmplitudeChain:
    @pytest.fixture(scope="class")
    def result(self):
        zphi_nlo = 1.0 + math.sqrt(74) / 2.0 + 0.5  # Z_φ^{(0)} + typical delta
        return cmb_amplitude_chain(zphi_nlo)

    def test_required_keys(self, result):
        for k in ("zphi_0", "zphi_nlo", "amp_ratio_at_zphi0",
                  "amp_ratio_at_nlo", "irreducible_floor_range",
                  "5d_irreducible_floor_label"):
            assert k in result

    def test_amp_ratio_at_nlo_greater_than_at_0(self, result):
        # NLO Z_φ > Z_φ^{(0)} → better amplitude suppression resolution
        avg_nlo = sum(result["amp_ratio_at_nlo"]) / 2
        avg_0 = sum(result["amp_ratio_at_zphi0"]) / 2
        assert avg_nlo >= avg_0

    def test_irreducible_floor_label(self, result):
        assert result["5d_irreducible_floor_label"] == "5D_IRREDUCIBLE_FLOOR"

    def test_floor_non_negative(self, result):
        for v in result["irreducible_floor_range"]:
            assert v >= 0

    def test_experiment_sensitivity_key(self, result):
        assert "experiment_sensitivity" in result


# ── p_r_chain ─────────────────────────────────────────────────────────────────


class TestPrChain:
    @pytest.fixture(scope="class")
    def result(self):
        return p_r_chain(0.125)

    def test_required_keys(self, result):
        for k in ("p_r_conditional", "e8_threshold_correction", "status",
                  "within_geometric_bounds", "within_two_loop_interval",
                  "open_condition", "upgrade_from"):
            assert k in result

    def test_p_r_positive(self, result):
        assert result["p_r_conditional"] > 0

    def test_within_geometric_bounds(self, result):
        assert result["within_geometric_bounds"] is True

    def test_status(self, result):
        assert "CONDITIONAL_DERIVATION" in result["status"]

    def test_upgrade_from_named(self, result):
        assert "517" in result["upgrade_from"]


# ── nlo_seed_chain ────────────────────────────────────────────────────────────


class TestNloSeedChain:
    @pytest.fixture(scope="class")
    def seed(self):
        return nlo_seed_chain()

    def test_required_keys(self, seed):
        for k in ("eta_bar_nlo", "pi_kr_nlo", "vol_cy3_nlo",
                  "pi_kr_shift_pct", "vol_cy3_shift_pct",
                  "all_within_nlo_bound_0_74"):
            assert k in seed

    def test_eta_bar_nlo(self, seed):
        assert seed["eta_bar_nlo"] == pytest.approx(0.5)

    def test_pi_kr_nlo_positive(self, seed):
        assert seed["pi_kr_nlo"] > 0

    def test_vol_cy3_nlo_positive(self, seed):
        assert seed["vol_cy3_nlo"] > 0

    def test_deterministic(self):
        s1 = nlo_seed_chain()
        s2 = nlo_seed_chain()
        assert s1["pi_kr_nlo"] == pytest.approx(s2["pi_kr_nlo"])
        assert s1["vol_cy3_nlo"] == pytest.approx(s2["vol_cy3_nlo"])


# ── falsifier_map ─────────────────────────────────────────────────────────────


class TestFalsifierMap:
    @pytest.fixture(scope="class")
    def fmap(self):
        return falsifier_map(zphi_nlo=9.0, p_r_conditional=0.365, pi_kr_nlo=37.01)

    def test_required_experiments(self, fmap):
        for exp in ("litebird", "cmb_s4", "spherex", "juno"):
            assert exp in fmap

    def test_litebird_not_distinguishable(self, fmap):
        # Birefringence set by K_CS, not CY₃ volume
        assert fmap["litebird"]["distinguishable_11d_correction"] is False

    def test_cmb_s4_has_sensitivity(self, fmap):
        assert "sensitivity" in fmap["cmb_s4"]

    def test_spherex_has_sensitivity(self, fmap):
        assert "sensitivity" in fmap["spherex"]

    def test_juno_not_distinguishable(self, fmap):
        assert fmap["juno"]["distinguishable_11d_correction"] is False


# ── pipeline_consistency_checks ───────────────────────────────────────────────


class TestPipelineConsistencyChecks:
    def test_all_checks_pass(self):
        # Build consistent mock data
        zphi = {
            "zphi_0": 5.3,
            "zphi_nlo": 5.9,
            "delta_zphi_g4": 0.6,
        }
        p_r = {"within_geometric_bounds": True}
        seed = {"eta_bar_nlo": 0.5}
        cmb = {"zphi_nlo": 5.9}
        result = pipeline_consistency_checks(zphi, p_r, seed, cmb)
        assert result["all_checks_pass"] is True

    def test_detects_zphi_regression(self):
        zphi = {
            "zphi_0": 5.9,
            "zphi_nlo": 5.3,  # Wrong: NLO < zero-point
            "delta_zphi_g4": -0.6,
        }
        p_r = {"within_geometric_bounds": True}
        seed = {"eta_bar_nlo": 0.5}
        cmb = {"zphi_nlo": 5.3}
        result = pipeline_consistency_checks(zphi, p_r, seed, cmb)
        assert result["zphi_nlo_greater_than_zphi_0"] is False
        assert result["all_checks_pass"] is False

    def test_detects_eta_bar_instability(self):
        zphi = {
            "zphi_0": 5.3,
            "zphi_nlo": 5.9,
        }
        p_r = {"within_geometric_bounds": True}
        seed = {"eta_bar_nlo": 0.6}  # Wrong: should be 0.5
        cmb = {"zphi_nlo": 5.9}
        result = pipeline_consistency_checks(zphi, p_r, seed, cmb)
        assert result["eta_bar_stable_at_0_5"] is False
        assert result["all_checks_pass"] is False


# ── precision_correction_pipeline (full integration) ──────────────────────────


class TestPrecisionCorrectionPipeline:
    @pytest.fixture(scope="class")
    def pipeline(self):
        return precision_correction_pipeline()

    def test_pillar_number(self, pipeline):
        assert pipeline["pillar"] == 522

    def test_status(self, pipeline):
        assert pipeline["status"] == "FRONTIER_COMPUTATION"

    def test_track_label(self, pipeline):
        assert "ADJACENT TRACK" in pipeline["track"]

    def test_deliverable_1_zphi_nlo(self, pipeline):
        assert pipeline["zphi_nlo"] > pipeline["zphi_0"]

    def test_deliverable_2_cmb_amplitude(self, pipeline):
        cmb = pipeline["cmb_amplitude"]
        assert cmb["pct_residual_resolved"] > 0
        assert "5D_IRREDUCIBLE_FLOOR" in cmb["5d_irreducible_floor_label"]

    def test_deliverable_3_p_r(self, pipeline):
        pr = pipeline["p_r_conditional"]
        assert pr["p_r_value"] > 0
        assert "CONDITIONAL_DERIVATION" in pr["status"]

    def test_deliverable_4_nlo_seed(self, pipeline):
        seed = pipeline["nlo_seed"]
        assert seed["eta_bar"] == pytest.approx(0.5)
        assert seed["pi_kr"] > 0
        assert seed["vol_cy3"] > 0

    def test_deliverable_5_falsifier_map(self, pipeline):
        fmap = pipeline["falsifier_map"]
        assert "litebird" in fmap
        assert "cmb_s4" in fmap
        assert "spherex" in fmap
        assert "juno" in fmap

    def test_consistency_checks_all_pass(self, pipeline):
        assert pipeline["consistency_checks"]["all_checks_pass"] is True

    def test_pipeline_steps_present(self, pipeline):
        assert len(pipeline["pipeline_steps"]) >= 5

    def test_upstream_pillars(self, pipeline):
        assert 519 in pipeline["upstream_pillars"]
        assert 520 in pipeline["upstream_pillars"]
        assert 521 in pipeline["upstream_pillars"]

    def test_downstream_pillars(self, pipeline):
        assert 523 in pipeline["downstream_pillars"]
        assert 524 in pipeline["downstream_pillars"]

    def test_no_hardgate_score_change(self, pipeline):
        assert pipeline["no_hardgate_score_change"] is True

    def test_deterministic(self):
        p1 = precision_correction_pipeline()
        p2 = precision_correction_pipeline()
        assert p1["zphi_nlo"] == pytest.approx(p2["zphi_nlo"])
        assert p1["p_r_conditional"]["p_r_value"] == pytest.approx(
            p2["p_r_conditional"]["p_r_value"]
        )
        assert p1["nlo_seed"]["pi_kr"] == pytest.approx(p2["nlo_seed"]["pi_kr"])
        assert p1["nlo_seed"]["vol_cy3"] == pytest.approx(p2["nlo_seed"]["vol_cy3"])

    def test_bit_reproducible_zphi(self):
        p1 = precision_correction_pipeline()
        p2 = precision_correction_pipeline()
        # Exact bit-for-bit equality (no randomness in pipeline)
        assert p1["zphi_nlo"] == p2["zphi_nlo"]
        assert p1["delta_zphi_g4"] == p2["delta_zphi_g4"]
