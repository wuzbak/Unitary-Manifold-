# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Workflow entrypoint for supervised pytest batching."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import shlex
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from importlib import metadata, util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if ROOT.as_posix() not in sys.path:
    sys.path.insert(0, ROOT.as_posix())

from src.core.regression_supervision_plan import (
    DEFAULT_FAST_BATCH_COUNT,
    DEFAULT_FULL_CORE_BATCH_COUNT,
    build_regression_supervision_plan_with_full_core_count,
    build_dependency_cost_batches,
    compactified_preflight_argv,
    fast_batch_argv,
    full_core_batch_argv,
    integration_preflight_argv,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--suite",
        choices=(
            "tests-fast",
            "compactified-preflight",
            "integration-preflight",
            "supervisor-check",
            "full-core",
            "full-core-supervisor-check",
        ),
        required=True,
    )
    parser.add_argument("--batch-count", type=int)
    parser.add_argument("--batch-index", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--emit-json", action="store_true")
    parser.add_argument("--result-dir", type=Path)
    parser.add_argument("--aggregate", action="store_true")
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--plan-file", type=Path)
    parser.add_argument("--write-plan", action="store_true")
    parser.add_argument("--durations-file", type=Path)
    parser.add_argument("--timings-dir", type=Path)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def _run(args: list[str], dry_run: bool, timeout: float | None = None,
         env: dict[str, str] | None = None) -> int:
    print(shlex.join(args), file=sys.stderr)
    if dry_run:
        return 0
    options = {"cwd": ROOT}
    if env is not None:
        options["env"] = env
    if timeout is None:
        return subprocess.run(args, check=False, **options).returncode
    # A new Linux session lets us terminate xdist workers as well as pytest.
    with subprocess.Popen(args, start_new_session=True, **options) as process:
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return 124


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _snapshot() -> dict:
    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", *args], cwd=ROOT)

    digest = hashlib.sha256(git("diff", "--binary", "HEAD", "--"))
    for name in sorted(git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0")):
        if not name:
            continue
        path = ROOT / os.fsdecode(name)
        content = os.fsencode(os.readlink(path)) if path.is_symlink() else path.read_bytes()
        digest.update(len(name).to_bytes(8, "big") + name)
        digest.update(len(content).to_bytes(8, "big") + content)
    return {"head": git("rev-parse", "HEAD").decode().strip(), "worktree_digest": digest.hexdigest()}


def _environment_fingerprint() -> dict:
    distributions = []
    for distribution in metadata.distributions():
        name = distribution.metadata.get("Name")
        version = distribution.version
        if not isinstance(name, str) or not name or not isinstance(version, str) or not version:
            raise ValueError("installed distribution lacks a name/version")
        distributions.append((name.casefold().replace("_", "-").replace(".", "-"), version))
    return {
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "distributions_digest": _digest(sorted(distributions)),
    }


def _execution_settings() -> dict:
    names = (
        "PYTHONPATH", "PYTHONOPTIMIZE", "PYTHONHASHSEED", "PYTEST_PLUGINS", "PYTEST_DISABLE_PLUGIN_AUTOLOAD",
        "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
        "NUMEXPR_NUM_THREADS", "MERLIN_TRAINING_RUNTIME_DIR",
    )
    return {"python": sys.executable, "environment": {name: os.environ.get(name) for name in names}}


def _junit(path: Path) -> tuple[dict, str]:
    content = path.read_bytes()
    if b"<!DOCTYPE" in content or b"<!ENTITY" in content:
        raise ValueError("JUnit declarations are not permitted")
    root = ET.fromstring(content)
    if root.tag not in {"testsuites", "testsuite"}:
        raise ValueError("invalid JUnit root")
    suites = list(root.iter("testsuite"))
    leaves = [suite for suite in suites if not suite.findall("testsuite")]
    if not leaves:
        raise ValueError("JUnit has no test suites")
    totals = dict.fromkeys(("tests", "failures", "errors", "skipped"), 0)
    for suite in leaves:
        counts = {key: int(suite.attrib[key]) for key in totals}
        cases = suite.findall("testcase")
        actual = {
            "tests": len(cases),
            "failures": sum(case.find("failure") is not None for case in cases),
            "errors": sum(case.find("error") is not None for case in cases),
            "skipped": sum(case.find("skipped") is not None for case in cases),
        }
        if counts != actual or any(value < 0 for value in counts.values()):
            raise ValueError("JUnit counts do not match test cases")
        for key in totals:
            totals[key] += counts[key]
    return totals, hashlib.sha256(content).hexdigest()


def _write_receipt(path: Path, receipt: dict) -> None:
    pending = path.with_suffix(".json.pending")
    pending.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    pending.replace(path)


def _verified_batch(result_dir: Path, suite: str, batches: list[dict],
                    index: int, identity: dict, environment: dict | None = None) -> dict:
    receipt = json.loads((result_dir / f"{suite}-{index}.json").read_text())
    expected = {**identity, "suite": suite, "batch_index": index, "batch_count": len(batches)}
    if not isinstance(receipt, dict) or any(receipt.get(key) != value for key, value in expected.items()):
        raise ValueError("stale or mismatched receipt")
    if receipt.get("status") == "empty":
        if batches[index]["test_paths"] or receipt.get("exit_code") != 0 or receipt.get("counts") != dict.fromkeys(
            ("tests", "failures", "errors", "skipped"), 0
        ):
            raise ValueError("invalid empty batch")
        return receipt
    if receipt.get("status") != "success" or receipt.get("exit_code") != 0:
        raise ValueError("batch did not complete successfully")
    if environment is not None and receipt.get("environment_fingerprint") != environment:
        raise ValueError("execution environment changed")
    counts, digest = _junit(result_dir / f"{suite}-{index}.xml")
    if counts != receipt.get("counts") or digest != receipt.get("junit_sha256"):
        raise ValueError("corrupt or mismatched JUnit")
    if counts["tests"] == 0 or counts["failures"] or counts["errors"]:
        raise ValueError("JUnit does not show a successful nonempty batch")
    if "execution_digest" in identity:
        command = _frozen_command(batches[index], identity["workers"])
        command = [*command, f"--junitxml={result_dir / f'{suite}-{index}.xml'}"]
        if receipt.get("command") != command:
            raise ValueError("execution command changed")
    return receipt


def _frozen_command(batch: dict, workers: int) -> list[str]:
    if not batch["test_paths"]:
        return []
    command = [sys.executable, "-m", "pytest"]
    if workers and not batch.get("integration"):
        command.extend(["-n", str(workers)])
    return [*command, "-m", "", *batch["test_paths"], "-q"]


def _measured_durations(directory: Path, files: list[str]) -> tuple[dict, list]:
    """Use validated historical receipts for scheduling, never as current proof."""
    allowed = set(files)
    observations: dict[str, list[float]] = {}
    provenance = []
    for path in sorted(directory.glob("full-core-*.json")):
        receipt = json.loads(path.read_text())
        if (not isinstance(receipt, dict) or type(receipt.get("batch_index")) is not int
                or receipt.get("status") != "success" or receipt.get("exit_code") != 0):
            continue
        xml_path = path.with_suffix(".xml")
        counts, digest = _junit(xml_path)
        if counts != receipt.get("counts") or digest != receipt.get("junit_sha256"):
            raise ValueError(f"timing receipt has corrupt JUnit: {path.name}")
        command = receipt.get("command")
        if not isinstance(command, list) or any(not isinstance(arg, str) for arg in command):
            raise ValueError("invalid timing command")
        paths = [arg for arg in command if arg in allowed]
        if not paths:
            continue
        durations = dict.fromkeys(paths, 0.0)
        matched = set()
        for case in ET.parse(xml_path).getroot().iter("testcase"):
            seconds = float(case.get("time", "0"))
            if not math.isfinite(seconds) or seconds < 0:
                raise ValueError("invalid JUnit duration")
            classname = case.get("classname", "")
            matches = [
                p for p in paths if case.get("file") == p
                or classname == p[:-3].replace("/", ".")
                or classname.startswith(p[:-3].replace("/", ".") + ".")
            ]
            if len(matches) == 1:
                durations[matches[0]] += seconds
                matched.add(matches[0])
        elapsed = receipt.get("elapsed_seconds")
        if elapsed is not None and (isinstance(elapsed, bool) or not isinstance(elapsed, (int, float))
                                    or not math.isfinite(elapsed) or elapsed < 0):
            raise ValueError("invalid receipt elapsed duration")
        overhead = max(0.0, (elapsed or 0.0) - sum(durations.values())) / len(paths)
        for p, duration in durations.items():
            if p in matched:
                observations.setdefault(p, []).append(max(0.001, duration + overhead))
        provenance.append({"receipt": path.name, "receipt_digest": _digest(receipt),
                           "junit_sha256": digest, "snapshot": receipt.get("snapshot")})
    return {p: max(values) for p, values in observations.items()}, provenance


def _load_frozen_plan(path: Path, snapshot: dict, environment: dict) -> dict:
    plan = json.loads(path.read_text())
    if not isinstance(plan, dict) or plan.get("schema") != "supervised-plan-v1":
        raise ValueError("invalid frozen plan schema")
    if plan.get("snapshot") != snapshot or plan.get("environment") != environment:
        raise ValueError("frozen source snapshot or environment changed; create a new plan")
    if plan.get("execution_settings") != _execution_settings():
        raise ValueError("frozen interpreter or execution settings changed")
    workers = plan.get("workers")
    if type(workers) is not int or workers < 0:
        raise ValueError("invalid frozen worker count")
    batches = plan.get("batches")
    if not isinstance(batches, list) or not batches:
        raise ValueError("frozen plan has no batches")
    for index, batch in enumerate(batches):
        if not isinstance(batch, dict) or batch.get("batch_index") != index or not isinstance(batch.get("test_paths"), list):
            raise ValueError("invalid frozen batch")
        if any(not isinstance(p, str) or Path(p).is_absolute() or ".." in Path(p).parts for p in batch["test_paths"]):
            raise ValueError("invalid frozen test path")
    if not batches[-1].get("integration") or batches[-1]["test_paths"] != integration_preflight_argv()[3:-3]:
        raise ValueError("frozen plan must include canonical shared-process integration")
    if any(batch.get("integration") for batch in batches[:-1]):
        raise ValueError("integration must be the final batch")
    discovered = build_regression_supervision_plan_with_full_core_count()["supervised_full_core_suite"]["batches"]
    expected = sorted(p for batch in discovered for p in batch["test_paths"])
    actual = sorted(p for batch in batches[:-1] for p in batch["test_paths"])
    if actual != expected or len(actual) != len(set(actual)):
        raise ValueError("frozen plan does not exactly cover full-core discovery")
    payload = {key: value for key, value in plan.items() if key != "digest"}
    if plan.get("digest") != _digest(payload):
        raise ValueError("frozen plan digest mismatch")
    return plan


def _aggregate(result_dir: Path, suite: str, batches: list[dict], identity: dict) -> int:
    totals = dict.fromkeys(("tests", "failures", "errors", "skipped"), 0)
    problems = []
    environment = None
    for index, batch in enumerate(batches):
        try:
            if "execution_digest" in identity:
                _verified_batch(result_dir, suite, batches, index, identity, identity["frozen_environment"])
            receipt = json.loads((result_dir / f"{suite}-{index}.json").read_text())
            if not isinstance(receipt, dict):
                raise ValueError("receipt must be a JSON object")
            expected = {**identity, "suite": suite, "batch_index": index, "batch_count": len(batches)}
            if any(receipt.get(key) != value for key, value in expected.items()):
                raise ValueError("stale or mismatched receipt")
            if receipt.get("status") == "empty":
                if batch["test_paths"] or receipt.get("exit_code") != 0 or receipt.get("counts") != dict.fromkeys(totals, 0):
                    raise ValueError("invalid empty batch")
                continue
            if not batch["test_paths"] or receipt.get("status") != "success" or receipt.get("exit_code") != 0:
                raise ValueError("batch did not complete successfully")
            fingerprint = receipt.get("environment_fingerprint")
            keys = {"python_implementation", "python_version", "platform_system",
                    "platform_machine", "distributions_digest"}
            if not isinstance(fingerprint, dict) or set(fingerprint) != keys or not all(
                isinstance(value, str) and value for value in fingerprint.values()
            ):
                raise ValueError("missing or invalid execution environment fingerprint")
            digest = fingerprint["distributions_digest"]
            if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                raise ValueError("invalid distribution digest")
            if environment is None:
                environment = fingerprint
            elif fingerprint != environment:
                raise ValueError("mixed batch execution environments")
            counts, digest = _junit(result_dir / f"{suite}-{index}.xml")
            if counts != receipt.get("counts") or digest != receipt.get("junit_sha256"):
                raise ValueError("corrupt or mismatched JUnit")
            if counts["tests"] == 0 or counts["failures"] or counts["errors"]:
                raise ValueError("JUnit does not show a successful nonempty batch")
            for key in totals:
                totals[key] += counts[key]
        except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
            problems.append(f"batch {index}: {exc}")
    if _snapshot() != identity["snapshot"]:
        problems.append("snapshot changed during aggregation")
    if "frozen_environment" in identity and _environment_fingerprint() != identity["frozen_environment"]:
        problems.append("environment changed during aggregation")
    if "execution_settings" in identity and _execution_settings() != identity["execution_settings"]:
        problems.append("execution settings changed during aggregation")
    summary = {**identity, "suite": suite, "batch_count": len(batches),
               "environment_fingerprint": environment,
               "status": "failure" if problems else "success", "counts": totals, "problems": problems}
    _write_receipt(result_dir / f"{suite}-aggregate.json", summary)
    print(json.dumps(summary, sort_keys=True))
    return int(bool(problems))


def _record_batch(result_dir: Path, suite: str, batches: list[dict], index: int,
                  identity: dict, command: list[str], dry_run: bool, timeout: float | None) -> int:
    receipt_path = result_dir / f"{suite}-{index}.json"
    xml_path = result_dir / f"{suite}-{index}.xml"
    xml_path.unlink(missing_ok=True)
    if command:
        command = [*command, f"--junitxml={xml_path}"]
    receipt = {**identity, "suite": suite, "batch_index": index, "batch_count": len(batches),
               "command": command, "exit_code": None, "status": "incomplete",
               "counts": None, "junit_sha256": None, "environment_fingerprint": None}
    _write_receipt(receipt_path, receipt)
    code = 1
    started = time.monotonic()
    try:
        if _snapshot() != identity["snapshot"]:
            raise ValueError("snapshot changed before batch execution")
        if "execution_settings" in identity and _execution_settings() != identity["execution_settings"]:
            raise ValueError("execution settings changed before batch")
        if dry_run:
            code = _run(command, True, timeout)
            receipt["exit_code"] = code
            receipt["status"] = "dry-run"
        elif not batches[index]["test_paths"]:
            code = 0
            receipt["exit_code"] = code
            receipt["status"] = "empty"
            receipt["counts"] = dict.fromkeys(("tests", "failures", "errors", "skipped"), 0)
        else:
            receipt["environment_fingerprint"] = _environment_fingerprint()
            if "frozen_environment" in identity and receipt["environment_fingerprint"] != identity["frozen_environment"]:
                raise ValueError("execution environment changed before batch")
            _write_receipt(receipt_path, receipt)
            code = _run(command, False, timeout)
            receipt["exit_code"] = code
            receipt["status"] = "incomplete" if code == 124 or code < 0 else "failure"
            if xml_path.exists():
                receipt["counts"], receipt["junit_sha256"] = _junit(xml_path)
                if code == 0 and receipt["counts"]["tests"] > 0 and not (
                    receipt["counts"]["failures"] or receipt["counts"]["errors"]
                ):
                    receipt["status"] = "success"
            elif code == 0:
                receipt["status"] = "incomplete"
            if receipt["status"] != "success" and code == 0:
                code = 1
        if _snapshot() != identity["snapshot"]:
            receipt["status"] = "incomplete"
            code = 1
        if "frozen_environment" in identity and _environment_fingerprint() != identity["frozen_environment"]:
            receipt["status"] = "incomplete"
            code = 1
        if "execution_settings" in identity and _execution_settings() != identity["execution_settings"]:
            receipt["status"] = "incomplete"
            code = 1
    except (OSError, ValueError, ET.ParseError, subprocess.SubprocessError) as exc:
        receipt["error"] = str(exc)
        receipt["status"] = "incomplete"
        code = 1
    receipt["elapsed_seconds"] = time.monotonic() - started
    _write_receipt(receipt_path, receipt)
    return code


def _frozen_main(args: argparse.Namespace) -> int:
    try:
        if args.suite != "full-core" or args.plan_file is None or os.environ.get("PYTEST_ADDOPTS"):
            raise ValueError("frozen plans require --suite full-core, --plan-file and empty PYTEST_ADDOPTS")
        if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE") not in (None, "", "0"):
            raise ValueError("frozen verification requires Python assertions enabled")
        plan_path = args.plan_file.resolve()
        if plan_path.is_relative_to(ROOT.resolve()):
            raise ValueError("--plan-file must be outside the repository")
        snapshot = _snapshot()
        environment = _environment_fingerprint()
        if args.write_plan:
            if args.aggregate or args.resume or args.batch_index is not None or args.dry_run:
                raise ValueError("--write-plan cannot execute, resume or aggregate")
            if plan_path.exists():
                raise ValueError("refusing to overwrite frozen plan")
            workers = args.workers if args.workers is not None else 0
            if workers and not util.find_spec("xdist"):
                raise ValueError("requested frozen workers require pytest-xdist")
            files = [
                p for batch in build_regression_supervision_plan_with_full_core_count()[
                    "supervised_full_core_suite"
                ]["batches"] for p in batch["test_paths"]
            ]
            if args.durations_file and args.timings_dir:
                raise ValueError("choose --durations-file or --timings-dir, not both")
            durations = json.loads(args.durations_file.read_text()) if args.durations_file else None
            timing_provenance = []
            if args.timings_dir:
                durations, timing_provenance = _measured_durations(args.timings_dir, files)
                if not durations:
                    raise ValueError("timings directory has no usable validated receipts")
            batches = build_dependency_cost_batches(
                files, args.batch_count if args.batch_count is not None else DEFAULT_FULL_CORE_BATCH_COUNT, durations
            )
            batches.append({
                "batch_index": len(batches), "test_paths": integration_preflight_argv()[3:-3],
                "integration": True,
            })
            plan = {
                "schema": "supervised-plan-v1", "snapshot": snapshot, "environment": environment,
                "execution_settings": _execution_settings(),
                "workers": workers, "batches": batches, "durations": durations,
                "timing_provenance": timing_provenance,
                "marker_expression": "", "scope": "full-core plus shared-process integration; not empirical proof",
            }
            plan["digest"] = _digest(plan)
            if _snapshot() != snapshot or _environment_fingerprint() != environment:
                raise ValueError("source or environment changed during planning")
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            with plan_path.open("x") as stream:
                json.dump(plan, stream, indent=2, sort_keys=True)
                stream.write("\n")
            print(f"Frozen {len(batches) - 1} dependency/cost chunks plus integration: {plan_path}")
            return 0
        if args.durations_file is not None or args.timings_dir is not None:
            raise ValueError("timing inputs are only accepted with --write-plan")
        plan = _load_frozen_plan(plan_path, snapshot, environment)
        if args.workers is not None and args.workers != plan["workers"]:
            raise ValueError("worker count differs from frozen plan")
        if args.batch_count is not None and args.batch_count != len(plan["batches"]) - 1:
            raise ValueError("batch count differs from frozen plan")
        if args.result_dir is None or args.dry_run:
            raise ValueError("frozen execution requires --result-dir and cannot be a dry run")
        artifact_names = [f"full-core-{index}.{suffix}" for index in range(len(plan["batches"]))
                          for suffix in ("json", "json.pending", "xml")]
        artifact_names.extend(("full-core-aggregate.json", "full-core-aggregate.json.pending"))
        for name in artifact_names:
            artifact = args.result_dir / name
            if artifact.resolve() == plan_path or (artifact.exists() and artifact.samefile(plan_path)):
                raise ValueError("frozen plan collides with a result artifact")
        result_dir = args.result_dir.resolve()
        if result_dir.is_relative_to(ROOT.resolve()):
            raise ValueError("--result-dir must be outside the repository")
        result_dir.mkdir(parents=True, exist_ok=True)
        batches = plan["batches"]
        identity = {
            "snapshot": snapshot, "plan_digest": plan["digest"], "execution_digest": _digest({
                "python": sys.executable, "workers": plan["workers"], "marker_expression": "",
            }),
            "workers": plan["workers"], "frozen_environment": environment,
            "execution_settings": plan["execution_settings"],
        }
        if args.aggregate:
            if args.resume or args.batch_index is not None:
                raise ValueError("--aggregate cannot resume or execute a batch")
            return _aggregate(result_dir, args.suite, batches, identity)
        if args.batch_index is None:
            if not args.resume or args.timeout is None:
                raise ValueError("executing all unresolved chunks requires --resume and --timeout")
            indices = range(len(batches))
        elif not 0 <= args.batch_index < len(batches):
            raise ValueError("invalid frozen batch index")
        else:
            indices = [args.batch_index]
        failed = False
        for index in indices:
            if (_snapshot() != snapshot or _environment_fingerprint() != environment
                    or _execution_settings() != plan["execution_settings"]):
                raise ValueError("source or environment changed during execution")
            if args.resume:
                try:
                    _verified_batch(result_dir, args.suite, batches, index, identity, environment)
                    print(f"batch {index}: verified receipt reused")
                    continue
                except (OSError, ValueError, KeyError, TypeError, ET.ParseError):
                    pass
            code = _record_batch(
                result_dir, args.suite, batches, index, identity,
                _frozen_command(batches[index], plan["workers"]), False, args.timeout,
            )
            failed = failed or code != 0
        if args.batch_index is None:
            return _aggregate(result_dir, args.suite, batches, identity)
        return int(failed)
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError, subprocess.SubprocessError) as exc:
        print(f"frozen verification rejected: {exc}", file=sys.stderr)
        return 2


def main() -> int:
    args = _parse_args()
    if args.workers is not None and args.workers < 0:
        print("--workers must be nonnegative", file=sys.stderr)
        return 2
    if args.timeout is not None and (not math.isfinite(args.timeout) or args.timeout <= 0):
        print("--timeout must be positive and finite", file=sys.stderr)
        return 2
    if args.write_plan or args.plan_file or args.durations_file or args.timings_dir or args.resume:
        return _frozen_main(args)
    if args.aggregate and (args.result_dir is None or args.dry_run or args.batch_index is not None):
        print("--aggregate requires --result-dir and no --dry-run/--batch-index", file=sys.stderr)
        return 2
    if (args.result_dir is not None or args.aggregate) and args.suite not in {"tests-fast", "full-core"}:
        print("receipts are supported only for tests-fast/full-core", file=sys.stderr)
        return 2
    if args.result_dir is not None and os.environ.get("PYTEST_ADDOPTS"):
        print("receipt-backed execution/aggregation requires empty PYTEST_ADDOPTS", file=sys.stderr)
        return 2
    if args.result_dir is not None:
        args.result_dir = args.result_dir.resolve()
        if args.result_dir.is_relative_to(ROOT.resolve()):
            print("--result-dir must be outside the repository", file=sys.stderr)
            return 2
        args.result_dir.mkdir(parents=True, exist_ok=True)
    try:
        snapshot = _snapshot() if args.result_dir is not None else None
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"cannot establish repository snapshot: {exc}", file=sys.stderr)
        return 2
    fast_batch_count = (
        args.batch_count if args.suite in {"tests-fast", "supervisor-check"} and args.batch_count is not None
        else DEFAULT_FAST_BATCH_COUNT
    )
    full_core_batch_count = (
        args.batch_count if args.suite in {"full-core", "full-core-supervisor-check"} and args.batch_count is not None
        else DEFAULT_FULL_CORE_BATCH_COUNT
    )
    plan = build_regression_supervision_plan_with_full_core_count(
        batch_count=fast_batch_count,
        full_core_batch_count=full_core_batch_count,
    )

    if args.emit_json:
        print(json.dumps(plan, indent=2, sort_keys=True))

    if args.suite == "supervisor-check":
        ok = plan["supervision"]["coverage_matches_discovery"] and plan["supervision"]["all_files_unique"]
        if not ok:
            print("supervised regression coverage check failed", file=sys.stderr)
            return 1
        stream = sys.stderr if args.emit_json else sys.stdout
        print("supervised regression structural file coverage check passed (not execution evidence)", file=stream)
        return 0

    if args.suite == "full-core-supervisor-check":
        ok = (
            plan["supervision"]["full_core_coverage_matches_discovery"]
            and plan["supervision"]["full_core_all_files_unique"]
        )
        if not ok:
            print("supervised full-core regression coverage check failed", file=sys.stderr)
            return 1
        stream = sys.stderr if args.emit_json else sys.stdout
        print("supervised full-core regression structural file coverage check passed (not execution evidence)", file=stream)
        return 0

    if args.suite == "compactified-preflight":
        return _run(compactified_preflight_argv(), dry_run=args.dry_run, timeout=args.timeout)

    if args.suite == "integration-preflight":
        return _run(integration_preflight_argv(), dry_run=args.dry_run, timeout=args.timeout,
                    env={**os.environ, "PYTEST_ADDOPTS": ""})

    section = plan["supervised_full_core_suite" if args.suite == "full-core" else "supervised_fast_suite"]
    batches = section["batches"]
    identity = None
    if args.result_dir is not None:
        identity = {"snapshot": snapshot, "plan_digest": _digest({
            "batches": [batch["test_paths"] for batch in batches],
            "marker_expression": section.get("marker_expression", ""),
        })}
    if args.aggregate:
        return _aggregate(args.result_dir, args.suite, batches, identity)

    if args.batch_index is None or not 0 <= args.batch_index < len(batches):
        print("--batch-index must identify an existing batch", file=sys.stderr)
        return 2
    count = full_core_batch_count if args.suite == "full-core" else fast_batch_count
    builder = full_core_batch_argv if args.suite == "full-core" else fast_batch_argv
    command = builder(batch_index=args.batch_index, batch_count=count)
    if args.workers is not None and "-n" in command:
        position = command.index("-n")
        command[position:position + 2] = [] if args.workers == 0 else ["-n", str(args.workers)]
    if args.result_dir is not None:
        return _record_batch(args.result_dir, args.suite, batches, args.batch_index,
                             identity, command, args.dry_run, args.timeout)
    if not command:
        print(f"no tests assigned to batch {args.batch_index}; skipping")
        return 0
    return _run(command, dry_run=args.dry_run, timeout=args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
