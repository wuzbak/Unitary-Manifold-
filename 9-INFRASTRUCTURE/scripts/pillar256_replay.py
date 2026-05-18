#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Public Pillar 256 replay utilities: snapshot, verify, compare, trend."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.core.pillar256_reproducibility import (  # noqa: E402
    DEFAULT_HISTORY_PATH,
    DEFAULT_TREND_PANELS_PATH,
    create_execution_snapshot,
    create_signed_run_manifest,
    read_run_history,
    verify_signed_run_manifest,
    write_snapshot_bundle,
    append_run_history,
    build_trend_panels,
    load_threshold_metadata,
    write_trend_panels,
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _print_gate_statuses(snapshot: dict) -> None:
    print("Gate statuses:")
    for gid, payload in sorted(snapshot["falsification_gate_evaluations"].items()):
        print(f"  - {gid}: {payload['status']}")


def cmd_snapshot(args: argparse.Namespace) -> int:
    observations = _load_json(Path(args.observations_json)) if args.observations_json else {}
    key = os.environ.get(args.signing_key_env) if args.signing_key_env else None

    snapshot = create_execution_snapshot(observations=observations)
    manifest = create_signed_run_manifest(snapshot, signing_key=key)

    written = write_snapshot_bundle(snapshot, manifest)
    append_run_history(snapshot, manifest, history_path=Path(args.history_path))

    trend = build_trend_panels(read_run_history(Path(args.history_path)), load_threshold_metadata())
    trend_path = write_trend_panels(trend, output_path=Path(args.trend_output))

    print(f"Snapshot written: {written['snapshot_path']}")
    print(f"Manifest written: {written['manifest_path']}")
    print(f"Trend panels written: {trend_path}")
    _print_gate_statuses(snapshot)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    snapshot = _load_json(Path(args.snapshot))
    manifest = _load_json(Path(args.manifest))
    key = os.environ.get(args.signing_key_env) if args.signing_key_env else None

    verdict = verify_signed_run_manifest(snapshot, manifest, signing_key=key)
    if verdict["valid"]:
        print("PASS: snapshot and manifest verification succeeded")
        return 0

    print("FAIL: verification errors")
    for err in verdict["errors"]:
        print(f"  - {err}")
    return 1


def cmd_compare(args: argparse.Namespace) -> int:
    left = _load_json(Path(args.left_snapshot))
    right = _load_json(Path(args.right_snapshot))

    print(f"Compare snapshots: {left['snapshot_id']} -> {right['snapshot_id']}")

    left_verdict = left["pillar256_report"]["hardening_verdict"]
    right_verdict = right["pillar256_report"]["hardening_verdict"]

    changed = 0
    for key in sorted(set(left_verdict) | set(right_verdict)):
        lv = left_verdict.get(key)
        rv = right_verdict.get(key)
        marker = "CHANGED" if lv != rv else "stable"
        if lv != rv:
            changed += 1
        print(f"  - {key}: {lv} -> {rv} [{marker}]")

    left_gates = left.get("falsification_gate_evaluations", {})
    right_gates = right.get("falsification_gate_evaluations", {})
    for gid in sorted(set(left_gates) | set(right_gates)):
        ls = left_gates.get(gid, {}).get("status")
        rs = right_gates.get(gid, {}).get("status")
        marker = "CHANGED" if ls != rs else "stable"
        print(f"  - gate {gid}: {ls} -> {rs} [{marker}]")

    return 0 if changed == 0 else 2


def cmd_trend(args: argparse.Namespace) -> int:
    history = read_run_history(Path(args.history_path))
    metadata = load_threshold_metadata()
    trend = build_trend_panels(history, metadata)
    output = write_trend_panels(trend, output_path=Path(args.trend_output))
    print(f"Trend panels written: {output}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    snap = sub.add_parser("snapshot", help="Generate Pillar 256 snapshot + signed manifest")
    snap.add_argument(
        "--observations-json",
        default=None,
        help="Optional path to JSON file with gate observations keyed by gate ID.",
    )
    snap.add_argument(
        "--signing-key-env",
        default="PILLAR256_MANIFEST_HMAC_KEY",
        help="Environment variable name containing optional HMAC signing key.",
    )
    snap.add_argument(
        "--history-path",
        default=str(DEFAULT_HISTORY_PATH),
        help="Run-history JSONL path for trend accumulation.",
    )
    snap.add_argument(
        "--trend-output",
        default=str(DEFAULT_TREND_PANELS_PATH),
        help="Trend-panels JSON output path.",
    )
    snap.set_defaults(func=cmd_snapshot)

    verify = sub.add_parser("verify", help="Verify a snapshot-manifest pair")
    verify.add_argument("--snapshot", required=True, help="Path to snapshot.json")
    verify.add_argument("--manifest", required=True, help="Path to manifest.json")
    verify.add_argument(
        "--signing-key-env",
        default="PILLAR256_MANIFEST_HMAC_KEY",
        help="Environment variable containing HMAC key (required for HMAC manifests).",
    )
    verify.set_defaults(func=cmd_verify)

    compare = sub.add_parser("compare", help="Compare two snapshot files")
    compare.add_argument("--left-snapshot", required=True)
    compare.add_argument("--right-snapshot", required=True)
    compare.set_defaults(func=cmd_compare)

    trend = sub.add_parser("trend", help="Rebuild trend panels from run history")
    trend.add_argument("--history-path", default=str(DEFAULT_HISTORY_PATH))
    trend.add_argument("--trend-output", default=str(DEFAULT_TREND_PANELS_PATH))
    trend.set_defaults(func=cmd_trend)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
