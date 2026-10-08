# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Structured pytest receipts; never infer results from terminal output."""

import json
import os
import uuid
from pathlib import Path

import pytest

_data = {
    "version": "1",
    "nonce": os.environ.get("UM_ARTS_NONCE"),
    "selected": [],
    "deselected": [],
    "partition_excluded": [],
    "collection": [],
    "reports": [],
    "internal_errors": [],
}


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    _data["root"] = str(config.rootpath.resolve())
    managed = bool(os.environ.get("UM_ARTS_RECEIPT"))
    output = os.environ.get("UM_ARTS_RECEIPT") or os.environ.get("UM_ARTS_PYTEST_REPORT")
    if not output or not Path(output).is_absolute():
        raise pytest.UsageError("UM-ARTS requires an absolute UM_ARTS_PYTEST_REPORT or UM_ARTS_RECEIPT")
    workerinput = getattr(config, "workerinput", {})
    _data["nonce"] = workerinput.get("um_arts_nonce") or _data["nonce"] or uuid.uuid4().hex
    _data["collection_only"] = bool(config.option.collectonly)
    processes = getattr(config.option, "numprocesses", None)
    if not managed and os.environ.get("UM_ARTS_CAPTURE_SERIAL") == "1":
        config.option.numprocesses = 0
        config.option.dist = "no"
        processes = 0
    _data["xdist"] = {
        "enabled": bool(workerinput) or processes not in (None, 0),
        "numprocesses": processes,
        "distribution": getattr(config.option, "dist", None),
        "worker_collections": {},
        "worker_receipts": {},
        "worker_errors": [],
    }
    if managed and processes not in (None, 0):
        raise pytest.UsageError("UM-ARTS forbids nested xdist workers")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_collection_modifyitems(config, items):
    yield
    if any(not item.path.resolve().is_relative_to(config.rootpath.resolve()) for item in items):
        raise pytest.UsageError("UM-ARTS refuses test identities outside its repository root")
    selection = os.environ.get("UM_ARTS_SELECTION")
    if selection:
        requested = json.loads(Path(selection).read_text(encoding="utf-8"))
        wanted = set(requested)
        excluded = [item for item in items if item.nodeid not in wanted]
        _data["partition_excluded"] = [item.nodeid for item in excluded]
        items[:] = [item for item in items if item.nodeid in wanted]
    _data["selected"] = [item.nodeid for item in items]


def pytest_deselected(items):
    _data["deselected"].extend(item.nodeid for item in items)


def pytest_collectreport(report):
    _data["collection"].append({
        "nodeid": report.nodeid,
        "outcome": report.outcome,
        "detail": str(report.longrepr) if report.failed or report.skipped else "",
    })


def pytest_runtest_logreport(report):
    _data["reports"].append({
        "nodeid": report.nodeid,
        "when": report.when,
        "outcome": report.outcome,
        "duration": report.duration,
        "wasxfail": str(report.wasxfail) if hasattr(report, "wasxfail") else None,
        "detail": str(report.longrepr) if report.failed or report.skipped else "",
        "worker_id": getattr(report, "worker_id", None),
    })


def pytest_internalerror(excrepr, excinfo):
    _data["internal_errors"].append(str(excrepr))


@pytest.hookimpl(optionalhook=True)
def pytest_configure_node(node):
    node.workerinput["um_arts_nonce"] = _data["nonce"]


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_node_collection_finished(node, ids):
    worker = node.workerinput["workerid"]
    _data["xdist"]["worker_collections"][worker] = list(ids)
    if not _data["selected"]:
        _data["selected"] = list(ids)
    elif _data["selected"] != list(ids):
        _data["internal_errors"].append(f"xdist collection mismatch: {worker}")


@pytest.hookimpl(optionalhook=True)
def pytest_testnodedown(node, error):
    worker = node.workerinput["workerid"]
    if error:
        _data["xdist"]["worker_errors"].append({"worker": worker, "error": str(error)})
    receipt = getattr(node, "workeroutput", {}).get("um_arts_collection")
    if not isinstance(receipt, dict):
        _data["xdist"]["worker_errors"].append({"worker": worker, "error": "missing worker receipt"})
        return
    _data["xdist"]["worker_receipts"][worker] = receipt
    if receipt.get("nonce") != _data["nonce"] or receipt.get("root") != _data["root"]:
        _data["internal_errors"].append(f"xdist worker identity mismatch: {worker}")
    _data["internal_errors"].extend(receipt.get("internal_errors", []))


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    _data["exitstatus"] = int(exitstatus)
    config = session.config
    if hasattr(config, "workerinput"):
        config.workeroutput["um_arts_collection"] = {
            key: _data[key] for key in ["version", "nonce", "root", "selected", "deselected",
                                       "partition_excluded", "collection", "reports",
                                       "internal_errors"]
        }
        return
    workers = _data["xdist"]["worker_receipts"]
    if workers:
        first = next(iter(workers.values()))
        _data["deselected"] = first["deselected"]
        _data["partition_excluded"] = first["partition_excluded"]
        # Collection runs independently on workers. Deduplicate repeated collection
        # reports while retaining every distinct collection failure/skip.
        collection = {json.dumps(item, sort_keys=True): item for item in _data["collection"]}
        for receipt in workers.values():
            collection.update({json.dumps(item, sort_keys=True): item
                               for item in receipt["collection"]})
        _data["collection"] = list(collection.values())
        reports = []
        for worker, receipt in workers.items():
            worker_reports = receipt.get("reports")
            if not isinstance(worker_reports, list):
                _data["internal_errors"].append(
                    f"xdist worker reports missing or malformed: {worker}")
                continue
            reports.extend(worker_reports)
        _data["reports"] = reports
    destination = Path(os.environ.get("UM_ARTS_RECEIPT") or os.environ["UM_ARTS_PYTEST_REPORT"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(_data, stream, sort_keys=True)
