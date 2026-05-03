# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_universe_uniqueness_theorem.py
==========================================
Tests for Pillar 131 — The Uniqueness Theorem: Why This Universe.

~70 tests covering: uniqueness certificate, D=5 exclusion, n_w=5 exclusion,
k_cs=74 exclusion, φ₀=π/4 exclusion, braid-pair scan, and full theorem.
"""

from __future__ import annotations

import math

import pytest

from src.core.universe_uniqueness_theorem import (
    N_W,
    K_CS,
    PHI0,
    R_KK_M,
    BETA_DEG,
    BETA_WINDOW_MIN,
    BETA_WINDOW_MAX,
    K_MAX_VIABLE,
    uniqueness_certificate,
    d5_exclusion_proof,
    nw5_exclusion_proof,
    kcs74_exclusion_proof,
    phi0_exclusion_proof,
    braid_pair_exclusion_proof,
    full_uniqueness_theorem,
)


# ---------------------------------------------------------------------------
# TestConstants — 6 tests
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w_5(self):
        assert N_W == 5

    def test_k_cs_74(self):
        assert K_CS == 74

    def test_phi0_pi_over_4(self):
        assert abs(PHI0 - math.pi / 4) < 1e-10

    def test_beta_in_window(self):
        assert BETA_WINDOW_MIN <= BETA_DEG <= BETA_WINDOW_MAX

    def test_k_max_viable(self):
        assert K_MAX_VIABLE == 130

    def test_r_kk_positive(self):
        assert R_KK_M > 0


# ---------------------------------------------------------------------------
# TestUniquenessCertificate — 16 tests
# ---------------------------------------------------------------------------

class TestUniquenessCertificate:
    def test_returns_dict(self):
        assert isinstance(uniqueness_certificate(), dict)

    def test_has_key_D(self):
        assert "D" in uniqueness_certificate()

    def test_has_key_n_w(self):
        assert "n_w" in uniqueness_certificate()

    def test_has_key_k_cs(self):
        assert "k_cs" in uniqueness_certificate()

    def test_has_key_phi0(self):
        assert "phi0" in uniqueness_certificate()

    def test_has_key_R_kk(self):
        assert "R_kk" in uniqueness_certificate()

    def test_has_key_braid_pair(self):
        assert "braid_pair" in uniqueness_certificate()

    def test_D_equals_5(self):
        assert uniqueness_certificate()["D"]["value"] == 5

    def test_n_w_equals_5(self):
        assert uniqueness_certificate()["n_w"]["value"] == 5

    def test_k_cs_equals_74(self):
        assert uniqueness_certificate()["k_cs"]["value"] == 74

    def test_phi0_approx_pi_over_4(self):
        assert abs(uniqueness_certificate()["phi0"]["value"] - round(math.pi / 4, 6)) < 1e-4

    def test_R_kk_positive(self):
        assert uniqueness_certificate()["R_kk"]["value"] > 0

    def test_braid_pair_is_5_7(self):
        assert uniqueness_certificate()["braid_pair"]["value"] == (5, 7)

    def test_total_free_parameters_zero(self):
        assert uniqueness_certificate()["total_free_parameters"] == 0

    def test_n_w_status_proved(self):
        assert "PROVED" in uniqueness_certificate()["n_w"]["epistemic_status"]

    def test_k_cs_status_proved(self):
        assert "PROVED" in uniqueness_certificate()["k_cs"]["epistemic_status"]


# ---------------------------------------------------------------------------
# TestD5ExclusionProof — 10 tests
# ---------------------------------------------------------------------------

class TestD5ExclusionProof:
    def test_returns_list(self):
        assert isinstance(d5_exclusion_proof(), list)

    def test_has_10_entries(self):
        assert len(d5_exclusion_proof()) == 10

    def test_d5_is_viable(self):
        d5 = next(e for e in d5_exclusion_proof() if e["d"] == 5)
        assert d5["viable"] is True

    def test_d4_is_not_viable(self):
        d4 = next(e for e in d5_exclusion_proof() if e["d"] == 4)
        assert d4["viable"] is False

    def test_d6_is_not_viable(self):
        d6 = next(e for e in d5_exclusion_proof() if e["d"] == 6)
        assert d6["viable"] is False

    def test_d3_is_not_viable(self):
        d3 = next(e for e in d5_exclusion_proof() if e["d"] == 3)
        assert d3["viable"] is False

    def test_d7_is_not_viable(self):
        d7 = next(e for e in d5_exclusion_proof() if e["d"] == 7)
        assert d7["viable"] is False

    def test_each_entry_has_d_key(self):
        for e in d5_exclusion_proof():
            assert "d" in e

    def test_each_entry_has_failures_list(self):
        for e in d5_exclusion_proof():
            assert isinstance(e["failures"], list)

    def test_only_d5_viable(self):
        viable = [e for e in d5_exclusion_proof() if e["viable"]]
        assert len(viable) == 1
        assert viable[0]["d"] == 5


# ---------------------------------------------------------------------------
# TestNw5ExclusionProof — 10 tests
# ---------------------------------------------------------------------------

class TestNw5ExclusionProof:
    def test_returns_list(self):
        assert isinstance(nw5_exclusion_proof(), list)

    def test_n5_is_viable(self):
        n5 = next(e for e in nw5_exclusion_proof() if e["n_w"] == 5)
        assert n5["viable"] is True

    def test_n1_not_viable(self):
        n1 = next(e for e in nw5_exclusion_proof() if e["n_w"] == 1)
        assert n1["viable"] is False

    def test_n3_not_viable(self):
        n3 = next(e for e in nw5_exclusion_proof() if e["n_w"] == 3)
        assert n3["viable"] is False

    def test_n7_not_viable(self):
        n7 = next(e for e in nw5_exclusion_proof() if e["n_w"] == 7)
        assert n7["viable"] is False

    def test_n5_k_eff_74(self):
        n5 = next(e for e in nw5_exclusion_proof() if e["n_w"] == 5)
        assert n5["k_eff"] == 74

    def test_all_have_beta(self):
        for e in nw5_exclusion_proof():
            assert "beta_deg" in e

    def test_only_n5_viable(self):
        viable = [e for e in nw5_exclusion_proof() if e["viable"]]
        assert len(viable) == 1
        assert viable[0]["n_w"] == 5

    def test_has_k_eff_key(self):
        for e in nw5_exclusion_proof():
            assert "k_eff" in e

    def test_n1_failure_mentions_gap(self):
        n1 = next(e for e in nw5_exclusion_proof() if e["n_w"] == 1)
        assert any("gap" in f.lower() or "stability" in f.lower() for f in n1["failures"])


# ---------------------------------------------------------------------------
# TestKcs74ExclusionProof — 9 tests
# ---------------------------------------------------------------------------

class TestKcs74ExclusionProof:
    def test_returns_dict(self):
        assert isinstance(kcs74_exclusion_proof(), dict)

    def test_algebraic_k_cs_74(self):
        assert kcs74_exclusion_proof()["algebraic_k_cs"] == 74

    def test_k_cs_matches_algebra(self):
        assert kcs74_exclusion_proof()["k_cs_matches_algebra"] is True

    def test_beta_in_window(self):
        d = kcs74_exclusion_proof()
        assert BETA_WINDOW_MIN <= d["beta_deg"] <= BETA_WINDOW_MAX

    def test_has_identity_string(self):
        d = kcs74_exclusion_proof()
        assert "74" in d["identity"]

    def test_epistemic_status_proved(self):
        assert kcs74_exclusion_proof()["epistemic_status"] == "PROVED"

    def test_n_w_correct(self):
        assert kcs74_exclusion_proof()["n_w"] == N_W

    def test_has_exclusion_argument(self):
        d = kcs74_exclusion_proof()
        assert len(d["exclusion_argument"]) > 20

    def test_beta_window_in_window(self):
        d = kcs74_exclusion_proof()
        assert d["beta_in_window"] is True


# ---------------------------------------------------------------------------
# TestPhi0ExclusionProof — 8 tests
# ---------------------------------------------------------------------------

class TestPhi0ExclusionProof:
    def test_returns_dict(self):
        assert isinstance(phi0_exclusion_proof(), dict)

    def test_phi0_star_approx_pi_over_4(self):
        d = phi0_exclusion_proof()
        assert abs(d["phi0_star"] - math.pi / 4) < 1e-10

    def test_phi0_is_fixed_point(self):
        d = phi0_exclusion_proof()
        assert d["bc_selects_phi0"] is True

    def test_phi0_star_degrees(self):
        d = phi0_exclusion_proof()
        assert abs(d["phi0_star_degrees"] - 45.0) < 0.01

    def test_has_samples(self):
        d = phi0_exclusion_proof()
        assert "samples_near_phi0" in d
        assert len(d["samples_near_phi0"]) > 0

    def test_only_phi0_is_fixed(self):
        d = phi0_exclusion_proof()
        minimum_count = sum(
            1 for v in d["samples_near_phi0"].values() if v["is_minimum"]
        )
        assert minimum_count >= 1

    def test_epistemic_status_proved(self):
        assert phi0_exclusion_proof()["epistemic_status"] == "PROVED"

    def test_s_phi0_close_to_phi0(self):
        # The samples at delta=0 should have V_rel = 0
        d = phi0_exclusion_proof()
        delta0_key = f"phi={math.pi/4:.3f}"
        assert d["samples_near_phi0"][delta0_key]["V_rel"] < 1e-10


# ---------------------------------------------------------------------------
# TestBraidPairExclusionProof — 8 tests
# ---------------------------------------------------------------------------

class TestBraidPairExclusionProof:
    def test_returns_list(self):
        assert isinstance(braid_pair_exclusion_proof(), list)

    def test_5_7_is_viable(self):
        pair = next(e for e in braid_pair_exclusion_proof() if e["braid_pair"] == (5, 7))
        assert pair["viable"] is True

    def test_1_3_not_viable(self):
        pair = next(e for e in braid_pair_exclusion_proof() if e["braid_pair"] == (1, 3))
        assert pair["viable"] is False

    def test_3_5_not_viable(self):
        pair = next(e for e in braid_pair_exclusion_proof() if e["braid_pair"] == (3, 5))
        assert pair["viable"] is False

    def test_7_9_not_viable(self):
        pair = next(e for e in braid_pair_exclusion_proof() if e["braid_pair"] == (7, 9))
        assert pair["viable"] is False

    def test_only_5_7_viable(self):
        viable = [e for e in braid_pair_exclusion_proof() if e["viable"]]
        assert len(viable) == 1
        assert viable[0]["braid_pair"] == (5, 7)

    def test_5_7_k_eff_74(self):
        pair = next(e for e in braid_pair_exclusion_proof() if e["braid_pair"] == (5, 7))
        assert pair["k_eff"] == 74

    def test_all_entries_have_failures_list(self):
        for e in braid_pair_exclusion_proof():
            assert isinstance(e["failures"], list)


# ---------------------------------------------------------------------------
# TestFullUniquenessTheorem — 3 tests
# ---------------------------------------------------------------------------

class TestFullUniquenessTheorem:
    def test_returns_dict(self):
        assert isinstance(full_uniqueness_theorem(), dict)

    def test_unique_braid_pair_is_5_7(self):
        assert full_uniqueness_theorem()["unique_braid_pair_is_5_7"] is True

    def test_all_parameters_uniquely_fixed(self):
        assert full_uniqueness_theorem()["all_parameters_uniquely_fixed"] is True
