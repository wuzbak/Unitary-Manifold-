# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""HTTP security boundaries and operational, evidence-backed local workflows."""

import http.client
import importlib
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from tests.test_um_arts import arts_workspace as _arts_workspace

PRODUCT = Path(__file__).resolve().parents[1] / "12-AZ-IP" / "26-um-arts"
sys.path.insert(0, str(PRODUCT))
server_module = importlib.import_module("um_arts.server")
Application = server_module.Application
LocalServer = server_module.LocalServer
EvidenceError = server_module.EvidenceError
arts_workspace = _arts_workspace


def repository(workspace, source="def test_ok(): assert True\n"):
    root = workspace / "repository"
    root.mkdir()
    (root / "tests").mkdir()
    (root / "tests" / "test_small.py").write_text(source, encoding="utf-8")
    config = workspace / "config.json"
    config.write_text(json.dumps({
        "adapter": "generic", "suites": [{"name": "unit", "paths": ["tests"]}],
        "timeout_seconds": 20,
    }), encoding="utf-8")
    return root, workspace / ".um-arts", config


@pytest.fixture
def http_app(arts_workspace):
    root, store, config = repository(arts_workspace)
    app = Application(root, store, config, "generic")
    server = LocalServer(app, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield app, server
    server.shutdown()
    server.server_close()
    thread.join()
    app.close()


def request(server, path, payload=None, *, headers=None, raw=None, method=None):
    connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=10)
    body = raw if raw is not None else json.dumps(payload) if payload is not None else None
    supplied = {"Content-Type": "application/json"} if body is not None else {}
    supplied.update(headers or {})
    connection.request(method or ("POST" if body is not None else "GET"), path, body, supplied)
    response = connection.getresponse()
    data = response.read()
    result = json.loads(data) if response.getheader("Content-Type") == "application/json" else data
    status, response_headers = response.status, dict(response.getheaders())
    connection.close()
    return status, result, response_headers


def submit(server, token, action, artifact_id=None):
    payload = {"action": action}
    if artifact_id is not None:
        payload["id"] = artifact_id
    status, result, _ = request(server, "/api/tasks", payload,
                                headers={"X-UM-ARTS-Token": token})
    assert status == 202, result
    return result


def wait_task(server, task_id):
    end = time.monotonic() + 30
    while time.monotonic() < end:
        status, result, _ = request(server, "/api/tasks/" + task_id)
        assert status == 200, result
        if result["status"] not in {"queued", "running"}:
            return result
        time.sleep(.03)
    pytest.fail("Local task did not finish")


def test_health_preflight_session_offline_ui(http_app):
    app, server = http_app
    assert request(server, "/api/health")[1]["status"] == "ok"
    status, preflight, _ = request(server, "/api/preflight")
    assert status == 200 and preflight["status"] == "ready"
    assert preflight["tools"]["pytest"]
    assert preflight["root"] == str(app.root)
    status, session, headers = request(server, "/api/session")
    assert status == 200 and session["token"] == app.token and len(app.token) >= 32
    assert headers["Cache-Control"] == "no-store"
    for path in ("/", "/app.js", "/style.css"):
        status, body, headers = request(server, path)
        assert status == 200 and body
        assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    script = request(server, "/app.js")[1].decode()
    assert "innerHTML" not in script and "setInterval" in script
    assert "textContent" in script and "submit(" in script
    html = request(server, "/")[1].decode()
    assert "Checks can modify the selected repository" in html
    assert "directly does not make the original checkout immutable" in html
    assert "snapshot --root TRUSTED_REPO --output ISOLATED_COPY" in html
    assert "serve --root ISOLATED_COPY/source --store STORE_OUTSIDE_SOURCE" in html
    assert html.index("Execution warning:") < html.index('id="plan"')


@pytest.mark.parametrize("failure", ["starting_log", "running_state", "finished_log"])
def test_transient_task_io_failure_does_not_strand_next_task(http_app, monkeypatch, failure):
    app, server = http_app
    original_log, original_save = app._log, app._save
    injected = []

    def log(task_id, message):
        trigger = message.startswith("Starting" if failure == "starting_log" else "Finished")
        if failure != "running_state" and trigger and not injected:
            injected.append(task_id)
            raise OSError("transient log failure")
        original_log(task_id, message)

    def save(task):
        if failure == "running_state" and task["status"] == "running" and not injected:
            injected.append(task["id"])
            raise OSError("transient persistence failure")
        original_save(task)

    monkeypatch.setattr(app, "_log", log)
    monkeypatch.setattr(app, "_save", save)
    monkeypatch.setattr(server_module.engine, "plan", lambda *args: {"status": "ready"})
    first = submit(server, app.token, "plan")
    assert wait_task(server, first["id"])["status"] == "blocked"
    app.pending.join()
    assert app.active is None and app.worker.is_alive()
    second = submit(server, app.token, "plan")
    assert wait_task(server, second["id"])["status"] == "ready"
    app.pending.join()
    assert app.active is None and app.worker_error is None


def test_terminal_persistence_failure_disables_new_submissions(http_app, monkeypatch):
    app, server = http_app
    original_save = app._save

    def save(task):
        if task["status"] not in {"queued", "running"}:
            raise OSError("evidence disk unavailable")
        original_save(task)

    monkeypatch.setattr(app, "_save", save)
    monkeypatch.setattr(server_module.engine, "plan", lambda *args: {"status": "ready"})
    first = submit(server, app.token, "plan")
    app.pending.join()
    assert app.task(first["id"])["status"] == "blocked"
    assert app.active is None and app.worker.is_alive()
    assert app.preflight()["status"] == "blocked"
    assert "disk unavailable" in app.preflight()["queue_error"]
    with pytest.raises(EvidenceError, match="unavailable"):
        app.submit({"action": "plan"})


@pytest.mark.parametrize("persistent", [False, True])
def test_submission_log_failure_never_leaves_unqueued_pending_task(http_app, monkeypatch, persistent):
    app, _ = http_app
    original_save = app._save

    def failed_log(*args):
        raise OSError("queue log failure")

    monkeypatch.setattr(app, "_log", failed_log)

    def save(task):
        if persistent and task["status"] == "blocked":
            raise OSError("failure record unavailable")
        original_save(task)

    monkeypatch.setattr(app, "_save", save)
    with pytest.raises(EvidenceError, match="submission failed"):
        app.submit({"action": "plan"})
    assert app.pending.empty()
    assert all(task["status"] == "blocked" for task in app.tasks())
    assert len(app.tasks()) == 1
    assert bool(app.worker_error) == persistent
    assert app.worker.is_alive()


def test_cli_serve_parser_and_dispatch(arts_workspace, monkeypatch):
    cli = importlib.import_module("um_arts.__main__")
    captured = []
    monkeypatch.setattr(server_module, "serve", lambda *args: captured.append(args) or 0)
    root, store, config = repository(arts_workspace)
    assert cli.main(["serve", "--root", str(root), "--store", str(store),
                     "--config", str(config), "--adapter", "generic", "--mode", "changed",
                     "--host", "127.0.0.1", "--port", "8769"]) == 0
    assert captured == [(root, store, config, "generic", "changed", "127.0.0.1", 8769)]
    defaults = cli.parser().parse_args(["serve"])
    assert defaults.host == "127.0.0.1" and defaults.port == 8765
    assert defaults.adapter == "um" and defaults.mode == "full"


@pytest.mark.parametrize("token", [None, "", "wrong-token", "caf\xe9"])
def test_unauthorized_mutation(http_app, token):
    app, server = http_app
    headers = {} if token is None else {"X-UM-ARTS-Token": token}
    assert request(server, "/api/tasks", {"action": "plan"}, headers=headers)[0] == 403
    assert app.tasks() == []


@pytest.mark.parametrize("headers", [
    {"Origin": "https://evil.example"},
    {"Origin": "null"},
    {"Host": "evil.example"},
    {"Host": "127.0.0.1.evil.example:8765"},
    {"Sec-Fetch-Site": "cross-site"},
    {"Sec-Fetch-Site": "same-site"},
])
def test_csrf_and_host_rebinding_rejected(http_app, headers):
    app, server = http_app
    headers = {**headers, "X-UM-ARTS-Token": app.token}
    assert request(server, "/api/tasks", {"action": "plan"}, headers=headers)[0] == 403
    assert request(server, "/api/session", headers=headers)[0] == 403
    assert not app.tasks()


def test_same_origin_mutation_and_token_rotation(http_app, monkeypatch):
    app, server = http_app
    monkeypatch.setattr(server_module.engine, "plan", lambda *args: {"status": "blocked", "errors": ["no evidence"]})
    headers = {"Origin": server.url, "X-UM-ARTS-Token": app.token, "Sec-Fetch-Site": "same-origin"}
    status, task, _ = request(server, "/api/tasks", {"action": "plan"}, headers=headers)
    assert status == 202
    assert wait_task(server, task["id"])["status"] == "blocked"
    other_store = app.store.parent / "another-store"
    second = Application(app.root, other_store, app.config, "generic")
    try:
        assert app.token != second.token
    finally:
        second.close()


@pytest.mark.parametrize("payload", [
    {"action": "plan", "root": "/etc"},
    {"action": "plan", "config": "untrusted.json"},
    {"action": "plan", "command": ["echo", "bad"]},
    {"action": "capture"},
    {"action": "run", "id": "../etc/passwd"},
    {"action": "resume", "id": "/etc/passwd"},
    {"action": "run", "id": "f" * 32, "path": "somewhere"},
    {"action": "run", "id": ["bad"]},
    {"action": "plan", "mode": "changed"},
    [],
])
def test_no_client_paths_configs_or_commands(http_app, payload):
    app, server = http_app
    assert request(server, "/api/tasks", payload, headers={"X-UM-ARTS-Token": app.token})[0] == 400
    assert not app.tasks()


@pytest.mark.parametrize("raw,status", [
    ("x" * (server_module.MAX_BODY + 1), 413),
    ('{"action":"plan","action":"plan"}', 400),
    ('{"action":NaN}', 400),
    ("{", 400),
    ("[" * 1500 + "]" * 1500, 400),
])
def test_bounded_strict_json(http_app, raw, status):
    app, server = http_app
    assert request(server, "/api/tasks", raw=raw,
                   headers={"X-UM-ARTS-Token": app.token})[0] == status
    assert not app.tasks()


def test_bad_content_type_and_transfer_encoding(http_app):
    app, server = http_app
    headers = {"X-UM-ARTS-Token": app.token, "Content-Type": "text/plain"}
    assert request(server, "/api/tasks", {"action": "plan"}, headers=headers)[0] == 415
    headers = {"X-UM-ARTS-Token": app.token, "Transfer-Encoding": "chunked"}
    assert request(server, "/api/tasks", {"action": "plan"}, headers=headers)[0] == 400


def test_serialized_queue_preserves_engine_status(http_app, monkeypatch):
    app, server = http_app
    entered, release = threading.Event(), threading.Event()
    calls = []

    def plan(*args):
        calls.append(args)
        entered.set()
        assert release.wait(5)
        return {"status": "blocked", "errors": ["deliberately unverified"]}

    monkeypatch.setattr(server_module.engine, "plan", plan)
    first = submit(server, app.token, "plan")
    assert entered.wait(5)
    second = submit(server, app.token, "plan")
    assert request(server, "/api/tasks/" + second["id"])[1]["status"] == "queued"
    assert len(calls) == 1
    release.set()
    assert wait_task(server, first["id"])["status"] == "blocked"
    assert wait_task(server, second["id"])["status"] == "blocked"
    assert len(calls) == 2 and calls[0] == (
        app.root, app.store, app.config, "generic", "full")
    logs = request(server, f"/api/tasks/{first['id']}/logs")[1]["text"]
    assert "Queued plan" in logs and "status: blocked" in logs


def test_missing_engine_status_never_passes(http_app, monkeypatch):
    app, server = http_app
    monkeypatch.setattr(server_module.engine, "plan", lambda *args: {"counts": {"passed": 1}})
    task = wait_task(server, submit(server, app.token, "plan")["id"])
    assert task["status"] == "blocked"
    assert "recognized evidence status" in task["error"]


def test_mocked_run_resume_receive_only_contained_preselected_artifacts(http_app, monkeypatch):
    app, server = http_app
    trusted = {"root": str(app.root), "store": str(app.store),
               "config": server_module.load_config(app.root, app.config, "generic"),
               "config_source": {"path": str(app.config)}}
    monkeypatch.setattr(server_module.engine, "validate_plan", lambda path: trusted)
    plan_id, attempt_id = "1" * 32, "2" * 32
    plan_dir = app.store / "plans" / plan_id
    plan_dir.mkdir(parents=True)
    (plan_dir / "plan.json").write_text("{}")
    attempt_dir = app.store / "attempts" / attempt_id
    (attempt_dir / "plan").mkdir(parents=True)
    calls = []

    def run(path):
        calls.append(("run", path))
        return {"status": "blocked", "errors": ["mocked execution"]}

    def resume(path):
        calls.append(("resume", path))
        return {"status": "incomplete", "errors": ["mocked incomplete"]}

    monkeypatch.setattr(server_module.engine, "run", run)
    monkeypatch.setattr(server_module.engine, "resume", resume)
    assert wait_task(server, submit(server, app.token, "run", plan_id)["id"])["status"] == "blocked"
    assert wait_task(server, submit(server, app.token, "resume", attempt_id)["id"])["status"] == "incomplete"
    assert calls == [("run", plan_dir / "plan.json"), ("resume", attempt_dir)]
    trusted["root"] = str(app.root.parent)
    status, result, _ = request(server, "/api/tasks", {"action": "run", "id": plan_id},
                                headers={"X-UM-ARTS-Token": app.token})
    assert status == 400 and "trusted execution inputs" in result["error"]
    assert len(calls) == 2


def test_bounded_queue_backpressure(http_app, monkeypatch):
    app, server = http_app
    entered, release = threading.Event(), threading.Event()

    def plan(*args):
        entered.set()
        assert release.wait(15)
        return {"status": "blocked"}

    monkeypatch.setattr(server_module.engine, "plan", plan)
    submit(server, app.token, "plan")
    assert entered.wait(5)
    try:
        for _ in range(server_module.MAX_QUEUE):
            submit(server, app.token, "plan")
        status, result, _ = request(server, "/api/tasks", {"action": "plan"},
                                    headers={"X-UM-ARTS-Token": app.token})
        assert status == 400 and "queue is full" in result["error"]
        assert len(app.tasks()) == server_module.MAX_QUEUE + 1
    finally:
        release.set()


def test_duplicate_security_headers_rejected(http_app):
    app, server = http_app
    for duplicated in ("Host", "Origin", "X-UM-ARTS-Token", "Content-Length"):
        connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
        body = '{"action":"plan"}'
        connection.putrequest("POST", "/api/tasks", skip_host=True)
        values = {"Host": f"127.0.0.1:{server.server_address[1]}",
                  "Origin": server.url, "X-UM-ARTS-Token": app.token,
                  "Content-Type": "application/json", "Content-Length": str(len(body))}
        for name, value in values.items():
            connection.putheader(name, value)
            if name == duplicated:
                connection.putheader(name, value)
        connection.endheaders(body.encode())
        response = connection.getresponse()
        assert response.status in {400, 403}
        response.read()
        connection.close()
    assert not app.tasks()


def test_log_tail_is_bounded_and_symlink_safe(http_app):
    app, server = http_app
    task_id = "7" * 32
    app._save({"id": task_id, "status": "blocked", "action": "plan", "created": time.time()})
    app._task_path(task_id, "log").write_text("x" * (server_module.MAX_LOG * 2))
    text = request(server, f"/api/tasks/{task_id}/logs")[1]["text"]
    assert len(text) == server_module.MAX_LOG
    app._task_path(task_id, "log").unlink()
    app._task_path(task_id, "log").symlink_to(app.config)
    assert request(server, f"/api/tasks/{task_id}/logs")[0] == 400


def test_restart_marks_queued_and_running_incomplete(arts_workspace):
    root, store, config = repository(arts_workspace)
    app = Application(root, store, config, "generic")
    app.close()
    for state, task_id in (("queued", "a" * 32), ("running", "b" * 32)):
        app._save({"id": task_id, "status": state, "created": time.time(), "action": "plan"})
    restarted = Application(root, store, config, "generic")
    try:
        assert {task["status"] for task in restarted.tasks()} == {"incomplete"}
        assert restarted.pending.empty()
        assert "not automatically resumed" in restarted.logs("a" * 32)
    finally:
        restarted.close()


def test_exclusive_store_lifecycle_lock_preserves_active_tasks(http_app, monkeypatch):
    app, server = http_app
    entered, release = threading.Event(), threading.Event()

    def plan(*args):
        entered.set()
        assert release.wait(10)
        return {"status": "blocked"}

    monkeypatch.setattr(server_module.engine, "plan", plan)
    task = submit(server, app.token, "plan")
    assert entered.wait(5)
    try:
        with pytest.raises(EvidenceError, match="Another UM-ARTS server"):
            Application(app.root, app.store, app.config, "generic")
        code = (
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0,sys.argv[1])\n"
            "from um_arts.server import Application, EvidenceError\n"
            "try:\n"
            " app=Application(Path(sys.argv[2]),Path(sys.argv[3]),Path(sys.argv[4]),'generic')\n"
            "except EvidenceError as exc:\n"
            " print(str(exc))\n"
            " sys.exit(0 if 'Another UM-ARTS server' in str(exc) else 2)\n"
            "app.close()\n"
            "sys.exit(1)\n"
        )
        result = subprocess.run([sys.executable, "-c", code, str(PRODUCT), str(app.root),
                                 str(app.store), str(app.config)], capture_output=True,
                                text=True, timeout=5, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
        assert app.task(task["id"])["status"] == "running"
    finally:
        release.set()
    assert wait_task(server, task["id"])["status"] == "blocked"


def test_store_lease_released_after_close(arts_workspace):
    root, store, config = repository(arts_workspace)
    app = Application(root, store, config, "generic")
    app.close()
    app.close()
    replacement = Application(root, store, config, "generic")
    replacement.close()
    assert (store / ".server.lock").is_file()


@pytest.mark.parametrize("host", ["0.0.0.0", "192.0.2.1", "::", "evil.example"])
def test_remote_binding_forbidden(http_app, host):
    app, _ = http_app
    with pytest.raises(EvidenceError, match="loopback|Remote"):
        LocalServer(app, host=host, port=0)


def test_symlink_artifacts_and_task_logs_rejected(http_app):
    app, server = http_app
    outside = app.store.parent / "outside"
    outside.mkdir()
    (app.store / "plans").mkdir()
    (app.store / "plans" / ("a" * 32)).symlink_to(outside, target_is_directory=True)
    assert request(server, "/api/artifacts/plans/" + "a" * 32)[0] == 400
    assert request(server, "/api/artifacts")[1] == []
    (app.store / "tasks" / ("b" * 32 + ".json")).symlink_to(app.config)
    assert request(server, "/api/tasks/" + "b" * 32)[0] == 400
    assert request(server, "/api/tasks/%2e%2e")[0] == 400
    assert request(server, "/api/artifacts/plans/" + "c" * 32 + "?path=/etc/passwd")[0] == 400


@pytest.mark.slow
def test_actual_generic_plan_run_resume_read_only_report(http_app, monkeypatch):
    app, server = http_app
    plan_task = wait_task(server, submit(server, app.token, "plan")["id"])
    assert plan_task["status"] == "ready", plan_task
    plan_id = plan_task["artifact"]["id"]
    run_task = wait_task(server, submit(server, app.token, "run", plan_id)["id"])
    assert run_task["status"] == "passed", run_task
    attempt_id = run_task["artifact"]["id"]
    status, evidence, _ = request(server, "/api/artifacts/attempts/" + attempt_id)
    assert status == 200 and evidence["status"] == "passed"
    assert evidence["counts"] == {"passed": 1}
    logs = request(server, "/api/tasks/" + run_task["id"] + "/logs")[1]["text"]
    assert "1 passed" in logs
    resumed = wait_task(server, submit(server, app.token, "resume", attempt_id)["id"])
    assert resumed["status"] == "passed", resumed
    assert resumed["artifact"]["id"] != attempt_id
    imported = server_module.engine.import_artifact(app.store / "attempts" / attempt_id, app.store)
    imported_id = Path(imported["attempt_path"]).name

    def no_execution(*args, **kwargs):
        pytest.fail("Read-only reporting must not execute engine tasks")

    monkeypatch.setattr(server_module.engine, "run", no_execution)
    monkeypatch.setattr(server_module.engine, "resume", no_execution)
    assert len(request(server, "/api/artifacts")[1]) == 4
    assert request(server, "/api/artifacts/plans/" + plan_id)[1]["status"] == "ready"
    assert request(server, "/api/artifacts/attempts/" + attempt_id)[1]["status"] == "passed"
    assert request(server, "/api/artifacts/imports/" + imported_id)[1]["status"] == "passed"


@pytest.mark.slow
def test_actual_failed_test_remains_blocked(http_app):
    app, server = http_app
    (app.root / "tests" / "test_small.py").write_text("def test_bad(): assert False\n", encoding="utf-8")
    planned = wait_task(server, submit(server, app.token, "plan")["id"])
    assert planned["status"] == "ready", planned
    task = wait_task(server, submit(server, app.token, "run", planned["artifact"]["id"])["id"])
    assert task["status"] == "blocked", task
    assert task["result"]["counts"]["failed"] == 1


@pytest.mark.slow
def test_source_changes_block_both_old_plan_and_resume(http_app):
    app, server = http_app
    planned = wait_task(server, submit(server, app.token, "plan")["id"])
    assert planned["status"] == "ready", planned
    run = wait_task(server, submit(server, app.token, "run", planned["artifact"]["id"])["id"])
    assert run["status"] == "passed", run
    (app.root / "tests" / "test_small.py").write_text("def test_changed(): assert True\n")
    for action, artifact_id in (("run", planned["artifact"]["id"]),
                                ("resume", run["artifact"]["id"])):
        task = wait_task(server, submit(server, app.token, action, artifact_id)["id"])
        assert task["status"] == "blocked" and task["result"] is None, task
        assert "no longer compatible" in task["error"], task
    assert len(app._artifact_ids("attempts")) == 1


@pytest.mark.slow
@pytest.mark.parametrize("capture_kind,expected", [
    ("pytest", "passed"), ("collection", "collection_passed"), ("command", "command_passed"),
])
def test_imported_captures_are_read_only_and_keep_scoped_status(http_app, monkeypatch,
                                                               capture_kind, expected):
    app, server = http_app
    capture = importlib.import_module("um_arts.capture")
    (app.root / "pytest.ini").write_text("[pytest]\n")
    command = ([sys.executable, "-c", "print('captured command')"] if capture_kind == "command"
               else [sys.executable, "-m", "pytest", "-q",
                     *(["--collect-only"] if capture_kind == "collection" else [])])
    # Trusted CLI capture output is outside the server's indexed store.
    output = app.store.parent / "external-capture"
    captured = capture.capture_command(command, output, app.root, timeout_seconds=20)
    assert captured["status"] == expected, captured
    assert request(server, "/api/artifacts")[1] == []
    imported = server_module.engine.import_artifact(output, app.store)
    imported_id = Path(imported["attempt_path"]).name

    def no_execution(*args, **kwargs):
        pytest.fail("Imported capture inspection must not execute commands")

    monkeypatch.setattr(subprocess, "Popen", no_execution)
    listed = request(server, "/api/artifacts")[1]
    assert len(listed) == 1 and listed[0] == {
        "kind": "imports", "id": imported_id, "status": "unverified", "verified": False,
        "evidence_kind": "capture", "resumable": False,
    }
    status, evidence, _ = request(server, "/api/artifacts/imports/" + imported_id)
    assert status == 200 and evidence["status"] == expected
    assert evidence["proof_claim"] is False
    assert evidence["test_gate"] is (capture_kind == "pytest")
    assert request(server, "/api/artifacts/imports/" + imported_id + "/logs")[0] == 200
    assert request(server, "/api/tasks", {"action": "resume", "id": imported_id},
                   headers={"X-UM-ARTS-Token": app.token})[0] == 400
    assert not app.tasks()
    script = request(server, "/app.js")[1].decode()
    assert 'artifact.kind === "plans" || artifact.resumable' in script
