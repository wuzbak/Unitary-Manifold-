# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Offline, bounded Python pattern scans with explicit coverage, not CodeQL equivalence."""

from __future__ import annotations

import math
import os
import shutil
from pathlib import Path

from .evidence import (
    EvidenceError,
    contained,
    digest,
    file_hash,
    fingerprints,
    read_json,
    seal,
    verify_seal,
    write_json,
)
from .process import execute

SCHEMA = 1
BOUNDARY = (
    "Only the selected Python files and explicitly supplied local rules are checked. "
    "Shards do not preserve cross-file data flow. No findings is not a security "
    "certification, CodeQL equivalent, Lean proof or executed regression test."
)


def _integer(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise EvidenceError(f"{name} must be an integer in [{low}, {high}]")


def _relative(root: Path, value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        try:
            value = path.relative_to(root).as_posix()
        except ValueError as exc:
            raise EvidenceError("Scanner reported a path outside its source root") from exc
    # Scanner may prefix relative paths with './'.
    while value.startswith("./"):
        value = value[2:]
    contained(root, value)
    return value


def _evaluate_shard(directory: Path, root: Path, selected: list[str]) -> dict:
    process = read_json(directory / "process.json")
    errors = []
    findings = []
    scanned = []
    version = None
    if process["timed_out"] or process["error"] or process["returncode"] != 0:
        errors.append("Scanner did not complete successfully")
    try:
        receipt = read_json(directory / "output.log")
        if not isinstance(receipt, dict) or not isinstance(receipt.get("results"), list) \
                or not isinstance(receipt.get("errors"), list) \
                or not isinstance(receipt.get("paths"), dict) \
                or not isinstance(receipt["paths"].get("scanned"), list):
            raise EvidenceError("Scanner JSON lacks structured findings/errors/coverage")
        version = receipt.get("version")
        scanned = [_relative(root, value) for value in receipt["paths"]["scanned"]]
        if len(scanned) != len(set(scanned)) or set(scanned) != set(selected):
            errors.append("Scanner coverage does not exactly match the assigned files")
        if receipt["errors"]:
            errors.append("Scanner reported parse, timeout, configuration or analysis errors")
        if receipt.get("skipped_rules"):
            errors.append("Scanner reported skipped rules")
        if receipt["paths"].get("skipped"):
            errors.append("Scanner reported skipped targets")
        for finding in receipt["results"]:
            if not isinstance(finding, dict) or not isinstance(finding.get("check_id"), str):
                raise EvidenceError("Malformed scanner finding")
            relative = _relative(root, finding["path"])
            if relative not in selected:
                raise EvidenceError("Finding is outside the assigned scan scope")
            start = finding["start"]
            if not isinstance(start, dict) or isinstance(start.get("line"), bool) \
                    or not isinstance(start.get("line"), int) or start["line"] < 1:
                raise EvidenceError("Finding lacks a valid source line")
            findings.append({"rule": finding["check_id"], "path": relative,
                             "line": start["line"], "review_required": True})
    except (EvidenceError, KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
    return {"status": "complete" if not errors else "blocked",
            "errors": errors, "scanned": sorted(scanned), "findings": findings,
            "reported_tool_version": version}


def scan(root: Path, output: Path, executable: Path, rules: Path, *,
         paths: list[str] | None = None, files_per_shard: int = 64,
         max_file_bytes: int = 2 * 1024 * 1024, timeout_seconds: float = 120,
         memory_mib: int = 512, previous: Path | None = None) -> dict:
    """Execute a trusted local Opengrep binary; never download code, rules or extensions."""
    _integer(files_per_shard, "files_per_shard", 1, 1024)
    _integer(max_file_bytes, "max_file_bytes", 1, 64 * 1024 * 1024)
    _integer(memory_mib, "memory_mib", 128, 16384)
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) \
            or not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 86400:
        raise EvidenceError("timeout_seconds must be finite and in (0, 86400]")
    root, output = root.resolve(), output.absolute()
    if not root.is_dir() or output.exists() or output.is_symlink() \
            or output.resolve().is_relative_to(root) or root.is_relative_to(output.resolve()):
        raise EvidenceError("Scan output must be a new directory outside the source tree")
    if any(parent.is_symlink() for parent in output.parents):
        raise EvidenceError("Scan output may not traverse symlinks")
    executable, rules = executable.resolve(), rules.resolve()
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise EvidenceError("Select an installed executable Opengrep binary")
    if not rules.is_file() or rules.stat().st_size > 2 * 1024 * 1024:
        raise EvidenceError("Select a local rule file of at most 2 MiB")
    prefixes = []
    for value in paths or ["."]:
        if value == ".":
            prefixes.append("")
        else:
            path = contained(root, value, must_exist=False)
            if not path.exists():
                raise EvidenceError(f"Missing scan path: {value}")
            prefixes.append(value.rstrip("/"))
    settings = {"schema": SCHEMA, "tool_sha256": file_hash(executable),
                "rules_sha256": file_hash(rules), "paths": prefixes,
                "files_per_shard": files_per_shard, "max_file_bytes": max_file_bytes,
                "timeout_seconds": timeout_seconds, "memory_mib": memory_mib}
    before = fingerprints(root, output, settings)
    selected = sorted(path for path in before["source_files"] if path.endswith(".py")
                      and any(not p or path == p or path.startswith(p + "/") for p in prefixes))
    oversized = [path for path in selected if (root / path).stat().st_size > max_file_bytes]
    oversized_set = set(oversized)
    targets = [path for path in selected if path not in oversized_set]
    prior = {}
    if previous is not None:
        previous = previous.resolve()
        if output.resolve().is_relative_to(previous):
            raise EvidenceError("New scan output must not be inside prior evidence")
        verify_seal(previous)
        previous_result = read_json(previous / "scan.json")
        if previous_result.get("schema") != SCHEMA:
            raise EvidenceError("Incompatible scanner artifact schema")
        if previous_result.get("source_stable") is True:
            prior = {entry["key"]: entry for entry in previous_result["shards"]
                     if entry["status"] == "complete"}
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "start_fingerprints.json", before)
    # Freeze the rule bytes for all shards; edits to the original cannot silently alter a run.
    shutil.copyfile(rules, output / "rules.yml")
    if file_hash(output / "rules.yml") != settings["rules_sha256"]:
        raise EvidenceError("Rule file changed while copying")
    shards = []
    environment = dict(os.environ)
    for key in list(environment):
        if key.startswith(("SEMGREP_", "OPENGREP_")):
            environment.pop(key)
    environment.update({"SEMGREP_SEND_METRICS": "off", "SEMGREP_ENABLE_VERSION_CHECK": "0"})
    for number, offset in enumerate(range(0, len(targets), files_per_shard)):
        assigned = targets[offset:offset + files_per_shard]
        shard_name = f"shards/{number:05d}"
        directory = output / shard_name
        key = digest({"settings": settings,
                      "inputs": {p: before["source_files"][p] for p in assigned}})
        reused = prior.get(key)
        if reused:
            source = contained(previous, reused["directory"], must_exist=False)
            verify_seal(source)
            if read_json(source / "request.json").get("key") != key:
                raise EvidenceError("Reusable shard request does not match its input digest")
            shutil.copytree(source, directory)
            result = _evaluate_shard(directory, root, assigned)
            result["reused"] = True
        else:
            directory.mkdir(parents=True)
            command = [str(executable), "scan", "--config", str(output / "rules.yml"),
                       "--json", "--disable-version-check",
                       "--no-git-ignore", "--disable-nosem", "--strict", "--jobs=1",
                       f"--max-memory={memory_mib}", f"--max-target-bytes={max_file_bytes}",
                       f"--timeout={min(timeout_seconds, 30)}", "--", *assigned]
            write_json(directory / "request.json", {"key": key, "files": assigned,
                                                   "command": command})
            execute(command, root, directory, timeout_seconds, environment,
                    stream=False, separate_stderr=True)
            result = _evaluate_shard(directory, root, assigned)
            result["reused"] = False
            write_json(directory / "evaluation.json", result)
            seal(directory)
        shards.append({**result, "directory": shard_name, "key": key})
    after = fingerprints(root, output, settings)
    write_json(output / "end_fingerprints.json", after)
    stable = before["compatibility"] == after["compatibility"] \
        and file_hash(executable) == settings["tool_sha256"] \
        and file_hash(rules) == settings["rules_sha256"]
    errors = []
    if not stable:
        errors.append("Source/environment/settings/tool/rules changed during scan")
    if not selected:
        errors.append("No Python files selected")
    if oversized:
        errors.append("Oversized Python files remain unscanned")
    if any(shard["status"] != "complete" for shard in shards):
        errors.append("One or more scanner shards lack complete coverage")
    findings = [item for shard in shards for item in shard["findings"]]
    result = {"schema": SCHEMA, "status": "blocked" if errors else
              "findings" if findings else "checked", "errors": errors,
              "source_stable": stable, "compatibility": before["compatibility"],
              "settings": settings, "selected": len(selected),
              "scanned": len({p for shard in shards for p in shard["scanned"]}),
              "oversized": oversized, "shards": shards, "findings": findings,
              "artifact": str(output), "security_certified": False, "boundary": BOUNDARY}
    write_json(output / "scan.json", result)
    seal(output)
    return result


def inspect_scan(artifact: Path) -> dict:
    """Verify hashes without executing the artifact's commands."""
    verify_seal(artifact)
    result = read_json(artifact / "scan.json")
    if result.get("schema") != SCHEMA or result.get("security_certified") is not False:
        raise EvidenceError("Unsupported scan artifact")
    return result
