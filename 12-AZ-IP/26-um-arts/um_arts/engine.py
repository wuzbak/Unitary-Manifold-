# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Planning, duration-balanced execution, immutable resume, and safe import."""

from __future__ import annotations

import fcntl
import os
import re
import shutil
import sys
import uuid
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path

from . import VERSION, formal
from .adapters import load_config, selection_policy
from .evidence import (
    EvidenceError,
    Index,
    contained,
    digest,
    file_hash,
    fingerprints,
    read_json,
    seal,
    verify_seal,
    write_json,
)
from .process import discard_scratch, execute
from .reconcile import evaluate_job


def _pytest_command(root: Path, directory: Path, suite: dict, config: dict,
                    *, collect: bool = False) -> list[str]:
    own_config = next((root / name for name in ["pytest.ini", ".pytest.ini", "pyproject.toml",
                                               "tox.ini", "setup.cfg"]
                       if (root / name).is_file()), None)
    if own_config is None:
        # Without -c pytest can accidentally inherit an unrelated ancestor project's
        # configuration. This empty, sealed config isolates generic fixture roots.
        own_config = directory / "pytest.ini"
        with own_config.open("x", encoding="utf-8") as stream:
            stream.write("[pytest]\n")
    return [sys.executable, "-m", "pytest", "-p", "um_arts.pytest_plugin",
            *(arg for plugin in config.get("plugins", []) for arg in ("-p", plugin)),
            "--rootdir", str(root), "--confcutdir", str(root), "-c", str(own_config),
            "--basetemp", str(directory / "scratch"),
            *suite["paths"], *config["pytest_args"], "-q",
            *(["--collect-only"] if collect else [])]


def _pytest(root: Path, directory: Path, suite: dict, config: dict,
            nodes: list[str] | None = None) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    nonce = uuid.uuid4().hex
    assigned_files = nodes is not None and not suite["serial"]
    execution_suite = suite
    if assigned_files:
        paths = sorted({node.split("::", 1)[0] for node in nodes})
        for path in paths:
            contained(root, path)
        execution_suite = {**suite, "paths": paths}
    command = _pytest_command(root, directory, execution_suite, config, collect=nodes is None)
    write_json(directory / "request.json", {"nonce": nonce, "command": command,
                                          "collection_only": nodes is None, "root": str(root),
                                          "collection_scope": "assigned_files" if assigned_files else "suite"})
    environment = dict(os.environ)
    environment.pop("PYTEST_ADDOPTS", None)
    environment.pop("PYTEST_PLUGINS", None)
    environment.pop("UM_ARTS_SELECTION", None)
    engine_root = str(Path(__file__).resolve().parents[1])
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(root), engine_root, environment.get("PYTHONPATH", "")])
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    environment["UM_ARTS_RECEIPT"] = str(directory / "events.json")
    environment["UM_ARTS_NONCE"] = nonce
    for name in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS"]:
        environment[name] = "1"
    if nodes is not None:
        write_json(directory / "selection.json", nodes)
        environment["UM_ARTS_SELECTION"] = str(directory / "selection.json")
    timeout = config.get("collection_timeout_seconds", config["timeout_seconds"]) \
        if nodes is None else config["timeout_seconds"]
    execute(command, root, directory, timeout, environment)
    discard_scratch(directory / "scratch")


def _freeze(directory: Path) -> None:
    for current, directories, files in os.walk(directory):
        for name in files:
            (Path(current) / name).chmod(0o444)
        for name in directories:
            (Path(current) / name).chmod(0o555)
    directory.chmod(0o555)


def _validate_store(root: Path, store: Path) -> None:
    if root.is_relative_to(store):
        raise EvidenceError("Artifact store may not be the repository root or its ancestor")


def balanced_jobs(suites: list[dict], workers: int, durations: dict[str, float],
                  files_per_job: int = 32) -> list[dict]:
    """LPT balancing by test file preserves module/class fixture locality."""
    if isinstance(files_per_job, bool) or not isinstance(files_per_job, int) \
            or not 1 <= files_per_job <= 1024:
        raise EvidenceError("files_per_job must be an integer in [1, 1024]")
    jobs = []
    for suite in suites:
        groups = defaultdict(list)
        for node in suite["nodes"]:
            groups[node.split("::", 1)[0]].append(node)
        count = (1 if suite["serial"] else max(
            workers, (len(groups) + files_per_job - 1) // files_per_job))
        bins = [[] for _ in range(min(count, len(groups)))]
        loads = [0.0 for _ in bins]
        file_counts = [0 for _ in bins]
        weighted = [(sum(durations.get(node, 1.0) for node in nodes), file, nodes)
                    for file, nodes in groups.items()]
        for weight, _, nodes in sorted(weighted, key=lambda value: (-value[0], value[1])):
            available = [index for index in range(len(bins))
                         if suite["serial"] or file_counts[index] < files_per_job]
            slot = min(available, key=lambda index: (loads[index], index))
            bins[slot].extend(nodes)
            loads[slot] += weight
            file_counts[slot] += 1
        for index, nodes in enumerate(bins):
            jobs.append({"id": f"{suite['name']}-{index:03d}", "suite": suite["name"],
                         "nodes": sorted(nodes), "estimated_seconds": loads[index]})
    return jobs


def plan(root: Path, store: Path, config_path: Path | None = None,
         adapter: str = "um", mode: str = "full") -> dict:
    root, store = root.resolve(), store.resolve()
    if not root.is_dir():
        raise EvidenceError("Repository root does not exist")
    _validate_store(root, store)
    config = load_config(root, config_path, adapter)
    config_source = ({"path": str(config_path.resolve()), "sha256": file_hash(config_path)}
                     if config_path else None)
    index = Index(store)
    before = fingerprints(root, store, config)
    directory = contained(store, "plans/" + uuid.uuid4().hex, must_exist=False)
    directory.mkdir(parents=True)
    suites = []
    errors = []
    seen = set()
    for suite in config["suites"]:
        job_dir = directory / "collection" / suite["name"]
        _pytest(root, job_dir, suite, config)
        evidence = evaluate_job(job_dir, None, collection=True)
        nodes = evidence["selected"]
        if evidence["status"] != "passed":
            errors.extend(f"{suite['name']}: {error}" for error in evidence["errors"])
        overlap = set(nodes) & seen
        if overlap:
            errors.append(f"Suites overlap: {sorted(overlap)[:5]}")
        seen.update(nodes)
        suites.append({**suite, "nodes": sorted(nodes),
                       "deselected": sorted(evidence["deselected"]),
                       "collection_skips": evidence["collection_skips"]})
    snapshot = formal.capture(root, directory / "formal", config)
    if config["adapter"] == "um" and snapshot["status"] != "captured":
        errors.append("Required UM formal registry could not be snapshotted")
    after = fingerprints(root, store, config)
    if before["compatibility"] != after["compatibility"]:
        errors.append("Source/environment/settings changed during collection")
    if config_source and (not config_path.is_file()
                          or file_hash(config_path) != config_source["sha256"]):
        errors.append("Original execution config changed during collection")
    spec = {
        "version": VERSION, "root": str(root), "store": str(store), "config": config,
        "fingerprints": before, "selection": selection_policy(mode),
        "suites": suites, "formal": snapshot,
        "jobs": balanced_jobs(suites, config["workers"], index.durations(before["compatibility"]),
                              config["files_per_job"]),
        "status": "ready" if not errors else "blocked", "errors": errors,
        "config_source": config_source,
    }
    write_json(directory / "plan.json", spec)
    seal(directory)
    _freeze(directory)
    return {"status": spec["status"], "plan_path": str(directory / "plan.json"),
            "selected": len(seen), "errors": errors, "selection": spec["selection"]}


def validate_plan(directory: Path) -> dict:
    verify_seal(directory)
    spec = read_json(contained(directory, "plan.json"))
    if not isinstance(spec, dict):
        raise EvidenceError("Plan must be a JSON object")
    if spec.get("version") != VERSION or spec.get("status") != "ready":
        raise EvidenceError("Plan is not ready or has an unsupported version")
    config = spec["config"]
    suites = spec["suites"]
    if not isinstance(config, dict) or not isinstance(suites, list) or not suites \
            or any(not isinstance(suite, dict) for suite in suites):
        raise EvidenceError("Malformed plan configuration/suites")
    names = [suite["name"] for suite in suites]
    if any(not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", name)
           for name in names):
        raise EvidenceError("Unsafe suite name in plan")
    if len(names) != len(set(names)):
        raise EvidenceError("Duplicate suites in plan")
    if [s["name"] for s in config["suites"]] != names:
        raise EvidenceError("Plan suites disagree with configuration")
    all_nodes = []
    for suite, configured in zip(suites, config["suites"]):
        if any(suite.get(key) != value for key, value in configured.items()):
            raise EvidenceError("Suite settings disagree with configuration")
        result = evaluate_job(directory / "collection" / suite["name"], suite["nodes"],
                              collection=True)
        if result["status"] != "passed":
            raise EvidenceError(f"Invalid collection evidence: {result['errors']}")
        if sorted(result["deselected"]) != sorted(suite["deselected"]) \
                or result["collection_skips"] != suite["collection_skips"]:
            raise EvidenceError("Collection exclusions disagree with plan")
        all_nodes.extend(suite["nodes"])
    if len(all_nodes) != len(set(all_nodes)):
        raise EvidenceError("Duplicate identities across plan suites")
    assigned = []
    identifiers = set()
    for job in spec["jobs"]:
        if not isinstance(job["id"], str) or not re.fullmatch(r"[A-Za-z0-9_-]+", job["id"]):
            raise EvidenceError("Unsafe job identifier in plan")
        if job["id"] in identifiers or job["suite"] not in names:
            raise EvidenceError("Duplicate or unknown execution job")
        contained(directory, "collection/" + job["suite"], must_exist=False)
        # IDs are artifact paths; validate even when reading untrusted imports.
        contained(directory, "jobs/" + job["id"], must_exist=False)
        identifiers.add(job["id"])
        suite = next(s for s in suites if s["name"] == job["suite"])
        if not job["nodes"] or not set(job["nodes"]).issubset(suite["nodes"]):
            raise EvidenceError("Job identities do not belong to its suite")
        assigned.extend(job["nodes"])
    if Counter(assigned) != Counter(all_nodes):
        raise EvidenceError("Jobs do not cover collected identities exactly once")
    return spec


def _job_evaluation(directory: Path, job: dict, suite: dict) -> dict:
    result = evaluate_job(directory, job["nodes"])
    if result["status"] == "passed":
        request = read_json(directory / "request.json")
        files = {node.split("::", 1)[0] for node in job["nodes"]}
        scope = request.get("collection_scope", "suite")
        if not isinstance(scope, str) or scope not in {"suite", "assigned_files"}:
            result["status"] = "blocked"
            result["errors"].append("Unknown execution collection scope")
            return result
        local = scope == "assigned_files"
        def in_scope(node):
            return not local or node.split("::", 1)[0] in files
        # Initial collection covers every suite. Each independent job recollects
        # its assigned files; global reconciliation still requires every planned ID.
        outside = {node for node in suite["nodes"] if in_scope(node)} - set(job["nodes"])
        deselected = [node for node in suite["deselected"] if in_scope(node)]
        skips = [node for node in suite["collection_skips"] if in_scope(node)]
        if set(result["partition_excluded"]) != outside \
                or Counter(result["deselected"]) != Counter(deselected) \
                or result["collection_skips"] != skips:
            result["status"] = "blocked"
            result["errors"].append("Suite collection universe/exclusions changed at execution")
    return result


@contextmanager
def _attempt_lock(attempt: Path, *, create: bool = False):
    """Prevent recovery while a runner or another recovery owns the attempt."""
    path = contained(attempt, "runner.lock", must_exist=not create)
    with path.open("xb" if create else "rb") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise EvidenceError("Attempt is still running or being recovered") from exc
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def _checkpoint_job(root: Path, store: Path, destination: Path, suite: dict,
                    config: dict, job: dict, compatibility: dict) -> None:
    before = fingerprints(root, store, config)["compatibility"]
    _pytest(root, destination, suite, config, job["nodes"])
    after = fingerprints(root, store, config)["compatibility"]
    write_json(destination / "checkpoint.json", {
        "version": VERSION, "job_digest": digest(job),
        "compatibility": compatibility, "before": before, "after": after,
    })
    seal(destination)
    _freeze(destination)


def _checked_checkpoint(directory: Path, job: dict, suite: dict,
                        compatibility: dict) -> dict:
    verify_seal(directory)
    checkpoint = read_json(contained(directory, "checkpoint.json"))
    if not isinstance(checkpoint, dict) or checkpoint.get("version") != VERSION \
            or checkpoint.get("job_digest") != digest(job) \
            or any(checkpoint.get(field) != compatibility
                   for field in ["compatibility", "before", "after"]):
        raise EvidenceError("Job checkpoint identity/source/environment/settings mismatch")
    return _job_evaluation(directory, job, suite)


def _execution_evaluation(directory: Path, job: dict, suite: dict,
                          compatibility: dict, *, required: bool = False) -> dict:
    if not (directory / "checkpoint.json").exists():
        if required:
            return {"status": "blocked", "errors": ["Required job checkpoint is missing"],
                    "counts": {}, "durations": {}, "selected": []}
        return _job_evaluation(directory, job, suite)
    try:
        return _checked_checkpoint(directory, job, suite, compatibility)
    except EvidenceError as exc:
        return {"status": "blocked", "errors": [str(exc)], "counts": {},
                "durations": {}, "selected": []}


def _attempt_identity(attempt: Path) -> tuple[dict, dict]:
    spec = read_json(contained(attempt, "attempt.json"))
    if not isinstance(spec, dict):
        raise EvidenceError("Attempt must be a JSON object")
    plan_spec = validate_plan(attempt / "plan")
    if spec.get("version") != VERSION or spec.get("plan_digest") != digest(plan_spec) \
            or spec.get("compatibility") != plan_spec["fingerprints"]["compatibility"]:
        raise EvidenceError("Attempt identity does not agree with its plan")
    if spec.get("checkpoint_policy") not in {None, "per-job-v1"}:
        raise EvidenceError("Unsupported attempt checkpoint policy")
    return spec, plan_spec


def evaluate_incomplete(attempt: Path) -> dict:
    """Unsealed runs can expose checked jobs but can never certify a baseline."""
    if attempt.is_symlink() or not attempt.is_dir():
        raise EvidenceError("Attempt root must be a regular directory")
    spec, plan_spec = _attempt_identity(attempt)
    start = read_json(contained(attempt, "start_fingerprints.json"))
    if start.get("compatibility") != spec["compatibility"]:
        raise EvidenceError("Attempt start fingerprints disagree with its plan")
    jobs = {}
    counts = Counter()
    durations = {}
    nodes = []
    suites = {}
    errors = ["Attempt is unsealed/incomplete; only validated job checkpoints are reusable"]
    for suite in plan_spec["suites"]:
        prerequisites_passed = all(suites.get(name) == "passed" for name in suite["requires"])
        results = []
        for job in [j for j in plan_spec["jobs"] if j["suite"] == suite["name"]]:
            directory = contained(attempt, "jobs/" + job["id"], must_exist=False)
            try:
                result = _checked_checkpoint(directory, job, suite, spec["compatibility"])
                if not prerequisites_passed:
                    raise EvidenceError("Checkpoint prerequisite suite is incomplete")
            except EvidenceError as exc:
                result = {"status": "incomplete", "errors": [str(exc)], "counts": {},
                          "durations": {}, "selected": []}
            jobs[job["id"]] = result
            results.append(result)
            counts.update(result["counts"])
            durations.update(result["durations"])
            nodes.extend(result["selected"])
        suites[suite["name"]] = "passed" if results and all(
            result["status"] == "passed" for result in results) else "incomplete"
    return {
        "version": VERSION, "attempt_id": spec["id"], "status": "incomplete",
        "errors": errors, "counts": dict(counts), "durations": durations,
        "selected": sum(len(suite["nodes"]) for suite in plan_spec["suites"]),
        "reconciled": len(nodes), "jobs": jobs, "suites": suites,
        "compatibility": spec["compatibility"], "selection": plan_spec["selection"],
        "formal": {"status": "incomplete", "proof_claim": False},
        "integrity_boundary": "Job hashes are not signatures or execution attestations.",
    }


def evaluate(attempt: Path) -> dict:
    if not (attempt / "manifest.json").exists() and not (attempt / "seal.json").exists():
        return evaluate_incomplete(attempt)
    manifest = verify_seal(attempt)
    if "capture.json" in manifest["files"]:
        from .capture import evaluate_capture
        return evaluate_capture(attempt)
    spec, plan_spec = _attempt_identity(attempt)
    counts = Counter()
    durations = {}
    nodes = []
    jobs = {}
    errors = list(spec.get("errors", []))
    if "execution_errors.json" in manifest["files"]:
        errors.extend(read_json(contained(attempt, "execution_errors.json")))
    if read_json(contained(attempt, "end_fingerprints.json"))["compatibility"] != spec["compatibility"]:
        errors.append("Source/environment/settings changed during execution")
    suite_status = {}
    for suite in plan_spec["suites"]:
        if not all(suite_status.get(name) == "passed" for name in suite["requires"]):
            errors.append(f"{suite['name']}: dependency did not pass")
        results = []
        for job in [job for job in plan_spec["jobs"] if job["suite"] == suite["name"]]:
            result = _execution_evaluation(attempt / "jobs" / job["id"], job, suite,
                                           spec["compatibility"],
                                           required=spec.get("checkpoint_policy") == "per-job-v1")
            jobs[job["id"]] = result
            results.append(result)
            counts.update(result["counts"])
            durations.update(result["durations"])
            nodes.extend(result["selected"])
            errors.extend(f"{job['id']}: {error}" for error in result["errors"])
        suite_status[suite["name"]] = "passed" if results and all(
            result["status"] == "passed" for result in results) else "blocked"
    planned = [node for suite in plan_spec["suites"] for node in suite["nodes"]]
    if Counter(nodes) != Counter(planned):
        errors.append("Global collected/executed identities do not match exactly")
    lean = formal.evaluate_build(attempt / "lean", plan_spec["config"]["lean"],
                                 expected_root=plan_spec["root"])
    if lean["status"] == "blocked":
        errors.append("Requested Lean build is blocked")
    if lean.get("inspection", {}).get("status") == "blocked":
        errors.append("Requested Lean declaration inspection is blocked")
    return {
        "version": VERSION, "attempt_id": spec["id"], "status": "passed" if not errors else "blocked",
        "errors": errors, "counts": dict(counts), "durations": durations,
        "selected": len(planned), "reconciled": len(nodes),
        "deselected": sum(len(suite["deselected"]) for suite in plan_spec["suites"]),
        "collection_skips": {suite["name"]: suite["collection_skips"]
                             for suite in plan_spec["suites"]},
        "jobs": jobs, "suites": suite_status, "compatibility": spec["compatibility"],
        "selection": plan_spec["selection"],
        "formal": formal.coverage(plan_spec["formal"], lean, nodes),
        "integrity_boundary": "SHA-256 detects accidental/torn/tampered evidence relative to "
                              "the seal; it is not a signature or an execution attestation.",
    }


def run(plan_path: Path, previous: Path | None = None) -> dict:
    source = plan_path.resolve().parent
    spec = validate_plan(source)
    root, store = Path(spec["root"]), Path(spec["store"])
    _validate_store(root, store)
    # Execution configs are trusted input. Reporting/import never enters this path.
    config = spec["config"]
    config_source = spec.get("config_source")
    if config_source:
        original_config = Path(config_source["path"])
        if not original_config.is_file() or file_hash(original_config) != config_source["sha256"]:
            raise EvidenceError("Original execution config changed or is missing; re-plan")
    current = fingerprints(root, store, config)
    if current["compatibility"] != spec["fingerprints"]["compatibility"]:
        raise EvidenceError("Plan source/environment/settings are no longer compatible; re-plan")
    prior = None
    prior_spec = None
    if previous:
        prior = evaluate(previous)
        prior_spec = read_json(contained(previous, "plan/plan.json"))
        if prior["compatibility"] != current["compatibility"]:
            raise EvidenceError("Resume evidence is incompatible with current source/environment/settings")
        if (previous / "end_fingerprints.json").is_file() and read_json(
                contained(previous, "end_fingerprints.json"))["compatibility"] != current["compatibility"]:
            raise EvidenceError("Source/environment/settings changed during prior execution; re-plan")
    index = Index(store)
    identifier = uuid.uuid4().hex
    attempt = contained(store, "attempts/" + identifier, must_exist=False)
    attempt.mkdir(parents=True)
    shutil.copytree(source, attempt / "plan")
    # copytree preserves read-only modes; the nested plan remains immutable.
    errors = []
    attempt_spec = {"version": VERSION, "id": identifier, "root": str(root), "store": str(store),
                    "plan_digest": digest(spec), "compatibility": current["compatibility"],
                    "previous_attempt": str(previous) if previous else None, "errors": errors,
                    "checkpoint_policy": "per-job-v1"}
    write_json(attempt / "start_fingerprints.json", current)
    write_json(attempt / "attempt.json", attempt_spec)
    suite_status = {}
    with _attempt_lock(attempt, create=True):
        try:
            for suite in spec["suites"]:
                if not all(suite_status.get(name) == "passed" for name in suite["requires"]):
                    suite_status[suite["name"]] = "blocked"
                    continue
                suite_jobs = [job for job in spec["jobs"] if job["suite"] == suite["name"]]
                pending = []
                for job in suite_jobs:
                    destination = attempt / "jobs" / job["id"]
                    same_job = prior_spec and job in prior_spec["jobs"]
                    if same_job and prior["jobs"].get(job["id"], {}).get("status") == "passed" \
                            and (previous / "jobs" / job["id"] / "checkpoint.json").is_file():
                        shutil.copytree(previous / "jobs" / job["id"], destination)
                    else:
                        pending.append((job, destination))
                with ThreadPoolExecutor(max_workers=config["workers"]) as pool:
                    futures = [pool.submit(_checkpoint_job, root, store, destination, suite,
                                           config, job, current["compatibility"])
                               for job, destination in pending]
                    for future in futures:
                        future.result()
                suite_status[suite["name"]] = "passed" if all(
                    _execution_evaluation(attempt / "jobs" / job["id"], job, suite,
                                          current["compatibility"], required=True)["status"] == "passed"
                    for job in suite_jobs) else "blocked"
            if config["lean"]:
                formal.build(root, attempt / "lean", config)
        except (OSError, ValueError, KeyboardInterrupt) as exc:
            errors.append(f"Execution interrupted: {type(exc).__name__}: {exc}")
        finally:
            write_json(attempt / "execution_errors.json", errors)
            write_json(attempt / "end_fingerprints.json", fingerprints(root, store, config))
            seal(attempt)
            _freeze(attempt)
    result = evaluate(attempt)
    index.record(attempt, result)
    return {"status": result["status"], "attempt_path": str(attempt),
            "counts": result["counts"], "errors": result["errors"]}


def resume(attempt: Path) -> dict:
    # The prior attempt is never mutated; completed evidence is copied and revalidated.
    evaluate(attempt)
    if (attempt / "capture.json").is_file():
        raise EvidenceError("Captured existing commands have no resumable plan; wrap the trusted command again")
    if not (attempt / "manifest.json").exists() and not (attempt / "seal.json").exists():
        with _attempt_lock(attempt):
            return run(attempt / "plan" / "plan.json", previous=attempt)
    return run(attempt / "plan" / "plan.json", previous=attempt)


def import_artifact(artifact: Path, store: Path) -> dict:
    """Import only regular, verified evidence files; never execute artifact commands."""
    result = evaluate(artifact)
    if result["status"] == "incomplete":
        raise EvidenceError("Unsealed attempts cannot be imported as completed evidence")
    manifest = verify_seal(artifact)
    index = Index(store)
    destination = contained(store.resolve(), "imports/" + uuid.uuid4().hex, must_exist=False)
    destination.mkdir(parents=True)
    try:
        for relative in [*manifest["files"], "manifest.json", "seal.json"]:
            original = contained(artifact, relative)
            target = contained(destination, relative, must_exist=False)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, target)
        # Detect modification between verification and copy.
        imported = evaluate(destination)
        def without_locations(value):
            if isinstance(value, dict):
                return {key: without_locations(item) for key, item in value.items()
                        if key not in {"attempt_path", "report_path"}}
            if isinstance(value, list):
                return [without_locations(item) for item in value]
            return value

        if without_locations(imported) != without_locations(result):
            raise EvidenceError("Artifact changed while importing")
        _freeze(destination)
        index.record(destination, imported)
    except Exception:
        shutil.rmtree(destination)
        raise
    return {"status": imported["status"], "attempt_path": str(destination),
            "imported": True, "executed_commands": False}
