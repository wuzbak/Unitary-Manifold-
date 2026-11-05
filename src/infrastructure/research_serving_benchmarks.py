# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Measure P43 full-prefix, cached serial and continuous-batch CPU decoding."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np

from .artifact_io import publish_immutable
from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance
from .research_serving import ResearchServingSession, ToriCPUDecoder
from az_tori_transformer.checkpoint import load_checkpoint
from az_tori_transformer.model import GeometricToriTransformer

ROOT = Path(__file__).resolve().parents[2]


def _full_generation(model: GeometricToriTransformer, prompt: tuple[int, ...], count: int) -> tuple[int, ...]:
    result: tuple[int, ...] = ()
    for _ in range(count):
        logits, _ = model(np.array([prompt + result], dtype=np.int64))
        if not np.all(np.isfinite(logits.data)):
            raise ValueError("nonfinite reference-model output")
        result += (int(logits.data[0, -1].argmax()),)
    return result


def benchmark_serving(model: GeometricToriTransformer) -> dict[str, object]:
    """Fixed token-ID workload, not model utility, semantic quality or a load test."""
    prompts = tuple(tuple(index % model.cfg.vocab_size for index in range(length))
                    for length in (3, 7, 2, 5))
    count = 8
    expected = []
    started = time.perf_counter()
    for prompt in prompts:
        expected.append(_full_generation(model, prompt, count))
    full_seconds = time.perf_counter() - started
    # Check every incremental logit independently of greedy token equality.
    parity_decoder = ToriCPUDecoder(model, max_context_tokens=64)
    maximum_logit_error = 0.0
    for prompt in prompts:
        cache = parity_decoder.empty_cache()
        for position, token in enumerate(prompt):
            cached, (cache,) = parity_decoder.decode_batch((token,), (cache,))
            reference, _ = model(np.array([prompt[:position + 1]], dtype=np.int64))
            error = float(np.max(np.abs(cached[0] - reference.data[0, -1])))
            maximum_logit_error = max(maximum_logit_error, error)
            if not np.allclose(cached[0], reference.data[0, -1], rtol=1e-10, atol=1e-10):
                raise ValueError("incremental/full-prefix logits differ beyond declared tolerance")

    def run(batch_size: int) -> dict[str, object]:
        decoder = ToriCPUDecoder(model, max_context_tokens=64)
        runtime = ResearchServingSession(
            decoder, max_cache_bytes=decoder.bytes_per_cached_token * 256,
            max_batch_size=batch_size, max_batch_padding_tokens=256,
        )
        identifiers = [
            runtime.submit(prompt, owner_scope=f"reference-{row}", max_new_tokens=count)
            for row, prompt in enumerate(prompts)
        ]
        start = time.perf_counter()
        completed: dict[str, float] = {}
        first_token: dict[str, float] = {}
        ticks = []
        for _ in range(sum(len(prompt) + count for prompt in prompts)):
            tick = runtime.tick()
            ticks.append(tick)
            for row, identifier in enumerate(identifiers):
                result = runtime.result(identifier, owner_scope=f"reference-{row}")
                if result["tokens"]:
                    first_token.setdefault(identifier, time.perf_counter() - start)
                if result["status"] == "completed":
                    completed.setdefault(identifier, time.perf_counter() - start)
            if len(completed) == len(identifiers):
                break
        else:
            raise ValueError("scheduler did not finish within the declared decoding-work bound")
        elapsed = time.perf_counter() - start
        results = [runtime.result(identifier, owner_scope=f"reference-{row}")
                   for row, identifier in enumerate(identifiers)]
        if [result["tokens"] for result in results] != expected:
            raise ValueError("cached generation differs from full-prefix greedy output")
        if any(result["cache_bytes"] != 0 for result in results):
            raise ValueError("terminal requests retained KV payload")
        completion_times = [completed[identifier] for identifier in identifiers]
        first_token_times = [first_token[identifier] for identifier in identifiers]
        return {
            "elapsed_seconds": elapsed, "generated_tokens": count * len(prompts),
            "generated_tokens_per_second": count * len(prompts) / elapsed,
            "request_completion_seconds": completion_times,
            "time_to_first_token_seconds": first_token_times,
            "request_completion_p50_seconds": float(np.median(completion_times)),
            "request_completion_p95_nearest_rank_seconds": sorted(completion_times)[-1],
            "latency_scope": "Four all-at-once requests measured from the first tick, including this scheduler's queue wait; not network latency.",
            "backend_batch_calls": decoder.calls, "decoded_token_rows": decoder.decoded_rows,
            "maximum_batch_size": max(tick["batch_size"] for tick in ticks),
            "peak_observed_kv_bytes_after_tick": max(tick.get("cache_bytes", 0) for tick in ticks),
            "peak_reserved_kv_bytes_after_tick": max(tick.get("reserved_cache_bytes", 0) for tick in ticks),
            "total_padded_token_slots": sum(tick["padded_token_slots"] for tick in ticks),
            "greedy_outputs_equal_full_prefix": True, "terminal_kv_payload_released": True,
            "execution_spine": runtime.receipt().to_dict(),
        }

    # Exercise each path once before timing the recorded repetitions.
    run(1)
    run(4)
    serial_samples = [run(1) for _ in range(3)]
    batch_samples = [run(4) for _ in range(3)]
    serial_seconds = float(np.median([sample["elapsed_seconds"] for sample in serial_samples]))
    batch_seconds = float(np.median([sample["elapsed_seconds"] for sample in batch_samples]))
    return {
        "schema_version": "az_ml_research_serving_v1",
        "workload": {
            "prompt_token_ids": prompts, "max_new_tokens": count,
            "arrival": "all admitted before the first tick", "warmup_runs_per_cached_path": 1,
            "measured_repetitions_per_cached_path": 3,
            "selection": "round robin under row and padded-KV-position limits",
        },
        "model_sha256": parity_decoder.model_sha256,
        "full_prefix": {
            "elapsed_seconds_single_run": full_seconds,
            "evaluated_token_positions": sum(sum(len(prompt) + step for step in range(count))
                                             for prompt in prompts),
            "generated_token_ids": expected,
            "scope": "Untimed warmup is not applied to this parity-only single-run reference.",
        },
        "cached_serial_samples": serial_samples, "continuous_batch_samples": batch_samples,
        "observed_median_serial_to_batch_ratio": serial_seconds / batch_seconds,
        "maximum_prefill_logit_absolute_error": maximum_logit_error,
        "gates": {
            "incremental_logits_allclose_rtol_atol_1e_10": True,
            "all_cached_and_batched_greedy_outputs_equal": True,
            "batched_backend_calls_lower_than_cached_serial":
                batch_samples[0]["backend_batch_calls"] < serial_samples[0]["backend_batch_calls"],
        },
        "scope": "Fixed CPU token-ID trace on one model; not semantic quality, production latency or a speedup guarantee.",
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "gpu": "unmeasured"},
        "promotion_eligible": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    models = parser.add_mutually_exclusive_group(required=True)
    models.add_argument("--checkpoint", type=Path, help="supported P43 NPZ; never download or train implicitly")
    models.add_argument("--quantized-model", type=Path, help="supported AZMQ artifact; reconstructed into float64, not low-bit kernels")
    parser.add_argument("--output-dir", type=Path, help="existing durable directory for immutable JSON evidence")
    args = parser.parse_args(argv)
    try:
        input_path = args.checkpoint or args.quantized_model
        input_bytes = input_path.read_bytes()
        input_sha256 = hashlib.sha256(input_bytes).hexdigest()
        if args.quantized_model is not None:
            from .research_quantization import load_model_artifact

            model = load_model_artifact(input_bytes)
        else:
            model = load_checkpoint(input_path).model
            if hashlib.sha256(input_path.read_bytes()).hexdigest() != input_sha256:
                raise ValueError("checkpoint changed while loading")
        report = benchmark_serving(model)
        if not all(report["gates"].values()):
            raise ValueError("declared serving-reference acceptance gates failed")
        report["model_input"] = {
            "format": "azmq" if args.quantized_model is not None else "p43_npz",
            "sha256": input_sha256,
            "evaluation_compute": "float64; packed weights are reconstructed before inference",
        }
        if args.checkpoint is not None:
            report["checkpoint_sha256"] = input_sha256
        paths = [
            "src/infrastructure/research_serving.py",
            "src/infrastructure/research_serving_benchmarks.py",
            "src/infrastructure/artifact_io.py",
            "src/infrastructure/execution_spine.py",
        ] + [path.relative_to(ROOT).as_posix() for path in sorted(
            (ROOT / "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer").glob("*.py"))]
        if args.quantized_model is not None:
            paths.extend(["src/infrastructure/research_quantization.py", "src/infrastructure/lowbit_quantization.py"])
        report["source_sha256"] = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths}
        report["execution_spine"] = ExecutionSpineRecord(
            surface_id="az-ml-measured-research-serving", surface_kind="reference_benchmark_receipt",
            lane="az_ml_infrastructure", status="scoped_reference_gates_passed",
            summary="Measured incremental and continuously batched CPU P43 decoding against full-prefix outputs.",
            canonical_paths=["src/infrastructure/research_serving_benchmarks.py"],
            governance=build_fail_closed_governance(
                epistemic_label="fixed research-model token trace",
                promotion_rule="Parity and measured CPU observations do not qualify production or general model quality.",
                residual_blockers=[
                    "No pretrained model, GPU, authenticated network service or load/failure deployment validation.",
                    "In-process scheduler is an execution component, not a new control plane.",
                ],
            ),
            compatibility={"model_input": report["model_input"], "source_sha256": report["source_sha256"]},
            promotion={"eligible": False, "physics_claim": False},
        ).to_dict()
        content = (json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
        if args.output_dir:
            print(publish_immutable(args.output_dir, hashlib.sha256(content).hexdigest(), content))
        else:
            print(content.decode(), end="")
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f"Research serving benchmark failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
