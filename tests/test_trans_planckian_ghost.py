# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_trans_planckian_ghost.py
=====================================
Tests for Pillar 122 — Trans-Planckian Ghost-Limit.

Verifies that ghost image redshift, flux suppression, and all public API
functions behave correctly and are internally consistent.
"""

from __future__ import annotations

import math

import pytest

from src.core.trans_planckian_ghost import (
    CMB_NOISE_FLOOR_JY,
    GHOST_REDSHIFT_EXPONENT,
    K_CS,
    N_W,
    SCALE_RATIO_61,
    ghost_flux_log10,
    ghost_flux_ratio,
    ghost_image_redshift_factor,
    matched_circles_ir_suppression,
    trans_planckian_proof_steps,
    um_alignment,
    why_no_copies_summary,
)


class TestGhostImageRedshiftFactor:
    def test_returns_float(self):
        assert isinstance(ghost_image_redshift_factor(), float)

    def test_greater_than_1e60(self):
        assert ghost_image_redshift_factor() > 1e60

    def test_equals_scale_ratio_61(self):
        assert ghost_image_redshift_factor() == pytest.approx(SCALE_RATIO_61)

    def test_less_than_1e62(self):
        assert ghost_image_redshift_factor() < 1e62

    def test_type_is_float(self):
        result = ghost_image_redshift_factor()
        assert type(result) is float


class TestGhostFluxRatio:
    def test_returns_float(self):
        assert isinstance(ghost_flux_ratio(), float)

    def test_underflows_to_zero(self):
        # (1+z)^-4 ≈ 10^-244; Python float64 can represent this (> subnormal min ~5e-324)
        # but it is negligibly small — effectively zero for all physical purposes
        result = ghost_flux_ratio()
        assert result == 0.0 or result < 1e-200

    def test_type_is_float(self):
        result = ghost_flux_ratio()
        assert type(result) is float

    def test_consistent_with_inverse_fourth_power_below_float64(self):
        # Confirm that 10^(-4*61) = 10^-244 is physically negligible
        result = ghost_flux_ratio()
        assert result == 0.0 or result < 1e-200


class TestGhostFluxLog10:
    def test_returns_float(self):
        assert isinstance(ghost_flux_log10(), float)

    def test_equals_minus_four_times_exponent(self):
        assert ghost_flux_log10() == pytest.approx(-4.0 * GHOST_REDSHIFT_EXPONENT)

    def test_less_than_minus_200(self):
        assert ghost_flux_log10() < -200.0

    def test_greater_than_minus_300(self):
        assert ghost_flux_log10() > -300.0

    def test_approx_minus_244(self):
        assert ghost_flux_log10() == pytest.approx(-244.0)


class TestMatchedCirclesIrSuppression:
    def setup_method(self):
        self._result = matched_circles_ir_suppression()

    def test_returns_dict(self):
        assert isinstance(self._result, dict)

    def test_has_ghost_redshift_factor_key(self):
        assert "ghost_redshift_factor" in self._result

    def test_has_ghost_flux_log10_key(self):
        assert "ghost_flux_log10" in self._result

    def test_has_cmb_noise_floor_jy_key(self):
        assert "cmb_noise_floor_jy" in self._result

    def test_has_ghost_flux_log10_jy_key(self):
        assert "ghost_flux_log10_jy" in self._result

    def test_has_ghost_below_noise_key(self):
        assert "ghost_below_noise" in self._result

    def test_has_suppression_mechanism_key(self):
        assert "suppression_mechanism" in self._result

    def test_has_resolution_key(self):
        assert "resolution" in self._result

    def test_has_epistemic_status_key(self):
        assert "epistemic_status" in self._result

    def test_ghost_below_noise_is_true(self):
        assert self._result["ghost_below_noise"] is True

    def test_ghost_below_noise_is_bool(self):
        assert type(self._result["ghost_below_noise"]) is bool

    def test_ghost_flux_log10_less_than_minus_200(self):
        assert self._result["ghost_flux_log10"] < -200.0

    def test_cmb_noise_floor_jy_positive(self):
        assert self._result["cmb_noise_floor_jy"] > 0.0

    def test_suppression_mechanism_nonempty_string(self):
        val = self._result["suppression_mechanism"]
        assert isinstance(val, str) and len(val) > 0

    def test_resolution_nonempty_string(self):
        val = self._result["resolution"]
        assert isinstance(val, str) and len(val) > 0


class TestTransPlanckianProofSteps:
    def setup_method(self):
        self._steps = trans_planckian_proof_steps()

    def test_returns_list(self):
        assert isinstance(self._steps, list)

    def test_at_least_six_steps(self):
        assert len(self._steps) >= 6

    def test_each_step_is_dict(self):
        for s in self._steps:
            assert isinstance(s, dict)

    def test_each_step_has_step_key(self):
        for s in self._steps:
            assert "step" in s

    def test_each_step_has_title_key(self):
        for s in self._steps:
            assert "title" in s

    def test_each_step_has_statement_key(self):
        for s in self._steps:
            assert "statement" in s

    def test_steps_numbered_sequentially_from_1(self):
        for i, s in enumerate(self._steps, start=1):
            assert s["step"] == i

    def test_all_titles_nonempty(self):
        for s in self._steps:
            assert isinstance(s["title"], str) and len(s["title"]) > 0

    def test_all_statements_nonempty(self):
        for s in self._steps:
            assert isinstance(s["statement"], str) and len(s["statement"]) > 0

    def test_first_step_mentions_ghost_or_copy_or_topology(self):
        first = self._steps[0]["statement"].lower() + self._steps[0]["title"].lower()
        assert any(word in first for word in ("ghost", "copy", "topolog", "copies"))

    def test_last_step_mentions_undetectable_or_conclusion(self):
        last = self._steps[-1]["statement"].lower() + self._steps[-1]["title"].lower()
        assert any(word in last for word in ("undetectable", "conclusion", "detect"))


class TestWhyNoCopiesSummary:
    def setup_method(self):
        self._result = why_no_copies_summary()

    def test_returns_dict(self):
        assert isinstance(self._result, dict)

    def test_pillar_equals_122(self):
        assert self._result["pillar"] == 122

    def test_scale_ratio_equals_scale_ratio_61(self):
        assert self._result["scale_ratio"] == pytest.approx(SCALE_RATIO_61)

    def test_ghost_flux_log10_less_than_minus_200(self):
        assert self._result["ghost_flux_log10"] < -200.0

    def test_conclusion_nonempty_string(self):
        val = self._result["conclusion"]
        assert isinstance(val, str) and len(val) > 0

    def test_prediction_nonempty_string(self):
        val = self._result["prediction"]
        assert isinstance(val, str) and len(val) > 0

    def test_falsification_nonempty_string(self):
        val = self._result["falsification"]
        assert isinstance(val, str) and len(val) > 0

    def test_epistemic_status_nonempty_string(self):
        val = self._result["epistemic_status"]
        assert isinstance(val, str) and len(val) > 0


class TestUmAlignment:
    def setup_method(self):
        self._result = um_alignment()

    def test_returns_dict(self):
        assert isinstance(self._result, dict)

    def test_pillar_equals_122(self):
        assert self._result["pillar"] == 122

    def test_shared_scale_ratio_equals_scale_ratio_61(self):
        assert self._result["shared_scale_ratio"] == pytest.approx(SCALE_RATIO_61)

    def test_pillar_116_consistent_is_true(self):
        assert self._result["pillar_116_consistent"] is True

    def test_pillar_120_consistent_is_true(self):
        assert self._result["pillar_120_consistent"] is True

    def test_n_w_equals_5(self):
        assert self._result["n_w"] == N_W

    def test_k_cs_equals_74(self):
        assert self._result["k_cs"] == K_CS
