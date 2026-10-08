# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Verify checkout, editable, and wheel installs expose the physics packages."""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path
from zipfile import ZipFile

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULES = ("core.metric", "holography.boundary", "multiverse.fixed_point")


def run(*args, cwd, env=None):
    result = subprocess.run(
        [sys.executable, *args], cwd=cwd, env=env,
        text=True, capture_output=True, timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


@pytest.fixture(scope="module")
def artifacts(tmp_path_factory):
    pytest.importorskip("setuptools")
    pytest.importorskip("wheel")
    root = tmp_path_factory.mktemp("packaging")
    scratch = root / "scratch"
    scratch.mkdir()
    env = dict(os.environ, TMPDIR=str(scratch), TEMP=str(scratch), TMP=str(scratch))
    wheel_dir = root / "wheels"
    run(
        "-m", "pip", "wheel", str(REPO_ROOT), "--no-deps",
        "--no-build-isolation", "--wheel-dir", str(wheel_dir),
        "--disable-pip-version-check", cwd=root, env=env,
    )
    return root, env, next(wheel_dir.glob("unitary_manifold-*.whl"))


def smoke_imports(target, expected_root, version):
    # -I excludes PYTHONPATH and the checkout; editable .pth files are loaded
    # explicitly, just as they would be in an installation's site-packages.
    run(
        "-I", "-c",
        "import importlib, importlib.metadata, pathlib, site, sys\n"
        "site.addsitedir(sys.argv[1])\n"
        "expected = pathlib.Path(sys.argv[2]).resolve()\n"
        "import unitary_manifold\n"
        "assert unitary_manifold.__version__ == sys.argv[3]\n"
        "assert importlib.metadata.version('unitary-manifold') == sys.argv[3]\n"
        f"for suffix in {MODULES!r}:\n"
        "    for prefix in ('unitary_manifold', 'src'):\n"
        "        module = importlib.import_module(prefix + '.' + suffix)\n"
        "        assert pathlib.Path(module.__file__).resolve().is_relative_to(expected), module.__file__\n"
        "from unitary_manifold.data_feeds import snapshot\n"
        "assert snapshot.load('noaa_co2')\n",
        str(target), str(expected_root), version, cwd=REPO_ROOT.parent,
    )


def test_checkout_namespace_and_version():
    metadata = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    run(
        "-I", "-c",
        "import importlib, pathlib, sys\n"
        "sys.path.insert(0, sys.argv[1])\n"
        "import unitary_manifold\n"
        "assert unitary_manifold.__version__ == sys.argv[2]\n"
        f"for suffix in {MODULES!r}:\n"
        "    public = importlib.import_module('unitary_manifold.' + suffix)\n"
        "    legacy = importlib.import_module('src.' + suffix)\n"
        "    assert pathlib.Path(public.__file__) == pathlib.Path(legacy.__file__)\n",
        str(REPO_ROOT), metadata["project"]["version"], cwd=REPO_ROOT.parent,
    )


@pytest.mark.slow
def test_wheel_contains_source_and_runtime_data(artifacts):
    _, _, wheel = artifacts
    with ZipFile(wheel) as archive:
        names = set(archive.namelist())
        assert "unitary_manifold/__init__.py" in names
        assert "src/__init__.py" in names
        for suffix in MODULES:
            assert f"src/{suffix.replace('.', '/')}.py" in names
        assert "src/data_feeds/latest_snapshot.json" in names
        assert not any("__pycache__" in name for name in names)


@pytest.mark.parametrize("editable", [False, True], ids=["wheel", "editable"])
@pytest.mark.slow
def test_install_imports_outside_checkout(artifacts, editable):
    root, env, wheel = artifacts
    target = root / ("editable" if editable else "installed")
    source = ["--editable", str(REPO_ROOT)] if editable else [str(wheel)]
    run(
        "-m", "pip", "install", *source, "--no-deps", "--no-build-isolation",
        "--target", str(target), "--disable-pip-version-check", cwd=root, env=env,
    )
    metadata = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    smoke_imports(target, REPO_ROOT if editable else target, metadata["project"]["version"])
