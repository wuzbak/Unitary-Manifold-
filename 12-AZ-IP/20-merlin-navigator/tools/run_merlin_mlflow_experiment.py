# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Run Merlin MLflow-ready experiment receipts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine.merlin_benchmark import (
    run_stage_b_head_to_head_receipts_sync,
    run_stage_c_head_to_head_receipts_sync,
)
from ox_navigator.engine.merlin_program import build_training_dataset_bundle


def _receipt_for_experiment(experiment: str, limit: int | None) -> dict:
    if experiment == "merlin_sft_repository_mastery":
        dataset = build_training_dataset_bundle(limit=limit)
        return {
            "ok": bool(dataset.get("ok")),
            "experiment_name": experiment,
            "mode": "dataset_preparation",
            "dataset_counts": ((dataset.get("dataset") or {}).get("counts") or {}),
        }
    if experiment == "merlin_dpo_boundary_discipline":
        stage_b = run_stage_b_head_to_head_receipts_sync(limit=limit)
        stage_c = run_stage_c_head_to_head_receipts_sync(limit=limit)
        return {
            "ok": bool(stage_b.get("ok")) and bool(stage_c.get("ok")),
            "experiment_name": experiment,
            "mode": "preference_evaluation",
            "stage_b_summary": stage_b.get("summary", {}),
            "stage_c_summary": stage_c.get("summary", {}),
        }
    if experiment == "merlin_stage_b_shadow_eval":
        payload = run_stage_b_head_to_head_receipts_sync(limit=limit)
        payload["experiment_name"] = experiment
        return payload
    if experiment == "merlin_stage_c_agentic_eval":
        payload = run_stage_c_head_to_head_receipts_sync(limit=limit)
        payload["experiment_name"] = experiment
        return payload
    return {"ok": False, "error": f"Unknown experiment: {experiment}"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Merlin MLflow-ready experiment receipts.")
    parser.add_argument(
        "--experiment",
        choices=[
            "merlin_sft_repository_mastery",
            "merlin_dpo_boundary_discipline",
            "merlin_stage_b_shadow_eval",
            "merlin_stage_c_agentic_eval",
        ],
        required=True,
    )
    parser.add_argument("--limit", type=int, default=None, help="Optional benchmark or dataset limit")
    parser.add_argument("--output", type=str, required=True, help="Output JSON path")
    args = parser.parse_args()

    payload = _receipt_for_experiment(args.experiment, args.limit)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
