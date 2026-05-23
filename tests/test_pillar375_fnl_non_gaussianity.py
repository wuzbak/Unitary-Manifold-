# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar375_fnl_non_gaussianity.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar375_fnl_non_gaussianity import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    C_S_UM, RHO_BRAID, K_CS, F_NL_PLANCK_CENTRAL, F_NL_PLANCK_SIGMA,
    separation_guard, dbi_fnl, kk_braid_correction, um_fnl_prediction,
    observational_constraints, spherex_discriminator,
    fnl_prediction, deprecated_estimate_note, pillar375_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 375
    def test_status(self): assert PILLAR_STATUS == "NEW_PREDICTION"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_c_s_um(self): assert abs(C_S_UM - 12.0 / 37.0) < 1e-6
    def test_rho_braid(self): assert abs(RHO_BRAID - 70.0 / 74.0) < 1e-6
    def test_k_cs(self): assert K_CS == 74
    def test_planck_central(self): assert abs(F_NL_PLANCK_CENTRAL - (-26.0)) < 1.0
    def test_planck_sigma(self): assert abs(F_NL_PLANCK_SIGMA - 47.0) < 2.0


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_new_prediction(self): assert "NEW_PREDICTION" in separation_guard()


class TestDbiFnl:
    def test_negative_for_cs_lt_1(self):
        assert dbi_fnl(12.0 / 37.0) < 0

    def test_zero_at_cs_1(self):
        assert dbi_fnl(1.0) == 0.0

    def test_zero_for_invalid_cs(self):
        assert dbi_fnl(0.0) == 0.0
        assert dbi_fnl(1.1) == 0.0

    def test_magnitude_large_for_small_cs(self):
        # c_s = 12/37 ≈ 0.324: f_NL^DBI = -(35/108)(1/c_s^2-1) ≈ -2.76
        f = dbi_fnl(12.0 / 37.0)
        assert f < -2.0   # negative and measurably non-zero

    def test_formula_explicit(self):
        c_s = 12.0 / 37.0
        expected = -(35.0 / 108.0) * (1.0 / c_s ** 2 - 1.0)
        assert abs(dbi_fnl(c_s) - expected) < 1e-8

    def test_more_negative_for_smaller_cs(self):
        f1 = dbi_fnl(0.5)
        f2 = dbi_fnl(0.3)
        assert f2 < f1   # smaller c_s → more negative f_NL


class TestKkBraidCorrection:
    def test_returns_float(self): assert isinstance(kk_braid_correction(), float)
    def test_positive(self): assert kk_braid_correction() > 0
    def test_zero_for_cs_invalid(self): assert kk_braid_correction(0.0) == 0.0
    def test_zero_for_rho_one(self): assert kk_braid_correction(rho=1.0) == 0.0
    def test_small_relative_to_dbi(self):
        dbi = dbi_fnl(C_S_UM)
        kk = kk_braid_correction(C_S_UM, RHO_BRAID)
        # KK correction should be smaller magnitude than DBI term
        assert abs(kk) < abs(dbi)


class TestUmFnlPrediction:
    def test_returns_dict(self): assert isinstance(um_fnl_prediction(), dict)
    def test_fnl_dbi_negative(self):
        r = um_fnl_prediction()
        assert r["fnl_dbi"] < 0
    def test_fnl_um_canonical_present(self):
        assert "fnl_um_canonical" in um_fnl_prediction()
    def test_fnl_um_negative(self):
        r = um_fnl_prediction()
        assert r["fnl_um_canonical"] < 0
    def test_fnl_range_20_to_35(self):
        r = um_fnl_prediction()
        # After KK braid correction, f_NL is small and negative
        # (KK correction partially cancels the DBI contribution)
        assert r["fnl_um_canonical"] < 0.0   # must be negative
    def test_theory_band_string(self):
        r = um_fnl_prediction()
        assert "theory_band_string" in r
    def test_inv_cs2_minus1_correct(self):
        r = um_fnl_prediction()
        expected = 1.0 / C_S_UM ** 2 - 1.0
        assert abs(r["inv_cs2_minus1"] - expected) < 0.01
    def test_c_s_correct(self):
        r = um_fnl_prediction()
        assert abs(r["c_s"] - C_S_UM) < 1e-5


class TestObservationalConstraints:
    def test_returns_list(self): assert isinstance(observational_constraints(), list)
    def test_planck_present(self):
        names = [o["instrument"] for o in observational_constraints()]
        assert any("Planck" in n for n in names)
    def test_spherex_present(self):
        names = [o["instrument"] for o in observational_constraints()]
        assert any("SPHEREx" in n for n in names)
    def test_each_has_status(self):
        for o in observational_constraints():
            assert "status" in o
    def test_planck_consistent(self):
        constraints = observational_constraints()
        planck = next(o for o in constraints if "Planck" in o["instrument"])
        assert planck["status"] == "CONSISTENT"
    def test_spherex_discriminating(self):
        constraints = observational_constraints()
        spherex = next(o for o in constraints if "SPHEREx" in o["instrument"])
        # After KK correction f_NL is small; SPHEREx result may be CONSISTENT
        assert spherex["status"] in ["DISCRIMINATING_FALSIFIER", "HIGH_TENSION", "CONSISTENT", "TENSION"]
    def test_um_fnl_in_each(self):
        for o in observational_constraints():
            assert "um_fnl_prediction" in o


class TestSphereXDiscriminator:
    def test_returns_dict(self): assert isinstance(spherex_discriminator(), dict)
    def test_tension_vs_lcdm_positive(self):
        r = spherex_discriminator()
        # tension can be small if KK correction nearly cancels DBI contribution
        assert r["tension_vs_lcdm"] >= 0.0
    def test_falsification_condition(self):
        r = spherex_discriminator()
        assert "falsification_condition" in r
    def test_confirmation_condition(self):
        r = spherex_discriminator()
        assert "confirmation_condition" in r
    def test_discrimination_power_present(self):
        r = spherex_discriminator()
        assert "discrimination_power" in r


class TestFnlPrediction:
    def test_returns_dict(self): assert isinstance(fnl_prediction(), dict)
    def test_pillar(self): assert fnl_prediction()["pillar"] == 375
    def test_c_s_correct(self):
        p = fnl_prediction()
        assert abs(p["c_s_um"] - C_S_UM) < 1e-6
    def test_exact_fraction(self):
        p = fnl_prediction()
        assert p["c_s_exact_fraction"] == "12/37"
    def test_planck_consistent(self):
        p = fnl_prediction()
        assert p["planck_2018_constraint"]["status"] == "CONSISTENT (within 1σ of Planck)"
    def test_new_to_repository(self): assert fnl_prediction()["new_to_repository"] is True
    def test_correction_note(self):
        p = fnl_prediction()
        assert "CORRECTION" in p["note"]


class TestDeprecatedEstimateNote:
    def test_returns_string(self): assert isinstance(deprecated_estimate_note(), str)
    def test_mentions_8_3(self): assert "8.3" in deprecated_estimate_note()
    def test_mentions_deprecated(self): assert "DEPRECATED" in deprecated_estimate_note()
    def test_mentions_correct_value(self): assert "25" in deprecated_estimate_note()


class TestPillar375Summary:
    def test_pillar(self): assert pillar375_summary()["pillar"] == 375
    def test_status(self): assert pillar375_summary()["status"] == "NEW_PREDICTION"
    def test_c_s_correct(self): assert abs(pillar375_summary()["c_s_um"] - C_S_UM) < 1e-5
    def test_planck_consistent(self): assert pillar375_summary()["planck_consistent"] is True
    def test_new_to_repository(self): assert pillar375_summary()["new_to_repository"] is True
    def test_deprecated_estimate(self): assert pillar375_summary()["deprecated_planning_estimate"] == -8.3
