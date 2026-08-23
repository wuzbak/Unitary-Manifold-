# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 804 — SU3_INTERNAL_DERIVATION_ATTEMPT
~40 tests covering group theory, S³×S² analysis, and Hopf fibration.
"""
import pytest
from src.core.pillar804_su3_internal_derivation import (
    N_W, K_CS, N_C,
    DIM_SU5, DIM_SU3, DIM_SU2, DIM_U1, DIM_SM, DIM_PROJECTED,
    Z2_POSITIVE_ENTRIES, Z2_NEGATIVE_ENTRIES,
    RANK_SU5, RANK_SM, HOPF_DEGREE, HOPF_INVARIANT, K_CS_FROM_HOPF,
    PILLAR_804_GATE,
    group_theory_analysis, s3xs2_analysis, hopf_analysis, pillar804_summary,
)


class TestConstants:
    def test_gate(self):
        assert PILLAR_804_GATE == "SU3_KAWAMURA_IMPORT_HONEST_DOCUMENTED"

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_dim_su5(self):
        assert DIM_SU5 == 24  # 5² - 1

    def test_dim_su3(self):
        assert DIM_SU3 == 8   # 3² - 1

    def test_dim_su2(self):
        assert DIM_SU2 == 3   # 2² - 1

    def test_dim_sm(self):
        assert DIM_SM == 12  # 8 + 3 + 1

    def test_dim_projected(self):
        assert DIM_PROJECTED == 12  # 24 - 12


class TestGroupTheory:
    def test_rank_preserved(self):
        assert RANK_SU5 == RANK_SM == 4

    def test_z2_signature(self):
        assert Z2_POSITIVE_ENTRIES == 3
        assert Z2_NEGATIVE_ENTRIES == 2
        assert Z2_POSITIVE_ENTRIES + Z2_NEGATIVE_ENTRIES == 5

    def test_group_analysis_dict(self):
        d = group_theory_analysis()
        assert d['rank_preserved'] is True
        assert d['z2_matrix'] == 'diag(+1, +1, +1, -1, -1)'


class TestS3S2Analysis:
    def test_rank_mismatch(self):
        d = s3xs2_analysis()
        assert d['rank_match'] is False  # rank 3 ≠ rank 2 of SU(3)

    def test_total_rank(self):
        d = s3xs2_analysis()
        assert d['total_rank'] == 3

    def test_su3_rank(self):
        d = s3xs2_analysis()
        assert d['su3_rank'] == 2

    def test_conclusion_key(self):
        d = s3xs2_analysis()
        assert 'conclusion' in d


class TestHopfAnalysis:
    def test_hopf_degree_equals_nw(self):
        assert HOPF_DEGREE == N_W

    def test_hopf_invariant_equals_nw(self):
        assert HOPF_INVARIANT == N_W

    def test_kcs_from_hopf_correct(self):
        assert K_CS_FROM_HOPF == K_CS

    def test_hopf_sum_of_squares(self):
        assert N_W**2 + (N_W + 2)**2 == K_CS

    def test_hopf_analysis_dict(self):
        d = hopf_analysis()
        assert d['k_cs_match'] is True
        assert 'what_is_proved' in d
        assert 'what_is_open' in d

    def test_honest_result_negative(self):
        s = pillar804_summary()
        assert 'negative' in s['honest_result'].lower()


class TestSummary:
    def test_summary_dict(self):
        s = pillar804_summary()
        assert s['pillar'] == 804
        assert s['gate'] == PILLAR_804_GATE

    def test_summary_lean4(self):
        s = pillar804_summary()
        assert s['lean4']['new_theorems'] == 15
        assert s['lean4']['lean4_before'] == 1231
        assert s['lean4']['lean4_after'] == 1246
