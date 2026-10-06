# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for synthetic bundle verification and verifier CLI exit codes."""

from pathlib import Path

import pytest

from eige.crypto import merkle
from eige.pipeline import build_synthetic_bundle
from eige.verify import main, verify_bundle

@pytest.fixture
def workdir(tmp_path):
    return tmp_path / "bundle"


def test_build_synthetic_bundle_verifies_with_zero_failed_checks(workdir):
    build_synthetic_bundle(workdir)
    report = verify_bundle(str(workdir))
    assert report.passed
    assert report.counts()["failed"] == 0
    assert report.counts()["verified"] >= 8


def test_cli_bundle_exit_codes_zero_one_and_two(workdir, capsys):
    build_synthetic_bundle(workdir)
    assert main(["bundle", str(workdir), "--audience", "json"]) == 0
    out = capsys.readouterr().out
    assert '"passed": true' in out

    (workdir / "heads.json").write_text("[]\n", encoding="utf-8")
    assert main(["bundle", str(workdir)]) == 1
    assert "FAILED" in capsys.readouterr().out

    assert main(["bundle", str(workdir / "missing")]) == 2
    assert "error:" in capsys.readouterr().err


def test_cli_inclusion_and_consistency_exit_codes(tmp_path, capsys):
    leaves = [b"one", b"two", b"three"]
    hashes = [merkle.leaf_hash(x) for x in leaves]
    leaf_file = tmp_path / "leaf.bin"
    leaf_file.write_bytes(leaves[1])
    root = merkle.root_from_leaf_hashes(hashes)
    proof = ",".join(x.hex() for x in merkle.inclusion_proof(hashes, 1))
    assert main(["inclusion", "--leaf-file", str(leaf_file), "--index", "1", "--tree-size", "3", "--root", root.hex(), "--proof", proof]) == 0
    assert "VERIFIED" in capsys.readouterr().out
    assert main(["inclusion", "--leaf-file", str(leaf_file), "--index", "0", "--tree-size", "3", "--root", root.hex(), "--proof", proof]) == 1
    assert "FAILED" in capsys.readouterr().out
    assert main(["inclusion", "--leaf-file", str(leaf_file), "--index", "0", "--tree-size", "3", "--root", "nothex"]) == 2

    old_root = merkle.root_from_leaf_hashes(hashes[:2])
    cproof = ",".join(x.hex() for x in merkle.consistency_proof(hashes, 2))
    assert main(["consistency", "--old-size", "2", "--old-root", old_root.hex(), "--new-size", "3", "--new-root", root.hex(), "--proof", cproof]) == 0
    assert "VERIFIED" in capsys.readouterr().out
