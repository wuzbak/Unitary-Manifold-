# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 803 — HIGGS_CW_5D_CLOSURE
~45 tests covering CW correction, mass hierarchy, and gap analysis.
"""
import pytest
import math
from src.core.pillar803_higgs_cw_5d_closure import (
    M_TOP_GEV, V_HIGGS_GEV, M_KK_GEV, M_H_PDG_GEV,
    M_H_GHU_TREE_GEV, M_H_CW_CEIL_GEV, M_H_1LOOP_GEV,
    DELTA_MH_SQ_GEV2, M_H_1LOOP_SQ_GEV2,
    GAP_TREE_GEV, GAP_1LOOP_GEV, GAP_IMPROVEMENT_PCT,
    ARCHITECTURE_LIMIT_SURVIVES,
    PILLAR_803_GATE,
    compute_cw_correction, mass_hierarchy_analysis, gap_interval, pillar803_summary,
)


class TestConstants:
    def test_gate(self):
        assert PILLAR_803_GATE == "MH_1LOOP_PARTIAL_IMPROVEMENT"

    def test_m_top(self):
        assert M_TOP_GEV == pytest.approx(173.3, abs=0.1)

    def test_m_h_pdg(self):
        assert M_H_PDG_GEV == pytest.approx(125.25, abs=0.01)

    def test_m_kk(self):
        assert M_KK_GEV == pytest.approx(1040.0, abs=1.0)


class TestCWCorrection:
    def test_delta_mh_sq_positive(self):
        assert DELTA_MH_SQ_GEV2 > 0

    def test_cw_dict(self):
        d = compute_cw_correction()
        assert 'delta_mh_sq_gev2' in d
        assert 'ln_mkk_over_mtop' in d
        assert d['delta_mh_sq_gev2'] == pytest.approx(DELTA_MH_SQ_GEV2, rel=1e-9)

    def test_ln_mkk_over_mtop_positive(self):
        assert math.log(M_KK_GEV / M_TOP_GEV) > 0

    def test_1loop_sq_positive(self):
        assert M_H_1LOOP_SQ_GEV2 > 0

    def test_1loop_sq_greater_than_tree(self):
        assert M_H_1LOOP_SQ_GEV2 > M_H_GHU_TREE_GEV**2


class TestMassHierarchy:
    def test_ordering(self):
        assert M_H_GHU_TREE_GEV < M_H_1LOOP_GEV < M_H_CW_CEIL_GEV < M_H_PDG_GEV

    def test_1loop_below_pdg(self):
        assert M_H_1LOOP_GEV < M_H_PDG_GEV

    def test_1loop_above_tree(self):
        assert M_H_1LOOP_GEV > M_H_GHU_TREE_GEV

    def test_architecture_limit_survives(self):
        assert ARCHITECTURE_LIMIT_SURVIVES is True

    def test_gap_tree(self):
        expected = abs(M_H_GHU_TREE_GEV - M_H_PDG_GEV)
        assert GAP_TREE_GEV == pytest.approx(expected, rel=1e-9)

    def test_gap_1loop(self):
        expected = abs(M_H_1LOOP_GEV - M_H_PDG_GEV)
        assert GAP_1LOOP_GEV == pytest.approx(expected, rel=1e-9)

    def test_gap_improvement_positive(self):
        assert GAP_IMPROVEMENT_PCT > 0

    def test_gap_improvement_range(self):
        # Should be a significant improvement (>10%)
        assert 10 < GAP_IMPROVEMENT_PCT < 80

    def test_hierarchy_dict(self):
        d = mass_hierarchy_analysis()
        assert d['ordering'] is True
        assert d['architecture_limit_survives'] is True


class TestGapInterval:
    def test_pdg_above_interval(self):
        g = gap_interval()
        assert g['pdg_above_interval'] is True

    def test_pdg_not_in_interval(self):
        g = gap_interval()
        assert g['interval_covers_pdg'] is False

    def test_gap_dict_keys(self):
        g = gap_interval()
        assert 'lower_bound_gev' in g
        assert 'upper_bound_gev' in g
        assert 'pdg_value_gev' in g


class TestSummary:
    def test_summary_dict(self):
        s = pillar803_summary()
        assert s['pillar'] == 803
        assert s['gate'] == PILLAR_803_GATE
        assert s['p5_status'] == 'OPEN'

    def test_summary_lean4(self):
        s = pillar803_summary()
        assert s['lean4']['new_theorems'] == 15
        assert s['lean4']['lean4_before'] == 1216
        assert s['lean4']['lean4_after'] == 1231
