# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Path spelling cannot weaken the offline context boundary."""

import pytest
from TOOLS.um_arts.assistance import _context_path
from TOOLS.um_arts.evidence import EvidenceError


@pytest.mark.parametrize("path", [
    ".github//agents/example.md",
    ".github/./agents/example.md",
    ".github///agents//example.py",
    ".um-arts//receipt.md",
    "vendor//internal.py",
])
def test_noncanonical_excluded_paths_are_rejected_without_reading(tmp_path, path):
    with pytest.raises(EvidenceError, match="allowlist"):
        _context_path(tmp_path, path)
