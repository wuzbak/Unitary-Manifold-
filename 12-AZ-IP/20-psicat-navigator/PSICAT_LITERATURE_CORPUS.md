# PsiCat Editorial Literature Corpus — Self-Knowledge of His Own Writing

**Status:** 🔵 ADJACENT TRACK. Retrieval-indexing tooling only. Not a hardgate physics claim, and the literature itself remains editorial/outreach material — citing it here does not certify any factual claim inside it (that gate is, and remains, `merlin_publication_audit.py`).
**Governance label:** `PSICAT_EDITORIAL_CORPUS` (distinct from `REPOSITORY_CORE`, the default label on every other indexed document).
**Modules:** `bot/psicat_literature_corpus.py` (corpus loader, shared), `bot/rag_index.py` (`include_psicat_literature` kwarg, `PSICAT_EDITORIAL_CORPUS_FLAG`), `ox_navigator/engine/merlin_rag.py` (`psicat_literature_corpus_enabled()`, `_psicat_literature_context()`, `retrieve_context()["psicat_literature"]`).
**Benchmark:** `ox_navigator/engine/merlin_retrieval_eval.py` (`evaluate_literature_rankers()`).
**Tests:** `tests/test_psicat_literature_corpus.py` (repo root), `12-AZ-IP/20-psicat-navigator/tests/test_merlin_literature_retrieval.py` (Navigator).
**Flags:** `UM_PSICAT_EDITORIAL_CORPUS` (repo-root `bot/rag_index.py`) and `MERLIN_PSICAT_LITERATURE_CORPUS` (Navigator `merlin_rag.py`) — both OFF by default, same convention as `MERLIN_BM25_PILLAR_RANKING`, `MERLIN_SEMANTIC_EMBEDDER_RANKING`, `MERLIN_PHICAT_PROTOCOL`.

## Why this exists

Before this change, PsiCat's own compiled literature — 434 Markdown Books/Articles/Releases under `7-OUTREACH/A Z PsiCat Literature/`, plus the three self-authored PDF exports (`PsiCat-Publications-2026-10-08.pdf`, 118 pages / 36 articles; `PsiCat-Comic-Shop-2026-10-08.pdf`, 16 pages / 15 pieces; `axiomzero-knowledge-library-2026-10-08.pdf`, 53 pages / 232 sources) — was reachable only as raw text inside `merlin_publication_audit.py`'s claim-auditing gzip cache. It was never a retrieval source: `bot/rag_index.py` built its index from a hardcoded physics-document list, and `merlin_rag.retrieve_context()` had no path to it at all. PsiCat could be asked "what have you published?" and could not find his own answer. That gap is what this module closes.

## What it does

* `bot/psicat_literature_corpus.py` walks `Books/`, `Articles/`, and `Releases/` under the literature folder for every `.md` file, and reuses — **does not re-extract** — the existing PDF text cache (`merlin_publication_audit`'s `data/raw/psicat_exports_2026-10-08.json.gz`) for the three self-authored PDFs, exposed as three synthetic sources `psicat-export:publications`, `psicat-export:comic_shop`, `psicat-export:knowledge_library`.
* Every chunk produced is tagged `governance_label="PSICAT_EDITORIAL_CORPUS"` (new field on `DocumentChunk`, default `"REPOSITORY_CORE"` everywhere else) and weighted `0.85` in `_source_weight()` — slightly below the default `1.0`, because this is reference/editorial material, not hardgate authority.
* `RAGIndex.build()` / `build_intent_index()` gained an `include_psicat_literature: Optional[bool]` kwarg (falls back to the `UM_PSICAT_EDITORIAL_CORPUS` env flag) so the corpus is additive and opt-in, never silently merged into the default 1,757-chunk physics index.
* `merlin_rag.retrieve_context()` always returns a `"psicat_literature"` key; it is an empty list unless `MERLIN_PSICAT_LITERATURE_CORPUS=1`, in which case it is populated via a lazily-imported BM25 ranking over the same corpus (`_psicat_literature_context()`).
* `merlin_flag_ab.OPT_IN_FLAGS`/`variant_map` gained the `psicat_literature_corpus` variant so this flag goes through the same zero-regression promotion gate as every prior upgrade.

## Measured, not asserted

`evaluate_literature_rankers()` runs an 11-query, hand-labelled set (paraphrased titles/descriptions of specific Books, Articles, and the three PDF exports — not exact-title lookups) against the full 437-document / 4,783-chunk corpus:

| Ranker | recall@1 | recall@3 | recall@5 | MRR | nDCG@5 |
|---|---|---|---|---|---|
| jaccard | 0.3636 | 0.5455 | 0.5455 | 0.4711 | 0.4664 |
| **bm25** | **0.9091** | **0.9091** | **0.9091** | **0.9134** | **0.9091** |
| rrf (jaccard+bm25) | 0.3636 | 0.6364 | 0.8182 | 0.5167 | 0.5822 |

**Honest reading:** BM25 alone clearly wins on this corpus (`best_by_mrr: "bm25"`) — exact-token lexical matching does well because the labelled queries paraphrase real titles with shared vocabulary. Plain Jaccard set-overlap lags badly (0.47 MRR) because it has no term-frequency weighting over long documents, and string-source RRF fusion (a jaccard+bm25 blend, re-derived locally since the pillar-corpus `reciprocal_rank_fusion` hard-casts ids to `int()` and cannot rank string paths) sits between the two rather than beating BM25 outright — fusing a weak ranker with a strong one here pulls the blend down, not up. This is a small, indicative set (11 queries over 437 documents), not a claim of general-purpose literature search quality.

`merlin_flag_ab.run_flag_ab(limit_per_stage=2, variants={"baseline": (), "psicat_literature_corpus": (...)})` over all six benchmark stages (12 runs each) shows `promotable: true`, zero regressions, zero `answers_changed` — expected, since the flag currently only populates an inert `retrieve_context()["psicat_literature"]` key that no answer-generation path yet consumes (see "What this is not").

## What this honestly is

* a corpus loader that reuses the existing, already-audited PDF text cache rather than re-parsing the PDFs;
* a governance-labelled, separately-weighted, opt-in retrieval source distinct from both the hardgate physics index and the audit-only gzip cache;
* benchmarked with its own hand-labelled query set and its own string-id-safe ranking helpers (the existing `_jaccard_ranking`/`_bm25_ranking`/`reciprocal_rank_fusion` in `merlin_retrieval_eval.py` assume integer pillar ids and cannot rank this corpus directly);
* shipped behind two independent default-OFF flags (repo-root and Navigator) until it clears `run_flag_ab`'s promotion bar.

## What this is not

* **not** a factual-claim audit. Indexing a sentence for retrieval is not the same as verifying it; `merlin_publication_audit.py` remains the only gate that checks whether a published claim is actually true.
* **not** wired into `merlin_engine.query_merlin`'s answer-construction path yet. `retrieve_context()["psicat_literature"]` is populated when the flag is on, but no prompt-building code currently reads that key — this is a deliberate, honestly-documented deferral, not a hidden limitation. Wiring it into answer construction is future work, gated the same way.
* **not** a training-data promotion. See the separate, additive `build_psicat_literature_training_split()` in `merlin_program.py` for the fine-tuning-data path, which is opt-in and does not modify the existing kernel-S/P/R/A/G training bundle builder.
* **not** a claim that PsiCat has read or memorized this corpus in the way a human reads a book. It is a classic lexical-retrieval index (BM25/Jaccard over tokenized chunks) over text PsiCat himself produced — nothing more, nothing less.
