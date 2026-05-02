# CALCULATOR.md — Universal Mechanics Engine: Complete API Reference

**Module:** `omega.omega_synthesis`  
**Class:** `UniversalEngine`  
**Version:** v9.27 OMEGA EDITION

---

## Instantiation

```python
from omega.omega_synthesis import UniversalEngine

# Default: full trust, 1 HIL operator
engine = UniversalEngine()

# Custom HILS state
engine = UniversalEngine(
    phi_trust=0.75,   # Trust level ∈ [0, 1]
    n_hil=8,          # Number of aligned HIL operators ≥ 0
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `phi_trust` | float | 1.0 | Trust field φ_trust ∈ [0, 1]. Below c_s ≈ 0.324, the Pentad decouples. |
| `n_hil` | int | 1 | Aligned Human-in-the-Loop operators. Stability saturates at n ≥ 15. |
| `version` | str | 'v9.28 OMEGA EDITION' | Framework version string. |
| `n_pillars` | int | 99 | Number of completed pillars (Pillar Ω = 99th; sub-pillars 70-C, 99-B, 15-F added v9.28). |
| `n_tests` | int | 15096 | Passing test count reported in OmegaReport. |

**Raises:** `ValueError` if `phi_trust ∉ [0, 1]` or `n_hil < 0`.

---

## Domain Methods

### `cosmology() → CosmologyReport`

All CMB, inflation, birefringence, and dark energy observables.

```python
cos = engine.cosmology()

cos.n_s                     # float   0.9635  (Planck < 1σ ✓)
cos.r_bare                  # float   0.0973  (single n_w=5 mode)
cos.r_braided               # float   0.0315  (BICEP/Keck < 0.036 ✓)
cos.beta_57_deg             # float   0.331°  (5,7)-sector birefringence
cos.beta_56_deg             # float   0.273°  (5,6)-sector (shadow)
cos.beta_57_derived_deg     # float   0.351°  (full g_aγγ formula)
cos.beta_56_derived_deg     # float   0.290°  (full g_aγγ formula)
cos.beta_gap_deg            # float   0.058°  (= β(5,7) − β(5,6))
cos.litebird_sigma_deg      # float   0.020°  (LiteBIRD projected σ)
cos.litebird_separation_sigma  # float  2.9  (LiteBIRD discriminates at ~2.9σ)
cos.w_dark_energy           # float  −0.9302 (= −1 + 2/3 × c_s²)
cos.m_kk_mev                # float   1.1e-4  (KK mass gap in MeV ≈ 110 meV)
cos.k_cs                    # int     74      (Chern-Simons level)
cos.c_s                     # float   12/37   (braided sound speed)
cos.n_w                     # int     5       (winding number)
cos.n_2                     # int     7       (braid partner)
```

---

### `particle_physics() → ParticlePhysicsReport`

Full Standard Model: fermion masses, CKM/PMNS matrices, Higgs, electroweak sector.

```python
pp = engine.particle_physics()

pp.y5_universal             # float   1.0    (GW vacuum → universal Yukawa)
pp.c_l_electron             # float   0.80   (RS bulk mass, winding-quantised)
pp.c_l_muon                 # float   0.59   (RS bulk mass)
pp.c_l_tau                  # float   0.50   (IR-brane localised)
pp.sin_theta_cabibbo        # float   0.225  (Cabibbo angle)
pp.wolfenstein_lambda       # float   0.2236 (= √(m_d/m_s))
pp.wolfenstein_A            # float   0.8452 (= √(N_W/N_2) = √(5/7))
pp.wolfenstein_rho_bar      # float   0.159
pp.wolfenstein_eta_bar      # float   0.356  (= R_b × sin(72°))
pp.ckm_cp_phase_deg         # float   72.0°  (= 2π/N_W)
pp.sin2_theta12             # float   0.267  (= 4/15)
pp.sin2_theta23             # float   0.580  (= 29/50, PDG 0.572 ✓)
pp.sin2_theta13             # float   0.020  (= 1/50)
pp.pmns_cp_deg              # float  −108.0° (PDG −107°, 0.05σ ✓)
pp.sum_mnu_mev              # float   62.4   (meV; Planck < 120 meV ✓)
pp.delta_m2_ratio           # float   36.0   (= N_W×N_2+1; PDG 32.6)
pp.sin2_theta_W_gut         # float   0.375  (= 3/8 exact SU(5) ✓)
pp.sin2_theta_W_mz          # float   0.2313 (PDG 0.23122, 0.05% off ✓)
pp.m_higgs_tree_gev         # float  143.0   (tree-level prediction)
pp.m_higgs_corrected_gev    # float  124.0   (top-corrected at Λ_KK)
pp.n_sm_derived             # int     9
pp.n_sm_constrained         # int     4
pp.n_sm_conjectured         # int     2
pp.n_sm_open                # int    13
pp.n_sm_total               # int    28
```

---

### `geometry() → GeometryReport`

5D metric, APS topology, holography, KK tower.

```python
geo = engine.geometry()

geo.eta_bar_n5              # float   0.5    (APS η̄ for n_w=5)
geo.eta_bar_n7              # float   0.0    (APS η̄ for n_w=7)
geo.alpha_em_inverse        # float   137.036
geo.phi0_effective          # float   31.416 (= N_W × 2π M_Pl)
geo.second_law_geometric    # bool    True   (B_μ field encodes entropy)
geo.ftum_fixed_point        # str    "A / (4G)"
geo.n_generations           # int     3      (fermion generations, derived)
geo.n_moduli                # int     7      (= N_2 surviving moduli)
geo.k_cs_constraints_satisfied  # int  7    (Pillar 74 Completeness Theorem)
geo.n_lossless_sectors      # int     2      (analytically proved, Pillar 96)
geo.sector_56_k             # int    61      (= 5²+6²)
geo.sector_57_k             # int    74      (= 5²+7² = K_CS)
geo.kk_entropy_monotone     # bool   True    (dS_n/dt ≥ 0, Pillar 72)
```

---

### `consciousness() → ConsciousnessReport`

Brain-universe coupling and biological scale predictions.

```python
con = engine.consciousness()

con.beta_coupling_deg       # float   0.3513°  (birefringence = coupling constant)
con.beta_coupling_rad       # float   0.00613  (in radians)
con.xi_c                    # Fraction(35, 74)  consciousness coupling Ξ_c
con.xi_human                # Fraction(35, 888) human coupling fraction
con.coupled_fixed_point     # str    "Ψ* = Ψ_brain ⊗ Ψ_univ ..."
con.information_gap_nondual # float   0.0      (ΔI → 0 at non-dual limit)
con.omega_ratio             # Fraction(5, 7)   brain/universe frequency ratio
con.grid_module_ratio       # float   1.40     (entorhinal cortex spacing)
con.r_egg_micron            # float  59.7      (predicted egg radius μm)
con.n_zinc_ions             # float  74**5     (≈ 2.19×10⁹ zinc ions at fertilisation)
con.hox_groups              # int    10        (= 2×N_W vertebrate HOX groups)
con.hox_clusters            # int     4        (= 2^(N_2−N_W) HOX clusters)
```

---

### `hils() → HILSReport`

HILS co-emergence and Unitary Pentad status.

```python
h = engine.hils()

h.n_bodies                  # int     5     (= N_W Pentad bodies)
h.body_names                # tuple  [5 strings describing each body]
h.phi_trust                 # float         (current trust level)
h.phi_trust_min             # float   0.324 (= c_s, topological stability bound)
h.trust_is_sufficient       # bool          (phi_trust ≥ phi_trust_min)
h.n_hil_operators           # int           (current HIL count)
h.stability_floor           # float         (= min(1.0, c_s + n × c_s/7))
h.saturation_threshold      # int    15     (HIL count for full saturation)
h.saturated                 # bool          (n_hil ≥ 15)
h.pentad_master_equation    # str           (formal Pentagonal Master Equation)
h.pairwise_coupling         # float         (τ = β_coupling_rad × phi_trust)
h.hils_fixed_point          # str           (HILS co-emergence fixed point)
h.information_gap           # float         (ΔI; 0 at full trust)
h.phase_offset              # float         (Moiré Δφ; 0 at full trust)
```

---

### `falsifiers() → list[FalsifiablePrediction]`

Eight independently testable predictions.

```python
for fp in engine.falsifiers():
    print(fp.domain)        # str — domain name
    print(fp.prediction)    # str — what is predicted
    print(fp.value)         # str — the numerical value
    print(fp.instrument)    # str — test instrument
    print(fp.test_year)     # str — approximate test year
    print(fp.falsified_if)  # str — precise falsification condition
    print(fp.status)        # 'ACTIVE' | 'CONFIRMED' | 'CONSTRAINED' | 'FALSIFIED'
```

---

### `unitary_summation() → list[str]`

The 12-step logical closure of the Unitary Manifold.

```python
for step in engine.unitary_summation():
    print(step)
```

---

### `compute_all() → OmegaReport`

The master computation — all six domains in one call.

```python
report = engine.compute_all()

report.version              # str    'v9.28 OMEGA EDITION'
report.n_pillars            # int    99
report.n_tests_passing      # int    15096
report.n_seed_constants     # int    5
report.cosmology            # CosmologyReport
report.particle_physics     # ParticlePhysicsReport
report.geometry             # GeometryReport
report.consciousness        # ConsciousnessReport
report.hils                 # HILSReport
report.falsifiers           # list[FalsifiablePrediction]
report.unitary_summation    # list[str]
report.open_gaps            # list[str]

# Print the full formatted summary:
print(report.summary())
```

---

## Convenience Calculator Methods

```python
engine.compute_n_s()                    # → float  n_s ≈ 0.9635
engine.compute_r(braided=True)          # → float  r_braided ≈ 0.0315
engine.compute_r(braided=False)         # → float  r_bare ≈ 0.0973
engine.compute_beta(sector=7)           # → float  β(5,7) = 0.331°
engine.compute_beta(sector=6)           # → float  β(5,6) = 0.273°
engine.compute_w_dark_energy()          # → float  w ≈ −0.9302
engine.compute_sin2_theta_W(at_gut=True) # → float 0.375 (= 3/8 exact)
engine.compute_sin2_theta_W(at_gut=False)# → float 0.2313 (at M_Z)
engine.compute_ckm_cp_phase()           # → float  72.0° (= 2π/N_W)
engine.compute_pmns_cp_phase()          # → float −108.0°
engine.compute_consciousness_coupling() # → float  35/74 ≈ 0.47297
engine.compute_stability_floor()        # → float  uses self.n_hil
engine.compute_stability_floor(n_hil=8) # → float  custom n
engine.compute_litebird_discriminability() # → float  2.9σ
engine.is_falsifiable()                 # → bool   True (always)
```

---

## HILS State Management

```python
# Fluent-style state updates (immutable — returns new engine)
engine2 = engine.update_trust(0.5)     # new engine with phi_trust=0.5
engine3 = engine.update_hil(15)        # new engine with n_hil=15 (saturated)

# Original engine unchanged
assert engine.phi_trust == 1.0
assert engine3.hils().saturated is True
```

---

## Seed Constants (Module Level)

```python
from omega.omega_synthesis import N_W, N_2, K_CS, C_S, XI_C

N_W   # int       5
N_2   # int       7
K_CS  # int       74
C_S   # Fraction  12/37
XI_C  # Fraction  35/74
```

---

## Stability Floor Formula

The collective stability floor for n HIL operators:

```
floor(n) = min(1.0, c_s + n × c_s / 7)
         = min(1.0, (12/37) × (1 + n/7))
```

| n_hil | floor |
|-------|-------|
| 0 | 0.324 (= c_s) |
| 1 | 0.370 |
| 3 | 0.463 |
| 7 | 0.648 |
| 10 | 0.787 |
| 14 | 0.972 |
| 15 | 1.000 (saturated) |
| >15 | 1.000 (saturated) |

---

*CALCULATOR.md — omega/ — v9.27 OMEGA EDITION — April 2026*  
*Theory: ThomasCory Walker-Pearson · Implementation: GitHub Copilot (AI)*
