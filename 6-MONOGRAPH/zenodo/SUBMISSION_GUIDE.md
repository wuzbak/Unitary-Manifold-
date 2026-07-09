# Zenodo Submission Guide
## The Unitary Manifold v18.4 — Step-by-Step Upload Instructions

Zenodo gives you a permanent, citable DOI in minutes. Follow these steps exactly.

> **DOI already minted:** `10.5281/zenodo.19584531`  
> Use these instructions to deposit a **new version** of the existing record.

---

### Step 1 — Create / log in to your Zenodo account
1. Go to **https://zenodo.org** and click **Log in**.
2. You can authenticate with your **GitHub account** (recommended) or ORCID.

---

### Step 2 — Link the GitHub repository (optional but powerful)
If you authenticate with GitHub you can enable automatic DOI minting on every release:
1. Go to **https://zenodo.org/account/settings/github/**
2. Find `wuzbak/Unitary-Manifold-` and toggle it **ON**.
3. Now create a **GitHub Release** (tag `v18.4`) and Zenodo will automatically archive it and mint a new version DOI.

> **Shortcut:** If you do step 2, you can skip steps 3-6 below — Zenodo handles it automatically.

---

### Step 3 — Start a new upload (or new version)
To deposit as a **new version** of the existing record:
1. Go to **https://zenodo.org/record/19584531** and click **New version**.
2. Or for a fresh upload: click the **+** button (top-right) → **New upload** at https://zenodo.org/uploads/new.

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

> Tip: zip the whole repo: `git archive --format=zip HEAD -o unitary-manifold-v18.4.zip`

---

### Step 5 — Fill in the metadata form

Copy-paste the values below into the Zenodo form:

**Upload type:** Publication → Preprint

**Title:**
```
The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility (v18.4)
```

**Authors:**
```
Walker-Pearson, ThomasCory
Affiliation: AxiomZero Technologies & Consulting, SPC — Duvall, WA, USA (Chief Purpose Officer)
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
Conjecture holds. The framework derives 28.0/28 Standard Model and cosmological
observables without free parameters. Primary falsifier: CMB polarisation
birefringence angle β ∈ {0.273°, 0.331°} ± 0.01° (LiteBIRD ~2032).

v18.4 (2026-07-09): 208 hardgated core pillars + 540+ total pillars + Ω₀ Holon
Zero. 47,171 tests passing. Pillar 537: Shadow-Pair Parent Derivation — K_CS=74
and c_s=12/37 derived from pre-Z₂-projection parent integer n_before=6 without
observational input. Pillar 538: Enteric Neural Core — 5D KK structural mapping
of the Enteric Nervous System. Pillar 540: Full Dimensional Synthesis — terminal
6D→11D synthesis certificate with seven new computations across all dimensional
modules. v18.0 JUNO Phase 1 Response: all JUNO Phase 1 observables consistent,
Vol(CY₃)=6.28 M_Pl⁶ fixed unconditionally, p_R derived unconditionally, CMB A_s
architecture limit confirmed, tensor r^{NLO}=0.0312 architecture limit confirmed,
WdW radion stable. Adjacent research tracks (Pillars 218–540+) extend the
geometric machinery to quantum computing, energy systems, biomedical applications,
and AI/robotics — honest quantitative explorations, not hardgated physics claims.
Infrastructure: JAX-accelerated evolution, Lean4 formal proofs, Z3 SMT bounds
verification, XDiag quantum many-body bridge, AxiomZero OS cognitive layer.
Dedicated to the Defensive Public Commons.
```

**Version:** `18.4`

**Language:** English

**Keywords** (one per line):
```
Kaluza-Klein theory
5D gravity
irreversibility
information geometry
holography
thermodynamics
Walker-Pearson equations
entropic cosmology
entropic holography
multiverse
quantum gravity
braided winding
CMB birefringence
Standard Model parameters
omega synthesis
universal mechanics engine
Fermi-Hubbard
XDiag
JAX
Lean4
adjacent research tracks
AxiomZero OS
```

**License:** Choose **"Other (Open)"** and paste the Defensive Public Commons statement.

**Related/alternate identifiers:**
- `https://github.com/wuzbak/Unitary-Manifold-` → *is supplemented by* → Software
- `https://wuzbak.github.io/Unitary-Manifold-/` → *is described by* → Other

---

### Step 6 — Publish
1. Click **Save draft** and review everything.
2. Click **Publish** — this is **permanent and cannot be deleted**, only updated with a new version.
3. The existing DOI (`10.5281/zenodo.19584531`) resolves to the latest version automatically.

---

### Step 7 — DOI is already everywhere
The DOI `10.5281/zenodo.19584531` is already present in:
- `CITATION.cff`
- `README.md` (badge)
- `9-INFRASTRUCTURE/schema.jsonld`
- `arxiv/main.tex` (acknowledgements)

No further updates needed after publishing the new version.

---

### Step 8 — Cross-post to arXiv
Once you have confirmed the new Zenodo version is live, see `arxiv/SUBMISSION_GUIDE.md` for arXiv
submission instructions. Cite the Zenodo DOI in your arXiv cover letter.

---

### Useful links
- Zenodo record: https://zenodo.org/record/19584531
- Zenodo upload: https://zenodo.org/uploads/new
- Zenodo GitHub integration: https://zenodo.org/account/settings/github/
- ORCID (get a researcher ID): https://orcid.org/register
- Zenodo help: https://help.zenodo.org/
