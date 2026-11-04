# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
import sys

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from sync_backend import server as sync_server


class SyncBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._original_store_path = sync_server.STORE_PATH
        cls._tempdir = tempfile.TemporaryDirectory(dir=PRODUCT_ROOT)
        sync_server.STORE_PATH = Path(cls._tempdir.name) / "sync_store.json"
        cls._server = sync_server.ThreadingHTTPServer(("127.0.0.1", 0), sync_server.SyncHandler)
        cls._server.instance_id = "owned-test-instance"
        cls._thread = threading.Thread(target=cls._server.serve_forever, daemon=True)
        cls._thread.start()
        cls.base_url = f"http://127.0.0.1:{cls._server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls._server.shutdown()
        cls._server.server_close()
        cls._thread.join(timeout=5)
        sync_server.STORE_PATH = cls._original_store_path
        cls._tempdir.cleanup()

    def tearDown(self) -> None:
        if sync_server.STORE_PATH.exists():
            sync_server.STORE_PATH.unlink()

    def request_json(self, path: str, *, method: str = "GET", payload: dict | None = None, token: str | None = None, origin: str | None = None):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["X-Sync-Token"] = token
        if origin is not None:
            headers["Origin"] = origin
        request = urllib.request.Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        with urllib.request.urlopen(request) as response:
            return response.status, json.loads(response.read().decode("utf-8"))

    def test_health_endpoint_reports_ready(self) -> None:
        status, payload = self.request_json("/api/sync/health")
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["instance_id"], "owned-test-instance")

    def test_remote_page_origins_cannot_read_or_write_the_local_sidecar(self) -> None:
        for method, path in (
            ("GET", "/api/sync/health"),
            ("POST", "/api/sync/push"),
            ("OPTIONS", "/api/sync/push"),
        ):
            with self.subTest(method=method):
                with self.assertRaises(urllib.error.HTTPError) as error:
                    self.request_json(path, method=method, origin="https://remote.example")
                self.assertEqual(error.exception.code, 403)
                self.assertIsNone(error.exception.headers.get("Access-Control-Allow-Origin"))
        self.assertFalse(sync_server.STORE_PATH.exists())

    def test_loopback_and_native_file_clients_keep_health_access(self) -> None:
        for origin in ("http://127.0.0.1:4173", "http://localhost:8327", "null"):
            with self.subTest(origin=origin):
                status, payload = self.request_json("/api/sync/health", origin=origin)
                self.assertEqual(status, 200)
                self.assertTrue(payload["ok"])

    def test_malformed_origin_is_rejected_without_crashing_the_handler(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.request_json("/api/sync/health", origin="http://[invalid")
        self.assertEqual(error.exception.code, 403)

    def test_push_then_pull_requires_matching_token(self) -> None:
        status, payload = self.request_json(
            "/api/sync/push",
            method="POST",
            payload={"account_email": "user@example.com", "packet": {"product": 24, "tabs": ["ok"]}},
            token="secret-token",
        )
        self.assertEqual(status, 200)
        self.assertEqual(payload["account_email"], "user@example.com")

        status, pulled = self.request_json(
            "/api/sync/pull?account_email=user%40example.com",
            token="secret-token",
        )
        self.assertEqual(status, 200)
        self.assertEqual(pulled["packet"]["tabs"], ["ok"])

        with self.assertRaises(urllib.error.HTTPError) as error:
            self.request_json(
                "/api/sync/pull?account_email=user%40example.com",
                token="wrong-token",
            )
        self.assertEqual(error.exception.code, 403)


if __name__ == "__main__":
    unittest.main()
