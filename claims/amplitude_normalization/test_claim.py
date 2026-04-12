"""
test_claim.py — Tests validating the amplitude_normalization claim:
λ_COBE is uniquely fixed by Aₛ; nₛ and r are λ-independent.

Run from the repository root:
    python -m pytest claims/amplitude_normalization/test_claim.py -v
"""
import sys
sys.path.insert(0, ".")

import pytest
from src.core.inflation import (
    cobe_normalization,
    slow_roll_amplitude,
    effective_phi0_kk,
    ns_from_phi0,
    PLANCK_AS_CENTRAL,
)

PHI0_BARE = 1.0
N_WINDING = 5


class TestAmplitudeNormalization:
    """COBE normalisation uniquely fixes λ; nₛ and r are λ-independent."""

    def test_lam_cobe_reproduces_planck_as(self):
        """cobe_normalization() recovers Aₛ = Planck 2018 value to 1 % accuracy.

        DELETE-POWER TEST: remove or break cobe_normalization() and this fails.
        """
        result = cobe_normalization(PHI0_BARE, N_WINDING)
        rel_error = abs(result["As_predicted"] - PLANCK_AS_CENTRAL) / PLANCK_AS_CENTRAL
        assert rel_error < 0.01, (
            f"λ_COBE gives Aₛ = {result['As_predicted']:.4e}, "
            f"but Planck target is {PLANCK_AS_CENTRAL:.4e} "
            f"(relative error {rel_error:.4f} > 0.01)."
        )

    def test_lam_cobe_value_stable(self):
        """λ_COBE ≈ 6.99 × 10⁻¹⁵ (code-verified value)."""
        result = cobe_normalization(PHI0_BARE, N_WINDING)
        assert abs(result["lam_cobe"] - 6.988e-15) / 6.988e-15 < 0.01, (
            f"λ_COBE = {result['lam_cobe']:.6e}, expected ≈ 6.988e-15. "
            "Code changed — update claim."
        )

    def test_ns_lambda_independent(self):
        """nₛ is identical (to 8 decimal places) for λ=1 and λ=λ_COBE.

        DELETE-POWER TEST: introduce λ-dependence in spectral_index() and this fails.
        """
        result = cobe_normalization(PHI0_BARE, N_WINDING)
        phi0_eff = effective_phi0_kk(PHI0_BARE, n_winding=N_WINDING)
        ns_lam1, *_ = ns_from_phi0(phi0_eff, lam=1.0)
        ns_cobe, *_ = ns_from_phi0(phi0_eff, lam=result["lam_cobe"])
        assert abs(ns_lam1 - ns_cobe) < 1e-8, (
            f"nₛ differs: lam=1 → {ns_lam1:.10f}, lam=λ_COBE → {ns_cobe:.10f}. "
            "nₛ has acquired λ-dependence — claim broken."
        )

    def test_r_lambda_independent(self):
        """r is identical (to 8 decimal places) for λ=1 and λ=λ_COBE."""
        result = cobe_normalization(PHI0_BARE, N_WINDING)
        phi0_eff = effective_phi0_kk(PHI0_BARE, n_winding=N_WINDING)
        _, r_lam1, *_ = ns_from_phi0(phi0_eff, lam=1.0)
        _, r_cobe, *_ = ns_from_phi0(phi0_eff, lam=result["lam_cobe"])
        assert abs(r_lam1 - r_cobe) < 1e-8, (
            f"r differs: lam=1 → {r_lam1:.10f}, lam=λ_COBE → {r_cobe:.10f}. "
            "r has acquired λ-dependence — claim broken."
        )

    def test_as_proportional_to_lambda(self):
        """Aₛ ∝ λ: doubling λ doubles Aₛ exactly.

        DELETE-POWER TEST: add a λ-independent additive term to slow_roll_amplitude
        and this fails.
        """
        phi0_eff = effective_phi0_kk(PHI0_BARE, n_winding=N_WINDING)
        phi_star = phi0_eff / (3 ** 0.5)
        sr1  = slow_roll_amplitude(phi0_eff, lam=1.0,   phi_star=phi_star)
        sr2  = slow_roll_amplitude(phi0_eff, lam=2.0,   phi_star=phi_star)
        ratio = sr2["As"] / sr1["As"]
        assert abs(ratio - 2.0) < 1e-6, (
            f"Aₛ(2λ)/Aₛ(λ) = {ratio:.8f}, expected 2.0 exactly. "
            "Linear λ-scaling broken — COBE uniqueness argument collapses."
        )

    def test_energy_scale_order_of_magnitude(self):
        """Inflation energy scale E_inf ∈ [10¹⁵, 10¹⁷] GeV (GUT scale range)."""
        result = cobe_normalization(PHI0_BARE, N_WINDING)
        E_GeV = result["E_inf_GeV"]
        assert 1e15 < E_GeV < 1e17, (
            f"E_inf = {E_GeV:.3e} GeV is outside the expected GUT-scale range."
        )
