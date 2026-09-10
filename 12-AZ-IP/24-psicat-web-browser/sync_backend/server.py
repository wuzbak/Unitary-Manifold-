#!/usr/bin/env python3
import argparse
import hashlib
import json
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
STORE_PATH = ROOT / "data" / "sync_store.json"
STORE_LOCK = threading.Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_store() -> dict:
    if not STORE_PATH.exists():
        return {}
    try:
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_store(payload: dict) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class SyncHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Sync-Token")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Sync-Token")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/sync/health":
            self._send_json(200, {"ok": True, "service": "psicat-sync-backend", "updated_at": utc_now()})
            return
        if parsed.path == "/api/sync/pull":
            account_email = parse_qs(parsed.query).get("account_email", [""])[0].strip().lower()
            token = self.headers.get("X-Sync-Token", "").strip()
            with STORE_LOCK:
                store = load_store()
                entry = store.get(account_email)
            if not account_email:
                self._send_json(400, {"error": "account_email is required"})
            elif not token:
                self._send_json(401, {"error": "X-Sync-Token is required"})
            elif not entry:
                self._send_json(404, {"error": "sync packet not found"})
            elif entry.get("token_hash") != hash_token(token):
                self._send_json(403, {"error": "sync token mismatch"})
            else:
                self._send_json(200, {key: value for key, value in entry.items() if key != "token_hash"})
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/sync/push":
            self._send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "request body must be valid JSON"})
            return
        account_email = str(payload.get("account_email", "")).strip().lower()
        packet = payload.get("packet")
        token = self.headers.get("X-Sync-Token", "").strip()
        if not account_email or not isinstance(packet, dict) or not token:
            self._send_json(400, {"error": "account_email, packet, and X-Sync-Token are required"})
            return
        with STORE_LOCK:
            store = load_store()
            existing = store.get(account_email)
            token_hash = hash_token(token)
            if existing and existing.get("token_hash") != token_hash:
                self._send_json(403, {"error": "sync token mismatch"})
                return
            entry = {
                "account_email": account_email,
                "updated_at": utc_now(),
                "packet": packet,
                "token_hash": token_hash,
            }
            store[account_email] = entry
            save_store(store)
        self._send_json(200, {key: value for key, value in entry.items() if key != "token_hash"})

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), SyncHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
