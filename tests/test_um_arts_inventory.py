# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Canonical discovery boundaries and adapter-backed repository planning."""

import json
import shutil
import uuid
from pathlib import Path

import pytest
from TOOLS.um_arts.adapters import load_config
from TOOLS.um_arts.engine import plan
from TOOLS.um_arts.evidence import EvidenceError
from TOOLS.um_arts.inventory import (
    discover_inventory,
    execution_config,
    selection_boundary,
)


@pytest.fixture
def inventory_work():
    directory = Path.cwd() / ".um-arts-inventory-work" / uuid.uuid4().hex
    directory.mkdir(parents=True)
    yield directory
    for path in directory.rglob("*"):
        if not path.is_symlink():
            path.chmod(0o755 if path.is_dir() else 0o644)
    shutil.rmtree(directory)


def put(root, relative, text="def test_ok():\n    assert True\n"):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_inventory_whole_repository_and_explicit_boundaries():
    root = Path(__file__).resolve().parents[1]
    inventory = discover_inventory(root)
    roots = {suite["root"] for suite in inventory["suites"]}
    assert {"tests", "recycling", "5-GOVERNANCE/Unitary Pentad", "proof",
            "COMPACTIFICATION", "12-AZ-IP/20-psicat-navigator/tests",
            "12-AZ-IP/10-filmers-companion/desktop/tests",
            "claims/anomaly_inflow"} <= roots
    identities = [path for suite in inventory["suites"] for path in suite["paths"]]
    assert len(identities) == len(set(identities))
    assert not any("/holon-zero/" in path for path in identities)
    assert "ALGEBRA_PROOF.py" not in identities
    assert "proof/ALGEBRA_PROOF.py" in identities
    assert not any("/07-holon-zero/" in path and path.endswith("test_holon_zero_engine.py")
                   for path in identities)
    assert not any(path.startswith("12-AZ-IP/06-omega-synthesis/")
                   and path.endswith("test_omega_synthesis.py") for path in identities)
    assert not any(path.startswith("12-AZ-IP/05-uos-kernel/")
                   and path.endswith("test_uos_security.py") for path in identities)
    assert any(item["path"] == "src/core/dirty_data_test.py" for item in inventory["uncovered"])
    assert inventory["status"] == "review-required"
    assert inventory["adapter"] == "um"
    assert {check["path"] for check in inventory["declared_checks"]} == {
        "proof/ALGEBRA_PROOF.py", "proof/VERIFY.py"}
    assert all(check["kind"] == "command" and check["status"] == "declared-not-executed"
               for check in inventory["declared_checks"])
    assert inventory["lean_projects"] == [
        {"project": "lean4", "scope": "unselected", "status": "not-built"}]
    assert "src/core/regression_supervision_plan.py" in inventory["collection_policy"]["sources"]
    assert any("not a certification" in boundary for boundary in inventory["boundaries"])


def test_unknown_and_disabled_candidates_are_not_silently_certified(inventory_work):
    put(inventory_work, "tests/test_known.py")
    put(inventory_work, "surprise/test_unknown.py")
    put(inventory_work, "src/core/manual_test.py")
    put(inventory_work, "proof/VERIFY.py", "print('not a pytest test')\n")
    inventory = discover_inventory(inventory_work)
    assert inventory["unclassified"] == [
        {"path": "surprise/test_unknown.py", "reason": "no canonical suite policy"}]
    assert {item["path"] for item in inventory["uncovered"]} == {
        "src/core/manual_test.py", "proof/VERIFY.py"}
    assert inventory["declared_checks"][0]["command"] == ["python", "proof/VERIFY.py"]
    assert [suite["paths"] for suite in inventory["suites"]] == [["tests/test_known.py"]]


@pytest.mark.parametrize("directory", [
    ".github/agents", "archive", "ARCHIVES", "vendor", "node_modules", ".lake",
    ".um-arts-private-store", "12-AZ-IP/example/archived", "docs/archived_hypotheses",
])
def test_excluded_subtrees_are_never_read(inventory_work, directory, monkeypatch):
    put(inventory_work, "tests/test_good.py")
    blocked = put(inventory_work, f"{directory}/test_bad.py")
    put(inventory_work, f"{directory}/conftest.py", "raise AssertionError('must not import')\n")
    original = Path.read_text

    def guarded_read(path, *args, **kwargs):
        assert not path.is_relative_to(blocked.parent)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded_read)
    inventory = discover_inventory(inventory_work)
    assert inventory["candidates"] == ["tests/test_good.py"]
    assert any(item["reason"] == "excluded_directory" for item in inventory["excluded"])


def test_symlinks_are_not_followed(inventory_work):
    put(inventory_work, "tests/test_good.py")
    (inventory_work / "tests/test_link.py").symlink_to("test_good.py")
    (inventory_work / "mirror").symlink_to("tests", target_is_directory=True)
    inventory = discover_inventory(inventory_work)
    assert inventory["candidates"] == ["tests/test_good.py"]
    assert len(inventory["excluded"]) == 2


def test_literal_collection_policy_without_conftest_execution(inventory_work):
    put(inventory_work, "pytest.ini", "[pytest]\npython_files = test_*.py ALGEBRA_PROOF.py\n")
    put(inventory_work, "conftest.py",
        "raise AssertionError('not executed')\ncollect_ignore_glob = ['tests/test_mirror*.py']\n")
    put(inventory_work, "tests/test_ok.py")
    put(inventory_work, "tests/test_mirror.py")
    put(inventory_work, "proof/ALGEBRA_PROOF.py")
    put(inventory_work, "ALGEBRA_PROOF.py")
    put(inventory_work, "claims/a/conftest.py", "collect_ignore = ['test_ignore.py']\n")
    put(inventory_work, "claims/a/test_ignore.py")
    inventory = discover_inventory(inventory_work)
    paths = [path for suite in inventory["suites"] for path in suite["paths"]]
    assert paths == ["proof/ALGEBRA_PROOF.py", "tests/test_ok.py"]
    assert len(inventory["excluded"]) == 3


def test_mirror_exclusion_requires_content_equality(inventory_work):
    canonical = "5-GOVERNANCE/Unitary Pentad/holon_zero/test_holon_zero_engine.py"
    mirror = "12-AZ-IP/07-holon-zero/tests/test_holon_zero_engine.py"
    put(inventory_work, canonical)
    put(inventory_work, mirror)
    assert any(item.get("canonical") == canonical
               for item in discover_inventory(inventory_work)["excluded"])
    put(inventory_work, mirror, "def test_different():\n    assert True\n")
    inventory = discover_inventory(inventory_work)
    assert mirror in [path for suite in inventory["suites"] for path in suite["paths"]]


def test_deterministic_config_selection_and_lean_scope(inventory_work):
    put(inventory_work, "tests/test_ok.py")
    put(inventory_work, "claims/example/test_claim.py")
    put(inventory_work, "lean4/lakefile.lean", "-- project\n")
    inventory = discover_inventory(inventory_work)
    assert inventory == discover_inventory(inventory_work)
    config = execution_config(inventory, lean_project="lean4")
    assert config["pytest_args"] == ["-m", ""]
    assert config["lean"] == {"project": "lean4", "scope": "full", "targets": []}
    path = put(inventory_work, "config.json", json.dumps(config))
    assert load_config(inventory_work, path)["pytest_args"] == ["-m", ""]
    selected = [inventory["suites"][0]["name"]]
    boundary = selection_boundary(inventory, selected)
    assert len(boundary["unselected"]) == 1
    assert boundary["lean_unselected"] == ["lean4"]
    assert boundary["collection_verified"] is boundary["proof_claim"] is False
    for invalid in [[], ["unknown"], selected * 2]:
        with pytest.raises(EvidenceError):
            execution_config(inventory, invalid)
    with pytest.raises(EvidenceError):
        execution_config(inventory, lean_project="outside")


def test_repository_example_covers_current_canonical_suites_without_mirrors():
    root = Path(__file__).resolve().parents[1]
    inventory = discover_inventory(root)
    config = load_config(root, root / "12-AZ-IP/26-um-arts/um_arts/examples/repository.json")
    assert config["adapter"] == "um"
    assert config["pytest_args"] == ["-m", ""]
    by_name = {suite["name"]: suite for suite in config["suites"]}
    assert set(by_name) == {suite["name"] for suite in inventory["suites"]}
    for suite in inventory["suites"]:
        configured = by_name[suite["name"]]["paths"]
        assert all(any(path == selected or path.startswith(selected + "/") for selected in configured)
                   for path in suite["paths"])
    for item in inventory["excluded"]:
        if item["reason"] == "exact product mirror":
            assert not any(
                item["path"] == path or item["path"].startswith(path + "/")
                for suite in config["suites"] for path in suite["paths"])


def test_engine_collection_includes_slow_with_reviewed_inventory_config(inventory_work):
    root = inventory_work / "repository"
    put(root, "pytest.ini", '[pytest]\naddopts = -m "not slow"\nmarkers = slow: slow\n')
    put(root, "tests/test_example.py",
        "import pytest\ndef test_fast(): pass\n@pytest.mark.slow\ndef test_slow(): pass\n")
    put(root, "12-AZ-IP/42-example/tests/test_product.py")
    put(root, "claims/example/test_claim.py")
    inventory = discover_inventory(root)
    config = execution_config(inventory)
    config_path = put(root, "reviewed.json", json.dumps(config))
    result = plan(root, inventory_work / "artifacts", config_path, adapter="generic")
    assert result["status"] == "ready", result["errors"]
    assert result["selected"] == 4
    spec = json.loads(Path(result["plan_path"]).read_text())
    assert all(not suite["deselected"] for suite in spec["suites"])
    assert spec["config"]["pytest_args"] == ["-m", ""]
