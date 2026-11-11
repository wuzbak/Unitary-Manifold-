# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""The CodeQL slice manifest must cover every tracked Python file and drive the workflow."""

from __future__ import annotations

import importlib.util
import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("codeql_slices", REPO_ROOT / "TOOLS" / "checks" / "codeql_slices.py")
cs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cs)

needs_git = pytest.mark.skipif(
    shutil.which("git") is None or not (REPO_ROOT / ".git").exists(), reason="needs a git checkout"
)


@pytest.mark.parametrize("path,pattern,expected", [
    ("src/core/metric.py", "src", True),
    ("src2/x.py", "src", False),
    ("src", "src", True),
    ("setup.py", "*.py", True),
    ("src/core/metric.py", "*.py", False),          # '*' does not cross '/'
    ("12-AZ-IP/20-psicat-navigator/run_server.py", "12-AZ-IP/20-psicat-navigator/run*.py", True),
    ("12-AZ-IP/20-psicat-navigator/tools/run.py", "12-AZ-IP/20-psicat-navigator/run*.py", False),
    ("a/b/c/README.md", "**/*.md", True),
    ("README.md", "**/*.md", True),
    ("a/node_modules/x/y.js", "**/node_modules/**", True),
    ("public-site/js/app.js", "public-site/**", True),
])
def test_patterns_follow_codeql_path_semantics(path, pattern, expected):
    assert cs.matches(path, pattern) is expected


def test_manifest_is_well_formed():
    m = cs.load_manifest()
    assert "python" in m["coverage"]
    assert any(s["slice_id"] == "python-eige" for s in m["slices"])


def test_python_slice_paths_do_not_use_literal_files():
    m = cs.load_manifest()
    for s in m["slices"]:
        if s["language"] != "python":
            continue
        for path in s["paths"]:
            # The Python extractor walks literal paths as directories.
            assert any(char in path for char in "*?[") or not (REPO_ROOT / path).is_file(), path
    fixture = "12-AZ-IP/20-psicat-navigator/conftest.py"
    assert any(cs.in_slice(fixture, s, m["paths_ignore"]) for s in m["slices"])


def test_manifest_rejects_duplicate_ids_and_empty_paths(tmp_path):
    bad = {"slices": [{"slice_id": "a", "language": "python", "build_mode": "none", "paths": ["x"]},
                      {"slice_id": "a", "language": "python", "build_mode": "none", "paths": ["y"]}]}
    p = tmp_path / "m.json"
    p.write_text(json.dumps(bad))
    with pytest.raises(cs.SliceError, match="duplicate"):
        cs.load_manifest(p)
    bad["slices"] = [{"slice_id": "a", "language": "python", "build_mode": "none", "paths": [""]}]
    p.write_text(json.dumps(bad))
    with pytest.raises(cs.SliceError, match="empty path"):
        cs.load_manifest(p)


def test_coverage_reports_files_in_no_slice():
    m = {"coverage": {"python": [".py"]}, "paths_ignore": ["**/*.md"],
         "slices": [{"slice_id": "s", "language": "python", "build_mode": "none", "paths": ["src"]}]}
    r = cs.coverage(m, ["src/a.py", "lib/b.py", "src/README.md"])["python"]
    assert r["files"] == 2 and r["covered"] == 1 and r["missing"] == ["lib/b.py"]


def test_stale_slice_paths_are_reported():
    m = {"slices": [{"slice_id": "s", "language": "python", "build_mode": "none", "paths": ["src", "gone"]}]}
    assert cs.stale_paths(m, ["src/a.py"]) == ["s: gone"]


@needs_git
def test_every_tracked_python_file_is_in_a_codeql_slice():
    files = cs.tracked_files()
    m = cs.load_manifest()
    r = cs.coverage(m, files)["python"]
    assert r["missing"] == [], f"{len(r['missing'])} Python files are in no CodeQL slice: {r['missing'][:20]}"
    assert cs.stale_paths(m, files) == []


@needs_git
def test_eige_is_analysed_by_exactly_one_python_slice():
    m = cs.load_manifest()
    files = [f for f in cs.tracked_files() if f.startswith("12-AZ-IP/03-eige/") and f.endswith(".py")]
    assert files
    py = [s for s in m["slices"] if s["language"] == "python"]
    for f in files:
        assert [s["slice_id"] for s in py if cs.in_slice(f, s, m["paths_ignore"])] == ["python-eige"], f


def test_plan_selects_changed_slices_and_everything_when_the_plan_changes():
    m = cs.load_manifest()
    ids = lambda changed: [s["slice_id"] for s in cs.plan(m, changed)]  # noqa: E731
    assert ids(["12-AZ-IP/03-eige/eige/verify.py"]) == ["python-eige"]
    assert ids(["12-AZ-IP/03-eige/README.md"]) == []
    assert ids(None) == ids([]) == [s["slice_id"] for s in m["slices"]]
    for trigger in cs.PLAN_INPUTS:
        assert len(ids([trigger])) == len(m["slices"])


def test_workflow_contract_tests_are_analysed_by_repository_tooling():
    manifest = cs.load_manifest()
    path = ".github/tests/test_embedded_model_download_contract.py"
    selected = [
        s["slice_id"] for s in manifest["slices"]
        if s["language"] == "python" and cs.in_slice(path, s, manifest["paths_ignore"])
    ]
    assert selected == ["python-repository-tooling"]
    assert [s["slice_id"] for s in cs.plan(manifest, [path])] == selected


def test_android_suite_sources_have_language_specific_analysis_slices():
    manifest = cs.load_manifest()
    cases = {
        "12-AZ-IP/46-axiomzero-android-suite/scripts/build_catalog.py": (
            "python", "python-azip-product-46"
        ),
        "12-AZ-IP/46-axiomzero-android-suite/tests/test_catalog_sync.py": (
            "python", "python-azip-product-46"
        ),
        "12-AZ-IP/46-axiomzero-android-suite/app/src/main/java/com/axiomzero/androidsuite/MainActivity.kt": (
            "java-kotlin", "java-kotlin-mobile"
        ),
    }
    for path, (language, expected_slice) in cases.items():
        selected = [
            s["slice_id"] for s in manifest["slices"]
            if s["language"] == language and cs.in_slice(path, s, manifest["paths_ignore"])
        ]
        assert selected == [expected_slice], path


@needs_git
def test_legacy_baseline_slices_preserve_scopes_and_have_replacement_coverage():
    manifest = cs.load_manifest()
    files = [f for f in cs.tracked_files() if f.endswith(".py")]
    legacy = {
        "python-core": (
            ["src", "tests", "recycling", "claims"],
            {"python-core-src", "python-core-tests"},
        ),
        "python-product20": (
            ["12-AZ-IP/20-psicat-navigator", "TOOLS/checks"],
            {"python-runtime-integration", "python-psicat-tests-tools"},
        ),
        "python-psicat-runtime": (
            [
                "12-AZ-IP/20-psicat-navigator/ox_navigator/app",
                "12-AZ-IP/20-psicat-navigator/ox_navigator/engine",
            ],
            {"python-runtime-integration"},
        ),
    }
    slices = {s["slice_id"]: s for s in manifest["slices"]}
    ignore = manifest["paths_ignore"]
    for slice_id, (historical_paths, replacement_ids) in legacy.items():
        assert slices[slice_id]["paths"] == historical_paths
        former_scope = {
            f for f in files
            if any(cs.matches(f, path) for path in historical_paths)
            and not any(cs.matches(f, path) for path in ignore)
        }
        replacement_scope = {
            f for f in files
            if any(
                cs.in_slice(f, slices[replacement_id], ignore)
                for replacement_id in replacement_ids
            )
        }
        assert former_scope, f"{slice_id} must remain a real analysis"
        assert former_scope <= replacement_scope, f"{slice_id} has uncovered former paths"


def test_plan_cli_writes_actions_outputs(tmp_path):
    changed = tmp_path / "changed.txt"
    changed.write_text("12-AZ-IP/03-eige/eige/county.py\n")
    out = tmp_path / "gh_output"
    scope = tmp_path / "scope.json"
    assert cs.main(["plan", "--changed-from", str(changed), "--github-output", str(out),
                    "--manifest-out", str(scope)]) == 0
    lines = dict(line.split("=", 1) for line in out.read_text().splitlines())
    assert lines["has_work"] == "true"
    include = json.loads(lines["matrix"])["include"]
    assert [i["slice_id"] for i in include] == ["python-eige"]
    config = yaml.safe_load(include[0]["config"])
    assert config["paths"] == ["12-AZ-IP/03-eige", "12-AZ-IP/EIGE"] and "**/*.md" in config["paths-ignore"]
    assert json.loads(scope.read_text())["selected_slice_ids"] == ["python-eige"]


def test_workflow_uses_the_manifest_and_enforces_coverage():
    wf = yaml.safe_load((REPO_ROOT / cs.WORKFLOW).read_text(encoding="utf-8"))
    steps = wf["jobs"]["plan-matrix"]["steps"]
    runs = "\n".join(s.get("run", "") for s in steps)
    assert "codeql_slices.py check" in runs and "codeql_slices.py plan" in runs
    init = next(s for s in wf["jobs"]["analyze"]["steps"] if "codeql-action/init" in s.get("uses", ""))
    assert init["with"]["config"] == "${{ matrix.config }}"
    assert init["with"]["queries"] == "security-extended"


def test_workflow_plans_every_category_for_complete_baseline_comparison(tmp_path):
    wf = yaml.safe_load((REPO_ROOT / cs.WORKFLOW).read_text(encoding="utf-8"))
    step = next(s for s in wf["jobs"]["plan-matrix"]["steps"] if s.get("id") == "plan")
    assert "--changed-from" not in step["run"]
    output = tmp_path / "github-output"
    script = step["run"].replace(
        "TOOLS/checks/codeql_slices.py",
        shlex.quote(str(REPO_ROOT / "TOOLS/checks/codeql_slices.py")),
    )
    completed = subprocess.run(
        ["bash", "-c", script], cwd=tmp_path,
        env={**os.environ, "GITHUB_OUTPUT": str(output)},
        capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    values = dict(line.split("=", 1) for line in output.read_text().splitlines())
    actual = json.loads(values["matrix"])["include"]
    expected = cs.load_manifest()["slices"]
    assert [s["slice_id"] for s in actual] == [s["slice_id"] for s in expected]
    assert values["has_work"] == "true"


@needs_git
def test_check_command_passes_on_this_repository():
    done = subprocess.run(["python3", str(REPO_ROOT / "TOOLS/checks/codeql_slices.py"), "check"],
                          cwd=REPO_ROOT, capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "0 in no slice" in done.stdout
