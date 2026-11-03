# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Real integration: grounding, computation, governed effects and continuity."""

import hashlib
import pytest

from az_weave import OBLIGATIONS, OPERATIONS
from az_weave.api import Weave, run_readonly, repository_root, compute_readonly
from az_weave.evidence import SourceIndex
from az_weave.memory import ReadOnlyFederation

PASS = {key: "PASS" for key in OBLIGATIONS}
ROOT = repository_root()


def oracle_input():
    return {
        "system_name": "Positional encoding experiment", "system_type": "software research",
        "body_specs": [
            {"label": role, "status": "OPEN", "phi_trust": 0.2,
             "open_gaps": "Synthetic probe only; no independent scientific certification."}
            for role in ["Reality", "Observer", "Human intent", "AI precision", "Trust coupling"]],
        "dim_scores": {name: 0.2 for name in [
            "Transparency", "Sequence Integrity", "Participation", "Accountability",
            "Resilience", "Epistemic Honesty", "Freedom Floor"]},
    }


@pytest.fixture
def weave(tmp_path):
    return Weave(tmp_path / "private", repo_root=ROOT)


def test_readonly_semantic_identity_is_separate_from_clock_and_run_id():
    one = run_readonly("geometric tori transformer positional encoding")
    two = run_readonly("geometric tori transformer positional encoding")
    assert one["semantic_sha256"] == two["semantic_sha256"]
    assert one["run_id"] != two["run_id"]
    assert one["status"] == "GROUNDED_RETRIEVAL"
    assert [stage["operation"] for stage in one["stages"]] == list(OPERATIONS)
    assert all(stage["state"] == "OK" for stage in one["stages"])
    assert any("43-az-geometric-tori-transformer/" in row["source"] for row in one["evidence"])
    assert not one["stages"][3]["value"]["model_inference"]
    assert one["execution_spine"]["promotion"]["physics"] is False


def test_no_source_abstains_instead_of_wrong_domain():
    result = run_readonly("zzyqqwwunrelatedunfindableidentifier")
    assert result["status"] == "HOLD"
    assert not result["answer"]
    assert "abstain" in " ".join(result["limitations"])


def test_failed_source_blocks_reasoning(weave, monkeypatch):
    def unavailable(*args, **kwargs):
        raise OSError("source unavailable")
    monkeypatch.setattr(weave.index, "search", unavailable)
    result = weave.query("toroidal", "alice")
    assert result["status"] == "HOLD"
    assert result["stages"][1]["state"] == "FAILED"
    assert result["stages"][3]["blocked_by"] == ["ground"]
    assert "source unavailable" in " ".join(result["limitations"])


def test_private_memory_governed_lifecycle_does_not_duplicate_payload(weave):
    secret = "private-unique-memory-payload-for-purge-check"
    arguments = {"text": secret}
    with pytest.raises(ValueError, match="approval"):
        weave.invoke("memory.put", arguments, "alice")
    decision = weave.approve("memory.put", arguments, "alice", obligations=PASS)
    result = weave.invoke("memory.put", arguments, "alice", decision)
    record_id = result["result"]["id"]
    assert "text" not in result["result"]
    assert not weave.memory.search("bob", secret)
    assert weave.memory.search("alice", secret)
    args = {"record_id": record_id}
    for action in ["memory.promote", "memory.delete"]:
        approved = weave.approve(action, args, "alice", obligations=PASS)
        weave.invoke(action, args, "alice", approved)
    assert not weave.memory.search("alice", secret)
    assert secret.encode() not in weave.memory.db_path.read_bytes()
    assert secret.encode() not in weave.journal.path.read_bytes()
    assert weave.journal.verify_audit()


def test_federated_historical_approval_is_inert(weave):
    weave.federation = ReadOnlyFederation(
        [{"id": "historical", "text": "toroidal experiment", "approved": True,
          "owner": "original-owner", "created_at": "2026-10-24"}], owner="alice")
    receipt = weave.query("toroidal experiment", "alice")
    memory = receipt["stages"][2]["value"]
    assert memory[0]["status"] == "candidate" and memory[0]["current"] is False
    assert not weave.query("toroidal experiment", "bob")["stages"][2]["value"]
    with pytest.raises(ValueError, match="approval"):
        weave.invoke("experiment", {"steps": 1}, "alice")


def test_stale_source_cannot_authorize_effect(weave, tmp_path):
    source = tmp_path / "readme.md"
    source.write_text("toroidal evidence")
    weave.index = SourceIndex(tmp_path, ["readme.md"])
    evidence = weave.index.search("toroidal")
    args = {"text": "candidate"}
    identifier = weave.approve("memory.put", args, "alice", obligations=PASS, sources=evidence)
    source.write_text("corrected evidence")
    with pytest.raises(ValueError, match="changed"):
        weave.invoke("memory.put", args, "alice", identifier)
    assert not weave.memory.search("alice", "candidate")


def test_configuration_change_invalidates_approval(weave):
    args = {"text": "candidate"}
    identifier = weave.approve("memory.put", args, "alice", obligations=PASS)
    weave.targets["different"] = "/new/operator/target"
    with pytest.raises(ValueError, match="exact action"):
        weave.invoke("memory.put", args, "alice", identifier)


def test_real_capstone_proposal_approval_computation_and_correction(weave):
    query = "geometric tori transformer positional encoding"
    arguments = {"steps": 2, "seed": 7, "context_length": 8, "dim": 4, "num_heads": 1}
    proposed = weave.investigate(query, "alice", experiment=arguments, oracle=oracle_input())
    assert proposed["status"] == "AWAITING_APPROVAL"
    assert proposed["stages"][3]["value"]["oracle"]["result"]["metadata"]["provider"].startswith("Product16")
    assert not (weave.state_dir / "models" / "experiments").exists()
    decision = weave.approve("experiment", arguments, "alice",
                             obligations=PASS, sources=proposed["evidence"])
    finished = weave.investigate(query, "alice", experiment=arguments,
                                oracle=oracle_input(), decision_id=decision)
    assert finished["status"] == "EXPERIMENT_RECORDED"
    measured = finished["experiment"]["result"]
    assert measured["metadata"]["evidence_kind"] == "measured_synthetic_factorial"
    assert not measured["metadata"]["claims_superiority"]
    for task in measured["tasks"].values():
        assert len(task["arms"]) == 4
        assert all(arm["completed_steps"] == 2 for arm in task["arms"].values())
    artifact = weave.state_dir / "models" / measured["artifact"]["path"]
    assert hashlib.sha256(artifact.read_bytes()).hexdigest() == measured["artifact"]["sha256"]
    assert not weave.memory.search("alice", "geometry")
    proposal = finished["lesson_proposal"]
    args = {"text": proposal["text"], "sources": proposal["sources"]}
    approved = weave.approve("memory.put", args, "alice", obligations=PASS,
                             sources=proposal["sources"])
    weave.invoke("memory.put", args, "alice", approved)
    restarted = Weave(weave.state_dir, repo_root=ROOT)
    assert restarted.memory.search("alice", "geometry")
    assert restarted.journal.verify_audit()
    replay = restarted.invoke("experiment", arguments, "alice", decision)
    assert replay["replayed"]


@pytest.mark.parametrize("query,limit", [("", 5), ("x" * 2049, 5), ("x", True), ("x", 0)])
def test_public_query_bounds(query, limit):
    with pytest.raises(ValueError):
        run_readonly(query, limit)


def test_native_computation_is_real_readonly_and_path_scoped(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AZ_WEAVE_CHECKPOINTS_JSON", raising=False)
    result = compute_readonly("geometry", {}, repo_root=ROOT)
    assert result["alias_period"] == 74
    assert not (tmp_path / ".axiomzero-weave").exists()
    for action in ["train", "experiment", "approve", "memory.put"]:
        with pytest.raises(ValueError, match="only"):
            compute_readonly(action, {}, repo_root=ROOT)
    with pytest.raises(ValueError, match="unknown"):
        compute_readonly("generate", {"checkpoint_path": "/arbitrary", "prompt": "x"}, repo_root=ROOT)
    monkeypatch.setenv("AZ_WEAVE_CHECKPOINTS_JSON", "[]")
    with pytest.raises(ValueError, match="object"):
        compute_readonly("geometry", {}, repo_root=ROOT)


def test_cli_readonly_does_not_create_state_and_errors_are_nonzero(tmp_path, capsys):
    from az_weave.__main__ import main
    state = tmp_path / "not-created"
    assert main(["--repo-root", str(ROOT), "--state-dir", str(state), "query", "toroidal"]) == 0
    assert not state.exists()
    assert "GROUNDED_RETRIEVAL" in capsys.readouterr().out
    assert main(["query", ""]) == 2
    assert "ValueError" in capsys.readouterr().err
