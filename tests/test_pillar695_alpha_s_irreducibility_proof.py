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
