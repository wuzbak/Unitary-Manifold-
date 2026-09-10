# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import contextlib
import http.client
import threading
import time
from urllib.parse import urlparse

import pytest


def playwright_sync_api():
    return pytest.importorskip("playwright.sync_api")


def _wait_for_http(base_url: str, ready_path: str = "/", timeout: float = 20.0) -> None:
    parsed = urlparse(base_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        connection = http.client.HTTPConnection(host, port, timeout=1)
        try:
            connection.request("GET", ready_path)
            response = connection.getresponse()
            response.read()
            if response.status < 500:
                return
        except Exception as exc:  # pragma: no cover - timing dependent
            last_error = exc
        finally:
            connection.close()
        time.sleep(0.1)
    raise AssertionError(f"Server at {base_url}{ready_path} did not become ready: {last_error}")


@contextlib.contextmanager
def running_server(server_factory, *, ready_path: str = "/", timeout: float = 20.0):
    server = server_factory()
    with contextlib.suppress(AttributeError, OSError, ValueError):
        host, port = server.socket.getsockname()[:2]
    if "port" not in locals() or port == 0:
        server.server_bind()
        server.server_activate()
        host, port = server.socket.getsockname()[:2]
    base_url = f"http://{host}:{port}/"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        _wait_for_http(base_url, ready_path=ready_path, timeout=timeout)
        yield base_url
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def launch_browser_or_skip(playwright, browser_name: str):
    browser_type = getattr(playwright, browser_name)
    try:
        return browser_type.launch(headless=True)
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"{browser_name} browser unavailable for Playwright contract test: {exc}")
