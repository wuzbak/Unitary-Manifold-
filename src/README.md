# src/ — Module Directory and Epistemic Tier Map

*Unitary Manifold v15.8 — 2026-06-05*  
*This README is the canonical navigation guide for new readers, referees, and
AI agents ingesting the repository.*

> **Cross-reference:** The full epistemic boundary definition is in
> [`SEPARATION.md`](../SEPARATION.md). The claim-status ledger is in
> [`1-THEORY/DERIVATION_STATUS.md`](../1-THEORY/DERIVATION_STATUS.md).
> The claim master board is in [`docs/CLAIM_MASTER_BOARD.md`](../docs/CLAIM_MASTER_BOARD.md).

---

## Three-Tier Architecture

All source modules are assigned to exactly one of three epistemic tiers. No
module is moved from its current location — the tier is a reading label, not
a directory restructuring. The three tiers are:

| Tier | Label | Meaning |
|------|-------|---------|
| **Tier 1** | `PHYSICS` | Derived from the 5D metric ansatz; falsifiable predictions; hardgate-eligible |
| **Tier 2** | `CONJECTURE / EXTENSION` | Self-consistent mathematical extensions; conjectural theorem lanes; adjacent tracks; not Tier 1 physics |
| **Tier 3** | `ANALOGY / BRIDGE` | Mathematical analogies borrowing UM structure; not derived from 5D action; no current experimental test |

**Referees should start with Tier 1 only.** Tier 2 and Tier 3 modules are
clearly labeled within each source file via their `PILLAR_STATUS` or module
docstring. The existence of Tier 2/3 modules does not weaken the Tier 1
physics claims.

---

## Tier 1 — Core Physics (Start Here)

These modules implement the falsifiable physics derived from the 5D metric
ansatz $G_{AB}$ with irreversibility 1-form $B_\mu$ and entropic dilaton $\phi$.

### `src/core/` (698 modules)

The primary derivation engine. Every Tier 1 prediction has a source module,
an epistemic label, and at least one test in `tests/`.

**Key Tier 1 modules (read in this order for institutional evaluation):**

| Module | Purpose | Pillar |
|--------|---------|--------|
| `metric.py` | 5D metric assembly, Christoffel symbols, curvature | Core |
| `evolution.py` | Walker-Pearson field equations, braid winding, run_evolution | Core |
| `inflation.py` | n_s, r, phi_0 from FTUM chain | Core |
| `braided_winding.py` | k_CS = 74, braid pair (5,7), birefringence | Core |
| `phi0_closure.py` | Radion VEV self-consistency | Core |
| `boltzmann.py` | CMB transfer function | Core |
| `sm_free_parameters.py` | 3 free parameters census (n_w, K_CS, c_s) | 492 |
| `formal_proof_hardening.py` | Theorem artifacts for all algebraic proofs | Core |
| `k_cs_topological_proof.py` | k_CS = 74 algebraic certificate | Core |
| `anomaly_closure.py` | CS cubic integral → k_CS | 99-B |
| `braid_uniqueness.py` | (5,7) minimum-step uniqueness certificate | 407 |
| `unitary_closure.py` | Two-sector existence proof: (5,7) and (5,6) | 96 |
| `pillar511_braid_winding_observable.py` | Gradient-space winding observable | 511 |
| `pillar513_topological_information_current.py` | Chern-Simons-corrected J^0 | 513 |
| `pillar514_dynamic_loopback_proof.py` | Forward-only irreversibility proof | 514 |
| `pillar507_frontier_proof_lane_certificate.py` | 5D-KK/P8/PMNS/L2γ/Lean4/CCR/ER=EPR lanes | 507 |
| `pillar508_no_and_earned_yes_claim_audit.py` | No-claim / earned-yes boundary | 508 |
| `pillar516_kk_backreaction_architecture_audit.py` | KK backreaction architecture limit | 516 |
| `canonical_ledger_consistency.py` | Cross-document consistency checker | Core |
| `proof_close_certification_report.py` | Residual gate aggregator | Core |

### `src/holography/` — Holographic boundary dynamics (Tier 1)
Implements holographic entropy $S = A/4G$ boundary condition. Core to the
irreversibility proof (FTUM contraction).

### `src/multiverse/` — FTUM fixed-point theory (Tier 1)
Implements the FTUM operator $U = I + H + T$ and the fixed-point chain
$\phi_0 \to n_s \to r$. Core to the CMB prediction chain.

### `src/quantum/` — Quantum unification theorems (Tier 1)
KK tower mass formula, P8 integer-lattice proof, ghost stability. CCR and
ER=EPR are Tier 2 (conditional theorem kernels, not unconditional).

### `src/physics/` — SM parameter derivations (Tier 1)
Lattice dynamics for the SM parameter matching chain.

---

## Tier 2 — Self-Consistent Conjectures and Adjacent Tracks

These modules are mathematically well-defined and internally tested, but are
**not promoted to Tier 1** unless both (a) a derivation from the 5D action
and (b) an explicit falsification path are established.

| Directory / Module | Domain | Status |
|-------------------|--------|--------|
| `src/sixd/` | 6D baryogenesis extension | ADJACENT TRACK 🔵 |
| `src/eightd/` | 8D extension | ADJACENT TRACK 🔵 |
| `src/nined/` | 9D extension | ADJACENT TRACK 🔵 |
| `src/tend/` | 10D UV completion | ADJACENT TRACK 🔵 |
| `src/eleventd/` | 11D M-theory | ADJACENT TRACK 🔵 |
| `src/sevend/` | 7D extension | ADJACENT TRACK 🔵 |
| `src/cold_fusion/` | Gamow-factor analysis | EXTENSION LANE — no 5D vertex yet |
| `src/astronomy/` | Observational astronomy bridges | PARTIALLY TIER 1 (see module docstrings) |
| `src/materials/` | Condensed matter analogies | TIER 2 / TIER 3 mixed |
| `src/chemistry/` | Molecular structure bridges | TIER 3 analogy |
| `src/atomic_structure/` | Atomic physics bridges | TIER 2 / TIER 3 mixed |

---

## Tier 3 — Mathematical Analogies and Phenomenological Bridges

These modules borrow the UM mathematical structure but are **not derived from
the 5D action**. They are included for research exploration and completeness.
They must not be cited as evidence for Tier 1 physics claims.

| Directory / Module | Domain | Note |
|-------------------|--------|------|
| `src/consciousness/` | Consciousness-geometry coupling | TIER 3 — mathematical analogy only. See `src/consciousness/AXIOMZERO_NOTICE.md` |
| `src/biology/` | Biological systems bridges | TIER 3 |
| `src/ecology/` | Ecological dynamics | TIER 3 |
| `src/marine/` | Ocean-atmosphere | TIER 3 |
| `src/medicine/` | Medical physics extensions | TIER 3 |
| `src/psychology/` | Psychological models | TIER 3 |
| `src/justice/` | Social dynamics models | TIER 3 |
| `src/genetics/` | Genetic information | TIER 3 |
| `src/neuroscience/` | Neural dynamics | TIER 3 |
| `src/climate/` | Climate modeling | TIER 3 |
| `src/earth/` | Geophysics | TIER 3 |

> **For referees:** Tier 3 modules do not affect the Tier 1 physics evaluation.
> The presence of analogical modules is documented in `SEPARATION.md §§ 2–3`.
> They are included here because the Unitary Manifold is explicitly a
> "full-scope" public-domain research platform, not a stripped-down submission.
> Evaluate Tier 1 on Tier 1 evidence.

---

## Governance and Meta

| Directory | Purpose | Tier |
|-----------|---------|------|
| `src/governance/` | Unitary Pentad, governance modules | Governance |
| `src/meta/` | Cross-module audit and consistency | Meta |
| `src/data/` | Physical constants and data tables | Data |
| `src/data_feeds/` | Live experimental data routing | Data |

---

## How to Use This Map

**For an institutional referee (time-efficient path):**
1. `src/core/metric.py` + `src/core/evolution.py` — the 5D kernel
2. `src/core/inflation.py` + `src/core/braided_winding.py` — the CMB prediction chain
3. `python VERIFY.py` — end-to-end executable check
4. `proof/TIER_1_FORMAL.md` — formal evaluation gate

**For a broad exploration:**
Use the derivation graph export at `10-UM-SOS/graph/index.html` to navigate
the full DAG of pillar dependencies.

**For AI agents:**
See `AGENTS.md` for the canonical ingest order.
