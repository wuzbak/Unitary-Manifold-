# ARCHIVE — Unitary Manifold Historical Records

**Archived: 2026-08-18 | Framework version at time of archival: v20.9**

This directory is the single authoritative archive for all historical records in the Unitary Manifold repository. It supersedes the now-deprecated `HISTORICAL-MILESTONES/` directory.

## Structure

```
ARCHIVE/
├── README.md                    ← this file
├── mas-ledgers/                 ← MAS Wave sprint ledgers (Waves 0–14) + templates
│   ├── MAS_W0_LEDGER.md         ← Wave 0 sprint ledger (historical)
│   ├── MAS_W1_LEDGER.md
│   ...
│   ├── MAS_W14_LEDGER.md        ← Wave 14 sprint ledger (historical)
│   ├── MAS_WAVE0_LEDGER_TEMPLATE.md
│   ├── POST_MAS_EXTENSION_LEDGER.md
│   └── POST_MAS_ROBUSTNESS_CERTIFICATE.md
├── reviews/                     ← Historical adversarial review responses
│   ├── REVIEW_CONCLUSION_v9.31.md
│   ├── REVIEW_CONCLUSION_v9.32.md
│   ├── REVIEW_CONCLUSION_v9.33.md
│   ├── REVIEW_CONCLUSION_v10.1.md
│   ├── REVIEW_CONCLUSION_Caltech_v10.2.md
│   └── FINAL_REVIEW_CONCLUSION.md
├── audits/                      ← Historical audit records
│   └── AUDIT_v10_42_2026-05-10.md
└── operational/                 ← Reserved for historical operational logs
```

## Why These Documents Were Archived

### `mas-ledgers/` — Wave Sprint Ledgers
MAS Wave sprint ledgers document completed work done during the 15-wave Machine-Assisted Sprint (Waves 0–14). They are **historical records of completed work**, not needed for current evaluation. The authoritative current summary is [`docs/WAVE_CHANGELOG.md`](../docs/WAVE_CHANGELOG.md).

Redirect stubs remain in `docs/` pointing here.

### `reviews/` — Adversarial Review Responses
The adversarial review responses (v9.31 through v10.2, plus FINAL_REVIEW_CONCLUSION) were accurate at their version but are **outdated relative to v20.9** — particularly around which pillars were "just added" and what the ToE score was at time of writing. They are preserved here as historical record. **Current adversarial review documents are in `3-FALSIFICATION/ADVERSARIAL_REVIEWS/`**.

### `audits/` — Audit Records
Historical infrastructure audit records. The most recent was at v10.42 (2026-05-10).

## Active Alternatives

| Instead of archived... | Use this active document |
|---|---|
| Wave ledgers | [`docs/WAVE_CHANGELOG.md`](../docs/WAVE_CHANGELOG.md) |
| Review responses | [`3-FALSIFICATION/ADVERSARIAL_REVIEWS/`](../3-FALSIFICATION/ADVERSARIAL_REVIEWS/) |
| Sprint status | [`docs/mas_tracker.yml`](../docs/mas_tracker.yml) (7,544 lines, machine-readable) |
| Pillar status | [`PILLARS/README.md`](../PILLARS/README.md) |

---
*Archive maintained by: GitHub Copilot (AI) | Scientific direction: ThomasCory Walker-Pearson*
