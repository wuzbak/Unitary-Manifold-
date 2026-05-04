# Unitary Manifold Q&A Bot — Deployment Options

This directory contains **four ready-to-deploy** chatbot options for the
[Unitary Manifold](https://github.com/wuzbak/Unitary-Manifold-) physics
repository. Each option trades setup complexity for control.

---

## Which option should I choose?

| Option | Setup time | Hosting cost | Code required | Best for |
|--------|-----------|-------------|---------------|----------|
| [1. Custom GPT / Claude Project](#1-custom-gpt--claude-project-zero-code) | ~10 min | Free (ChatGPT Plus / Claude Pro) | None | Personal use, demos |
| [2. GitHub Pages chatbot](#2-github-pages-chatbot-static-js) | ~5 min | Free (GitHub Pages) | Copy 1 file | Embedding on the project site |
| [3. GitHub Copilot Extension](#3-github-copilot-extension-copilot-chat) | ~30 min | Free (public repo) | Node 18 server | Developer-facing `@unitary-manifold` in Copilot Chat |
| [4. Python RAG bot (HuggingFace Spaces)](#4-python-rag-bot-huggingface-spaces) | ~20 min | Free (HF Spaces) | Python + OpenAI key | Public chatbot with knowledge-base RAG |

---

## 1. Custom GPT / Claude Project (zero-code)

**Directory:** [`custom-gpt/`](custom-gpt/)

Create a private or public AI assistant in minutes by uploading the theory
documents as knowledge files.

### Quick start

1. Read [`custom-gpt/SETUP_GUIDE.md`](custom-gpt/SETUP_GUIDE.md) for step-by-step instructions.
2. Copy the system prompt from [`custom-gpt/SYSTEM_PROMPT.md`](custom-gpt/SYSTEM_PROMPT.md).
3. Upload the six knowledge files listed in the guide.
4. Done — share the link.

### Files

| File | Purpose |
|------|---------|
| `SETUP_GUIDE.md` | Step-by-step creation guide for ChatGPT and Claude |
| `SYSTEM_PROMPT.md` | Ready-to-paste system prompt |

---

## 2. GitHub Pages Chatbot (static JS)

**Directory:** [`pages-chatbot/`](pages-chatbot/)

A floating 💬 button injected into any GitHub Pages / Jekyll site. Users
enter their own OpenAI API key (stored in `localStorage`). Zero server cost.

### Quick start

```bash
cp bot/pages-chatbot/chatbot-widget.js docs/
```

Then add to `docs/_layouts/default.html` (or any page):

```html
<script src="/chatbot-widget.js"></script>
```

See [`pages-chatbot/README.md`](pages-chatbot/README.md) for full instructions.

---

## 3. GitHub Copilot Extension (Copilot Chat)

**Directory:** [`copilot-extension/`](copilot-extension/)

Exposes the assistant as `@unitary-manifold` inside GitHub Copilot Chat.
Developers can ask questions without leaving their editor.

### Quick start

```bash
cd bot/copilot-extension
npm install
cp .env.example .env
npm run dev          # local dev server on :3000
```

See [`copilot-extension/DEPLOY.md`](copilot-extension/DEPLOY.md) for full
registration and production-deploy instructions.

### Files

| File | Purpose |
|------|---------|
| `server.js` | Express server implementing the Copilot Extensions skillset API |
| `package.json` | Node dependencies |
| `.env.example` | Environment variable template |
| `DEPLOY.md` | Full deployment guide |

---

## 4. Python RAG Bot (HuggingFace Spaces)

**Directory:** [`rag/`](rag/)

A full retrieval-augmented-generation bot with:
- In-memory keyword search over pre-chunked knowledge files
- FastAPI backend (`--serve` mode)
- Gradio chat UI deployable to HuggingFace Spaces
- CLI mode for quick testing

### Quick start (local)

```bash
cd bot/rag
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
python bot.py "What is α and how is it derived?"
```

### Start the Gradio UI

```bash
python app.py
```

See [`rag/DEPLOY.md`](rag/DEPLOY.md) for HuggingFace Spaces deployment.

### Files

| File | Purpose |
|------|---------|
| `bot.py` | RAG pipeline + CLI + FastAPI server |
| `app.py` | Gradio chat UI |
| `requirements.txt` | Python dependencies |
| `knowledge/` | Pre-chunked knowledge documents |
| `DEPLOY.md` | HuggingFace Spaces deployment guide |

---

## Knowledge sync — full repository

All four options are synced to the **complete repository knowledge**, not just
a hand-written summary.  160+ test files across 142 pillars + Ω₀ + Pillar Ω + Unitary Pentad, ~700K characters, ~175K tokens.

### How it works

| Option | How knowledge is loaded |
|--------|------------------------|
| Custom GPT / Claude Project | Upload `bot/context_snapshot.md` as a knowledge file |
| GitHub Pages chatbot | Full knowledge inlined in `chatbot-widget.js` at build time |
| Copilot Extension | All repo documents loaded from disk at server startup |
| RAG bot | Loads `bot/rag/knowledge/` summaries + full repo docs at runtime |

### Keeping it fresh

Whenever the repository content changes, regenerate the snapshot:

```bash
python bot/scripts/build_context.py
```

This reads every document in [AGENTS.md](../AGENTS.md) ingest order
(Tier 1 → 4) and writes `bot/context_snapshot.md`.  The file is gitignored
(generated, not hand-edited).  Re-upload it to your Custom GPT / Claude
Project after any significant theory update.

### What is indexed

```
Tier 1  WHAT_THIS_MEANS.md, MCP_INGEST.md, llms.txt, CITATION.cff, schema.jsonld
Tier 2  README.md, UNIFICATION_PROOF.md, QUANTUM_THEOREMS.md, FALLIBILITY.md,
        BIG_QUESTIONS.md, UNDERSTANDABLE_EXPLANATION.md, LEGEND.md, RELAY.md
Tier 3  wiki/ (7 pages), manuscript/ch02, submission/, docs/semantic-bridge.md,
        REVIEW_CONCLUSION.md, FINAL_REVIEW_CONCLUSION.md, NATURAL_SCIENCES.md,
        recycling/README.md, co-emergence/ (7 files: LIVING_PROOF.md, FRAMEWORK.md,
        INTENT_LAYER.md, TRUST_PROTOCOL.md, TRUTH_SYNTHESIS.md, OPEN_QUESTIONS.md,
        GENESIS.md), discussions/
Tier 4  src/core/metric.py, evolution.py, boundary.py, fixed_point.py,
        braided_winding.py, kk_geodesic_reduction.py, kk_gauge_spectrum.py,
        im_action.py, src/medicine/, src/justice/, src/governance/,
        src/neuroscience/, src/ecology/, src/climate/, src/marine/,
        src/psychology/, src/genetics/, src/materials/
Tier 5  Unitary Pentad/README.md, unitary_pentad.py, five_seven_architecture.py,
        pentad_scenarios.py, collective_braid.py, consciousness_autopilot.py,
        consciousness_constant.py, distributed_authority.py,
        sentinel_load_balance.py, mvm.py, resonance_dynamics.py
```

The monograph PDF (`THEBOOKV9a (1).pdf`) is not indexed by the RAG bot or
Copilot Extension — it is too large for automated processing.  Upload it
manually to Custom GPT / Claude Project if you want full 74-chapter coverage.

---

## Repository links

- Main repo: <https://github.com/wuzbak/Unitary-Manifold->
- Theory overview: [`MCP_INGEST.md`](../MCP_INGEST.md)
- Plain-language summary: [`WHAT_THIS_MEANS.md`](../WHAT_THIS_MEANS.md)

