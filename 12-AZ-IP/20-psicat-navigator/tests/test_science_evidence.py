# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Synthetic test fixtures exercise gates; they are not model-run evidence."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
for root in (REPO_ROOT, PRODUCT_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from ox_navigator.engine.merlin_science_evidence import (
    LANES,
    evaluate_science_evidence,
    evaluate_science_expansion,
    get_science_evidence_registry,
    get_science_collaboration_benchmark_spec,
    get_science_collaboration_benchmark_corpus,
    run_collaboration_benchmark,
    run_science_collaboration_tool,
    science_evidence_digest,
)


def budget(tokens=100, tool_calls=4, seconds=10, cost=1):
    return dict(tokens=tokens, tool_calls=tool_calls, seconds=seconds, cost=cost)


def fixture_request():
    tasks = [
        {
            "task_id": f"heldout-{index}", "prompt": f"Fixture question {index}",
            "expected": {"answer": index}, "split": "held_out",
            "provenance_url": f"https://example.org/tasks/{index}",
            "holdout_review_id": f"fixture-holdout-{index}",
        }
        for index in range(2)
    ]
    outputs = {}
    for lane in LANES:
        outputs[lane] = []
        for index, task in enumerate(tasks):
            kinds = ("merlin", "model") if lane == "collaboration" else (
                "model" if lane == "llm" else "merlin",
            )
            executions = []
            for participant, kind in enumerate(kinds):
                allocation = budget(50, 2, 5, .5) if lane == "collaboration" else budget()
                executions.append({
                    "execution_id": f"fixture-{lane}-{index}-{participant}",
                    "system_id": f"fixture-{kind}",
                    "model_revision": "fixture-revision-not-a-real-model",
                    "kind": kind,
                    "execution_mode": "recorded",
                    "artifact_url": f"https://example.org/fixtures/{lane}/{index}/{participant}",
                    "budget": allocation,
                    "usage": budget(10, 1, 1, .1),
                })
            outputs[lane].append({
                "task_id": task["task_id"], "task_digest": science_evidence_digest(task),
                "lane": lane, "origin": "recorded",
                "complete_execution_accounting": True,
                "output": deepcopy(task["expected"]) if lane == "collaboration" else {"answer": -1},
                "executions": executions,
            })
    return {
        "tasks": tasks, "budgets": {lane: budget() for lane in LANES},
        "training_task_ids": ["training-0"], "recorded_outputs": outputs,
    }


def artifact_store_verifier(request):
    """Simulate independently stored fixture artifacts, not receipt flags."""
    manifest = {
        "tasks": request["tasks"], "training_task_ids": request["training_task_ids"],
    }
    manifest_digest = science_evidence_digest(manifest)
    records = {
        science_evidence_digest(record): deepcopy(record)
        for records in request["recorded_outputs"].values() for record in records
    }

    def verify(packet):
        if packet["kind"] == "held_out_manifest":
            return (
                packet["manifest_digest"] == manifest_digest
                and packet["tasks"] == manifest["tasks"]
                and packet["training_task_ids"] == manifest["training_task_ids"]
            )
        return (
            packet["kind"] == "execution_receipt"
            and records.get(packet["receipt_id"]) == packet["record"]
        )

    return verify


def deterministic_fixture_request():
    request = fixture_request()
    request["execution_mode"] = "deterministic"
    request["frozen_manifest_digest"] = science_evidence_digest({
        "tasks": request["tasks"], "training_task_ids": request["training_task_ids"],
    })
    for records in request["recorded_outputs"].values():
        for record in records:
            for execution in record["executions"]:
                execution["kind"] = "merlin"
                execution["execution_mode"] = "deterministic"
                execution.pop("model_revision")
    return request


def evidence_fixture():
    return {
        "resource_id": "fixture-only",
        "discovery_url": "https://hai.stanford.edu/news/fixture",
        "canonical_truth": False,
        "limitations": ["Test fixture, not scientific evidence or actual license review."],
        **{
            category: [{
                "url": f"https://example.org/{category}/fixture",
                "revision": "fixture-version",
                "provenance_url": f"https://example.org/reviews/{category}",
                "license": {
                    "identifier": "LicenseRef-Test-Fixture",
                    "url": f"https://example.org/{category}/license",
                    "reuse_permitted": True, "review_id": f"fixture-rights-{category}",
                },
            }]
            for category in ("papers", "code", "datasets")
        },
    }


def expansion_fixture():
    request = fixture_request()
    verifier = artifact_store_verifier(request)
    evidence = evidence_fixture()
    hardware = {
        "resource_id": evidence["resource_id"], "assessment_id": "fixture-hardware",
        "required_memory_gb": 2, "available_memory_gb": 4,
        "required_seconds": 10, "available_seconds": 20,
    }
    benchmark = run_collaboration_benchmark(**request, receipt_verifier=verifier)
    approval = {
        "actor_type": "human", "actor_id": "fixture-steward", "approved": True,
        "approval_id": "fixture-approval", "resource_id": evidence["resource_id"],
        "benchmark_digest": benchmark["benchmark_digest"],
        "evidence_digest": science_evidence_digest(evidence),
        "hardware_digest": science_evidence_digest(hardware),
    }
    approved_packets = [
        {"kind": "source_rights_and_provenance", "resource_id": evidence["resource_id"],
         "category": category, "source": source}
        for category in ("papers", "code", "datasets") for source in evidence[category]
    ] + [
        {"kind": "hardware_assessment", "assessment": deepcopy(hardware)},
        {"kind": "human_approval", "approval": deepcopy(approval)},
    ]
    approved_digests = {science_evidence_digest(packet) for packet in approved_packets}
    return {
        "evidence": evidence, "benchmark_request": request,
        "hardware": hardware, "human_approval": approval,
        "receipt_verifier": verifier,
        "review_verifier": lambda packet: science_evidence_digest(packet) in approved_digests,
    }


def test_discovery_registry_source_chains_do_not_invent_rights_or_scientific_review():
    registry = get_science_evidence_registry()
    assert registry["discovery"]["role"] == "discovery_only"
    assert registry["external_evidence_is_canonical_truth"] is False
    assert registry["automatic_integrations"] is False
    assert {entry["code"][0]["url"] for entry in registry["candidates"]} == {
        "https://github.com/snap-stanford/Biomni",
        "https://github.com/zou-group/virtual-lab",
        "https://github.com/ArcInstitute/evo2",
    }
    expected_papers = {
        "biomni": "https://www.biorxiv.org/content/10.1101/2025.05.30.656746v1",
        "virtual_lab": "https://www.nature.com/articles/s41586-025-09442-9",
        "evo2": "https://www.nature.com/articles/s41586-026-10176-5",
    }
    expected_licenses = {"biomni": "Apache-2.0", "virtual_lab": "MIT", "evo2": "Apache-2.0"}
    for entry in registry["candidates"]:
        assert entry["papers"][0]["url"] == expected_papers[entry["resource_id"]]
        assert entry["datasets"]
        assert entry["license_status"] == "code_document_identified_data_and_paper_rights_unknown"
        assert entry["reuse_allowed"] is False
        assert entry["paper_verification"] == "citation_link_in_readme_only_not_scientific_review"
        code_license = entry["code"][0]["license"]
        assert code_license["identifier"] == expected_licenses[entry["resource_id"]]
        assert code_license["document_verification"] == "content_fetched_and_identifier_checked"
        assert code_license["scope"] == "repository_code_document_only"
        assert code_license["reuse_permitted"] is False
        assert len(code_license["sha256"]) == 64
        assert code_license["revision"] in code_license["url"]
        assert entry["upstream_readme"]["revision"] in entry["upstream_readme"]["url"]
        assert len(entry["upstream_readme"]["sha256"]) == 64
        for source in entry["papers"] + entry["datasets"]:
            assert source["license"] is None
            assert source["scientific_review"] == "unverified"
            assert source["link_verification"] == "documented_in_fetched_upstream_readme"
            assert source["provenance_url"] == entry["upstream_readme"]["url"]
        assert not evaluate_science_evidence(entry, review_verifier=lambda _: True)["reuse_allowed"]
    assert registry["collaboration_benchmark"]["status"] == "pending_real_model_run"
    registry["candidates"].clear()
    assert len(get_science_evidence_registry()["candidates"]) == 3


def test_registry_distinguishes_dataset_locations_datalake_docs_and_demonstration_outputs():
    entries = {entry["resource_id"]: entry for entry in get_science_evidence_registry()["candidates"]}
    assert entries["biomni"]["datasets"][0]["url"] == "https://huggingface.co/datasets/biomni/Eval1"
    assert entries["biomni"]["datasets"][1]["artifact_kind"] == "datalake_documentation_not_dataset_snapshot"
    assert "#controlling-datalake-loading" in entries["biomni"]["datasets"][1]["url"]
    assert entries["virtual_lab"]["datasets"][0]["url"] == "https://github.com/zou-group/virtual-lab/tree/main/nanobody_design"
    assert entries["virtual_lab"]["datasets"][0]["artifact_kind"] == "demonstration_outputs_not_independently_reviewed_dataset"
    assert entries["evo2"]["datasets"][0]["url"] == "https://huggingface.co/datasets/arcinstitute/opengenome2"
    assert "NVIDIA" in " ".join(entries["evo2"]["limitations"])
    assert "LICENSE.txt" in " ".join(entries["virtual_lab"]["limitations"])


def test_exact_discovery_events_are_locations_not_verified_event_membership():
    discovery = get_science_evidence_registry()["discovery"]
    assert "https://hai.stanford.edu/events/conference-on-physics-and-ai-pai26" in discovery["event_urls"]
    assert "https://hai.stanford.edu/events/brian-hie-genome-modeling-design-across-all-domains-of-life" in discovery["event_urls"]
    assert discovery["event_location_verification"] == "web_search_index_only"
    assert discovery["event_page_fetch_status"] == "not_fetched_dns_resolution_failed"
    assert discovery["candidate_event_membership"] == "not_asserted"


def test_public_spec_corpus_is_concrete_frozen_and_honest_about_non_holdout_status():
    corpus = get_science_collaboration_benchmark_corpus()
    assert len(corpus["tasks"]) == 5
    assert corpus["expected_answers_public"] is True
    assert corpus["eligible_for_model_benefit_evidence"] is False
    assert corpus["held_out_provenance_verified"] is False
    assert all(task["split"] == "public_example" for task in corpus["tasks"])
    assert corpus["task_manifest_digest"] == science_evidence_digest({
        "tasks": corpus["tasks"], "training_task_ids": corpus["training_task_ids"],
    })
    assert get_science_collaboration_benchmark_spec()["corpus"] == corpus
    corpus["tasks"][0]["expected"] = "tampered"
    assert get_science_collaboration_benchmark_corpus()["tasks"][0]["expected"] == {
        "mean": 5, "population_variance": 5,
    }


def test_public_corpus_executable_only_as_deterministic_non_evidence():
    corpus = get_science_collaboration_benchmark_corpus()
    request = deterministic_fixture_request()
    request.update(
        tasks=corpus["tasks"], training_task_ids=corpus["training_task_ids"],
        frozen_manifest_digest=corpus["task_manifest_digest"],
    )
    for lane in LANES:
        template = deepcopy(request["recorded_outputs"][lane][0])
        request["recorded_outputs"][lane] = []
        for index, task in enumerate(corpus["tasks"]):
            record = deepcopy(template)
            record.update(
                task_id=task["task_id"], task_digest=science_evidence_digest(task),
                output=deepcopy(task["expected"]),
            )
            for participant, execution in enumerate(record["executions"]):
                execution["execution_id"] = f"public-fixture-{lane}-{index}-{participant}"
                execution["artifact_url"] = f"https://example.org/public-fixtures/{lane}/{index}/{participant}"
            request["recorded_outputs"][lane].append(record)
    result = run_science_collaboration_tool(**request)
    assert result["status"] == "completed_deterministic_validation"
    assert result["scores"] == {lane: [1] * 5 for lane in LANES}
    assert result["winner"] is None
    assert result["measured_benefit"] is False
    request["execution_mode"] = "model"
    assert run_collaboration_benchmark(**request, receipt_verifier=lambda _: True)["status"] == "blocked"


def test_registry_integrated_without_replacing_existing_resources():
    from ox_navigator.engine.merlin_program import get_open_science_resource_registry

    registry = get_open_science_resource_registry()
    assert any(resource["resource_id"] == "mlflow" for resource in registry["resources"])
    assert registry["science_evidence"] == get_science_evidence_registry()


def test_existing_registry_http_endpoint_exposes_pending_evidence_policy():
    from browser_contract_helpers import running_server
    from httpx import Client
    from ox_navigator.app.server import serve

    with running_server(lambda: serve(port=0)) as base_url:
        with Client(base_url=base_url.rstrip("/")) as client:
            response = client.get("/api/merlin/open-science-registry")
            assert response.status_code == 200
            payload = response.json()
            assert payload["ok"] is True
            registry = payload["open_science_registry"]
            assert registry["science_evidence"]["automatic_integrations"] is False
            assert registry["science_evidence"]["collaboration_benchmark"]["status"] == "pending_real_model_run"
            spec = registry["science_evidence"]["collaboration_benchmark"]
            assert spec["execution_tool"] == "runMerlinScienceCollaborationBenchmark"
            assert spec["execution_performed"] is False
            assert "intermediate_model_calls" in spec["budget_policy"]["includes"]
            invocation = client.post("/api/agentInvoke", json={
                "tool": spec["execution_tool"], "args": {},
            })
            assert invocation.status_code == 200
            assert invocation.json()["ok"] is True
            assert invocation.json()["result"]["data"] == spec
            deterministic = client.post("/api/agentInvoke", json={
                "tool": spec["execution_tool"], "args": deterministic_fixture_request(),
            })
            assert deterministic.status_code == 200
            benchmark = deterministic.json()["result"]["data"]
            assert benchmark["status"] == "completed_deterministic_validation"
            assert benchmark["model_invocation_performed"] is False
            assert benchmark["winner"] is None


def test_pending_benchmark_tools_discoverable_and_do_not_execute_models():
    from ox_navigator.engine.merlin_tools import get_toolkit_view, route_tool

    spec = get_science_collaboration_benchmark_spec()
    for tool in (spec["spec_tool"], spec["execution_tool"]):
        assert "error" not in get_toolkit_view("tool", tool=tool)
        result = route_tool(tool, {})
        assert result["ok"] is True
        assert result["result"]["data"] == spec
        assert result["result"]["data"]["model_invocation_performed"] is False


def test_deterministic_tool_evaluates_frozen_records_without_claiming_model_benefit():
    from ox_navigator.engine.merlin_tools import route_tool

    result = route_tool("runMerlinScienceCollaborationBenchmark", deterministic_fixture_request())
    assert result["ok"] is True
    benchmark = result["result"]["data"]
    assert benchmark["status"] == "completed_deterministic_validation"
    assert benchmark["scores"]["collaboration"] == [1, 1]
    assert benchmark["winner"] is None
    assert benchmark["measured_benefit"] is False
    assert benchmark["model_invocation_performed"] is False
    assert benchmark["receipts_independently_verified"] is False
    assert benchmark["held_out_provenance_verified"] is False
    assert benchmark["comparison_kind"] == "deterministic_surrogates"


def test_tool_rejects_self_supplied_verifiers_and_unverified_model_receipts():
    from ox_navigator.engine.merlin_tools import route_tool

    request = fixture_request()
    result = route_tool("runMerlinScienceCollaborationBenchmark", request)
    assert result["ok"] is True
    assert result["result"]["data"]["status"] == "blocked"
    request["receipt_verifier"] = True
    assert route_tool("runMerlinScienceCollaborationBenchmark", request)["ok"] is False
    assert run_science_collaboration_tool(**request)["status"] == "blocked"
    request["receipt_verifier"] = lambda _: True
    assert run_science_collaboration_tool(**request)["status"] == "blocked"
    assert run_science_collaboration_tool(tasks=[])["status"] == "blocked"


@pytest.mark.parametrize("change", [
    lambda r: r.pop("frozen_manifest_digest"),
    lambda r: r.update(frozen_manifest_digest="changed"),
    lambda r: r["tasks"][0].update(expected="tampered"),
    lambda r: r["recorded_outputs"]["llm"][0]["executions"][0].update(execution_mode="recorded"),
    lambda r: r["recorded_outputs"]["llm"][0]["executions"][0].update(kind="model"),
])
def test_deterministic_evaluation_rejects_changed_tasks_or_model_impersonation(change):
    request = deterministic_fixture_request()
    change(request)
    assert run_science_collaboration_tool(**request)["status"] == "blocked"


def test_deterministic_callbacks_optional_and_cannot_promote_expansion():
    request = deterministic_fixture_request()
    records = request.pop("recorded_outputs")
    result = run_collaboration_benchmark(
        **request,
        callbacks={
            lane: lambda packet, lane=lane: next(
                record for record in records[lane] if record["task_id"] == packet["task_id"]
            )
            for lane in LANES
        },
    )
    assert result["status"] == "completed_deterministic_validation"
    assert result["evaluation_transport"] == "callbacks"
    assert result["model_invocation_performed"] is False
    fixture = expansion_fixture()
    fixture["benchmark_request"] = deterministic_fixture_request()
    assert evaluate_science_expansion(**fixture)["expansion_allowed"] is False


def test_intermediate_calls_count_toward_total_allocations_and_usage():
    request = fixture_request()
    for record in request["recorded_outputs"]["collaboration"]:
        model = record["executions"][1]
        model["budget"] = budget(25, 1, 2.5, .25)
        intermediate = deepcopy(model)
        intermediate["execution_id"] += "-intermediate"
        intermediate["artifact_url"] += "/intermediate"
        record["executions"].append(intermediate)
    result = run_collaboration_benchmark(**request, receipt_verifier=artifact_store_verifier(request))
    assert result["status"] == "completed_verified_runs"
    accounting = result["execution_accounting"]["collaboration"][0]
    assert len(accounting["executions"]) == 3
    assert accounting["total_allocated"] == budget()
    assert accounting["total_usage"] == budget(30, 3, 3, .3)
    assert result["evaluation_transport"] == "recorded_outputs"
    assert result["model_invocation_performed"] is False
    request["recorded_outputs"]["collaboration"][0]["executions"][-1]["budget"]["tokens"] += 1
    assert run_collaboration_benchmark(
        **request, receipt_verifier=artifact_store_verifier(request),
    )["status"] == "blocked"


@pytest.mark.parametrize("label", ["live", "recorded", "deterministic", None, "fake"])
def test_model_execution_modes_are_explicit_and_deterministic_is_not_a_model(label):
    request = fixture_request()
    for record in request["recorded_outputs"]["llm"]:
        record["executions"][0]["execution_mode"] = label
    result = run_collaboration_benchmark(**request, receipt_verifier=artifact_store_verifier(request))
    assert result["status"] == ("completed_verified_runs" if label in ("live", "recorded") else "blocked")


def test_live_callback_model_invocation_distinguished_from_record_replay():
    request = fixture_request()
    for records in request["recorded_outputs"].values():
        for record in records:
            record["origin"] = "callback"
            for execution in record["executions"]:
                execution["execution_mode"] = "live"
    verifier = artifact_store_verifier(request)
    records = request.pop("recorded_outputs")
    callbacks = {
        lane: lambda packet, lane=lane: next(
            record for record in records[lane] if record["task_id"] == packet["task_id"]
        )
        for lane in LANES
    }
    live = run_collaboration_benchmark(**request, callbacks=callbacks, receipt_verifier=verifier)
    assert live["model_invocation_performed"] is None
    assert live["live_model_receipts_present"] is True
    replay = run_collaboration_benchmark(**request, recorded_outputs=records, receipt_verifier=verifier)
    assert replay["model_invocation_performed"] is False


def test_evidence_requires_independent_rights_and_provenance_review():
    evidence = evidence_fixture()
    assert evaluate_science_evidence(evidence)["reuse_allowed"] is False
    fixture = expansion_fixture()
    approved = evaluate_science_evidence(evidence, review_verifier=fixture["review_verifier"])
    assert approved["reuse_allowed"] is True
    assert approved["canonical_truth"] is approved["automatic_integration"] is False


@pytest.mark.parametrize("url", [
    "https://hai.stanford.edu.evil.org/news/fixture",
    "https://evil.org/?hai.stanford.edu",
    "https://hai.stanford.edu@evil.org/",
    "http://hai.stanford.edu/", "https://hai.stanford.edu:444/",
    "https://hai.stanford.edu:bad/", None, 1,
])
def test_only_stanford_hai_discovery(url):
    evidence = evidence_fixture()
    evidence["discovery_url"] = url
    assert evaluate_science_evidence(evidence, review_verifier=lambda _: True)["status"] == "blocked"


@pytest.mark.parametrize("category", ["papers", "code", "datasets"])
@pytest.mark.parametrize("license", [
    None, {}, "MIT", {"identifier": "unknown"},
    {"identifier": " Unknown ", "url": "https://example.org/license", "reuse_permitted": True, "review_id": "fixture"},
])
def test_unknown_license_always_blocks_reuse(category, license):
    evidence = evidence_fixture()
    evidence[category][0]["license"] = license
    assert not evaluate_science_evidence(evidence, review_verifier=lambda _: True)["reuse_allowed"]


@pytest.mark.parametrize("change", [
    lambda record: record.update(canonical_truth=True),
    lambda record: record.pop("canonical_truth"),
    lambda record: record.update(limitations=[]),
    lambda record: record.update(papers=[]),
    lambda record: record["code"][0].update(revision=""),
    lambda record: record["datasets"][0].update(provenance_url=""),
    lambda record: record["papers"][0]["license"].update(reuse_permitted=False),
    lambda record: record["code"][0]["license"].update(identifier="unknown"),
    lambda record: record["code"][0]["license"].update(url="file:///license"),
    lambda record: record.update(unrelated=float("nan")),
])
def test_evidence_missing_or_nonfinite_data_fails_closed(change):
    evidence = evidence_fixture()
    change(evidence)
    assert evaluate_science_evidence(evidence, review_verifier=lambda _: True)["status"] == "blocked"


@pytest.mark.parametrize("malformed", [None, [], 1, {"code": [None]}, {"x": object()}])
def test_malformed_evidence_fails_closed(malformed):
    assert evaluate_science_evidence(malformed)["status"] == "blocked"


def test_pending_without_model_runs_and_never_fake_llm_win():
    request = fixture_request()
    request.pop("recorded_outputs")
    result = run_collaboration_benchmark(**request)
    assert result["status"] == "pending_real_model_run"
    assert result["winner"] is None
    assert result["measured_benefit"] is False


def test_real_recorded_transport_scores_objectively_and_preserves_inputs():
    request = fixture_request()
    before = deepcopy(request)
    result = run_collaboration_benchmark(**request, receipt_verifier=artifact_store_verifier(request))
    assert result["status"] == "completed_verified_runs"
    assert result["scores"] == {"merlin": [0, 0], "llm": [0, 0], "collaboration": [1, 1]}
    assert result["paired_mean_gain"] == {"merlin": 1, "llm": 1}
    assert result["winner"] == "collaboration"
    assert result["scientific_truth_established"] is result["automatic_integration"] is False
    assert request == before


def test_callbacks_receive_no_answers_and_require_verified_artifacts():
    request = fixture_request()
    verifier = artifact_store_verifier(request)
    records = request.pop("recorded_outputs")
    calls = []

    def runner(lane):
        def execute(packet):
            assert "expected" not in packet
            assert set(packet) == {"task_id", "prompt", "task_digest", "lane", "total_budget"}
            calls.append((lane, packet["task_id"]))
            return next(record for record in records[lane] if record["task_id"] == packet["task_id"])
        return execute

    result = run_collaboration_benchmark(
        **request, callbacks={lane: runner(lane) for lane in LANES}, receipt_verifier=verifier,
    )
    assert result["status"] == "completed_verified_runs"
    assert len(calls) == 6
    assert len(set(calls)) == 6
    assert run_collaboration_benchmark(
        **request, callbacks={lane: runner(lane) for lane in LANES},
    )["status"] == "blocked"


@pytest.mark.parametrize("lane", ["merlin", "llm"])
def test_no_benefit_if_collaboration_does_not_beat_both_baselines(lane):
    request = fixture_request()
    for index, record in enumerate(request["recorded_outputs"][lane]):
        record["output"] = deepcopy(request["tasks"][index]["expected"])
    result = run_collaboration_benchmark(**request, receipt_verifier=artifact_store_verifier(request))
    assert result["status"] == "completed_verified_runs"
    assert result["measured_benefit"] is False
    assert result["winner"] is None


def test_paired_scores_ignore_self_reported_scores_and_distinguish_boolean_from_integer():
    request = fixture_request()
    for record in request["recorded_outputs"]["collaboration"]:
        record["score"] = 1
        record["output"] = {"answer": False}
    result = run_collaboration_benchmark(**request, receipt_verifier=artifact_store_verifier(request))
    assert result["scores"]["collaboration"] == [0, 0]
    assert result["measured_benefit"] is False


@pytest.mark.parametrize("field", ["tokens", "tool_calls", "seconds", "cost"])
def test_total_budget_comparison_includes_all_dimensions(field):
    request = fixture_request()
    request["budgets"]["collaboration"][field] += 1
    assert run_collaboration_benchmark(**request)["status"] == "blocked"


@pytest.mark.parametrize("field", ["tokens", "tool_calls", "seconds", "cost"])
def test_collaboration_must_sum_all_participant_allocations(field):
    request = fixture_request()
    request["recorded_outputs"]["collaboration"][0]["executions"][1]["budget"][field] += 1
    result = run_collaboration_benchmark(**request, receipt_verifier=artifact_store_verifier(request))
    assert result["status"] == "blocked"
    assert "TOTAL" in result["reasons"][0]


def test_tiny_fractional_budget_difference_is_not_hidden_by_tolerance():
    request = fixture_request()
    request["recorded_outputs"]["collaboration"][0]["executions"][1]["budget"]["cost"] += 1e-10
    result = run_collaboration_benchmark(**request, receipt_verifier=artifact_store_verifier(request))
    assert result["status"] == "blocked"


def test_large_integer_allocations_are_compared_without_float_rounding():
    request = fixture_request()
    tokens = 2**54
    for lane in LANES:
        request["budgets"][lane]["tokens"] = tokens
        for record in request["recorded_outputs"][lane]:
            for execution in record["executions"]:
                execution["budget"]["tokens"] = tokens // len(record["executions"])
    request["recorded_outputs"]["llm"][0]["executions"][0]["budget"]["tokens"] += 1
    result = run_collaboration_benchmark(**request, receipt_verifier=artifact_store_verifier(request))
    assert result["status"] == "blocked"


def test_decimal_participant_allocations_sum_to_same_declared_total():
    request = fixture_request()
    for lane in LANES:
        request["budgets"][lane]["cost"] = .3
        for record in request["recorded_outputs"][lane]:
            for index, execution in enumerate(record["executions"]):
                execution["budget"]["cost"] = (.1 if index == 0 else .2) if lane == "collaboration" else .3
    result = run_collaboration_benchmark(**request, receipt_verifier=artifact_store_verifier(request))
    assert result["status"] == "completed_verified_runs"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, True, "10", None])
@pytest.mark.parametrize("location", ["budget", "usage", "task", "output"])
def test_nonfinite_and_malformed_benchmark_data_fails_closed(location, value):
    request = fixture_request()
    if location == "budget":
        request["budgets"]["llm"]["tokens"] = value
    elif location == "usage":
        request["recorded_outputs"]["llm"][0]["executions"][0]["usage"]["tokens"] = value
    elif location == "task":
        request["tasks"][0]["task_id"] = value
    else:
        request["recorded_outputs"]["llm"][0]["output"] = {"answer": value}
        # Finite, valid JSON answers remain scoreable (not metadata or budget numbers).
        if value not in (float("inf"),) and value == value:
            result = run_collaboration_benchmark(**request, receipt_verifier=artifact_store_verifier(request))
            assert result["status"] == "completed_verified_runs"
            return
    assert run_collaboration_benchmark(**request, receipt_verifier=lambda _: True)["status"] == "blocked"


@pytest.mark.parametrize("change", [
    lambda r: r["tasks"].clear(),
    lambda r: r["tasks"][0].update(split="training"),
    lambda r: r["tasks"][0].update(provenance_url=""),
    lambda r: r["tasks"][0].pop("expected"),
    lambda r: r["tasks"][0].pop("holdout_review_id"),
    lambda r: r["tasks"][1].update(task_id=r["tasks"][0]["task_id"]),
    lambda r: r["training_task_ids"].append(r["tasks"][0]["task_id"]),
    lambda r: r.update(training_task_ids=None),
    lambda r: r["recorded_outputs"].pop("llm"),
    lambda r: r["recorded_outputs"]["llm"].pop(),
    lambda r: r["recorded_outputs"]["llm"][0].update(origin="synthetic"),
    lambda r: r["recorded_outputs"]["llm"][0].update(task_digest="fake"),
    lambda r: r["recorded_outputs"]["llm"][0].update(lane="merlin"),
    lambda r: r["recorded_outputs"]["llm"][0].update(complete_execution_accounting=False),
    lambda r: r["recorded_outputs"]["llm"][0].pop("output"),
    lambda r: r["recorded_outputs"]["llm"][0].update(executions=[]),
    lambda r: r["recorded_outputs"]["llm"][0]["executions"][0].update(model_revision=""),
    lambda r: r["recorded_outputs"]["llm"][0]["executions"][0].update(artifact_url=""),
    lambda r: r["recorded_outputs"]["llm"][0]["executions"][0]["usage"].update(tokens=0),
    lambda r: r["recorded_outputs"]["merlin"][0]["executions"][0]["usage"].update(seconds=0),
    lambda r: r["recorded_outputs"]["llm"][0]["executions"][0]["usage"].update(tokens=101),
    lambda r: r["recorded_outputs"]["merlin"][0]["executions"][0].update(kind="model"),
    lambda r: r["recorded_outputs"]["collaboration"][0]["executions"][1].update(kind="tool"),
    lambda r: r["recorded_outputs"]["llm"][1]["executions"][0].update(execution_id="fixture-llm-0-0"),
    lambda r: r["recorded_outputs"]["llm"][1]["executions"][0].update(
        artifact_url="https://example.org/fixtures/llm/0/0"),
])
def test_invalid_heldout_protocol_or_execution_receipts_rejected(change):
    request = fixture_request()
    change(request)
    result = run_collaboration_benchmark(**request, receipt_verifier=lambda _: True)
    assert result["status"] == "blocked"
    assert result["winner"] is None


def test_fake_or_tampered_receipts_fail_independent_verification():
    request = fixture_request()
    verifier = artifact_store_verifier(request)
    request["recorded_outputs"]["llm"][0]["output"] = {"answer": 0}
    request["recorded_outputs"]["llm"][0]["verified"] = True
    assert run_collaboration_benchmark(**request, receipt_verifier=verifier)["status"] == "blocked"
    assert run_collaboration_benchmark(**request)["status"] == "blocked"


@pytest.mark.parametrize("verifier", [
    lambda _: False, lambda _: 1, lambda _: {"verified": True},
    lambda _: (_ for _ in ()).throw(RuntimeError("fixture verifier failure")),
])
def test_verifier_must_explicitly_confirm_and_failures_close_gate(verifier):
    assert run_collaboration_benchmark(**fixture_request(), receipt_verifier=verifier)["status"] == "blocked"
    assert evaluate_science_evidence(evidence_fixture(), review_verifier=verifier)["status"] == "blocked"


def test_callback_exception_is_not_a_completed_model_run():
    request = fixture_request()
    verifier = artifact_store_verifier(request)
    request.pop("recorded_outputs")
    result = run_collaboration_benchmark(
        **request, receipt_verifier=verifier,
        callbacks={lane: lambda _: (_ for _ in ()).throw(RuntimeError("no model")) for lane in LANES},
    )
    assert result["status"] == "blocked"
    assert result["winner"] is None


def test_expansion_gates_replay_verified_measurement_and_human_approval():
    fixture = expansion_fixture()
    result = evaluate_science_expansion(**fixture)
    assert result["status"] == "eligible_for_human_directed_expansion"
    assert result["expansion_allowed"] is True
    assert result["automatic_integration"] is result["canonical_truth"] is False
    assert evaluate_science_expansion(**fixture, minimum_gain=1)["expansion_allowed"] is False


@pytest.mark.parametrize("change", [
    lambda f: f.update(receipt_verifier=None),
    lambda f: f.update(review_verifier=None),
    lambda f: f["evidence"]["code"][0].update(license=None),
    lambda f: f["evidence"].update(canonical_truth=True),
    lambda f: f["benchmark_request"].update(recorded_outputs=None),
    lambda f: f["benchmark_request"].update(winner="collaboration", measured_benefit=True),
    lambda f: f["hardware"].update(available_memory_gb=1),
    lambda f: f["hardware"].update(available_seconds=1),
    lambda f: f["hardware"].update(required_memory_gb=float("nan")),
    lambda f: f["hardware"].update(available_memory_gb=float("inf")),
    lambda f: f["hardware"].update(required_memory_gb=-1),
    lambda f: f["hardware"].update(assessment_id=""),
    lambda f: f["hardware"].update(resource_id="different-candidate"),
    lambda f: f["human_approval"].update(actor_type="ai"),
    lambda f: f["human_approval"].update(approved=False),
    lambda f: f["human_approval"].update(approved=1),
    lambda f: f["human_approval"].update(actor_id=""),
    lambda f: f["human_approval"].update(approval_id=""),
    lambda f: f["human_approval"].update(benchmark_digest="fake"),
    lambda f: f["human_approval"].update(evidence_digest="fake"),
    lambda f: f["human_approval"].update(hardware_digest="fake"),
    lambda f: f["human_approval"].update(resource_id="different-candidate"),
])
def test_expansion_fails_closed_on_missing_gates_or_fake_claims(change):
    fixture = expansion_fixture()
    change(fixture)
    result = evaluate_science_expansion(**fixture)
    assert result["status"] == "blocked"
    assert result["expansion_allowed"] is False
    assert result["automatic_integration"] is False


@pytest.mark.parametrize("minimum_gain", [float("nan"), float("inf"), -1, True, None, "1"])
def test_expansion_threshold_must_be_finite_nonnegative(minimum_gain):
    assert not evaluate_science_expansion(**expansion_fixture(), minimum_gain=minimum_gain)["expansion_allowed"]


def test_gate_does_not_trust_forged_benchmark_summary():
    fixture = expansion_fixture()
    fixture["benchmark_request"] = {
        "status": "completed_verified_runs", "winner": "collaboration",
        "measured_benefit": True, "paired_mean_gain": {"merlin": 1, "llm": 1},
        "benchmark_digest": fixture["human_approval"]["benchmark_digest"],
    }
    assert not evaluate_science_expansion(**fixture)["expansion_allowed"]


def test_pending_model_run_never_opens_expansion():
    fixture = expansion_fixture()
    fixture["benchmark_request"]["recorded_outputs"] = None
    result = evaluate_science_expansion(**fixture)
    assert result["benchmark"]["status"] == "pending_real_model_run"
    assert result["expansion_allowed"] is False


def test_verifiers_cannot_mutate_what_is_scored():
    request = fixture_request()

    def mutating_verifier(packet):
        if packet["kind"] == "execution_receipt":
            packet["record"]["output"] = {"answer": 1000}
        return True

    assert run_collaboration_benchmark(**request, receipt_verifier=mutating_verifier)["scores"]["collaboration"] == [1, 1]
