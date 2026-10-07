# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Fail-closed reconciliation of collected identities and phase receipts."""

from __future__ import annotations

import math
from collections import Counter
from pathlib import Path

from .evidence import EvidenceError, read_json


def check_events(events: dict, process: dict, nonce: str, expected: list[str] | None,
                 *, collection: bool = False) -> dict:
    if not isinstance(events, dict) or not isinstance(process, dict):
        raise EvidenceError("Receipt and process evidence must be JSON objects")
    for field in ["collection", "reports", "internal_errors"]:
        if not isinstance(events.get(field), list):
            raise EvidenceError(f"Receipt requires a structured {field} array")
    for field in ["collection", "reports"]:
        if any(not isinstance(item, dict) for item in events[field]):
            raise EvidenceError(f"Receipt contains malformed {field} entries")
    if not isinstance(nonce, str) or not nonce:
        raise EvidenceError("Missing invocation nonce")
    if type(process.get("timed_out")) is not bool \
            or type(process.get("returncode")) is not int \
            or type(events.get("exitstatus")) is not int:
        raise EvidenceError("Invalid process/session status types")
    errors = []
    if process.get("timed_out") or process.get("error"):
        errors.append("Subprocess timed out, interrupted, or failed to launch")
    if events.get("version") != "1" or events.get("nonce") != nonce:
        errors.append("Receipt version/nonce mismatch")
    if events.get("internal_errors"):
        errors.append("Pytest internal error")
    selected = events.get("selected", [])
    deselected = events.get("deselected", [])
    excluded = events.get("partition_excluded", [])
    for label, nodes in [("selected", selected), ("deselected", deselected),
                         ("partition_excluded", excluded)]:
        if not isinstance(nodes, list) or any(not isinstance(n, str) or not n for n in nodes):
            raise EvidenceError(f"Invalid {label} node identities")
        if len(nodes) != len(set(nodes)):
            errors.append(f"Duplicate {label} node identities")
    if set(selected) & (set(deselected) | set(excluded)) or set(deselected) & set(excluded):
        errors.append("Selected/deselected/excluded identities overlap")
    selected_set = set(selected)
    if expected is not None and Counter(selected) != Counter(expected):
        errors.append("Collected identities do not exactly match the plan")
    collection_reports = events.get("collection", [])
    if any(item.get("outcome") not in {"passed", "skipped"} for item in collection_reports):
        errors.append("Collection errors")
    collection_skips = [item["nodeid"] for item in collection_reports
                        if item.get("outcome") == "skipped"]
    if not selected:
        errors.append("No selected tests; empty runs are not green")
    code = process.get("returncode")
    if events.get("exitstatus") != code:
        errors.append("Session and process exit codes disagree")
    if code != 0:
        errors.append(f"Nonzero pytest exit: {code}")
    reports = events.get("reports", [])
    counts = Counter()
    durations = {}
    if collection:
        if reports:
            errors.append("Collection-only receipt unexpectedly contains execution")
    else:
        by_node = {}
        for report in reports:
            node = report.get("nodeid")
            if node not in selected_set:
                errors.append(f"Unexpected executed node: {node}")
            by_node.setdefault(node, []).append(report)
        if set(by_node) != selected_set:
            errors.append("Missing or extra executed test identities")
        for node in selected:
            phases = by_node.get(node, [])
            phase_names = [report.get("when") for report in phases]
            if phase_names not in [["setup", "call", "teardown"], ["setup", "teardown"]]:
                errors.append(f"Incomplete/duplicate/out-of-order test phases: {node}")
                continue
            duration = 0.0
            for phase in phases:
                seconds = phase.get("duration")
                if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) \
                        or not math.isfinite(seconds) or seconds < 0:
                    errors.append(f"Invalid test duration: {node}")
                else:
                    duration += seconds
            durations[node] = duration
            if any(phase.get("outcome") == "failed" for phase in phases):
                counts["failed"] += 1
                errors.append(f"Test setup/call/teardown failed: {node}")
            elif any(phase.get("outcome") not in {"passed", "skipped"} for phase in phases):
                errors.append(f"Unknown phase outcome: {node}")
            elif phases[-1].get("outcome") != "passed":
                errors.append(f"Teardown did not pass: {node}")
            elif phases[0].get("outcome") == "skipped":
                if len(phases) != 2:
                    errors.append(f"Skipped setup unexpectedly executed a call: {node}")
                counts["xfailed" if phases[0].get("wasxfail") is not None else "skipped"] += 1
            elif phases[0].get("outcome") != "passed" or len(phases) != 3:
                errors.append(f"Missing call after successful setup: {node}")
            elif phases[1].get("outcome") == "skipped":
                counts["xfailed" if phases[1].get("wasxfail") is not None else "skipped"] += 1
            elif phases[1].get("wasxfail") is not None:
                counts["xpassed"] += 1
                # Unexpected success is visible, and does not silently satisfy the gate.
                errors.append(f"Unexpected xfail success: {node}")
            else:
                counts["passed"] += 1
    return {"status": "passed" if not errors else "blocked", "errors": errors,
            "counts": dict(counts), "durations": durations, "selected": selected,
            "deselected": deselected, "partition_excluded": excluded,
            "collection_skips": collection_skips}


def evaluate_job(directory: Path, expected: list[str] | None,
                 *, collection: bool = False) -> dict:
    process = None
    try:
        process = read_json(directory / "process.json")
        request = read_json(directory / "request.json")
        events = read_json(directory / "events.json")
        result = check_events(events, process, request["nonce"], expected, collection=collection)
        if process.get("command") != request.get("command") \
                or request.get("collection_only") != collection \
                or events.get("root") != request.get("root") \
                or process.get("cwd") != request.get("root"):
            result["errors"].append("Process command does not match the structured request")
            result["status"] = "blocked"
        if not collection:
            requested = read_json(directory / "selection.json")
            if Counter(requested) != Counter(expected or []):
                result["errors"].append("Selection file does not match the planned job")
                result["status"] = "blocked"
        return result
    except (EvidenceError, KeyError, TypeError, ValueError, AttributeError) as exc:
        errors = [str(exc)]
        if isinstance(process, dict):
            if process.get("timed_out") is True:
                errors.append("Subprocess timed out; complete pytest evidence is unavailable")
            if isinstance(process.get("error"), str) and process["error"]:
                errors.append("Subprocess interrupted or failed to launch; complete pytest evidence is unavailable")
            code = process.get("returncode")
            if type(code) is int and code != 0:
                errors.append(f"Nonzero subprocess exit: {code}")
        return {"status": "blocked", "errors": errors, "counts": {}, "durations": {},
                "selected": [], "deselected": [], "collection_skips": []}
