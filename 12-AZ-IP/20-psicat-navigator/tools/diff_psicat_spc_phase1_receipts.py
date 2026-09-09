# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Diff two PsiCat SPC phase-1 baseline receipt artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _lane_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("lane_id") or ""): dict(item)
        for item in list(payload.get("lane_receipts") or [])
        if str(item.get("lane_id") or "")
    }


def build_diff(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    prev_lanes = _lane_index(previous)
    curr_lanes = _lane_index(current)
    lane_ids = sorted(set(prev_lanes) | set(curr_lanes))

    lane_deltas: list[dict[str, Any]] = []
    for lane_id in lane_ids:
        prev = prev_lanes.get(lane_id, {})
        curr = curr_lanes.get(lane_id, {})
        lane_deltas.append(
            {
                "lane_id": lane_id,
                "previous_verdict": prev.get("lane_verdict"),
                "current_verdict": curr.get("lane_verdict"),
                "previous_mean_score_100": prev.get("mean_score_100"),
                "current_mean_score_100": curr.get("mean_score_100"),
                "mean_score_delta": round(
                    float(curr.get("mean_score_100") or 0.0) - float(prev.get("mean_score_100") or 0.0),
                    2,
                ),
                "previous_hard_fail_count": prev.get("hard_fail_count"),
                "current_hard_fail_count": curr.get("hard_fail_count"),
            }
        )

    prev_blockers = list(previous.get("blocker_register") or [])
    curr_blockers = list(current.get("blocker_register") or [])
    prev_ids = {str(item.get("blocker_id") or "") for item in prev_blockers}
    curr_ids = {str(item.get("blocker_id") or "") for item in curr_blockers}

    return {
        "ok": True,
        "previous_generated_at": previous.get("generated_at"),
        "current_generated_at": current.get("generated_at"),
        "previous_phase_verdict": previous.get("phase_verdict"),
        "current_phase_verdict": current.get("phase_verdict"),
        "lane_deltas": lane_deltas,
        "blockers_added": sorted(curr_ids - prev_ids),
        "blockers_removed": sorted(prev_ids - curr_ids),
        "blocker_count_delta": len(curr_blockers) - len(prev_blockers),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff PsiCat SPC phase-1 baseline receipt artifacts.")
    parser.add_argument("--previous", required=True, help="Previous artifact path")
    parser.add_argument("--current", required=True, help="Current artifact path")
    parser.add_argument("--output", required=True, help="Output diff JSON path")
    args = parser.parse_args()

    previous = _load(Path(args.previous))
    current = _load(Path(args.current))
    payload = build_diff(previous, current)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
