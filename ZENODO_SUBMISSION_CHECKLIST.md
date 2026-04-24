# Zenodo & arXiv Submission Checklist — v9.13

> **Role split:** Copilot (me) has already updated all metadata files and staged everything.
> The steps below are **yours** — things only a human with an account can do.

---

## ✅ Already done by Copilot

- [x] `zenodo/.zenodo.json` — updated to v9.13, ~9700 tests, 57 pillars, expanded keywords
- [x] `CITATION.cff` — updated to v1.0.0, date 2026-04-24
- [x] `arxiv/main.tex` — header updated to v9.13
- [x] `arxiv/build_submission.sh` — helper script to compile LaTeX and create upload archive
- [x] This checklist
- [x] New pillars added: 56 (φ₀ self-consistency), 57 (CMB acoustic peak resolution), 45-D (LiteBIRD forecast), 51-B (Fermilab g-2 watch)

---

## PART A — Zenodo (get a permanent DOI)

**What you need:** A free Zenodo account at https://zenodo.org

### Step A-1 — Create / log in to your Zenodo account
- Go to **https://zenodo.org** → click **Log in** (or **Sign up** if new)
- You can authenticate with GitHub — easiest option

### Step A-2 — Start a new upload
- Click **+** → **New Upload** (top nav bar)

### Step A-3 — Upload files
Upload ALL of the following (drag-and-drop or click Upload):

| File | Where it lives in the repo |
|------|---------------------------|
| `THEBOOKV9a (1).pdf` | repo root |
| `README.md` | repo root |
| `UNIFICATION_PROOF.md` | repo root |
| `QUANTUM_THEOREMS.md` | repo root |
| `submission/falsification_report.md` | submission/ |
| `submission/one_page_summary.md` | submission/ |

> You can also upload a ZIP of the entire repo if you want the full source attached.
> Get it from: https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.zip

### Step A-4 — Fill in the metadata form

Zenodo will use `.zenodo.json` automatically **if you link the GitHub repo** (see Step A-5).
If filling manually, use these exact values:

| Field | Value |
|-------|-------|
| **Upload type** | Publication |
| **Publication type** | Preprint |
| **Title** | The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility (Version 9.11) |
| **Authors** | Walker-Pearson, ThomasCory — Independent Researcher, Pacific Northwest, USA |
| **Version** | 9.11 |
| **License** | Other (Open) |
| **Access** | Open Access |
| **Keywords** | Kaluza-Klein theory, 5D gravity, irreversibility, information geometry, holography, Walker-Pearson equations, entropic cosmology, quantum gravity, cold fusion, neuroscience, ecology, climate science, psychology, genetics, materials science |

Paste the description from `zenodo/.zenodo.json` (the `description` field) into the Abstract box.

### Step A-5 — Link GitHub (recommended — auto-uses .zenodo.json)
- Go to **https://zenodo.org/account/settings/github/**
- Find `wuzbak/Unitary-Manifold-` and flip the toggle **ON**
- Then create a **GitHub Release** on the main branch — Zenodo will auto-archive it and assign a DOI

### Step A-6 — Publish
- Click **Save** → **Publish**
- **Copy your DOI** — it looks like `10.5281/zenodo.XXXXXXX`

---

## PART B — arXiv submission

**What you need:** An arXiv account + endorsement in `gr-qc` (or submit to `physics.gen-ph` without endorsement)

### Step B-1 — Build the upload archive
On your local machine (with LaTeX installed):
```bash
git clone https://github.com/wuzbak/Unitary-Manifold-
cd Unitary-Manifold-
bash arxiv/build_submission.sh
# → creates arxiv/unitary-manifold-arxiv.tar.gz
```

### Step B-2 — Go to arXiv
- https://arxiv.org/submit → **Start New Submission**
- Primary archive: **Physics → gr-qc**
- Upload: `arxiv/unitary-manifold-arxiv.tar.gz`

### Step B-3 — Fill in arXiv metadata

**Title:**
```
The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility
```

**Authors:**
```
ThomasCory Walker-Pearson
```

**Abstract** (paste exactly):
```
We present the Unitary Manifold (UM), a five-dimensional Kaluza-Klein
framework in which thermodynamic irreversibility, information flow, and
quantum transition asymmetry are unified as projections of a single
higher-dimensional geometry. The fifth dimension is compact, the cylinder
condition is imposed, and the 5D metric is cast in the standard
Kaluza-Klein block form with a vector field B_mu (the irreversibility
1-form) and a scalar phi (the entropic dilaton). Dimensional reduction of
the 5D Einstein-Hilbert action yields a 4D effective action whose field
equations — the Walker-Pearson equations — demonstrate: (i) the Second
Law of Thermodynamics is a geometric identity rather than a statistical
postulate; (ii) information pressure provides a geometric alternative to
dark energy; (iii) entropic holography identifies boundary entropy with
bulk area; and (iv) a Thermodynamic Cosmic Censorship Conjecture holds.
Version 9.14 extends the framework to 26+ physical pillars (atomic
structure, cold fusion, medicine, justice, governance, neuroscience,
ecology, climate, marine biology, psychology, genetics, materials science,
observational frontiers, solitonic charge, AdS/CFT KK tower, delay field,
three generations, collider resonances, geometric collapse, coupled history)
with 8906 passing tests. Numerical code for independent verification at
https://github.com/wuzbak/Unitary-Manifold-
```

**Comments field:**
```
72 pages, 0 figures. Numerical implementation (7646 tests) at
https://github.com/wuzbak/Unitary-Manifold-
Zenodo DOI: 10.5281/zenodo.XXXXXXX
Dedicated to the Defensive Public Commons.
```
*(Replace XXXXXXX with your actual Zenodo DOI from Part A)*

**MSC classes:**
```
83E15, 83C45, 94A17, 82C99
```

### Step B-4 — Submit
- Preview the PDF → check equations render correctly
- Click **Submit** — paper appears in 1–2 business days

---

## PART C — After both are live

Once you have your arXiv ID (e.g. `arXiv:2604.XXXXX`):

1. Add the arXiv badge to `README.md`:
   ```markdown
   [![arXiv](https://img.shields.io/badge/arXiv-2604.XXXXX-b31b1b.svg)](https://arxiv.org/abs/2604.XXXXX)
   ```
2. Add to `CITATION.cff`:
   ```yaml
   identifiers:
     - type: url
       value: "https://arxiv.org/abs/2604.XXXXX"
     - type: doi
       value: "10.5281/zenodo.XXXXXXX"
   ```
3. Tell me the arXiv ID and Zenodo DOI — I'll update all the metadata files in one shot.

---

## Quick-reference URLs

| Destination | URL |
|-------------|-----|
| Zenodo upload | https://zenodo.org/uploads/new |
| Zenodo GitHub integration | https://zenodo.org/account/settings/github/ |
| arXiv submit | https://arxiv.org/submit |
| arXiv gr-qc | https://arxiv.org/list/gr-qc/recent |
| Repo ZIP download | https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.zip |
