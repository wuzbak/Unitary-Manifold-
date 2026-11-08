# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 793 — GRAVITON_MASS_BOUND_KK_SPECTRUM

Status: zero mode massless; nonzero KK mass is model-dependent and
        experimentally unestablished.

Derives from the 5D KK geometry that:
  1. The zero-mode (n=0) graviton is massless in the stated model assumptions.
  2. The remaining functions calculate illustrative values from supplied
     benchmark inputs; they do not establish a physical KK graviton mass.
  3. No detector verdict follows from a mass-only comparison: the spectrum,
     coupling and experimental channel contract are unreconciled.
  4. Width calculations are likewise conditional on the supplied inputs.

Key results
-----------
  Zero-mode graviton mass: m_G(0) = 0                         [EXACT_MASSLESS]
  Zero-mode mass: m_G(0) = 0                                 [MODEL ASSUMPTION]
  Illustrative formula output for supplied M_KK=1 TeV: ≈0.403 TeV
                                                            [NOT A MASS DETERMINATION]
  Detector verdict: MODEL_DEPENDENT_UNESTABLISHED
  Gate: GRAVITON_MASSLESS_KK_BOUND_DERIVED                     [GATE]
  Lean4: GravitonMassBound.lean +15 theorems (1051→1066)       [FORMAL]

Physics
-------
The 5D metric ansatz (Pillar 2) with RS1 warping:

    ds² = e^{-2kπRσ} η_{μν} dx^μ dx^ν − R² dσ²   σ ∈ [0,1]

yields 4D graviton Kaluza-Klein mass eigenstates m_n satisfying:

    m_n = x_n · k · e^{-kπR}

where x_n are zeros of the Bessel function J_1(x_n)=0:
    x_1 ≈ 3.832,  x_2 ≈ 7.016,  x_3 ≈ 10.173, ...

With k·e^{-kπR} represented by a separately supplied benchmark
M_KK = 1.0 TeV (not derived as a graviton mass by Pillar 790):

    M_G*(n=1) = x_1 · M_KK ≈ 3.83 TeV   [full RS1]

However, in the braided n_w=5 geometry the effective warp is modified:

    k_eff = k · c_s²   where c_s = 12/37

giving M_G*(n=1)_braided = M_KK · x_1 · c_s² ≈ 0.403 TeV for the supplied
inputs (illustrative formula output, not a measured or derived mass).

The zero-mode is protected by the Bianchi identity: ∇_μ G^{μν} = 0 in 5D
implies m₀ = 0 exactly.

These substitutions define an illustrative calculation only. Pillar 790
calculates a first mode of 24.622 GeV; its separately supplied 1 TeV benchmark
does not establish the graviton mass calculated here. The formula above gives
about 0.403 TeV for the supplied inputs, not the former 1 TeV headline.

The spin-2 KK graviton coupling and width below remain conditional model inputs:

    c_{G*} = k / (√2 · M_Pl)

Its total width:

    Γ_G* = c_{G*}² · M_G* · N_SM / (16π)

where N_SM = 39 (SM degrees of freedom coupling to T^{μν}).

Detector comparison
-------------------
The 4 TeV exclusion and k/M_Pl=0.1 are retained as supplied historical
benchmarks, not as a verified HL-LHC observation or a shared channel/model
contract. The old mass-only PASS/TENSION/FALSIFIED classification is retired.
EXP-5 remains MODEL_DEPENDENT_UNESTABLISHED until spectrum, coupling, and
detector-channel assumptions are reconciled.
"""

from __future__ import annotations
import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
N_W = 5
K_CS = 74
C_S = 12.0 / 37.0                  # braided sound speed
M_KK_TEV = 1.0                     # separately supplied benchmark; not a P790 graviton mass
M_KK_GEV = M_KK_TEV * 1e3
M_PL_GEV = 1.2209e19

# Bessel zeros J_1(x_n) = 0  (first 5)
BESSEL_ZEROS_J1 = [3.8317, 7.0156, 10.1735, 13.3237, 16.4706]

# RS1 benchmark coupling
K_OVER_MPL_BENCHMARK = 0.1         # standard RS1 benchmark
N_SM_DOF = 39                       # SM dof coupling to T^{μν}

# HL-LHC exclusion (EXP-5, Pillar 787)
HLLHC_EXCLUSION_TEV = 4.0          # supplied historical benchmark; not a current detector verdict

GATE = "GRAVITON_MASSLESS_KK_BOUND_DERIVED"

# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def zero_mode_mass() -> float:
    """Return exact zero-mode graviton mass = 0 (protected by 5D diff-inv)."""
    return 0.0


def kk_graviton_mass_tev(n: int = 1,
                          m_kk_tev: float = M_KK_TEV,
                          c_s: float = C_S) -> float:
    """
    Illustrative formula value for mode n (TeV); not an established mass.

    M_G*(n) = x_n · M_KK · c_s²

    where x_n is the n-th zero of J_1.
    """
    if n < 1 or n > len(BESSEL_ZEROS_J1):
        raise ValueError(f"Mode n must be 1..{len(BESSEL_ZEROS_J1)}, got {n}")
    x_n = BESSEL_ZEROS_J1[n - 1]
    return float(x_n * m_kk_tev * c_s**2)


def kk_mass_spectrum_tev(n_modes: int = 5) -> list[float]:
    """Return illustrative formula values (TeV) for modes 1..n_modes."""
    return [kk_graviton_mass_tev(n) for n in range(1, n_modes + 1)]


def kk_graviton_width_gev(n: int = 1,
                           k_over_mpl: float = K_OVER_MPL_BENCHMARK,
                           n_sm: int = N_SM_DOF) -> float:
    """
    Illustrative conditional width for mode n (GeV); not an observation.

    Γ_G* = (k/M_Pl)² · M_G* · N_SM / (16π)
    """
    m_gev = kk_graviton_mass_tev(n) * 1e3
    return float((k_over_mpl**2 * m_gev * n_sm) / (16.0 * np.pi))


def width_to_mass_ratio(n: int = 1,
                        k_over_mpl: float = K_OVER_MPL_BENCHMARK) -> float:
    """Illustrative conditional Γ/M ratio for KK mode n."""
    m_gev = kk_graviton_mass_tev(n) * 1e3
    width = kk_graviton_width_gev(n, k_over_mpl)
    return float(width / m_gev)


def hllhc_verdict(m_g_star_tev: float | None = None) -> str:
    """
    Retain the former function signature, but do not infer a detector verdict.

    The historical mass-only threshold logic is retired: values alone cannot
    supply the missing spectrum, coupling, and detector-channel contract.
    """
    return "MODEL_DEPENDENT_UNESTABLISHED"


def masslessness_proof_sketch() -> dict:
    """
    Return a machine-readable proof sketch that m_G(0) = 0.

    The proof uses the 5D Bianchi identity projected to 4D:
      ∇_μ T^{μν} = 0  ⟹  m₀ = 0 (no longitudinal polarisation).
    """
    return {
        "claim": "zero-mode graviton is massless",
        "mechanism": "5D diffeomorphism invariance + Z2 orbifold parity",
        "bianchi": "∇_μ G^{μν}_{5D} = 0 → m₀ = 0 in 4D effective theory",
        "status": "EXACT_MASSLESS",
        "caveats": [
            "Assumes unbroken 4D Lorentz invariance on the IR brane",
            "Loop corrections suppressed by (M_KK/M_Pl)² ≪ 1",
        ],
    }


def graviton_gate_summary() -> dict:
    """Machine-readable summary; calculated values are illustrative only."""
    m1 = kk_graviton_mass_tev(1)
    spectrum = kk_mass_spectrum_tev()
    verdict = hllhc_verdict(m1)
    return {
        "pillar": 793,
        "gate": GATE,
        "zero_mode_mass_gev": zero_mode_mass(),
        "illustrative_formula_value_n1_tev": round(m1, 3),
        "illustrative_formula_spectrum_tev": [round(m, 3) for m in spectrum],
        "width_to_mass_n1": round(width_to_mass_ratio(1), 4),
        "supplied_exclusion_benchmark_tev": HLLHC_EXCLUSION_TEV,
        "detector_verdict": verdict,
        "detector_verdict_status": "MODEL_DEPENDENT_UNESTABLISHED",
        "masslessness": masslessness_proof_sketch(),
        "lean4": "GravitonMassBound.lean +15 (1051→1066)",
        "detector_verdict_contract": (
            "No PASS, TENSION, or FALSIFIED classification without reconciled "
            "spectrum, coupling, and detector-channel assumptions."
        ),
    }


PILLAR_793_GATE = GATE
GRAVITON_GATE_SUMMARY = graviton_gate_summary
