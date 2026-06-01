# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 502 — Completion Master Audit.

Executable, machine-readable audit of what is already done, what is still
actionable inside repository architecture, and what remains external.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

__all__ = [
    "extract_post_number",
    "next_substack_slot",
    "latest_monograph_major_version",
    "completion_master_audit",
]

_POST_RE = re.compile(r"post-(\d+)-", flags=re.IGNORECASE)
_MONOGRAPH_VERSION_RE = re.compile(r"v(\d+)", flags=re.IGNORECASE)


def extract_post_number(filename: str) -> Optional[int]:
    """Extract a Substack post number from a filename."""
    match = _POST_RE.search(filename)
    return int(match.group(1)) if match else None


def next_substack_slot(repo_root: str | Path) -> int:
    """Return the next Substack numeric slot."""
    posts_dir = Path(repo_root) / "7-OUTREACH" / "substack" / "posts"
    numbers: List[int] = []
    if posts_dir.exists():
        for path in posts_dir.glob("*.md"):
            n = extract_post_number(path.name)
            if n is not None:
                numbers.append(n)
    return (max(numbers) + 1) if numbers else 1


def _max_version_from_names(names: List[str]) -> Optional[int]:
    versions: List[int] = []
    for name in names:
        for match in _MONOGRAPH_VERSION_RE.finditer(name):
            versions.append(int(match.group(1)))
    return max(versions) if versions else None


def latest_monograph_major_version(repo_root: str | Path) -> Optional[int]:
    """Infer latest monograph major version from filenames in 6-MONOGRAPH."""
    monograph_dir = Path(repo_root) / "6-MONOGRAPH"
    if not monograph_dir.exists():
        return None
    names = [path.name for path in monograph_dir.iterdir() if path.is_file()]
    return _max_version_from_names(names)


def _task(
    *,
    key: str,
    title: str,
    status: str,
    evidence: str,
    category: str,
) -> Dict[str, str]:
    return {
        "key": key,
        "title": title,
        "status": status,
        "evidence": evidence,
        "category": category,
    }


def _completion_fraction(tasks: List[Dict[str, str]]) -> float:
    executable = [t for t in tasks if t["category"] == "EXECUTABLE"]
    if not executable:
        return 1.0
    done = sum(1 for t in executable if t["status"] == "DONE")
    return done / len(executable)


def _completion_grade(fraction: float) -> str:
    if fraction >= 1.0:
        return "COMPLETE"
    if fraction >= 0.75:
        return "NEAR_COMPLETE"
    if fraction >= 0.5:
        return "IN_PROGRESS"
    return "EARLY"


def _path_exists(repo_root: Path, relpath: str) -> bool:
    return (repo_root / relpath).exists()


def _lean4_compiles_now() -> bool:
    # Tier-2 compilation requires running lake/Lean toolchain in CI or local;
    # this audit is static and therefore marks this as pending unless explicitly
    # upgraded by a dedicated compilation certificate.
    return False


def completion_master_audit(repo_root: str | Path = ".") -> Dict[str, object]:
    """Build a machine-readable completion snapshot for current repository state."""
    root = Path(repo_root)
    monograph_version = latest_monograph_major_version(root)
    substack_next = next_substack_slot(root)

    tasks = [
        _task(
            key="desi_dr3_contingency_architecture",
            title="DESI DR3 contingency architecture executable",
            status="DONE"
            if _path_exists(root, "src/core/pillar285_dark_energy_extension_specification.py")
            and _path_exists(root, "src/core/pillar486_desi_dr3_final_prep.py")
            else "PENDING",
            evidence="pillar285 + pillar486 modules",
            category="EXECUTABLE",
        ),
        _task(
            key="wzw_nlo_tensor_correction",
            title="WZW NLO tensor correction executable",
            status="DONE"
            if _path_exists(root, "src/core/pillar303_wzw_one_loop_r_correction.py")
            else "PENDING",
            evidence="pillar303 module",
            category="EXECUTABLE",
        ),
        _task(
            key="camb_class_bridge",
            title="CAMB/CLASS bridge implemented",
            status="DONE" if _path_exists(root, "src/core/boltzmann_bridge.py") else "PENDING",
            evidence="boltzmann_bridge.py",
            category="EXECUTABLE",
        ),
        _task(
            key="lean4_tier2_compile",
            title="Lean4 Tier-2 compilation certified",
            status="DONE" if _lean4_compiles_now() else "PENDING",
            evidence="requires explicit compile certificate",
            category="EXECUTABLE",
        ),
        _task(
            key="monograph_v15_plus",
            title="Monograph major version >= 15",
            status="DONE" if (monograph_version is not None and monograph_version >= 15) else "PENDING",
            evidence=f"detected major version: {monograph_version}",
            category="EXECUTABLE",
        ),
        _task(
            key="arxiv_submitted",
            title="arXiv submission externally verified",
            status="EXTERNAL_UNVERIFIED",
            evidence="repository can prove package readiness, not remote submission receipt",
            category="EXTERNAL",
        ),
        _task(
            key="zenodo_doi_minted",
            title="Zenodo DOI externally verified",
            status="EXTERNAL_UNVERIFIED",
            evidence="repository can track checklist, not DOI API receipt",
            category="EXTERNAL",
        ),
    ]

    fraction = _completion_fraction(tasks)
    pending_exec = [t for t in tasks if t["category"] == "EXECUTABLE" and t["status"] != "DONE"]
    pending_external = [t for t in tasks if t["category"] == "EXTERNAL" and t["status"] != "DONE"]

    blockers: List[Tuple[str, str]] = [(t["key"], t["title"]) for t in pending_exec]
    external_unknowns: List[Tuple[str, str]] = [(t["key"], t["title"]) for t in pending_external]

    return {
        "pillar": 502,
        "title": "COMPLETION_MASTER_AUDIT",
        "status_grade": _completion_grade(fraction),
        "completion_fraction_executable": fraction,
        "latest_monograph_major_version": monograph_version,
        "next_substack_slot": substack_next,
        "tasks": tasks,
        "blockers_executable": blockers,
        "external_unknowns": external_unknowns,
        "immediate_actions": [
            "Resolve Lean4 Tier-2 compilation certificate.",
            "Upgrade monograph to v15+ publication package.",
            "Attach arXiv submission receipt and Zenodo DOI receipt.",
        ],
    }

