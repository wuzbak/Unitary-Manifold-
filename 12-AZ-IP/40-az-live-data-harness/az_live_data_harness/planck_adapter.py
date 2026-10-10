# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Real adapter demonstration: wrap `src/data/fetch_planck.py`'s Planck
2018 n_s comparison through the generic harness, attempting a real
(network-dependent) live fetch first and falling back to the module's
own hard-coded best-fit values on failure — exercising the fallback path
honestly rather than assuming it.
"""

from __future__ import annotations

import json
from urllib import request

from ._repo import ensure_repo_on_path

_REPO_ROOT = ensure_repo_on_path()

from src.data.fetch_planck import PLANCK_2018_BESTFIT

from .harness import FetchResult, Verdict, compute_verdict, fetch_with_fallback

#: Same (unreachable without real network access) ESA Planck Legacy
#: Archive endpoint `fetch_planck.py` names but never actually calls.
_PLA_ENDPOINT = "https://pla.esac.esa.int/pla/"


def _attempt_live_fetch_n_s() -> float:
    """Attempt a real network call for Planck n_s. This endpoint does not
    serve a simple JSON n_s value in reality (ESA's PLA requires an
    authenticated query), so this call is expected to fail in virtually
    every environment, including this sandboxed one — which is exactly
    why `fetch_planck.py` never implemented it and always returns the
    hard-coded fallback instead. We attempt it anyway so the fallback
    path in the harness is genuinely exercised rather than mocked."""
    with request.urlopen(_PLA_ENDPOINT, timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
        return float(payload["n_s"])


def fetch_planck_n_s_via_harness() -> FetchResult:
    """Fetch Planck 2018 n_s through the generic harness, falling back to
    `PLANCK_2018_BESTFIT['n_s']` on any failure."""
    return fetch_with_fallback(_attempt_live_fetch_n_s, PLANCK_2018_BESTFIT["n_s"])


def planck_n_s_verdict(um_ns: float = 0.9635) -> Verdict:
    """Compare the UM n_s prediction against the harness-fetched Planck
    value, through the generic `compute_verdict()`."""
    fetch_result = fetch_planck_n_s_via_harness()
    return compute_verdict(
        predicted=um_ns,
        measured=fetch_result.value,
        sigma=PLANCK_2018_BESTFIT["n_s_sigma"],
        note=f"source={fetch_result.source.value}",
    )
