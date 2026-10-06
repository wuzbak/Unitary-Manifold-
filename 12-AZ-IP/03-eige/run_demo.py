#!/usr/bin/env python3
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE v22 end-to-end demo on synthetic data.

1. Build a synthetic county publication bundle: election definition, ballot
   manifest, CVRs in an RFC 6962 Merkle log, signed tree heads, a witness
   cosignature, results, homomorphic tally commitments, a seeded audit
   sample, and hand-interpretation (MVR) inputs for a comparison RLA.
2. Verify it with the standalone verifier and print the official report.
3. Build a second bundle with one stuffed ballot and show that the verifier
   reports it as failed.

All keys are development keys. This script refuses to run when
EIGE_MODE=production. Exit code 0 means the clean bundle verified and the
tampered bundle was caught.

Run from the EIGE directory:  python run_demo.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from eige.canonical import canonical_bytes  # noqa: E402
from eige.config import require_non_production  # noqa: E402
from eige.pipeline import build_synthetic_bundle  # noqa: E402
from eige.verify import verify_bundle  # noqa: E402


def _stuff_one_ballot(state: dict) -> None:
    extra = {"id": "B00-9999", "batch_id": "B00", "ballot_style": "1",
             "selections": {"mayor": ["alvarez"], "measure-1": ["yes"]}}
    state["entries"].append(canonical_bytes({"type": "cvr", "cvr": extra}))


def main() -> int:
    require_non_production("run_demo (synthetic data, development keys)")
    with tempfile.TemporaryDirectory(prefix="eige-demo-") as tmp:
        clean_dir = Path(tmp) / "clean"
        build_synthetic_bundle(clean_dir)
        clean = verify_bundle(str(clean_dir))
        print(clean.render("official"))
        print()

        tampered_dir = Path(tmp) / "tampered"
        build_synthetic_bundle(tampered_dir, tamper=_stuff_one_ballot)
        tampered = verify_bundle(str(tampered_dir))
        print("Tampered bundle (one ballot appended after the signed tree head):")
        for c in tampered.by_status("failed"):
            print(f"  FAILED {c.check}: {c.detail}")

    ok = clean.passed and not tampered.passed
    print()
    print("Demo result:", "clean bundle verified; tampering detected" if ok else "UNEXPECTED RESULT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
