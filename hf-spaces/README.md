# AxiomZero HF Spaces — Complete Webspace

**Status source:** `https://raw.githubusercontent.com/wuzbak/Unitary-Manifold-/main/9-INFRASTRUCTURE/um_live_status.json` (canonical live metrics for version/tests/Lean4/pillars)

Full Hugging Face deployment surfaces for the [axiomzerospc.org](https://axiomzerospc.org) webspace.
Canonical AZ product count is 23; HF spaces currently host Products 01–20 directly, while Products 21–23 are linked via the public AZ app hub / repository.

## Spaces

| Space | SDK | Products | Description |
|-------|-----|----------|-------------|
| `az-portal/` | Static HTML | Hub | Full portal hub — links to all spaces, physics constants, live status |
| `oracle-space/` | Gradio | 16, 20 (Merlin/OX-compatible) | Grand Synthesis Engine + Merlin compatibility AI |
| `cmb-calc-space/` | Gradio | CMB, Birefringence, KK, DESI | Physics calculators — 5 tabs |
| `axiom-apps/` | Gradio | 01–10 | AxiomOS, EIGE, UM-SOS, Omega Synthesis, Holon Zero, Journalist, OmegaHolon, Filmer |
| `az-tools/` | Gradio | 11–20 | Terra-OS, Lithos-OS, DelPhi, SDAM, Pentacorder, Oracle, + legacy utility trio (Falsification Obs, Interrogator, Flashcard) and Merlin/OX-compatible navigator |
| `vqe-sandbox/` | Gradio | Quantum | VQE + Fermi-Hubbard simulation — JW encoding + KK φ-weighted ansatz |
| `az-os/` | Gradio | 01, 11, 12 | AxiomOS + Terra-OS + Lithos-OS unified OS environment |
| `az-ip/` | Gradio | IP Catalog | IP registry browser (legacy in-space snapshot + canonical links to current 23-product registry) |
| `um-knowledge-dataset/` | Dataset | RAG | pillars.jsonl, theorems.jsonl, claims.jsonl, fallibility.jsonl, apps.jsonl, docs.jsonl |

## Deploy to Hugging Face

Each space deploys independently. Push the contents of each subfolder to the corresponding HF Space.

### Organization: `axiomzero`

```bash
# Clone each space repo, copy contents, push
# Example for oracle-space:
git clone https://huggingface.co/spaces/axiomzero/oracle-space /tmp/oracle-space
cp hf-spaces/oracle-space/* /tmp/oracle-space/
cd /tmp/oracle-space && git add -A && git commit -m "Deploy from canonical status feed" && git push

# For the dataset:
git clone https://huggingface.co/datasets/axiomzero/um-knowledge-dataset /tmp/um-knowledge-dataset
cp hf-spaces/um-knowledge-dataset/* /tmp/um-knowledge-dataset/
cd /tmp/um-knowledge-dataset && git add -A && git commit -m "Add JSONL data files" && git push
```

## Environment Variables

| Space | Variable | Purpose |
|-------|----------|---------|
| oracle-space | `OPENROUTER_API_KEY` | Optional compatibility path for Merlin/OX model routing |
| axiom-apps | `OPENROUTER_API_KEY` | AxiomOS + Journalist AI |
| az-tools | `OPENROUTER_API_KEY` | Optional compatibility path for Product 20 Merlin/OX routing |
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
├── space_core/                  ← shared runtime contract utilities
│   ├── __init__.py
│   └── live_status.py           ← canonical status loader (um_live_status.json)
└── um-knowledge-dataset/        ← RAG Knowledge Base Dataset
    ├── README.md
    ├── pillars.jsonl            ← 13 pillar records
    ├── theorems.jsonl           ← 5 theorem records
    ├── fallibility.jsonl        ← 4 open gap records
    ├── claims.jsonl             ← 5 claim records
    ├── apps.jsonl               ← 6 app records
    └── docs.jsonl               ← 5 doc records
```

## Runtime contract

- Shared status loader for spaces: `hf-spaces/space_core/live_status.py`
- Canonical live metrics feed: `9-INFRASTRUCTURE/um_live_status.json`
- Drift enforcement gate: `9-INFRASTRUCTURE/check_status_drift.py`
- Nightly endpoint canary: `.github/workflows/hf-spaces-canary.yml`

## Coverage notes

- Canonical product registry and naming authority: `12-AZ-IP/README.md` (Products 01–23).
- HF spaces provide direct hosted coverage for Products 01–20 plus portal/dataset surfaces.
- Products 21 (UM Geophysical Monitor), 22 (AxiomZero SGE), and 23 (Merlin DM Guide & Player Assistant) are linked through:
  - `public-site/az-apps/index.html`
  - `docs/APPS_SPACES_FINALIZATION_MATRIX.md`
  - product folders under `12-AZ-IP/21-geo-monitor/`, `12-AZ-IP/22-az-sge/`, `12-AZ-IP/23-merlin-dm-assistant/`

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
