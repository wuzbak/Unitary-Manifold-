# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Evaluate structured receipts from existing CI invocations without rerunning tests."""

from __future__ import annotations

import math
import os
import re
import shlex
import shutil
import uuid
from collections import Counter
from pathlib import Path

from . import VERSION
from .evidence import (
    EvidenceError,
    digest,
    fingerprints,
    read_json,
    seal,
    verify_seal,
    write_json,
)
from .process import execute
from .reconcile import check_events


def _serial_pytest_arguments(arguments: list[str]) -> tuple[list[str], list[str]]:
    """Remove only worker-spawning/distribution switches in explicit capture mode."""
    value_options = {"-n", "--numprocesses", "--dist", "--max-worker-restart",
                     "--maxschedchunk", "--tx", "--px", "--rsyncdir", "--rsyncignore"}
    flag_options = {"-d", "--loadscope-reorder", "--no-loadscope-reorder"}
    preserved_value_options = {
        "-k", "-m", "-c", "-p", "-o", "--override-ini", "--rootdir", "--confcutdir",
        "--basetemp", "--ignore", "--ignore-glob", "--deselect", "--maxfail", "--tb",
        "--capture", "--color", "--durations", "--durations-min", "--assert",
        "--verbosity", "--log-level", "--log-cli-level", "--log-file",
        "--log-file-level", "--junitxml", "--junit-prefix",
    }
    kept, removed = [], []
    index = 0
    while index < len(arguments):
        arg = arguments[index]
        if arg == "--":
            kept.extend(arguments[index:])
            break
        if arg in preserved_value_options and index + 1 < len(arguments):
            kept.extend(arguments[index:index + 2])
            index += 2
        elif arg in value_options:
            if index + 1 >= len(arguments):
                raise EvidenceError(f"Missing worker option value: {arg}")
            removed.extend(arguments[index:index + 2])
            index += 2
        elif arg in flag_options or any(arg.startswith(option + "=") for option in value_options) \
                or re.fullmatch(r"-n(?:=?[0-9]+|=?auto|=?logical)", arg):
            removed.append(arg)
            index += 1
        else:
            kept.append(arg)
            index += 1
    return kept, removed


def evaluate_report(path: str | Path, *, returncode: int,
                    expected_nodeids: list[str] | None = None, timed_out: bool = False,
                    collection_only: bool | None = None) -> dict:
    """Gate an existing subprocess using its actual exit code and plugin receipt.

    Set UM_ARTS_PYTEST_REPORT to an absolute, previously nonexistent JSON path,
    and add ``-p TOOLS.um_arts.pytest_plugin`` to the *existing* pytest invocation.
    The caller must pass its real subprocess return code, not a value inferred
    from this receipt. Imported/reported artifacts never execute commands here.
    """
    try:
        events = read_json(Path(path))
        if not isinstance(events, dict):
            raise EvidenceError("Pytest report must be a JSON object")
        selected = events.get("selected")
        if collection_only is None:
            collection_only = events.get("collection_only", False)
        if type(collection_only) is not bool:
            raise EvidenceError("collection_only must be boolean")
        if events.get("collection_only") != collection_only:
            raise EvidenceError("Receipt collection/execution mode mismatch")
        result = check_events(
            events, {"returncode": returncode, "timed_out": timed_out, "error": None},
            events.get("nonce"), expected_nodeids if expected_nodeids is not None else selected,
            collection=collection_only,
        )
        xdist = events.get("xdist", {})
        if not isinstance(xdist, dict):
            raise EvidenceError("Malformed xdist metadata")
        if xdist.get("enabled") and not collection_only:
            collections = xdist.get("worker_collections")
            receipts = xdist.get("worker_receipts")
            if not isinstance(collections, dict) or not collections \
                    or not isinstance(receipts, dict) or set(collections) != set(receipts):
                result["errors"].append("Missing xdist collection/completion receipts")
            else:
                reference_collection = next(iter(receipts.values())).get("collection")
                if not isinstance(reference_collection, list):
                    raise EvidenceError("Missing structured xdist collection reports")
                for worker, identities in collections.items():
                    receipt = receipts[worker]
                    if not isinstance(identities, list) or len(identities) != len(set(identities)) \
                            or Counter(identities) != Counter(selected):
                        result["errors"].append(f"xdist collected identities disagree: {worker}")
                    if not isinstance(receipt, dict) or receipt.get("version") != "1" \
                            or receipt.get("nonce") != events["nonce"] \
                            or receipt.get("root") != events.get("root") \
                            or Counter(receipt.get("selected", [])) != Counter(selected) \
                            or Counter(receipt.get("deselected", [])) != Counter(events["deselected"]) \
                            or Counter(receipt.get("partition_excluded", [])) != Counter(
                                events["partition_excluded"]) \
                            or receipt.get("internal_errors"):
                        result["errors"].append(f"Invalid xdist worker receipt: {worker}")
                    if receipt.get("collection") != reference_collection:
                        result["errors"].append(f"xdist collection reports disagree: {worker}")
            if xdist.get("worker_errors"):
                result["errors"].append("xdist worker error/crash")
        result["status"] = "passed" if not result["errors"] else "blocked"
        result["report_path"] = str(Path(path))
        result["executed_commands"] = False
        result["evidence_class"] = "RAW_STRUCTURED_PYTEST_RECEIPT"
        result["sealed"] = False
        result["proof_claim"] = False
        result["integrity_boundary"] = (
            "Caller exit code and phases are reconciled; raw JSON is not a sealed "
            "provenance artifact or certification.")
        result["xdist"] = {"enabled": bool(xdist.get("enabled")),
                           "workers": sorted(xdist.get("worker_collections", {}))}
        return result
    except (EvidenceError, KeyError, TypeError, ValueError, AttributeError) as exc:
        return {"status": "blocked", "errors": [str(exc)], "counts": {}, "durations": {},
                "report_path": str(path), "executed_commands": False,
                "evidence_class": "RAW_STRUCTURED_PYTEST_RECEIPT", "sealed": False,
                "proof_claim": False}


def capture_command(command: list[str], output: Path, root: Path | None = None,
                    timeout_seconds: float = 600) -> dict:
    """Run an explicitly trusted existing command once, sealing its evidence."""
    if not isinstance(command, list) or not command or not command[0] or any(
            not isinstance(arg, str) or "\x00" in arg for arg in command):
        raise EvidenceError("A nonempty command argument list is required")
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) \
            or not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 86400:
        raise EvidenceError("Capture timeout must be finite and in (0, 86400]")
    root = (root or Path.cwd()).resolve()
    output = output.resolve()
    if not root.is_dir() or root.is_relative_to(output):
        raise EvidenceError("Capture output may not be the source root or its ancestor")
    output.mkdir(parents=True, exist_ok=False)
    pytest_command = (len(command) >= 3 and command[1:3] == ["-m", "pytest"]) \
        or Path(command[0]).name in {"pytest", "pytest-3", "py.test"}
    effective = list(command)
    environment = dict(os.environ)
    environment.pop("UM_ARTS_RECEIPT", None)
    environment.pop("UM_ARTS_SELECTION", None)
    environment.pop("UM_ARTS_PYTEST_REPORT", None)
    if pytest_command:
        insertion = 3 if command[1:3] == ["-m", "pytest"] else 1
        arguments, removed_worker_options = _serial_pytest_arguments(command[insertion:])
        effective = [*command[:insertion], *arguments]
        addopts, removed_environment_options = _serial_pytest_arguments(
            shlex.split(environment.get("PYTEST_ADDOPTS", "")))
        environment["PYTEST_ADDOPTS"] = shlex.join(addopts)
        environment["UM_ARTS_CAPTURE_SERIAL"] = "1"
        if not any("TOOLS.um_arts.pytest_plugin" in arg for arg in command):
            effective[insertion:insertion] = ["-p", "TOOLS.um_arts.pytest_plugin"]
        environment["UM_ARTS_PYTEST_REPORT"] = str(output / "pytest.json")
        environment["PYTHONPATH"] = os.pathsep.join(
            [str(Path(__file__).resolve().parents[2]), str(root), environment.get("PYTHONPATH", "")])
        for option in ["--rootdir", "--confcutdir"]:
            if not any(arg == option or arg.startswith(option + "=") for arg in command):
                effective.extend([option, str(root)])
        if not any(arg == "--basetemp" or arg.startswith("--basetemp=") for arg in command):
            effective.extend(["--basetemp", str(output / "scratch")])
        if "-c" not in command:
            own_config = next((root / name for name in ["pytest.ini", ".pytest.ini", "pyproject.toml",
                                                       "tox.ini", "setup.cfg"]
                               if (root / name).is_file()), None)
            if own_config is None:
                own_config = output / "pytest.ini"
                own_config.write_text("[pytest]\n", encoding="utf-8")
            effective.extend(["-c", str(own_config)])
    settings = {"command": command, "timeout_seconds": timeout_seconds,
                "structured_pytest": pytest_command, "capture_version": VERSION}
    if pytest_command:
        settings.update({"xdist_policy": "serial_in_explicit_capture_wrapper",
                         "removed_worker_options": removed_worker_options,
                         "removed_environment_worker_options": removed_environment_options})
    request = {"command": effective, "original_command": command, "root": str(root),
               "settings": settings}
    write_json(output / "request.json", request)
    before = fingerprints(root, output, settings)
    write_json(output / "start_fingerprints.json", before)
    execute(effective, root, output, timeout_seconds, environment)
    scratch = output / "scratch"
    if scratch.is_symlink():
        scratch.unlink()
    elif scratch.exists():
        shutil.rmtree(scratch)
    write_json(output / "end_fingerprints.json", fingerprints(root, output, settings))
    write_json(output / "capture.json", {
        "version": VERSION, "id": uuid.uuid4().hex, "root": str(root),
        "compatibility": before["compatibility"], "structured_pytest": pytest_command,
        "request_digest": digest(request),
    })
    seal(output)
    for path in output.rglob("*"):
        path.chmod(0o555 if path.is_dir() else 0o444)
    output.chmod(0o555)
    return evaluate_capture(output)


def evaluate_capture(directory: Path) -> dict:
    """Read a sealed captured command; never execute its command or project code."""
    verify_seal(directory)
    spec = read_json(directory / "capture.json")
    request = read_json(directory / "request.json")
    process = read_json(directory / "process.json")
    start = read_json(directory / "start_fingerprints.json")
    end = read_json(directory / "end_fingerprints.json")
    if not isinstance(spec, dict) or spec.get("version") != VERSION \
            or spec.get("request_digest") != digest(request) \
            or spec.get("compatibility") != start.get("compatibility") \
            or spec.get("root") != request.get("root"):
        raise EvidenceError("Captured command provenance does not reconcile")
    errors = []
    if type(process.get("returncode")) is not int or type(process.get("timed_out")) is not bool:
        errors.append("Captured process status has invalid types")
    if process.get("command") != request.get("command") or process.get("cwd") != spec["root"]:
        errors.append("Captured process command/root differs from request")
    if end.get("compatibility") != start["compatibility"]:
        errors.append("Source/environment/settings changed during captured execution")
    if process.get("returncode") != 0 or process.get("timed_out") or process.get("error"):
        errors.append("Captured command exited nonzero, timed out, or failed")
    structured = spec.get("structured_pytest")
    collection_only = False
    if type(structured) is not bool:
        raise EvidenceError("Invalid structured capture flag")
    if structured:
        tests = evaluate_report(directory / "pytest.json", returncode=process["returncode"],
                                timed_out=process["timed_out"])
        errors.extend(tests["errors"])
        raw = read_json(directory / "pytest.json") if (directory / "pytest.json").is_file() else {}
        collection_only = raw.get("collection_only") is True
        if raw.get("root") != spec["root"]:
            errors.append("Pytest receipt root differs from captured source root")
    else:
        tests = {"counts": {}, "durations": {}, "selected": [], "deselected": [],
                 "collection_skips": [], "status": "not_observed"}
    status = ("blocked" if errors else "collection_passed" if collection_only
              else "passed" if structured else "command_passed")
    return {
        "version": VERSION, "attempt_id": spec["id"], "attempt_path": str(directory),
        "status": status, "errors": errors, "counts": tests["counts"],
        "durations": tests["durations"], "compatibility": spec["compatibility"],
        "selected": len(tests.get("selected", [])), "reconciled": len(tests.get("durations", {})),
        "deselected": len(tests.get("deselected", [])),
        "collection_skips": tests.get("collection_skips", []),
        "suites": {"captured_pytest" if structured else "command": status},
        "jobs": {"captured": tests}, "command": request["original_command"],
        "effective_command": process["command"], "returncode": process["returncode"],
        "evidence_class": ("STRUCTURED_PYTEST_COLLECTION" if collection_only
                           else "STRUCTURED_PYTEST_EXECUTION" if structured
                           else "COMMAND_EXECUTION_ONLY"),
        "sealed": True, "proof_claim": False,
        "test_gate": structured and not collection_only and not errors,
        "collection_only": collection_only, "pytest_status": tests["status"],
        "formal": {"proof_claim": False, "correspondence": "UNRESOLVED",
                   "boundary": "Command/test evidence is not formal proof."},
        "provenance": {
            "command": request["original_command"], "effective_command": process["command"],
            "root": spec["root"], "returncode": process["returncode"],
            "source_files": start["source_files"], "source_policy": start["source_policy"],
            "environment": start["environment"], "git": start["git"],
            "engine": start["engine"], "settings": request["settings"],
            "before": start["compatibility"], "after": end["compatibility"],
            "source_stable": start["compatibility"]["source"] == end["compatibility"]["source"],
            "environment_stable": start["compatibility"]["environment"] == end["compatibility"]["environment"],
            "logs": {"stdout_and_stderr": "output.log", "process": "process.json"},
        },
        "integrity_boundary": "SHA-256 seals are integrity checks, not execution signatures.",
    }
