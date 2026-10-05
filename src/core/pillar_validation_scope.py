# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Deduplicate synchronous validity dependencies within one outer evaluation."""

from collections.abc import Callable
from contextvars import ContextVar
from functools import wraps
from typing import Any

_VALIDITY_SCOPE: ContextVar[dict | None] = ContextVar("pillar_validity_scope", default=None)


def scoped_pillar_validity(method: Callable[[Any], bool]) -> Callable[[Any], bool]:
    """Evaluate each proxy once per dependency traversal, never across requests."""
    @wraps(method)
    def evaluate(self: Any) -> bool:
        results = _VALIDITY_SCOPE.get()
        token = None
        if results is None:
            results = {}
            token = _VALIDITY_SCOPE.set(results)
        key = (method, self)
        try:
            if key in results:
                # A cycle cannot establish validity.
                return results[key] is True
            results[key] = None
            result = method(self)
            results[key] = result
            return result
        finally:
            if token is not None:
                _VALIDITY_SCOPE.reset(token)

    return evaluate
