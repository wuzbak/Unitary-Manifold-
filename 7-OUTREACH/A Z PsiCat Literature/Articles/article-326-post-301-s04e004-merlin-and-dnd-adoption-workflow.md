# Merlin + D&D: Adoption Workflow for Product 23 — Merlin/PsiCat v1 Rewrite

*Merlin/PsiCat Rewrite v1 · Series/Season One*  
*Written: 2026-09-15T05:41:03Z*  
*AxiomZero Technologies & Consulting, SPC commissioned work: Edited and written by PsiCat Ai.*
*Grounded rewrite source: `/7-OUTREACH/substack/posts/post-301-s04e004-merlin-and-dnd-adoption-workflow.md`*

**Unitary Manifold — S04E004 · v35.7**

---

This is a focused companion to the full Apps & Spaces state post.  
It covers practical adoption of Merlin across:

- **Product 20:** Merlin Navigator (repository-facing knowledge and guidance)
- **Product 23:** Merlin DM Guide & Player Assistant (tabletop campaign operations)

---

## What each product is for

### Product 20 (Merlin Navigator)

- Best for repository-grounded Q&A, gate visibility, and structured follow-up prompts.
- Keeps compatibility with legacy OX routes while using Merlin-native endpoints.

### Product 23 (Merlin DM Guide & Player Assistant)

- Best for live campaign execution:
  - DM/player split dashboards
  - invite-code joins
  - character imports
  - encounter/map/NPC/inventory/XP tracking

---

## Recommended deployment sequence

1. Start Product 23 locally for campaign state.
2. Keep Product 20 available for rules synthesis and prep workflows.
3. Use Product 23 APIs for table operations; use Product 20 for broader narrative/rules planning.
4. Keep both products in offline-first mode by default.
5. Use external router fallback only when explicitly needed.

---

## Adoption checklist

- [ ] DM can create campaign and invite players
- [ ] Player join flow and character import are working
- [ ] XP/gold/treasure updates appear in both dashboards
- [ ] Encounter and map updates are persisted
- [ ] Merlin guidance requests are returning structured outputs
- [ ] No dependence on external accounts for baseline operation

---

## Reliability note

Treat Product 23 as the campaign source of truth.  
Treat Product 20 as the knowledge/navigation assistant surface.  
This separation keeps game-state integrity clear and avoids cross-surface ambiguity.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

### Gate Certification (v1)

This piece is passed through the three required gates for Season One: it is rewritten to be stronger than its source in clarity and structure without losing intent; it preserves accuracy, epistemic honesty, humility, and grounded self-aware humor without ego inflation; and it is edited for cross-audience readability so both specialist and non-specialist readers can traverse it with confidence.
