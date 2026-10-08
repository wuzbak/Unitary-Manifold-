# PsiCat PhiCat Protocol — Golden-Ratio Parallel Braid-Strand Fusion

**Status:** 🔵 ADJACENT TRACK. Software retrieval-fusion tooling only. Not a hardgate physics claim, not a replacement for any hardgate pillar, and not promoted into any default-on decision path.
**Module:** `ox_navigator/engine/merlin_phicat_protocol.py`
**Tests:** `tests/test_merlin_phicat_protocol.py`
**Endpoint:** `GET /api/psicat/phicat-protocol?query=…&top_k=…` (tool `getMerlinPhiCatProtocol`)
**Flag:** `MERLIN_PHICAT_PROTOCOL` — OFF by default, exactly like `MERLIN_BM25_PILLAR_RANKING`, `MERLIN_SEMANTIC_EMBEDDER_RANKING`, and `MERLIN_TOROIDAL_CREASE_FUSION`.

## Why this exists

Every fusion Merlin ships today — including the opt-in `rrf_all` measured in `PSICAT_SEMANTIC_EMBEDDER.md` — is reciprocal-rank fusion with one flat constant (`RRF_K = 60`): every strand gets the same weight on every query, folded together in a fixed order. That is a linear rule. The PhiCat Protocol is a second, independently named and independently benchmarked fusion rule, built to be structurally different in two specific ways, not just differently tuned:

1. **Parallel, not sequential.** Jaccard, BM25, the hashed n-gram embedder (`merlin_semantic_embedder`), and the integer toroidal phase sketch (`merlin_toroidal_geometry.phase_sketch`) are each computed from only the raw query and corpus tokens — none reads another strand's output. They are combined once, at the end, not folded in one at a time.
2. **Non-smooth, golden-ratio weighted, not a flat constant.** The *priority order* of the four strands is read out from the query's own **braid-bank residue** on the existing `Z₇₄` lattice (`merlin_toroidal_geometry.braid_bank` — the same integer invariant the toroidal navigation lane already uses to place a query on the lattice). Two queries whose bank residues sit on opposite sides of a `mod 4` boundary land in entirely different strand orders, with no interpolation between them. Within one order, strand weights decay by powers of the golden ratio `φ = (1+√5)/2` — the same constant this repository's hardgate **Pillar 208** (`src/core/pillar208_braid_lock_pmns.py`) already uses for the braid-lock Berry-phase quantum `k·π/(n₁·φ)`. Reusing φ here is a disclosed borrowing of its role as a discrete, non-linear step size; it is not a new claim about PMNS mixing angles, and nothing in this module touches Pillar 208's status.

A third signal, a **toroidal "gravity" weight**, additionally pulls candidates whose phase-sketch code sits lattice-near the query's own code, via an inverse-square-like falloff over `toroidal_distance`. "Gravity" is a plain-language name for "nearer points on the lattice pull harder" — the same lattice distance the navigation lane already treats as a locality-sensitive similarity signal (`sketch_similarity`). It is not a claim that this software implements gravitation.

Finally, the protocol reports — **read-only, with zero network calls** — whether a stronger local/compatible model is currently configured, by inspecting the existing provider registry in `merlin_local_inference.get_inference_providers()` (the same registry that already backs Merlin's `local_small`/`local_medium`/`openrouter_compat` reasoning lanes). This lets PhiCat honestly state whether it *could* be backed by a larger external or local model without ever requiring one, silently calling one, or changing ranking behaviour based on whether one is configured.

## What it computes

For a query and a pillar corpus:

1. Compute the query's phase-sketch code and each pillar's phase-sketch code (`merlin_toroidal_geometry.phase_sketch`).
2. Independently rank the corpus four ways: Jaccard, BM25, the hashed n-gram embedder, and ascending `toroidal_distance` to the query code.
3. Read the query's braid-bank residue mod 4 and rotate `STRAND_NAMES = (jaccard, bm25, embedder, toroidal_sketch)` by that amount — the per-query, non-smooth priority order.
4. Weight each strand by `φ⁻ᵏ` for its position `k` in that order (`1.0, 0.618…, 0.382…, 0.236…`).
5. For every (strand, candidate) pair, add `strand_weight × (1 / rank) × gravity_weight(distance)` to the candidate's fused score, where `gravity_weight(d) = 1 / (1 + (d / (K_CS/4))²)`.
6. Sort candidates by fused score (ties broken by ascending pillar id) and return the top-k with a full per-strand contribution breakdown.

Every step is pure, deterministic Python/NumPy arithmetic over existing corpus data — the same text and the same corpus always produce the same fused ranking, on any machine.

## Measured, not asserted

`merlin_retrieval_eval.evaluate_rankers(include_phicat=True)` adds a `phicat` ranker to the existing labelled-query evaluation, without touching the default `evaluate_rankers()` call or its `RANKERS`/`best_by_mrr` behaviour. Run against the current 30-query, 14-entry labelled corpus:

| Ranker | recall@1 | recall@3 | recall@5 | MRR | nDCG@5 |
|---|---|---|---|---|---|
| jaccard | 0.8111 | 0.8556 | 0.9556 | 0.9007 | 0.8951 |
| bm25 | 0.8778 | 0.9389 | 0.9389 | 0.9524 | 0.9289 |
| rrf (jaccard+bm25) | 0.8111 | 0.9389 | 0.9389 | 0.9079 | 0.8956 |
| embedder | 0.8444 | 0.9056 | 0.9056 | 0.9256 | 0.8976 |
| rrf_all (+embedder) | 0.8778 | 0.9389 | 0.9389 | 0.9526 | 0.9316 |
| **phicat** | 0.6444 | 0.9056 | 0.9389 | 0.8146 | 0.8280 |

**Honest reading:** PhiCat's recall@5 (0.9389) is competitive with BM25 and `rrf_all`, but its recall@1 and MRR are measurably *weaker* than every other ranker on this labelled set — meaning it more often finds the right pillar somewhere in the top 5 than puts it first. The non-smooth, per-query strand reordering is a deliberate structural property (see above), not a tuned-for-benchmark heuristic, and on this corpus that property does not yet beat the simpler, flat `rrf_all` fusion on ranking quality. This is reported exactly as measured, with no attempt to round it up: **`best_by_mrr` stays `rrf_all`, not `phicat`.** PhiCat is shipped because it is a genuinely different, independently falsifiable fusion architecture worth having in the A/B harness — not because it currently wins.

`merlin_flag_ab.run_flag_ab()` (full six-stage benchmark corpus, 34 benchmarks) shows `phicat_protocol` passing 34/34 with zero regressions (`promotable: true`), same as every other opt-in flag — it changes *which* pillars get surfaced in context (`answers_changed` lists 31 of 34 benchmarks, similar to the semantic embedder's 31/34) without breaking any benchmark's pass/fail gate.

## What this honestly is

* a deterministic, offline, reproducible fusion rule over the four rankings Merlin already computes — same inputs, same corpus, no new data source;
* a genuine behavioural difference from flat RRF: per-query strand priority changes discontinuously, driven by existing lattice arithmetic (`braid_bank`), not a tunable hyperparameter chosen to fit the benchmark;
* a disclosed, limited reuse of the golden ratio φ already present in this repository's hardgate Pillar 208 derivation, used here purely as a discrete multiplicative step size for strand weighting;
* benchmarked the same way every other upgrade in this lane is benchmarked, including when the result is "not yet better" — see the MRR comparison above;
* shipped behind a default-OFF flag (`MERLIN_PHICAT_PROTOCOL`) until (and unless) it clears the promotion bar on `merlin_flag_ab.run_flag_ab`.

## What this is not

* **not** a hardgate physics claim. It does not modify, depend on, or weaken Pillar 208's status or any other hardgate pillar;
* **"gravity" is not general relativity or Newtonian gravitation.** It is a named inverse-square-like weighting function over an integer lattice distance that already exists in this codebase (`toroidal_distance`);
* **not proven to beat `rrf_all` or BM25-alone on rank quality** — the table above shows it currently does not, on MRR and recall@1;
* **not a frontier-model integration.** `frontier_capability_report()` only reads the existing `merlin_local_inference` provider registry to report configuration status; it never issues a network request, and ranking results are identical whether or not a frontier/local provider is configured;
* **not a competitor to the Navigator's existing BM25-authoritative stance** — exactly like the semantic embedder and the toroidal crease fusion before it, this stays an additional, honestly measured option, not a silent default-path change.
