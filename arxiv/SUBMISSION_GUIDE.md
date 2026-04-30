# arXiv Submission Guide
## The Unitary Manifold v9.27 OMEGA EDITION — Step-by-Step Instructions

---

### Required arXiv categories
- **Primary:** `gr-qc` (General Relativity and Quantum Cosmology)
- **Cross-list:** `hep-th` (High Energy Physics – Theory), `math-ph` (Mathematical Physics)

---

### Step 1 — Get an arXiv account
1. Go to **https://arxiv.org/user/register** and register with your email.
2. arXiv requires an **endorsement** for first-time submitters in `gr-qc`.
   - Ask a colleague who has published in `gr-qc` to endorse you, **or**
   - Use the endorsement request form: https://arxiv.org/auth/endorse

> **Tip:** You may submit to `physics.gen-ph` (General Physics) without endorsement,
> but `gr-qc` is the correct primary category and gives maximum visibility.

---

### Step 2 — Prepare your files
Run the following in the `arxiv/` folder to verify the LaTeX compiles:

```bash
cd arxiv/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex   # run twice for cross-references
```

arXiv requires these files in a **single `.tar.gz` or `.zip`**:

```
main.tex
references.bib
```

> Do NOT include the compiled `.pdf` — arXiv compiles it automatically.
> Do NOT include `.aux`, `.log`, or `.bbl` files (they are generated during compilation).

Create the archive:
```bash
cd arxiv/
tar -czf unitary-manifold-arxiv.tar.gz main.tex references.bib
```

---

### Step 3 — Submission metadata

**Title:**
```
The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility
```

**Authors:**
```
ThomasCory Walker-Pearson
```

**Abstract** (paste verbatim — keep under 1920 characters):
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
A Thermodynamic Multiverse topology and a Final Theorem unifying
irreversibility, holography, and topology are also developed. Numerical
code for independent verification is available at
https://github.com/wuzbak/Unitary-Manifold-
```

**Comments field:**
```
72 pages, 0 figures. Numerical implementation at
https://github.com/wuzbak/Unitary-Manifold-
Dedicated to the Defensive Public Commons.
Zenodo DOI: 10.5281/zenodo.XXXXXXX
```
*(Replace XXXXXXX with your actual Zenodo DOI)*

**MSC classes (optional but helpful):**
```
83E15, 83C45, 94A17, 82C99
```

**ACM classes (optional):**
```
J.2
```

---

### Step 4 — Submit
1. Go to **https://arxiv.org/submit** and click **Start New Submission**.
2. Choose primary archive: **Physics** → **gr-qc**.
3. Upload your `unitary-manifold-arxiv.tar.gz`.
4. Fill in the metadata from Step 3.
5. Check the preview PDF carefully — especially that all equations render.
6. Click **Submit**.

arXiv moderates new submissions; your paper will appear within **1–2 business days**.

---

### Step 5 — After acceptance
Your paper will have an ID like `arXiv:2604.XXXXX`.

1. Add this to `README.md`:
   ```markdown
   [![arXiv](https://img.shields.io/badge/arXiv-2604.XXXXX-b31b1b.svg)](https://arxiv.org/abs/2604.XXXXX)
   ```
2. Add it to `CITATION.cff`:
   ```yaml
   identifiers:
     - type: url
       value: "https://arxiv.org/abs/2604.XXXXX"
   ```
3. Share the link on:
   - [Physics Stack Exchange](https://physics.stackexchange.com) (create a question or answer)
   - [r/Physics](https://reddit.com/r/Physics) and [r/math](https://reddit.com/r/math)
   - [ResearchGate](https://www.researchgate.net) — import from arXiv automatically

---

### Useful links
- arXiv submission: https://arxiv.org/submit
- arXiv endorsement: https://arxiv.org/auth/endorse
- arXiv `gr-qc` category: https://arxiv.org/list/gr-qc/recent
- LaTeX guide for arXiv: https://arxiv.org/help/submit_tex
