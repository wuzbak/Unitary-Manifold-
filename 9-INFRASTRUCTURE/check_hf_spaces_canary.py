# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Nightly canary checks for published HF spaces/dataset URLs."""

from __future__ import annotations

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


def check_url(url: str, timeout: int = 12) -> tuple[bool, str]:
    request = Request(url, method="GET", headers={"User-Agent": "um-hf-canary/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            code = getattr(response, "status", 200)
            if 200 <= code < 400:
                return True, f"{url} -> {code}"
            return False, f"{url} -> {code}"
    except HTTPError as exc:
        return False, f"{url} -> HTTP {exc.code}"
    except URLError as exc:
        return False, f"{url} -> URL error: {exc.reason}"
    except Exception as exc:
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

