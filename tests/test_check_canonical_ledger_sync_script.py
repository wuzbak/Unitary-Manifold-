# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import importlib.util
from pathlib import Path


def test_tracked_patch_paths_include_rename_source_and_target():
    script_path = Path(__file__).resolve().parents[1] / "TOOLS" / "checks" / "check_canonical_ledger_sync.py"
    spec = importlib.util.spec_from_file_location("check_canonical_ledger_sync", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    paths = module._tracked_patch_paths(
        [
            "R100\tsrc/core/pillar1119_old_name.py\tsrc/core/pillar1119_new_name.py",
            "M\tsrc/core/sm_free_parameters.py",
        ]
    )
    assert paths == [
        "src/core/pillar1119_new_name.py",
        "src/core/pillar1119_old_name.py",
        "src/core/sm_free_parameters.py",
    ]
