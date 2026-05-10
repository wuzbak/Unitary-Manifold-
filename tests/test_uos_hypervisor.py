"""
tests/test_uos_hypervisor.py
============================
Unit tests for UOS/hypervisor.py.

Covers:
  - ManifoldState: construction, equality, hash
  - UOSHypervisor: boot, tick, run, attach_to_host
  - resource_report: keys and value ranges
  - manifold_invariant_ok: returns bool
  - history ring-buffer
  - error paths: tick before boot, StopIteration at n_ticks
"""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from UOS.hypervisor import ManifoldState, UOSHypervisor, _flat_initial_state
from UOS.constants import UOS_PROCESS_SLOTS, PHI_BACKGROUND


# ---------------------------------------------------------------------------
# ManifoldState
# ---------------------------------------------------------------------------

class TestManifoldState:
    def test_construction(self):
        g, B, phi = _flat_initial_state(8)
        ms = ManifoldState(g=g, B=B, phi=phi, t=0.0, tick=0)
        assert ms.tick == 0
        assert ms.t == 0.0
        assert ms.phi.shape == (8,)

    def test_equality(self):
        g, B, phi = _flat_initial_state(8)
        ms1 = ManifoldState(g=g.copy(), B=B.copy(), phi=phi.copy(), t=0.0, tick=0)
        ms2 = ManifoldState(g=g.copy(), B=B.copy(), phi=phi.copy(), t=0.0, tick=0)
        assert ms1 == ms2

    def test_inequality_tick(self):
        g, B, phi = _flat_initial_state(8)
        ms1 = ManifoldState(g=g, B=B, phi=phi, t=0.0, tick=0)
        ms2 = ManifoldState(g=g, B=B, phi=phi, t=0.0, tick=1)
        assert ms1 != ms2

    def test_hash_is_int(self):
        g, B, phi = _flat_initial_state(8)
        ms = ManifoldState(g=g, B=B, phi=phi, t=0.0, tick=0)
        assert isinstance(hash(ms), int)


# ---------------------------------------------------------------------------
# _flat_initial_state
# ---------------------------------------------------------------------------

class TestFlatInitialState:
    def test_shapes(self):
        N = 16
        g, B, phi = _flat_initial_state(N)
        assert g.shape == (N, 4, 4)
        assert B.shape == (N, 4)
        assert phi.shape == (N,)

    def test_metric_signature(self):
        g, _, _ = _flat_initial_state(16)
        # g[i,0,0] should be close to -1 (Minkowski)
        assert np.all(g[:, 0, 0] < 0)

    def test_phi_near_background(self):
        _, _, phi = _flat_initial_state(16)
        assert np.all(np.abs(phi - PHI_BACKGROUND) < 1e-3)


# ---------------------------------------------------------------------------
# UOSHypervisor — boot
# ---------------------------------------------------------------------------

class TestHypervisorBoot:
    def test_boot_sets_booted(self):
        hv = UOSHypervisor(n_grid=8)
        assert not hv._booted
        hv.boot()
        assert hv._booted

    def test_state_none_before_boot(self):
        hv = UOSHypervisor(n_grid=8)
        assert hv.state is None

    def test_state_after_boot(self):
        hv = UOSHypervisor(n_grid=8)
        hv.boot()
        assert isinstance(hv.state, ManifoldState)
        assert hv.state.tick == 0

    def test_history_length_after_boot(self):
        hv = UOSHypervisor(n_grid=8)
        hv.boot()
        assert len(hv.history) == 1

    def test_double_boot_resets(self):
        hv = UOSHypervisor(n_grid=8)
        hv.boot()
        hv.boot()
        assert hv._tick == 0
        assert len(hv.history) == 1


# ---------------------------------------------------------------------------
# UOSHypervisor — tick
# ---------------------------------------------------------------------------

class TestHypervisorTick:
    def test_tick_before_boot_raises(self):
        hv = UOSHypervisor(n_grid=8)
        with pytest.raises(RuntimeError):
            hv.tick()

    def test_tick_advances_t(self):
        hv = UOSHypervisor(n_grid=8)
        hv.boot()
        snap = hv.tick()
        assert snap.t > 0.0

    def test_tick_advances_tick_count(self):
        hv = UOSHypervisor(n_grid=8)
        hv.boot()
        snap = hv.tick()
        assert snap.tick == 1

    def test_tick_returns_manifold_state(self):
        hv = UOSHypervisor(n_grid=8)
        hv.boot()
        snap = hv.tick()
        assert isinstance(snap, ManifoldState)

    def test_multiple_ticks_monotone_t(self):
        hv = UOSHypervisor(n_grid=8)
        hv.boot()
        times = [hv.tick().t for _ in range(5)]
        assert all(times[i] < times[i+1] for i in range(len(times)-1))

    def test_tick_at_limit_raises(self):
        hv = UOSHypervisor(n_grid=8, n_ticks=3)
        hv.boot()
        for _ in range(3):
            hv.tick()
        with pytest.raises(StopIteration):
            hv.tick()


# ---------------------------------------------------------------------------
# UOSHypervisor — run
# ---------------------------------------------------------------------------

class TestHypervisorRun:
    def test_run_returns_list(self):
        hv = UOSHypervisor(n_grid=8)
        hv.boot()
        result = hv.run(steps=5)
        assert isinstance(result, list)
        assert len(result) == 5

    def test_run_boots_if_needed(self):
        hv = UOSHypervisor(n_grid=8)
        result = hv.run(steps=3)
        assert len(result) == 3

    def test_run_state_types(self):
        hv = UOSHypervisor(n_grid=8)
        snaps = hv.run(steps=4)
        for s in snaps:
            assert isinstance(s, ManifoldState)

    def test_run_tick_sequence(self):
        hv = UOSHypervisor(n_grid=8)
        snaps = hv.run(steps=4)
        ticks = [s.tick for s in snaps]
        assert ticks == list(range(1, 5))


# ---------------------------------------------------------------------------
# UOSHypervisor — attach_to_host
# ---------------------------------------------------------------------------

class TestAttachToHost:
    def test_attach_sets_loads(self):
        hv = UOSHypervisor(n_grid=8)
        hv.attach_to_host(cpu_load=0.7, mem_load=0.3)
        assert abs(hv._host_cpu_load - 0.7) < 1e-9
        assert abs(hv._host_mem_load - 0.3) < 1e-9

    def test_attach_clamps_values(self):
        hv = UOSHypervisor(n_grid=8)
        hv.attach_to_host(cpu_load=2.0, mem_load=-0.5)
        assert hv._host_cpu_load == 1.0
        assert hv._host_mem_load == 0.0

    def test_attach_then_run(self):
        hv = UOSHypervisor(n_grid=8)
        hv.boot()
        hv.attach_to_host(cpu_load=0.5, mem_load=0.5)
        snaps = hv.run(steps=5)
        assert len(snaps) == 5


# ---------------------------------------------------------------------------
# UOSHypervisor — resource_report
# ---------------------------------------------------------------------------

class TestResourceReport:
    def _booted_hv(self):
        hv = UOSHypervisor(n_grid=8)
        hv.boot()
        return hv

    def test_report_keys(self):
        hv = self._booted_hv()
        report = hv.resource_report()
        expected = {
            "phi_mean", "phi_std", "B_rms", "g_det_mean",
            "tick", "t", "process_capacity", "invariant_ok",
        }
        assert expected.issubset(report.keys())

    def test_process_capacity_value(self):
        hv = self._booted_hv()
        assert hv.resource_report()["process_capacity"] == UOS_PROCESS_SLOTS

    def test_phi_mean_near_background(self):
        hv = self._booted_hv()
        report = hv.resource_report()
        assert abs(report["phi_mean"] - PHI_BACKGROUND) < 0.5

    def test_invariant_ok_is_bool(self):
        hv = self._booted_hv()
        assert isinstance(hv.resource_report()["invariant_ok"], bool)

    def test_g_det_mean_positive(self):
        hv = self._booted_hv()
        assert hv.resource_report()["g_det_mean"] > 0.0


# ---------------------------------------------------------------------------
# manifold_invariant_ok
# ---------------------------------------------------------------------------

class TestManifoldInvariantOk:
    def test_ok_after_boot(self):
        hv = UOSHypervisor(n_grid=16)
        hv.boot()
        assert hv.manifold_invariant_ok() is True

    def test_ok_after_run(self):
        hv = UOSHypervisor(n_grid=16)
        hv.run(steps=10)
        assert hv.manifold_invariant_ok() is True

    def test_false_before_boot(self):
        hv = UOSHypervisor(n_grid=8)
        assert hv.manifold_invariant_ok() is False


# ---------------------------------------------------------------------------
# History ring-buffer
# ---------------------------------------------------------------------------

class TestHistory:
    def test_history_grows(self):
        hv = UOSHypervisor(n_grid=8)
        hv.boot()
        for _ in range(5):
            hv.tick()
        # boot adds 1, each tick adds 1 → 6 total (≤ 128)
        assert len(hv.history) == 6

    def test_history_capped_at_128(self):
        hv = UOSHypervisor(n_grid=4, n_ticks=200)
        hv.boot()
        for _ in range(150):
            hv.tick()
        assert len(hv.history) <= 128
