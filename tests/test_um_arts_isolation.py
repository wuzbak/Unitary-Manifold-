# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Source isolation does not turn mutating checks into certificates."""

import json
from pathlib import Path

import pytest
from TOOLS.um_arts.evidence import EvidenceError
from TOOLS.um_arts.isolation import snapshot


def test_snapshot_preserves_inputs_and_redirects_absolute_internal_aliases(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "inputs").mkdir()
    (root / "inputs" / "test.py").write_text("value = 1\n")
    (root / "alias").symlink_to(root / "inputs", target_is_directory=True)
    (root / ".git").mkdir()
    (root / ".git" / "metadata").write_text("excluded")
    result = snapshot(root, tmp_path / "isolated")
    copied = Path(result["snapshot_root"])
    assert (copied / "alias").resolve() == copied / "inputs"
    assert not (copied / ".git").exists()
    (copied / "alias" / "test.py").write_text("changed")
    assert (root / "inputs" / "test.py").read_text() == "value = 1\n"
    manifest = json.loads((tmp_path / "isolated" / "snapshot.json").read_text())
    assert manifest["test_gate"] is False
    assert manifest["status"] == "snapshot_ready"


@pytest.mark.parametrize("location", ["existing", "inside", "ancestor", "symlink"])
def test_snapshot_rejects_unsafe_destinations(tmp_path, location):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "input").write_text("data")
    if location == "existing":
        output = tmp_path / "existing"
        output.mkdir()
    elif location == "inside":
        output = root / "snapshot"
    elif location == "ancestor":
        output = tmp_path
    else:
        link = tmp_path / "link"
        link.symlink_to(tmp_path, target_is_directory=True)
        output = link / "snapshot"
    with pytest.raises(EvidenceError):
        snapshot(root, output)
    assert (root / "input").read_text() == "data"


def test_snapshot_rejects_external_source_links_without_copying(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "external").symlink_to(tmp_path / "not_present")
    with pytest.raises(EvidenceError):
        snapshot(root, tmp_path / "snapshot")
    assert not (tmp_path / "snapshot").exists()


def test_snapshot_preserves_empty_internal_directory_alias(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "empty").mkdir()
    (root / "alias").symlink_to("empty", target_is_directory=True)
    copied = Path(snapshot(root, tmp_path / "snapshot")["snapshot_root"])
    assert (copied / "alias").is_dir()
    assert (copied / "alias").resolve() == copied / "empty"
