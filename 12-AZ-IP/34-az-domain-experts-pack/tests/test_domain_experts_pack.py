# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_domain_experts_pack import MATERIALS_EXPERT, SPECTROSCOPY_EXPERT, DomainExpert


def test_materials_expert_builds_a_nonempty_index():
    n = MATERIALS_EXPERT.build()
    assert n > 0


def test_materials_expert_answers_polariton_query():
    MATERIALS_EXPERT.build()
    results = MATERIALS_EXPERT.query("polariton vortex critical angle")
    assert len(results) > 0
    assert any("polariton" in r["symbol"].lower() or "vortex" in r["text"].lower() for r in results)


def test_spectroscopy_expert_builds_a_nonempty_index():
    n = SPECTROSCOPY_EXPERT.build()
    assert n > 0


def test_spectroscopy_expert_answers_orbital_query():
    SPECTROSCOPY_EXPERT.build()
    results = SPECTROSCOPY_EXPERT.query("fine structure orbital spectroscopy")
    assert len(results) > 0


def test_domain_expert_query_before_build_builds_lazily():
    expert = DomainExpert("materials-science", MATERIALS_EXPERT.source_dir)
    results = expert.query("polariton")
    assert isinstance(results, list)


def test_domain_expert_query_empty_question_returns_empty():
    MATERIALS_EXPERT.build()
    assert MATERIALS_EXPERT.query("") == []


def test_domain_expert_query_no_overlap_returns_empty():
    MATERIALS_EXPERT.build()
    assert MATERIALS_EXPERT.query("xyzxyz_not_a_real_word_qqq") == []


def test_domain_expert_on_missing_directory_builds_empty_index():
    expert = DomainExpert("nonexistent", MATERIALS_EXPERT.source_dir / "does-not-exist")
    assert expert.build() == 0
    assert expert.query("anything") == []


def test_domain_expert_results_are_ranked_by_score_descending():
    MATERIALS_EXPERT.build()
    results = MATERIALS_EXPERT.query("polariton vortex critical angle feature velocity")
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)
