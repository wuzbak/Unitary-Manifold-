# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1091_lean_python_bridge_hardening import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    lean_python_bridge_hardening,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1091
    assert PILLAR_GATE == 'LEAN_PYTHON_BRIDGE_HARDENING'
    assert PILLAR_STATUS == 'LEAN_PYTHON_BRIDGE_HARDENING_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1092


def test_bridge_registry_contract() -> None:
    report = lean_python_bridge_hardening()
    assert report['outcome'] in {'LEAN_PYTHON_BRIDGE_HARDENING_READY', 'LEAN_PYTHON_BRIDGE_HARDENING_BLOCKED'}
    assert report['runtime_alignment']['mode'] in {'MANUAL_PORT_WITH_TRACEABILITY', 'DIRECT_OR_HYBRID_INTEGRATION'}
    assert any(row['bridge_class'] == 'runtime_heuristic' for row in report['bridge_registry'])
