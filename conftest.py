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

    Policy:
    - Pentad-local session-scoped fixtures are blocked because they can hide
      unintended shared mutable state when moving to full ``-n auto`` runs.
    - Module/function scopes remain allowed.
    """
    pentad_items = [item for item in session.items if _is_pentad_item(item)]
    if not pentad_items:
        return

    violations = set()
    audited_fixture_keys = set()
    module_scoped_count = 0

    for item in pentad_items:
        fixture_map = getattr(getattr(item, "_fixtureinfo", None), "name2fixturedefs", {}) or {}
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
                    violations.add(f"{fixture_name} ({fixture_def.baseid})")

    if violations:
        msg = (
            "Unitary Pentad fixture-scope audit failed for parallel readiness: "
            "session-scoped Pentad fixtures are not allowed before enabling full '-n auto'. "
            f"Found: {', '.join(sorted(violations))}"
        )
        raise pytest.UsageError(msg)

    tr = session.config.pluginmanager.get_plugin("terminalreporter")
    if tr is not None:
        tr.write_line(
            f"Pentad fixture-scope audit: PASS (module-scoped fixtures: {module_scoped_count}, session-scoped fixtures: 0)"
        )
