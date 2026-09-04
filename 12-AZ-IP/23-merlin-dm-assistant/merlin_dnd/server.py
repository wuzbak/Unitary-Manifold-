# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .service import MerlinDndService

SERVICE = MerlinDndService()
UI_ROOT = Path(__file__).resolve().parents[1] / "ui"


def dispatch_request(method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    payload = payload or {}
    parsed = urlparse(path)
    query = parse_qs(parsed.query)
    if method == "GET" and parsed.path in {"/", "/index.html"}:
        return 200, {
            "content_type": "text/html; charset=utf-8",
            "body": (UI_ROOT / "index.html").read_text(encoding="utf-8"),
        }
    if method == "GET" and parsed.path == "/app.js":
        return 200, {
            "content_type": "application/javascript; charset=utf-8",
            "body": (UI_ROOT / "app.js").read_text(encoding="utf-8"),
        }
    if method == "GET" and parsed.path == "/api/health":
        return 200, {"status": "ok", "service": "merlin-dm-assistant", "version": "1.0.0"}
    if method == "GET" and parsed.path == "/api/rules":
        spell_name = query.get("spell", [None])[0]
        return 200, SERVICE.rules_reference(spell_name)
    if method == "GET" and parsed.path == "/api/monsters":
        environment = query.get("environment", [None])[0]
        raw_max_cr = query.get("max_cr", [None])[0]
        try:
            max_cr = float(raw_max_cr) if raw_max_cr is not None else None
        except (TypeError, ValueError):
            return 400, {"error": "Query parameter 'max_cr' must be numeric."}
        return 200, {"items": SERVICE.search_monsters(environment=environment, max_cr=max_cr)}
    if method == "GET" and parsed.path == "/api/merchants":
        return 200, {"items": SERVICE.list_merchants()}
    if method == "GET" and parsed.path == "/api/campaigns":
        return 200, {"items": SERVICE.list_campaigns()}
    if method == "POST" and parsed.path == "/api/campaigns":
        return 201, {"campaign": SERVICE.create_campaign(payload).to_dict()}
    if method == "POST" and parsed.path == "/api/campaigns/import":
        return 201, {"campaign": SERVICE.import_campaign(payload).to_dict()}
    if method == "POST" and parsed.path == "/api/characters":
        return 201, {"character": SERVICE.build_character(payload).to_dict()}
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 3 and parts[0] == "api" and parts[1] == "campaigns":
        campaign_id = parts[2]
        if method == "GET" and len(parts) == 4 and parts[3] == "export":
            return 200, SERVICE.export_campaign(campaign_id)
        if method == "POST" and len(parts) == 4 and parts[3] == "characters":
            return 201, {"character": SERVICE.add_character_to_campaign(campaign_id, payload).to_dict()}
        if method == "POST" and len(parts) == 4 and parts[3] == "quests":
            return 201, {"quest": SERVICE.add_quest(campaign_id, payload).to_dict()}
        if method == "POST" and len(parts) == 4 and parts[3] == "layouts":
            return 201, {"layout": SERVICE.add_layout(campaign_id, payload).to_dict()}
        if method == "POST" and len(parts) == 4 and parts[3] == "encounters":
            return 201, {"encounter": SERVICE.plan_encounter(campaign_id, payload).to_dict()}
        if method == "POST" and len(parts) == 4 and parts[3] == "image-brief":
            return 200, {"image_brief": SERVICE.build_image_brief(campaign_id, payload).to_dict()}
        if method == "POST" and len(parts) == 4 and parts[3] == "merlin":
            return 200, {"response": SERVICE.merlin_query(campaign_id, str(payload.get("prompt") or ""))}
    return 404, {"error": "Not found"}


class MerlinDndRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A003
        return

    def _send(self, status: int, payload: dict) -> None:
        if "body" in payload and "content_type" in payload:
            body = str(payload["body"]).encode("utf-8")
            content_type = str(payload["content_type"])
        else:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            content_type = "application/json; charset=utf-8"
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Request body must be valid JSON.") from exc

    def do_GET(self) -> None:  # noqa: N802
        status, payload = dispatch_request("GET", self.path)
        self._send(status, payload)

    def do_POST(self) -> None:  # noqa: N802
        try:
            body = self._body()
        except ValueError as exc:
            self._send(400, {"error": str(exc)})
            return
        status, payload = dispatch_request("POST", self.path, body)
        self._send(status, payload)


def serve(host: str = "127.0.0.1", port: int = 8033) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), MerlinDndRequestHandler)
