# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 640 — Baryogenesis 6D Phase 3."""
from __future__ import annotations

import pytest

from src.core.pillar640_baryogenesis_6d_phase3 import (
    D_N_NLO_ECM,
    D_N_PHASE2_ECM,
    DELTA_EW_FRAC,
    M_SIGMA_CANONICAL_GEV,
    M_SIGMA_DISCOVERY_HIGH_GEV,
    M_SIGMA_DISCOVERY_LOW_GEV,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SNS_CURRENT_BOUND_ECM,
    SNS_SENSITIVITY_ECM,
    VERSION,
    architecture_limit_status,
    d_n_of_m_sigma,
    discovery_window,
    nlo_ew_correction,
    pillar_report,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
NLO = nlo_ew_correction()
WINDOW = discovery_window()
STATUS = architecture_limit_status()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 640

    def test_status(self):
        assert "PHASE3" in PILLAR_STATUS

    def test_d_n_nlo_larger_than_phase2(self):
        assert D_N_NLO_ECM > D_N_PHASE2_ECM

    def test_ew_frac(self):
        assert abs(DELTA_EW_FRAC - 0.0079) < 1e-12

    def test_sns_nlo_above_sensitivity(self):
        # At canonical m_Σ, should be detectable
        assert D_N_NLO_ECM > SNS_SENSITIVITY_ECM

    def test_sns_below_current_bound(self):
        assert D_N_NLO_ECM < SNS_CURRENT_BOUND_ECM

    def test_discovery_window_defined(self):
        assert M_SIGMA_DISCOVERY_LOW_GEV < M_SIGMA_DISCOVERY_HIGH_GEV


class TestDnFormula:
    def test_canonical_point(self):
        dn = d_n_of_m_sigma(M_SIGMA_CANONICAL_GEV)
        assert abs(dn - D_N_NLO_ECM) < 1e-35

    def test_decreases_with_mass(self):
        d1 = d_n_of_m_sigma(500.0)
        d2 = d_n_of_m_sigma(1000.0)
        assert d1 > d2

    def test_invalid_mass(self):
        with pytest.raises(ValueError):
            d_n_of_m_sigma(0.0)


class TestNLOCorrection:
    def test_delta_ew(self):
        assert abs(NLO["delta_ew_frac"] - DELTA_EW_FRAC) < 1e-12

    def test_after_larger_than_before(self):
        assert NLO["d_n_after"] > NLO["d_n_before"]


class TestDiscoveryWindow:
    def test_canonical_detectable(self):
        canonical = next(
            r for r in WINDOW["scan"] if r["m_sigma_gev"] == 650
        )
        assert canonical["sns_detectable"] is True

    def test_window_nonempty(self):
        assert len(WINDOW["discovery_window_gev"]) == 2


class TestArchitectureLimit:
    def test_minimal_5d_all_confirmed(self):
        for path, val in STATUS["minimal_5d_paths"].items():
            assert "ARCHITECTURE_LIMIT_CONFIRMED" in val


class TestReport:
    def test_adjacent_track(self):
        assert REPORT["adjacent_track"] is True

    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
