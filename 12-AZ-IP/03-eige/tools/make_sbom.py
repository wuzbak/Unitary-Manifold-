# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Generate ``sbom.cdx.json`` (CycloneDX 1.5) deterministically from ``requirements.lock``.

Usage (from the product directory)::

    python tools/make_sbom.py            # write sbom.cdx.json
    python tools/make_sbom.py --check    # exit 1 if the committed SBOM is stale

The output has no timestamps and a serial number derived from the lock file
hash, so the same lock always yields byte-identical output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
import uuid
from typing import Dict, List

PRODUCT = pathlib.Path(__file__).resolve().parent.parent
LOCK = PRODUCT / "requirements.lock"
SBOM = PRODUCT / "sbom.cdx.json"
EIGE_VERSION = "22.0.0"

# Packages needed only to run the test suite (CycloneDX scope "optional").
TEST_ONLY = frozenset({"pytest", "hypothesis", "iniconfig", "pluggy", "packaging", "pygments", "sortedcontainers"})

_PIN = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s\\]+)")
_HASH = re.compile(r"--hash=sha256:([0-9a-f]{64})")


def parse_lock(text: str) -> Dict[str, Dict[str, object]]:
    """Return ``{name: {"version": str, "hashes": [sha256, ...]}}`` from a pip-compile lock."""
    out: Dict[str, Dict[str, object]] = {}
    current = None
    for line in text.splitlines():
        m = _PIN.match(line)
        if m:
            current = m.group(1).lower()
            out[current] = {"version": m.group(2), "hashes": []}
            continue
        if current is not None:
            out[current]["hashes"].extend(_HASH.findall(line))  # type: ignore[union-attr]
    return out


def build_sbom(lock_text: str) -> dict:
    packages = parse_lock(lock_text)
    serial = uuid.UUID(hashlib.sha256(lock_text.encode("utf-8")).hexdigest()[:32], version=5)
    components: List[dict] = []
    for name in sorted(packages):
        info = packages[name]
        components.append({
            "type": "library",
            "bom-ref": f"pkg:pypi/{name}@{info['version']}",
            "name": name,
            "version": info["version"],
            "purl": f"pkg:pypi/{name}@{info['version']}",
            "scope": "optional" if name in TEST_ONLY else "required",
            "hashes": [{"alg": "SHA-256", "content": h} for h in sorted(info["hashes"])],
        })
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{serial}",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "bom-ref": f"eige@{EIGE_VERSION}",
                "name": "eige",
                "version": EIGE_VERSION,
                "description": "EIGE election tamper-evidence and audit-support tool",
            },
            "properties": [
                {"name": "eige:source", "value": "requirements.lock (pip-compile --generate-hashes)"},
                {"name": "eige:hash-note", "value": "hashes list every published distribution file for the pinned version"},
            ],
        },
        "components": components,
        "dependencies": [
            {"ref": f"eige@{EIGE_VERSION}", "dependsOn": [c["bom-ref"] for c in components]},
        ],
    }


def render(lock_text: str) -> str:
    return json.dumps(build_sbom(lock_text), indent=2, sort_keys=True) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if sbom.cdx.json is out of date")
    args = parser.parse_args(argv)
    expected = render(LOCK.read_text(encoding="utf-8"))
    if args.check:
        current = SBOM.read_text(encoding="utf-8") if SBOM.exists() else ""
        if current != expected:
            print("sbom.cdx.json is stale; run python tools/make_sbom.py", file=sys.stderr)
            return 1
        return 0
    SBOM.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
