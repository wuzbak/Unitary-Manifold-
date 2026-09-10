# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

from httpx import Client

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.app.server import serve
from ox_navigator.engine.merlin_testing_stack import get_psicat_prompt_contracts, get_psicat_testing_stack


def test_psicat_testing_stack_engine_shape() -> None:
    payload = get_psicat_testing_stack()
    assert payload["browser_default"]["tool"] == "Playwright"
    assert payload["product24_parallel_branch_role"].startswith("Product 24's Playwright and Node validation lane is merged")
    assert payload["psicat"]["ai_evaluation_lane"]["prompt_contract_case_count"] >= 3
    assert "/api/psicat/testing-stack" in payload["psicat"]["api_lane"]["required_endpoints"]
    assert payload["integration_classes"]["class_a"]["products"][0]["id"] == 17


def test_psicat_prompt_contracts_manifest_shape() -> None:
    contracts = get_psicat_prompt_contracts()
    assert contracts["suite"] == "psicat_prompt_contracts"
    assert "hallucination_resistance" in contracts["quality_dimensions"]
    assert all("FOLLOWUPS:" in case["required_contract_sections"] for case in contracts["cases"])
    assert any("/api/psicat/telemetry" in case["observability_endpoints"] for case in contracts["cases"])


def test_psicat_testing_stack_endpoint_exposes_machine_readable_doctrine() -> None:
    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with Client(base_url=f"http://127.0.0.1:{httpd.server_port}") as client:
            response = client.get("/api/psicat/testing-stack")
            assert response.status_code == 200
            payload = response.json()
            assert payload["ok"] is True
            assert payload["testing_stack"]["browser_default"]["tool"] == "Playwright"
            assert payload["testing_stack"]["psicat"]["ai_evaluation_lane"]["prompt_contract_case_count"] >= 3
            assert payload["prompt_contracts"]["suite"] == "psicat_prompt_contracts"
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)


def test_shared_testing_manifest_and_prompt_contract_files_are_valid_json() -> None:
    manifest = PRODUCT_ROOT.parents[0] / "tools" / "testing_stack_manifest.json"
    prompt_contracts = PRODUCT_ROOT / "testing" / "psicat_prompt_contracts.json"
    assert json.loads(manifest.read_text(encoding="utf-8"))["browser_default"]["tool"] == "Playwright"
    assert len(json.loads(prompt_contracts.read_text(encoding="utf-8"))["cases"]) >= 3
