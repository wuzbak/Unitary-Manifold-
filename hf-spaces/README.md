# AxiomZero HF Spaces — Complete Webspace

**Status:** v24.1 · 57,927 passing tests · 1,246 Lean4 theorems · 208 hardgate pillars

Full Hugging Face deployment of the [axiomzerospc.org](https://axiomzerospc.org) webspace.
ALL apps, OS environments, physics engines, IP catalog, and knowledge base — fully functional.

## Spaces

| Space | SDK | Products | Description |
|-------|-----|----------|-------------|
| `az-portal/` | Static HTML | Hub | Full portal hub — links to all spaces, physics constants, live status |
| `oracle-space/` | Gradio | 16, 20 (OX Alpha) | Grand Synthesis Engine + OX Alpha AI |
| `cmb-calc-space/` | Gradio | CMB, Birefringence, KK, DESI | Physics calculators — 5 tabs |
| `axiom-apps/` | Gradio | 01–10 | AxiomOS, EIGE, UM-SOS, Omega Synthesis, Holon Zero, Journalist, OmegaHolon, Filmer |
| `az-tools/` | Gradio | 11–20 | Terra-OS, Lithos-OS, DelPhi, SDAM, Pentacorder, Oracle, Falsification-Obs, Interrogator, Flashcard, OX Navigator |
| `vqe-sandbox/` | Gradio | Quantum | VQE + Fermi-Hubbard simulation — JW encoding + KK φ-weighted ansatz |
| `az-os/` | Gradio | 01, 11, 12 | AxiomOS + Terra-OS + Lithos-OS unified OS environment |
| `az-ip/` | Gradio | IP Catalog | Full IP registry — 20 products, engines, OS, tools, fingerprint browser |
| `um-knowledge-dataset/` | Dataset | RAG | pillars.jsonl, theorems.jsonl, claims.jsonl, fallibility.jsonl, apps.jsonl, docs.jsonl |

## Deploy to Hugging Face

Each space deploys independently. Push the contents of each subfolder to the corresponding HF Space.

### Organization: `axiomzero`

```bash
# Clone each space repo, copy contents, push
# Example for oracle-space:
git clone https://huggingface.co/spaces/axiomzero/oracle-space /tmp/oracle-space
cp hf-spaces/oracle-space/* /tmp/oracle-space/
cd /tmp/oracle-space && git add -A && git commit -m "Deploy v24.1" && git push

# For the dataset:
git clone https://huggingface.co/datasets/axiomzero/um-knowledge-dataset /tmp/um-knowledge-dataset
cp hf-spaces/um-knowledge-dataset/* /tmp/um-knowledge-dataset/
cd /tmp/um-knowledge-dataset && git add -A && git commit -m "Add JSONL data files" && git push
```

## Environment Variables

| Space | Variable | Purpose |
|-------|----------|---------|
| oracle-space | `OPENROUTER_API_KEY` | OX Alpha (stealth/ox-alpha) — extended memory AI |
| axiom-apps | `OPENROUTER_API_KEY` | AxiomOS + Journalist AI |
| az-tools | `OPENROUTER_API_KEY` | OX Navigator (Product 20) |
| az-os | `OPENROUTER_API_KEY` | AxiomOS cognitive queries |

Set via HF Space Settings → Variables and Secrets. Never commit API keys.

## Architecture

```
hf-spaces/
├── README.md                    ← This file (deployment guide)
├── az-portal/                   ← Static HTML portal hub
│   ├── README.md                ← HF Space metadata (sdk: static)
│   └── index.html               ← Full portal — 535 lines
├── oracle-space/                ← Grand Synthesis Engine (Product 16)
│   ├── README.md                ← HF Space metadata
│   ├── app.py                   ← Gradio app — OX Alpha + all physics tabs
│   └── requirements.txt
├── cmb-calc-space/              ← CMB Calculator (5 tabs)
│   ├── README.md
│   ├── app.py                   ← CMB + Birefringence + KK Mass + DESI + Report
│   └── requirements.txt
├── axiom-apps/                  ← Products 01–10
│   ├── README.md
│   ├── app.py                   ← 839 lines, 10 products
│   └── requirements.txt
├── az-tools/                    ← Products 11–20
│   ├── README.md
│   ├── app.py                   ← 904 lines, 10 products
│   └── requirements.txt
├── vqe-sandbox/                 ← Quantum VQE + Fermi-Hubbard
│   ├── README.md
│   ├── app.py                   ← JW encoding, KK φ-ansatz, BK info, XDiag bridge
│   └── requirements.txt
├── az-os/                       ← AxiomOS + Terra-OS + Lithos-OS
│   ├── README.md
│   ├── app.py                   ← 432 lines, unified OS
│   └── requirements.txt
├── az-ip/                       ← IP Registry & Catalog
│   ├── README.md
│   ├── app.py                   ← 539 lines, full catalog
│   └── requirements.txt
└── um-knowledge-dataset/        ← RAG Knowledge Base Dataset
    ├── README.md
    ├── pillars.jsonl            ← 13 pillar records
    ├── theorems.jsonl           ← 5 theorem records
    ├── fallibility.jsonl        ← 4 open gap records
    ├── claims.jsonl             ← 5 claim records
    ├── apps.jsonl               ← 6 app records
    └── docs.jsonl               ← 5 doc records
```

## Epistemic Notes

- All outputs carry gate labels: `HARDGATE`, `ADJACENT_TRACK`, `OPEN_GAP`, `GOVERNANCE`
- No "ToE score" or "100% hardgate" language — plain epistemic status only
- Open gaps are documented and displayed, never hidden
- Primary falsifier: β ∈ {≈0.273°, ≈0.331°} — LiteBIRD ~2032
- DESI tension (w_a≠0) is an acknowledged open gap

## License

Defensive Public Commons License v1.0 (2026) — public domain.
No patents on core equations. All content freely available.

*Theory: ThomasCory Walker-Pearson · Code: GitHub Copilot (AI)*  
*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876*
