# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Trusted explicit plugins enable optional suites without autoload or xdist."""

import json
from pathlib import Path

import pytest
from TOOLS.um_arts.adapters import load_config
from TOOLS.um_arts.evidence import EvidenceError

from TOOLS.um_arts import engine


@pytest.mark.parametrize("plugins", [
    ["xdist.plugin"], ["um_arts.pytest_plugin"], ["TOOLS.um_arts.pytest_plugin"],
    ["other", "other"], ["../unsafe"], [123], "pytest_asyncio.plugin",
])
def test_reserved_or_invalid_plugins_are_rejected(tmp_path, plugins):
    (tmp_path / "tests").mkdir()
    config = tmp_path / "config.json"
    config.write_text(json.dumps({
        "adapter": "generic", "suites": [{"name": "unit", "paths": ["tests"]}],
        "plugins": plugins}))
    with pytest.raises(EvidenceError, match="plugins"):
        load_config(tmp_path, config, "generic")


def test_explicit_plugin_is_required_and_loaded_for_execution(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "tests").mkdir()
    (root / "trusted_fixture_plugin.py").write_text(
        "import pytest\n@pytest.fixture\ndef external_fixture(): return 42\n")
    (root / "tests" / "test_example.py").write_text(
        "def test_plugin(external_fixture): assert external_fixture == 42\n")
    config = tmp_path / "config.json"
    settings = {"adapter": "generic", "suites": [{"name": "unit", "paths": ["tests"]}]}
    config.write_text(json.dumps(settings))
    planned = engine.plan(root, tmp_path / "store", config, adapter="generic")
    assert planned["status"] == "ready", planned
    assert engine.run(Path(planned["plan_path"]))["status"] == "blocked"
    settings["plugins"] = ["trusted_fixture_plugin"]
    config.write_text(json.dumps(settings))
    planned = engine.plan(root, tmp_path / "store", config, adapter="generic")
    result = engine.run(Path(planned["plan_path"]))
    assert result["status"] == "passed", result
    assert result["counts"] == {"passed": 1}
