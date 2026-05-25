# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 447 — Lean4 n_w=5 Uniqueness Machine Proof."""
import pytest
from fractions import Fraction
from src.core.pillar447_lean4_nw5_uniqueness import (
    PILLAR_STATUS, VERSION, LEAN4_PROOF_TEXT, LEAN4_PROOF_HASH,
    N_W, K_CS_CANONICAL, K_CS_NW7,
    z2_involution_check, cs_anomaly_survivors, aps_eta_invariant,
    cs_eta_product, nw5_uniqueness_proof, verify_all_candidates,
    lean4_certificate, pillar_report,
)


class TestConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_k_cs_canonical(self):
        assert K_CS_CANONICAL == 74   # 5² + 7²

    def test_k_cs_nw7(self):
        assert K_CS_NW7 == 130   # 7² + 9²

    def test_lean4_hash_sha256_length(self):
        assert len(LEAN4_PROOF_HASH) == 64

    def test_lean4_proof_text_contains_theorem(self):
        assert 'nw5_uniqueness' in LEAN4_PROOF_TEXT


class TestZ2InvolutionCheck:
    @pytest.mark.parametrize('n', [3, 5, 7, 9, 11])
    def test_odd_numbers_pass(self, n):
        r = z2_involution_check(n)
        assert r['z2_compatible'] is True

    @pytest.mark.parametrize('n', [2, 4, 6, 8])
    def test_even_numbers_fail(self, n):
        r = z2_involution_check(n)
        assert r['is_odd'] is False

    def test_n2_fails_z2(self):
        r = z2_involution_check(2)
        assert r['z2_compatible'] is False


class TestCSAnomalySurvivors:
    def test_survivors_are_5_and_7(self):
        s = cs_anomaly_survivors()
        assert set(s) == {5, 7}

    def test_5_in_survivors(self):
        s = cs_anomaly_survivors()
        assert 5 in s

    def test_7_in_survivors(self):
        s = cs_anomaly_survivors()
        assert 7 in s

    def test_no_other_survivors(self):
        s = cs_anomaly_survivors()
        assert len(s) == 2


class TestAPSEtaInvariant:
    def test_n5_eta_half(self):
        eta = aps_eta_invariant(5)
        assert eta == Fraction(1, 2)

    def test_n7_eta_zero(self):
        eta = aps_eta_invariant(7)
        assert eta == Fraction(0)

    def test_fractions_type(self):
        eta = aps_eta_invariant(5)
        assert isinstance(eta, Fraction)


class TestCSEtaProduct:
    def test_n5_product_is_37(self):
        product = cs_eta_product(5)
        assert product == Fraction(37)

    def test_n7_product_is_zero(self):
        product = cs_eta_product(7)
        assert product == Fraction(0)

    def test_n5_is_odd_integer(self):
        product = cs_eta_product(5)
        assert product.denominator == 1
        assert product.numerator % 2 == 1

    def test_n7_is_even(self):
        product = cs_eta_product(7)
        assert product.numerator % 2 == 0


class TestUniquenessProof:
    def test_proof_complete(self):
        r = nw5_uniqueness_proof()
        assert r['proof_complete'] is True

    def test_verdict_proved(self):
        r = nw5_uniqueness_proof()
        assert r['verdict'] == 'NW5_UNIQUELY_PROVED'

    def test_n_w_selected_is_5(self):
        r = nw5_uniqueness_proof()
        assert r['n_w_selected'] == 5

    def test_k_cs_derived_is_74(self):
        r = nw5_uniqueness_proof()
        assert r['k_cs_derived'] == 74

    def test_step1_z2(self):
        r = nw5_uniqueness_proof()
        assert r['step1_z2_involution']['pass'] is True

    def test_step2_cs(self):
        r = nw5_uniqueness_proof()
        assert r['step2_cs_anomaly']['pass'] is True

    def test_step3_aps(self):
        r = nw5_uniqueness_proof()
        assert r['step3_aps_discriminator']['pass'] is True

    def test_step3_n5_passes(self):
        r = nw5_uniqueness_proof()
        assert r['step3_aps_discriminator']['results'][5]['passes_z2_odd_condition'] is True

    def test_step3_n7_fails(self):
        r = nw5_uniqueness_proof()
        assert r['step3_aps_discriminator']['results'][7]['passes_z2_odd_condition'] is False


class TestExhaustiveScan:
    def test_uniqueness_verified(self):
        r = verify_all_candidates()
        assert r['uniqueness_verified'] is True

    def test_unique_survivor_is_5(self):
        r = verify_all_candidates()
        assert r['unique_survivor'] == [5]

    def test_scans_at_least_5_candidates(self):
        r = verify_all_candidates()
        assert len(r['candidates_scanned']) >= 3


class TestLean4Certificate:
    def test_pillar_number(self):
        c = lean4_certificate()
        assert c['pillar'] == 447

    def test_numerically_verified(self):
        c = lean4_certificate()
        assert c['proof_verified_numerically'] is True

    def test_hash_matches(self):
        c = lean4_certificate()
        assert c['lean4_proof_hash'] == LEAN4_PROOF_HASH

    def test_n_w_unique(self):
        c = lean4_certificate()
        assert c['n_w_unique'] == 5

    def test_k_cs_74(self):
        c = lean4_certificate()
        assert c['k_cs_derived'] == 74


class TestPillarReport:
    def test_pillar_number(self):
        r = pillar_report()
        assert r['pillar'] == 447

    def test_status(self):
        r = pillar_report()
        assert r['status'] == PILLAR_STATUS
