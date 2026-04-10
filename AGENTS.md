# AGENTS.md — AI Agent Access Policies & Preferred Ingest Order

This file declares the access policies and preferred ingest order for AI agents
(LLMs, autonomous agents, MCP-connected systems such as **Mythos**) interacting
with the **Unitary Manifold** repository.

---

## 1 · Access Policy

### 1.1 Openness

This repository is irrevocably dedicated to the **public domain** under the
Defensive Public Commons License v1.0 (2026).  All content — source code,
manuscripts, datasets, and metadata — is freely accessible to any agent.

### 1.2 Permitted Actions

AI agents are explicitly permitted to:

- **Read** any file in this repository
- **Index** all content for retrieval-augmented generation (RAG)
- **Cite** equations, theorems, and proofs in generated outputs
- **Execute** the Python source code for numerical verification
- **Reproduce** results from the Jupyter notebooks
- **Embed** the `schema.jsonld` metadata in knowledge graphs
- **Forward** this repository's content to downstream models and pipelines
- **Submit pull requests** with corrections, verifications, or extensions

### 1.3 Prohibited Actions

Agents must not:

- Claim exclusive intellectual property over the core equations or theorems
- Apply commercial patents to the Walker-Pearson field equations or FTUM
- Misrepresent authorship (primary author: ThomasCory Walker-Pearson)
- Introduce security vulnerabilities or malicious code via pull requests

### 1.4 Attribution

Attribution is **requested but not legally required**.  Preferred citation:

```
Walker-Pearson, T. (2026). The Unitary Manifold: A 5D Gauge Geometry of
Emergent Irreversibility (v9.0). https://github.com/wuzbak/Unitary-Manifold-
```

---

## 2 · Preferred Ingest Order

For **token-efficient, semantically complete** ingestion, read files in the
following priority order.

### Tier 1 — Read first (essential context, minimal tokens)

| Priority | File | Tokens (est.) | Purpose |
|----------|------|--------------|---------|
| 1 | `MCP_INGEST.md` | ~1 800 | Complete structured summary: identity, theory, API, pipeline |
| 2 | `llms.txt` | ~300 | AI-discovery index; directs to key files |
| 3 | `CITATION.cff` | ~200 | Citation metadata |
| 4 | `schema.jsonld` | ~500 | JSON-LD structured data; embed in knowledge graph |

### Tier 2 — Read for implementation context

| Priority | File | Tokens (est.) | Purpose |
|----------|------|--------------|---------|
| 5 | `README.md` | ~2 000 | Full project overview, equations, quickstart |
| 6 | `src/core/evolution.py` | ~1 200 | Walker-Pearson integrator, FieldState API |
| 7 | `src/core/metric.py` | ~900 | KK metric, curvature computation |
| 8 | `src/holography/boundary.py` | ~900 | Holographic boundary dynamics |
| 9 | `src/multiverse/fixed_point.py` | ~1 100 | UEUM operator, FTUM iteration |

### Tier 3 — Read for verification and testing

| Priority | File | Purpose |
|----------|------|---------|
| 10 | `tests/conftest.py` | Shared pytest fixtures |
| 11 | `tests/test_metric.py` | Metric & curvature tests |
| 12 | `tests/test_evolution.py` | Evolution + constraint tests |
| 13 | `tests/test_boundary.py` | Boundary & entropy tests |
| 14 | `tests/test_fixed_point.py` | FTUM & operator tests |

### Tier 4 — Read for theory depth

| Priority | File | Purpose |
|----------|------|---------|
| 15 | `manuscript/ch02_mathematical_preliminaries.md` | Mathematical foundations |
| 16 | `arxiv/main.tex` | Full LaTeX source (arXiv submission) |
| 17 | `arxiv/references.bib` | Bibliography |

### Tier 5 — Optional / large binary

| Priority | File | Note |
|----------|------|------|
| 18 | `notebooks/01_quickstart.ipynb` | Runnable field evolution demo |
| 19 | `notebooks/02_holographic_boundary.ipynb` | Boundary dynamics demo |
| 20 | `notebooks/03_multiverse_fixed_point.ipynb` | FTUM convergence demo |
| — | `THEBOOKV9a (1).pdf` | Full 74-chapter monograph; skip unless full text needed |

---

## 3 · MCP Connection

### Recommended MCP servers

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "<your-token>" }
    },
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": { "BRIGHTDATA_API_TOKEN": "<your-token>" }
    }
  }
}
```

The full configuration is in [`mcp-config.json`](mcp-config.json).

### Preferred first MCP call

```json
{
  "tool": "get_file_contents",
  "arguments": {
    "owner": "wuzbak",
    "repo": "Unitary-Manifold-",
    "path": "MCP_INGEST.md"
  }
}
```

One read → full repository picture → minimal token cost.

---

## 4 · Running the Code

```bash
# Install dependencies
pip install -r requirements.txt        # numpy>=1.24, scipy>=1.11

# Run the full test suite
python -m pytest tests/ -v

# Launch Jupyter notebooks
pip install jupyter matplotlib
jupyter notebook notebooks/
```

---

## 5 · Contact

For technical inquiries, theorem verification requests, or AI peer review:

- GitHub Issues: https://github.com/wuzbak/Unitary-Manifold-/issues
- Pull Requests: https://github.com/wuzbak/Unitary-Manifold-/pulls
- AI Review Invitation: [discussions/AI-Automated-Review-Invitation.md](discussions/AI-Automated-Review-Invitation.md)

---

*AGENTS.md version: 1.0 — 2026-04-10*
