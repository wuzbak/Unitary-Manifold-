# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero android/client.py — Termux Thin Client

Lightweight CLI that connects to the Omen 45L's AxiomZero API.
The phone is read-mostly (status, query, approve/reject HILS decisions).
Write operations (code changes, pillar additions) require the desktop client.

Usage::
    python client.py --server http://192.168.x.x:8000

Or set AXIOMZERO_SERVER environment variable.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

# Minimal dependencies for Termux compatibility
try:
    import httpx
    _HTTPX = True
except ImportError:
    _HTTPX = False
    print("⚠ httpx not installed. Run: pip install httpx")

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    _RICH = True
    console = Console()
except ImportError:
    _RICH = False
    console = None  # type: ignore[assignment]


def _print(msg: str, style: str = "") -> None:
    if _RICH and console:
        console.print(msg, style=style)
    else:
        print(msg)


class AxiomZeroClient:
    """Thin client for the AxiomZero API server."""

    def __init__(self, server_url: str):
        self.server = server_url.rstrip("/")
        if not _HTTPX:
            raise ImportError("httpx required: pip install httpx")
        self.client = httpx.Client(base_url=self.server, timeout=30)

    def _get(self, path: str) -> Any:
        try:
            r = self.client.get(path)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPError as exc:
            _print(f"✗ HTTP error: {exc}", "red")
            return None
        except Exception as exc:
            _print(f"✗ Error: {exc}", "red")
            return None

    def _post(self, path: str, data: Dict) -> Any:
        try:
            r = self.client.post(path, json=data)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPError as exc:
            _print(f"✗ HTTP error: {exc}", "red")
            return None
        except Exception as exc:
            _print(f"✗ Error: {exc}", "red")
            return None

    def status(self) -> None:
        """Show orchestrator status."""
        data = self._get("/status")
        if not data:
            return
        _print(f"\n[bold cyan]⚛ AxiomZero Status[/bold cyan] — {self.server}")
        _print(f"  LangGraph: {'✔' if data.get('langgraph_available') else '⚠ stub mode'}")
        _print(f"  Active tasks: {data.get('active_tasks', 0)}")
        _print(f"  Pending approvals: {data.get('pending_approvals', 0)}")
        _print(f"  Total tasks: {data.get('total_tasks', 0)}")

        if data.get("pending_approvals", 0) > 0:
            _print("\n  [bold yellow]⚠ Human approval required![/bold yellow]")
            _print("  Run: python client.py --server ... approvals")

    def tasks(self, n: int = 10) -> None:
        """List recent tasks."""
        data = self._get("/tasks")
        if data is None:
            return

        _print("\n[bold cyan]Recent Tasks[/bold cyan]")
        if not data:
            _print("  (none)")
            return

        for t in list(reversed(data))[:n]:
            status = t.get("status", "?")
            icon = {"complete": "✔", "human_review": "⚠", "failed": "✗",
                    "running": "◎", "rejected": "✗"}.get(status, "·")
            color = {"complete": "green", "human_review": "yellow",
                     "failed": "red", "rejected": "red"}.get(status, "white")
            _print(f"  {icon} [{color}]{t['task_id']}[/{color}] "
                   f"[dim]{t.get('epistemic_label', '')}[/dim] "
                   f"{t['description'][:60]}")

    def approvals(self) -> None:
        """Show pending HILS approvals."""
        data = self._get("/approvals/pending")
        if not data:
            _print("  No pending approvals.")
            return

        _print(f"\n[bold yellow]⚠ {len(data)} task(s) require your approval[/bold yellow]")
        for t in data:
            _print(f"\n  Task: [bold]{t['task_id']}[/bold]")
            _print(f"  Description: {t['description']}")
            _print(f"  Label: {t.get('epistemic_label', '')}")
            _print(f"  Results: {json.dumps(t.get('results', {}))[:200]}")

            answer = input("\n  Approve? [y/N] ").strip().lower()
            approved = answer in ("y", "yes")
            result = self._post(f"/tasks/{t['task_id']}/approve",
                                {"approved": approved, "note": "Android thin client decision"})
            if result:
                _print(f"  {'✔ Approved' if approved else '✗ Rejected'}", "green" if approved else "red")

    def query(self, question: str) -> None:
        """Submit a task to the agent network."""
        data = self._post("/tasks", {
            "description": question,
            "epistemic_label": "HARDGATE",
            "payload": {"web_query": question},
        })
        if data:
            _print(f"✔ Task submitted: [cyan]{data.get('task_id')}[/cyan]")

    def rag(self, query: str) -> None:
        """Query the RAG vector store."""
        data = self._post("/rag/query", {"query": query, "n_results": 3})
        if data:
            _print(f"\n[bold cyan]RAG Results for:[/bold cyan] {query}")
            for i, r in enumerate(data.get("results", []), 1):
                source = r.get("source", "?")
                text = r.get("text", "")[:300]
                _print(f"\n  [{i}] {source}\n  {text}")

    def logs(self, n: int = 20) -> None:
        """Show recent audit log."""
        data = self._get(f"/logs?n={n}")
        if not data:
            return
        _print("\n[bold cyan]Recent Audit Log[/bold cyan]")
        for e in data:
            import datetime
            ts = datetime.datetime.fromtimestamp(e.get("ts", 0)).strftime("%H:%M:%S")
            event = e.get("event_type", "?")
            mgr = e.get("manager", "?")
            _print(f"  [{ts}] {event} · {mgr} · {e.get('task_id', '')}")

    def vram(self) -> None:
        """Show GPU VRAM status."""
        data = self._get("/health/vram")
        if data:
            pct = data.get("vram_pct")
            if pct is not None:
                color = "green" if pct < 70 else "yellow" if pct < 90 else "red"
                _print(f"  GPU VRAM: [{color}]{pct:.1f}%[/{color}] {'⚠ PAUSED' if data.get('paused') else ''}")
            else:
                _print("  GPU VRAM: unavailable (no GPU or nvidia-smi absent)")

    def close(self) -> None:
        self.client.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AxiomZero Android/Termux thin client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  status      Show system status
  tasks       List recent tasks
  approvals   Review and approve/reject pending HILS decisions
  query TEXT  Submit a task to the agent network
  rag TEXT    Query the RAG vector store
  logs        Show recent audit log
  vram        Show GPU VRAM status
        """,
    )
    parser.add_argument(
        "--server",
        default=os.environ.get("AXIOMZERO_SERVER", "http://localhost:8000"),
        help="AxiomZero server URL (default: AXIOMZERO_SERVER env or http://localhost:8000)",
    )
    parser.add_argument("command", nargs="?", default="status",
                        choices=["status", "tasks", "approvals", "query", "rag", "logs", "vram"],
                        help="Command to run")
    parser.add_argument("text", nargs="*", help="Argument for query/rag commands")
    args = parser.parse_args()

    if not _HTTPX:
        print("Install httpx: pip install httpx")
        sys.exit(1)

    client = AxiomZeroClient(args.server)

    try:
        if args.command == "status":
            client.status()
        elif args.command == "tasks":
            client.tasks()
        elif args.command == "approvals":
            client.approvals()
        elif args.command == "query":
            if not args.text:
                print("Usage: python client.py query <question>")
                sys.exit(1)
            client.query(" ".join(args.text))
        elif args.command == "rag":
            if not args.text:
                print("Usage: python client.py rag <search terms>")
                sys.exit(1)
            client.rag(" ".join(args.text))
        elif args.command == "logs":
            client.logs()
        elif args.command == "vram":
            client.vram()
    except KeyboardInterrupt:
        _print("\n  Interrupted.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
