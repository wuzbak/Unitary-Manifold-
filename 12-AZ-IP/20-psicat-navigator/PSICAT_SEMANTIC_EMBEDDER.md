# PsiCat Semantic Embedder — Local Token-to-Coordinate Projector

**Status:** 🔵 ADJACENT TRACK. Software retrieval tooling only. Not a hardgate physics claim, not a trained neural model, and not promoted into any default-on decision path.
**Module:** `ox_navigator/engine/merlin_semantic_embedder.py`
**Tests:** `tests/test_merlin_semantic_embedder.py`
**Endpoint:** `GET /api/psicat/semantic-embedder?query=…&top_k=…` (tool `getMerlinSemanticEmbedder`)
**Flag:** `MERLIN_SEMANTIC_EMBEDDER_RANKING` — OFF by default, exactly like `MERLIN_BM25_PILLAR_RANKING` and `MERLIN_TOROIDAL_CREASE_FUSION`.

## Why this exists

An outside reviewer pointed out a real gap: Merlin's retrieval stack (Jaccard, BM25, the integer toroidal phase sketch) all operate on exact or near-exact token matches. None of them give partial credit for morphological variants — "neutrino" against "neutrinos", "splitting" against "splittings" — because they split text into whole tokens before comparing anything. The reviewer called the missing piece a "token-to-manifold translation layer" and suggested stitching in a quantized third-party open-weights model to produce it.

This module builds the same *kind* of thing — a deterministic function from text to a fixed-dimensional dense vector — without a third-party model, a network call, or a training step. It is a signed feature-hashed bag of character n-grams (the "hashing trick": Weinberger et al., *Feature Hashing for Large Scale Multitask Learning*, 2009), not a learned embedding. That distinction matters and is stated here plainly so nobody mistakes a sketching technique for semantic understanding.

## What it computes

For each token in a query or document:

1. Pad the token with `#` boundary markers and extract its 3-, 4-, and 5-character n-grams.
2. Hash each n-gram with BLAKE2b into a bucket index (`mod dims`) and a sign bit, then add the signed unit to that bucket of a `dims`-length vector (default `dims = 256`).
3. Hash the whole token itself (prefixed `@`) into another bucket with double weight, so exact token matches still count for more than their n-gram overlap alone.
4. L2-normalise the accumulated vector.

Similarity between two texts is the cosine of their vectors. Everything is pure Python/NumPy arithmetic; the same text produces the same vector on any machine, with no dependence on `PYTHONHASHSEED` or any external service — unlike Python's built-in `hash()`, BLAKE2b digests are stable across interpreter runs and platforms.

`EmbedderIndex` holds the hashed vectors for a document set and ranks a query against them by cosine similarity. `pillar_embedder_report` runs this over Merlin's pillar knowledge base and reports the embedder ranking alongside BM25's, and their top-k agreement — the same honesty pattern `merlin_toroidal_router.toroidal_rank` already uses for the integer phase sketch. BM25 remains the stated authority in both reports.

## Measured, not asserted

`merlin_retrieval_eval.evaluate_rankers(include_embedder=True)` adds two more measured rankers — `embedder` and `rrf_all` (reciprocal-rank fusion of Jaccard, BM25, and the embedder) — to the existing labelled-query evaluation, without touching the default `evaluate_rankers()` call or its `RANKERS`/`best_by_mrr` behaviour at all. Run against the current 30-query, 14-entry labelled corpus:

| Ranker | recall@1 | recall@3 | recall@5 | MRR | nDCG@5 |
|---|---|---|---|---|---|
| jaccard | 0.8111 | 0.8556 | 0.9556 | 0.9007 | 0.8951 |
| bm25 | 0.8778 | 0.9389 | 0.9389 | 0.9524 | 0.9289 |
| rrf (jaccard+bm25) | 0.8111 | 0.9389 | 0.9389 | 0.9079 | 0.8956 |
| **embedder** | 0.8444 | 0.9056 | 0.9056 | 0.9256 | 0.8976 |
| **rrf_all** (+embedder) | 0.8778 | 0.9389 | 0.9389 | 0.9526 | 0.9316 |

The embedder alone does not beat BM25 on this corpus — it sits between Jaccard and BM25 on MRR, which is the honest expectation for a lossy hashed sketch competing with an exact-term ranker on a vocabulary-matched labelled set. Fusing it with Jaccard and BM25 (`rrf_all`) edges out BM25 alone by a small margin (MRR 0.9526 vs 0.9524) on this run. That margin is inside the noise of a 30-query, hand-labelled set over a 14-entry corpus — indicative, not decisive, exactly as `merlin_retrieval_eval`'s existing caveat already says about `rrf`. The honest reading is: safe to measure, not yet earned a default-on promotion.

## Promotion path (unchanged from the existing toroidal lane)

1. The flag stays OFF by default. `retrieve_context`'s output is byte-for-byte unchanged unless `MERLIN_SEMANTIC_EMBEDDER_RANKING` is explicitly set, exactly as the existing BM25 pillar-ranking test (`test_bm25_pillar_ranking_flag_changes_order_only`) and the new embedder test (`test_semantic_embedder_ranking_flag_changes_order_only`) both check.
2. `merlin_flag_ab.run_flag_ab()` now includes a `semantic_embedder` variant (and `all_flags`, replacing the narrower meaning `both` used to carry alone) so the flag must clear the same zero-regression bar as every other opt-in upgrade in this lane before any future default-on discussion.
3. If both `MERLIN_BM25_PILLAR_RANKING` and `MERLIN_SEMANTIC_EMBEDDER_RANKING` are set, the embedder ranking is applied (it runs after the BM25 branch in `retrieve_context`); this precedence is deliberate and covered by `test_semantic_embedder_flag_takes_precedence_over_bm25_flag`.

## What this is not

* Not a projection onto the 5D Kaluza-Klein manifold. The toroidal lane's lattice routing (`merlin_toroidal_geometry`, `merlin_toroidal_router`) is the repository's separate, already-labelled 🔵 adjacent-track software emulation of a discrete phase space; this module does not feed into it and makes no claim to.
* Not a replacement for BM25, which both `toroidal_rank` and `pillar_embedder_report` keep as the stated retrieval authority.
* Not a general execution harness or an "operating system" for the agent. The existing fail-closed `merlin_local_execution` loop remains the only sanctioned path from a Navigator decision to a local system action, with its own allowlist, timeout cap, and token gate.
