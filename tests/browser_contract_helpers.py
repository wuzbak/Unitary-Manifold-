# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import contextlib
import http.client
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import pytest


def playwright_sync_api():
    return pytest.importorskip("playwright.sync_api")


def reserve_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


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
def running_server(
    product_root: Path,
    command_args: list[str],
    *,
    base_url: str,
    ready_path: str = "/",
    timeout: float = 20.0,
    env: dict[str, str] | None = None,
):
    merged_env = os.environ.copy()
    merged_env.setdefault("PYTHONUNBUFFERED", "1")
    if env:
        merged_env.update(env)
    process = subprocess.Popen(
        [sys.executable, *command_args],
        cwd=str(product_root),
        env=merged_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_for_http(base_url, ready_path=ready_path, timeout=timeout)
    except Exception:
        output = ""
        if process.stdout:
            try:
                output = process.stdout.read()
            except Exception:  # pragma: no cover - defensive
                output = ""
        raise AssertionError(f"Server failed for {product_root}.\n{output}") from None
    try:
        yield base_url
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:  # pragma: no cover - defensive
                process.kill()
                process.wait(timeout=5)
        if process.stdout:
            process.stdout.close()


def launch_browser_or_skip(playwright, browser_name: str):
    browser_type = getattr(playwright, browser_name)
    try:
        return browser_type.launch(headless=True)
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"{browser_name} browser unavailable for Playwright contract test: {exc}")
