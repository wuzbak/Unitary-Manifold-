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


def _no_float(text: str) -> Any:
    raise CanonicalEncodingError(f"floating-point literal {text!r} is not allowed")


def _no_constant(text: str) -> Any:
    raise CanonicalEncodingError(f"non-finite literal {text!r} is not allowed")


_DECODER = json.JSONDecoder(parse_float=_no_float, parse_constant=_no_constant)
_ENCODER = json.JSONEncoder(sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def decode_canonical(data: bytes) -> Any:
    """Parse ``data`` and return the object only if ``data`` is exactly its canonical encoding.

    Floats and non-finite constants are rejected during parsing, so the result
    is safe to re-encode without a separate validation walk.  Raises
    :class:`CanonicalEncodingError` (or ``ValueError``) when the input is not
    canonical JSON.
    """
    try:
        text = data.decode("utf-8")
        obj = _DECODER.decode(text)
    except UnicodeDecodeError as exc:
        raise CanonicalEncodingError("entry is not valid UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise CanonicalEncodingError(f"invalid JSON: {exc}") from exc
    if _ENCODER.encode(obj) != text:
        raise CanonicalEncodingError("entry is not in canonical form")
    return obj
