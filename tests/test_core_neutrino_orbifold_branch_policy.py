# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/neutrino_orbifold_branch_policy.py."""

from __future__ import annotations

from src.core.neutrino_orbifold_branch_policy import (
    minimal_5d_branch,
    neutrino_branch_policy,
    uv_extended_majorana_branch,
)


def test_minimal_branch_is_dirac_and_runtime_default():
    branch = minimal_5d_branch()
    assert branch["predicted_type"] == "DIRAC"
    assert branch["selected_for_runtime"] is True


def test_uv_branch_is_not_runtime_default():
    branch = uv_extended_majorana_branch()
    assert branch["selected_for_runtime"] is False
    assert "RESOLVED" in branch["status"]


def test_policy_keeps_branches_explicit_and_separate():
    policy = neutrino_branch_policy()
    assert policy["canonical_runtime_branch"] == "MINIMAL_5D_DIRAC"
    assert policy["uv_only_branch"] == "UV_EXTENDED_MAJORANA"
    assert policy["status"] == "BRANCHES_SEPARATED_AND_EXPLICIT"
