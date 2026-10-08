# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Regression checks for broken public exports and the Lodge dashboard."""

import importlib

import pytest


@pytest.mark.parametrize("module_name", [
    "src.core.cmbs4_ns_r_joint_falsifier",
    "src.core.pillar308_2027_readiness_mock_drill",
    "src.core.pillar637_fermion_hierarchy_fn_complete",
])
def test_public_exports_exist(module_name):
    module = importlib.import_module(module_name)
    assert all(hasattr(module, name) for name in module.__all__)


def test_lodge_dashboard_renders_registry_difficulties(tmp_path, monkeypatch, capsys):
    from lodge import watch

    leaderboard = watch.Leaderboard(db_path=tmp_path / "leaderboard.db")
    monkeypatch.setattr(watch, "_clear", lambda: None)
    monkeypatch.setattr(watch, "Leaderboard", lambda: leaderboard)
    watch.render_dashboard(ledger_dir=tmp_path)
    output = capsys.readouterr().out
    assert "REGISTRY SUMMARY" in output
    for difficulty in watch.REGISTRY.summary()["by_difficulty"]:
        assert f"{difficulty.capitalize():10s}" in output
