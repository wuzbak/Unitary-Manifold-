# Post 325 (S04E028): By the Numbers — Reconciliation Audit (Corrected)

You were right to call this out. The prior draft undercounted books because it looked at `/7-OUTREACH/books` instead of the Substack books lane at `/7-OUTREACH/substack/books`.

This is the corrected reconciliation pass, with explicit counting rules.

## Counting rules used for this audit

All file counts are from tracked paths only (`git ls-files`) as of 2026-09-08.

- **Tracked entries** include regular files and symlinks.
- **Extension and line metrics below** are reported for **regular files** (symlinks excluded) to avoid duplicate counting through linked paths.
- **Line counts** are computed from decodable text files (UTF-8/Latin-1); binary/undecodable files are excluded from line totals.

## Reconciliation (what was wrong before)

- Prior draft books: **2** → Correct Substack books: **42** (`/7-OUTREACH/substack/books/book*.md`)
- Prior draft articles scope was narrow/inconsistent; corrected article count is the full Substack posts lane: **349** (`/7-OUTREACH/substack/posts/**/*.md`)

## Repository scale (corrected)

- **Tracked entries:** 6,887
- **Regular files:** 6,858
- **Symlinks:** 29
- **Text files counted for line totals:** 6,471
- **Binary/undecodable regular files:** 387
- **Total text lines:** 1,691,025
- **Total source-code lines (programming/source extensions):** 1,064,413

## Document and source-type totals (regular files)

- **Python (`.py`)**: 3,710 files
- **Markdown (`.md`)**: 1,462 files
- **Lean (`.lean`)**: 159 files
- **JSON (`.json`)**: 155 files
- **Kotlin (`.kt` + `.kts`)**: 175 files
- **YAML (`.yml` + `.yaml`)**: 62 files
- **HTML (`.html`)**: 72 files
- **XML (`.xml`)**: 27 files
- **CSS (`.css`)**: 11 files
- **Jupyter notebooks (`.ipynb`)**: 5 files
- **TeX (`.tex`)**: 2 files
- **BibTeX (`.bib`)**: 1 file
- **PDF (`.pdf`)**: 3 files
- **Text (`.txt`)**: 38 files

## Books, articles, applications, engines, OS, AI

- **Substack books:** 42 (`/7-OUTREACH/substack/books/book*.md`)
- **Substack posts/articles:** 349 (`/7-OUTREACH/substack/posts/**/*.md`)
- **Substack references:** 1 (`/7-OUTREACH/substack/references/**/*.md`)
- **Substack markdown total (books + posts + references):** 392

- **Applications/products:** 23 (`/12-AZ-IP/NN-*` directories)
- **Engine directories under 12-AZ-IP:** 22
- **Engine directories across repo (all paths named `engine`):** 23

- **OS product directories:** 5 (`01-axiom-os`, `02-az-kernel`, `05-uos-kernel`, `11-terra-os`, `12-lithos-os`)
- **OS root codebase directories:** 4 (`11-AZ-OS`, `az-os`, `az_os`, `12-AZ-IP/os`)

- **Explicit AI units tracked in this audit:** 8
  (`bot`, `9-INFRASTRUCTURE/bot`, `12-AZ-IP/08-axiom-journalist`, `12-AZ-IP/16-oracle`, `12-AZ-IP/20-psicat-navigator`, `12-AZ-IP/23-psicat-dm-assistant`, `az-os/agents`, `az_os/agents`)

## Pillars and verification status

From `/9-INFRASTRUCTURE/um_live_status.json`:

- **Hardgate pillars:** 208
- **Total pillar slots used:** 1,087
- **Next pillar slot:** 1,088
- **Latest full regression headline:** 64,138 passed · 22 skipped · 18 deselected · 0 failed
- **Lean4 theorem count (declared):** 4,080

## Languages used (programming lanes)

Programming languages with tracked source presence in this repository:

- Python, Kotlin, Lean4, JavaScript, TypeScript, Rust, C/C++, Shell, Batch, Java

**Total programming-language families in active source files:** 10

Top language/source line totals:

- Python: 982,759
- Kotlin: 35,336
- Lean4: 18,454
- JavaScript: 12,090
- C/C++: 10,081
- Rust: 2,221

## Bottom line

The corrected numbers show a large multi-lane body of work: a million-plus lines of source and document text, a substantial Substack publication archive (including 42 books), a 23-product application stack, and an active 1,087-slot pillar ledger with explicit open-lane tracking.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
