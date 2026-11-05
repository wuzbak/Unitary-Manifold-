# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Real integration: grounding, computation, governed effects and continuity."""

import hashlib
from datetime import datetime, timedelta, timezone
import pytest

from az_weave import OBLIGATIONS, OPERATIONS
from az_weave.api import TemporalQueryContext, Weave, run_readonly, repository_root, compute_readonly
from az_weave.evidence import SourceIndex
from az_weave.memory import ReadOnlyFederation
from src.infrastructure.temporal_data import TemporalFeatureRecord, TemporalSnapshot

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


def test_query_temporal_context_is_point_in_time_scoped_and_separate(weave):
    utc = timezone.utc
    start = datetime(2026, 1, 1, tzinfo=utc)
    owner = "alice"
    records = (
        TemporalFeatureRecord(owner, "entity-1", "balance", 10, start, start),
        TemporalFeatureRecord(
            owner, "entity-1", "balance", 20, start, start + timedelta(hours=2),
            revision_at=start + timedelta(hours=2),
        ),
        TemporalFeatureRecord(
            owner, "entity-1", "balance", 30, start + timedelta(hours=1),
            start + timedelta(hours=3), revision_at=start + timedelta(hours=3),
        ),
        TemporalFeatureRecord(owner, "entity-1", "stale", 4, start, start),
        TemporalFeatureRecord(
            owner, "entity-1", "explicitly_missing", None, start, start,
            missing_reason="source_value_missing",
        ),
        TemporalFeatureRecord(
            owner, "entity-1", "synthetic", 9, start, start, origin="synthetic",
        ),
    )
    snapshot = TemporalSnapshot(owner, start + timedelta(hours=4), records)
    weave.memory.put(owner, "geometric tori transformer memory note")

    def context(at, *, features=("balance",), ttl=None, origins=("real",)):
        return TemporalQueryContext(
            snapshot=snapshot,
            owner_scope=owner,
            snapshot_hash=snapshot.content_hash,
            entity_id="entity-1",
            feature_names=features,
            decision_time=at,
            freshness_ttl_seconds=ttl,
            allow_origins=origins,
        )

    before_correction = weave.query(
        "geometric tori transformer", owner,
        temporal=context(start + timedelta(hours=1)),
    )["temporal_context"]
    after_correction = weave.query(
        "geometric tori transformer", owner,
        temporal=context(start + timedelta(hours=2, minutes=30)),
    )["temporal_context"]
    after_future_record = weave.query(
        "geometric tori transformer", owner,
        temporal=context(start + timedelta(hours=3, minutes=30)),
    )["temporal_context"]
    assert [item["value"] for item in (
        before_correction["features"][0],
        after_correction["features"][0],
        after_future_record["features"][0],
    )] == [10, 20, 30]
    assert before_correction["snapshot_hash"] == snapshot.content_hash
    assert before_correction["owner_scope"] == owner
    assert before_correction["decision_time"] == "2026-01-01T01:00:00.000000Z"
    assert before_correction["allow_origins"] == ["real"]
    assert before_correction["features"][0]["available_at"] == "2026-01-01T00:00:00.000000Z"
    assert after_correction["features"][0]["revision_at"] == "2026-01-01T02:00:00.000000Z"

    bounded = weave.query(
        "geometric tori transformer", owner,
        temporal=context(
            start + timedelta(hours=4),
            features=("stale", "explicitly_missing", "absent", "synthetic"),
            ttl=2,
        ),
    )["temporal_context"]["features"]
    assert [(item["value"], item["missing_reason"]) for item in bounded] == [
        (None, "stale"),
        (None, "source_value_missing"),
        (None, "no_point_in_time_data"),
        (None, "origin_not_allowed"),
    ]
    assert bounded[3]["origin"] is None

    opted_in_synthetic = weave.query(
        "geometric tori transformer", owner,
        temporal=context(
            start + timedelta(hours=1), features=("synthetic",),
            origins=("real", "synthetic"),
        ),
    )["temporal_context"]["features"][0]
    assert opted_in_synthetic["value"] == 9
    assert opted_in_synthetic["origin"] == "synthetic"

    with pytest.raises(ValueError, match="snapshot_hash"):
        TemporalQueryContext(
            snapshot=snapshot, owner_scope=owner, snapshot_hash="0" * 64,
            entity_id="entity-1", feature_names=("balance",),
            decision_time=start, freshness_ttl_seconds=None,
        )
    with pytest.raises(ValueError, match="owner_scope"):
        TemporalQueryContext(
            snapshot=snapshot, owner_scope="bob", snapshot_hash=snapshot.content_hash,
            entity_id="entity-1", feature_names=("balance",),
            decision_time=start, freshness_ttl_seconds=None,
        )
    with pytest.raises(ValueError, match="already loaded"):
        TemporalQueryContext(
            snapshot=weave.state_dir / "snapshot.json", owner_scope=owner,
            snapshot_hash="0" * 64, entity_id="entity-1",
            feature_names=("balance",), decision_time=start,
            freshness_ttl_seconds=None,
        )
    with pytest.raises(ValueError, match="query principal"):
        weave.query("geometric tori transformer", "bob", temporal=context(start))

    before_memory = weave.memory.db_path.read_bytes()
    before_journal = weave.journal.path.read_bytes()
    legacy = weave.query("geometric tori transformer", owner)
    with_temporal = weave.query(
        "geometric tori transformer", owner, temporal=context(start),
    )
    assert with_temporal["evidence"] == legacy["evidence"]
    assert with_temporal["stages"] == legacy["stages"]
    assert with_temporal["status"] == legacy["status"]
    assert with_temporal["stages"][2]["value"][0]["text"] == "geometric tori transformer memory note"
    assert weave.memory.db_path.read_bytes() == before_memory
    assert weave.journal.path.read_bytes() == before_journal
    assert "temporal_context" not in legacy
    assert with_temporal["semantic_sha256"] != legacy["semantic_sha256"]
    repeated = weave.query("geometric tori transformer", owner, temporal=context(start))
    changed = weave.query(
        "geometric tori transformer", owner,
        temporal=context(start + timedelta(hours=1)),
    )
    assert repeated["semantic_sha256"] == with_temporal["semantic_sha256"]
    assert changed["semantic_sha256"] != with_temporal["semantic_sha256"]


@pytest.mark.parametrize(("changes", "message"), [
    ({"entity_id": ""}, "entity_id"),
    ({"feature_names": ()}, "feature_names"),
    ({"feature_names": ["balance"]}, "feature_names"),
    ({"feature_names": ("balance", "balance")}, "feature_names"),
    ({"feature_names": ("",)}, "feature_names"),
    ({"decision_time": datetime(2026, 1, 1)}, "timezone-aware"),
    ({"freshness_ttl_seconds": True}, "freshness_ttl_seconds"),
    ({"freshness_ttl_seconds": -1}, "freshness_ttl_seconds"),
    ({"freshness_ttl_seconds": float("inf")}, "freshness_ttl_seconds"),
    ({"freshness_ttl_seconds": float("nan")}, "freshness_ttl_seconds"),
    ({"allow_origins": ("unrecognized",)}, "allow_origins"),
    ({"allow_origins": ("real", "real")}, "allow_origins"),
    ({"allow_origins": ["real"]}, "allow_origins"),
])
def test_temporal_query_context_rejects_invalid_policy(changes, message):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    snapshot = TemporalSnapshot("alice", start, ())
    arguments = {
        "snapshot": snapshot,
        "owner_scope": "alice",
        "snapshot_hash": snapshot.content_hash,
        "entity_id": "entity-1",
        "feature_names": ("balance",),
        "decision_time": start,
        "freshness_ttl_seconds": None,
    }
    arguments.update(changes)
    with pytest.raises(ValueError, match=message):
        TemporalQueryContext(**arguments)


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
