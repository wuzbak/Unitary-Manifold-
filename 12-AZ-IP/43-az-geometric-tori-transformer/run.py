#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Geometric Tori Transformer (Product 43)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_tori_transformer import (
    generate_text,
    modular_alias_diagnostics,
    run_positional_ablation,
    run_toroidal_copy_demo,
    train_text_file,
)
from az_tori_transformer.text_workflow import run_text_ablation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AZ Geometric Tori Transformer")
    sub = parser.add_subparsers(dest="command")
    serve_cmd = sub.add_parser("serve", help="Run the studio as a live HTTP product")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8143)
    demo_cmd = sub.add_parser("demo", help="Run the toroidal-copy training demo and print the report")
    demo_cmd.add_argument("--steps", type=int, default=200)
    ablate_cmd = sub.add_parser("ablate", help="Run a matched-parameter synthetic positional ablation")
    ablate_cmd.add_argument("--steps", type=int, default=120)
    ablate_cmd.add_argument("--seed", type=int, default=0)
    diagnose_cmd = sub.add_parser("diagnose", help="Report modular phase and bank-address aliases")
    diagnose_cmd.add_argument("--seq-len", type=int, default=80)
    diagnose_cmd.add_argument("--head-dim", type=int, default=8)
    train_cmd = sub.add_parser("train", help="Train or resume a causal character model on a UTF-8 corpus")
    train_cmd.add_argument("--text-file", required=True, help="UTF-8 corpus (maximum 8 MiB)")
    train_cmd.add_argument("--checkpoint", required=True, help="NPZ output checkpoint path")
    train_cmd.add_argument("--context-length", type=int, default=32)
    train_cmd.add_argument("--steps", type=int, default=100)
    train_cmd.add_argument("--batch-size", type=int, default=16)
    train_cmd.add_argument("--learning-rate", type=float)
    train_cmd.add_argument("--validation-fraction", type=float, default=0.1)
    train_cmd.add_argument("--dim", type=int, default=32)
    train_cmd.add_argument("--heads", type=int, default=4)
    train_cmd.add_argument("--layers", type=int, default=2)
    train_cmd.add_argument("--seed", type=int, default=0)
    train_cmd.add_argument("--resume", action="store_true", help="Continue the compatible checkpoint in place")
    train_cmd.add_argument("--positional-mode", choices=("toroidal", "rope_matched"), default="toroidal")
    compare_cmd = sub.add_parser("compare-text", help="Train corpus checkpoints and a matched RoPE control; not an assistant benchmark")
    compare_cmd.add_argument("--text-file", required=True)
    compare_cmd.add_argument("--output-directory", required=True, help="Existing directory for private corpus snapshot, checkpoints and receipts")
    compare_cmd.add_argument("--steps", type=int, default=100)
    compare_cmd.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    compare_cmd.add_argument("--context-length", type=int, default=32)
    compare_cmd.add_argument("--batch-size", type=int, default=16)
    compare_cmd.add_argument("--dim", type=int, default=32)
    compare_cmd.add_argument("--heads", type=int, default=4)
    compare_cmd.add_argument("--layers", type=int, default=2)
    compare_cmd.add_argument("--validation-fraction", type=float, default=0.1)
    generate_cmd = sub.add_parser("generate", help="Sample text from a trained character-model checkpoint")
    generate_cmd.add_argument("--checkpoint", required=True)
    generate_cmd.add_argument("--prompt", required=True)
    generate_cmd.add_argument("--max-new-tokens", type=int, default=100)
    generate_cmd.add_argument("--temperature", type=float, default=1.0)
    generate_cmd.add_argument("--top-k", type=int)
    generate_cmd.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    if args.command == "train":
        try:
            report = train_text_file(
                args.text_file,
                args.checkpoint,
                context_length=args.context_length,
                steps=args.steps,
                batch_size=args.batch_size,
                learning_rate=args.learning_rate,
                validation_fraction=args.validation_fraction,
                dim=args.dim,
                num_heads=args.heads,
                num_layers=args.layers,
                seed=args.seed,
                resume=args.resume,
                positional_mode=args.positional_mode,
            )
        except (OSError, ValueError, FloatingPointError) as exc:
            parser.error(str(exc))
        print(json.dumps(report, indent=2))
        return 0

    if args.command == "compare-text":
        try:
            report = run_text_ablation(
                args.text_file, args.output_directory, seeds=tuple(args.seeds),
                steps=args.steps, context_length=args.context_length,
                batch_size=args.batch_size, dim=args.dim, num_heads=args.heads,
                num_layers=args.layers, validation_fraction=args.validation_fraction,
            )
        except (OSError, ValueError, FloatingPointError) as exc:
            parser.error(str(exc))
        print(json.dumps(report, indent=2))
        return 0

    if args.command == "generate":
        try:
            text = generate_text(
                args.checkpoint,
                args.prompt,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_k=args.top_k,
                seed=args.seed,
            )
        except (OSError, ValueError, FloatingPointError) as exc:
            parser.error(str(exc))
        print(json.dumps({
            "prompt": args.prompt,
            "completion": text[len(args.prompt):],
            "text": text,
            "max_new_tokens": args.max_new_tokens,
            "seed": args.seed,
        }, ensure_ascii=False, indent=2))
        return 0

    if args.command == "diagnose":
        print(json.dumps(modular_alias_diagnostics(args.seq_len, args.head_dim), indent=2))
        return 0

    if args.command == "ablate":
        print(json.dumps(run_positional_ablation(steps=args.steps, seed=args.seed), indent=2))
        print("Descriptive synthetic comparison only; not a real-corpus benchmark.")
        return 0

    if args.command == "serve":
        from az_tori_transformer.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    steps = args.steps if args.command == "demo" else 200
    report = run_toroidal_copy_demo(steps=steps)
    trace = report.pop("loss_trace")
    print(json.dumps(report, indent=2))
    print(f"loss[0]={trace[0]:.4f}  loss[-1]={trace[-1]:.4f}")
    print(
        "This is a synthetic cyclic-copy architecture smoke test, not a "
        "language-modelling benchmark result. Run `serve` to start the live "
        "HTTP product."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
