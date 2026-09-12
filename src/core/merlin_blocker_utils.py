# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Shared Merlin blocker compatibility helpers."""

from __future__ import annotations

from typing import Any


def effective_blocking_pass(blocker: dict[str, Any]) -> Any:
    blocking_pass = blocker.get("blocking_pass")
    if isinstance(blocking_pass, bool):
        return blocking_pass
    return blocker.get("pass")
