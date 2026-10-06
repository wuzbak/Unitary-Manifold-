# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Deterministic supervised regression batching for oversized pytest suites."""

from __future__ import annotations

import shlex
import importlib.util
import ast
import math
from pathlib import Path
from typing import Any, Dict, List

_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FAST_BATCH_COUNT = 4
DEFAULT_FULL_CORE_BATCH_COUNT = 8
FAST_MARK_EXPRESSION = "not slow"
SLOW_MARK_EXPRESSION = "slow"
FAST_SUITE_PATH = "tests/"
CLAIMS_SUITE_PATH = "claims/"
RECYCLING_SUITE_PATH = "recycling/"
PENTAD_SUITE_PATH = "5-GOVERNANCE/Unitary Pentad/"
FULL_CORE_SUITE_PATHS = (
    FAST_SUITE_PATH,
    RECYCLING_SUITE_PATH,
    PENTAD_SUITE_PATH,
)
FAST_SUITE_EXCLUDED_FILES = {
    "tests/test_richardson_multitime.py",
}
COMPACTIFIED_PREFLIGHT_FILES = [
    "COMPACTIFICATION/test_maps.py",
    "tests/test_closure_batch1.py",
    "tests/test_closure_batch2.py",
    "tests/test_formal_bridge_schema.py",
    "tests/test_lean_python_bridge_ir.py",
    "tests/test_formal_traceability_spine.py",
    "tests/test_action_to_evolution_contract.py",
]
INTEGRATION_PREFLIGHT_FILES = [
    "tests/test_metric.py",
    "tests/test_action_derived_flow.py",
    "tests/test_evolution.py",
    "tests/test_dark_matter_geometry.py",
    "tests/test_boundary.py",
    "tests/test_fixed_point.py",
]

def discover_fast_suite_files() -> List[str]:
    """Return the deterministic sorted test-file list for the repository-root tests/ suite."""
    return [path for path in _discover_suite_files(FAST_SUITE_PATH)
            if path not in FAST_SUITE_EXCLUDED_FILES]


def _discover_suite_files(suite_path: str) -> List[str]:
    suite_root = _ROOT / suite_path.rstrip("/")
    if not suite_root.exists():
        return []
    return sorted(
        path.relative_to(_ROOT).as_posix()
        for pattern in ("test_*.py", "ALGEBRA_PROOF.py")
        for path in suite_root.rglob(pattern)
        if path.is_file()
        and not path.relative_to(_ROOT).as_posix().startswith("5-GOVERNANCE/Unitary Pentad/holon-zero/")
    )


def discover_full_core_suite_files() -> List[str]:
    """Return the deterministic sorted file list for the combined tests/recycling/pentad core."""
    combined: List[str] = []
    for suite_path in FULL_CORE_SUITE_PATHS:
        combined.extend(_discover_suite_files(suite_path))
    return sorted(combined)


def _partition_evenly(items: List[str], batch_count: int) -> List[List[str]]:
    if batch_count <= 0:
        raise ValueError("batch_count must be positive")
    if not items:
        return [[] for _ in range(batch_count)]
    base = len(items) // batch_count
    remainder = len(items) % batch_count
    partitions: List[List[str]] = []
    start = 0
    for index in range(batch_count):
        size = base + (1 if index < remainder else 0)
        stop = start + size
        partitions.append(items[start:stop])
        start = stop
    return partitions


def build_dependency_cost_batches(
    files: list[str],
    batch_count: int,
    durations: dict[str, float] | None = None,
) -> list[dict]:
    """Partition files without executing imports, keeping strongest shared costs together.

    Estimates are measured per-file seconds, not source-module timings. Static
    reachability is bounded and ignores external/dynamic imports. Each file
    chooses one strongest shared dependency rather than joining all intersecting
    families; otherwise common base modules would connect nearly the whole suite.
    """
    if isinstance(batch_count, bool) or not isinstance(batch_count, int) or batch_count <= 0:
        raise ValueError("batch_count must be a positive integer")

    def local_path(value: str) -> Path:
        if not isinstance(value, str) or not value:
            raise ValueError("paths must be nonempty repository-relative Python paths")
        path = Path(value)
        if (
            path.is_absolute() or ".." in path.parts or "\\" in value
            or path.as_posix() != value or path.suffix != ".py"
            or ".github" in path.parts
        ):
            raise ValueError(f"invalid repository-relative Python path: {value!r}")
        resolved = (_ROOT / path).resolve()
        if not resolved.is_relative_to(_ROOT.resolve()):
            raise ValueError(f"path escapes repository: {value!r}")
        return resolved

    if not isinstance(files, list) or any(not isinstance(path, str) for path in files):
        raise ValueError("files must be a list of repository-relative Python paths")
    if durations is not None and not isinstance(durations, dict):
        raise ValueError("durations must be a mapping of paths to positive finite seconds")
    costs: dict[str, float] = {}
    for path, value in (durations or {}).items():
        local_path(path)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"duration must be positive and finite: {path}")
        try:
            cost = float(value)
        except OverflowError as exc:
            raise ValueError(f"duration must be positive and finite: {path}") from exc
        if not math.isfinite(cost) or cost <= 0:
            raise ValueError(f"duration must be positive and finite: {path}")
        costs[path] = cost
    paths = sorted(set(files))
    if len(paths) != len(files):
        raise ValueError("files must contain unique paths")
    for path in paths:
        if not local_path(path).is_file():
            raise ValueError(f"test file does not exist: {path}")
    costs = {path: costs.get(path, 1.0) for path in paths}
    try:
        math.fsum(costs.values())
    except OverflowError as exc:
        raise ValueError("total estimated duration must be finite") from exc
    explicit_roots = {
        "src.core.pillar952_observational_readiness_v4",
        "src.core.pillar982_architecture_limit_registry_runtime",
        "src.core.pillar987_uv_completion_compactification_layer",
        "src.core.pillar988_fully_coupled_kk_backreaction_engine",
        "src.core.pillar989_flavor_closure_geometric_layer",
    }
    generic_names = {
        "__init__", "base", "config", "constants", "evolution", "geometry",
        "metric", "units", "utils", "regression_supervision_plan",
    }
    parse_failures: set[str] = set()
    import_cache: dict[str, set[str]] = {}
    source_cache: dict[str, Path | None] = {}

    def source_for(module: str) -> Path | None:
        if module not in source_cache:
            if not module.startswith("src.core."):
                return None
            relative = module.replace(".", "/")
            candidates = (relative + ".py", relative + "/__init__.py")
            source_cache[module] = next(
                (local_path(candidate) for candidate in candidates
                 if local_path(candidate).is_file()), None,
            )
        return source_cache[module]

    def imports(path: Path, module: str = "") -> set[str]:
        key = path.relative_to(_ROOT.resolve()).as_posix()
        if key in import_cache:
            return import_cache[key]
        try:
            tree = ast.parse(path.read_bytes(), filename=key)
        except (OSError, SyntaxError, ValueError):
            parse_failures.add(key)
            import_cache[key] = set()
            return set()
        found: set[str] = set()
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    package = module.split(".") if path.name == "__init__.py" else module.split(".")[:-1]
                    if not module or node.level > len(package):
                        continue
                    base = ".".join(package[:len(package) - node.level + 1] + ([base] if base else []))
                names = [base, *(base + "." + alias.name for alias in node.names)]
            for name in names:
                if name.startswith("src.core.") and source_for(name) is not None:
                    found.add(name)
        import_cache[key] = found
        return found

    signatures: dict[str, set[str]] = {}
    truncated: list[str] = []
    for path in paths:
        seen: set[str] = set()
        frontier = imports(local_path(path))
        for _ in range(8):
            pending = sorted(frontier - seen)
            if not pending:
                break
            remaining = 256 - len(seen)
            if len(pending) > remaining:
                truncated.append(path)
            pending = pending[:remaining]
            if not pending:
                break
            seen.update(pending)
            frontier = set()
            for module in pending:
                source = source_for(module)
                if source is not None:
                    frontier.update(imports(source, module))
        if frontier - seen and path not in truncated:
            truncated.append(path)
        signatures[path] = seen
    users: dict[str, list[str]] = {}
    for path in paths:
        for module in sorted(signatures[path]):
            users.setdefault(module, []).append(path)
    # A broad non-pillar hub is not evidence of shared expensive initialization.
    candidates = {
        module for module, members in users.items()
        if len(members) > 1
        and module.rsplit(".", 1)[-1] not in generic_names
        and (
            module in explicit_roots or module.rsplit(".", 1)[-1].startswith("pillar")
            or len(members) <= max(8, math.ceil(len(paths) / 4))
        )
    }
    ranked = sorted(
        candidates,
        key=lambda module: (
            module not in explicit_roots,
            -math.fsum(costs[path] for path in users[module]),
            -len(users[module]), module,
        ),
    )
    grouped: dict[str, list[str]] = {}
    for path in paths:
        root = next((module for module in ranked if module in signatures[path]), "")
        grouped.setdefault(root or f"file:{path}", []).append(path)
    groups = [
        {
            "dependency_root": "" if root.startswith("file:") else root,
            "test_paths": members,
            "estimated_seconds": math.fsum(costs[path] for path in members),
        }
        for root, members in grouped.items()
    ]
    groups.sort(key=lambda group: (-group["estimated_seconds"], group["test_paths"]))
    assumptions = {
        "fallback_seconds_per_file": 1.0,
        "static_import_depth_limit": 8,
        "static_import_module_limit_per_file": 256,
        "grouping": "strongest shared explicit costly root, then aggregate file cost; no group splitting",
        "estimates": "sum of per-file durations, not measured import costs; unknown files use fallback",
        "imports": "AST-only local src.core imports; no execution, dynamic or external imports",
        "generic_hubs": "common base names and broad non-pillar hubs excluded as grouping roots",
        "unparsed_paths": sorted(parse_failures),
        "truncated_test_paths": sorted(truncated),
    }
    batches = [
        {
            "batch_index": index, "batch_count": batch_count, "test_paths": [],
            "file_count": 0, "estimated_seconds": 0.0, "dependency_groups": [],
            "assumptions": dict(assumptions),
        }
        for index in range(batch_count)
    ]
    for group in groups:
        batch = min(batches, key=lambda item: (item["estimated_seconds"], item["batch_index"]))
        batch["dependency_groups"].append(group)
        batch["test_paths"].extend(group["test_paths"])
        batch["estimated_seconds"] = math.fsum(
            item["estimated_seconds"] for item in batch["dependency_groups"]
        )
    for batch in batches:
        batch["test_paths"].sort()
        batch["file_count"] = len(batch["test_paths"])
    return batches


def pytest_xdist_available() -> bool:
    """Return whether pytest-xdist is importable in the current environment."""
    return importlib.util.find_spec("xdist") is not None


def build_fast_suite_batches(batch_count: int = DEFAULT_FAST_BATCH_COUNT) -> List[Dict[str, Any]]:
    """Return deterministic supervised file batches for the non-slow tests/ suite."""
    files = discover_fast_suite_files()
    partitions = _partition_evenly(files, batch_count)
    batches: List[Dict[str, Any]] = []
    for index, batch_files in enumerate(partitions):
        batches.append(
            {
                "batch_index": index,
                "batch_count": batch_count,
                "marker_expression": FAST_MARK_EXPRESSION,
                "test_paths": batch_files,
                "file_count": len(batch_files),
                "first_file": batch_files[0] if batch_files else "",
                "last_file": batch_files[-1] if batch_files else "",
            }
        )
    return batches


def build_full_core_batches(batch_count: int = DEFAULT_FULL_CORE_BATCH_COUNT) -> List[Dict[str, Any]]:
    """Return deterministic supervised file batches for the full tests/recycling/pentad core."""
    files = discover_full_core_suite_files()
    partitions = _partition_evenly(files, batch_count)
    batches: List[Dict[str, Any]] = []
    for index, batch_files in enumerate(partitions):
        batches.append(
            {
                "batch_index": index,
                "batch_count": batch_count,
                "suite_paths": list(FULL_CORE_SUITE_PATHS),
                "test_paths": batch_files,
                "file_count": len(batch_files),
                "first_file": batch_files[0] if batch_files else "",
                "last_file": batch_files[-1] if batch_files else "",
            }
        )
    return batches


def _pytest_argv_from_paths(paths: List[str], marker_expression: str | None = None) -> List[str]:
    if not paths:
        return []
    command = ["python", "-m", "pytest"]
    if pytest_xdist_available():
        command.extend(["-n", "auto"])
    if marker_expression is not None:
        command.extend(["-m", marker_expression])
    command.extend([*paths, "-q"])
    return command


def _fast_batch_command_from_paths(paths: List[str]) -> str:
    return shlex.join(_pytest_argv_from_paths(paths, marker_expression=FAST_MARK_EXPRESSION))


def _full_core_batch_command_from_paths(paths: List[str]) -> str:
    return shlex.join(_pytest_argv_from_paths(paths, marker_expression=""))


def fast_batch_command(batch_index: int, batch_count: int = DEFAULT_FAST_BATCH_COUNT) -> str:
    """Return the canonical pytest command for one supervised non-slow batch."""
    batches = build_fast_suite_batches(batch_count=batch_count)
    if batch_index < 0 or batch_index >= len(batches):
        raise IndexError("batch_index out of range")
    return _fast_batch_command_from_paths(batches[batch_index]["test_paths"])


def fast_batch_argv(batch_index: int, batch_count: int = DEFAULT_FAST_BATCH_COUNT) -> List[str]:
    """Return the canonical pytest argv for one supervised non-slow batch."""
    batches = build_fast_suite_batches(batch_count=batch_count)
    if batch_index < 0 or batch_index >= len(batches):
        raise IndexError("batch_index out of range")
    return _pytest_argv_from_paths(
        batches[batch_index]["test_paths"],
        marker_expression=FAST_MARK_EXPRESSION,
    )


def full_core_batch_command(
    batch_index: int,
    batch_count: int = DEFAULT_FULL_CORE_BATCH_COUNT,
) -> str:
    """Return the canonical pytest command for one supervised full-core batch."""
    batches = build_full_core_batches(batch_count=batch_count)
    if batch_index < 0 or batch_index >= len(batches):
        raise IndexError("batch_index out of range")
    return _full_core_batch_command_from_paths(batches[batch_index]["test_paths"])


def full_core_batch_argv(
    batch_index: int,
    batch_count: int = DEFAULT_FULL_CORE_BATCH_COUNT,
) -> List[str]:
    """Return the canonical pytest argv for one supervised full-core batch."""
    batches = build_full_core_batches(batch_count=batch_count)
    if batch_index < 0 or batch_index >= len(batches):
        raise IndexError("batch_index out of range")
    return _pytest_argv_from_paths(batches[batch_index]["test_paths"], marker_expression="")


def compactified_preflight_command() -> str:
    """Return the canonical compactified preflight command."""
    return shlex.join(compactified_preflight_argv())


def compactified_preflight_argv() -> List[str]:
    """Return the canonical compactified preflight argv."""
    return ["python", "-m", "pytest", *COMPACTIFIED_PREFLIGHT_FILES, "-q"]


def integration_preflight_argv() -> List[str]:
    """Run the coupled core in one process, including slow tests; not a universe validation."""
    return ["python", "-m", "pytest", *INTEGRATION_PREFLIGHT_FILES, "-m", "", "-q"]


def build_regression_supervision_plan(
    batch_count: int = DEFAULT_FAST_BATCH_COUNT,
    full_core_batch_count: int = DEFAULT_FULL_CORE_BATCH_COUNT,
) -> Dict[str, Any]:
    """Return the machine-readable supervised regression plan."""
    return build_regression_supervision_plan_with_full_core_count(
        batch_count=batch_count,
        full_core_batch_count=full_core_batch_count,
    )


def build_regression_supervision_plan_with_full_core_count(
    batch_count: int = DEFAULT_FAST_BATCH_COUNT,
    full_core_batch_count: int = DEFAULT_FULL_CORE_BATCH_COUNT,
) -> Dict[str, Any]:
    """Return the machine-readable supervised regression plan."""
    batches = build_fast_suite_batches(batch_count=batch_count)
    all_files = [path for batch in batches for path in batch["test_paths"]]
    discovered = discover_fast_suite_files()
    unique_files = sorted(set(all_files))
    full_core_batches = build_full_core_batches(batch_count=full_core_batch_count)
    full_core_files = [path for batch in full_core_batches for path in batch["test_paths"]]
    full_core_discovered = discover_full_core_suite_files()
    full_core_unique = sorted(set(full_core_files))
    remaining_canonical_suites: Dict[str, str] = {
        "slow": f'python -m pytest {FAST_SUITE_PATH} -m "{SLOW_MARK_EXPRESSION}" -q',
        "recycling": f"python -m pytest {RECYCLING_SUITE_PATH} -q",
        "pentad": f'python -m pytest "{PENTAD_SUITE_PATH}" -q',
        "full": f'python3 -m pytest {FAST_SUITE_PATH} {RECYCLING_SUITE_PATH} "{PENTAD_SUITE_PATH}" -m "" -q',
    }
    if (_ROOT / CLAIMS_SUITE_PATH.rstrip("/")).is_dir():
        remaining_canonical_suites["claims"] = f"python -m pytest {CLAIMS_SUITE_PATH} -q"
    return {
        "default_fast_batch_count": batch_count,
        "compactified_preflight": {
            "test_paths": list(COMPACTIFIED_PREFLIGHT_FILES),
            "command": compactified_preflight_command(),
        },
        "integration_preflight": {
            "test_paths": list(INTEGRATION_PREFLIGHT_FILES),
            "command": shlex.join(integration_preflight_argv()),
            "execution": "shared_process",
            "scope": "software integration; not physical-time evolution or empirical validation",
        },
        "supervised_fast_suite": {
            "suite_path": FAST_SUITE_PATH,
            "marker_expression": FAST_MARK_EXPRESSION,
            "batches": batches,
            "batch_commands": [
                _fast_batch_command_from_paths(batch["test_paths"])
                for batch in batches
            ],
        },
        "supervised_full_core_suite": {
            "suite_paths": list(FULL_CORE_SUITE_PATHS),
            "default_batch_count": full_core_batch_count,
            "batches": full_core_batches,
            "batch_commands": [
                _full_core_batch_command_from_paths(batch["test_paths"])
                for batch in full_core_batches
            ],
        },
        "remaining_canonical_suites": remaining_canonical_suites,
        "scope": {
            "full_core_includes_slow": True,
            "file_partition_is_not_execution_evidence": True,
            "product_test_paths_outside_full_core": _discover_suite_files("12-AZ-IP/"),
            "other_test_paths_outside_full_core": (
                _discover_suite_files("COMPACTIFICATION/")
                + _discover_suite_files("proof/")
                + (["ALGEBRA_PROOF.py"] if (_ROOT / "ALGEBRA_PROOF.py").is_file() else [])
            ),
        },
        "supervision": {
            "coverage_matches_discovery": all_files == discovered,
            "all_files_unique": len(unique_files) == len(all_files),
            "discovered_file_count": len(discovered),
            "batched_file_count": len(all_files),
            "full_core_coverage_matches_discovery": full_core_files == full_core_discovered,
            "full_core_all_files_unique": len(full_core_unique) == len(full_core_files),
            "full_core_discovered_file_count": len(full_core_discovered),
            "full_core_batched_file_count": len(full_core_files),
        },
    }


__all__ = [
    "COMPACTIFIED_PREFLIGHT_FILES",
    "INTEGRATION_PREFLIGHT_FILES",
    "DEFAULT_FAST_BATCH_COUNT",
    "DEFAULT_FULL_CORE_BATCH_COUNT",
    "FAST_MARK_EXPRESSION",
    "FULL_CORE_SUITE_PATHS",
    "build_fast_suite_batches",
    "build_full_core_batches",
    "build_regression_supervision_plan",
    "build_regression_supervision_plan_with_full_core_count",
    "compactified_preflight_argv",
    "compactified_preflight_command",
    "discover_fast_suite_files",
    "discover_full_core_suite_files",
    "fast_batch_argv",
    "fast_batch_command",
    "full_core_batch_argv",
    "full_core_batch_command",
    "integration_preflight_argv",
]
