# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Content-addressed evidence, compatibility fingerprints, and SQLite index."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import VERSION


class EvidenceError(ValueError):
    """Evidence or configuration cannot support the requested operation."""


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical(value))


def read_json(path: Path) -> Any:
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"Nonfinite JSON number: {value}")

    try:
        if path.stat().st_size > 128 * 1024 * 1024:
            raise ValueError("JSON evidence exceeds the 128 MiB read limit")
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (OSError, ValueError) as exc:
        raise EvidenceError(f"Unreadable JSON evidence: {path}: {exc}") from exc


def contained(root: Path, relative: str, *, must_exist: bool = True) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise EvidenceError("Invalid relative artifact path")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise EvidenceError(f"Unsafe relative path: {relative}")
    result = root / path
    if not result.resolve().is_relative_to(root.resolve()):
        raise EvidenceError(f"Path escapes root: {relative}")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise EvidenceError(f"Symlink forbidden in evidence: {relative}")
    if must_exist and not result.is_file():
        raise EvidenceError(f"Missing regular evidence file: {relative}")
    return result


def tree_hashes(directory: Path, exclude: tuple[str, ...] = ()) -> dict[str, str]:
    entries = {}
    for current, directories, files in os.walk(directory, followlinks=False):
        for name in directories:
            if (Path(current) / name).is_symlink():
                raise EvidenceError("Artifact directory contains a symlink")
        for name in files:
            relative = (Path(current) / name).relative_to(directory).as_posix()
            if relative not in exclude:
                entries[relative] = file_hash(contained(directory, relative))
    return dict(sorted(entries.items()))


def seal(directory: Path) -> None:
    manifest = {"version": VERSION, "files": tree_hashes(directory, ("manifest.json", "seal.json"))}
    write_json(directory / "manifest.json", manifest)
    write_json(directory / "seal.json", {"sha256": digest(manifest)})


def verify_seal(directory: Path) -> dict:
    if directory.is_symlink() or not directory.is_dir():
        raise EvidenceError("Artifact root must be a regular directory")
    manifest = read_json(contained(directory, "manifest.json"))
    signature = read_json(contained(directory, "seal.json"))
    if not isinstance(manifest, dict) or not isinstance(signature, dict):
        raise EvidenceError("Manifest and seal must be JSON objects")
    if manifest.get("version") != VERSION or signature != {"sha256": digest(manifest)}:
        raise EvidenceError("Invalid manifest seal")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise EvidenceError("Empty or invalid manifest")
    for relative, expected in files.items():
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise EvidenceError("Invalid manifest hash")
        if file_hash(contained(directory, relative)) != expected:
            raise EvidenceError(f"Evidence hash mismatch: {relative}")
    actual = tree_hashes(directory, ("manifest.json", "seal.json"))
    if actual != files:
        raise EvidenceError("Missing or unexpected artifact files")
    return manifest


def fingerprints(root: Path, store: Path, config: dict) -> dict:
    """Hash source bytes, not merely commit IDs or modification timestamps."""
    excluded = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
                ".ruff_cache", ".lake", "node_modules", ".um-arts", ".um-arts-test-work"}
    sources = {}
    links = {}

    def record_link(path):
        try:
            target = path.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise EvidenceError(f"Unresolvable source symlink: {path}") from exc
        if not target.is_relative_to(root) or target.is_relative_to(store):
            raise EvidenceError(f"Source symlink target is outside source scope: {path}")
        relative = target.relative_to(root)
        if any(part in excluded for part in relative.parts) \
                or relative.as_posix().startswith(".github/agents/") \
                or relative.as_posix() == ".github/agents" \
                or target.suffix in {".pyc", ".pyo", ".olean", ".ilean"} \
                or not (target.is_file() or target.is_dir()):
            raise EvidenceError(f"Source symlink target is excluded or nonregular: {path}")
        links[path.relative_to(root).as_posix()] = {
            "target": os.readlink(path), "resolved": relative.as_posix(),
        }

    for current, directories, files in os.walk(root, followlinks=False):
        for name in directories:
            path = Path(current) / name
            if name not in excluded and path.is_symlink() \
                   and path.relative_to(root).as_posix() != ".github/agents":
                record_link(path)
        directories[:] = sorted(name for name in directories
                                if name not in excluded
                                and (Path(current) / name).relative_to(root).as_posix() != ".github/agents"
                                and not (Path(current) / name).resolve().is_relative_to(store)
                                and not (Path(current) / name).is_symlink())
        for name in sorted(files):
            path = Path(current) / name
            if path.suffix not in {".pyc", ".pyo", ".olean", ".ilean"}:
                if path.is_symlink():
                    record_link(path)
                    continue
                if path.resolve().is_relative_to(store):
                    continue
                if not path.is_file():
                    raise EvidenceError(f"Nonregular source input cannot be fingerprinted: {path}")
                sources[path.relative_to(root).as_posix()] = file_hash(path)
    engine = {p.name: file_hash(p) for p in Path(__file__).parent.glob("*.py")}
    packages = sorted({(dist.metadata.get("Name", ""), dist.version)
                       for dist in importlib.metadata.distributions()})
    environment = {
        "python": sys.version, "executable": str(Path(sys.executable).resolve()),
        "platform": platform.platform(), "packages": packages,
        "tools": {},
        "variables_digest": digest({name: value
                      for name, value in sorted(os.environ.items())
                      if not name.startswith("UM_ARTS_")
                      and name not in {"PWD", "OLDPWD", "SHLVL", "_", "PYTEST_CURRENT_TEST"}}),
    }
    for name in ["lake", "lean"]:
        command = shutil.which(name)
        resolved = Path(command).resolve() if command else None
        environment["tools"][name] = (
            {"path": command, "resolved": str(resolved), "sha256": file_hash(resolved)}
            if resolved and resolved.is_file() else None)
    git = {}
    for key, args in [("root", ["rev-parse", "--show-toplevel"]),
                      ("head", ["rev-parse", "HEAD"]), ("status", ["status", "--porcelain"]),
                      ("branch", ["rev-parse", "--abbrev-ref", "HEAD"])]:
        if key != "root" and git.get("root") != str(root):
            git[key] = None
            continue
        try:
            result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                                    text=True, timeout=15, check=False)
            git[key] = result.stdout.strip() if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            git[key] = None
    compatibility = {"source": digest({"files": sources, "links": links}), "environment": digest(environment),
                     "settings": digest(config), "engine": digest(engine), "git": digest(git)}
    return {"compatibility": compatibility, "source_files": sources, "source_links": links,
            "environment": environment, "git": git, "engine": engine,
            "source_policy": {"included": "all regular files including datasets and binaries; "
                                         "internal source aliases recorded without recursive traversal",
                              "excluded_directories": sorted(excluded),
                              "excluded_suffixes": [".pyc", ".pyo", ".olean", ".ilean"],
                              "excluded_store": str(store)}}


class Index:
    """An index is disposable; sealed artifacts remain the source of truth."""

    def __init__(self, store: Path):
        self.store = store.resolve()
        self.store.mkdir(parents=True, exist_ok=True)
        self.path = self.store / "index.sqlite3"
        if self.path.is_symlink():
            raise EvidenceError("SQLite index may not be a symlink")
        with sqlite3.connect(self.path) as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS attempts (
                    id TEXT PRIMARY KEY, path TEXT NOT NULL, compatibility TEXT NOT NULL,
                    status TEXT NOT NULL, created REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS durations (
                    compatibility TEXT NOT NULL, nodeid TEXT NOT NULL, seconds REAL NOT NULL,
                    PRIMARY KEY (compatibility, nodeid)
                );
            """)

    def record(self, attempt: Path, evaluation: dict) -> None:
        import time
        spec = read_json(attempt / ("capture.json" if (attempt / "capture.json").is_file()
                                    else "attempt.json"))
        key = digest(spec["compatibility"])
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT OR REPLACE INTO attempts VALUES (?,?,?,?,?)",
                       (spec["id"], str(attempt), key, evaluation["status"], time.time()))
            if evaluation["status"] == "passed":
                db.executemany("INSERT OR REPLACE INTO durations VALUES (?,?,?)",
                               [(self.duration_profile(spec["compatibility"]), node, duration)
                                for node, duration in evaluation["durations"].items()])

    @staticmethod
    def duration_profile(compatibility: dict) -> str:
        """Timings are scheduling hints, never reusable execution evidence."""
        return digest({"purpose": "scheduling-v1",
                       **{key: compatibility[key] for key in ["environment", "settings", "engine"]}})

    def durations(self, compatibility: dict) -> dict[str, float]:
        with sqlite3.connect(self.path) as db:
            return dict(db.execute("SELECT nodeid, seconds FROM durations WHERE compatibility=?",
                                  (self.duration_profile(compatibility),)))
