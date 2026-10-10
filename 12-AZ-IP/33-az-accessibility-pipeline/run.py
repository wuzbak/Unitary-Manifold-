#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""CLI entrypoint for the AZ Accessibility Pipeline (Product 33)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from az_accessibility_pipeline import build_accessibility_report

_DEMO_TEXT = (
    "The braided sound speed predicts a birefringence window LiteBIRD will test. "
    "Separately, the CMB spectral index n_s is already in tension with ACT data."
)


def main(argv: list[str] | None = None) -> int:
    text = " ".join(argv) if argv else _DEMO_TEXT
    report = build_accessibility_report(text)
    print(
        json.dumps(
            {
                "segments": [{"index": s.index, "text": s.text} for s in report.segments],
                "suggested_visuals": report.suggested_visuals,
                "claim_verdicts": report.claim_verdicts,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
