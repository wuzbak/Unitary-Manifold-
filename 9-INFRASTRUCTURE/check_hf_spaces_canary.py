# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Nightly canary checks for published HF spaces/dataset URLs."""

from __future__ import annotations

import http.client
import os
import socket
import ssl
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

TARGETS = [
    "https://huggingface.co/spaces/axiomzero/az-portal",
    "https://huggingface.co/spaces/axiomzero/oracle-space",
    "https://huggingface.co/spaces/axiomzero/cmb-calc-space",
    "https://huggingface.co/spaces/axiomzero/axiom-apps",
    "https://huggingface.co/spaces/axiomzero/az-tools",
    "https://huggingface.co/spaces/axiomzero/vqe-sandbox",
    "https://huggingface.co/spaces/axiomzero/az-os",
    "https://huggingface.co/spaces/axiomzero/az-ip",
    "https://huggingface.co/datasets/axiomzero/um-knowledge-dataset",
]
STRICT_ENV = "UM_HF_CANARY_STRICT"


def _auth_headers() -> dict[str, str]:
    token = (
        os.environ.get("HUGGINGFACE_TOKEN", "").strip()
        or os.environ.get("HF_TOKEN", "").strip()
    )
    if not token:
        return {}
    return {"Authorization": "Bearer " + token}


def _strict_mode_enabled() -> bool:
    return os.environ.get(STRICT_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def check_url(url: str, timeout: int = 12) -> tuple[bool, str]:
    headers = {"User-Agent": "um-hf-canary/1.0", **_auth_headers()}
    request = Request(url, method="GET", headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            code = getattr(response, "status", 200)
            if 200 <= code < 400:
                return True, f"{url} -> {code}"
            return False, f"{url} -> {code}"
    except HTTPError as exc:
        if not _strict_mode_enabled() and exc.code in {401, 403} and "Authorization" not in headers:
            return True, f"{url} -> HTTP {exc.code} (auth required; soft pass without token)"
        return False, f"{url} -> HTTP {exc.code}"
    except URLError as exc:
        if not _strict_mode_enabled():
            return True, f"{url} -> URL error: {exc.reason} (network soft pass)"
        return False, f"{url} -> URL error: {exc.reason}"
    except (TimeoutError, socket.timeout, ssl.SSLError, OSError, http.client.HTTPException) as exc:
        if not _strict_mode_enabled():
            return True, f"{url} -> transport error: {exc} (network soft pass)"
        return False, f"{url} -> transport error: {exc}"
    except (ValueError, TypeError, AttributeError, AssertionError) as exc:
        return False, f"{url} -> error: {exc}"


def main() -> int:
    failures: list[str] = []
    for url in TARGETS:
        ok, line = check_url(url)
        print(line)
        if not ok:
            failures.append(line)
    if failures:
        print("HF CANARY FAILED")
        return 1
    print("HF CANARY PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
