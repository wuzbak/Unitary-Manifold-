# Copyright (C) 2026 ThomasCory Walker-Pearson
# SPDX-License-Identifier: CC0-1.0
"""Exporter structure checks and optional actual pinned-Lean environment tests.

Source checks are interface safeguards, never proof certification. Integration
tests use only locally installed core Lean libraries: no lake build, dependency
fetch, toolchain installation, or Mathlib compilation.
"""

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEAN_DIR = ROOT / "lean4"
EXPORTER = LEAN_DIR / "UMArtsExport.lean"


@pytest.fixture(scope="module")
def source():
    return EXPORTER.read_text(encoding="utf-8")


def test_executable_is_registered_without_mathlib_import(source):
    lakefile = (LEAN_DIR / "lakefile.lean").read_text(encoding="utf-8")
    assert "lean_exe um_arts_export where\n  root := `UMArtsExport" in lakefile
    assert "\nimport Lean\n" in source
    assert "import Lean.Util.CollectAxioms" in source
    assert "\nimport Mathlib" not in source
    assert (LEAN_DIR / "lean-toolchain").read_text().strip() == (
        "leanprover/lean4:v4.22.0-rc2"
    )


def test_default_build_includes_formal_library_not_only_exporter():
    lakefile = (LEAN_DIR / "lakefile.lean").read_text(encoding="utf-8")
    assert "@[default_target]\nlean_lib UnitaryManifold where" in lakefile


def test_input_requires_modules_and_exact_declarations(source):
    assert '"--module" :: value :: rest' in source
    assert '"--decl" :: value :: rest' in source
    assert "request.modules.isEmpty || request.declarations.isEmpty" in source
    assert "env.checked.get.find? name" in source
    assert "declaration not found in checked environment" in source
    assert "env.constants.toList" not in source
    assert "Regex" not in source


def test_imports_and_metadata_use_lean_environment_apis(source):
    assert "Lean.importModules imports options" in source
    assert "(trustLevel := 0) (loadExts := true)" in source
    assert "enableInitializersExecution" in source
    assert "collectAxioms info.name" in source
    assert "info.getUsedConstantsAsSet" in source
    assert "PrettyPrinter.ppExpr info.type" in source
    assert '("name", .str info.name.toString)' in source
    assert ".thmInfo _ =>" in source
    assert ".axiomInfo _ =>" in source


def test_sorry_rejected_and_axioms_distinct_from_dependencies(source):
    assert "axioms.contains ``sorryAx" in source
    assert "isTheorem && !hasSorry" in source
    assert '("axioms", namesJson axioms)' in source
    assert '("dependencies", namesJson dependencies)' in source
    assert '"depends_on_sorry"' in source
    assert "NOT an axiom-free proof" in source


def test_v1_output_deterministic_and_errors_nonzero(source):
    assert '("schema_version", toJson (1 : Nat))' in source
    assert '("lean_version", .str Lean.versionString)' in source
    assert "sortedStrings request.declarations" in source
    assert "sortedStrings request.modules" in source
    assert "sortedStrings (names.map Name.toString)" in source
    assert "document.compress" in source
    assert "(← IO.getStderr).putStrLn" in source
    assert "return 1" in source


@pytest.fixture(scope="module")
def installed_lean():
    if shutil.which("lake") is None:
        pytest.skip("lake unavailable; exporter compilation is unvalidated")
    lean = shutil.which("lean")
    if lean is None:
        pytest.skip("Lean compiler unavailable; no automatic provisioning")
    # Elan proxy invocation can download toolchains; use an existing physical
    # pinned toolchain compiler directly instead.
    if Path(lean).resolve().name == "elan":
        elan_home = Path(os.environ.get("ELAN_HOME", str(Path.home() / ".elan")))
        physical = (
            elan_home / "toolchains" / "leanprover--lean4---v4.22.0-rc2"
            / "bin" / "lean"
        )
        if not physical.is_file():
            pytest.skip("pinned Lean toolchain not installed; no auto-install")
        lean = str(physical)
    result = subprocess.run(
        [lean, "--version"], capture_output=True, text=True, check=False,
        timeout=30, cwd=LEAN_DIR,
    )
    if result.returncode != 0 or "version 4.22.0-rc2" not in result.stdout:
        pytest.skip("local Lean does not match the pinned 4.22.0-rc2 toolchain")
    return lean


@pytest.fixture(scope="module")
def lean_fixture(installed_lean):
    module = "UMArtsExporterFixture" + uuid.uuid4().hex
    source_path = LEAN_DIR / f"{module}.lean"
    olean_path = LEAN_DIR / f"{module}.olean"
    source_path.write_text(
        "import Lean\n"
        "namespace ExportFixture\n"
        "axiom assumed : True\n"
        "theorem clean : True := True.intro\n"
        "theorem conditional : True := assumed\n"
        "theorem indirect : True := conditional\n"
        "theorem unfinished : True := by sorry\n"
        "theorem indirectSorry : True := unfinished\n"
        "def value : Nat := 7\n"
        "opaque hidden : Nat := 3\n"
        "end ExportFixture\n",
        encoding="utf-8",
    )
    env = dict(os.environ)
    env["LEAN_PATH"] = str(LEAN_DIR) + os.pathsep + env.get("LEAN_PATH", "")
    try:
        prefix = subprocess.run(
            [installed_lean, "--print-prefix"], capture_output=True, text=True,
            check=True, timeout=30, cwd=LEAN_DIR,
        )
        env["LEAN_SYSROOT"] = prefix.stdout.strip()
        compiled = subprocess.run(
            [installed_lean, "-o", str(olean_path), str(source_path)],
            capture_output=True, text=True, check=False, timeout=60,
            cwd=LEAN_DIR, env=env,
        )
        assert compiled.returncode == 0, compiled.stdout + compiled.stderr
        yield installed_lean, module, env
    finally:
        source_path.unlink(missing_ok=True)
        olean_path.unlink(missing_ok=True)
        source_path.with_suffix(".ilean").unlink(missing_ok=True)


def run_export(fixture, *args):
    lean, _, env = fixture
    return subprocess.run(
        [lean, "--run", str(EXPORTER), *args],
        cwd=LEAN_DIR, env=env, capture_output=True, text=True,
        check=False, timeout=90,
    )


def test_real_export_checks_types_axioms_and_transitive_sorry(lean_fixture):
    _, module, _ = lean_fixture
    names = [
        "ExportFixture.clean", "ExportFixture.conditional",
        "ExportFixture.indirect", "ExportFixture.unfinished",
        "ExportFixture.indirectSorry", "ExportFixture.assumed",
        "ExportFixture.value", "ExportFixture.hidden",
    ]
    args = ["--module", module, "--module", "Init"]
    for name in names:
        args.extend(["--decl", name])
    result = run_export(lean_fixture, *args)
    assert result.returncode == 0, result.stdout + result.stderr
    document = json.loads(result.stdout)
    assert document["schema_version"] == 1
    assert document["lean_version"] == "4.22.0-rc2"
    assert document["modules"] == sorted([module, "Init"])
    assert [row["name"] for row in document["declarations"]] == sorted(names)
    rows = {row["name"]: row for row in document["declarations"]}
    clean = rows["ExportFixture.clean"]
    assert clean["kind"] == "theorem"
    assert clean["checked"] is True
    assert clean["axioms"] == []
    assert "True" in clean["statement"]
    for name in ("conditional", "indirect"):
        row = rows[f"ExportFixture.{name}"]
        assert row["checked"] is True
        assert row["axioms"] == ["ExportFixture.assumed"]
    assert "ExportFixture.conditional" in rows["ExportFixture.indirect"]["dependencies"]
    assert "ExportFixture.assumed" not in rows["ExportFixture.indirect"]["dependencies"]
    for name in ("unfinished", "indirectSorry"):
        row = rows[f"ExportFixture.{name}"]
        assert row["checked"] is False
        assert "sorryAx" in row["axioms"]
        assert row["proof_status"] == "depends_on_sorry"
    for name, kind in (("assumed", "axiom"), ("value", "definition"), ("hidden", "opaque")):
        row = rows[f"ExportFixture.{name}"]
        assert row["kind"] == kind
        assert row["checked"] is False
    for row in rows.values():
        assert row["axioms"] == sorted(set(row["axioms"]))
        assert row["dependencies"] == sorted(set(row["dependencies"]))
    # Reordering and duplicate requests must not change the JSON bytes.
    reversed_args = ["--module", "Init", "--module", module, "--module", module]
    for name in reversed(names):
        reversed_args.extend(["--decl", name])
    reversed_args.extend(["--decl", names[0]])
    repeated = run_export(lean_fixture, *reversed_args)
    assert repeated.returncode == 0, repeated.stdout + repeated.stderr
    assert repeated.stdout == result.stdout


@pytest.mark.parametrize("args", [
    [],
    ["--module", "Init"],
    ["--decl", "True.intro"],
    ["--module", "Init", "--decl"],
    ["--module", "Init", "--decl", "clean"],
    ["--module", "Init", "--decl", "ExportFixture.missing"],
    ["--module", "Init", "--decl", "True.intro", "--unknown"],
    ["--module", "ModuleThatDoesNotExistUMArts", "--decl", "True.intro"],
])
def test_real_export_failure_is_nonzero_without_partial_json(lean_fixture, args):
    result = run_export(lean_fixture, *args)
    assert result.returncode != 0
    assert not result.stdout.strip()
    assert result.stderr.strip()


def test_real_export_mixed_missing_declaration_is_atomic(lean_fixture):
    _, module, _ = lean_fixture
    result = run_export(
        lean_fixture, "--module", module,
        "--decl", "ExportFixture.clean", "--decl", "ExportFixture.missing",
    )
    assert result.returncode != 0
    assert not result.stdout.strip()
    assert "declaration not found" in result.stderr
