# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""JSON API dispatch for the public USGS live-data integration."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from .usgs_adapter import USGS_FEED_URL, fetch_earthquake_summary

API_ENDPOINTS = ("/api/status", "/api/fetch-result")


def dispatch_api_request(path: str, query: Mapping[str, List[str]]) -> Dict[str, Any]:
    if path == "/api/status":
        return {
            "product": "AZ Live-Data Harness",
            "endpoints": list(API_ENDPOINTS),
            "adapter": "usgs_adapter.fetch_earthquake_summary",
            "source": USGS_FEED_URL,
            "fallback": False,
        }

    if path == "/api/fetch-result":
        return fetch_earthquake_summary()

    raise KeyError(f"unknown API endpoint: {path}")
