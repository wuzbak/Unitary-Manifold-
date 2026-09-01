# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
arXiv preprint feed helpers for the Falsification Observatory.

Fetches recent preprints related to:
- Kaluza-Klein extra dimensions
- CMB birefringence
- DESI dark energy
- LiteBIRD

All network calls have offline fallbacks — never raise on network failure.
"""
from __future__ import annotations

import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from typing import Any

ARXIV_API_BASE = "https://export.arxiv.org/api/query"

SEARCH_QUERIES: dict[str, str] = {
    "kk_extra_dimensions": "Kaluza-Klein extra dimensions 5D",
    "cmb_birefringence":   "CMB cosmic birefringence polarization rotation",
    "desi_dark_energy":    "DESI dark energy equation of state w0 wa",
    "litebird":            "LiteBIRD CMB polarization satellite",
}


def _fetch_arxiv(query: str, max_results: int = 5) -> list[dict]:
    """Fetch arXiv results for a query. Returns [] on any error."""
    params = urllib.parse.urlencode({
        "search_query": f"all:{urllib.parse.quote(query)}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
    })
    url = f"{ARXIV_API_BASE}?{params}"
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            xml_data = resp.read().decode("utf-8")
    except Exception:
        return []

    try:
        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = []
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            summary_el = entry.find("atom:summary", ns)
            id_el = entry.find("atom:id", ns)
            published_el = entry.find("atom:published", ns)
            entries.append({
                "title": (title_el.text or "").strip() if title_el is not None else "",
                "summary": ((summary_el.text or "").strip()[:300] + "...") if summary_el is not None else "",
                "arxiv_id": (id_el.text or "").strip() if id_el is not None else "",
                "published": (published_el.text or "").strip()[:10] if published_el is not None else "",
            })
        return entries
    except Exception:
        return []


def fetch_recent_kk_preprints(topic: str = "kk_extra_dimensions", max_results: int = 5) -> list[dict]:
    """
    Fetch recent arXiv preprints for a given topic key.

    Parameters
    ----------
    topic : str
        One of: 'kk_extra_dimensions', 'cmb_birefringence', 'desi_dark_energy', 'litebird'
    max_results : int
        Maximum number of results to return.

    Returns
    -------
    list of dicts with title, summary, arxiv_id, published.
    Returns [] on network failure.
    """
    query = SEARCH_QUERIES.get(topic, SEARCH_QUERIES["kk_extra_dimensions"])
    return _fetch_arxiv(query, max_results)


def fetch_all_relevant_preprints(max_per_topic: int = 3) -> dict[str, list[dict]]:
    """Fetch preprints for all tracked topics. Returns dict keyed by topic."""
    return {
        topic: _fetch_arxiv(query, max_per_topic)
        for topic, query in SEARCH_QUERIES.items()
    }
