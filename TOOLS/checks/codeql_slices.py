# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""CodeQL path slices: one manifest for CI planning, coverage checking and local runs.

A single CodeQL database for every Python file in this repository is larger
than the analysis service accepts, so Python is analysed in path slices
(``.github/codeql/slices.json``).  A slice list maintained by hand drifts:
before this manifest existed, 666 of 4,006 tracked Python files (EIGE among
them) belonged to no slice and were never analysed.  This module makes that
failure mode visible and testable.

Commands::

    python TOOLS/checks/codeql_slices.py check            # every tracked file is in a slice
    python TOOLS/checks/codeql_slices.py plan             # GitHub Actions matrix (CI)
    python TOOLS/checks/codeql_slices.py analyze python-eige [--codeql PATH]

Path patterns follow CodeQL's ``paths`` semantics: a pattern without glob
characters matches that file or everything below that directory; ``*`` and
``?`` do not cross ``/``; ``**`` matches any number of path segments.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / ".github" / "codeql" / "slices.json"
WORKFLOW = ".github/workflows/codeql-language-matrix.yml"
# Files whose change means every slice must be re-analysed.
PLAN_INPUTS = (WORKFLOW, ".github/codeql/slices.json", "TOOLS/checks/codeql_slices.py")


class SliceError(Exception):
    """The manifest is malformed or a CodeQL run failed."""


@lru_cache(maxsize=None)
def _regex(pattern: str) -> "re.Pattern[str]":
    pattern = pattern.strip("/")
    if not any(ch in pattern for ch in "*?["):
        return re.compile(re.escape(pattern) + r"(?:/.*)?\Z")
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append(r"(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(r".*")
            i += 2
        elif pattern[i] == "*":
            out.append(r"[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append(r"[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"(?:/.*)?\Z")


def matches(path: str, pattern: str) -> bool:
    """True if ``path`` (repository-relative, ``/``-separated) is selected by ``pattern``."""
    return _regex(pattern).match(path) is not None


def load_manifest(path: Path = MANIFEST) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    slices = data.get("slices")
    if not isinstance(slices, list) or not slices:
        raise SliceError("manifest has no slices")
    seen = set()
    for s in slices:
        for key in ("slice_id", "language", "build_mode", "paths"):
            if key not in s:
                raise SliceError(f"slice {s.get('slice_id', '?')!r} is missing {key!r}")
        if s["slice_id"] in seen:
            raise SliceError(f"duplicate slice_id {s['slice_id']!r}")
        seen.add(s["slice_id"])
        if not s["paths"] or not all(isinstance(p, str) and p.strip("/") for p in s["paths"]):
            raise SliceError(f"slice {s['slice_id']!r} has an empty path")
    return data


def in_slice(path: str, s: dict, ignore: Sequence[str]) -> bool:
    if any(matches(path, p) for p in ignore):
        return False
    return any(matches(path, p) for p in s["paths"])


def tracked_files(root: Path = REPO_ROOT) -> List[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True)
    return [p for p in out.stdout.decode("utf-8").split("\0") if p]


def coverage(manifest: dict, files: Iterable[str]) -> Dict[str, object]:
    """Which tracked source files each language's slices cover, and which they miss."""
    ignore = manifest.get("paths_ignore", [])
    exclusions = manifest.get("coverage_exclusions", {})
    report: Dict[str, object] = {}
    for language, exts in manifest.get("coverage", {}).items():
        slices = [s for s in manifest["slices"] if s["language"] == language]
        relevant = [f for f in files if f.endswith(tuple(exts))]
        missing, excluded, per_slice = [], [], {s["slice_id"]: 0 for s in slices}
        for f in relevant:
            hit = [s["slice_id"] for s in slices if in_slice(f, s, ignore)]
            for sid in hit:
                per_slice[sid] += 1
            if hit:
                continue
            if any(matches(f, p) for p in exclusions.get(language, {})):
                excluded.append(f)
            else:
                missing.append(f)
        report[language] = {"files": len(relevant), "covered": len(relevant) - len(missing) - len(excluded),
                            "excluded": excluded, "missing": missing, "per_slice": per_slice}
    return report


def stale_paths(manifest: dict, files: Sequence[str]) -> List[str]:
    """Slice paths that select no tracked file.  CodeQL aborts on a path that does not exist."""
    return [f"{s['slice_id']}: {p}" for s in manifest["slices"] for p in s["paths"]
            if not any(matches(f, p) for f in files)]


def plan(manifest: dict, changed: Optional[Sequence[str]]) -> List[dict]:
    """Slices to analyse: all of them when ``changed`` is None/empty or the plan itself changed."""
    slices = manifest["slices"]
    if not changed or any(c in PLAN_INPUTS for c in changed):
        return list(slices)
    ignore = manifest.get("paths_ignore", [])
    return [s for s in slices if any(in_slice(c, s, ignore) for c in changed)]


def codeql_config(manifest: dict, s: dict) -> str:
    """CodeQL configuration (YAML is a superset of JSON) restricting analysis to one slice."""
    return json.dumps({"paths": list(s["paths"]), "paths-ignore": list(manifest.get("paths_ignore", []))}, indent=2)


def find_codeql(explicit: Optional[str] = None) -> str:
    candidates = [explicit, os.environ.get("CODEQL_CLI"), shutil.which("codeql")]
    cache = Path("/opt/hostedtoolcache/CodeQL")
    if cache.is_dir():
        candidates += [str(p) for p in sorted(cache.glob("*/x64/codeql/codeql"), reverse=True)]
    for c in candidates:
        if c and Path(c).is_file() and os.access(c, os.X_OK):
            return c
    raise SliceError("CodeQL CLI not found; pass --codeql or set CODEQL_CLI")


def summarise_sarif(sarif_path: Path) -> dict:
    run = json.loads(sarif_path.read_text(encoding="utf-8"))["runs"][0]
    rules = {}
    for component in [run["tool"]["driver"]] + run["tool"].get("extensions", []):
        for r in component.get("rules", []):
            rules[r["id"]] = r
    results = []
    for r in run.get("results", []):
        rule = rules.get(r.get("ruleId"), {})
        loc = r["locations"][0]["physicalLocation"]
        results.append({
            "rule": r.get("ruleId"),
            "level": r.get("level") or rule.get("defaultConfiguration", {}).get("level", "warning"),
            "security_severity": rule.get("properties", {}).get("security-severity"),
            "path": loc["artifactLocation"]["uri"],
            "line": loc.get("region", {}).get("startLine"),
            "message": r["message"]["text"],
        })
    return {"rules_evaluated": len(rules), "results": results}


def analyze(manifest: dict, slice_id: str, codeql: str, suite: str, out_dir: Path, threads: int = 0) -> dict:
    s = next((x for x in manifest["slices"] if x["slice_id"] == slice_id), None)
    if s is None:
        raise SliceError(f"unknown slice {slice_id!r}")
    out_dir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=f"codeql-{slice_id}-"))
    try:
        cfg = work / "config.yml"
        cfg.write_text(codeql_config(manifest, s), encoding="utf-8")
        db = work / "db"
        cmd = [codeql, "database", "create", str(db), f"--language={s['language']}",
               f"--build-mode={s['build_mode']}", f"--source-root={REPO_ROOT}",
               f"--codescanning-config={cfg}", f"--threads={threads}", "--overwrite"]
        done = subprocess.run(cmd, capture_output=True, text=True)
        if done.returncode != 0:
            raise SliceError(f"database create failed for {slice_id}: {(done.stderr or done.stdout)[-3000:]}")
        sarif = out_dir / f"{slice_id}.sarif"
        pack = {"python": "codeql/python-queries"}.get(s["language"], f"codeql/{s['language']}-queries")
        cmd = [codeql, "database", "analyze", str(db), f"{pack}:codeql-suites/{s['language']}-{suite}.qls",
               "--format=sarif-latest", f"--output={sarif}", f"--threads={threads}"]
        done = subprocess.run(cmd, capture_output=True, text=True)
        if done.returncode != 0:
            raise SliceError(f"analysis failed for {slice_id}: {done.stderr[-2000:]}")
        scanned = re.search(r"scanned (\d+) out of (\d+)", done.stdout + done.stderr)
        summary = summarise_sarif(sarif)
        summary.update({"slice_id": slice_id, "suite": suite, "sarif": str(sarif),
                        "files_scanned": int(scanned.group(1)) if scanned else None,
                        "files_seen": int(scanned.group(2)) if scanned else None})
        return summary
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="fail if any tracked source file is in no slice")
    p = sub.add_parser("plan", help="print the Actions matrix for the changed files")
    p.add_argument("--changed-from", help="file listing changed paths, one per line (omit: all slices)")
    p.add_argument("--github-output", help="append has_work/matrix to this file")
    p.add_argument("--manifest-out", help="write the scope manifest JSON here")
    a = sub.add_parser("analyze", help="run CodeQL locally on one or more slices")
    a.add_argument("slices", nargs="+")
    a.add_argument("--codeql")
    a.add_argument("--suite", default="security-extended",
                   choices=["code-scanning", "security-extended", "security-and-quality"])
    a.add_argument("--out", default="codeql-results")
    a.add_argument("--threads", type=int, default=0)
    a.add_argument("--fail-on-results", action="store_true",
                   help="exit 1 if any result has level error or warning")
    args = ap.parse_args(argv)
    manifest = load_manifest()

    if args.cmd == "check":
        files = tracked_files()
        report = coverage(manifest, files)
        stale = stale_paths(manifest, files)
        for entry in stale:
            print(f"STALE SLICE PATH (matches no tracked file; CodeQL would abort): {entry}")
        bad = bool(stale)
        for language, r in report.items():
            print(f"{language}: {r['covered']}/{r['files']} tracked files in a slice, "
                  f"{len(r['excluded'])} excluded by policy, {len(r['missing'])} in no slice")
            for sid, n in r["per_slice"].items():
                print(f"  {sid}: {n}")
            for f in r["missing"]:
                print(f"  NOT COVERED: {f}")
            bad = bad or bool(r["missing"])
        return 1 if bad else 0

    if args.cmd == "plan":
        changed = None
        if args.changed_from:
            changed = [ln.strip() for ln in Path(args.changed_from).read_text(encoding="utf-8").splitlines() if ln.strip()]
        selected = plan(manifest, changed)
        include = [{"slice_id": s["slice_id"], "language": s["language"], "build_mode": s["build_mode"],
                    "config": codeql_config(manifest, s)} for s in selected]
        if args.manifest_out:
            Path(args.manifest_out).write_text(json.dumps({
                "changed_files_count": len(changed or []), "changed_files": changed or [],
                "selected_slice_ids": [s["slice_id"] for s in selected]}, indent=2), encoding="utf-8")
        if args.github_output:
            with open(args.github_output, "a", encoding="utf-8") as fh:
                fh.write(f"has_work={'true' if include else 'false'}\n")
                fh.write(f"matrix={json.dumps({'include': include})}\n")
        else:
            print(json.dumps({"include": include}, indent=2))
        return 0

    codeql = find_codeql(args.codeql)
    worst = 0
    for sid in args.slices:
        try:
            summary = analyze(manifest, sid, codeql, args.suite, Path(args.out), args.threads)
        except SliceError as exc:  # report and continue: one broken slice must not hide the others
            print(f"{sid}: FAILED — {exc}")
            worst = 2
            continue
        (Path(args.out) / f"{sid}.summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        levels: Dict[str, int] = {}
        for r in summary["results"]:
            levels[r["level"]] = levels.get(r["level"], 0) + 1
        print(f"{sid}: scanned {summary['files_scanned']}/{summary['files_seen']} files, "
              f"{summary['rules_evaluated']} rules ({args.suite}), results by level {levels or '{}'}")
        for r in summary["results"]:
            print(f"  [{r['level']}] {r['rule']} {r['path']}:{r['line']} {r['message'][:140]}")
        if args.fail_on_results and (levels.get("error") or levels.get("warning")):
            worst = max(worst, 1)
    return worst


if __name__ == "__main__":
    sys.exit(main())
