# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Read-only repository discovery; file inventory is not collection evidence."""

from __future__ import annotations

import ast
import configparser
import fnmatch
import hashlib
import os
import re
from pathlib import Path

from .evidence import EvidenceError, contained

EXCLUDED_DIRECTORIES = frozenset({
    ".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache", ".lake",
    "node_modules", "vendor", "vendors", "third_party", "third-party",
    "archive", "archives", "archived", "build", "dist", ".um-arts",
    ".um-arts-test-work", ".um-arts-assistance-work", ".um-arts-inventory-work",
    ".lean-library-check",
})
POLICY_SOURCES = (
    "pytest.ini", "conftest.py", "src/core/regression_supervision_plan.py",
    "TOOLS/checks/run_supervised_pytest_batch.py", "proof/README.md",
)
BOUNDARIES = [
    "Static candidate discovery only; pytest collection and execution have not occurred.",
    "Canonical file paths are identities, not a certification that imports or tests pass.",
    "Conftest hooks, optional dependencies, parametrization and plugins can change collection.",
    "Full filtering means explicit -m ''; skip/xfail and collection errors still require review.",
    "Excluded directories are not inspected; unclassified/uncovered candidates remain open.",
    "Lean builds and Python tests do not establish Python↔Lean correspondence or physics claims.",
]


def excluded_path(relative: str) -> bool:
    """Shared exclusion boundary, including agent instructions and private runtime data."""
    parts = Path(relative).parts
    return (
        any(part.lower() in EXCLUDED_DIRECTORIES for part in parts)
        or any(part.lower().startswith(("archive_", "archive-", "archived_", "archived-",
                                      "vendor_", "vendor-")) for part in parts)
        or any(part.lower().startswith(".um-arts-") for part in parts)
        or relative == ".github/agents"
        or relative.startswith(".github/agents/")
    )


def _walk(root: Path):
    for current, directories, files in os.walk(root, followlinks=False):
        parent = Path(current)
        for name in sorted(directories):
            path = parent / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or excluded_path(relative):
                directories.remove(name)
                yield relative, "excluded_directory"
        directories.sort()
        for name in sorted(files):
            path = parent / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                yield relative, "excluded_symlink"
            elif not excluded_path(relative):
                yield relative, "file"


def _literal_ignores(root: Path, paths: list[str]) -> tuple[list[dict], list[str]]:
    rules, warnings = [], []
    for relative in paths:
        try:
            path = contained(root, relative)
            if path.stat().st_size > 256 * 1024:
                warnings.append(f"{relative}: conftest exceeds static policy read bound")
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError) as exc:
            warnings.append(f"{relative}: static policy unavailable ({type(exc).__name__})")
            continue
        for node in tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if not isinstance(target, ast.Name) or target.id not in {
                    "collect_ignore", "collect_ignore_glob",
                }:
                    continue
                try:
                    values = ast.literal_eval(node.value)
                    if not isinstance(values, (list, tuple)) or not all(
                        isinstance(value, str) for value in values
                    ):
                        raise ValueError
                except (ValueError, TypeError):
                    warnings.append(f"{relative}: dynamic {target.id} requires pytest collection")
                    continue
                parent = Path(relative).parent
                for value in values:
                    rules.append({
                        "pattern": (parent / value).as_posix(),
                        "glob": target.id == "collect_ignore_glob",
                        "source": relative,
                    })
    return rules, warnings


def _suite_root(relative: str) -> tuple[str, str] | None:
    parts = Path(relative).parts
    if parts[0] == "tests":
        return "tests", "physics-and-integration"
    if parts[0] == "recycling":
        return "recycling", "recycling"
    if parts[:2] == ("5-GOVERNANCE", "Unitary Pentad"):
        return "5-GOVERNANCE/Unitary Pentad", "independent-governance"
    if parts[0] == "12-AZ-IP" and len(parts) > 2:
        # Separate nested test roots (e.g. desktop/tests) from embedded checks.
        if "tests" in parts[2:-1]:
            index = parts.index("tests", 2)
            return "/".join(parts[:index + 1]), "product"
        return "/".join(parts[:-1]), "product-embedded"
    if parts[0] == "claims" and len(parts) > 2:
        return "/".join(parts[:2]), "claim-regression"
    if parts[0] == "proof":
        return "proof", "isolated-formal-checks"
    if parts[0] == "COMPACTIFICATION":
        return "COMPACTIFICATION", "compactification-checks"
    if parts[0] == "lean4":
        return "lean4", "lean-python-checks"
    if parts[:2] == ("src", "core"):
        return "/".join(parts[:-1]), "embedded-core-checks"
    return None


def discover_inventory(root: str | Path) -> dict:
    """Discover canonical executable candidates without importing test or policy code."""
    root = Path(root).resolve()
    if not root.is_dir():
        raise EvidenceError("Repository root does not exist")
    entries = list(_walk(root))
    files = [path for path, kind in entries if kind == "file"]
    excluded = [{"path": path, "reason": kind} for path, kind in entries if kind != "file"]
    patterns = ["test_*.py"]
    warnings = []
    if "pytest.ini" in files:
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read_string(contained(root, "pytest.ini").read_text(encoding="utf-8"))
            patterns = parser.get("pytest", "python_files", fallback="test_*.py").split()
        except (OSError, configparser.Error) as exc:
            warnings.append(f"pytest.ini: unavailable ({type(exc).__name__}); fallback test_*.py")
    elif any(path in files for path in ["pyproject.toml", "tox.ini", "setup.cfg", ".pytest.ini"]):
        warnings.append("Non-pytest.ini discovery settings not parsed; confirm via engine collection")
    rules, policy_warnings = _literal_ignores(
        root, [path for path in files if Path(path).name == "conftest.py"])
    warnings.extend(policy_warnings)
    candidates = sorted(path for path in files if path.endswith(".py") and (
        any(fnmatch.fnmatchcase(Path(path).name, pattern) for pattern in patterns)
        or fnmatch.fnmatchcase(Path(path).name, "*_test.py")
        or path in {"proof/ALGEBRA_PROOF.py", "ALGEBRA_PROOF.py", "proof/VERIFY.py", "VERIFY.py"}
    ))
    groups, unclassified, uncovered = {}, [], []
    for relative in candidates:
        rule = next((rule for rule in rules if (
            fnmatch.fnmatchcase(relative, rule["pattern"]) if rule["glob"]
            else relative == rule["pattern"] or relative.startswith(rule["pattern"].rstrip("/") + "/")
        )), None)
        if rule:
            excluded.append({"path": relative, "reason": "conftest collection ignore", **rule})
            continue
        if relative in {"ALGEBRA_PROOF.py", "VERIFY.py"} and f"proof/{relative}" in files:
            excluded.append({"path": relative, "reason": "compatibility mirror",
                             "canonical": f"proof/{relative}"})
            continue
        # Known shipping-copy families only: identical arbitrary tests can exercise
        # different fixtures, so content equality alone is not a universal mirror rule.
        if relative.startswith(("12-AZ-IP/05-uos-kernel/", "12-AZ-IP/06-omega-synthesis/",
                                "12-AZ-IP/07-holon-zero/")):
            mirror = None
            basename = Path(relative).name
            if relative.startswith("12-AZ-IP/05-uos-kernel/") and basename.startswith("test_uos_"):
                mirror = "5-GOVERNANCE/Unitary Pentad/" + basename
            elif relative.startswith("12-AZ-IP/06-omega-synthesis/") and basename == "test_omega_synthesis.py":
                mirror = "5-GOVERNANCE/Unitary Pentad/omega/test_omega_synthesis.py"
            elif basename == "test_holon_zero_engine.py":
                mirror = "5-GOVERNANCE/Unitary Pentad/holon_zero/test_holon_zero_engine.py"
            elif basename == "test_holon_landscape.py":
                mirror = "5-GOVERNANCE/Unitary Pentad/holon_zero/subpillars/test_holon_landscape.py"
            elif basename == "test_holon_zero.py":
                mirror = "tests/test_holon_zero.py"
            if mirror and mirror in files and (
                contained(root, relative).read_bytes() == contained(root, mirror).read_bytes()
            ):
                excluded.append({"path": relative, "reason": "exact product mirror", "canonical": mirror})
                continue
        if not any(fnmatch.fnmatchcase(Path(relative).name, pattern) for pattern in patterns):
            uncovered.append({"path": relative, "reason": "not enabled by pytest python_files"})
            continue
        classification = _suite_root(relative)
        if classification is None:
            unclassified.append({"path": relative, "reason": "no canonical suite policy"})
            continue
        suite_root, kind = classification
        groups.setdefault((suite_root, kind), []).append(relative)
    suites = []
    for (suite_root, kind), paths in sorted(groups.items()):
        # The digest suffix prevents collisions between similarly slugged paths.
        name = re.sub(r"[^A-Za-z0-9_-]", "-", suite_root).strip("-")
        name += "-" + hashlib.sha256(suite_root.encode()).hexdigest()[:8]
        suites.append({"name": name, "root": suite_root, "kind": kind,
                       "paths": sorted(paths), "requires": [], "serial": True})
    lean_projects = sorted({
        Path(path).parent.as_posix() for path in files
        if Path(path).name in {"lakefile.lean", "lakefile.toml"}
    })
    declared_checks = [
        {
            "id": identifier, "path": path, "kind": "command",
            "command": ["python", path], "cwd": ".",
            "status": "declared-not-executed",
            "scope": "Selected conditional algebra/model checks only; not formal proof "
                     "or physical confirmation. Command capture is separate from pytest coverage.",
        }
        for identifier, path in [
            ("proof-algebra-command", "proof/ALGEBRA_PROOF.py"),
            ("proof-observable-consistency-command", "proof/VERIFY.py"),
        ] if path in files
    ]
    return {
        "schema_version": "um-arts-inventory-v1",
        "adapter": "um" if "src/core/formal_traceability_spine.py" in files else "generic",
        "status": "review-required",
        "suites": suites, "candidates": candidates,
        "excluded": sorted(excluded, key=lambda item: item["path"]),
        "unclassified": unclassified, "uncovered": uncovered,
        "declared_checks": declared_checks,
        "lean_projects": [{"project": path, "status": "not-built",
                           "scope": "unselected"} for path in lean_projects],
        "collection_policy": {"python_files": patterns, "ignore_rules": rules,
                              "sources": [path for path in POLICY_SOURCES if path in files],
                              "warnings": warnings,
                              "full_pytest_args": ["-m", ""]},
        "boundaries": BOUNDARIES.copy(),
    }


def execution_config(inventory: dict, selected: list[str] | None = None,
                     lean_project: str | None = None) -> dict:
    """Return a reviewable adapter config; collection/execution belong to the engine."""
    available = {suite["name"]: suite for suite in inventory["suites"]}
    if selected is None:
        selected = sorted(available)
    if not selected or len(selected) != len(set(selected)) or set(selected) - available.keys():
        raise EvidenceError("Select unique known suite identities")
    config = {
        "adapter": inventory.get("adapter", "generic"), "workers": 1, "timeout_seconds": 900,
        "pytest_args": ["-m", ""],
        "suites": [{key: available[name][key] for key in ["name", "paths", "requires", "serial"]}
                   for name in sorted(selected)],
    }
    if lean_project is not None:
        projects = {item["project"] for item in inventory["lean_projects"]}
        if lean_project not in projects:
            raise EvidenceError("Select a discovered Lean project")
        config["lean"] = {"project": lean_project, "scope": "full", "targets": []}
    return config


def selection_boundary(inventory: dict, selected: list[str] | None = None,
                       lean_project: str | None = None) -> dict:
    """Explicitly enumerate static coverage holes alongside an execution configuration."""
    config = execution_config(inventory, selected, lean_project)
    selected_names = {suite["name"] for suite in config["suites"]}
    return {
        "scope": "selected canonical candidates only; no repository-wide certification",
        "selected": sorted(selected_names),
        "unselected": [suite["name"] for suite in inventory["suites"]
                       if suite["name"] not in selected_names],
        "unclassified": inventory["unclassified"],
        "uncovered": inventory["uncovered"],
        "lean_unselected": [item["project"] for item in inventory["lean_projects"]
                            if item["project"] != lean_project],
        "unexecuted_declared_checks": [item["id"] for item in inventory["declared_checks"]],
        "collection_verified": False, "proof_claim": False,
    }
