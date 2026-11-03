#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Braided Qubit Ansatz Studio (Product 31)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_braided_qubit_ansatz_studio import (
    build_braided_ansatz_circuit,
    export_openqasm2,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AZ Braided Qubit Ansatz Studio")
    sub = parser.add_subparsers(dest="command", required=True)
    export_cmd = sub.add_parser("export", help="Export a deterministic ansatz as OpenQASM 2.0")
    export_cmd.add_argument("--n-qubits", type=int, default=8)
    export_cmd.add_argument("--n-layers", type=int, default=2)
    parameter_source = export_cmd.add_mutually_exclusive_group(required=True)
    parameter_source.add_argument("--seed", type=int, help="Generate deterministic parameters from this seed")
    parameter_source.add_argument(
        "--angles",
        help="Use comma-separated user-supplied RY angles in qubit/layer order",
    )
    serve_cmd = sub.add_parser("serve", help="Run the studio as a live HTTP product")
    serve_cmd.add_argument("--host", default="127.0.0.1")
    serve_cmd.add_argument("--port", type=int, default=8131)
    args = parser.parse_args(argv)

    if args.command == "serve":
        from az_braided_qubit_ansatz_studio.app.server import serve

        serve(host=args.host, port=args.port)
        return 0

    if args.command == "export":
        from az_braided_qubit_ansatz_studio.circuit_export import (
            MAX_LAYERS,
            MAX_QUBITS,
            MIN_QUBITS,
        )

        if not MIN_QUBITS <= args.n_qubits <= MAX_QUBITS:
            parser.error(f"--n-qubits must be in {MIN_QUBITS}..{MAX_QUBITS}")
        if not 0 <= args.n_layers <= MAX_LAYERS:
            parser.error(f"--n-layers must be in 0..{MAX_LAYERS}")
        if args.seed is not None:
            if not 0 <= args.seed <= 2**32 - 1:
                parser.error("--seed must be in 0..4294967295")
            rng = np.random.default_rng(args.seed)
            theta = rng.uniform(-np.pi, np.pi, size=args.n_qubits * (args.n_layers + 1))
        else:
            if len(args.angles) > 4096:
                parser.error("--angles must be no longer than 4096 characters")
            try:
                theta = np.asarray([float(value.strip()) for value in args.angles.split(",")])
            except (TypeError, ValueError, OverflowError):
                parser.error("--angles must be comma-separated finite numbers")
        try:
            circuit = build_braided_ansatz_circuit(theta, args.n_qubits, args.n_layers)
        except ValueError as exc:
            parser.error(str(exc))
        print(export_openqasm2(circuit), end="")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
