# Downloading the Unitary Manifold Project

Three ways to get everything onto your PC, from easiest to most flexible.

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
   `unitary-manifold`, then click the green **Run workflow** button.
4. Wait ~30 seconds for the run to complete (green ✓).
5. Open the completed run and scroll down to **Artifacts**.
6. Click **unitary-manifold** to download the zip.
7. Extract it — the top-level folder is `unitary-manifold/`.

> **Tip:** The artifact is kept for **30 days**.  Re-run the workflow any time
> to get a fresh copy with the latest changes.

---

## Option 3 — Local script (best if you have Python installed)

Run this from inside the repository folder after cloning or extracting:

```bash
# Clone once (skip if you already have the folder)
git clone https://github.com/wuzbak/Unitary-Manifold-.git
cd Unitary-Manifold-

# Create the archive
python scripts/create_archive.py

# Optional: give the archive a custom base name
python scripts/create_archive.py --out my_unitary_manifold_backup
```

The script creates a `unitary-manifold_YYYYMMDD_HHMMSS.zip` file in the
repository root.  Extract it anywhere you like.

**Windows PowerShell:**
```powershell
Expand-Archive unitary-manifold_*.zip -DestinationPath .
```

**macOS / Linux:**
```bash
unzip unitary-manifold_*.zip
```

---

## What's inside the archive

```
unitary-manifold/
├── THEBOOKV9a (1).pdf              ← Full monograph (PDF)
├── README.md                       ← Project overview
├── CITATION.cff                    ← Citation metadata
├── requirements.txt                ← Python dependencies
│
├── arxiv/
│   ├── main.tex                    ← LaTeX source
│   ├── references.bib              ← Bibliography
│   └── SUBMISSION_GUIDE.md        ← arXiv upload walkthrough
│
├── manuscript/
│   └── ch02_mathematical_preliminaries.md
│
├── src/
│   ├── core/
│   │   ├── metric.py               ← Unitary metric tensor
│   │   └── evolution.py            ← Geometric / quantum evolution
│   ├── holography/
│   │   └── boundary.py             ← AdS/CFT boundary tools
│   └── multiverse/
│       └── fixed_point.py          ← Fixed-point / attractor analysis
│
├── discussions/
│   └── AI-Automated-Review-Invitation.md
│
├── zenodo/
│   ├── .zenodo.json
│   └── SUBMISSION_GUIDE.md        ← Zenodo DOI deposit guide
│
└── scripts/
    └── create_archive.py           ← Re-run to rebuild the archive
```

---

## Setting up Python code

```bash
pip install -r requirements.txt
python -c "from src.core import metric, evolution; print('Setup OK')"
```
