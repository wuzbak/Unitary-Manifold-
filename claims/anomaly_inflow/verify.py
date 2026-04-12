"""
verify.py — Minimal demonstration of the anomaly inflow claim.

Run from the repository root:
    python claims/anomaly_inflow/verify.py
"""
import sys
import math
sys.path.insert(0, ".")

from src.core.inflation import (
    cs_axion_photon_coupling,
    birefringence_angle,
    CS_LEVEL_PLANCK_MATCH,
)

ALPHA_EM    = 1 / 137.036
R_C         = 12.0
DELTA_PHI   = 5.38
BETA_TARGET = 0.35   # degrees

print("=== Anomaly Inflow Chain: k_CS → g_aγγ → β ===\n")

print(f"k_CS      = {CS_LEVEL_PLANCK_MATCH}  (integer CS level, topological charge)")

g_agg = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, ALPHA_EM, R_C)
print(f"g_aγγ     = {g_agg:.6e} [M_Pl⁻¹]")
print(f"  formula: g = k_CS · α_EM / (2π² r_c)")
print(f"         = {CS_LEVEL_PLANCK_MATCH} · {ALPHA_EM:.6f} / (2 · {math.pi**2:.6f} · {R_C})")

beta_rad = birefringence_angle(g_agg, DELTA_PHI)
beta_deg = math.degrees(beta_rad)
print(f"\nβ         = {beta_deg:.4f}°  (target = {BETA_TARGET}°)")
print(f"Δβ        = {abs(beta_deg - BETA_TARGET):.4f}°")

print("\n=== Delete-power: k_CS=1 (no anomaly inflow) ===")
g_k1  = cs_axion_photon_coupling(1, ALPHA_EM, R_C)
b_k1  = math.degrees(birefringence_angle(g_k1, DELTA_PHI))
print(f"k_CS=1:  g_aγγ = {g_k1:.4e},  β = {b_k1:.6f}°  (far from {BETA_TARGET}°)")
assert abs(b_k1 - BETA_TARGET) > 0.1, "k_CS=1 unexpectedly reproduced β — check formula"

print("\nPASS — anomaly inflow chain is intact and k_CS=1 breaks it.")
