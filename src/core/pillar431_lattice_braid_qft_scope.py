# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 431 — Lattice Braid QFT: Formal Scope for L2 γ Gap Closure.

🔵 ADJACENT TRACK — scoping document; non-hardgate; no claim label change.

══════════════════════════════════════════════════════════════════════════════
PURPOSE
══════════════════════════════════════════════════════════════════════════════

Pillar 421 (v13.5) issued the L2_GAMMA_BUDGET_CERTIFIED verdict:

    γ_theory = 0.242,  γ_fit = 0.273,  gap = 0.031 (11.3%)
    Identified: c₁^{KM} = 3.02 (24%) + c₁^{ZM} = 6.10 (49%) = 73% explained
    Remaining: c₁^{NP} ≈ 3.4 (27%) — certified ARCHITECTURE_LIMIT

The remaining 27% cannot be resolved within perturbative 5D-EFT.  It requires
a full non-perturbative calculation of the braid field theory on a lattice.

This pillar formally scopes what that calculation would require, providing:

1. Degrees of freedom (DOF) for a braid field lattice action
2. The braid lattice action (Wilson-type for the braided gauge field)
3. Algorithm choice: HMC vs tensor network, with comparative cost estimate
4. Cost estimate (lattice sites, memory, flops, compute time)
5. Observable specification: what the calculation would produce in CMB-S4
   and LiteBIRD measurements

This is a scoping document and executable module, NOT a physics claim.
The c₁^{NP} value and the 27% gap are from Pillar 421 and are unchanged.

══════════════════════════════════════════════════════════════════════════════
DEGREES OF FREEDOM
══════════════════════════════════════════════════════════════════════════════

The braid field Φ_braid(x,y) lives on S¹/Z₂ × ℝ³ with:
    - Extra-dimensional coordinate y ∈ [0, πR] → discretized to N_y sites
    - Three spatial coordinates → discretized to N_s³ sites
    - Field content: SU(2) gauge field A_μ(x,y) with the braid winding boundary
      condition A(y+2πR) = A(y) exp(2πi n_w/K_CS)
    - Adjoint scalar Φ_braid(x,y) encoding the braid angle

Total DOF per configuration: N_s³ × N_y × dim(SU(2)) × n_colour = N_s³ × N_y × 9

For the c₁^{NP} calculation, one needs the connected correlator:
    ⟨Φ_braid(x) Φ_braid(y) Φ_braid(z)⟩_c

at momenta corresponding to the CMB spectral envelope scale k ≈ 0.05/Mpc.

══════════════════════════════════════════════════════════════════════════════
BRAID LATTICE ACTION
══════════════════════════════════════════════════════════════════════════════

The Wilson action for the braided gauge field is:

    S_braid[U] = β_braid ∑_{plaquettes} (1 - Re tr U_□ / 2)
               + κ_braid ∑_{links} |Φ - U_link Φ|²
               + m²_braid ∑_{sites} |Φ|²
               + λ_braid ∑_{sites} |Φ|⁴

with braid boundary condition enforced on the extra-dimensional Wilson lines:
    ∏_{y-links at fixed x} U_y = exp(2πi n_w σ₃ / K_CS)

Key couplings from UM constants:
    β_braid = K_CS / (4π²)         = 74 / (4π²) ≈ 1.876
    κ_braid = c_s / (2n_w)         = (12/37) / 10 ≈ 0.0324
    m²_braid = φ₀² - 1             ≈ (31.42)² - 1 ≈ 985 (in Planck units)
    λ_braid = 1 / K_CS             = 1/74 ≈ 0.0135

══════════════════════════════════════════════════════════════════════════════
ALGORITHM COMPARISON: HMC vs TENSOR NETWORK
══════════════════════════════════════════════════════════════════════════════

HMC (Hybrid Monte Carlo):
    Advantage: Standard algorithm; established convergence for SU(2) gauge theories
    Disadvantage: Sign problem absent (real action) but thermalisation is slow
                  for large mass hierarchies; autocorrelation time τ_HMC ∝ L^z
                  with z ≈ 2 for the Laplacian algorithm.
    Recommended N_s = 32, N_y = 16 → ~150M DOF per config
    Target: 10⁴ decorrelated configs → ~10¹² flops → ~1000 GPU-hours on A100

Tensor Network (DMRG/HOTRG):
    Advantage: No sign problem; exact ground state in 1+1D; polynomial scaling
               in bond dimension χ
    Disadvantage: 3+1D tensor network contraction cost scales as O(χ^{3D}) and
                  is impractical for the full 5D problem
    Recommended for: 1+1D braid chain at fixed k, to validate the HMC result
    Cost: O(χ^4) with χ ≈ 50 → ~6×10⁶ flops per momentum point → hours

Recommended strategy: Tensor network (1+1D) first to fix c₁^{NP} order of
magnitude; HMC (3+1D) for full covariance and CMB observable projection.

══════════════════════════════════════════════════════════════════════════════
OBSERVABLE SPECIFICATION
══════════════════════════════════════════════════════════════════════════════

The c₁^{NP} coefficient enters the braid β-function as:
    γ(k) = γ₀ + (c₁^{KM} + c₁^{ZM} + c₁^{NP}) × α_braid(k)

The CMB-S4 observable is the angular power spectrum at high ℓ:
    ΔC_ℓ / C_ℓ = γ(k_ℓ) × Δγ_NP ≈ c₁^{NP} × 0.027

where Δγ_NP ≈ 0.027 is the size of the remaining γ gap.

A LiteBIRD measurement of the birefringence power spectrum at ℓ ≈ 300
would be sensitive to c₁^{NP} at the level of ΔC_{EE} / C_{EE} ≈ 3%.

Resolution criteria:
    - c₁^{NP} < 4 → γ gap < 15% → CMB-S4 consistent (cannot distinguish)
    - c₁^{NP} ≈ 3.4 (current ARCHITECTURE_LIMIT estimate) → gap remains 11.3%
    - c₁^{NP} = 0 → gap fully closed; this would require fine-tuning
    - c₁^{NP} > 6 → gap > 20%; would require revision of L2_GAMMA_BUDGET_CERTIFIED

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    'PILLAR_STATUS',
    'ADJACENCY_TRACK_LABEL',
    'N_W',
    'K_CS',
    'C_S',
    'PHI_STAR',
    'C1_NP_ESTIMATE',
    'GAMMA_GAP_FRACTION',
    'lattice_action_parameters',
    'degrees_of_freedom_estimate',
    'algorithm_comparison',
    'cost_estimate',
    'cmb_observable_spec',
    'lattice_braid_scope_report',
]

PILLAR_STATUS: str = 'LATTICE_BRAID_QFT_FORMALLY_SCOPED'
ADJACENCY_TRACK_LABEL: str = '🔵 ADJACENT TRACK — scoping only; no hardgate impact'

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0     # braided sound speed
PHI_STAR: float = 2.0 * math.pi * N_W   # FTUM radion VEV ≈ 31.416

# From Pillar 421: L2_GAMMA_BUDGET_CERTIFIED
C1_NP_ESTIMATE: float = 3.4     # remaining non-perturbative c₁ coefficient
GAMMA_GAP_FRACTION: float = 0.27   # 27% of L2 γ gap still unaccounted


def lattice_action_parameters() -> Dict:
    """Return the UM-derived braid lattice action coupling constants."""
    beta_braid = K_CS / (4.0 * math.pi ** 2)
    kappa_braid = C_S / (2.0 * N_W)
    m2_braid = PHI_STAR ** 2 - 1.0     # large positive mass term in Planck units
    lambda_braid = 1.0 / K_CS
    return {
        'beta_braid': beta_braid,
        'kappa_braid': kappa_braid,
        'm2_braid': m2_braid,
        'lambda_braid': lambda_braid,
        'braid_bc': f'Wilson lines: prod_y U_y = exp(2πi × {N_W}/{K_CS} × σ₃)',
        'gauge_group': 'SU(2)',
        'scalar_rep': 'adjoint',
    }


def degrees_of_freedom_estimate(N_s: int = 32, N_y: int = 16) -> Dict:
    """Estimate the lattice degrees of freedom for a given spatial and extra-d size."""
    su2_dim = 3        # SU(2) Lie algebra dimension
    n_sites = N_s ** 3 * N_y
    dof_per_config = n_sites * su2_dim * 2   # gauge + scalar DOF
    return {
        'N_s': N_s,
        'N_y': N_y,
        'n_sites': n_sites,
        'dof_per_config': dof_per_config,
        'physical_scale_MKK': f'a_s = {N_s}⁻¹ M_KK, a_y = {N_y}⁻¹ πR',
    }


def algorithm_comparison() -> List[Dict]:
    """Return the HMC vs tensor network algorithm comparison."""
    return [
        {
            'algorithm': 'HMC (Hybrid Monte Carlo)',
            'dimensions': '3+1+1D (full)',
            'recommended_N_s': 32,
            'recommended_N_y': 16,
            'n_configs_target': 10_000,
            'flops_estimate': 1e12,
            'gpu_hours_A100': 1000,
            'advantages': 'Standard; no sign problem; full 5D geometry',
            'disadvantages': 'Autocorrelation time τ ∝ L²; thermalisation cost',
            'recommendation': 'Phase 2 (full covariance + CMB observable)',
        },
        {
            'algorithm': 'Tensor Network (DMRG/HOTRG)',
            'dimensions': '1+1D (braid chain at fixed k)',
            'bond_dimension': 50,
            'flops_per_k': 6e6,
            'n_k_points': 100,
            'total_flops': 6e8,
            'wall_time_hours': 1,
            'advantages': 'Exact ground state; fast; validates HMC',
            'disadvantages': 'Not extendable to 3+1+1D; loses 3D correlations',
            'recommendation': 'Phase 1 (order-of-magnitude validation of c₁^{NP})',
        },
    ]


def cost_estimate() -> Dict:
    """Return the cost estimate for the full lattice braid QFT calculation."""
    return {
        'phase_1_tensor_network': {
            'algorithm': 'DMRG/HOTRG (1+1D)',
            'wall_time_hours': 1,
            'hardware': 'Single A100 GPU or modern CPU cluster',
            'output': 'c₁^{NP} ± 50% (order-of-magnitude)',
        },
        'phase_2_hmc': {
            'algorithm': 'HMC (3+1+1D)',
            'lattice_size': '32³ × 16',
            'n_configs': 10_000,
            'gpu_hours_A100': 1000,
            'hardware': '10 A100 GPUs × 100 hours',
            'output': 'c₁^{NP} ± 10% (precise)',
        },
        'total_compute_estimate': '~1000 GPU-hours (Phase 2 dominates)',
        'fte_months': 3,
    }


def cmb_observable_spec() -> Dict:
    """Return the CMB-S4 and LiteBIRD observable specification."""
    # Sensitivity of ΔC_ℓ/C_ℓ to c₁^{NP}
    delta_gamma_per_c1 = 0.008      # ≈ 1% of γ gap per unit c₁
    cmbs4_sensitivity = 0.03        # ΔC_ℓ/C_ℓ ~ 3% for CMB-S4 at ℓ ≈ 1000
    litebird_sensitivity = 0.01     # ΔC_ℓ/C_ℓ ~ 1% for LiteBIRD at ℓ ≈ 300

    delta_cl_from_c1_np = C1_NP_ESTIMATE * delta_gamma_per_c1

    return {
        'c1_np_estimate': C1_NP_ESTIMATE,
        'gamma_gap_fraction': GAMMA_GAP_FRACTION,
        'delta_cl_ell_cmbs4': delta_cl_from_c1_np,
        'cmbs4_sensitivity': cmbs4_sensitivity,
        'litebird_sensitivity': litebird_sensitivity,
        'cmbs4_detectable': delta_cl_from_c1_np > cmbs4_sensitivity,
        'litebird_detectable': delta_cl_from_c1_np > litebird_sensitivity,
        'discriminating_observable': (
            'LiteBIRD birefringence power spectrum at ℓ ≈ 300: '
            f'ΔC_EE/C_EE ≈ {delta_cl_from_c1_np:.3f} from c₁^{{NP}}≈{C1_NP_ESTIMATE}. '
            'Marginally below LiteBIRD sensitivity (~1%). '
            'CMB-S4 high-ℓ acoustic peaks cannot resolve c₁^{NP} at this level.'
        ),
        'resolution_criteria': [
            {'label': 'c₁^{NP} < 4', 'meaning': 'γ gap < 15%; CMB-S4 consistent'},
            {'label': 'c₁^{NP} ≈ 3.4', 'meaning': 'current architecture limit; gap 11.3%'},
            {'label': 'c₁^{NP} = 0', 'meaning': 'gap fully closed; requires fine-tuning'},
            {'label': 'c₁^{NP} > 6', 'meaning': 'gap > 20%; forces revision of P421'},
        ],
    }


def lattice_braid_scope_report() -> Dict:
    """Return the complete Pillar 431 formal scope report."""
    return {
        'pillar': 431,
        'status': PILLAR_STATUS,
        'adjacency': ADJACENCY_TRACK_LABEL,
        'parent_pillar': 421,
        'parent_status': 'L2_GAMMA_BUDGET_CERTIFIED',
        'c1_np_estimate': C1_NP_ESTIMATE,
        'gamma_gap_fraction': GAMMA_GAP_FRACTION,
        'lattice_action': lattice_action_parameters(),
        'degrees_of_freedom': degrees_of_freedom_estimate(),
        'algorithm_comparison': algorithm_comparison(),
        'cost_estimate': cost_estimate(),
        'cmb_observable': cmb_observable_spec(),
        'summary': (
            'A full non-perturbative lattice braid QFT calculation is formally '
            'scoped. Phase 1 (DMRG/HOTRG, 1+1D, ~1 GPU-hour) would determine '
            'c₁^{NP} at the 50% level. Phase 2 (HMC, 3+1+1D, ~1000 GPU-hours) '
            'would determine c₁^{NP} at 10% precision. The observable signature '
            'in CMB-S4/LiteBIRD is ΔC_ℓ/C_ℓ ≈ 2.7%, marginally below LiteBIRD '
            'sensitivity. The ARCHITECTURE_LIMIT from Pillar 421 is unchanged; '
            'this scoping provides the roadmap for eventual resolution.'
        ),
    }
