# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Live-Data Harness — Product 40.

Phase 1 of article-354 direction #13: a shared fetch -> normalize ->
fallback -> verdict harness, generalized from the repeated hand-rolled
pattern in `src/data/fetch_planck.py`,
`12-AZ-IP/21-geo-monitor/geo_monitor/engine/feeds.py`, and
`12-AZ-IP/19-falsification-observatory`'s routing functions.

Epistemic status: `planck_adapter.py` is a real, working adapter — not a
mock — demonstrating the harness against `fetch_planck.py`'s actual Planck
2018 n_s comparison, attempting a genuine network call that is expected
to (and does, in this sandboxed environment) fail, exercising the
fallback path honestly. Migrating the other two source modules
(`feeds.py`, `falsification_observatory`'s routing functions) to depend
on this harness directly is out of scope for this product; they remain
independent and canonical.
"""

from .harness import (
    FetchSource,
    FetchResult,
    fetch_with_fallback,
    VerdictLabel,
    Verdict,
    compute_verdict,
)
from .planck_adapter import fetch_planck_n_s_via_harness, planck_n_s_verdict
from .api import API_ENDPOINTS, dispatch_api_request

__all__ = [
    "FetchSource",
    "FetchResult",
    "fetch_with_fallback",
    "VerdictLabel",
    "Verdict",
    "compute_verdict",
    "fetch_planck_n_s_via_harness",
    "planck_n_s_verdict",
    "API_ENDPOINTS",
    "dispatch_api_request",
]

__version__ = "1.1.0"
