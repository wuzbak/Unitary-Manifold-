# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.regression_supervision_plan import (
    COMPACTIFIED_PREFLIGHT_FILES,
    DEFAULT_FAST_BATCH_COUNT,
    DEFAULT_FULL_CORE_BATCH_COUNT,
    FAST_MARK_EXPRESSION,
    INTEGRATION_PREFLIGHT_FILES,
    build_fast_suite_batches,
    build_dependency_cost_batches,
    build_full_core_batches,
    build_regression_supervision_plan,
    build_regression_supervision_plan_with_full_core_count,
    compactified_preflight_command,
    discover_fast_suite_files,
    discover_full_core_suite_files,
    fast_batch_command,
    full_core_batch_command,
    integration_preflight_argv,
)
import pytest


def test_discovery_returns_sorted_files() -> None:
    files = discover_fast_suite_files()
    assert files == sorted(files)
    assert 'tests/test_regression_supervision_plan.py' in files
    assert 'tests/test_richardson_multitime.py' not in files


def test_batches_cover_discovered_fast_suite_without_overlap() -> None:
    batches = build_fast_suite_batches()
    discovered = discover_fast_suite_files()
    flattened = [path for batch in batches for path in batch['test_paths']]
    assert flattened == discovered
    assert len(set(flattened)) == len(flattened)
    assert all(batch['marker_expression'] == FAST_MARK_EXPRESSION for batch in batches)


def test_full_core_discovery_includes_all_canonical_suites() -> None:
    files = discover_full_core_suite_files()
    assert 'tests/test_regression_supervision_plan.py' in files
    assert 'recycling/tests/test_recycling.py' in files
    assert '5-GOVERNANCE/Unitary Pentad/test_unitary_pentad.py' in files


def test_full_core_batches_cover_discovered_suite_without_overlap() -> None:
    batches = build_full_core_batches()
    discovered = discover_full_core_suite_files()
    flattened = [path for batch in batches for path in batch['test_paths']]
    assert flattened == discovered
    assert len(set(flattened)) == len(flattened)


def test_fast_batch_command_uses_non_slow_marker() -> None:
    command = fast_batch_command(batch_index=0, batch_count=DEFAULT_FAST_BATCH_COUNT)
    assert command.startswith("python -m pytest ")
    assert "-m 'not slow'" in command
    assert command.endswith(' -q')
    assert 'tests/' in command


def test_full_core_batch_command_overrides_default_marker() -> None:
    import shlex

    command = full_core_batch_command(batch_index=0, batch_count=DEFAULT_FULL_CORE_BATCH_COUNT)
    assert command.startswith("python -m pytest ")
    assert "not slow" not in command
    args = shlex.split(command)
    assert args[args.index("-m", 3) + 1] == ""
    assert command.endswith(' -q')


def test_fast_batch_command_omits_xdist_when_plugin_is_missing(monkeypatch) -> None:
    import src.core.regression_supervision_plan as supervision

    monkeypatch.setattr(supervision, 'pytest_xdist_available', lambda: False)

    command = supervision.fast_batch_command(batch_index=0, batch_count=DEFAULT_FAST_BATCH_COUNT)

    assert "python -m pytest -n auto" not in command
    assert "-m 'not slow'" in command


def test_full_core_batch_command_omits_xdist_when_plugin_is_missing(monkeypatch) -> None:
    import src.core.regression_supervision_plan as supervision

    monkeypatch.setattr(supervision, 'pytest_xdist_available', lambda: False)

    command = supervision.full_core_batch_command(batch_index=0, batch_count=DEFAULT_FULL_CORE_BATCH_COUNT)

    assert "python -m pytest -n auto" not in command
    assert command.startswith("python -m pytest ")


def test_fast_batch_command_returns_empty_string_for_empty_batch(tmp_path, monkeypatch) -> None:
    import src.core.regression_supervision_plan as supervision

    tests_dir = tmp_path / 'tests'
    tests_dir.mkdir()
    (tests_dir / 'test_fast.py').write_text('def test_fast():\n    assert True\n', encoding='utf-8')
    monkeypatch.setattr(supervision, '_ROOT', tmp_path)

    assert supervision.fast_batch_command(batch_index=1, batch_count=2) == ""


def test_build_fast_suite_batches_rejects_non_positive_batch_count() -> None:
    import pytest

    with pytest.raises(ValueError, match='batch_count must be positive'):
        build_fast_suite_batches(batch_count=0)


def test_compactified_preflight_files_exist_and_command_is_canonical() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    command = compactified_preflight_command()
    assert command.startswith('python -m pytest ')
    for path in COMPACTIFIED_PREFLIGHT_FILES:
        assert path in command
        assert (root / path).is_file()


def test_integration_preflight_is_serial_and_explicit_about_scope() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    command = integration_preflight_argv()
    assert "-n" not in command
    assert command[-3:] == ["-m", "", "-q"]
    assert all((root / path).is_file() for path in INTEGRATION_PREFLIGHT_FILES)
    plan = build_regression_supervision_plan()
    assert plan["integration_preflight"]["execution"] == "shared_process"
    assert "not physical-time" in plan["integration_preflight"]["scope"]


def test_supervision_reports_product_tests_outside_core(tmp_path, monkeypatch) -> None:
    import src.core.regression_supervision_plan as supervision

    product_tests = tmp_path / "12-AZ-IP" / "new-product" / "tests"
    product_tests.mkdir(parents=True)
    (product_tests / "test_product.py").write_text("def test_ok(): pass\n")
    monkeypatch.setattr(supervision, "_ROOT", tmp_path)
    plan = supervision.build_regression_supervision_plan(batch_count=1)
    assert plan["scope"]["product_test_paths_outside_full_core"] == [
        "12-AZ-IP/new-product/tests/test_product.py"
    ]
    assert plan["scope"]["file_partition_is_not_execution_evidence"] is True
    assert plan["supervised_full_core_suite"]["batches"][0]["test_paths"] == []


def test_regression_supervision_plan_reports_consistent_coverage() -> None:
    plan = build_regression_supervision_plan()
    assert plan['supervision']['evidence_scope'] == "file partitioning only; no test execution is certified"
    assert plan['supervision']['coverage_matches_discovery'] is True
    assert plan['supervision']['all_files_unique'] is True
    assert plan['supervision']['full_core_coverage_matches_discovery'] is True
    assert plan['supervision']['full_core_all_files_unique'] is True
    assert len(plan['supervised_fast_suite']['batches']) == DEFAULT_FAST_BATCH_COUNT
    assert len(plan['supervised_full_core_suite']['batches']) == DEFAULT_FULL_CORE_BATCH_COUNT
    assert plan['remaining_canonical_suites']['slow'] == 'python -m pytest tests/ -m "slow" -q'
    assert '-m ""' in plan['remaining_canonical_suites']['full']
    assert plan['remaining_canonical_suites']['claims'] == 'python -m pytest claims/ -q'


def test_regression_supervision_plan_accepts_custom_full_core_batch_count() -> None:
    plan = build_regression_supervision_plan(full_core_batch_count=3)

    assert len(plan['supervised_full_core_suite']['batches']) == 3
    assert plan['supervised_full_core_suite']['default_batch_count'] == 3


def test_regression_supervision_plan_respects_custom_full_core_batch_count() -> None:
    plan = build_regression_supervision_plan_with_full_core_count(
        batch_count=DEFAULT_FAST_BATCH_COUNT,
        full_core_batch_count=3,
    )

    assert len(plan['supervised_full_core_suite']['batches']) == 3
    assert plan['supervised_full_core_suite']['default_batch_count'] == 3


def test_regression_supervision_plan_omits_claims_when_directory_is_missing(tmp_path, monkeypatch) -> None:
    import src.core.regression_supervision_plan as supervision

    tests_dir = tmp_path / 'tests'
    tests_dir.mkdir()
    (tests_dir / 'test_fast.py').write_text('def test_fast():\n    assert True\n', encoding='utf-8')
    monkeypatch.setattr(supervision, '_ROOT', tmp_path)

    plan = supervision.build_regression_supervision_plan(batch_count=1)

    assert 'claims' not in plan['remaining_canonical_suites']


def test_discovery_keeps_syntax_error_files_in_fast_suite(tmp_path, monkeypatch) -> None:
    import src.core.regression_supervision_plan as supervision

    tests_dir = tmp_path / 'tests'
    tests_dir.mkdir()
    broken = tests_dir / 'test_broken.py'
    broken.write_text('def test_broken(:\n    pass\n', encoding='utf-8')
    monkeypatch.setattr(supervision, '_ROOT', tmp_path)

    assert supervision.discover_fast_suite_files() == ['tests/test_broken.py']


def test_full_core_override_collects_slow_tests(tmp_path, monkeypatch) -> None:
    import subprocess
    import sys

    import src.core.regression_supervision_plan as supervision

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tmp_path / "pytest.ini").write_text(
        '[pytest]\naddopts = -m "not slow"\nmarkers =\n    slow: slow test\n',
        encoding="utf-8",
    )
    (tests_dir / "test_scope.py").write_text(
        "import pytest\n"
        "def test_fast():\n    pass\n"
        "@pytest.mark.slow\n"
        "def test_slow():\n    pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(supervision, "_ROOT", tmp_path)
    monkeypatch.setattr(supervision, "pytest_xdist_available", lambda: False)
    command = supervision.full_core_batch_argv(0, 1)
    command[0] = sys.executable
    result = subprocess.run(
        [*command, "--collect-only"], cwd=tmp_path, capture_output=True, text=True,
        timeout=30, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "test_scope.py::test_slow" in result.stdout
    assert "2 tests collected" in result.stdout


def test_discovery_matches_special_pytest_filename_pattern(tmp_path, monkeypatch) -> None:
    import src.core.regression_supervision_plan as supervision

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "ALGEBRA_PROOF.py").write_text("def test_ok(): pass\n")
    monkeypatch.setattr(supervision, "_ROOT", tmp_path)
    assert supervision.discover_fast_suite_files() == ["tests/ALGEBRA_PROOF.py"]
    assert supervision.discover_full_core_suite_files() == ["tests/ALGEBRA_PROOF.py"]


def test_full_core_batch_collects_slow_tests_despite_default_addopts(tmp_path, monkeypatch) -> None:
    import subprocess
    import sys
    import src.core.regression_supervision_plan as supervision

    (tmp_path / 'pytest.ini').write_text(
        '[pytest]\naddopts = -m "not slow"\nmarkers = slow: slow tests\n',
        encoding='utf-8',
    )
    tests_dir = tmp_path / 'tests'
    tests_dir.mkdir()
    (tests_dir / 'test_modes.py').write_text(
        'import pytest\n'
        'def test_fast(): pass\n'
        '@pytest.mark.slow\n'
        'def test_slow(): pass\n',
        encoding='utf-8',
    )
    monkeypatch.setattr(supervision, '_ROOT', tmp_path)
    monkeypatch.setattr(supervision, 'pytest_xdist_available', lambda: False)
    command = supervision.full_core_batch_argv(0, 1)
    command[0] = sys.executable
    result = subprocess.run(
        [*command, '--collect-only'], cwd=tmp_path, capture_output=True, text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'test_modes.py::test_slow' in result.stdout
    assert '2 tests collected' in result.stdout


@pytest.fixture
def dependency_suite(tmp_path, monkeypatch):
    import src.core.regression_supervision_plan as supervision

    monkeypatch.setattr(supervision, "_ROOT", tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "core").mkdir(parents=True)

    def write(path, content=""):
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        return path

    return write


def test_dependency_cost_batches_are_order_independent(dependency_suite):
    write = dependency_suite
    write("src/core/expensive.py")
    files = [
        write("tests/test_a.py", "from src.core.expensive import value\n"),
        write("tests/test_b.py", "import src.core.expensive\n"),
        write("tests/test_c.py"),
        write("tests/test_d.py"),
    ]
    durations = dict(zip(files, [8.0, 7.0, 10.0, 5.0]))
    batches = build_dependency_cost_batches(files, 2, durations)
    assert batches == build_dependency_cost_batches(
        files[::-1], 2, dict(reversed(list(durations.items()))),
    )
    assert [batch["estimated_seconds"] for batch in batches] == [15.0, 15.0]
    assert any(batch["test_paths"] == files[:2] for batch in batches)
    assert sorted(path for batch in batches for path in batch["test_paths"]) == files
    assert all(batch["test_paths"] == sorted(batch["test_paths"]) for batch in batches)


def test_dependency_cost_batches_keep_static_costly_chain_together(dependency_suite):
    write = dependency_suite
    readiness = "pillar952_observational_readiness_v4"
    registry = "pillar982_architecture_limit_registry_runtime"
    write(f"src/core/{readiness}.py", "from .metric import Metric\nraise RuntimeError('never run')\n")
    write(f"src/core/{registry}.py", f"from .{readiness} import OPEN_LANES\n")
    write("src/core/metric.py", "import numpy\nraise RuntimeError('never run')\n")
    a = write("tests/test_a.py", f"import src.core.{readiness}\nraise RuntimeError('never run')\n")
    b = write("tests/test_b.py", f"from src.core import {registry}\n")
    c = write("tests/test_c.py", "from src.core.metric import Metric\n")
    batches = build_dependency_cost_batches([c, b, a], 3, {a: 12.0, b: 12.0})
    assert batches[0]["test_paths"] == [a, b]
    assert batches[0]["estimated_seconds"] == 24.0
    assert batches[0]["dependency_groups"][0]["dependency_root"] == f"src.core.{readiness}"
    assert batches[1]["test_paths"] == [c]
    assert batches[2]["test_paths"] == []
    assert batches[1]["estimated_seconds"] == 1.0


def test_dependency_cost_batches_do_not_import_or_read_agents(dependency_suite, monkeypatch):
    import builtins

    write = dependency_suite
    write("src/core/expensive.py", "raise RuntimeError('source executed')\n")
    write(".github/agents/private.py", "raise RuntimeError('agent executed')\n")
    files = [
        write("tests/test_a.py", "import src.core.expensive\nimport private\n"),
        write("tests/test_b.py", "from src.core.expensive import value\n"),
    ]
    original_import = builtins.__import__
    def guarded_import(name, *args, **kwargs):
        assert not name.startswith("src.core") and name != "private"
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", guarded_import)
    from pathlib import Path
    original_read = Path.read_bytes
    def guarded_read(path):
        assert ".github" not in path.parts
        return original_read(path)
    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    batches = build_dependency_cost_batches(files, 2)
    assert batches[0]["test_paths"] == files


def test_dependency_cost_batches_balance_unrelated_measured_files(dependency_suite):
    files = [dependency_suite(f"tests/test_{index}.py") for index in range(4)]
    batches = build_dependency_cost_batches(files, 2, dict(zip(files, [8, 7, 6, 5])))
    assert [batch["estimated_seconds"] for batch in batches] == [13, 13]
    assert all(batch["file_count"] == 2 for batch in batches)


def test_dependency_cost_batches_generic_hubs_do_not_join_families(dependency_suite):
    write = dependency_suite
    write("src/core/metric.py")
    write("src/core/alpha.py", "from src.core.metric import Metric\n")
    write("src/core/beta.py", "from src.core.metric import Metric\n")
    files = [
        write(f"tests/test_{name}{index}.py", f"from src.core.{name} import value\n")
        for name in ("alpha", "beta") for index in range(2)
    ]
    batches = build_dependency_cost_batches(files, 2)
    assert [batch["test_paths"] for batch in batches] == [files[:2], files[2:]]


def test_dependency_cost_batches_choose_one_strongest_family_not_union(dependency_suite):
    write = dependency_suite
    write("src/core/alpha.py")
    write("src/core/beta.py")
    a = write("tests/test_a.py", "import src.core.alpha\n")
    b = write("tests/test_b.py", "import src.core.alpha\nimport src.core.beta\n")
    c = write("tests/test_c.py", "import src.core.beta\n")
    batches = build_dependency_cost_batches([a, b, c], 2, {a: 8, b: 2, c: 1})
    assert batches[0]["test_paths"] == [a, b]
    assert batches[1]["test_paths"] == [c]


def test_dependency_cost_batches_follow_package_imports_and_cycles(dependency_suite):
    write = dependency_suite
    write("src/core/family/__init__.py", "from .heavy import value\n")
    write("src/core/family/heavy.py", "from ..family import value\n")
    files = [
        write("tests/test_a.py", "from src.core.family import value\n"),
        write("tests/test_b.py", "from src.core.family.heavy import value\n"),
    ]
    batches = build_dependency_cost_batches(files, 2)
    assert batches[0]["test_paths"] == files


def test_dependency_cost_batches_report_static_bounds_and_syntax_errors(dependency_suite):
    write = dependency_suite
    for index in range(10):
        write(f"src/core/chain{index}.py", f"import src.core.chain{index + 1}\n")
    a = write("tests/test_a.py", "import src.core.chain0\n")
    b = write("tests/test_b.py", "def test_broken(:\n")
    batches = build_dependency_cost_batches([a, b], 1)
    assert batches[0]["test_paths"] == [a, b]
    assert batches[0]["assumptions"]["unparsed_paths"] == [b]
    assert batches[0]["assumptions"]["truncated_test_paths"] == [a]


def test_dependency_cost_batches_use_fresh_new_and_deleted_files(dependency_suite):
    import src.core.regression_supervision_plan as supervision

    write = dependency_suite
    old = write("tests/test_old.py")
    assert build_dependency_cost_batches(supervision.discover_fast_suite_files(), 1)[0]["test_paths"] == [old]
    (supervision._ROOT / old).unlink()
    new = write("tests/test_new.py")
    batches = build_dependency_cost_batches(supervision.discover_fast_suite_files(), 1, {old: 9})
    assert batches[0]["test_paths"] == [new]
    assert batches[0]["estimated_seconds"] == 1
    with pytest.raises(ValueError, match="does not exist"):
        build_dependency_cost_batches([old], 1)


@pytest.mark.parametrize("count", [0, -1, True, 2.5, "2", None])
def test_dependency_cost_batches_reject_invalid_batch_count(count):
    with pytest.raises(ValueError, match="batch_count"):
        build_dependency_cost_batches([], count)


@pytest.mark.parametrize("duration", [0, -1, float("nan"), float("inf"), float("-inf"), True, "1", None])
def test_dependency_cost_batches_reject_invalid_durations(dependency_suite, duration):
    path = dependency_suite("tests/test_a.py")
    with pytest.raises(ValueError, match="positive and finite"):
        build_dependency_cost_batches([path], 1, {path: duration})


@pytest.mark.parametrize("path", ["../outside.py", "/absolute.py", "tests/../test_a.py",
                                 "./tests/test_a.py", "tests//test_a.py", "tests\\test_a.py",
                                 ".github/agents/example.py", "tests/test_a.txt", ""])
def test_dependency_cost_batches_reject_invalid_paths(path):
    with pytest.raises(ValueError, match="path"):
        build_dependency_cost_batches([path], 1)
    with pytest.raises(ValueError, match="path"):
        build_dependency_cost_batches([], 1, {path: 1})


def test_dependency_cost_batches_reject_duplicate_paths(dependency_suite):
    path = dependency_suite("tests/test_a.py")
    with pytest.raises(ValueError, match="unique"):
        build_dependency_cost_batches([path, path], 1)


def test_dependency_cost_batches_reject_overflowing_total_cost(dependency_suite):
    files = [dependency_suite(f"tests/test_{index}.py") for index in range(2)]
    with pytest.raises(ValueError, match="total estimated duration"):
        build_dependency_cost_batches(files, 1, dict.fromkeys(files, 1e308))


def test_dependency_cost_batches_reject_symlink_escape(dependency_suite):
    import src.core.regression_supervision_plan as supervision

    root = supervision._ROOT
    link = root / "tests" / "test_escape.py"
    link.symlink_to(root.parent / "outside.py")
    with pytest.raises(ValueError, match="escapes repository"):
        build_dependency_cost_batches(["tests/test_escape.py"], 1)


def test_dependency_cost_batches_do_not_cache_source_changes(dependency_suite):
    write = dependency_suite
    write("src/core/alpha.py")
    files = [
        write("tests/test_a.py", "import src.core.alpha\n"),
        write("tests/test_b.py", "import src.core.alpha\n"),
    ]
    assert build_dependency_cost_batches(files, 2)[0]["test_paths"] == files
    write("tests/test_b.py")
    assert [batch["file_count"] for batch in build_dependency_cost_batches(files, 2)] == [1, 1]


def test_dependency_cost_batches_empty_and_sparse_batches(dependency_suite):
    assert len(build_dependency_cost_batches([], 3)) == 3
    path = dependency_suite("tests/test_a.py")
    batches = build_dependency_cost_batches([path], 3)
    assert [batch["file_count"] for batch in batches] == [1, 0, 0]
    assert [batch["estimated_seconds"] for batch in batches] == [1, 0, 0]
