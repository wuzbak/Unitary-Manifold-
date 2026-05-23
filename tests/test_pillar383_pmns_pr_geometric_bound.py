# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar383_pmns_pr_geometric_bound.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar383_pmns_pr_geometric_bound import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    N_W, K_CS, P_R_EFF, P_R_PMNS_UPPER, P_R_GEOM_LOWER,
    C_R_VALUES, THETA23_SQ, THETA13_COS_SQ,
    separation_guard,
    c_r_from_bc,
    wavefunction_profile_R,
    overlap_integral_LR,
    geometric_pr_lower_bound,
    pmns_pr_upper_bound,
    pr_geometric_bound_interval,
    pr_consistency_check,
    p17_status_upgrade,
    pillar383_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 383
    def test_status(self): assert PILLAR_STATUS == "BOUNDED_FROM_GEOMETRY"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_n_w(self): assert N_W == 5
    def test_k_cs(self): assert K_CS == 74
    def test_p_r_eff(self): assert abs(P_R_EFF - 0.364) < 0.001
    def test_p_r_pmns_upper(self): assert abs(P_R_PMNS_UPPER - THETA23_SQ * THETA13_COS_SQ) < 1e-10
    def test_p_r_geom_lower(self): assert P_R_GEOM_LOWER > 0
    def test_c_r_values_count(self): assert len(C_R_VALUES) == 3
    def test_c_r_1(self): assert abs(C_R_VALUES[0] - 0.3) < 1e-6
    def test_c_r_2(self): assert abs(C_R_VALUES[1] - 0.1) < 1e-6
    def test_c_r_3(self): assert abs(C_R_VALUES[2] + 0.1) < 1e-6
    def test_theta23_sq_between_0_and_1(self): assert 0 < THETA23_SQ < 1
    def test_theta13_cos_sq_between_0_and_1(self): assert 0 < THETA13_COS_SQ < 1


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_bounded_from_geometry(self): assert "BOUNDED_FROM_GEOMETRY" in separation_guard()
    def test_p_r_in_string(self): assert "p_R" in separation_guard() or "0.364" in separation_guard()


class TestCRFromBC:
    def test_n1(self): assert abs(c_r_from_bc(1) - 0.3) < 1e-10
    def test_n2(self): assert abs(c_r_from_bc(2) - 0.1) < 1e-10
    def test_n3(self): assert abs(c_r_from_bc(3) + 0.1) < 1e-10
    def test_n5(self): assert abs(c_r_from_bc(5) + 0.5) < 1e-10
    def test_formula(self):
        for n in range(1, 6):
            assert abs(c_r_from_bc(n) - (0.5 - n / N_W)) < 1e-10
    def test_invalid_n(self):
        with pytest.raises(ValueError):
            c_r_from_bc(0)


class TestWavefunctionProfileR:
    def test_returns_float(self):
        f = wavefunction_profile_R(0.5, 0.3)
        assert isinstance(f, float)

    def test_positive(self):
        f = wavefunction_profile_R(0.5, 0.3)
        assert f > 0

    def test_decreases_with_y(self):
        f0 = wavefunction_profile_R(0.0, 0.3)
        f1 = wavefunction_profile_R(1.0, 0.3)
        assert f0 > f1  # right-handed: decreases toward IR

    def test_different_c_r_values(self):
        f_c1 = wavefunction_profile_R(0.5, 0.3)
        f_c2 = wavefunction_profile_R(0.5, 0.1)
        # Both should be positive
        assert f_c1 > 0
        assert f_c2 > 0


class TestOverlapIntegralLR:
    def test_returns_float(self):
        i = overlap_integral_LR()
        assert isinstance(i, float)

    def test_finite(self):
        i = overlap_integral_LR()
        assert math.isfinite(i)

    def test_positive(self):
        i = overlap_integral_LR()
        assert i > 0

    def test_varies_with_c_r(self):
        i1 = overlap_integral_LR(c_r=0.3)
        i2 = overlap_integral_LR(c_r=0.1)
        # Different c_r values → different overlaps
        assert i1 != i2

    def test_custom_n_steps(self):
        i1 = overlap_integral_LR(n_steps=50)
        i2 = overlap_integral_LR(n_steps=100)
        # Should converge (within ~10%)
        assert abs(i1 - i2) / abs(i2) < 0.2


class TestGeometricPrLowerBound:
    def test_returns_dict(self): assert isinstance(geometric_pr_lower_bound(), dict)

    def test_p_r_geom_positive(self):
        r = geometric_pr_lower_bound()
        assert r["p_r_geom"] > 0

    def test_i_lr_finite(self):
        r = geometric_pr_lower_bound()
        assert math.isfinite(r["i_lr_1"])

    def test_lower_bound_derived(self):
        r = geometric_pr_lower_bound()
        assert "LOWER_BOUND" in r["verdict"]

    def test_c_r_1_correct(self):
        r = geometric_pr_lower_bound()
        assert abs(r["c_r_1"] - 0.3) < 1e-6

    def test_c_l_0_correct(self):
        r = geometric_pr_lower_bound()
        assert abs(r["c_l_0"] - 0.4) < 1e-6


class TestPMNSPrUpperBound:
    def test_returns_dict(self): assert isinstance(pmns_pr_upper_bound(), dict)

    def test_upper_bound_value(self):
        r = pmns_pr_upper_bound()
        expected = THETA23_SQ * THETA13_COS_SQ
        assert abs(r["p_r_upper"] - expected) < 1e-10

    def test_upper_bound_less_than_1(self):
        r = pmns_pr_upper_bound()
        assert r["p_r_upper"] < 1.0

    def test_upper_bound_positive(self):
        r = pmns_pr_upper_bound()
        assert r["p_r_upper"] > 0

    def test_verdict_upper_bound(self):
        r = pmns_pr_upper_bound()
        assert "UPPER_BOUND" in r["verdict"]


class TestPrGeometricBoundInterval:
    def test_returns_dict(self): assert isinstance(pr_geometric_bound_interval(), dict)

    def test_p_r_min_positive(self):
        r = pr_geometric_bound_interval()
        assert r["p_r_min"] > 0

    def test_p_r_max_less_than_1(self):
        r = pr_geometric_bound_interval()
        assert r["p_r_max"] < 1.0

    def test_interval_ordered(self):
        r = pr_geometric_bound_interval()
        assert r["p_r_min"] < r["p_r_max"]

    def test_p_r_eff_in_interval(self):
        r = pr_geometric_bound_interval()
        assert r["p_r_eff_in_interval"] is True

    def test_verdict_consistent(self):
        r = pr_geometric_bound_interval()
        assert "consistent" in r["verdict"].lower() or "INTERVAL" in r["verdict"]


class TestPrConsistencyCheck:
    def test_returns_dict(self): assert isinstance(pr_consistency_check(), dict)

    def test_p_r_in_interval(self):
        r = pr_consistency_check()
        assert r["in_interval"] is True

    def test_discrepancy_factor_large(self):
        r = pr_consistency_check()
        assert r["discrepancy_factor"] > 1000  # > O(10³)

    def test_status_consistent(self):
        r = pr_consistency_check()
        assert "CONSISTENT" in r["status"]

    def test_c_r_mode_values(self):
        r = pr_consistency_check()
        assert len(r["c_r_mode_values"]) == 3


class TestP17StatusUpgrade:
    def test_returns_dict(self): assert isinstance(p17_status_upgrade(), dict)

    def test_all_conditions_met(self):
        r = p17_status_upgrade()
        assert r["all_conditions_met"] is True

    def test_previous_status(self):
        r = p17_status_upgrade()
        assert "CONDITIONAL_DERIVATION" in r["previous_status"]

    def test_new_status(self):
        r = p17_status_upgrade()
        assert r["new_status"] == "BOUNDED_FROM_GEOMETRY"

    def test_derivation_5_steps(self):
        r = p17_status_upgrade()
        assert len(r["derivation_chain"]) == 5

    def test_certificate_status(self):
        r = p17_status_upgrade()
        assert "BOUNDED_FROM_GEOMETRY" in r["certificate_status"]

    def test_p_r_eff_in_interval(self):
        r = p17_status_upgrade()
        lo, hi = r["bound_interval"]
        assert lo <= P_R_EFF <= hi


class TestPillar383Summary:
    def test_returns_dict(self): assert isinstance(pillar383_summary(), dict)
    def test_pillar_number(self):
        r = pillar383_summary()
        assert r["pillar_number"] == PILLAR_NUMBER
    def test_status(self):
        r = pillar383_summary()
        assert r["status"] == "BOUNDED_FROM_GEOMETRY"
    def test_key_result_mentions_pr(self):
        r = pillar383_summary()
        assert "p_R" in r["key_result"] or "0.364" in r["key_result"]
    def test_previous_status(self):
        r = pillar383_summary()
        assert r["previous_status"] == "CONDITIONAL_DERIVATION"
    def test_new_status(self):
        r = pillar383_summary()
        assert r["new_status"] == "BOUNDED_FROM_GEOMETRY"
