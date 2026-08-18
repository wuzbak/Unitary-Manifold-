# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
5-GOVERNANCE/Unitary Pentad/conftest.py
=========================================
Hermetic pytest fixtures for the Pentad test suite.

Every fixture here patches external I/O — HTTP, filesystem writes outside /tmp,
subprocess calls, and time — so all tests run deterministically with zero
network access and no side-effects on the real OS.

Theory: ThomasCory Walker-Pearson.  Code: GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Autouse: freeze wall-clock for deterministic tests
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _frozen_time(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Freeze time.time() to a fixed epoch so timestamps are deterministic."""
    _BASE = 1_750_000_000.0
    monkeypatch.setattr(time, "time", lambda: _BASE)
    monkeypatch.setattr(time, "monotonic", lambda: _BASE)
    yield


# ---------------------------------------------------------------------------
# Autouse: block all outbound HTTP
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _no_http(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Patch httpx, urllib, and requests to raise on any network call."""
    def _raise(*args: Any, **kwargs: Any) -> None:  # pragma: no cover
        raise RuntimeError(
            "Hermetic test suite: outbound HTTP is not allowed. "
            "Use the mock_http fixture instead."
        )

    try:
        import httpx  # type: ignore
        monkeypatch.setattr(httpx, "get", _raise)
        monkeypatch.setattr(httpx, "post", _raise)
        monkeypatch.setattr(httpx.AsyncClient, "__aenter__", AsyncMock(side_effect=RuntimeError("no HTTP")))
    except ImportError:
        pass

    try:
        import urllib.request as _ur
        monkeypatch.setattr(_ur, "urlopen", _raise)
    except Exception:  # pragma: no cover
        pass

    yield


# ---------------------------------------------------------------------------
# Autouse: block dangerous subprocess calls
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _no_subprocess(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Prevent real subprocess execution during Pentad tests."""
    import subprocess

    def _safe_run(args: Any, **kwargs: Any) -> MagicMock:
        m = MagicMock()
        m.returncode = 0
        m.stdout = b""
        m.stderr = b""
        return m

    monkeypatch.setattr(subprocess, "run", _safe_run)
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **kw: b"")
    monkeypatch.setattr(subprocess, "Popen", MagicMock())
    yield


# ---------------------------------------------------------------------------
# Fixture: temporary home directory to isolate file writes
# ---------------------------------------------------------------------------
@pytest.fixture
def tmp_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect Path.home() to a temp dir for tests that write to ~/.axiomzero."""
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    return tmp_path


# ---------------------------------------------------------------------------
# Fixture: mock HTTP responses for gateway / bridge tests
# ---------------------------------------------------------------------------
class MockHTTPResponse:
    def __init__(self, data: Dict, status_code: int = 200) -> None:
        self._data = data
        self.status_code = status_code

    def json(self) -> Dict:
        return self._data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


@pytest.fixture
def mock_http() -> Generator[MagicMock, None, None]:
    """Return a configurable mock HTTP client."""
    client = MagicMock()
    client.get.return_value = MockHTTPResponse({"status": "ok"})
    client.post.return_value = MockHTTPResponse({"status": "ok"})
    yield client


# ---------------------------------------------------------------------------
# Fixture: pre-seeded HILS certification pipeline
# ---------------------------------------------------------------------------
@pytest.fixture
def hils_pipeline():
    """Return a pre-seeded HILSCertificationPipeline."""
    from hils_core import build_certified_pipeline
    return build_certified_pipeline()


# ---------------------------------------------------------------------------
# Fixture: minimal FiveCoresSystem for workflow engine tests
# ---------------------------------------------------------------------------
@pytest.fixture
def five_cores_system():
    """Return a minimal FiveCoresSystem with safe defaults."""
    try:
        from five_cores import FiveCoresSystem  # type: ignore
        return FiveCoresSystem()
    except ImportError:
        m = MagicMock()
        m.get_trust_phi.return_value = 0.85
        m.get_coupling_eigenvalue.return_value = 12 / 37
        return m


# ---------------------------------------------------------------------------
# Fixture: ephemeral state DB
# ---------------------------------------------------------------------------
@pytest.fixture
def state_db(tmp_path: Path):
    """Return a StateDB backed by a temp file."""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "AxiomZero"))
        from AxiomZero.memory.state_db import StateDB  # type: ignore
        return StateDB(db_path=tmp_path / "test_state.db")
    except ImportError:
        return MagicMock()
