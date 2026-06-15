# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 529 — Tensor Spectrum NLO KK Graviton Mixing."""

from __future__ import annotations

import math
import pytest

from src.core.tensor_spectrum_nlo_kk import (
    ACT_UPPER_LIMIT,
    DELTA_KK_GRAV,
    K_CS,
    N_W,
    PI_KR,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    R_LO,
    R_NLO,
    act_tension_verdict,
    delta_kk_graviton_mixing,
    pillar529_report,
    r_nlo,
)


class TestPillarMetadata:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 529

    def test_status(self):
        assert PILLAR_STATUS == "TENSOR_NLO_KK_MIXING_CERTIFIED"

    def test_title_mentions_kk(self):
        assert "KK" in PILLAR_TITLE or "Graviton" in PILLAR_TITLE

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_pi_kr(self):
        assert abs(PI_KR - 37.0) < 1e-10


class TestRLO:
    def test_value(self):
        expected = 0.0315
        assert abs(R_LO - expected) < 1e-10

    def test_approximately_0315(self):
        assert abs(R_LO - 0.0315) < 1e-10

    def test_positive(self):
        assert R_LO > 0


class TestDeltaKKGraviton:
    def test_negative(self):
        assert DELTA_KK_GRAV < 0

    def test_small_magnitude(self):
        assert abs(DELTA_KK_GRAV) < 0.02  # < 2%

    def test_formula(self):
        expected = -2.0 * (N_W / K_CS) ** 2
        assert abs(delta_kk_graviton_mixing() - expected) < 1e-12

    def test_matches_constant(self):
        assert abs(delta_kk_graviton_mixing() - DELTA_KK_GRAV) < 1e-12


class TestRNLO:
    def test_below_lo(self):
        assert R_NLO < R_LO

    def test_positive(self):
        assert R_NLO > 0

    def test_close_to_lo(self):
        # NLO correction should be small (< 2%)
        assert abs(R_NLO - R_LO) / R_LO < 0.02

    def test_matches_constant(self):
        assert abs(r_nlo() - R_NLO) < 1e-10

    def test_custom_parameters(self):
        r = r_nlo(R_LO, 5, 74)
        assert abs(r - R_NLO) < 1e-10

    def test_still_above_act_limit(self):
        # NLO correction does NOT resolve ACT tension
        assert R_NLO > ACT_UPPER_LIMIT


class TestACTTensionVerdict:
    def setup_method(self):
        self.v = act_tension_verdict()

    def test_returns_dict(self):
        assert isinstance(self.v, dict)

    def test_r_recorded(self):
        assert abs(self.v["r"] - R_NLO) < 1e-4

    def test_act_upper_limit(self):
        assert self.v["act_upper_limit"] == ACT_UPPER_LIMIT

    def test_passes_act_false(self):
        assert self.v["passes_act"] is False

    def test_verdict_high_tension(self):
        assert self.v["verdict"] == "HIGH_TENSION_ACT"

    def test_architecture_limit_unchanged(self):
        assert self.v["architecture_limit_unchanged"] is True

    def test_custom_r_below_act(self):
        v = act_tension_verdict(0.010)
        assert v["passes_act"] is True
        assert v["verdict"] == "PASSES_ACT"


class TestPillar529Report:
    def setup_method(self):
        self.r = pillar529_report()

    def test_returns_dict(self):
        assert isinstance(self.r, dict)

    def test_pillar_number(self):
        assert self.r["pillar"] == 529

    def test_status(self):
        assert self.r["status"] == "TENSOR_NLO_KK_MIXING_CERTIFIED"

    def test_derivation_keys(self):
        d = self.r["derivation"]
        for k in ("r_lo", "delta_kk_grav", "r_nlo", "correction_pct"):
            assert k in d

    def test_correction_pct_negative(self):
        assert self.r["derivation"]["correction_pct"] < 0

    def test_architecture_verdict_act_tension(self):
        assert "ACT" in self.r["architecture_verdict"]

    def test_summary_mentions_architecture(self):
        assert "Architecture" in self.r["summary"] or "architecture" in self.r["summary"]
