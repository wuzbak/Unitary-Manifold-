# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Measure EIGE at county/state scale: build and verify synthetic counties.

Each phase runs in a fresh subprocess so the reported peak RSS belongs to that
phase alone (including worker processes for parallel verification).

    python tools/scale_benchmark.py --ballots 1000000 --contests 5 --workers 4
"""

from __future__ import annotations

import argparse
import json
import os
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _peak_rss_mib() -> float:
    own = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    kids = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    return max(own, kids) / 1024.0  # Linux reports KiB


def _phase(argv: list) -> None:
    sys.path.insert(0, str(ROOT))
    kind = argv[0]
    t0 = time.perf_counter()
    if kind == "build":
        from eige.synthetic_scale import build_county
        info = build_county(argv[1], int(argv[2]), n_contests=int(argv[3]), n_units=int(argv[4]))
    else:
        from eige.verify import verify_bundle
        rep = verify_bundle(argv[1], workers=int(argv[2]))
        info = {"counts": rep.counts(), "ok": rep.passed}
    info["seconds"] = round(time.perf_counter() - t0, 2)
    info["peak_rss_mib"] = round(_peak_rss_mib(), 1)
    print(json.dumps(info))


def _run(args: list) -> dict:
    out = subprocess.run([sys.executable, __file__, "--phase", *map(str, args)], check=True,
                         capture_output=True, text=True, cwd=ROOT)
    return json.loads(out.stdout.strip().splitlines()[-1])


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--phase":
        _phase(sys.argv[2:])
        return 0
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--ballots", type=int, nargs="+", default=[100_000])
    p.add_argument("--contests", type=int, default=5)
    p.add_argument("--units", type=int, default=200)
    p.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    p.add_argument("--dir", help="keep bundles here instead of a temporary directory")
    a = p.parse_args()
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(a.dir or tmp)
        for n in a.ballots:
            d = base / f"county-{n}"
            build = _run(["build", d, n, a.contests, a.units])
            serial = _run(["verify", d, 1])
            par = _run(["verify", d, a.workers]) if a.workers > 1 else None
            log_bytes = (d / "log.jsonl").stat().st_size
            row = {"ballots": n, "contests": a.contests, "log_mib": round(log_bytes / 2**20, 1),
                   "build": build, "verify_serial": serial, "verify_parallel": par, "workers": a.workers}
            rows.append(row)
            print(json.dumps(row), flush=True)
            for v in (serial, par):
                if v is not None and not v["ok"]:
                    print("verification FAILED on a clean synthetic bundle", file=sys.stderr)
                    return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
