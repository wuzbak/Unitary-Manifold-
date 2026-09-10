# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import json
import os
import importlib.util
import sys
import threading
from pathlib import Path

import httpx

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.app.server import serve
from ox_navigator.engine.merlin_local_execution import get_local_execution_status, run_local_execution_loop
from ox_navigator.engine.merlin_program import get_psicat_spc_phase0_execution_packet


def test_local_execution_status_includes_fail_closed_policy():
    status = get_local_execution_status()
    assert status["mode"] == "fail_closed_local_execution_loop"
    assert "python" in status["allowed_commands"]
    assert status["policy"]["execution_shell"] == "disabled"


def test_local_execution_loop_runs_allowlisted_python():
    result = run_local_execution_loop(command='python -c "print(7)"')
    assert result["ok"] is True
    assert result["execution"]["returncode"] == 0
    assert "passed" in result["contract"]["body"]


def test_local_execution_loop_blocks_unallowlisted_command():
    result = run_local_execution_loop(command="cat /etc/hosts")
    assert result["ok"] is False
    assert "allowlisted" in result["error"]
    assert result["governance"]["fail_closed"] is True


def test_local_execution_loop_blocks_path_qualified_command():
    result = run_local_execution_loop(command='/usr/bin/python3 -c "print(1)"')
    assert result["ok"] is False
    assert "Path-qualified executables" in result["error"]
    assert result["governance"]["reason"] == "path_qualified_executable_forbidden"


def test_local_execution_loop_rejects_out_of_repo_cwd():
    result = run_local_execution_loop(command='python -c "print(1)"', cwd="/tmp")
    assert result["ok"] is False
    assert "outside repository" in result["contract"]["body"]


def test_server_local_execution_endpoints_and_phase0_packet_validation(monkeypatch):
    from ox_navigator.app import server as server_module

    original_env = os.environ.get("MERLIN_LOCAL_EXECUTION_ENABLED")
    os.environ["MERLIN_LOCAL_EXECUTION_ENABLED"] = "1"
    monkeypatch.setattr(
        server_module,
        "get_psicat_spc_phase0_execution_packet",
        lambda: {"ok": False, "error": "schema invalid", "validation_error_count": 1, "validation_errors": ["x"]},
    )
    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=10.0) as client:
            status = client.get("/api/merlin/local-execution/status")
            assert status.status_code == 200
            assert status.json()["ok"] is True
            assert status.json()["local_execution_status"]["enabled"] is True
            canonical_status = client.get("/api/psicat/local-execution/status")
            assert canonical_status.status_code == 200
            assert canonical_status.json()["ok"] is True

            blocked = client.post("/api/merlin/local-execution/run", json={"command": "cat /etc/hosts"})
            assert blocked.status_code == 403
            assert blocked.json()["ok"] is False

            good = client.post("/api/merlin/local-execution/run", json={"command": 'python -c "print(11)"'})
            assert good.status_code == 200
            assert good.json()["ok"] is True
            assert good.json()["local_execution"]["execution"]["returncode"] == 0

            bad_phase0 = client.get("/api/merlin/spc-phase0-packet")
            assert bad_phase0.status_code == 422
            assert bad_phase0.json()["ok"] is False
    finally:
        if original_env is None:
            os.environ.pop("MERLIN_LOCAL_EXECUTION_ENABLED", None)
        else:
            os.environ["MERLIN_LOCAL_EXECUTION_ENABLED"] = original_env
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_server_phase0_packet_backend_failure_returns_500(monkeypatch):
    from ox_navigator.app import server as server_module

    monkeypatch.setattr(
        server_module,
        "get_psicat_spc_phase0_execution_packet",
        lambda: {"ok": False, "error": "Unable to load phase-0 packet artifact: boom"},
    )
    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=10.0) as client:
            response = client.get("/api/merlin/spc-phase0-packet")
            assert response.status_code == 500
            assert response.json()["ok"] is False
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_phase0_packet_schema_validation_fails_closed(tmp_path, monkeypatch):
    from ox_navigator.engine import merlin_program as program

    bad_packet = tmp_path / "psicat_spc_phase0_execution_packet.json"
    bad_packet.write_text(json.dumps({"ok": True}), encoding="utf-8")
    monkeypatch.setattr(program, "PSICAT_SPC_PHASE0_PACKET_PATH", bad_packet)
    payload = get_psicat_spc_phase0_execution_packet()
    assert payload["ok"] is False
    assert payload["validation_error_count"] > 0
    assert "fail-closed schema validation" in payload["error"]


def test_run_py_local_execution_flags_wire_environment(monkeypatch):
    script_path = PRODUCT_ROOT / "run.py"
    spec = importlib.util.spec_from_file_location("psicat_run", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class _DummyServer:
        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            return None

    monkeypatch.setattr(module, "serve", lambda **kwargs: _DummyServer())
    monkeypatch.setenv("MERLIN_LOCAL_EXECUTION_ENABLED", "1")
    monkeypatch.delenv("MERLIN_LOCAL_EXECUTION_ALLOWED_COMMANDS", raising=False)
    rc = module.main([
        "--local-execution", "off",
        "--local-execution-timeout", "33",
        "--local-execution-allowlist", "python,pytest",
        "--no-open",
    ])
    assert rc == 0
    assert os.environ["MERLIN_LOCAL_EXECUTION_ENABLED"] == "0"
    assert os.environ["MERLIN_LOCAL_EXECUTION_MAX_TIMEOUT"] == "33"
    assert os.environ["MERLIN_LOCAL_EXECUTION_ALLOWED_COMMANDS"] == "python,pytest"


def test_run_py_local_execution_timeout_has_lower_bound(monkeypatch):
    script_path = PRODUCT_ROOT / "run.py"
    spec = importlib.util.spec_from_file_location("psicat_run", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class _DummyServer:
        def serve_forever(self):
            raise KeyboardInterrupt

        def server_close(self):
            return None

    monkeypatch.setattr(module, "serve", lambda **kwargs: _DummyServer())
    rc = module.main(["--local-execution-timeout", "1", "--no-open"])
    assert rc == 0
    assert os.environ["MERLIN_LOCAL_EXECUTION_MAX_TIMEOUT"] == "5"
