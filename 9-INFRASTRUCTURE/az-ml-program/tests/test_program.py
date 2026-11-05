# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Offline contract checks for the ALL 21 planning inventory."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import fields
import json
from pathlib import Path
import subprocess
import sys

import pytest

from src.infrastructure.execution_spine import ExecutionSpineRecord
from src.infrastructure.ml_program import (
    CAPABILITY_NAMES,
    Capability,
    DEFAULT_MANIFEST,
    DEPENDENCY_SEMANTICS,
    ManifestError,
    REPO_ROOT,
    STAGES,
    load_manifest,
    main,
    validate_manifest,
)


@pytest.fixture
def payload():
    return json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))


def test_inventory_exact_identity_scope_and_reuse(payload):
    program = validate_manifest(payload)
    assert [c.id for c in program.capabilities] == list(range(1, 22))
    assert tuple(c.name for c in program.capabilities) == CAPABILITY_NAMES
    assert len({c.domain for c in program.capabilities}) == 5
    expected_stages = {
        1: "original", 2: "baseline", 3: "baseline", 7: "baseline", 8: "baseline",
        5: "original", 10: "baseline", 11: "baseline", 13: "baseline", 14: "original", 18: "baseline", 20: "baseline",
    }
    for capability in program.capabilities:
        assert capability.status == ("in_progress" if capability.id in expected_stages else "planned")
        assert capability.stage == expected_stages.get(capability.id, "inventory")
        assert not capability.completion_evidence
        assert capability.external_prerequisites
        assert capability.original_algorithm_goal
        assert capability.baseline_adapters
        assert all((REPO_ROOT / p).is_file() for p in capability.source_references)
    tokenizer = program.capabilities[9]
    assert "impossible" in tokenizer.nonclaim
    assert "supported" in " ".join(tokenizer.acceptance_gates)


def test_temporal_foundations_are_partial_and_have_concrete_next_steps(payload):
    program = validate_manifest(payload)
    for identifier in (11, 14):
        capability = program.capabilities[identifier - 1]
        assert "src/infrastructure/temporal_data.py" in capability.source_references
        assert "9-INFRASTRUCTURE/az-ml-program/tests/test_temporal_data.py" in capability.source_references
        assert "partial baseline foundation only" in capability.nonclaim
        assert not capability.completion_evidence
    assert "Product 40" in program.capabilities[10].next_action
    assert "predictive consumer" in program.capabilities[10].next_action
    assert "DVC interchange" in program.capabilities[13].next_action


def test_integration_dag_preserves_program_dependencies(payload):
    program = validate_manifest(payload)
    assert program.dependency_semantics == DEPENDENCY_SEMANTICS
    expected = {
        1: (10, 18, 20), 2: (9, 18), 3: (2, 18), 4: (18,), 5: (14,),
        6: (9, 14), 7: (14,), 8: (7, 9), 9: (), 10: (), 11: (14,),
        12: (9, 14), 13: (11,), 14: (), 15: (9,), 16: (9,), 17: (9, 18),
        18: (), 19: (6, 9), 20: (10,), 21: (7, 14),
    }
    assert {c.id: c.dependencies for c in program.capabilities} == expected
    assert {c.id for c in program.capabilities if not c.dependencies} == {9, 10, 14, 18}


@pytest.mark.parametrize("key", [
    "schema_version", "scope", "dependency_semantics", "nonclaims", "foundation_commands", "capabilities",
])
def test_missing_manifest_fields_rejected(payload, key):
    del payload[key]
    with pytest.raises(ManifestError):
        validate_manifest(payload)


@pytest.mark.parametrize("value", ["", " ", "Execution prerequisites", None, True, [], {}])
def test_dependency_semantics_must_match_known_contract(payload, value):
    payload["dependency_semantics"] = value
    with pytest.raises(ManifestError, match="dependency_semantics"):
        validate_manifest(payload)


@pytest.mark.parametrize("key", [field.name for field in fields(Capability)])
def test_missing_capability_fields_rejected(payload, key):
    del payload["capabilities"][0][key]
    with pytest.raises(ManifestError):
        validate_manifest(payload)


@pytest.mark.parametrize("value", [True, False, 1.0, "1", None, 0, 22, [], {}])
def test_invalid_id_types_and_range(payload, value):
    payload["capabilities"][0]["id"] = value
    with pytest.raises(ManifestError):
        validate_manifest(payload)


@pytest.mark.parametrize("operation", ["missing", "extra", "duplicate"])
def test_exact_21_once(payload, operation):
    if operation == "missing":
        payload["capabilities"].pop()
    elif operation == "extra":
        payload["capabilities"].append(deepcopy(payload["capabilities"][0]))
    else:
        payload["capabilities"][-1] = deepcopy(payload["capabilities"][0])
    with pytest.raises(ManifestError):
        validate_manifest(payload)


@pytest.mark.parametrize("deps", [[22], [True], ["2"], [1], [2, 2], None, {}, "2"])
def test_invalid_dependencies(payload, deps):
    payload["capabilities"][0]["dependencies"] = deps
    with pytest.raises(ManifestError):
        validate_manifest(payload)


@pytest.mark.parametrize("cycle", [[1, 2], [1, 2, 3, 4]])
def test_cycles_rejected(payload, cycle):
    for index, identifier in enumerate(cycle):
        payload["capabilities"][identifier - 1]["dependencies"] = [cycle[(index + 1) % len(cycle)]]
    with pytest.raises(ManifestError, match="cycle"):
        validate_manifest(payload)


@pytest.mark.parametrize(("key", "value"), [
    ("name", "Wrong ambition"),
    ("domain", "physics"),
    ("stage", "production"),
    ("stage", True),
    ("status", "integrated"),
    ("status", None),
    ("acceptance_gates", []),
    ("acceptance_gates", [""]),
    ("acceptance_gates", "passed"),
    ("acceptance_gates", [True]),
    ("next_action", ""),
    ("next_action", "   "),
    ("owner_role", []),
    ("hardware_requirements", []),
    ("baseline_adapters", []),
    ("original_algorithm_goal", None),
    ("nonclaim", ""),
    ("external_prerequisites", "cuda"),
    ("external_prerequisites", [1]),
    ("source_references", []),
    ("source_references", ["missing-source.py"]),
    ("source_references", ["../outside.py"]),
    ("source_references", ["/etc/passwd"]),
    ("source_references", ["src/./infrastructure/execution_spine.py"]),
    ("completion_evidence", "tests passed"),
])
def test_invalid_capability_fields(payload, key, value):
    payload["capabilities"][0][key] = value
    with pytest.raises(ManifestError):
        validate_manifest(payload)


@pytest.mark.parametrize("stage", STAGES)
def test_documented_stages_accepted(payload, stage):
    payload["capabilities"][0]["stage"] = stage
    assert validate_manifest(payload).capabilities[0].stage == stage


def test_completion_requires_validation_and_explicit_evidence(payload):
    capability = payload["capabilities"][6]
    capability["status"] = "completed"
    with pytest.raises(ManifestError, match="completed requires"):
        validate_manifest(payload)
    capability["stage"] = "validation"
    with pytest.raises(ManifestError, match="completed requires"):
        validate_manifest(payload)
    capability["completion_evidence"] = ["does-not-exist.json"]
    with pytest.raises(ManifestError, match="missing"):
        validate_manifest(payload)


def test_next_does_not_confuse_planned_with_completed(payload):
    program = validate_manifest(payload)
    work = program.next_work()
    candidates = {c["id"]: c for c in work["candidates"]}
    assert set(candidates) == {9, 10, 14, 18}
    assert len(work["blocked"]) == 17
    assert work["blocked"][-1] == {
        "id": 21, "unfinished_dependencies": [7, 14], "explicitly_blocked": False,
    }
    assert "integration/validation" in work["scope"]
    assert work["dependency_semantics"] == DEPENDENCY_SEMANTICS
    assert work["not_execution_ready"]
    for candidate in candidates.values():
        assert candidate["dependency_ready"]
        assert candidate["execution_ready"] is False
        assert candidate["external_prerequisites"]
    assert all(not c.completion_evidence for c in program.capabilities)


def test_next_uses_only_declared_completion_and_keeps_external_blockers(payload):
    for identifier in (7, 14):
        payload["capabilities"][identifier - 1].update(
            status="completed", stage="validation",
            completion_evidence=["src/infrastructure/execution_spine.py"],
        )
    work = validate_manifest(payload).next_work()
    candidates = {c["id"]: c for c in work["candidates"]}
    assert 7 not in candidates
    assert candidates[21]["dependency_ready"]
    assert candidates[21]["external_prerequisites"]
    assert candidates[21]["execution_ready"] is False


def test_explicit_blocking_not_inferred_from_external_backend(payload):
    payload["capabilities"][8]["status"] = "blocked"
    work = validate_manifest(payload).next_work()
    assert 9 not in {c["id"] for c in work["candidates"]}
    assert next(c for c in work["blocked"] if c["id"] == 9) == {
        "id": 9, "unfinished_dependencies": [], "explicitly_blocked": True,
    }


def test_empty_external_list_is_not_execution_authority(payload):
    payload["capabilities"][8]["external_prerequisites"] = []
    candidate = validate_manifest(payload).next_work()["candidates"][0]
    assert candidate["external_prerequisites"] == []
    assert candidate["execution_ready"] is False


def test_completed_cannot_bypass_unfinished_dependencies(payload):
    payload["capabilities"][20].update(
        status="completed", stage="validation",
        completion_evidence=["src/infrastructure/execution_spine.py"],
    )
    with pytest.raises(ManifestError, match="unfinished dependencies"):
        validate_manifest(payload)


def test_status_is_inventory_not_test_count_readiness():
    status = load_manifest().status()
    assert status["status_counts"] == {"in_progress": 12, "planned": 9}
    assert status["stage_counts"] == {"baseline": 9, "inventory": 9, "original": 3}
    assert "ready" not in status
    assert "test_count" not in status


def test_receipt_reuses_spine_without_promotion_or_model_claims():
    record = load_manifest().receipt()
    assert isinstance(record, ExecutionSpineRecord)
    packet = record.to_dict()
    assert ExecutionSpineRecord.from_dict(packet).to_dict() == packet
    assert packet["status"] == "inventory_validated"
    assert packet["promotion"]["eligible"] is False
    assert packet["promotion"]["model_claim"] is False
    assert packet["promotion"]["physics_claim"] is False
    assert packet["governance"]["fail_closed"]
    assert packet["health_checks"][0]["details"] == {
        "model_evaluation_performed": False, "backend_probe_performed": False,
    }
    assert packet["compatibility"]["inventory"]["capability_count"] == 21


def test_order_independent_deterministic_outputs(payload):
    original = validate_manifest(payload)
    payload["capabilities"].reverse()
    shuffled = validate_manifest(payload)
    assert shuffled.status() == original.status()
    assert shuffled.next_work() == original.next_work()
    assert shuffled.receipt().to_dict() == original.receipt().to_dict()


@pytest.mark.parametrize("command", ["check", "status", "next", "receipt"])
def test_cli_json_deterministic_and_no_mutation(command, capsys):
    original = DEFAULT_MANIFEST.read_bytes()
    assert main([command]) == 0
    first = capsys.readouterr()
    assert not first.err
    assert main([command]) == 0
    second = capsys.readouterr()
    assert first.out == second.out
    assert isinstance(json.loads(first.out), dict)
    assert DEFAULT_MANIFEST.read_bytes() == original


def test_cli_module_entrypoint_stdlib_only():
    result = subprocess.run(
        [sys.executable, "-S", "-m", "src.infrastructure.ml_program", "check"],
        cwd=REPO_ROOT, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["valid"] is True


def test_cli_missing_manifest_fails_closed(capsys):
    assert main(["--manifest", str(REPO_ROOT / "does-not-exist.json"), "receipt"]) == 2
    output = capsys.readouterr()
    assert not output.out
    assert json.loads(output.err)["valid"] is False


@pytest.mark.parametrize("text", [
    "{", "[]", "null", '{"schema_version":"x"}', '{"x":1,"x":2}',
    '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}',
])
def test_loader_malformed_manifests_without_files(monkeypatch, text):
    monkeypatch.setattr(Path, "read_text", lambda *args, **kwargs: text)
    with pytest.raises(ManifestError):
        load_manifest()


def test_loader_unicode_error_is_actionable(monkeypatch):
    def fail(*args, **kwargs):
        raise UnicodeError("invalid input encoding")
    monkeypatch.setattr(Path, "read_text", fail)
    with pytest.raises(ManifestError, match="Cannot load manifest"):
        load_manifest()


def test_cli_custom_manifest_and_malformed_error(monkeypatch, capsys, payload):
    observed = []
    def read(path, **kwargs):
        observed.append(path)
        return json.dumps(payload)
    monkeypatch.setattr(Path, "read_text", read)
    assert main(["--manifest", "custom.json", "check"]) == 0
    assert observed == [Path("custom.json")]
    assert json.loads(capsys.readouterr().out)["valid"]
    payload["capabilities"][0]["id"] = True
    assert main(["--manifest", "custom.json", "check"]) == 2
    captured = capsys.readouterr()
    assert not captured.out
    assert "integer IDs" in json.loads(captured.err)["error"]
