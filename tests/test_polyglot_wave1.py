import json
from pathlib import Path

import numpy as np
import pytest

from src.core.evolution import FieldState, rhs_backend_report
from src.core.julia_acceleration import benchmark_callable, parity_report
from src.core.metric import compute_curvature, compute_curvature_backend
from src.core.polyglot_execution_matrix import (
    PolyglotExecutionConfig,
    load_polyglot_execution_config,
    no_regression_gate,
    polyglot_lane_matrix,
)
from src.core.sm_parameter_ledger import LedgerRecord, SmParameterLedger


def _flat_fields(N: int = 12):
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1))
    B = np.zeros((N, 4))
    phi = np.ones(N)
    return g, B, phi


def test_compute_curvature_backend_python_matches_reference():
    g, B, phi = _flat_fields()
    ref = compute_curvature(g, B, phi, dx=0.1, lam=1.0)
    got = compute_curvature_backend(g, B, phi, dx=0.1, lam=1.0, backend="python")
    for a, b in zip(ref, got):
        np.testing.assert_allclose(a, b, atol=1e-14)


def test_compute_curvature_backend_rejects_unknown_backend():
    g, B, phi = _flat_fields()
    with pytest.raises(ValueError, match="Unsupported backend"):
        compute_curvature_backend(g, B, phi, dx=0.1, backend="not-a-backend")


def test_polyglot_config_defaults_are_safe():
    cfg = load_polyglot_execution_config()
    assert isinstance(cfg, PolyglotExecutionConfig)
    assert cfg.core_backend in {"python", "julia"}
    assert cfg.parity_rtol > 0
    assert cfg.parity_atol > 0


def test_lane_matrix_contains_requested_tracks():
    lanes = polyglot_lane_matrix()
    for key in (
        "julia_acceleration",
        "julia_cuda_scaling",
        "lean4_formal_lane",
        "symbolic_validation_lane",
        "rust_safety_lane",
        "typescript_dashboard_lane",
        "shader_visual_lane",
        "duckdb_ledger_lane",
        "mojo_lane",
        "cpp_cuda_lane",
    ):
        assert key in lanes


def test_no_regression_gate_zero_failure_only():
    assert no_regression_gate(0) is True


def test_parity_report_detects_exact_match():
    x = (np.array([1.0, 2.0]), np.array([[3.0]]))
    y = (np.array([1.0, 2.0]), np.array([[3.0]]))
    verdict = parity_report(x, y)
    assert verdict["parity_passed"] is True
    assert verdict["max_abs_error"] == 0.0


def test_benchmark_callable_emits_summary():
    result = benchmark_callable(sum, [1, 2, 3], repeats=2)
    assert result["min_seconds"] >= 0.0
    assert result["max_seconds"] >= result["min_seconds"]


def test_rhs_backend_report_python_path():
    state = FieldState.flat(N=8, dx=0.1, rng=np.random.default_rng(3))
    report = rhs_backend_report(state)
    assert report["backend"] in {"python", "julia"}
    if report["backend"] == "python":
        assert report["parity_checked"] is False


def test_sm_parameter_ledger_round_trip(tmp_path):
    pytest.importorskip("duckdb")
    db = tmp_path / "sm_ledger.duckdb"
    ledger = SmParameterLedger(str(db))
    inserted = ledger.insert_many(
        [
            LedgerRecord(
                sprint="Sprint-Test",
                parameter="alpha_s",
                value=0.1181,
                unit="dimensionless",
                source="unit-test",
                note="baseline",
                recorded_at="2026-09-09T00:00:00+00:00",
            )
        ]
    )
    assert inserted == 1
    rows = ledger.latest_by_sprint("Sprint-Test")
    assert len(rows) == 1
    assert rows[0]["parameter"] == "alpha_s"


def test_wave1_receipt_script_import_and_json_shape(tmp_path):
    import importlib.util

    script_path = Path(__file__).resolve().parents[1] / "9-INFRASTRUCTURE" / "provenance" / "generate_polyglot_wave1_receipt.py"
    spec = importlib.util.spec_from_file_location("generate_polyglot_wave1_receipt", script_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(mod)
    payload = mod.build_receipt()
    assert payload["test"] == "polyglot_wave1_backend_lock"
    assert payload["parity"]["curvature"]["parity_passed"] is True
    out = tmp_path / "receipt.json"
    out.write_text(json.dumps(payload), encoding="utf-8")
    assert out.exists()
