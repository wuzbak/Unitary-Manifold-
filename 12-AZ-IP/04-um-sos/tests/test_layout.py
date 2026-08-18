# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
from pathlib import Path

def test_um_sos_assets_present():
    root = Path(__file__).resolve().parents[1]
    for rel in ["backend/app.py", "frontend/index.html", "graph/dag.json", "registry/predictions.json", "scripts/build_graph.py", "scripts/build_registry.py"]:
        assert (root / rel).exists(), rel
