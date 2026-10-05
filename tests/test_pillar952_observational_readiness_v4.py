# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 952 — Observational Readiness v4."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import subprocess
import sys
from threading import Barrier, Event
from types import ModuleType
from unittest.mock import Mock

import pytest

from src.core import pillar952_observational_readiness_v4 as readiness
from src.core.pillar952_observational_readiness_v4 import (
    PILLAR_NUMBER, PILLAR_GATE, PILLAR_STATUS, PILLAR_VALID,
    OBSERVATIONAL_MATRIX_VERSION, PREDICTIONS, OPEN_LANES, ARCHITECTURE_LIMITS,
    observational_readiness_v4_summary,
)


def _fresh_readiness_module():
    spec = importlib.util.spec_from_file_location(readiness.__name__, readiness.__file__)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def lazy_readiness(monkeypatch):
    uv = {
        "status": "TEST_UV",
        "best_point": {"tau": 1.23, "rho": 0.87, "alpha_s_uv": 0.109, "n_d3_model": 15.4},
    }
    kk = {
        "status": "TEST_KK",
        "tail_spread": 0.012,
        "mean_phi_final": 1.47,
        "mean_winding_abs": 4.9,
    }
    flavor = {
        "status": "TEST_FLAVOR",
        "theta13_deg": 0.203,
        "vub": 0.0035,
        "ckm_ok": False,
        "hierarchy_ok": True,
    }
    solvers = [Mock(return_value=report) for report in (uv, kk, flavor)]
    dependencies = [
        ("pillar987_uv_completion_compactification_layer", "solve_uv_moduli_point"),
        ("pillar988_fully_coupled_kk_backreaction_engine", "run_fully_coupled_kk_backreaction"),
        ("pillar989_flavor_closure_geometric_layer", "flavor_closure_observables"),
    ]
    for (module_name, function_name), solver in zip(dependencies, solvers):
        stub = ModuleType(f"src.core.{module_name}")
        setattr(stub, function_name, solver)
        monkeypatch.setitem(sys.modules, stub.__name__, stub)
    return _fresh_readiness_module(), solvers, (uv, kk, flavor)


def _assert_called_once(solvers):
    solvers[0].assert_called_once_with()
    solvers[1].assert_called_once_with(steps=12)
    solvers[2].assert_called_once_with()


def test_fresh_import_does_not_load_or_run_deep_layers():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
import sys

def reject_solver(frame, event, arg):
    if event == "call" and frame.f_code.co_name in {
        "solve_uv_moduli_point",
        "run_fully_coupled_kk_backreaction",
        "flavor_closure_observables",
    }:
        raise AssertionError("import executed a deep-layer solver")

sys.setprofile(reject_solver)
from src.core import pillar952_observational_readiness_v4 as module
assert module.PILLAR_VALID is True
assert len(module.OPEN_LANES) == 6
assert "DEEP_LAYER_CHAIN" not in vars(module)
assert not any(name in sys.modules for name in (
    "src.core.pillar987_uv_completion_compactification_layer",
    "src.core.pillar988_fully_coupled_kk_backreaction_engine",
    "src.core.pillar989_flavor_closure_geometric_layer",
))
""",
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr


def test_first_access_computes_once_and_preserves_mutable_list(lazy_readiness):
    module, solvers, _ = lazy_readiness
    assert "DEEP_LAYER_CHAIN" not in vars(module)
    for solver in solvers:
        solver.assert_not_called()
    chain = module.DEEP_LAYER_CHAIN
    assert type(chain) is list
    assert all(type(row) is dict for row in chain)
    assert module.DEEP_LAYER_CHAIN is chain
    assert vars(module)["DEEP_LAYER_CHAIN"] is chain
    _assert_called_once(solvers)
    chain[0]["key_output"]["tau"] = 9.0
    chain.append({"pillar": 123})
    summary = module.observational_readiness_v4_summary()
    assert summary["deep_layer_chain"] is chain
    assert summary["deep_layer_chain"][0]["key_output"]["tau"] == 9.0
    assert summary["n_deep_layers"] == 4
    _assert_called_once(solvers)


def test_summary_triggers_calculation_and_forwards_fields(lazy_readiness):
    module, solvers, (uv, kk, flavor) = lazy_readiness
    summary = module.observational_readiness_v4_summary()
    chain = summary["deep_layer_chain"]
    assert chain == [
        {
            "pillar": 987,
            "name": "UV_COMPLETION_COMPACTIFICATION_LAYER",
            "status": uv["status"],
            "key_output": uv["best_point"],
        },
        {
            "pillar": 988,
            "name": "FULLY_COUPLED_KK_BACKREACTION_ENGINE",
            "status": kk["status"],
            "key_output": {key: value for key, value in kk.items() if key != "status"},
        },
        {
            "pillar": 989,
            "name": "FLAVOR_CLOSURE_GEOMETRIC_LAYER",
            "status": flavor["status"],
            "key_output": {key: value for key, value in flavor.items() if key != "status"},
        },
    ]
    assert summary["n_deep_layers"] == 3
    assert summary["predictions"] is module.PREDICTIONS
    assert summary["open_lanes"] is module.OPEN_LANES
    assert summary["architecture_limits"] is module.ARCHITECTURE_LIMITS
    assert module.observational_readiness_v4_summary()["deep_layer_chain"] is chain
    assert module.DEEP_LAYER_CHAIN is chain
    _assert_called_once(solvers)


def test_import_star_and_named_import_materialize_same_list(lazy_readiness, monkeypatch):
    module, solvers, _ = lazy_readiness
    monkeypatch.setitem(sys.modules, module.__name__, module)
    namespace = {}
    exec(f"from {module.__name__} import *", namespace)
    assert set(module.__all__) <= namespace.keys()
    assert namespace["DEEP_LAYER_CHAIN"] is module.DEEP_LAYER_CHAIN
    named_namespace = {}
    exec(f"from {module.__name__} import DEEP_LAYER_CHAIN", named_namespace)
    assert named_namespace["DEEP_LAYER_CHAIN"] is namespace["DEEP_LAYER_CHAIN"]
    _assert_called_once(solvers)


def test_unknown_attribute_does_not_compute(lazy_readiness):
    module, solvers, _ = lazy_readiness
    with pytest.raises(AttributeError, match="not_an_export"):
        module.not_an_export
    for solver in solvers:
        solver.assert_not_called()


def test_reload_invalidates_chain_without_computing(lazy_readiness, monkeypatch):
    module, solvers, _ = lazy_readiness
    chain = module.DEEP_LAYER_CHAIN
    monkeypatch.setitem(sys.modules, module.__name__, module)
    assert importlib.reload(module) is module
    assert "DEEP_LAYER_CHAIN" not in vars(module)
    _assert_called_once(solvers)
    assert module.DEEP_LAYER_CHAIN == chain
    assert module.DEEP_LAYER_CHAIN is not chain
    assert all(solver.call_count == 2 for solver in solvers)


def test_failed_computation_can_be_retried(lazy_readiness):
    module, solvers, _ = lazy_readiness
    solvers[1].side_effect = RuntimeError("calculation failed")
    with pytest.raises(RuntimeError, match="calculation failed"):
        module.DEEP_LAYER_CHAIN
    assert "DEEP_LAYER_CHAIN" not in vars(module)
    solvers[2].assert_not_called()
    solvers[1].side_effect = None
    assert len(module.DEEP_LAYER_CHAIN) == 3
    assert solvers[0].call_count == solvers[1].call_count == 2
    solvers[2].assert_called_once_with()


def test_concurrent_first_access_computes_once(lazy_readiness):
    module, solvers, (uv, _, _) = lazy_readiness
    start = Barrier(9)
    entered = Event()
    release = Event()

    def solve():
        entered.set()
        assert release.wait(timeout=5)
        return uv

    def access(index):
        start.wait(timeout=5)
        if index % 2:
            return module.observational_readiness_v4_summary()["deep_layer_chain"]
        return module.DEEP_LAYER_CHAIN

    solvers[0].side_effect = solve
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(access, index) for index in range(8)]
        start.wait(timeout=5)
        try:
            assert entered.wait(timeout=5)
        finally:
            release.set()
        chains = [future.result(timeout=10) for future in futures]
    assert all(chain is chains[0] for chain in chains)
    _assert_called_once(solvers)


def test_deep_layer_values_match_real_numerical_calculations():
    from src.core.pillar987_uv_completion_compactification_layer import solve_uv_moduli_point
    from src.core.pillar988_fully_coupled_kk_backreaction_engine import (
        run_fully_coupled_kk_backreaction,
    )
    from src.core.pillar989_flavor_closure_geometric_layer import flavor_closure_observables

    reports = [
        solve_uv_moduli_point(),
        run_fully_coupled_kk_backreaction(steps=12),
        flavor_closure_observables(),
    ]
    chain = readiness.DEEP_LAYER_CHAIN
    assert [row["pillar"] for row in chain] == [987, 988, 989]
    for row, report in zip(chain, reports):
        assert row["status"] == report["status"]
        source = report.get("best_point", report)
        for key, value in row["key_output"].items():
            assert value == source[key]


def test_pillar_number(): assert PILLAR_NUMBER == 952
def test_gate(): assert PILLAR_GATE == "OBSERVATIONAL_READINESS_V4"
def test_valid(): assert PILLAR_VALID is True
def test_status(): assert PILLAR_STATUS == "OBSERVATIONAL_READINESS_V4_COMPLETE"
def test_version(): assert OBSERVATIONAL_MATRIX_VERSION == "v4"

def test_predictions_count(): assert len(PREDICTIONS) == 8

def test_predictions_have_required_fields():
    for p in PREDICTIONS:
        assert "id" in p
        assert "observable" in p
        assert "prediction" in p
        assert "status" in p

def test_prediction_ns_consistent():
    ns_pred = next(p for p in PREDICTIONS if p["id"] == "P1_NS")
    assert ns_pred["status"] == "CONSISTENT"

def test_prediction_r_consistent():
    r_pred = next(p for p in PREDICTIONS if p["id"] == "P2_R")
    assert r_pred["status"] == "CONSISTENT"

def test_prediction_dark_energy_monitoring():
    de_pred = next(p for p in PREDICTIONS if p["id"] == "P5_DARK_ENERGY")
    assert de_pred["status"] == "MONITORING"

def test_open_lanes_count(): assert len(OPEN_LANES) == 6

def test_open_lanes_b3_present():
    ids = [l["item"] for l in OPEN_LANES]
    assert "B3_G4_FLUX" in ids

def test_open_lanes_ckm_present():
    ids = [l["item"] for l in OPEN_LANES]
    assert "CKM_TEXTURE_13D" in ids

def test_open_lanes_fermion_present():
    ids = [l["item"] for l in OPEN_LANES]
    assert "FERMION_MASS_RATIO" in ids

def test_b3_upgraded_to_bounded():
    b3 = next(l for l in OPEN_LANES if l["item"] == "B3_G4_FLUX")
    assert "BOUNDED" in b3["status"]

def test_ckm_upgraded_to_true_arch_limit():
    ckm = next(l for l in OPEN_LANES if l["item"] == "CKM_TEXTURE_13D")
    assert "TRUE_ARCHITECTURE_LIMIT" in ckm["status"]

def test_fermion_upgraded_to_window_constrained():
    fm = next(l for l in OPEN_LANES if l["item"] == "FERMION_MASS_RATIO")
    assert "CONSTRAINED" in fm["status"]

def test_architecture_limits_count(): assert len(ARCHITECTURE_LIMITS) >= 4

def test_litebird_mentioned():
    all_text = str(PREDICTIONS) + str(OPEN_LANES)
    assert "LiteBIRD" in all_text or "LITEBIRD" in all_text

def test_summary_keys():
    s = observational_readiness_v4_summary()
    for key in ["pillar", "gate", "status", "valid", "version",
                "n_predictions", "n_open_lanes", "predictions", "open_lanes",
                "primary_falsifier", "deep_layer_chain", "n_deep_layers"]:
        assert key in s

def test_summary_valid(): assert observational_readiness_v4_summary()["valid"] is True
def test_summary_pillar(): assert observational_readiness_v4_summary()["pillar"] == 952
def test_summary_primary_falsifier():
    s = observational_readiness_v4_summary()
    assert "LiteBIRD" in s["primary_falsifier"] or "litebird" in s["primary_falsifier"].lower()


def test_deep_layer_chain_present():
    assert len(readiness.DEEP_LAYER_CHAIN) == 3
    pillars = {row["pillar"] for row in readiness.DEEP_LAYER_CHAIN}
    assert pillars == {987, 988, 989}


def test_deep_layer_chain_in_summary():
    s = observational_readiness_v4_summary()
    assert s["n_deep_layers"] == 3
