import importlib.util
from pathlib import Path

import numpy as np
import pytest

from src.core.evolution import FieldState, _compute_rhs
from src.core.julia_acceleration import (
    julia_runtime_status,
    parity_report,
    run_julia_tensor_kernels,
)
from src.core.metric import assemble_5d_metric, field_strength
from src.core.polyglot_dependency_health import polyglot_stack_health_report
from src.core.polyglot_execution_matrix import evaluate_promotion_gate


def test_julia_runtime_status_has_cuda_field():
    status = julia_runtime_status(use_cuda=False)
    assert hasattr(status, "cuda_functional")
    assert status.backend == "julia"


def test_promotion_gate_pass_case():
    verdict = evaluate_promotion_gate(
        parity_passed=True,
        speedup=2.0,
        pytest_failures=0,
        cuda_required=False,
        cuda_available=False,
    )
    assert verdict.passed is True
    assert verdict.reasons == ()


def test_promotion_gate_blocks_on_parity_fail():
    verdict = evaluate_promotion_gate(
        parity_passed=False,
        speedup=2.0,
        pytest_failures=0,
        cuda_required=False,
        cuda_available=False,
    )
    assert verdict.passed is False
    assert "parity_failed" in verdict.reasons


def test_polyglot_stack_health_sections_present():
    report = polyglot_stack_health_report()
    for key in (
        "languages",
        "data_storage",
        "execution_compute",
        "verification_logic",
        "docs_pipelines",
    ):
        assert key in report


def test_parquet_probe_has_boolean_flags():
    report = polyglot_stack_health_report()
    parquet = report["data_storage"]["parquet"]
    assert isinstance(parquet["supported_via_pyarrow"], bool)
    assert isinstance(parquet["supported_via_polars"], bool)


def test_julia_tensor_kernels_unavailable_without_juliacall():
    if importlib.util.find_spec("juliacall") is not None and julia_runtime_status().juliacall_available:
        pytest.skip("juliacall runtime available; unavailable-path test not applicable.")
    g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (8, 1, 1))
    B = np.zeros((8, 4))
    phi = np.ones(8)
    with pytest.raises(RuntimeError, match="Julia backend unavailable"):
        run_julia_tensor_kernels(g, B, phi, lam=1.0, dx=0.1, coordinate_index=1)


def test_julia_tensor_kernels_match_python_when_available():
    if not julia_runtime_status().juliacall_available:
        pytest.skip("juliacall runtime not available")
    rng = np.random.default_rng(13)
    g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (8, 1, 1))
    g = g + 1e-4 * rng.standard_normal(g.shape)
    g = 0.5 * (g + g.transpose(0, 2, 1))
    B = 1e-3 * rng.standard_normal((8, 4))
    phi = 1.0 + 1e-4 * rng.standard_normal(8)
    out = run_julia_tensor_kernels(g, B, phi, lam=1.0, dx=0.1, coordinate_index=1)
    np.testing.assert_allclose(out["G5"], assemble_5d_metric(g, B, phi, 1.0), rtol=1e-9, atol=1e-12)
    np.testing.assert_allclose(out["H"], field_strength(B, 0.1, coordinate_index=1), rtol=1e-9, atol=1e-12)


def test_compute_rhs_python_backend_default(monkeypatch):
    monkeypatch.setenv("UM_CORE_BACKEND", "python")
    s = FieldState.flat(N=8, dx=0.1, rng=np.random.default_rng(5))
    dg, dB, dphi = _compute_rhs(s)
    assert dg.shape == (8, 4, 4)
    assert dB.shape == (8, 4)
    assert dphi.shape == (8,)


def test_wave2_receipt_builder_has_gate():
    script_path = Path(__file__).resolve().parents[1] / "9-INFRASTRUCTURE" / "provenance" / "generate_polyglot_wave2_receipt.py"
    spec = importlib.util.spec_from_file_location("generate_polyglot_wave2_receipt", script_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(mod)
    payload = mod.build_receipt()
    assert payload["test"] == "polyglot_wave2_julia_cuda_promotion"
    assert "promotion_gate" in payload
    assert "stack_health" in payload
