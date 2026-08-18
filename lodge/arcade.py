# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
lodge/arcade.py — Pillar Arcade CLI Runner (Zone 1)

Interactive command-line interface for running physics challenges against the
208-pillar registry.  Any agent — human, LLM, or script — can use this runner
to submit answers and receive scored results.

Usage
-----
    # Interactive human session
    python -m lodge.arcade

    # Scripted agent session (pass answers via stdin JSON)
    echo '{"2": 0.3243, "4": {"ns": 0.9635, "r_eff": 0.0315}}' | \\
        python -m lodge.arcade --agent-label my-llm --zone arcade --batch

    # List available challenges
    python -m lodge.arcade --list

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure repo root is on path
_REPO_ROOT = Path(__file__).parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from lodge.pillar_registry import REGISTRY, PillarEntry
from lodge.scoring import score_answer, PrecisionResult
from lodge.session_logger import SessionLogger
from lodge.leaderboard import Leaderboard

__all__ = ["run_interactive", "run_batch", "main"]

# ANSI colour codes (disabled automatically when not a TTY)
_USE_COLOUR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    if not _USE_COLOUR:
        return text
    codes = {
        "green": "\033[32m", "red": "\033[31m", "yellow": "\033[33m",
        "cyan": "\033[36m", "blue": "\033[34m", "bold": "\033[1m",
        "reset": "\033[0m", "dim": "\033[2m",
    }
    return f"{codes.get(code, '')}{text}{codes['reset']}"


def _banner() -> None:
    print(_c("cyan", "═" * 70))
    print(_c("bold", "  AxiomZero Logic Lodge — Pillar Arcade  (Zone 1)"))
    print(_c("dim", "  208 derivation challenges. Every score is a mathematical truth value."))
    print(_c("cyan", "═" * 70))
    print()


def _print_challenge(entry: PillarEntry, show_hint: bool) -> None:
    tier_colour = {"easy": "green", "medium": "yellow", "hard": "red"}
    colour = tier_colour.get(entry.difficulty, "reset")
    print(_c("bold", f"\n── Pillar #{entry.pillar_id}: {entry.name}"))
    print(_c(colour, f"   [{entry.difficulty.upper()}] [{entry.domain}]"))
    print()
    # Wrap long prompt text
    for line in textwrap.wrap(entry.prompt, width=68):
        print(f"   {line}")
    if show_hint and entry.difficulty in ("easy", "medium"):
        print()
        print(_c("dim", f"   Hint: {entry.hint}"))
    print()


def _print_result(result: PrecisionResult) -> None:
    colour = "green" if result.passed else "red"
    status = "✅  PASS" if result.passed else "❌  BELOW THRESHOLD"
    print(_c(colour, f"\n   {status}"))
    print(f"   Raw score:   {result.raw_score:.4f}")
    if result.epistemic_bonus:
        print(_c("cyan", f"   Epistemic bonus:  +{result.epistemic_bonus:.4f}"))
    if result.overclaim_penalty:
        print(_c("red", f"   Overclaim penalty: −{result.overclaim_penalty:.4f}"))
    print(_c("bold", f"   Final score: {result.final_score:.4f}"))
    if result.detail.get("per_key"):
        print(_c("dim", "   Per-key breakdown:"))
        for k, v in result.detail["per_key"].items():
            bar = "█" * int(v * 20) + "░" * (20 - int(v * 20))
            print(_c("dim", f"     {k:30s} {bar}  {v:.4f}"))
    print()


# ---------------------------------------------------------------------------
# Interactive session
# ---------------------------------------------------------------------------

def run_interactive(
    agent_label: str = "human",
    difficulty_filter: Optional[str] = None,
    domain_filter: Optional[str] = None,
    show_hints: bool = True,
) -> None:
    """Run an interactive terminal session for a human or pasted-in answers."""
    _banner()
    entries = REGISTRY.all()
    if difficulty_filter:
        entries = [e for e in entries if e.difficulty == difficulty_filter]
    if domain_filter:
        entries = [e for e in entries if e.domain == domain_filter]

    if not entries:
        print("No challenges match the selected filters.")
        return

    logger = SessionLogger(agent_label=agent_label, agent_class="human", zone="arcade")
    logger.start()
    lb = Leaderboard()

    print(f"  {len(entries)} challenges loaded.  Type your answer and press Enter.")
    print(f"  Press Ctrl-C or type 'quit' to end the session.\n")

    for entry in entries:
        _print_challenge(entry, show_hints)
        try:
            raw = input("   Your answer › ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Session interrupted — saving progress…")
            break

        if raw.lower() in ("quit", "exit", "q"):
            print("\n  Ending session — saving progress…")
            break

        # Parse answer: try JSON first, then float
        agent_answer: Any
        try:
            agent_answer = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            try:
                agent_answer = float(raw)
            except ValueError:
                agent_answer = raw  # string — will score 0 for numeric pillars

        # Load ground truth
        try:
            truth = entry.load_ground_truth()
        except Exception as exc:
            print(_c("red", f"   ⚠  Could not load ground truth: {exc}"))
            continue

        result = score_answer(
            pillar_id=entry.pillar_id,
            agent_label=agent_label,
            agent_answer=agent_answer,
            ground_truth=truth,
            expected_type=entry.expected_type,
        )
        _print_result(result)
        logger.record(entry.pillar_id, result.raw_score, result.final_score)
        lb.upsert(agent_label=agent_label, result=result, zone="arcade")

        cont = input("   Continue to next challenge? [Y/n] › ").strip().lower()
        if cont in ("n", "no"):
            break

    path = logger.close()
    print(_c("cyan", f"\n  Session saved → {path}"))
    print(_c("bold", f"  Mean score: {_mean_score(logger):.4f}"))
    _print_leaderboard_snippet(lb, agent_label)


def _mean_score(logger: SessionLogger) -> float:
    scores = list(logger._final_scores.values())
    return sum(scores) / max(len(scores), 1)


def _print_leaderboard_snippet(lb: "Leaderboard", highlight: str) -> None:
    rows = lb.top(n=5, zone="arcade")
    if not rows:
        return
    print(_c("cyan", "\n  ── Arcade Leaderboard (top 5) ───────────────────────────"))
    for i, row in enumerate(rows, 1):
        flag = " ◀" if row["agent_label"] == highlight else ""
        print(f"  {i:2d}. {row['agent_label']:30s} {row['mean_score']:.4f}{flag}")
    print()


# ---------------------------------------------------------------------------
# Batch (scripted) session
# ---------------------------------------------------------------------------

def run_batch(
    answers: Dict[str, Any],
    agent_label: str = "script",
    agent_class: str = "llm-api",
    zone: str = "arcade",
) -> List[PrecisionResult]:
    """
    Score a pre-computed dict of {pillar_id_str: answer} without any I/O.

    Returns a list of PrecisionResult objects and writes a session file.
    """
    logger = SessionLogger(agent_label=agent_label, agent_class=agent_class, zone=zone)
    logger.start()
    lb = Leaderboard()
    results: List[PrecisionResult] = []

    for pid_str, agent_answer in answers.items():
        try:
            pid = int(pid_str)
        except ValueError:
            continue

        entry = REGISTRY.get(pid)
        if entry is None:
            continue

        try:
            truth = entry.load_ground_truth()
        except Exception:
            continue

        result = score_answer(
            pillar_id=pid,
            agent_label=agent_label,
            agent_answer=agent_answer,
            ground_truth=truth,
            expected_type=entry.expected_type,
        )
        logger.record(pid, result.raw_score, result.final_score)
        lb.upsert(agent_label=agent_label, result=result, zone=zone)
        results.append(result)

    logger.close()
    return results


# ---------------------------------------------------------------------------
# List challenges
# ---------------------------------------------------------------------------

def list_challenges(
    difficulty: Optional[str] = None,
    domain: Optional[str] = None,
) -> None:
    """Pretty-print the challenge catalogue."""
    entries = REGISTRY.all()
    if difficulty:
        entries = [e for e in entries if e.difficulty == difficulty]
    if domain:
        entries = [e for e in entries if e.domain == domain]

    tier_colour = {"easy": "green", "medium": "yellow", "hard": "red"}
    print(_c("bold", f"\n{'ID':>4}  {'Difficulty':10}  {'Domain':12}  Name"))
    print("─" * 68)
    for e in entries:
        col = tier_colour.get(e.difficulty, "reset")
        print(
            f"{e.pillar_id:>4}  "
            + _c(col, f"{e.difficulty:10}  ")
            + f"{e.domain:12}  {e.name}"
        )
    print(f"\n  {len(entries)} challenge(s) listed.  Registry: {REGISTRY.summary()}\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="AxiomZero Logic Lodge — Pillar Arcade runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--agent-label", default="anonymous",
                        help="Identifier for this agent in the leaderboard")
    parser.add_argument("--agent-class", default="human",
                        choices=["human", "llm-api", "rl-agent"],
                        help="Class of agent (for leaderboard grouping)")
    parser.add_argument("--zone", default="arcade",
                        choices=["arcade", "lodge", "training", "exchange"])
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"],
                        help="Filter to a specific difficulty tier")
    parser.add_argument("--domain", help="Filter to a specific domain")
    parser.add_argument("--no-hints", action="store_true",
                        help="Hide hints (all difficulties)")
    parser.add_argument("--list", action="store_true",
                        help="List all available challenges and exit")
    parser.add_argument("--batch", action="store_true",
                        help="Read a JSON dict of {pillar_id: answer} from stdin")
    args = parser.parse_args(argv)

    if args.list:
        list_challenges(difficulty=args.difficulty, domain=args.domain)
        return

    if args.batch:
        raw = sys.stdin.read().strip()
        try:
            answers = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"Error: could not parse stdin as JSON: {exc}", file=sys.stderr)
            sys.exit(1)
        results = run_batch(answers, agent_label=args.agent_label,
                            agent_class=args.agent_class, zone=args.zone)
        for r in results:
            print(r.summary())
        mean = sum(r.final_score for r in results) / max(len(results), 1)
        print(f"\nMean score: {mean:.4f}  ({len(results)} pillars attempted)")
        return

    run_interactive(
        agent_label=args.agent_label,
        difficulty_filter=args.difficulty,
        domain_filter=args.domain,
        show_hints=not args.no_hints,
    )


if __name__ == "__main__":
    main()
