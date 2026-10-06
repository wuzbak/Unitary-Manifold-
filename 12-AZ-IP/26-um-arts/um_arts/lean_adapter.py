# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Typed receipts from the exact-name Lean environment exporter."""

from __future__ import annotations

import os
import re
from pathlib import Path

from .evidence import EvidenceError, file_hash, read_json, write_json
from .process import execute


def decode(document: dict, request: dict, expected_version: str | None = None) -> dict:
    """Validate exporter metadata without reading source or invoking Lean."""
    if not isinstance(document, dict) or type(document.get("schema_version")) is not int \
            or document["schema_version"] != 1:
        raise EvidenceError("Unsupported Lean exporter schema")
    version = document.get("lean_version")
    if not isinstance(version, str) or not version or (
            expected_version is not None and version != expected_version):
        raise EvidenceError("Lean exporter version does not match the pinned toolchain")
    modules = document.get("modules")
    if not isinstance(modules, list) or modules != sorted(set(request["modules"])):
        raise EvidenceError("Lean exporter modules do not exactly match the request")
    declarations = document.get("declarations")
    if not isinstance(declarations, list) or any(not isinstance(row, dict) for row in declarations):
        raise EvidenceError("Lean exporter declarations must be a structured list")
    names = [row.get("name") for row in declarations]
    if names != sorted(set(request["declarations"])):
        raise EvidenceError("Missing, duplicate, unexpected, or unordered Lean declaration names")
    rows = []
    for row in declarations:
        name = row["name"]
        if not isinstance(row.get("statement"), str) or not row["statement"] \
                or not isinstance(row.get("kind"), str) or not row["kind"] \
                or type(row.get("checked")) is not bool:
            raise EvidenceError(f"Malformed Lean declaration metadata: {name}")
        for field in ["axioms", "dependencies"]:
            values = row.get(field)
            if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values) \
                    or values != sorted(set(values)):
                raise EvidenceError(f"Malformed Lean {field}: {name}")
        has_sorry = any(value == "sorryAx" or value.endswith(".sorryAx")
                        for value in [*row["axioms"], *row["dependencies"]])
        theorem = row["kind"] == "theorem"
        if row["checked"] != (theorem and not has_sorry):
            raise EvidenceError(f"Inconsistent checked/sorry/kind semantics: {name}")
        classification = (
            "UNCHECKED_SORRY_DEPENDENCY" if theorem and has_sorry else
            "CHECKED_THEOREM_WITH_REPORTED_AXIOMS" if theorem and row["axioms"] else
            "CHECKED_THEOREM_NO_AXIOMS_REPORTED" if theorem else
            "AXIOM_DECLARATION" if row["kind"] == "axiom" else "NON_THEOREM_DECLARATION"
        )
        validated = {field: row[field] for field in [
            "name", "statement", "kind", "axioms", "dependencies", "checked"]}
        rows.append({**validated, "classification": classification,
                     "correspondence": "UNRESOLVED", "proof_claim": False})
    return {
        "status": "inspected", "lean_version": version, "modules": modules,
        "declarations": rows, "proof_claim": False, "correspondence": "UNRESOLVED",
        "all_requested_theorems_checked": bool(rows) and all(
            row["kind"] == "theorem" and row["checked"] for row in rows),
        "boundary": "Exact declaration metadata from a checked Lean environment does not "
                    "discharge reported axioms, establish Python correspondence, or prove the physics.",
    }


def blocked(directory: Path, request: dict, reason: str) -> None:
    if not (directory / "request.json").exists():
        write_json(directory / "request.json", request)
    write_json(directory / "inspection.json", {
        "status": "blocked", "reason": reason, "proof_claim": False,
        "correspondence": "UNRESOLVED", "declarations": [],
    })


def inspect(project: Path, directory: Path, request: dict, lake: str, timeout: float) -> None:
    """Explicitly requested execution; reporting/import never invokes this function."""
    write_json(directory / "request.json", request)
    result = execute([lake, "build", "um_arts_export"], project, directory / "exporter_build", timeout)
    if result["returncode"] != 0 or result["timed_out"] or result["error"]:
        blocked(directory, request, "Lean exporter executable build failed or was blocked")
        return
    binary = project / ".lake/build/bin/um_arts_export"
    if not binary.is_file() or not binary.resolve().is_relative_to(project.resolve()) \
            or not os.access(binary, os.X_OK):
        blocked(directory, request, "Lean exporter executable is missing or outside the project")
        return
    pin = project / "lean-toolchain"
    expected_version = (pin.read_text(encoding="utf-8").strip().split(":")[-1].removeprefix("v")
                        if pin.is_file() else None)
    binary_hash = file_hash(binary)
    write_json(directory / "environment.json", {
        "binary": str(binary), "binary_sha256": binary_hash, "lake": lake,
        "project_root": str(project), "expected_lean_version": expected_version,
    })
    # Lake's environment supplies the module search path and pinned Lean sysroot.
    # Build chatter and stderr are kept separate from the JSON stdout receipt.
    command = [lake, "env", str(binary)]
    for module in request["modules"]:
        command.extend(["--module", module])
    for declaration in request["declarations"]:
        command.extend(["--decl", declaration])
    result = execute(command, project, directory / "export", timeout, separate_stderr=True)
    if result["returncode"] != 0 or result["timed_out"] or result["error"]:
        blocked(directory, request, "Lean declaration export failed or was blocked")
        return
    try:
        if file_hash(binary) != binary_hash:
            raise EvidenceError("Lean exporter binary changed during inspection")
        decoded = decode(read_json(directory / "export/output.log"), request, expected_version)
        write_json(directory / "inspection.json", decoded)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        blocked(directory, request, str(exc))


def evaluate(directory: Path, request: dict | None, expected_project: str | None = None) -> dict:
    """Reconcile saved build/execution/JSON evidence; no commands or root imports."""
    if request is None:
        return {"status": "not_requested", "declarations": [], "proof_claim": False,
                "correspondence": "UNRESOLVED"}
    try:
        receipt = read_json(directory / "inspection.json")
        if read_json(directory / "request.json") != request or receipt.get("proof_claim") is not False \
                or receipt.get("correspondence") != "UNRESOLVED":
            raise EvidenceError("Lean inspection request or proof boundary mismatch")
        if receipt.get("status") == "blocked":
            return receipt
        environment = read_json(directory / "environment.json")
        binary = environment["binary"]
        project = expected_project or environment["project_root"]
        if binary != str(Path(project) / ".lake/build/bin/um_arts_export") \
                or environment["project_root"] != project \
                or not re.fullmatch(r"[0-9a-f]{64}", environment["binary_sha256"]):
            raise EvidenceError("Lean exporter binary provenance mismatch")
        command = [environment["lake"], "env", binary]
        for module in request["modules"]:
            command.extend(["--module", module])
        for declaration in request["declarations"]:
            command.extend(["--decl", declaration])
        for phase, expected in [
            ("exporter_build", [environment["lake"], "build", "um_arts_export"]),
            ("export", command),
        ]:
            if not (directory / phase / "output.log").is_file() or (
                    phase == "export" and not (directory / phase / "stderr.log").is_file()):
                raise EvidenceError(f"Missing Lean {phase} output stream receipt")
            process = read_json(directory / phase / "process.json")
            if process.get("command") != expected or process.get("cwd") != project \
                    or type(process.get("returncode")) is not int or process["returncode"] != 0 \
                    or process.get("timed_out") is not False or process.get("error"):
                raise EvidenceError(f"No successful bounded Lean {phase} receipt")
        decoded = decode(read_json(directory / "export/output.log"), request,
                         environment["expected_lean_version"])
        if decoded != receipt:
            raise EvidenceError("Saved Lean inspection differs from exact exported metadata")
        return decoded
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return {"status": "blocked", "reason": str(exc), "declarations": [], "proof_claim": False,
                "correspondence": "UNRESOLVED"}
