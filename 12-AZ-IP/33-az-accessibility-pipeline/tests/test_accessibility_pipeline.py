# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_accessibility_pipeline import (
    split_into_reading_segments,
    suggest_visual_concepts,
    route_recognizable_claims,
    build_accessibility_report,
)


def test_split_into_reading_segments_basic():
    segments = split_into_reading_segments("First sentence. Second sentence! Third?")
    assert [s.text for s in segments] == ["First sentence.", "Second sentence!", "Third?"]
    assert [s.index for s in segments] == [0, 1, 2]


def test_split_into_reading_segments_empty_text():
    assert split_into_reading_segments("   ") == []


def test_suggest_visual_concepts_matches_birefringence():
    concepts = suggest_visual_concepts("LiteBIRD will test the birefringence prediction.")
    assert "birefringence" in concepts


def test_suggest_visual_concepts_matches_multiple():
    concepts = suggest_visual_concepts(
        "The spectral index n_s and the braid winding number both matter here."
    )
    assert "cmb" in concepts
    assert "braid" in concepts


def test_suggest_visual_concepts_no_match_returns_empty():
    assert suggest_visual_concepts("The weather today is sunny.") == []


def test_route_recognizable_claims_routes_birefringence_to_litebird():
    results = route_recognizable_claims("This passage is about birefringence.")
    assert len(results) == 1
    assert results[0]["exp_id"] == "EXP-1"
    assert results[0]["verdict"] == "AWAITING_DATA"


def test_route_recognizable_claims_dedupes_same_experiment():
    results = route_recognizable_claims("dark energy and w_a both route to DESI")
    exp_ids = [r["exp_id"] for r in results]
    assert exp_ids.count("EXP-2") == 1


def test_route_recognizable_claims_no_match_returns_empty():
    assert route_recognizable_claims("Nothing physics-related here.") == []


def test_build_accessibility_report_combines_all_three_phases():
    report = build_accessibility_report(
        "The birefringence prediction from LiteBIRD matters. It is a CMB test."
    )
    assert len(report.segments) == 2
    assert "birefringence" in report.suggested_visuals
    assert any(v["exp_id"] == "EXP-1" for v in report.claim_verdicts)
