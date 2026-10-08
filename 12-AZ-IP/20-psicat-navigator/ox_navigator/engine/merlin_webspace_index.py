# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""The full webspace machine index: reconstructed, verified and audited.

ADJACENT TRACK.  The steward supplied the complete ``axiomzero.machine-index/v2``
document as a PDF exported from a word processor (``WEBSPACE10_01.pdf``,
2,190 pages).  PDF text extraction is lossy in known ways: strings wrap across
lines, and extra spaces appear before some punctuation.  This module

1. rebuilds the JSON from the extracted text (``reconstruct_index_text``);
2. undoes the extraction artefacts with a fixed, counted rule set
   (``normalise_extraction_artifacts``);
3. proves the reconstruction is exact where it matters by recomputing the
   published tree hash over all 1,454 file digests (``verify_tree_hash``);
4. audits what the index says about the dependency tree, the backend and the
   clock, and reports each inconsistency as a finding.

The normalised copy lives in ``data/raw/``.  Prose whitespace inside long
descriptions is best-effort; paths, digests, counts and flags are exact,
and the tree hash is the proof.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

from .constants import MERLIN_TICK_DENOMINATOR, MERLIN_TICK_NUMERATOR

STATUS_LABEL = "ADJACENT_TRACK"
RAW_DIR = Path(__file__).resolve().parent / "data" / "raw"
INDEX_PATH = RAW_DIR / "machine_index_2026-10-07.json.gz"
PROVENANCE_PATH = RAW_DIR / "machine_index_2026-10-07.provenance.json"
PAGE_BREAK = "\n<<<PAGE>>>\n"
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}
REDACTED_PHONE = "omitted-in-repository-copy"

_PHONE = re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")
_TRAILING_ARTIFACT = re.compile(r"(?<=[.:;!?)\"'\]]) +$")


# --- reconstruction ------------------------------------------------------------------

def reconstruct_index_text(extracted: str) -> str:
    """Join PDF-extracted text back into JSON text.

    Line breaks inside JSON strings are wrap points introduced by the page
    layout, so they are dropped; breaks outside strings are whitespace and kept.
    """
    text = extracted.replace(PAGE_BREAK, "\n")
    out: list[str] = []
    in_string = escaped = False
    for ch in text:
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            elif ch == "\n":
                continue
        elif ch == '"':
            in_string = True
        out.append(ch)
    return "".join(out)


_STRING_RULES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("leading_space_before_dot", re.compile(r"^ (?=\.)"), ""),
    ("space_after_glob_star", re.compile(r"(?<=\*) (?=\.)"), ""),
    ("space_before_glob_star", re.compile(r"(?<=\.) (?=\*)"), ""),
    ("space_before_comma", re.compile(r" (?=,)"), ""),
    ("trailing_space_after_punctuation", _TRAILING_ARTIFACT, ""),
)


def normalise_extraction_artifacts(value: Any, counts: Counter | None = None) -> Any:
    """Apply the fixed artefact rules to every key and string value, counting each."""
    counts = counts if counts is not None else Counter()

    def fix(text: str) -> str:
        for name, pattern, repl in _STRING_RULES:
            text, n = pattern.subn(repl, text)
            if n:
                counts[name] += n
        return text

    if isinstance(value, dict):
        return {fix(k): normalise_extraction_artifacts(v, counts) for k, v in value.items()}
    if isinstance(value, list):
        return [normalise_extraction_artifacts(v, counts) for v in value]
    if isinstance(value, str):
        return fix(value)
    return value


def redact_phone_shaped_strings(index: dict[str, Any]) -> int:
    """Withhold the agency telephone samples, as the earlier snapshot did."""
    sample = index.get("redaction", {}).get("phone_shaped_strings", {}).get("sample", [])
    hits = sum(1 for s in sample if _PHONE.search(str(s)))
    if hits:
        index["redaction"]["phone_shaped_strings"]["sample"] = [REDACTED_PHONE] * len(sample)
    return hits


def reconstruct_index(extracted: str) -> tuple[dict[str, Any], dict[str, int]]:
    counts: Counter = Counter()
    index = normalise_extraction_artifacts(json.loads(reconstruct_index_text(extracted)), counts)
    return index, dict(counts)


def extract_pdf_text(pdf_path: str | Path) -> str:  # pragma: no cover - needs pypdf and the PDF
    from pypdf import PdfReader

    return PAGE_BREAK.join(page.extract_text() for page in PdfReader(str(pdf_path)).pages)


# --- loading -------------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_full_index(path: str | None = None) -> dict[str, Any] | None:
    target = Path(path) if path else INDEX_PATH
    if not target.exists():
        return None
    with gzip.open(target, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def load_index_provenance() -> dict[str, Any]:
    try:
        return json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


# --- verification --------------------------------------------------------------------

def verify_tree_hash(index: dict[str, Any]) -> dict[str, Any]:
    hashes = index.get("hashes", {})
    files = hashes.get("files", {})
    lines = [f"{path}\0{str(entry.get('sha256', '')).lower()}" for path, entry in sorted(files.items())]
    recomputed = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    published = hashes.get("tree_hash") or index.get("provenance", {}).get("tree_hash_sha256")
    return {
        "published": published,
        "recomputed": recomputed,
        "verified": recomputed == published,
        "file_count": len(files),
        "declared_file_count": index.get("provenance", {}).get("file_count"),
        "total_bytes": sum(int(e.get("bytes", 0)) for e in files.values()),
        "declared_total_bytes": index.get("provenance", {}).get("total_bytes"),
    }


# --- semver (caret ranges are the only form package.json uses here) -----------------

def _core(version: str) -> tuple[tuple[int, int, int], str]:
    main, _, pre = str(version).lstrip("^~=v").partition("-")
    parts = [int(p) for p in re.findall(r"\d+", main)[:3]]
    while len(parts) < 3:
        parts.append(0)
    return (parts[0], parts[1], parts[2]), pre


def satisfies_caret(version: str, spec: str) -> bool:
    """npm caret semantics: ^1.2.3 → >=1.2.3 <2; ^0.2.3 → <0.3; ^0.0.3 → exactly 0.0.3."""
    if not str(spec).startswith("^"):
        return _core(version) == _core(spec)
    (v, v_pre), (s, s_pre) = _core(version), _core(spec)
    if v_pre and (v != s or not s_pre):
        return False
    if v < s or (v == s and v_pre and s_pre and v_pre < s_pre):
        return False
    if s[0] > 0:
        return v[0] == s[0]
    if s[1] > 0:
        return v[:2] == s[:2]
    return v == s


# --- audits --------------------------------------------------------------------------

def _finding(fid: str, severity: str, title: str, evidence: str, recommendation: str) -> dict[str, Any]:
    return {"id": fid, "severity": severity, "title": title, "evidence": evidence, "recommendation": recommendation}


def sbom_integrity(index: dict[str, Any]) -> dict[str, Any]:
    sbom = index.get("sbom", {})
    packages = sbom.get("packages", [])
    runtime = sbom.get("declared_runtime_dependencies", {})
    dev = sbom.get("declared_dev_dependencies", {})
    declared = {**runtime, **dev}
    key_counts = Counter((p["name"], p["version"], p.get("integrity")) for p in packages)
    repeats = sorted(((n, k[0], k[1]) for k, n in key_counts.items() if n > 1), reverse=True)
    unsatisfied = [p for p in packages
                   if p.get("direct") and p["name"] in declared and not satisfies_caret(p["version"], declared[p["name"]])]
    wrong_direct = sorted({(p["name"], p["version"], declared[p["name"]]) for p in unsatisfied})
    flagged_dev: dict[str, set[bool]] = defaultdict(set)
    for p in packages:
        if p["name"] in dev and satisfies_caret(p["version"], dev[p["name"]]):
            flagged_dev[p["name"]].add(bool(p.get("dev")))
    dev_misflagged = sorted(name for name, flags in flagged_dev.items() if flags == {False})
    majors: dict[str, set[int]] = defaultdict(set)
    for p in packages:
        if p["name"] in declared:
            majors[p["name"]].add(_core(p["version"])[0][0])
    multi_major = {name: sorted(m) for name, m in sorted(majors.items()) if len(m) > 1}
    licences = Counter(str(p.get("license")) for p in packages)
    return {
        "entries": len(packages),
        "declared_package_count": sbom.get("package_count"),
        "distinct_name_version_integrity": len(key_counts),
        "distinct_names": len({p["name"] for p in packages}),
        "repeated_entries": [{"name": n, "version": v, "occurrences": c} for c, n, v in repeats],
        "repeat_surplus": sum(c - 1 for c, _, _ in repeats),
        "direct_entries": sum(1 for p in packages if p.get("direct")),
        "declared_direct": len(declared),
        "direct_flag_unsatisfied": [{"name": n, "version": v, "spec": s} for n, v, s in wrong_direct],
        "direct_flag_unsatisfied_entries": len(unsatisfied),
        "dev_declared_but_flagged_runtime": dev_misflagged,
        "declared_packages_with_multiple_majors": multi_major,
        "hippocratic_packages": sorted(f"{p['name']}@{p['version']}" for p in packages if "Hippocratic" in str(p.get("license"))),
        "direct_hippocratic": sorted(p["name"] for p in packages if "Hippocratic" in str(p.get("license")) and p["name"] in declared),
        "python_licensed": sorted(f"{p['name']}@{p['version']} (dev={p.get('dev')})" for p in packages if p.get("license") == "Python-2.0"),
        "licence_histogram_recomputed": dict(licences.most_common()),
    }


def _cron_runs_per_day(expr: str | None) -> float | None:
    if not expr:
        return None
    fields = expr.split()
    if len(fields) != 5:
        return None

    def count(field: str, span: int, low: int = 0) -> int:
        total = set()
        for part in field.split(","):
            base, _, step = part.partition("/")
            step_n = int(step) if step else 1
            if base == "*":
                lo, hi = low, low + span - 1
            elif "-" in base:
                lo, hi = (int(x) for x in base.split("-"))
            else:
                lo = hi = int(base)
            total.update(range(lo, hi + 1, step_n))
        return len(total)

    minute, hour, _dom, _month, dow = fields
    days = 7 if dow == "*" else count(dow, 7)
    return count(minute, 60) * count(hour, 24) * days / 7.0


def backend_posture(index: dict[str, Any]) -> dict[str, Any]:
    backend = index.get("backend", {})
    functions = backend.get("functions", [])
    service_unauth = sorted(f["name"] for f in functions
                            if f.get("service_role") and not f.get("auth_checked") and not f.get("admin_only"))
    unused_secrets = sorted(s["name"] for s in backend.get("secrets", []) if not s.get("referenced_by_count"))
    published_secret_values = [s["name"] for s in backend.get("secrets", [])
                               if s.get("value") and not str(s["value"]).startswith("NOT PUBLISHED")]
    write_scopes = {"public_repo", "repo", "w_organization_social", "w_member_social"}
    connectors = [{"type": c.get("type"), "granted_scopes": c.get("granted_scopes", []),
                   "write_capable_scopes": sorted(write_scopes & set(c.get("granted_scopes", [])))}
                  for c in backend.get("connectors", [])]
    by_call: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    runs_per_day: dict[str, float] = {}
    for w in backend.get("workflows", []):
        rate = _cron_runs_per_day(w.get("cron_expression"))
        if rate is None and w.get("interval"):
            match = re.match(r"(\d+)\s*hour", str(w["interval"]))
            rate = 24.0 / int(match.group(1)) if match else None
        if rate is not None:
            runs_per_day[w["name"]] = round(rate, 3)
        if w.get("trigger_type") == "scheduled":
            graph = json.dumps(w.get("execution_graph", []), sort_keys=True)
            by_call[(graph, str(w.get("cron_expression")), str(w.get("interval")))].append(w["name"])
    duplicate_schedules = [names for names in by_call.values() if len(names) > 1]
    repo_writers = [f for f in functions if f["name"] in ("psicatRepoWrite", "psicatRepoContributorCredit")]
    stub_refusals = all(f.get("ast_counts", {}).get("conditionals", 1) == 0 and not f.get("secrets_referenced")
                        and not f.get("external_hosts") for f in repo_writers) if repo_writers else None
    return {
        "functions": len(functions),
        "service_role_without_auth_check": service_unauth,
        "secret_names": len(backend.get("secrets", [])),
        "secret_values_published": published_secret_values,
        "unreferenced_secrets": unused_secrets,
        "connectors": connectors,
        "scheduled_runs_per_day": dict(sorted(runs_per_day.items(), key=lambda kv: -kv[1])),
        "total_scheduled_runs_per_day": round(sum(runs_per_day.values()), 1),
        "duplicate_schedules": duplicate_schedules,
        "repo_write_functions_are_stub_refusals": stub_refusals,
    }


def clock_comparison(index: dict[str, Any]) -> dict[str, Any]:
    backend = index.get("backend", {})
    blob = json.dumps(backend, ensure_ascii=False)
    ratio_hits = [w["name"] for w in backend.get("workflows", []) if "12/37" in str(w.get("description", ""))]
    clock_workflows = {w["name"]: {"cron": w.get("cron_expression"), "calls": w.get("calls_functions")}
                       for w in backend.get("workflows", [])
                       if any(t in w["name"] for t in ("Clock", "Chronometer"))}
    chronometry = next((m for m in backend.get("shared_modules", []) if m.get("name") == "chronometry"), {})
    return {
        "merlin_tick": f"{MERLIN_TICK_NUMERATOR}/{MERLIN_TICK_DENOMINATOR}",
        "webspace_clock_workflows": clock_workflows,
        "webspace_clock_kind": "wall-clock cross-verification against external time hosts",
        "webspace_time_hosts": chronometry.get("external_hosts", []),
        "chronometry_exports": chronometry.get("exports", []),
        "ratio_12_37_mentions_in_index": blob.count("12/37"),
        "ratio_12_37_context": ratio_hits,
        "constants_visible": False,
        "reading": (
            "The index publishes the clock's metadata, not its source. It shows a 15-minute durable tick and an "
            "hourly cross-check against external time hosts. 12/37 appears only as c_s in the Cat Nap replay. "
            "Whether CHRONOMETER_CONSTANTS uses 12/37 needs chronometry.ts from machine-source.json."
        ),
    }


def audit_full_index(index: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    idx = index if index is not None else load_full_index()
    if idx is None:
        return []
    findings: list[dict[str, Any]] = []
    tree = verify_tree_hash(idx)
    if tree["verified"]:
        findings.append(_finding(
            "IX-TREE-HASH-VERIFIED", "info", "Machine-index tree hash reproduces exactly",
            f"SHA-256 over {tree['file_count']} sorted '<path>\\0<sha256>' lines = {tree['recomputed']}, "
            "equal to the published tree hash. Every path and file digest in this copy is exact.",
            "Keep publishing the definition next to the digest; this is what makes the index checkable.",
        ))
    else:
        findings.append(_finding(
            "IX-TREE-HASH-MISMATCH", "high", "Machine-index tree hash does not reproduce",
            f"recomputed {tree['recomputed']} vs published {tree['published']}.",
            "Re-export the index; do not rely on per-file digests until this matches.",
        ))
    if tree["file_count"] != tree["declared_file_count"] or tree["total_bytes"] != tree["declared_total_bytes"]:
        findings.append(_finding(
            "IX-FILE-ARITHMETIC", "low", "Declared file totals disagree with the hash list",
            f"hash list: {tree['file_count']} files, {tree['total_bytes']} bytes; declared: "
            f"{tree['declared_file_count']} files, {tree['declared_total_bytes']} bytes.", "Recount.",
        ))

    sb = sbom_integrity(idx)
    if sb["repeat_surplus"]:
        top = ", ".join(f"{r['name']}@{r['version']}×{r['occurrences']}" for r in sb["repeated_entries"][:4])
        findings.append(_finding(
            "IX-SBOM-INSTALL-LOCATIONS", "low", "SBOM package_count counts install locations, not packages",
            f"{sb['entries']} entries, {sb['distinct_name_version_integrity']} distinct name+version+integrity "
            f"({sb['repeat_surplus']} repeats; {top}). The entries carry no lockfile path, so repeats cannot be told apart.",
            "Publish the lockfile path per entry, or de-duplicate and report both counts.",
        ))
    if sb["direct_flag_unsatisfied"]:
        listed = ", ".join(f"{d['name']}@{d['version']} (spec {d['spec']})" for d in sb["direct_flag_unsatisfied"])
        findings.append(_finding(
            "IX-SBOM-DIRECT-FLAG", "medium", "Nested copies are marked direct",
            f"{sb['direct_entries']} entries are flagged direct, but package.json declares {sb['declared_direct']}. "
            f"{sb['direct_flag_unsatisfied_entries']} flagged entries cannot satisfy the declared range: {listed}. "
            f"The remaining {sb['direct_entries'] - sb['declared_direct'] - sb['direct_flag_unsatisfied_entries']} "
            "are extra in-range copies. The generator appears to set `direct` by package name.",
            "Set direct only on the top-level node_modules entry, which is the one npm resolves for package.json.",
        ))
    if sb["dev_declared_but_flagged_runtime"]:
        findings.append(_finding(
            "IX-SBOM-DEV-FLAG", "low", "Declared dev dependencies are flagged as runtime",
            ", ".join(sb["dev_declared_but_flagged_runtime"]) + ": declared in devDependencies; every matching "
            "entry has dev=false. npm clears the dev flag when a runtime package also depends on it, so this "
            "may be correct for the lockfile but misleading as a bundle claim.",
            "Report the declared role and the lockfile flag separately.",
        ))
    if sb["declared_packages_with_multiple_majors"]:
        listed = ", ".join(f"{k} {v}" for k, v in sb["declared_packages_with_multiple_majors"].items())
        findings.append(_finding(
            "IX-SBOM-MULTI-MAJOR", "info", "Declared packages installed at more than one major version",
            listed + ". The older copies are nested under other dependencies.",
            "Check which copies reach the browser bundle; two TensorFlow.js majors is a real size cost.",
        ))
    if sb["hippocratic_packages"]:
        findings.append(_finding(
            "IX-HIPPOCRATIC-NAMED", "medium", "The Hippocratic-licensed packages, named",
            f"{', '.join(sb['hippocratic_packages'])}; directly declared: {', '.join(sb['direct_hippocratic']) or 'none'}.",
            "react-leaflet is a direct dependency, so the field-of-use terms reach the shipped app. Decide deliberately.",
        ))

    be = backend_posture(idx)
    if be["service_role_without_auth_check"]:
        findings.append(_finding(
            "IX-SERVICE-ROLE-UNAUTHENTICATED", "high", "Service-role functions with no detected auth check",
            f"{len(be['service_role_without_auth_check'])} of {be['functions']} functions use the service role, "
            "are not admin-only, and show no auth check in the index's static analysis: "
            f"{', '.join(be['service_role_without_auth_check'][:12])}, …",
            "Confirm each is either scheduler-only and rejects user calls, or add an explicit auth check. "
            "The flag is static analysis; read the source before concluding.",
        ))
    for conn in be["connectors"]:
        if conn["type"] == "github" and conn["write_capable_scopes"]:
            unused = [s for s in be["unreferenced_secrets"] if "GITHUB" in s]
            findings.append(_finding(
                "IX-GITHUB-WRITE-SCOPE", "high", "GitHub connector holds a write-capable scope under a read-only policy",
                f"granted scopes {conn['granted_scopes']}; 'public_repo' grants write access to public repositories. "
                f"The index's own VF-5 says repository writes are hard refusals in code. Unreferenced GitHub secret: "
                f"{', '.join(unused) or 'none'}.",
                "Reduce the connector to read-only access (no scope is needed to read public repos), and revoke unused tokens.",
            ))
    if be["unreferenced_secrets"]:
        findings.append(_finding(
            "IX-UNREFERENCED-SECRETS", "low", "Secrets configured but referenced by no function",
            ", ".join(be["unreferenced_secrets"]), "Revoke credentials nothing uses.",
        ))
    if be["secret_values_published"]:
        findings.append(_finding("IX-SECRET-VALUE", "high", "A secret value appears in the index",
                                 ", ".join(be["secret_values_published"]), "Rotate immediately."))
    for names in be["duplicate_schedules"]:
        findings.append(_finding(
            "IX-DUPLICATE-SCHEDULE", "low", "Two scheduled workflows run the same call on the same cadence",
            " and ".join(names) + " invoke the same function with the same arguments on the same schedule.",
            "Delete one; each run is billed and the second can race the first.",
        ))
    if be["total_scheduled_runs_per_day"]:
        busiest = ", ".join(f"{k} {v:g}/day" for k, v in list(be["scheduled_runs_per_day"].items())[:4])
        findings.append(_finding(
            "IX-SCHEDULE-LOAD", "info", "Scheduled workflow load",
            f"about {be['total_scheduled_runs_per_day']:g} scheduled runs per day across "
            f"{len(be['scheduled_runs_per_day'])} schedules; busiest: {busiest}.",
            "Weigh each five-minute schedule against what it produces; most work here is not that urgent.",
        ))
    if be["repo_write_functions_are_stub_refusals"] is False:
        findings.append(_finding("IX-REPO-WRITE", "high", "Repository-write functions are not simple refusals",
                                 "psicatRepoWrite / psicatRepoContributorCredit show branching or external calls.",
                                 "Read the source."))

    for vf in idx.get("verification_findings", []):
        evidence = vf.get("evidence", {})
        if vf.get("id") == "VF-6" and isinstance(evidence, dict):
            leaked = [p for p in evidence.get("in_bundle_not_in_tree", []) if p.strip() in (".npmrc", ".env")]
            if leaked:
                findings.append(_finding(
                    "IX-STALE-BUNDLE-CREDENTIAL-FILE", "high", "The stale public source bundle contains .npmrc",
                    f"VF-6: the bundle served to listSourceFiles/readSourceFile ({evidence.get('bundle_file_count')} files) "
                    f"includes {', '.join(leaked)}, a file type the index's own exclusions withhold because it "
                    "may carry registry credentials.",
                    "Inspect that file in the bundle; if it holds a token, rotate it, then rebuild or delete the bundle.",
                ))
        if vf.get("status") == "open":
            findings.append(_finding(
                f"IX-SELF-{vf.get('id')}", "info", f"Webspace self-reported open finding {vf.get('id')}",
                str(vf.get("finding", "")).strip(), "Tracked by the webspace; restated here so it is not lost.",
            ))

    clock = clock_comparison(idx)
    findings.append(_finding(
        "IX-CLOCK-12-37", "info", "Webspace clock vs Merlin's 12/37 tick: not comparable from the index",
        clock["reading"], "Supply base44/shared/chronometry.ts (or machine-source.json) to settle it.",
    ))
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), f["id"]))
    return findings


def summarise_full_index(index: dict[str, Any] | None = None) -> dict[str, Any]:
    idx = index if index is not None else load_full_index()
    if idx is None:
        return {"status": STATUS_LABEL, "available": False}
    findings = audit_full_index(idx)
    counts = Counter(f["severity"] for f in findings)
    backend = idx.get("backend", {})
    frontend = idx.get("frontend", {})
    return {
        "status": STATUS_LABEL,
        "available": True,
        "source": load_index_provenance(),
        "generated_at": idx.get("provenance", {}).get("generated_at"),
        "git_commit": idx.get("provenance", {}).get("git_commit"),
        "declared_framework_version": idx.get("identity", {}).get("declared_framework_version"),
        "tree_hash": verify_tree_hash(idx),
        "inventory": {
            "files": len(idx.get("hashes", {}).get("files", {})),
            "routes": len(frontend.get("routes", [])),
            "components": len(frontend.get("components", [])),
            "functions": len(backend.get("functions", [])),
            "entities": len(backend.get("entities", [])),
            "workflows": len(backend.get("workflows", [])),
            "agents": [a.get("name") for a in backend.get("agents", [])],
            "agent_skills": len(backend.get("agent_skills", [])),
            "articles": idx.get("content", {}).get("articles_source", {}).get("count"),
        },
        "sbom": sbom_integrity(idx),
        "backend": backend_posture(idx),
        "clock": clock_comparison(idx),
        "severity_counts": dict(counts),
        "findings": findings,
    }
