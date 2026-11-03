# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Static file server for the standalone UI."""

from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit

from geo_monitor.engine.feeds import (
    EONETFeedParser,
    NOAAAlertsFeedParser,
    NWACFeedParser,
    USGSFeedParser,
)
from geo_monitor.engine.ionosphere_feed import KP_URL, fetch_kp_index
from geo_monitor.engine.firms_feed import fetch_firms_active_fires_with_status


class UIRequestHandler(SimpleHTTPRequestHandler):
    """Serve the browser UI and a first-party live-feed health API."""

    def do_GET(self) -> None:  # noqa: N802
        if urlsplit(self.path).path == "/api/feeds":
            payload = fetch_live_feeds()
            body = json.dumps(payload, sort_keys=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass

def ui_directory() -> Path:
    """Return the absolute path to the bundled UI directory."""
    return Path(__file__).resolve().parents[2] / "ui"


def fetch_live_feeds() -> dict[str, Any]:
    """Fetch each configured public data source independently.

    A failed or unconfigured source is represented explicitly; empty data
    is never used to imply that a source was reachable.
    """
    sources: dict[str, tuple[str, Callable[[], Any]]] = {
        "usgs": (
            USGSFeedParser.USGS_FEED_URL_PAST_MONTH_SIG,
            lambda: USGSFeedParser().fetch(USGSFeedParser.USGS_FEED_URL_PAST_MONTH_SIG),
        ),
        "eonet": (
            EONETFeedParser.EONET_API_URL,
            lambda: EONETFeedParser().fetch(limit=200, days=30),
        ),
        "nws": (
            NOAAAlertsFeedParser.NWS_ALERTS_BASE_URL,
            lambda: NOAAAlertsFeedParser().fetch(),
        ),
        "nwac": (
            NWACFeedParser.NWAC_API_URL,
            lambda: NWACFeedParser().fetch(),
        ),
        "kp": (
            KP_URL,
            _fetch_kp,
        ),
    }
    if os.environ.get("FIRMS_MAP_KEY"):
        sources["firms"] = (
            "https://firms.modaps.eosdis.nasa.gov/",
            fetch_firms_active_fires_with_status,
        )

    results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=len(sources)) as pool:
        futures = {pool.submit(fetcher): name for name, (_, fetcher) in sources.items()}
        for future in as_completed(futures):
            name = futures[future]
            source_url, _ = sources[name]
            try:
                value = future.result()
                if name == "firms":
                    results[name] = {
                        "status": "error" if value.error else "live",
                        "source_url": source_url,
                        "fetched_at": datetime.now(timezone.utc).isoformat() if not value.error else None,
                        "payload": value.events if not value.error else None,
                        "error": value.error,
                    }
                else:
                    _validate_feed_payload(name, value)
                    results[name] = {
                        "status": "live",
                        "source_url": source_url,
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                        "payload": value,
                        "error": None,
                    }
            except Exception as exc:
                results[name] = {
                    "status": "error",
                    "source_url": source_url,
                    "fetched_at": None,
                    "payload": None,
                    "error": f"{type(exc).__name__}: {exc}",
                }

    if "firms" not in results:
        results["firms"] = {
            "status": "unconfigured",
            "source_url": "https://firms.modaps.eosdis.nasa.gov/",
            "fetched_at": None,
            "payload": None,
            "error": "Set FIRMS_MAP_KEY to enable NASA FIRMS active-fire data.",
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "feeds": results,
    }


def _fetch_kp() -> dict[str, Any]:
    result = fetch_kp_index()
    if result.get("observed_time") is None:
        raise RuntimeError("NOAA returned no observation timestamp")
    kp = float(result["kp"])
    if not 0 <= kp <= 9:
        raise ValueError(f"NOAA Kp value is outside the expected 0-9 range: {kp}")
    return result


def _validate_feed_payload(name: str, payload: Any) -> None:
    if name == "usgs" and (
        not isinstance(payload, dict) or not isinstance(payload.get("features"), list)
    ):
        raise ValueError("USGS response has no GeoJSON features array")
    if name == "eonet" and (
        not isinstance(payload, dict) or not isinstance(payload.get("events"), list)
    ):
        raise ValueError("EONET response has no events array")
    if name == "nws" and (
        not isinstance(payload, dict) or not isinstance(payload.get("features"), list)
    ):
        raise ValueError("NOAA NWS response has no GeoJSON features array")
    if name == "nwac" and not (
        isinstance(payload, list)
        or isinstance(payload, dict) and isinstance(payload.get("data"), list)
    ):
        raise ValueError("NWAC response has no product array")


def build_server(host: str = "127.0.0.1", port: int = 8021) -> ThreadingHTTPServer:
    """Create the UI and live-feed API server without starting its loop."""
    handler = partial(UIRequestHandler, directory=str(ui_directory()))
    return ThreadingHTTPServer((host, port), handler)


def serve_ui(port: int = 8021) -> None:
    """Serve the UI until interrupted."""
    directory = str(ui_directory())
    with build_server(port=port) as httpd:
        print(f"Serving UM Geophysical Monitor at http://127.0.0.1:{port}")
        print(f"UI root: {directory}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down server.")
