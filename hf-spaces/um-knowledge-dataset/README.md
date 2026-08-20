---
license: other
license_name: defensive-public-commons-license
license_link: https://github.com/wuzbak/Unitary-Manifold-/blob/main/LICENSE
language:
  - en
tags:
  - physics
  - kaluza-klein
  - open-science
  - unitary-manifold
  - axiomzero
  - rag
  - knowledge-base
size_categories:
  - 1K<n<10K
---

# Unitary Manifold Knowledge Base — RAG Dataset

Chunked and embedded knowledge base for the **Unitary Manifold** 5D Kaluza-Klein physics framework.

Powering the persistent AI assistant at [axiomzerosp.org](https://axiomzerosp.org).

## Contents

| File | Description |
|------|-------------|
| `pillars.jsonl` | All 208+ physics pillar descriptions with gate labels |
| `theorems.jsonl` | 872+ Lean4 theorem statements and pillar mappings |
| `claims.jsonl` | Claim Master Board entries with tension values |
| `fallibility.jsonl` | All FALLIBILITY.md admissions and open gaps |
| `apps.jsonl` | 16 AZ-IP product descriptions |
| `docs.jsonl` | Monograph chapters, arXiv sections, key markdown docs |

## Schema

Each record:
```json
{
  "id": "pillar-4",
  "type": "PILLAR | THEOREM | CLAIM | FALLIBILITY | APP | DOC",
  "gate": "HARDGATE | ADJACENT_TRACK | OPEN_GAP | ARCHITECTURE_LIMIT",
  "title": "...",
  "text": "...",
  "source": "path/to/file.py or lean4/...",
  "version": "v22.6",
  "pillar_ids": [4]
}
```

## Gate labels

- **HARDGATE** — formally closed pillar, highest epistemic confidence
- **ADJACENT_TRACK** — exploratory research track, not a hardgate physics claim
- **OPEN_GAP** — documented open problem, actively tracked
- **ARCHITECTURE_LIMIT** — known framework boundary

## Epistemic note

This dataset represents the current state of a falsifiable framework — not a proven theory.
Primary falsifier: birefringence β — testable by LiteBIRD (~2032).
All open gaps and failures are included without hiding.

## Citation

```bibtex
@software{walker-pearson2026unitary,
  author  = {Walker-Pearson, ThomasCory},
  title   = {The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility},
  year    = {2026},
  doi     = {10.5281/zenodo.19584531},
  url     = {https://doi.org/10.5281/zenodo.19584531},
}
```

*AxiomZero Technologies & Consulting, SPC — UBI 606 239 876*
*Open science artifact — public domain under Defensive Public Commons License v1.0*
