# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Lightweight SPDX-style SBOM generation helpers."""

from __future__ import annotations

import json
import re
from pathlib import Path


def _clean_version(raw: str) -> str:
    cleaned = raw.strip().strip('"').strip("'")
    cleaned = re.sub(r"^[^0-9]+", "", cleaned)
    return cleaned or "UNKNOWN"


def _parse_requirements(path: Path) -> list[dict]:
    packages = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)\s*[=<>!~]{1,2}\s*([^\s;#]+)", line)
        if match:
            packages.append(
                {
                    "name": match.group(1),
                    "version": _clean_version(match.group(2)),
                    "ecosystem": "pip",
                    "path": str(path),
                }
            )
    return packages


def _parse_package_json(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    packages = []
    for section in ("dependencies", "devDependencies"):
        for name, version in payload.get(section, {}).items():
            packages.append(
                {
                    "name": name,
                    "version": _clean_version(str(version)),
                    "ecosystem": "npm",
                    "path": str(path),
                }
            )
    return packages


def _parse_cargo_toml(path: Path) -> list[dict]:
    packages = []
    in_deps = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("["):
            in_deps = line == "[dependencies]"
            continue
        if not in_deps or not line or line.startswith("#") or "=" not in line:
            continue
        name, version = [part.strip() for part in line.split("=", 1)]
        if version.startswith("{"):
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', version)
            version = match.group(1) if match else "UNKNOWN"
        packages.append(
            {
                "name": name,
                "version": _clean_version(version),
                "ecosystem": "cargo",
                "path": str(path),
            }
        )
    return packages


def generate_sbom(project_path: str) -> dict:
    """Scan common manifests and emit an SPDX-lite dictionary."""
    root = Path(project_path)
    found = []
    for manifest in root.rglob("requirements.txt"):
        found.extend(_parse_requirements(manifest))
    for manifest in root.rglob("package.json"):
        found.extend(_parse_package_json(manifest))
    for manifest in root.rglob("Cargo.toml"):
        found.extend(_parse_cargo_toml(manifest))

    packages = []
    relationships = []
    doc_name = root.name or "project"
    for index, package in enumerate(found, start=1):
        spdx_id = f"SPDXRef-Package-{index}"
        packages.append(
            {
                "name": package["name"],
                "versionInfo": package["version"],
                "ecosystem": package["ecosystem"],
                "SPDXID": spdx_id,
                "path": package["path"],
            }
        )
        relationships.append(
            {
                "spdxElementId": "SPDXRef-DOCUMENT",
                "relationshipType": "DESCRIBES",
                "relatedSpdxElement": spdx_id,
            }
        )
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": doc_name,
        "documentNamespace": f"https://unitarymanifold.local/sbom/{doc_name}",
        "filesAnalyzed": False,
        "packages": packages,
        "relationships": relationships,
    }


def format_sbom_spdx(sbom: dict) -> str:
    """Render an SPDX-lite tag-value document."""
    lines = [
        f"SPDXVersion: {sbom.get('spdxVersion', 'SPDX-2.3')}",
        f"DataLicense: {sbom.get('dataLicense', 'CC0-1.0')}",
        f"SPDXID: {sbom.get('SPDXID', 'SPDXRef-DOCUMENT')}",
        f"DocumentName: {sbom.get('name', 'project')}",
        f"DocumentNamespace: {sbom.get('documentNamespace', 'https://unitarymanifold.local/sbom/project')}",
        "FilesAnalyzed: false",
    ]
    for package in sbom.get("packages", []):
        lines.extend(
            [
                "",
                f"PackageName: {package['name']}",
                f"SPDXID: {package['SPDXID']}",
                f"PackageVersion: {package['versionInfo']}",
                f"PackageSupplier: NOASSERTION ({package['ecosystem']})",
                f"PackageDownloadLocation: {package['path']}",
            ]
        )
    for rel in sbom.get("relationships", []):
        lines.append(
            f"Relationship: {rel['spdxElementId']} {rel['relationshipType']} {rel['relatedSpdxElement']}"
        )
    return "\n".join(lines)
