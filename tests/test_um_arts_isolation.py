# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Source isolation does not turn mutating checks into certificates."""

import json
import subprocess
from pathlib import Path

import pytest
from TOOLS.um_arts.evidence import EvidenceError, fingerprints
from TOOLS.um_arts.isolation import snapshot


@pytest.mark.parametrize("artifact_directory", [".um-arts-completion", ".lean-library-check"])
def test_provisioning_artifacts_are_excluded_but_ordinary_inputs_remain_tracked(tmp_path, artifact_directory):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "source.py").write_text("VALUE = 1\n")
    original = fingerprints(root, tmp_path / "store", {})
    tools = root / artifact_directory / "lean" / "include"
    tools.mkdir(parents=True)
    (tools / "generated.py").write_text("GENERATED = 1\n")
    (tools / "alias").symlink_to(tmp_path / "external-tool-input")
    changed = fingerprints(root, tmp_path / "store", {})
    assert changed["compatibility"]["source"] == original["compatibility"]["source"]
    assert artifact_directory in changed["source_policy"]["excluded_directories"]
    copied = Path(snapshot(root, tmp_path / "snapshot")["snapshot_root"])
    assert not (copied / artifact_directory).exists()
    inputs = root / ".um-arts-real-inputs"
    inputs.mkdir()
    (inputs / "data.json").write_text('{"input": true}')
    actual = fingerprints(root, tmp_path / "store", {})
    assert ".um-arts-real-inputs/data.json" in actual["source_files"]
    assert actual["compatibility"]["source"] != original["compatibility"]["source"]


@pytest.mark.parametrize("artifact_directory", [".um-arts-completion", ".lean-library-check"])
def test_git_does_not_enumerate_provisioning_artifacts(tmp_path, artifact_directory):
    root = tmp_path / "repo"
    root.mkdir()
    ignore = Path(__file__).resolve().parents[1] / ".gitignore"
    (root / ".gitignore").write_bytes(ignore.read_bytes())
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    tools = root / artifact_directory / "lean"
    tools.mkdir(parents=True)
    for index in range(100):
        (tools / f"generated-{index}.h").write_text("tool input")
    (root / "source.py").write_text("VALUE = 1\n")
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard", "-z", "--"],
        check=True, capture_output=True,
    )
    assert set(result.stdout.split(b"\0")) == {b".gitignore", b"source.py", b""}


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


def test_empty_source_directories_affect_fingerprints_and_survive_snapshot(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    empty = root / "required" / "empty"
    empty.mkdir(parents=True)
    original = fingerprints(root, tmp_path / "store", {})
    assert original["source_directories"] == ["required", "required/empty"]
    copied = Path(snapshot(root, tmp_path / "snapshot")["snapshot_root"])
    assert (copied / "required" / "empty").is_dir()
    empty.rmdir()
    changed = fingerprints(root, tmp_path / "store", {})
    assert changed["compatibility"]["source"] != original["compatibility"]["source"]


def test_snapshot_never_copies_worktree_git_pointer_files(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    external = tmp_path / "original-git-metadata"
    external.mkdir()
    pointer = root / ".git"
    pointer.write_text(f"gitdir: {external}\n")
    (root / "source.py").write_text("VALUE = 1\n")
    original = fingerprints(root, tmp_path / "store", {})
    assert ".git" not in original["source_files"]
    copied = Path(snapshot(root, tmp_path / "snapshot")["snapshot_root"])
    assert not (copied / ".git").exists()
    assert pointer.read_text() == f"gitdir: {external}\n"


@pytest.mark.parametrize("runtime_directory", [".benchmarks", ".hypothesis"])
def test_pytest_runtime_caches_are_disclosed_but_not_source_input(tmp_path, runtime_directory):
    root = tmp_path / "repo"
    root.mkdir()
    original = fingerprints(root, tmp_path / "store", {})
    cache = root / runtime_directory / "generated"
    cache.mkdir(parents=True)
    (cache / "state.json").write_text('{"runtime": true}')
    changed = fingerprints(root, tmp_path / "store", {})
    assert changed["compatibility"] == original["compatibility"]
    assert runtime_directory in changed["source_policy"]["excluded_directories"]
    assert not any(path.startswith(runtime_directory + "/") for path in changed["source_files"])
