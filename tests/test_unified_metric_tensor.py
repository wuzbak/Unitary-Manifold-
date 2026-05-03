# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_unified_metric_tensor.py
=====================================
Tests for Pillar 124 — Unitary-Manifold Metric Tensor (Unified).

src/core/unified_metric_tensor.py
"""

from __future__ import annotations

import math

import pytest

from src.core.unified_metric_tensor import (
    R_KK_M,
    N_W,
    K_CS,
    PHI0,
    N_EXTRA_DIMS,
    effective_4d_metric,
    flrw_metric_components,
    kaluza_klein_reduction,
    metric_unification_proof,
    um_internal_dof,
    unified_5d_metric,
)


# ---------------------------------------------------------------------------
# TestFlrwMetricComponents (10 tests)
# ---------------------------------------------------------------------------

class TestFlrwMetricComponents:
    def test_returns_dict(self):
        result = flrw_metric_components(1.0)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = flrw_metric_components(1.0)
        for key in ("g_tt", "g_xx", "g_yy", "g_zz", "a", "signature", "metric_type", "determinant"):
            assert key in result

    def test_g_tt_is_minus_one(self):
        result = flrw_metric_components(2.5)
        assert result["g_tt"] == pytest.approx(-1.0)

    def test_g_xx_at_a_equals_1(self):
        result = flrw_metric_components(1.0)
        assert result["g_xx"] == pytest.approx(1.0)

    def test_g_xx_at_a_equals_2(self):
        result = flrw_metric_components(2.0)
        assert result["g_xx"] == pytest.approx(4.0)

    def test_spatial_components_equal(self):
        result = flrw_metric_components(3.0)
        assert result["g_yy"] == pytest.approx(result["g_xx"])
        assert result["g_zz"] == pytest.approx(result["g_xx"])

    def test_signature_tuple(self):
        result = flrw_metric_components(1.0)
        assert result["signature"] == (-1, +1, +1, +1)

    def test_value_error_for_zero_a(self):
        with pytest.raises(ValueError):
            flrw_metric_components(0.0)

    def test_value_error_for_negative_a(self):
        with pytest.raises(ValueError):
            flrw_metric_components(-1.0)

    def test_determinant_negative(self):
        result = flrw_metric_components(2.0)
        assert result["determinant"] < 0

    def test_determinant_value_at_a_equals_2(self):
        result = flrw_metric_components(2.0)
        assert result["determinant"] == pytest.approx(-(2.0 ** 6))


# ---------------------------------------------------------------------------
# TestUmInternalDof (8 tests)
# ---------------------------------------------------------------------------

class TestUmInternalDof:
    def test_returns_dict(self):
        result = um_internal_dof()
        assert isinstance(result, dict)

    def test_winding_number(self):
        result = um_internal_dof()
        assert result["winding_number"] == 5

    def test_cs_level(self):
        result = um_internal_dof()
        assert result["cs_level"] == 74

    def test_radion_R_kk_m(self):
        result = um_internal_dof()
        assert result["radion_R_kk_m"] == pytest.approx(R_KK_M, rel=1e-9)

    def test_extra_dims(self):
        result = um_internal_dof()
        assert result["extra_dims"] == 1

    def test_phi0_close_to_pi_over_4(self):
        result = um_internal_dof()
        assert result["phi0"] == pytest.approx(math.pi / 4, rel=1e-3)

    def test_orbifold(self):
        result = um_internal_dof()
        assert result["orbifold"] == "S¹/Z₂"

    def test_n_free_parameters(self):
        result = um_internal_dof()
        assert result["n_free_parameters"] == 0

    def test_braided_sound_speed(self):
        result = um_internal_dof()
        assert result["braided_sound_speed"] == pytest.approx(12.0 / 37.0, rel=1e-6)


# ---------------------------------------------------------------------------
# TestUnified5dMetric (12 tests)
# ---------------------------------------------------------------------------

class TestUnified5dMetric:
    def test_returns_dict(self):
        result = unified_5d_metric(1.0, 0.0, R_KK_M)
        assert isinstance(result, dict)

    def test_has_11_keys(self):
        result = unified_5d_metric(1.0, 0.0, R_KK_M)
        assert len(result) == 11

    def test_g_00_is_minus_one(self):
        result = unified_5d_metric(2.0, 0.5, R_KK_M)
        assert result["g_00"] == pytest.approx(-1.0)

    def test_g_11_equals_a_squared(self):
        a = 3.0
        result = unified_5d_metric(a, 0.0, R_KK_M)
        assert result["g_11"] == pytest.approx(a ** 2)

    def test_off_diagonal_is_zero(self):
        result = unified_5d_metric(1.0, 0.0, R_KK_M)
        assert result["off_diagonal"] == pytest.approx(0.0)

    def test_dimensions_is_5(self):
        result = unified_5d_metric(1.0, 0.0, R_KK_M)
        assert result["dimensions"] == 5

    def test_signature_5d(self):
        result = unified_5d_metric(1.0, 0.0, R_KK_M)
        assert result["signature"] == (-1, +1, +1, +1, +1)

    def test_value_error_for_a_zero(self):
        with pytest.raises(ValueError):
            unified_5d_metric(0.0, 0.0, R_KK_M)

    def test_value_error_for_R_kk_zero(self):
        with pytest.raises(ValueError):
            unified_5d_metric(1.0, 0.0, 0.0)

    def test_g_44_positive(self):
        result = unified_5d_metric(1.0, 0.5, R_KK_M)
        assert result["g_44"] > 0

    def test_g_44_equals_one_at_natural_values(self):
        # R_kk = R_KK_M → ρ=1; phi_val=0 → g_44 = 1²*(1+0) = 1
        result = unified_5d_metric(1.0, 0.0, R_KK_M)
        assert result["g_44"] == pytest.approx(1.0)

    def test_g_11_at_a_equals_2(self):
        result = unified_5d_metric(2.0, 0.0, R_KK_M)
        assert result["g_11"] == pytest.approx(4.0)

    def test_g_44_increases_with_phi_val(self):
        r1 = unified_5d_metric(1.0, 0.0, R_KK_M)
        r2 = unified_5d_metric(1.0, 1.0, R_KK_M)
        assert r2["g_44"] > r1["g_44"]


# ---------------------------------------------------------------------------
# TestKaluzaKleinReduction (12 tests)
# ---------------------------------------------------------------------------

class TestKaluzaKleinReduction:
    def test_returns_dict(self):
        result = kaluza_klein_reduction(1.0, R_KK_M)
        assert isinstance(result, dict)

    def test_has_all_keys(self):
        result = kaluza_klein_reduction(1.0, R_KK_M)
        for key in (
            "g_tt_4d", "g_xx_4d", "g_yy_4d", "g_zz_4d",
            "radion_sigma", "g_eff_normalized", "flrw_recovered",
            "reduction_method", "kk_mass_scale_mpl",
        ):
            assert key in result

    def test_g_tt_4d_is_minus_one(self):
        result = kaluza_klein_reduction(1.0, R_KK_M)
        assert result["g_tt_4d"] == pytest.approx(-1.0)

    def test_g_xx_4d_at_a_equals_1(self):
        result = kaluza_klein_reduction(1.0, R_KK_M)
        assert result["g_xx_4d"] == pytest.approx(1.0)

    def test_flrw_recovered_is_bool_true(self):
        result = kaluza_klein_reduction(1.0, R_KK_M)
        assert result["flrw_recovered"] is True

    def test_radion_sigma_zero_at_natural_radius(self):
        result = kaluza_klein_reduction(1.0, R_KK_M)
        assert result["radion_sigma"] == pytest.approx(0.0, abs=1e-12)

    def test_value_error_for_a_zero(self):
        with pytest.raises(ValueError):
            kaluza_klein_reduction(0.0, R_KK_M)

    def test_value_error_for_a_negative(self):
        with pytest.raises(ValueError):
            kaluza_klein_reduction(-1.0, R_KK_M)

    def test_value_error_for_R_kk_zero(self):
        with pytest.raises(ValueError):
            kaluza_klein_reduction(1.0, 0.0)

    def test_value_error_for_R_kk_negative(self):
        with pytest.raises(ValueError):
            kaluza_klein_reduction(1.0, -R_KK_M)

    def test_g_eff_normalized_one_at_natural_radius(self):
        result = kaluza_klein_reduction(1.0, R_KK_M)
        assert result["g_eff_normalized"] == pytest.approx(1.0)

    def test_radion_sigma_positive_for_larger_R_kk(self):
        result = kaluza_klein_reduction(1.0, 2.0 * R_KK_M)
        assert result["radion_sigma"] > 0.0


# ---------------------------------------------------------------------------
# TestMetricUnificationProof (8 tests)
# ---------------------------------------------------------------------------

class TestMetricUnificationProof:
    def test_returns_list(self):
        result = metric_unification_proof()
        assert isinstance(result, list)

    def test_at_least_5_steps(self):
        result = metric_unification_proof()
        assert len(result) >= 5

    def test_each_step_is_dict(self):
        for step in metric_unification_proof():
            assert isinstance(step, dict)

    def test_each_step_has_required_keys(self):
        for step in metric_unification_proof():
            assert "step" in step
            assert "title" in step
            assert "statement" in step

    def test_steps_numbered_sequentially(self):
        steps = metric_unification_proof()
        for i, step in enumerate(steps, start=1):
            assert step["step"] == i

    def test_all_titles_non_empty(self):
        for step in metric_unification_proof():
            assert len(step["title"]) > 0

    def test_all_statements_non_empty(self):
        for step in metric_unification_proof():
            assert len(step["statement"]) > 0

    def test_first_step_mentions_ansatz_or_5d(self):
        first = metric_unification_proof()[0]
        text = (first["title"] + " " + first["statement"]).lower()
        assert "ansatz" in text or "5d" in text

    def test_last_step_mentions_flrw_or_recovery(self):
        last = metric_unification_proof()[-1]
        text = (last["title"] + " " + last["statement"]).lower()
        assert "flrw" in text or "recovery" in text or "recover" in text


# ---------------------------------------------------------------------------
# TestEffective4dMetric (5 tests)
# ---------------------------------------------------------------------------

class TestEffective4dMetric:
    def test_returns_dict(self):
        result = effective_4d_metric(1.0)
        assert isinstance(result, dict)

    def test_g_tt_is_minus_one(self):
        result = effective_4d_metric(2.0)
        assert result["g_tt"] == pytest.approx(-1.0)

    def test_g_xx_equals_a_squared(self):
        a = 3.0
        result = effective_4d_metric(a)
        assert result["g_xx"] == pytest.approx(a ** 2)

    def test_radion_stabilized_true(self):
        result = effective_4d_metric(1.0)
        assert result["radion_stabilized"] is True

    def test_radion_sigma_zero(self):
        result = effective_4d_metric(1.0)
        assert result["radion_sigma"] == pytest.approx(0.0)

    def test_um_correction_zero(self):
        result = effective_4d_metric(1.0)
        assert result["um_correction"] == pytest.approx(0.0)
