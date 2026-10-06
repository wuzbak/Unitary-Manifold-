# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Canonical JSON encoding used for every hashed or signed EIGE object.

Rules (see ``docs/FORMATS.md``): UTF-8, keys sorted, no insignificant
whitespace, no floating-point numbers (floats are rejected because their
textual form is not stable across implementations).
"""

from __future__ import annotations

import json
from typing import Any


class CanonicalEncodingError(ValueError):
    """Raised when an object cannot be canonically encoded."""


def _reject_floats(obj: Any, path: str = "$") -> None:
    if isinstance(obj, bool) or obj is None or isinstance(obj, (int, str)):
        return
    if isinstance(obj, float):
        raise CanonicalEncodingError(f"floating-point value at {path} is not allowed in signed objects")
    if isinstance(obj, dict):
        for key, value in obj.items():
            if not isinstance(key, str):
                raise CanonicalEncodingError(f"non-string key at {path}")
            _reject_floats(value, f"{path}.{key}")
        return
    if isinstance(obj, (list, tuple)):
        for i, value in enumerate(obj):
            _reject_floats(value, f"{path}[{i}]")
        return
    raise CanonicalEncodingError(f"unsupported type {type(obj).__name__} at {path}")


def canonical_bytes(obj: Any) -> bytes:
    """Return the canonical UTF-8 JSON encoding of ``obj``."""
    _reject_floats(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
