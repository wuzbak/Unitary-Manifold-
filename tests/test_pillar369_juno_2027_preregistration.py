# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar369_juno_2027_preregistration.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar369_juno_2027_preregistration import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    DM31_LEGACY_PREDICTION, DM31_NLO_PREDICTION, DM31_PDG_2024,
    DM31_PDG_SIGMA, JUNO_PROJECTED_PRECISION,
    SEESAW_PARTICIPATION_P_R,
    separation_guard, legacy_residual_fraction, nlo_residual_fraction,
    juno_2027_verdict, hyperk_2028_verdict,
    combined_neutrino_routing, preregistration_hash,
    preregistration_checklist, pillar369_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 369
    def test_status(self): assert PILLAR_STATUS == "ROUTING_INFRASTRUCTURE"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_dm31_nlo_prediction(self): assert abs(DM31_NLO_PREDICTION - 2.452e-3) < 1e-7
    def test_dm31_legacy_prediction(self): assert abs(DM31_LEGACY_PREDICTION - 2.399e-3) < 1e-7
    def test_dm31_pdg_2024(self): assert abs(DM31_PDG_2024 - 2.453e-3) < 1e-7
    def test_juno_precision(self): assert abs(JUNO_PROJECTED_PRECISION - 0.005) < 1e-6
    def test_seesaw_participation(self): assert 0.0 < SEESAW_PARTICIPATION_P_R < 1.0
    def test_nlo_closer_than_legacy(self):
        nlo = nlo_residual_fraction()
        legacy = legacy_residual_fraction()
        assert nlo < legacy


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_mentions_juno(self): assert "JUNO" in separation_guard()


class TestResiduals:
    def test_legacy_residual_positive(self): assert legacy_residual_fraction() > 0
    def test_nlo_residual_positive(self): assert nlo_residual_fraction() > 0
    def test_nlo_small(self): assert nlo_residual_fraction() < 0.001
    def test_legacy_larger(self): assert legacy_residual_fraction() > nlo_residual_fraction()
    def test_nlo_residual_approx(self):
        # |2.452 - 2.453| / 2.453 ≈ 0.000408
        r = nlo_residual_fraction()
        assert r < 0.001
    def test_custom_pdg_value(self):
        r = nlo_residual_fraction(2.452e-3)   # perfect match
        assert r == 0.0


class TestJuno2027Verdict:
    def test_returns_dict(self): assert isinstance(juno_2027_verdict(2.452e-3, 1e-5), dict)

    def test_consistent_at_nlo_prediction(self):
        v = juno_2027_verdict(DM31_NLO_PREDICTION, 1e-5)
        assert v["verdict"] == "CONSISTENT"

    def test_falsified_at_large_deviation(self):
        # 10× sigma deviation
        sigma = 1e-5
        v = juno_2027_verdict(2.452e-3 + 4.0 * sigma, sigma)
        assert v["verdict"] == "FALSIFIED"

    def test_tension_at_2sigma(self):
        sigma = 1e-5
        v = juno_2027_verdict(2.452e-3 + 2.5 * sigma, sigma)
        assert v["verdict"] in ["TENSION", "FALSIFIED"]

    def test_pillar_number(self):
        v = juno_2027_verdict(2.452e-3, 1e-5)
        assert v["pillar"] == PILLAR_NUMBER

    def test_instrument(self):
        v = juno_2027_verdict(2.452e-3, 1e-5)
        assert "JUNO" in v["instrument"]

    def test_zero_sigma_returns_error(self):
        v = juno_2027_verdict(2.452e-3, 0.0)
        assert "error" in v

    def test_residual_present(self):
        v = juno_2027_verdict(2.452e-3, 1e-5)
        assert "residual_eV2" in v

    def test_nlo_prediction_in_result(self):
        v = juno_2027_verdict(2.452e-3, 1e-5)
        assert abs(v["um_prediction_nlo"] - DM31_NLO_PREDICTION) < 1e-10

    def test_pdg_consistent(self):
        # JUNO measures PDG value ~ 2.453e-3; NLO prediction 2.452e-3; sigma ~ 0.012e-3
        sigma = JUNO_PROJECTED_PRECISION * DM31_PDG_2024
        v = juno_2027_verdict(DM31_PDG_2024, sigma)
        assert v["verdict"] in ["CONSISTENT", "TENSION"]


class TestHyperK2028Verdict:
    def test_returns_dict(self): assert isinstance(hyperk_2028_verdict(2.452e-3, 1e-5), dict)
    def test_consistent_at_nlo(self):
        v = hyperk_2028_verdict(DM31_NLO_PREDICTION, 1e-5)
        assert v["verdict"] == "CONSISTENT"
    def test_instrument(self):
        v = hyperk_2028_verdict(DM31_NLO_PREDICTION, 1e-5)
        assert "Hyper" in v["instrument"]
    def test_zero_sigma_error(self):
        v = hyperk_2028_verdict(2.452e-3, 0.0)
        assert "error" in v


class TestCombinedNeutrinoRouting:
    def test_returns_dict(self): assert isinstance(combined_neutrino_routing(), dict)
    def test_pending_before_juno(self):
        r = combined_neutrino_routing()
        assert "PENDING" in r.get("current_status", "")
    def test_with_juno_data(self):
        r = combined_neutrino_routing(juno_dm31=2.452e-3, juno_sigma=1e-5)
        assert "juno" in r
    def test_with_hyperk_data(self):
        r = combined_neutrino_routing(hyperk_dm31=2.452e-3, hyperk_sigma=1e-5)
        assert "hyperk" in r
    def test_nlo_residual_present(self):
        r = combined_neutrino_routing()
        assert "nlo_residual_fraction" in r


class TestPreregistrationHash:
    def test_returns_string(self): assert isinstance(preregistration_hash(), str)
    def test_length_64_hex(self): assert len(preregistration_hash()) == 64
    def test_hex_chars_only(self):
        h = preregistration_hash()
        assert all(c in "0123456789abcdef" for c in h)
    def test_deterministic(self):
        assert preregistration_hash() == preregistration_hash()


class TestPreregistrationChecklist:
    def test_returns_list(self): assert isinstance(preregistration_checklist(), list)
    def test_at_least_4(self): assert len(preregistration_checklist()) >= 4
    def test_each_has_status(self):
        for item in preregistration_checklist():
            assert "status" in item
    def test_open_item_present(self):
        items = [i for i in preregistration_checklist() if "OPEN" in i["status"]]
        assert len(items) >= 1


class TestPillar369Summary:
    def test_pillar(self): assert pillar369_summary()["pillar"] == 369
    def test_status(self): assert pillar369_summary()["status"] == "ROUTING_INFRASTRUCTURE"
    def test_nlo_prediction(self):
        assert abs(pillar369_summary()["dm31_nlo_prediction"] - 2.452e-3) < 1e-7
    def test_preregistration_complete(self): assert pillar369_summary()["preregistration_complete"] is True
    def test_hash_present(self): assert len(pillar369_summary()["preregistration_hash"]) == 64
