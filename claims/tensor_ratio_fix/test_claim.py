"""
test_claim.py — Tests validating the tensor_ratio_fix claim: r=0.097 is the
honest code-verified prediction and represents an active tension with BICEP/Keck.

Run from the repository root:
    python -m pytest claims/tensor_ratio_fix/test_claim.py -v
"""
import sys
sys.path.insert(0, ".")

import pytest
from src.core.inflation import (
    ns_from_phi0, effective_phi0_kk,
    PLANCK_NS_CENTRAL, PLANCK_NS_SIGMA,
)

BICEP_KECK_R_LIMIT   = 0.036   # BICEP/Keck 2022 95 % CL upper bound
NS_SIGMA_WINDOW      = 1.0     # number of σ defining "ns-consistent"
N_W_CANONICAL        = 5       # winding number required by ns


class TestTensorRatioTension:
    """r=0.097 (n_w=5) is the code-verified prediction; tension with r<0.036 is real."""

    def test_canonical_ns_within_planck_1sigma(self):
        """n_w=5 gives nₛ inside the Planck 1-σ window."""
        phi0_eff = effective_phi0_kk(1.0, n_winding=N_W_CANONICAL)
        ns, r, eps, eta = ns_from_phi0(phi0_eff)
        sigma_deviation = abs(ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        assert sigma_deviation <= NS_SIGMA_WINDOW, (
            f"n_w={N_W_CANONICAL}: ns={ns:.5f} is {sigma_deviation:.2f}σ from Planck. "
            "Expected ≤ 1σ."
        )

    def test_canonical_r_exceeds_bicep_keck_bound(self):
        """n_w=5 gives r > 0.036 — the tension is real and code-verified.

        DELETE-POWER TEST: change N_W_CANONICAL or the effective_phi0_kk formula
        and this test either fails (tension hidden) or triggers a different assertion.
        """
        phi0_eff = effective_phi0_kk(1.0, n_winding=N_W_CANONICAL)
        ns, r, eps, eta = ns_from_phi0(phi0_eff)
        assert r > BICEP_KECK_R_LIMIT, (
            f"r={r:.5f} is below BICEP/Keck bound {BICEP_KECK_R_LIMIT}. "
            "Either the tension has been resolved (update README) or the code changed."
        )

    def test_canonical_r_value_is_correct(self):
        """n_w=5 gives r ≈ 0.097 (code-verified)."""
        phi0_eff = effective_phi0_kk(1.0, n_winding=N_W_CANONICAL)
        ns, r, eps, eta = ns_from_phi0(phi0_eff)
        assert abs(r - 0.0973) < 0.001, (
            f"r={r:.5f} differs from documented value 0.0973 by > 0.001. "
            "Code changed — update claim."
        )

    def test_no_integer_n_w_satisfies_both_constraints(self):
        """No integer n_w in [1, 15] simultaneously satisfies ns within 1σ AND r < 0.036.

        DELETE-POWER TEST: if a new mechanism is added that suppresses r while
        preserving ns, this test will fail — which is the CORRECT signal to update
        the claim.
        """
        satisfies_both = []
        for n_w in range(1, 16):
            phi0_eff = effective_phi0_kk(1.0, n_winding=n_w)
            ns, r, eps, eta = ns_from_phi0(phi0_eff)
            ns_ok = abs(ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA <= NS_SIGMA_WINDOW
            r_ok  = r < BICEP_KECK_R_LIMIT
            if ns_ok and r_ok:
                satisfies_both.append(n_w)

        assert len(satisfies_both) == 0, (
            f"Integer n_w={satisfies_both} now satisfies BOTH constraints. "
            "The tension may be resolved — update the claim and this test."
        )

    def test_high_n_w_fixes_r_but_breaks_ns(self):
        """n_w=9 satisfies r < 0.036 but nₛ is excluded at > 4σ."""
        phi0_eff = effective_phi0_kk(1.0, n_winding=9)
        ns, r, eps, eta = ns_from_phi0(phi0_eff)
        assert r < BICEP_KECK_R_LIMIT, f"n_w=9 should give r < 0.036, got {r:.5f}"
        sigma_ns = abs(ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        assert sigma_ns > 4.0, (
            f"n_w=9: ns={ns:.5f} is only {sigma_ns:.1f}σ from Planck. "
            "Expected > 4σ exclusion."
        )

    def test_low_n_w_breaks_ns_low_side(self):
        """n_w=4 gives ns below the Planck 2σ window."""
        phi0_eff = effective_phi0_kk(1.0, n_winding=4)
        ns, r, eps, eta = ns_from_phi0(phi0_eff)
        sigma_ns = (PLANCK_NS_CENTRAL - ns) / PLANCK_NS_SIGMA   # ns too low → positive
        assert sigma_ns > 1.5, (
            f"n_w=4: ns={ns:.5f} only {sigma_ns:.1f}σ below Planck centre. "
            "Expected > 1.5σ low."
        )
