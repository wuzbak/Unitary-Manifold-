# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Formal Verification Library — Product 38.

Phase 1 of article-354 direction #11: a generalized, templated Z3
safety-property checker library, factored out of
`src/core/z3_pentad_checker.py`'s four hard-coded Pentad checks.

Epistemic status: the generic `SafetyProperty`/`run_property`/`run_suite`
API in `checker.py` is the deliverable. `pentad_example.py` reproduces the
Pentad's own four checks using this template as a worked example / test
fixture — it does not replace `src/core/z3_pentad_checker.py`, which
remains the canonical Pentad checker.
"""

from ._repo import ensure_repo_on_path

ensure_repo_on_path()

from .checker import (
    Z3_AVAILABLE,
    require_z3,
    SafetyProperty,
    CheckResult,
    run_property,
    run_suite,
)
from .pentad_example import PENTAD_SAFETY_PROPERTIES
from .api import API_ENDPOINTS, dispatch_api_request

__all__ = [
    "Z3_AVAILABLE",
    "require_z3",
    "SafetyProperty",
    "CheckResult",
    "run_property",
    "run_suite",
    "PENTAD_SAFETY_PROPERTIES",
    "API_ENDPOINTS",
    "dispatch_api_request",
]

__version__ = "1.1.0"
