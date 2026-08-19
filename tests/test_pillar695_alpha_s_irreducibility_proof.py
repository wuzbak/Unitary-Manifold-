# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 695 — α_s irreducibility proof."""

from src.core.pillar695_alpha_s_irreducibility_proof import (
    N_W,
    K_CS,
    ALPHA_S_PDG_MZ,
    all_alpha_s_paths,
    irreducibility_proof,
    alpha_s_irreducibility_cert,
)


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert ALPHA_S_PDG_MZ == 0.1180


def test_all_paths_returns_list():
    assert isinstance(all_alpha_s_paths(), list)


def test_all_paths_count():
    assert len(all_alpha_s_paths()) == 5


def test_all_paths_labels():
    labels = {item["path"] for item in all_alpha_s_paths()}
    assert labels == {"A", "B", "C", "693", "694"}


def test_all_paths_have_required_fields():
    for item in all_alpha_s_paths():
        for field in ("path", "method", "alpha_s", "residual_pct", "verdict"):
            assert field in item


def test_all_paths_alpha_positive():
    for item in all_alpha_s_paths():
        assert item["alpha_s"] > 0.0


def test_all_paths_residual_above_10():
    for item in all_alpha_s_paths():
        assert item["residual_pct"] > 10.0


def test_ads_path_best():
    proof = irreducibility_proof()
    assert proof["best_path"]["path"] == "C"


def test_best_estimate_matches_best_path():
    proof = irreducibility_proof()
    assert proof["combined_best_estimate"] == proof["best_path"]["alpha_s"]


def test_best_path_residual_above_40():
    proof = irreducibility_proof()
    assert proof["best_path"]["residual_pct"] > 40.0


def test_irreducibility_proof_returns_dict():
    assert isinstance(irreducibility_proof(), dict)


def test_irreducibility_status():
    proof = irreducibility_proof()
    assert proof["status"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_irreducibility_certificate_field():
    proof = irreducibility_proof()
    assert proof["certificate"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_remaining_gap_matches_best_path():
    proof = irreducibility_proof()
    assert proof["remaining_irreducible_gap_pct"] == proof["best_path"]["residual_pct"]


def test_formal_statement_mentions_no_path():
    proof = irreducibility_proof()
    assert "No currently identified geometric path" in proof["formal_statement"]


def test_cert_returns_dict():
    assert isinstance(alpha_s_irreducibility_cert(), dict)


def test_cert_status_matches_proof():
    cert = alpha_s_irreducibility_cert()
    assert cert["status"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_cert_contains_proof():
    cert = alpha_s_irreducibility_cert()
    assert "proof" in cert


def test_cert_honest_note_mentions_alternative():
    cert = alpha_s_irreducibility_cert()
    assert "alternative closure mechanisms" in cert["honest_note"]


def test_path_693_is_worst_or_near_worst():
    paths = {item["path"]: item for item in all_alpha_s_paths()}
    assert paths["693"]["residual_pct"] >= paths["694"]["residual_pct"]


# ---------------------------------------------------------------------------
# TestAlphaS5DGeometricUpperBound — G2 gap closure
# ---------------------------------------------------------------------------

from src.core.pillar695_alpha_s_irreducibility_proof import alpha_s_5d_geometric_upper_bound
import math


class TestAlphaS5DGeometricUpperBound:
    """Tests for G2 closure: rigorous proved lower bound on α_s gap."""

    def test_status(self):
        r = alpha_s_5d_geometric_upper_bound()
        assert r["status"] == "ARCHITECTURE_LIMIT_RIGOROUS_BOUND_PROVED"

    def test_ads_bound_value(self):
        """α_s^{AdS} = π²/148 ≈ 0.0667."""
        r = alpha_s_5d_geometric_upper_bound()
        expected = math.pi**2 / 148.0
        assert abs(r["alpha_s_ads_bound"] - expected) < 1e-10

    def test_ads_bound_less_than_pdg(self):
        r = alpha_s_5d_geometric_upper_bound()
        assert r["alpha_s_ads_bound"] < r["alpha_s_pdg"]

    def test_gap_fraction_positive(self):
        r = alpha_s_5d_geometric_upper_bound()
        assert r["gap_fraction_min"] > 0.0

    def test_gap_pct_at_least_40(self):
        """Gap must be proved ≥ 40% (architecture limit)."""
        r = alpha_s_5d_geometric_upper_bound()
        assert r["gap_pct_min"] >= 40.0

    def test_bound_is_tight(self):
        """The bound is achieved by Path C (AdS/QCD)."""
        r = alpha_s_5d_geometric_upper_bound()
        assert r["bound_is_tight"] is True

    def test_theorem_string_contains_theorem(self):
        r = alpha_s_5d_geometric_upper_bound()
        assert "THEOREM" in r["theorem"]

    def test_path_a_less_than_ads(self):
        r = alpha_s_5d_geometric_upper_bound()
        assert r["path_a_value"] < r["alpha_s_ads_bound"]

    def test_corollary_mentions_proved(self):
        r = alpha_s_5d_geometric_upper_bound()
        assert "proved" in r["corollary"].lower() or "≥" in r["corollary"]
