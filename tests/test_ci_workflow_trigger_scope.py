# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import json
import os
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _load(name: str) -> dict:
    content = (WORKFLOWS / name).read_text(encoding="utf-8")
    return yaml.safe_load(content)


def _extract_branches(workflow_name: str, event_name: str) -> list[str]:
    workflow = _load(workflow_name)
    on_block = workflow.get("on") or workflow.get(True) or {}
    return list((on_block.get(event_name, {}) or {}).get("branches", []))


def test_hosted_ci_workflows_limit_pushes_to_main_and_explicit_health_branch() -> None:
    for workflow_name in [
        "ci.yml",
        "tests.yml",
        "status-drift-gate.yml",
        "lean4-check.yml",
        "codeql-language-matrix.yml",
    ]:
        expected = ["main"]
        if workflow_name in ("lean4-check.yml", "codeql-language-matrix.yml"):
            expected.append("copilot/full-health-check-fix")
        assert _extract_branches(workflow_name, "push") == expected
        assert _extract_branches(workflow_name, "pull_request") == ["**"]


def test_psicat_performance_gate_limits_pushes_to_main() -> None:
    assert _extract_branches("psicat-performance-gate.yml", "push") == ["main"]
    assert _extract_branches("psicat-performance-gate.yml", "pull_request") == ["**"]


def test_kernel_build_tracks_canonical_sources_and_preserves_release_failures() -> None:
    workflow = _load("kernel-ci.yml")
    events = workflow.get("on") or workflow.get(True)
    for event in ("push", "pull_request"):
        assert "12-AZ-IP/02-az-kernel/**" in events[event]["paths"]
        assert "11-AZ-OS/**" in events[event]["paths"]
    assert workflow["env"]["RUSTFLAGS"] == "-D warnings"
    steps = workflow["jobs"]["build-kernel"]["steps"]
    release = next(step for step in steps if step.get("name") == "Build kernel (release)")
    assert release["run"].index("set -o pipefail") < release["run"].index("cargo build")
    assert "|| true" not in release["run"]
    dev = next(step for step in steps if step.get("name") == "Build kernel (dev)")
    assert dev["run"] == "cargo build --target x86_64-unknown-uefi"


def test_psicat_pr_smoke_jobs_include_repository_root_on_pythonpath() -> None:
    expected = "${{ github.workspace }}"
    for workflow_name, job_name in [
        ("merlin-benchmark-gate.yml", "merlin-stage-a-pr-smoke"),
        ("psicat-performance-gate.yml", "lane-e-pr-smoke"),
    ]:
        job = _load(workflow_name)["jobs"][job_name]
        assert job["defaults"]["run"]["working-directory"] == "12-AZ-IP/20-psicat-navigator"
        assert job["env"]["PYTHONPATH"] == expected


def test_android_release_publication_targets_repository_and_checksums_download_name() -> None:
    job = _load("android-suite-release.yml")["jobs"]["publish"]
    publication = next(step for step in job["steps"] if step.get("name") == "Publish the pre-release assets")
    assert publication["env"]["GH_REPO"] == "${{ github.repository }}"
    assert publication["env"]["GH_TOKEN"] == "${{ github.token }}"
    assert "gh release create" in publication["run"]
    assert "--verify-tag" in publication["run"]
    assert "build" in job["needs"]


def test_windows_installer_helper_is_checked_before_dependent_packaging() -> None:
    jobs = _load("pc-suite-windows.yml")["jobs"]
    step = next(
        step for step in jobs["browser-desktop-runtime"]["steps"]
        if "installer-kit helper" in step.get("name", "")
    )
    assert step["shell"] == "powershell"
    assert step["working-directory"] == "12-AZ-IP/45-axiomzero-pc-suite"
    assert '$env:P45_POWERSHELL = "powershell.exe"' in step["run"]
    assert "node --test tests/download-installer-kit.test.cjs" in step["run"]
    assert "throw" in step["run"]
    assert "browser-desktop-runtime" in jobs["test-and-package"]["needs"]
    assert any(step.get("run") == "npm run smoke:win" for step in jobs["test-and-package"]["steps"])


def test_android_packaging_and_release_share_mandatory_device_verification() -> None:
    build_workflow = "./.github/workflows/android-suite-build.yml"
    assert _load("pc-suite-platforms.yml")["jobs"]["android-suite"]["uses"] == build_workflow
    assert _load("android-suite-release.yml")["jobs"]["build"]["uses"] == build_workflow
    job = _load("android-suite-build.yml")["jobs"]["build"]
    steps = job["steps"]
    sdk = next(step for step in steps if step.get("name") == "Provision the Android SDK")
    assert sdk["with"]["packages"] == "platform-tools"
    native_tools = next(step for step in steps if step.get("name") == "Install the pinned Android native toolchain")
    assert '"ndk;26.1.10909125"' in native_tools["run"]
    assert '"cmake;3.22.1"' in native_tools["run"]
    emulator = next(step for step in steps if "android-emulator-runner@" in step.get("uses", ""))
    assert emulator["with"]["arch"] == "x86_64"
    assert emulator["with"]["script"] == "bash ../../.github/scripts/verify-android-suite.sh"
    script = (REPO_ROOT / ".github/scripts/verify-android-suite.sh").read_text()
    assert ":app:connectedDebugAndroidTest" in script
    assert "adb install -r app/build/outputs/apk/debug/app-debug.apk" in script
    assert "adb install -r app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk" in script
    assert "-e requireRealModel true" in script
    assert "-e modelSource app-download" in script
    assert "if" not in emulator
    assert not emulator.get("continue-on-error")
    apk = next(step for step in steps if step.get("with", {}).get("name") == "axiomzero-android-suite-debug")
    assert steps.index(emulator) < steps.index(apk)
    assert "if" not in apk


@pytest.mark.skipif(os.name != "posix" or shutil.which("bash") is None, reason="Requires the Linux-hosted Android gate")
@pytest.mark.parametrize("invalid", [None, "installation", "instrumentation", "synthetic", "import_verified", "model_bytes", "thinking_enabled", "reasoning_only", "output"])
def test_android_real_model_gate_rejects_failed_or_unqualified_receipts(tmp_path: Path, invalid: str | None) -> None:
    receipt = {
        "mode": "real-pinned-model-app-download",
        "synthetic": False,
        "inference_executed": True,
        "import_verified": True,
        "source": "app-download",
        "model_bytes": 1280835840,
        "model_sha256": "aaf42c8b7c3cab2bf3d69c355048d4a0ee9973d48f16c731c0520ee914699223",
        "context_tokens": 512,
        "generation_max_tokens": 16,
        "thinking_enabled": False,
        "output": "HELLO",  # Synthetic receipt fixture, not a native inference result.
    }
    if invalid == "synthetic":
        receipt["synthetic"] = True
    elif invalid == "import_verified":
        receipt["import_verified"] = False
    elif invalid == "model_bytes":
        receipt["model_bytes"] = 1
    elif invalid == "thinking_enabled":
        receipt["thinking_enabled"] = True
    elif invalid == "reasoning_only":
        receipt["output"] = "<think>Thinking Process: analyze the request..."
    elif invalid == "output":
        receipt["output"] = ""
    receipt_path = tmp_path / "fixture.json"
    receipt_path.write_text(json.dumps(receipt))
    (tmp_path / "gradlew").write_text("#!/usr/bin/env bash\nexit 0\n")
    (tmp_path / "gradlew").chmod(0o755)
    adb = tmp_path / "adb"
    adb.write_text(
        '#!/usr/bin/env bash\n'
        'if [[ "$1" == install && "$P46_RESULT" == INSTALL_FAILED ]]; then exit 1; fi\n'
        'if [[ "$1" == shell ]]; then printf "%s\\n" "$P46_RESULT"; '
        'else cat "$P46_RECEIPT"; fi\n'
    )
    adb.chmod(0o755)
    result = subprocess.run(
        ["bash", str(REPO_ROOT / ".github/scripts/verify-android-suite.sh")],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"],
            "P46_RECEIPT": str(receipt_path),
            "P46_RESULT": {
                "instrumentation": "FAILURES!!!", "installation": "INSTALL_FAILED"
            }.get(invalid, "OK (2 tests)"),
        },
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert (result.returncode == 0) is (invalid is None), result.stdout + result.stderr


def test_product_download_buttons_lead_to_platform_installation_guides() -> None:
    class Page(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []
            self.ids = set()

        def handle_starttag(self, tag, attrs):
            attributes = dict(attrs)
            if "id" in attributes:
                self.ids.add(attributes["id"])
            if tag == "a":
                self.links.append(attributes.get("href", ""))

    site = REPO_ROOT / "public-site"
    main = Page()
    main.feed((site / "index.html").read_text(encoding="utf-8"))
    guide = Page()
    guide.feed((site / "downloads.html").read_text(encoding="utf-8"))
    for platform in ("windows", "android"):
        assert f"downloads.html#{platform}" in main.links
        assert platform in guide.ids
    for prefix in ("pc-suite-v", "android-suite-v"):
        assert f"https://github.com/wuzbak/Unitary-Manifold-/releases?q={prefix}" in guide.links


@pytest.mark.skipif(
    not shutil.which("bash") or not shutil.which("sha256sum"),
    reason="Android release checksum step requires bash and sha256sum",
)
def test_android_release_checksum_can_be_verified_next_to_downloaded_apk(tmp_path: Path) -> None:
    job = _load("android-suite-release.yml")["jobs"]["publish"]
    checksum = next(step for step in job["steps"] if step.get("name") == "Verify and checksum the APK")
    assert checksum["working-directory"] == "release-assets"
    (tmp_path / "app-debug.apk").write_bytes(b"synthetic APK")
    subprocess.run(["bash", "-e", "-c", checksum["run"]], cwd=tmp_path, check=True)
    subprocess.run(["sha256sum", "--check", "SHA256SUMS.txt"], cwd=tmp_path, check=True)


def test_tests_workflow_restores_required_coverage_gate() -> None:
    workflow = _load("tests.yml")
    jobs = workflow["jobs"]

    coverage_job = jobs["coverage-gate"]
    coverage_step = next(
        step for step in coverage_job["steps"] if step.get("name") == "Run coverage regression gate"
    )

    assert "--cov=src" in coverage_step["run"]
    assert "--cov-fail-under=85" in coverage_step["run"]
    assert "coverage-gate" in jobs["full-regression-gate"]["needs"]


def test_ledger_consistency_installs_shared_and_navigator_requirements() -> None:
    job = _load("tests.yml")["jobs"]["ledger-consistency"]
    steps = job["steps"]
    installation = next(step for step in steps if step.get("name") == "Install dependencies")
    command = installation["run"]
    assert "python -m pip install" in command
    for requirements in (
        "requirements.txt",
        "requirements-dev.txt",
        "12-AZ-IP/20-psicat-navigator/requirements.txt",
    ):
        assert f"-r {requirements}" in command
    assert "pytest>=7.0,<9.1" in (REPO_ROOT / "requirements.txt").read_text().splitlines()
    assert "--no-deps" not in command
    assert "pytest" not in command
    assert "continue-on-error" not in job
    checks = [step for step in steps if "python -m pytest" in step.get("run", "")]
    assert len(checks) == 2
    for check in checks:
        assert steps.index(installation) < steps.index(check)
        assert "continue-on-error" not in check
        assert "--noconftest" not in check["run"]
        assert "--confcutdir" not in check["run"]
        assert "|| true" not in check["run"]


def test_full_core_evidence_runs_outside_the_agent_session() -> None:
    workflow = _load("um-arts-full-core.yml")
    job = workflow["jobs"]["full-core"]
    assert _extract_branches("um-arts-full-core.yml", "push") == [
        "main", "copilot/um-arts-*", "copilot/full-health-check-fix",
    ]
    assert _extract_branches("um-arts-full-core.yml", "pull_request") == ["**"]
    assert workflow["concurrency"]["cancel-in-progress"] is False
    assert job["steps"][0]["with"]["fetch-depth"] == 0
    assert job["timeout-minutes"] == 330
    assert "WANDB_DIR" not in job["env"]
    execution = next(step for step in job["steps"] if "Collect, execute" in step.get("name", ""))
    assert execution["env"]["WANDB_DIR"] == "${{ runner.temp }}/um-arts-wandb"
    assert 'Path(os.environ["WANDB_DIR"]).mkdir(parents=True, exist_ok=True)' in execution["run"]
    assert execution["timeout-minutes"] < job["timeout-minutes"]
    assert 'verified["status"] != "passed"' in execution["run"]
    assert 'verified["selected"] != verified["reconciled"]' in execution["run"]
    upload = job["steps"][-1]
    assert upload["if"] == "always()"
    assert upload["with"]["include-hidden-files"] is True
    assert upload["with"]["retention-days"] == 90


def test_health_branch_verification_outlives_the_cloud_agent_job() -> None:
    branch = "copilot/full-health-check-fix"
    for name in ("um-arts-full-core.yml", "lean4-check.yml", "codeql-language-matrix.yml"):
        assert branch in _extract_branches(name, "push")
    assert _load("lean4-check.yml")["jobs"]["lean4-build"]["timeout-minutes"] > 59
    assert _load("codeql-language-matrix.yml")["jobs"]["python-full"]["timeout-minutes"] > 59


@pytest.mark.parametrize("requirements", [[], ["12-AZ-IP/01-axiom-os/requirements.txt"]])
def test_product_dependencies_install_without_duplicate_wheel_cache(
    monkeypatch: pytest.MonkeyPatch, requirements: list[str],
) -> None:
    job = _load("um-arts-full-core.yml")["jobs"]["product-suite-tests"]
    setup = next(step for step in job["steps"] if "setup-python@" in step.get("uses", ""))
    assert "cache" not in setup["with"]
    installation = next(
        step for step in job["steps"]
        if step.get("name") == "Install root and package-declared test dependencies"
    )
    assert installation["env"]["PIP_NO_CACHE_DIR"] == "1"
    monkeypatch.setenv("PIP_NO_CACHE_DIR", installation["env"]["PIP_NO_CACHE_DIR"])
    monkeypatch.setenv("PRODUCT_REQUIREMENTS", json.dumps(requirements))
    calls = []

    def record_install(command, *, check):
        assert check is True
        assert os.environ["PIP_NO_CACHE_DIR"] == "1"
        calls.append(command[1:])

    monkeypatch.setattr(subprocess, "run", record_install)
    script = installation["run"].split("python - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    exec(compile(script, "<product-dependency-install>", "exec"), {})
    expected = [
        ["-m", "pip", "install", "-r", "requirements.txt", "-r", "requirements-dev.txt"]
    ]
    if requirements:
        expected.append(["-m", "pip", "install", "-r", requirements[0]])
    assert calls == expected


def test_health_setup_uses_node24_python_action_without_changing_the_runtime() -> None:
    setup = _load("copilot-setup-steps.yml")["jobs"]["copilot-setup-steps"]
    assert setup["timeout-minutes"] == 59
    assert setup["permissions"] == {"contents": "read"}
    jobs = [setup, *_load("um-arts-full-core.yml")["jobs"].values()]
    for job in jobs:
        python_steps = [
            step for step in job["steps"]
            if step.get("uses", "").startswith("actions/setup-python@")
        ]
        assert len(python_steps) == 1
        assert python_steps[0]["uses"] == "actions/setup-python@v7.0.0"
        assert python_steps[0]["with"]["python-version"] == "3.12"


def test_fast_pytest_redirects_wandb_to_external_step_runtime() -> None:
    jobs = _load("tests.yml")["jobs"]
    execution = next(
        step for job in jobs.values() for step in job.get("steps", [])
        if step.get("name", "").startswith("Run pytest (fast suite shard")
    )
    assert execution["env"]["WANDB_DIR"] == "${{ runner.temp }}/um-arts-wandb"
    assert 'mkdir -p "$WANDB_DIR"' in execution["run"]
    assert execution["run"].index('mkdir -p "$WANDB_DIR"') < execution["run"].index(
        "python TOOLS/checks/run_supervised_pytest_batch.py")


def test_full_core_config_covers_slow_tests_and_independent_suites() -> None:
    from TOOLS.um_arts.adapters import load_config

    config = load_config(
        REPO_ROOT, REPO_ROOT / "12-AZ-IP/26-um-arts/um_arts/examples/full-core-ci.json")
    assert config["pytest_args"] == ["-m", ""]
    assert config["files_per_job"] == 32
    assert config["collection_timeout_seconds"] == 900
    assert {path for suite in config["suites"] for path in suite["paths"]} == {
        "tests", "recycling", "5-GOVERNANCE/Unitary Pentad"}
    assert all(not suite["requires"] for suite in config["suites"])
    assert config["plugins"] == ["pytest_asyncio.plugin", "pytest_benchmark.plugin"]


def test_full_python_codeql_is_not_changed_surface_only() -> None:
    job = _load("codeql-language-matrix.yml")["jobs"]["python-full"]
    assert "needs" not in job and "if" not in job
    assert job["permissions"]["security-events"] == "write"
    init = next(step for step in job["steps"] if "Initialize" in step.get("name", ""))
    assert init["with"]["languages"] == "python"
    config = yaml.safe_load(init["with"]["config"])
    assert "paths" not in config
    assert config["paths-ignore"] == [".github/agents"]
    analyze = next(step for step in job["steps"] if "Analyze full" in step.get("name", ""))
    assert analyze["with"]["category"] == "/language:python/repository-wide"
    assert job["steps"][-1]["if"] == "always()"


def test_lean_cache_failures_are_captured_after_independent_checks() -> None:
    steps = _load("lean4-check.yml")["jobs"]["lean4-build"]["steps"]
    names = [step.get("name") for step in steps]
    cache = steps[names.index("Download Mathlib cache")]
    assert "|| true" not in cache["run"]
    assert "TOOLS.um_arts capture" in cache["run"]
    assert "--timeout 600" in cache["run"]
    assert names.index("Verify exporter with the pinned Lean toolchain") < names.index("Download Mathlib cache")
    assert names.index("Verify NumericalChecks compile") < names.index("Download Mathlib cache")
    assert names.index("Download Mathlib cache") < names.index("Lake build")


def test_lean_install_persists_the_repository_toolchain_pin() -> None:
    job = _load("lean4-check.yml")["jobs"]["lean4-build"]
    assert job["defaults"]["run"]["working-directory"] == "lean4"
    steps = job["steps"]
    installation = next(step for step in steps if step.get("name") == "Install elan")
    pin_command = 'echo "ELAN_TOOLCHAIN=$(cat lean-toolchain)" >> "$GITHUB_ENV"'
    assert pin_command in installation["run"]
    assert steps.index(installation) < next(
        index for index, step in enumerate(steps) if "lake " in step.get("run", "")
    )
    completed = subprocess.run(
        ["bash", "-e", "-c", pin_command],
        cwd=REPO_ROOT / "lean4",
        env={**os.environ, "GITHUB_ENV": "/dev/stdout"},
        capture_output=True,
        text=True,
        check=True,
    )
    pin = (REPO_ROOT / "lean4/lean-toolchain").read_text().strip()
    assert completed.stdout.strip() == f"ELAN_TOOLCHAIN={pin}"


@pytest.mark.parametrize(
    ("name", "command", "allows_failure"),
    [
        ("Verify NumericalChecks compile", "build UnitaryManifold.NumericalChecks", False),
        ("Download Mathlib cache", "exe cache get", True),
        ("Lake build", "build", False),
    ],
)
def test_root_lean_captures_use_the_persisted_pin(name, command, allows_failure) -> None:
    steps = _load("lean4-check.yml")["jobs"]["lean4-build"]["steps"]
    step = next(step for step in steps if step.get("name") == name)
    assert step["working-directory"] == "."
    assert step.get("continue-on-error", False) is allows_failure
    if name == "Download Mathlib cache":
        assert '--repo "$GITHUB_WORKSPACE/lean4"' in step["run"]
        assert "-- lake " + command in step["run"]
        expected_arguments = ["lake", *command.split()]
    else:
        assert "-- lake -d lean4 " + command in step["run"]
        expected_arguments = ["lake", "-d", "lean4", *command.split()]
    assert "|| true" not in step["run"]
    pin = (REPO_ROOT / "lean4/lean-toolchain").read_text().strip()
    completed = subprocess.run(
        ["bash", "-e", "-c",
         'python3() { printf "%s\\n" "$ELAN_TOOLCHAIN" "$@"; }\n' + step["run"]],
        cwd=REPO_ROOT,
        env={**os.environ, "ELAN_TOOLCHAIN": pin, "GITHUB_WORKSPACE": str(REPO_ROOT)},
        capture_output=True,
        text=True,
        check=True,
    )
    arguments = completed.stdout.splitlines()
    assert arguments[0] == pin
    assert arguments[arguments.index("--") + 1:] == expected_arguments


def test_coverage_retains_failure_evidence_without_weakening_the_gate(
    tmp_path: Path,
) -> None:
    jobs = _load("tests.yml")["jobs"]
    coverage_job = jobs["coverage-gate"]
    steps = {step.get("name"): step for step in coverage_job["steps"]}
    run = steps["Run coverage regression gate"]["run"]
    assert 'tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/"' in run
    assert "--ignore" not in run
    assert "--signal=TERM --kill-after=60s 160m" in run
    assert "-n 2 --dist loadfile" in run
    assert "pytest-xdist" in steps["Install dependencies"]["run"]
    integration = steps["Run serial non-slow coverage integration"]["run"]
    assert "--signal=TERM --kill-after=60s 10m" in integration
    assert "--cov-append" in integration
    assert "--cov-fail-under=85" in integration
    assert "-m 'not slow'" in integration
    assert "-n " not in integration
    assert "--dist" not in integration
    assert "set -o pipefail" in integration
    slow_runs = [
        step["run"]
        for step in jobs["test-slow"]["steps"]
        if "run" in step
    ]
    assert any("tests/ -m slow" in run for run in slow_runs)
    from src.core.regression_supervision_plan import INTEGRATION_PREFLIGHT_FILES

    for path in INTEGRATION_PREFLIGHT_FILES:
        assert path in integration
    assert coverage_job["timeout-minutes"] > 172
    assert "set -o pipefail" in run
    assert "tee coverage.log" in run
    partial = steps["Retain partial coverage evidence after failure"]
    assert partial["if"] == "always()"
    assert "[ -f coverage.xml ]" in partial["run"]
    assert "coverage combine --keep" in partial["run"]
    assert "--fail-under=85" in partial["run"]
    report = tmp_path / "coverage.xml"
    report.write_text("existing coverage report", encoding="utf-8")
    retained = subprocess.run(
        ["bash", "-e", "-c", partial["run"]],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "preserving the original report" in retained.stdout
    assert report.read_text(encoding="utf-8") == "existing coverage report"
    assert "|| echo" in partial["run"]
    upload = steps["Upload coverage report"]
    assert upload["if"] == "always()"
    assert upload["with"]["include-hidden-files"] is True
    for path in (
        "coverage.xml", ".coverage*", "coverage-tests.xml", "coverage.log",
        "coverage-integration.xml", "coverage-integration.log",
    ):
        assert path in upload["with"]["path"].splitlines()
    assert jobs["full-regression-gate"]["if"] == "always()"
    assert "continue-on-error" not in coverage_job
    assert all("continue-on-error" not in step for step in coverage_job["steps"])


def test_fast_supervisor_remains_fail_closed_after_failed_or_missing_receipts() -> None:
    jobs = _load("tests.yml")["jobs"]
    supervisor = jobs["test-fast-supervisor"]
    assert supervisor["if"] == "always()"
    assert supervisor["needs"] == ["regression-environment", "test-fast-batched"]
    steps = {step.get("name"): step for step in supervisor["steps"]}
    for name in (
        "Download fast-suite execution evidence",
        "Require complete matching fast-suite execution receipts",
        "Require successful fast-suite jobs",
    ):
        assert steps[name]["if"] == "always()"
    assert "--aggregate" in steps["Require complete matching fast-suite execution receipts"]["run"]
    assert 'test "${BATCH_RESULT}" = "success"' in steps["Require successful fast-suite jobs"]["run"]
    assert "test-fast-supervisor" in jobs["full-regression-gate"]["needs"]


def test_macos_smoke_uses_supported_runner_without_reducing_coverage() -> None:
    jobs = _load("ci.yml")["jobs"]
    macos = jobs["platform-smoke-macos"]
    assert macos["runs-on"] == "macos-15"
    assert macos["name"] == "Platform smoke (macos-15) [advisory]"
    assert macos["timeout-minutes"] == 30
    assert macos["continue-on-error"] is True
    assert "if" not in macos
    macos_smoke = next(
        step["run"] for step in macos["steps"]
        if step.get("name") == "Run smoke tests and compactified preflight"
    )
    ubuntu_smoke = next(
        step["run"] for step in jobs["platform-smoke"]["steps"]
        if step.get("name") == "Run smoke tests and compactified preflight"
    )
    assert macos_smoke == ubuntu_smoke


def test_main_regression_uses_frozen_cost_plan_and_serial_integration_slice() -> None:
    jobs = _load("ci.yml")["jobs"]
    batch = jobs["push-full-regression-batched"]
    assert batch["strategy"]["matrix"]["batch-index"] == list(range(13))
    assert batch["strategy"]["fail-fast"] is False
    steps = {step.get("name"): step for step in batch["steps"]}
    freeze = steps["Freeze dependency-cost regression plan"]["run"]
    run = steps["Run full regression slice"]["run"]
    assert "--batch-count 12 --workers 2 --write-plan" in freeze
    assert "--plan-file" in freeze and "--plan-file" in run
    assert "plan-${{ matrix.batch-index }}.json" in freeze
    assert "plan-${{ matrix.batch-index }}.json" in run
    assert "--timeout 5100" in run
    assert batch["timeout-minutes"] * 60 > 5100 + 600
    fast_batch = _load("tests.yml")["jobs"]["test-fast-batched"]
    assert fast_batch["timeout-minutes"] * 60 > 5100 + 600
    installation = steps["Install dependencies"]
    supervisor = jobs["push-full-regression-supervisor"]
    assert supervisor["if"].startswith("always()")
    steps = {step.get("name"): step for step in supervisor["steps"]}
    matching = steps["Install matching regression dependencies"]
    assert matching["uses"] == installation["uses"]
    assert matching["with"] == installation["with"]
    aggregate = steps["Require complete matching execution receipts"]
    assert aggregate["if"] == "always()"
    assert "--plan-file" in aggregate["run"] and "plan-0.json" in aggregate["run"]
    assert "--batch-count 12 --aggregate" in aggregate["run"]


@pytest.mark.parametrize(
    ("workflow", "batch", "supervisor"),
    [("ci.yml", "push-full-regression-batched", "push-full-regression-supervisor"),
     ("tests.yml", "test-fast-batched", "test-fast-supervisor")],
)
def test_receipt_jobs_share_one_locked_isolated_environment(workflow, batch, supervisor) -> None:
    jobs = _load(workflow)["jobs"]
    resolver = jobs["regression-environment"]
    assert resolver["uses"] == "./.github/workflows/regression-environment.yml"
    for name in (batch, supervisor):
        job = jobs[name]
        assert "regression-environment" in job["needs"]
        install = next(
            step for step in job["steps"]
            if step.get("uses") == "./.github/actions/regression-environment"
        )
        assert install["with"]["python-version"] == (
            "${{ needs.regression-environment.outputs.python-version }}"
        )
        assert all(step.get("uses") != "actions/setup-python@v5" for step in job["steps"])
        assert not any("pip install" in step.get("run", "") for step in job["steps"])


def test_regression_environment_freezes_all_packages_outside_checkout() -> None:
    resolver = _load("regression-environment.yml")
    freeze = resolver["jobs"]["freeze"]
    steps = freeze["steps"]
    command = next(step["run"] for step in steps if step.get("id") == "freeze")
    assert 'python -m venv "${RUNNER_TEMP}/regression-venv"' in command
    assert "-m pip freeze --all" in command
    assert "platform.python_version()" in command
    assert "-m pip check" in command
    artifact = next(step for step in steps if "upload-artifact" in step.get("uses", ""))
    assert artifact["with"]["name"] == "regression-environment"
    assert artifact["with"]["path"].startswith("${{ runner.temp }}/")
    assert artifact["with"]["if-no-files-found"] == "error"
    action = yaml.safe_load(
        (REPO_ROOT / ".github/actions/regression-environment/action.yml").read_text()
    )
    steps = action["runs"]["steps"]
    assert steps[0]["with"]["python-version"] == "${{ inputs.python-version }}"
    assert steps[1]["with"]["name"] == artifact["with"]["name"]
    command = steps[2]["run"]
    assert 'python -m venv "${RUNNER_TEMP}/regression-venv"' in command
    assert "-m pip check" in command
    assert "-m pip freeze --all" in command
    assert "diff -u" in command
    assert '"${GITHUB_PATH}"' in command
    assert "set -euo pipefail" in command
    assert "--system-site-packages" not in command


def test_navigator_smoke_declares_the_symbolic_bridge_dependency() -> None:
    requirements = (
        REPO_ROOT / "12-AZ-IP/20-psicat-navigator/requirements.txt"
    ).read_text().splitlines()
    assert "sympy>=1.14,<2" in requirements
    for workflow, job in (
        ("merlin-benchmark-gate.yml", "merlin-stage-a-pr-smoke"),
        ("psicat-performance-gate.yml", "lane-e-pr-smoke"),
    ):
        steps = _load(workflow)["jobs"][job]["steps"]
        assert any("pip install -r requirements.txt" in step.get("run", "") for step in steps)


@pytest.mark.parametrize(
    ("required", "result", "expected"),
    [("true", "success", 0), ("true", "skipped", 1), ("true", "failure", 1),
     ("true", "cancelled", 1), ("false", "skipped", 0), ("false", "failure", 1)],
)
def test_ci_gate_requires_main_execution_but_allows_pr_only_skips(
    tmp_path: Path, required: str, result: str, expected: int
) -> None:
    gate = _load("ci.yml")["jobs"]["ci-gate"]
    assert gate["if"] == "always()"
    step = gate["steps"][0]
    assert "github.event_name == 'push'" in step["env"]["REQUIRE_FULL_REGRESSION"]
    env = {
        **os.environ,
        "PLATFORM_SMOKE_RESULT": "success",
        "SUITE_COLLECTION_SMOKE_RESULT": "success",
        "PUSH_FULL_REGRESSION_BATCHED_RESULT": result,
        "PUSH_FULL_REGRESSION_RESULT": result,
        "REQUIRE_FULL_REGRESSION": required,
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
    }
    completed = subprocess.run(["bash", "-c", step["run"]], env=env, capture_output=True)
    assert completed.returncode == expected
