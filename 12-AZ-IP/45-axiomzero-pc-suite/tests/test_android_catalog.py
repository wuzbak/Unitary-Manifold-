# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from pathlib import Path
import re
import tomllib


def test_pentacorder_catalog_covers_every_declared_dependency_alias():
    root = Path(__file__).resolve().parents[2] / "15-pentacorder"
    catalog = tomllib.loads((root / "gradle/libs.versions.toml").read_text())
    aliases = {
        "libs." + name.replace("-", "."): value
        for name, value in catalog["libraries"].items()
    }
    aliases.update({
        "libs.plugins." + name.replace("-", "."): value
        for name, value in catalog["plugins"].items()
    })
    for build in root.rglob("build.gradle.kts"):
        if "build" in build.relative_to(root).parts:
            continue
        for match in re.findall(r"\blibs(?:\.[A-Za-z0-9_]+)+", build.read_text()):
            if match == "libs.versions.compose.compiler.get":
                assert "compose-compiler" in catalog["versions"]
            else:
                assert match in aliases, f"{build.relative_to(root)}: {match}"
    for dependency in aliases.values():
        if isinstance(dependency.get("version"), dict):
            assert dependency["version"]["ref"] in catalog["versions"]
