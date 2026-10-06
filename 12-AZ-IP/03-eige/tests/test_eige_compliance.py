# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Every claimed control and every threat-model mitigation must point at real tests."""

from __future__ import annotations

import ast
import json
import pathlib
import re

import pytest

from eige.compliance import CONTROL_MAPPINGS, STATUSES, ControlMapping, oscal_component_definition

PRODUCT = pathlib.Path(__file__).resolve().parent.parent
_REF = re.compile(r"(tests/test_[A-Za-z0-9_]+\.py)::([A-Za-z0-9_]+)")


def _defined_names(path: pathlib.Path) -> set:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def _assert_ref_exists(ref: str) -> None:
    m = _REF.fullmatch(ref)
    assert m, f"malformed test reference {ref!r}"
    path = PRODUCT / m.group(1)
    assert path.is_file(), f"{ref}: file missing"
    name = m.group(2)
    assert name.startswith(("test_", "Test")), f"{ref}: not a test"
    assert name in _defined_names(path), f"{ref}: test not found"


@pytest.mark.parametrize("mapping", CONTROL_MAPPINGS, ids=lambda m: f"{m.framework}:{m.control_id}")
def test_control_mapping_tests_exist(mapping):
    assert mapping.status in STATUSES
    for ref in mapping.tests:
        _assert_ref_exists(ref)


def test_threat_model_test_references_exist():
    text = (PRODUCT / "THREAT_MODEL.md").read_text(encoding="utf-8")
    refs = [m.group(0) for m in _REF.finditer(text)]
    assert len(refs) >= 20
    for ref in refs:
        _assert_ref_exists(ref)


def test_mitigated_threats_name_tests():
    text = (PRODUCT / "THREAT_MODEL.md").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("| ") and "| Mitigated" in line:
            assert _REF.search(line), f"mitigated threat without tests: {line[:80]}"


def test_claimed_controls_require_tests_and_planned_claim_none():
    with pytest.raises(ValueError):
        ControlMapping("x", "AU-2", "t", "implemented", ("m",), "s")
    with pytest.raises(ValueError):
        ControlMapping("x", "AU-2", "t", "planned", (), "s", ("tests/test_x.py::test_y",))
    with pytest.raises(ValueError):
        ControlMapping("x", "AU-2", "t", "compliant", (), "s")


def test_compliance_md_states_the_same_status():
    text = (PRODUCT / "COMPLIANCE.md").read_text(encoding="utf-8")
    for m in CONTROL_MAPPINGS:
        if m.framework != "NIST SP 800-53r5":
            continue
        row = re.search(rf"^\| {re.escape(m.control_id)} [^|]*\|\s*([a-z-]+)\s*\|", text, re.M)
        assert row, f"{m.control_id} missing from COMPLIANCE.md"
        assert row.group(1) == m.status, f"{m.control_id}: COMPLIANCE.md says {row.group(1)}, code says {m.status}"


def test_oscal_output_reflects_mapping_status():
    doc = oscal_component_definition()
    reqs = doc["component-definition"]["components"][0]["control-implementations"][0]["implemented-requirements"]
    statuses = {r["control-id"]: [p["value"] for p in r["props"] if p["name"] == "implementation-status"][0] for r in reqs}
    assert statuses["au-2"] == "implemented"
    assert statuses["si-7.6"] == "planned"
    assert set(statuses.values()) <= set(STATUSES)
    assert json.dumps(doc) == json.dumps(oscal_component_definition())  # deterministic
    assert "zero-knowledge" not in json.dumps(doc).lower()
