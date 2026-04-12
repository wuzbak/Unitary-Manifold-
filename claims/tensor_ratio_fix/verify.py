"""
verify.py — Minimal demonstration of the r-tension (tensor_ratio_fix claim).

Run from the repository root:
    python claims/tensor_ratio_fix/verify.py
"""
import sys
sys.path.insert(0, ".")

from src.core.inflation import ns_from_phi0, effective_phi0_kk, PLANCK_NS_CENTRAL, PLANCK_NS_SIGMA

BICEP_KECK_R_LIMIT = 0.036   # 95 % CL upper bound, BICEP/Keck 2022
N_SIGMA_PLANCK     = 1.0

print("n_w scan — checking ns and r constraints simultaneously")
print(f"{'n_w':>4}  {'φ₀_eff':>8}  {'nₛ':>8}  {'σ_Planck':>10}  {'r':>8}  {'r<0.036':>8}")
print("-" * 62)

n_w_satisfies_both = []
for n_w in range(1, 16):
    phi0_eff = effective_phi0_kk(1.0, n_winding=n_w)
    ns, r, eps, eta = ns_from_phi0(phi0_eff)
    sigma = (ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
    ns_ok = abs(sigma) <= N_SIGMA_PLANCK
    r_ok  = r < BICEP_KECK_R_LIMIT
    marker = "✓ BOTH" if (ns_ok and r_ok) else ""
    if ns_ok and r_ok:
        n_w_satisfies_both.append(n_w)
    print(f"{n_w:>4}  {phi0_eff:>8.3f}  {ns:>8.5f}  {sigma:>+10.2f}σ  {r:>8.5f}  {str(r_ok):>8} {marker}")

print()
if n_w_satisfies_both:
    print(f"WARNING: integer(s) satisfying BOTH: {n_w_satisfies_both}")
else:
    print("CONFIRMED: no integer n_w in [1,15] satisfies BOTH ns within 1σ AND r < 0.036.")
    print(f"  n_w=5: ns-consistent but r={ns_from_phi0(effective_phi0_kk(1.0,5))[1]:.4f} (tension)")
