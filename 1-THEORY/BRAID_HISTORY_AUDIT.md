# Braid History Audit — Canonical, Historical, and Superseded Braid-Facing Surfaces

**Status:** Canonical document-usage audit for the braid lane  
**Theory:** ThomasCory Walker-Pearson  
**Documentation:** GitHub Copilot (AI)  
**Purpose:** Distinguish current canonical braid-facing files from useful historical material and from documents whose stronger claims must now defer to the present truth/fallibility surface.

---

## 1 · Why this audit exists

The repository contains braid material across theory, falsification, implementation, and outreach layers. Some of those files were written before the latest fallibility and truth-layer refinements. That does not make them worthless, but it does mean they must be read in the correct order.

This audit is a reading and citation discipline, not a deletion list.

---

## 2 · Priority rule

When two braid-facing documents disagree in strength or tone, use this order:

1. current canonical honesty/ledger files,
2. current implementation-facing braid files,
3. historical theory/outreach files for provenance,
4. older narrative or milestone materials only with explicit historical framing.

---

## 3 · Current braid document map

| File | Role | Current use verdict | Guidance |
|------|------|---------------------|----------|
| [`BRAID_DOSSIER.md`](BRAID_DOSSIER.md) | Canonical braid lane framing memo | **CANONICAL** | Start here for scope, status, and closure discipline |
| [`DERIVATION_STATUS.md`](DERIVATION_STATUS.md) | Repository-wide epistemic ledger | **CANONICAL** | Use for current claim-status vocabulary and scope corrections |
| [`../FALLIBILITY.md`](../FALLIBILITY.md) | Limits, open obligations, falsifiers | **CANONICAL** | Use whenever a braid claim touches scientific closure |
| [`../docs/TRUTH_LAYER.md`](../docs/TRUTH_LAYER.md) | Full truth-layer context | **CANONICAL** | Use when historical closure claims need current correction |
| [`../3-FALSIFICATION/BIREFRINGENCE_CLARIFICATION.md`](../3-FALSIFICATION/BIREFRINGENCE_CLARIFICATION.md) | Authoritative β map | **CANONICAL** | Use for sector/path distinctions and gap-domain statements |
| [`../3-FALSIFICATION/prediction.md`](../3-FALSIFICATION/prediction.md) | Quantitative braid-facing predictions | **CANONICAL** | Use for current prediction values and practical falsifier language |
| [`WINDING_NUMBER_DERIVATION.md`](WINDING_NUMBER_DERIVATION.md) | Detailed winding-selection walkthrough | **USE WITH CURRENT LEDGERS** | Helpful exposition, but read through the newer fallibility/truth-layer guardrails |
| [`NW_UNIQUENESS_STATUS.md`](NW_UNIQUENESS_STATUS.md) | Consolidated winding-number case | **USE WITH CAUTION** | Strong and useful, but some claims are stronger than the more conservative current truth-layer phrasing |
| [`BRAID_TWIN_DUALITY.md`](BRAID_TWIN_DUALITY.md) | Two-sector braid exposition | **USE WITH CURRENT FALSIFIER FILES** | Good for dual-sector structure; defer to canonical β documents for final wording |
| [`../src/core/braided_winding.py`](../src/core/braided_winding.py) | Executable braided sector | **CANONICAL IMPLEMENTATION SURFACE** | Source of actual formulas and internal API |
| [`../src/core/nw5_pure_theorem.py`](../src/core/nw5_pure_theorem.py) | Internal theorem statement | **IMPLEMENTATION SURFACE; READ WITH HONESTY LAYER** | Important, but final scientific wording should still defer to current fallibility/truth-layer constraints |
| [`../src/multiverse/layering.py`](../src/multiverse/layering.py) | Executable Big Bang layering model | **CANONICAL INTERNAL MODEL** | Safe for the internal layering interpretation; not proof of external topology correspondences |
| [`../3-FALSIFICATION/BIG_QUESTIONS.md`](../3-FALSIFICATION/BIG_QUESTIONS.md) | Historical synthesis / Q&A surface | **HISTORICAL-USEFUL, NOT PRIMARY** | Valuable provenance, but its stronger closure language must not override current canonical files |
| `7-OUTREACH/substack/posts/post-012-braided-winding.md` | Narrative explanation of braid rescue of \(r\) | **OUTREACH-USEFUL** | Useful exposition, not the primary scientific ledger |
| `7-OUTREACH/substack/posts/post-030-early-universe.md` | Narrative early-universe braid explanation | **OUTREACH-USEFUL** | Good for explanatory prose, but not the authority for current closure claims |

---

## 4 · The main tension to watch

The main interpretive tension in the current braid lane is simple:

- some braid-facing theory and implementation files present a stronger closure picture for \(n_w=5\),
- while the repository's current fallibility/truth-layer surface continues to foreground broader unresolved obligations such as photon origin, action-to-evolution equivalence, and independent CMB normalization.

The correct response is not to erase the stronger files. It is to read them under the current honesty layer and cite them with scope.

---

## 5 · Practical citation rules

Use the following citation discipline:

- If the statement is about **current claim status**, cite `DERIVATION_STATUS.md`, `FALLIBILITY.md`, and `docs/TRUTH_LAYER.md`.
- If the statement is about **β values or the inter-sector gap**, cite `BIREFRINGENCE_CLARIFICATION.md` and `prediction.md`.
- If the statement is about **how the executable braid machinery is implemented**, cite `src/core/braided_winding.py`, `src/core/nw5_pure_theorem.py`, or `src/multiverse/layering.py`.
- If the statement comes from **older synthesis or outreach material**, label it historical, narrative, or explanatory rather than canonical.

---

## 6 · Recommended use in future edits

Before editing braid-facing docs, decide which of these jobs you are doing:

- **canonical status update,**
- **implementation description,**
- **historical provenance,**
- **outreach explanation,**
- or **external-comparison research.**

Using the wrong source class is the fastest way to reintroduce overclaim.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
