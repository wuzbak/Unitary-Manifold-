# Downloading the Unitary Manifold Project (v9.29)

Three ways to get everything onto your PC, from easiest to most flexible.

---

## Option 0 — Direct download link (one click, always current)

| Format | URL |
|--------|-----|
| **ZIP** | https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.zip |
| **Tarball** | https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.tar.gz |

These URLs are permanent and always deliver the latest state of the `main`
branch — no account, no login, no extra steps required.  Just click (or
`curl`/`wget`) and extract.

```bash
# Download and extract in one go (Linux / macOS / WSL)
curl -L https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.zip \
     -o unitary-manifold-omega-v9.29.zip
unzip unitary-manifold-omega-v9.29.zip
```

---

## Option 1 — GitHub "Download ZIP" button (simplest, no account needed)

1. Go to the repository home page on GitHub.
2. Click the green **`< > Code`** button near the top-right.
3. Choose **Download ZIP**.
4. Extract the downloaded file; you'll find a single folder with everything inside.

---

## Option 2 — GitHub Actions (one-click, well-organised archive)

This produces a cleanly labelled zip with a table-of-contents comment and
excludes cache files, making it ideal for archiving.

1. Go to the **Actions** tab of this repository on GitHub.
2. In the left-hand sidebar click **Build Download Archive**.
3. Click **Run workflow** (top-right of the workflow list), leave the name as
   `unitary-manifold-omega-v9.29`, then click the green **Run workflow** button.
4. Wait ~30 seconds for the run to complete (green ✓).
5. Open the completed run and scroll down to **Artifacts**.
6. Click **unitary-manifold-omega-v9.29** to download the zip.
7. Extract it — the top-level folder is `unitary-manifold-omega-v9.29/`.

> **Tip:** The artifact is kept for **30 days**.  Re-run the workflow any time
> to get a fresh copy with the latest changes.

---

## Option 3 — Local script (best if you have Python installed)

Run this from inside the repository folder after cloning or extracting:

```bash
# Clone once (skip if you already have the folder)
git clone https://github.com/wuzbak/Unitary-Manifold-.git
cd Unitary-Manifold-

# Create the archive (default name includes "omega-v9.29")
python scripts/create_archive.py

# Optional: give the archive a custom base name
python scripts/create_archive.py --out my_unitary_manifold_backup
```

The script creates a `unitary-manifold-omega-v9.29_YYYYMMDD_HHMMSS.zip` file in the
repository root.  Extract it anywhere you like.

**Windows PowerShell:**
```powershell
Expand-Archive unitary-manifold-omega-v9.29_*.zip -DestinationPath .
```

**macOS / Linux:**
```bash
unzip unitary-manifold-omega-v9.29_*.zip
```

---

## What's inside the archive

```
unitary-manifold-omega-v9.29/
├── THEBOOKV9a (1).pdf              ← Full monograph (PDF)
├── README.md                       ← Project overview and quick-start (v9.29)
├── CITATION.cff                    ← Citation metadata
├── requirements.txt                ← Python dependencies
├── VERIFY.py                       ← 30-second standalone proof (14 checks, all PASS)
│
├── src/
│   ├── core/                       ← 50+ modules: KK metric, evolution, braided winding,
│   │   │                              APS topology, Yukawa, CKM/PMNS, SM audit, …
│   │   ├── metric.py               ← Unitary metric tensor (Pillar 1)
│   │   ├── evolution.py            ← Walker-Pearson integrator (Pillar 2)
│   │   └── [48 further modules]    ← Pillars 27–98
│   ├── holography/
│   │   └── boundary.py             ← AdS/CFT boundary + entropy-area (Pillar 3–4)
│   └── multiverse/
│       └── fixed_point.py          ← FTUM fixed-point iteration (Pillar 5)
│
├── omega/                          ← Pillar Ω — Universal Mechanics Engine
│   ├── omega_synthesis.py          ← UniversalEngine: 5 seeds → all observables
│   ├── test_omega_synthesis.py     ← 170 tests
│   ├── README.md                   ← Architecture and API guide
│   └── CALCULATOR.md               ← Complete API reference
│
├── recycling/                      ← Pillar 16 — φ-debt entropy accounting (316 tests)
│
├── Unitary Pentad/                 ← HILS governance framework — 18 modules (1,266 tests)
│
├── tests/                          ← 150+ test files, ~15,926 passing tests (Pillars 1–132)
│
├── embryology-manifold/            ← Pillar TVC: egg radius, zinc count, HOX predictions
│
├── systems-engineering/            ← Stability framework for engineers across 14 domains
│   ├── README.md
│   ├── AUDIENCE_GUIDE.md
│   ├── MANIFOLD_SYSTEM_STABILITY.md
│   ├── CURRENT_SYSTEMS_FAILURE_ANALYSIS.md
│   ├── FIRMWARE_FIXES.md
│   ├── FUTURE_SOFTWARE_HARDWARE.md
│   ├── UPGRADE_ROADMAP.md
│   └── QUICK_REFERENCE.md
│
├── arxiv/
│   ├── main.tex                    ← LaTeX source
│   ├── references.bib              ← Bibliography
│   └── SUBMISSION_GUIDE.md        ← arXiv upload walkthrough
│
├── manuscript/
│   └── ch02_mathematical_preliminaries.md
│
├── notebooks/
│   ├── 01_quickstart.ipynb         ← Field evolution demo
│   ├── 02_holographic_boundary.ipynb
│   └── 03_multiverse_fixed_point.ipynb
│
├── discussions/
│   └── AI-Automated-Review-Invitation.md
│
├── zenodo/
│   ├── .zenodo.json
│   └── SUBMISSION_GUIDE.md        ← Zenodo DOI deposit guide
│
└── scripts/
    ├── create_archive.py           ← Re-run to rebuild this archive
    ├── run_evolution.py            ← Field evolution demo
    ├── run_metric.py               ← Metric and curvature demo
    ├── run_boundary.py             ← Holographic boundary demo
    ├── run_fixed_point.py          ← FTUM convergence demo
    ├── run_inflation.py            ← CMB spectral index demo
    └── live_report.py              ← Real-world comparison report
```

---

## Setting up Python code

```bash
pip install -r requirements.txt
python -c "from src.core import metric, evolution; print('Setup OK')"
```
