# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar_epistemics.py
================================
Tests for Pillar 101 — Honest Epistemics Table (§XIV.4).
(src/core/pillar_epistemics.py)

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import pytest

from src.core.pillar_epistemics import (
    PHYSICS_DERIVATION,
    CONDITIONAL_THEOREM,
    FALSIFIABLE_PREDICTION,
    FORMAL_ANALOGY,
    VALID_EPISTEMOLOGIES,
    pillar_epistemics_table,
    epistemics_summary,
)
from src.cold_fusion.falsification_protocol import cold_fusion_physics_link


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_physics_derivation_string(self):
        assert PHYSICS_DERIVATION == "PHYSICS_DERIVATION"

    def test_conditional_theorem_string(self):
        assert CONDITIONAL_THEOREM == "CONDITIONAL_THEOREM"

    def test_falsifiable_prediction_string(self):
        assert FALSIFIABLE_PREDICTION == "FALSIFIABLE_PREDICTION"

    def test_formal_analogy_string(self):
        assert FORMAL_ANALOGY == "FORMAL_ANALOGY"

    def test_valid_epistemologies_has_four_members(self):
        assert len(VALID_EPISTEMOLOGIES) == 4


# ---------------------------------------------------------------------------
# pillar_epistemics_table()
# ---------------------------------------------------------------------------

class TestPillarEpistemicsTable:

    @pytest.fixture(autouse=True)
    def table(self):
        self.table = pillar_epistemics_table()

    def test_returns_list(self):
        assert isinstance(self.table, list)

    def test_at_least_26_entries(self):
        assert len(self.table) >= 26

    def test_required_fields_in_every_entry(self):
        required = {"pillar", "domain", "module_path", "epistemology",
                    "analogy_coupling", "path_to_upgrade", "exception_note"}
        for entry in self.table:
            assert required.issubset(entry.keys()), (
                f"Missing fields in pillar {entry.get('pillar')}: "
                f"{required - entry.keys()}"
            )

    def test_all_epistemologies_valid(self):
        for entry in self.table:
            assert entry["epistemology"] in VALID_EPISTEMOLOGIES, (
                f"Pillar {entry['pillar']} has invalid epistemology: "
                f"{entry['epistemology']}"
            )

    def test_pillar_10_is_formal_analogy(self):
        p10 = next(e for e in self.table if str(e["pillar"]) == "10")
        assert p10["epistemology"] == FORMAL_ANALOGY

    def test_pillar_15_is_falsifiable_prediction(self):
        p15 = next(e for e in self.table if str(e["pillar"]) == "15")
        assert p15["epistemology"] == FALSIFIABLE_PREDICTION

    def test_pillar_15b_is_falsifiable_prediction(self):
        p15b = next(e for e in self.table if str(e["pillar"]) == "15-B")
        assert p15b["epistemology"] == FALSIFIABLE_PREDICTION

    def test_pillar_14_is_conditional_theorem(self):
        p14 = next(e for e in self.table if str(e["pillar"]) == "14")
        assert p14["epistemology"] == CONDITIONAL_THEOREM

    def test_pillar_1_is_physics_derivation(self):
        p1 = next(e for e in self.table if str(e["pillar"]) == "1")
        assert p1["epistemology"] == PHYSICS_DERIVATION

    def test_pillar_70d_is_physics_derivation(self):
        p70 = next(e for e in self.table if str(e["pillar"]) == "70-D")
        assert p70["epistemology"] == PHYSICS_DERIVATION

    def test_pillar_100_is_physics_derivation(self):
        p100 = next(e for e in self.table if str(e["pillar"]) == "100")
        assert p100["epistemology"] == PHYSICS_DERIVATION

    def test_at_least_5_physics_derivations(self):
        phys = [e for e in self.table if e["epistemology"] == PHYSICS_DERIVATION]
        assert len(phys) >= 5

    def test_at_least_10_formal_analogies(self):
        anal = [e for e in self.table if e["epistemology"] == FORMAL_ANALOGY]
        assert len(anal) >= 10

    def test_at_least_1_falsifiable_prediction(self):
        fals = [e for e in self.table if e["epistemology"] == FALSIFIABLE_PREDICTION]
        assert len(fals) >= 1

    def test_pillar_15_exception_note_mentions_cop(self):
        p15 = next(e for e in self.table if str(e["pillar"]) == "15")
        assert "COP" in p15["exception_note"] or "calorimetry" in p15["exception_note"].lower()

    def test_pillar_26_is_formal_analogy(self):
        p26 = next(e for e in self.table if str(e["pillar"]) == "26")
        assert p26["epistemology"] == FORMAL_ANALOGY

    def test_pillar_26_analogy_coupling_mentions_kcs(self):
        p26 = next(e for e in self.table if str(e["pillar"]) == "26")
        assert "K_CS" in p26["analogy_coupling"]

    def test_all_module_paths_non_empty(self):
        for entry in self.table:
            assert entry["module_path"], f"Pillar {entry['pillar']} has empty module_path"

    def test_all_domains_non_empty(self):
        for entry in self.table:
            assert entry["domain"], f"Pillar {entry['pillar']} has empty domain"


# ---------------------------------------------------------------------------
# epistemics_summary()
# ---------------------------------------------------------------------------

class TestEpistemicsSummary:

    @pytest.fixture(autouse=True)
    def summary(self):
        self.summary = epistemics_summary()

    def test_returns_dict(self):
        assert isinstance(self.summary, dict)

    def test_required_keys(self):
        assert {"total_pillars", "counts_by_category", "pillar_lists", "summary", "section"}.issubset(
            self.summary.keys()
        )

    def test_section_label(self):
        assert self.summary["section"] == "§XIV.4"

    def test_total_matches_table_length(self):
        table = pillar_epistemics_table()
        assert self.summary["total_pillars"] == len(table)

    def test_counts_sum_to_total(self):
        total = self.summary["total_pillars"]
        count_sum = sum(self.summary["counts_by_category"].values())
        assert count_sum == total

    def test_summary_text_mentions_formal_analogy(self):
        assert "FORMAL_ANALOGY" in self.summary["summary"] or "formal analogy" in self.summary["summary"].lower()

    def test_summary_text_mentions_pillar_15(self):
        assert "15" in self.summary["summary"]

    def test_pillar_lists_contains_15(self):
        assert "15" in self.summary["pillar_lists"][FALSIFIABLE_PREDICTION]


# ---------------------------------------------------------------------------
# cold_fusion_physics_link() (imported separately)
# ---------------------------------------------------------------------------

class TestColdFusionPhysicsLink:

    @pytest.fixture(autouse=True)
    def link(self):
        self.link = cold_fusion_physics_link()

    def test_returns_dict(self):
        assert isinstance(self.link, dict)

    def test_epistemology_is_falsifiable_prediction(self):
        assert self.link["epistemology"] == "FALSIFIABLE_PREDICTION"

    def test_section_label(self):
        assert self.link["section"] == "§XIV.4"

    def test_chain_has_four_steps(self):
        assert len(self.link["chain"]) == 4

    def test_step1_mentions_m_kk(self):
        assert "M_KK" in self.link["chain"][0]["um_constant"]

    def test_step3_mentions_gamow(self):
        step3 = self.link["chain"][2]
        assert "Gamow" in step3["claim"] or "10^47" in step3["claim"]

    def test_falsification_criteria_has_three_items(self):
        assert len(self.link["falsification_criteria"]) == 3

    def test_f1_criterion_mentions_cop(self):
        assert "COP" in self.link["falsification_criteria"][0]

    def test_honest_note_mentions_only_pillar_in_range(self):
        assert "ONLY" in self.link["honest_note"] or "only" in self.link["honest_note"]

    def test_um_constants_listed(self):
        assert len(self.link["um_constants_used"]) >= 3
