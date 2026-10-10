#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Differentiable Cosmology Slider (Product 36)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_cosmology_slider import require_jax, slider_reading, sweep_phi0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Differentiable cosmology slider")
    parser.add_argument("--phi0", type=float, default=10.0)
    parser.add_argument("--n-w", type=float, default=5.0)
    parser.add_argument("--sweep", action="store_true", help="sweep phi0 from phi0-2 to phi0+2")
    args = parser.parse_args(argv)

    require_jax()
    if args.sweep:
        for reading in sweep_phi0(args.n_w, [args.phi0 + d for d in (-2, -1, 0, 1, 2)]):
            print(reading)
    else:
        print(slider_reading(args.phi0, args.n_w))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
