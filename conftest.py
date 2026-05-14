"""
Repository-wide pytest path setup for nested Pentad packages.
"""

from __future__ import annotations

import os
import sys
from typing import Any

import pytest

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_PENTAD_DIR = os.path.join(_REPO_ROOT, "5-GOVERNANCE", "Unitary Pentad")

if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)


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
