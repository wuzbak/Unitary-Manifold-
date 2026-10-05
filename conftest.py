"""
Repository-wide pytest path setup for nested Pentad packages.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
import types
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_PENTAD_DIR = os.path.join(_REPO_ROOT, "5-GOVERNANCE", "Unitary Pentad")
_TRAINING_RUNTIME_ENV = "MERLIN_TRAINING_RUNTIME_DIR"


def _start_training_runtime(config: Any) -> None:
    """Isolate persisted training state before any test modules are imported."""
    original = os.environ.get(_TRAINING_RUNTIME_ENV)
    if original is not None:
        if not original.strip():
            raise pytest.UsageError(f"{_TRAINING_RUNTIME_ENV} must not be empty")
        runtime_path = Path(original).expanduser().resolve()
        if runtime_path.is_relative_to(Path(_REPO_ROOT).resolve()):
            raise pytest.UsageError(f"{_TRAINING_RUNTIME_ENV} must be outside the repository for pytest")
    worker = hasattr(config, "workerinput")
    if not worker and getattr(getattr(config, "option", None), "numprocesses", None):
        # The xdist controller does not collect; workers own independent state.
        return
    if original is not None and not worker:
        return
    runtime = tempfile.TemporaryDirectory(prefix="merlin-training-pytest-")
    config._merlin_training_runtime = runtime
    config._merlin_training_runtime_original = original
    config.add_cleanup(lambda: _finish_training_runtime(config))
    try:
        if original is not None:
            for name in (
                "three_lane_execution_bundle.json",
                "lane_e_runtime_profiles.json",
                "performance_gate_history.json",
            ):
                source = runtime_path / name
                if source.is_file():
                    shutil.copy2(source, Path(runtime.name) / name)
        os.environ[_TRAINING_RUNTIME_ENV] = runtime.name
    except BaseException:
        _finish_training_runtime(config)
        raise


def _finish_training_runtime(config: Any) -> None:
    runtime = getattr(config, "_merlin_training_runtime", None)
    if runtime is not None:
        try:
            runtime.cleanup()
        finally:
            original = config._merlin_training_runtime_original
            if original is None:
                os.environ.pop(_TRAINING_RUNTIME_ENV, None)
            else:
                os.environ[_TRAINING_RUNTIME_ENV] = original
            config._merlin_training_runtime = None


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    _start_training_runtime(session.config)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    _finish_training_runtime(session.config)

if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

# Mirror docs path with copied tests; canonical executable package is holon_zero/.
collect_ignore_glob = [
    "5-GOVERNANCE/Unitary Pentad/holon-zero/test_*.py",
]

_APP_ROOTS = [
    os.path.join(_REPO_ROOT, '12-AZ-IP', '11-terra-os'),
    os.path.join(_REPO_ROOT, '12-AZ-IP', '12-lithos-os'),
    os.path.join(_REPO_ROOT, '12-AZ-IP', '04-um-sos'),
    os.path.join(_REPO_ROOT, '12-AZ-IP', '05-uos-kernel'),
]

for _app_root in _APP_ROOTS:
    if _app_root not in sys.path:
        sys.path.insert(0, _app_root)

for _pkg_name, _pkg_root in {
    'terra': os.path.join(_REPO_ROOT, '12-AZ-IP', '11-terra-os'),
    'lithic': os.path.join(_REPO_ROOT, '12-AZ-IP', '12-lithos-os'),
}.items():
    if _pkg_name not in sys.modules:
        _pkg = types.ModuleType(_pkg_name)
        _pkg.__path__ = [_pkg_root]
        sys.modules[_pkg_name] = _pkg


def _is_pentad_item(item: Any) -> bool:
    node_path = str(getattr(item, "fspath", ""))
    return "/5-GOVERNANCE/Unitary Pentad/" in node_path.replace("\\", "/")


def _fixture_defined_in_pentad(fixture_def: Any) -> bool:
    baseid = str(getattr(fixture_def, "baseid", "")).replace("\\", "/")
    return baseid.startswith("5-GOVERNANCE/Unitary Pentad/")


def pytest_collection_finish(session: pytest.Session) -> None:
    """Audit fixture scopes for Pentad xdist readiness.

    Runs once after collection is complete and before test execution starts.

    Policy:
    - Pentad-local session-scoped fixtures are blocked because they can hide
      unintended shared mutable state when moving to full ``-n auto`` runs.
    - Module/function scopes remain allowed.
    """
    pentad_items = [item for item in session.items if _is_pentad_item(item)]
    if not pentad_items:
        return

    session_scoped_violations = set()
    audited_fixture_keys = set()
    module_scoped_count = 0
    session_scoped_count = 0

    for item in pentad_items:
        fixture_info = getattr(item, "_fixtureinfo", None)
        fixture_map = getattr(fixture_info, "name2fixturedefs", {}) if fixture_info else {}
        for fixture_name, fixture_defs in fixture_map.items():
            for fixture_def in fixture_defs:
                if not _fixture_defined_in_pentad(fixture_def):
                    continue
                fixture_key = (
                    fixture_name,
                    getattr(fixture_def, "scope", "function"),
                    str(getattr(fixture_def, "baseid", "")),
                )
                if fixture_key in audited_fixture_keys:
                    continue
                audited_fixture_keys.add(fixture_key)

                scope = getattr(fixture_def, "scope", "function")
                if scope == "module":
                    module_scoped_count += 1
                if scope == "session":
                    session_scoped_count += 1
                    session_scoped_violations.add(f"{fixture_name} ({fixture_def.baseid})")

    if session_scoped_violations:
        msg = (
            "Unitary Pentad fixture-scope audit failed for xdist readiness: "
            "session-scoped Pentad fixtures are blocked to keep the suite safe for future full '-n auto' execution. "
            f"Found: {', '.join(sorted(session_scoped_violations))}"
        )
        raise pytest.UsageError(msg)

    tr = session.config.pluginmanager.get_plugin("terminalreporter")
    if tr is not None:
        tr.write_line(
            f"Pentad fixture-scope audit: PASS (module-scoped fixtures: {module_scoped_count}, session-scoped fixtures: {session_scoped_count})"
        )
