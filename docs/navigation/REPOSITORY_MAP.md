# Repository Map — Human and AI Navigation

This map separates current canonical surfaces from historical records, tools, archives, and downstream outreach.

## Start here

| Need | Start with |
|------|------------|
| Public overview | [`../../README.md`](../../README.md) |
| Current status | [`../../STATUS.md`](../../STATUS.md) |
| Limits and non-claims | [`../../FALLIBILITY.md`](../../FALLIBILITY.md) |
| Formal proof gate | [`../../proof/TIER_1_FORMAL.md`](../../proof/TIER_1_FORMAL.md) |
| AI ingest order | [`../../AGENTS.md`](../../AGENTS.md) |
| Tool/provenance inventory | [`../../9-INFRASTRUCTURE/provenance/README.md`](../../9-INFRASTRUCTURE/provenance/README.md) |

## Numbered epistemic layers

| Layer | Folder | Role |
|-------|--------|------|
| 1 | [`../../1-THEORY/`](../../1-THEORY/) | Peer-reviewable derivations, proofs, theorem registry, claim status. |
| 2 | [`../../2-REPRODUCIBILITY/`](../../2-REPRODUCIBILITY/) | Validation reports, simulation runs, reproducibility snapshots. |
| 3 | [`../../3-FALSIFICATION/`](../../3-FALSIFICATION/) | Predictions, falsification conditions, observation trackers. |
| 4 | [`../../4-IMPLICATIONS/`](../../4-IMPLICATIONS/) | Downstream implications and adjacent applications; not the formal proof gate. |
| 5 | [`../../5-GOVERNANCE/`](../../5-GOVERNANCE/) | Unitary Pentad governance framework, independent of physics correctness. |
| 6 | [`../../6-MONOGRAPH/`](../../6-MONOGRAPH/) | Monograph, manuscript, arXiv, submission, Zenodo material. |
| 7 | [`../../7-OUTREACH/`](../../7-OUTREACH/) | Substack posts, books, visualizations, public explanations. |
| 8 | [`../../8-SAFETY/`](../../8-SAFETY/) | Safety notices, radiological review, dual-use controls. |
| 9 | [`../../9-INFRASTRUCTURE/`](../../9-INFRASTRUCTURE/) | Bots, notebooks, scripts, provenance, result assets. |
| 10 | [`../../10-UM-SOS/`](../../10-UM-SOS/) | UM-SOS architecture and application layer. |

## Cross-cutting folders

| Folder | Role |
|--------|------|
| [`../../TOOLS/`](../../TOOLS/) | Index of calculators, verification scripts, notebooks, and maintenance utilities. |
| [`../../HISTORICAL-MILESTONES/`](../../HISTORICAL-MILESTONES/) | Dated milestone records and historical audits. |
| [`../../ARCHIVE/`](../../ARCHIVE/) | Superseded or inactive material retained for provenance. |
| [`../../docs/`](../../docs/) | Book/site docs, canonical ledgers, policy/review homes, and navigation aids. |
| [`../../proof/`](../../proof/) | Isolated formal evaluation surface. |
| [`../../src/`](../../src/) | Main Python implementation modules. |
| [`../../tests/`](../../tests/) | Main regression tests. |
| [`../../recycling/`](../../recycling/) | Recycling implementation and tests. |
| [`../../claims/`](../../claims/) | Claim-specific reproducibility packages. |
| [`../../data/`](../../data/) | DVC-managed data and payloads. |

## Canonical vs historical rule

- Canonical/current status lives in `STATUS.md`, `FALLIBILITY.md`, `docs/mas_tracker.yml`, `docs/WAVE_CHANGELOG.md`, and provenance docs.
- Historical files preserve what was true at a point in time; they are not automatically current.
- Archive files are retained for evidence and traceability, not as live instructions.

## Quick commands

```bash
python VERIFY.py
python -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q
python TOOLS/audit/check_internal_links.py
```
