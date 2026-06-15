# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
AxiomZero Manager 6 — Web Research & OSINT

Maps to: bot/research_resources.py, arXiv/ADS references

Sub-agents:
    SA6.1  arXiv parser (gr-qc, hep-th, astro-ph.CO)
    SA6.2  NASA ADS query engine
    SA6.3  Brave Search (10K queries/month free tier)
    SA6.4  Peer-review critic
    SA6.5  Citation compiler

Purpose: Live connection to the academic world.  Monitors for new papers
that confirm or threaten UM predictions (especially LiteBIRD birefringence
β ∈ {≈0.273°, ≈0.331°}).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class WebManager:
    """Manager 6: Web Research & OSINT."""

    name = "M6_Web"
    model_key = "strategic"
    sub_agents = [
        "SA6.1_arxiv_parser",
        "SA6.2_nasa_ads",
        "SA6.3_brave_search",
        "SA6.4_peer_review_critic",
        "SA6.5_citation_compiler",
    ]

    # Falsification sentinel: LiteBIRD birefringence window
    BETA_ADMISSIBLE = (0.22, 0.38)    # degrees
    BETA_PREDICTED = [(0.273, 0.281), (0.329, 0.333)]  # canonical canonical
    BETA_FORBIDDEN_GAP = (0.29, 0.31)  # within admissible but not predicted

    # Allowed domains for browser-based research
    ALLOWED_DOMAINS = {
        "arxiv.org", "ui.adsabs.harvard.edu", "api.semanticscholar.org",
        "inspirehep.net", "zenodo.org", "github.com", "export.arxiv.org",
    }

    def __init__(self, config: Dict, model_router: Any, repo_root: Path):
        self.config = config
        self.model_router = model_router
        self.repo_root = repo_root
        self._brave_key = os.environ.get("BRAVE_API_KEY", "")

    async def run(self, state: Any) -> Dict[str, Any]:
        task = state.task
        payload = task.payload
        query = payload.get("web_query", task.description)

        logger.info("[%s] Web research for task %s", self.name, task.task_id)

        results = {}
        results["arxiv"] = await self._sa_arxiv(query, payload)
        results["ads"] = await self._sa_nasa_ads(query, payload)
        results["brave"] = await self._sa_brave(query)
        results["critic"] = await self._sa_peer_review_critic(results)
        results["citations"] = await self._sa_compile_citations(results)

        # Check for LiteBIRD birefringence papers
        beta_alert = self._check_birefringence_papers(results)

        return {
            "manager": self.name,
            "status": "ok",
            "papers_found": sum(len(r.get("papers", [])) for r in results.values() if isinstance(r, dict)),
            "birefringence_alert": beta_alert,
            "sub_agent_results": results,
        }

    async def _sa_arxiv(self, query: str, payload: Dict) -> Dict:
        """SA6.1: Query arXiv API for relevant papers."""
        try:
            import httpx  # type: ignore
        except ImportError:
            return {"ok": False, "error": "httpx not installed", "papers": []}

        categories = self.config.get("web_research", {}).get(
            "arxiv_categories", ["gr-qc", "hep-th", "astro-ph.CO"]
        )
        cat_filter = " OR ".join(f"cat:{c}" for c in categories)
        search_query = f"({query}) AND ({cat_filter})"

        try:
            url = "https://export.arxiv.org/api/query"
            params = {
                "search_query": search_query,
                "max_results": 5,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }
            _timeout = httpx.Timeout(connect=3.0, read=5.0)
            async with httpx.AsyncClient(timeout=_timeout) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                papers = self._parse_arxiv_feed(resp.text)
                return {"ok": True, "papers": papers, "query": search_query}
        except Exception as exc:
            logger.warning("[M6_Web] arXiv query failed: %s", exc)
            return {"ok": False, "error": str(exc), "papers": []}

    def _parse_arxiv_feed(self, xml_text: str) -> List[Dict]:
        """Parse arXiv Atom feed into paper list."""
        import xml.etree.ElementTree as ET
        ns = "{http://www.w3.org/2005/Atom}"
        try:
            root = ET.fromstring(xml_text)
            papers = []
            for entry in root.findall(f"{ns}entry"):
                title = (entry.findtext(f"{ns}title") or "").strip()
                summary = (entry.findtext(f"{ns}summary") or "").strip()[:300]
                arxiv_id = (entry.findtext(f"{ns}id") or "").strip()
                published = (entry.findtext(f"{ns}published") or "").strip()
                papers.append({
                    "title": title,
                    "summary": summary,
                    "id": arxiv_id,
                    "published": published,
                })
            return papers
        except Exception:
            return []

    async def _sa_nasa_ads(self, query: str, payload: Dict) -> Dict:
        """SA6.2: NASA ADS query for observational astronomy papers."""
        try:
            import httpx  # type: ignore
        except ImportError:
            return {"ok": False, "error": "httpx not installed", "papers": []}

        # ADS public API (token optional for higher rate limits)
        ads_token = os.environ.get("NASA_ADS_TOKEN", "")
        headers = {}
        if ads_token:
            headers["Authorization"] = f"******"

        # Focus on LiteBIRD / CMB birefringence keywords
        ads_query = f"{query} CMB birefringence LiteBIRD"
        try:
            _timeout = httpx.Timeout(connect=3.0, read=5.0)
            async with httpx.AsyncClient(timeout=_timeout) as client:
                resp = await client.get(
                    "https://api.adsabs.harvard.edu/v1/search/query",
                    params={"q": ads_query, "rows": 3, "fl": "title,abstract,bibcode,year"},
                    headers=headers,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    docs = data.get("response", {}).get("docs", [])
                    papers = [{"title": d.get("title", [""])[0],
                               "bibcode": d.get("bibcode"),
                               "year": d.get("year")} for d in docs]
                    return {"ok": True, "papers": papers}
                return {"ok": False, "error": f"ADS HTTP {resp.status_code}", "papers": []}
        except Exception as exc:
            logger.warning("[M6_Web] NASA ADS query failed: %s", exc)
            return {"ok": False, "error": str(exc), "papers": []}

    async def _sa_brave(self, query: str) -> Dict:
        """SA6.3: Brave Search API (free tier, 10K/month)."""
        if not self._brave_key:
            return {"ok": False, "error": "BRAVE_API_KEY not set", "results": []}
        try:
            import httpx  # type: ignore
            _timeout = httpx.Timeout(connect=3.0, read=5.0)
            async with httpx.AsyncClient(timeout=_timeout) as client:
                resp = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": 5},
                    headers={"X-Subscription-Token": self._brave_key,
                             "Accept": "application/json"},
                )
                resp.raise_for_status()
                data = resp.json()
                items = data.get("web", {}).get("results", [])
                return {"ok": True, "results": [{"title": r.get("title"), "url": r.get("url"),
                                                  "description": r.get("description", "")[:200]}
                                                 for r in items]}
        except Exception as exc:
            logger.warning("[M6_Web] Brave Search failed: %s", exc)
            return {"ok": False, "error": str(exc), "results": []}

    async def _sa_peer_review_critic(self, prior_results: Dict) -> Dict:
        """SA6.4: Critically assess retrieved papers for UM relevance."""
        all_papers = []
        for key in ("arxiv", "ads"):
            r = prior_results.get(key, {})
            all_papers.extend(r.get("papers", []))

        # Look for birefringence mentions
        birefringence_papers = [
            p for p in all_papers
            if any(kw in (p.get("title", "") + p.get("summary", "")).lower()
                   for kw in ("birefringence", "litebird", "cmb polarization rotation"))
        ]
        return {
            "ok": True,
            "total_papers_reviewed": len(all_papers),
            "birefringence_relevant": len(birefringence_papers),
            "birefringence_papers": birefringence_papers[:3],
        }

    async def _sa_compile_citations(self, prior_results: Dict) -> Dict:
        """SA6.5: Compile a citation list in preferred format."""
        citations = []
        for key in ("arxiv", "ads"):
            r = prior_results.get(key, {})
            for p in r.get("papers", []):
                if p.get("id"):
                    citations.append(f"arXiv:{p['id'].split('/')[-1]} — {p.get('title', '')}")
                elif p.get("bibcode"):
                    citations.append(f"ADS:{p['bibcode']} — {p.get('title', '')}")
        return {"ok": True, "citations": citations}

    def _check_birefringence_papers(self, results: Dict) -> Optional[Dict]:
        """Check if any retrieved papers report a β measurement that threatens UM."""
        critic = results.get("critic", {})
        beta_papers = critic.get("birefringence_papers", [])
        if not beta_papers:
            return None
        return {
            "alert": True,
            "message": f"Found {len(beta_papers)} birefringence-relevant papers — human review recommended",
            "papers": beta_papers,
            "falsification_window": {
                "admissible": self.BETA_ADMISSIBLE,
                "predicted_values": self.BETA_PREDICTED,
                "forbidden_gap": self.BETA_FORBIDDEN_GAP,
            },
        }
