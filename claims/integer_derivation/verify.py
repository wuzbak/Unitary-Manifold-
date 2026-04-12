"""
verify.py — Minimal demonstration of the k_CS = 74 derivation.

Run from the repository root:
    python claims/integer_derivation/verify.py
"""
import sys
import math
sys.path.insert(0, ".")

from src.core.inflation import (
    cs_level_for_birefringence,
    cs_axion_photon_coupling,
    birefringence_angle,
    CS_LEVEL_PLANCK_MATCH,
)

# Physical parameters used in the derivation
BETA_TARGET_DEG = 0.35        # observational hint (Minami & Komatsu / Diego-Palazuelos)
ALPHA_EM        = 1 / 137.036 # fine-structure constant
R_C             = 12.0        # compactification radius [M_Pl = 1]
DELTA_PHI       = 5.38        # field displacement |Δφ| from horizon exit to GW minimum

# Step 1: continuous k_CS value
k_float = cs_level_for_birefringence(BETA_TARGET_DEG, ALPHA_EM, R_C, DELTA_PHI)
k_int   = round(k_float)
print(f"Continuous k_CS : {k_float:.4f}")
print(f"Rounded  k_CS   : {k_int}")
print(f"Constant         : CS_LEVEL_PLANCK_MATCH = {CS_LEVEL_PLANCK_MATCH}")
assert k_int == CS_LEVEL_PLANCK_MATCH, f"Mismatch: {k_int} != {CS_LEVEL_PLANCK_MATCH}"

# Step 2: back-compute β(74) and compare with target
g_agg    = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
beta_rad = birefringence_angle(g_agg, DELTA_PHI)
beta_deg = math.degrees(beta_rad)
print(f"\nβ(k_CS=74) : {beta_deg:.4f}°   (target = {BETA_TARGET_DEG}°)")
residual = abs(beta_deg - BETA_TARGET_DEG)
print(f"Residual   : {residual:.4f}°")

# Step 3: confirm no other integer k ∈ [1, 100] has a smaller residual
best_k    = CS_LEVEL_PLANCK_MATCH
best_resid = residual
for k in range(1, 101):
    g = cs_axion_photon_coupling(k, ALPHA_EM, R_C)
    b = math.degrees(birefringence_angle(g, DELTA_PHI))
    r = abs(b - BETA_TARGET_DEG)
    if r < best_resid:
        best_resid = r
        best_k = k

print(f"\nBest integer in [1,100]: k = {best_k}  (residual = {best_resid:.6f}°)")
assert best_k == CS_LEVEL_PLANCK_MATCH, (
    f"Uniqueness FAILED: k={best_k} has smaller residual than k=74"
)
print("PASS — k_CS = 74 is the unique minimiser.")
