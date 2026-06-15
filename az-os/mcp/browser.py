# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/mcp/browser.py — MCP Browser Server

Provides agents with a headless browser for academic web research.
Sprint 2: HTTP-only implementation using urllib (no browser binary required).
Sprint 3: Playwright integration for JavaScript-rendered pages.

Allowed domains (whitelist):
  - arxiv.org, export.arxiv.org
  - nasa.gov, ui.adsabs.harvard.edu
  - github.com (read-only)
  - zenodo.org
  - api.search.brave.com

Blocked:
  - All other domains (default-deny)
  - Any URL containing credentials or tokens in query string

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from urllib.error import URLError

ALLOWED_DOMAINS = {
    "arxiv.org",
    "export.arxiv.org",
    "nasa.gov",
    "ui.adsabs.harvard.edu",
    "github.com",
    "raw.githubusercontent.com",
    "zenodo.org",
    "api.search.brave.com",
    "openalex.org",
}

# Rate limiting: minimum seconds between requests to the same domain
MIN_INTERVAL_S = 1.0
_last_request: dict[str, float] = {}

USER_AGENT = "AxiomZero/0.1 (academic research agent; +https://github.com/wuzbak/Unitary-Manifold-)"


class MCPBrowserError(Exception):
    """Raised when a browser request is blocked or fails."""


@dataclass
class FetchResult:
    url: str
    status_code: int
    content: str
    content_type: str
    duration_s: float
    blocked: bool = False
    block_reason: str = ""


class MCPBrowserServer:
    """
    MCP Browser Server — safe web fetching for academic research.

    Usage::

        browser = MCPBrowserServer()
        result = browser.fetch("https://export.arxiv.org/abs/2503.12345")
        print(result.content[:1000])
    """

    def __init__(self) -> None:
        self._request_log: list[dict] = []

    def fetch(self, url: str, timeout: int = 15) -> FetchResult:
        """
        Fetch a URL.  Returns FetchResult.  Never raises on HTTP error.

        Blocked if:
          - Domain not in allowlist
          - Rate limit exceeded (< 1s since last request to this domain)
          - URL contains suspicious query params (tokens, passwords)
        """
        # Validate
        block_reason = self._validate_url(url)
        if block_reason:
            result = FetchResult(url=url, status_code=0, content="",
                                 content_type="", duration_s=0.0,
                                 blocked=True, block_reason=block_reason)
            self._log(result)
            return result

        # Rate limiting
        domain = urlparse(url).netloc
        now = time.time()
        last = _last_request.get(domain, 0.0)
        wait = MIN_INTERVAL_S - (now - last)
        if wait > 0:
            time.sleep(wait)
        _last_request[domain] = time.time()

        start = time.time()
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=timeout) as resp:
                content_bytes = resp.read(1024 * 512)  # max 512 KiB
                content = content_bytes.decode("utf-8", errors="replace")
                content_type = resp.headers.get("Content-Type", "")
                status_code = resp.status
        except URLError as exc:
            duration = time.time() - start
            result = FetchResult(url=url, status_code=0, content="",
                                 content_type="", duration_s=duration,
                                 blocked=False, block_reason=str(exc))
            self._log(result)
            return result
        except Exception as exc:
            duration = time.time() - start
            result = FetchResult(url=url, status_code=500, content="",
                                 content_type="", duration_s=duration,
                                 blocked=False, block_reason=str(exc))
            self._log(result)
            return result

        duration = time.time() - start
        result = FetchResult(
            url=url,
            status_code=status_code,
            content=content,
            content_type=content_type,
            duration_s=duration,
        )
        self._log(result)
        return result

    def request_log(self) -> list[dict]:
        return list(self._request_log)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _validate_url(self, url: str) -> str:
        """Return a block reason string, or empty string if URL is permitted."""
        try:
            parsed = urlparse(url)
        except Exception:
            return "invalid URL"

        if parsed.scheme not in ("http", "https"):
            return f"scheme '{parsed.scheme}' not permitted"

        domain = parsed.netloc.lower()
        # Remove port if present
        domain = domain.split(":")[0]

        if not any(domain == d or domain.endswith("." + d) for d in ALLOWED_DOMAINS):
            return f"domain '{domain}' not in browser allowlist"

        # Block tokens in query string
        query = parsed.query.lower()
        suspicious = ["token=", "key=", "secret=", "api_key="]
        for s in suspicious:
            if s in query:
                return f"URL contains suspicious query parameter '{s}'"

        return ""

    def _log(self, result: FetchResult) -> None:
        self._request_log.append({
            "timestamp": time.time(),
            "url": result.url,
            "status_code": result.status_code,
            "blocked": result.blocked,
            "block_reason": result.block_reason,
            "duration_s": result.duration_s,
        })
