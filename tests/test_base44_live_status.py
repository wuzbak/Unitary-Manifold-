# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_base44_live_status.py — Base44 live-status integration tests

Covers:
  - 9-INFRASTRUCTURE/generate_live_status.py parsing and validation
  - 9-INFRASTRUCTURE/um_live_status.json generated artifact
  - bot/assistant_api.py /api/status canonical + compatibility response

0 test failures required.
"""

from __future__ import annotations

import importlib.util
import json
import re
from copy import deepcopy
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
STATUS_PATH = REPO_ROOT / "STATUS.md"
LIVE_STATUS_PATH = REPO_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def live_status_module():
    return _load_module(
        "generate_live_status_test",
        REPO_ROOT / "9-INFRASTRUCTURE" / "generate_live_status.py",
    )


@pytest.fixture(scope="module")
def assistant_api_module():
    pytest.importorskip("fastapi", reason="fastapi not installed")
    pytest.importorskip("httpx", reason="httpx not installed")
    pytest.importorskip("numpy", reason="numpy not installed")
    return _load_module(
        "assistant_api_base44_test",
        REPO_ROOT / "bot" / "assistant_api.py",
    )


def _first_sprint_entry() -> str:
    text = STATUS_PATH.read_text(encoding="utf-8")
    sprint_start = text.find("*v")
    assert sprint_start >= 0
    return text[sprint_start:].split("\n\n", 1)[0].strip()


def _extract_expected_tests() -> tuple[int, int, int, int]:
    pattern = (
        r"~?([\d,]+)\s+passed\s*[·•]\s*(\d+)\s+skipped\s*[·•]\s*(\d+)\s+deselected\s*[·•]\s*(\d+)\s+failed"
    )
    entry_match = re.search(pattern, _first_sprint_entry())
    if entry_match:
        return (
            int(entry_match.group(1).replace(",", "")),
            int(entry_match.group(2)),
            int(entry_match.group(3)),
            int(entry_match.group(4)),
        )
    full_text = STATUS_PATH.read_text(encoding="utf-8")
    sprint_start = full_text.find("*v")
    canonical_prefix = full_text[:sprint_start] if sprint_start >= 0 else full_text
    slash_match = re.search(
        r"Resumed combined regression record:\s*\*\*([\d,]+)\s*/\s*(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\*\*",
        canonical_prefix,
    )
    if slash_match:
        return (
            int(slash_match.group(1).replace(",", "")),
            int(slash_match.group(2)),
            int(slash_match.group(3)),
            int(slash_match.group(4)),
        )
    all_matches = re.findall(pattern, canonical_prefix)
    assert all_matches
    passed, skipped, deselected, failed = all_matches[-1]
    return (
        int(passed.replace(",", "")),
        int(skipped),
        int(deselected),
        int(failed),
    )


def test_build_live_status_matches_headline_entry(live_status_module):
    entry = _first_sprint_entry()
    version_match = re.search(r"\*v([\d.]+) Sprint (\w+)", entry)
    expected_lean4 = int(re.findall(r"Lean4[^)]*?(?:total\s+|→)(\d{3,5})", entry)[0])
    expected_tests = _extract_expected_tests()
    expected_next_slot = int(re.search(r"next slot (\d+)", entry).group(1))

    data = live_status_module.build_live_status()

    assert data["meta"]["version"] == version_match.group(1)
    assert data["meta"]["sprint"] == version_match.group(2)
    assert data["tests"]["passed"] == expected_tests[0]
    assert data["tests"]["skipped"] == expected_tests[1]
    assert data["tests"]["deselected"] == expected_tests[2]
    assert data["tests"]["failed"] == expected_tests[3]
    assert data["lean4"]["theorem_count"] == expected_lean4
    assert data["pillars"]["next_slot"] == expected_next_slot


def test_live_status_validation_passes(live_status_module):
    data = live_status_module.build_live_status()
    assert live_status_module.validate(data) == []


def test_status_distinguishes_registry_counts_from_scientific_proofs(live_status_module):
    data = live_status_module.build_live_status()
    assert data["lean4"]["physical_proof_count"] is None
    assert data["lean4"]["count_scope"] == "HISTORICAL_DECLARATIONS_NOT_PHYSICAL_PROOF_OBLIGATIONS"
    assessment = data["scientific_assessment"]
    assert assessment["closure_earned"] is False
    assert assessment["photon_origin"].startswith("OPEN:")
    assert assessment["cmb_normalization"].startswith("CALIBRATED:")
    assert "Historical" in data["meta"]["regression_provenance"]
    assert data["physics"]["birefringence_admissible_window"] == [0.22, 0.38]
    assert data["physics"]["birefringence_gap_forbidden"] == [0.29, 0.31]


def test_generated_live_status_file_is_current(live_status_module):
    assert LIVE_STATUS_PATH.exists(), "um_live_status.json not found — run 9-INFRASTRUCTURE/generate_live_status.py"
    repo_json = json.loads(LIVE_STATUS_PATH.read_text(encoding="utf-8"))
    assert repo_json == live_status_module.build_live_status()


def test_live_status_includes_historical_continuity(live_status_module):
    data = live_status_module.build_live_status()
    first = data["historical_continuity"][0]
    assert first["version"] == data["meta"]["version"]
    assert first["sprint"] == data["meta"]["sprint"]
    assert first["next_slot"] == data["pillars"]["next_slot"]
    pillars_label = str(first["pillars"])
    assert re.fullmatch(r"\d+(?:-\d+)?", pillars_label)
    current_total = data["pillars"]["total_slots"]
    if "-" in pillars_label:
        start, end = pillars_label.split("-", 1)
        assert len(data["historical_continuity"]) > 1
        assert int(start) == int(data["historical_continuity"][1]["next_slot"])
        assert int(end) == current_total
    else:
        assert int(pillars_label) == current_total
    assert any(
        entry == {"version": "37.5", "sprint": "CS", "pillars": "1119", "next_slot": 1120}
        for entry in data["historical_continuity"]
    )


def test_generated_live_status_has_no_keys():
    assert LIVE_STATUS_PATH.exists(), "um_live_status.json not found — run 9-INFRASTRUCTURE/generate_live_status.py"
    text = LIVE_STATUS_PATH.read_text(encoding="utf-8")
    assert re.search(r"\bsk-[A-Za-z0-9]{20,}", text) is None
    assert "OPENROUTER_API_KEY" not in text
    assert "HF_API_TOKEN" not in text


def test_assistant_api_status_uses_live_status(assistant_api_module, live_status_module):
    from fastapi.testclient import TestClient

    client = TestClient(assistant_api_module.app)
    response = client.get("/api/status")
    assert response.status_code == 200

    payload = response.json()
    live_status = live_status_module.build_live_status()

    assert payload["meta"]["version"] == live_status["meta"]["version"]
    assert payload["tests"]["passed"] == live_status["tests"]["passed"]
    assert payload["lean4"]["theorem_count"] == live_status["lean4"]["theorem_count"]
    assert payload["pillars"]["next_slot"] == live_status["pillars"]["next_slot"]
    assert payload["tests_passed"] == live_status["tests"]["passed"]
    assert payload["tests_skipped"] == live_status["tests"]["skipped"]
    assert payload["tests_deselected"] == live_status["tests"]["deselected"]
    assert payload["tests_failed"] == live_status["tests"]["failed"]
    assert payload["lean4_theorems"] == live_status["lean4"]["theorem_count"]
    assert payload["pillars_hardgate"] == live_status["pillars"]["hardgate_count"]
    assert payload["pillars_total"] == live_status["pillars"]["total_slots"]
    assert payload["next_pillar_slot"] == live_status["pillars"]["next_slot"]
    assert payload["status_source"]
    assert payload["regression"].startswith("Historical regression:")
    assert "foundation obligations remain open" in payload["epistemic_status"]


def test_live_status_does_not_publish_unsupported_detector_or_mass_claims(live_status_module):
    data = live_status_module.build_live_status()
    predictions = {row["id"]: row for row in data["predictions"]}
    assert data["physics"]["kk_graviton_mass_tev"] is None
    assert predictions["EXP-5"]["status"] == "MODEL_DEPENDENT_UNESTABLISHED"
    assert "0.403 TeV" in predictions["EXP-5"]["verdict"]
    assert predictions["EXP-7"]["status"] == "UNSUPPORTED"
    assert predictions["EXP-7"]["cross_section_cm2"] is None
    assert predictions["EXP-7"]["limit_ratio"] is None
    assert "not an operative physical falsifier" in predictions["EXP-7"]["kill_condition_scope"]


@pytest.mark.parametrize("experiment", ["EXP-5", "EXP-7"])
def test_validation_rejects_fabricated_detector_pass(live_status_module, experiment):
    data = deepcopy(live_status_module.build_live_status())
    next(row for row in data["predictions"] if row["id"] == experiment)["status"] = "PASS"
    assert any(experiment in error for error in live_status_module.validate(data))


@pytest.mark.parametrize("field", ["cross_section_cm2", "limit_ratio"])
def test_validation_rejects_physical_values_for_unsupported_proxy(live_status_module, field):
    data = deepcopy(live_status_module.build_live_status())
    next(row for row in data["predictions"] if row["id"] == "EXP-7")[field] = 1.0
    assert any("EXP-7" in error for error in live_status_module.validate(data))


@pytest.mark.parametrize("version", ["unknown", "999.9"])
def test_validation_rejects_noncanonical_version(live_status_module, version):
    data = deepcopy(live_status_module.build_live_status())
    data["meta"]["version"] = version
    assert any("meta.version" in error for error in live_status_module.validate(data))


def test_generator_check_compares_artifact(live_status_module, tmp_path, capsys):
    output = tmp_path / "status.json"
    assert live_status_module.main(["--output", str(output)]) == 0
    assert live_status_module.main(["--check", "--output", str(output)]) == 0
    recorded = json.loads(output.read_text())
    recorded["meta"]["version"] = "unknown"
    output.write_text(json.dumps(recorded))
    assert live_status_module.main(["--check", "--output", str(output)]) == 1
    assert "stale live-status artifact" in capsys.readouterr().err


@pytest.mark.parametrize("contents", [None, "{invalid json"])
def test_generator_check_reports_missing_or_invalid_artifact(live_status_module, tmp_path, capsys, contents):
    output = tmp_path / "status.json"
    if contents is not None:
        output.write_text(contents)
    assert live_status_module.main(["--check", "--output", str(output)]) == 1
    assert "cannot read live-status artifact" in capsys.readouterr().err


def test_api_status_unavailable_is_not_zero_failures(assistant_api_module, monkeypatch, caplog):
    monkeypatch.setattr(assistant_api_module, "_build_live_status_from_generator", lambda: None)
    monkeypatch.setattr(assistant_api_module, "_read_json_file", lambda path: None)
    payload = assistant_api_module.build_status_response()
    assert payload["status_source"] == "unavailable"
    assert payload["tests"] == dict.fromkeys(("passed", "skipped", "deselected", "failed"))
    for field in ("tests_passed", "tests_skipped", "tests_deselected", "tests_failed", "failures"):
        assert payload[field] is None
    assert payload["regression"].startswith("Regression unavailable:")
    assert payload["epistemic_status"].startswith("Unavailable:")
    assert "Live status unavailable" in caplog.text


@pytest.mark.parametrize("source", ["artifact", "legacy", "partial_legacy", "string_legacy"])
def test_api_status_fallback_preserves_provenance(assistant_api_module, live_status_module, monkeypatch, source):
    monkeypatch.setattr(assistant_api_module, "_build_live_status_from_generator", lambda: None)
    canonical = live_status_module.build_live_status()
    legacy = {"version": "34.9", "tests_passed": 63787}
    if source in ("legacy", "string_legacy"):
        legacy.update(tests_skipped=23, tests_deselected=12, tests_failed=0)
    if source == "string_legacy":
        legacy.update(tests_passed="63787", tests_skipped="23", tests_deselected="12", tests_failed="0")

    def read_status(path):
        if source == "artifact" and path == assistant_api_module.LIVE_STATUS_PATH:
            return canonical
        if source != "artifact" and path == assistant_api_module.LEGACY_STATUS_PATH:
            return legacy
        return None

    monkeypatch.setattr(assistant_api_module, "_read_json_file", read_status)
    payload = assistant_api_module.build_status_response()
    assert "foundation obligations remain open" in payload["epistemic_status"]
    if source == "partial_legacy":
        assert payload["tests_failed"] is None
        assert payload["failures"] is None
        assert payload["regression"].startswith("Regression unavailable:")
    else:
        assert payload["regression"].startswith("Historical regression:")
        assert payload["tests_failed"] == 0
        assert payload["tests"]["failed"] == 0


def test_legacy_assistant_retrieval_marks_historical_claim_scope(assistant_api_module):
    context = assistant_api_module.retrieve_context("pillar 2")
    assert context.startswith("[Current evidence boundary]")
    assert "historical navigation data, not current closure" in context
    assert "HARDGATE is a registry label" in context
    assert "docs/TRUTH_LAYER.md#foundation-reassessment" in context


@pytest.mark.parametrize("payload,expected_passed,expected_failed", [
    ({"tests_passed": None, "tests_failed": None, "tests": {"passed": 0, "failed": 0}}, "Unknown", "Unknown"),
    ({"tests": {"passed": 0, "failed": 0}}, "0", "0"),
    ({}, "Unknown", "Unknown"),
    (None, "Unknown", "Unknown"),
    ({"api_unavailable": True, "snapshot": {"tests_passed": 10, "tests_failed": 0}}, "10", "0"),
])
def test_verification_dashboard_preserves_unknown_counts(payload, expected_passed, expected_failed):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js required for dashboard execution")
    script = """
const fs = require('fs');
const vm = require('vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const code = [...html.matchAll(/<script>([\\s\\S]*?)<\\/script>/g)]
  .map(match => match[1]).find(source => source.includes('function loadStatusJson'));
const payload = JSON.parse(process.argv[2]);
const nodes = {};
const errors = [];
const requests = [];
const document = {
  getElementById: id => nodes[id] ||= {textContent: 'Unknown', insertAdjacentHTML() {}},
  addEventListener: (name, callback) => callback()
};
vm.runInNewContext(code, {
  document,
  console: {warn() {}, error: message => errors.push(message)},
  UM: {verificationDashboardData: () => ({
    admissions: [], predictions: [], primary_falsifier: 'beta',
    tests_total: 63787, lean4_total: 4080, pillars_total: 1135
  })},
  fetch: url => {
    requests.push(url);
    return payload === null || (payload.api_unavailable && url === '/api/status')
      ? Promise.reject(new Error('status unavailable'))
      : Promise.resolve({ok: true, json: () => Promise.resolve(payload.snapshot || payload)});
  }
});
setImmediate(() => console.log(JSON.stringify({nodes, errors, requests})));
"""
    result = subprocess.run(
        [node, "-e", script, str(REPO_ROOT / "public-site/apps/verification-dashboard.html"), json.dumps(payload)],
        check=True, capture_output=True, text=True,
    )
    rendered = json.loads(result.stdout)
    assert rendered["nodes"]["vd-tests"]["textContent"] == expected_passed
    assert rendered["nodes"]["vd-failed"]["textContent"] == expected_failed
    assert rendered["requests"] == (
        ["/api/status", "../data/status.json"]
        if payload is None or payload.get("api_unavailable") else ["/api/status"]
    )
    if payload is None:
        assert "Verification status unavailable" in rendered["errors"]
        assert "Status unavailable" in rendered["nodes"]["vd-summary"]["textContent"]
