# ⬛ AXIOM — Investigative Journalist AI

> *"The document is the primary reality of investigative journalism."*  
> — AxiomZero Investigative Methodology

**Folder:** `apps/axiom-journalist/`  
**Product:** AXIOM Investigative Journalist AI  
**Version:** v1.0  
**Company:** AxiomZero Technologies  
**Status:** Active — functional Gradio application

---

## What AXIOM Is

AXIOM is an AI-assisted investigative journalism research platform. It is built around a single
principle: **the journalist's job is to judge. AXIOM's job is to do the legwork so that
judgment is possible.**

The platform takes an investigative lead and works through a structured research process —
entity mapping, source classification, confidence scoring, legal risk flagging, and brief
generation — and produces a structured investigative brief for human review.

AXIOM does **not** write articles. It does not produce publishable copy. It researches,
organizes, and scores — and then a journalist decides what to do with what it found.

---

## Quick Start

```bash
cd apps/axiom-journalist

# Install dependencies
pip install -r requirements.txt

# Launch
python run.py
# → opens at http://localhost:7870
```

---

## Application Tabs

### 1. 📋 New Investigation

Start a case by giving it a title, your name, and the investigative lead. A lead
is the starting premise: the allegation, the tip, the document you received, or the
pattern you spotted. The more specific the lead, the better the platform performs.

The case is immediately saved to a local SQLite database.

### 2. 👥 Entities

Map every named person, organization, government agency, and corporate structure
relevant to the investigation. For each entity you record:

- **Name** and **type** (Person / Organization / Government Agency / Corporate Structure / ...)
- **Description** — who they are and their relationship to the investigation
- **Stated position** — what they have said publicly
- **Contradictions** — where the documentary record differs from their stated position

Entity mapping is the foundation of investigative journalism. You cannot track
contradictions you haven't mapped.

### 3. 📁 Sources

Every claim in AXIOM traces back to a logged source. Sources are classified into tiers:

| Tier | Examples | Weight |
|------|----------|--------|
| **Tier 1** — Primary Record | Court filings, regulatory filings, FOIA documents, legislation, financial disclosures | 1.00 |
| **Tier 2** — Established/On-Record | Established journalism, academic papers, on-record official statements, expert testimony | 0.65 |
| **Tier 3** — Secondary/Unverified | Press releases, social media, anonymous tips, secondary reports | 0.25 |

**The investigation is only as strong as its Tier-1 sources.** Tier-3 sources generate
leads, not conclusions.

For each source you record:
- Title and type (court filing, news article, interview, etc.)
- URL or document reference
- Date
- Key excerpt (the passage that matters)

### 4. ⚖ Claims

Add the factual claims your investigation is building toward. Each claim is:

**Auto-scored for confidence** based on the sources you attach to it:

| Confidence | Criteria |
|------------|----------|
| **CONFIRMED** | ≥2 Tier-1 sources; independently verifiable |
| **CORROBORATED** | ≥1 Tier-1 + ≥1 Tier-2 source |
| **ALLEGED** | ≥1 source, not fully corroborated |
| **UNVERIFIED** | Single low-tier source, contradicted, or no sources |

**Flagged for legal risk** — you select from:
- `LIBEL_EXPOSURE` — claim about a named party that may require special care
- `SOURCE_PROTECT` — source protection considerations apply
- `WHISTLEBLOWER` — whistleblower legal considerations
- `PRIVACY` — privacy law may apply
- `NATIONAL_SECURITY` — national security law may apply

### 5. 📄 Generate Brief

AXIOM assembles everything into a **structured investigative brief**:

```
================================================================
  AXIOM INVESTIGATIVE BRIEF — [TITLE]
  Prepared: YYYY-MM-DD HH:MM | Status: Active
================================================================

INVESTIGATIVE LEAD
...

ENTITIES IDENTIFIED
  [Person] Jane Smith
    Description: CFO, Acme Corp
    Stated position: "We followed all regulations."
    ⚠ Contradiction: SEC filing 10-K shows unreported offshore account.

SOURCES (3 total | quality score: 0.78)
  [1] Tier 1 — Primary Record
      SEC Filing 10-K 2025 — Acme Corp
      Ref: https://sec.gov/...
      Excerpt: "...undisclosed foreign subsidiaries..."

CLAIMS & CONFIDENCE (2 claims | avg confidence: 0.75)
  [1] [✓ CONFIRMED] Acme Corp failed to disclose offshore subsidiaries.
      Entities: Jane Smith, Acme Corp
      Sources: SEC Filing 10-K 2025, FOIA 2024-001

OPEN QUESTIONS
  [1] What is the value of assets held in the offshore entity?

================================================================
  ⚠ AXIOM OUTPUT — FOR HUMAN REVIEW ONLY. NOT READY TO PUBLISH.
================================================================
```

The brief can be saved (cached in the database) and retrieved at any time.

### 6. 🗂 Case Library

Browse all saved investigations. Load a case to resume work on it. Delete cases you
no longer need.

---

## The AxiomZero Investigative Methodology

The methodology formalizes practices the best investigative journalists have always used:

1. **Every claim is attached to a source.** Every source has a tier classification.
   Tier 1 anchors the investigation. Lower tiers generate leads.

2. **Investigations follow the evidence.** If the evidence exonerates, that is the story.
   If it implicates, that is the story. AXIOM does not begin with a desired outcome.

3. **Transparent research trail.** Every brief accounts for what sources were consulted,
   what confidence each claim was assigned, what contradictions were found, and what
   remains unanswered. A reader should be able to replicate the research path.

4. **Human judgment is structural, not optional.** The platform enforces a gate:
   no output is presented as ready to publish. It is presented as ready to review.

---

## Data Storage

All cases are stored in a local SQLite database at `data/axiom_cases.db`. The database
is created automatically on first run. No data leaves your machine.

Schema:
- `cases` — investigation metadata
- `entities` — mapped people and organizations
- `sources` — logged documents and records
- `claims` — factual claims with confidence scores
- `open_questions` — outstanding research questions

---

## Architecture

```
apps/axiom-journalist/
├── run.py                    # Launcher (python run.py)
├── requirements.txt
├── README.md                 # This document
├── data/
│   └── axiom_cases.db       # SQLite (auto-created)
└── app/
    ├── __init__.py
    ├── main.py               # Gradio UI — all tabs
    ├── core/
    │   ├── __init__.py
    │   └── investigator.py   # Core engine: entities, sources, claims, brief
    └── db/
        ├── __init__.py
        └── cases.py          # SQLite persistence
```

---

## What AXIOM Is Not

- **Not a content generator.** It does not write articles or publishable copy.
- **Not a fact-checker for existing articles.** It is a research engine for
  investigations that have not yet been written.
- **Not a replacement for source relationships**, editorial judgment, legal review,
  or the reporter's instinct for what a story actually means.
- **Not connected to the internet.** AXIOM is an offline research organizer.
  You bring the sources; AXIOM organizes and scores them.

---

## Authorship

*Theory, investigative methodology, product concept: **ThomasCory Walker-Pearson** / AxiomZero Technologies.*  
*Code architecture, implementation, document engineering: **GitHub Copilot** (AI).*

---

*AXIOM v1.0 — apps/axiom-journalist/ — 2026*
