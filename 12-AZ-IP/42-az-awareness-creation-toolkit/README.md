# AZ Awareness & Creation Toolkit — Product 42

**Folder:** `12-AZ-IP/42-az-awareness-creation-toolkit/`
**Version:** 1.0.0
**TRL:** TRL-2 (stdlib-first prototypes; composes existing tested products, no new verdict logic)
**Local URL:** `http://127.0.0.1:8142/`
**License:** AGPL-3.0-or-later

## Why this product exists

A holistic audit of PsiCat/Merlin's tool registry
(`12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_tools.py`, ~200
registered functions) found that **zero** of those tools referenced any of
this monorepo's other 41 sibling products. PsiCat could reason deeply
about Kaluza-Klein geometry, governance, and benchmark corpora, but had no
native awareness of its own house, and no general-purpose (non-physics)
creation tools.

This is a deliberately curated response, not an "overstuffed fat cat": seven
features, each addressing a distinct, non-redundant gap, each reusing
already-tested logic wherever a sibling product already owns it.

| Module | Ability |
|---|---|
| `registry.py` | **Feature 1 — product-registry awareness.** Parses the canonical `12-AZ-IP/README.md` table directly (`load_product_registry`, `get_product`) — no static, driftable duplicate. |
| `registry.py` | **Feature 2 — capability router.** `route_capability_request(intent)` ranks sibling products against a free-text intent using explainable term-overlap scoring (name matches score higher than description-only matches). |
| `documents.py` | **Feature 3 — document & config structural awareness.** `inspect_repository_document(path)` parses Markdown (headings + YAML front matter), YAML, TOML, JSON, and CSV repository documents using stdlib `tomllib`/`csv`/`json` plus already-used `PyYAML`. Paths are confined to the repository root. |
| `charts.py` | **Feature 4 — general-purpose SVG chart creation.** `create_bar_chart_svg`/`create_line_chart_svg`/`create_pie_chart_svg` for arbitrary labelled data, dependency-free. Distinct from Product 17's UM-physics-specific plots. |
| `cards.py` | **Feature 5 — knowledge-card deck creation with SM-2 spaced repetition.** `create_card_deck`/`review_card` generalize Product 20's fixed, bundled `flashcard.py` deck into a true creation tool for arbitrary Q/A content. |
| `citations.py` | **Feature 6 — citation/evidence verification.** `verify_citation_string` checks whether a claimed `path:line` or `path:line-line,line-line` citation (this repository's own evidence format) is real and resolvable. |
| `dashboard.py` | **Feature 7 — cross-product "home health" dashboard.** `build_home_health_snapshot()` composes the live registry count, Product 39's `ResearchDebtTracker.health_score()`, and Product 19's `route_all({})` falsification verdicts into one snapshot, adding no new scoring logic of its own (same non-duplication pattern as Product 33's accessibility pipeline). |

## Relationship to PsiCat/Merlin

All seven capabilities are wired as native PsiCat tool functions in
`merlin_tools.py` (`getPsiCatProductRegistry`, `routePsiCatCapabilityRequest`,
`inspectPsiCatRepositoryDocument`, `createPsiCatDataChart`,
`createPsiCatKnowledgeCardDeck`, `reviewPsiCatKnowledgeCard`,
`verifyPsiCatCitation`, `getPsiCatHomeHealthDashboard`), so PsiCat can call
them directly rather than this product existing only as a standalone web
surface.

## Epistemic status

- The capability router and citation verifier are intentionally simple,
  fully explainable term-overlap / regex-based tools — not machine
  learning, not semantic embeddings. Every suggestion or verdict can be
  traced back to which terms or line ranges matched.
- Document structural awareness degrades gracefully (reports an explicit
  error field) rather than silently failing when PyYAML is unavailable in
  a given environment; `tomllib` is Python 3.11+ stdlib and always
  available.
- The home-health dashboard reuses Product 19's and Product 39's already
  tested verdict/scoring logic verbatim via direct import — it does not
  reimplement or approximate either.
- SVG chart creation is pure arithmetic and string templating; there is no
  rendering engine, so output fidelity is limited to what hand-written SVG
  primitives (`rect`, `polyline`, `circle`, `path`) can express.

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for 12+ further research directions
considered but deliberately deferred (OCR, ASR/speech-to-text, a real
`ffmpeg` video bridge, translation, and more), each with a brief rationale
for why it was not included in this first increment.

## Running it

```bash
cd 12-AZ-IP/42-az-awareness-creation-toolkit
python3 run.py                         # demo: registry + router + chart + card deck + dashboard
python3 run.py route "comic video audio media"
python3 run.py verify-citation "src/core/metric.py:1-5"
python3 run.py serve --port 8142       # live HTTP product + UI at http://127.0.0.1:8142/
python3 -m pytest tests/ -q
```
