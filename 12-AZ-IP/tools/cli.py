#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
12-AZ-IP/tools/cli.py — Typer-based CLI for AZ-IP tools.

Usage::
    python cli.py --help
    python cli.py engines list
    python cli.py engines run kk_geometry --phi 0.618
    python cli.py engines health
    python cli.py audit show --n 20
    python cli.py classify "describe what this does"

Add --json flag to any subcommand for machine-readable output.

Theory: ThomasCory Walker-Pearson.  Code: GitHub Copilot (AI).
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Optional

# Add lib to path
_LIB = Path(__file__).parent.parent / "lib"
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

try:
    import typer  # type: ignore
    _TYPER = True
except ImportError:
    _TYPER = False

if not _TYPER:
    print("typer not installed. Run: pip install typer")
    sys.exit(1)

from audit_log import log_invocation, read_recent  # type: ignore

app = typer.Typer(
    name="azip",
    help="AZ-IP tools — physics-grounded AI apps, engines, and calculators",
    no_args_is_help=True,
)
engines_app = typer.Typer(help="Engine registry commands")
audit_app = typer.Typer(help="Audit log commands")
app.add_typer(engines_app, name="engines")
app.add_typer(audit_app, name="audit")

# Global JSON output flag
_JSON = False


def _out(data: object) -> None:
    if _JSON:
        typer.echo(json.dumps(data, indent=2, default=str))
    else:
        typer.echo(str(data))


@app.callback()
def main(
    json_output: bool = typer.Option(False, "--json", help="Machine-readable JSON output"),
) -> None:
    global _JSON
    _JSON = json_output


# ── Engines ─────────────────────────────────────────────────────────────────

@engines_app.command("list")
def engines_list() -> None:
    """List all registered engines."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "engines"))
    from engine_registry import registry  # type: ignore
    registry.load()
    info = registry.list_engines()
    _out(info if _JSON else "\n".join(
        f"  {e['name']} v{e['version']} [{e['epistemic_label']}]"
        for e in info
    ))


@engines_app.command("run")
def engines_run(
    engine_name: str = typer.Argument(..., help="Engine name"),
    kwargs_json: str = typer.Option("{}", "--kwargs", help="JSON dict of kwargs"),
    no_hils: bool = typer.Option(False, "--no-hils", help="Skip HILS gate (dev only)"),
) -> None:
    """Run a named engine with the given kwargs."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "engines"))
    from engine_registry import registry  # type: ignore

    registry.load()
    try:
        kwargs = json.loads(kwargs_json)
    except json.JSONDecodeError as exc:
        typer.echo(f"Invalid JSON kwargs: {exc}", err=True)
        raise typer.Exit(1)

    start = time.time()
    result = asyncio.run(registry.run(engine_name, hils_approved=not no_hils, **kwargs))
    elapsed = time.time() - start
    log_invocation(
        tool_name=f"engines.run.{engine_name}",
        args=kwargs,
        result=result.to_dict() if hasattr(result, "to_dict") else result,
        elapsed_s=elapsed,
    )
    data = result.to_dict() if hasattr(result, "to_dict") else result
    _out(data)
    if hasattr(result, "ok") and not result.ok:
        raise typer.Exit(1)


@engines_app.command("health")
def engines_health() -> None:
    """Check health of all registered engines."""
    sys.path.insert(0, str(Path(__file__).parent.parent / "engines"))
    from engine_registry import registry  # type: ignore

    registry.load()
    results = asyncio.run(registry.health_all())
    _out(results)
    all_ok = all(v.get("ok", False) for v in results.values())
    if not all_ok:
        raise typer.Exit(1)


# ── Audit ────────────────────────────────────────────────────────────────────

@audit_app.command("show")
def audit_show(
    n: int = typer.Option(20, "--n", "-n", help="Number of recent records to show"),
) -> None:
    """Show recent audit log entries."""
    records = read_recent(n=n)
    if _JSON:
        _out(records)
    else:
        for r in records:
            typer.echo(
                f"  [{r.get('ts','')}] {r.get('user','')} → {r.get('tool','')} "
                f"({r.get('elapsed_s',0):.3f}s)"
            )


# ── Classify ─────────────────────────────────────────────────────────────────

@app.command("classify")
def classify(
    task_summary: str = typer.Argument(..., help="Task description to classify"),
    axiomzero_url: str = typer.Option("http://localhost:8000", "--url"),
) -> None:
    """Classify a task description via the Pentad governance endpoint."""
    from az_ip_common.pentad import pentad_classify  # type: ignore

    start = time.time()
    result = asyncio.run(pentad_classify(task_summary, axiomzero_url=axiomzero_url))
    elapsed = time.time() - start
    log_invocation("classify", task_summary, result, elapsed_s=elapsed)
    _out(result)


if __name__ == "__main__":
    app()
