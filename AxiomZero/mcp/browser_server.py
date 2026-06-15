# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero mcp/browser_server.py — Scoped Playwright Browser Server

Provides headless browser for M6 web research, restricted to approved
academic domains only.  Not a general web proxy.

Approved domains:
  arxiv.org, ui.adsabs.harvard.edu, api.semanticscholar.org,
  inspirehep.net, zenodo.org, github.com, export.arxiv.org

Requires: pip install playwright && playwright install chromium

Gracefully degrades to httpx-based fallback if Playwright is absent.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

ALLOWED_DOMAINS = {
    "arxiv.org",
    "export.arxiv.org",
    "ui.adsabs.harvard.edu",
    "api.semanticscholar.org",
    "inspirehep.net",
    "zenodo.org",
    "github.com",
    "raw.githubusercontent.com",
    "api.adsabs.harvard.edu",
    "api.search.brave.com",
}

# Optional Playwright
try:
    from playwright.async_api import async_playwright  # type: ignore
    _PLAYWRIGHT = True
except ImportError:
    _PLAYWRIGHT = False


class BrowserServer:
    """
    Scoped headless browser for academic web research.

    Usage::

        browser = BrowserServer()
        result = await browser.fetch("https://arxiv.org/abs/2401.00001")
        text = result["text"]
    """

    def __init__(self, allowed_domains: Optional[set] = None):
        self.allowed_domains = allowed_domains or ALLOWED_DOMAINS
        self._browser = None
        self._playwright = None

    async def start(self) -> bool:
        """Start the Playwright browser (call once at boot)."""
        if not _PLAYWRIGHT:
            logger.warning("Playwright not installed — browser server unavailable")
            return False
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            logger.info("BrowserServer: Playwright chromium started")
            return True
        except Exception as exc:
            logger.error("BrowserServer start failed: %s", exc)
            return False

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def fetch(self, url: str, extract_text: bool = True) -> Dict:
        """
        Fetch a URL — must be in allowed_domains.
        Returns: {ok, url, text, html, status, error}
        """
        # Domain check
        domain_check = self._check_domain(url)
        if not domain_check["allowed"]:
            return {
                "ok": False,
                "url": url,
                "error": domain_check["reason"],
                "blocked": True,
            }

        # Try Playwright first
        if _PLAYWRIGHT and self._browser:
            return await self._fetch_playwright(url, extract_text)

        # Fallback: httpx
        return await self._fetch_httpx(url)

    async def _fetch_playwright(self, url: str, extract_text: bool) -> Dict:
        try:
            page = await self._browser.new_page()
            # Block non-essential resources for speed
            await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}", lambda r: r.abort())
            response = await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            html = await page.content()
            text = await page.inner_text("body") if extract_text else ""
            await page.close()
            return {
                "ok": response.ok if response else False,
                "url": url,
                "status": response.status if response else 0,
                "html": html[:50000],
                "text": self._clean_text(text)[:10000],
            }
        except Exception as exc:
            return {"ok": False, "url": url, "error": str(exc)}

    async def _fetch_httpx(self, url: str) -> Dict:
        try:
            import httpx  # type: ignore
            async with httpx.AsyncClient(
                timeout=30,
                follow_redirects=True,
                headers={"User-Agent": "AxiomZero-Research/1.0 (academic use)"},
            ) as client:
                resp = await client.get(url)
                return {
                    "ok": resp.is_success,
                    "url": url,
                    "status": resp.status_code,
                    "text": resp.text[:10000],
                    "html": resp.text[:50000],
                }
        except Exception as exc:
            return {"ok": False, "url": url, "error": str(exc)}

    async def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict]:
        """Convenience: search arXiv via the export API."""
        url = (
            f"https://export.arxiv.org/api/query"
            f"?search_query={query}&max_results={max_results}"
            f"&sortBy=submittedDate&sortOrder=descending"
        )
        result = await self.fetch(url, extract_text=False)
        if not result["ok"]:
            return []
        # Parse minimal XML
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(result["html"])
            ns = "{http://www.w3.org/2005/Atom}"
            papers = []
            for entry in root.findall(f"{ns}entry"):
                papers.append({
                    "title": (entry.findtext(f"{ns}title") or "").strip(),
                    "id": (entry.findtext(f"{ns}id") or "").strip(),
                    "published": (entry.findtext(f"{ns}published") or "").strip(),
                    "summary": (entry.findtext(f"{ns}summary") or "").strip()[:300],
                })
            return papers
        except Exception:
            return []

    def _check_domain(self, url: str) -> Dict:
        try:
            parsed = urlparse(url)
            host = parsed.netloc.lower()
            # Strip port
            host = host.split(":")[0]
            # Check exact match or subdomain of allowed domain
            for allowed in self.allowed_domains:
                if host == allowed or host.endswith(f".{allowed}"):
                    return {"allowed": True}
            return {
                "allowed": False,
                "reason": f"Domain '{host}' not in allowed list: {sorted(self.allowed_domains)}",
            }
        except Exception as exc:
            return {"allowed": False, "reason": str(exc)}

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted page text."""
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()
