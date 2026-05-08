# How We Decide What to Work On: The MAS Wave Plan

*Post 134 of the Unitary Manifold series.*  
*Epistemic category: **A** — methodology and process; not a physics claim.*  
*v10.20+, May 2026.*

---

A research project with 208 pillars and 28 parameters to close needs a methodology for deciding what to do next. "Work on what feels interesting" is not a method. "Work on what a journal reviewer would notice" is a bias, not a plan.

This post explains the MAS Wave Plan — the system we built to make these decisions explicit, auditable, and resistant to motivated reasoning.

---

## What MAS Stands For

**MAS: Milestone Acceleration Sprint**

A MAS wave is a bounded work unit with:
- A defined set of target parameters (P-numbers)
- A defined promotion gate for each parameter (what residual threshold qualifies as "closed")
- A defined scope of geometric tools allowed (which pillars, which dimensional corrections)
- A defined test requirement (how many passing tests certify the closure)
- A defined timeline

The tracker lives at `docs/mas_tracker.yml`. Every wave is recorded with its input state, deliverables, actual results, and any gates that were not passed.

---

## The Promotion Ladder

Each Standard Model parameter moves through a defined sequence of epistemic states:

```
OPEN → ARCHITECTURE_LIMIT_CERTIFIED → CONSTRAINED → GEOMETRIC_ESTIMATE_CERTIFIED → GEOMETRIC_PREDICTION → ALGEBRAIC
```

Moving up the ladder requires:
1. **Documented derivation** in a named Python module
2. **Residual below the tier threshold** (CONSTRAINED: <50%, GEOMETRIC_PREDICTION: <5%, ALGEBRAIC: exactly 0)
3. **Independent cross-check** from a second geometric path
4. **Test coverage** verifying the calculation and the threshold
5. **Hardgate sign-off** — an explicit entry in the tracker recording what was checked

Moving down the ladder — demotion — is also possible and has happened. P17 was demoted from an earlier estimate when a computation error was found. The tracker records demotions with the same detail as promotions.

---

## How a Wave Is Planned

At the start of each wave, the planner (human + AI jointly) reviews:

1. **Current ToE scorecard** — which parameters are closest to the next promotion threshold?
2. **Blocking dependencies** — which parameters require another parameter or module to close first?
3. **Geometric tool availability** — which dimensional corrections (NLO, 7D, 9D, etc.) are already implemented?
4. **Risk budget** — how many parameters are in the wave? Large waves risk delivering nothing if all targets miss their gates.

The usual output is a wave of 3–6 parameters with defined deliverables and a fallback plan for the most likely failure mode.

---

## Recent Wave Results

| Wave | Version | Parameters Targeted | Promotions Delivered | Gate Failures |
|------|---------|---------------------|----------------------|---------------|
| Braid c_L spectrum arc | v10.6 | P16, P26 | 0 direct; infrastructure closed | P16 still CONSTRAINED |
| Route A consolidation | v10.27 | P18, P20 | Both promoted (+0.6 pts) | None |
| Tier-4 Yukawa sprint | v10.28 | P7–P10, P17 | All five promoted (+1.7 pts) | None |

The route-A consolidation wave and the Tier-4 sprint are the two most successful waves in the project's history. They succeeded in part because the blocking dependencies — the braid spectrum and c_L geometry — were already closed by earlier waves that appeared, at the time, to deliver nothing directly.

---

## The Honest Accounting of Failed Gates

Not every wave succeeds. P17 failed its GEOMETRIC_PREDICTION gate three times before it passed in v10.28. The failures were documented in the tracker with the specific residual that caused the failure and the geometric path that was attempted.

This documentation serves two purposes:

1. **Scientific honesty**: anyone auditing the tracker can see that P17 was not smoothly promoted — it struggled, and the struggle is recorded.
2. **Research guidance**: the failed attempts narrowed down which geometric corrections were necessary. The 9D KK+GS path that eventually closed P17 was identified by analyzing why the 7D-only path failed.

---

## What the MAS Wave Plan Is Not

It is not a guarantee. Parameters sometimes miss their gates. Waves sometimes close zero parameters.

It is not a roadmap that implies the remaining parameters will be closed. The ToE score at 76% does not mean that 24% of the work remains and will be done in the same way. Some architecture limits (P27, P28) may require physics that the 5D framework cannot provide without extension to 10D or 11D.

It is a discipline for being honest about what has been done, what is in progress, and what is genuinely unknown.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
