# ROADMAP.md — AZ Awareness & Creation Toolkit (Product 42)

## v1.0 — Seven immediate features ✅ (Current)

- [x] Feature 1 — live product-registry awareness (`registry.py`)
- [x] Feature 2 — capability router (`registry.route_capability_request`)
- [x] Feature 3 — document & config structural awareness (`documents.py`)
- [x] Feature 4 — general-purpose SVG chart creation (`charts.py`)
- [x] Feature 5 — knowledge-card deck creation with SM-2 spaced repetition (`cards.py`)
- [x] Feature 6 — citation/evidence (`path:line`) verification (`citations.py`)
- [x] Feature 7 — cross-product "home health" dashboard (`dashboard.py`)
- [x] All seven wired as native PsiCat tools in `merlin_tools.py`
- [x] 58 passing tests (7 test files)

## Future roadmap — 12+ further research directions

These were considered during the deep-dive research pass and deliberately
**not** built in v1.0, each for a specific, stated reason (usually: needs a
new external dependency this repository does not yet carry, or needs more
design work than a single increment allows). Listed roughly in order of
how close each is to being buildable with only already-available tools.

1. **OCR for comic/scanned-page text extraction.** Would let the comic
   viewer (Product 41) extract dialogue/captions as text. Needs a new
   dependency (`pytesseract` + the `tesseract` binary, or a pure-Python
   OCR model) not currently in `requirements.txt`; flag for
   `runtime-tools-gh-advisory-database` review before adding.
2. **ASR / speech-to-text for the audio module.** Would let Product 41's
   audio understanding transcribe spoken WAV content, not just report
   signal statistics. Needs a model dependency (e.g. `vosk`, `whisper.cpp`
   bindings); no network-hosted inference should be used given this
   repo's offline-first conventions.
3. **A real `ffmpeg` bridge for the video module.** The current `.azvid`
   container is an honest, stdlib-only zip-of-PNG-frames format; a real
   bridge would let Product 41 read/write actual MP4/WebM. Requires
   either bundling `ffmpeg` (a large native binary, licensing review
   needed) or a `pyav`/`imageio-ffmpeg` dependency.
4. **Neural text-to-speech for narration/accessibility.** Would pair with
   Product 33's accessibility pipeline to narrate articles/documents
   aloud. Needs a TTS model dependency and a decision on voice/licensing.
5. **Translation layer for PsiCat Literature and documentation.** Would
   let 7-OUTREACH content be offered in additional languages. Needs either
   a local translation model or an external API call, which conflicts
   with this repo's no-silent-network-calls convention unless explicitly
   opt-in and logged.
6. **Repository-wide semantic search index.** Feature 3 (document
   awareness) parses structure; a further step would build a searchable
   index over all Markdown/Python docstrings for PsiCat to query by
   meaning, not just keyword overlap. Needs an embeddings model and a
   vector-store decision (sqlite-vec vs. a dependency-free approach).
7. **Document-freshness CI linter.** A lightweight checker that flags
   Markdown documents whose referenced `path:line` citations (Feature 6)
   have drifted stale because the cited file changed since the citation
   was written. Buildable with only stdlib + `git`, but needs careful
   design to avoid false positives on intentional edits; a natural
   follow-up once Feature 6 has real-world usage data.
8. **Accessibility-profile-aware chart rendering.** Extend Feature 4's SVG
   charts with colorblind-safe palettes and pattern-fill fallbacks,
   feeding into Product 33's accessibility pipeline. Low-dependency, but
   needs a palette-selection and contrast-ratio design pass.
9. **Geospatial awareness bridge to Product 21 (geo-monitor).** Let the
   capability router and dashboard also surface geo-monitor's live
   environmental signals. Deferred because Product 21's data sources are
   network-dependent and would need an explicit offline-fallback
   contract, mirroring Product 40's live-data-harness pattern.
10. **Civic/public-record awareness bridge to Product 08 (AXIOM
    Journalist).** Would let the capability router surface journalist
    case-lifecycle status alongside physics/governance tools. Deferred
    pending a privacy/scope review, since journalist cases may reference
    real-world subjects.
11. **3D/mesh awareness for Product 17's visualizations.** Extending
    structural document/data awareness to 3D mesh or point-cloud formats.
    Needs a mesh-parsing dependency (e.g. `trimesh`) not currently
    installed, and a clearer use case before committing to one format.
12. **Memory-graph visualization.** Render this session's/PsiCat's own
    stored memories (subjects, citations, scope) as an SVG graph using
    Feature 4's chart primitives. Deferred because it needs a stable,
    read-only memory-export format to build against first.
13. **Code-diff / PR semantic awareness.** Let PsiCat summarize a PR diff
    in terms of which products/pillars it touches, using Feature 1's
    registry to map changed paths back to products. Buildable without new
    dependencies, but needs git-diff parsing design beyond this
    increment's scope.
14. **Calendar/email ingestion with a strict privacy boundary.** Explicitly
    flagged as sensitive: would require an opt-in, locally-scoped,
    no-third-party-forwarding design reviewed separately before any code
    is written, consistent with this repository's prohibition on handling
    personal data without an explicit, deliberate privacy boundary.
15. **Mobile/sensor sync bridge** (pairing with Product 01's Android
    client and Product 25's Braided Brain PWA). Deferred pending a
    concrete sync-protocol decision; the existing products already define
    their own save/export formats this bridge would need to respect
    without duplicating.
16. **Comic panel-layout creation assist** (auto-suggest panel grids when
    creating new CBZ pages via Product 41). A natural Feature 4 + Product
    41 crossover, deferred so Feature 4's chart/SVG primitives can mature
    first and be reused rather than re-invented.
17. **Auto-insight charting** — automatically choose bar vs. line vs. pie
    for a given dataset shape when calling Feature 4, rather than
    requiring the caller to pick a chart type. Deferred as a usability
    polish pass once real usage patterns from v1.0 are observed.

Each item above should get its own small, scoped increment (own module,
own tests, own PsiCat tool registration) rather than being folded into an
already-shipped feature, consistent with this product's "no overstuffed
fat cat" design intent.
