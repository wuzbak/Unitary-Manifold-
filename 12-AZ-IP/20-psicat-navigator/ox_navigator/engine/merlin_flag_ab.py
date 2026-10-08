# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Flag A/B harness: run Merlin's benchmark stages with opt-in upgrades OFF vs ON.

ADJACENT TRACK.  Every upgrade in the toroidal lane ships behind a default-OFF
environment flag.  This harness is how a flag earns promotion: it runs the
same benchmark queries in fresh sessions under each flag configuration and
reports score deltas and regressions.  A flag with any regression stays OFF.

Flags are process-global, so variants run sequentially under a lock and the
original environment is always restored.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import threading
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Any

from .merlin_benchmark import evaluate_benchmark_response, get_benchmark_corpus
from .merlin_rag import (
    BM25_PILLAR_RANKING_FLAG,
    PHICAT_PROTOCOL_FLAG,
    RRF_FUSION_RANKING_FLAG,
    SEMANTIC_EMBEDDER_RANKING_FLAG,
    TOROIDAL_CREASE_FUSION_FLAG,
)

OPT_IN_FLAGS = (
    TOROIDAL_CREASE_FUSION_FLAG,
    BM25_PILLAR_RANKING_FLAG,
    SEMANTIC_EMBEDDER_RANKING_FLAG,
    PHICAT_PROTOCOL_FLAG,
    RRF_FUSION_RANKING_FLAG,
)
_ENV_LOCK = threading.Lock()


@contextmanager
def _flag_environment(enabled: Sequence[str]) -> Iterator[None]:
    with _ENV_LOCK:
        saved = {flag: os.environ.get(flag) for flag in OPT_IN_FLAGS}
        try:
            for flag in OPT_IN_FLAGS:
                if flag in enabled:
                    os.environ[flag] = "1"
                else:
                    os.environ.pop(flag, None)
            yield
        finally:
            for flag, value in saved.items():
                if value is None:
                    os.environ.pop(flag, None)
                else:
                    os.environ[flag] = value


async def _run_one(benchmark: dict[str, Any], stage: str) -> dict[str, Any]:
    from .merlin_engine import query_merlin
    from .merlin_memory import MerlinSession

    session = MerlinSession()
    for setup_turn in list(benchmark.get("setup_turns") or []):
        await query_merlin(text=str(setup_turn), session=session)
    result = await query_merlin(text=str(benchmark["query"]), session=session)
    evaluation = evaluate_benchmark_response(str(benchmark["id"]), result, stage=stage)
    return {
        "benchmark_id": str(benchmark["id"]),
        "score": float(evaluation.get("score", 0.0)),
        "pass": bool(evaluation.get("pass")),
        "answer_chars": len(str(result.get("answer") or "")),
        "answer_sha256": hashlib.sha256(str(result.get("answer") or "").encode("utf-8")).hexdigest(),
    }


def _run_async(coro: Any) -> Any:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    box: dict[str, Any] = {}

    def runner() -> None:
        try:
            box["value"] = asyncio.run(coro)
        except Exception as exc:  # noqa: BLE001 - re-raised in the caller thread
            box["error"] = exc

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()
    thread.join()
    if "error" in box:
        raise box["error"]
    return box["value"]


async def _run_variant(selected: list[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    return [{"stage": stage, **(await _run_one(benchmark, stage))} for stage, benchmark in selected]


def run_flag_ab(
    *,
    stages: Sequence[str] | None = None,
    limit_per_stage: int | None = None,
    variants: dict[str, Sequence[str]] | None = None,
) -> dict[str, Any]:
    corpus = get_benchmark_corpus()
    stage_ids = list(stages) if stages else list(corpus.get("stages") or [])
    selected: list[tuple[str, dict[str, Any]]] = []
    for stage in stage_ids:
        stage_corpus = get_benchmark_corpus(stage)
        if stage_corpus.get("ok") is False:
            return {"ok": False, "error": f"Unknown benchmark stage: {stage}"}
        items = list(stage_corpus.get("benchmarks") or [])
        if limit_per_stage is not None:
            items = items[: max(0, int(limit_per_stage))]
        selected.extend((stage, item) for item in items)
    variant_map = dict(variants) if variants else {
        "baseline": (),
        "crease_fusion": (TOROIDAL_CREASE_FUSION_FLAG,),
        "bm25_pillars": (BM25_PILLAR_RANKING_FLAG,),
        "both": (TOROIDAL_CREASE_FUSION_FLAG, BM25_PILLAR_RANKING_FLAG),
        "semantic_embedder": (SEMANTIC_EMBEDDER_RANKING_FLAG,),
        "phicat_protocol": (PHICAT_PROTOCOL_FLAG,),
        "rrf_fusion": (RRF_FUSION_RANKING_FLAG,),
        "all_flags": OPT_IN_FLAGS,
    }
    if "baseline" not in variant_map:
        variant_map = {"baseline": (), **variant_map}
    results: dict[str, list[dict[str, Any]]] = {}
    for name, flags in variant_map.items():
        unknown = [flag for flag in flags if flag not in OPT_IN_FLAGS]
        if unknown:
            return {"ok": False, "error": f"Unknown flags: {unknown}"}
        with _flag_environment(tuple(flags)):
            results[name] = _run_async(_run_variant(selected))
    baseline = {(r["stage"], r["benchmark_id"]): r for r in results["baseline"]}
    summary: dict[str, Any] = {}
    for name, rows in results.items():
        regressions = [
            r["benchmark_id"] for r in rows
            if r["score"] < baseline[(r["stage"], r["benchmark_id"])]["score"]
            or (baseline[(r["stage"], r["benchmark_id"])]["pass"] and not r["pass"])
        ]
        improvements = [
            r["benchmark_id"] for r in rows
            if r["score"] > baseline[(r["stage"], r["benchmark_id"])]["score"]
        ]
        changed = [
            r["benchmark_id"] for r in rows
            if r["answer_sha256"] != baseline[(r["stage"], r["benchmark_id"])]["answer_sha256"]
        ]
        n = max(len(rows), 1)
        summary[name] = {
            "flags": list(variant_map[name]),
            "runs": len(rows),
            "passed": sum(1 for r in rows if r["pass"]),
            "mean_score": round(sum(r["score"] for r in rows) / n, 4),
            "regressions": regressions,
            "improvements": improvements,
            "answers_changed": changed,
            "promotable": not regressions,
        }
    return {
        "ok": True,
        "status": "ADJACENT_TRACK",
        "stages": stage_ids,
        "benchmark_count": len(selected),
        "summary": summary,
        "runs": results,
        "policy": "A flag stays OFF if any benchmark regresses; equal scores show safety, not benefit.",
    }


__all__ = ["OPT_IN_FLAGS", "run_flag_ab"]
