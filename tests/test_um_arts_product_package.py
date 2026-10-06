# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Canonical product packaging and historical import compatibility."""

import importlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from tests.test_um_arts import arts_workspace as _arts_workspace

arts_workspace = _arts_workspace
ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "12-AZ-IP" / "26-um-arts"


def test_legacy_namespace_points_to_canonical_product():
    legacy = importlib.import_module("TOOLS.um_arts")
    canonical = importlib.import_module("um_arts")
    assert legacy.VERSION == canonical.VERSION
    assert list(legacy.__path__) == list(canonical.__path__)
    for module in ["engine", "capture", "evidence", "pytest_plugin", "__main__"]:
        old = importlib.import_module(f"TOOLS.um_arts.{module}")
        new = importlib.import_module(f"um_arts.{module}")
        assert Path(old.__file__) == Path(new.__file__)
        assert Path(new.__file__).is_relative_to(PRODUCT / "um_arts")


@pytest.mark.parametrize("command,cwd", [
    ([sys.executable, "-m", "TOOLS.um_arts", "--help"], ROOT),
    ([sys.executable, "-m", "um_arts", "--help"], PRODUCT),
    ([sys.executable, str(PRODUCT / "run.py"), "--help"], ROOT),
])
def test_product_and_legacy_cli(command, cwd):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
                            timeout=30, check=False)
    assert result.returncode == 0, result.stderr
    assert "capture" in result.stdout and "plan" in result.stdout


@pytest.mark.parametrize("name,path", [
    ("um_arts.pytest_plugin", PRODUCT),
    ("TOOLS.um_arts.pytest_plugin", ROOT),
])
def test_explicit_canonical_and_legacy_plugin(name, path, arts_workspace):
    root = arts_workspace / "repository"
    root.mkdir()
    (root / "pytest.ini").write_text("[pytest]\n")
    (root / "test_sample.py").write_text("def test_ok(): assert True\n")
    report = arts_workspace / "receipt.json"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(path)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["UM_ARTS_PYTEST_REPORT"] = str(report)
    for key in ["PYTEST_ADDOPTS", "PYTEST_PLUGINS", "UM_ARTS_RECEIPT", "UM_ARTS_SELECTION"]:
        env.pop(key, None)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", name, "-q", "-c", str(root / "pytest.ini"),
         "--rootdir", str(root), "--confcutdir", str(root),
         "--basetemp", str(arts_workspace / "scratch")],
        cwd=root, env=env, text=True, capture_output=True, timeout=30, check=False)
    assert result.returncode == 0, result.stderr
    receipt = json.loads(report.read_text())
    assert receipt["selected"] == ["test_sample.py::test_ok"]
    assert receipt["exitstatus"] == 0


def test_fingerprints_capture_canonical_engine(arts_workspace):
    from TOOLS.um_arts.evidence import file_hash, fingerprints

    root = arts_workspace / "repository"
    root.mkdir()
    (root / "source.py").write_text("VALUE = 1\n")
    result = fingerprints(root, arts_workspace / "store", {})
    assert result["engine"]["engine.py"] == file_hash(PRODUCT / "um_arts" / "engine.py")
    assert result["engine"]["__init__.py"] == file_hash(PRODUCT / "um_arts" / "__init__.py")


def test_package_metadata_and_registry():
    from TOOLS.um_arts.evidence import file_hash

    metadata = tomllib.loads((PRODUCT / "pyproject.toml").read_text())
    assert metadata["project"]["dependencies"] == []
    assert metadata["project"]["scripts"]["um-arts"] == "um_arts.__main__:main"
    assert "pytest11" not in metadata["project"].get("entry-points", {})
    registry = json.loads((ROOT / "12-AZ-IP" / "IP_REGISTRY.json").read_text())
    product = next(item for item in registry["products"] if item["name"] == "UM-ARTS")
    assert product["link"] == "26-um-arts/"
    assert product["trl"] == "Not assessed"
    for relative in ["12-AZ-IP/26-um-arts/run.py", "12-AZ-IP/26-um-arts/pyproject.toml"]:
        asset = registry["assets"][relative]
        assert asset["sha256"] == file_hash(ROOT / relative)
        assert asset["size_bytes"] == (ROOT / relative).stat().st_size


def test_serve_cli_dispatches_product_backend(monkeypatch):
    from um_arts import __main__ as cli
    from um_arts import server

    received = []
    monkeypatch.setattr(server, "serve", lambda *args: received.append(args))
    assert cli.main(["serve", "--root", str(ROOT), "--store", str(ROOT / ".um-arts"),
                     "--config", "adapter.json", "--adapter", "generic",
                     "--mode", "changed", "--host", "127.0.0.1", "--port", "8766"]) == 0
    assert received == [(ROOT, ROOT / ".um-arts", Path("adapter.json"),
                         "generic", "changed", "127.0.0.1", 8766)]


def test_serve_cli_loopback_defaults():
    from um_arts.__main__ import parser

    args = parser().parse_args(["serve"])
    assert args.host == "127.0.0.1"
    assert args.port == 8765
    assert args.store == Path(".um-arts")


def test_inventory_cli_generates_reviewable_config(arts_workspace, capsys):
    from um_arts.__main__ import main

    root = arts_workspace / "repository"
    (root / "tests").mkdir(parents=True)
    (root / "tests" / "test_ok.py").write_text("def test_ok(): assert True\n")
    output = arts_workspace / "inventory.json"
    config = arts_workspace / "config.json"
    assert main(["inventory", "--root", str(root), "--output", str(output),
                 "--config-output", str(config)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "review-required"
    assert result["selection_boundary"]["collection_verified"] is False
    assert json.loads(output.read_text()) == result
    assert json.loads(config.read_text())["pytest_args"] == ["-m", ""]
    assert main(["inventory", "--root", str(root), "--output", str(output)]) == 2


def test_assist_cli_is_cited_and_cannot_promote_report(arts_workspace, capsys):
    from um_arts.__main__ import main

    root = arts_workspace / "repository"
    root.mkdir()
    (root / "README.md").write_text("Collection evidence scope requires exact identities.\n")
    output = arts_workspace / "context.json"
    assert main(["assist", "--root", str(root), "--query", "collection evidence",
                 "--paths", "README.md", "--output", str(output)]) == 0
    context = json.loads(capsys.readouterr().out)
    assert context["citations"][0]["path"] == "README.md"
    assert context["proof_claim"] is False
    input_report = arts_workspace / "report.json"
    input_report.write_text('{"status":"blocked","errors":["missing receipt"]}')
    assert main(["assist", "--root", str(root), "--report", str(input_report),
                 "--paths", "README.md"]) == 0
    packet = json.loads(capsys.readouterr().out)
    assert packet["report_status"] == "blocked"
    assert packet["gate_changes"] == []
    assert packet["proof_claim"] is False
    assert main(["assist", "--root", str(root), "--attempt", str(arts_workspace / "attempt"),
                 "--output", str(arts_workspace / "attempt" / "diagnostic.json")]) == 2


def test_snapshot_cli_dispatch_and_success_status(monkeypatch, capsys):
    from um_arts import __main__ as cli
    from um_arts import isolation

    received = []

    def snapshot(root, output):
        received.append((root, output))
        return {"status": "snapshot_ready", "source_root": str(root), "snapshot_root": str(output)}

    monkeypatch.setattr(isolation, "snapshot", snapshot)
    assert cli.main(["snapshot", "--root", str(ROOT), "--output", "copy"]) == 0
    assert received == [(ROOT, Path("copy"))]
    assert json.loads(capsys.readouterr().out)["status"] == "snapshot_ready"


@pytest.mark.parametrize("status,code", [("passed", 0), ("blocked", 2)])
def test_certify_cli_dispatch_and_gate_status(monkeypatch, capsys, status, code):
    from um_arts import __main__ as cli
    from um_arts import certification

    received = []

    def certify(manifest):
        received.append(manifest)
        return {"status": status, "coverage_scope": "explicit manifest only"}

    monkeypatch.setattr(certification, "certify", certify)
    assert cli.main(["certify", "--manifest", "required-checks.json"]) == code
    assert received == [Path("required-checks.json")]
    assert json.loads(capsys.readouterr().out)["status"] == status
