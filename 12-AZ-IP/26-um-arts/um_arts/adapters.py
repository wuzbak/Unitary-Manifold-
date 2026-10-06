# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Trusted execution configuration and conservative repository adapters."""

from __future__ import annotations

import math
import re
from pathlib import Path

from .evidence import EvidenceError, contained, read_json


def load_config(root: Path, path: Path | None = None, adapter: str = "um") -> dict:
    if path:
        raw = read_json(path)
    elif adapter == "um":
        raw = {
            "adapter": "um",
            "suites": [
                {"name": "physics", "paths": ["tests"]},
                {"name": "recycling", "paths": ["recycling"], "requires": ["physics"]},
                {"name": "pentad", "paths": ["5-GOVERNANCE/Unitary Pentad"],
                 "requires": ["recycling"], "serial": True},
            ],
        }
    else:
        raise EvidenceError("The generic adapter requires --config")
    if not isinstance(raw, dict):
        raise EvidenceError("Configuration must be a JSON object")
    allowed = {"adapter", "suites", "workers", "timeout_seconds", "pytest_args", "lean", "files_per_job"}
    if set(raw) - allowed:
        raise EvidenceError(f"Unknown config settings: {sorted(set(raw) - allowed)}")
    config = {
        "adapter": raw.get("adapter", adapter),
        "workers": raw.get("workers", 1),
        "files_per_job": raw.get("files_per_job", 32),
        "timeout_seconds": raw.get("timeout_seconds", 600),
        "pytest_args": raw.get("pytest_args", []),
        "suites": raw.get("suites", []),
        "lean": raw.get("lean"),
    }
    if config["adapter"] not in {"um", "generic"}:
        raise EvidenceError("Unknown adapter")
    workers = config["workers"]
    if isinstance(workers, bool) or not isinstance(workers, int) or not 1 <= workers <= 32:
        raise EvidenceError("workers must be an integer in [1, 32]")
    files_per_job = config["files_per_job"]
    if isinstance(files_per_job, bool) or not isinstance(files_per_job, int) \
            or not 1 <= files_per_job <= 1024:
        raise EvidenceError("files_per_job must be an integer in [1, 1024]")
    timeout = config["timeout_seconds"]
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) \
            or not math.isfinite(timeout) or not 0 < timeout <= 86400:
        raise EvidenceError("timeout_seconds must be finite and in (0, 86400]")
    args = config["pytest_args"]
    if not isinstance(args, list) or any(not isinstance(arg, str) for arg in args):
        raise EvidenceError("pytest_args must be strings")
    forbidden = ("-n", "--numprocesses", "--dist", "--collect", "--override-ini",
                 "--confcutdir", "--rootdir", "--basetemp")
    if any(arg.startswith(forbidden) or arg in {"-o", "-c"}
           or arg.startswith(("-p", "@")) for arg in args):
        raise EvidenceError("pytest_args may not alter collection plumbing or spawn xdist")
    suites = config["suites"]
    if not isinstance(suites, list) or not suites:
        raise EvidenceError("At least one suite is required")
    names = set()
    normalized = []
    for suite in suites:
        if not isinstance(suite, dict) or set(suite) - {"name", "paths", "requires", "serial"}:
            raise EvidenceError("Invalid suite configuration")
        name = suite.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", name) or name in names:
            raise EvidenceError("Suite names must be unique safe identifiers")
        names.add(name)
        paths = suite.get("paths")
        if not isinstance(paths, list) or not paths:
            raise EvidenceError("Suite paths must be a nonempty list")
        for entry in paths:
            # Test paths are files/directories, not command-line switches or selectors.
            if not isinstance(entry, str) or entry.startswith("-") or "::" in entry:
                raise EvidenceError("Suite paths must name repository files or directories")
            contained(root, entry, must_exist=False)
            if not (root / entry).exists():
                raise EvidenceError(f"Suite path does not exist: {entry}")
        requires = suite.get("requires", [])
        if not isinstance(requires, list) or any(not isinstance(item, str) for item in requires):
            raise EvidenceError("Suite requires must be a list of names")
        if not isinstance(suite.get("serial", False), bool):
            raise EvidenceError("Suite serial must be boolean")
        normalized.append({"name": name, "paths": paths, "requires": requires,
                           "serial": suite.get("serial", False)})
    ordered = []
    while len(ordered) < len(normalized):
        ready = [suite for suite in normalized if suite not in ordered
                 and set(suite["requires"]).issubset({s["name"] for s in ordered})]
        if not ready:
            raise EvidenceError("Suite dependencies are cyclic or unknown")
        ordered.extend(ready)
    config["suites"] = ordered
    lean = config["lean"]
    if lean is not None:
        if not isinstance(lean, dict) or set(lean) - {"scope", "project", "targets", "inspection"}:
            raise EvidenceError("Invalid Lean configuration")
        if lean.get("scope") not in {"full", "scoped"}:
            raise EvidenceError("Lean scope must be full or scoped")
        project = lean.get("project", "lean4")
        contained(root, project, must_exist=False)
        if not (root / project).is_dir():
            raise EvidenceError("Lean project does not exist")
        targets = lean.get("targets", [])
        if not isinstance(targets, list) or any(
                not isinstance(target, str)
                or not re.fullmatch(r"[A-Za-z0-9_.]+", target) for target in targets):
            raise EvidenceError("Lean targets must be module identifiers")
        if lean["scope"] == "scoped" and not targets:
            raise EvidenceError("Scoped Lean requires explicit build targets")
        if lean["scope"] == "full" and targets:
            raise EvidenceError("Full Lean build may not specify scoped targets")
        config["lean"] = {"scope": lean["scope"], "project": project, "targets": targets}
        inspection = lean.get("inspection")
        if inspection is not None:
            if not isinstance(inspection, dict) or set(inspection) != {"modules", "declarations"}:
                raise EvidenceError("Lean inspection requires modules and exact declaration names")
            for field in ["modules", "declarations"]:
                values = inspection[field]
                if not isinstance(values, list) or not values or any(
                        not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.']+", value)
                        for value in values) or len(values) != len(set(values)):
                    raise EvidenceError(f"Lean inspection {field} must be unique nonempty names")
            if lean["scope"] == "scoped" and not set(inspection["modules"]).issubset(targets):
                raise EvidenceError("Scoped inspection modules must belong to scoped build targets")
            config["lean"]["inspection"] = {
                "modules": sorted(inspection["modules"]),
                "declarations": sorted(inspection["declarations"]),
            }
    return config


def selection_policy(mode: str) -> dict:
    if mode not in {"full", "changed"}:
        raise EvidenceError("Unknown selection mode")
    # A git diff is not a sound Python import/fixture/dependency graph.
    return {
        "requested_mode": mode,
        "effective_mode": "full",
        "fallback_reason": ("No certified dependency graph; changed mode conservatively runs "
                            "every configured suite.") if mode == "changed" else None,
        "coverage_scope": "configured suites only; not an assertion of all repository tests",
    }
