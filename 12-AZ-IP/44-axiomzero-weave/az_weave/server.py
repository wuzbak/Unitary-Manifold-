# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Loopback-only local host; bearer possession represents the local operator."""

from __future__ import annotations

from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
from pathlib import Path
import secrets
from urllib.parse import urlsplit

from .api import Weave, capabilities
from .governance import canonical

MAX_BODY = 200_000


def load_token(state_dir: Path) -> str:
    path = state_dir / "operator.token"
    if path.is_symlink():
        raise ValueError("token file must not be a symlink")
    try:
        with path.open("x", encoding="ascii") as handle:
            path.chmod(0o600)
            handle.write(secrets.token_hex(32))
    except FileExistsError:
        pass
    token = path.read_text(encoding="ascii").strip()
    if len(token) != 64 or any(c not in "0123456789abcdef" for c in token):
        raise ValueError("invalid operator token file")
    path.chmod(0o600)
    return token


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, weave: Weave, token: str, **kwargs):
        self.weave = weave
        self.token = token
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        # Never put query content, bearer tokens or private memory into logs.
        return

    def _reply(self, status: int, data, *, html: bool = False):
        raw = data.encode() if html else canonical(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8" if html else "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                         "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def _host_allowed(self) -> bool:
        expected = f"127.0.0.1:{self.server.server_port}"
        return self.headers.get("Host") in {expected, f"localhost:{self.server.server_port}"}

    def do_GET(self):
        if not self._host_allowed():
            return self._reply(403, {"error": "loopback Host required"})
        if self.path == "/":
            return self._reply(200, (Path(__file__).parent / "ui.html").read_text(), html=True)
        if self.path == "/health":
            return self._reply(200, {"status": "ready", "product": 44})
        return self._reply(404, {"error": "not found"})

    def do_POST(self):
        if not self._host_allowed():
            return self._reply(403, {"error": "loopback Host required"})
        origin = self.headers.get("Origin")
        if origin is not None and origin != f"http://{self.headers.get('Host')}":
            return self._reply(403, {"error": "cross-origin requests denied"})
        scheme, _, presented = self.headers.get("Authorization", "").partition(" ")
        if scheme != "Bearer" or not hmac.compare_digest(presented.encode(), self.token.encode()):
            return self._reply(401, {"error": "local operator bearer required"})
        if self.headers.get_content_type() != "application/json":
            return self._reply(415, {"error": "application/json required"})
        if self.headers.get("Transfer-Encoding"):
            return self._reply(400, {"error": "transfer encoding not supported"})
        try:
            size = int(self.headers.get("Content-Length", "-1"))
            if not 0 <= size <= MAX_BODY:
                raise ValueError("request body must be bounded")
            body = json.loads(self.rfile.read(size), parse_constant=lambda value: _reject_number(value))
            if not isinstance(body, dict):
                raise ValueError("JSON object required")
            route = urlsplit(self.path).path
            principal = "local-operator"
            if route == "/api/capabilities":
                result = {**capabilities(), "backends": self.weave.backends.capabilities()}
            elif route == "/api/query":
                result = self.weave.query(body["query"], principal, body.get("limit", 5))
            elif route == "/api/investigate":
                result = self.weave.investigate(
                    body["query"], principal, experiment=body["experiment"], oracle=body["oracle"],
                    decision_id=body.get("decision_id"))
            elif route == "/api/approve":
                result = {"decision_id": self.weave.approve(
                    body["action"], body["arguments"], principal, obligations=body["obligations"],
                    sources=body.get("sources"), ttl=body.get("ttl", 300))}
            elif route == "/api/invoke":
                result = self.weave.invoke(body["action"], body["arguments"], principal,
                                           body.get("decision_id"))
            elif route == "/api/decision":
                result = self.weave.journal.get(body["decision_id"], principal)
            elif route == "/api/revoke":
                self.weave.journal.revoke(body["decision_id"], principal)
                result = {"state": "REVOKED"}
            elif route == "/api/reconcile":
                self.weave.journal.reconcile(body["decision_id"], principal, resolution=body["resolution"])
                result = {"state": body["resolution"]}
            else:
                return self._reply(404, {"error": "not found"})
        except (ValueError, KeyError, TypeError) as exc:
            return self._reply(400, {"error": f"{type(exc).__name__}: {exc}"})
        except (OSError, RuntimeError, ImportError) as exc:
            return self._reply(503, {"error": f"{type(exc).__name__}: {exc}"})
        return self._reply(200, result)


def _reject_number(value):
    raise ValueError(f"non-finite JSON number {value} is not allowed")


def make_server(weave: Weave, *, port: int = 8144) -> ThreadingHTTPServer:
    token = load_token(weave.state_dir)
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, weave=weave, token=token))
    server.daemon_threads = True
    return server
