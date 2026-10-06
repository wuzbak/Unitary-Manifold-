# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Read-only JSON reporting and escaped, offline static dashboards."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

from .engine import evaluate


def report(attempt: Path, baseline: Path | None = None) -> dict:
    result = evaluate(attempt)
    if baseline:
        previous = evaluate(baseline)
        compatible = previous["compatibility"] == result["compatibility"]
        result["comparison"] = {
            "compatible": compatible,
            "baseline_attempt": previous["attempt_id"],
            "reason": None if compatible else "Source/environment/settings/engine differ; no comparison",
        }
        if compatible and result["status"] == previous["status"] == "passed":
            result["comparison"]["duration_delta_seconds"] = (
                sum(result["durations"].values()) - sum(previous["durations"].values()))
            result["comparison"]["count_delta"] = {
                key: result["counts"].get(key, 0) - previous["counts"].get(key, 0)
                for key in set(result["counts"]) | set(previous["counts"])
            }
        elif compatible:
            result["comparison"]["reason"] = "Both attempts must pass before performance comparison"
    return result


def dashboard(data: dict) -> str:
    # The dashboard is a rendering of exactly the JSON evaluation, not another gate.
    payload = escape(json.dumps(data, sort_keys=True, indent=2))
    rows = "".join(
        f"<tr><td>{escape(str(name))}</td><td>{escape(str(status))}</td></tr>"
        for name, status in data["suites"].items())
    return (
        "<!doctype html><html lang='en'><meta charset='utf-8'>"
        "<meta http-equiv='Content-Security-Policy' "
        "content=\"default-src 'none'; style-src 'unsafe-inline'\">"
        "<title>UM-ARTS evidence dashboard</title>"
        "<style>body{font-family:system-ui;max-width:1000px;margin:2em auto;padding:1em}"
        "pre{white-space:pre-wrap;overflow-wrap:anywhere}td,th{padding:.5em;text-align:left}</style>"
        f"<h1>UM-ARTS: {escape(data['status'])}</h1>"
        f"<p>Attempt {escape(data['attempt_id'])}</p>"
        "<p>Execution evidence only. Python↔Lean correspondence remains unresolved.</p>"
        "<table><thead><tr><th>Suite</th><th>Status</th></tr></thead>"
        f"<tbody>{rows}</tbody></table><h2>Evaluation data</h2><pre>{payload}</pre></html>"
    )
