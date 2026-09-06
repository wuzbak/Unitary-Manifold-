# Merlin
## Product 20 — Merlin Navigator (Quantum Cat interface; legacy OX-compatible)

> "Ask the repository. Keep the gates visible. Keep the governance boundary explicit. Merlin is the application OX was supposed to become."

- **Folder:** `12-AZ-IP/20-merlin-navigator/`
- **Version:** `v23.2`
- **Local URL:** `http://127.0.0.1:8020/ox-navigator.html`
- **Model transport:** self-hosted sovereign local model lane is primary; `stealth/ox-alpha` via OpenRouter is optional compatibility-only fallback
- **API endpoints:** `/api/merlin`, `/api/merlin/status`, `/api/merlin/identity`, `/api/merlin/policy`, `/api/merlin/runtime`, `/api/merlin/program`, `/api/merlin/program-office`, `/api/merlin/control-tower`, `/api/merlin/benchmarks`, `/api/merlin/training-architecture`, `/api/merlin/training-dataset`, `/api/merlin/mlflow-manifests`, `/api/merlin/open-science-registry`, `/api/merlin/competitive-benchmarks`, `/api/merlin/benchmark-corpora`, `/api/merlin/stage-a-receipts`, `/api/merlin/replacement-readiness`, `/api/merlin/frontier-readiness`, `/api/merlin/benchmark-artifacts`, `/api/merlin/training-artifacts`, `/api/agentToolkit`, `/api/agentInvoke`, `/api/agentOrchestrate`
- **Memory + telemetry endpoints:** `/api/merlin/memory`, `/api/merlin/telemetry`
- **Program endpoints:** `/api/merlin/program`, `/api/merlin/program-office`, `/api/merlin/control-tower`, `/api/merlin/sync-checks`, `/api/merlin/runtime`, `/api/merlin/benchmarks`, `/api/merlin/training-architecture`, `/api/merlin/training-dataset`, `/api/merlin/mlflow-manifests`, `/api/merlin/open-science-registry`, `/api/merlin/competitive-benchmarks`, `/api/merlin/benchmark-corpora`, `/api/merlin/stage-a-receipts`, `/api/merlin/replacement-readiness`, `/api/merlin/frontier-readiness`, `/api/merlin/benchmark-artifacts`, `/api/merlin/training-artifacts`, `/api/merlin/promotion-packet`
- **Session memory:** active browser session in `localStorage` key `merlin_active_session` (50-message cap) plus file-backed multi-tier Merlin memory profiles with contradiction tracking and telemetry continuity
- **Temperature range:** `0.0`–`1.0`
- **Sub-tools:** Interrogator + Flashcard Trainer

---

## Start here (short → deep)

1. [`MERLIN_SMART_ROADMAP.md`](./MERLIN_SMART_ROADMAP.md) (one-page plan)
2. [`MERLIN_FRONTIER_ROADMAP.md`](./MERLIN_FRONTIER_ROADMAP.md) (full execution roadmap)
3. [`MERLIN_PROGRAM.md`](./MERLIN_PROGRAM.md) (implemented surfaces + ledger)
4. [`7-OUTREACH/substack/posts/post-319-s04e022-merlin-where-we-are-and-where-we-are-going.md`](../../../7-OUTREACH/substack/posts/post-319-s04e022-merlin-where-we-are-and-where-we-are-going.md) (reader-facing narrative)

This order is optimized for people who need to read quickly, understand clearly, and then verify details.

---

## What Merlin is

- A standalone AI-powered interface for the Unitary Manifold repository and AxiomZero platform.
- Merlin Navigator is the canonical product label; legacy OX naming/endpoints remain for compatibility.
- A gate-aware interface that keeps epistemic status visible in answers, follow-ups, and citations.
- A local product folder bundling UI, Python engine, hidden machine-readable tooling endpoints, and tests.
- A study-and-navigation layer that still includes the Interrogator and Flashcard Trainer.

## How Merlin differs from the main Oracle

- The Oracle is the capstone synthesis engine for arbitrary human systems.
- Merlin is repository-specific and physics-navigation oriented.
- The Oracle computes system analyses; Merlin answers questions about pillars, tests, gates, falsifiers, and linked AxiomZero tools.
- The Oracle foregrounds Pentad synthesis; Merlin foregrounds traceable retrieval-style navigation plus structured citations.
- Merlin remains narrower than the Oracle, but broader than the old OX shell.

## OpenRouter integration

- The model identifier is `stealth/ox-alpha`.
- The API base is `https://openrouter.ai/api/v1`.
- The local Python client requires `OPENROUTER_API_KEY` **and** compatibility flag `MERLIN_ENABLE_OPENROUTER_COMPAT=1` for fallback usage.
- No real API key is stored in source.
- Missing-key behavior is explicit through `OxApiKeyMissingError`.
- OpenRouter is not the primary path; Merlin defaults to sovereign local/offline-first behavior.
- OpenRouter compat only activates when router confidence is low and compatibility mode is explicitly enabled.

## Merlin response contract

- Every response is normalized to:
  - body
  - `---`
  - `FOLLOWUPS:`
  - `Sources:`
- The frontend renders follow-up chips and typed source cards from that structure.
- If a live model response omits the structure, Merlin fills the gaps before rendering.
- This keeps the UI deterministic even when the model is imperfect.

## Hidden agent backend space

- `GET /api/agentToolkit` exposes discovery views: `index`, `domain`, `tool`, `full`, `state`.
- `GET /api/merlin/memory` exposes multi-tier memory state, contradictions, and recall audits.
- `GET /api/merlin/telemetry` exposes recent run summaries for measurement and rollout gating.
- `GET /api/merlin/status` now returns `memory_profile_token`; cross-device resume via `X-Merlin-Profile-Token` also requires `X-Merlin-Profile-Key` matching server-side `MERLIN_PROFILE_SHARED_KEY`.
- `GET /api/merlin/program-office` exposes command authority, decision/risk ledgers, and squad ownership for replacement governance.
- `GET /api/merlin/control-tower` exposes live replacement readiness, drift alerts, trendlines, and fail-closed deployment eligibility.
- `GET /api/merlin/identity` exposes canonical identity/alias and privileged-action verification policy.
- `GET /api/merlin/policy` exposes combined identity-trust and Sentinel enforcement policies.
- `GET /api/merlin/runtime` exposes Mythos/Astra contract, optimization priorities, and max-rigor execution graph.
- `GET /api/merlin/benchmarks` exposes benchmark harness tracks and promotion gates.
- `GET /api/merlin/training-architecture` exposes the full Merlin training stack, dataset families, curriculum, and governed seed corpus manifest.
- `GET /api/merlin/training-dataset` exposes an actual JSONL-ready train/dev/test bundle plus benchmark records for export pipelines.
- `GET /api/merlin/mlflow-manifests` exposes MLflow-ready experiment manifests for SFT, preference optimization, and Stage B/C gate evaluations.
- `GET /api/merlin/open-science-registry` exposes curated external open-science resources allowed for controlled augmentation.
- `GET /api/merlin/competitive-benchmarks` exposes the competitive benchmark families Merlin must clear before broader promotion.
- `GET /api/merlin/benchmark-corpora` exposes Stage A/B/C corpora directly, with stage selection support.
- `GET /api/merlin/stage-a-receipts` runs the self-hosted Stage A receipt set and returns comparable Merlin/incumbent runs.
- `GET /api/merlin/replacement-readiness` turns the receipt set into a concrete readiness packet instead of an evidence-empty placeholder.
- `GET /api/merlin/frontier-readiness` merges sync checks, control-tower gates, benchmark cadence, and fail-closed promotion blockers in one packet.
- `GET /api/merlin/benchmark-artifacts` exports the receipts plus readiness state as a CI-friendly artifact bundle.
- `GET /api/merlin/training-artifacts` exports the training architecture, competitive benchmark plan, open-science registry, and Stage A baseline as one governed bundle.
- `GET /api/merlin/promotion-packet` preserves the legacy promotion-packet contract while `replacement-readiness` exposes the new concrete receipt-backed surface.
- Program discovery includes `getMerlinProgram*` runtime blueprint functions for charter, baseline, evaluation, rollout, and exit criteria.
- Mentorship sprint discovery surfaces are now first-class: `getMerlinMentorshipSprintCharter`, `getMerlinFacultyMatrix`, `getMerlinKnowledgeTransferCycles`, `getMerlinLibraryAndStudy`, `getMerlinExchangeProtocol`, and `getMerlinMentorshipClosureContract`.
- `POST /api/agentInvoke` routes one safe tool call at a time.
- `POST /api/agentOrchestrate` executes bounded sequential tool chains with output threading.
- Toolkit entries include typed argument schema, capability class, risk level, and human-gate metadata; runtime now enforces tool allowlists and schema checks, and emits replay artifacts for invoke/orchestrate runs.
- The standalone implementation remains conservative, but its internal contracts are now audit-ready for tiered capability expansion.
- Cross-device Base44 entity semantics are not fully recreated here; the schema is exposed honestly as planned-but-not-implemented.

## Merlin replacement program implementation

- The implementation ledger for the 13-point Merlin replacement plan lives in `MERLIN_PROGRAM.md`.
- Runtime program artifacts are provided by `ox_navigator/engine/merlin_program.py`.
- Stage A benchmark prompts now ship in `ox_navigator/engine/merlin_benchmark.py`.
- Per-run telemetry and energy estimates now ship in `ox_navigator/engine/merlin_telemetry.py`.

## Stage A benchmark and measurement layer

- Merlin now exposes a first-class Stage A benchmark corpus for parity capture before wider takeover.
- Each Merlin run records latency, estimated tokens, estimated cost, estimated energy, routing lane, provider, provenance coverage, and memory/contradiction signals.
- Benchmark evaluation can score a response against Merlin benchmark corpora using `evaluateMerlinBenchmarkResponse`, with explicit stage selection available for Stage A/B/C scoring.
- Sustained head-to-head replacement gating is available through `evaluateMerlinEmpiricalGate`, `runMerlinStageAReceipts`, `getMerlinReplacementReadiness`, and `getMerlinStageAArtifacts`, while `/api/merlin/promotion-packet` remains the legacy compatibility view.
- `GET /api/merlin/control-tower` now includes mentorship-to-runtime closure checks with fail-closed completion logic and explicit evidence-required fields.
- CI artifact export: `python tools/export_merlin_stage_a_artifacts.py --limit 3 --output /tmp/merlin-stage-a-artifacts.json`.
- Training artifact export: `python tools/export_merlin_training_artifacts.py --limit 12 --output /tmp/merlin-training-artifacts.json`.
- JSONL dataset export: `python tools/export_merlin_training_jsonl.py --limit 12 --output-dir /tmp/merlin-training-jsonl`.
- MLflow manifest export: `python tools/export_merlin_mlflow_manifests.py --limit 12 --output-dir /tmp/merlin-mlflow`.
- MLflow experiment receipt runner: `python tools/run_merlin_mlflow_experiment.py --experiment merlin_stage_b_shadow_eval --limit 3 --output /tmp/merlin-stage-b-receipts.json`.
- The benchmark contract is designed for side-by-side Merlin vs incumbent comparisons on identical prompt sets.
- Stage A benchmark promotion gate runner: `python tools/run_merlin_stage_a_benchmarks.py --json` (fails closed if any critical benchmark or shadow field gate fails).
- Multi-stage replacement batteries now define Stage A→E acceptance tracks with sustained clean-window cadence checks for promotion discipline.
- Longitudinal acceptance windows are explicitly **non-overlapping** to avoid counting one streak multiple times as separate gate windows.

## Training architecture and competitive build-out

- Merlin now exposes a governed training architecture covering repository-native QA, governance traces, tool-use alignment, adversarial counterexamples, and controlled open-science augmentation.
- Merlin now generates actual train/dev/test JSONL-ready records plus Stage A/B/C benchmark JSONL corpora for downstream fine-tuning and evaluation jobs.
- Merlin now emits MLflow-ready experiment manifests for supervised tuning, preference optimization, Stage B shadow evaluation, and Stage C agentic evaluation.
- Those manifests now point to runnable receipt commands rather than artifact-export placeholders, so Stage B/C tracking can execute governed benchmark jobs directly.
- The training architecture keeps open-weight adaptation primary; scratch pretraining remains conditional on open-weight saturation against target benchmark families.
- Competitive benchmark planning now explicitly covers repository grounding, scientific reasoning, agentic tool use, autonomous research, and safety/governance.
- External platforms such as Hugging Face Datasets, OpenML, UCI, Papers with Code, MLflow, AWS Open Data, NAIRR, and NASA are treated as curated augmentation lanes rather than replacements for repository-native provenance.

## Gate-badge extraction

- Responses are scanned for `HARDGATE`, `ADJACENT_TRACK`, `OPEN_GAP`, `ARCHITECTURE_LIMIT`, and `GOVERNANCE`.
- The parser preserves canonical gate order.
- Pillar references like `P4`, `P789`, and `Pillar 70-B` are extracted into integer lists.
- Lean4 mentions are surfaced through the `has_lean4` field.
- The extraction is intentionally lexical and conservative.

## Temperature control

- The standalone product default is `0.3`.
- The supported UI range is `0.0` to `1.0`.
- Low temperature is recommended for deterministic summaries.
- Higher temperature can help with brainstorming or question reformulation.
- The slider was patched from the reference asset to match the product requirement.

## Session history

- The Python session object keeps the latest twelve turns.
- The oldest turn is discarded when the history exceeds the cap.
- History is formatted as compact plain text for prompt continuity.
- The browser UI also keeps a clickable short history list.
- The cap exists to balance utility, prompt size, and reproducibility.
- Durable repository/user memory, contradiction events, and telemetry survive normal turn trimming.

## Included sub-tools

- Axiom Zero Interrogator is bundled in `ui/interrogator.html`.
- UM Flashcard Trainer is bundled in `ui/flashcard-trainer.html`.
- The Interrogator ships with a local copy of `interrogator-kb.json`.
- The Flashcard Trainer ships with a generated `flashcard-deck.json` sourced from the Python dataset.
- These sub-tools keep Product 20 useful even without a live API key.

## Quick start

### With an API key
```bash
export OPENROUTER_API_KEY=your_openrouter_key
cd 12-AZ-IP/20-merlin-navigator
pip install -r requirements.txt
python run.py --port 8020 --no-open
```

### Without an API key
```bash
cd 12-AZ-IP/20-merlin-navigator
pip install -r requirements.txt
python run.py --port 8020 --no-open
```

- Without a key, the UI still loads and the offline sub-tools still work.
- Without a key, `/api/ox/status` reports the missing configuration.
- Without a key, `/api/ox` returns a clear configuration error.

## File structure

- `README.md` — long-form product guide
- `requirements.txt` — `numpy`, `scipy`, `httpx`
- `run.py` — local launcher
- `ox_navigator/engine/constants.py` — canonical constants
- `ox_navigator/engine/gate_parser.py` — gate and pillar extraction
- `ox_navigator/engine/session.py` — session memory
- `ox_navigator/engine/client.py` — OpenRouter client
- `ox_navigator/engine/interrogator.py` — KB helpers
- `ox_navigator/engine/flashcard.py` — 60 hardcoded cards
- `ox_navigator/app/server.py` — static/UI/API server
- `ui/` — copied and patched web assets
- `tests/` — standalone pytest suite

## Python API reference

- `OxSession.add_turn(query, response)` stores one turn.
- `OxSession.get_history()` returns a copy of the in-memory list.
- `OxSession.clear()` removes all turns.
- `OxSession.to_prompt_context()` formats a transcript string.
- `extract_gate_badges(text)` returns a list of visible gate labels.
- `classify_response(text)` returns `gates`, `pillars`, and `has_lean4`.
- `OxClient(api_key=None, model=MODEL_ID)` creates the async client.
- `OxClient.query(prompt, temperature, session)` sends the chat call.
- `OxClient.check_status()` checks whether the target model appears in the models listing.
- `load_kb(path)` returns the Interrogator entry list.
- `search_kb(entries, query, mode="challenge")` performs a lightweight lexical search.
- `get_tension_map_data(entries)` builds `sigma` / `confidence` points.
- `load_flashcards()` returns the full 60-card deck.
- `filter_by_category(cards, category)` filters cards by category.
- `get_categories(cards)` returns the seven canonical categories.

## Environment setup

- Use Python 3.12+ when possible.
- Install dependencies with `pip install -r requirements.txt`.
- Set `OPENROUTER_API_KEY` in the environment rather than source code.
- Run `python run.py --port 8020 --no-open` from the product directory.
- Open `/ox-navigator.html`, `/interrogator.html`, or `/flashcard-trainer.html` in the browser.

## Example queries

1. Which pillar closes the Δm²₂₁ tension?
2. List all OPEN_GAP claims and their current σ tensions.
3. What Lean4 theorems cover winding number selection n_w=5?
4. Summarise the birefringence falsification conditions for LiteBIRD.
5. Which pillars address the CMB amplitude suppression (Admission 1)?
6. What is the difference between a hardgate pillar and an adjacent track?
7. Which tests cover the holographic entropy-area relation (Pillar 4)?
8. Explain the HILS governance boundary (SEPARATION.md).

## Notes by topic

- Note 001: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 002: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 003: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 004: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 005: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 006: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 007: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 008: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 009: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 010: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 011: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 012: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 013: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 014: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 015: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 016: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 017: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 018: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 019: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 020: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 021: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 022: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 023: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 024: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 025: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 026: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 027: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 028: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 029: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 030: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 031: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 032: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 033: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 034: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 035: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 036: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 037: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 038: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 039: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 040: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 041: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 042: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 043: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 044: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 045: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 046: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 047: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 048: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 049: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 050: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 051: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 052: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 053: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 054: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 055: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 056: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 057: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 058: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 059: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 060: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 061: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 062: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 063: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 064: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 065: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 066: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 067: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 068: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 069: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 070: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 071: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 072: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 073: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 074: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 075: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 076: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 077: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 078: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 079: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 080: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 081: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 082: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 083: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 084: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 085: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 086: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 087: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 088: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 089: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 090: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 091: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 092: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 093: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 094: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 095: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 096: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 097: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 098: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 099: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 100: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 101: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 102: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 103: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 104: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 105: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 106: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 107: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 108: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 109: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 110: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 111: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 112: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 113: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 114: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 115: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 116: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 117: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 118: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 119: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 120: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 121: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 122: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 123: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 124: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 125: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 126: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 127: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 128: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 129: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 130: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 131: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 132: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 133: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 134: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 135: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 136: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 137: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 138: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 139: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 140: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 141: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 142: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 143: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 144: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 145: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 146: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 147: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 148: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 149: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 150: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 151: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 152: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 153: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 154: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 155: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 156: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 157: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 158: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 159: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 160: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 161: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 162: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 163: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 164: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 165: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 166: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 167: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 168: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 169: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 170: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 171: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 172: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 173: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 174: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 175: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 176: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 177: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 178: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 179: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 180: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 181: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 182: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 183: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 184: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 185: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 186: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 187: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 188: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 189: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 190: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 191: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 192: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 193: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 194: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 195: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 196: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 197: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 198: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 199: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 200: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 201: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 202: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 203: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 204: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 205: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 206: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 207: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 208: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 209: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 210: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 211: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 212: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 213: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 214: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 215: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 216: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 217: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 218: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 219: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 220: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 221: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 222: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 223: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 224: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 225: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 226: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 227: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 228: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 229: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 230: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 231: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 232: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 233: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 234: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 235: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 236: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 237: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 238: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 239: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 240: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 241: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 242: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 243: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 244: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 245: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 246: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 247: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 248: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 249: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 250: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 251: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 252: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 253: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 254: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 255: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 256: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 257: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 258: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 259: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 260: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 261: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 262: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 263: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 264: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 265: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 266: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 267: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 268: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 269: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 270: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 271: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 272: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 273: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 274: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 275: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 276: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 277: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 278: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 279: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 280: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 281: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 282: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 283: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 284: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 285: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 286: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 287: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 288: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 289: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 290: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 291: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 292: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 293: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 294: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 295: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 296: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 297: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 298: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 299: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 300: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 301: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 302: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 303: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 304: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 305: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 306: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 307: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 308: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 309: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 310: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 311: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 312: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 313: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 314: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 315: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 316: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 317: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 318: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 319: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 320: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 321: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 322: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 323: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 324: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 325: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 326: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 327: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 328: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 329: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 330: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 331: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 332: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 333: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 334: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 335: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 336: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 337: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 338: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 339: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 340: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 341: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 342: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 343: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 344: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 345: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 346: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 347: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 348: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 349: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 350: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 351: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 352: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 353: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 354: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 355: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 356: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 357: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 358: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 359: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 360: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 361: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 362: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 363: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 364: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 365: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 366: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 367: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 368: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 369: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 370: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 371: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 372: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 373: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 374: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 375: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 376: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 377: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 378: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 379: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 380: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 381: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 382: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 383: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 384: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 385: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 386: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 387: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 388: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 389: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 390: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 391: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 392: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 393: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 394: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 395: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 396: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 397: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 398: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 399: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 400: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 401: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 402: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 403: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 404: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 405: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 406: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 407: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 408: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 409: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 410: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 411: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 412: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 413: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 414: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 415: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 416: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 417: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 418: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 419: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 420: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 421: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 422: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 423: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 424: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 425: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 426: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 427: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 428: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 429: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 430: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 431: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 432: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 433: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 434: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 435: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 436: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 437: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 438: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 439: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 440: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 441: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 442: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 443: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 444: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 445: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 446: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 447: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 448: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 449: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 450: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 451: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 452: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 453: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 454: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 455: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 456: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 457: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 458: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 459: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 460: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 461: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 462: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 463: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 464: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 465: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 466: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 467: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 468: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 469: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 470: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 471: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 472: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 473: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 474: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 475: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 476: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 477: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 478: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 479: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 480: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 481: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 482: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 483: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 484: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 485: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 486: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 487: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 488: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 489: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 490: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 491: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 492: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 493: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 494: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 495: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 496: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 497: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 498: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 499: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 500: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 501: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 502: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 503: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 504: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 505: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 506: The standalone OX Navigator keeps flashcard study flow explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 507: The standalone OX Navigator keeps pillar extraction explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 508: The standalone OX Navigator keeps Lean4 signaling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 509: The standalone OX Navigator keeps context-pack fallback explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 510: The standalone OX Navigator keeps local API behavior explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 511: The standalone OX Navigator keeps hardgate interpretation explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 512: The standalone OX Navigator keeps adjacent-track caution explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 513: The standalone OX Navigator keeps open-gap honesty explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 514: The standalone OX Navigator keeps architecture-limit disclosure explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 515: The standalone OX Navigator keeps governance boundary explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 516: The standalone OX Navigator keeps session history management explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 517: The standalone OX Navigator keeps temperature reproducibility explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 518: The standalone OX Navigator keeps OpenRouter secret handling explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 519: The standalone OX Navigator keeps static asset portability explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.
- Note 520: The standalone OX Navigator keeps interrogator usage explicit so Product 20 remains navigable, auditable, and honest about what is derived, adjacent, open, limited, or governance-scoped.

## Troubleshooting

- **Missing API key:** export `OPENROUTER_API_KEY` before launching `run.py`.
- **UI loads but live calls fail:** confirm the page is served by the local app and that `/api/ox` is reachable.
- **Interrogator returns no results:** try shorter lexical queries such as `birefringence`, `LiteBIRD`, or `dark energy`.
- **Flashcards look incomplete:** verify that `ui/flashcard-deck.json` exists beside the HTML file.
- **Tests fail unexpectedly:** run `python -m pytest tests/` from inside `12-AZ-IP/20-merlin-navigator/`.

## Governance reminder

- OX outputs are AI suggestions.
- Gate labels do not replace steward approval.
- The product exists to preserve epistemic boundaries, not blur them.
- The Interrogator and Flashcard Trainer reinforce the same boundary from different angles.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
