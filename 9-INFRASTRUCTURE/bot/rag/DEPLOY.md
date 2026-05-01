# Deploying the Unitary Manifold RAG Bot to HuggingFace Spaces

This guide covers deploying the Gradio chat UI to a free public HuggingFace
Space, as well as running the bot locally.

---

## Local development

### 1. Install dependencies

```bash
cd bot/rag
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

```bash
export OPENAI_API_KEY=sk-...
```

### 3. CLI mode (quick test)

```bash
python bot.py "What is the core claim of the Unitary Manifold?"
python bot.py "What is α and how is it derived?"
python bot.py "What are the honest gaps in the theory?"
```

### 4. FastAPI server mode

```bash
python bot.py --serve --port 8000
```

Then query it:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the FTUM?"}'
```

### 5. Gradio UI (local)

```bash
python app.py
# Opens http://localhost:7860 in your browser
```

---

## Deploying to HuggingFace Spaces

### Step 1 — Create a new Space

1. Go to <https://huggingface.co/spaces>
2. Click **Create new Space**
3. Fill in:
   - **Space name**: `unitary-manifold-assistant` (or your preferred name)
   - **License**: MIT (or as preferred)
   - **SDK**: **Gradio**
   - **Visibility**: Public (or Private)
4. Click **Create Space**

### Step 2 — Upload the bot files

Upload the following files from `bot/rag/` to the root of your Space:

| Local path | Upload as |
|-----------|-----------|
| `bot/rag/app.py` | `app.py` |
| `bot/rag/bot.py` | `bot.py` |
| `bot/rag/requirements.txt` | `requirements.txt` |
| `bot/rag/knowledge/01_core_theory.md` | `knowledge/01_core_theory.md` |
| `bot/rag/knowledge/02_equations.md` | `knowledge/02_equations.md` |
| `bot/rag/knowledge/03_predictions.md` | `knowledge/03_predictions.md` |
| `bot/rag/knowledge/04_python_api.md` | `knowledge/04_python_api.md` |
| `bot/rag/knowledge/05_quantum_theorems.md` | `knowledge/05_quantum_theorems.md` |

You can upload via the Space's web UI, or clone the Space repo and push:

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/unitary-manifold-assistant
cd unitary-manifold-assistant
# copy the files in
cp /path/to/bot/rag/app.py .
cp /path/to/bot/rag/bot.py .
cp /path/to/bot/rag/requirements.txt .
mkdir -p knowledge
cp /path/to/bot/rag/knowledge/*.md knowledge/
git add .
git commit -m "Add Unitary Manifold bot"
git push
```

### Step 3 — Add the OpenAI API key as a Space secret

If you want to pre-fund the Space so users don't need their own key:

1. Space page → **Settings** → **Variables and secrets**
2. Click **New secret**
3. Name: `OPENAI_API_KEY`
4. Value: your `sk-...` key
5. Click **Save**

> **Note:** If you don't add a secret, users enter their own API key in the
> chat UI. Both modes work.

### Step 4 — The Space is live

HuggingFace builds and starts the Gradio app automatically after each push.
The public URL is:

```
https://huggingface.co/spaces/YOUR_USERNAME/unitary-manifold-assistant
```

Share this URL in your repository README or social media.

---

## Adding the Space URL to the repository README

Open `README.md` in the repo root and add:

```markdown
## 🤖 Interactive Assistant

Try the live chatbot: [Unitary Manifold Assistant](https://huggingface.co/spaces/YOUR_USERNAME/unitary-manifold-assistant)
```

---

## Updating the knowledge base

When the repository's theory documents are updated:

1. Edit the relevant file(s) in `bot/rag/knowledge/`
2. Push to your HuggingFace Space repo
3. The Space rebuilds automatically

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: gradio` | Run `pip install -r requirements.txt` |
| `No module named 'bot'` | Ensure `bot.py` is in the same directory as `app.py` |
| Empty responses | Check that `knowledge/` directory exists and contains `.md` files |
| OpenAI error 401 | API key is invalid or expired |
| Space build fails | Check the Space logs; usually a missing dependency in `requirements.txt` |
