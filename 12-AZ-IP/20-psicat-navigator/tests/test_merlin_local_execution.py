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
from ox_navigator.engine.merlin_memory import MerlinSession
from ox_navigator.engine.merlin_program import get_psicat_spc_phase0_execution_packet
from ox_navigator.engine.merlin_tools import route_tool


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


def test_local_execution_loop_accepts_repo_relative_cwd():
    result = run_local_execution_loop(
        command='python -c "import pathlib; print(pathlib.Path.cwd().name)"',
        cwd="12-AZ-IP/20-psicat-navigator",
    )
    assert result["ok"] is True
    assert result["execution"]["stdout"].strip() == "20-psicat-navigator"


def test_local_execution_loop_sanitizes_environment(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret-value")
    result = run_local_execution_loop(command='python -c "import os; print(os.getenv(\'OPENROUTER_API_KEY\', \'\'))"')
    assert result["ok"] is True
    assert result["execution"]["stdout"].strip() == ""


def test_local_execution_loop_timeout_fails_closed():
    result = run_local_execution_loop(
        command='python -c "import time; time.sleep(6)"',
        timeout_seconds=5,
    )
    assert result["ok"] is False
    assert result["governance"]["reason"] == "command_timeout"
    assert "timeout" in result["contract"]["body"].lower()


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
            good_canonical = client.post("/api/psicat/local-execution/run", json={"command": 'python -c "print(12)"'})
            assert good_canonical.status_code == 200
            assert good_canonical.json()["ok"] is True

            bad_phase0 = client.get("/api/merlin/spc-phase0-packet")
            assert bad_phase0.status_code == 422
            assert bad_phase0.json()["ok"] is False
            bad_phase0_canonical = client.get("/api/psicat/spc-phase0-packet")
            assert bad_phase0_canonical.status_code == 422
            assert bad_phase0_canonical.json()["ok"] is False
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


def test_phase0_packet_schema_validation_success_contract_fields():
    payload = get_psicat_spc_phase0_execution_packet()
    assert payload["ok"] is True
    assert payload["validation_error_count"] == 0
    assert payload["validation_errors"] == []


def test_phase0_packet_schema_validation_rejects_partial_lane_corruption(tmp_path, monkeypatch):
    from ox_navigator.engine import merlin_program as program

    canonical = get_psicat_spc_phase0_execution_packet()
    packet = dict(canonical["packet"])
    lanes = list(packet["lanes"])
    first = dict(lanes[0])
    first["focus"] = []
    lanes[0] = first
    packet["lanes"] = lanes
    bad_packet = tmp_path / "psicat_spc_phase0_execution_packet.json"
    bad_packet.write_text(json.dumps(packet), encoding="utf-8")
    monkeypatch.setattr(program, "PSICAT_SPC_PHASE0_PACKET_PATH", bad_packet)
    payload = get_psicat_spc_phase0_execution_packet()
    assert payload["ok"] is False
    assert payload["validation_error_count"] >= 1
    assert any("Lane[0] field 'focus'" in item for item in payload["validation_errors"])


def test_phase0_packet_schema_validation_rejects_missing_evidence_field(tmp_path, monkeypatch):
    from ox_navigator.engine import merlin_program as program

    canonical = get_psicat_spc_phase0_execution_packet()
    packet = dict(canonical["packet"])
    packet["evidence_packet_required_fields"] = [field for field in packet["evidence_packet_required_fields"] if field != "review_verdict"]
    bad_packet = tmp_path / "psicat_spc_phase0_execution_packet.json"
    bad_packet.write_text(json.dumps(packet), encoding="utf-8")
    monkeypatch.setattr(program, "PSICAT_SPC_PHASE0_PACKET_PATH", bad_packet)
    payload = get_psicat_spc_phase0_execution_packet()
    assert payload["ok"] is False
    assert payload["validation_error_count"] >= 1
    assert any("evidence_packet_required_fields missing required entries" in item for item in payload["validation_errors"])


def test_route_tool_psicat_achievement_session_passthrough(monkeypatch):
    from ox_navigator.engine import merlin_tools as tools

    captured: dict[str, object] = {}

    def _fake_packet(*, limit=3, training_limit=9, session=None):
        captured["session"] = session
        return {"ok": True, "limit": limit, "training_limit": training_limit}

    monkeypatch.setattr(tools, "get_psicat_achievement_benchmark_promotion_sprint", _fake_packet)
    monkeypatch.setitem(
        tools._FUNCTIONS,
        "getPsiCatAchievementBenchmarkPromotionSprint",
        lambda **args: {"data": tools.get_psicat_achievement_benchmark_promotion_sprint(
            limit=args.get("limit"),
            training_limit=args.get("training_limit"),
            session=args.get("__session") if isinstance(args.get("__session"), MerlinSession) else None,
        )},
    )

    active = MerlinSession()
    with_session = route_tool("getPsiCatAchievementBenchmarkPromotionSprint", {"limit": 2}, session=active)
    assert with_session["ok"] is True
    assert captured["session"] is active

    captured.clear()
    without_session = route_tool("getPsiCatAchievementBenchmarkPromotionSprint", {"limit": 2})
    assert without_session["ok"] is True
    assert isinstance(captured["session"], MerlinSession)


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
