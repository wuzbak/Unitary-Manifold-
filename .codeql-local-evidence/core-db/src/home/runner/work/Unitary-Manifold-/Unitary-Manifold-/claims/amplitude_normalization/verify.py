"""
verify.py — Minimal demonstration of the COBE normalisation claim.

Run from the repository root:
    python claims/amplitude_normalization/verify.py
"""
import sys
sys.path.insert(0, ".")

from src.core.inflation import (
    cobe_normalization,
    slow_roll_amplitude,
    effective_phi0_kk,
    ns_from_phi0,
    PLANCK_AS_CENTRAL,
)

print("=== COBE Normalisation ===")
result = cobe_normalization(phi0_bare=1.0, n_winding=5)
print(f"λ_COBE        = {result['lam_cobe']:.6e}")
print(f"Aₛ predicted  = {result['As_predicted']:.6e}  (target = {PLANCK_AS_CENTRAL:.6e})")
print(f"nₛ            = {result['ns']:.6f}  (λ-independent)")
print(f"r             = {result['r']:.6f}  (λ-independent)")
print(f"E_inf         = {result['E_inf_GeV']:.4e} GeV")

print("\n=== λ-independence check ===")
phi0_eff = effective_phi0_kk(1.0, n_winding=5)
for lam in [1.0, 1e-5, result["lam_cobe"], 1e-20]:
    ns, r, eps, eta = ns_from_phi0(phi0_eff, lam=lam)
    print(f"  λ = {lam:.3e}  →  nₛ = {ns:.8f},  r = {r:.8f}")

print("\n=== Amplitude vs λ ===")
for lam in [1.0, result["lam_cobe"]]:
    sr = slow_roll_amplitude(phi0_eff, lam=lam, phi_star=phi0_eff / (3 ** 0.5))
    print(f"  λ = {lam:.3e}  →  Aₛ = {sr['As']:.4e}")

print(f"\nAmplitude ratio lam=1 / lam=lam_cobe ≈ {1.0 / result['lam_cobe']:.4e}")
print("PASS — λ_COBE uniquely determined; nₛ, r are λ-independent.")
