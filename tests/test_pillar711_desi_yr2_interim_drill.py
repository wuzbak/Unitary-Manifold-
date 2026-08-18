# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 711 — DESI Year 2 interim drill."""
from __future__ import annotations

import re

import pytest

from src.core.pillar711_desi_yr2_interim_drill import (
    DESI_DR3_SIGMA_WA,
    DESI_YR2_SIGMA_WA,
    DESI_YR2_WA,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SURVIVAL_THRESHOLD_DR3_WA,
    WA_UM,
    W0_UM,
    desi_2027_preregistration,
    desi_dr3_projection,
    desi_yr2_interim_verdict,
    wa_tension_drill,
)

YR2 = desi_yr2_interim_verdict()
DR3 = desi_dr3_projection()
PREREG = desi_2027_preregistration()


class TestConstants:
    def test_identity(self):
        assert PILLAR_NUMBER == 711
        assert PILLAR_STATUS == "DESI_YR2_INTERIM_DRILL_CERTIFIED"
        assert PILLAR_TITLE == "DESI Year 2 Interim Drill"

    def test_core_constants(self):
        assert WA_UM == 0.0
        assert W0_UM == pytest.approx(-0.9302)
        assert DESI_YR2_WA == pytest.approx(-0.52)
        assert DESI_YR2_SIGMA_WA == pytest.approx(0.26)
        assert DESI_DR3_SIGMA_WA == pytest.approx(0.18)


class TestWaDrill:
    def test_year2_tension_exact(self):
        result = wa_tension_drill()
        assert result["tension_sigma"] == pytest.approx(2.0)
        assert result["status"] == "TENSION"

    def test_pass_branch(self):
        result = wa_tension_drill(-0.1, 0.2)
        assert result["status"] == "PASS"

    def test_falsified_branch(self):
        result = wa_tension_drill(-0.61, 0.2)
        assert result["status"] == "FALSIFIED"

    def test_invalid_sigma(self):
        with pytest.raises(ValueError):
            wa_tension_drill(-0.52, 0.0)


class TestInterimVerdict:
    def test_interim_status(self):
        assert YR2["status"] == "TENSION"
        assert YR2["verdict"] == "TENSION"
        assert YR2["falsified"] is False

    def test_interim_w0_tension(self):
        assert YR2["w0_tension_sigma"] == pytest.approx(abs(-0.84 - W0_UM) / 0.06)

    def test_dr3_projection(self):
        assert DR3["projected_tension_sigma"] == pytest.approx(abs(DESI_YR2_WA - WA_UM) / DESI_DR3_SIGMA_WA)
        assert DR3["status"] == "TENSION"
        assert DR3["survives_at_current_central"] is True

    def test_cutoffs(self):
        assert DR3["survival_cutoff_wa"] == pytest.approx(SURVIVAL_THRESHOLD_DR3_WA)
        assert DR3["falsification_cutoff_wa"] == pytest.approx(-0.54)


class TestPreregistration:
    def test_hash_shape(self):
        assert re.fullmatch(r"[0-9a-f]{64}", PREREG["sha256"]) is not None

    def test_payload_mentions_cutoff(self):
        assert "-0.36" in PREREG["payload"]

    def test_falsification_cutoff_abs(self):
        assert PREREG["falsification_cutoff_abs_wa"] == pytest.approx(0.54)
