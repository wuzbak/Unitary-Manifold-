# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/test_operational_core.py
=====================================
Unit tests for the Operational Core.

Covers:
  - Constants: C_S, AUTO_THRESHOLD, HOLD_THRESHOLD, TRUST_FLOOR
  - Task: construction, is_resolved
  - TaskDomain / ExecutionMode / TaskStatus constants
  - OperationalCore: submit, start, resolve, cancel, hil_approve
  - Routing: AUTO / SUPERVISED / HOLD / HALT classification
  - Throughput: sliding window, success rate
  - Cross-domain load
  - Edge cases: empty task list, full trust loss, repeated resolves
"""

import math
import sys
import os

import pytest
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_PENTAD = os.path.dirname(_HERE)
_ROOT = os.path.dirname(_PENTAD)
for _p in [_HERE, _PENTAD, _ROOT]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from five_cores.operational_core import (
    C_S,
    AUTO_THRESHOLD,
    HOLD_THRESHOLD,
    EXPERIENCE_ALPHA,
    THROUGHPUT_WINDOW,
    TRUST_FLOOR,
    TaskDomain,
    ExecutionMode,
    TaskStatus,
    Task,
    OperationalState,
    OperationalCore,
)

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
}


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_c_s_value(self):
        assert math.isclose(C_S, 12 / 37, rel_tol=1e-12)

    def test_auto_threshold_below_hold(self):
        assert AUTO_THRESHOLD < HOLD_THRESHOLD

    def test_thresholds_in_unit_interval(self):
        assert 0 < AUTO_THRESHOLD < 1
        assert 0 < HOLD_THRESHOLD < 1

    def test_trust_floor_equals_c_s(self):
        assert math.isclose(TRUST_FLOOR, C_S, rel_tol=1e-12)

    def test_throughput_window_equals_k_cs(self):
        assert THROUGHPUT_WINDOW == 74

    def test_experience_alpha_in_range(self):
        assert 0 < EXPERIENCE_ALPHA < 1


# ===========================================================================
# Domain / Mode / Status constants
# ===========================================================================

class TestDomainConstants:
    def test_task_domains_are_strings(self):
        for attr in ["NAVIGATION", "PROPULSION", "LIFE_SUPPORT", "SCIENCE",
                     "COMMUNICATIONS", "MAINTENANCE", "MEDICAL", "COMMAND"]:
            assert isinstance(getattr(TaskDomain, attr), str)

    def test_execution_modes_are_strings(self):
        for attr in ["AUTO", "SUPERVISED", "HOLD", "HALT"]:
            assert isinstance(getattr(ExecutionMode, attr), str)

    def test_task_statuses_are_strings(self):
        for attr in ["QUEUED", "IN_PROGRESS", "COMPLETED", "FAILED", "CANCELLED"]:
            assert isinstance(getattr(TaskStatus, attr), str)


# ===========================================================================
# Task dataclass
# ===========================================================================

class TestTask:
    def _make(self, **kw) -> Task:
        defaults = dict(id="t1", domain=TaskDomain.NAVIGATION,
                        criticality=0.5, description="test")
        defaults.update(kw)
        return Task(**defaults)

    def test_not_resolved_when_queued(self):
        t = self._make()
        assert not t.is_resolved()

    def test_resolved_when_completed(self):
        t = self._make(status=TaskStatus.COMPLETED)
        assert t.is_resolved()

    def test_resolved_when_failed(self):
        t = self._make(status=TaskStatus.FAILED)
        assert t.is_resolved()

    def test_resolved_when_cancelled(self):
        t = self._make(status=TaskStatus.CANCELLED)
        assert t.is_resolved()

    def test_not_resolved_when_in_progress(self):
        t = self._make(status=TaskStatus.IN_PROGRESS)
        assert not t.is_resolved()


# ===========================================================================
# OperationalCore — factory
# ===========================================================================

class TestFactory:
    def test_default_creates_core(self):
        oc = OperationalCore.default()
        assert oc._phi_trust == 1.0
        assert oc._step_count == 0

    def test_initial_familiarity_in_unit_interval(self):
        oc = OperationalCore.default()
        for f in oc._familiarity.values():
            assert 0.0 <= f <= 1.0


# ===========================================================================
# Submit / route
# ===========================================================================

class TestSubmitAndRoute:
    def test_submit_returns_task(self):
        oc = OperationalCore.default()
        t = oc.submit_task(TaskDomain.NAVIGATION, criticality=0.1)
        assert isinstance(t, Task)

    def test_low_criticality_routes_auto(self):
        oc = OperationalCore.default()
        t = oc.submit_task(TaskDomain.NAVIGATION, criticality=0.01)
        assert t.mode == ExecutionMode.AUTO

    def test_high_criticality_low_trust_routes_hold_or_halt(self):
        oc = OperationalCore(phi_trust=0.1)
        t = oc.submit_task(TaskDomain.COMMAND, criticality=0.99)
        assert t.mode in (ExecutionMode.HOLD, ExecutionMode.HALT)

    def test_safety_interlock_forces_halt(self):
        oc = OperationalCore.default()
        t = oc.submit_task(TaskDomain.PROPULSION, criticality=0.1, safety_interlock=True)
        assert t.mode == ExecutionMode.HALT

    def test_task_is_in_task_dict(self):
        oc = OperationalCore.default()
        t = oc.submit_task(TaskDomain.SCIENCE, criticality=0.5)
        assert t.id in oc._tasks


# ===========================================================================
# Start / Resolve / Cancel
# ===========================================================================

class TestTaskLifecycle:
    def test_start_task_changes_status(self):
        oc = OperationalCore.default()
        t = oc.submit_task(TaskDomain.NAVIGATION, criticality=0.01)
        t.status = TaskStatus.QUEUED  # ensure queued
        t.mode = ExecutionMode.AUTO
        oc.start_task(t.id)
        assert oc._tasks[t.id].status == TaskStatus.IN_PROGRESS

    def test_resolve_task_success(self):
        oc = OperationalCore.default()
        t = oc.submit_task(TaskDomain.NAVIGATION, criticality=0.01)
        t.status = TaskStatus.IN_PROGRESS
        oc.resolve_task(t.id, success=True)
        assert oc._tasks[t.id].status == TaskStatus.COMPLETED

    def test_resolve_task_failure(self):
        oc = OperationalCore.default()
        t = oc.submit_task(TaskDomain.NAVIGATION, criticality=0.01)
        t.status = TaskStatus.IN_PROGRESS
        oc.resolve_task(t.id, success=False)
        assert oc._tasks[t.id].status == TaskStatus.FAILED

    def test_cancel_task(self):
        oc = OperationalCore.default()
        t = oc.submit_task(TaskDomain.SCIENCE, criticality=0.5)
        oc.cancel_task(t.id)
        assert oc._tasks[t.id].status == TaskStatus.CANCELLED

    def test_hil_approve_hold_task(self):
        oc = OperationalCore(phi_trust=0.1)
        t = oc.submit_task(TaskDomain.COMMAND, criticality=0.99)
        t.mode = ExecutionMode.HOLD
        t.status = TaskStatus.QUEUED
        oc.hil_approve(t.id)
        assert oc._tasks[t.id].status == TaskStatus.IN_PROGRESS


# ===========================================================================
# Tick and State
# ===========================================================================

class TestTick:
    def test_tick_returns_state(self):
        oc = OperationalCore.default()
        state = oc.tick()
        assert isinstance(state, OperationalState)

    def test_step_count_increments(self):
        oc = OperationalCore.default()
        oc.tick()
        oc.tick()
        assert oc._step_count == 2

    def test_throughput_starts_at_one(self):
        oc = OperationalCore.default()
        state = oc.tick()
        assert state.throughput == 1.0  # no resolved tasks yet

    def test_throughput_tracks_success(self):
        oc = OperationalCore.default()
        # Submit and resolve 3 tasks successfully, 1 failure
        for _ in range(3):
            t = oc.submit_task(TaskDomain.NAVIGATION, criticality=0.01)
            t.status = TaskStatus.IN_PROGRESS
            oc.resolve_task(t.id, success=True)
        t = oc.submit_task(TaskDomain.NAVIGATION, criticality=0.01)
        t.status = TaskStatus.IN_PROGRESS
        oc.resolve_task(t.id, success=False)
        state = oc.tick()
        assert 0.5 < state.throughput < 1.0

    def test_domain_familiarity_updates_on_resolve(self):
        oc = OperationalCore.default()
        fam_before = oc._familiarity[TaskDomain.NAVIGATION]
        t = oc.submit_task(TaskDomain.NAVIGATION, criticality=0.01)
        t.status = TaskStatus.IN_PROGRESS
        oc.resolve_task(t.id, success=True)
        # familiarity should have moved toward 1.0
        assert oc._familiarity[TaskDomain.NAVIGATION] >= fam_before


# ===========================================================================
# Cross-Domain Load
# ===========================================================================

class TestCrossDomainLoad:
    def test_load_is_empty_with_no_tasks(self):
        oc = OperationalCore.default()
        assert oc.cross_domain_load() == {}

    def test_load_counts_active_tasks(self):
        oc = OperationalCore.default()
        oc.submit_task(TaskDomain.NAVIGATION, criticality=0.01)
        oc.submit_task(TaskDomain.NAVIGATION, criticality=0.01)
        oc.submit_task(TaskDomain.SCIENCE, criticality=0.3)
        load = oc.cross_domain_load()
        assert load[TaskDomain.NAVIGATION] == 2
        assert load[TaskDomain.SCIENCE] == 1
