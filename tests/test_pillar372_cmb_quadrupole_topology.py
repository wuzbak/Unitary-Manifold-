# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""tests/test_pillar372_cmb_quadrupole_topology.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar372_cmb_quadrupole_topology import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    QUADRUPOLE_DEFICIT_FRACTION_LOW, QUADRUPOLE_DEFICIT_FRACTION_HIGH,
    L_HUBBLE_M, R_C_M, K_MIN_5D_PER_M, K_QUAD_PER_M,
    separation_guard, mechanism_a_topology, mechanism_b_kk_ir_cutoff,
    mechanism_c_ftum_preinflationary, quadrupole_analysis_summary,
    pillar372_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 372
    def test_status(self): assert PILLAR_STATUS == "MECHANISM_INCONCLUSIVE"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_deficit_low(self): assert abs(QUADRUPOLE_DEFICIT_FRACTION_LOW - 0.26) < 0.01
    def test_deficit_high(self): assert abs(QUADRUPOLE_DEFICIT_FRACTION_HIGH - 0.47) < 0.01
    def test_l_hubble_m(self): assert L_HUBBLE_M > 1e25
    def test_r_c_m_microscopic(self): assert R_C_M < 1e-5
    def test_k_min_5d_large(self): assert K_MIN_5D_PER_M > 1e4
    def test_k_quad_tiny(self): assert K_QUAD_PER_M < 1e-25
    def test_k_ratio_huge(self):
        ratio = K_MIN_5D_PER_M / K_QUAD_PER_M
        assert ratio > 1e30


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_mechanism_inconclusive(self): assert "MECHANISM_INCONCLUSIVE" in separation_guard()


class TestMechanismATopology:
    def test_returns_dict(self): assert isinstance(mechanism_a_topology(), dict)
    def test_mechanism_present(self):
        r = mechanism_a_topology()
        assert "mechanism" in r
    def test_verdict_possible_candidate(self):
        r = mechanism_a_topology()
        assert "POSSIBLE_CANDIDATE" in r["verdict"]
    def test_required_scale_present(self):
        r = mechanism_a_topology()
        assert "required_scale_in_hubble_units" in r
    def test_required_scale_order_one(self):
        r = mechanism_a_topology()
        assert 0.5 < r["required_scale_in_hubble_units"] < 2.0
    def test_reference_present(self):
        r = mechanism_a_topology()
        assert "reference" in r


class TestMechanismBKkIrCutoff:
    def test_returns_dict(self): assert isinstance(mechanism_b_kk_ir_cutoff(), dict)
    def test_verdict_ruled_out(self):
        r = mechanism_b_kk_ir_cutoff()
        assert "RULED_OUT" in r["verdict"]
    def test_ratio_present(self):
        r = mechanism_b_kk_ir_cutoff()
        assert "k_min_over_k_quad" in r
    def test_ratio_massive(self):
        r = mechanism_b_kk_ir_cutoff()
        assert r["k_min_over_k_quad"] > 1e30
    def test_log10_ratio_positive_large(self):
        r = mechanism_b_kk_ir_cutoff()
        assert r["log10_ratio"] > 30.0
    def test_physical_analysis_present(self):
        r = mechanism_b_kk_ir_cutoff()
        assert "physical_analysis" in r


class TestMechanismCFtumPreinflationary:
    def test_returns_dict(self): assert isinstance(mechanism_c_ftum_preinflationary(), dict)
    def test_verdict_ruled_out(self):
        r = mechanism_c_ftum_preinflationary()
        assert "RULED_OUT" in r["verdict"]
    def test_n_e_inflation_present(self):
        r = mechanism_c_ftum_preinflationary()
        assert "n_e_inflation" in r
    def test_pre_inflationary_scale_tiny(self):
        r = mechanism_c_ftum_preinflationary()
        assert r["l_pre_inflationary_hubble_units"] < 1e-20
    def test_physical_analysis_present(self):
        r = mechanism_c_ftum_preinflationary()
        assert "physical_analysis" in r


class TestQuadrupoleAnalysisSummary:
    def test_returns_dict(self): assert isinstance(quadrupole_analysis_summary(), dict)
    def test_pillar(self): assert quadrupole_analysis_summary()["pillar"] == 372
    def test_all_mechanisms_present(self):
        r = quadrupole_analysis_summary()
        assert "mechanism_a_topology" in r
        assert "mechanism_b_kk_ir_cutoff" in r
        assert "mechanism_c_ftum_pre_inflation" in r
    def test_verdicts_dict(self):
        r = quadrupole_analysis_summary()
        assert "verdicts" in r
    def test_kk_ir_ruled_out(self):
        r = quadrupole_analysis_summary()
        assert "RULED_OUT" in r["verdicts"]["kk_ir_cutoff"]
    def test_ftum_ruled_out(self):
        r = quadrupole_analysis_summary()
        assert "RULED_OUT" in r["verdicts"]["ftum_pre_inflation"]
    def test_overall_verdict_mechanism_inconclusive(self):
        r = quadrupole_analysis_summary()
        assert "MECHANISM_INCONCLUSIVE" in r["overall_verdict"]
    def test_connection_to_362(self):
        r = quadrupole_analysis_summary()
        assert "362" in r["connection_to_pillar_362"]


class TestPillar372Summary:
    def test_pillar(self): assert pillar372_summary()["pillar"] == 372
    def test_status(self): assert pillar372_summary()["status"] == "MECHANISM_INCONCLUSIVE"
    def test_kk_ruled_out(self): assert "RULED_OUT" in pillar372_summary()["mechanism_b_kk_ir_cutoff"]
    def test_ftum_ruled_out(self): assert "RULED_OUT" in pillar372_summary()["mechanism_c_ftum_pre_inflation"]
    def test_gap_remains(self): assert pillar372_summary()["gap_remains"] is True
