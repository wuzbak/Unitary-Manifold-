# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import importlib.util
import http.client
import socket
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest
import yaml


_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "9-INFRASTRUCTURE"
    / "check_hf_spaces_canary.py"
)
_SPEC = importlib.util.spec_from_file_location("check_hf_spaces_canary", _MODULE_PATH)
assert _SPEC and _SPEC.loader
canary = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(canary)


def test_space_deployment_is_mainline_or_explicit_manual_with_read_only_github_token():
    workflow = yaml.safe_load(
        (_MODULE_PATH.parents[1] / ".github/workflows/deploy-hf-spaces.yml").read_text()
    )
    events = workflow.get("on", workflow.get(True))
    assert events["push"]["branches"] == ["main"]
    assert events["push"]["paths"] == ["hf-spaces/**"]
    assert "workflow_dispatch" in events
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["jobs"]["deploy"]["timeout-minutes"] == 30


@pytest.mark.parametrize(
    "readme",
    sorted((_MODULE_PATH.parents[1] / "hf-spaces").glob("*/README.md")),
    ids=lambda path: path.parent.name,
)
def test_space_readme_short_descriptions_fit_hub_limit(readme: Path) -> None:
    text = readme.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return
    metadata = yaml.safe_load(text.split("---", 2)[1])
    if "sdk" not in metadata or "short_description" not in metadata:
        return
    description = metadata["short_description"]
    assert isinstance(description, str), f"{readme}: short_description must be text"
    assert len(description) <= 60, (
        f"{readme}: short_description has {len(description)} characters; "
        "Hugging Face Spaces permits at most 60"
    )


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


def test_http_exception_fails_in_strict_mode(monkeypatch) -> None:
    monkeypatch.setenv(canary.STRICT_ENV, "1")

    def _raise(request, timeout=12):
        raise http.client.RemoteDisconnected("remote end closed connection without response")

    monkeypatch.setattr(canary, "urlopen", _raise)
    ok, message = canary.check_url(canary.TARGETS[0])
    assert ok is False
    assert "transport error" in message


def test_unexpected_transport_exception_hard_fails(monkeypatch) -> None:
    monkeypatch.delenv(canary.STRICT_ENV, raising=False)

    def _raise(request, timeout=12):
        raise OSError("unexpected local io failure")

    monkeypatch.setattr(canary, "urlopen", _raise)
    ok, message = canary.check_url(canary.TARGETS[0])
    assert ok is False
    assert "error:" in message


def test_main_aggregates_failures_and_returns_nonzero(monkeypatch, capsys) -> None:
    monkeypatch.setattr(canary, "TARGETS", ["https://ok", "https://fail"])

    def _check_url(url: str, timeout: int = 12) -> tuple[bool, str]:
        if url.endswith("fail"):
            return False, f"{url} -> HTTP 500"
        return True, f"{url} -> 200"

    monkeypatch.setattr(canary, "check_url", _check_url)
    assert canary.main() == 1
    output = capsys.readouterr().out
    assert "https://ok -> 200" in output
    assert "https://fail -> HTTP 500" in output
    assert "HF CANARY FAILED" in output
