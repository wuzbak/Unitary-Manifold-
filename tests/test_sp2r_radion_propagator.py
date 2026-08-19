# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from __future__ import annotations

import pytest

from src.core.sp2r_radion_propagator import (
    DIM_13,
    EPISTEMIC_STATUS,
    M_PL_GEV,
    PILLAR_NUMBER,
    RADION_INDEX,
    STATUS,
    propagator_uv_scaling,
    radion_propagator_standard,
    sp2r_modified_propagator,
    sp2r_null_cone_constraints,
    sp2r_radion_propagator_report,
    sp2r_uv_form_factor,
    uv_fixed_point_probe,
)


class TestMetadata:
    def test_constants(self):
        assert PILLAR_NUMBER == 779
        assert STATUS == "SP2R_UV_IMPROVED"
        assert EPISTEMIC_STATUS == "UV_IMPROVED"
        assert DIM_13 == 13
        assert RADION_INDEX == 12


class TestConstraints:
    def test_constraints_count(self):
        r = sp2r_null_cone_constraints()
        assert len(r["constraints"]) == 3

    def test_invalid_dimension_raises(self):
        with pytest.raises(ValueError):
            sp2r_null_cone_constraints(2)

    def test_gauge_fixed_second_time(self):
        r = sp2r_null_cone_constraints()
        assert r["gauge_fixed_second_time"] is True


class TestStandardPropagator:
    def test_negative_p2_raises(self):
        with pytest.raises(ValueError):
            radion_propagator_standard(-1.0)

    def test_positive_propagator(self):
        r = radion_propagator_standard(0.0)
        assert r["propagator_gev_minus2"] > 0.0

    def test_propagator_decreases_with_p2(self):
        low = radion_propagator_standard(1.0)["propagator_gev_minus2"]
        high = radion_propagator_standard(10.0)["propagator_gev_minus2"]
        assert high < low


class TestUVFormFactor:
    def test_form_factor_is_one_at_zero(self):
        r = sp2r_uv_form_factor(0.0)
        assert r["form_factor"] == pytest.approx(1.0)

    def test_large_p2_suppresses(self):
        r = sp2r_uv_form_factor(M_PL_GEV * M_PL_GEV)
        assert r["form_factor"] == pytest.approx(0.5)

    def test_invalid_planck_mass_raises(self):
        with pytest.raises(ValueError):
            sp2r_uv_form_factor(1.0, m_pl_gev=0.0)


class TestModifiedPropagator:
    def test_modified_is_not_larger_than_standard(self):
        r = sp2r_modified_propagator(10.0)
        assert r["modified_propagator_gev_minus2"] <= r["standard_propagator_gev_minus2"]

    def test_uv_behavior_label(self):
        r = sp2r_modified_propagator(1.0)
        assert r["uv_behavior"] == "UV_SOFTER_1_OVER_P4"


class TestFixedPointAndScaling:
    def test_fixed_point_proxy_positive(self):
        r = uv_fixed_point_probe()
        assert r["fixed_point_exists_proxy"] is True
        assert r["g5_star_proxy"] > 0.0

    def test_invalid_bulk_dimension_raises(self):
        with pytest.raises(ValueError):
            uv_fixed_point_probe(d_bulk=2)

    def test_scaling_ratios_match_expectation(self):
        r = propagator_uv_scaling()
        assert r["standard_ratio"] == pytest.approx(r["expected_standard_ratio"], rel=1e-3)
        assert r["modified_ratio"] == pytest.approx(r["expected_modified_ratio"], rel=1e-3)

    def test_report_contains_sections(self):
        r = sp2r_radion_propagator_report()
        for key in ["constraints", "sample_standard", "sample_modified", "uv_scaling", "fixed_point_probe"]:
            assert key in r
