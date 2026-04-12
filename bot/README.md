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

## Knowledge files (shared across all options)

The `rag/knowledge/` directory contains five pre-chunked markdown files that
are used by the RAG bot and can be uploaded to Custom GPT / Claude Projects:

| File | Content |
|------|---------|
| `01_core_theory.md` | 5D geometry, irreversibility field, KK reduction |
| `02_equations.md` | All key equations and field symbol table |
| `03_predictions.md` | nₛ, β, α predictions + gaps + falsification |
| `04_python_api.md` | Python API usage with code examples |
| `05_quantum_theorems.md` | Theorems XII–XV |

---

## Repository links

- Main repo: <https://github.com/wuzbak/Unitary-Manifold->
- Theory overview: [`MCP_INGEST.md`](../MCP_INGEST.md)
- Plain-language summary: [`WHAT_THIS_MEANS.md`](../WHAT_THIS_MEANS.md)
