# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Compatibility namespace for the canonical AZ-IP UM-ARTS product."""

import sys
from pathlib import Path

_product = Path(__file__).resolve().parents[2] / "12-AZ-IP" / "26-um-arts"
if str(_product) not in sys.path:
    sys.path.insert(0, str(_product))

from um_arts import VERSION, __path__  # noqa: F401
