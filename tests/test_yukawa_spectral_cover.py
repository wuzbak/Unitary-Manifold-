# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from __future__ import annotations

import math

import pytest

from src.twelved.yukawa_spectral_cover import (
    EPISTEMIC_STATUS,
    K_CS,
    N_W,
    PI_KR,
    PILLAR_NUMBER,
    STATUS,
    bottom_tau_yukawa_so12_point,
    fn_ratio_from_warp,
    light_generation_hierarchy,
    matter_curves_su5,
    spectral_cover_equation,
    top_yukawa_e6_point,
    yukawa_matrix_spectral,
    yukawa_spectral_cover_report,
)


class TestMetadata:
    def test_constants(self):
        assert PILLAR_NUMBER == 781
        assert STATUS == "YUKAWA_SPECTRAL_COVER_ADJACENT_TRACK"
        assert EPISTEMIC_STATUS == "ADJACENT_TRACK"
        assert N_W == 5
        assert K_CS == 74


class TestSpectralCover:
    def test_degree_five_cover(self):
        r = spectral_cover_equation()
        assert r["degree"] == 5
        assert r["rank_match"] is True

    def test_invalid_degree_raises(self):
        with pytest.raises(ValueError):
            spectral_cover_equation(4)

    def test_equation_mentions_a5(self):
        r = spectral_cover_equation()
        assert "a5" in r["equation"]


class TestMatterCurves:
    def test_ten_curve(self):
        r = matter_curves_su5()
        assert r["curves"]["10_M"] == "a5 = 0"

    def test_fivebar_curve_has_quadratic_piece(self):
        r = matter_curves_su5()
        assert "a3^2" in r["curves"]["5bar_M"]


class TestYukawaPoints:
    def test_top_yukawa_order_one(self):
        r = top_yukawa_e6_point()
        assert r["top_yukawa_estimate"] == pytest.approx(1.0)
        assert r["order_of_magnitude"] == "O(1)"

    def test_bottom_tau_benchmark_in_band(self):
        r = bottom_tau_yukawa_so12_point()
        low, high = r["constrained_band"]
        assert low <= r["benchmark_ratio"] <= high


class TestWarpAndHierarchy:
    def test_fn_ratio_matches_exp_formula(self):
        r = fn_ratio_from_warp()
        assert r["fn_ratio"] == pytest.approx(math.exp(-PI_KR * 0.1))

    def test_negative_delta_raises(self):
        with pytest.raises(ValueError):
            fn_ratio_from_warp(delta_frac=-0.1)

    def test_hierarchy_is_ordered(self):
        r = light_generation_hierarchy()
        ratios = r["yukawa_ratios"]
        assert ratios["Y_u_over_Y_t"] < ratios["Y_c_over_Y_t"] < ratios["Y_t_over_Y_t"]


class TestTexturesAndReport:
    def test_texture_shapes(self):
        r = yukawa_matrix_spectral()
        assert len(r["up_matrix"]) == 3
        assert len(r["up_matrix"][0]) == 3
        assert len(r["down_matrix"]) == 3
        assert len(r["down_matrix"][0]) == 3

    def test_textures_are_symmetric(self):
        r = yukawa_matrix_spectral()
        up = r["up_matrix"]
        down = r["down_matrix"]
        assert up[0][1] == pytest.approx(up[1][0])
        assert down[0][2] == pytest.approx(down[2][0])

    def test_report_contains_sections(self):
        r = yukawa_spectral_cover_report()
        for key in ["spectral_cover", "matter_curves", "top_yukawa", "bottom_tau", "hierarchy", "textures"]:
            assert key in r
