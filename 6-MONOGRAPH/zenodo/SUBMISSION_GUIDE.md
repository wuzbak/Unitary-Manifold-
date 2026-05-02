# Zenodo Submission Guide
## The Unitary Manifold v9.29 — Step-by-Step Upload Instructions

Zenodo gives you a permanent, citable DOI in minutes. Follow these steps exactly.

---

### Step 1 — Create / log in to your Zenodo account
1. Go to **https://zenodo.org** and click **Log in**.
2. You can authenticate with your **GitHub account** (recommended) or ORCID.

---

### Step 2 — Link the GitHub repository (optional but powerful)
If you authenticate with GitHub you can enable automatic DOI minting on every release:
1. Go to **https://zenodo.org/account/settings/github/**
2. Find `wuzbak/Unitary-Manifold-` and toggle it **ON**.
3. Now create a **GitHub Release** (tag `v9.29`) and Zenodo will automatically archive it and mint a DOI.

> **Shortcut:** If you do step 2, you can skip steps 3-6 below — Zenodo handles it automatically.

---

### Step 3 — Start a new upload
1. Click the **+** button (top-right) → **New upload**.
2. Or go directly to **https://zenodo.org/uploads/new**.

---

### Step 4 — Upload files
Drag and drop **all** of the following files (or a single `.zip`):

| File | What it is |
|------|-----------|
| `THEBOOKV9a (1).pdf` | Full monograph PDF — **primary file** |
| `arxiv/main.tex` | LaTeX source |
| `arxiv/references.bib` | Bibliography |
| `README.md` | Code overview |
| `requirements.txt` | Python dependencies |
| `src/` (zip the folder) | Numerical implementation |
| `CITATION.cff` | Citation metadata |

> Tip: zip the whole repo: `git archive --format=zip HEAD -o unitary-manifold-v9.29.zip`

---

### Step 5 — Fill in the metadata form

Copy-paste the values below into the Zenodo form:

**Upload type:** Publication → Preprint

**Title:**
```
The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility (Version 9.29)
```

**Authors:**
```
Walker-Pearson, ThomasCory
Affiliation: Independent Researcher, Pacific Northwest, USA
```

**Description** (paste verbatim):
```
We present the Unitary Manifold (UM), a five-dimensional Kaluza-Klein framework
in which thermodynamic irreversibility, information flow, and quantum transition
asymmetry are unified as projections of a single higher-dimensional geometry.
The fifth dimension is compact, the cylinder condition ∂₅G_AB = 0 is imposed,
and the 5D metric is cast in the standard Kaluza-Klein block form with a vector
field B_μ — the irreversibility 1-form — and a scalar φ — the entropic dilaton.
Dimensional reduction of the 5D Einstein-Hilbert action yields a 4D effective
action whose field equations (the Walker-Pearson equations) demonstrate that:
(i) the Second Law is a geometric identity; (ii) information pressure provides
a geometric alternative to dark energy; (iii) entropic holography identifies
boundary entropy with bulk area; and (iv) a Thermodynamic Cosmic Censorship
Conjecture holds. Numerical implementation is included for independent
verification. Version 9.0 — Academic Edition. Dedicated to the Defensive Public
Commons.
```

**Version:** `9.27`

**Language:** English

**Keywords** (one per line):
```
Kaluza-Klein theory
5D gravity
irreversibility
information geometry
holography
thermodynamics
dark energy
Generalized Second Law
Walker-Pearson equations
entropic holography
multiverse
quantum gravity
```

**License:** Choose **"Other (Open)"** and paste the Defensive Public Commons statement.

**Related/alternate identifiers:**
- `https://github.com/wuzbak/Unitary-Manifold-` → *is supplemented by* → Software
- `https://wuzbak.github.io/Unitary-Manifold-/` → *is described by* → Other

---

### Step 6 — Publish
1. Click **Save draft** and review everything.
2. Click **Publish** — this is **permanent and cannot be deleted**, only updated with a new version.
3. Copy your **DOI** (format: `10.5281/zenodo.XXXXXXX`).

---

### Step 7 — Add your DOI everywhere
After publishing, update these files with your DOI:

**In `CITATION.cff`**, add a line:
```yaml
doi: "10.5281/zenodo.XXXXXXX"
```

**In `README.md`**, add a badge at the top:
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

**In `arxiv/main.tex`**, add to acknowledgements:
```latex
This work is archived at \url{https://doi.org/10.5281/zenodo.XXXXXXX}.
```

---

### Step 8 — Cross-post to arXiv
Once you have the Zenodo DOI, see `arxiv/SUBMISSION_GUIDE.md` for arXiv submission
instructions. Cite the Zenodo DOI in your arXiv cover letter.

---

### Useful links
- Zenodo upload: https://zenodo.org/uploads/new
- Zenodo GitHub integration: https://zenodo.org/account/settings/github/
- ORCID (get a researcher ID): https://orcid.org/register
- Zenodo help: https://help.zenodo.org/
