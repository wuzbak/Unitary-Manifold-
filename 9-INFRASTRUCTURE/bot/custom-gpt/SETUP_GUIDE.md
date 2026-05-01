# Custom GPT & Claude Project — Setup Guide

This guide walks you through creating a dedicated Q&A assistant for the
Unitary Manifold theory using either **ChatGPT Custom GPT** (requires
ChatGPT Plus) or a **Claude Project** (requires Claude Pro / Teams).

Both options require **zero code**. The entire setup takes about 10 minutes.

---

## Knowledge files to upload

Upload all six files below. They give the model complete coverage of the
theory, equations, predictions, and Python API.

| File | Where to find it | Why it matters |
|------|-----------------|----------------|
| `MCP_INGEST.md` | repo root | Compact structured summary — identity, theory, API |
| `WHAT_THIS_MEANS.md` | repo root | Plain-language core claim |
| `README.md` | repo root | Full project overview + quickstart |
| `QUANTUM_THEOREMS.md` | repo root | Theorems XII–XV (BH info, CCR, Hawking T, ER=EPR) |
| `UNIFICATION_PROOF.md` | repo root | QM/EM/SM as exact projections of 5D geometry |
| `THEBOOKV9a (1).pdf` | repo root | Full 74-chapter monograph (optional but thorough) |

You can also upload the five pre-chunked knowledge files from `bot/rag/knowledge/`
for denser coverage of equations and API usage.

---

## A — Create a Custom GPT on ChatGPT

### Prerequisites

- ChatGPT Plus, Team, or Enterprise subscription
- Files downloaded locally from the repository

### Steps

1. **Open the GPT builder**
   Navigate to <https://chat.openai.com/> → your profile → **My GPTs** →
   **Create a GPT**.

2. **Switch to the Configure tab**
   Click **Configure** at the top of the builder.

3. **Set the name**
   ```
   Unitary Manifold Assistant
   ```

4. **Set the description**
   ```
   Expert assistant for ThomasCory Walker-Pearson's 5D Kaluza-Klein 
   gauge-geometric framework — the Unitary Manifold theory.
   ```

5. **Paste the system prompt**
   Copy the entire contents of [`SYSTEM_PROMPT.md`](SYSTEM_PROMPT.md)
   and paste it into the **Instructions** field.

6. **Upload knowledge files**
   Under **Knowledge** → **Upload files**, upload each of the six files
   listed above. ChatGPT will use these for retrieval when answering.

7. **Capabilities**
   - ✅ Web Search — keep enabled (for up-to-date Planck/LiteBIRD news)
   - ✅ Code Interpreter — keep enabled (users may want to run Python snippets)
   - ☐ Image Generation — disable (not relevant)

8. **Set conversation starters** (optional but helpful)
   ```
   What is the core claim of the Unitary Manifold?
   What is α and how is it derived?
   What are the key predictions and how can they be falsified?
   How does the FTUM work?
   ```

9. **Save and publish**
   - Click **Save** → choose visibility:
     - **Only me** — private use
     - **Anyone with a link** — share with collaborators
     - **Everyone** — public GPT store listing
   - Copy the share link and add it to your repository README.

---

## B — Create a Claude Project on claude.ai

### Prerequisites

- Claude Pro, Team, or Enterprise subscription
- Files downloaded locally from the repository

### Steps

1. **Create a new Project**
   Navigate to <https://claude.ai/> → **Projects** (left sidebar) →
   **New project**.

2. **Name the project**
   ```
   Unitary Manifold Assistant
   ```

3. **Add the system prompt (Project Instructions)**
   Click **Set project instructions** and paste the entire contents of
   [`SYSTEM_PROMPT.md`](SYSTEM_PROMPT.md).

4. **Upload knowledge files**
   Inside the project, click **Add content** → **Upload files**.
   Upload each of the six files listed above.
   
   > **Tip:** Claude Projects support up to 200,000 tokens of project
   > knowledge. The PDF alone is large — if you hit the limit, prioritise
   > the five `.md` files and skip the PDF.

5. **Start a conversation**
   Open a new conversation inside the project. All conversations in the
   project inherit the instructions and knowledge automatically.

6. **Share the project** (Teams/Enterprise only)
   Click **Share** → invite collaborators by email or copy the project link.

---

## Publishing checklist

Before sharing either assistant, verify:

- [ ] The assistant correctly states the core claim (Second Law as geometric identity)
- [ ] It gives the correct nₛ ≈ 0.9635 prediction
- [ ] It acknowledges the CMB amplitude gap honestly
- [ ] It correctly describes how to call `run_evolution()` in Python
- [ ] It cites specific files when asked (e.g., "see QUANTUM_THEOREMS.md")

---

## Keeping the assistant up to date

When the repository is updated (new theorems, revised predictions, code
changes), re-download the changed files and re-upload them to replace the
old knowledge files in your GPT or Claude Project.
