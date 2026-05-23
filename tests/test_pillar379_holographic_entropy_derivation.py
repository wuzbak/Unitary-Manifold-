# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar379_holographic_entropy_derivation.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar379_holographic_entropy_derivation import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    G5_NATURAL, PHI0_PLANCK, R_C, G_N_4D, PI,
    separation_guard,
    kk_reduction_g_newton,
    ftum_entropy_fixedpoint,
    bekenstein_hawking_4d,
    entropy_matching,
    p6_derivation_chain,
    p6_upgrade_certificate,
    pillar379_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 379
    def test_status(self): assert PILLAR_STATUS == "DERIVED_CONDITIONAL"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_g5_natural(self): assert G5_NATURAL == 1.0
    def test_phi0_planck(self): assert PHI0_PLANCK == 1.0
    def test_r_c(self): assert R_C == PHI0_PLANCK
    def test_g_n_4d_formula(self):
        assert abs(G_N_4D - G5_NATURAL / (PI * R_C)) < 1e-10
    def test_g_n_4d_positive(self): assert G_N_4D > 0
    def test_pi_value(self): assert abs(PI - math.pi) < 1e-10


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_p6(self): assert "P6" in separation_guard()
    def test_derived_conditional(self): assert "DERIVED_CONDITIONAL" in separation_guard()


class TestKKReductionGNewton:
    def test_returns_dict(self): assert isinstance(kk_reduction_g_newton(), dict)

    def test_g_n_4d_positive(self):
        r = kk_reduction_g_newton()
        assert r["g_n_4d"] > 0

    def test_g_n_formula(self):
        r = kk_reduction_g_newton()
        expected = r["g5"] / (math.pi * r["r_c"])
        assert abs(r["g_n_4d"] - expected) < 1e-10

    def test_custom_g5_r_c(self):
        r = kk_reduction_g_newton(g5=2.0, r_c=0.5)
        assert abs(r["g_n_4d"] - 2.0 / (math.pi * 0.5)) < 1e-10

    def test_formula_string_present(self):
        r = kk_reduction_g_newton()
        assert "G_N" in r["formula"]


class TestFTUMEntropyFixedpoint:
    def test_returns_dict(self): assert isinstance(ftum_entropy_fixedpoint(1.0), dict)

    def test_s_star_positive(self):
        r = ftum_entropy_fixedpoint(1.0)
        assert r["s_star_5d"] > 0

    def test_a_5d_greater_than_a_4d(self):
        # A_5D = A_4D × πR_c > A_4D (for πR_c > 1)
        r = ftum_entropy_fixedpoint(1.0)
        if r["r_c"] > 1.0 / math.pi:
            assert r["a_5d"] > r["a_4d"]

    def test_scales_with_area(self):
        r1 = ftum_entropy_fixedpoint(1.0)
        r2 = ftum_entropy_fixedpoint(2.0)
        assert abs(r2["s_star_5d"] / r1["s_star_5d"] - 2.0) < 1e-10

    def test_formula_chain(self):
        r = ftum_entropy_fixedpoint(1.0)
        # S* = A_4D × πR_c / (4G5)
        expected = 1.0 * math.pi * R_C / (4.0 * G5_NATURAL)
        assert abs(r["s_star_5d"] - expected) < 1e-10


class TestBekensteinHawking4D:
    def test_returns_dict(self): assert isinstance(bekenstein_hawking_4d(1.0), dict)

    def test_s_bh_positive(self):
        r = bekenstein_hawking_4d(1.0)
        assert r["s_bh_4d"] > 0

    def test_s_bh_formula(self):
        r = bekenstein_hawking_4d(1.0)
        expected = 1.0 / (4.0 * r["g_n_4d"])
        assert abs(r["s_bh_4d"] - expected) < 1e-10

    def test_scales_with_area(self):
        r1 = bekenstein_hawking_4d(1.0)
        r2 = bekenstein_hawking_4d(4.0)
        assert abs(r2["s_bh_4d"] / r1["s_bh_4d"] - 4.0) < 1e-10


class TestEntropyMatching:
    def test_returns_dict(self): assert isinstance(entropy_matching(), dict)

    def test_exact_match(self):
        r = entropy_matching()
        assert r["s_star_equals_s_bh"] is True

    def test_relative_error_tiny(self):
        r = entropy_matching()
        assert r["relative_error"] < 1e-10

    def test_matching_for_various_areas(self):
        for a in [0.001, 0.1, 1.0, 10.0, 100.0]:
            r = entropy_matching(a)
            assert r["s_star_equals_s_bh"] is True

    def test_key_identity_present(self):
        r = entropy_matching()
        assert "S*(FTUM) = S_BH^{4D}" in r["key_identity"]

    def test_matching_status_exact(self):
        r = entropy_matching()
        assert "EXACT_MATCH" in r["matching_status"]

    def test_s_star_equals_s_bh_numerically(self):
        r = entropy_matching(2.5)
        assert abs(r["s_star_ftum"] - r["s_bh_4d"]) < 1e-10


class TestP6DerivationChain:
    def test_returns_dict(self): assert isinstance(p6_derivation_chain(), dict)

    def test_all_tests_pass(self):
        r = p6_derivation_chain()
        assert r["all_tests_pass"] is True

    def test_previous_status_assumed(self):
        r = p6_derivation_chain()
        assert "ASSUMED" in r["previous_status"]

    def test_new_status_derived(self):
        r = p6_derivation_chain()
        assert "DERIVED" in r["new_status"]

    def test_5_steps(self):
        r = p6_derivation_chain()
        assert len(r["derivation_chain"]) == 5

    def test_prerequisites_listed(self):
        r = p6_derivation_chain()
        prereq_str = " ".join(r["prerequisites"])
        assert "P1" in prereq_str
        assert "P5" in prereq_str


class TestP6UpgradeCertificate:
    def test_returns_dict(self): assert isinstance(p6_upgrade_certificate(), dict)

    def test_all_conditions_met(self):
        r = p6_upgrade_certificate()
        assert r["all_conditions_met"] is True

    def test_new_status_derived(self):
        r = p6_upgrade_certificate()
        assert r["new_status"] == "DERIVED_CONDITIONAL"

    def test_relative_error_tiny(self):
        r = p6_upgrade_certificate()
        assert r["relative_error"] < 1e-10

    def test_certificate_p6(self):
        r = p6_upgrade_certificate()
        assert "P6_DERIVED" in r["certificate_status"]

    def test_impact_present(self):
        r = p6_upgrade_certificate()
        assert "impact" in r
        assert len(r["impact"]) > 50


class TestPillar379Summary:
    def test_returns_dict(self): assert isinstance(pillar379_summary(), dict)
    def test_pillar_number(self):
        r = pillar379_summary()
        assert r["pillar_number"] == PILLAR_NUMBER
    def test_status(self):
        r = pillar379_summary()
        assert r["status"] == "DERIVED_CONDITIONAL"
    def test_foundational_impact(self):
        r = pillar379_summary()
        assert "foundational_impact" in r
    def test_no_assumed_items_claim(self):
        r = pillar379_summary()
        assert "ASSUMED" in r["foundational_impact"] or "assumed" in r["foundational_impact"].lower()
    def test_falsification_present(self):
        r = pillar379_summary()
        assert "falsification" in r
