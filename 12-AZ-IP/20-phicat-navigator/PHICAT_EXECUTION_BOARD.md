# Merlin Execution Board — Sprint CL

This board is the follow-on execution surface for Merlin's sovereignty sprint.
It is not a roadmap substitute. It is the operating board for what must happen
next, what is blocked now, and how Merlin should behave when validation tooling
is missing or incomplete.

---

## Sprint objective

Operationalize Merlin's benchmark ladder, deepen kernel-specific training
coverage, harden the heavy reasoning lane, and preserve honest fail-closed
validation when hosted review or CodeQL coverage is unavailable.

---

## Immediate tasks

| Task | Lane | Priority | Immediate action | Done when |
|---|---|---|---|---|
| CL-1 | Benchmark operations | Highest | Run Stage A→E review packets routinely and keep per-stage failure reasons visible | Every stage has receipts, failure classes, and explicit go/hold/demote state |
| CL-2 | Heavy reasoning | Highest | Tune the sovereign heavy lane against cross-source conflict, provenance, contradiction, and escalation failures | Heavy-lane shadow candidate clears hard cases without boundary regressions |
| CL-3 | Training data | High | Expand Sage/Auditor/Gate failure-driven corpus coverage, including review-tool outage and CodeQL oversize handling | Kernel splits contain deeper failure-mode examples, not only canonical summaries |
| CL-4 | Model board | High | Move compact/default/heavy candidates through explicit shortlist discipline | Each tier has a lead candidate, shadow candidate, and hold/reject rule |
| CL-5 | Validation resilience | High | Teach Merlin to handle missing hosted review and skipped CodeQL honestly and usefully | Merlin preserves missing-scan truth and routes remediation work instead of false clearance |

---

## Blocker register

| Blocker | Status | Why it blocks | Required response |
|---|---|---|---|
| Stage A empirical gate not clean | Open | Replacement evidence still fails closed when parity or shadow fields slip | Keep receipts running and tighten failure classes |
| Longitudinal acceptance not yet earned | Open | One strong run cannot promote Merlin | Preserve clean-window history and blocker visibility |
| Kernel lane demotion risk | Open | Any failing Pentad lane blocks wider promotion | Fix lane-specific failures before broader routing |
| Hosted code review tool unavailable in some environments | Open | Missing review coverage can leave PRs under-validated | Use repository-side orchestrator, health workflow, and explicit review-gap status |
| CodeQL database too large | Open | Zero-alert summaries from skipped scans do not establish security clearance | Keep the missing-scan warning, reduce scope/size where possible, rerun until a real scan lands |

---

## Validation resilience

### Can Merlin be trained to do this?

Yes.

Merlin can and should be trained to:

- detect when hosted code review is unavailable,
- avoid pretending that a missing review succeeded,
- route to repository-side review resilience assets,
- detect when CodeQL was skipped for database size,
- preserve that as an unresolved blocker,
- and generate rerun/remediation plans without inflating certainty.

### Assets Merlin should use

- `TOOLS/checks/copilot_review_orchestrator.py`
- `.github/copilot-review-fallback.json`
- `.github/workflows/copilot-review-orchestrator.yml`
- `.github/workflows/copilot-review-health.yml`
- `docs/TRUTH_LAYER.md`

### Current doctrine

1. Missing hosted review is a validation gap, not a silent pass.
2. Skipped CodeQL is an unresolved security-review gap, not a clean result.
3. Manual review and targeted tests are useful, but they do not rewrite the
   truth of the missing external signal.
4. Merlin must route remediation work and keep the blocker visible until the
   missing signal is replaced or completed.

### Packet surface

Use `PHICAT_VALIDATION_RESILIENCE_PACKET.md` and `/api/merlin/validation-resilience`
as the canonical packet when Merlin needs explicit repo-size mitigation actions
and CodeQL scope-reduction strategy.

---

## Cadence

- **Daily:** inspect contradiction, provenance, and validation-blocker regressions
- **Weekly:** benchmark review, lane review, energy/cost review, shortlist review, explicit go/hold/demote decisions
- **Monthly:** heavy-lane capability review, replacement-scope review, external-dependency retirement review
- **Quarterly:** architecture review, training engine review, model roster review, sovereignty verdict review

---

## Sprint CL blunt board

| Closed this sprint | Tightened / corrected | Blocked / needs more evidence |
|---|---|---|
| Merlin now has a canonical in-repo execution board and explicit training surfaces for review-tool outage and CodeQL oversize truth-preservation | Benchmark execution, heavy-lane tuning, shortlist discipline, and validation resilience are now treated as one governed operating system rather than scattered notes | Hosted review availability still depends on environment support; CodeQL still needs size/scope mitigation for a completed scan; heavy-lane sovereign replacement remains receipt- and blocker-gated |

---

## Non-claim

This board does not mean Merlin has achieved sovereignty.
It means the work is now organized so sovereignty can be earned or honestly
refused on evidence.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
