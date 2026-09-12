# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import importlib.util
import http.client
import socket
from pathlib import Path
from urllib.error import HTTPError, URLError


_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "9-INFRASTRUCTURE"
    / "check_hf_spaces_canary.py"
)
_SPEC = importlib.util.spec_from_file_location("check_hf_spaces_canary", _MODULE_PATH)
assert _SPEC and _SPEC.loader
canary = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(canary)


def test_401_soft_pass_without_token(monkeypatch) -> None:
    monkeypatch.delenv("HUGGINGFACE_TOKEN", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv(canary.STRICT_ENV, raising=False)

    def _raise(request, timeout=12):
        raise HTTPError(
            request.full_url,
            401,
            "Unauthorized",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(canary, "urlopen", _raise)
    ok, message = canary.check_url(canary.TARGETS[0])
    assert ok is True
    assert "soft pass" in message


def test_401_fails_in_strict_mode(monkeypatch) -> None:
    monkeypatch.delenv("HUGGINGFACE_TOKEN", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.setenv(canary.STRICT_ENV, "1")

    def _raise(request, timeout=12):
        raise HTTPError(
            request.full_url,
            401,
            "Unauthorized",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(canary, "urlopen", _raise)
    ok, message = canary.check_url(canary.TARGETS[0])
    assert ok is False
    assert "HTTP 401" in message


def test_non_auth_http_error_stays_hard_failure(monkeypatch) -> None:
    monkeypatch.delenv("HUGGINGFACE_TOKEN", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv(canary.STRICT_ENV, raising=False)

    def _raise(request, timeout=12):
        raise HTTPError(
            request.full_url,
            500,
            "Server Error",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(canary, "urlopen", _raise)
    ok, message = canary.check_url(canary.TARGETS[0])
    assert ok is False
    assert "HTTP 500" in message


def test_dns_error_soft_passes_in_non_strict_mode(monkeypatch) -> None:
    monkeypatch.delenv(canary.STRICT_ENV, raising=False)
    monkeypatch.setattr(
        canary,
        "urlopen",
        lambda request, timeout=12: (_ for _ in ()).throw(
            URLError(socket.gaierror(-5, "No address associated with hostname"))
        ),
    )
    ok, message = canary.check_url(canary.TARGETS[0])
    assert ok is True
    assert "network soft pass" in message


def test_dns_error_fails_in_strict_mode(monkeypatch) -> None:
    monkeypatch.setenv(canary.STRICT_ENV, "1")
    monkeypatch.setattr(
        canary,
        "urlopen",
        lambda request, timeout=12: (_ for _ in ()).throw(
            URLError(socket.gaierror(-5, "No address associated with hostname"))
        ),
    )
    ok, message = canary.check_url(canary.TARGETS[0])
    assert ok is False
    assert "URL error" in message


def test_direct_transport_exception_soft_passes_in_non_strict_mode(monkeypatch) -> None:
    monkeypatch.delenv(canary.STRICT_ENV, raising=False)

    def _raise(request, timeout=12):
        raise ConnectionResetError("connection reset by peer")

    monkeypatch.setattr(canary, "urlopen", _raise)
    ok, message = canary.check_url(canary.TARGETS[0])
    assert ok is True
    assert "transport error" in message


def test_direct_transport_exception_fails_in_strict_mode(monkeypatch) -> None:
    monkeypatch.setenv(canary.STRICT_ENV, "1")

    def _raise(request, timeout=12):
        raise ConnectionResetError("connection reset by peer")

    monkeypatch.setattr(canary, "urlopen", _raise)
    ok, message = canary.check_url(canary.TARGETS[0])
    assert ok is False
    assert "transport error" in message


def test_http_exception_soft_passes_in_non_strict_mode(monkeypatch) -> None:
    monkeypatch.delenv(canary.STRICT_ENV, raising=False)

    def _raise(request, timeout=12):
        raise http.client.RemoteDisconnected("remote end closed connection without response")

    monkeypatch.setattr(canary, "urlopen", _raise)
    ok, message = canary.check_url(canary.TARGETS[0])
    assert ok is True
    assert "transport error" in message
