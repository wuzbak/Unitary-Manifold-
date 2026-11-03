# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""AZ Live-Data Harness — Product 40.

The generic fetch/verdict helpers remain available, and the product
includes a validated, read-only integration with the public USGS
earthquake feed. The live adapter reports source timestamps and staleness;
it never substitutes offline observations when the feed fails.
"""

from .harness import (
    FetchSource,
    FetchResult,
    fetch_with_fallback,
    VerdictLabel,
    Verdict,
    compute_verdict,
)
from .usgs_adapter import LiveDataError, USGS_FEED_URL, fetch_earthquake_summary
from .api import API_ENDPOINTS, dispatch_api_request

__all__ = [
    "FetchSource",
    "FetchResult",
    "fetch_with_fallback",
    "VerdictLabel",
    "Verdict",
    "compute_verdict",
    "LiveDataError",
    "USGS_FEED_URL",
    "fetch_earthquake_summary",
    "API_ENDPOINTS",
    "dispatch_api_request",
]

__version__ = "1.2.0"
