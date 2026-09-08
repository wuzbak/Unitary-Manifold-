# Post 325 (S04E028): By the Numbers — Quantifying the Repository So Far

This is the accounting pass we should have published earlier: one snapshot, one ledger, no hand-waving.

As of 2026-09-08, using tracked files in this repository (`git ls-files`) and line counts from decodable text files:

## 1) Global size

- **Tracked files:** 6,886
- **Text files counted for line totals:** 6,482
- **Total text lines:** 1,693,488
- **Code files (major code extensions + Makefile):** 4,158
- **Total code lines:** **1,066,360**

## 2) Document/file-type totals

File counts by type:

- **Markdown (`.md`):** 1,463 files
- **Python (`.py`):** 3,716 files
- **PDF (`.pdf`):** 3 files
- **JSON (`.json`):** 155 files
- **YAML (`.yml` + `.yaml`):** 63 files
- **XML (`.xml`):** 27 files
- **HTML (`.html`):** 72 files
- **CSS (`.css`):** 11 files
- **Notebooks (`.ipynb`):** 5 files
- **TeX (`.tex`):** 2 files
- **BibTeX (`.bib`):** 1 file
- **Text (`.txt`):** 39 files

(Reference scale: Markdown alone contributes **225,864** lines.)

## 3) Books, articles, applications, engines, OS, AI

Using explicit in-repo paths and naming:

- **Books:** **2** (`/7-OUTREACH/books/*.md`)
- **Articles:** **348** (`/7-OUTREACH/substack/posts/**/*.md`)
- **Applications:** **23** product directories (`/12-AZ-IP/NN-*`)
- **Engines:** **23** directories named `engine`
- **OS units:** **8** (base OS directories + OS product directories)
- **AI units:** **8** explicitly AI-focused infrastructure/product paths

## 4) What this tells us

The repository is no longer a small theory codebase. It is a large multi-lane system with over a million lines of code, a substantial publication track, and a product/engine/OS/AI stack that now needs ongoing metric discipline.

From here on, this type of inventory should be updated on cadence rather than reconstructed late.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
