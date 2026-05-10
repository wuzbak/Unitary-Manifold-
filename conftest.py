"""
Repository-wide pytest path setup for nested Pentad packages.
"""

from __future__ import annotations

import os
import sys


_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_PENTAD_DIR = os.path.join(_REPO_ROOT, "5-GOVERNANCE", "Unitary Pentad")

if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)
