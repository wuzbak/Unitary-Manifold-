# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
app/server.py — AxiomZero SGE HTTP Dashboard Server
====================================================

Serves the single-page dashboard (ui/index.html) and a JSON API:

  GET  /             → dashboard HTML
  GET  /api/status   → full engine status JSON
  GET  /api/events   → recent security events JSON
  GET  /api/chain    → hash chain head + length + integrity
  GET  /api/threats  → threat intel summary
  GET  /api/firewall → firewall audit summary
  GET  /api/quarantine → quarantine summary + records
  POST /api/scan-url  → body: {"url": str, "payload_b64": str, "content_type": str}
  POST /api/check-domain → body: {"domain": str}
  POST /api/check-hash → body: {"hash": str}
  POST /api/check-cve  → body: {"cve_id": str}

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import base64
import http.server
import json
import os
import threading
from pathlib import Path
from typing import Optional

from ..engine.sge_core import SGECore, SGEConfig


_UI_DIR = Path(__file__).resolve().parents[1] / "ui"


def _json_response(handler: http.server.BaseHTTPRequestHandler, data: object, status: int = 200) -> None:
    body = json.dumps(data, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _error(handler: http.server.BaseHTTPRequestHandler, msg: str, status: int = 400) -> None:
    _json_response(handler, {"error": msg}, status)


def _read_body(handler: http.server.BaseHTTPRequestHandler) -> Optional[dict]:
    try:
        length = int(handler.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = handler.rfile.read(length)
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


class SGERequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for the SGE dashboard."""

    sge: SGECore  # class-level reference set by serve_ui()

    def log_message(self, fmt, *args):  # suppress default access log spam
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")

        if path in ("", "/"):
            self._serve_file(_UI_DIR / "index.html", "text/html")
            return

        route_map = {
            "/api/status":     self._api_status,
            "/api/events":     self._api_events,
            "/api/chain":      self._api_chain,
            "/api/threats":    self._api_threats,
            "/api/firewall":   self._api_firewall,
            "/api/quarantine": self._api_quarantine,
        }
        handler_fn = route_map.get(path)
        if handler_fn:
            handler_fn()
        else:
            _error(self, "Not found", 404)

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/")
        body = _read_body(self)
        if body is None:
            _error(self, "Invalid JSON body")
            return

        if path == "/api/scan-url":
            self._api_scan_url(body)
        elif path == "/api/check-domain":
            self._api_check_domain(body)
        elif path == "/api/check-hash":
            self._api_check_hash(body)
        elif path == "/api/check-cve":
            self._api_check_cve(body)
        else:
            _error(self, "Not found", 404)

    # ---------------------------------------------------------------
    # GET handlers
    # ---------------------------------------------------------------

    def _api_status(self):
        _json_response(self, self.sge.status())

    def _api_events(self):
        n = 100
        _json_response(self, {"events": self.sge.recent_events(n)})

    def _api_chain(self):
        ok, bad_idx, reason = self.sge.verify_chain()
        _json_response(self, {
            "head": self.sge.chain_head(),
            "merkle_root": self.sge.chain_merkle_root(),
            "integrity": ok,
            "bad_index": bad_idx,
            "reason": reason,
        })

    def _api_threats(self):
        _json_response(self, self.sge.threat_intel_summary())

    def _api_firewall(self):
        _json_response(self, self.sge._firewall.audit_summary())

    def _api_quarantine(self):
        _json_response(self, {
            "summary": self.sge._quarantine.summary(),
            "records": [r.to_dict() for r in self.sge._quarantine.all_records()[-20:]],
        })

    # ---------------------------------------------------------------
    # POST handlers
    # ---------------------------------------------------------------

    def _api_scan_url(self, body: dict):
        url = body.get("url", "")
        payload_b64 = body.get("payload_b64", "")
        ct = body.get("content_type", "")
        try:
            data = base64.b64decode(payload_b64 + "==") if payload_b64 else b""
        except Exception:
            _error(self, "Invalid base64 payload")
            return
        result = self.sge.check_url_payload(url, data, ct)
        _json_response(self, result.to_dict())

    def _api_check_domain(self, body: dict):
        domain = body.get("domain", "")
        blocked, rule = self.sge.check_domain(domain)
        ti = self.sge.check_threat_intel_domain(domain)
        _json_response(self, {
            "domain": domain,
            "blocked": blocked,
            "matched_rule": rule,
            "threat_indicator": ti.to_dict() if ti else None,
        })

    def _api_check_hash(self, body: dict):
        h = body.get("hash", "")
        indicator = self.sge.lookup_file_hash(h)
        _json_response(self, {
            "hash": h,
            "is_malware": indicator is not None,
            "indicator": indicator.to_dict() if indicator else None,
        })

    def _api_check_cve(self, body: dict):
        cve_id = body.get("cve_id", "")
        indicator = self.sge.lookup_cve(cve_id)
        _json_response(self, {
            "cve_id": cve_id,
            "found": indicator is not None,
            "indicator": indicator.to_dict() if indicator else None,
        })

    # ---------------------------------------------------------------
    # Static file
    # ---------------------------------------------------------------

    def _serve_file(self, path: Path, content_type: str):
        if not path.exists():
            _error(self, "Not found", 404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def make_handler(sge_instance: SGECore):
    """Create a handler class with the sge instance bound."""
    class _Handler(SGERequestHandler):
        sge = sge_instance
    return _Handler


def serve_ui(
    sge: SGECore,
    host: str = "127.0.0.1",
    port: int = 7622,
    daemon: bool = False,
) -> http.server.HTTPServer:
    """Start the HTTP server.

    Parameters
    ----------
    sge : SGECore
        Engine instance to expose via the API.
    host : str
        Bind address (default: loopback only — never expose to 0.0.0.0 in prod).
    port : int
        Listen port.
    daemon : bool
        If True, run server in a daemon thread (non-blocking).

    Returns
    -------
    HTTPServer instance.
    """
    handler = make_handler(sge)
    server = http.server.HTTPServer((host, port), handler)
    if daemon:
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
    return server
