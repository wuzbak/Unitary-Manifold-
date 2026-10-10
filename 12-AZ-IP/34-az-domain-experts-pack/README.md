# AZ Domain Experts Pack — Product 34

**Folder:** `12-AZ-IP/34-az-domain-experts-pack/`
**Version:** 1.1.0
**TRL:** TRL-3 (retrieval over existing, already-tested source content)
**Status:** Active — Phase 0 of article-354's domain-experts roadmap, now a runnable web product

## What this is

Terra OS (Product 11) and Lithos OS (Product 12) both run the same
architecture — retrieval over domain content — aimed at different subject
matter. This product stands up the fourth and fifth siblings the article
names directly:

- `MATERIALS_EXPERT` — indexes `src/materials/` (polariton vortex, Froehlich
  polaron, metamaterials, condensed matter, semiconductors).
- `SPECTROSCOPY_EXPERT` — indexes `src/atomic_structure/` (orbitals,
  fine structure, spectroscopy).

Each `DomainExpert` builds a retrieval index from the module and
function/class docstrings already present in its source directory (via
`ast`, no new documentation is authored), and answers queries by keyword
overlap — the same reusable, cheap retrieval-and-serving scaffolding that
is the actual non-domain-specific part of the Terra/Lithos/PsiCat pattern.

## Epistemic status

Retrieval only; this product makes no new physics claim and asserts no new
documentation beyond what the indexed modules already say. A thin FastAPI
serving layer, following Terra/Lithos's own pattern, is a direct extension
of this index but is not part of this version — see `DomainExpert.query()`
for the API a server would wrap.

## Usage

```bash
python 12-AZ-IP/34-az-domain-experts-pack/run.py "polariton vortex critical angle"
```

```python
from az_domain_experts_pack import MATERIALS_EXPERT

MATERIALS_EXPERT.build()
MATERIALS_EXPERT.query("feature velocity critical angle")
```

## Running as a web product

The "thin FastAPI layer on top of the retrieval index" the retrieval module's own
docstring describes is implemented here with the stdlib (no FastAPI dependency is
installed in this environment), dispatching through `dispatch_api_request`
(covered by `tests/test_api.py`):

```bash
python 12-AZ-IP/34-az-domain-experts-pack/run.py serve --port 8134
# then open http://127.0.0.1:8134/
```

Endpoints: `GET /api/status`, `GET /api/experts`, `GET /api/query?expert=&question=&top_k=`.

## Tests

```bash
python -m pytest 12-AZ-IP/34-az-domain-experts-pack/tests -q
```

## Sources

- `src/materials/`, `src/atomic_structure/`
- `12-AZ-IP/11-terra-os`, `12-AZ-IP/12-lithos-os`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #7

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
