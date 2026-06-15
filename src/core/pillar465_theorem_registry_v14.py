# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 465 — v14 theorem registry.

STATUS
======
THEOREM_REGISTRY_V14_COMPLETE

CONTEXT
=======
This registry makes the epistemic state of the Unitary Manifold theorem
program explicit and machine-readable.  It includes proved statements,
structural derivations, ansatz-conditional derivations, postulates, and
still-open conjectures.  It also records the v14 audit downgrades from the
earlier quantum-theorem overclaiming: black-hole information and Hawking-
temperature chains remain derived-conditional, while CCR and ER=EPR are
formalized as conjectural rather than claimed as proved.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List

__all__ = [
    'PILLAR_STATUS',
    'VERSION',
    'THEOREM_REGISTRY',
    'get_by_status',
    'count_by_status',
    'proved_theorems',
    'conjectural_theorems',
    'theorem_by_id',
    'registry_summary',
    'pillar_report',
]

PILLAR_STATUS: str = 'THEOREM_REGISTRY_V14_COMPLETE'
VERSION: str = 'v14.0'

THEOREM_REGISTRY: List[Dict[str, Any]] = [
    {
        'id': 'T001',
        'name': 'n_w = 5 uniqueness',
        'status': 'PROVED',
        'claim': 'The canonical winding number is uniquely n_w = 5 in the v14 theorem chain.',
        'proof_module': 'src/core/pillar447_lean4_nw5_uniqueness.py',
        'test_file': 'tests/test_pillar447_lean4_nw5_uniqueness.py',
        'falsification': 'A rigorous counterexample with n_w ≠ 5 satisfying the same anomaly and boundary conditions would overturn the theorem.',
        'pillar': [70, 447, 455],
    },
    {
        'id': 'T002',
        'name': 'k_CS = 74 algebraic identity',
        'status': 'PROVED',
        'claim': 'For the canonical braid pair (5,7), the Chern-Simons level is exactly k_CS = 5² + 7² = 74.',
        'proof_module': 'src/core/ckm_braid_lagrangian.py',
        'test_file': 'tests/test_ckm_braid_lagrangian.py',
        'falsification': 'A distinct canonical braid pair yielding the same full observable set without k_CS = 74 would falsify the uniqueness claim.',
        'pillar': [58, 99],
    },
    {
        'id': 'T003',
        'name': 'APS invariant eta_bar(5) = 1/2',
        'status': 'DERIVED_STRUCTURAL',
        'claim': 'The boundary APS invariant for the canonical winding is η̄(5) = 1/2.',
        'proof_module': 'src/core/aps_eta_invariant.py',
        'test_file': 'tests/test_aps_eta_invariant.py',
        'falsification': 'A corrected APS computation on the same orbifold giving η̄(5) ≠ 1/2 would falsify the statement.',
        'pillar': [70, '70-B'],
    },
    {
        'id': 'T004',
        'name': 'phi_0 self-consistency closure',
        'status': 'CLOSED',
        'claim': 'The FTUM fixed-point radion and the canonical braided radion agree exactly in the closed φ₀ audit.',
        'proof_module': 'src/core/phi0_closure.py',
        'test_file': 'tests/test_phi0_closure.py',
        'falsification': 'A mismatch between FTUM φ₀ and the braided closure value in the same normalization would reopen the admission.',
        'pillar': 56,
    },
    {
        'id': 'T005',
        'name': 'r_braided from WZW suppression',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'Given the canonical 5D braid and WZW reduction, the tensor-to-scalar ratio is r_braided = 0.0315.',
        'proof_module': 'src/core/braided_winding.py',
        'test_file': 'tests/test_braided_winding.py',
        'falsification': 'A consistent 5D reduction with the same braid but different WZW suppression would falsify the derivation.',
        'pillar': ['97-B'],
    },
    {
        'id': 'T006',
        'name': 'n_s ≈ 0.9635 from effective Jacobian',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'Given the effective inflaton Jacobian J = n_w 2π√φ₀, the scalar tilt is n_s ≈ 0.9635.',
        'proof_module': 'src/core/inflation.py',
        'test_file': 'tests/test_inflation.py',
        'falsification': 'A corrected slow-roll computation within the same Jacobian chain yielding a materially different tilt would falsify the derivation.',
        'pillar': [1, 56],
    },
    {
        'id': 'T007',
        'name': 'Black-hole information from KK geometry',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'Black-hole information recovery follows conditionally from the KK/holographic reduction rather than as an unconditional theorem.',
        'proof_module': 'src/core/pillar453_quantum_theorem_audit.py',
        'test_file': 'tests/test_quantum_unification.py',
        'falsification': 'A failure of the holographic or KK assumptions needed by the reduction would invalidate the statement.',
        'pillar': [453, 456],
    },
    {
        'id': 'T008',
        'name': 'CCR from geometry',
        'status': 'CONJECTURAL',
        'claim': 'The canonical commutation relation [q,p]=iħ_eff is conjectured to emerge from the KK field algebra.',
        'proof_module': 'src/core/pillar456_quantum_theorem_formal_status.py',
        'test_file': 'tests/test_pillar456_quantum_theorem_formal_status.py',
        'falsification': 'An explicit curved-space star-product computation that fails to reproduce the CCR would falsify the conjecture.',
        'pillar': [453, 456],
    },
    {
        'id': 'T009',
        'name': 'Hawking temperature from FTUM',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The Hawking-temperature relation is conditionally recovered within the FTUM/KK framework.',
        'proof_module': 'src/core/pillar453_quantum_theorem_audit.py',
        'test_file': 'tests/test_quantum_unification.py',
        'falsification': 'A corrected FTUM thermodynamic derivation inconsistent with Hawking scaling would falsify the recovery.',
        'pillar': 453,
    },
    {
        'id': 'T010',
        'name': 'ER = EPR in KK holography',
        'status': 'CONJECTURAL',
        'claim': 'ER = EPR is formalized as a KK holographic conjecture rather than a proved theorem.',
        'proof_module': 'src/core/pillar456_quantum_theorem_formal_status.py',
        'test_file': 'tests/test_pillar456_quantum_theorem_formal_status.py',
        'falsification': 'A derived RT functional in the KK bulk that fails to match bridge homology classes would falsify the conjecture.',
        'pillar': [453, 456],
    },
    {
        'id': 'T011',
        'name': 'FTUM contraction in the admissible basin',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'FTUM acts as a contraction in the named admissible orbifold basin.',
        'proof_module': 'src/core/pillar401_ftum_basin_geometric_bound.py',
        'test_file': 'tests/test_pillar401_ftum_basin_geometric_bound.py',
        'falsification': 'A counterexample inside the certified basin with Lipschitz constant ≥ 1 would falsify the result.',
        'pillar': 401,
    },
    {
        'id': 'T012',
        'name': 'Three generations from T²/Z₃',
        'status': 'DERIVED_STRUCTURAL',
        'claim': 'The T²/Z₃ orbifold structure yields exactly N_gen = 3 light generations.',
        'proof_module': 'src/core/generation_theorem.py',
        'test_file': 'tests/test_generation_theorem.py',
        'falsification': 'A corrected orbifold count giving a different generation number would falsify the structural claim.',
        'pillar': [6, 7, 8],
    },
    {
        'id': 'T013',
        'name': 'SU(3)×SU(2)×U(1) from the winding chain',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The Standard Model gauge structure emerges conditionally from the canonical winding/orbifold reduction.',
        'proof_module': 'src/core/gut_projection.py',
        'test_file': 'tests/test_gut_projection.py',
        'falsification': 'A corrected reduction that fails to reproduce the Standard Model gauge factors would falsify the derivation.',
        'pillar': [21, 70],
    },
    {
        'id': 'T014',
        'name': 'Holographic entropy S = A/4G',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The holographic boundary dynamics recover the entropy-area relation S=A/4G conditionally on the KK boundary assumptions.',
        'proof_module': 'src/holography/boundary.py',
        'test_file': 'tests/test_boundary.py',
        'falsification': 'A corrected boundary reduction yielding a non-area leading entropy law would falsify the recovery.',
        'pillar': [4, 406],
    },
    {
        'id': 'T015',
        'name': 'Metric ansatz uniqueness',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The canonical KK metric ansatz is unique up to the named λ-normalization residual under the audited constraints C1–C5.',
        'proof_module': 'src/core/pillar448_p2_ansatz_upgrade_audit.py',
        'test_file': 'tests/test_pillar448_p2_ansatz_upgrade_audit.py',
        'falsification': 'A distinct C1–C5-compatible ansatz with the same field content and no extra residual would falsify uniqueness.',
        'pillar': 448,
    },
    {
        'id': 'T016',
        'name': 'KK irreversibility lower bound',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The KK irreversibility sector enforces a nonzero lower bound on the arrow-of-time functional.',
        'proof_module': 'src/core/arrow_of_time.py',
        'test_file': 'tests/test_arrow_of_time.py',
        'falsification': 'A zero or negative admissible irreversibility solution in the same framework would falsify the lower bound.',
        'pillar': [3, 29],
    },
    {
        'id': 'T017',
        'name': 'P8 braid partner on the integer lattice',
        'status': 'DERIVED_STRUCTURAL',
        'claim': 'Over the integer winding lattice, the braid partner is the minimum positive even step n₂ = n_w + 2.',
        'proof_module': 'src/core/pillar455_p8_field_theoretic_proof.py',
        'test_file': 'tests/test_pillar455_p8_field_theoretic_proof.py',
        'falsification': 'An integer-lattice counterexample with a lower-action allowed partner would falsify the result.',
        'pillar': 455,
    },
    {
        'id': 'T018',
        'name': 'P8 residual over full functional space',
        'status': 'CONJECTURAL',
        'claim': 'The Δn = 2 braid-partner rule is conjectured to remain globally dominant over the full non-perturbative functional space.',
        'proof_module': 'src/core/pillar455_p8_field_theoretic_proof.py',
        'test_file': 'tests/test_pillar455_p8_field_theoretic_proof.py',
        'falsification': 'A lower-action non-perturbative saddle with Δn ≠ 2 would falsify the conjecture.',
        'pillar': 455,
    },
    {
        'id': 'T019',
        'name': 'ν_GW = n_w / K_CS',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The Goldberger-Wise bulk parameter obeys ν_GW = n_w/K_CS in the UM normalization.',
        'proof_module': 'src/core/pillar404_lambda_gw_derivation.py',
        'test_file': 'tests/test_pillar404_lambda_gw_derivation.py',
        'falsification': 'A corrected GW normalization analysis producing ν_GW unrelated to n_w/K_CS would falsify the derivation.',
        'pillar': 404,
    },
    {
        'id': 'T020',
        'name': 'N_e ≈ 60 conditional closure',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The e-fold count closes conditionally once the λ_GW reheating chain is accepted.',
        'proof_module': 'src/core/pillar400_ne_sensitivity_closure.py',
        'test_file': 'tests/test_pillar400_ne_sensitivity_closure.py',
        'falsification': 'A corrected reheating propagation that fails to reach the required e-fold range would falsify the closure.',
        'pillar': [400, 404],
    },
    {
        'id': 'T021',
        'name': 'FTUM orbifold-basin contractivity',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The orbifold basin supporting FTUM evolution is contractive in the certified domain.',
        'proof_module': 'src/core/pillar401_ftum_basin_geometric_bound.py',
        'test_file': 'tests/test_pillar401_ftum_basin_geometric_bound.py',
        'falsification': 'A certified-domain orbit with contractivity failure would falsify the statement.',
        'pillar': 401,
    },
    {
        'id': 'T022',
        'name': 'CMB peak three-term decomposition',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The peak-amplitude residual factorizes as S_total = S_braid × S_alphaGW × S_5D_cap.',
        'proof_module': 'src/core/pillar277_cmb_peak_three_term_decomposition.py',
        'test_file': 'tests/test_pillar277_cmb_peak_three_term_decomposition.py',
        'falsification': 'A corrected transfer calculation that prevents this factorization would falsify the theorem.',
        'pillar': 277,
    },
    {
        'id': 'T023',
        'name': 'α_GW interval narrowing',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The α_GW interval narrows to [4.31, 4.67]×10⁻¹⁰ at canonical ε_UV = 0.04 up to higher-order EFT corrections.',
        'proof_module': 'src/core/pillar451_alpha_gw_sc2_narrowing.py',
        'test_file': 'tests/test_pillar451_alpha_gw_sc2.py',
        'falsification': 'A corrected EFT audit invalidating the c_UV-independent narrowing would falsify the result.',
        'pillar': [280, 451, 463],
    },
    {
        'id': 'T024',
        'name': 'α_s 2026 closure basin',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The 2026 α_s audit identifies a closed consistency basin rather than a free continuous tuning direction.',
        'proof_module': 'src/core/pillar462_alpha_s_closure_2026.py',
        'test_file': 'tests/test_pillar462_alpha_s_closure_2026.py',
        'falsification': 'A corrected α_s propagation showing no consistent basin would falsify the claim.',
        'pillar': 462,
    },
    {
        'id': 'T025',
        'name': 'PMNS p_R constrained window',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The PMNS right-handed parameter p_R is constrained to a narrow physical window by the geometric chain.',
        'proof_module': 'src/core/pillar452_pmns_pr_derivation.py',
        'test_file': 'tests/test_pillar452_pmns_pr_derivation.py',
        'falsification': 'A corrected PMNS scan allowing no overlap with the derived window would falsify the statement.',
        'pillar': [452, 461],
    },
    {
        'id': 'T026',
        'name': 'δ_CP geometric phase derivation',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The leptonic CP phase δ_CP follows conditionally from the higher-dimensional torsion/phase structure.',
        'proof_module': 'src/core/pillar409_resonant_leptogenesis.py',
        'test_file': 'tests/test_pillar409_resonant_leptogenesis.py',
        'falsification': 'A corrected phase-reduction chain inconsistent with the derived δ_CP value would falsify the derivation.',
        'pillar': [409, 443],
    },
    {
        'id': 'T027',
        'name': 'CKM rho_bar embedding',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The CKM parameter ρ̄ is conditionally embedded in the 7D/9D flavor geometry.',
        'proof_module': 'src/core/pillar420_ckm_flavor_symmetry.py',
        'test_file': 'tests/test_pillar420_ckm_flavor_symmetry.py',
        'falsification': 'A corrected flavor embedding with no consistent ρ̄ interval would falsify the statement.',
        'pillar': [420, 398],
    },
    {
        'id': 'T028',
        'name': 'α_GUT = 3/74',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The geometric GUT coupling satisfies α_GUT = 3/74 in the SU(N_c) Chern-Simons normalization chain.',
        'proof_module': 'src/core/rge_running.py',
        'test_file': 'tests/test_rge_running.py',
        'falsification': 'A corrected CS quantization derivation inconsistent with α_GUT = 3/74 would falsify the result.',
        'pillar': 153,
    },
    {
        'id': 'T029',
        'name': 'Λ_QCD geometric primary path',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'A geometric primary path yields Λ_QCD ≈ 198 MeV without using the SM RGE as the primary derivation.',
        'proof_module': 'src/core/qcd_geometry_primary.py',
        'test_file': 'tests/test_pillar182_precision.py',
        'falsification': 'A corrected geometric derivation missing the hadronic scale by orders of magnitude would falsify the primary-path claim.',
        'pillar': 182,
    },
    {
        'id': 'T030',
        'name': 'Higgs mass from the KK Higgs chain',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The Higgs mass is conditionally recovered near 125.25 GeV in the KK reduction chain.',
        'proof_module': 'src/core/higgs_sector.py',
        'test_file': 'tests/test_higgs_sector.py',
        'falsification': 'A corrected Higgs reduction yielding no overlap with the observed mass would falsify the conditional recovery.',
        'pillar': 5,
    },
    {
        'id': 'T031',
        'name': 'Weak mixing angle recovery',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The electroweak mixing angle is conditionally recovered near sin²θ_W ≈ 0.231.',
        'proof_module': 'src/core/electroweak_orbifold.py',
        'test_file': 'tests/test_electroweak_orbifold.py',
        'falsification': 'A corrected electroweak reduction with no overlap near the observed mixing angle would falsify the recovery.',
        'pillar': [21, 70],
    },
    {
        'id': 'T032',
        'name': 'Proton stability bound roadmap',
        'status': 'DERIVED_CONDITIONAL',
        'claim': 'The proton lifetime is expected to obey a geometry-linked lower bound τ_p ≥ f(n_w, k_CS, M_KK).',
        'proof_module': 'src/core/pillar472_proton_stability_bound.py (planned)',
        'test_file': 'tests/test_pillar472_proton_stability_bound.py (planned)',
        'falsification': 'Hyper-K observing proton decay below the eventual bound would falsify the claim once the explicit theorem is instantiated.',
        'pillar': 472,
    },
]


def get_by_status(status: str) -> List[Dict[str, Any]]:
    """Return all theorem entries with the requested status."""
    return [copy.deepcopy(entry) for entry in THEOREM_REGISTRY if entry['status'] == status]


def count_by_status() -> Dict[str, int]:
    """Return theorem counts by epistemic status."""
    counts: Dict[str, int] = {}
    for entry in THEOREM_REGISTRY:
        counts[entry['status']] = counts.get(entry['status'], 0) + 1
    return counts


def proved_theorems() -> List[Dict[str, Any]]:
    """Return theorems carrying the strict PROVED label."""
    return get_by_status('PROVED')


def conjectural_theorems() -> List[Dict[str, Any]]:
    """Return theorem entries still marked conjectural."""
    return get_by_status('CONJECTURAL')


def theorem_by_id(theorem_id: str) -> Dict[str, Any]:
    """Return one theorem by id."""
    for entry in THEOREM_REGISTRY:
        if entry['id'] == theorem_id:
            return copy.deepcopy(entry)
    raise KeyError(f'Unknown theorem id: {theorem_id}')


def registry_summary() -> Dict[str, Any]:
    """Return a summary of the full theorem registry."""
    counts = count_by_status()
    total = len(THEOREM_REGISTRY)
    proved = counts.get('PROVED', 0)
    return {
        'total_theorems': total,
        'by_status': counts,
        'proved_count': proved,
        'proved_fraction': proved / total if total else 0.0,
        'conjectural_count': counts.get('CONJECTURAL', 0),
    }


def pillar_report() -> Dict[str, Any]:
    """Return the Pillar 465 report."""
    return {
        'pillar': 465,
        'status': PILLAR_STATUS,
        'version': VERSION,
        'theorem_registry': copy.deepcopy(THEOREM_REGISTRY),
        'summary': registry_summary(),
    }


_PILLAR_STATUS: Dict[str, Any] = pillar_report()
