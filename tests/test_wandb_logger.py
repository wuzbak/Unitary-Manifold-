# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_wandb_logger.py
==============================
Tests for src/core/wandb_logger.py — W&B experiment logger.
All tests run in offline mode (no WANDB_API_KEY required).
"""
import os
import pytest
import wandb

from src.core.wandb_logger import (
    init_run,
    log_field_evolution,
    log_kk_spectrum,
    log_inflation_observables,
    log_z3_check,
    finish_run,
    run_standard_experiment,
    PLANCK_NS,
    PLANCK_NS_SIGMA,
    PLANCK_R_UPPER,
    UM_NS,
    UM_R,
)

# Force offline in all tests
os.environ.setdefault("WANDB_MODE", "offline")


# ---------------------------------------------------------------------------
# Import check
# ---------------------------------------------------------------------------

def test_wandb_importable():
    assert hasattr(wandb, "init")
    assert hasattr(wandb, "run")


# ---------------------------------------------------------------------------
# init_run / finish_run
# ---------------------------------------------------------------------------

def test_init_run_offline():
    run = init_run(name="test-offline", mode="offline")
    assert run is not None
    finish_run(run)


def test_init_run_returns_run():
    run = init_run(name="test-run-obj", mode="offline")
    assert run is not None
    assert hasattr(run, "log")
    finish_run(run)


def test_finish_run_none_safe():
    # Should not raise even if run is None
    finish_run(None)


# ---------------------------------------------------------------------------
# log_inflation_observables
# ---------------------------------------------------------------------------

def test_log_inflation_observables():
    run = init_run(name="test-inflation", mode="offline")
    log_inflation_observables(UM_NS, UM_R, run)
    finish_run(run)


def test_log_inflation_observables_no_run():
    # Should not raise when run=None
    log_inflation_observables(UM_NS, UM_R, None)


# ---------------------------------------------------------------------------
# log_kk_spectrum
# ---------------------------------------------------------------------------

def test_log_kk_spectrum():
    run = init_run(name="test-kk", mode="offline")
    log_kk_spectrum([0.01, 0.05, 0.15], run)
    finish_run(run)


def test_log_kk_spectrum_no_run():
    log_kk_spectrum([0.01, 0.05], None)


# ---------------------------------------------------------------------------
# log_z3_check
# ---------------------------------------------------------------------------

def test_log_z3_check():
    run = init_run(name="test-z3", mode="offline")
    fake_z3 = {
        "all_pass": True,
        "trust_stability": {"status": "PASS"},
        "no_deadlock": {"status": "PASS"},
        "cs_bound": {"status": "PASS"},
        "xi_c_rational": {"status": "PASS"},
    }
    log_z3_check(fake_z3, run)
    finish_run(run)


# ---------------------------------------------------------------------------
# run_standard_experiment
# ---------------------------------------------------------------------------

def test_run_standard_experiment():
    result = run_standard_experiment(steps=3, dt=0.001, mode="offline")
    assert isinstance(result, dict)
    assert "n_s" in result
    assert "r" in result
    assert "z3_all_pass" in result
    assert "passed" in result


def test_run_standard_experiment_ns_close_to_planck():
    result = run_standard_experiment(steps=3, dt=0.001, mode="offline")
    n_s = result["n_s"]
    sigma_pull = abs(n_s - PLANCK_NS) / PLANCK_NS_SIGMA
    assert sigma_pull < 5.0, f"n_s={n_s} is {sigma_pull:.1f}σ from Planck"


def test_run_standard_experiment_z3_pass():
    result = run_standard_experiment(steps=3, dt=0.001, mode="offline")
    assert result["z3_all_pass"] is True


def test_run_standard_experiment_r_consistent():
    result = run_standard_experiment(steps=3, dt=0.001, mode="offline")
    assert result["r"] < PLANCK_R_UPPER


def test_planck_constants():
    assert abs(PLANCK_NS - 0.9649) < 1e-10
    assert abs(PLANCK_NS_SIGMA - 0.0042) < 1e-10
    assert abs(PLANCK_R_UPPER - 0.036) < 1e-10


def test_um_constants():
    assert abs(UM_NS - 0.9635) < 1e-10
    assert abs(UM_R - 0.0315) < 1e-10
