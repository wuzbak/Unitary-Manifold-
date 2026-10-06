# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Snapshot existing formal registries; build success is never a proof claim."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from . import lean_adapter
from .evidence import read_json, write_json
from .process import execute


def capture(root: Path, directory: Path, config: dict) -> dict:
    if config["adapter"] != "um":
        return {"status": "not_applicable", "units": [],
                "correspondence": "UNRESOLVED", "reason": "Generic adapter has no UM registry"}
    if not (root / "src/core/formal_traceability_spine.py").is_file():
        return {"status": "blocked", "units": [], "correspondence": "UNRESOLVED",
                "reason": "UM formal registry is missing"}
    destination = directory / "snapshot.json"
    script = (
        "import json,sys; "
        "from src.core import formal_traceability_spine as s; "
        "from src.core.lean_python_bridge_ir import build_formal_unit_ir; "
        "from src.core import formal_bridge_schema as b; "
        "data={'status':'captured','correspondence':'UNRESOLVED',"
        "'rows':s.TRACEABILITY_ROWS,'lanes':s.PRIMARY_LANES,"
        "'units':build_formal_unit_ir(rows=s.TRACEABILITY_ROWS,primary_lanes=s.PRIMARY_LANES),"
        "'schema':{'layers':b.BRIDGE_ARCHITECTURE_LAYERS,"
        "'certificates':b.CERTIFICATE_TYPES,'float_policy':b.NO_FLOAT_PROMOTION_POLICY}}; "
        "open(sys.argv[1],'x',encoding='utf-8').write(json.dumps(data,sort_keys=True))"
    )
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(root)
    result = execute([sys.executable, "-c", script, str(destination)], root, directory,
                     min(config["timeout_seconds"], 60), environment, stream=False)
    if result["returncode"] != 0 or result["timed_out"] or result["error"] or not destination.is_file():
        return {"status": "blocked", "units": [], "correspondence": "UNRESOLVED",
                "reason": "Could not snapshot the existing formal registry"}
    return read_json(destination)


def build(root: Path, directory: Path, config: dict) -> None:
    lean = config["lean"]
    write_json(directory / "request.json", lean)
    lake = shutil.which("lake")
    reason = "lake is not installed"
    if lake and Path(lake).resolve().name == "elan":
        pin_file = root / lean["project"] / "lean-toolchain"
        pin = pin_file.read_text(encoding="utf-8").strip() if pin_file.is_file() else ""
        if not pin or "/" not in pin or ":" not in pin or ".." in pin:
            lake = None
            reason = "Cannot resolve a locally installed pinned Lean toolchain"
        else:
            folder = pin.replace("/", "--").replace(":", "---")
            home = Path(os.environ.get("ELAN_HOME", str(Path.home() / ".elan")))
            physical = home / "toolchains" / folder / "bin" / "lake"
            lake = str(physical) if physical.is_file() else None
            reason = "Pinned Lean toolchain is not installed; automatic provisioning is disabled"
    if not lake:
        write_json(directory / "build.json", {
            "status": "blocked", "reason": reason, "scope": lean["scope"],
            "targets": lean["targets"], "proof_claim": False,
        })
        if lean.get("inspection"):
            lean_adapter.blocked(directory / "inspection", lean["inspection"], reason)
        return
    command = [lake, "build", *lean["targets"]]
    result = execute(command, root / lean["project"], directory,
                     config["timeout_seconds"])
    write_json(directory / "build.json", {
        "status": "built" if result["returncode"] == 0 and not result["timed_out"]
        and not result["error"] else "blocked",
        "scope": lean["scope"], "targets": lean["targets"], "proof_claim": False,
    })
    if lean.get("inspection"):
        if result["returncode"] == 0 and not result["timed_out"] and not result["error"]:
            lean_adapter.inspect(root / lean["project"], directory / "inspection",
                                 lean["inspection"], lake, config["timeout_seconds"])
        else:
            lean_adapter.blocked(directory / "inspection", lean["inspection"],
                                 "Requested Lean build did not pass; inspection was not executed")


def evaluate_build(directory: Path, lean: dict | None, expected_root: str | None = None) -> dict:
    if lean is None:
        return {"status": "not_requested", "proof_claim": False, "scope": None, "targets": []}
    try:
        receipt = read_json(directory / "build.json")
        if read_json(directory / "request.json") != lean:
            raise ValueError("Lean build request mismatch")
        if receipt.get("scope") != lean["scope"] or receipt.get("targets") != lean["targets"] \
                or receipt.get("proof_claim") is not False:
            raise ValueError("Lean scope or proof boundary mismatch")
        if receipt.get("status") == "built":
            process = read_json(directory / "process.json")
            command = process.get("command", [])
            if len(command) < 2 or Path(command[0]).name != "lake" \
                    or command[1:] != ["build", *lean["targets"]] \
                    or process.get("returncode") != 0 or process.get("timed_out") \
                    or process.get("error") or (expected_root is not None
                    and process.get("cwd") != str(Path(expected_root) / lean["project"])):
                raise ValueError("Lean build has no successful bounded build receipt")
        elif receipt.get("status") != "blocked":
            raise ValueError("Invalid Lean build status")
        if lean.get("inspection"):
            inspection = lean_adapter.evaluate(directory / "inspection", lean["inspection"],
                                               str(Path(expected_root) / lean["project"])
                                               if expected_root else None)
            return {**receipt, "inspection": inspection}
        return receipt
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return {"status": "blocked", "reason": str(exc), "proof_claim": False,
                "scope": lean["scope"], "targets": lean["targets"]}


def coverage(snapshot: dict, lean_receipt: dict, executed_nodes: list[str]) -> dict:
    files = {node.split("::", 1)[0] for node in executed_nodes}
    units = []
    for unit in snapshot.get("units", []):
        lean = unit.get("lean", {})
        translation = unit.get("translation_contract", {})
        targets = lean_receipt.get("targets", [])
        built = lean_receipt["status"] == "built" and (
            lean_receipt.get("scope") == "full" or lean.get("build_target") in targets)
        units.append({
            "unit_id": unit.get("unit_id"), "declared_proof_class": unit.get("proof_class"),
            "python_tests_in_run": sorted(set(unit.get("python", {}).get("tests", [])) & files),
            "lean_build_covered": built, "correspondence": "UNRESOLVED",
            "normalization_contract": translation.get("normalization_contract", {}),
            "certificate_requirements": translation.get("certificate_contract", {}).get(
                "required_certificate_types", []),
            "proof_claim": False,
        })
    return {"registry_status": snapshot.get("status", "blocked"), "units": units,
            "lean_build": lean_receipt, "inspection": lean_receipt.get("inspection", {
                "status": "not_requested", "declarations": [], "proof_claim": False}),
            "correspondence": "UNRESOLVED", "proof_claim": False,
            "boundary": "Passing Python tests and Lean builds do not certify Python↔Lean "
                        "correspondence, discharge named axioms, or prove the physics."}
