# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
from pathlib import Path
import os
import shlex
import shutil
import subprocess
import sys

import pytest

def test_um_sos_assets_present():
    root = Path(__file__).resolve().parents[1]
    for rel in ["backend/app.py", "frontend/index.html", "graph/dag.json", "registry/predictions.json", "scripts/build_graph.py", "scripts/build_registry.py"]:
        assert (root / rel).exists(), rel


@pytest.mark.skipif(shutil.which("make") is None, reason="make is unavailable")
def test_docker_target_uses_repository_context_from_another_directory(tmp_path):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["make", "--no-print-directory", "-n", "-f", str(root / "Makefile"), "docker"],
        cwd=tmp_path, check=True, capture_output=True, text=True,
    )
    arguments = shlex.split(result.stdout.strip())
    assert arguments[:4] == ["docker", "build", "-t", "um-sos"]
    assert Path(arguments[arguments.index("-f") + 1]) == root / "Dockerfile"
    assert Path(arguments[-1]) == root.parents[1]


@pytest.mark.skipif(shutil.which("make") is None, reason="make is unavailable")
def test_container_binding_and_host_publication_are_distinct():
    root = Path(__file__).resolve().parents[1]
    dockerfile = (root / "Dockerfile").read_text()
    assert "ENV UM_SOS_HOST=0.0.0.0" in dockerfile
    result = subprocess.run(
        ["make", "--no-print-directory", "-n", "-C", str(root), "docker-run"],
        check=True, capture_output=True, text=True,
    )
    assert shlex.split(result.stdout.strip()) == [
        "docker", "run", "-p", "127.0.0.1:8000:8000", "um-sos",
    ]


def test_launcher_imports_repository_from_unrelated_directory(tmp_path):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-I", "-c",
         "import runpy, sys; module = runpy.run_path(sys.argv[1]); "
         "assert module['app']; print(module['REPO_ROOT'])", str(root / "run.py")],
        cwd=tmp_path, check=True, capture_output=True, text=True,
        env={**os.environ, "UM_SOS_PREREGISTRATION_DB": str(tmp_path / "records.sqlite3")},
    )
    assert result.stdout.strip() == str(root.parents[1])
