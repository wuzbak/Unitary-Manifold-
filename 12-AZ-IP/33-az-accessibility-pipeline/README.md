# AZ Accessibility Pipeline — Product 33

**Folder:** `12-AZ-IP/33-az-accessibility-pipeline/`
**Version:** 1.1.0
**TRL:** TRL-2 (orchestration layer over three existing products; claim recognition is keyword-based)
**Status:** Active — Phases 0-2 (narrow slice) of article-354's accessibility roadmap, now a runnable web product

## What this is

`12-AZ-IP/18-um-reader` (TTS reading), `12-AZ-IP/17-um-image-generator`
(concept visualization), and `12-AZ-IP/19-falsification-observatory`
(live experimental verdicts) are three separate products. This pipeline
wires their *logic* together behind one call, `build_accessibility_report()`:

1. **Reading layer** (`split_into_reading_segments`) — sentence-level
   chunking suitable for feeding one segment at a time to a TTS engine.
2. **Visualization layer** (`suggest_visual_concepts`) — keyword-matches
   recognizable UM concepts against the eight visuals Product 17 already
   renders (CMB plane, birefringence window, KK tower, braid topology, 5D
   metric, Δm²₂₁ timeline, hardgate domain pie, falsification calendar).
3. **Fact-check layer** (`route_recognizable_claims`) — keyword-matches
   recognizable claims against Product 19's seven live falsification
   fronts and routes them through Product 19's own, already-tested
   `route_litebird`, `route_desi`, `route_juno`, `route_act`,
   `route_hllhc`, `route_nedm`, and `route_xenon` functions. This product
   introduces **no new verdict logic** — every verdict is whatever
   Product 19 already computes.

## Epistemic status

Claim recognition here is deliberately simple keyword matching, not a
general NLP claim-extraction model — the article is explicit that this is
"the hardest phase, because it requires a claim-recognition step that does
not fully exist yet." This product covers a narrow, honest slice of that
phase: recognizable, pre-named claims only. The web interface can read
individual sentence segments or the full passage continuously using the
browser's built-in speech-synthesis service, with voice and speed controls.
Available voices and speech quality depend on the browser and operating
system. The pipeline suggests visual concepts but does not render images;
rendering remains Product 17's responsibility.

## Usage

```bash
python 12-AZ-IP/33-az-accessibility-pipeline/run.py
python 12-AZ-IP/33-az-accessibility-pipeline/run.py "Your own passage about birefringence here."
```

## Running as a web product

A stdlib-only JSON API plus a static dashboard sits over the same pipeline above
(`app/server.py` dispatches to `dispatch_api_request`, covered by `tests/test_api.py`):

```bash
python 12-AZ-IP/33-az-accessibility-pipeline/run.py serve --port 8133
# then open http://127.0.0.1:8133/
```

Endpoints: `GET /api/status`, `GET /api/report?text=`.

The dashboard turns the report into readable sentence cards, continuous or
per-sentence speech playback, concept suggestions, and claim-verdict summaries.
Speech playback is a browser feature and is unavailable in browsers without the
Web Speech API; the text report remains usable there. The JSON endpoints and CLI
remain available independently of browser speech support.

## Tests

```bash
python -m pytest 12-AZ-IP/33-az-accessibility-pipeline/tests -q
```

## Sources

- `12-AZ-IP/18-um-reader`, `12-AZ-IP/17-um-image-generator`, `12-AZ-IP/19-falsification-observatory`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #6

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
