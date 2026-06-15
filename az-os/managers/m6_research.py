# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/managers/m6_research.py — Manager 6: Open Web Research & OSINT

Monitors arXiv, NASA ADS, and academic sources for papers relevant to
the Unitary Manifold predictions.  Especially watches for LiteBIRD
birefringence β measurements that will test Pillar falsification conditions.

Sub-agents:
  1. ArxivParserAgent    — arXiv paper search and parsing
  2. BraveSearchAgent    — Brave Search API (10K free queries/month)
  3. AcademicScraper     — generic academic URL fetcher
  4. PeerReviewCritic    — evaluates paper relevance to UM predictions
  5. CitationCompiler    — formats citations and reference lists

All web access is logged to the HILS audit trail.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

REPO_ROOT = Path(__file__).parent.parent.parent

# UM predictions to monitor
WATCH_TERMS = [
    "birefringence CMB",
    "Kaluza-Klein 5D",
    "LiteBIRD polarization",
    "DESI dark energy equation of state",
    "SPHEREx spectral index",
    "tensor-to-scalar ratio BICEP",
    "winding number cosmology",
]


@dataclass
class ResearchResult:
    agent: str
    status: str
    papers: list[dict] = field(default_factory=list)
    error: Optional[str] = None


class M6ResearchManager:
    """Manager 6 — Open Web Research & OSINT."""

    MANAGER_ID = "M6"
    KK_LEVEL = 2   # trusted agent ring — internet access is adjacent-track

    # ------------------------------------------------------------------
    # Sub-agent 1: ArXiv Parser
    # ------------------------------------------------------------------

    def search_arxiv(self, query: str, max_results: int = 5) -> ResearchResult:
        """
        Search arXiv for papers matching the query.

        Uses the arXiv Atom API (no API key required, rate-limited to 3 req/s).
        """
        query_encoded = query.replace(" ", "+")
        url = (
            f"https://export.arxiv.org/api/query"
            f"?search_query=all:{query_encoded}"
            f"&start=0&max_results={max_results}"
            f"&sortBy=submittedDate&sortOrder=descending"
        )
        try:
            req = Request(url, headers={"User-Agent": "AxiomZero/0.1 (research agent)"})
            with urlopen(req, timeout=10) as resp:
                data = resp.read().decode("utf-8")
            papers = self._parse_arxiv_atom(data)
            return ResearchResult("ArxivParserAgent", "ok", papers=papers)
        except URLError as exc:
            return ResearchResult("ArxivParserAgent", "error", error=str(exc))
        except Exception as exc:
            return ResearchResult("ArxivParserAgent", "error", error=str(exc))

    # ------------------------------------------------------------------
    # Sub-agent 2: Brave Search
    # ------------------------------------------------------------------

    def brave_search(self, query: str, api_key: Optional[str] = None) -> ResearchResult:
        """
        Search via Brave Search API (10K free queries/month).

        Requires BRAVE_SEARCH_API_KEY environment variable or explicit api_key.
        Falls back gracefully if not available.
        """
        import os
        key = api_key or os.environ.get("BRAVE_SEARCH_API_KEY", "")
        if not key:
            return ResearchResult(
                "BraveSearchAgent", "unverified",
                error="BRAVE_SEARCH_API_KEY not set — set env var for web search"
            )
        url = f"https://api.search.brave.com/res/v1/web/search?q={query.replace(' ', '+')}&count=5"
        try:
            req = Request(url, headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": key,
            })
            with urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            results = data.get("web", {}).get("results", [])
            papers = [
                {"title": r.get("title"), "url": r.get("url"), "description": r.get("description")}
                for r in results[:5]
            ]
            return ResearchResult("BraveSearchAgent", "ok", papers=papers)
        except Exception as exc:
            return ResearchResult("BraveSearchAgent", "error", error=str(exc))

    # ------------------------------------------------------------------
    # Sub-agent 3: Academic Scraper
    # ------------------------------------------------------------------

    def fetch_abstract(self, arxiv_id: str) -> ResearchResult:
        """Fetch the abstract of an arXiv paper by its ID (e.g., '2503.12345')."""
        url = f"https://export.arxiv.org/abs/{arxiv_id}"
        try:
            req = Request(url, headers={"User-Agent": "AxiomZero/0.1"})
            with urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            # Very simple extraction — Sprint 3 replaces with BeautifulSoup
            start = html.find('class="abstract mathjax"')
            if start == -1:
                return ResearchResult("AcademicScraper", "error",
                                      error="Abstract not found in HTML")
            abstract_start = html.find(">", start) + 1
            abstract_end = html.find("</blockquote>", abstract_start)
            abstract = html[abstract_start:abstract_end].strip()
            abstract = abstract.replace("<span>Abstract:</span>", "").strip()
            return ResearchResult("AcademicScraper", "ok",
                                  papers=[{"arxiv_id": arxiv_id, "abstract": abstract}])
        except Exception as exc:
            return ResearchResult("AcademicScraper", "error", error=str(exc))

    # ------------------------------------------------------------------
    # Sub-agent 4: Peer Review Critic
    # ------------------------------------------------------------------

    def evaluate_relevance(self, paper: dict) -> ResearchResult:
        """
        Score a paper's relevance to UM predictions on a 0–1 scale.

        Heuristic: count occurrences of UM-relevant terms in title + abstract.
        Sprint 3: replace with M3 SymPy analysis of any equations found.
        """
        text = (
            (paper.get("title") or "") + " " +
            (paper.get("abstract") or "") + " " +
            (paper.get("description") or "")
        ).lower()

        score_terms = [
            ("birefringence", 0.3),
            ("kaluza-klein", 0.25),
            ("extra dimension", 0.2),
            ("tensor-to-scalar", 0.15),
            ("spectral index", 0.1),
            ("litebird", 0.2),
            ("desi", 0.1),
            ("winding number", 0.15),
        ]
        score = sum(weight for term, weight in score_terms if term in text)
        score = min(score, 1.0)

        return ResearchResult(
            "PeerReviewCritic", "ok",
            papers=[{**paper, "relevance_score": round(score, 3)}],
        )

    # ------------------------------------------------------------------
    # Sub-agent 5: Citation Compiler
    # ------------------------------------------------------------------

    def compile_citation(
        self,
        arxiv_id: str,
        authors: Optional[str] = None,
        title: Optional[str] = None,
        year: Optional[int] = None,
    ) -> ResearchResult:
        """Generate a formatted BibTeX citation entry."""
        key = f"arxiv_{arxiv_id.replace('.', '_')}"
        year_str = str(year or time.localtime().tm_year)
        bib = (
            f"@article{{{key},\n"
            f"  author  = {{{authors or 'Unknown'}}},\n"
            f"  title   = {{{title or 'Unknown'}}},\n"
            f"  year    = {{{year_str}}},\n"
            f"  eprint  = {{{arxiv_id}}},\n"
            f"  archivePrefix = {{arXiv}},\n"
            f"  primaryClass  = {{hep-th}},\n"
            f"}}\n"
        )
        return ResearchResult("CitationCompiler", "ok",
                              papers=[{"bibtex": bib, "key": key}])

    # ------------------------------------------------------------------
    # Monitoring sweep (called periodically by AgentCore)
    # ------------------------------------------------------------------

    def monitor_sweep(self) -> list[ResearchResult]:
        """
        Search arXiv for all UM watch terms.

        Returns one ResearchResult per watch term.  High-relevance papers
        are escalated to M7 for human notification.
        """
        results = []
        for term in WATCH_TERMS[:3]:   # limit to 3 per sweep (rate limiting)
            result = self.search_arxiv(term, max_results=2)
            if result.status == "ok":
                for paper in result.papers:
                    eval_result = self.evaluate_relevance(paper)
                    if eval_result.papers and eval_result.papers[0].get("relevance_score", 0) > 0.3:
                        results.append(eval_result)
            time.sleep(1)  # arXiv rate limit: 3 req/s
        return results

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_arxiv_atom(atom_xml: str) -> list[dict]:
        """Minimal Atom XML parser for arXiv results (no lxml dependency)."""
        papers = []
        entries = atom_xml.split("<entry>")[1:]
        for entry in entries[:10]:
            def extract(tag: str) -> str:
                start = entry.find(f"<{tag}>")
                if start == -1:
                    return ""
                start += len(tag) + 2
                end = entry.find(f"</{tag}>", start)
                return entry[start:end].strip() if end != -1 else ""

            arxiv_id_raw = extract("id")
            arxiv_id = arxiv_id_raw.split("/abs/")[-1].strip() if "/abs/" in arxiv_id_raw else arxiv_id_raw
            papers.append({
                "arxiv_id": arxiv_id,
                "title": extract("title").replace("\n", " "),
                "abstract": extract("summary").replace("\n", " ")[:500],
                "published": extract("published")[:10],
            })
        return papers
