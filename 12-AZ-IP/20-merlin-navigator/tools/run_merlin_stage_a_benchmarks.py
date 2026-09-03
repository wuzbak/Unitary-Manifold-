# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Run Stage A incumbent-vs-Merlin benchmark gates."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ox_navigator.engine.merlin_benchmark import evaluate_benchmark_response, get_stage_a_benchmark_corpus
from ox_navigator.engine.merlin_engine import query_merlin
from ox_navigator.engine.merlin_memory import MerlinSession

REQUIRED_SHADOW_FIELDS = [
    ("telemetry", "provider"),
    ("telemetry", "lane"),
    ("telemetry", "latency_ms"),
    ("telemetry", "energy", "estimated_joules"),
    ("telemetry", "quality_signals"),
]


def _path_has(payload: dict, path: tuple[str, ...]) -> bool:
    value = payload
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return False
        value = value[key]
    return True


async def _run_once(benchmark: dict) -> dict:
    merlin_session = MerlinSession()
    incumbent_session = MerlinSession()
    merlin_result = await query_merlin(text=str(benchmark["query"]), session=merlin_session)
    incumbent_result = await query_merlin(
        text=str(benchmark["query"]),
        session=incumbent_session,
        runtime_mode="incumbent_compat",
    )
    merlin_eval = evaluate_benchmark_response(str(benchmark["id"]), merlin_result)
    incumbent_eval = evaluate_benchmark_response(str(benchmark["id"]), incumbent_result)
    shadow = {"/".join(path): _path_has(merlin_result, path) for path in REQUIRED_SHADOW_FIELDS}
    shadow_ok = all(shadow.values())
    parity_ok = float(merlin_eval.get("score", 0.0)) >= float(incumbent_eval.get("score", 0.0))
    return {
        "benchmark_id": benchmark["id"],
        "track": benchmark["track"],
        "query": benchmark["query"],
        "merlin_evaluation": merlin_eval,
        "incumbent_evaluation": incumbent_eval,
        "parity_ok": parity_ok,
        "shadow_fields": shadow,
        "shadow_ok": shadow_ok,
    }


async def run_benchmarks() -> dict:
    corpus = get_stage_a_benchmark_corpus()
    runs = []
    for benchmark in corpus["benchmarks"]:
        runs.append(await _run_once(benchmark))
    failed = [
        item
        for item in runs
        if (not item["merlin_evaluation"].get("pass")) or (not item["shadow_ok"]) or (not item["parity_ok"])
    ]
    return {
        "stage": corpus["stage"],
        "runs": runs,
        "summary": {
            "total": len(runs),
            "passed": len(runs) - len(failed),
            "failed": len(failed),
            "promotion_gate_pass": len(failed) == 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Merlin Stage A benchmark promotion gates.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    payload = asyncio.run(run_benchmarks())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    if not payload["summary"]["promotion_gate_pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
