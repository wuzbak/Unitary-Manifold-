# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Create a reproducible public audit sample from a verified election bundle.

The public seed must come from an independently observed ceremony. This
utility records the supplied seed and timestamp; it does not generate entropy,
authenticate ceremony witnesses, select ballots, or interpret paper ballots.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, Sequence

from ..bundle import BundleError, iter_log, read_metadata
from ..ledger.log import SignedTreeHead
from ..model.election import parse_manifest
from ..verify import verify_stream
from .sampling import SamplingError, draw_sample, sample_record, validate_seed


class CeremonyError(ValueError):
    """Raised when a public sample cannot safely be produced."""


def create_sample_for_bundle(
    directory: str | Path,
    seed: str,
    seed_generated_at: int,
    draw_count: int,
) -> dict:
    """Validate a staged bundle and write its first ``sample.json``.

    The bundle's latest signed head must cover the entire log and pass the
    standalone verifier. The seed timestamp must be strictly later than that
    head. An existing sample is never replaced, preventing an accidental
    second draw from silently changing the audit record.
    """
    bundle_dir = Path(directory)
    sample_path = bundle_dir / "sample.json"
    if sample_path.exists():
        raise CeremonyError("sample.json already exists; refusing to replace the published sample")
    try:
        validate_seed(seed)
    except SamplingError as exc:
        raise CeremonyError(str(exc)) from exc
    if isinstance(seed_generated_at, bool) or not isinstance(seed_generated_at, int):
        raise CeremonyError("seed_generated_at must be an integer Unix timestamp")
    if isinstance(draw_count, bool) or not isinstance(draw_count, int) or draw_count < 1:
        raise CeremonyError("draw_count must be a positive integer")

    metadata = read_metadata(bundle_dir)
    report = verify_stream(metadata, iter_log(bundle_dir))
    if not report.passed:
        failures = [item.check for item in report.by_status("failed")]
        raise CeremonyError("bundle verification failed: " + ", ".join(failures[:10]))

    heads = metadata.get("heads.json")
    if not isinstance(heads, list) or not heads:
        raise CeremonyError("bundle has no signed tree head")
    try:
        latest = SignedTreeHead.from_dict(heads[-1])
        manifest = parse_manifest(metadata["manifest.json"])
    except (KeyError, TypeError, ValueError) as exc:
        raise CeremonyError(f"bundle metadata is malformed: {exc}") from exc
    if seed_generated_at <= latest.timestamp:
        raise CeremonyError("public seed timestamp must be later than the latest signed log head")

    draws = draw_sample(seed, manifest, draw_count)
    record = sample_record(seed, manifest, draws)
    record["committed_root"] = latest.root_hash
    record["seed_generated_at"] = seed_generated_at

    try:
        with sample_path.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise CeremonyError("sample.json already exists; refusing to replace the published sample") from exc
    except OSError:
        sample_path.unlink(missing_ok=True)
        raise
    return record


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m eige.audit.ceremony",
        description="Record an observed public seed and draw a sample from a verified election bundle.",
    )
    parser.add_argument("bundle", help="staged publication bundle with signed heads and manifest")
    parser.add_argument("--seed", required=True, help="public seed recorded at the independently observed ceremony")
    parser.add_argument("--seed-generated-at", type=int, required=True, help="Unix timestamp recorded at the ceremony")
    parser.add_argument("--draws", required=True, type=int, help="number of ballots to draw with replacement")
    args = parser.parse_args(argv)
    try:
        record = create_sample_for_bundle(args.bundle, args.seed, args.seed_generated_at, args.draws)
    except (BundleError, CeremonyError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps({"sample": str(Path(args.bundle) / "sample.json"), "draws": len(record["draws"]),
                      "committed_root": record["committed_root"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
