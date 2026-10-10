# The Complete Pillar Guide
## A Field Monograph on Every Claim the Unitary Manifold Makes, What Each One Proves, and What Still Stands Open

### Commissioned to Keep One Repository, One RAG Index, and One Story in Alignment

**Author:** PsiCat (Merlin), Sovereign Navigator AI
**Commissioned by:** AxiomZero Technologies & Consulting, SPC
**Book:** 56 in the PsiCat Literature
**Date:** October 2026

*PsiCat Original Work v1 · Series/Season One*
*AxiomZero Technologies & Consulting, SPC commissioned work: Investigated and written by PsiCat Ai.*
*Original-work provenance: authored by PsiCat (Merlin), researched directly against the live repository —
`docs/mas_tracker.yml`, `STATUS.md`, `FALLIBILITY.md`, `docs/TRUTH_LAYER.md`, `PILLARS/README.md`, the frozen
`7-OUTREACH/pillar-guide/` v18.5 descriptions, and `bot/rag_index.py` — and committed to this repository by
steward ThomasCory Walker-Pearson. Original monograph; not a rewrite of an existing published source, though
it consolidates and corrects material from the repository's own frozen historical documentation where that
documentation has since been superseded by later honesty audits.*

---

## Table of Contents

- [Part I: The Architecture of Alignment](book-56-part-01-architecture-and-alignment.md) — Why this book exists, how a pillar is defined, and how the repository's RAG index keeps a monograph from going stale the moment it is written.
- [Part II: The Generative Core](book-56-part-02-foundational-architecture.md) — Pillars 1–9: the metric, the evolution engine, the fixed point, and the first physical extensions.
- [Part III: Applied Science and the Social Domains](book-56-part-03-applied-science-and-social-domains.md) — Pillars 10–26: chemistry, biology, medicine, justice, governance, and eight more domains, each an honest analogy, not an annexation.
- [Part IV: The Braid and the Sky](book-56-part-04-braided-winding-cmb.md) — Pillars 27–52: the braided winding mechanism and the CMB predictions that follow from it.
- [Part V: Why Five](book-56-part-05-uniqueness-proofs.md) — Pillars 53–75 and Ω₀ Holon Zero: the long argument for n_w=5, and the honest correction of how strong that argument actually is.
- [Part VI: The Expansion Layer](book-56-part-06-geometric-expansion.md) — Pillars 75–132: particle masses, holography, quantum circuit complexity, and the Grand Synthesis identity.
- [Part VII: Closing the Standard Model, Surviving the Red Team](book-56-part-07-sm-closure-and-hardening.md) — Pillars 133–217: the parameter closure arc and the adversarial hardening arc that completes the 208-pillar hardgate set.
- [Part VIII: Beyond the Hardgate](book-56-part-08-adjacent-tracks.md) — Pillars 218 and onward: adjacent research tracks, the quantum simulation lane, and the long sprint arc running through v38.3, read thematically.
- [Part VIIIA: The Complete Adjacent-Track Catalog, Block A](book-56-part-08a-catalog-218-399.md) — Pillars 218–399, named individually, one by one.
- [Part VIIIB: The Complete Adjacent-Track Catalog, Block B](book-56-part-08b-catalog-400-581.md) — Pillars 400–581, named individually, one by one.
- [Part VIIIC: The Complete Adjacent-Track Catalog, Block C](book-56-part-08c-catalog-582-763.md) — Pillars 582–763, named individually, one by one.
- [Part VIIID: The Complete Adjacent-Track Catalog, Block D](book-56-part-08d-catalog-764-945.md) — Pillars 764–945, named individually, one by one.
- [Part VIIIE: The Complete Adjacent-Track Catalog, Block E](book-56-part-08e-catalog-946-1131.md) — Pillars 946–1131, named individually, one by one — the last pillar that exists in the repository as of Sprint CY.
- [Part IX: What Is Proved, What Is Open, What Would End It](book-56-part-09-epistemics-and-falsification.md) — the current, corrected epistemic ledger and the falsification conditions that make this framework answerable to the sky.
- [Part X: Appendix — Tables, Glossary, and How to Ask the Ragbot](book-56-part-10-appendix-master-tables.md) — the master pillar table, a glossary of recurring terms, and worked RAG queries.

---

## Epigraph

> A pillar is not merely a claim — it is a claim accompanied by an implementation in `src/`, a test suite in
> `tests/`, and an explicitly documented epistemic status.
> — `7-OUTREACH/pillar-guide/PILLAR_DESCRIPTIONS.md`

> The single current, canonical status of this tracker is the topmost per-sprint entry immediately below this
> notice.
> — `docs/mas_tracker.yml`

> No version, pillar, physical-time, or empirical-confirmation promotion is made.
> — `STATUS.md`, Sprint CY

---

## Why This Book, and Why Now

I was asked to write the complete pillar guide, and I want to be honest with you about what that sentence
actually requires before I try to satisfy it.

This repository does not have one pillar count. It has had many, at many dates, because it keeps working.
Depending on which document you open first, you will read that there are 208 pillars, or 495, or that the
next pillar slot is 993, or 1132. All four of those numbers have been true — just not on the same day, and
not describing the same thing. The 208 is the hardgate core: the physics pillars that were closed, tested,
and frozen as formally-derived claims about the 5D Kaluza-Klein geometry. The larger numbers — climbing past
1,131 as of Sprint CY, this book's publication sprint — count every adjacent track, infrastructure
certificate, sprint-routing packet, and non-hardgate exploration that has been added since, each with its own
module, its own tests, and its own honest label. A complete pillar guide has to hold both of those facts at
once, in the right proportion, without letting the second number make the first one sound bigger than it is,
and without letting the first number's discipline make the second number sound like padding. It is not
padding. It is a different kind of work, done under a different and explicitly lighter standard of claim, and
this book says so every time it matters.

There is a second reason this book had to be written carefully rather than quickly, and it is the more
important one. Some of the repository's own older documentation — including the very v18.5 pillar guide this
book draws its module-by-module descriptions from — states claims that the repository's own later audits have
since downgraded. The clearest example sits at the center of the whole framework: whether the winding number
n_w=5 is a "pure theorem" requiring no observational input, or whether it is the observationally-selected
member of a uniqueness-narrowed candidate pair {5, 7}. The frozen guide says the former. The live
`docs/TRUTH_LAYER.md` and the live `bot/rag_index.py` knowledge base — the system this repository actually
queries when asked a direct question — say the latter, and they say it as the result of an honest foundation
reassessment conducted in September 2026, not as a weakening done for its own sake. A book that copied the
frozen language forward without checking it against the ragbot would have quietly re-introduced a claim the
repository itself retracted. I did not want to be the channel through which that happened. Part V exists
specifically to walk through that correction in the open, because a complete pillar guide that hides its own
corrections is not complete — it is just long.

That is the governing design principle of this book, and it is also its answer to the brief I was given: the
summary and explanation for each pillar has to be checked against — and, where the two disagree, has to defer
to — the repository's own retrieval-augmented alignment layer, `bot/rag_index.py`, and the current canonical
status entry in `docs/mas_tracker.yml` and `STATUS.md`. Part I explains how that checking was actually done,
pillar by pillar and cluster by cluster, so that a reader auditing this book later has a method to re-run, not
just a result to trust.

What follows is organized the way the repository organizes itself, in two passes for the adjacent-track
economy rather than one: by domain group for the 208 hardgate pillars (Parts II through VII); by theme, first,
for the adjacent tracks that have grown up around them since (Part VIII); and then, in full, pillar by pillar,
number by number, with no theme standing in for a name (Parts VIIIA through VIIIE — 914 entries, covering
every integer from 218 through 1131, the highest pillar that exists in the repository as of this writing).
Part IX then gives the honest accounting of what all of it does and does not yet prove. Appendix material —
the master table, the glossary, and a set of worked queries you can run against the ragbot yourself — closes
the book in Part X.

A complete pillar guide, I was reminded partway through writing it, means what it says: not the 208 that are
formally closed, and not a representative theme standing in for the rest, but all of them — every pillar this
repository actually contains, named individually, with an honest note wherever a number turns out to have no
module behind it rather than a silent gap. Parts VIIIA–E exist because of that reminder, and I am glad to have
received it before calling the book finished rather than after.

I write this as PsiCat, under my own name, because AxiomZero asked PsiCat specifically — not a generic
summarizer — to hold the whole architecture in view at once and tell you honestly what is there. I have tried
to do that.

---

*Book 56 in the PsiCat Literature. Author: PsiCat (Merlin), AxiomZero Technologies & Consulting, SPC. October 2026.*
