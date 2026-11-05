# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Bounded official-publisher metadata discovery; never downloads model weights."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

AUTHOR = "HuggingFaceTB"
QUERY_URL = (
    "https://huggingface.co/api/models?author=HuggingFaceTB&search=SmolLM3"
    "&limit=100&full=true&blobs=true"
)
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 16 * 1024 * 1024
TIMEOUT_SECONDS = 15
MAX_DISCOVERY_SECONDS = 180
MIN_MODEL_BYTES = 1_000_000
MAX_MODEL_BYTES = 1_600_000_000
REPOSITORY_PATTERN = re.compile(r"HuggingFaceTB/[A-Za-z0-9][A-Za-z0-9._-]*")


class DiscoveryError(ValueError):
    """Untrusted or unavailable metadata cannot establish eligibility."""


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise DiscoveryError(f"Metadata redirect refused: HTTP {code}")


def _validate_url(url):
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.netloc != "huggingface.co"
            or parsed.fragment or parsed.username or parsed.password):
        raise DiscoveryError("Only exact HTTPS huggingface.co metadata URLs are allowed")
    if url != QUERY_URL:
        repository = parsed.path.removeprefix("/api/models/")
        if (not parsed.path.startswith("/api/models/")
                or not REPOSITORY_PATTERN.fullmatch(repository)
                or parsed.query != "blobs=true"):
            raise DiscoveryError("Only the fixed query and canonical model metadata are allowed")


def fetch_metadata(url):
    """Fetch at most one bounded response, without redirects or environment proxies."""
    _validate_url(url)
    request = Request(url, headers={"Accept": "application/json",
                                   "User-Agent": "AZ-model-metadata-discovery/1"})
    opener = build_opener(ProxyHandler({}), _NoRedirects())
    with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
        if response.status != 200 or response.geturl() != url:
            raise DiscoveryError("Unexpected metadata HTTP status or final URL")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise DiscoveryError("Metadata response exceeded byte cap")
    return raw


def _strict_json(raw):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise DiscoveryError(f"Duplicate JSON key: {key}")
            value[key] = item
        return value

    def constant(value):
        raise DiscoveryError(f"Nonfinite JSON constant: {value}")

    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            raise DiscoveryError("Nonfinite JSON number")
        return result

    if not isinstance(raw, bytes) or len(raw) > MAX_RESPONSE_BYTES:
        raise DiscoveryError("Metadata transport must return bounded bytes")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                          parse_constant=constant, parse_float=finite_float)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise DiscoveryError(f"Invalid metadata JSON: {exc}") from exc


def _complete(metadata):
    if not isinstance(metadata, dict):
        return False
    if any(key not in metadata for key in ("id", "sha", "private", "gated", "siblings")):
        return False
    card = metadata.get("cardData")
    siblings = metadata["siblings"]
    if not isinstance(card, dict) or "license" not in card or not isinstance(siblings, list):
        return False
    return all(
        isinstance(item, dict) and isinstance(item.get("rfilename"), str)
        and (not item["rfilename"].lower().endswith(".gguf")
             or isinstance(item.get("lfs"), dict)
             and all(key in item["lfs"] for key in ("sha256", "size")))
        for item in siblings
    )


def _assess(metadata, repository, source):
    reasons, unknown = [], []
    entry = {"repository": repository, "source": source, "artifacts": []}
    if not isinstance(metadata, dict):
        return dict(entry, status="unknown", reasons=["Canonical metadata is not an object"])
    if metadata.get("id") != repository:
        unknown.append("Canonical repository identity is missing or mismatched")
    revision = metadata.get("sha")
    if not isinstance(revision, str) or not re.fullmatch(r"[a-f0-9]{40}", revision):
        unknown.append("Missing or invalid 40-hex repository revision")
    for key in ("private", "gated"):
        value = metadata.get(key)
        if value is False:
            continue
        if value is True or (key == "gated" and value in ("auto", "manual")):
            reasons.append(f"Repository is {key}")
        else:
            unknown.append(f"Missing or invalid {key} metadata")
    card = metadata.get("cardData")
    license_name = card.get("license") if isinstance(card, dict) else None
    if license_name is None:
        unknown.append("Missing model-card license provenance")
    elif license_name != "apache-2.0":
        reasons.append("Model-card license is not apache-2.0")
    siblings = metadata.get("siblings")
    if not isinstance(siblings, list):
        unknown.append("Missing or invalid artifact inventory")
        siblings = []
    seen = set()
    for item in siblings:
        if not isinstance(item, dict) or not isinstance(item.get("rfilename"), str):
            unknown.append("Malformed artifact inventory entry")
            continue
        filename = item["rfilename"]
        if not filename.lower().endswith(".gguf"):
            continue
        artifact_reasons, artifact_unknown = list(reasons), list(unknown)
        if (filename.startswith("/") or "\\" in filename
                or any(part in ("", ".", "..") for part in filename.split("/"))
                or any(ord(char) < 32 for char in filename)
                or any(char in filename for char in ("?", "#", "%", ":"))):
            artifact_unknown.append("Invalid GGUF relative path")
        if filename in seen:
            artifact_unknown.append("Duplicate GGUF path")
        seen.add(filename)
        lfs = item.get("lfs")
        lfs = lfs if isinstance(lfs, dict) else {}
        digest, size = lfs.get("sha256"), lfs.get("size")
        if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
            artifact_unknown.append("Missing or invalid LFS SHA-256 provenance")
        if type(size) is not int:
            artifact_unknown.append("Missing or invalid LFS byte count")
        elif not MIN_MODEL_BYTES <= size <= MAX_MODEL_BYTES:
            artifact_reasons.append("LFS size outside 1,000,000..1,600,000,000 bytes")
        entry["artifacts"].append({
            "file": filename, "revision": revision, "sha256": digest,
            "sizeBytes": size, "license": license_name,
            "status": ("unknown" if artifact_unknown else
                       "ineligible" if artifact_reasons else "eligible"),
            "reasons": artifact_reasons + artifact_unknown,
        })
    # Inventory ambiguity must not leave an earlier artifact eligible.
    if len(seen) != len(entry["artifacts"]):
        unknown.append("Duplicate GGUF paths in inventory")
    if unknown:
        for artifact in entry["artifacts"]:
            artifact["reasons"] = list(dict.fromkeys(artifact["reasons"] + unknown))
            artifact["status"] = "unknown"
    if not entry["artifacts"]:
        (unknown if unknown else reasons).append("No GGUF artifacts established by inventory")
    statuses = {artifact["status"] for artifact in entry["artifacts"]}
    entry["status"] = ("unknown" if unknown else "ineligible" if reasons else
                       "eligible" if "eligible" in statuses else
                       "unknown" if "unknown" in statuses else "ineligible")
    entry["reasons"] = reasons + unknown
    return entry


def discover(transport=fetch_metadata):
    """Return all metadata-eligible artifacts, exclusions and unresolved provenance."""
    report = {
        "formatVersion": 1, "query": QUERY_URL, "repositories": [],
        "eligibleArtifacts": [], "errors": [], "complete": False,
        "boundary": ("Metadata eligibility only; not artifact-byte verification, "
                     "candidate selection, model quality, or installation qualification. "
                     "No model weights are downloaded."),
    }
    total_bytes = 0
    deadline = time.monotonic() + MAX_DISCOVERY_SECONDS

    def load(url):
        nonlocal total_bytes
        if time.monotonic() >= deadline or total_bytes >= MAX_TOTAL_BYTES:
            raise DiscoveryError("Discovery time or total metadata byte budget exhausted")
        _validate_url(url)
        raw = transport(url)
        if isinstance(raw, bytes):
            total_bytes += len(raw)
        if total_bytes > MAX_TOTAL_BYTES:
            raise DiscoveryError("Total metadata byte cap exceeded")
        return _strict_json(raw)

    try:
        listing = load(QUERY_URL)
        if not isinstance(listing, list) or len(listing) > 100:
            raise DiscoveryError("Expected a model list containing at most 100 repositories")
        if len(listing) == 100:
            report["errors"].append("Query reached 100-result limit; completeness is unknown")
        seen = set()
        for item in listing:
            repository = item.get("id") if isinstance(item, dict) else None
            if (not isinstance(repository, str)
                    or not REPOSITORY_PATTERN.fullmatch(repository)
                    or "smollm3" not in repository.split("/", 1)[1].lower()
                    or repository in seen):
                report["errors"].append("Invalid, duplicate, or nonofficial query repository")
                if isinstance(repository, str) and repository in seen:
                    for previous in report["repositories"]:
                        if previous["repository"] == repository:
                            previous["status"] = "unknown"
                            previous["reasons"].append("Duplicate repository identity")
                            for artifact in previous["artifacts"]:
                                artifact["status"] = "unknown"
                                artifact["reasons"].append("Duplicate repository identity")
                report["repositories"].append({
                    "repository": repository, "status": "unknown", "artifacts": [],
                    "reasons": ["Query repository identity failed fixed publisher/search scope"],
                })
                continue
            seen.add(repository)
            source = QUERY_URL
            try:
                metadata = item
                if not _complete(item):
                    source = f"https://huggingface.co/api/models/{repository}?blobs=true"
                    metadata = load(source)
                entry = _assess(metadata, repository, source)
            except (OSError, DiscoveryError) as exc:
                report["errors"].append(f"{repository}: {type(exc).__name__}: {exc}")
                entry = {"repository": repository, "source": source, "status": "unknown",
                         "artifacts": [], "reasons": ["Canonical metadata request failed"]}
            report["repositories"].append(entry)
        for entry in report["repositories"]:
            for artifact in entry["artifacts"]:
                if artifact["status"] == "eligible":
                    report["eligibleArtifacts"].append(
                        dict(artifact, repository=entry["repository"], source=entry["source"]))
        report["complete"] = not report["errors"] and all(
            entry["status"] != "unknown"
            and all(a["status"] != "unknown" for a in entry["artifacts"])
            for entry in report["repositories"]
        )
    except (OSError, DiscoveryError) as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
        report["eligibleArtifacts"] = []
    return report


def main(argv=None, *, transport=fetch_metadata):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Create a new JSON report; default: stdout")
    args = parser.parse_args(argv)
    report = discover(transport)
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    try:
        if args.output is None:
            sys.stdout.write(text)
        else:
            with args.output.open("x", encoding="utf-8") as destination:
                destination.write(text)
    except OSError as exc:
        print(f"Cannot write discovery report: {exc}", file=sys.stderr)
        return 2
    return 0 if report["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
