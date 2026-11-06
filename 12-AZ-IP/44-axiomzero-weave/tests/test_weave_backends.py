# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Real local Product 16/43 adapter tests, isolated from repository hooks."""

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import types
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest


ROOT = Path(__file__).resolve().parents[3]
PRODUCT = ROOT / "12-AZ-IP" / "44-axiomzero-weave"
sys.path.insert(0, str(PRODUCT))
from az_weave.backends import Backends


@pytest.fixture
def workspace(tmp_path):
    return tmp_path


@pytest.fixture
def backend(workspace):
    state = workspace / "state"
    return Backends(ROOT, state, {"tiny": state / "models" / "tiny.npz"})


def oracle_input():
    return {
        "system_name": "Explicit synthetic project",
        "system_type": "software test",
        "body_specs": [
            {"label": f"Body {i}", "status": status, "phi_trust": 0.2 * i}
            for i, status in enumerate(("SOLID", "CONSTRAINED", "ESTIMATED", "OPEN", "OPEN"))
        ],
        "dim_scores": {
            "Transparency": 0.1, "Sequence Integrity": 0.2, "Participation": 0.3,
            "Accountability": 0.4, "Resilience": 0.5, "Epistemic Honesty": 0.6,
            "Freedom Floor": 0.7,
        },
    }


def train_input():
    return {
        "checkpoint_id": "tiny", "corpus": "abc abca cab\n" * 24,
        "steps": 2, "context_length": 4, "dim": 4, "num_heads": 1, "batch_size": 1,
    }


def test_registry_lazy_and_no_checkpoint_fallback(workspace, monkeypatch):
    state = workspace / "state"
    backend = Backends(ROOT, state)
    monkeypatch.setattr(backend, "_import", lambda _: pytest.fail("capabilities imported a provider"))
    caps = backend.capabilities()
    assert set(caps) == {"geometry", "oracle", "generate", "experiment", "train"}
    assert {key for key, value in caps.items() if value["effect"]} == {"train", "experiment"}
    assert caps["geometry"]["available"]
    assert caps["oracle"]["available"]
    assert not caps["generate"]["available"]
    assert not caps["train"]["available"]
    assert not state.exists()
    with pytest.raises(ValueError, match="allowlist"):
        backend.execute("generate", {"checkpoint_id": "missing", "prompt": "hello"})


def test_missing_numerical_dependency_is_unavailable(backend, monkeypatch):
    original = importlib.util.find_spec
    monkeypatch.setattr(importlib.util, "find_spec", lambda name: None if name == "numpy" else original(name))
    caps = backend.capabilities()
    assert caps["oracle"]["available"]
    assert all(not caps[key]["available"] for key in ("geometry", "experiment", "generate", "train"))


@pytest.mark.parametrize("fail_first", [False, True])
def test_provider_import_lock_covers_snapshot_import_restore_across_instances(backend, monkeypatch, fail_first):
    import az_weave.backends as adapters

    original = list(sys.path)
    first_entered, release, second_requested, second_entered = (
        threading.Event() for _ in range(4))
    sibling = Backends(ROOT, backend.state_dir)

    def importing(module):
        if module.startswith("az_tori_transformer"):
            assert sys.path[0] == str(ROOT / "12-AZ-IP/43-az-geometric-tori-transformer")
            first_entered.set()
            assert release.wait(5)
            if fail_first:
                raise ImportError("controlled provider failure")
        else:
            second_entered.set()
            assert sys.path[0] == str(ROOT / "12-AZ-IP/16-oracle")
        return types.SimpleNamespace(name=module)

    def second():
        second_requested.set()
        return sibling._import("oracle.engine.synthesis")

    monkeypatch.setattr(adapters.importlib, "import_module", importing)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(backend._import, "az_tori_transformer.toroidal_geometry")
        try:
            assert first_entered.wait(5)
            other = pool.submit(second)
            assert second_requested.wait(5)
            assert not second_entered.wait(0.1)
        finally:
            release.set()
        if fail_first:
            with pytest.raises(ImportError, match="controlled"):
                first.result(timeout=5)
        else:
            assert first.result(timeout=5).name.startswith("az_tori_transformer")
        assert other.result(timeout=5).name == "oracle.engine.synthesis"
    assert sys.path == original


def test_effect_preflight_is_readonly_and_uses_same_input_validation(backend):
    backend.preflight("train", train_input())
    backend.preflight("experiment", {"steps": 1})
    assert not backend.state_dir.exists()
    for action, args in [
        ("train", {}),
        ("train", {**train_input(), "validation_fraction": False}),
        ("train", {**train_input(), "corpus": "short"}),
        ("experiment", {"steps": 0}),
        ("experiment", {"alias_probe": True}),
        ("experiment", {"extra": "unknown"}),
    ]:
        with pytest.raises(ValueError):
            backend.preflight(action, args)
        with pytest.raises(ValueError):
            backend.execute(action, args)
    assert not backend.state_dir.exists()


def test_missing_provider_explicit_error(workspace):
    backend = Backends(workspace, workspace / "state")
    assert not any(item["available"] for item in backend.capabilities().values())
    with pytest.raises(ImportError, match="absent"):
        backend.execute("geometry", {})


def test_geometry_exact_real_diagnostics_and_alias74(backend):
    result = backend.execute("geometry", {"head_dim": 8})
    geometry = backend._import("az_tori_transformer.toroidal_geometry")
    positional = backend._import("az_tori_transformer.positional")
    assert result["diagnostics"] == positional.modular_alias_diagnostics(80, 8)
    assert result["alias_period"] == 74
    assert result["positions"] == [
        {"position": i, "code": list(geometry.position_code(i)), "bank": geometry.position_bank(i)}
        for i in range(80)
    ]
    assert result["positions"][0]["code"] == result["positions"][74]["code"]
    assert result["positions"][0]["bank"] == result["positions"][74]["bank"]
    assert result["diagnostics"]["scalar_bank_projection"]["output_coordinate_count"] == 1
    assert not backend.state_dir.exists()
    assert len(result["metadata"]["implementation_sha256"]) == 64
    assert not result["metadata"]["claims_superiority"]
    json.dumps(result, allow_nan=False)


def test_oracle_calls_real_orchestrator_explicit_assessments(backend):
    args = oracle_input()
    result = backend.execute("oracle", args)
    module = backend._import("oracle.engine.synthesis")
    report = module.SynthesisOrchestrator().synthesize(**args)
    assert result["scores"] == {
        "omega": report.omega_score, "integrity": report.integrity_score,
        "synthesis": report.synthesis_score,
    }
    assert [body["epistemic_status"] for body in result["report"]["pentad"]["bodies"]] == [
        item["status"] for item in args["body_specs"]
    ]
    assert "not independently verified authority" in result["interpretation"]
    assert result["metadata"]["evidence_kind"] == "input_derived_heuristic"
    assert not backend.state_dir.exists()
    json.dumps(result, allow_nan=False)


def test_oracle_import_collision_is_not_silently_replaced(backend, monkeypatch):
    impostor = types.ModuleType("oracle")
    impostor.__file__ = str(ROOT / "unrelated" / "oracle.py")
    monkeypatch.setitem(sys.modules, "oracle", impostor)
    assert not backend.capabilities()["oracle"]["available"]
    with pytest.raises(ImportError, match="collision"):
        backend.execute("oracle", oracle_input())
    assert sys.modules["oracle"] is impostor


@pytest.mark.parametrize("change", [
    lambda a: a.pop("body_specs"),
    lambda a: a.update(body_specs=a["body_specs"][:4]),
    lambda a: a["body_specs"][0].pop("status"),
    lambda a: a["body_specs"][0].pop("phi_trust"),
    lambda a: a["body_specs"][0].update(status="solid"),
    lambda a: a["body_specs"][0].update(phi_trust=True),
    lambda a: a["body_specs"][0].update(phi_trust=1.1),
    lambda a: a["body_specs"][0].update(label="Body 1"),
    lambda a: a["dim_scores"].pop("Freedom Floor"),
    lambda a: a["dim_scores"].update(Transparency=-0.1),
    lambda a: a["dim_scores"].update(Transparency=False),
    lambda a: a["dim_scores"].update(Extra=0.5),
])
def test_oracle_rejects_missing_optimistic_defaults_and_invalid_values(backend, change):
    args = oracle_input()
    change(args)
    with pytest.raises(ValueError):
        backend.execute("oracle", args)


@pytest.mark.parametrize(("action", "args"), [
    ("memory", {}),
    ("geometry", []),
    ("geometry", {"head_dim": True}),
    ("geometry", {"head_dim": 3}),
    ("geometry", {"head_dim": 66}),
    ("geometry", {"path": "arbitrary"}),
    ("train", {"checkpoint_id": "../x", "corpus": "x"}),
    ("train", {"checkpoint_id": "tiny", "corpus": "x", "steps": True}),
    ("train", {**train_input(), "steps": 101}),
    ("train", {**train_input(), "batch_size": 17}),
    ("train", {**train_input(), "context_length": 129}),
    ("train", {**train_input(), "dim": 65}),
    ("train", {**train_input(), "num_heads": 3}),
    ("train", {**train_input(), "learning_rate": float("nan")}),
    ("train", {**train_input(), "validation_fraction": 0}),
    ("train", {**train_input(), "corpus": "x"}),
    ("train", {**train_input(), "corpus": "é" * 40000}),
    ("train", {**train_input(), "corpus": "".join(chr(i + 1000) for i in range(257)) * 4}),
    ("train", {**train_input(), "corpus_path": "/etc/passwd"}),
    ("train", {**train_input(), "learning_rate": 10**400}),
    ("experiment", {"steps": False}),
    ("experiment", {"alias_probe": "true"}),
    ("experiment", {"alias_probe": True, "context_length": 74}),
    ("experiment", {"steps": 100, "batch_size": 16, "context_length": 128, "dim": 64}),
    ("geometry", {"head_dim": float("inf")}),
    ("geometry", {1: "not JSON"}),
    ("geometry", {"head_dim": object()}),
])
def test_strict_bounds_before_effects(backend, action, args):
    with pytest.raises(ValueError):
        backend.execute(action, args)
    assert not backend.state_dir.exists()


def test_training_rejects_external_destination_and_symlink_escape(workspace):
    state = workspace / "state"
    outside = workspace / "outside"
    outside.mkdir()
    state.mkdir()
    (state / "escape").symlink_to(outside, target_is_directory=True)
    for path in (outside / "model.npz", state / "escape" / "model.npz"):
        backend = Backends(ROOT, state, {"tiny": path})
        with pytest.raises(ValueError, match="inside state_dir"):
            backend.execute("train", train_input())
    assert not list(outside.iterdir())


def test_tiny_real_train_then_configured_generation(backend):
    assert not backend.capabilities()["generate"]["available"]
    with pytest.raises(RuntimeError, match="unavailable"):
        backend.execute("generate", {"checkpoint_id": "tiny", "prompt": "abc"})
    trained = backend.execute("train", train_input())
    checkpoint_path = backend.checkpoints["tiny"]
    assert checkpoint_path.is_file()
    assert trained["checkpoint_sha256"] == hashlib.sha256(checkpoint_path.read_bytes()).hexdigest()
    assert trained["model_config"]["dim"] == 4
    assert trained["metrics"]["completed_steps"] == 2
    assert math.isfinite(trained["metrics"]["final_validation_loss"])
    assert trained["metrics"]["validation_characters"] > 4
    assert backend.capabilities()["generate"]["available"]
    assert checkpoint_path.stat().st_mode & 0o777 == 0o600
    assert backend.state_dir.stat().st_mode & 0o777 == 0o700
    corpus = list((backend.state_dir / "corpora").glob("*.txt"))
    assert len(corpus) == 1
    assert corpus[0].read_text() == train_input()["corpus"]
    assert corpus[0].stat().st_mode & 0o777 == 0o600
    assert not list(backend.state_dir.rglob("*.pending"))

    args = {"checkpoint_id": "tiny", "prompt": "abc", "max_new_tokens": 8, "seed": 3}
    generated = backend.execute("generate", args)
    workflow = backend._import("az_tori_transformer.text_workflow")
    assert generated["text"] == workflow.generate_text(checkpoint_path, "abc", max_new_tokens=8, seed=3)
    assert generated["text"].startswith("abc")
    assert len(generated["text"]) == 11
    assert generated["checkpoint_sha256"] == trained["checkpoint_sha256"]
    assert generated["model_config"] == trained["model_config"]
    before = {p: p.read_bytes() for p in backend.state_dir.rglob("*") if p.is_file()}
    assert backend.execute("generate", args)["text"] == generated["text"]
    assert before == {p: p.read_bytes() for p in backend.state_dir.rglob("*") if p.is_file()}
    for bad in ({"max_new_tokens": 129}, {"max_new_tokens": True}, {"prompt": "z"},
                {"temperature": False}, {"top_k": 257}, {"checkpoint_path": str(checkpoint_path)}):
        with pytest.raises(ValueError):
            backend.execute("generate", {**args, **bad})
    json.dumps(trained, allow_nan=False)
    json.dumps(generated, allow_nan=False)


def test_experiment_runs_four_real_arms_two_tasks_and_persists_private_evidence(backend):
    args = {"steps": 2, "dim": 4, "num_heads": 1, "context_length": 6, "batch_size": 1}
    result = backend.execute("experiment", args)
    assert set(result["tasks"]) == {"periodic_copy", "nonperiodic_copy"}
    assert result["run_scope"] == "default smoke execution only"
    assert result["controls"]["identical_initial_parameters"]
    assert result["controls"]["identical_batches_per_arm"]
    assert not result["shared_settings"]["causal"]
    for task in result["tasks"].values():
        arms = task["arms"]
        assert len(arms) == 4
        assert len({arm["parameter_count"] for arm in arms.values()}) == 1
        for name, arm in arms.items():
            assert arm["completed_steps"] == 2
            assert math.isfinite(arm["heldout_loss"])
            assert 0 <= arm["heldout_accuracy"] <= 1
            if name.endswith("_off"):
                assert arm["active_parameter_count"] == arm["parameter_count"] - 38
                assert arm["bias_l2"] == 0
            else:
                assert arm["active_parameter_count"] == arm["parameter_count"]
                assert arm["bias_l2"] > 0
    artifact = backend.state_dir / result["artifact"]["path"]
    assert artifact.is_file()
    assert result["artifact"]["sha256"] == hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert json.loads(artifact.read_text())["tasks"] == result["tasks"]
    assert artifact.stat().st_mode & 0o777 == 0o600
    rerun = backend.execute("experiment", args)
    assert rerun["tasks"] == result["tasks"]


def test_opt_in_alias74_probe_really_trains_on_context75(backend):
    result = backend.execute("experiment", {
        "alias_probe": True, "context_length": 75, "steps": 1, "batch_size": 1,
        "dim": 2, "num_heads": 1,
    })
    assert result["shared_settings"]["context_length"] == 75
    assert result["run_scope"] == "alias-sensitive synthetic probe"
    task = result["tasks"]["alias74_lag_copy"]
    assert "only positions i>=74" in task["target_rule"]
    assert len(task["arms"]) == 4
    assert all(item["completed_steps"] == 1 for item in task["arms"].values())
    assert all(math.isfinite(item["heldout_loss"]) for item in task["arms"].values())


def test_bad_constructor_checkpoint_configuration(workspace):
    for mapping in ([], {"../escape": workspace / "x"}, {"id": "request-path"}):
        with pytest.raises(ValueError):
            Backends(ROOT, workspace / "state", mapping)


@pytest.mark.parametrize(("field", "value"), [
    ("dim", 128), ("num_heads", True), ("num_layers", 3),
    ("ff_hidden_dim", 512), ("vocab_size", 300), ("context_length", 129),
])
def test_configured_checkpoint_preflight_rejects_oversized_models_before_loading(backend, monkeypatch, field, value):
    import numpy as np

    path = backend.checkpoints["tiny"]
    path.parent.mkdir(parents=True)
    config = {"dim": 4, "num_heads": 1, "num_layers": 1, "ff_hidden_dim": 64, "vocab_size": 4}
    metadata = {"context_length": 4}
    (metadata if field == "context_length" else config)[field] = value
    with path.open("wb") as stream:
        np.savez(stream, manifest=np.array(json.dumps({"config": config, "metadata": metadata})))
    checkpoint = backend._import("az_tori_transformer.checkpoint")
    monkeypatch.setattr(checkpoint, "load_checkpoint", lambda _: pytest.fail("unbounded checkpoint allocated"))
    with pytest.raises(ValueError, match=f"checkpoint {field}"):
        backend.execute("generate", {"checkpoint_id": "tiny", "prompt": "a"})


def test_generation_rejects_checkpoint_swap_instead_of_wrong_identity(backend, monkeypatch):
    backend.execute("train", train_input())
    workflow = backend._import("az_tori_transformer.text_workflow")
    original = workflow.generate_text

    def swapped(path, *args, **kwargs):
        output = original(path, *args, **kwargs)
        with path.open("ab") as stream:
            stream.write(b"changed")
        return output

    monkeypatch.setattr(workflow, "generate_text", swapped)
    with pytest.raises(RuntimeError, match="changed during generation"):
        backend.execute("generate", {"checkpoint_id": "tiny", "prompt": "a", "max_new_tokens": 1})


def test_real_resume_binds_hash_and_preserves_optimizer_progress(backend):
    trained = backend.execute("train", train_input())
    resumed = backend.execute("train", {
        "checkpoint_id": "tiny", "corpus": train_input()["corpus"], "steps": 2,
        "resume": True, "expected_checkpoint_sha256": trained["checkpoint_sha256"],
    })
    assert resumed["metrics"]["resumed"]
    assert resumed["metrics"]["completed_steps"] == 4
    assert resumed["metrics"]["steps_this_run"] == 2
    assert resumed["resumed_from_checkpoint_sha256"] == trained["checkpoint_sha256"]
    assert resumed["checkpoint_sha256"] != trained["checkpoint_sha256"]
    assert resumed["model_config"] == trained["model_config"]
    before = {p: p.read_bytes() for p in backend.state_dir.rglob("*") if p.is_file()}
    with pytest.raises(ValueError, match="does not match"):
        backend.execute("train", {
            **train_input(), "resume": True, "expected_checkpoint_sha256": trained["checkpoint_sha256"],
        })
    assert before == {p: p.read_bytes() for p in backend.state_dir.rglob("*") if p.is_file()}


@pytest.mark.parametrize("changes", [
    {"expected_checkpoint_sha256": None},
    {"expected_checkpoint_sha256": True},
    {"corpus": "different corpus " * 24},
    {"context_length": 6},
    {"dim": 8},
    {"learning_rate": 0.02},
    {"validation_fraction": 0.3},
    {"resume": "yes"},
])
def test_resume_validation_fails_without_writes(backend, changes):
    trained = backend.execute("train", train_input())
    args = {
        **train_input(), "resume": True,
        "expected_checkpoint_sha256": trained["checkpoint_sha256"], **changes,
    }
    before = {p: p.read_bytes() for p in backend.state_dir.rglob("*") if p.is_file()}
    with pytest.raises(ValueError):
        backend.execute("train", args)
    assert before == {p: p.read_bytes() for p in backend.state_dir.rglob("*") if p.is_file()}


def oracle_decision_input():
    return {
        **oracle_input(), "decision_question": "Which explicit intervention?",
        "decision_options": [
            {"name": name, "phi_trust_impact": impact, "impacts": [
                {"body_label": "Body 3", "direction": "improve", "magnitude": magnitude},
            ]}
            for name, impact, magnitude in (("Prototype", 0.1, 0.4), ("Measure", 0.2, 0.8))
        ],
        "commitments": [{
            "domain": "software", "commitment": "Measure heldout accuracy",
            "falsification_condition": "Accuracy does not improve over the declared baseline",
            "test_horizon": "one week",
        }],
    }


def test_oracle_real_alternatives_and_falsifiable_commitments(backend):
    args = oracle_decision_input()
    result = backend.execute("oracle", args)
    report = backend._import("oracle.engine.synthesis").SynthesisOrchestrator().synthesize(**args)
    from dataclasses import asdict

    assert result["report"]["decision_analysis"] == asdict(report.decision_analysis)
    assert result["report"]["commitments"] == args["commitments"]
    assert result["report"]["decision_analysis"]["question"] == args["decision_question"]
    assert not backend.state_dir.exists()
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("change", [
    lambda a: a.update(decision_question=""),
    lambda a: a.update(decision_options=[]),
    lambda a: a.update(decision_options=a["decision_options"][:1]),
    lambda a: a.update(decision_options=a["decision_options"] * 5),
    lambda a: a["decision_options"][0].update(phi_trust_impact=True),
    lambda a: a["decision_options"][0].pop("phi_trust_impact"),
    lambda a: a["decision_options"][0]["impacts"][0].update(body_label="Unknown"),
    lambda a: a["decision_options"][0]["impacts"][0].update(direction="positive"),
    lambda a: a["decision_options"][0]["impacts"][0].update(magnitude=2.1),
    lambda a: a["decision_options"][0]["impacts"][0].update(magnitude=False),
    lambda a: a["decision_options"][0].update(impacts=[{}]),
    lambda a: a["commitments"][0].pop("falsification_condition"),
    lambda a: a["commitments"][0].update(test_horizon=False),
    lambda a: a.update(commitments=a["commitments"] * 17),
])
def test_oracle_optional_decision_validation_is_strict(backend, change):
    args = oracle_decision_input()
    change(args)
    with pytest.raises(ValueError):
        backend.execute("oracle", args)
    assert not backend.state_dir.exists()
