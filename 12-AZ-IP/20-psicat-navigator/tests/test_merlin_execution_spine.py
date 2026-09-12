# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import sys
import threading
from pathlib import Path

import httpx

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.app.server import serve
from ox_navigator.engine.merlin_benchmark import build_stage_a_artifact_bundle
from ox_navigator.engine.merlin_program import build_training_artifact_bundle, get_psicat_convergence_charter


def test_convergence_charter_surface_and_artifacts() -> None:
    charter = get_psicat_convergence_charter()
    assert charter["execution_spine"]["surface_id"] == "psicat_convergence_charter"
    assert charter["completion_maps"]["primary_targets"][0] == "12-AZ-IP/20-psicat-navigator"

    stage_a = build_stage_a_artifact_bundle(limit=1)
    assert stage_a["artifact_bundle"]["execution_spine"]["surface_kind"] == "benchmark_artifact_bundle"

    training = build_training_artifact_bundle(limit=1)
    assert training["artifact_bundle"]["execution_spine"]["surface_kind"] == "training_artifact_bundle"
    assert training["artifact_bundle"]["convergence_charter"]["document_path"] == (
        "9-INFRASTRUCTURE/EXECUTION_SPINE_CONVERGENCE_CHARTER.md"
    )


def test_server_convergence_charter_endpoint() -> None:
    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=10.0) as client:
            response = client.get("/api/merlin/convergence-charter")
            assert response.status_code == 200
            payload = response.json()
            assert payload["ok"] is True
            assert payload["convergence_charter"]["document_path"] == (
                "9-INFRASTRUCTURE/EXECUTION_SPINE_CONVERGENCE_CHARTER.md"
            )
    finally:
        httpd.shutdown()
        thread.join(timeout=5)
