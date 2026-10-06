# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Dependency pins, hash lock, SBOM and test vectors stay in sync."""

from __future__ import annotations

import json
import pathlib
import re
import sys

import pytest

PRODUCT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PRODUCT / "tools"))

import make_sbom  # noqa: E402
import make_test_vectors  # noqa: E402

_PIN = re.compile(r"^([A-Za-z0-9_.-]+)==(\S+)$")


def _pins(path: pathlib.Path) -> dict:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _PIN.match(line.strip())
        if m:
            out[m.group(1).lower()] = m.group(2)
    return out


def test_requirements_txt_matches_lock():
    lock = {k: v["version"] for k, v in make_sbom.parse_lock((PRODUCT / "requirements.lock").read_text(encoding="utf-8")).items()}
    assert _pins(PRODUCT / "requirements.txt") == lock


def test_every_lock_entry_is_hashed():
    lock = make_sbom.parse_lock((PRODUCT / "requirements.lock").read_text(encoding="utf-8"))
    assert lock
    for name, info in lock.items():
        assert info["hashes"], f"{name} has no hashes"


def test_direct_dependencies_are_declared():
    pins = _pins(PRODUCT / "requirements.txt")
    for name in ("cryptography", "flask", "hypothesis", "pytest", "mpmath"):
        assert name in pins
    direct = _pins(PRODUCT / "requirements.in")
    assert set(direct) <= set(pins)


def test_sbom_is_current():
    expected = make_sbom.render((PRODUCT / "requirements.lock").read_text(encoding="utf-8"))
    assert (PRODUCT / "sbom.cdx.json").read_text(encoding="utf-8") == expected
    doc = json.loads(expected)
    assert doc["bomFormat"] == "CycloneDX"
    assert {c["name"] for c in doc["components"]} >= {"cryptography", "flask"}


@pytest.mark.slow
def test_test_vectors_are_current():
    assert make_test_vectors.main(["--check"]) == 0


def test_published_vectors_verify():
    from eige.crypto import merkle
    from eige.verify import verify_bundle

    vec = json.loads((PRODUCT / "test_vectors" / "merkle.json").read_text(encoding="utf-8"))
    assert vec["roots"]["8"] == "5dc9da79a70659a9ad559cb701ded9a2ab9d823aad2f4960cfe370eff4604328"
    for case in vec["inclusion"]:
        assert merkle.verify_inclusion(
            bytes.fromhex(case["leaf_hash"]), case["leaf_index"], case["tree_size"],
            [bytes.fromhex(p) for p in case["proof"]], bytes.fromhex(case["root"]),
        )
    report = verify_bundle(str(PRODUCT / "test_vectors" / "bundle"))
    assert report.passed
