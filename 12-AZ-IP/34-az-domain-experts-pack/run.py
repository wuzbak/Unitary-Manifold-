#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Domain Experts Pack (Product 34)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_domain_experts_pack import MATERIALS_EXPERT, SPECTROSCOPY_EXPERT


def main(argv: list[str] | None = None) -> int:
    query = " ".join(argv) if argv else "polariton vortex critical angle"
    MATERIALS_EXPERT.build()
    SPECTROSCOPY_EXPERT.build()
    print(
        json.dumps(
            {
                "materials_science": MATERIALS_EXPERT.query(query),
                "atomic_spectroscopy": SPECTROSCOPY_EXPERT.query(query),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
