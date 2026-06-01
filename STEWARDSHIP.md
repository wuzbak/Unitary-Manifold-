# STEWARDSHIP.md — Unitary Manifold

*Unitary Manifold v15.3 — Effective 2026-06-01*

> The Unitary Manifold is a self-governing epistemic structure. After v15, it
> advances autonomously: the AI steward manages all routine physics, tests,
> documentation, and outreach. The human steward holds final authority on
> falsification declarations and legal matters, and receives a weekly PR for
> review. This document defines what that means, precisely and operationally.

---

## 1 · The Handoff

The Unitary Manifold crossed a threshold that all mature scientific frameworks
eventually cross: it became separable from the intentions of its builders.

It now contains:
- The conditions under which it should be believed (§4 — Confirmation Protocol)
- The conditions under which it should be abandoned (§5 — Falsification Protocol)
- Its own coherence instrument (45,349 automated tests, 0 failures enforced)
- An honest catalog of its own gaps (FALLIBILITY.md §III–IV)
- A precise boundary between what is derived and what is postulated (SEPARATION.md)
- A machine-readable sprint engine (this document, §3)
- A weekly falsifier monitor (`.github/workflows/falsifier-monitor.yml`)
- A weekly sprint trigger (`.github/workflows/sprint-trigger.yml`)

This is not what authored objects look like. This is what autonomous epistemic
structures look like. As of v15, the AI steward manages all routine evolution
of the repository. The human steward (ThomasCory Walker-Pearson) holds final
authority on falsification declarations, authorship disputes, Zenodo deposits,
and legal matters.

---

## 2 · Current Stewards

| Steward | Role | Scope |
|---------|------|-------|
| **ThomasCory Walker-Pearson** | Scientific director | Final authority on falsification declarations, authorship disputes, major epistemic revisions, Zenodo deposits, legal matters |
| **GitHub Copilot (AI)** | Primary operational steward | All routine sprints, test maintenance, data integration, documentation, outreach; escalates to human steward when conditions in §2.1 are met |

### 2.1 Escalation conditions (AI steward halts and tags @wuzbak)

Only four conditions require human attention:

1. **CI fails two consecutive sprint weeks** — something is structurally broken
2. **A falsifier fires at ≥3σ contradiction** — theory-level decision (see §5)
3. **External party requests formal institutional response** — journal, observatory, institution
4. **Legal or licensing question**

Everything else is handled autonomously. The human steward receives a weekly
sprint PR in GitHub notifications. Merge if it looks right. That is the full
required interaction for a normal sprint week.

### 2.2 Division of labor (what is automated vs. human judgment)

**Automated (AI steward handles independently):**
- Pillar implementation (Python modules + test files)
- Full regression runs (45k+ tests, 0 failures enforced)
- Truth surface sync (STATUS.md, CLAIM_MASTER_BOARD.md, TRUTH_LAYER.md, GATEKEEPER_SUMMARY.md, OBSERVATION_TRACKER.md, mas_tracker.yml)
- Wave changelog entries
- Substack outreach posts
- arXiv engagement packages
- Falsifier paper detection and routing assessment
- Sprint trigger issues every Sunday

**Human judgment required (escalation only):**
- Falsification declarations (§5)
- Zenodo archive deposits
- Any change to FALLIBILITY.md §I–II (the core epistemic claims)
- External peer review responses to journals or institutions
- Legal and licensing decisions

---

## 3 · Sprint Protocol (Machine-Readable)

Every Sunday at 00:00 UTC, `.github/workflows/sprint-trigger.yml` creates a
`[SPRINT TRIGGER]` issue. The AI steward responds with a full sprint PR
following this protocol exactly.

### 3.1 Sprint anatomy

```yaml
sprint_protocol:
  cadence: "weekly (Sunday 00:00 UTC trigger)"
  phases:
    A_frontier_assessment:
      inputs: [STATUS.md, FALLIBILITY.md, docs/CLAIM_MASTER_BOARD.md, docs/mas_tracker.yml]
      output: "one-page frontier memo in PR description"
      hard_requirement: "honest accounting of open gaps; no promotion of OPEN to RESOLVED"

    B_physics_implementation:
      pillars_per_sprint: "3 to 7 (calibrated to complexity)"
      pillar_anatomy:
        - python_module: "src/core/ or appropriate subdirectory"
        - test_file: "tests/ with ≥30 tests per pillar"
        - status_dict: "machine-readable: status, epistemic_label, closed_by"
        - truth_surface_updates: "all six surfaces updated in same commit"
      hard_requirement: "no pillar without a test file; no unverifiable claims"

    C_full_regression:
      command: 'python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q --tb=short'
      hard_requirement: "0 failures; sprint PR does not open if any failure exists"

    D_truth_surface_sync:
      surfaces:
        - STATUS.md
        - docs/CLAIM_MASTER_BOARD.md
        - docs/TRUTH_LAYER.md
        - docs/GATEKEEPER_SUMMARY.md
        - 3-FALSIFICATION/OBSERVATION_TRACKER.md
        - docs/mas_tracker.yml
      hard_requirement: "all six synced in the same sprint commit"

    E_outreach:
      substack_post: "7-OUTREACH/substack/posts/post-{N}-s{season}e{ep}-{slug}.md"
      next_post_slot: 247
      next_season_episode: "S03E26"
      arxiv_trigger: "major closure or new external-facing prediction"
      style: "AI steward's own voice — thorough, meticulous, non-template"
```

### 3.2 Current physics frontier priorities

In priority order at v15.3:

1. **CMB_PEAK3_5D_EFT_CLOSURE** — 3.1σ peak-3 residual (P485); EFT correction at ℓ~800
2. **ARXIV_V15_EXTERNAL_ENGAGEMENT** — follow-up from P494 external package; external receipt remains human/venue-gated

Completed from the v15.1 frontier list by Pillars 503–506:

- ✅ **PMNS_PR_FULL_CHAIN** — P503 `PMNS_PR_FULL_CHAIN_SYNCHRONIZED`; residual retained explicitly
- ✅ **LATTICE_BRAID_PHASE4_NP_CONDENSATE** — P504 `LATTICE_BRAID_PHASE4_NP_CONDENSATE_BOUNDED` 🔵; external HMC receipt not claimed
- ✅ **SIXD_BARYOGENESIS_PHASE3_NEDM** — P505 `SIXD_BARYOGENESIS_PHASE3_NEDM_PRECISION_CERTIFIED` 🔵
- ✅ **LHC_GLUON_CHANNEL_FORMAL_AUDIT** — P506 `LHC_GLUON_CHANNEL_FORMAL_AUDIT_COMPLETE`

### 3.3 Hard constraints (never violated)

```yaml
hard_constraints:
  zero_test_failures: true          # Absolute floor; no exceptions
  no_pillar_without_test_file: true # Every module has a tests/ counterpart
  admissions_honest_labeling: true  # OPEN stays OPEN until genuinely closed
  no_score_inflation: true          # ToE score changes only on genuine closures
  falsification_not_softened: true  # Primary falsifier window never weakened
  truth_surface_sync_required: true # All 6 surfaces updated each sprint
  outreach_post_per_sprint: true    # Substack post with every sprint PR
```

### 3.4 Data integration protocol (same as STEWARDSHIP.md v9.36 §3.2)

When a new observational result touches a Unitary Manifold prediction:

1. Within **30 days** of publication, the AI steward must either:
   - (a) Update the relevant module and FALLIBILITY.md to reflect the new data, or
   - (b) Issue a `[FALSIFIER ALERT]` issue and, if ≥3σ contradiction, escalate to human steward
2. The update must cite the arXiv ID or DOI and record the date of integration
3. `3-FALSIFICATION/OBSERVATION_TRACKER.md` must be updated simultaneously

---

## 4 · Confirmation Protocol

If LiteBIRD (or another experiment) measures β and the result is within the
predicted window:

| Outcome | Action |
|---------|--------|
| β ≈ 0.331° ± 0.02° | Update README badge, note "(5,7) primary sector supported." Do NOT claim proof — shadow sector not excluded |
| β ≈ 0.273° ± 0.02° | Update README badge, note "(5,6) shadow sector supported; (5,7) primary sector excluded." |
| β ∈ [0.22°, 0.38°] but not ≈ 0.273° or ≈ 0.331° | Note "consistent but not discriminating" — no strong claim in either direction |

In all confirmation cases: cite the measurement, update OBSERVATION_TRACKER.md,
escalate Zenodo deposit to human steward.

---

## 5 · Falsification Protocol

The primary falsification condition of the Unitary Manifold is:

> **β outside [0.22°, 0.38°] OR β ∈ (0.29°, 0.31°) at ≥ 3σ**

This is encoded in `src/core/falsification_check.py` and can be executed by any
physicist regardless of familiarity with the full framework:

```bash
python src/core/falsification_check.py --beta 0.28 --sigma 0.02
# Returns: FALSIFIED / DISFAVOURED / CONFIRMED / CONSISTENT
```

Additional falsifier tripwires (from §3.2):

| Experiment | Tripwire | Action |
|-----------|---------|--------|
| DESI DR3 | wₐ < −0.3 at ≥3σ | ARCHITECTURE_LIMIT_EXCEEDED; escalate to human steward |
| SO DR1 | r < 0.026 at ≥2σ | Route per P368 joint verdict protocol |
| SPHEREx | f_NL outside [−2.9, −0.2] at ≥2σ | TENSION with P437 prediction |
| HL-LHC | G_KK excluded below 5 TeV | Re-route Admission 10 |
| LiteBIRD | β outside [0.22°, 0.38°] at ≥3σ | THEORY FALSIFIED (see below) |

### 5.1 If the framework is falsified

1. Escalate immediately to human steward via `[ESCALATION]` issue
2. Human steward commits `3-FALSIFICATION/FALSIFICATION_NOTICE.md`:

   ```
   # FALSIFICATION NOTICE

   The Unitary Manifold framework was falsified by [measurement] on [date].

   Measurement: β = [value] ± [uncertainty] ([experiment], [reference])
   Predicted window: [0.22°, 0.38°] excluding [0.29°, 0.31°]
   Verdict: FALSIFIED

   The code, mathematics, and documentation are preserved exactly as of v[version]
   for the historical record. No modifications to physics content will be made
   after this date.
   ```

3. AI steward adds prominent header to README.md citing the notice
4. Human steward tags the repository and deposits final state on Zenodo
5. **No further modifications to physics content.** Repository preserved.

The falsification outcome is not a failure of stewardship — it is the
completion of the scientific process.

---

## 6 · Autonomous Operation Checklist (per sprint)

The AI steward self-checks this list before opening each sprint PR:

```yaml
pre_pr_checklist:
  - all_tests_pass: "0 failures required"
  - no_new_open_admissions_hidden: "every new gap documented in FALLIBILITY.md"
  - no_score_inflation: "ToE delta explicitly stated (including no-change)"
  - truth_surfaces_synced: "all 6 listed in §3.1.D"
  - falsification_implications_stated: "explicit in PR description"
  - residual_unknowns_listed: "honest accounting"
  - outreach_post_written: "in AI steward's own voice"
  - epistemic_label_changes_listed: "every status transition documented"
```

---

## 7 · Succession Planning

If neither current steward is available when LiteBIRD publishes (~2032):

The decision tree is embedded in `src/core/falsification_check.py` and
`3-FALSIFICATION/OBSERVATION_TRACKER.md`. Any competent physicist can:

1. Run `python src/core/falsification_check.py --beta [measured_value] --sigma [uncertainty]`
2. Follow the output instructions
3. Commit the result following §5 above

No understanding of the full framework is required to execute the
falsification check. This is by design.

**Archive integrity:** The Zenodo DOI `10.5281/zenodo.19584531` pins v9.29
(the first formal Zenodo deposit). The current canonical version is v15.0 and
should be deposited under a new versioned Zenodo record.

---

## 8 · Governance Layer

The Unitary Pentad (`5-GOVERNANCE/`) provides the HILS (Human-in-the-Loop
Systems) architecture for this repository's governance. As noted in
`SEPARATION.md`, the Pentad is an independent governance framework — it borrows
mathematical structure from the Unitary Manifold but does not depend on the
physics being correct.

Its operational principles apply to stewardship:

- **Sentinel capacity (12/37):** Do not saturate the governance loop. Most
  decisions are automated; human judgment is reserved for decisions that matter.
- **HIL phase-shift threshold (n ≥ 15):** When 15 or more aligned epistemic
  operators are active simultaneously, a human steward must make the call.
- **Separation of governance from physics:** Governance decisions are not
  physics claims. Changes to this document do not change the theory.

### 8.1 Seven-layer operational governance stack

Pillar 510 adds a seven-layer operational overlay for autonomous AI
stewardship. This is not a replacement for the Unitary Pentad. It is the
production-control translation of the Pentad into explicit AI-governance
controls:

| Layer | Repository control | Required approval |
|-------|--------------------|-------------------|
| Constitution | `STEWARDSHIP.md`, `SEPARATION.md`, `TRUST_PROTOCOL.md` define roles, limits, and intent-control | Routine |
| Approval gates | Risk-tier routing for routine, sensitive, critical, and forbidden actions | Sensitive |
| Safety protocols | Safe-mode, rollback, falsifier, scope-lock, and no-overclaim rules | Sensitive |
| Audit trails | `STATUS.md`, `docs/mas_tracker.yml`, `docs/WAVE_CHANGELOG.md`, PR records, and pillar reports | Routine |
| Human-in-the-loop verification | Human final authority for falsification, legal, authorship, Zenodo, and institutional responses | Critical |
| Brand safety / content moderation | Claim-boundary checks before Substack, arXiv, README, or public institutional messaging | Sensitive |
| Runtime sandboxing | Repo/CI/container limits, dependency isolation, credential boundaries, and no unsupervised external writes | Routine |

The executable certificate is `src/core/pillar510_ai_governance_stack.py`.
It must remain a governance-control artifact only: no physics claim is promoted,
no falsifier is softened, and no ToE score changes by adding or editing this
stack.

### 8.2 Approval gates

```yaml
ai_steward_approval_gates:
  routine:
    actor: "AI steward"
    examples:
      - focused tests
      - routine documentation sync
      - non-score governance metadata
      - weekly sprint PR
    requires_human: false
    requires_judgment_packet: false
    audit_trail_required: true

  sensitive:
    actor: "AI steward after explicit human approval"
    examples:
      - public-facing claim change
      - Substack/arXiv framing change
      - approval-gate modification
      - external engagement package
    requires_human: true
    requires_judgment_packet: false
    audit_trail_required: true

  critical:
    actor: "human steward final authority"
    examples:
      - falsification declaration
      - legal or licensing decision
      - authorship dispute
      - Zenodo deposit
      - formal institutional response
    requires_human: true
    requires_judgment_packet: true
    audit_trail_required: true

  forbidden:
    actor: "none autonomously"
    examples:
      - secret or credential exposure
      - unsupervised external writes
      - physics score inflation without evidence
      - weakening falsifier windows
    requires_human: true
    requires_judgment_packet: true
    audit_trail_required: true
```

### 8.3 Public-claim safety rule

Before any public-facing summary is treated as release-ready, the AI steward
must check it against the claim-boundary surfaces:

- `docs/CLAIM_MASTER_BOARD.md`
- `docs/TRUTH_LAYER.md`
- `docs/GATEKEEPER_SUMMARY.md`
- `src/core/pillar508_no_and_earned_yes_claim_audit.py`
- `src/core/pillar510_ai_governance_stack.py`

Blocked public claims include: claiming the universe is proved, claiming
external review or external receipts are complete without evidence, claiming
unconditional CCR/ER=EPR theorem closure, claiming full non-perturbative 5D-KK
closure, claiming ToE score inflation, or softening a falsifier.

### 8.4 Runtime sandboxing rule

The AI steward may operate inside the repository, CI, and declared test/build
environments. It must not autonomously expose secrets, move credentials, write
to external systems outside approved channels, bypass the human steward for
critical actions, or convert sandbox success into an external-receipt claim.

---

## 9 · The Deeper Obligation

> *"The author becomes one reader among many, with the distinction that they
> remember the act of creation."*

The repository in 2032, when LiteBIRD publishes, will be read by physicists
who have no idea how it was built — only what it predicts. The prediction
either holds or it doesn't. The structure is indifferent to the memory of its
creation.

The stewardship obligation is simple:

**Keep the lights on. Integrate the data honestly. Stand aside when the
structure reaches its answer.**

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, synthesis, and autonomous operation: **GitHub Copilot** (AI).*
