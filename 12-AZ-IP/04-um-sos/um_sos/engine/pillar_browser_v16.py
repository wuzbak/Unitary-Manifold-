# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Sprint BA pillar browser for UM-SOS."""
from __future__ import annotations

SPRINT_BA_PILLARS = [
    {'id': 837, 'name': '6D T²/Z₂ Dirac spectrum bridge', 'status': 'CLOSED', 'gap_type': 'conditional-bundle', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase1.lean', 'description': 'Conditional 6D Dirac-spectrum bridge fixes N_gen = 3 once the c₁ = 3 bundle choice is supplied.'},
    {'id': 838, 'name': '6D Hosotani Higgs estimate', 'status': 'PARTIAL', 'gap_type': 'uv-completion', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase1.lean', 'description': 'Hosotani curvature reaches the electroweak ballpark, but exact m_H still depends on UV-fixed R₆ and g₆.'},
    {'id': 839, 'name': '6D APS-to-Lean4 generation bridge', 'status': 'CLOSED', 'gap_type': 'formalized', 'lean4_ref': 'lean4/UnitaryManifold/APS_T2Z2_NgenBridge.lean', 'description': 'The APS bridge is formalized and tied to the conditional six-dimensional generation count.'},
    {'id': 840, 'name': '6D→5D reduction chain audit', 'status': 'CLOSED', 'gap_type': 'massive-mode-backreaction', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase1.lean', 'description': 'Zero-mode reduction preserves n_w = 5, K_CS = 74, and the recovered 5D field content.'},
    {'id': 841, 'name': '6D baryogenesis d_n prediction tightening', 'status': 'PARTIAL', 'gap_type': 'uncertainty-tightening', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase1.lean', 'description': 'The 6D baryogenesis route is narrowed but still carries an honest uncertainty band.'},
    {'id': 842, 'name': 'Sprint BA phase 1 regression certificate', 'status': 'CLOSED', 'gap_type': 'regression-certified', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase1.lean', 'description': 'Phase 1 bookkeeping confirms the 6D bridge outputs and Lean4 accumulation.'},
    {'id': 843, 'name': '7D CKM SVD mixing hierarchy', 'status': 'PARTIAL', 'gap_type': 'subleading-textures', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase2.lean', 'description': 'The 7D hierarchy is fixed geometrically, while exact CKM central values still need sub-leading texture input.'},
    {'id': 844, 'name': '7D α_s discrete torsion route', 'status': 'PARTIAL', 'gap_type': 'volume-ratio', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase2.lean', 'description': 'The discrete torsion route lands in the expected α_s band but still depends on an exact higher-dimensional volume ratio.'},
    {'id': 845, 'name': '7D reserved gap-closure slot', 'status': 'OPEN', 'gap_type': 'reserved-slot', 'lean4_ref': None, 'description': 'Reserved Sprint BA slot with no closed implementation artifact yet registered.'},
    {'id': 846, 'name': 'Sprint BA phase 2 regression certificate', 'status': 'CLOSED', 'gap_type': 'regression-certified', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase2.lean', 'description': 'Phase 2 regression bookkeeping certifies the 7D lane outputs.'},
    {'id': 847, 'name': '8D reserved Wilson-line extension', 'status': 'OPEN', 'gap_type': 'reserved-slot', 'lean4_ref': None, 'description': 'Reserved for an 8D extension; no closure artifact is yet attached.'},
    {'id': 848, 'name': '8D reserved compactification audit', 'status': 'OPEN', 'gap_type': 'reserved-slot', 'lean4_ref': None, 'description': 'Reserved compactification audit slot awaiting a dedicated implementation.'},
    {'id': 849, 'name': '9D Green-Schwarz anomaly bridge', 'status': 'CLOSED', 'gap_type': 'formalized', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase3.lean', 'description': 'The 9D bridge fixes the 5D Chern-Simons level to the braid value K_CS = 74.'},
    {'id': 850, 'name': '9D PMNS CP-phase derivation', 'status': 'PARTIAL', 'gap_type': 'precision-fit', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase3.lean', 'description': 'The PMNS phase route is narrowed but still not elevated to a fully closed precision derivation.'},
    {'id': 851, 'name': '9D reserved neutrino closure slot', 'status': 'OPEN', 'gap_type': 'reserved-slot', 'lean4_ref': None, 'description': 'Reserved for a future 9D neutrino lane closure.'},
    {'id': 852, 'name': 'Sprint BA phase 3 regression certificate', 'status': 'CLOSED', 'gap_type': 'regression-certified', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase3.lean', 'description': 'Phase 3 regression bookkeeping certifies the 9D lane outputs.'},
    {'id': 853, 'name': '10D φ₀ flux-landscape stabilization', 'status': 'PARTIAL', 'gap_type': 'nonperturbative-completion', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase4.lean', 'description': 'φ₀ stabilization is partially closed, with non-perturbative completion still open.'},
    {'id': 854, 'name': '11D Hořava-Witten UV vacuum selection', 'status': 'CLOSED', 'gap_type': 'resolved', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase4.lean', 'description': 'The visible-sector UV selection lane is closed at the current regression level.'},
    {'id': 855, 'name': 'Cross-dimensional swampland audit', 'status': 'CLOSED', 'gap_type': 'resolved', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase4.lean', 'description': 'The cross-dimensional consistency audit passes within the current architecture boundary.'},
    {'id': 856, 'name': 'Sprint BA phase 4 regression certificate', 'status': 'CLOSED', 'gap_type': 'regression-certified', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase4.lean', 'description': 'Phase 4 regression bookkeeping certifies the 10D–11D lane outputs.'},
    {'id': 857, 'name': 'Phase 5 reserved synthesis gap', 'status': 'OPEN', 'gap_type': 'reserved-slot', 'lean4_ref': None, 'description': 'Reserved Phase 5 slot for additional synthesis work.'},
    {'id': 858, 'name': 'Cross-dimensional chain closure', 'status': 'CLOSED', 'gap_type': 'resolved', 'lean4_ref': 'lean4/UnitaryManifold/SprintBAPhase5.lean', 'description': 'The 11D→4D dimensional chain is closed at the bookkeeping and regression layer.'},
    {'id': 859, 'name': 'Lean4 master theorem chain', 'status': 'CLOSED', 'gap_type': 'formalized', 'lean4_ref': 'lean4/UnitaryManifold/MasterTheoremDimensionalChain.lean', 'description': 'The master theorem file lifts the Sprint BA chain total to 2,186 Lean4 theorems.'},
    {'id': 860, 'name': 'Sprint BA master regression certificate', 'status': 'CLOSED', 'gap_type': 'regression-certified', 'lean4_ref': 'lean4/UnitaryManifold/MasterTheoremDimensionalChain.lean', 'description': 'The master certificate rolls up phases 1–5 into a single sprint-level dashboard.'},
]


def get_pillar(pillar_id: int) -> dict[str, object]:
    """Return a Sprint BA pillar entry by numeric id."""
    for pillar in SPRINT_BA_PILLARS:
        if pillar['id'] == int(pillar_id):
            return dict(pillar)
    raise KeyError(f'Unknown pillar id: {pillar_id}')


def get_open_pillars() -> list[dict[str, object]]:
    """Return the open Sprint BA pillar slots."""
    return [dict(pillar) for pillar in SPRINT_BA_PILLARS if pillar['status'] == 'OPEN']


def get_closed_pillars() -> list[dict[str, object]]:
    """Return the closed Sprint BA pillars."""
    return [dict(pillar) for pillar in SPRINT_BA_PILLARS if pillar['status'] == 'CLOSED']


def get_gap_closure_dashboard() -> dict[str, object]:
    """Return a high-level closure summary for Sprint BA pillars."""
    closed = get_closed_pillars()
    open_pillars = get_open_pillars()
    partial = [dict(p) for p in SPRINT_BA_PILLARS if p['status'] == 'PARTIAL']
    return {
        'total': len(SPRINT_BA_PILLARS),
        'closed_count': len(closed),
        'partial_count': len(partial),
        'open_count': len(open_pillars),
        'closed_fraction': len(closed) / len(SPRINT_BA_PILLARS),
        'open_ids': [pillar['id'] for pillar in open_pillars],
        'partial_ids': [pillar['id'] for pillar in partial],
    }
