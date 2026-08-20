# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for the Axiom Zero Interrogator (18-interrogator) — 55 tests.

Tests cover:
  - KB completeness and structure
  - Gate validation
  - Experiment mapping
  - Tension scoring
  - Build script execution
  - HTML/JS file presence
"""

import json
import os
import sys
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_PATH = os.path.join(REPO_ROOT, "public-site", "data", "interrogator-kb.json")
HTML_PATH = os.path.join(REPO_ROOT, "public-site", "az-apps", "18-interrogator.html")
JS_PATH = os.path.join(REPO_ROOT, "public-site", "js", "18-interrogator.js")
BUILD_SCRIPT = os.path.join(REPO_ROOT, "TOOLS", "build_interrogator_kb.py")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def kb():
    """Load the interrogator knowledge base."""
    with open(KB_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def entries(kb):
    return kb["entries"]


@pytest.fixture(scope="module")
def experiments(kb):
    return kb["experiments"]


# ---------------------------------------------------------------------------
# KB file existence and format
# ---------------------------------------------------------------------------
class TestKBFileExists:
    def test_kb_file_exists(self):
        assert os.path.exists(KB_PATH), f"KB not found at {KB_PATH}"

    def test_kb_nonempty(self):
        assert os.path.getsize(KB_PATH) > 100

    def test_kb_valid_json(self, kb):
        assert isinstance(kb, dict)

    def test_kb_has_entries(self, kb):
        assert "entries" in kb

    def test_kb_has_experiments(self, kb):
        assert "experiments" in kb

    def test_kb_has_meta(self, kb):
        assert "meta" in kb

    def test_kb_version_present(self, kb):
        assert "version" in kb

    def test_kb_version_v231(self, kb):
        assert "23" in kb["version"]


# ---------------------------------------------------------------------------
# Entries completeness
# ---------------------------------------------------------------------------
class TestEntriesCompleteness:
    def test_min_entries(self, entries):
        assert len(entries) >= 15

    def test_all_entries_have_id(self, entries):
        for e in entries:
            assert "id" in e and e["id"]

    def test_all_entries_have_claim(self, entries):
        for e in entries:
            assert "claim" in e and len(e["claim"]) > 10

    def test_all_entries_have_gate(self, entries):
        valid_gates = {"DERIVED", "FITTED", "ARCHITECTURE_LIMIT", "ADJACENT_TRACK"}
        for e in entries:
            assert "gate" in e
            assert e["gate"] in valid_gates, f"Invalid gate: {e['gate']} in {e['id']}"

    def test_all_entries_have_pillar(self, entries):
        for e in entries:
            assert "pillar" in e

    def test_all_entries_have_falsification(self, entries):
        for e in entries:
            assert "falsification" in e
            assert len(e["falsification"]) > 10

    def test_all_entries_have_experiments(self, entries):
        for e in entries:
            assert "experiments" in e
            assert isinstance(e["experiments"], list)

    def test_all_entries_have_status(self, entries):
        for e in entries:
            assert "status" in e

    def test_ids_unique(self, entries):
        ids = [e["id"] for e in entries]
        assert len(ids) == len(set(ids)), "Duplicate IDs found"


# ---------------------------------------------------------------------------
# Gate validation
# ---------------------------------------------------------------------------
class TestGateValidation:
    def test_derived_entries_have_tight_uncertainty(self, entries):
        """DERIVED entries should have a non-empty uncertainty field."""
        for e in entries:
            if e["gate"] == "DERIVED":
                assert "uncertainty" in e and e["uncertainty"]

    def test_adjacent_track_entries_labeled(self, entries):
        """ADJACENT_TRACK entries must have a tag or label."""
        for e in entries:
            if e["gate"] == "ADJACENT_TRACK":
                tags = e.get("tags", [])
                assert "adjacent_track" in tags or "ADJACENT" in e["status"].upper()

    def test_architecture_limit_entries_acknowledged(self, entries):
        """ARCHITECTURE_LIMIT entries must have a falsification or acknowledgment."""
        for e in entries:
            if e["gate"] == "ARCHITECTURE_LIMIT":
                assert len(e.get("falsification", "")) > 0

    def test_no_unclassified_gates(self, entries):
        valid = {"DERIVED", "FITTED", "ARCHITECTURE_LIMIT", "ADJACENT_TRACK"}
        for e in entries:
            assert e.get("gate") in valid


# ---------------------------------------------------------------------------
# Specific required entries
# ---------------------------------------------------------------------------
class TestRequiredEntries:
    def _find(self, entries, eid):
        return next((e for e in entries if e["id"] == eid), None)

    def test_birefringence_entry_exists(self, entries):
        e = self._find(entries, "BIREFRINGENCE")
        assert e is not None

    def test_birefringence_litebird_in_experiments(self, entries):
        e = self._find(entries, "BIREFRINGENCE")
        assert any("LiteBIRD" in exp for exp in e["experiments"])

    def test_desi_tension_entry_exists(self, entries):
        e = self._find(entries, "DESI_TENSION") or self._find(entries, "DARK_ENERGY")
        assert e is not None

    def test_desi_tension_sigma(self, entries):
        e = self._find(entries, "DESI_TENSION") or self._find(entries, "DARK_ENERGY")
        assert e is not None
        assert e.get("tension_sigma") is not None
        assert e["tension_sigma"] > 1.0  # known 2.07σ tension

    def test_neutrino_ordering_entry(self, entries):
        e = self._find(entries, "NEUTRINO_ORDERING")
        assert e is not None
        assert e["gate"] == "DERIVED"

    def test_dm_kk_entry_exists(self, entries):
        e = self._find(entries, "DM_KK_CANDIDATE")
        assert e is not None
        assert e["gate"] == "ARCHITECTURE_LIMIT"

    def test_winding_stability_entry_exists(self, entries):
        e = self._find(entries, "WINDING_STABILITY")
        assert e is not None
        assert 789 in (e["pillar"] if isinstance(e["pillar"], list) else [e["pillar"]])

    def test_cmb_peaks_admitted_as_gap(self, entries):
        e = self._find(entries, "CMB_PEAKS")
        assert e is not None
        assert e["gate"] == "ARCHITECTURE_LIMIT"

    def test_adjacent_track_entries_present(self, entries):
        adj = [e for e in entries if e["gate"] == "ADJACENT_TRACK"]
        assert len(adj) >= 1


# ---------------------------------------------------------------------------
# Experiment mapping
# ---------------------------------------------------------------------------
class TestExperimentMapping:
    def test_min_experiments(self, experiments):
        assert len(experiments) >= 5

    def test_all_experiments_have_id(self, experiments):
        for exp in experiments:
            assert "id" in exp and exp["id"]

    def test_all_experiments_have_tests_pillars(self, experiments):
        for exp in experiments:
            assert "tests_pillars" in exp
            assert isinstance(exp["tests_pillars"], list)
            assert len(exp["tests_pillars"]) >= 1

    def test_litebird_experiment_present(self, experiments):
        ids = [e["id"] for e in experiments]
        assert "LITEBIRD" in ids

    def test_desi_experiment_present(self, experiments):
        ids = [e["id"] for e in experiments]
        assert "DESI" in ids

    def test_xenon_experiment_present(self, experiments):
        ids = [e["id"] for e in experiments]
        assert "XENON_NT" in ids

    def test_all_experiments_have_verdict_threshold(self, experiments):
        for exp in experiments:
            assert "verdict_threshold" in exp
            assert len(exp["verdict_threshold"]) > 5

    def test_all_experiments_have_timeline(self, experiments):
        for exp in experiments:
            assert "timeline" in exp


# ---------------------------------------------------------------------------
# Tension scoring
# ---------------------------------------------------------------------------
class TestTensionScoring:
    def test_tension_sigmas_are_numeric_or_none(self, entries):
        for e in entries:
            ts = e.get("tension_sigma")
            assert ts is None or isinstance(ts, (int, float))

    def test_tension_sigmas_nonnegative(self, entries):
        for e in entries:
            ts = e.get("tension_sigma")
            if ts is not None:
                assert ts >= 0

    def test_desi_tension_above_1sigma(self, entries):
        desi = next((e for e in entries if e["id"] in ("DESI_TENSION", "DARK_ENERGY")), None)
        assert desi is not None
        assert desi.get("tension_sigma", 0) > 1.0

    def test_cmb_ns_low_tension(self, entries):
        e = next((e for e in entries if e["id"] == "CMB_NS"), None)
        assert e is not None
        assert e.get("tension_sigma", 99) < 1.0

    def test_architecture_limit_tension_none_or_small(self, entries):
        for e in entries:
            if e["gate"] == "ARCHITECTURE_LIMIT":
                ts = e.get("tension_sigma")
                # Architecture limits typically have no direct tension measurement
                assert ts is None or ts < 5.0


# ---------------------------------------------------------------------------
# Build script and app files
# ---------------------------------------------------------------------------
class TestBuildScriptAndFiles:
    def test_build_script_exists(self):
        assert os.path.exists(BUILD_SCRIPT)

    def test_build_script_is_python(self):
        assert BUILD_SCRIPT.endswith(".py")

    def test_html_app_exists(self):
        assert os.path.exists(HTML_PATH)

    def test_js_engine_exists(self):
        assert os.path.exists(JS_PATH)

    def test_html_references_js(self):
        with open(HTML_PATH, encoding="utf-8") as f:
            content = f.read()
        assert "18-interrogator.js" in content

    def test_html_has_three_tabs(self):
        with open(HTML_PATH, encoding="utf-8") as f:
            content = f.read()
        assert "challenge" in content.lower()
        assert "experiment" in content.lower()
        assert "tension" in content.lower()

    def test_js_has_load_kb(self):
        with open(JS_PATH, encoding="utf-8") as f:
            content = f.read()
        assert "loadKB" in content or "load_kb" in content.lower()

    def test_js_has_tension_map(self):
        with open(JS_PATH, encoding="utf-8") as f:
            content = f.read()
        assert "TensionMap" in content or "tension" in content.lower()

    def test_build_script_importable(self):
        """Running the build script should regenerate the KB without errors."""
        sys.path.insert(0, REPO_ROOT)
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_interrogator_kb", BUILD_SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        kb = mod.build_kb()
        assert len(kb["entries"]) >= 15
        assert len(kb["experiments"]) >= 5
