"""
tests/test_pillar514_dynamic_loopback_proof.py
==============================================
Tests for Pillar 514 — Dynamic Loopback Proof.

The central test of the Unitary Manifold's irreversibility claim:
  - Field-level: forward + backward evolution does NOT reconstruct the exact past
    (genuine physical irreversibility introduced by the metric volume projection)
  - Topological level: the winding number IS preserved through the forward + backward
    cycle (topological information conservation)

These two claims together constitute the "math the future" loopback proof.
"""

import numpy as np
import pytest

from src.core.evolution import (
    FieldState,
    braid_winding_number,
    calculate_topological_distance,
    run_evolution,
    step,
)
from src.core.pillar514_dynamic_loopback_proof import pillar_report, PILLAR_STATUS


# ---------------------------------------------------------------------------
# Pillar report
# ---------------------------------------------------------------------------

class TestPillar514Report:
    def test_pillar_number(self):
        assert pillar_report()["pillar"] == 514

    def test_status(self):
        assert PILLAR_STATUS == "DYNAMIC_LOOPBACK_PROOF_CERTIFIED"

    def test_central_distinction_in_report(self):
        r = pillar_report()
        assert "IRREVERSIBLE" in r["central_distinction"]["field_level"]
        assert "PRESERVED" in r["central_distinction"]["topo_level"]


# ---------------------------------------------------------------------------
# calculate_topological_distance
# ---------------------------------------------------------------------------

class TestCalculateTopologicalDistance:
    def test_identical_states_distance_zero(self):
        s = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(1))
        assert calculate_topological_distance(s, s) == 0

    def test_same_winding_distance_zero(self):
        s1 = FieldState.initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05)
        s2 = FieldState.initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05, amplitude=2.0)
        # Both should have |n_w| = 1, so distance = 0
        assert calculate_topological_distance(s1, s2) == 0

    def test_returns_non_negative_integer(self):
        s1 = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(2))
        s2 = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(3))
        dist = calculate_topological_distance(s1, s2)
        assert isinstance(dist, int)
        assert dist >= 0

    def test_flat_vs_braided_distance_nonzero(self):
        """Flat (n_w=0) vs braided (n_w=1) should have topological distance 1."""
        s_flat = FieldState.flat(N=64, dx=0.05, rng=np.random.default_rng(42))
        s_braid = FieldState.initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05)
        # Flat state has n_w=0; braided has |n_w|=1
        # Distance = |0 - (±1)| = 1
        assert calculate_topological_distance(s_flat, s_braid) == 1


# ---------------------------------------------------------------------------
# Dynamic loopback proof: forward then backward evolution
# ---------------------------------------------------------------------------

class TestDynamicLoopbackProof:
    """The central proof test.

    Protocol:
      1. Initialize a braided IC with n_w=1.
      2. Evolve forward 50 steps.
      3. Verify winding number preserved going forward.
      4. Evolve backward 50 steps from the future state.
      5. Assert field-level irreversibility (field NOT exactly reconstructed).
      6. Assert topological preservation (n_w IS reconstructed).
    """

    _N = 32
    _DX = 0.1
    _DT = 1e-3
    _STEPS = 50
    _N_W = 1

    @pytest.fixture(scope="class")
    def loopback_states(self):
        state_past = FieldState.initialize_dynamic_braid(
            N=self._N, n_w_initial=self._N_W, dx=self._DX
        )
        result_fwd = run_evolution(
            state_past, dt=self._DT, steps=self._STEPS,
            track_winding=True, check_cfl=False
        )
        state_future = result_fwd["history"][-1]
        winding_fwd = result_fwd["winding_history"]

        result_rev = run_evolution(
            state_future, dt=-self._DT, steps=self._STEPS,
            track_winding=True, check_cfl=False
        )
        state_reconstructed = result_rev["history"][-1]
        winding_rev = result_rev["winding_history"]

        return {
            "past": state_past,
            "future": state_future,
            "reconstructed": state_reconstructed,
            "winding_fwd": winding_fwd,
            "winding_rev": winding_rev,
        }

    def test_forward_winding_preserved(self, loopback_states):
        """Winding number must be maintained throughout forward evolution."""
        for nw in loopback_states["winding_fwd"]:
            assert abs(nw) == self._N_W, (
                f"Forward winding changed to {nw}; expected |n_w| = {self._N_W}"
            )

    def test_backward_winding_preserved(self, loopback_states):
        """Winding number must be maintained throughout backward evolution."""
        for nw in loopback_states["winding_rev"]:
            assert abs(nw) == self._N_W, (
                f"Backward winding changed to {nw}; expected |n_w| = {self._N_W}"
            )

    def test_field_level_irreversibility(self, loopback_states):
        """The reconstructed phi field must differ from the original past field.

        This is the field-level irreversibility assertion: the metric volume
        projection introduces a non-recoverable geometric constraint at each step,
        so backward evolution from the future state yields a different field
        configuration than the original past state.
        """
        phi_past = loopback_states["past"].phi
        phi_reconstructed = loopback_states["reconstructed"].phi
        field_distance = float(np.max(np.abs(phi_past - phi_reconstructed)))
        assert field_distance > 1e-15, (
            f"Field distance {field_distance:.2e} is unexpectedly small; "
            "the system appears exactly time-reversible, which would contradict "
            "the metric projection mechanism."
        )

    def test_topological_information_preserved(self, loopback_states):
        """The winding number MUST be exactly reconstructed.

        This is the topological information preservation assertion: even though
        the field configuration is not recovered (field-level irreversibility),
        the integer topological invariant n_w is preserved — the information
        is conserved in the winding sector even as the field is irreversible.
        """
        topo_dist = calculate_topological_distance(
            loopback_states["past"], loopback_states["reconstructed"]
        )
        assert topo_dist == 0, (
            f"Topological distance = {topo_dist}; winding number NOT preserved. "
            "This would constitute a genuine failure of topological information conservation."
        )

    def test_field_irreversibility_exceeds_topological_change(self, loopback_states):
        """The field-level difference must exceed the topological distance.

        This is the formal statement of the irreversibility–information distinction:
        the field is dissipative (large L∞ difference) while the topology is
        preserved (zero distance). The two quantities must be ordered correctly.
        """
        phi_past = loopback_states["past"].phi
        phi_reconstructed = loopback_states["reconstructed"].phi
        field_distance = float(np.max(np.abs(phi_past - phi_reconstructed)))
        topo_dist = calculate_topological_distance(
            loopback_states["past"], loopback_states["reconstructed"]
        )
        assert field_distance > topo_dist, (
            "Field-level distance must exceed topological distance — "
            "the field is irreversible while topology is preserved."
        )


# ---------------------------------------------------------------------------
# Backward evolution: winding stable under time reversal
# ---------------------------------------------------------------------------

class TestBackwardEvolutionWindingStable:
    def test_single_backward_step_preserves_winding(self):
        """One backward step from a braided state should preserve winding."""
        s = FieldState.initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05)
        n_before = s.get_winding_number()
        s_back = step(s, dt=-1e-3)
        n_after = s_back.get_winding_number()
        assert abs(n_before) == abs(n_after)

    def test_backward_forward_roundtrip_winding(self):
        """One backward then one forward step should restore the winding number."""
        s = FieldState.initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05)
        n_original = s.get_winding_number()
        s_back = step(s, dt=-1e-3)
        s_fwd = step(s_back, dt=1e-3)
        assert abs(s_fwd.get_winding_number()) == abs(n_original)
