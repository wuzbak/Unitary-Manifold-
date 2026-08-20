# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""
Tests for the Axiom Zero Interrogator app.

Covers:
- KB JSON completeness and schema
- JS engine constants
- HTML structure
- KB builder script
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
KB_PATH     = REPO_ROOT / "public-site" / "data" / "interrogator-kb.json"
JS_PATH     = REPO_ROOT / "public-site" / "js" / "18-interrogator.js"
HTML_PATH   = REPO_ROOT / "public-site" / "az-apps" / "18-interrogator.html"
BUILDER_PATH = REPO_ROOT / "TOOLS" / "build_interrogator_kb.py"

KB_TEXT   = KB_PATH.read_text(encoding="utf-8")
JS_TEXT   = JS_PATH.read_text(encoding="utf-8")
HTML_TEXT = HTML_PATH.read_text(encoding="utf-8")
KB        = json.loads(KB_TEXT)


# ── KB JSON schema ────────────────────────────────────────────────────────

def test_kb_has_version():
    assert KB["version"] == "v23.0"

def test_kb_has_claims():
    assert "claims" in KB

def test_kb_claim_count_positive():
    assert KB["total_claims"] >= 15

def test_kb_claims_length_matches_total():
    assert len(KB["claims"]) == KB["total_claims"]

def test_kb_has_experiments():
    assert "experiments" in KB
    assert len(KB["experiments"]) == 7

def test_kb_has_tensions():
    assert "tensions" in KB
    assert len(KB["tensions"]) >= 5

def test_kb_has_gate_types():
    assert "gate_types" in KB
    assert len(KB["gate_types"]) >= 8

# ── Claim schema validation ───────────────────────────────────────────────

REQUIRED_CLAIM_FIELDS = ["id", "pillar", "track", "claim", "tags", "gate",
                          "predicted_value", "observed_value", "falsification"]

def test_all_claims_have_required_fields():
    for c in KB["claims"]:
        for f in REQUIRED_CLAIM_FIELDS:
            assert f in c, f"Claim {c.get('id', '?')} missing field {f!r}"

def test_all_claim_ids_unique():
    ids = [c["id"] for c in KB["claims"]]
    assert len(ids) == len(set(ids))

def test_all_claim_tracks_valid():
    valid_tracks = {"HARDGATE", "ADJACENT_TRACK", "OPEN_TENSION"}
    for c in KB["claims"]:
        assert c["track"] in valid_tracks, f"Claim {c['id']} has invalid track {c['track']!r}"

def test_all_claim_tags_are_lists():
    for c in KB["claims"]:
        assert isinstance(c["tags"], list), f"Claim {c['id']} has non-list tags"

def test_all_claim_gates_nonempty():
    for c in KB["claims"]:
        assert isinstance(c["gate"], str) and len(c["gate"]) > 3

def test_all_claim_claims_nonempty():
    for c in KB["claims"]:
        assert isinstance(c["claim"], str) and len(c["claim"]) > 10

# ── Key claims present ─────────────────────────────────────────────────────

def test_p002_ns_present():
    ids = {c["id"] for c in KB["claims"]}
    assert "p002_ns" in ids

def test_p786_basin_present():
    ids = {c["id"] for c in KB["claims"]}
    assert "p786_basin" in ids

def test_p787_falsmap_present():
    ids = {c["id"] for c in KB["claims"]}
    assert "p787_falsmap" in ids

def test_p015_cold_fusion_present():
    ids = {c["id"] for c in KB["claims"]}
    assert "p015_cold_fusion" in ids

def test_open_tensions_present():
    ids = {c["id"] for c in KB["claims"]}
    assert "open_cmb_amplitude" in ids
    assert "open_desi" in ids
    assert "open_fn_charges" in ids

# ── Claim specific epistemic values ─────────────────────────────────────────

def test_ns_claim_gate_is_derived():
    c = next(c for c in KB["claims"] if c["id"] == "p002_ns")
    assert c["gate"] == "DERIVED"

def test_stability_basin_gate():
    c = next(c for c in KB["claims"] if c["id"] == "p786_basin")
    assert c["gate"] == "WINDING_BASIN_CLOSED"

def test_cmb_peaks_gate_is_architecture_limit():
    c = next(c for c in KB["claims"] if c["id"] == "p780_cmb_peaks")
    assert c["gate"] == "ARCHITECTURE_LIMIT"

def test_cold_fusion_has_admission():
    c = next(c for c in KB["claims"] if c["id"] == "p015_cold_fusion")
    assert c["admission"] is not None and len(c["admission"]) > 10

def test_consciousness_is_adjacent_track():
    c = next(c for c in KB["claims"] if c["id"] == "p009_consciousness")
    assert c["track"] == "ADJACENT_TRACK"

def test_desi_has_tension_sigma():
    c = next(c for c in KB["claims"] if c["id"] == "open_desi")
    assert c["tension_sigma"] is not None
    assert c["tension_sigma"] > 1.0

# ── Experiment schema ──────────────────────────────────────────────────────

REQUIRED_EXP_FIELDS = ["id", "name", "tests_pillars", "primary", "status", "description"]

def test_all_experiments_have_required_fields():
    for e in KB["experiments"]:
        for f in REQUIRED_EXP_FIELDS:
            assert f in e, f"Experiment {e.get('id','?')} missing {f!r}"

def test_litebird_is_primary_falsifier():
    lb = next(e for e in KB["experiments"] if e["id"] == "litebird")
    assert lb["primary"] is True

def test_desi_experiment_present():
    ids = {e["id"] for e in KB["experiments"]}
    assert "desi" in ids

def test_juno_experiment_present():
    ids = {e["id"] for e in KB["experiments"]}
    assert "juno" in ids

def test_xenon_nt_experiment_present():
    ids = {e["id"] for e in KB["experiments"]}
    assert "xenon_nt" in ids

# ── Tension schema ────────────────────────────────────────────────────────

REQUIRED_TENSION_FIELDS = ["id", "label", "sigma", "confidence", "description",
                            "experiment", "pillar_ids"]

def test_all_tensions_have_required_fields():
    for t in KB["tensions"]:
        for f in REQUIRED_TENSION_FIELDS:
            assert f in t, f"Tension {t.get('id','?')} missing {f!r}"

def test_desi_tension_sigma_gt_1():
    t = next(t for t in KB["tensions"] if t["id"] == "desi_wa")
    assert t["sigma"] > 1.0

def test_birefringence_tension_present():
    ids = {t["id"] for t in KB["tensions"]}
    assert "birefringence" in ids

def test_tensions_confidence_in_range():
    for t in KB["tensions"]:
        c = t.get("confidence")
        if c is not None:
            assert 0.0 <= c <= 1.0, f"Tension {t['id']} confidence out of range: {c}"

# ── JS engine constants ────────────────────────────────────────────────────

def test_js_version():
    assert 'INTERROGATOR_VERSION = "v23.0"' in JS_TEXT

def test_js_gate_colors_present():
    assert "GATE_COLORS" in JS_TEXT

def test_js_derived_color():
    assert "DERIVED" in JS_TEXT
    assert "#30d158" in JS_TEXT  # green

def test_js_architecture_limit_color():
    assert "ARCHITECTURE_LIMIT" in JS_TEXT
    assert "#ff9f0a" in JS_TEXT  # orange

def test_js_score_match_function():
    assert "function scoreMatch" in JS_TEXT or "export function scoreMatch" in JS_TEXT

def test_js_search_claims_function():
    assert "searchClaims" in JS_TEXT

def test_js_claims_for_experiment_function():
    assert "claimsForExperiment" in JS_TEXT

def test_js_sorted_tensions_function():
    assert "sortedTensions" in JS_TEXT

def test_js_draw_tension_map_function():
    assert "drawTensionMap" in JS_TEXT

def test_js_render_claim_card_function():
    assert "renderClaimCard" in JS_TEXT

def test_js_interrogator_class():
    assert "class Interrogator" in JS_TEXT

def test_js_esc_html_function():
    assert "escHtml" in JS_TEXT

def test_js_gate_rank_function():
    assert "gateRank" in JS_TEXT

# ── HTML structure ────────────────────────────────────────────────────────

def test_html_title():
    assert "Interrogator" in HTML_TEXT

def test_html_product_id_badge():
    assert "Product 19" in HTML_TEXT

def test_html_three_tabs():
    assert "challenge" in HTML_TEXT
    assert "experiment" in HTML_TEXT
    assert "tension" in HTML_TEXT

def test_html_canvas_element():
    assert 'id="iq-tension-canvas"' in HTML_TEXT

def test_html_challenge_input():
    assert 'id="iq-challenge-input"' in HTML_TEXT

def test_html_challenge_btn():
    assert 'id="iq-challenge-btn"' in HTML_TEXT

def test_html_experiment_list():
    assert 'id="iq-experiment-list"' in HTML_TEXT

def test_html_tension_detail():
    assert 'id="iq-tension-detail"' in HTML_TEXT

def test_html_imports_interrogator_js():
    assert "18-interrogator.js" in HTML_TEXT

def test_html_stat_bar():
    assert "iq-statbar" in HTML_TEXT

def test_html_quick_chips():
    assert "iq-chip" in HTML_TEXT
    assert "birefringence" in HTML_TEXT

def test_html_offline_badge():
    assert "Offline" in HTML_TEXT or "offline" in HTML_TEXT

def test_html_nav_v23():
    assert "v23" in HTML_TEXT

def test_html_authorship_footer():
    assert "ThomasCory Walker-Pearson" in HTML_TEXT

# ── Builder script ────────────────────────────────────────────────────────

def test_builder_script_exists():
    assert BUILDER_PATH.exists()

def test_builder_script_has_main():
    builder_text = BUILDER_PATH.read_text(encoding="utf-8")
    assert "def main" in builder_text

def test_builder_script_has_kb_list():
    builder_text = BUILDER_PATH.read_text(encoding="utf-8")
    assert "KB:" in builder_text or "KB =" in builder_text

def test_builder_output_exists():
    assert KB_PATH.exists()

def test_builder_output_is_valid_json():
    data = json.loads(KB_TEXT)
    assert isinstance(data, dict)

# ── Cross-consistency ─────────────────────────────────────────────────────

def test_experiment_pillar_refs_exist_in_claims():
    claim_ids = {c["id"] for c in KB["claims"]}
    for exp in KB["experiments"]:
        for pid in exp["tests_pillars"]:
            assert pid in claim_ids, f"Experiment {exp['id']} references unknown claim {pid!r}"

def test_tension_pillar_refs_exist_in_claims():
    claim_ids = {c["id"] for c in KB["claims"]}
    for t in KB["tensions"]:
        for pid in t["pillar_ids"]:
            assert pid in claim_ids, f"Tension {t['id']} references unknown claim {pid!r}"

def test_all_hardgate_claims_have_falsification():
    for c in KB["claims"]:
        if c["track"] == "HARDGATE":
            assert c.get("falsification"), f"Hardgate claim {c['id']} has no falsification"

def test_no_toe_score_language():
    """No ToE score branding in any interrogator file."""
    for text, path in [(KB_TEXT, "KB"), (JS_TEXT, "JS"), (HTML_TEXT, "HTML")]:
        assert "ToE score" not in text, f"ToE score language found in {path}"
        assert "toe-score" not in text.lower(), f"toe-score found in {path}"
