# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Read-only aggregation of explicitly required, compatible captured checks."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from .capture import evaluate_capture
from .evidence import EvidenceError, contained, digest, read_json


def certify(manifest_path: Path) -> dict:
    """Reconcile named evidence; never execute commands from a manifest."""
    manifest = read_json(manifest_path)
    if not isinstance(manifest, dict) or set(manifest) != {"label", "checks"} \
            or not isinstance(manifest["label"], str) or not manifest["label"].strip() \
            or not isinstance(manifest["checks"], list) or not 1 <= len(manifest["checks"]) <= 1024:
        raise EvidenceError("Certification requires a label and between 1 and 1024 checks")
    names = set()
    artifacts = set()
    nodes = set()
    counts = Counter()
    checks = {}
    errors = []
    baseline = None
    for check in manifest["checks"]:
        if not isinstance(check, dict) or set(check) != {"id", "artifact", "command", "kind", "scope"}:
            raise EvidenceError("Every check requires id, artifact, command, kind and scope")
        name = check["id"]
        command = check["command"]
        if not isinstance(name, str) or not name or name in names \
                or not isinstance(check["kind"], str) or check["kind"] not in {"pytest", "command"} \
                or not isinstance(check["scope"], str) or not check["scope"].strip() \
                or not isinstance(command, list) or not command or not command[0] \
                or any(not isinstance(arg, str) or "\x00" in arg for arg in command):
            raise EvidenceError("Invalid or duplicate certification check")
        names.add(name)
        artifact = contained(manifest_path.resolve().parent, check["artifact"], must_exist=False)
        if artifact in artifacts:
            raise EvidenceError("One artifact cannot satisfy multiple required checks")
        artifacts.add(artifact)
        try:
            result = evaluate_capture(artifact)
            provenance = result["provenance"]
            compatibility = {
                field: result["compatibility"][field]
                for field in ["source", "environment", "engine", "git"]
            }
            compatibility["root"] = provenance["root"]
            if baseline is None:
                baseline = compatibility
            elif compatibility != baseline:
                raise EvidenceError("Required checks have incompatible source/environment/engine/git/root")
            if result["command"] != command:
                raise EvidenceError("Captured command does not match required command")
            if check["kind"] == "pytest":
                if result["status"] != "passed" or result["test_gate"] is not True \
                        or result["evidence_class"] != "STRUCTURED_PYTEST_EXECUTION":
                    raise EvidenceError("Required pytest execution gate did not pass")
                selected = result["jobs"]["captured"]["selected"]
                if nodes.intersection(selected):
                    raise EvidenceError("Required pytest checks overlap; totals would double-count tests")
                nodes.update(selected)
                counts.update(result["counts"])
            elif result["status"] != "command_passed" \
                    or result["evidence_class"] != "COMMAND_EXECUTION_ONLY":
                raise EvidenceError("Required command-only gate did not pass")
            checks[name] = {"status": "passed", "kind": check["kind"], "scope": check["scope"],
                            "attempt_id": result["attempt_id"], "artifact": check["artifact"],
                            "command": command, "deselected": result["deselected"],
                            "collection_skips": result["collection_skips"]}
        except (EvidenceError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"{name}: {exc}")
            checks[name] = {"status": "blocked", "kind": check["kind"],
                            "scope": check["scope"], "reason": str(exc)}
    return {
        "status": "passed" if not errors else "blocked", "label": manifest["label"],
        "manifest_digest": digest(manifest), "checks": checks, "errors": errors,
        "counts": dict(counts), "unique_test_identities": len(nodes),
        "compatibility": baseline, "proof_claim": False,
        "coverage_scope": "Only checks explicitly required by this manifest; "
                          "not an assertion that every repository check is covered.",
        "boundary": "Artifact hashes are not signatures. Matching command execution "
                    "is distinct from pytest completeness or formal proof.",
    }
