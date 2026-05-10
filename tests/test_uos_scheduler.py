"""
tests/test_uos_scheduler.py
===========================
Unit tests for UOS/scheduler.py.

Covers:
  - ProcessGeodesic: construction, state_vector shape, affinity_score
  - GeodesicScheduler: enqueue, dequeue, next_process, update_state
  - Queue capacity, duplicate PID, empty queue
  - phi_gradient computation
"""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from UOS.scheduler import ProcessGeodesic, GeodesicScheduler, PHASE_DIM
from UOS.constants import UOS_PROCESS_SLOTS, PHI_BACKGROUND


# ---------------------------------------------------------------------------
# ProcessGeodesic
# ---------------------------------------------------------------------------

class TestProcessGeodesic:
    def test_default_state_vector(self):
        p = ProcessGeodesic(pid=1)
        assert p.state_vector.shape == (PHASE_DIM,)
        assert np.all(p.state_vector == 0.0)

    def test_custom_state_vector(self):
        sv = np.ones(PHASE_DIM)
        p = ProcessGeodesic(pid=2, state_vector=sv)
        np.testing.assert_array_equal(p.state_vector, sv)

    def test_wrong_state_vector_shape_raises(self):
        with pytest.raises(ValueError):
            ProcessGeodesic(pid=3, state_vector=np.zeros(PHASE_DIM + 1))

    def test_priority_clamped_high(self):
        p = ProcessGeodesic(pid=4, priority=5.0)
        assert p.priority == 1.0

    def test_priority_clamped_low(self):
        p = ProcessGeodesic(pid=5, priority=-1.0)
        assert p.priority == 0.0

    def test_affinity_score_positive_for_aligned(self):
        grad = np.ones(PHASE_DIM)
        p = ProcessGeodesic(pid=6, priority=1.0, phi_weight=1.0,
                            state_vector=np.ones(PHASE_DIM))
        score = p.affinity_score(grad)
        assert score > 0.0

    def test_affinity_score_zero_priority(self):
        grad = np.ones(PHASE_DIM)
        p = ProcessGeodesic(pid=7, priority=0.0, state_vector=np.ones(PHASE_DIM))
        assert p.affinity_score(grad) == 0.0

    def test_affinity_score_type(self):
        p = ProcessGeodesic(pid=8)
        score = p.affinity_score(np.zeros(PHASE_DIM))
        assert isinstance(score, float)


# ---------------------------------------------------------------------------
# GeodesicScheduler — basic operations
# ---------------------------------------------------------------------------

class TestGeodesicSchedulerBasic:
    def test_empty_queue(self):
        sched = GeodesicScheduler()
        assert sched.queue_depth() == 0

    def test_enqueue_increases_depth(self):
        sched = GeodesicScheduler()
        sched.enqueue(ProcessGeodesic(pid=1))
        assert sched.queue_depth() == 1

    def test_dequeue_returns_proc(self):
        sched = GeodesicScheduler()
        p = ProcessGeodesic(pid=10, priority=0.8)
        sched.enqueue(p)
        out = sched.dequeue(10)
        assert out.pid == 10

    def test_dequeue_reduces_depth(self):
        sched = GeodesicScheduler()
        sched.enqueue(ProcessGeodesic(pid=1))
        sched.dequeue(1)
        assert sched.queue_depth() == 0

    def test_dequeue_missing_raises(self):
        sched = GeodesicScheduler()
        with pytest.raises(KeyError):
            sched.dequeue(999)

    def test_duplicate_enqueue_raises(self):
        sched = GeodesicScheduler()
        sched.enqueue(ProcessGeodesic(pid=1))
        with pytest.raises(KeyError):
            sched.enqueue(ProcessGeodesic(pid=1))


# ---------------------------------------------------------------------------
# GeodesicScheduler — next_process
# ---------------------------------------------------------------------------

class TestGeodesicSchedulerNextProcess:
    def test_empty_returns_none(self):
        sched = GeodesicScheduler()
        phi = np.ones(32)
        assert sched.next_process(phi) is None

    def test_single_process_returned(self):
        sched = GeodesicScheduler()
        sched.enqueue(ProcessGeodesic(pid=42))
        chosen = sched.next_process(np.ones(32))
        assert chosen.pid == 42

    def test_highest_priority_wins(self):
        sched = GeodesicScheduler()
        sched.enqueue(ProcessGeodesic(pid=1, priority=0.1,
                                      state_vector=np.ones(PHASE_DIM)))
        sched.enqueue(ProcessGeodesic(pid=2, priority=0.9,
                                      state_vector=np.ones(PHASE_DIM)))
        chosen = sched.next_process(np.ones(32))
        assert chosen.pid == 2

    def test_process_remains_in_queue_after_selection(self):
        sched = GeodesicScheduler()
        sched.enqueue(ProcessGeodesic(pid=1))
        sched.next_process(np.ones(32))
        assert sched.queue_depth() == 1

    def test_gradient_influences_selection(self):
        """Process with aligned state vector should score higher."""
        sched = GeodesicScheduler()
        # Process A: state vector aligned with gradient
        sv_a = np.array([1.0, 0.0, 0.0, 0.0, 0.0])
        # Process B: anti-aligned
        sv_b = np.array([-1.0, 0.0, 0.0, 0.0, 0.0])
        sched.enqueue(ProcessGeodesic(pid=1, priority=0.5, state_vector=sv_a))
        sched.enqueue(ProcessGeodesic(pid=2, priority=0.5, state_vector=sv_b))

        phi = np.zeros(32)
        phi[:16] = 1.0  # positive gradient in first half → gradient positive
        chosen = sched.next_process(phi)
        assert chosen.pid == 1


# ---------------------------------------------------------------------------
# GeodesicScheduler — update_state
# ---------------------------------------------------------------------------

class TestGeodesicSchedulerUpdateState:
    def test_update_sets_state(self):
        sched = GeodesicScheduler()
        sched.enqueue(ProcessGeodesic(pid=1))
        new_sv = np.arange(PHASE_DIM, dtype=float)
        sched.update_state(1, new_sv)
        np.testing.assert_array_almost_equal(
            sched._queue[1].state_vector, new_sv
        )

    def test_update_missing_raises(self):
        sched = GeodesicScheduler()
        with pytest.raises(KeyError):
            sched.update_state(999, np.zeros(PHASE_DIM))

    def test_update_truncates_long_vector(self):
        sched = GeodesicScheduler()
        sched.enqueue(ProcessGeodesic(pid=1))
        long_sv = np.ones(PHASE_DIM + 3)
        sched.update_state(1, long_sv)
        assert sched._queue[1].state_vector.shape == (PHASE_DIM,)


# ---------------------------------------------------------------------------
# GeodesicScheduler — capacity
# ---------------------------------------------------------------------------

class TestGeodesicSchedulerCapacity:
    def test_overflow_raises(self):
        sched = GeodesicScheduler(max_slots=3)
        for i in range(3):
            sched.enqueue(ProcessGeodesic(pid=i))
        with pytest.raises(OverflowError):
            sched.enqueue(ProcessGeodesic(pid=99))

    def test_queue_pids_sorted(self):
        sched = GeodesicScheduler()
        for pid in [5, 2, 8, 1]:
            sched.enqueue(ProcessGeodesic(pid=pid))
        assert sched.queue_pids() == [1, 2, 5, 8]


# ---------------------------------------------------------------------------
# GeodesicScheduler — queue_summary
# ---------------------------------------------------------------------------

class TestQueueSummary:
    def test_summary_contains_pid_priority_phi_weight(self):
        sched = GeodesicScheduler()
        sched.enqueue(ProcessGeodesic(pid=1, priority=0.7, phi_weight=1.5))
        summary = sched.queue_summary()
        assert len(summary) == 1
        assert summary[0]["pid"] == 1
        assert abs(summary[0]["priority"] - 0.7) < 1e-9
        assert abs(summary[0]["phi_weight"] - 1.5) < 1e-9


# ---------------------------------------------------------------------------
# Internal: phi_gradient
# ---------------------------------------------------------------------------

class TestPhiGradient:
    def test_gradient_length(self):
        phi = np.linspace(0, 1, 32)
        grad = GeodesicScheduler._phi_gradient(phi)
        assert grad.shape == (PHASE_DIM,)

    def test_zero_field_gives_zero_gradient(self):
        phi = np.zeros(32)
        grad = GeodesicScheduler._phi_gradient(phi)
        np.testing.assert_array_almost_equal(grad, 0.0)

    def test_linear_field_gives_positive_gradient(self):
        phi = np.linspace(0, 1, 32)
        grad = GeodesicScheduler._phi_gradient(phi)
        # Most gradient values should be positive for an ascending field
        assert np.sum(grad > 0) >= PHASE_DIM // 2
