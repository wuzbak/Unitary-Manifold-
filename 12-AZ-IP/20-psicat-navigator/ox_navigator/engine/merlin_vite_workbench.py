# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Authenticated client for the standalone PsiCat Vite Web Workbench."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


DEFAULT_WORKBENCH_URL = "http://127.0.0.1:8327"


def _workbench_url() -> str:
    candidate = str(os.environ.get("PSICAT_VITE_WORKBENCH_URL") or DEFAULT_WORKBENCH_URL).strip().rstrip("/")
    parsed = urlsplit(candidate)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "localhost"}
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ValueError("PsiCat Vite Workbench URL must be a loopback HTTP origin.")
    return candidate


def _request(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    token = str(os.environ.get("PSICAT_VITE_WORKBENCH_TOKEN") or "")
    if len(token) < 32:
        return {
            "ok": False,
            "error": "PsiCat Vite Workbench is not connected: configure PSICAT_VITE_WORKBENCH_TOKEN (at least 32 characters).",
        }
    try:
        url = _workbench_url() + path
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=body, headers=headers, method="POST" if body is not None else "GET")
    try:
        with urlopen(request, timeout=8) as response:
            result = json.loads(response.read(256 * 1024).decode("utf-8"))
    except HTTPError as exc:
        return {"ok": False, "error": f"Workbench request failed with HTTP {exc.code}."}
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": f"PsiCat Vite Workbench is unavailable: {type(exc).__name__}."}
    if not isinstance(result, dict):
        return {"ok": False, "error": "Workbench returned an invalid response."}
    return result


def workbench_status(**_args: Any) -> dict[str, Any]:
    return {"data": _request("/api/status")}


def list_workbench_projects(**_args: Any) -> dict[str, Any]:
    return {"data": _request("/api/projects")}


def inspect_workbench_project(*, name: str, **_args: Any) -> dict[str, Any]:
    return {"data": _request("/api/action", {"action": "inspect", "name": name})}


def create_workbench_project(*, name: str, template: str = "vanilla-js", **_args: Any) -> dict[str, Any]:
    return {"data": _request("/api/action", {"action": "create", "name": name, "template": template})}


def start_workbench_preview(*, name: str, **_args: Any) -> dict[str, Any]:
    return {"data": _request("/api/action", {"action": "preview_start", "name": name})}


def stop_workbench_preview(*, name: str, **_args: Any) -> dict[str, Any]:
    return {"data": _request("/api/action", {"action": "preview_stop", "name": name})}


def build_workbench_project(*, name: str, **_args: Any) -> dict[str, Any]:
    return {"data": _request("/api/action", {"action": "build", "name": name})}
