# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 631 — DESI DR3 rolling-radion falsification response protocol."""
from __future__ import annotations

import pytest

from src.core.pillar631_desi_dr3_falsification_response import (
    ARCHITECTURE_TRIGGER_FIRED,
    FALSIFICATION_THRESHOLD,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    ROLLING_RADION_EPS_GW_NATURAL,
    ROLLING_RADION_EPS_GW_REQUIRED,
    ROMAN_ST_SIGMA_WA,
    SIGMA_DR2_WA_1D,
    SIGMA_DR3_PROJECTED_1D,
    SIX_D_DILATON_WA_FORMULA,
    VERSION,
    architecture_trigger,
    desi_dr3_response_branch,
    pillar_report,
    rolling_radion_extension_spec,
    roman_st_cross_check,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
BRANCH = desi_dr3_response_branch()
SPEC = rolling_radion_extension_spec()
ROMAN = roman_st_cross_check()
TRIGGER = architecture_trigger()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 631

    def test_status(self):
        assert PILLAR_STATUS == "DESI_DR3_FALSIFICATION_RESPONSE_PREREGISTERED"

    def test_version(self):
        assert VERSION == "v20.9"

    def test_sigma_dr2_below_threshold(self):
        assert SIGMA_DR2_WA_1D < FALSIFICATION_THRESHOLD

    def test_sigma_dr3_above_threshold(self):
        assert SIGMA_DR3_PROJECTED_1D >= FALSIFICATION_THRESHOLD

    def test_architecture_trigger_fired(self):
        assert ARCHITECTURE_TRIGGER_FIRED is True

    def test_fine_tuning_ratio(self):
        ratio = ROLLING_RADION_EPS_GW_REQUIRED / ROLLING_RADION_EPS_GW_NATURAL
        assert ratio < 1e-50

    def test_six_d_formula_basic(self):
        wa = SIX_D_DILATON_WA_FORMULA(0.30)
        assert wa < 0.0
        assert abs(wa - (-2 * 0.30 / 0.70)) < 1e-12

    def test_six_d_formula_zero_eps(self):
        assert SIX_D_DILATON_WA_FORMULA(0.0) == 0.0

    def test_six_d_formula_invalid(self):
        with pytest.raises(ValueError):
            SIX_D_DILATON_WA_FORMULA(-0.1)
        with pytest.raises(ValueError):
            SIX_D_DILATON_WA_FORMULA(1.0)


class TestResponseBranch:
    def test_pass_branch(self):
        r = desi_dr3_response_branch(1.5)
        assert r["branch"] == "PASS"
        assert r["extension_activated"] is False

    def test_tension_branch(self):
        r = desi_dr3_response_branch(2.5)
        assert r["branch"] == "TENSION"
        assert r["extension_activated"] is False

    def test_falsified_branch(self):
        r = desi_dr3_response_branch(3.5)
        assert r["branch"] == "FALSIFIED"
        assert r["extension_activated"] is True

    def test_projected_branch(self):
        assert BRANCH["branch"] == "FALSIFIED"
        assert BRANCH["extension_activated"] is True

    def test_invalid_sigma(self):
        with pytest.raises(ValueError):
            desi_dr3_response_branch(-1.0)


class TestRollingRadionSpec:
    def test_keys(self):
        for key in ["architecture_limit_reason", "replacement_geometry", "wa_formula",
                    "eps_gw_natural", "eps_gw_required_for_desi", "fine_tuning_ratio"]:
            assert key in SPEC

    def test_6d_dilaton_geometry(self):
        assert "6D" in SPEC["replacement_geometry"]

    def test_wa_6d_negative(self):
        assert SPEC["wa_6d_at_target"] < 0.0


class TestRomanST:
    def test_cross_check_activated(self):
        assert ROMAN["cross_check_activated"] is True

    def test_sigma_wa(self):
        assert ROMAN_ST_SIGMA_WA < 0.2


class TestArchitectureTrigger:
    def test_fired(self):
        assert TRIGGER["fired"] is True

    def test_nominated_replacement(self):
        assert "6D" in TRIGGER["nominated_replacement"]


class TestReport:
    def test_keys(self):
        for key in ["pillar", "title", "status", "version", "adjacent_track",
                    "desi_dr3_response_branch", "rolling_radion_extension_spec",
                    "roman_st_cross_check", "architecture_trigger",
                    "what_is_claimed", "what_is_NOT_claimed"]:
            assert key in REPORT

    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims_nonempty(self):
        assert len(what_is_claimed()) >= 5
        assert len(what_is_NOT_claimed()) >= 4
