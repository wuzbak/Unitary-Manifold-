# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "06-omega-synthesis"))

from library_console import Workbench, make_handler  # noqa: E402
from http.server import ThreadingHTTPServer  # noqa: E402


def _server():
    bench = Workbench("omega", "Omega", Path(__file__).resolve().parents[2] / "06-omega-synthesis")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(bench, 0))
    port = httpd.server_address[1]
    httpd.RequestHandlerClass = make_handler(bench, port)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def _post(port, headers):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/call", data=b"{}", method="POST",
        headers={"Content-Type": "application/json", **headers})
    try:
        return urllib.request.urlopen(req, timeout=10).status
    except urllib.error.HTTPError as err:
        return err.code


def test_health_and_post_guards():
    httpd, port = _server()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=10) as r:
            assert json.load(r)
        assert _post(port, {}) == 403
        assert _post(port, {"X-Console": "1", "Host": "evil.example"}) == 403
    finally:
        httpd.shutdown()
