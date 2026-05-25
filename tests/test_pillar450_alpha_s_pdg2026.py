# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 450 — α_s PDG 2026 Basin Stability Audit."""
import pytest
from src.core.pillar450_alpha_s_pdg2026_basin import (
    PILLAR_STATUS, VERSION,
    ALPHA_S_UM, ALPHA_S_PDG2024, ALPHA_S_PDG2026, ALPHA_S_PDG2026_UNC,
    M_Z_GEV, M_KK_GEV, K_CS,
    STABLE_CORE_MAX, MARGIN_ZONE_MAX,
    um_alpha_s_running, flux_correction_10d, residual_from_pdg,
    basin_classification, pdg2026_audit, pillar_report,
)


class TestConstants:
    def test_alpha_s_um(self):
        assert abs(ALPHA_S_UM - 0.113) < 1e-4

    def test_alpha_s_pdg2026(self):
        assert abs(ALPHA_S_PDG2026 - 0.118) < 1e-3

    def test_basin_zones(self):
        assert STABLE_CORE_MAX == 0.025
        assert MARGIN_ZONE_MAX == 0.050

    def test_k_cs(self):
        assert K_CS == 74


class TestUMRunning:
    def test_running_returns_dict(self):
        r = um_alpha_s_running()
        assert isinstance(r, dict)

    def test_running_has_mz_value(self):
        r = um_alpha_s_running()
        assert 'alpha_s_mz_1loop' in r

    def test_b0_correct(self):
        r = um_alpha_s_running()
        # b_0 = 11 - 2×6/3 = 7
        assert r['b_0'] == 7.0


class TestFluxCorrection:
    def test_sub_leading_note(self):
        r = flux_correction_10d()
        # The note describes the correction as negligible
        assert 'negligible' in r['note'].lower() or r['delta_alpha_s'] < 0.001

    def test_cannot_close_to_3pct(self):
        r = flux_correction_10d()
        assert r['can_close_to_3pct'] is False

    def test_delta_alpha_s_small(self):
        r = flux_correction_10d()
        assert abs(r['delta_alpha_s']) < 0.005


class TestResidualFromPDG:
    def test_residual_positive(self):
        r = residual_from_pdg()
        assert r['residual_abs'] > 0

    def test_residual_fraction(self):
        r = residual_from_pdg()
        expected = abs(ALPHA_S_UM - ALPHA_S_PDG2026) / ALPHA_S_PDG2026
        assert abs(r['residual_fraction'] - expected) < 1e-10

    def test_within_5pct(self):
        r = residual_from_pdg()
        assert r['within_5pct'] is True

    def test_not_within_2_5pct(self):
        r = residual_from_pdg()
        # UM is at ~4.24% → outside STABLE_CORE
        assert r['within_2_5pct'] is False


class TestBasinClassification:
    def test_margin_zone(self):
        r = basin_classification()
        assert r['zone'] == 'MARGIN_ZONE'

    def test_residual_in_margin_range(self):
        r = basin_classification()
        assert STABLE_CORE_MAX <= r['residual_frac'] < MARGIN_ZONE_MAX

    def test_pdg_year_2026(self):
        r = basin_classification()
        assert '2026' in r['at_pdg_year']

    def test_custom_residual(self):
        # Below stable core
        r = basin_classification(0.02)
        assert r['zone'] == 'STABLE_CORE'
        # Above volatile
        r = basin_classification(0.06)
        assert r['zone'] == 'VOLATILE_OUTER'


class TestPDG2026Audit:
    def test_final_label_margin_zone(self):
        r = pdg2026_audit()
        assert r['final_label'] == 'MARGIN_ZONE'

    def test_no_escalation_to_constrained(self):
        r = pdg2026_audit()
        assert r['escalation_to_constrained'] is False

    def test_pdg_unchanged(self):
        r = pdg2026_audit()
        assert abs(r['alpha_s_pdg_2026'] - r['alpha_s_pdg_2024']) < 0.001


class TestPillarReport:
    def test_pillar_number(self):
        r = pillar_report()
        assert r['pillar'] == 450

    def test_status(self):
        r = pillar_report()
        assert r['status'] == PILLAR_STATUS
