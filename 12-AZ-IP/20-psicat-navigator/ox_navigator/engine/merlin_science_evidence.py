# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""External science intake and replayable, human-gated collaboration evaluation.

No network requests, model invocation defaults, downloads, or integrations occur
here. Verifiers are a caller-supplied trust boundary: they must check an actual
artifact/review store, not accept a receipt's self-declared ``verified`` flag.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import math
from typing import Any
from urllib.parse import urlsplit


LANES = ("merlin", "llm", "collaboration")
BUDGET_FIELDS = ("tokens", "tool_calls", "seconds", "cost")
VERIFIED_CODE_LOCATIONS = {
    "biomni": "https://github.com/snap-stanford/Biomni",
    "virtual_lab": "https://github.com/zou-group/virtual-lab",
    "evo2": "https://github.com/ArcInstitute/evo2",
}
Verifier = Callable[[dict[str, Any]], bool]


def _json_value(value: Any) -> None:
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float and math.isfinite(value):
        return
    if type(value) is list:
        for item in value:
            _json_value(item)
        return
    if type(value) is dict and all(type(key) is str for key in value):
        for item in value.values():
            _json_value(item)
        return
    raise ValueError("Expected finite JSON data.")


def _digest(value: Any) -> str:
    _json_value(value)
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def science_evidence_digest(value: Any) -> str:
    """Stable SHA-256 binding for tasks, execution artifacts, and human reviews."""
    return _digest(value)


def _text(value: Any) -> bool:
    return type(value) is str and bool(value.strip())


def _https(value: Any, host: str | None = None) -> bool:
    if not _text(value):
        return False
    try:
        url = urlsplit(value)
        return (
            url.scheme == "https"
            and bool(url.hostname)
            and url.username is None
            and url.password is None
            and url.port in (None, 443)
            and (host is None or url.hostname == host)
            and not any(char.isspace() for char in value)
        )
    except ValueError:
        return False


def _verified(verifier: Verifier | None, record: dict[str, Any]) -> bool:
    if not callable(verifier):
        return False
    try:
        return verifier(deepcopy(record)) is True
    except Exception:
        return False


def get_science_evidence_registry() -> dict[str, Any]:
    """Expose discovery candidates without inventing paper or license checks."""
    return {
        "discovery": {
            "url": "https://hai.stanford.edu/",
            "role": "discovery_only",
            "policy": "Follow primary papers, code, datasets, licenses, and limitations; HAI is not scientific verification.",
        },
        "external_evidence_is_canonical_truth": False,
        "automatic_integrations": False,
        "candidates": [
            {
                "resource_id": resource_id,
                "code": [{"url": url, "verification": "location_only", "license": None}],
                "papers": [],
                "datasets": [],
                "discovery_article": None,
                "license_status": "unknown",
                "reuse_allowed": False,
                "paper_verification": "not_performed",
                "limitations": [
                    "Primary paper, dataset, and license reviews are pending.",
                    "A repository location is not a capability, safety, or scientific-validity receipt.",
                ],
                "status": "discovery_candidate",
            }
            for resource_id, url in VERIFIED_CODE_LOCATIONS.items()
        ],
        "collaboration_benchmark": {
            "status": "pending_real_model_run",
            "lanes": list(LANES),
            "scoring": "held_out_exact_json_match",
            "budget_policy": "Equal TOTAL allocation per task in every lane, summed over every participant, retry, and tool.",
            "receipt_policy": "Independent artifact verification required; no self-attested or synthetic LLM wins.",
            "winner": None,
        },
        "expansion_gates": [
            "measured_paired_benefit",
            "verified_rights_and_provenance",
            "verified_hardware_capacity",
            "human_approval_bound_to_benchmark",
        ],
    }


def evaluate_science_evidence(
    record: dict[str, Any], *, review_verifier: Verifier | None = None
) -> dict[str, Any]:
    """Fail closed for incomplete metadata or unverified, artifact-specific rights."""
    reasons: list[str] = []
    try:
        _json_value(record)
        if type(record) is not dict:
            raise ValueError("Evidence must be an object.")
        if not _text(record.get("resource_id")):
            reasons.append("missing_resource_id")
        if not _https(record.get("discovery_url"), "hai.stanford.edu"):
            reasons.append("stanford_hai_discovery_required")
        if record.get("canonical_truth") is not False:
            reasons.append("external_evidence_never_canonical")
        limitations = record.get("limitations")
        if type(limitations) is not list or not limitations or not all(map(_text, limitations)):
            reasons.append("explicit_limitations_required")
        for category in ("papers", "code", "datasets"):
            sources = record.get(category)
            if type(sources) is not list or not sources:
                reasons.append(f"{category}_primary_links_required")
                continue
            for source in sources:
                if type(source) is not dict or not _https(source.get("url")):
                    reasons.append(f"{category}_invalid_source")
                    continue
                if not _text(source.get("revision")) or not _https(source.get("provenance_url")):
                    reasons.append(f"{category}_missing_provenance")
                license_review = source.get("license")
                if (
                    type(license_review) is not dict
                    or not _text(license_review.get("identifier"))
                    or license_review.get("identifier", "").strip().casefold() in (
                        "unknown", "pending", "unverified", "none", "unlicensed",
                    )
                    or not _https(license_review.get("url"))
                    or license_review.get("reuse_permitted") is not True
                    or not _text(license_review.get("review_id"))
                ):
                    reasons.append(f"{category}_unknown_or_restricted_license")
                elif not _verified(review_verifier, {
                    "kind": "source_rights_and_provenance",
                    "resource_id": record.get("resource_id"),
                    "category": category,
                    "source": source,
                }):
                    reasons.append(f"{category}_unverified_rights_or_provenance")
    except (ValueError, TypeError, OverflowError, RecursionError):
        reasons.append("malformed_or_nonfinite_evidence")
    return {
        "status": "reviewed_external_evidence" if not reasons else "blocked",
        "reuse_allowed": not reasons,
        "canonical_truth": False,
        "automatic_integration": False,
        "reasons": sorted(set(reasons)),
    }


def _budget(value: Any) -> dict[str, int | float]:
    if type(value) is not dict or set(value) != set(BUDGET_FIELDS):
        raise ValueError("All TOTAL budget dimensions are required.")
    for key, number in value.items():
        if type(number) not in (int, float) or not math.isfinite(number) or number < 0:
            raise ValueError("Budgets and usage must be finite nonnegative numbers.")
        if key in ("tokens", "tool_calls") and type(number) is not int:
            raise ValueError("Token and tool counts must be integers.")
    return value


def _tasks(tasks: Any, training_task_ids: Any) -> list[dict[str, Any]]:
    _json_value(tasks)
    if type(training_task_ids) is not list or not all(map(_text, training_task_ids)):
        raise ValueError("Training task IDs must be explicit.")
    if type(tasks) is not list or not tasks:
        raise ValueError("Nonempty held-out task set required.")
    seen: set[str] = set()
    for task in tasks:
        if type(task) is not dict:
            raise ValueError("Task must be an object.")
        task_id = task.get("task_id")
        if not _text(task_id) or task_id in seen or task_id in training_task_ids:
            raise ValueError("Duplicate or contaminated held-out task.")
        if (
            task.get("split") != "held_out"
            or not _text(task.get("prompt"))
            or "expected" not in task
            or not _https(task.get("provenance_url"))
            or not _text(task.get("holdout_review_id"))
        ):
            raise ValueError("Held-out task provenance and objective answer required.")
        seen.add(task_id)
    return tasks


def _validate_run(
    record: Any, task: dict[str, Any], lane: str, budget: dict[str, Any],
    verifier: Verifier | None,
) -> tuple[Any, str, bool]:
    _json_value(record)
    if type(record) is not dict or "output" not in record:
        raise ValueError("Recorded output required; scores alone are not evidence.")
    if record.get("task_id") != task["task_id"] or record.get("lane") != lane:
        raise ValueError("Receipt task/lane mismatch.")
    if record.get("task_digest") != _digest(task):
        raise ValueError("Receipt must bind the complete held-out task.")
    if record.get("origin") not in ("recorded", "callback"):
        raise ValueError("Synthetic runs cannot establish benefit.")
    if record.get("complete_execution_accounting") is not True:
        raise ValueError("All participants, retries, and tools must be accounted for.")
    executions = record.get("executions")
    if type(executions) is not list or not executions:
        raise ValueError("Execution provenance required.")
    totals = {key: Fraction(0) for key in BUDGET_FIELDS}
    has_model = False
    has_merlin = False
    ids: set[str] = set()
    for execution in executions:
        if type(execution) is not dict:
            raise ValueError("Execution must be an object.")
        execution_id = execution.get("execution_id")
        if not _text(execution_id) or execution_id in ids:
            raise ValueError("Unique execution IDs required.")
        ids.add(execution_id)
        if (
            not _text(execution.get("system_id"))
            or not _https(execution.get("artifact_url"))
            or execution.get("kind") not in ("model", "merlin", "tool")
        ):
            raise ValueError("Execution identity and artifact provenance required.")
        if execution["kind"] == "model":
            if not _text(execution.get("model_revision")):
                raise ValueError("Real model revision required.")
            has_model = True
        has_merlin |= execution["kind"] == "merlin"
        allocation = _budget(execution.get("budget"))
        usage = _budget(execution.get("usage"))
        if execution["kind"] == "model" and (usage["tokens"] <= 0 or usage["seconds"] <= 0):
            raise ValueError("Model receipt requires actual inference usage.")
        if execution["kind"] == "merlin" and usage["seconds"] <= 0:
            raise ValueError("Merlin receipt requires actual execution usage.")
        for key in BUDGET_FIELDS:
            if usage[key] > allocation[key]:
                raise ValueError("Execution exceeded allocated budget.")
            totals[key] += Fraction(str(allocation[key]))
    if any(totals[key] != Fraction(str(budget[key])) for key in BUDGET_FIELDS):
        raise ValueError("Unequal TOTAL budgets across lanes.")
    if lane == "merlin" and (not has_merlin or has_model):
        raise ValueError("Merlin baseline must not contain an LLM.")
    if lane == "llm" and (not has_model or has_merlin):
        raise ValueError("LLM baseline must be standalone.")
    if lane == "collaboration" and not (has_model and has_merlin):
        raise ValueError("Collaboration requires both Merlin and an actual model.")
    receipt_id = _digest(record)
    if not _verified(verifier, {"kind": "execution_receipt", "receipt_id": receipt_id, "record": record}):
        raise ValueError("Independent artifact verification failed.")
    return record["output"], receipt_id, has_model


def run_collaboration_benchmark(
    *,
    tasks: list[dict[str, Any]],
    budgets: dict[str, dict[str, int | float]],
    training_task_ids: list[str],
    recorded_outputs: dict[str, list[dict[str, Any]]] | None = None,
    callbacks: Mapping[str, Callable[[dict[str, Any]], dict[str, Any]]] | None = None,
    receipt_verifier: Verifier | None = None,
) -> dict[str, Any]:
    """Score paired outputs; callbacks receive prompts, never held-out answers.

    A trusted receipt verifier must independently check execution artifacts AND
    held-out provenance. Callbacks are transport, not proof of real inference.
    Unequal allocations, partial lanes, and unverifiable receipts block results.
    """
    blocked = {"status": "blocked", "winner": None, "measured_benefit": False}
    try:
        tasks = deepcopy(_tasks(tasks, training_task_ids))
        _json_value(budgets)
        if type(budgets) is not dict or set(budgets) != set(LANES):
            raise ValueError("All three lanes require budgets.")
        common = _budget(budgets["merlin"])
        if any(_budget(budgets[lane]) != common for lane in LANES):
            raise ValueError("Unequal TOTAL budgets across lanes.")
        if common["tokens"] <= 0 or common["seconds"] <= 0:
            raise ValueError("Positive token/time allocations required.")
        manifest_digest = _digest({"tasks": tasks, "training_task_ids": training_task_ids})
        if recorded_outputs is None and callbacks is None:
            return {
                "status": "pending_real_model_run", "winner": None,
                "measured_benefit": False, "task_manifest_digest": manifest_digest,
            }
        if (recorded_outputs is None) == (callbacks is None):
            raise ValueError("Choose recorded outputs OR callbacks, never both.")
        if not _verified(receipt_verifier, {
            "kind": "held_out_manifest", "manifest_digest": manifest_digest,
            "tasks": tasks, "training_task_ids": training_task_ids,
        }):
            raise ValueError("Held-out provenance not independently verified.")
        source = recorded_outputs if recorded_outputs is not None else callbacks
        if not isinstance(source, Mapping) or set(source) != set(LANES):
            raise ValueError("Complete paired lanes required.")
        outputs: dict[str, list[dict[str, Any]]] = {}
        for lane in LANES:
            if callbacks is not None:
                if not callable(callbacks[lane]):
                    raise ValueError("Every lane requires a callback.")
                outputs[lane] = [
                    callbacks[lane]({
                        "task_id": task["task_id"], "prompt": task["prompt"],
                        "task_digest": _digest(task), "lane": lane,
                        "total_budget": deepcopy(common),
                    })
                    for task in tasks
                ]
            else:
                outputs[lane] = deepcopy(recorded_outputs[lane])
            if type(outputs[lane]) is not list or len(outputs[lane]) != len(tasks):
                raise ValueError("Missing or extra task outputs.")
        scores: dict[str, list[int]] = {lane: [] for lane in LANES}
        receipts: dict[str, list[str]] = {lane: [] for lane in LANES}
        all_execution_ids: set[str] = set()
        all_artifact_urls: set[str] = set()
        for index, task in enumerate(tasks):
            for lane in LANES:
                record = outputs[lane][index]
                output, receipt_id, _ = _validate_run(record, task, lane, common, receipt_verifier)
                execution_ids = {execution["execution_id"] for execution in record["executions"]}
                if execution_ids & all_execution_ids:
                    raise ValueError("Replayed execution artifact across task/lane.")
                all_execution_ids.update(execution_ids)
                artifact_urls = [execution["artifact_url"] for execution in record["executions"]]
                if len(set(artifact_urls)) != len(artifact_urls) or set(artifact_urls) & all_artifact_urls:
                    raise ValueError("Replayed execution artifact URL across task/lane.")
                all_artifact_urls.update(artifact_urls)
                scores[lane].append(int(_digest(output) == _digest(task["expected"])))
                receipts[lane].append(receipt_id)
        means = {lane: sum(scores[lane]) / len(tasks) for lane in LANES}
        deltas = {
            lane: [
                paired - baseline for paired, baseline in zip(scores["collaboration"], scores[lane])
            ]
            for lane in ("merlin", "llm")
        }
        gains = {lane: sum(values) / len(tasks) for lane, values in deltas.items()}
        benefit = all(value > 0 for value in gains.values())
        result = {
            "status": "completed_verified_runs",
            "winner": "collaboration" if benefit else None,
            "measured_benefit": benefit,
            "scientific_truth_established": False,
            "automatic_integration": False,
            "scoring": "held_out_exact_json_match",
            "task_manifest_digest": manifest_digest,
            "task_count": len(tasks),
            "total_budget_per_task": deepcopy(common),
            "scores": scores, "mean_scores": means,
            "paired_deltas": deltas, "paired_mean_gain": gains,
            "receipt_ids": receipts,
            "limitations": ["Benefit is confined to these tasks and budgets; it is not a general LLM superiority claim."],
        }
        result["benchmark_digest"] = _digest(result)
        return result
    except Exception as exc:
        return {**blocked, "reasons": [str(exc) or "invalid_benchmark"]}


def evaluate_science_expansion(
    *,
    evidence: dict[str, Any],
    benchmark_request: dict[str, Any],
    hardware: dict[str, Any],
    human_approval: dict[str, Any],
    receipt_verifier: Verifier | None = None,
    review_verifier: Verifier | None = None,
    minimum_gain: float = 0.0,
) -> dict[str, Any]:
    """Recompute evidence, never promote from a supplied score/winner flag."""
    reasons: list[str] = []
    benchmark: dict[str, Any] = {}
    try:
        if type(minimum_gain) not in (int, float) or not math.isfinite(minimum_gain) or minimum_gain < 0:
            raise ValueError("Invalid measured benefit threshold.")
        if not evaluate_science_evidence(evidence, review_verifier=review_verifier)["reuse_allowed"]:
            reasons.append("rights_or_provenance_blocked")
        if type(benchmark_request) is not dict or "callbacks" in benchmark_request:
            raise ValueError("Expansion needs replayable recorded receipts, not new callbacks.")
        benchmark = run_collaboration_benchmark(**benchmark_request, receipt_verifier=receipt_verifier)
        if (
            benchmark.get("status") != "completed_verified_runs"
            or benchmark.get("measured_benefit") is not True
            or any(gain <= minimum_gain for gain in benchmark.get("paired_mean_gain", {}).values())
        ):
            reasons.append("measured_paired_benefit_required")
        _json_value(hardware)
        if type(hardware) is not dict:
            raise ValueError("Hardware assessment required.")
        for field in ("required_memory_gb", "available_memory_gb", "required_seconds", "available_seconds"):
            number = hardware.get(field)
            if type(number) not in (int, float) or not math.isfinite(number) or number <= 0:
                raise ValueError("Finite positive hardware requirements/capacity required.")
        if (
            hardware["available_memory_gb"] < hardware["required_memory_gb"]
            or hardware["available_seconds"] < hardware["required_seconds"]
            or hardware.get("resource_id") != evidence.get("resource_id")
            or not _text(hardware.get("assessment_id"))
            or not _verified(review_verifier, {"kind": "hardware_assessment", "assessment": hardware})
        ):
            reasons.append("hardware_gate_blocked")
        _json_value(human_approval)
        if (
            type(human_approval) is not dict
            or human_approval.get("actor_type") != "human"
            or human_approval.get("approved") is not True
            or not _text(human_approval.get("actor_id"))
            or not _text(human_approval.get("approval_id"))
            or human_approval.get("resource_id") != evidence.get("resource_id")
            or not _text(benchmark.get("benchmark_digest"))
            or human_approval.get("benchmark_digest") != benchmark.get("benchmark_digest")
            or human_approval.get("evidence_digest") != _digest(evidence)
            or human_approval.get("hardware_digest") != _digest(hardware)
            or not _verified(review_verifier, {"kind": "human_approval", "approval": human_approval})
        ):
            reasons.append("human_approval_required")
    except Exception as exc:
        reasons.append(str(exc) or "malformed_expansion_request")
    return {
        "status": "eligible_for_human_directed_expansion" if not reasons else "blocked",
        "expansion_allowed": not reasons,
        "automatic_integration": False,
        "canonical_truth": False,
        "benchmark": benchmark,
        "reasons": sorted(set(reasons)),
    }
