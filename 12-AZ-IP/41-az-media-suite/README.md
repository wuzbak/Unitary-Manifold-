# AZ Media & Feature-Inspection Suite — Product 41

**Folder:** `12-AZ-IP/41-az-media-suite/`
**Version:** 1.0.0
**TRL:** TRL-2 (stdlib-first prototypes; no native codec/rar toolchains bundled)
**Local URL:** `http://127.0.0.1:8141/`
**License:** AGPL-3.0-or-later

## What this is

This product gives PsiCat/Merlin the "collected suite" abilities requested
for comic, audio, and video media, plus an evidence-based feature-discovery
tool adapted from the workflow popularized by
[github.com/morluto/rea](https://github.com/morluto/rea) ("REA"):

| Module | Ability |
|---|---|
| `comic.py` | Parse (`inspect_comic_archive`), read individual pages from (`read_comic_page`), and create (`create_comic_archive`) CBZ (zip) comic archives, including `ComicInfo.xml` metadata. |
| `audio.py` | Parse WAV container metadata and simple signal statistics (`inspect_audio_file`), and synthesize tones/tone-sequences to PCM16 WAV (`synthesize_tone`, `create_tone_sequence_wav`). |
| `video.py` | Parse (`inspect_video_container`) and create (`create_video_container`) a lightweight, honest "AZ video container" (`.azvid`: zip of `manifest.json` + ordered PNG frames). |
| `feature_inspection.py` | Scan local HTML/JS/TS source for known feature signatures and report evidence-cited findings (`scan_app_features`). |

## Relationship to REA — what was and was not adopted

REA inspects native binaries (via Hopper/Ghidra/IDA), compiled
JS/Electron bundles, .NET assemblies, and live websites through an MCP
server and CLI, and returns pseudocode/assembly/strings with supporting
evidence. This repository does **not** install, bundle, or call REA's npm
package or MCP server — doing so would add an unreviewed third-party
runtime dependency and, for arbitrary third-party binaries, raise
reverse-engineering legal/licensing questions out of scope here.

What *was* adopted is REA's core methodology: **evidence-cited feature
discovery** — "results include the evidence and limitations behind each
conclusion." `feature_inspection.scan_app_features()` reimplements that
idea narrowly and safely: it only reads plain-text source already on disk
(no binary disassembly, no execution of foreign code, no network calls),
and every finding cites the exact file, line number, and matched line text
so it can be independently re-verified. This is intentionally a much
smaller and more conservative tool than REA — pattern matching against a
small, legible signature table (`_FEATURE_SIGNATURES`), not semantic
analysis.

## Epistemic status

- The comic viewer supports CBZ (zip) archives only. CBR/RAR archives are
  detected and rejected with a clear error (`UnsupportedComicFormatError`)
  rather than silently failing, because RAR extraction needs a non-stdlib
  `unrar` binary this repository does not bundle.
- "Audio understanding" is container metadata plus RMS/peak amplitude —
  not speech recognition or music transcription.
- "Video understanding/creation" covers only this product's own
  self-contained `.azvid` frame-sequence container, not real video codecs
  (H.264/VP9/...), which need ffmpeg or a similar native toolchain not
  bundled here.
- The feature inspector is conservative substring matching: a match means
  the signature text is present in the source, not that the feature is
  necessarily wired up correctly or still live.

## Usage

```bash
python 12-AZ-IP/41-az-media-suite/run.py                       # demo comic/audio/video round trip
python 12-AZ-IP/41-az-media-suite/run.py inspect-features ui   # evidence-cited feature scan of a directory
python 12-AZ-IP/41-az-media-suite/run.py serve --port 8141     # start the live HTTP product
```

Endpoints: `GET /api/status`, `GET /api/comic/demo`, `GET /api/audio/demo`,
`GET /api/video/demo`, `GET /api/inspect/self`. Every endpoint operates on
a fixed, product-local `workspace/` directory or this product's own
bundled `ui/` directory — there are no arbitrary-filesystem-path query
parameters, so path traversal is not applicable rather than merely
sanitized.

## Tests

```bash
python -m pytest 12-AZ-IP/41-az-media-suite/tests/ -q
```

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
