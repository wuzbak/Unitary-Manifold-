# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Sprint AN Wave 6: Higgs mass no-go / one-loop upgrade."""
import pytest
from src.core.higgs_mass_nogo_proof import (
    route_1_ghu,
    route_2_casimir_wilson,
    route_3_brane_kinetic,
    route_4_brane_mixing,
    route_5_sixd_correction,
    nogo_proof,
    total_higgs_mass_all_routes,
    higgs_p5_certificate,
    HIGGS_NOGO_STATUS,
)


def test_status_token():
    assert HIGGS_NOGO_STATUS == "NOGO_AT_TREE_LEVEL_BUT_CLOSED_AT_ONE_LOOP"


def test_route_1_ghu_has_tree_mass():
    r = route_1_ghu()
    assert "m_H_tree_GeV" in r
    assert r["m_H_tree_GeV"] > 125.25


def test_route_1_ghu_has_eff_mass():
    r = route_1_ghu()
    assert "m_H_eff_GeV" in r
    assert 120 < r["m_H_eff_GeV"] < 130


def test_route_1_within_1pct():
    r = route_1_ghu()
    assert r["within_1pct"] is True


def test_route_2_returns_dict():
    r = route_2_casimir_wilson()
    assert isinstance(r, dict)


def test_route_3_returns_dict():
    r = route_3_brane_kinetic()
    assert isinstance(r, dict)


def test_route_4_returns_dict():
    r = route_4_brane_mixing()
    assert isinstance(r, dict)


def test_route_5_returns_dict():
    r = route_5_sixd_correction()
    assert isinstance(r, dict)


def test_nogo_proof_status():
    proof = nogo_proof()
    assert proof["HIGGS_NOGO_STATUS"] == "NOGO_AT_TREE_LEVEL_BUT_CLOSED_AT_ONE_LOOP"


def test_nogo_proof_p5_upgrade():
    proof = nogo_proof()
    assert "p5_status_correction" in proof
    assert "ONE_LOOP" in proof["p5_status_correction"]


def test_total_routes_returns_dict():
    r = total_higgs_mass_all_routes()
    assert isinstance(r, dict)


def test_certificate_status():
    cert = higgs_p5_certificate()
    assert cert["HIGGS_NOGO_STATUS"] == "NOGO_AT_TREE_LEVEL_BUT_CLOSED_AT_ONE_LOOP"
