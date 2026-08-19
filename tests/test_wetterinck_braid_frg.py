# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from __future__ import annotations

import pytest

from src.core.wetterinck_braid_frg import (
    EPISTEMIC_STATUS,
    K_CS,
    PILLAR_NUMBER,
    STATUS,
    beta_cosmological_constant,
    beta_cs_level,
    beta_newton_coupling,
    braid_rg_invariance_proof,
    litim_regulator,
    rg_flow_g5,
    uv_fixed_point_g5,
    wetterinck_braid_frg_report,
)


class TestMetadata:
    def test_constants(self):
        assert PILLAR_NUMBER == 780
        assert STATUS == "BRAID_FRG_SCAFFOLD"
        assert EPISTEMIC_STATUS == "SCAFFOLD"
        assert K_CS == 74


class TestLitimRegulator:
    def test_active_regulator(self):
        r = litim_regulator(0.25, 1.0)
        assert r["regulator"] == pytest.approx(0.75)
        assert r["regulator_active"] is True

    def test_inactive_regulator(self):
        r = litim_regulator(2.0, 1.0)
        assert r["regulator"] == 0.0
        assert r["regulator_active"] is False

    def test_negative_input_raises(self):
        with pytest.raises(ValueError):
            litim_regulator(-1.0, 1.0)


class TestNewtonBeta:
    def test_small_g_beta_positive(self):
        r = beta_newton_coupling(0.1)
        assert r["beta_g"] > 0.0

    def test_zero_g_beta_zero(self):
        r = beta_newton_coupling(0.0)
        assert r["beta_g"] == pytest.approx(0.0)

    def test_singularity_raises(self):
        c_g = beta_newton_coupling(0.1)["c_g"]
        with pytest.raises(ValueError):
            beta_newton_coupling(2.0 / c_g, c_g=c_g)


class TestFixedPointAndCS:
    def test_uv_fixed_point_large_and_positive(self):
        r = uv_fixed_point_g5()
        assert r["g_star"] > 1000.0
        assert r["fixed_point_exists"] is True

    def test_cs_beta_zero(self):
        r = beta_cs_level()
        assert r["beta_k_cs"] == pytest.approx(0.0)
        assert r["protected"] is True

    def test_braid_invariance(self):
        r = braid_rg_invariance_proof()
        assert r["invariant_under_rg"] is True


class TestCosmologicalAndFlow:
    def test_cosmological_beta_positive_at_zero_lambda(self):
        r = beta_cosmological_constant(0.0, 10.0)
        assert r["beta_lambda"] > 0.0

    def test_negative_k_raises(self):
        with pytest.raises(ValueError):
            beta_cosmological_constant(0.0, -1.0)

    def test_rg_flow_requires_positive_scales(self):
        with pytest.raises(ValueError):
            rg_flow_g5(0.0, 1.0)

    def test_rg_flow_grows_toward_uv(self):
        r = rg_flow_g5(1.0e3, 1.0e6)
        assert r["g_final"] > r["g_initial"]
        assert r["approached_uv_fixed_point"] is True

    def test_report_contains_sections(self):
        r = wetterinck_braid_frg_report()
        for key in ["regulator", "beta_g", "uv_fixed_point", "beta_k_cs", "beta_lambda", "rg_flow", "invariance"]:
            assert key in r
