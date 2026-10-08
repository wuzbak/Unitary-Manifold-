# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Webspace provenance audit: what the AxiomZero webspace says about itself, checked.

ADJACENT TRACK.  Merlin reads two artefacts that the webspace publishes about
its own structure: the ``axiomzero.machine-index/v2`` document and the
"Data Provenance" page.  A transcription of both, as supplied by the steward,
lives in ``data/webspace_provenance_snapshot.json``.

The authority split is taken from the machine index itself.  The repository's
live registry is the authority for framework status; the machine index is the
authority for the webspace's own code and configuration.  This module therefore
never lets a webspace page override the repository on version or claims, and it
never treats a webspace self-description as verified merely because it says so.

What it does:
- recomputes hashes where the inputs are actually available (provenance chain,
  tree hash), with the hashing convention stated explicitly;
- checks the internal arithmetic of the published counts;
- cross-checks versions and licences against the repository and against the
  SBOM the same webspace publishes;
- reports every inconsistency as a finding with severity and evidence.

When the full index is present in ``data/raw/`` (see ``merlin_webspace_index``),
its findings are merged in and the partial-transcription notice is dropped.

What it does not do: fetch anything over the network, or certify that the live
site matches this snapshot.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence

from .merlin_webspace_index import audit_full_index, load_full_index, verify_tree_hash

STATUS_LABEL = "ADJACENT_TRACK"
SNAPSHOT_PATH = Path(__file__).resolve().parent / "data" / "webspace_provenance_snapshot.json"
REPO_ROOT = Path(__file__).resolve().parents[4]
LIVE_REGISTRY_PATH = REPO_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"
REPO_LICENSE_FILES = ("LICENSE", "LICENSE-AGPL")

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_HEX = re.compile(r"^[0-9a-f]+$")
# Five or more successive truncated digests: a random SHA-256 prefix steps
# every nibble by exactly -1 (mod 16) with probability 1/16.
RANDOM_NIBBLE_STEP_RATE = 1.0 / 16.0
PLACEHOLDER_STEP_RATE_THRESHOLD = 0.5
_STOPWORDS = frozenset("a an and are as at be by does do for from how in is it of on or the this to was what when where which who why with".split())
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}


@lru_cache(maxsize=1)
def load_snapshot(path: str | None = None) -> dict[str, Any]:
    return json.loads(Path(path or SNAPSHOT_PATH).read_text(encoding="utf-8"))


def _version_tuple(text: str | None) -> tuple[int, ...] | None:
    match = re.search(r"(\d+(?:\.\d+)*)", str(text or ""))
    return tuple(int(part) for part in match.group(1).split(".")) if match else None


def _repo_framework_version(path: Path = LIVE_REGISTRY_PATH) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    version = (data.get("meta") or {}).get("version")
    return str(version) if version is not None else None


# --- hashing -------------------------------------------------------------------------

def is_sha256_hex(value: str) -> bool:
    return bool(_HEX64.match(str(value or "")))


def chain_hash(component_hashes: Sequence[str], *, separator: str = "", sort: bool = False) -> str:
    """SHA-256 over concatenated hex component hashes.

    The Data Provenance page says only "all component hashes concatenated", which
    leaves order, separator and encoding open.  The convention used here is
    stated: lowercase hex text, UTF-8, joined by ``separator`` in the given order
    (or sorted, if ``sort``).  Different conventions give different chains.
    """
    hashes = [str(h).strip().lower() for h in component_hashes]
    bad = [h for h in hashes if not is_sha256_hex(h)]
    if bad:
        raise ValueError(f"component hashes must be 64-char hex SHA-256 digests: {bad[:3]}")
    if sort:
        hashes.sort()
    return hashlib.sha256(separator.join(hashes).encode("utf-8")).hexdigest()


def verify_chain_hash(component_hashes: Sequence[str], published: str) -> dict[str, Any]:
    """Try the plausible concatenation conventions and report which, if any, match."""
    published = str(published or "").strip().lower()
    conventions = {
        "ordered_no_separator": {"separator": "", "sort": False},
        "sorted_no_separator": {"separator": "", "sort": True},
        "ordered_newline": {"separator": "\n", "sort": False},
        "sorted_newline": {"separator": "\n", "sort": True},
    }
    results = {name: chain_hash(component_hashes, **kw) for name, kw in conventions.items()}
    matched = [name for name, value in results.items() if value == published]
    return {"published": published, "candidates": results, "matched_conventions": matched, "verified": bool(matched)}


def tree_hash(file_hashes: dict[str, str]) -> str:
    """Recompute the machine-index tree hash exactly as the index defines it."""
    lines = [f"{path}\0{str(digest).lower()}" for path, digest in sorted(file_hashes.items())]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def nibble_step_rate(prefixes: Sequence[str]) -> dict[str, Any]:
    """Fraction of nibbles that decrease by exactly one between successive digests."""
    steps = hits = 0
    for left, right in zip(prefixes, prefixes[1:]):
        for a, b in zip(left.lower(), right.lower()):
            steps += 1
            hits += int((int(a, 16) - int(b, 16)) % 16 == 1)
    rate = hits / steps if steps else 0.0
    return {"steps": steps, "unit_decrements": hits, "rate": round(rate, 4), "random_expectation": RANDOM_NIBBLE_STEP_RATE}


# --- audit ---------------------------------------------------------------------------

def _finding(fid: str, severity: str, title: str, evidence: str, recommendation: str) -> dict[str, Any]:
    return {"id": fid, "severity": severity, "title": title, "evidence": evidence, "recommendation": recommendation}


def _audit_machine_index(mi: dict[str, Any], repo_version: str | None) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not mi.get("received_complete", True):
        findings.append(_finding(
            "MI-TRUNCATED", "info", "Machine index transcription is partial",
            f"Received text stops at {mi.get('truncated_at')}; agents, workflows and function contracts were not received.",
            "Fetch machine-index.json and machine-source.json directly before auditing agents or contracts.",
        ))
    declared = mi.get("identity", {}).get("declared_framework_version")
    if repo_version and _version_tuple(declared) != _version_tuple(repo_version):
        findings.append(_finding(
            "MI-VERSION-DRIFT", "medium", "Webspace declares a different framework version than the repository",
            f"machine index declares {declared}; repository live registry reports v{repo_version}.",
            "Per the index's own authority split, read the version from the live registry instead of restating it.",
        ))
    fe = mi.get("coverage", {}).get("frontend", {})
    parts = fe.get("page_files_routed", 0) + fe.get("page_files_embedded", 0) + fe.get("page_files_orphaned", 0)
    if parts != fe.get("page_files_total"):
        findings.append(_finding("MI-PAGE-ARITHMETIC", "low", "Page-file counts do not sum",
                                 f"routed+embedded+orphaned={parts} vs total={fe.get('page_files_total')}", "Recount."))
    if fe.get("page_files_orphaned"):
        findings.append(_finding(
            "MI-ORPHAN-PAGES", "low", "Orphaned page files",
            f"{fe['page_files_orphaned']} page files are neither routed nor embedded.",
            "Route, embed or delete them; orphaned pages drift silently.",
        ))
    sbom = mi.get("sbom", {})
    runtime = len(sbom.get("declared_runtime_dependencies", {}))
    dev = len(sbom.get("declared_dev_dependencies", {}))
    deps = mi.get("coverage", {}).get("dependencies", {})
    if (runtime, dev) != (deps.get("direct_dependencies"), deps.get("direct_dev_dependencies")):
        findings.append(_finding("MI-DIRECT-DEPS", "low", "Declared dependency lists disagree with coverage counts",
                                 f"lists: {runtime} runtime, {dev} dev; coverage: {deps.get('direct_dependencies')}, "
                                 f"{deps.get('direct_dev_dependencies')}", "Recount."))
    if sbom.get("direct_count") is not None and sbom.get("direct_count") != runtime + dev:
        findings.append(_finding(
            "MI-DIRECT-COUNT", "low", "SBOM direct_count does not equal declared direct dependencies",
            f"sbom.direct_count={sbom.get('direct_count')} but package.json declares {runtime}+{dev}={runtime + dev}.",
            "State how direct_count is derived (lockfile flags vs package.json) or reconcile it.",
        ))
    histogram_total = sum(sbom.get("license_histogram", {}).values())
    unlicensed = len(sbom.get("packages_without_license_metadata", []))
    if histogram_total + unlicensed != sbom.get("package_count"):
        findings.append(_finding("MI-LICENSE-HISTOGRAM", "low", "License histogram does not account for every package",
                                 f"{histogram_total} + {unlicensed} unlicensed != {sbom.get('package_count')}", "Recount."))
    hippocratic = sbom.get("license_histogram", {}).get("Hippocratic-2.1", 0)
    if hippocratic:
        findings.append(_finding(
            "MI-HIPPOCRATIC", "medium", "Use-restricted licence in the dependency tree",
            f"{hippocratic} packages are Hippocratic-2.1, which is not an OSI open-source licence and adds field-of-use terms.",
            "Confirm compatibility with AGPL-3.0 distribution of the webspace, or replace those packages.",
        ))
    if unlicensed:
        findings.append(_finding(
            "MI-NO-LICENSE-METADATA", "low", "Packages without licence metadata",
            ", ".join(sbom.get("packages_without_license_metadata", [])),
            "Read each package's LICENSE file and record the result; absence of metadata is not permission.",
        ))
    for pkg in sbom.get("copyleft_packages", []):
        if " OR " in str(pkg.get("license", "")):
            findings.append(_finding(
                "MI-COPYLEFT-CLASSIFICATION", "info", f"{pkg.get('name')} is dual-licensed with a permissive option",
                f"{pkg.get('license')} is counted as copyleft; Apache-2.0 can be elected instead.",
                "Record which licence is elected so the copyleft count is meaningful.",
            ))
    return findings


def _audit_provenance_page(page: dict[str, Any], mi: dict[str, Any], repo_version: str | None,
                           repo_root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    components = page.get("components", [])
    published = page.get("chain_hash", "")
    if not is_sha256_hex(published):
        findings.append(_finding("DP-CHAIN-FORMAT", "high", "Chain hash is not a SHA-256 hex digest",
                                 published, "Publish a 64-character lowercase hex digest."))
    if not any(is_sha256_hex(c.get("sha256", "")) for c in components):
        findings.append(_finding(
            "DP-CHAIN-UNVERIFIABLE", "high", "Provenance chain hash cannot be recomputed from the page",
            "The page publishes the chain digest but not the per-component SHA-256 values it is computed from, "
            "and does not fix the concatenation order, separator or encoding.",
            "Publish each component's full digest and a precise definition, as the machine index does for its tree hash.",
        ))
    timeline = page.get("timeline", [])
    prefixes = [t.get("hash_prefix", "") for t in timeline if _HEX.match(str(t.get("hash_prefix", "")))]
    if timeline and all(len(p) < 64 for p in prefixes):
        findings.append(_finding(
            "DP-TIMELINE-TRUNCATED", "medium", "Timeline hashes are truncated",
            f"Timeline shows {len(prefixes)} 8-character prefixes; a 32-bit prefix cannot be verified against a file.",
            "Link each event to its full digest and to the commit or artefact it attests.",
        ))
    # Per-component events, in the order the page shows them.
    pattern_prefixes = [t["hash_prefix"] for t in timeline
                        if t.get("component") != "All modules" and _HEX.match(str(t.get("hash_prefix", "")))]
    if len(pattern_prefixes) >= 3:
        best = nibble_step_rate(pattern_prefixes)
        if best["rate"] >= PLACEHOLDER_STEP_RATE_THRESHOLD:
            findings.append(_finding(
                "DP-TIMELINE-PLACEHOLDER", "high", "Per-component timeline hashes look synthetic",
                f"{best['unit_decrements']}/{best['steps']} successive nibbles step down by exactly one "
                f"(rate {best['rate']}; random SHA-256 prefixes give about {RANDOM_NIBBLE_STEP_RATE:.4f}).",
                "Replace them with digests computed from real artefacts, or label them as illustrative.",
            ))
    dates = [t.get("date", "") for t in timeline]
    if dates and dates != sorted(dates, reverse=True) and dates != sorted(dates):
        findings.append(_finding("DP-TIMELINE-ORDER", "low", "Timeline is not in date order",
                                 " → ".join(dates), "Sort events by date."))
    generated = str(mi.get("provenance", {}).get("generated_at", ""))[:10]
    if dates and generated and max(dates) < generated:
        findings.append(_finding(
            "DP-TIMELINE-STALE", "medium", "Latest provenance event predates the current webspace build",
            f"last event {max(dates)}; machine index generated {generated}.",
            "Emit a timeline event on every attested build.",
        ))
    internal = [c for c in components if c.get("kind") == "internal"]
    mit_internal = [c["name"] for c in internal if str(c.get("license", "")).upper() == "MIT"]
    summary = str(page.get("license_summary", {}).get("all_components", ""))
    repo_has_dpc_agpl = all((repo_root / name).exists() for name in REPO_LICENSE_FILES)
    if mit_internal and ("AGPL" in summary or repo_has_dpc_agpl):
        findings.append(_finding(
            "DP-LICENSE-CONTRADICTION", "high", "Internal components are labelled MIT, but the stated licence is DPC + AGPL-3.0",
            f"{', '.join(mit_internal)} show MIT; the page's licence summary, the machine index "
            f"('{mi.get('identity', {}).get('license')}') and the repository LICENSE/LICENSE-AGPL say otherwise.",
            "Relabel internal components DPC-1.0 (theory) / AGPL-3.0-or-later (code). MIT would grant rights the project does not grant.",
        ))
    declared = mi.get("identity", {}).get("declared_framework_version")
    stale = sorted({c["version"] for c in internal if c.get("name") != "Tarot Oracle Engine"})
    reference = repo_version or declared
    if stale and reference and any(_version_tuple(v) != _version_tuple(reference) for v in stale):
        findings.append(_finding(
            "DP-VERSION-DRIFT", "medium", "Component versions lag the framework",
            f"internal components show {', '.join(stale)}; machine index declares {declared}; "
            f"repository live registry reports v{repo_version}. Timeline's last bump is v24.1.",
            "Read the version from the live registry at render time.",
        ))
    runtime = mi.get("sbom", {}).get("declared_runtime_dependencies", {})
    dev = mi.get("sbom", {}).get("declared_dev_dependencies", {})
    for comp in components:
        pkg = comp.get("npm_package")
        if not pkg:
            continue
        spec = runtime.get(pkg) or dev.get(pkg)
        if spec and _version_tuple(spec) != _version_tuple(comp.get("version")):
            findings.append(_finding(
                f"DP-DEP-VERSION-{pkg.upper()}", "low", f"{comp['name']} version differs from package.json",
                f"page shows {comp.get('version')}; package.json declares {pkg} {spec}.",
                "Render versions from the lockfile, not by hand.",
            ))
    ext = page.get("license_summary", {}).get("external_dependencies", {})
    sbom_total = mi.get("sbom", {}).get("package_count")
    if sbom_total and ext.get("count") is not None and ext["count"] < sbom_total:
        findings.append(_finding(
            "DP-EXTERNAL-UNDERCOUNT", "medium", "External dependency count understates the SBOM",
            f"page lists {ext['count']} external packages as '{ext.get('attestation')}'; the SBOM lists {sbom_total} "
            f"packages ({len(runtime)} direct runtime, {len(dev)} direct dev).",
            "Either scope the claim ('3 showcased packages') or link the full SBOM with integrity hashes.",
        ))
    internal_count = page.get("license_summary", {}).get("internal_components", {}).get("count")
    if internal_count is not None and internal_count != len(internal):
        findings.append(_finding("DP-INTERNAL-COUNT", "low", "Internal component count mismatch",
                                 f"summary {internal_count} vs registry {len(internal)}", "Recount."))
    return findings


def audit_webspace_provenance(snapshot: dict[str, Any] | None = None, *,
                              repo_version: str | None = None, repo_root: Path | None = None,
                              include_full_index: bool = True) -> dict[str, Any]:
    snap = snapshot if snapshot is not None else load_snapshot()
    root = repo_root or REPO_ROOT
    version = repo_version if repo_version is not None else _repo_framework_version(root / "9-INFRASTRUCTURE" / "um_live_status.json")
    mi = snap.get("machine_index", {})
    page = snap.get("data_provenance_page", {})
    findings = _audit_machine_index(mi, version) + _audit_provenance_page(page, mi, version, root)
    full = load_full_index() if include_full_index else None
    tree = None
    if full is not None:
        # The complete index supersedes the partial transcription.
        findings = [f for f in findings if f["id"] != "MI-TRUNCATED"] + audit_full_index(full)
        tree = verify_tree_hash(full)
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f["severity"], 9), f["id"]))
    counts: dict[str, int] = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    return {
        "status": STATUS_LABEL,
        "audited_on": date.today().isoformat(),
        "authority_split": mi.get("authority_split"),
        "repository_framework_version": version,
        "webspace_declared_version": mi.get("identity", {}).get("declared_framework_version"),
        "machine_index_tree_hash": mi.get("provenance", {}).get("tree_hash_sha256"),
        "provenance_chain_hash": page.get("chain_hash"),
        "full_index_available": full is not None,
        "machine_index_tree_hash_check": tree,
        "verifiable_now": [
            "count arithmetic in the machine index",
            "licence and version consistency against the repository",
        ] + (["machine-index tree hash over every file digest",
              "SBOM flags against package.json ranges",
              "backend auth, connector scope and schedule posture"] if full is not None else []),
        "verifiable_with_more_data": [
            "provenance chain hash (needs full per-component digests and the concatenation rule)",
            "webspace clock constants (needs base44/shared/chronometry.ts from machine-source.json)",
        ] + ([] if full is not None else ["machine-index tree hash (needs the full index)"]),
        "severity_counts": counts,
        "findings": findings,
    }


def answer_provenance_question(question: str, snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    """Route a question about the webspace to the right authority, per the authority split."""
    text = str(question or "").lower()
    science_terms = ("version", "pillar", "theorem", "falsif", "claim", "status", "prediction", "sprint")
    authority = "repository_live_registry" if any(term in text for term in science_terms) else "machine_index"
    audit = audit_webspace_provenance(snapshot)
    words = set(re.findall(r"[a-z0-9]+", text)) - _STOPWORDS
    relevant = [f for f in audit["findings"]
                if words & set(re.findall(r"[a-z0-9]+", (f["title"] + " " + f["evidence"]).lower()))]
    return {"authority": authority, "relevant_findings": relevant[:5], "severity_counts": audit["severity_counts"]}


def list_findings(ids: Iterable[str] | None = None) -> list[dict[str, Any]]:
    findings = audit_webspace_provenance()["findings"]
    wanted = set(ids or [])
    return [f for f in findings if not wanted or f["id"] in wanted]
