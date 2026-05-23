# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar376_um_vs_lcdm_discriminator.py"""
from __future__ import annotations
import pytest
from src.core.pillar376_um_vs_lcdm_discriminator import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    separation_guard, um_vs_lcdm_discriminator_matrix,
    top_discriminators, rank_by_discriminating_power,
    preregistered_routing_summary, catalogue_for_external_reviewers,
    pillar376_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 376
    def test_status(self): assert PILLAR_STATUS == "DISCRIMINATOR_CATALOGUE"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
    def test_discriminator(self): assert "discriminator" in separation_guard().lower()


class TestUmVsLcdmDiscriminatorMatrix:
    def test_returns_list(self): assert isinstance(um_vs_lcdm_discriminator_matrix(), list)
    def test_at_least_10_entries(self): assert len(um_vs_lcdm_discriminator_matrix()) >= 10

    def test_each_has_rank(self):
        for e in um_vs_lcdm_discriminator_matrix():
            assert "rank" in e

    def test_each_has_observable(self):
        for e in um_vs_lcdm_discriminator_matrix():
            assert "observable" in e

    def test_each_has_um_prediction(self):
        for e in um_vs_lcdm_discriminator_matrix():
            assert "um_prediction" in e

    def test_each_has_verdict(self):
        for e in um_vs_lcdm_discriminator_matrix():
            assert "verdict" in e

    def test_each_has_discriminating_power_score(self):
        for e in um_vs_lcdm_discriminator_matrix():
            assert "discriminating_power_score" in e

    def test_birefringence_entry_present(self):
        observables = [e["observable"].lower() for e in um_vs_lcdm_discriminator_matrix()]
        assert any("birefringence" in o for o in observables)

    def test_fnl_entry_present(self):
        observables = [e["observable"].lower() for e in um_vs_lcdm_discriminator_matrix()]
        assert any("gaussianity" in o or "f_nl" in o for o in observables)

    def test_r_prediction_entry(self):
        observables = [e["observable"].lower() for e in um_vs_lcdm_discriminator_matrix()]
        assert any("tensor" in o or "scalar" in o for o in observables)

    def test_unique_ranks(self):
        matrix = um_vs_lcdm_discriminator_matrix()
        ranks = [e["rank"] for e in matrix]
        assert len(ranks) == len(set(ranks))

    def test_scores_positive(self):
        for e in um_vs_lcdm_discriminator_matrix():
            assert e["discriminating_power_score"] > 0


class TestTopDiscriminators:
    def test_returns_list(self): assert isinstance(top_discriminators(3), list)
    def test_returns_n_items(self):
        assert len(top_discriminators(5)) == 5
    def test_sorted_descending(self):
        top = top_discriminators(5)
        scores = [t["discriminating_power_score"] for t in top]
        assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))
    def test_highest_score_first(self):
        top = top_discriminators(1)
        all_matrix = um_vs_lcdm_discriminator_matrix()
        max_score = max(e["discriminating_power_score"] for e in all_matrix)
        assert abs(top[0]["discriminating_power_score"] - max_score) < 0.1


class TestRankByDiscriminatingPower:
    def test_returns_list(self): assert isinstance(rank_by_discriminating_power(), list)
    def test_same_length_as_matrix(self):
        assert len(rank_by_discriminating_power()) == len(um_vs_lcdm_discriminator_matrix())
    def test_sorted_descending(self):
        ranked = rank_by_discriminating_power()
        scores = [r["discriminating_power_score"] for r in ranked]
        assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))


class TestPreregisteredRoutingSummary:
    def test_returns_dict(self): assert isinstance(preregistered_routing_summary(), dict)
    def test_desi_dr3_present(self): assert "desi_dr3" in preregistered_routing_summary()
    def test_so_dr1_present(self): assert "simons_observatory_dr1" in preregistered_routing_summary()
    def test_juno_present(self): assert "juno_2027" in preregistered_routing_summary()
    def test_litebird_present(self): assert "litebird_2032" in preregistered_routing_summary()
    def test_fnl_spherex_present(self): assert "fnl_spherex" in preregistered_routing_summary()
    def test_roman_present(self): assert "roman_space_telescope" in preregistered_routing_summary()
    def test_each_has_function(self):
        for key, val in preregistered_routing_summary().items():
            assert "function" in val
    def test_each_has_falsification_condition(self):
        for key, val in preregistered_routing_summary().items():
            assert "falsification_condition" in val


class TestCatalogueForExternalReviewers:
    def test_returns_dict(self): assert isinstance(catalogue_for_external_reviewers(), dict)
    def test_pillar(self): assert catalogue_for_external_reviewers()["pillar"] == 376
    def test_total_discriminators(self):
        c = catalogue_for_external_reviewers()
        assert c["total_discriminators"] >= 10
    def test_high_power_present(self):
        c = catalogue_for_external_reviewers()
        assert "high_discriminating_power" in c
    def test_timeline_present(self):
        c = catalogue_for_external_reviewers()
        assert "decisive_test_timeline" in c
    def test_litebird_2032_in_timeline(self):
        c = catalogue_for_external_reviewers()
        timeline = c["decisive_test_timeline"]
        assert "2032" in timeline
    def test_preregistered_routing_list(self):
        c = catalogue_for_external_reviewers()
        assert len(c["preregistered_routing"]) >= 5


class TestPillar376Summary:
    def test_pillar(self): assert pillar376_summary()["pillar"] == 376
    def test_status(self): assert pillar376_summary()["status"] == "DISCRIMINATOR_CATALOGUE"
    def test_total_discriminators(self): assert pillar376_summary()["total_discriminators"] >= 10
    def test_high_power_count(self): assert pillar376_summary()["high_power_count"] >= 2
    def test_new_addition_fnl(self):
        assert "f_NL" in pillar376_summary()["new_addition"] or "fnl" in pillar376_summary()["new_addition"].lower()
    def test_preregistered_routing_count(self): assert pillar376_summary()["preregistered_routing_count"] >= 5
