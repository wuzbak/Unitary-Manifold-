# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
from pathlib import Path

def test_legacy_layers_present():
    root = Path(__file__).resolve().parents[1]
    for rel in ["managers/m1_geometry.py", "mcp/filesystem.py", "phi_decision_engine.py", "AxiomZero/core/agent_core.py", "az_os/agent_core.py"]:
        assert (root / rel).exists(), rel
