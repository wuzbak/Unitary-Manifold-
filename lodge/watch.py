# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
lodge/watch.py — Real-Time Observability Terminal Monitor (Zone 4)

Reads live session files from the lodge ledger directory and renders a
colour-coded terminal dashboard at 2 Hz.  Runs in a separate console window
alongside active Arcade / Training sessions.

Usage
-----
    # Watch all active sessions
    python -m lodge.watch

    # Watch only RL training sessions
    python -m lodge.watch --zone training

    # Watch leaderboard only
    python -m lodge.watch --leaderboard

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from lodge.session_logger import list_sessions, _DEFAULT_LEDGER_DIR
from lodge.leaderboard import Leaderboard
from lodge.pillar_registry import REGISTRY

__all__ = ["render_dashboard", "watch"]

_REFRESH_HZ = 2.0

# ANSI colour helpers
def _g(t: str) -> str: return f"\033[32m{t}\033[0m"
def _y(t: str) -> str: return f"\033[33m{t}\033[0m"
def _r(t: str) -> str: return f"\033[31m{t}\033[0m"
def _c(t: str) -> str: return f"\033[36m{t}\033[0m"
def _b(t: str) -> str: return f"\033[34m{t}\033[0m"
def _m(t: str) -> str: return f"\033[35m{t}\033[0m"
def _bold(t: str) -> str: return f"\033[1m{t}\033[0m"
def _dim(t: str) -> str: return f"\033[2m{t}\033[0m"

_BAR_WIDTH = 20


def _score_bar(score: float) -> str:
    filled = int(score * _BAR_WIDTH)
    empty = _BAR_WIDTH - filled
    bar = "█" * filled + "░" * empty
    if score >= 0.90:
        return _g(bar)
    elif score >= 0.75:
        return _y(bar)
    else:
        return _r(bar)


def _score_colour(score: float) -> str:
    if score >= 0.90:
        return _g(f"{score:.4f}")
    elif score >= 0.75:
        return _y(f"{score:.4f}")
    return _r(f"{score:.4f}")


def _clear() -> None:
    os.system("clear" if os.name != "nt" else "cls")


def render_dashboard(
    zone: Optional[str] = None,
    ledger_dir: Optional[Path] = None,
    leaderboard_only: bool = False,
    n_top: int = 10,
) -> None:
    """Render one frame of the observability dashboard."""
    _clear()
    lb = Leaderboard()
    sessions = list_sessions(ledger_dir=ledger_dir, zone=zone)

    # ── Header ───────────────────────────────────────────────────────────────
    print(_g("═" * 76))
    print(_bold("  AXIOMZERO LOGIC LODGE — OBSERVABILITY CONSOLE") +
          _dim(f"  (zone: {zone or 'all'})"))
    print(_g("═" * 76))

    # ── Leaderboard ───────────────────────────────────────────────────────────
    top = lb.top(n=n_top, zone=zone)
    print(_bold("\n  LEADERBOARD — Top agents by mean final score"))
    print(_b("  " + "─" * 72))
    if not top:
        print(_dim("  No scores recorded yet."))
    else:
        print(_dim(f"  {'#':>3}  {'Agent':30s}  {'Score':>8}  {'Pillars':>7}  Last active"))
        for i, row in enumerate(top, 1):
            score = float(row.get("mean_score") or 0.0)
            n_att = int(row.get("pillars_attempted") or 0)
            latest = str(row.get("latest") or "")[:16]
            print(f"  {i:>3}  {row['agent_label']:30s}  "
                  f"{_score_colour(score)}  {n_att:>7}  {_dim(latest)}")

    lb_summary = lb.summary()
    print(_dim(f"\n  {lb_summary['n_agents']} agents · "
               f"{lb_summary['n_score_rows']} total scores · "
               f"global mean: {lb_summary['global_mean_score']:.4f}"))

    if leaderboard_only:
        print(_g("\n" + "═" * 76))
        return

    # ── Recent sessions ───────────────────────────────────────────────────────
    print(_bold("\n  RECENT SESSIONS"))
    print(_b("  " + "─" * 72))
    shown = sessions[:5]
    if not shown:
        print(_dim("  No session files in ledger directory yet."))
    else:
        for s in shown:
            sid = s.get("session_id", "")[:8]
            label = s.get("agent_label", "?")
            z = s.get("zone", "?")
            mean = float(s.get("mean_score") or 0.0)
            n_att = len(s.get("pillars_attempted") or [])
            ts = str(s.get("timestamp_end") or s.get("timestamp_start") or "")[:16]
            status = _g("● CLOSED") if s.get("timestamp_end") else _y("● ACTIVE")
            print(f"  {status}  {sid}…  {label:25s}  zone={z:8s}  "
                  f"pillars={n_att:3d}  {_score_colour(mean)}  {_dim(ts)}")

    # ── Pillar difficulty distribution ────────────────────────────────────────
    print(_bold("\n  REGISTRY SUMMARY"))
    print(_b("  " + "─" * 72))
    summary = REGISTRY.summary()
    print(f"  Total pillars in registry: {_c(str(summary['total']))}")
    for diff, count in summary.get("by_difficulty", {}).items():
        colour = {"easy": _g, "medium": _y, "hard": _r}.get(diff, _dim)
        print(f"  {colour(diff.capitalize():10s)}  {count} challenges")

    # ── Hardest pillars (lowest mean scores) ─────────────────────────────────
    pillar_stats = []
    for entry in REGISTRY.all():
        ps = lb.pillar_stats(entry.pillar_id)
        if ps.get("mean_score") is not None:
            pillar_stats.append((entry.pillar_id, entry.name[:35], ps["mean_score"], ps["n_attempts"]))

    if pillar_stats:
        pillar_stats.sort(key=lambda x: x[2])
        print(_bold("\n  HARDEST PILLARS (lowest mean score)"))
        print(_b("  " + "─" * 72))
        for pid, name, ms, n in pillar_stats[:5]:
            print(f"  Pillar {pid:>3}  {name:38s}  "
                  f"{_score_bar(ms)}  {_score_colour(ms)}  (n={n})")

    print(_g("\n" + "═" * 76))
    print(_dim(f"  Refreshing every {1/(_REFRESH_HZ):.1f}s · Ctrl-C to detach"))


def watch(
    zone: Optional[str] = None,
    ledger_dir: Optional[Path] = None,
    leaderboard_only: bool = False,
) -> None:
    """Run the dashboard in a continuous refresh loop."""
    try:
        while True:
            render_dashboard(zone=zone, ledger_dir=ledger_dir,
                             leaderboard_only=leaderboard_only)
            time.sleep(1.0 / _REFRESH_HZ)
    except KeyboardInterrupt:
        print("\n\nObservability console detached.")
        sys.exit(0)


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="AxiomZero Lodge — Observability Console"
    )
    parser.add_argument("--zone", choices=["arcade", "lodge", "training", "exchange"])
    parser.add_argument("--leaderboard", action="store_true",
                        help="Show leaderboard only (no session details)")
    parser.add_argument("--once", action="store_true",
                        help="Render one frame and exit (useful for CI / snapshots)")
    args = parser.parse_args(argv)

    if args.once:
        render_dashboard(zone=args.zone, leaderboard_only=args.leaderboard)
    else:
        watch(zone=args.zone, leaderboard_only=args.leaderboard)


if __name__ == "__main__":
    main()
