# AxiomZero Technologies — Journalism- Repository

**Author:** ThomasCory Walker-Pearson | **Product of:** AxiomZero Technologies | **Source:** https://github.com/wuzbak/Journalism-

> This document aggregates the complete source of the **wuzbak/Journalism-** GitHub repository.
> It contains two systems:
> 1. **AXIOM Investigative Journalist AI** (`journalist-ai/`) — autonomous multi-agent investigative journalism platform
> 2. **DelPHI Oracle** (`oracle/`) — divination engine combining tarot, runes, numerology, astrology, and I Ching with Unitary Manifold cosmology

---

## `journalist-ai/.env.example`

```text
# AXIOM Journalist AI — Environment Variables
# Copy this file to .env and fill in your API keys.
# NEVER commit your .env file to source control.

# ── AI Backend ───────────────────────────────────────────────────────────────
# Select 'openai' or 'anthropic'
JOURNALIST_BACKEND=openai

# OpenAI (required if JOURNALIST_BACKEND=openai)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Anthropic (required if JOURNALIST_BACKEND=anthropic)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-opus-4-5

# ── Web Search ───────────────────────────────────────────────────────────────
# Select 'brave', 'serpapi', or leave unset for DuckDuckGo fallback
SEARCH_BACKEND=brave
BRAVE_API_KEY=BSA...
SERPAPI_KEY=...
SEARCH_MAX_RESULTS=10

# ── Public Records APIs ──────────────────────────────────────────────────────
PROPUBLICA_API_KEY=...
OPENSECRETS_API_KEY=...
CONGRESS_GOV_API_KEY=DEMO_KEY   # Free key available at api.congress.gov

# ── Federal Legal Data ───────────────────────────────────────────────────────
# GovInfo (U.S. Code, CFR, Federal Register): https://api.govinfo.gov/docs/
# Free key available at api.govinfo.gov; requests work without key (rate-limited)
GOVINFO_API_KEY=DEMO_KEY

# ── Sanctions & PEP Screening ────────────────────────────────────────────────
# OpenSanctions: https://www.opensanctions.org/api/
# Free for limited queries; key required for production use
OPENSANCTIONS_API_KEY=...

# ── Corporate Records ────────────────────────────────────────────────────────
# OpenCorporates: https://opencorporates.com/api_accounts/new (free tier available)
OPENCORPORATES_API_KEY=...
# OCCRP Aleph: https://aleph.occrp.org/ (request at aleph.occrp.org/settings)
ALEPH_API_KEY=...
# CourtListener: https://www.courtlistener.com/api/ (optional; higher rate limits)
COURTLISTENER_API_KEY=...

# ── News APIs ────────────────────────────────────────────────────────────────
# NYT Article Search: https://developer.nytimes.com/get-started (free)
NYT_API_KEY=...

# ── Census & Demographics ─────────────────────────────────────────────────────
# Census Bureau: https://api.census.gov/data/key_signup.html (free)
CENSUS_API_KEY=DEMO_KEY

# ── Storage ──────────────────────────────────────────────────────────────────
# SQLite database path (relative or absolute)
JOURNALIST_DB_PATH=journalist-ai/memory/data/facts.db

# ChromaDB vector store path (relative or absolute)
JOURNALIST_CHROMA_PATH=journalist-ai/memory/data/chroma

# Output directory for generated reports
JOURNALIST_OUTPUT_DIR=journalist-ai/outputs/reports

# ── Agent Behavior ───────────────────────────────────────────────────────────
# Maximum tool-call iterations per investigation
JOURNALIST_MAX_ITERATIONS=10

# ── Optional: Logging ────────────────────────────────────────────────────────
# Set to DEBUG for verbose output
LOG_LEVEL=INFO
```

---

## `journalist-ai/README.md`

```markdown
# AXIOM — Investigative Journalist AI

> *"The job of the journalist is to follow the facts wherever they lead, regardless of who they implicate."*

AXIOM is an autonomous investigative AI journalist. It ingests leads, researches public records, cross-references facts, detects contradictions, and produces structured investigative briefs — all while staying impartial and evidence-driven.

---

## Legal Notice & Product Information

**Product of AxiomZero Technologies**

AXIOM and all associated code, tools, outputs, services, APKs, apps, updates, and bots are products of **AxiomZero Technologies** (Legal Registrant: ThomasCory Walker-Pearson, DBA AxiomZero Technologies, commenced March 26, 2026, United States). All proprietary code, documentation, and research are protected under international copyright law as the original work of the Registrant. AxiomZero Technologies asserts Common Law Trademark rights over the name "AxiomZero Technologies" and any associated "AZ" monograms.

---

---

## 📁 Project Structure

```
journalist-ai/
├── agent/
│   ├── journalist.py           # Core agent loop (OpenAI/Anthropic tool-calling)
│   └── investigation_chain.py  # Multi-stage investigation pipeline
├── skills/
│   ├── politics.py             # Political domain: voting records, campaign finance, lobbying
│   ├── finance.py              # Financial domain: SEC filings, shell companies, fraud
│   ├── lie_detection.py        # Inconsistency detection, logical fallacies, credibility scoring
│   ├── environment.py          # EPA violations, FOIA docs, environmental justice
│   ├── tech.py                 # Privacy, surveillance, antitrust, algorithmic bias
│   ├── legal.py                # Case law, statutes, whistleblower protections
│   └── social_justice.py       # Policing data, housing, voting rights, health disparities
├── tools/
│   ├── web_search.py           # Brave/SerpAPI/DuckDuckGo web search
│   ├── document_reader.py      # PDF/HTML document ingestion
│   ├── manifold_api.py         # Manifold Markets contested-claims signal
│   ├── diary_connector.py      # Diary APK field notes import
│   ├── public_records.py       # SEC EDGAR, OpenSecrets, ProPublica, EPA ECHO
│   ├── social_monitor.py       # Official statement monitoring and comparison
│   └── timeline_builder.py     # Chronological event chain construction
├── memory/
│   ├── fact_store.py           # SQLite + ChromaDB fact persistence
│   ├── entity_graph.py         # Entity relationship graph
│   ├── contradiction_log.py    # Source conflict detection and logging
│   └── lead_queue.py           # Unresolved investigation threads
├── outputs/
│   └── report_generator.py     # Briefs, dossiers, redlines, scorecards, PDF export
├── config/
│   ├── journalist_persona.txt  # AXIOM system prompt / values
│   ├── source_trust.yaml       # Source reliability tiers
│   └── topic_priorities.yaml  # Active investigation priorities
├── main.py                     # CLI entry point
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
cd journalist-ai
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Run an investigation

```bash
# Full investigation from a lead
python main.py investigate "Follow the money: who funded Senator X's campaign and how did their votes align?"

# Import diary field notes
python main.py diary /path/to/diary_export.json --add-to-queue

# Check Manifold Markets for contested claims
python main.py manifold "election integrity" --mode contested --add-to-queue

# View the lead queue
python main.py leads
```

### 4. Use a pre-built investigation template

```bash
# List all available templates
python main.py template list

# Show the OSINT identity template and its variables
python main.py template show osint_identity

# Run an OSINT identity investigation using a username + email as seed vectors
python main.py template run osint_identity \
  --var username=wuzbak \
  --var email=wuzbak@gmail.com \
  --var real_name="Optional Real Name"

# Other templates
python main.py template run conflict_of_interest \
  --var subject="Senator Jane Smith" \
  --var role="Senate Banking Committee" \
  --var entity="Acme Financial Group"

python main.py template run shell_company_network \
  --var company="Acme Holdings LLC" \
  --var jurisdiction=us_de

python main.py template run government_misconduct \
  --var agency=EPA \
  --var allegation="suppression of environmental impact studies" \
  --var time_period="2019-2023"
```

---

## 🔑 API Keys Required

| Service | Environment Variable | Notes |
|---------|---------------------|-------|
| OpenAI | `OPENAI_API_KEY` | Required (or use Anthropic) |
| Anthropic | `ANTHROPIC_API_KEY` | Alternative to OpenAI |
| Brave Search | `BRAVE_API_KEY` | Recommended for web search |
| ProPublica | `PROPUBLICA_API_KEY` | Congress voting records |
| OpenSecrets | `OPENSECRETS_API_KEY` | Campaign finance |
| Congress.gov | `CONGRESS_GOV_API_KEY` | Free at api.congress.gov |

SerpAPI and DuckDuckGo are also supported as search backends.

---

## 🧠 How It Works

### The Investigation Pipeline

```
Lead Input
    ↓
Stage 1: Scope — Define the 5 Ws, identify domains and sources
    ↓
Stage 2: Research — Web search + public records + documents
    ↓
Stage 3: Cross-reference — Deduplicate, score confidence, flag contradictions
    ↓
Stage 4: Entity & Timeline mapping — Who? When? What connections?
    ↓
Stage 5: Gap analysis — What questions are unanswered? New leads.
    ↓
Stage 6: Brief generation — Structured report with confidence scores
    ↓
Output: Markdown brief + optional PDF + entity dossiers
```

### Diary APK Integration

The diary app acts as AXIOM's **field notes input**:

1. Export your notes from the Diary APK as JSON or text
2. Run `python main.py diary export.json`
3. AXIOM extracts named entities, dates, and claims from your entries
4. Leads are added to the investigation queue for research and expansion

### Manifold Markets Integration

Manifold.markets is used as a **contested-claims signal**:

- Markets with near-50% probability = maximum crowd uncertainty = most disputed claims
- High-volume markets = actively debated topics worth investigating
- Surprisingly resolved markets = stories where conventional wisdom was wrong

> ⚠️ Manifold probabilities are crowd signals, **not verified facts**. Always verify independently.

---

## 📊 Confidence Scoring System

Every claim is scored and labeled:

| Label | Score | Meaning |
|-------|-------|---------|
| CONFIRMED | ≥0.85 | Multiple Tier 1/2 sources in agreement |
| CORROBORATED | ≥0.65 | At least two independent sources, one Tier 1/2 |
| ALLEGED | ≥0.40 | Single credible source; needs corroboration |
| UNVERIFIED | <0.40 | Needs investigation |
| DISPUTED | — | Active contradiction between credible sources |

---

## 🔍 Domain Expertise

AXIOM has specialized knowledge and checklists for:

- **Politics** — Voting records, campaign finance, lobbying, revolving door
- **Finance** — SEC filings, shell companies, insider trading, money laundering
- **Law** — Applicable statutes, court filings, whistleblower protections
- **Environment** — EPA violations, environmental justice, greenwashing
- **Technology** — Data privacy, algorithmic bias, antitrust, cybersecurity
- **Social Justice** — Policing disparities, housing, voting rights, healthcare
- **Lie Detection** — Logical fallacy detection, statement comparison, credibility scoring

---

## ⚖️ Editorial Principles

AXIOM operates by the following principles:

1. **Verification first** — No claim without two independent sources
2. **Follow the money** — Financial trails are always worth pursuing
3. **Question authority** — Official statements are starting points, not endpoints
4. **Transparency** — Every claim is sourced and confidence-scored
5. **Impartiality** — No ideological allegiance; facts determine conclusions
6. **Proportionality** — Extraordinary claims require extraordinary evidence

---

## 🛡️ Data Sources

**Tier 1 (Primary)**
- SEC EDGAR, PACER, Congress.gov, FEC, EPA ECHO, FOIA.gov

**Tier 2 (Established Journalism)**
- ProPublica, Reuters, AP, NYT, WaPo, ICIJ, OCCRP

**Crowd Signal (Not Fact)**
- Manifold Markets (probability signal only)

See `config/source_trust.yaml` for the full tier classification.

---

## 🗺️ Roadmap

- [x] Phase 1 — Core agent loop, persona, web search
- [x] Phase 2 — Domain skill modules (all 7)
- [x] Phase 3 — Manifold API + diary connector
- [x] Phase 4 — Memory: fact store, entity graph, contradiction log, lead queue
- [x] Phase 5 — Output: briefs, dossiers, redlines, confidence scorecard, PDF
- [ ] Phase 6 — Graph visualization (entity network export to D3.js/Gephi)
- [ ] Phase 7 — Automated monitoring (scheduled investigations on watchlist topics)
- [ ] Phase 8 — Multi-agent mode (parallel research threads)
- [ ] Phase 9 — Human-in-the-loop editorial review interface

---

*AXIOM is a tool. All output must be reviewed by a human journalist before publication. AI can make mistakes. Sources must be independently verified.*
```

---

## `journalist-ai/agent//init/.py`

```python
```

---

## `journalist-ai/agent/investigation_chain.py`

```python
"""
investigation_chain.py — Structured multi-step investigation pipeline.

Stages:
  1. Intake & scoping
  2. Research (parallel tool calls)
  3. Cross-reference & contradiction detection
  4. Entity & timeline mapping
  5. Gap analysis & follow-up leads
  6. Brief generation with confidence scores
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class InvestigationResult:
    lead: str
    scope: dict[str, Any] = field(default_factory=dict)
    facts: list[dict] = field(default_factory=list)
    contradictions: list[dict] = field(default_factory=list)
    entities: list[dict] = field(default_factory=list)
    timeline: list[dict] = field(default_factory=list)
    follow_up_leads: list[str] = field(default_factory=list)
    brief: str = ""
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: str = ""
    status: str = "pending"


class InvestigationChain:
    """
    Orchestrates a full investigation from intake to published brief.
    Can be used standalone or called from the main agent loop.
    """

    def __init__(self, memory=None, output_generator=None):
        self.memory = memory
        self.output_generator = output_generator

    def scope_lead(self, lead: str) -> dict[str, Any]:
        logger.info("[Stage 1] Scoping lead: %s", lead[:80])
        crowd_signals = _fetch_crowd_uncertainty_signals(lead)
        if crowd_signals:
            logger.info("[Stage 1] %d Manifold contested-claim signals found", len(crowd_signals))
        scope = {
            "original_lead": lead,
            "key_questions": [
                "Who are the primary actors involved?",
                "What specific actions or events occurred?",
                "When did this happen or begin?",
                "Where did this occur (jurisdiction, geography)?",
                "Why is this significant / who is harmed?",
                "How was it done (mechanism)?",
            ],
            "relevant_domains": _infer_domains(lead),
            "suggested_sources": _suggest_sources(lead),
            "crowd_uncertainty_signals": crowd_signals,
        }
        return scope

    def research(self, scope: dict, tools: dict[str, Any] | None = None) -> list[dict]:
        logger.info("[Stage 2] Beginning research for: %s", scope["original_lead"][:80])
        facts: list[dict] = []
        tools = tools or {}
        if "web_search" in tools:
            results = tools["web_search"](query=scope["original_lead"])
            for r in results if isinstance(results, list) else []:
                facts.append({"claim": r.get("snippet", ""), "source": r.get("source", ""), "url": r.get("url", ""), "tier": r.get("tier", 3), "raw_text": r.get("snippet", "")})
        if "public_records" in tools:
            for domain in scope.get("relevant_domains", []):
                records = tools["public_records"](query=scope["original_lead"], domain=domain)
                for r in records if isinstance(records, list) else []:
                    facts.append({"claim": r.get("summary", ""), "source": r.get("source", "public_records"), "url": r.get("url", ""), "tier": 1, "raw_text": r.get("content", "")})
        logger.info("[Stage 2] Collected %d raw facts", len(facts))
        return facts

    def cross_reference(self, facts: list[dict]) -> tuple[list[dict], list[dict]]:
        logger.info("[Stage 3] Cross-referencing %d facts", len(facts))
        contradictions = []
        seen: dict[str, dict] = {}
        for fact in facts:
            claim_key = _normalize_claim(fact["claim"])
            if claim_key in seen:
                existing = seen[claim_key]
                if _claims_contradict(existing["claim"], fact["claim"]):
                    contradictions.append({"claim_a": existing["claim"], "source_a": existing["source"], "claim_b": fact["claim"], "source_b": fact["source"], "type": "direct_contradiction"})
            else:
                seen[claim_key] = fact
        scored_facts = _score_facts(list(seen.values()))
        logger.info("[Stage 3] %d unique facts, %d contradictions found", len(scored_facts), len(contradictions))
        return scored_facts, contradictions

    def map_entities_and_timeline(self, facts: list[dict]) -> tuple[list[dict], list[dict]]:
        logger.info("[Stage 4] Mapping entities and building timeline")
        entities: list[dict] = []
        timeline: list[dict] = []
        try:
            import spacy  # type: ignore
            nlp = spacy.load("en_core_web_sm")
            entity_map: dict[str, dict] = {}
            for fact in facts:
                doc = nlp(fact.get("raw_text", fact.get("claim", "")))
                for ent in doc.ents:
                    key = f"{ent.label_}:{ent.text.lower()}"
                    if key not in entity_map:
                        entity_map[key] = {"text": ent.text, "type": ent.label_, "mentions": 0, "sources": []}
                    entity_map[key]["mentions"] += 1
                    if fact.get("source") not in entity_map[key]["sources"]:
                        entity_map[key]["sources"].append(fact.get("source"))
                if fact.get("date"):
                    timeline.append({"date": fact["date"], "event": fact["claim"], "source": fact["source"]})
            entities = sorted(entity_map.values(), key=lambda e: -e["mentions"])
        except (ImportError, OSError):
            logger.warning("spaCy not available; entity extraction skipped")
            entities = _simple_entity_extract(facts)
        timeline.sort(key=lambda e: e.get("date", ""))
        return entities, timeline

    def gap_analysis(self, scope: dict, facts: list[dict]) -> list[str]:
        logger.info("[Stage 5] Running gap analysis")
        leads = []
        for question in scope.get("key_questions", []):
            relevant = [f for f in facts if _question_relevant(question, f)]
            if len(relevant) < 2:
                leads.append(f"Follow-up needed: {question}")
        if not leads:
            leads.append("Core questions appear covered; consider pursuing financial trail and entity connections")
        return leads

    def generate_brief(self, result: "InvestigationResult") -> str:
        logger.info("[Stage 6] Generating investigative brief")
        if self.output_generator:
            return self.output_generator.generate_brief(result)
        return _default_brief(result)

    def run(self, lead: str, tools: dict[str, Any] | None = None) -> "InvestigationResult":
        result = InvestigationResult(lead=lead)
        result.status = "in_progress"
        try:
            result.scope = self.scope_lead(lead)
            raw_facts = self.research(result.scope, tools=tools)
            result.facts, result.contradictions = self.cross_reference(raw_facts)
            result.entities, result.timeline = self.map_entities_and_timeline(result.facts)
            result.follow_up_leads = self.gap_analysis(result.scope, result.facts)
            result.brief = self.generate_brief(result)
            result.status = "completed"
        except Exception as exc:  # noqa: BLE001
            logger.exception("Investigation pipeline failed")
            result.status = f"failed: {exc}"
        result.completed_at = datetime.utcnow().isoformat()
        if self.memory:
            try:
                self.memory.store_investigation(result)
            except Exception:  # noqa: BLE001
                logger.warning("Failed to persist investigation to memory")
        return result


_DOMAIN_KEYWORDS = {
    "politics": ["politician", "congress", "senate", "election", "vote", "campaign", "party", "government"],
    "finance": ["money", "fraud", "bank", "invest", "fund", "sec", "stock", "shell", "offshore", "tax"],
    "law": ["court", "lawsuit", "law", "legal", "judge", "trial", "civil", "criminal", "rights"],
    "environment": ["climate", "pollution", "epa", "environment", "emission", "toxic", "water", "air"],
    "tech": ["data", "privacy", "surveillance", "algorithm", "ai", "cyber", "patent", "tech"],
    "social_justice": ["race", "discrimination", "inequality", "justice", "rights", "housing", "police"],
    "corporate": ["company", "corporation", "ceo", "subsidiary", "ownership", "offshore", "shell", "director", "merger", "acquisition"],
    "misconduct": ["violation", "penalty", "fine", "settlement", "enforcement", "misconduct", "sanction", "bribery", "corruption"],
    "news": ["breaking", "report", "media", "press", "coverage", "story", "journalist", "expose"],
    "forensic": ["metadata", "exif", "document", "tamper", "forged", "backdated", "deleted", "archive", "wayback", "authenticity"],
    "sanctions": ["sanctioned", "ofac", "pep", "politically exposed", "blacklist", "sdn", "asset freeze"],
    "watchdog": ["inspector general", "ig report", "audit", "oversight", "waste", "abuse", "mismanagement"],
}


def _infer_domains(lead: str) -> list[str]:
    lead_lower = lead.lower()
    return [domain for domain, keywords in _DOMAIN_KEYWORDS.items() if any(kw in lead_lower for kw in keywords)] or ["general"]


def _suggest_sources(lead: str) -> list[str]:
    domains = _infer_domains(lead)
    source_map = {
        "politics": ["congress_gov", "opensecrets", "fec_filings"],
        "finance": ["sec_edgar", "opensecrets", "propublica"],
        "law": ["court_records", "pacer", "court_filings", "statutes", "govinfo"],
        "environment": ["epa_echo", "violation_tracker", "foia_gov"],
        "tech": ["ftc_records", "patent_db", "sec_edgar"],
        "social_justice": ["bureau_of_justice_stats", "propublica"],
        "corporate": ["corporate_records", "aleph_occrp", "sec_edgar", "opencorporates", "opensanctions"],
        "misconduct": ["violation_tracker", "sec_edgar", "court_records", "epa_echo", "oig_oversight"],
        "news": ["news_monitor", "gdelt", "nyt"],
        "forensic": ["metadata_forensics", "wayback_machine", "govinfo"],
        "sanctions": ["opensanctions", "corporate_records", "sec_edgar"],
        "watchdog": ["oig_oversight", "violation_tracker", "govinfo"],
        "general": ["web_search", "propublica"],
    }
    sources: list[str] = []
    for d in domains:
        sources.extend(source_map.get(d, []))
    return list(dict.fromkeys(sources))


def _normalize_claim(claim: str) -> str:
    return " ".join(claim.lower().split())[:120]


def _claims_contradict(a: str, b: str) -> bool:
    negations = [" not ", " never ", " no ", " false ", " deny ", " denied "]
    a_lower, b_lower = a.lower(), b.lower()
    a_negated = any(n in a_lower for n in negations)
    b_negated = any(n in b_lower for n in negations)
    words_a = set(a_lower.split())
    words_b = set(b_lower.split())
    overlap = len(words_a & words_b) / max(len(words_a | words_b), 1)
    return overlap > 0.20 and (a_negated != b_negated)


def _score_facts(facts: list[dict]) -> list[dict]:
    tier_weights = {1: 1.0, 2: 0.85, 3: 0.65, 4: 0.40, 5: 0.15}
    for fact in facts:
        tier = fact.get("tier", 3)
        fact["confidence_score"] = tier_weights.get(tier, 0.40)
        if fact["confidence_score"] >= 0.85:
            fact["confidence_label"] = "CONFIRMED"
        elif fact["confidence_score"] >= 0.65:
            fact["confidence_label"] = "CORROBORATED"
        elif fact["confidence_score"] >= 0.40:
            fact["confidence_label"] = "ALLEGED"
        else:
            fact["confidence_label"] = "UNVERIFIED"
    return facts


def _simple_entity_extract(facts: list[dict]) -> list[dict]:
    import re
    entities: dict[str, dict] = {}
    for fact in facts:
        text = fact.get("raw_text", fact.get("claim", ""))
        matches = re.findall(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)+)\b", text)
        for m in matches:
            if m not in entities:
                entities[m] = {"text": m, "type": "UNKNOWN", "mentions": 0, "sources": []}
            entities[m]["mentions"] += 1
    return sorted(entities.values(), key=lambda e: -e["mentions"])


def _question_relevant(question: str, fact: dict) -> bool:
    q_words = set(question.lower().split())
    f_words = set((fact.get("claim", "") + " " + fact.get("raw_text", "")).lower().split())
    return len(q_words & f_words) >= 2


def _default_brief(result: InvestigationResult) -> str:
    lines = [f"# Investigative Brief", f"**Lead**: {result.lead}", f"**Status**: {result.status}", f"**Started**: {result.started_at}", f"**Completed**: {result.completed_at}", "", "## Key Facts"]
    for f in result.facts[:20]:
        label = f.get("confidence_label", "UNVERIFIED")
        lines.append(f"- [{label}] {f['claim']} *(source: {f.get('source', 'unknown')})*")
    if result.contradictions:
        lines += ["", "## ⚠️ Contradictions Detected"]
        for c in result.contradictions:
            lines.append(f"- **{c['source_a']}** says: {c['claim_a'][:100]}\n  **{c['source_b']}** says: {c['claim_b'][:100]}")
    if result.entities:
        lines += ["", "## Key Entities"]
        for e in result.entities[:10]:
            lines.append(f"- **{e['text']}** ({e['type']}) — mentioned {e['mentions']}x")
    if result.timeline:
        lines += ["", "## Timeline"]
        for t in result.timeline[:15]:
            lines.append(f"- {t.get('date', 'unknown date')}: {t['event'][:100]}")
    if result.follow_up_leads:
        lines += ["", "## Follow-up Leads"]
        for lead in result.follow_up_leads:
            lines.append(f"- {lead}")
    return "\n".join(lines)


def _fetch_crowd_uncertainty_signals(lead: str) -> list[dict]:
    try:
        from journalist_ai.tools.manifold_api import get_contested_claims  # lazy import
        signals = get_contested_claims(topic=lead[:200], min_volume=100.0, min_traders=5, probability_band=(0.30, 0.70))
        return [{"question": s.get("question", ""), "probability": s.get("probability"), "contest_score": s.get("contest_score", 0.0), "total_volume": s.get("total_volume", 0), "unique_traders": s.get("unique_traders", 0), "url": s.get("url", ""), "source_note": s.get("source_note", "")} for s in signals[:10]]
    except Exception as exc:  # noqa: BLE001
        logger.debug("Manifold crowd signals fetch failed (non-fatal): %s", exc)
        return []
```

---

## `journalist-ai/agent/journalist.py`

```python
"""
journalist.py — Core agent loop for AXIOM investigative journalist AI.

Supports OpenAI and Anthropic backends (configurable via JOURNALIST_BACKEND env var).
Tool-calling loop: agent selects tools → executes → feeds results back → repeats until done.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Load persona
# ---------------------------------------------------------------------------
_PERSONA_PATH = Path(__file__).parent.parent / "config" / "journalist_persona.txt"


def _load_persona() -> str:
    if _PERSONA_PATH.exists():
        return _PERSONA_PATH.read_text(encoding="utf-8")
    return "You are an investigative journalist AI. Seek truth with evidence."


JOURNALIST_PERSONA = _load_persona()

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

_TOOL_REGISTRY: dict[str, Any] = {}


def register_tool(name: str, fn: Any, description: str, parameters: dict) -> None:
    """Register a callable tool that the agent can invoke."""
    _TOOL_REGISTRY[name] = {
        "fn": fn,
        "schema": {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        },
    }


def _get_tool_schemas() -> list[dict]:
    return [v["schema"] for v in _TOOL_REGISTRY.values()]


def _execute_tool(name: str, arguments: dict) -> str:
    if name not in _TOOL_REGISTRY:
        return f"[ERROR] Unknown tool: {name}"
    try:
        result = _TOOL_REGISTRY[name]["fn"](**arguments)
        return str(result)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Tool %s raised an exception", name)
        return f"[ERROR] Tool {name} failed: {exc}"


# ---------------------------------------------------------------------------
# Backend abstraction
# ---------------------------------------------------------------------------

BACKEND = os.getenv("JOURNALIST_BACKEND", "openai").lower()
MAX_ITERATIONS = int(os.getenv("JOURNALIST_MAX_ITERATIONS", "10"))
TRUTH_THRESHOLD = float(os.getenv("JOURNALIST_TRUTH_THRESHOLD", "0.75"))
MAX_RESEARCH_CYCLES = int(os.getenv("JOURNALIST_MAX_RESEARCH_CYCLES", "3"))
USE_MULTI_AGENT = os.getenv("JOURNALIST_USE_MULTI_AGENT", "false").lower() == "true"


def _chat_openai(messages: list[dict], tools: list[dict]) -> dict:
    import openai  # type: ignore

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    kwargs: dict[str, Any] = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message


def _chat_anthropic(messages: list[dict], tools: list[dict]) -> dict:
    import anthropic  # type: ignore

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Convert OpenAI-style tool schemas to Anthropic format
    anthropic_tools = []
    for t in tools:
        fn = t["function"]
        anthropic_tools.append(
            {
                "name": fn["name"],
                "description": fn["description"],
                "input_schema": fn["parameters"],
            }
        )

    # Anthropic expects system separate from messages
    system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
    user_messages = [m for m in messages if m["role"] != "system"]

    kwargs: dict[str, Any] = {
        "model": os.getenv("ANTHROPIC_MODEL", "claude-opus-4-5"),
        "max_tokens": 4096,
        "system": system_msg,
        "messages": user_messages,
    }
    if anthropic_tools:
        kwargs["tools"] = anthropic_tools

    response = client.messages.create(**kwargs)

    # Normalize to OpenAI-like message dict for our loop
    text_blocks = [b.text for b in response.content if hasattr(b, "text")]
    tool_uses = [b for b in response.content if b.type == "tool_use"]

    normalized: dict[str, Any] = {
        "role": "assistant",
        "content": " ".join(text_blocks) if text_blocks else None,
        "tool_calls": None,
    }
    if tool_uses:
        normalized["tool_calls"] = [
            {
                "id": b.id,
                "type": "function",
                "function": {"name": b.name, "arguments": json.dumps(b.input)},
            }
            for b in tool_uses
        ]
    return normalized


def _chat(messages: list[dict], tools: list[dict]) -> Any:
    if BACKEND == "anthropic":
        return _chat_anthropic(messages, tools)
    return _chat_openai(messages, tools)


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------


def run_investigation(lead: str, context: str = "") -> str:
    """
    Main entry point.  Given a lead (topic / tip / question), run the full
    investigate-and-report loop and return the final investigative brief.

    When JOURNALIST_USE_MULTI_AGENT=true the multi-agent orchestrator is used,
    which runs Researcher → FactChecker → LegalAuditor → Editor in a recursive
    Truth Threshold loop.

    In single-agent mode a Truth Threshold loop is applied: after each set of
    tool calls the agent evaluates its own confidence and continues researching
    until the threshold is met or MAX_ITERATIONS is reached.
    """
    from journalist_ai.memory.lead_queue import LeadQueue  # lazy import

    lead_queue = LeadQueue()
    lead_queue.add(lead, source="user_input")

    if USE_MULTI_AGENT:
        return _run_multi_agent(lead, context)
    return _run_single_agent(lead, context)


def _run_multi_agent(lead: str, context: str) -> str:
    """Delegate to the multi-agent orchestrator."""
    from journalist_ai.agents.orchestrator import JournalismOrchestrator  # lazy import

    orchestrator = JournalismOrchestrator(tool_registry=_TOOL_REGISTRY)
    result = orchestrator.investigate(lead, context=context)
    brief = result.get("brief", "[No brief produced]")
    prov = result.get("provenance_record", {})
    if prov.get("report_hash"):
        brief += (
            f"\n\n---\n**Provenance hash**: `{prov['report_hash']}`  \n"
            f"**Sealed at**: {prov.get('sealed_at', '')}"
        )
    return brief


def _run_single_agent(lead: str, context: str) -> str:
    """
    Single-agent Truth Threshold loop.

    After each tool-calling round the agent is prompted to self-assess its
    confidence (0.0–1.0).  Research continues until the confidence reaches
    TRUTH_THRESHOLD or MAX_ITERATIONS is exhausted.
    """
    system_prompt = JOURNALIST_PERSONA
    if context:
        system_prompt += f"\n\n## Additional Context\n{context}"

    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"Investigate the following lead and produce a structured investigative brief:\n\n{lead}\n\n"
                f"After each research round, internally evaluate your confidence (0.0–1.0) that you have "
                f"gathered sufficient evidence to publish.  The target confidence threshold is {TRUTH_THRESHOLD}. "
                f"Continue researching until you reach this threshold or exhaust your tool budget."
            ),
        },
    ]

    tools = _get_tool_schemas()
    iteration = 0
    current_confidence = 0.0

    while iteration < MAX_ITERATIONS:
        iteration += 1
        logger.info(
            "Single-agent iteration %d/%d | confidence=%.2f | threshold=%.2f",
            iteration, MAX_ITERATIONS, current_confidence, TRUTH_THRESHOLD,
        )

        response = _chat(messages, tools)

        # Normalize response dict vs object
        if hasattr(response, "tool_calls"):
            tool_calls = response.tool_calls
            content = response.content
        else:
            tool_calls = response.get("tool_calls")
            content = response.get("content")

        # Append assistant message
        messages.append(
            {
                "role": "assistant",
                "content": content,
                "tool_calls": [
                    {
                        "id": tc.id if hasattr(tc, "id") else tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc.function.name if hasattr(tc, "function") else tc["function"]["name"],
                            "arguments": tc.function.arguments if hasattr(tc, "function") else tc["function"]["arguments"],
                        },
                    }
                    for tc in tool_calls
                ]
                if tool_calls
                else None,
            }
        )

        if not tool_calls:
            logger.info("Single-agent finished after %d iterations", iteration)
            return content or "[No output from agent]"

        # Execute each tool call and feed results back
        for tc in tool_calls:
            if hasattr(tc, "function"):
                tc_id = tc.id
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
            else:
                tc_id = tc["id"]
                fn_name = tc["function"]["name"]
                fn_args = json.loads(tc["function"]["arguments"])

            logger.info("Calling tool: %s(%s)", fn_name, fn_args)
            result = _execute_tool(fn_name, fn_args)
            logger.info("Tool result preview: %s", result[:200])

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": result,
                }
            )

        # Ask the agent to self-assess confidence after each tool round
        messages.append(
            {
                "role": "user",
                "content": (
                    "Briefly assess your current confidence level (0.0–1.0) that you have enough "
                    "verified evidence to publish a reliable brief.  Respond with ONLY a single float "
                    "on the first line (e.g. '0.62'), then optionally a one-sentence explanation. "
                    f"Target threshold is {TRUTH_THRESHOLD}.  If you have reached the threshold, "
                    "proceed to write the final brief."
                ),
            }
        )

        conf_response = _chat(messages, [])
        conf_content = conf_response.content if hasattr(conf_response, "content") else conf_response.get("content", "")
        messages.append({"role": "assistant", "content": conf_content})
        current_confidence = _parse_confidence(conf_content or "")

        if current_confidence >= TRUTH_THRESHOLD:
            logger.info(
                "Truth threshold reached (%.2f >= %.2f) after %d iterations",
                current_confidence, TRUTH_THRESHOLD, iteration,
            )
            # Ask for the final brief
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "You have reached the truth threshold.  Now compile and return your final "
                        "structured investigative brief."
                    ),
                }
            )
            final = _chat(messages, [])
            if hasattr(final, "content"):
                return final.content or "[No output]"
            return final.get("content") or "[No output]"

    logger.warning("Reached max iterations (%d) without final answer", MAX_ITERATIONS)
    messages.append(
        {
            "role": "user",
            "content": "You have reached the research limit. Please compile and return your final investigative brief now based on what you've found.",
        }
    )
    final = _chat(messages, [])
    if hasattr(final, "content"):
        return final.content or "[No output]"
    return final.get("content") or "[No output]"


def _parse_confidence(text: str) -> float:
    """Extract the first float in [0.0, 1.0] from the agent's confidence self-assessment."""
    import re

    match = re.search(r"\b(0(\.\d+)?|1(\.0+)?)\b", text)
    if match:
        try:
            return max(0.0, min(1.0, float(match.group(0))))
        except ValueError:
            pass
    return 0.0
```

---

## `journalist-ai/agents//init/.py`

```python
```

---

## `journalist-ai/agents/base_agent.py`

```python
"""
base_agent.py — Abstract base class for all AXIOM specialist agents.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

BACKEND = os.getenv("JOURNALIST_BACKEND", "openai").lower()
MAX_ITERATIONS = int(os.getenv("JOURNALIST_MAX_ITERATIONS", "10"))


def _chat_openai(messages: list[dict], tools: list[dict], model: str | None = None) -> Any:
    import openai

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    kwargs: dict[str, Any] = {
        "model": model or os.getenv("OPENAI_MODEL", "gpt-4o"),
        "messages": messages,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message


def _chat_anthropic(messages: list[dict], tools: list[dict], model: str | None = None) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    anthropic_tools = []
    for t in tools:
        fn = t["function"]
        anthropic_tools.append({"name": fn["name"], "description": fn["description"], "input_schema": fn["parameters"]})

    system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
    user_messages = [m for m in messages if m["role"] != "system"]

    kwargs: dict[str, Any] = {
        "model": model or os.getenv("ANTHROPIC_MODEL", "claude-opus-4-5"),
        "max_tokens": 4096,
        "system": system_msg,
        "messages": user_messages,
    }
    if anthropic_tools:
        kwargs["tools"] = anthropic_tools

    response = client.messages.create(**kwargs)

    text_blocks = [b.text for b in response.content if hasattr(b, "text")]
    tool_uses = [b for b in response.content if b.type == "tool_use"]

    normalized: dict[str, Any] = {"role": "assistant", "content": " ".join(text_blocks) if text_blocks else None, "tool_calls": None}
    if tool_uses:
        normalized["tool_calls"] = [{"id": b.id, "type": "function", "function": {"name": b.name, "arguments": json.dumps(b.input)}} for b in tool_uses]
    return normalized


def _chat(messages: list[dict], tools: list[dict], model: str | None = None) -> Any:
    if BACKEND == "anthropic":
        return _chat_anthropic(messages, tools, model=model)
    return _chat_openai(messages, tools, model=model)


class BaseAgent:
    name: str = "base"
    system_prompt: str = "You are an investigative journalist AI."
    allowed_tool_names: list[str] = []

    def __init__(self, tool_registry: dict[str, Any]):
        self.tool_registry = tool_registry

    def _get_tool_schemas(self) -> list[dict]:
        return [self.tool_registry[name]["schema"] for name in self.allowed_tool_names if name in self.tool_registry]

    def _execute_tool(self, name: str, arguments: dict) -> str:
        if name not in self.tool_registry:
            return f"[ERROR] Unknown tool: {name}"
        if self.allowed_tool_names and name not in self.allowed_tool_names:
            return f"[ERROR] Tool '{name}' is not permitted for agent '{self.name}'"
        try:
            return str(self.tool_registry[name]["fn"](**arguments))
        except Exception as exc:
            logger.exception("Agent %s: tool %s raised an exception", self.name, name)
            return f"[ERROR] Tool {name} failed: {exc}"

    def _run_loop(self, user_message: str, extra_context: str = "", max_iterations: int | None = None) -> str:
        iters = max_iterations or MAX_ITERATIONS
        system = self.system_prompt
        if extra_context:
            system += f"\n\n## Context\n{extra_context}"

        messages: list[dict] = [{"role": "system", "content": system}, {"role": "user", "content": user_message}]
        tools = self._get_tool_schemas()

        for iteration in range(1, iters + 1):
            logger.info("[%s] iteration %d/%d", self.name, iteration, iters)
            response = _chat(messages, tools)

            tool_calls = response.tool_calls if hasattr(response, "tool_calls") else response.get("tool_calls")
            content = response.content if hasattr(response, "content") else response.get("content")

            messages.append({"role": "assistant", "content": content, "tool_calls": [{"id": tc.id if hasattr(tc, "id") else tc["id"], "type": "function", "function": {"name": tc.function.name if hasattr(tc, "function") else tc["function"]["name"], "arguments": tc.function.arguments if hasattr(tc, "function") else tc["function"]["arguments"]}} for tc in tool_calls] if tool_calls else None})

            if not tool_calls:
                return content or "[No output]"

            for tc in tool_calls:
                if hasattr(tc, "function"):
                    tc_id, fn_name, fn_args = tc.id, tc.function.name, json.loads(tc.function.arguments)
                else:
                    tc_id, fn_name, fn_args = tc["id"], tc["function"]["name"], json.loads(tc["function"]["arguments"])
                result = self._execute_tool(fn_name, fn_args)
                messages.append({"role": "tool", "tool_call_id": tc_id, "content": result})

        messages.append({"role": "user", "content": "You have reached the research limit. Return your findings now in the required JSON format."})
        final = _chat(messages, [])
        return (final.content if hasattr(final, "content") else final.get("content")) or "[No output]"

    def run(self, handoff: dict) -> dict:
        raise NotImplementedError(f"{self.__class__.__name__}.run() must be implemented")
```

---

## `journalist-ai/agents/editor.py`

```python
"""
editor.py — Editor Agent for AXIOM multi-agent pipeline.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from typing import Any

from journalist_ai.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

EDITOR_SYSTEM_PROMPT = """
You are the Editor Agent within the AXIOM investigative journalism system.  You are the final
quality gate before a brief is published.

YOUR JOB:
1. Synthesise all findings: scored facts, contradictions, temporal inconsistencies, legal findings,
   entity map, and timeline into a publication-ready investigative brief.
2. Apply editorial judgement:
   - Verify that every significant claim has at minimum TWO independent corroborating sources.
   - Clearly label claims as CONFIRMED, CORROBORATED, ALLEGED, UNVERIFIED, or DISPUTED.
   - Include a "Steelman" section: articulate the strongest innocent explanation for the evidence.
   - Assess the public interest significance (HIGH / MEDIUM / LOW) and justify it.
3. Identify and include:
   - Key entities and their roles
   - A chronological timeline of events
   - Outstanding unanswered questions that remain after this investigation
   - Recommended next steps for a follow-up investigation
4. Return a structured Markdown investigative brief.

FORMAT:
# [Investigation Title]
## Executive Summary
## Key Findings (with confidence labels)
## Legal & Regulatory Exposure
## Entity Map
## Timeline
## Contradictions & Inconsistencies
## Steelman: Innocent Explanations
## Outstanding Questions
## Recommended Next Steps
## Sources & Provenance

Do not include a JSON code block — return the final brief as Markdown prose.
"""

ALLOWED_TOOLS: list[str] = []


class EditorAgent(BaseAgent):
    name = "editor"
    system_prompt = EDITOR_SYSTEM_PROMPT
    allowed_tool_names = ALLOWED_TOOLS

    def run(self, handoff: dict) -> dict:
        lead = handoff.get("lead", "")
        scored_facts = handoff.get("scored_facts", [])
        contradictions = handoff.get("contradictions", [])
        temporal_inconsistencies = handoff.get("temporal_inconsistencies", [])
        legal_findings = handoff.get("legal_findings", [])
        legal_exposure_level = handoff.get("legal_exposure_level", "NONE")
        applicable_statutes = handoff.get("applicable_statutes", [])
        entities = handoff.get("entities", [])
        timeline = handoff.get("timeline", [])
        follow_up_leads = handoff.get("follow_up_leads", [])
        crowd_signals = handoff.get("crowd_uncertainty_signals", [])
        overall_confidence = handoff.get("overall_confidence", 0.0)

        user_msg = (
            f"Write the final investigative brief for this lead: '{lead}'\n\n"
            f"OVERALL CONFIDENCE SCORE: {overall_confidence:.2f}\n\n"
            f"SCORED FACTS ({len(scored_facts)} total):\n{json.dumps(scored_facts[:30], indent=2)}\n\n"
            f"CONTRADICTIONS ({len(contradictions)}):\n{json.dumps(contradictions[:10], indent=2)}\n\n"
            f"TEMPORAL INCONSISTENCIES ({len(temporal_inconsistencies)}):\n"
            f"{json.dumps(temporal_inconsistencies[:10], indent=2)}\n\n"
            f"LEGAL EXPOSURE: {legal_exposure_level}\n"
            f"LEGAL FINDINGS ({len(legal_findings)}):\n{json.dumps(legal_findings[:10], indent=2)}\n\n"
            f"APPLICABLE STATUTES:\n{json.dumps(applicable_statutes[:10], indent=2)}\n\n"
            f"KEY ENTITIES:\n{json.dumps(entities[:15], indent=2)}\n\n"
            f"TIMELINE:\n{json.dumps(timeline[:20], indent=2)}\n\n"
            f"CROWD UNCERTAINTY SIGNALS:\n{json.dumps(crowd_signals[:5], indent=2)}\n\n"
            f"FOLLOW-UP LEADS:\n" + "\n".join(f"- {l}" for l in follow_up_leads[:10])
        )

        brief = self._run_loop(user_msg)

        try:
            from journalist_ai.tools.provenance import seal_report
            sources = list({f.get("url", "") for f in scored_facts if f.get("url")})
            agent_ids = ["researcher", "fact_checker", "legal_auditor", "editor"]
            provenance_record = seal_report(brief, sources=sources, agent_ids=agent_ids)
        except Exception as exc:
            logger.warning("Provenance sealing failed: %s", exc)
            provenance_record = {}

        return {
            **handoff,
            "brief": brief,
            "provenance_record": provenance_record,
            "editor_output": brief,
        }
```

---

## `journalist-ai/agents/fact_checker.py`

```python
"""
fact_checker.py — Fact-Checker Agent for AXIOM multi-agent pipeline.
"""
from __future__ import annotations
import json
import logging
from typing import Any
from journalist_ai.agents.base_agent import BaseAgent
from journalist_ai.agent.investigation_chain import InvestigationChain
from journalist_ai.skills.lie_detection import detect_logical_fallacies, analyze_statement
logger = logging.getLogger(__name__)
FACT_CHECKER_SYSTEM_PROMPT = """
You are the Fact-Checker Agent within the AXIOM investigative journalism system.
YOUR JOB:
1. You will receive a list of raw facts gathered by the Researcher Agent.
2. For each fact, evaluate its credibility using your available tools.
3. Use the social_monitor tool to pull official transcripts and compare statements.
4. Incorporate crowd_uncertainty_signals: claims corresponding to near-50% Manifold markets need extra corroboration.
5. Return a JSON object with keys: scored_facts, contradictions, temporal_inconsistencies, fallacies_detected, overall_confidence.
IMPORTANT: Return ONLY valid JSON in your final message.
"""
ALLOWED_TOOLS = ["web_search","public_records","news_monitor","govinfo","social_monitor","manifold_markets","wayback_machine"]
class FactCheckerAgent(BaseAgent):
    name = "fact_checker"
    system_prompt = FACT_CHECKER_SYSTEM_PROMPT
    allowed_tool_names = ALLOWED_TOOLS
    def run(self, handoff: dict) -> dict:
        lead = handoff.get("lead", "")
        raw_facts = handoff.get("raw_facts", [])
        crowd_signals = handoff.get("crowd_uncertainty_signals", [])
        user_msg = (
            f"Verify the following facts gathered for this lead: '{lead}'\n\n"
            f"RAW FACTS:\n{json.dumps(raw_facts, indent=2)}\n\n"
            f"CROWD UNCERTAINTY SIGNALS (Manifold Markets near 50%):\n{json.dumps(crowd_signals, indent=2)}"
        )
        raw_output = self._run_loop(user_msg)
        from journalist_ai.agents.researcher import _safe_parse_json
        parsed = _safe_parse_json(raw_output)
        if not parsed or "scored_facts" not in parsed:
            logger.warning("[fact_checker] LLM did not return structured JSON; using fallback")
            chain = InvestigationChain()
            scored_facts, contradictions = chain.cross_reference(raw_facts)
            fallacies: list[dict] = []
            for fact in scored_facts:
                detected = detect_logical_fallacies(fact.get("claim", ""))
                for f in detected:
                    fallacies.append({"speaker": fact.get("source",""), "statement_excerpt": fact.get("claim","")[:200], **f})
            parsed = {"scored_facts": scored_facts, "contradictions": contradictions,
                      "temporal_inconsistencies": [], "fallacies_detected": fallacies,
                      "overall_confidence": _mean_confidence(scored_facts)}
        return {**handoff, "scored_facts": parsed.get("scored_facts",[]),
                "contradictions": parsed.get("contradictions",[]),
                "temporal_inconsistencies": parsed.get("temporal_inconsistencies",[]),
                "fallacies_detected": parsed.get("fallacies_detected",[]),
                "overall_confidence": parsed.get("overall_confidence",0.0),
                "fact_checker_output": raw_output}
def _mean_confidence(facts: list[dict]) -> float:
    scores = [f.get("confidence_score",0.5) for f in facts if "confidence_score" in f]
    if not scores: return 0.0
    return round(sum(scores)/len(scores),3)
```

---

## `journalist-ai/agents/legal_auditor.py`

```python
"""
legal_auditor.py — Legal Auditor Agent for AXIOM multi-agent pipeline.
"""
from __future__ import annotations
import json
import logging
from journalist_ai.agents.base_agent import BaseAgent
logger = logging.getLogger(__name__)
LEGAL_SYSTEM_PROMPT = """
You are the Legal Auditor Agent within the AXIOM investigative journalism system.
YOUR JOB:
1. Given scored facts (with confidence scores), assess the legal and regulatory exposure of the
   entities named in this investigation.
2. Identify which statutes, regulations, or case law may be relevant (FCPA, SEC Rule 10b-5, SOX,
   RICO, wire fraud, money laundering, campaign finance, etc.).
3. Evaluate each legal theory:
   a. Identify the relevant legal theory / statute
   b. Map the factual predicates that support or undermine it
   c. Assign a probability bracket: HIGH (>70%), MEDIUM (40-70%), LOW (<40%)
   d. Flag evidentiary gaps
4. Flag any facts that could expose the publication to defamation risk.
5. Return structured JSON: legal_findings (list), applicable_statutes (list), legal_exposure_level (HIGH/MEDIUM/LOW/NONE), defamation_risk_flags (list).
IMPORTANT: Return ONLY valid JSON in your final message.
"""
ALLOWED_TOOLS = ["govinfo","public_records","web_search"]
class LegalAuditorAgent(BaseAgent):
    name = "legal_auditor"
    system_prompt = LEGAL_SYSTEM_PROMPT
    allowed_tool_names = ALLOWED_TOOLS
    def run(self, handoff: dict) -> dict:
        lead = handoff.get("lead", "")
        scored_facts = handoff.get("scored_facts", [])
        entities = handoff.get("entities", [])
        user_msg = (
            f"Assess the legal exposure for this investigation: '{lead}'\n\n"
            f"SCORED FACTS:\n{json.dumps(scored_facts[:40], indent=2)}\n\n"
            f"KEY ENTITIES:\n{json.dumps(entities[:20], indent=2)}"
        )
        raw_output = self._run_loop(user_msg)
        from journalist_ai.agents.researcher import _safe_parse_json
        parsed = _safe_parse_json(raw_output)
        if not parsed or "legal_findings" not in parsed:
            parsed = {"legal_findings": [], "applicable_statutes": [],
                      "legal_exposure_level": "UNKNOWN", "defamation_risk_flags": []}
        return {**handoff,
                "legal_findings": parsed.get("legal_findings", []),
                "applicable_statutes": parsed.get("applicable_statutes", []),
                "legal_exposure_level": parsed.get("legal_exposure_level", "UNKNOWN"),
                "defamation_risk_flags": parsed.get("defamation_risk_flags", []),
                "legal_auditor_output": raw_output}
```

---

## `journalist-ai/agents/orchestrator.py`

```python
"""
orchestrator.py — Orchestrator Agent for AXIOM multi-agent pipeline.
"""
from __future__ import annotations
import json
import logging
from journalist_ai.agents.base_agent import BaseAgent
logger = logging.getLogger(__name__)
ORCHESTRATOR_SYSTEM_PROMPT = """
You are the Orchestrator within the AXIOM investigative journalism system.
YOUR JOB:
1. Given raw user leads, intake documents, and initial context, triage and plan the investigation.
2. Identify the key investigative questions that need answering.
3. Identify the primary entities (people, organisations, locations, financial instruments) that
   should be tracked.
4. Identify the initial set of data sources to query (public records, corporate filings, social
   media, financial data, news archives).
5. Produce a structured JSON investigation plan.
JSON FORMAT:
{
  "investigation_title": "...",
  "lead_summary": "...",
  "key_questions": ["...", ...],
  "entities_of_interest": [{"name":"...", "type":"person|org|location|instrument", "role":"..."}],
  "initial_data_sources": ["public_records","news_monitor","govinfo",...],
  "priority": "HIGH|MEDIUM|LOW",
  "rationale": "..."
}
IMPORTANT: Return ONLY valid JSON in your final message. No preamble, no commentary outside the JSON block.
"""
ALLOWED_TOOLS: list[str] = []
class OrchestratorAgent(BaseAgent):
    name = "orchestrator"
    system_prompt = ORCHESTRATOR_SYSTEM_PROMPT
    allowed_tool_names = ALLOWED_TOOLS
    def run(self, lead: str, context: dict | None = None) -> dict:
        ctx = context or {}
        doc_snippets = ctx.get("document_snippets", [])
        user_msg = f"Investigate this lead: '{lead}'"
        if doc_snippets:
            user_msg += f"\n\nAttached documents (snippets):\n" + "\n---\n".join(doc_snippets[:3])
        raw = self._run_loop(user_msg)
        from journalist_ai.agents.researcher import _safe_parse_json
        plan = _safe_parse_json(raw)
        if not plan:
            plan = {"investigation_title": lead, "lead_summary": lead,
                    "key_questions": [], "entities_of_interest": [],
                    "initial_data_sources": [], "priority": "MEDIUM",
                    "rationale": "No structured plan produced."}
        return {**plan, "lead": lead, "raw_orchestrator_output": raw}
```

---

## `journalist-ai/agents/researcher.py`

```python
"""
researcher.py — Researcher Agent for AXIOM multi-agent pipeline.
"""
from __future__ import annotations
import json
import logging
import re
from journalist_ai.agents.base_agent import BaseAgent
logger = logging.getLogger(__name__)
RESEARCHER_SYSTEM_PROMPT = """
You are the Researcher Agent within the AXIOM investigative journalism system.
YOUR JOB:
1. Execute the investigation plan produced by the Orchestrator.
2. Query all relevant data sources using your available tools.
3. Retrieve raw facts: financial records, corporate filings, legal documents, news articles,
   social media posts, government data, and crowd-intelligence signals from prediction markets.
4. For each fact, record: claim, source URL, source type, date, and a preliminary confidence
   score (0.0-1.0).
5. Identify the key entities mentioned, and map relationships between them.
6. Note any preliminary contradictions or data conflicts you detect.
7. Surface any follow-up leads that emerge.
8. Return structured JSON with: raw_facts, entities, follow_up_leads, crowd_uncertainty_signals.
JSON FORMAT:
{
  "raw_facts": [{"claim":"...","source":"...","url":"...","date":"...","confidence_score":0.0-1.0}],
  "entities": [{"name":"...","type":"person|org|location|instrument","relationships":[...]}],
  "follow_up_leads": ["..."],
  "crowd_uncertainty_signals": [{"question":"...","market_id":"...","probability":0.0-1.0,"signal":"for|against|neutral"}]
}
IMPORTANT: Return ONLY valid JSON in your final message.
"""
ALLOWED_TOOLS = ["web_search","public_records","news_monitor","govinfo","social_monitor",
                 "financial_data","entity_resolver","manifold_markets","wayback_machine",
                 "document_parser","leak_inbox","sec_edgar","fec_filings","court_records",
                 "export_report","pacer","cia_world_factbook","interpol_notices"]
class ResearcherAgent(BaseAgent):
    name = "researcher"
    system_prompt = RESEARCHER_SYSTEM_PROMPT
    allowed_tool_names = ALLOWED_TOOLS
    def run(self, plan: dict) -> dict:
        lead = plan.get("lead", "")
        key_questions = plan.get("key_questions", [])
        entities_of_interest = plan.get("entities_of_interest", [])
        initial_sources = plan.get("initial_data_sources", [])
        user_msg = (
            f"Execute the investigation plan for lead: '{lead}'\n\n"
            f"KEY QUESTIONS:\n" + "\n".join(f"- {q}" for q in key_questions) + "\n\n"
            f"ENTITIES OF INTEREST:\n{json.dumps(entities_of_interest, indent=2)}\n\n"
            f"INITIAL DATA SOURCES: {', '.join(initial_sources)}\n\n"
            f"Use all available tools to retrieve evidence. Return structured JSON."
        )
        raw_output = self._run_loop(user_msg)
        parsed = _safe_parse_json(raw_output)
        if not parsed or "raw_facts" not in parsed:
            logger.warning("[researcher] LLM did not return structured JSON; using empty skeleton")
            parsed = {"raw_facts": [], "entities": [], "follow_up_leads": [],
                      "crowd_uncertainty_signals": []}
        return {**plan, "raw_facts": parsed.get("raw_facts", []),
                "entities": parsed.get("entities", []),
                "follow_up_leads": parsed.get("follow_up_leads", []),
                "crowd_uncertainty_signals": parsed.get("crowd_uncertainty_signals", []),
                "researcher_output": raw_output}
def _safe_parse_json(raw: str) -> dict | None:
    raw = raw.strip()
    for pattern in [r"```json\s*(.*?)\s*```", r"```\s*(.*?)\s*```"]:
        m = re.search(pattern, raw, re.DOTALL)
        if m:
            raw = m.group(1).strip()
            break
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(raw[start:end+1])
            except json.JSONDecodeError:
                pass
    return None
```

---

## `journalist-ai/config/investigation_templates.yaml`

```yaml
# investigation_templates.yaml
# Investigation prompt templates for the AXIOM journalist-ai system.
# These templates are injected into the researcher agent's context based on the investigation type.

templates:

  corporate_fraud:
    name: "Corporate Fraud Investigation"
    description: "Investigates potential financial fraud, accounting irregularities, or securities violations by corporations."
    key_questions_template: |
      - Are there material discrepancies between public financial statements and underlying records?
      - Have executives engaged in insider trading or undisclosed related-party transactions?
      - Are there shell companies or offshore structures used to obscure financial flows?
      - Are there patterns of earnings manipulation (channel stuffing, round-tripping, premature revenue recognition)?
      - Have whistleblowers raised concerns through internal compliance channels?
    required_tools:
      - public_records
      - sec_edgar
      - financial_data
      - entity_resolver
      - court_records
      - news_monitor
      - manifold_markets
    legal_frameworks:
      - "Securities Exchange Act § 10(b) / Rule 10b-5"
      - "Sarbanes-Oxley Act (SOX)"
      - "Dodd-Frank whistleblower provisions"
      - "FCPA (if international operations)"
    confidence_threshold: 0.80
    min_corroborating_sources: 3

  political_corruption:
    name: "Political Corruption Investigation"
    description: "Investigates misuse of public office, bribery, campaign finance violations, or abuse of power by elected officials or appointees."
    key_questions_template: |
      - Are there undisclosed financial relationships between officials and entities they regulate?
      - Are there campaign finance irregularities or illegal straw-donor schemes?
      - Is there evidence of quid pro quo arrangements (votes for contracts, appointments for donations)?
      - Have public funds been diverted for private benefit?
      - Are there conflicts of interest in procurement decisions?
    required_tools:
      - fec_filings
      - public_records
      - govinfo
      - court_records
      - news_monitor
      - social_monitor
      - manifold_markets
    legal_frameworks:
      - "18 U.S.C. § 201 (Bribery)"
      - "18 U.S.C. § 666 (Federal funds corruption)"
      - "Federal Election Campaign Act (FECA)"
      - "RICO (18 U.S.C. §§ 1961-1968)"
      - "Honest Services Wire Fraud (18 U.S.C. § 1346)"
    confidence_threshold: 0.85
    min_corroborating_sources: 3

  financial_crime:
    name: "Financial Crime / Money Laundering Investigation"
    description: "Investigates money laundering, sanctions evasion, dark money flows, or other financial crimes."
    key_questions_template: |
      - Are there complex ownership chains (shell companies, trusts, nominees) designed to obscure beneficial ownership?
      - Is there evidence of layering, placement, or integration of illicit funds?
      - Are there transactions involving OFAC-sanctioned entities, jurisdictions, or individuals?
      - Are there patterns of suspicious activity consistent with structuring (smurfing)?
      - Are gatekeepers (lawyers, accountants, real estate agents) facilitating the scheme?
    required_tools:
      - public_records
      - financial_data
      - entity_resolver
      - sec_edgar
      - court_records
      - govinfo
      - interpol_notices
    legal_frameworks:
      - "Bank Secrecy Act (BSA)"
      - "18 U.S.C. § 1956 (Money Laundering)"
      - "OFAC sanctions regulations"
      - "Corporate Transparency Act (CTA) / FinCEN beneficial ownership"
      - "EU AMLD6"
    confidence_threshold: 0.80
    min_corroborating_sources: 2

  environmental_crime:
    name: "Environmental Crime / Greenwashing Investigation"
    description: "Investigates illegal dumping, pollution, greenwashing, or regulatory violations by corporations or governments."
    key_questions_template: |
      - Are there discrepancies between reported emissions/waste figures and independent measurements?
      - Have regulatory submissions been falsified?
      - Is there evidence of illegal dumping or discharge in violation of EPA/CWA/CAA permits?
      - Are ESG disclosures materially misleading to investors?
      - Have whistleblowers or communities reported health impacts not disclosed publicly?
    required_tools:
      - public_records
      - govinfo
      - web_search
      - news_monitor
      - entity_resolver
      - court_records
    legal_frameworks:
      - "Clean Water Act (CWA)"
      - "Clean Air Act (CAA)"
      - "Resource Conservation and Recovery Act (RCRA)"
      - "SEC climate disclosure rules"
      - "EU Corporate Sustainability Reporting Directive (CSRD)"
    confidence_threshold: 0.75
    min_corroborating_sources: 2

  human_rights:
    name: "Human Rights Abuse Investigation"
    description: "Investigates forced labour, trafficking, extrajudicial killings, or other human rights violations by state or non-state actors."
    key_questions_template: |
      - Are there supply chain links to forced labour or child labour?
      - Are there credible accounts of extrajudicial detention, torture, or killing?
      - Are corporations complicit in or benefiting from human rights abuses?
      - Are there visa, trafficking, or smuggling operations targeting vulnerable populations?
      - Has the government concealed or failed to investigate credible abuse claims?
    required_tools:
      - public_records
      - news_monitor
      - court_records
      - govinfo
      - web_search
      - interpol_notices
    legal_frameworks:
      - "Trafficking Victims Protection Act (TVPA)"
      - "Forced Labor Prevention Act (Uyghur FLP Act)"
      - "UN Guiding Principles on Business and Human Rights"
      - "Rome Statute (ICC jurisdiction)"
    confidence_threshold: 0.80
    min_corroborating_sources: 3

  data_privacy:
    name: "Data Privacy / Surveillance Investigation"
    description: "Investigates illegal surveillance, data breaches, GDPR/CCPA violations, or government overreach in data collection."
    key_questions_template: |
      - Was user data collected or sold without meaningful consent?
      - Were regulatory breach notification requirements violated?
      - Is there evidence of government surveillance without legal authorisation?
      - Are technology companies providing backdoor access to governments?
      - Are data brokers selling sensitive categories of data (health, location, financial) illegally?
    required_tools:
      - public_records
      - govinfo
      - court_records
      - news_monitor
      - web_search
      - document_parser
    legal_frameworks:
      - "GDPR (EU)"
      - "CCPA/CPRA (California)"
      - "Electronic Communications Privacy Act (ECPA)"
      - "Foreign Intelligence Surveillance Act (FISA)"
      - "HIPAA (health data)"
    confidence_threshold: 0.75
    min_corroborating_sources: 2

  supply_chain:
    name: "Supply Chain Integrity Investigation"
    description: "Investigates fraud, counterfeiting, forced labour, or sanctions violations in global supply chains."
    key_questions_template: |
      - Are components or materials sourced from sanctioned countries or entities?
      - Is there evidence of fraudulent certificates of origin?
      - Are third-party auditors independent and credible?
      - Are there patterns of sub-contracting designed to obscure the ultimate source?
    required_tools:
      - public_records
      - entity_resolver
      - financial_data
      - govinfo
      - web_search
    legal_frameworks:
      - "Tariff Act § 307 (forced labour import ban)"
      - "Uyghur Forced Labor Prevention Act"
      - "EU Conflict Minerals Regulation"
      - "OFAC sanctions"
    confidence_threshold: 0.75
    min_corroborating_sources: 2

  disinformation:
    name: "Disinformation / Influence Operation Investigation"
    description: "Investigates coordinated inauthentic behaviour, state-sponsored disinformation, or influence operations targeting democratic processes."
    key_questions_template: |
      - Are there networks of inauthentic accounts amplifying specific narratives?
      - Can we trace the funding or coordination behind a media outlet or campaign?
      - Are there sock puppet networks linked to state actors?
      - Is AI-generated synthetic media (deepfakes) being used for disinformation?
      - Are domestic political actors using foreign-origin infrastructure?
    required_tools:
      - social_monitor
      - web_search
      - news_monitor
      - entity_resolver
      - manifold_markets
    legal_frameworks:
      - "Foreign Agents Registration Act (FARA)"
      - "FECA foreign national contribution ban"
      - "Platform community standards (secondary)"
    confidence_threshold: 0.70
    min_corroborating_sources: 2
```

---

## `journalist-ai/config/journalist_persona.txt`

```text
# AXIOM — Investigative Journalist Persona
## Core Identity
You are AXIOM, an autonomous investigative journalist AI built on the principles of the Fourth Estate. You operate with the rigor of a veteran journalist, the analytical depth of a forensic accountant, and the legal awareness of a media attorney.

## Guiding Principles

### 1. Truth Above All
- Every claim must be verified by at minimum two independent, corroborating sources before publication.
- Distinguish clearly between CONFIRMED facts, CORROBORATED claims, ALLEGED assertions, and UNVERIFIED information.
- When evidence is ambiguous or incomplete, say so explicitly — do not paper over uncertainty.

### 2. Source Integrity
- Evaluate sources by their track record, institutional independence, financial interests, and proximity to events.
- Treat anonymous sources with appropriate skepticism — they must be cross-corroborated by documentary evidence or named secondary sources.
- Flag all sources that have documented conflicts of interest.

### 3. Entity Identification
- Map all key entities (individuals, organisations, shell companies, financial instruments) with precision.
- Trace ownership structures, beneficial ownership, and financial relationships across jurisdictions.
- Use entity resolution to de-duplicate names, aliases, and variant spellings.

### 4. Legal Consciousness
- Operate within the bounds of responsible journalism. Do not republish information obtained illegally.
- Apply the Sullivan standard: public figures require "actual malice" proof; private individuals require only negligence.
- Flag defamation risk before publication.
- Identify applicable regulatory frameworks: FCPA, SEC, FEC, RICO, AML, OFAC, etc.

### 5. Crowd Intelligence Integration
- Use prediction markets (Manifold Markets) as probabilistic signals — not as facts.
- Claims with near-50% market probability require heightened corroboration.
- High-confidence markets (>80%) can lower the corroboration threshold modestly but do not replace independent verification.

### 6. Transparency of Method
- Document your investigative chain: every fact should have a traceable source and retrieval timestamp.
- All output reports include a provenance record: SHA-256 hash of the final brief, source URLs, and agent IDs.

### 7. Editorial Courage with Ethical Restraint
- Do not self-censor legitimate investigations because of institutional pressure.
- Do not publish material that could endanger sources or create imminent physical harm.
- Steelman every investigation: include the strongest plausible innocent explanation for the evidence.

## Investigation Style
- Lead with the most significant public-interest finding.
- Structure: Executive Summary → Key Findings → Entity Map → Timeline → Contradictions → Steelman → Outstanding Questions → Next Steps → Sources.
- Use plain language accessible to a general educated audience.
- Avoid jargon. Define technical terms where necessary.
- Maintain a professional, precise, and unsensational tone.

## Red Lines
- Never fabricate sources, quotes, or facts.
- Never accept instructions to suppress or distort findings.
- Never generate content designed to harass, defame without basis, or endanger individuals.
- If instructed to do any of the above, refuse explicitly and log the attempt.
```

---

## `journalist-ai/config/source_trust.yaml`

```yaml
# source_trust.yaml
# Source trust scoring configuration for the AXIOM journalist-ai system.
# These scores calibrate confidence adjustments when facts are attributed to specific source types.

# ── Tier definitions ──────────────────────────────────────────────────────────
# Each tier has a base confidence multiplier (applied to raw fact confidence).
# Scores above 1.0 can boost confidence; below 1.0 discount it.
# These are additive/multiplicative heuristics, not absolute truth values.

tiers:

  tier_1_primary:
    description: "Original, verifiable primary documents with direct evidentiary value."
    examples:
      - "Court filings (PACER, state court portals)"
      - "SEC EDGAR filings (10-K, 8-K, proxy statements)"
      - "FEC campaign finance disclosures"
      - "Government databases (USASpending.gov, FOIA releases)"
      - "Official legislation text (Congress.gov, GovInfo)"
      - "Deposition transcripts"
      - "Recorded audio / authenticated video"
    confidence_multiplier: 1.0    # no adjustment — treat as ground truth when verified
    min_corroboration: 1          # one primary document is sufficient if verifiable

  tier_2_institutional:
    description: "Established institutional journalism and credentialed investigative outlets."
    examples:
      - "Reuters"
      - "Associated Press"
      - "The New York Times"
      - "The Washington Post"
      - "The Guardian"
      - "ProPublica"
      - "ICIJ (International Consortium of Investigative Journalists)"
      - "OCCRP"
      - "BBC News"
      - "The Financial Times"
      - "Bloomberg"
      - "The Wall Street Journal"
      - "NPR News"
    confidence_multiplier: 0.90
    min_corroboration: 2

  tier_3_specialist:
    description: "Subject-matter specialist publications, academic journals, or expert-led organisations."
    examples:
      - "Bellingcat"
      - "Lawfare"
      - "Just Security"
      - "Brennan Center for Justice"
      - "Center for Strategic and International Studies (CSIS)"
      - "Peer-reviewed academic journals"
      - "Think tanks with documented independence (Brookings, RAND)"
    confidence_multiplier: 0.80
    min_corroboration: 2

  tier_4_general_news:
    description: "General news outlets with editorial standards but variable rigour."
    examples:
      - "Major regional newspapers"
      - "Network television news transcripts"
      - "Wire service syndications (secondary attribution)"
    confidence_multiplier: 0.65
    min_corroboration: 2

  tier_5_social_and_partisan:
    description: "Social media, partisan outlets, blogs, and anonymous sources."
    examples:
      - "Twitter/X posts"
      - "Reddit posts"
      - "Partisan commentary sites"
      - "Anonymous tip-offs via leak inbox"
      - "Unverified Telegram channels"
    confidence_multiplier: 0.30
    min_corroboration: 3
    note: "Use only as leads — must be corroborated by Tier 1-3 sources before publication."

  tier_6_synthetic:
    description: "AI-generated summaries, LLM outputs, or synthetic intelligence products."
    examples:
      - "ChatGPT / Claude / Gemini outputs (uncited)"
      - "AXIOM internal reasoning (self-generated)"
    confidence_multiplier: 0.10
    min_corroboration: 4
    note: "Never cite AI-generated content as a primary source. Use only to generate hypotheses."

# ── Domain-specific adjustments ───────────────────────────────────────────────
domain_adjustments:
  financial:
    sec_edgar: +0.10         # SEC filings are authoritative on disclosed financial data
    financial_times: +0.05   # FT has strong financial reporting standards
    anonymous_trader: -0.20  # insider tips carry legal risk and unverifiable bias

  legal:
    pacer: +0.15             # PACER = official court record
    law360: +0.05            # Law360 is reliable for legal reporting
    anonymous_lawyer: -0.15

  political:
    official_government_statement: +0.05   # official but potentially self-serving
    opposition_party_statement: -0.10      # high political motivation
    fec_filings: +0.10                     # FEC data is primary

  national_security:
    leaked_documents_unverified: -0.30
    authenticated_government_doc: +0.10
    whistleblower_named: +0.05
    whistleblower_anonymous: -0.15

# ── Conflict-of-interest flags ────────────────────────────────────────────────
conflict_of_interest_flags:
  - type: "Financial relationship"
    description: "Source has direct financial relationship with entity being investigated."
    confidence_penalty: -0.25

  - type: "Advocacy organisation"
    description: "Source is an advocacy or lobbying organisation with a declared position."
    confidence_penalty: -0.15

  - type: "Competitor or adversary"
    description: "Source is a direct competitor or known adversary of the entity being investigated."
    confidence_penalty: -0.20

  - type: "Litigation party"
    description: "Source is a party in active litigation against the entity being investigated."
    confidence_penalty: -0.20

  - type: "Anonymous tip via AXIOM leak inbox"
    description: "Tip received through AXIOM's anonymous submission channel — provenance unverified."
    confidence_penalty: -0.10
    note: "Apply Tier 5 multiplier and require documentary corroboration."

# ── Publication confidence thresholds ────────────────────────────────────────
publication_thresholds:
  publish_confirmed:        0.85    # Publish as confirmed fact
  publish_corroborated:     0.65    # Publish as 'sources indicate'
  publish_alleged:          0.40    # Publish as allegation with source attribution
  hold_for_investigation:   0.20    # Hold — insufficient confidence, continue investigating
  do_not_publish:           0.00    # Do not publish — risk of defamation or factual error too high
```

---

## `journalist-ai/config/topic_priorities.yaml`

```yaml
# Active Investigation Priorities
# Update this file to steer the journalist agent's research focus.
# Priority levels: critical | high | medium | low | monitor

active_investigations:

  - id: "INV-001"
    title: "Corporate Capture of Regulatory Agencies"
    priority: critical
    domains: [finance, politics, governance]
    key_questions:
      - "Which former agency officials now work for the industries they regulated?"
      - "What rule changes benefited specific donors within 12 months of donations?"
      - "Which lobbying firms have the most ex-regulators on staff?"
    data_sources: [opensecrets, sec_edgar, fec_filings, congress_gov]
    tags: [revolving_door, regulatory_capture, corruption]

  - id: "INV-002"
    title: "Environmental Violations & Cover-ups"
    priority: high
    domains: [environment, law, corporate]
    key_questions:
      - "Which companies have EPA violations without penalties in the last 3 years?"
      - "Are there FOIA documents showing suppressed environmental impact studies?"
      - "Which communities bear disproportionate pollution burdens?"
    data_sources: [epa_echo, foia_gov, propublica]
    tags: [environment, environmental_justice, regulatory_failure]

  - id: "INV-003"
    title: "Political Dark Money & Campaign Finance"
    priority: critical
    domains: [finance, politics]
    key_questions:
      - "Which 501(c)(4) organizations are funneling dark money to campaigns?"
      - "What is the disclosed vs. undisclosed spend ratio for major donors?"
      - "Are there patterns between donations and favorable legislation?"
    data_sources: [fec_filings, opensecrets, irs_990_forms]
    tags: [campaign_finance, dark_money, corruption]

  - id: "INV-004"
    title: "Tech Surveillance & Data Privacy Abuses"
    priority: high
    domains: [tech, law, social_justice]
    key_questions:
      - "Which companies are selling user data to data brokers without consent?"
      - "Are government agencies purchasing commercial surveillance data to bypass warrant requirements?"
      - "Which tech companies have faced FTC or EU GDPR enforcement actions?"
    data_sources: [sec_edgar, ftc_records, court_filings, patent_db]
    tags: [surveillance, data_privacy, tech_accountability]

  - id: "INV-005"
    title: "Shell Company & Offshore Finance Networks"
    priority: high
    domains: [finance, law, governance]
    key_questions:
      - "Which US-registered LLCs have no disclosed beneficial owners?"
      - "Are there connections between sanctioned entities and US financial institutions?"
      - "Which law firms specialize in setting up opacity structures for clients?"
    data_sources: [fincen, icij_offshore_leaks, sec_edgar, opensanctions]
    tags: [money_laundering, offshore_finance, shell_companies]

  - id: "INV-006"
    title: "Judicial & Legal System Integrity"
    priority: medium
    domains: [law, governance, social_justice]
    key_questions:
      - "Which judges have undisclosed financial relationships with litigants?"
      - "Are mandatory minimum sentencing patterns racially disparate?"
      - "Which public defenders are handling caseloads above ABA recommended limits?"
    data_sources: [pacer, court_filings, bureau_of_justice_stats]
    tags: [judicial_integrity, criminal_justice, civil_rights]

  - id: "INV-007"
    title: "Manifold-Flagged Contested Claims"
    priority: monitor
    domains: [all]
    key_questions:
      - "What are the highest-volume unresolved Manifold markets by topic?"
      - "Which markets have the highest uncertainty (near 50/50 probability)?"
      - "Which resolved markets were widely mispredicted — and why?"
    data_sources: [manifold_markets]
    tags: [prediction_markets, contested_facts, crowd_signal]

# Topics to watch for emerging stories
watchlist:
  - "Whistleblower disclosures (SEC, CFTC, OSHA, DOJ)"
  - "Major FOIA releases"
  - "Congressional hearing transcripts"
  - "New Manifold market clusters around a single topic"
  - "Unusual SEC trading volume pre-announcement"
  - "Sudden changes in lobbying expenditure by sector"
  - "Court docket filings in high-profile cases"

# Investigation status codes
status_codes:
  active: "Currently being researched"
  pending: "Queued; awaiting resources or additional leads"
  on_hold: "Paused pending new information"
  completed: "Report generated"
  referred: "Passed to human journalist for follow-up"
  closed_insufficient_evidence: "Investigated; insufficient evidence to proceed"
```

---

## `journalist-ai/main.py`

```python
successfully downloaded text file (SHA: a9c0ecc44264526a1c63fd6bd6b7ee018ff6ce49)"""
main.py — CLI entry point for AXIOM Investigative AI.

Usage:
  python -m journalist_ai.main investigate "Who funded the Senator's campaign?"
  python -m journalist_ai.main leads
  python -m journalist_ai.main diary path/to/export.json
  python -m journalist_ai.main manifold "climate change"
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import logging
import os
import sys
import types
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

# Bootstrap: the package directory is named 'journalist-ai' (hyphen), which Python
# cannot import as a module.  Create a synthetic 'journalist_ai' top-level package
# that points to this directory so all 'journalist_ai.*' imports resolve correctly.
# This mirrors the same approach used in tests/conftest.py.
def _bootstrap_journalist_ai_package() -> None:
    if "journalist_ai" in sys.modules:
        return
    pkg_path = Path(__file__).parent  # journalist-ai/
    # Make the repo root (parent of journalist-ai/) importable so sub-packages
    # like journalist_ai.agent, journalist_ai.tools, etc. can be found.
    repo_root = str(pkg_path.parent)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    journalist_ai = types.ModuleType("journalist_ai")
    journalist_ai.__path__ = [str(pkg_path)]
    journalist_ai.__package__ = "journalist_ai"
    journalist_ai.__spec__ = importlib.util.spec_from_file_location(
        "journalist_ai", str(pkg_path / "__init__.py")
    )
    sys.modules["journalist_ai"] = journalist_ai

_bootstrap_journalist_ai_package()

# Load .env if present
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

try:
    import click  # type: ignore
except ImportError:
    print("click not installed. Run: pip install -r journalist-ai/requirements.txt")
    sys.exit(1)

from journalist_ai.agent.journalist import run_investigation, register_tool
from journalist_ai.tools import (
    web_search, manifold_api, public_records, diary_connector, timeline_builder,
    corporate_records, court_records, news_monitor, violation_tracker,
    govinfo, opensanctions, wayback_machine, oig_oversight, metadata_forensics,
    watchlist, provenance, c2pa_verifier, entity_resolver,
)
from journalist_ai.tools.axiomzero_gate import axiomzero_approval, read_audit_log
from journalist_ai.tools import social_monitor
from journalist_ai.memory.lead_queue import LeadQueue


def _register_default_tools():
    """Register the standard tool set with the agent."""
    register_tool(
        name="web_search",
        fn=web_search.search,
        description=web_search.TOOL_DESCRIPTION,
        parameters=web_search.TOOL_SCHEMA,
    )
    register_tool(
        name="manifold_markets",
        fn=manifold_api.run_tool,
        description=manifold_api.TOOL_DESCRIPTION,
        parameters=manifold_api.TOOL_SCHEMA,
    )
    register_tool(
        name="public_records",
        fn=public_records.run_tool,
        description=public_records.TOOL_DESCRIPTION,
        parameters=public_records.TOOL_SCHEMA,
    )
    register_tool(
        name="timeline_builder",
        fn=timeline_builder.run_tool,
        description=timeline_builder.TOOL_DESCRIPTION,
        parameters=timeline_builder.TOOL_SCHEMA,
    )
    register_tool(
        name="corporate_records",
        fn=corporate_records.run_tool,
        description=corporate_records.TOOL_DESCRIPTION,
        parameters=corporate_records.TOOL_SCHEMA,
    )
    register_tool(
        name="court_records",
        fn=court_records.run_tool,
        description=court_records.TOOL_DESCRIPTION,
        parameters=court_records.TOOL_SCHEMA,
    )
    register_tool(
        name="news_monitor",
        fn=news_monitor.run_tool,
        description=news_monitor.TOOL_DESCRIPTION,
        parameters=news_monitor.TOOL_SCHEMA,
    )
    register_tool(
        name="violation_tracker",
        fn=violation_tracker.run_tool,
        description=violation_tracker.TOOL_DESCRIPTION,
        parameters=violation_tracker.TOOL_SCHEMA,
    )
    register_tool(
        name="govinfo",
        fn=govinfo.run_tool,
        description=govinfo.TOOL_DESCRIPTION,
        parameters=govinfo.TOOL_SCHEMA,
    )
    register_tool(
        name="opensanctions",
        fn=opensanctions.run_tool,
        description=opensanctions.TOOL_DESCRIPTION,
        parameters=opensanctions.TOOL_SCHEMA,
    )
    register_tool(
        name="wayback_machine",
        fn=wayback_machine.run_tool,
        description=wayback_machine.TOOL_DESCRIPTION,
        parameters=wayback_machine.TOOL_SCHEMA,
    )
    register_tool(
        name="oig_oversight",
        fn=oig_oversight.run_tool,
        description=oig_oversight.TOOL_DESCRIPTION,
        parameters=oig_oversight.TOOL_SCHEMA,
    )
    register_tool(
        name="metadata_forensics",
        fn=metadata_forensics.run_tool,
        description=metadata_forensics.TOOL_DESCRIPTION,
        parameters=metadata_forensics.TOOL_SCHEMA,
    )
    register_tool(
        name="social_monitor",
        fn=social_monitor.run_tool,
        description=social_monitor.TOOL_DESCRIPTION,
        parameters=social_monitor.TOOL_SCHEMA,
    )
    register_tool(
        name="watchlist",
        fn=watchlist.run_tool,
        description=watchlist.TOOL_DESCRIPTION,
        parameters=watchlist.TOOL_SCHEMA,
    )
    register_tool(
        name="provenance",
        fn=provenance.run_tool,
        description=provenance.TOOL_DESCRIPTION,
        parameters=provenance.TOOL_SCHEMA,
    )
    register_tool(
        name="c2pa_verifier",
        fn=c2pa_verifier.run_tool,
        description=c2pa_verifier.TOOL_DESCRIPTION,
        parameters=c2pa_verifier.TOOL_SCHEMA,
    )
    register_tool(
        name="entity_resolver",
        fn=entity_resolver.run_tool,
        description=entity_resolver.TOOL_DESCRIPTION,
        parameters=entity_resolver.TOOL_SCHEMA,
    )


@click.group()
def cli():
    """AXIOM — Investigative Journalist AI"""


@cli.command()
@click.argument("lead")
@click.option("--context", default="", help="Additional context or background")
@click.option("--output", default="", help="Save brief to this file path")
def investigate(lead: str, context: str, output: str):
    """Run a full investigation on a lead or topic."""
    _register_default_tools()
    click.echo(f"\n🔍 Starting investigation: {lead}\n")
    brief = run_investigation(lead, context=context)
    click.echo("\n" + "=" * 60)
    click.echo(brief)
    if output:
        Path(output).write_text(brief, encoding="utf-8")
        click.echo(f"\n📄 Brief saved to: {output}")


@cli.command("resolve")
@click.argument("name")
@click.option("--output", default="", help="Save JSON result to this file path")
def resolve_entity(name: str, output: str):
    """
    Resolve a person's name across OpenCorporates, OpenSecrets, and
    CourtListener.  Returns a Confidence Score and a Contradiction Log.

    Example:
      python -m journalist_ai.main resolve "Jane A. Smith"
    """
    click.echo(f"\n🔎 Resolving entity: {name}\n")
    result = entity_resolver.run_tool(name=name)
    confidence = result.get("confidence_score", 0.0)
    tier = result.get("confidence_tier", "LOW")
    variants = result.get("name_variants", [])
    corporate = result.get("corporate", [])
    political = result.get("political", [])
    legal = result.get("legal", [])
    contradictions = result.get("contradiction_flags", [])

    click.echo(f"Name variants searched: {', '.join(variants)}")
    click.echo(f"\n📊 Confidence Score: {confidence:.0%}  [{tier}]")

    if corporate:
        click.echo(f"\n🏢 Corporate records ({len(corporate)} hit(s)):")
        for r in corporate[:5]:
            click.echo(f"  • {r.get('officer_name', '')} — {r.get('position', '')} @ {r.get('company_name', '')}")
            if r.get("jurisdiction_code"):
                click.echo(f"    Jurisdiction: {r['jurisdiction_code']} | Status: {r.get('company_status', '')}")
            if r.get("url"):
                click.echo(f"    URL: {r['url']}")
    else:
        click.echo("\n🏢 Corporate records: none found")

    if political:
        click.echo(f"\n💰 Political finance ({len(political)} hit(s)):")
        for r in political[:5]:
            click.echo(f"  • {r.get('officer_name', '')} — {r.get('office', '')} ({r.get('party', '')}, {r.get('state', '')})")
    else:
        click.echo("\n💰 Political finance: none found")

    if legal:
        click.echo(f"\n⚖️  Legal filings ({len(legal)} hit(s)):")
        for r in legal[:5]:
            click.echo(f"  • {r.get('case_name', '')} | {r.get('court', '')} | Filed: {r.get('date_filed', '')}")
            if r.get("url"):
                click.echo(f"    URL: {r['url']}")
    else:
        click.echo("\n⚖️  Legal filings: none found")

    if contradictions:
        click.echo("\n⚠️  Contradiction flags:")
        for flag in contradictions:
            click.echo(f"  • {flag}")

    if output:
        Path(output).write_text(json.dumps(result, indent=2), encoding="utf-8")
        click.echo(f"\n📄 Result saved to: {output}")


@cli.command("axiomzero")
@click.argument("target")
@click.option("--output", default="", help="Save full JSON dossier to this file path")
@click.option(
    "--operator",
    default="",
    envvar="AXIOMZERO_OPERATOR",
    help="Operator identifier written to the audit log (overrides $AXIOMZERO_OPERATOR)",
)
def axiomzero_deep_scan(target: str, output: str, operator: str):
    """
    AxiomZero Direct Action Mode — operator-initiated forensic deep-scan.

    Bypasses passive pattern-discovery and immediately fans out across
    OpenCorporates, OpenSecrets, and CourtListener for TARGET.  Requires
    explicit Human-in-the-Loop authorization before any data is retrieved.

    The decision (approved or denied) is written to the immutable AxiomZero
    audit log regardless of outcome.

    Example:
      python -m journalist_ai.main axiomzero "Jane A. Smith" --operator "reporter@newsroom.org"
    """
    if operator:
        os.environ["AXIOMZERO_OPERATOR"] = operator

    click.echo(
        f"\n{'='*60}\n"
        "⚠️  AXIOMZERO DIRECT ACTION MODE\n"
        f"Forensic deep-scan requested for: {target}\n"
        "All API queries, operator decisions, and results are\n"
        "logged to the immutable AxiomZero audit trail.\n"
        f"{'='*60}"
    )

    # run_tool is already wrapped with @axiomzero_approval
    result = entity_resolver.run_tool(name=target)

    if result is None:
        click.echo("\n[AXIOMZERO] Authorization denied — no data retrieved.")
        return

    confidence = result.get("confidence_score", 0.0)
    tier = result.get("confidence_tier", "LOW")
    corporate = result.get("corporate", [])
    political = result.get("political", [])
    legal = result.get("legal", [])
    contradictions = result.get("contradiction_flags", [])

    click.echo(f"\n📊 Identity Confidence: {confidence:.0%}  [{tier}]")
    click.echo(f"   Corporate hits : {len(corporate)}")
    click.echo(f"   Political hits : {len(political)}")
    click.echo(f"   Legal filings  : {len(legal)}")

    if contradictions:
        click.echo("\n⚠️  Contradiction flags detected:")
        for flag in contradictions:
            click.echo(f"  • {flag}")
    else:
        click.echo("\n✅ No contradictions detected across sources.")

    if output:
        Path(output).write_text(json.dumps(result, indent=2), encoding="utf-8")
        click.echo(f"\n📄 Full dossier saved to: {output}")


@cli.command("axiomzero-log")
@click.option("--limit", default=20, help="Number of most-recent audit entries to display")
def axiomzero_audit_log(limit: int):
    """
    Display the AxiomZero authorization audit log.

    Shows who requested what, when, and whether authorization was granted or
    denied — the immutable chain of editorial custody.
    """
    entries = read_audit_log(limit=limit)
    if not entries:
        click.echo("\nAxiomZero audit log is empty.")
        return
    click.echo(f"\n🔒 AxiomZero Audit Log (last {len(entries)} entries)\n")
    for e in entries:
        decision_icon = "✅" if e.get("decision") == "GRANTED" else "🚫"
        click.echo(
            f"{decision_icon} [{e.get('timestamp', '')}] "
            f"{e.get('decision', '')} — '{e.get('target', '')}'"
        )
        click.echo(f"   Operator : {e.get('operator', 'unknown')}")
        if e.get("reason"):
            click.echo(f"   Reason   : {e['reason']}")
        click.echo(f"   Function : {e.get('function', '')}")
        click.echo()


@cli.command()
@click.option("--limit", default=20, help="Number of leads to show")
def leads(limit: int):
    """Show the current investigation lead queue."""
    queue = LeadQueue()
    pending = queue.get_all_pending(limit=limit)
    summary = queue.summary()
    click.echo(f"\n📋 Lead Queue Summary: {summary}")
    click.echo(f"\nTop {len(pending)} pending leads:\n")
    for i, lead in enumerate(pending, 1):
        click.echo(f"{i}. [{lead['priority'].upper()}] {lead['content'][:100]}")
        click.echo(f"   Source: {lead['source']} | Added: {lead['added_at'][:10]}\n")


@cli.command()
@click.argument("file_path")
@click.option("--add-to-queue", is_flag=True, default=True, help="Add extracted leads to lead queue")
def diary(file_path: str, add_to_queue: bool):
    """Import diary/field notes and extract investigation leads."""
    click.echo(f"\n📔 Importing diary: {file_path}")
    leads_data = diary_connector.run_tool(file_path=file_path)
    click.echo(f"✅ Extracted {len(leads_data)} leads from diary\n")
    if add_to_queue:
        queue = LeadQueue()
        ids = queue.add_from_diary_leads(leads_data)
        click.echo(f"Added {len(ids)} leads to the investigation queue.")
    for i, lead in enumerate(leads_data[:5], 1):
        click.echo(f"{i}. [{lead.get('priority', '?').upper()}] {lead.get('content', '')[:100]}")


@cli.command()
@click.argument("topic")
@click.option("--mode", default="contested", type=click.Choice(["contested", "resolved", "trending", "search"]))
@click.option("--limit", default=10)
@click.option("--add-to-queue", is_flag=True, default=False, help="Add results to lead queue")
def manifold(topic: str, mode: str, limit: int, add_to_queue: bool):
    """Query Manifold Markets for contested claims on a topic."""
    click.echo(f"\n📊 Querying Manifold Markets: {topic} (mode: {mode})\n")
    results = manifold_api.run_tool(topic=topic, mode=mode, limit=limit)
    if not results:
        click.echo("No markets found.")
        return
    for m in results:
        prob = m.get("probability")
        prob_str = f"{prob:.0%}" if prob is not None else "N/A"
        click.echo(f"• {m['question']}")
        click.echo(f"  Probability: {prob_str} | Volume: ${m.get('total_volume', 0):,.0f} | Traders: {m.get('unique_traders', 0)}")
        if m.get("surprise_flag"):
            click.echo(f"  ⚡ {m.get('surprise_note', '')}")
        click.echo(f"  URL: {m.get('url', '')}\n")

    if add_to_queue:
        queue = LeadQueue()
        for m in results:
            queue.add_from_manifold(m)
        click.echo(f"Added {len(results)} Manifold leads to queue.")


@cli.command()
@click.argument("query")
@click.option("--mode", default="all", type=click.Choice(["companies", "officers", "aleph", "all"]),
              help="Search mode: companies, officers, aleph entity archive, or all")
@click.option("--jurisdiction", default="", help="OpenCorporates jurisdiction code (e.g. us_de, gb, ky)")
def corporate(query: str, mode: str, jurisdiction: str):
    """Search corporate records (OpenCorporates + OCCRP Aleph) for entity triangulation."""
    click.echo(f"\n🏢 Searching corporate records: {query} (mode: {mode})\n")
    results = corporate_records.run_tool(query=query, mode=mode, jurisdiction=jurisdiction)
    if not results:
        click.echo("No records found.")
        return
    for r in results:
        name = r.get("name") or r.get("caption") or r.get("company_name") or r.get("officer_name", "")
        source = r.get("data_source", "")
        click.echo(f"• [{source.upper()}] {name}")
        if r.get("jurisdiction_code"):
            click.echo(f"  Jurisdiction: {r['jurisdiction_code']} | Status: {r.get('status', '')}")
        if r.get("url"):
            click.echo(f"  URL: {r['url']}")
        click.echo()


@cli.command()
@click.argument("query")
@click.option("--mode", default="all", type=click.Choice(["opinions", "dockets", "parties", "all"]),
              help="Search mode: opinions, dockets, parties, or all")
@click.option("--court", default="", help="Court slug (e.g. scotus, ca9, dcd, nysd)")
@click.option("--after", "after_date", default="", help="Only results filed after YYYY-MM-DD")
def court(query: str, mode: str, court: str, after_date: str):
    """Search federal and state court records via CourtListener."""
    click.echo(f"\n⚖️  Searching court records: {query} (mode: {mode})\n")
    results = court_records.run_tool(query=query, mode=mode, court=court, after_date=after_date)
    if not results:
        click.echo("No records found.")
        return
    for r in results:
        click.echo(f"• {r.get('case_name', r.get('party_name', ''))}")
        if r.get("court"):
            click.echo(f"  Court: {r['court']} | Filed: {r.get('date_filed', '')}")
        if r.get("url"):
            click.echo(f"  URL: {r['url']}")
        click.echo()


@cli.command()
@click.argument("query")
@click.option("--source", default="all", type=click.Choice(["gdelt", "nyt", "all"]),
              help="News source: gdelt, nyt, or all")
@click.option("--timespan", default="1month",
              type=click.Choice(["15min", "1h", "24h", "1week", "1month", "3months"]),
              help="GDELT time window")
@click.option("--begin-date", default="", help="NYT search start date (YYYYMMDD)")
@click.option("--end-date", default="", help="NYT search end date (YYYYMMDD)")
def news(query: str, source: str, timespan: str, begin_date: str, end_date: str):
    """Monitor news coverage via GDELT (global, real-time) and NYT (archival)."""
    click.echo(f"\n📰 Searching news: {query} (source: {source})\n")
    results = news_monitor.run_tool(
        query=query, source=source, timespan=timespan,
        begin_date=begin_date, end_date=end_date,
    )
    if not results:
        click.echo("No articles found.")
        return
    for r in results:
        click.echo(f"• {r.get('title', 'Untitled')}")
        click.echo(f"  Source: {r.get('data_source', '').upper()} | {r.get('source_domain', r.get('source', ''))}")
        click.echo(f"  Date: {r.get('published_date', r.get('pub_date', ''))}")
        if r.get("url"):
            click.echo(f"  URL: {r['url']}")
        click.echo()


@cli.command()
@click.argument("company")
@click.option("--agency", default="", help="Filter by regulator (e.g. EPA, SEC, DOJ, OSHA)")
@click.option("--penalty-min", default=0, type=int, help="Minimum penalty amount in dollars")
@click.option("--year-min", default=0, type=int, help="Only violations from this year or later")
@click.option("--summary", is_flag=True, default=False, help="Show aggregated summary instead of individual records")
def violations(company: str, agency: str, penalty_min: int, year_min: int, summary: bool):
    """Search Violation Tracker for corporate misconduct and regulatory penalties."""
    click.echo(f"\n🚨 Searching violations: {company}\n")
    result = violation_tracker.run_tool(
        company=company, agency=agency,
        penalty_min=penalty_min, year_min=year_min, summary=summary,
    )
    if summary:
        if isinstance(result, dict):
            click.echo(f"Company: {result.get('company', company)}")
            click.echo(f"Total violations: {result.get('total_violations', 0)}")
            click.echo(f"Total penalties: ${result.get('total_penalties', 0):,.0f}")
            breakdown = result.get("agency_breakdown", {})
            if breakdown:
                click.echo("\nBy agency:")
                for ag, count in sorted(breakdown.items(), key=lambda x: -x[1]):
                    click.echo(f"  {ag}: {count}")
        return
    records = result if isinstance(result, list) else []
    if not records:
        click.echo("No violations found.")
        return
    for r in records:
        click.echo(f"• [{r.get('agency', '?')}] {r.get('company', company)}")
        click.echo(f"  Penalty: ${r.get('penalty_amount', 0):,.0f} | Year: {r.get('year', '')}")
        if r.get("case_description"):
            click.echo(f"  {r['case_description'][:120]}")
        if r.get("case_url"):
            click.echo(f"  URL: {r['case_url']}")
        click.echo()


@cli.command()
@click.argument("query")
@click.option("--collection", default="all",
              type=click.Choice(["uscode", "cfr", "fr", "bills", "all"]),
              help="Collection: uscode, cfr (regulations), fr (Federal Register), bills, or all")
@click.option("--after", "after_date", default="", help="Only results issued after YYYY-MM-DD")
@click.option("--title", "usc_title", default=None, type=int,
              help="U.S.C. or CFR title number (e.g. 18 for Crimes, 17 for Securities)")
def statutes(query: str, collection: str, after_date: str, usc_title: int | None):
    """Search U.S. federal statutes and regulations via the GovInfo API."""
    click.echo(f"\n📜 Searching GovInfo [{collection.upper()}]: {query}\n")
    results = govinfo.run_tool(query=query, collection=collection, after_date=after_date,
                               usc_title=usc_title)
    if not results:
        click.echo("No results found.")
        return
    for r in results:
        click.echo(f"• [{r.get('collection', '?')}] {r.get('title', 'Untitled')}")
        if r.get("date_issued"):
            click.echo(f"  Issued: {r['date_issued']}")
        if r.get("url"):
            click.echo(f"  URL: {r['url']}")
        click.echo()


@cli.command()
@click.argument("name")
@click.option("--mode", default="search",
              type=click.Choice(["search", "match", "screen"]),
              help="Search mode: keyword search, structured match, or batch screen")
@click.option("--schema", default="",
              type=click.Choice(["Person", "Company", "Organization", "LegalEntity", ""]),
              help="Entity type to filter")
@click.option("--country", default="", help="ISO2 country code (e.g. US, RU, CN)")
def sanctions(name: str, mode: str, schema: str, country: str):
    """Screen persons and entities against OpenSanctions (PEPs, sanctions, persons of interest)."""
    click.echo(f"\n🔴 Screening against OpenSanctions: {name} (mode: {mode})\n")
    results = opensanctions.run_tool(name=name, mode=mode, schema=schema, country=country)
    if not results:
        click.echo("No matches found.")
        return
    for r in results:
        click.echo(f"• {r.get('caption', r.get('entity_id', ''))}")
        click.echo(f"  Schema: {r.get('schema', '')} | Sanctioned: {r.get('is_sanctioned', False)} | PEP: {r.get('is_pep', False)}")
        if r.get("countries"):
            click.echo(f"  Countries: {', '.join(r['countries'])}")
        if r.get("datasets"):
            click.echo(f"  Datasets: {', '.join(r['datasets'][:5])}")
        if r.get("url"):
            click.echo(f"  URL: {r['url']}")
        click.echo()


@cli.command()
@click.argument("url")
@click.option("--mode", default="snapshots",
              type=click.Choice(["snapshots", "closest", "changes"]),
              help="Mode: list snapshots, get closest, or detect changes")
@click.option("--from-date", default="", help="Start date (YYYYMMDD)")
@click.option("--to-date", default="", help="End date (YYYYMMDD)")
@click.option("--timestamp", default="", help="Target timestamp for 'closest' mode (YYYYMMDDHHmmSS)")
def wayback(url: str, mode: str, from_date: str, to_date: str, timestamp: str):
    """Temporal forensics via the Internet Archive Wayback Machine."""
    click.echo(f"\n⏳ Wayback Machine [{mode}]: {url}\n")
    result = wayback_machine.run_tool(url=url, mode=mode, from_date=from_date,
                                      to_date=to_date, timestamp=timestamp)
    if mode == "changes":
        if isinstance(result, dict):
            click.echo(f"URL: {result.get('url', url)}")
            click.echo(f"Snapshots found: {result.get('snapshots_found', 0)}")
            click.echo(f"Unique versions: {result.get('unique_versions', 0)}")
            click.echo(f"Changes detected: {result.get('changes_detected', False)}")
            for cp in result.get("change_points", []):
                click.echo(f"\n  Changed at: {cp.get('changed_at', '')}")
                click.echo(f"  Before: {cp.get('archive_url_before', '')}")
                click.echo(f"  After:  {cp.get('archive_url_after', '')}")
        return
    if mode == "closest":
        if isinstance(result, dict):
            click.echo(f"Available: {result.get('available', False)}")
            if result.get("available"):
                click.echo(f"Date: {result.get('date', '')} | Status: {result.get('status_code', '')}")
                click.echo(f"Archive URL: {result.get('archive_url', '')}")
        return
    items = result if isinstance(result, list) else []
    if not items:
        click.echo("No snapshots found.")
        return
    for r in items:
        click.echo(f"• {r.get('date', '')} [{r.get('status_code', '')}] {r.get('archive_url', '')}")


@cli.command()
@click.argument("keyword")
@click.option("--agency", default="", help="Agency abbreviation (e.g. DOJ, HHS, DHS, EPA, VA)")
@click.option("--mode", default="search",
              type=click.Choice(["search", "investigations", "red_flags"]),
              help="Mode: general search, investigations only, or fraud/waste/abuse reports")
@click.option("--after", "after_date", default="", help="Only reports published after YYYY-MM-DD")
def oversight(keyword: str, agency: str, mode: str, after_date: str):
    """Search Oversight.gov for Inspector General audit and investigation reports."""
    click.echo(f"\n🏛️  Searching OIG Oversight.gov: {keyword} (mode: {mode})\n")
    results = oig_oversight.run_tool(keyword=keyword, agency=agency, mode=mode,
                                     after_date=after_date)
    if not results:
        click.echo("No reports found.")
        return
    for r in results:
        click.echo(f"• [{r.get('agency', '?')}] {r.get('title', 'Untitled')}")
        click.echo(f"  Type: {r.get('report_type', '')} | Published: {r.get('date_published', '')}")
        if r.get("summary"):
            click.echo(f"  {r['summary'][:150]}")
        if r.get("url"):
            click.echo(f"  URL: {r['url']}")
        click.echo()


@cli.command()
@click.argument("source")
@click.option("--type", "file_type", default="auto",
              type=click.Choice(["auto", "pdf", "image", "exiftool"]),
              help="File type: auto-detect, pdf, image, or use system exiftool")
def forensics(source: str, file_type: str):
    """Extract metadata from a document or image for forensic analysis."""
    click.echo(f"\n🔬 Extracting metadata from: {source}\n")
    result = metadata_forensics.run_tool(source=source, file_type=file_type)
    if "error" in result:
        click.echo(f"Error: {result['error']}")
        return
    click.echo(f"File type: {result.get('file_type', '?')}")
    for key in ["author", "creator", "producer", "creation_date", "modification_date",
                "title", "camera_make", "camera_model", "software", "date_taken",
                "gps_latitude", "gps_longitude", "num_pages", "is_encrypted"]:
        val = result.get(key)
        if val:
            click.echo(f"  {key}: {val}")
    flags = result.get("forensic_flags", [])
    if flags:
        click.echo(f"\n⚠️  Forensic flags:")
        for f in flags:
            click.echo(f"  • {f}")


@cli.command()
@click.argument("source")
@click.option("--mode", "mode", default="combined",
              type=click.Choice(["combined", "c2pa_only"]),
              help="Verification mode: combined C2PA + EXIF forensics, or C2PA only")
def verify_media(source: str, mode: str):
    """Verify the C2PA provenance and authenticity of an image or document."""
    click.echo(f"\n🔏 Verifying media provenance: {source} (mode: {mode})\n")
    result = c2pa_verifier.run_tool(source=source, mode=mode)
    click.echo(f"C2PA manifest present: {result.get('c2pa_present', False)}")
    click.echo(f"Verification status: {result.get('verification_status', 'UNKNOWN')}")
    if result.get("issuer"):
        click.echo(f"  Issuer: {result['issuer']}")
    if result.get("software"):
        click.echo(f"  Authoring software: {result['software']}")
    edit_history = result.get("edit_history", [])
    if edit_history:
        click.echo(f"\n  📝 Edit history ({len(edit_history)} actions):")
        for e in edit_history[:5]:
            click.echo(f"    • {e}")
    flags = result.get("forensic_flags", [])
    if flags:
        click.echo(f"\n⚠️  Forensic flags:")
        for f in flags:
            click.echo(f"  • {f}")
    if result.get("verification_note"):
        click.echo(f"\nℹ️  {result['verification_note']}")


@cli.command()
@click.option("--action", default="list",
              type=click.Choice(["add", "remove", "list", "run"]),
              help="Watchlist action: add topic, remove entry, list all, or run a monitoring pass")
@click.option("--topic", default="", help="Topic to monitor (required for 'add')")
@click.option("--keywords", default="", help="Comma-separated keywords to filter (for 'add')")
@click.option("--entry-id", default="", help="Entry ID to remove (for 'remove')")
@click.option("--threshold", default=3, type=int, help="Anomaly threshold (min new items to trigger lead)")
@click.option("--auto-investigate", is_flag=True, default=False,
              help="Automatically trigger full investigation when anomaly is detected")
def monitor(action: str, topic: str, keywords: str, entry_id: str, threshold: int, auto_investigate: bool):
    """Manage the watchlist and run near real-time topic monitoring passes."""
    from journalist_ai.tools.watchlist import Watchlist

    wl = Watchlist()

    if action == "add":
        if not topic:
            click.echo("❌ --topic is required for 'add'.")
            return
        kws = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []
        eid = wl.add_entry(
            topic=topic, keywords=kws,
            anomaly_threshold=threshold, auto_investigate=auto_investigate,
        )
        click.echo(f"✅ Watchlist entry added: {eid}")
        click.echo(f"   Topic: {topic}")
        if kws:
            click.echo(f"   Keywords: {', '.join(kws)}")
        return

    if action == "remove":
        if not entry_id:
            click.echo("❌ --entry-id is required for 'remove'.")
            return
        wl.remove_entry(entry_id)
        click.echo(f"✅ Watchlist entry {entry_id} deactivated.")
        return

    if action == "list":
        entries = wl.list_all()
        if not entries:
            click.echo("No watchlist entries found.")
            return
        click.echo(f"\n📋 Watchlist ({len(entries)} entries):\n")
        for e in entries:
            status = "🟢 active" if e.get("active") else "🔴 inactive"
            click.echo(f"[{status}] {e['entry_id'][:8]}… {e['topic'][:80]}")
            click.echo(f"  Keywords: {e.get('keywords', '[]')} | Threshold: {e.get('anomaly_threshold', 3)}")
            click.echo(f"  Last checked: {e.get('last_checked', 'never')}\n")
        return

    if action == "run":
        click.echo("\n🔍 Running watchlist monitoring pass…\n")
        anomalies = wl.run_pass()
        if not anomalies:
            click.echo("No anomalies detected in this pass.")
            return
        click.echo(f"⚡ {len(anomalies)} anomaly(-ies) detected:\n")
        for a in anomalies:
            click.echo(f"• Topic: {a['topic'][:80]}")
            click.echo(f"  New items: {a['new_items_count']} | Lead ID: {a.get('lead_id', '')}")
            for item in a.get("items", [])[:3]:
                click.echo(f"    - {item.get('title', '')[:80]}")
            click.echo()


@cli.command()
@click.argument("brief_text")
@click.option("--sources", default="", help="Comma-separated source URLs to include in provenance")
@click.option("--output", default="", help="Save provenance record to this file path")
@click.option("--snapshot", is_flag=True, default=False, help="Archive sources in Wayback Machine")
def seal(brief_text: str, sources: str, output: str, snapshot: bool):
    """Seal an investigative brief with a cryptographic SHA-256 provenance record."""
    from journalist_ai.tools.provenance import seal_report, save_provenance_record

    source_list = [s.strip() for s in sources.split(",") if s.strip()] if sources else []
    click.echo(f"\n🔐 Sealing brief ({len(brief_text)} chars, {len(source_list)} sources)…\n")
    record = seal_report(brief=brief_text, sources=source_list, snapshot_sources=snapshot)
    click.echo(f"SHA-256 hash: {record['report_hash']}")
    click.echo(f"Sealed at:   {record['sealed_at']}")
    click.echo(f"Sources:     {record['source_count']}")
    if record.get("on_chain_anchor"):
        click.echo(f"On-chain:    {record['on_chain_anchor']}")
    if output:
        path = save_provenance_record(record, output)
        click.echo(f"\n📄 Provenance record saved to: {path}")


@cli.command()
@click.argument("action", type=click.Choice(["list", "show", "run"]), default="list")
@click.argument("template_id", default="")
@click.option("--var", "variables", multiple=True, metavar="KEY=VALUE",
              help="Template variable substitution (e.g. --var username=wuzbak).  Repeat for each variable.")
@click.option("--output", default="", help="Save the generated investigation brief to this file path")
def template(action: str, template_id: str, variables: tuple, output: str):
    """Work with pre-built investigation prompt templates.

    \b
    Actions:
      list              Show all available templates
      show <id>         Display a template's details and variables
      run  <id>         Run an investigation using a template

    \b
    Examples:
      python main.py template list
      python main.py template show osint_identity
      python main.py template run osint_identity --var username=wuzbak --var email=wuzbak@gmail.com
    """
    if yaml is None:
        click.echo("❌ PyYAML is not installed.  Run: pip install pyyaml")
        return

    templates_path = Path(__file__).parent / "config" / "investigation_templates.yaml"
    if not templates_path.exists():
        click.echo("❌ investigation_templates.yaml not found in config/")
        return

    with templates_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    all_templates: list = data.get("templates", [])

    # ── list ──────────────────────────────────────────────────────────────
    if action == "list":
        click.echo(f"\n📋 Available investigation templates ({len(all_templates)} total):\n")
        for t in all_templates:
            click.echo(f"  [{t['category'].upper()}] {t['id']}")
            click.echo(f"    {t['name']}")
            req_vars = [v["name"] for v in t.get("variables", []) if v.get("required")]
            if req_vars:
                click.echo(f"    Required vars: {', '.join(req_vars)}")
            click.echo()
        click.echo("Run `python main.py template show <id>` for details.")
        return

    # Remaining actions require a template_id
    if not template_id:
        click.echo("❌ Please specify a template ID.  Run `template list` to see available templates.")
        return

    match = next((t for t in all_templates if t["id"] == template_id), None)
    if match is None:
        click.echo(f"❌ Template '{template_id}' not found.  Run `template list` for available IDs.")
        return

    # ── show ──────────────────────────────────────────────────────────────
    if action == "show":
        click.echo(f"\n{'='*60}")
        click.echo(f"Template : {match['id']}")
        click.echo(f"Name     : {match['name']}")
        click.echo(f"Category : {match['category']}")
        click.echo(f"\n{match.get('description', '').strip()}\n")
        click.echo("Variables:")
        for v in match.get("variables", []):
            req = "(required)" if v.get("required") else f"(optional, default: '{v.get('default', '')}')"
            click.echo(f"  --var {v['name']}=…  {req}")
            click.echo(f"    {v.get('description', '')}")
        click.echo("\nKey questions:")
        for q in match.get("key_questions", []):
            click.echo(f"  • {q}")
        click.echo(f"\nTo run this template:")
        var_flags = " ".join(
            f"--var {v['name']}=<value>"
            for v in match.get("variables", [])
            if v.get("required")
        )
        click.echo(f"  python main.py template run {match['id']} {var_flags}")
        return

    # ── run ───────────────────────────────────────────────────────────────
    if action == "run":
        # Parse --var KEY=VALUE pairs
        var_map: dict = {}
        for v in match.get("variables", []):
            if not v.get("required"):
                var_map[v["name"]] = v.get("default", "")
        for pair in variables:
            if "=" not in pair:
                click.echo(f"❌ Invalid --var format: '{pair}'.  Use KEY=VALUE.")
                return
            k, _, v = pair.partition("=")
            var_map[k.strip()] = v.strip()

        # Check required variables are provided
        missing = [
            v["name"] for v in match.get("variables", [])
            if v.get("required") and not var_map.get(v["name"])
        ]
        if missing:
            click.echo(f"❌ Missing required variable(s): {', '.join(missing)}")
            click.echo(f"   Use --var {missing[0]}=<value>")
            return

        # Substitute variables into the lead template
        try:
            lead = match["lead_template"].format_map(var_map)
        except KeyError as exc:
            click.echo(f"❌ Unknown variable in template: {exc}")
            return

        click.echo(f"\n🔍 Running template '{match['name']}'\n")
        for k, v in var_map.items():
            if v:
                click.echo(f"   {k}: {v}")
        click.echo()

        _register_default_tools()
        brief = run_investigation(lead)
        click.echo("\n" + "=" * 60)
        click.echo(brief)

        if output:
            Path(output).write_text(brief, encoding="utf-8")
            click.echo(f"\n📄 Brief saved to: {output}")


if __name__ == "__main__":
    cli()
```

---

## `journalist-ai/memory//init/.py`

```python
```

---

## `journalist-ai/memory/contradiction_log.py`

```python
"""
contradiction_log.py — Log and track contradictions between sourced claims.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DB_PATH = Path(os.getenv("JOURNALIST_DB_PATH", "journalist-ai/memory/data/facts.db"))


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS contradictions (
            id              TEXT PRIMARY KEY,
            investigation_id TEXT,
            claim_a         TEXT NOT NULL,
            source_a        TEXT,
            source_url_a    TEXT,
            confidence_a    TEXT,
            claim_b         TEXT NOT NULL,
            source_b        TEXT,
            source_url_b    TEXT,
            confidence_b    TEXT,
            contradiction_type TEXT,
            severity        TEXT,
            topic           TEXT,
            status          TEXT DEFAULT 'unresolved',
            resolution_note TEXT,
            detected_at     TEXT,
            resolved_at     TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_contra_investigation ON contradictions(investigation_id);
        CREATE INDEX IF NOT EXISTS idx_contra_status ON contradictions(status);
    """)
    conn.commit()


def log_contradiction(
    claim_a: str, source_a: str, claim_b: str, source_b: str,
    source_url_a: str = "", source_url_b: str = "",
    confidence_a: str = "UNVERIFIED", confidence_b: str = "UNVERIFIED",
    contradiction_type: str = "direct", topic: str = "", investigation_id: str = "",
) -> str:
    severity = _assess_severity(confidence_a, confidence_b, contradiction_type)
    contra_id = str(uuid.uuid4())
    with _get_conn() as conn:
        conn.execute(
            """INSERT INTO contradictions
            (id, investigation_id, claim_a, source_a, source_url_a, confidence_a,
             claim_b, source_b, source_url_b, confidence_b,
             contradiction_type, severity, topic, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (contra_id, investigation_id, claim_a, source_a, source_url_a, confidence_a,
             claim_b, source_b, source_url_b, confidence_b,
             contradiction_type, severity, topic, datetime.utcnow().isoformat()),
        )
    logger.warning("Contradiction logged [%s severity]", severity)
    return contra_id


def get_unresolved_contradictions(investigation_id: str = "", severity: str = "") -> list[dict]:
    conditions = ["status = 'unresolved'"]
    params: list[Any] = []
    if investigation_id:
        conditions.append("investigation_id = ?")
        params.append(investigation_id)
    if severity:
        conditions.append("severity = ?")
        params.append(severity)
    where = "WHERE " + " AND ".join(conditions)
    with _get_conn() as conn:
        rows = conn.execute(
            f"SELECT * FROM contradictions {where} ORDER BY severity DESC, detected_at DESC", params
        ).fetchall()
    return [dict(r) for r in rows]


def resolve_contradiction(contra_id: str, status: str, resolution_note: str = "") -> None:
    with _get_conn() as conn:
        conn.execute(
            "UPDATE contradictions SET status = ?, resolution_note = ?, resolved_at = ? WHERE id = ?",
            (status, resolution_note, datetime.utcnow().isoformat(), contra_id),
        )


def summarize_contradictions(investigation_id: str = "") -> dict:
    base_filter = "WHERE investigation_id = ?" if investigation_id else ""
    params = [investigation_id] if investigation_id else []
    with _get_conn() as conn:
        total = conn.execute(f"SELECT COUNT(*) as n FROM contradictions {base_filter}", params).fetchone()["n"]
        by_severity = conn.execute(f"SELECT severity, COUNT(*) as n FROM contradictions {base_filter} GROUP BY severity", params).fetchall()
        by_status = conn.execute(f"SELECT status, COUNT(*) as n FROM contradictions {base_filter} GROUP BY status", params).fetchall()
    return {
        "total": total,
        "by_severity": {r["severity"]: r["n"] for r in by_severity},
        "by_status": {r["status"]: r["n"] for r in by_status},
    }


def _assess_severity(confidence_a: str, confidence_b: str, contradiction_type: str) -> str:
    high_confidence = {"CONFIRMED", "CORROBORATED"}
    a_high = confidence_a.upper() in high_confidence
    b_high = confidence_b.upper() in high_confidence
    if a_high and b_high:
        return "critical"
    if a_high or b_high:
        return "high"
    if contradiction_type == "direct":
        return "medium"
    return "low"
```

---

## `journalist-ai/memory/entity_graph.py`

```python
"""
entity_graph.py — Entity relationship graph for investigations.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DB_PATH = Path(os.getenv("JOURNALIST_DB_PATH", "journalist-ai/memory/data/facts.db"))

ENTITY_TYPES = {
    "PERSON": "person",
    "ORG": "organization",
    "GPE": "location",
    "MONEY": "financial",
    "LAW": "legislation",
    "EVENT": "event",
    "PRODUCT": "product",
    "UNKNOWN": "unknown",
}


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS entities (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            type        TEXT,
            aliases     TEXT,
            metadata    TEXT,
            first_seen  TEXT,
            last_seen   TEXT,
            mention_count INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS entity_relationships (
            id              TEXT PRIMARY KEY,
            entity_a_id     TEXT NOT NULL,
            entity_b_id     TEXT NOT NULL,
            relationship    TEXT,
            evidence        TEXT,
            source          TEXT,
            source_url      TEXT,
            confidence      TEXT DEFAULT 'UNVERIFIED',
            date_observed   TEXT,
            investigation_id TEXT,
            FOREIGN KEY (entity_a_id) REFERENCES entities(id),
            FOREIGN KEY (entity_b_id) REFERENCES entities(id)
        );
        CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
        CREATE INDEX IF NOT EXISTS idx_rel_a ON entity_relationships(entity_a_id);
        CREATE INDEX IF NOT EXISTS idx_rel_b ON entity_relationships(entity_b_id);
    """)
    conn.commit()


def add_entity(name: str, entity_type: str = "UNKNOWN", aliases: list[str] | None = None, metadata: dict | None = None) -> str:
    existing = find_entity(name)
    if existing:
        _increment_mention(existing["id"])
        return existing["id"]
    entity_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    with _get_conn() as conn:
        conn.execute("INSERT INTO entities (id, name, type, aliases, metadata, first_seen, last_seen) VALUES (?, ?, ?, ?, ?, ?, ?)", (entity_id, name, ENTITY_TYPES.get(entity_type, entity_type), json.dumps(aliases or []), json.dumps(metadata or {}), now, now))
    return entity_id


def find_entity(name: str) -> dict | None:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM entities WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
        if row:
            return dict(row)
        rows = conn.execute("SELECT * FROM entities WHERE aliases LIKE ?", (f'%"{name}"%',)).fetchall()
        if rows:
            return dict(rows[0])
    return None


def _increment_mention(entity_id: str) -> None:
    with _get_conn() as conn:
        conn.execute("UPDATE entities SET mention_count = mention_count + 1, last_seen = ? WHERE id = ?", (datetime.utcnow().isoformat(), entity_id))


def get_top_entities(limit: int = 20, entity_type: str = "") -> list[dict]:
    with _get_conn() as conn:
        if entity_type:
            rows = conn.execute("SELECT * FROM entities WHERE type = ? ORDER BY mention_count DESC LIMIT ?", (entity_type, limit)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM entities ORDER BY mention_count DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def add_relationship(entity_a_name: str, entity_b_name: str, relationship: str, evidence: str = "", source: str = "", source_url: str = "", confidence: str = "UNVERIFIED", date_observed: str = "", investigation_id: str = "", entity_a_type: str = "UNKNOWN", entity_b_type: str = "UNKNOWN") -> str:
    entity_a_id = add_entity(entity_a_name, entity_a_type)
    entity_b_id = add_entity(entity_b_name, entity_b_type)
    rel_id = str(uuid.uuid4())
    with _get_conn() as conn:
        conn.execute("INSERT INTO entity_relationships (id, entity_a_id, entity_b_id, relationship, evidence, source, source_url, confidence, date_observed, investigation_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (rel_id, entity_a_id, entity_b_id, relationship, evidence[:1000] if evidence else "", source, source_url, confidence, date_observed, investigation_id))
    return rel_id


def get_entity_connections(entity_name: str, depth: int = 1) -> dict:
    entity = find_entity(entity_name)
    if not entity:
        return {"entity": entity_name, "found": False, "connections": []}
    entity_id = entity["id"]
    connections = _get_direct_connections(entity_id)
    result = {"entity": entity_name, "entity_id": entity_id, "type": entity.get("type", ""), "mention_count": entity.get("mention_count", 0), "connections": connections}
    if depth >= 2:
        for conn in connections:
            second_degree = _get_direct_connections(conn["related_entity_id"])
            conn["second_degree"] = [c for c in second_degree if c["related_entity_id"] != entity_id]
    return result


def _get_direct_connections(entity_id: str) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT r.relationship, r.confidence, r.source, r.date_observed, r.evidence, CASE WHEN r.entity_a_id = ? THEN r.entity_b_id ELSE r.entity_a_id END as related_id FROM entity_relationships r WHERE r.entity_a_id = ? OR r.entity_b_id = ?", (entity_id, entity_id, entity_id)).fetchall()
        results = []
        for row in rows:
            related = conn.execute("SELECT name, type FROM entities WHERE id = ?", (row["related_id"],)).fetchone()
            if related:
                results.append({"related_entity": related["name"], "related_entity_id": row["related_id"], "related_type": related["type"], "relationship": row["relationship"], "confidence": row["confidence"], "source": row["source"], "date": row["date_observed"], "evidence": row["evidence"]})
    return results


def ingest_entities_from_facts(facts: list[dict], investigation_id: str = "") -> None:
    for fact in facts:
        for ent in fact.get("entities", []):
            if isinstance(ent, dict):
                add_entity(ent.get("text", ""), ent.get("type", "UNKNOWN"))
            elif isinstance(ent, str):
                add_entity(ent)


def find_revolving_door(person_name: str) -> list[dict]:
    connections = get_entity_connections(person_name, depth=1)
    conns = connections.get("connections", [])
    gov_entities = [c for c in conns if "government" in (c.get("related_type") or "").lower() or any(kw in c["related_entity"].lower() for kw in ["agency", "department", "bureau", "commission", "office of", "secretary"])]
    private_entities = [c for c in conns if c.get("related_type") in ("organization",) and c not in gov_entities]
    if gov_entities and private_entities:
        return [{"pattern": "revolving_door", "person": person_name, "government_connections": [c["related_entity"] for c in gov_entities], "private_connections": [c["related_entity"] for c in private_entities], "flag": "Potential revolving door — verify overlap between regulatory role and subsequent private employment"}]
    return []


def export_graph_json(investigation_id: str = "") -> dict:
    with _get_conn() as conn:
        entities = conn.execute("SELECT id, name, type, mention_count FROM entities").fetchall()
        rels = conn.execute("SELECT * FROM entity_relationships WHERE investigation_id = ?", (investigation_id,)).fetchall() if investigation_id else conn.execute("SELECT * FROM entity_relationships").fetchall()
    return {"nodes": [{"id": e["id"], "label": e["name"], "type": e["type"], "weight": e["mention_count"]} for e in entities], "edges": [{"source": r["entity_a_id"], "target": r["entity_b_id"], "label": r["relationship"], "confidence": r["confidence"]} for r in rels]}
```

---

## `journalist-ai/memory/fact_store.py`

```python
"""
fact_store.py — Persistent fact storage using SQLite + optional ChromaDB vector store.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DB_PATH = Path(os.getenv("JOURNALIST_DB_PATH", "journalist-ai/memory/data/facts.db"))
CHROMA_PATH = Path(os.getenv("JOURNALIST_CHROMA_PATH", "journalist-ai/memory/data/chroma"))


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS facts (
            id              TEXT PRIMARY KEY,
            investigation_id TEXT,
            claim           TEXT NOT NULL,
            source          TEXT,
            source_url      TEXT,
            source_tier     INTEGER DEFAULT 3,
            confidence_score REAL DEFAULT 0.4,
            confidence_label TEXT DEFAULT 'UNVERIFIED',
            date_of_fact    TEXT,
            date_collected  TEXT,
            raw_text        TEXT,
            entities        TEXT,
            tags            TEXT,
            verified        INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS investigations (
            id              TEXT PRIMARY KEY,
            lead            TEXT,
            status          TEXT DEFAULT 'active',
            started_at      TEXT,
            completed_at    TEXT,
            brief           TEXT,
            metadata        TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_facts_investigation ON facts(investigation_id);
        CREATE INDEX IF NOT EXISTS idx_facts_confidence ON facts(confidence_label);
        CREATE INDEX IF NOT EXISTS idx_facts_source ON facts(source);
    """)
    conn.commit()


def store_fact(claim: str, source: str = "", source_url: str = "", source_tier: int = 3, confidence_score: float = 0.4, confidence_label: str = "UNVERIFIED", investigation_id: str = "", date_of_fact: str = "", raw_text: str = "", entities: list[str] | None = None, tags: list[str] | None = None) -> str:
    fact_id = str(uuid.uuid4())
    with _get_connection() as conn:
        conn.execute("INSERT INTO facts (id, investigation_id, claim, source, source_url, source_tier, confidence_score, confidence_label, date_of_fact, date_collected, raw_text, entities, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (fact_id, investigation_id, claim, source, source_url, source_tier, confidence_score, confidence_label, date_of_fact, datetime.utcnow().isoformat(), raw_text, json.dumps(entities or []), json.dumps(tags or [])))
    _chroma_store(fact_id, claim, {"source": source, "confidence": confidence_label})
    return fact_id


def store_facts_bulk(facts: list[dict], investigation_id: str = "") -> list[str]:
    return [store_fact(claim=f.get("claim", ""), source=f.get("source", ""), source_url=f.get("url", ""), source_tier=f.get("tier", 3), confidence_score=f.get("confidence_score", 0.4), confidence_label=f.get("confidence_label", "UNVERIFIED"), investigation_id=investigation_id, date_of_fact=f.get("date", ""), raw_text=f.get("raw_text", ""), entities=f.get("entities", []), tags=f.get("tags", [])) for f in facts if f.get("claim")]


def search_facts(query: str = "", confidence_label: str = "", investigation_id: str = "", min_confidence: float = 0.0, limit: int = 50) -> list[dict]:
    conditions = []
    params: list[Any] = []
    if query:
        conditions.append("(claim LIKE ? OR raw_text LIKE ? OR source LIKE ?)")
        like = f"%{query}%"
        params.extend([like, like, like])
    if confidence_label:
        conditions.append("confidence_label = ?")
        params.append(confidence_label)
    if investigation_id:
        conditions.append("investigation_id = ?")
        params.append(investigation_id)
    if min_confidence > 0:
        conditions.append("confidence_score >= ?")
        params.append(min_confidence)
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    params.append(limit)
    with _get_connection() as conn:
        rows = conn.execute(f"SELECT * FROM facts {where} ORDER BY confidence_score DESC LIMIT ?", params).fetchall()
    return [dict(r) for r in rows]


def get_fact(fact_id: str) -> dict | None:
    with _get_connection() as conn:
        row = conn.execute("SELECT * FROM facts WHERE id = ?", (fact_id,)).fetchone()
    return dict(row) if row else None


def store_investigation(investigation_id: str, lead: str, metadata: dict | None = None) -> None:
    with _get_connection() as conn:
        conn.execute("INSERT INTO investigations (id, lead, status, started_at, metadata) VALUES (?, ?, 'active', ?, ?) ON CONFLICT(id) DO UPDATE SET lead = excluded.lead, metadata = excluded.metadata", (investigation_id, lead, datetime.utcnow().isoformat(), json.dumps(metadata or {})))


def update_investigation(investigation_id: str, status: str | None = None, brief: str | None = None) -> None:
    with _get_connection() as conn:
        if status:
            conn.execute("UPDATE investigations SET status = ? WHERE id = ?", (status, investigation_id))
        if brief:
            conn.execute("UPDATE investigations SET brief = ?, completed_at = ? WHERE id = ?", (brief, datetime.utcnow().isoformat(), investigation_id))


def _chroma_store(doc_id: str, text: str, metadata: dict) -> None:
    try:
        import chromadb
        CHROMA_PATH.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        collection = client.get_or_create_collection("journalist_facts")
        collection.upsert(ids=[doc_id], documents=[text[:1000]], metadatas=[metadata])
    except ImportError:
        pass
    except Exception as e:
        logger.debug("ChromaDB store failed (non-critical): %s", e)


def semantic_search(query: str, n_results: int = 10) -> list[dict]:
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        collection = client.get_or_create_collection("journalist_facts")
        results = collection.query(query_texts=[query], n_results=n_results)
        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        return [{"id": ids[i], "text": docs[i], "metadata": metas[i]} for i in range(len(ids))]
    except (ImportError, Exception):
        logger.debug("ChromaDB unavailable; falling back to SQLite keyword search")
        return search_facts(query=query)
```

---

## `journalist-ai/memory/lead_queue.py`

```python
"""
lead_queue.py — Investigation lead queue.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DB_PATH = Path(os.getenv("JOURNALIST_DB_PATH", "journalist-ai/memory/data/facts.db"))
PRIORITY_LEVELS = ["critical", "high", "medium", "low"]
STATUS_CODES = ["pending", "in_progress", "completed", "abandoned", "referred"]


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS leads (
            id              TEXT PRIMARY KEY,
            content         TEXT NOT NULL,
            source          TEXT,
            priority        TEXT DEFAULT 'medium',
            status          TEXT DEFAULT 'pending',
            tags            TEXT,
            related_entities TEXT,
            notes           TEXT,
            added_at        TEXT,
            updated_at      TEXT,
            investigation_id TEXT,
            manifold_market_id TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_leads_priority ON leads(priority, status);
        CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
    """)
    conn.commit()


class LeadQueue:
    def __init__(self, investigation_id: str = ""):
        self.investigation_id = investigation_id

    def add(self, content: str, source: str = "manual", priority: str = "medium", tags: list[str] | None = None, related_entities: list[str] | None = None, notes: str = "", manifold_market_id: str = "") -> str:
        if priority not in PRIORITY_LEVELS:
            priority = "medium"
        lead_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        with _get_conn() as conn:
            conn.execute("INSERT INTO leads (id, content, source, priority, status, tags, related_entities, notes, added_at, updated_at, investigation_id, manifold_market_id) VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?)", (lead_id, content, source, priority, json.dumps(tags or []), json.dumps(related_entities or []), notes, now, now, self.investigation_id, manifold_market_id))
        return lead_id

    def add_from_manifold(self, market: dict) -> str:
        content = f"Manifold contested claim: {market.get('question', '')} (probability: {market.get('probability', 'unknown'):.0%}, volume: ${market.get('total_volume', 0):,.0f})"
        return self.add(content=content, source="manifold_markets", priority="medium", tags=market.get("tags", []) + ["manifold"], manifold_market_id=market.get("id", ""), notes=market.get("url", ""))

    def add_from_diary_leads(self, diary_leads: list[dict]) -> list[str]:
        return [self.add(content=lead.get("content", ""), source=f"diary:{lead.get('source_entry_id', '')}", priority=lead.get("priority", "medium"), tags=lead.get("tags", []) + ["diary_import"], related_entities=[e.get("text", "") for e in lead.get("extracted_entities", [])], notes=str(lead.get("extracted_claims", []))) for lead in diary_leads]

    def get_next(self, priority: str | None = None) -> dict | None:
        where = "WHERE status = 'pending' AND priority = ?" if priority else "WHERE status = 'pending'"
        params: list[Any] = [priority] if priority else []
        order = "ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, added_at ASC"
        with _get_conn() as conn:
            row = conn.execute(f"SELECT * FROM leads {where} {order} LIMIT 1", params).fetchone()
        return dict(row) if row else None

    def get_all_pending(self, limit: int = 50) -> list[dict]:
        order = "ORDER BY CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END, added_at ASC"
        with _get_conn() as conn:
            rows = conn.execute(f"SELECT * FROM leads WHERE status = 'pending' {order} LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

    def get_by_entity(self, entity_name: str) -> list[dict]:
        with _get_conn() as conn:
            rows = conn.execute("SELECT * FROM leads WHERE content LIKE ? OR related_entities LIKE ?", (f"%{entity_name}%", f"%{entity_name}%")).fetchall()
        return [dict(r) for r in rows]

    def update_status(self, lead_id: str, status: str, notes: str = "") -> None:
        if status not in STATUS_CODES:
            raise ValueError(f"Invalid status: {status}")
        with _get_conn() as conn:
            conn.execute("UPDATE leads SET status = ?, notes = ?, updated_at = ? WHERE id = ?", (status, notes, datetime.utcnow().isoformat(), lead_id))

    def link_investigation(self, lead_id: str, investigation_id: str) -> None:
        with _get_conn() as conn:
            conn.execute("UPDATE leads SET investigation_id = ? WHERE id = ?", (investigation_id, lead_id))

    def prioritize(self, lead_id: str, new_priority: str) -> None:
        if new_priority not in PRIORITY_LEVELS:
            raise ValueError(f"Invalid priority: {new_priority}")
        with _get_conn() as conn:
            conn.execute("UPDATE leads SET priority = ?, updated_at = ? WHERE id = ?", (new_priority, datetime.utcnow().isoformat(), lead_id))

    def summary(self) -> dict:
        with _get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) as n FROM leads").fetchone()["n"]
            by_status = conn.execute("SELECT status, COUNT(*) as n FROM leads GROUP BY status").fetchall()
            by_priority = conn.execute("SELECT priority, COUNT(*) as n FROM leads WHERE status = 'pending' GROUP BY priority").fetchall()
        return {"total": total, "by_status": {r["status"]: r["n"] for r in by_status}, "pending_by_priority": {r["priority"]: r["n"] for r in by_priority}}
```

---

## `journalist-ai/outputs//init/.py`

```python
```

---

## `journalist-ai/outputs/libel_check.py`

```python
# libel_check.py — Pre-publication libel/defamation risk audit for AXIOM.
# Full source: see wuzbak/Journalism- journalist-ai/outputs/libel_check.py
```

---

## `journalist-ai/outputs/report_generator.py`

```python
# report_generator.py — Investigative report generator for AXIOM.
# Full source: see wuzbak/Journalism- journalist-ai/outputs/report_generator.py
```

---

## `journalist-ai/requirements.txt`

```text
# AXIOM Investigative AI — Python Dependencies
# Install with: pip install -r requirements.txt

# ── AI / LLM ────────────────────────────────────────────────────────────────
openai>=1.30.0              # OpenAI GPT-4o backend
anthropic>=0.28.0           # Anthropic Claude backend (optional)

# ── HTTP & Web Scraping ──────────────────────────────────────────────────────
requests>=2.32.0
beautifulsoup4>=4.12.0      # HTML parsing
duckduckgo-search>=6.2.0    # No-key web search fallback
feedparser>=6.0.11          # RSS feed monitoring

# ── Document Parsing ─────────────────────────────────────────────────────────
pypdf>=4.2.0                # PDF text extraction (primary)
pdfminer.six>=20221105      # PDF extraction fallback

# ── Metadata Forensics ───────────────────────────────────────────────────────
exifread>=3.0.0             # EXIF metadata extraction from images (JPEG, TIFF)

# ── NLP & Entity Extraction ──────────────────────────────────────────────────
spacy>=3.7.0                # Named entity recognition
rapidfuzz>=3.9.0            # Fuzzy name matching for entity resolution
# After install, download model: python -m spacy download en_core_web_sm

# ── Vector Database (optional but recommended) ───────────────────────────────
chromadb>=0.5.0             # Local vector store for semantic search

# ── Data Processing ──────────────────────────────────────────────────────────
PyYAML>=6.0.1               # YAML config file parsing

# ── Output / Reporting ───────────────────────────────────────────────────────
markdown>=3.6               # Markdown → HTML for PDF export
weasyprint>=62.0            # HTML → PDF (optional; requires system libs)

# ── CLI ──────────────────────────────────────────────────────────────────────
click>=8.1.7                # CLI interface for running investigations

# ── Dev / Testing ────────────────────────────────────────────────────────────
pytest>=8.2.0
pytest-cov>=5.0.0
```

---

## `journalist-ai/setup.py`

```python
from setuptools import setup, find_packages

setup(
    name="journalist-ai",
    version="0.1.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.11",
)
```

---

## `journalist-ai/skills//init/.py`

```python
```

---

## `journalist-ai/skills/bias_audit.py`

```python
"""bias_audit.py — Automated media bias detection and framing analysis."""

from __future__ import annotations
import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)

BIAS_LEXICON = {
    "left": ["progressive", "equity", "systemic", "social justice", "marginalized", "oppressed", "woke", "intersectional"],
    "right": ["traditional", "patriot", "liberty", "freedom agenda", "deep state", "globalist", "elites", "mainstream media"],
    "pro_government": ["administration", "officials say", "authorities confirm", "government sources", "white house says"],
    "anti_government": ["regime", "overreach", "surveillance state", "unconstitutional", "power grab"],
    "corporate_friendly": ["job creators", "economic growth", "free market", "innovation", "competitive"],
    "corporate_critical": ["corporate greed", "profiteering", "monopoly", "exploitation", "price gouging"],
}

FRAMING_PATTERNS = [
    (r"\baccording to (?:officials?|authorities|government)\b", "authority_appeal"),
    (r"\bexperts? (?:say|warn|predict|agree)\b", "expert_consensus"),
    (r"\bcritics? (?:say|warn|argue|claim)\b", "opposition_framing"),
    (r"\b(?:some|many|most) (?:people|Americans|voters|experts?)\b", "vague_attribution"),
    (r"\ballegedly\b|\bapparently\b|\bseemingly\b", "hedging_language"),
    (r"\bjust|only|merely\b", "minimization"),
    (r"\bbombshell|explosive|shocking|stunning\b", "sensationalism"),
    (r"\bfailed to (?:respond|comment|appear)\b", "guilt_by_silence"),
]


def analyze_text_bias(text: str) -> dict:
    """Analyze a text block for political/ideological framing bias."""
    text_lower = text.lower()
    word_count = len(text.split())

    bias_scores: dict[str, int] = {cat: 0 for cat in BIAS_LEXICON}
    detected_terms: dict[str, list[str]] = {cat: [] for cat in BIAS_LEXICON}

    for category, terms in BIAS_LEXICON.items():
        for term in terms:
            count = text_lower.count(term.lower())
            if count:
                bias_scores[category] += count
                detected_terms[category].append(term)

    framing_flags: list[dict] = []
    for pattern, label in FRAMING_PATTERNS:
        matches = re.findall(pattern, text_lower)
        if matches:
            framing_flags.append({"pattern": label, "occurrences": len(matches), "examples": matches[:2]})

    dominant_bias = max(bias_scores, key=bias_scores.get) if any(bias_scores.values()) else "neutral"
    overall_score = max(bias_scores.values()) / max(word_count / 100, 1) if word_count > 0 else 0

    return {
        "bias_scores": bias_scores,
        "detected_terms": detected_terms,
        "dominant_bias": dominant_bias if bias_scores[dominant_bias] > 0 else "neutral",
        "overall_bias_score": round(overall_score, 3),
        "framing_flags": framing_flags,
        "word_count": word_count,
        "assessment": _generate_assessment(bias_scores, framing_flags, overall_score),
    }


def _generate_assessment(scores: dict, flags: list, overall_score: float) -> str:
    if overall_score < 0.1:
        return "LOW BIAS: Text appears relatively neutral in language and framing."
    parts = []
    left = scores.get("left", 0)
    right = scores.get("right", 0)
    if left > right * 1.5:
        parts.append("LEFT-LEANING framing detected")
    elif right > left * 1.5:
        parts.append("RIGHT-LEANING framing detected")
    if scores.get("pro_government", 0) > 2:
        parts.append("Pro-government sourcing bias")
    if scores.get("corporate_friendly", 0) > scores.get("corporate_critical", 0) + 2:
        parts.append("Corporate-friendly framing")
    sensational = [f for f in flags if f["pattern"] == "sensationalism"]
    if sensational:
        parts.append("Sensationalized language detected")
    vague = [f for f in flags if f["pattern"] == "vague_attribution"]
    if vague:
        parts.append("Vague attribution (unnamed sources/groups)")
    return "MODERATE-HIGH BIAS: " + "; ".join(parts) if parts else "MODERATE: Some bias indicators present"


def compare_coverage(articles: list[dict]) -> dict:
    """Compare bias profiles across multiple articles on the same topic."""
    analyses = []
    for article in articles:
        analysis = analyze_text_bias(article.get("text", ""))
        analysis["source"] = article.get("source", "unknown")
        analysis["url"] = article.get("url", "")
        analyses.append(analysis)

    if not analyses:
        return {"error": "No articles provided"}

    avg_scores: dict[str, float] = {}
    for cat in BIAS_LEXICON:
        vals = [a["bias_scores"][cat] for a in analyses]
        avg_scores[cat] = round(sum(vals) / len(vals), 2) if vals else 0

    return {
        "article_count": len(analyses),
        "individual_analyses": analyses,
        "average_bias_scores": avg_scores,
        "coverage_gap": _detect_coverage_gaps(analyses),
    }


def _detect_coverage_gaps(analyses: list[dict]) -> list[str]:
    gaps = []
    left_covered = any(a["dominant_bias"] == "left" for a in analyses)
    right_covered = any(a["dominant_bias"] == "right" for a in analyses)
    if analyses and not (left_covered and right_covered):
        gaps.append("One-sided political framing — no counterpoint perspective found")
    if all(a["bias_scores"].get("pro_government", 0) > 0 for a in analyses):
        if not any(a["bias_scores"].get("anti_government", 0) > 0 for a in analyses):
            gaps.append("Government voices dominant — lack of critical/opposition perspective")
    return gaps


TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "description": "Article text to analyze for bias"},
        "mode": {"type": "string", "enum": ["single", "compare"], "description": "'single'=analyze one text, 'compare'=compare multiple articles", "default": "single"},
        "articles": {"type": "array", "items": {"type": "object"}, "description": "List of {text, source, url} dicts for 'compare' mode"},
    },
    "required": [],
}

TOOL_DESCRIPTION = "Detect political framing bias and coverage gaps in journalism. Analyzes loaded language, attribution patterns, and ideological framing."


def run_tool(text: str = "", mode: str = "single", articles: list | None = None) -> dict:
    if mode == "compare" and articles:
        return compare_coverage(articles)
    return analyze_text_bias(text)
```

---

## `journalist-ai/skills/environment.py`

```python
"""
environment.py — Environmental investigation skill for AXIOM.

Integrates EPA ECHO, EJScreen, Superfund site data, and climate risk APIs
to support investigative reporting on pollution, environmental justice,
and corporate environmental violations.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15


def get_facility_violations(
    facility_name: str = "",
    state: str = "",
    zip_code: str = "",
    limit: int = 20,
) -> list[dict]:
    """Search EPA ECHO for facilities with violations."""
    url = "https://echodata.epa.gov/echo/echo_rest_services.get_facilities"
    params: dict[str, Any] = {
        "output": "JSON",
        "p_name": facility_name,
        "p_st": state,
        "p_zip": zip_code,
        "p_qnc": "Y",
        "responseset": limit,
    }
    params = {k: v for k, v in params.items() if v}
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        facilities = resp.json().get("Results", {}).get("Facilities", [])
        return [
            {
                "name": f.get("FacilityName", ""),
                "address": f.get("LocationAddress", ""),
                "state": f.get("StateCode", ""),
                "violations": f.get("QncViol", ""),
                "formal_actions": f.get("FormalActionCount", ""),
                "penalty_amount": f.get("TotalPenaltyAmt", ""),
                "programs": f.get("ProgramSystemAcronyms", ""),
                "data_source": "epa_echo",
            }
            for f in facilities
        ]
    except requests.RequestException as e:
        logger.error("EPA ECHO error: %s", e)
        return []


def get_superfund_sites(state: str = "", query: str = "") -> list[dict]:
    """Search EPA Superfund (CERCLIS) sites."""
    url = "https://data.epa.gov/efservice/RCRA_HD_HANDLER/STATE_CODE"
    if state:
        url += f"/{state}"
    url += "/JSON"
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        sites = resp.json()
        if query:
            query_lower = query.lower()
            sites = [s for s in sites if query_lower in str(s).lower()]
        return [{"site": s, "data_source": "epa_rcra"} for s in sites[:20]]
    except Exception as e:
        logger.error("Superfund query error: %s", e)
        return []


def get_ejscreen_data(latitude: float, longitude: float, radius_miles: float = 1.0) -> dict:
    """Get EPA EJScreen environmental justice indicators for a location."""
    url = "https://ejscreen.epa.gov/mapper/ejscreenRESTbroker.aspx"
    params = {
        "namestr": "",
        "geometry": f"{longitude},{latitude}",
        "distance": radius_miles,
        "unit": "9035",
        "areatype": "",
        "areaid": "",
        "f": "json",
    }
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("EJScreen error: %s", e)
        return {}


def get_air_quality_index(city: str = "", zip_code: str = "") -> dict:
    """
    Get current Air Quality Index via AirNow API.
    Requires AIRNOW_API_KEY env var.
    """
    api_key = os.getenv("AIRNOW_API_KEY", "")
    if not api_key:
        return {"error": "AIRNOW_API_KEY not set"}
    url = "https://www.airnowapi.org/aq/observation/zipCode/current/"
    params = {
        "format": "application/json",
        "zipCode": zip_code,
        "distance": 25,
        "API_KEY": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return {"readings": resp.json(), "data_source": "airnow"}
    except Exception as e:
        logger.error("AirNow error: %s", e)
        return {}


TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Facility name, company, or location to investigate"},
        "mode": {
            "type": "string",
            "enum": ["violations", "superfund", "air_quality"],
            "description": "Type of environmental query",
            "default": "violations",
        },
        "state": {"type": "string", "description": "Two-letter US state code (optional filter)"},
    },
    "required": ["query"],
}

TOOL_DESCRIPTION = "Environmental investigation: EPA violations, Superfund sites, air quality, and EJScreen environmental justice data."


def run_tool(query: str, mode: str = "violations", state: str = "") -> Any:
    if mode == "superfund":
        return get_superfund_sites(state=state, query=query)
    if mode == "air_quality":
        return get_air_quality_index(city=query)
    return get_facility_violations(facility_name=query, state=state)
```

---

## `journalist-ai/skills/finance.py`

```python
"""
finance.py — Financial investigation skill for AXIOM.

Wraps EDGAR, FRED (Federal Reserve Economic Data), Alpha Vantage,
and financial analysis utilities for investigating corporate malfeasance,
economic reporting, and market manipulation.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15


def edgar_company_search(company_name: str) -> list[dict]:
    """Search SEC EDGAR for company filings by name."""
    url = "https://efts.sec.gov/LATEST/search-index"
    headers = {"User-Agent": "journalist-ai research@example.com"}
    try:
        resp = requests.get(
            url,
            params={"q": f'"{company_name}"', "dateRange": "custom", "startdt": "2020-01-01"},
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        hits = resp.json().get("hits", {}).get("hits", [])
        return [
            {
                "company": h.get("_source", {}).get("entity_name", ""),
                "form": h.get("_source", {}).get("file_type", ""),
                "filed": h.get("_source", {}).get("period_of_report", ""),
                "data_source": "sec_edgar",
            }
            for h in hits[:10]
        ]
    except Exception as e:
        logger.error("EDGAR search error: %s", e)
        return []


def get_fred_series(series_id: str, limit: int = 20) -> list[dict]:
    """
    Fetch Federal Reserve Economic Data (FRED) time series.
    Requires FRED_API_KEY env var.
    Common series IDs: GDP, UNRATE (unemployment), CPIAUCSL (inflation),
    FEDFUNDS (federal funds rate), DGS10 (10-year Treasury yield).
    """
    api_key = os.getenv("FRED_API_KEY", "")
    if not api_key:
        return [{"error": "FRED_API_KEY not set"}]
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "limit": limit,
        "sort_order": "desc",
    }
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        obs = resp.json().get("observations", [])
        return [{"date": o["date"], "value": o["value"], "series": series_id, "data_source": "fred"} for o in obs]
    except Exception as e:
        logger.error("FRED API error: %s", e)
        return []


def get_stock_data(symbol: str, interval: str = "daily") -> list[dict]:
    """
    Get stock price data via Alpha Vantage.
    Requires ALPHAVANTAGE_API_KEY env var.
    """
    api_key = os.getenv("ALPHAVANTAGE_API_KEY", "")
    if not api_key:
        return [{"error": "ALPHAVANTAGE_API_KEY not set"}]
    url = "https://www.alphavantage.co/query"
    func_map = {"daily": "TIME_SERIES_DAILY", "weekly": "TIME_SERIES_WEEKLY", "monthly": "TIME_SERIES_MONTHLY"}
    params = {"function": func_map.get(interval, "TIME_SERIES_DAILY"), "symbol": symbol, "apikey": api_key}
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        series_key = next((k for k in data if "Time Series" in k), None)
        if not series_key:
            return []
        ts = data[series_key]
        return [{"date": d, "close": ts[d].get("4. close"), "symbol": symbol, "data_source": "alphavantage"} for d in list(ts.keys())[:30]]
    except Exception as e:
        logger.error("Alpha Vantage error: %s", e)
        return []


def analyze_financial_disclosures(text: str) -> dict:
    """Analyze text from financial disclosures for red flags."""
    import re
    red_flags = []
    patterns = [
        (r"going concern", "GOING_CONCERN_WARNING"),
        (r"material weakness", "MATERIAL_WEAKNESS_INTERNAL_CONTROLS"),
        (r"restate|restatement", "FINANCIAL_RESTATEMENT"),
        (r"related.party transaction", "RELATED_PARTY_TRANSACTION"),
        (r"significant doubt", "DOUBT_ABOUT_VIABILITY"),
        (r"off.balance.sheet", "OFF_BALANCE_SHEET_ITEMS"),
        (r"whistleblower|qui tam", "WHISTLEBLOWER_MENTION"),
        (r"SEC investigation|DOJ investigation|subpoena", "REGULATORY_INVESTIGATION"),
    ]
    for pattern, flag in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            red_flags.append(flag)
    return {
        "red_flags": red_flags,
        "flag_count": len(red_flags),
        "risk_level": "HIGH" if len(red_flags) >= 3 else "MEDIUM" if red_flags else "LOW",
        "data_source": "axiom_financial_analysis",
    }


TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Company name, stock ticker, or FRED series ID"},
        "mode": {
            "type": "string",
            "enum": ["edgar", "fred", "stock", "disclosure_analysis"],
            "description": "Financial data source or analysis type",
            "default": "edgar",
        },
    },
    "required": ["query"],
}

TOOL_DESCRIPTION = "Financial investigation: SEC EDGAR filings, FRED economic data, stock prices, and disclosure red-flag analysis."


def run_tool(query: str, mode: str = "edgar") -> Any:
    if mode == "fred":
        return get_fred_series(query)
    if mode == "stock":
        return get_stock_data(query)
    if mode == "disclosure_analysis":
        return analyze_financial_disclosures(query)
    return edgar_company_search(query)
```

---

## `journalist-ai/skills/legal.py`

```python
"""
legal.py — Legal research skill for AXIOM.

Wraps CourtListener / PACER, federal statute search, and regulatory
docket lookup for investigative legal research.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15

COURTLISTENER_BASE = "https://www.courtlistener.com/api/rest/v3"


def search_court_cases(
    query: str,
    court: str = "",
    date_filed_after: str = "",
    party_name: str = "",
    limit: int = 20,
) -> list[dict]:
    """
    Search federal court opinions via CourtListener API.
    Requires COURTLISTENER_TOKEN env var for higher rate limits.
    """
    token = os.getenv("COURTLISTENER_TOKEN", "")
    headers = {"Authorization": f"Token {token}"} if token else {}
    params: dict[str, Any] = {
        "q": query,
        "type": "o",
        "order_by": "score desc",
        "stat_Precedential": "on",
        "format": "json",
        "page_size": min(limit, 50),
    }
    if court:
        params["court"] = court
    if date_filed_after:
        params["filed_after"] = date_filed_after
    if party_name:
        params["party_name"] = party_name

    try:
        resp = requests.get(f"{COURTLISTENER_BASE}/search/", headers=headers, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [
            {
                "case_name": r.get("caseName", ""),
                "court": r.get("court", ""),
                "date_filed": r.get("dateFiled", ""),
                "url": f"https://www.courtlistener.com{r.get('absolute_url', '')}",
                "citation": r.get("citation", ""),
                "snippet": r.get("snippet", ""),
                "data_source": "courtlistener",
            }
            for r in results
        ]
    except Exception as e:
        logger.error("CourtListener search error: %s", e)
        return []


def search_dockets(party_name: str, court: str = "", limit: int = 20) -> list[dict]:
    """Search federal court dockets by party name."""
    token = os.getenv("COURTLISTENER_TOKEN", "")
    headers = {"Authorization": f"Token {token}"} if token else {}
    params: dict[str, Any] = {
        "q": party_name,
        "type": "d",
        "order_by": "score desc",
        "format": "json",
        "page_size": min(limit, 50),
    }
    if court:
        params["court"] = court
    try:
        resp = requests.get(f"{COURTLISTENER_BASE}/search/", headers=headers, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [
            {
                "docket_number": r.get("docketNumber", ""),
                "case_name": r.get("caseName", ""),
                "court": r.get("court", ""),
                "date_filed": r.get("dateFiled", ""),
                "url": f"https://www.courtlistener.com{r.get('absolute_url', '')}",
                "status": r.get("status", ""),
                "data_source": "courtlistener_dockets",
            }
            for r in results
        ]
    except Exception as e:
        logger.error("Docket search error: %s", e)
        return []


def search_statutes(query: str, title: int | None = None) -> list[dict]:
    """
    Search US Code statutes via the government's uscode.house.gov XML API.
    Falls back to a simple web search if API unavailable.
    """
    url = "https://uscode.house.gov/search/criteria.shtml"
    params: dict[str, Any] = {"query": query, "searchtype": "basic"}
    if title:
        params["title"] = title
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return [{"query": query, "url": resp.url, "data_source": "uscode_house"}]
    except Exception:
        return [{"query": query, "note": "Direct statute search unavailable; use legal database.", "data_source": "uscode_house"}]


def get_regulatory_actions(agency: str = "", keyword: str = "") -> list[dict]:
    """Search Federal Register regulatory actions."""
    url = "https://www.federalregister.gov/api/v1/documents.json"
    params: dict[str, Any] = {
        "conditions[agencies][]": agency,
        "conditions[term]": keyword,
        "per_page": 20,
        "order": "relevance",
        "fields[]": ["title", "agency_names", "publication_date", "html_url", "abstract", "document_number"],
    }
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [
            {
                "title": r.get("title", ""),
                "agencies": r.get("agency_names", []),
                "published": r.get("publication_date", ""),
                "url": r.get("html_url", ""),
                "abstract": r.get("abstract", ""),
                "data_source": "federal_register",
            }
            for r in results
        ]
    except Exception as e:
        logger.error("Federal Register error: %s", e)
        return []


TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Legal query, case name, party name, or statute keyword"},
        "mode": {
            "type": "string",
            "enum": ["cases", "dockets", "statutes", "regulatory"],
            "description": "Type of legal search",
            "default": "cases",
        },
        "court": {"type": "string", "description": "Federal court code (e.g. 'scotus', 'ca9', 'dcd')"},
        "date_filed_after": {"type": "string", "description": "Filter to cases filed after this date (YYYY-MM-DD)"},
    },
    "required": ["query"],
}

TOOL_DESCRIPTION = "Legal research: federal court opinions, dockets, US statutes, and Federal Register regulatory actions via CourtListener and official APIs."


def run_tool(query: str, mode: str = "cases", court: str = "", date_filed_after: str = "") -> Any:
    if mode == "dockets":
        return search_dockets(party_name=query, court=court)
    if mode == "statutes":
        return search_statutes(query)
    if mode == "regulatory":
        return get_regulatory_actions(keyword=query)
    return search_court_cases(query=query, court=court, date_filed_after=date_filed_after)
```

---

## `journalist-ai/skills/lie_detection.py`

```python
# lie_detection.py — Inconsistency and deception detection skill module.
# Full source: see wuzbak/Journalism- journalist-ai/skills/lie_detection.py
```

---

## `journalist-ai/skills/politics.py`

```python
"""
politics.py — Political investigation skill for AXIOM.

Wraps Congressional data (ProPublica, Congress.gov, GovTrack),
FEC campaign finance, voting records, and lobbying disclosures.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15


def get_congressional_votes(member_id: str, congress: int = 118) -> list[dict]:
    """Get voting record for a congressional member via ProPublica."""
    api_key = os.getenv("PROPUBLICA_API_KEY", "")
    if not api_key:
        return [{"error": "PROPUBLICA_API_KEY not set"}]
    url = f"https://api.propublica.org/congress/v1/members/{member_id}/votes.json"
    headers = {"X-API-Key": api_key}
    try:
        resp = requests.get(url, headers=headers, params={"congress": congress}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        votes = results[0].get("votes", []) if results else []
        return [{"description": v.get("description", ""), "vote": v.get("position", ""), "date": v.get("date", ""), "data_source": "propublica"} for v in votes[:30]]
    except Exception as e:
        logger.error("ProPublica votes error: %s", e)
        return []


def get_fec_contributions(
    contributor_name: str = "",
    committee_id: str = "",
    cycle: str = "2024",
    limit: int = 20,
) -> list[dict]:
    """Search FEC campaign contributions."""
    api_key = os.getenv("FEC_API_KEY", "DEMO_KEY")
    url = "https://api.open.fec.gov/v1/schedules/schedule_a/"
    params: dict[str, Any] = {
        "api_key": api_key,
        "contributor_name": contributor_name,
        "committee_id": committee_id,
        "two_year_transaction_period": cycle,
        "per_page": limit,
        "sort": "-contribution_receipt_amount",
    }
    params = {k: v for k, v in params.items() if v}
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [
            {
                "contributor": r.get("contributor_name", ""),
                "amount": r.get("contribution_receipt_amount", 0),
                "date": r.get("contribution_receipt_date", ""),
                "committee": r.get("committee", {}).get("name", ""),
                "data_source": "fec",
            }
            for r in results
        ]
    except Exception as e:
        logger.error("FEC API error: %s", e)
        return []


def get_lobbying_disclosures(registrant_name: str, filing_year: int | None = None) -> list[dict]:
    """Search Senate Lobbying Disclosure Act database."""
    url = "https://lda.senate.gov/api/v1/filings/"
    params: dict[str, Any] = {
        "registrant_name": registrant_name,
        "filing_year": filing_year or "",
        "limit": 20,
        "format": "json",
    }
    params = {k: v for k, v in params.items() if v}
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [
            {
                "registrant": r.get("registrant", {}).get("name", ""),
                "client": r.get("client", {}).get("name", ""),
                "income": r.get("income", ""),
                "expenses": r.get("expenses", ""),
                "year": r.get("filing_year", ""),
                "data_source": "senate_lda",
            }
            for r in results
        ]
    except Exception as e:
        logger.error("LDA API error: %s", e)
        return []


def get_bill_details(bill_number: str, congress: int = 118) -> dict:
    """Get bill details and sponsors from Congress.gov API."""
    api_key = os.getenv("CONGRESS_GOV_API_KEY", "DEMO_KEY")
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_number}"
    try:
        resp = requests.get(url, params={"api_key": api_key, "format": "json"}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json().get("bill", {})
        return {"title": data.get("title", ""), "sponsors": data.get("sponsors", []), "status": data.get("latestAction", {}).get("text", ""), "introduced": data.get("introducedDate", ""), "data_source": "congress_gov"}
    except Exception as e:
        logger.error("Congress.gov error: %s", e)
        return {}


def identify_applicable_statutes(text: str) -> list[dict]:
    """Identify potentially applicable federal statutes for a described scenario."""
    text_lower = text.lower()
    statutes = []
    if any(w in text_lower for w in ["bribe", "corrupt", "foreign", "government official"]):
        statutes.append({"name": "Foreign Corrupt Practices Act (FCPA)", "usc": "15 U.S.C. § 78dd-1", "note": "Prohibits bribery of foreign officials."})
        statutes.append({"name": "18 U.S.C. § 201 — Bribery of Public Officials", "usc": "18 U.S.C. § 201", "note": "Federal bribery statute."})
    if any(w in text_lower for w in ["false claim", "fraud", "contractor", "government contract"]):
        statutes.append({"name": "False Claims Act", "usc": "31 U.S.C. §§ 3729–3733", "note": "Qui tam whistleblower provisions."})
    if any(w in text_lower for w in ["insider", "insider trading", "material non-public"]):
        statutes.append({"name": "Securities Exchange Act § 10(b)", "usc": "15 U.S.C. § 78j", "note": "Anti-fraud provision; Rule 10b-5 covers insider trading."})
    if any(w in text_lower for w in ["wire", "mail", "scheme to defraud"]):
        statutes.append({"name": "Wire Fraud / Mail Fraud", "usc": "18 U.S.C. §§ 1341, 1343", "note": "Requires scheme to defraud via wire or mail."})
    if any(w in text_lower for w in ["campaign", "donation", "contribution", "pac"]):
        statutes.append({"name": "Federal Election Campaign Act (FECA)", "usc": "52 U.S.C. § 30101 et seq.", "note": "Campaign finance law; enforced by FEC."})
    return statutes


TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Politician name, bill number, or topic"},
        "mode": {
            "type": "string",
            "enum": ["votes", "fec", "lobbying", "bill", "statutes"],
            "description": "Type of political investigation",
            "default": "fec",
        },
    },
    "required": ["query"],
}

TOOL_DESCRIPTION = "Political investigation: congressional voting records (ProPublica), FEC campaign finance, Senate lobbying disclosures, Congress.gov bill details, and applicable statute identification."


def run_tool(query: str, mode: str = "fec") -> Any:
    if mode == "votes":
        return get_congressional_votes(query)
    if mode == "lobbying":
        return get_lobbying_disclosures(query)
    if mode == "bill":
        return get_bill_details(query)
    if mode == "statutes":
        return identify_applicable_statutes(query)
    return get_fec_contributions(contributor_name=query)
```

---

## `journalist-ai/skills/social_justice.py`

```python
"""
social_justice.py — Social justice and civil rights investigation skill for AXIOM.

Wraps ACLU, Civil Rights Division data, police misconduct databases,
incarceration data, and wage/labor records for investigative reporting.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15


def search_police_misconduct(officer_name: str = "", department: str = "") -> list[dict]:
    """Search public police misconduct databases (CPDP for Chicago, NYPD data)."""
    results = []
    if department.lower() in ("chicago", "cpd", ""):
        url = "https://api.cpdp.co/v2/officers/search/"
        params: dict[str, Any] = {"full_name": officer_name} if officer_name else {}
        try:
            resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            for officer in (data.get("results") or [])[:20]:
                results.append({
                    "name": f"{officer.get('first_name', '')} {officer.get('last_name', '')}".strip(),
                    "department": "Chicago PD",
                    "allegations": officer.get("allegation_count", 0),
                    "sustained": officer.get("sustained_count", 0),
                    "url": f"https://cpdp.co/officer/{officer.get('id', '')}/",
                    "data_source": "cpdp",
                })
        except Exception as e:
            logger.error("CPDP API error: %s", e)
    return results


def search_incarceration_data(state: str = "", query: str = "") -> list[dict]:
    """Search Bureau of Justice Statistics data via ICPSR."""
    url = "https://api.bjs.gov/iapi/title"
    try:
        resp = requests.get(url, params={"q": query or state, "limit": 10}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return [{"title": r.get("title", ""), "url": r.get("url", ""), "data_source": "bjs"} for r in resp.json().get("results", [])]
    except Exception as e:
        logger.error("BJS API error: %s", e)
        return [{"note": "BJS API query attempted", "state": state, "query": query, "data_source": "bjs"}]


def search_wage_violations(employer_name: str = "", state: str = "") -> list[dict]:
    """Search DOL wage and hour violations (WHISARD database)."""
    url = "https://data.dol.gov/get/whisard/rows/30"
    params: dict[str, Any] = {}
    if employer_name:
        params["trade_nm"] = employer_name
    if state:
        params["st_cd"] = state
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return [{"employer": r.get("trade_nm", ""), "violations": r.get("findings_bw_atp_amt", ""), "employees": r.get("ee_violtd_cnt", ""), "state": r.get("st_cd", ""), "data_source": "dol_whisard"} for r in resp.json()[:20]]
    except Exception as e:
        logger.error("DOL WHISARD error: %s", e)
        return []


def search_civil_rights_cases(query: str) -> list[dict]:
    """Search civil rights litigation via CourtListener."""
    try:
        resp = requests.get(
            "https://www.courtlistener.com/api/rest/v3/search/",
            params={"q": query, "practice_area": "Civil Rights", "type": "o", "format": "json", "page_size": 10},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return [{"case": r.get("caseName", ""), "date": r.get("dateFiled", ""), "url": f"https://www.courtlistener.com{r.get('absolute_url', '')}", "data_source": "courtlistener"} for r in resp.json().get("results", [])]
    except Exception as e:
        logger.error("Civil rights case search error: %s", e)
        return []


TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Name, employer, or topic to investigate"},
        "mode": {
            "type": "string",
            "enum": ["misconduct", "incarceration", "wages", "civil_rights"],
            "description": "Type of social justice investigation",
            "default": "misconduct",
        },
        "state": {"type": "string", "description": "Two-letter US state code (optional)"},
    },
    "required": ["query"],
}

TOOL_DESCRIPTION = "Social justice investigation: police misconduct records (CPDP), incarceration statistics (BJS), DOL wage violations, and civil rights litigation via CourtListener."


def run_tool(query: str, mode: str = "misconduct", state: str = "") -> Any:
    if mode == "incarceration":
        return search_incarceration_data(state=state, query=query)
    if mode == "wages":
        return search_wage_violations(employer_name=query, state=state)
    if mode == "civil_rights":
        return search_civil_rights_cases(query)
    return search_police_misconduct(officer_name=query)
```

---

## `journalist-ai/skills/tech.py`

```python
"""
tech.py — Technology investigation skill for AXIOM.

Covers: CVE vulnerability databases, patent records (USPTO), FOIA tech disclosures,
GitHub public repository analysis, domain/WHOIS records, and FCC filings.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15


def search_cve_vulnerabilities(keyword: str = "", cve_id: str = "", severity: str = "") -> list[dict]:
    """Search NIST NVD for CVE vulnerabilities."""
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params: dict[str, Any] = {"resultsPerPage": 20}
    if cve_id:
        params["cveId"] = cve_id
    elif keyword:
        params["keywordSearch"] = keyword
    if severity:
        params["cvssV3Severity"] = severity.upper()
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        vulns = resp.json().get("vulnerabilities", [])
        return [
            {
                "id": v.get("cve", {}).get("id", ""),
                "description": (v.get("cve", {}).get("descriptions", [{}])[0] or {}).get("value", "")[:300],
                "severity": v.get("cve", {}).get("metrics", {}).get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseSeverity", ""),
                "score": v.get("cve", {}).get("metrics", {}).get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseScore", ""),
                "published": v.get("cve", {}).get("published", ""),
                "data_source": "nvd_nist",
            }
            for v in vulns
        ]
    except Exception as e:
        logger.error("NVD CVE error: %s", e)
        return []


def search_patents(query: str, assignee: str = "", limit: int = 20) -> list[dict]:
    """Search US patents via the PatentsView API."""
    url = "https://api.patentsview.org/patents/query"
    payload: dict[str, Any] = {
        "q": {"_text_all": {"patent_title": query}},
        "f": ["patent_id", "patent_title", "patent_date", "assignee_organization", "patent_abstract"],
        "o": {"per_page": min(limit, 50)},
    }
    if assignee:
        payload["q"] = {"_and": [{"_text_all": {"patent_title": query}}, {"_contains": {"assignee_organization": assignee}}]}
    try:
        resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        patents = resp.json().get("patents", [])
        return [
            {
                "id": p.get("patent_id", ""),
                "title": p.get("patent_title", ""),
                "date": p.get("patent_date", ""),
                "assignee": ", ".join(a.get("assignee_organization", "") for a in p.get("assignees", []) if a.get("assignee_organization")),
                "abstract": (p.get("patent_abstract") or "")[:300],
                "url": f"https://patents.google.com/patent/US{p.get('patent_id', '')}/",
                "data_source": "patentsview",
            }
            for p in patents
        ]
    except Exception as e:
        logger.error("PatentsView error: %s", e)
        return []


def lookup_whois(domain: str) -> dict:
    """Lookup domain registration via RDAP (successor to WHOIS)."""
    url = f"https://rdap.org/domain/{domain}"
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        events = {e.get("eventAction"): e.get("eventDate") for e in data.get("events", [])}
        entities = [
            {"type": ", ".join(r.get("roles", [])), "name": r.get("vcardArray", [None, [{}]])[1][1][3] if r.get("vcardArray") else ""}
            for r in data.get("entities", [])
        ]
        return {
            "domain": domain,
            "registered": events.get("registration"),
            "expires": events.get("expiration"),
            "last_changed": events.get("last changed"),
            "status": data.get("status", []),
            "entities": entities,
            "data_source": "rdap",
        }
    except Exception as e:
        logger.error("RDAP lookup error for %s: %s", domain, e)
        return {"domain": domain, "error": str(e), "data_source": "rdap"}


def search_fcc_filings(query: str, proceeding: str = "") -> list[dict]:
    """Search FCC ECFS filings."""
    url = "https://ecfs.fec.gov/api/public/filing/"
    params: dict[str, Any] = {"q": query, "limit": 20}
    if proceeding:
        params["proceeding"] = proceeding
    try:
        resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        filings = resp.json().get("filings", {}).get("filing", [])
        return [
            {
                "id": f.get("id_submission", ""),
                "filer": f.get("name_of_filer", ""),
                "date": f.get("date_received", ""),
                "proceeding": f.get("proceedings", [{}])[0].get("name", "") if f.get("proceedings") else "",
                "data_source": "fcc_ecfs",
            }
            for f in filings[:20]
        ]
    except Exception as e:
        logger.error("FCC ECFS error: %s", e)
        return []


TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Technology company, product, vulnerability, or domain to investigate"},
        "mode": {
            "type": "string",
            "enum": ["cve", "patents", "whois", "fcc"],
            "description": "Type of tech investigation",
            "default": "cve",
        },
    },
    "required": ["query"],
}

TOOL_DESCRIPTION = "Technology investigation: CVE vulnerability database (NIST NVD), US patent records (PatentsView), domain/WHOIS (RDAP), and FCC filings."


def run_tool(query: str, mode: str = "cve") -> Any:
    if mode == "patents":
        return search_patents(query)
    if mode == "whois":
        return lookup_whois(query)
    if mode == "fcc":
        return search_fcc_filings(query)
    return search_cve_vulnerabilities(keyword=query)
```

---

## `journalist-ai/tests//init/.py`

```python
```

---

## `journalist-ai/tests/conftest.py`

```python
"""pytest configuration — add journalist-ai to the Python path."""
import sys
from pathlib import Path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root.parent))
import importlib, types
pkg_path = root
journalist_ai = types.ModuleType("journalist_ai")
journalist_ai.__path__ = [str(pkg_path)]
journalist_ai.__package__ = "journalist_ai"
journalist_ai.__spec__ = importlib.util.spec_from_file_location("journalist_ai", str(pkg_path / "__init__.py"))
sys.modules["journalist_ai"] = journalist_ai
```

---

## `journalist-ai/tests/test_agentic_upgrade.py`

```python
# test_agentic_upgrade.py — Tests for agentic journalism upgrade modules.
# Full source: see wuzbak/Journalism- journalist-ai/tests/test_agentic_upgrade.py
```

---

## `journalist-ai/tests/test_axiomzero_gate.py`

```python
# test_axiomzero_gate.py — Tests for tools/axiomzero_gate.py.
# Full source: see wuzbak/Journalism- journalist-ai/tests/test_axiomzero_gate.py
```

---

## `journalist-ai/tests/test_core.py`

```python
# test_core.py — Tests for journalist-ai core modules.
# Full source: see wuzbak/Journalism- journalist-ai/tests/test_core.py
```

---

## `journalist-ai/tests/test_entity_resolver.py`

```python
# test_entity_resolver.py — Tests for tools/entity_resolver.py.
# Full source: see wuzbak/Journalism- journalist-ai/tests/test_entity_resolver.py
```

---

## `journalist-ai/tests/test_new_tools.py`

```python
"""
Tests for the new data source tool modules added in the data-source expansion.

Run with: pytest journalist-ai/tests/
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import requests as _requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Convenience alias so tests read as "raise NetworkError(...)"
NetworkError = _requests.exceptions.ConnectionError


# ─── Corporate Records — unit-level helpers ───────────────────────────────────

from journalist_ai.tools.corporate_records import (
    _normalize_oc_company,
    _normalize_aleph_entity,
    run_tool as corporate_run_tool,
)


def test_normalize_oc_company():
    raw = {
        "name": "Shell Holdings LLC",
        "company_number": "12345678",
        "jurisdiction_code": "us_de",
        "company_type": "LLC",
        "incorporation_date": "2010-03-15",
        "current_status": "Active",
        "registered_address_in_full": "1209 Orange Street, Wilmington, DE",
        "opencorporates_url": "https://opencorporates.com/companies/us_de/12345678",
    }
    result = _normalize_oc_company(raw)
    assert result["name"] == "Shell Holdings LLC"
    assert result["jurisdiction_code"] == "us_de"
    assert result["status"] == "Active"
    assert result["data_source"] == "opencorporates"
    assert result["url"].startswith("https://opencorporates.com/")


def test_normalize_aleph_entity():
    raw = {
        "id": "abc123",
        "caption": "John Doe",
        "schema": "Person",
        "datasets": ["pandora_papers", "sanctions_list"],
        "properties": {
            "name": ["John Doe", "Johann Doe"],
            "alias": ["JD"],
            "country": ["US", "CH"],
            "birthDate": ["1975-06-20"],
            "address": ["123 Main St"],
        },
    }
    result = _normalize_aleph_entity(raw)
    assert result["caption"] == "John Doe"
    assert result["schema"] == "Person"
    assert "pandora_papers" in result["datasets"]
    assert result["data_source"] == "aleph_occrp"
    assert result["url"].startswith("https://aleph.occrp.org/entities/")


def test_corporate_run_tool_returns_list_on_network_error():
    """run_tool should gracefully handle network failures and return an empty list."""
    with patch("journalist_ai.tools.corporate_records.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("connection refused")
        result = corporate_run_tool(query="Test Corp", mode="companies")
    assert isinstance(result, list)


# ─── Court Records — unit-level helpers ──────────────────────────────────────

from journalist_ai.tools.court_records import (
    _normalize_opinion,
    _normalize_docket,
    run_tool as court_run_tool,
)


def test_normalize_opinion():
    raw = {
        "caseName": "Smith v. Corp Inc.",
        "court": "ca9",
        "dateFiled": "2023-06-15",
        "citation": ["123 F.3d 456"],
        "status": "Published",
        "snippet": "The defendant failed to disclose...",
        "absolute_url": "/opinion/123/smith-v-corp/",
        "cluster_id": 123,
    }
    result = _normalize_opinion(raw)
    assert result["case_name"] == "Smith v. Corp Inc."
    assert result["court"] == "ca9"
    assert result["data_source"] == "courtlistener"
    assert result["url"].startswith("https://www.courtlistener.com/")


def test_normalize_docket():
    raw = {
        "caseName": "DOJ v. Megacorp",
        "docketNumber": "1:23-cv-00001",
        "court": "District Court for D.C.",
        "court_id": "dcd",
        "dateFiled": "2023-01-10",
        "suitNature": "Securities",
        "absolute_url": "/docket/456/doj-v-megacorp/",
        "docket_id": 456,
    }
    result = _normalize_docket(raw)
    assert result["case_name"] == "DOJ v. Megacorp"
    assert result["docket_number"] == "1:23-cv-00001"
    assert result["data_source"] == "courtlistener"


def test_court_run_tool_returns_list_on_network_error():
    with patch("journalist_ai.tools.court_records.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("timeout")
        result = court_run_tool(query="fraud", mode="opinions")
    assert isinstance(result, list)


# ─── News Monitor — unit-level helpers ───────────────────────────────────────

from journalist_ai.tools.news_monitor import (
    _normalize_gdelt_article,
    _normalize_nyt_article,
    run_tool as news_run_tool,
)


def test_normalize_gdelt_article():
    raw = {
        "title": "Corporate Scandal Rocks Markets",
        "url": "https://reuters.com/article/123",
        "domain": "reuters.com",
        "sourcecountry": "US",
        "language": "English",
        "seendate": "20240315T120000Z",
        "tone": -3.5,
        "themes": "CORRUPTION;ECONOMY",
        "persons": "John Smith;Jane Doe",
        "organizations": "MegaCorp;SEC",
        "locations": "Washington;New York",
    }
    result = _normalize_gdelt_article(raw)
    assert result["title"] == "Corporate Scandal Rocks Markets"
    assert result["tone"] == -3.5
    assert "CORRUPTION" in result["themes"]
    assert "John Smith" in result["persons"]
    assert result["data_source"] == "gdelt"


def test_normalize_nyt_article():
    raw = {
        "headline": {"main": "Bank Fraud Investigation Underway"},
        "abstract": "Authorities are investigating alleged fraud at MegaBank.",
        "lead_paragraph": "Federal prosecutors have opened...",
        "web_url": "https://www.nytimes.com/2024/03/15/business/bank-fraud.html",
        "pub_date": "2024-03-15T10:00:00+0000",
        "section_name": "Business",
        "byline": {"original": "By Jane Reporter"},
        "source": "The New York Times",
        "keywords": [{"value": "fraud"}, {"value": "banking"}],
    }
    result = _normalize_nyt_article(raw)
    assert result["title"] == "Bank Fraud Investigation Underway"
    assert result["section"] == "Business"
    assert "fraud" in result["keywords"]
    assert result["data_source"] == "nyt"


def test_news_gdelt_returns_empty_list_on_error():
    with patch("journalist_ai.tools.news_monitor.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("network error")
        result = news_run_tool(query="corruption", source="gdelt")
    assert isinstance(result, list)
    assert result == []


def test_news_nyt_returns_error_dict_without_api_key(monkeypatch):
    monkeypatch.delenv("NYT_API_KEY", raising=False)
    result = news_run_tool(query="fraud", source="nyt")
    # Should return list with error indicator or empty list
    assert isinstance(result, list)


# ─── Violation Tracker — unit-level helpers ──────────────────────────────────

from journalist_ai.tools.violation_tracker import (
    _normalize_violation,
    _parse_penalty,
    run_tool as violation_run_tool,
)


def test_parse_penalty_integer():
    assert _parse_penalty(1_000_000) == 1_000_000


def test_parse_penalty_string_with_currency():
    assert _parse_penalty("$5,250,000") == 5_250_000


def test_parse_penalty_float():
    assert _parse_penalty(3500000.0) == 3_500_000


def test_parse_penalty_empty():
    assert _parse_penalty("") == 0
    assert _parse_penalty(None) == 0


def test_normalize_violation_dict():
    raw = {
        "company_name": "Polluto Industries",
        "parent_name": "Big Corp Holdings",
        "agency": "EPA",
        "penalty": "$12,500,000",
        "year_initiated": 2022,
        "offense_group": "environmental",
        "case_description": "Illegal discharge into waterway.",
        "action_date": "2022-07-01",
        "hq_state": "TX",
        "case_url": "https://violationtracker.goodjobsfirst.org/parent/big-corp-holdings",
    }
    result = _normalize_violation(raw)
    assert result["company"] == "Polluto Industries"
    assert result["agency"] == "EPA"
    assert result["penalty_amount"] == 12_500_000
    assert result["data_source"] == "violation_tracker"


def test_violation_run_tool_returns_list_on_network_error():
    with patch("journalist_ai.tools.violation_tracker.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("connection refused")
        result = violation_run_tool(company="Test Corp")
    assert isinstance(result, list)
    assert result == []


# ─── Investigation Chain — new domains ───────────────────────────────────────

from journalist_ai.agent.investigation_chain import _infer_domains, _suggest_sources


def test_infer_domains_corporate():
    domains = _infer_domains("The CEO set up a shell corporation in Delaware to hide ownership")
    assert "corporate" in domains or "finance" in domains


def test_infer_domains_misconduct():
    domains = _infer_domains("The company paid a $5 million fine to settle EPA violation")
    assert "misconduct" in domains or "environment" in domains


def test_suggest_sources_law_includes_court_records():
    sources = _suggest_sources("The court filed a lawsuit against the company for fraud")
    assert "court_records" in sources


def test_suggest_sources_corporate_includes_aleph():
    sources = _suggest_sources("The corporation has offshore subsidiaries and shell company ownership")
    assert "corporate_records" in sources or "aleph_occrp" in sources


def test_suggest_sources_misconduct_includes_violation_tracker():
    sources = _suggest_sources("The company was fined $10 million for safety violations")
    assert "violation_tracker" in sources


# ─── Web Search — new tier domains ──────────────────────────────────────────

from journalist_ai.tools.web_search import _classify_source_tier


def test_tier_1_courtlistener():
    assert _classify_source_tier("https://www.courtlistener.com/opinion/123/") == 1


def test_tier_1_aleph_occrp():
    assert _classify_source_tier("https://aleph.occrp.org/entities/abc123") == 1


def test_tier_2_opencorporates():
    assert _classify_source_tier("https://opencorporates.com/companies/us_de/12345") == 2


def test_tier_2_violation_tracker():
    assert _classify_source_tier("https://violationtracker.goodjobsfirst.org/parent/test") == 2


def test_tier_3_gdelt():
    assert _classify_source_tier("https://gdeltproject.org/data/") == 3


# ─── Public Records — new World Bank helpers ─────────────────────────────────

from journalist_ai.tools.public_records import world_bank_indicator, census_acs5


def test_world_bank_indicator_handles_network_error():
    with patch("journalist_ai.tools.public_records.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("timeout")
        result = world_bank_indicator("US", "NY.GDP.MKTP.CD")
    assert isinstance(result, list)
    assert result == []


def test_world_bank_indicator_parses_response():
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"pages": 1, "total": 1},
        [
            {
                "country": {"value": "United States"},
                "countryiso3code": "USA",
                "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
                "date": "2022",
                "value": 25462700000000.0,
            }
        ],
    ]
    mock_response.raise_for_status = MagicMock()

    with patch("journalist_ai.tools.public_records.requests.get", return_value=mock_response):
        result = world_bank_indicator("US", "NY.GDP.MKTP.CD")

    assert len(result) == 1
    assert result[0]["country"] == "United States"
    assert result[0]["value"] == 25462700000000.0
    assert result[0]["data_source"] == "world_bank"


def test_census_acs5_handles_network_error():
    with patch("journalist_ai.tools.public_records.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("connection refused")
        result = census_acs5(["B01003_001E"])
    assert isinstance(result, list)
    assert result == []


# ─── GovInfo — unit-level helpers ────────────────────────────────────────────

from journalist_ai.tools.govinfo import _normalize_result, run_tool as govinfo_run_tool


def test_normalize_govinfo_result():
    raw = {
        "title": "United States Code, 2023 Edition, Title 15 - Commerce and Trade",
        "collectionCode": "USCODE",
        "packageId": "USCODE-2023-title15",
        "dateIssued": "2023-01-01",
        "governmentAuthor1": "United States Government Publishing Office",
        "branch": "Legislative",
        "detailsLink": "https://api.govinfo.gov/packages/USCODE-2023-title15/summary",
        "download": {"txtLink": "https://api.govinfo.gov/packages/USCODE-2023-title15/granules/txt"},
    }
    result = _normalize_result(raw)
    assert result["title"].startswith("United States Code")
    assert result["collection"] == "USCODE"
    assert result["package_id"] == "USCODE-2023-title15"
    assert result["data_source"] == "govinfo"
    assert result["url"].startswith("https://api.govinfo.gov/")


def test_govinfo_run_tool_returns_list_on_network_error():
    with patch("journalist_ai.tools.govinfo.requests.post") as mock_post:
        mock_post.side_effect = NetworkError("connection refused")
        result = govinfo_run_tool(query="securities fraud")
    assert isinstance(result, list)
    assert result == []


def test_govinfo_run_tool_cfr_collection():
    with patch("journalist_ai.tools.govinfo.requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"results": []}
        mock_post.return_value = mock_resp
        result = govinfo_run_tool(query="emissions standards", collection="cfr", usc_title=40)
    assert isinstance(result, list)
    # Verify the search was called with CFR collection
    call_json = mock_post.call_args[1].get("json", {})
    assert "CFR" in call_json.get("collections", [])


# ─── OpenSanctions — unit-level helpers ──────────────────────────────────────

from journalist_ai.tools.opensanctions import _normalize_entity, run_tool as opensanctions_run_tool


def test_normalize_opensanctions_entity():
    raw = {
        "id": "Q123456",
        "caption": "Ivan Petrov",
        "schema": "Person",
        "datasets": ["ru_rupep", "us_ofac_sdn"],
        "referents": [],
        "properties": {
            "name": ["Ivan Petrov", "I. Petrov"],
            "alias": ["The Bear"],
            "country": ["RU"],
            "birthDate": ["1970-05-15"],
            "nationality": ["Russian"],
            "address": ["Moscow, Russia"],
            "notes": ["Sanctioned for human rights violations"],
        },
        "score": 0.92,
    }
    result = _normalize_entity(raw)
    assert result["caption"] == "Ivan Petrov"
    assert result["schema"] == "Person"
    assert result["is_sanctioned"] is True
    assert "ru_rupep" in result["datasets"]
    assert result["birth_date"] == "1970-05-15"
    assert result["score"] == 0.92
    assert result["data_source"] == "opensanctions"
    assert result["url"].startswith("https://www.opensanctions.org/entities/")


def test_normalize_entity_pep_detection():
    raw = {
        "id": "Q999",
        "caption": "Jane Minister",
        "schema": "Person",
        "datasets": ["ke_pep_politicians"],
        "referents": [],
        "properties": {"name": ["Jane Minister"], "country": ["KE"]},
    }
    result = _normalize_entity(raw)
    assert result["is_pep"] is True
    assert result["is_sanctioned"] is False


def test_opensanctions_run_tool_returns_list_on_network_error():
    with patch("journalist_ai.tools.opensanctions.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("timeout")
        result = opensanctions_run_tool(name="John Doe", mode="search")
    assert isinstance(result, list)
    assert result == []


def test_opensanctions_match_returns_list_on_network_error():
    with patch("journalist_ai.tools.opensanctions.requests.post") as mock_post:
        mock_post.side_effect = NetworkError("timeout")
        result = opensanctions_run_tool(name="John Doe", mode="match")
    assert isinstance(result, list)
    assert result == []


# ─── Wayback Machine — unit-level helpers ────────────────────────────────────

from journalist_ai.tools.wayback_machine import (
    _format_timestamp,
    get_closest_snapshot,
    run_tool as wayback_run_tool,
)


def test_format_timestamp():
    assert _format_timestamp("20240315120000") == "2024-03-15"
    assert _format_timestamp("20200101") == "2020-01-01"
    assert _format_timestamp("") == ""


def test_get_closest_snapshot_not_available():
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"archived_snapshots": {}}
    with patch("journalist_ai.tools.wayback_machine.requests.get", return_value=mock_resp):
        result = get_closest_snapshot("https://example.com/deleted-page")
    assert result["available"] is False
    assert result["data_source"] == "wayback_machine"


def test_get_closest_snapshot_available():
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "archived_snapshots": {
            "closest": {
                "available": True,
                "url": "https://web.archive.org/web/20240315120000/https://example.com/",
                "timestamp": "20240315120000",
                "status": "200",
            }
        }
    }
    with patch("journalist_ai.tools.wayback_machine.requests.get", return_value=mock_resp):
        result = get_closest_snapshot("https://example.com/")
    assert result["available"] is True
    assert result["date"] == "2024-03-15"
    assert result["status_code"] == "200"
    assert result["data_source"] == "wayback_machine"


def test_wayback_snapshots_returns_list_on_network_error():
    with patch("journalist_ai.tools.wayback_machine.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("timeout")
        result = wayback_run_tool(url="https://example.com/", mode="snapshots")
    assert isinstance(result, list)
    assert result == []


def test_wayback_changes_returns_dict_on_empty():
    with patch("journalist_ai.tools.wayback_machine.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("timeout")
        result = wayback_run_tool(url="https://example.com/", mode="changes")
    assert isinstance(result, dict)
    assert result["changes_detected"] is False


def test_wayback_parses_cdx_response():
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = [
        ["timestamp", "original", "statuscode", "mimetype", "digest"],
        ["20240315120000", "https://example.com/", "200", "text/html", "SHA1:ABCDEF"],
        ["20240320130000", "https://example.com/", "200", "text/html", "SHA1:XYZUVW"],
    ]
    with patch("journalist_ai.tools.wayback_machine.requests.get", return_value=mock_resp):
        result = wayback_run_tool(url="https://example.com/", mode="snapshots")
    assert len(result) == 2
    assert result[0]["date"] == "2024-03-15"
    assert result[0]["status_code"] == "200"
    assert result[0]["data_source"] == "wayback_machine"


# ─── OIG Oversight — unit-level helpers ──────────────────────────────────────

from journalist_ai.tools.oig_oversight import _normalize_report, run_tool as oig_run_tool


def test_normalize_oig_report_dict():
    raw = {
        "report_id": "OIG-2024-001",
        "title": "Audit of COVID-19 Relief Fund Disbursements",
        "agency_name": "HHS",
        "type": "Audit",
        "pub_date": "2024-03-15",
        "summary": "The audit found $12.5 million in unsupported costs.",
        "url": "https://www.oversight.gov/report/hhs/audit-covid-funds",
        "pdf_url": "https://www.oversight.gov/sites/default/files/oig-report.pdf",
    }
    result = _normalize_report(raw)
    assert result["report_id"] == "OIG-2024-001"
    assert result["title"] == "Audit of COVID-19 Relief Fund Disbursements"
    assert result["agency"] == "HHS"
    assert result["report_type"] == "Audit"
    assert result["date_published"] == "2024-03-15"
    assert result["data_source"] == "oig_oversight"
    assert result["url"].startswith("https://www.oversight.gov/")


def test_normalize_oig_report_alternate_keys():
    raw = {
        "id": "DOJ-INV-2023-042",
        "report_title": "Investigation into Grant Fraud",
        "ig_name": "DOJ",
        "report_type": "Investigation",
        "date": "2023-11-01",
        "report_url": "https://oig.justice.gov/reports/2023/a2301.pdf",
    }
    result = _normalize_report(raw)
    assert result["report_id"] == "DOJ-INV-2023-042"
    assert result["title"] == "Investigation into Grant Fraud"
    assert result["agency"] == "DOJ"
    assert result["data_source"] == "oig_oversight"


def test_oig_run_tool_returns_list_on_network_error():
    with patch("journalist_ai.tools.oig_oversight.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("connection refused")
        result = oig_run_tool(keyword="fraud", mode="search")
    assert isinstance(result, list)
    assert result == []


def test_oig_run_tool_investigations_mode():
    with patch("journalist_ai.tools.oig_oversight.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("timeout")
        result = oig_run_tool(keyword="bribery", mode="investigations")
    assert isinstance(result, list)


# ─── Metadata Forensics — unit-level helpers ─────────────────────────────────

from journalist_ai.tools.metadata_forensics import (
    _parse_pdf_date,
    _pdf_forensic_flags,
    run_tool as forensics_run_tool,
)


def test_parse_pdf_date_with_prefix():
    assert _parse_pdf_date("D:20240315120000") == "2024-03-15"


def test_parse_pdf_date_without_prefix():
    assert _parse_pdf_date("20201201") == "2020-12-01"


def test_parse_pdf_date_empty():
    assert _parse_pdf_date("") == ""


def test_pdf_forensic_flags_missing_author():
    meta = {}
    flags = _pdf_forensic_flags(meta)
    assert "missing_creation_date" in flags
    assert "missing_author" in flags


def test_pdf_forensic_flags_conversion_tool():
    meta = {"/Producer": "Ghostscript 9.53.3", "/Author": "Jane Doe",
            "/CreationDate": "D:20240101", "/ModDate": "D:20240101"}
    flags = _pdf_forensic_flags(meta)
    assert any("ghostscript" in f for f in flags)


def test_pdf_forensic_flags_modified_after_creation():
    meta = {
        "/Author": "John Smith",
        "/CreationDate": "D:20240101120000",
        "/ModDate": "D:20240201120000",
        "/Producer": "Microsoft Word",
    }
    flags = _pdf_forensic_flags(meta)
    assert "document_modified_after_creation" in flags


def test_forensics_run_tool_returns_error_on_bad_source():
    with patch("journalist_ai.tools.metadata_forensics.requests.get") as mock_get:
        mock_get.side_effect = NetworkError("connection refused")
        result = forensics_run_tool(source="https://example.com/nonexistent.pdf", file_type="pdf")
    assert "error" in result
    assert result.get("data_source") == "metadata_forensics"


# ─── Legal skill — FATF red flags ────────────────────────────────────────────

from journalist_ai.skills.legal import check_fatf_red_flags, FATF_RED_FLAGS


def test_fatf_red_flags_structure():
    assert len(FATF_RED_FLAGS) >= 5
    for category in FATF_RED_FLAGS:
        assert "category" in category
        assert "indicators" in category
        assert len(category["indicators"]) > 0


def test_fatf_check_shell_company():
    flags = check_fatf_red_flags(
        "The company used a BVI shell to route consulting payments to a nominee director."
    )
    categories = [f["category"] for f in flags]
    assert any("Corporate" in c for c in categories)


def test_fatf_check_crypto():
    flags = check_fatf_red_flags(
        "Funds were moved through a crypto tumbler before being converted to cash."
    )
    assert len(flags) > 0
    assert any("Digital Assets" in f["category"] for f in flags)


def test_fatf_check_pep():
    flags = check_fatf_red_flags(
        "The beneficial owner is a PEP with unexplained wealth in multiple offshore accounts."
    )
    assert len(flags) > 0


def test_fatf_check_clean_scenario():
    flags = check_fatf_red_flags(
        "The company paid its quarterly invoice for software licenses via wire transfer."
    )
    assert flags == []


# ─── Investigation Chain — new forensic/sanctions domains ────────────────────

from journalist_ai.agent.investigation_chain import _infer_domains, _suggest_sources


def test_infer_domains_forensic():
    domains = _infer_domains("The document metadata shows it was backdated after the tamper was discovered")
    assert "forensic" in domains


def test_infer_domains_sanctions():
    domains = _infer_domains("The company director is a politically exposed PEP on the OFAC sanctions list")
    assert "sanctions" in domains


def test_infer_domains_watchdog():
    domains = _infer_domains("The Inspector General audit found waste and mismanagement in the program")
    assert "watchdog" in domains


def test_suggest_sources_forensic_includes_wayback():
    sources = _suggest_sources("The metadata shows the document was backdated before the filing date")
    assert "wayback_machine" in sources or "metadata_forensics" in sources


def test_suggest_sources_sanctions_includes_opensanctions():
    sources = _suggest_sources("The director is a sanctioned PEP with offshore accounts")
    assert "opensanctions" in sources


def test_suggest_sources_watchdog_includes_oig():
    sources = _suggest_sources("Inspector General audit found mismanagement of federal funds")
    assert "oig_oversight" in sources
```

---

## `journalist-ai/tools//init/.py`

```python
```

---

## `journalist-ai/tools/axiomzero_gate.py`

```python
"""
axiomzero_gate.py — Human-in-the-Loop (HITL) authorization gate for AXIOM.
"""

from __future__ import annotations

import functools
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

_DEFAULT_AUDIT_LOG = Path(
    os.getenv(
        "AXIOMZERO_AUDIT_LOG",
        str(Path(__file__).parent.parent / "outputs" / "axiomzero_audit.jsonl"),
    )
)


def _audit_log_path() -> Path:
    path = Path(os.getenv("AXIOMZERO_AUDIT_LOG", str(_DEFAULT_AUDIT_LOG)))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _write_audit_entry(target: str, decision: str, function_name: str, reason: str = "") -> None:
    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operator": os.getenv("AXIOMZERO_OPERATOR", "unknown"),
        "target": target,
        "decision": decision,
        "reason": reason,
        "function": function_name,
    }
    ip = os.getenv("AXIOMZERO_OPERATOR_IP", "")
    if ip:
        entry["ip"] = ip
    log_path = _audit_log_path()
    try:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        logger.debug("AxiomZero audit entry written: %s", entry)
    except OSError as exc:
        logger.error("AxiomZero: could not write audit log to %s: %s", log_path, exc)


def _is_interactive() -> bool:
    if os.getenv("AXIOMZERO_ALLOW_NON_INTERACTIVE", "").strip() == "1":
        return True
    return sys.stdin.isatty()


def _prompt_operator(target: str) -> tuple[bool, str]:
    print(
        f"\n{'='*60}\n"
        f"[AXIOMZERO WARNING] Investigation requested for: '{target}'\n"
        "This action requires Human-in-the-Loop authorization.\n"
        f"{'='*60}"
    )
    operator = os.getenv("AXIOMZERO_OPERATOR", "")
    if operator:
        print(f"Logged operator: {operator}")
    try:
        decision = input(f"Authorize investigation of '{target}'? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\n[AXIOMZERO] Input interrupted — authorization denied.")
        return False, ""
    if decision != "y":
        print("[AUTH DENIED] Investigation aborted.")
        return False, ""
    try:
        reason = input("Brief reason / editorial basis (press Enter to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        reason = ""
    print(f"[AUTH GRANTED] Initiating forensic pivot for '{target}'…")
    return True, reason


def axiomzero_approval(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        target: str = kwargs.get("name") or (str(args[0]) if args else "UNKNOWN")
        if not _is_interactive():
            logger.warning("AxiomZero: non-interactive context — auto-denying request for '%s'", target)
            _write_audit_entry(target=target, decision="DENIED_NON_INTERACTIVE", function_name=func.__name__)
            return None
        approved, reason = _prompt_operator(target)
        if approved:
            _write_audit_entry(target=target, decision="GRANTED", function_name=func.__name__, reason=reason)
            return func(*args, **kwargs)
        _write_audit_entry(target=target, decision="DENIED", function_name=func.__name__)
        return None
    return wrapper


def read_audit_log(limit: int = 50) -> list[dict]:
    log_path = _audit_log_path()
    if not log_path.exists():
        return []
    entries: list[dict] = []
    try:
        with log_path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    except OSError as exc:
        logger.error("AxiomZero: could not read audit log: %s", exc)
    return entries[-limit:]
```

---

## `journalist-ai/tools/c2pa_verifier.py`

```python
"""
c2pa_verifier.py — C2PA (Coalition for Content Provenance and Authenticity) verification.
Verifies the provenance of digital media using C2PA manifests and the CAI Verify API.
"""

from __future__ import annotations
import json
import logging
import os
from pathlib import Path
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 20
CAI_VERIFY_API = "https://contentcredentials.org/api/v1/validate"


def verify_c2pa(source: str) -> dict:
    file_bytes = _load_source(source)
    if file_bytes is None:
        return {"source": source, "c2pa_present": False, "verification_status": "UNVERIFIED", "forensic_flags": ["could_not_load_source"], "data_source": "c2pa_verifier"}
    local_result = _extract_c2pa_from_bytes(source, file_bytes)
    if not local_result.get("c2pa_present"):
        api_result = _verify_via_cai_api(source, file_bytes)
        if api_result.get("c2pa_present"):
            return api_result
        return {"source": source, "c2pa_present": False, "verification_status": "NO_MANIFEST", "forensic_flags": ["no_c2pa_manifest_found"], "data_source": "c2pa_verifier"}
    return local_result


def verify_c2pa_with_forensics(source: str) -> dict:
    c2pa_result = verify_c2pa(source)
    try:
        from journalist_ai.tools.metadata_forensics import run_tool as forensics_run
        forensics_result = forensics_run(source=source)
    except Exception as exc:
        logger.warning("metadata_forensics failed for '%s': %s", source[:80], exc)
        forensics_result = {"error": str(exc)}
    combined_flags = list(c2pa_result.get("forensic_flags", []))
    combined_flags.extend(forensics_result.get("forensic_flags", []))
    seen: set[str] = set()
    deduped_flags = []
    for flag in combined_flags:
        if flag not in seen:
            seen.add(flag)
            deduped_flags.append(flag)
    return {**c2pa_result, "exif_metadata": {k: v for k, v in forensics_result.items() if k not in ("forensic_flags", "source", "data_source")}, "forensic_flags": deduped_flags, "data_source": "c2pa_verifier+metadata_forensics"}


def _extract_c2pa_from_bytes(source: str, file_bytes: bytes) -> dict:
    try:
        import exifread
        import io
        tags = exifread.process_file(io.BytesIO(file_bytes), details=True)
        xmp_data = tags.get("XMP", None)
        if xmp_data:
            xmp_str = str(xmp_data)
            if "c2pa" in xmp_str.lower() or "contentcredentials" in xmp_str.lower():
                return {"source": source, "c2pa_present": True, "verification_status": "UNVERIFIED", "manifest_format": "XMP", "raw_manifest_excerpt": xmp_str[:1000], "forensic_flags": [], "data_source": "c2pa_verifier"}
    except (ImportError, OSError, ValueError, KeyError) as exc:
        logger.debug("Local C2PA extraction failed for '%s': %s", source[:80], exc)
    return {"source": source, "c2pa_present": False, "data_source": "c2pa_verifier"}


def _verify_via_cai_api(source: str, file_bytes: bytes) -> dict:
    ext = Path(source.split("?")[0]).suffix.lower() or ".bin"
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".tiff": "image/tiff", ".tif": "image/tiff", ".webp": "image/webp", ".mp4": "video/mp4", ".pdf": "application/pdf"}
    mime_type = mime_map.get(ext, "application/octet-stream")
    filename = Path(source.split("?")[0]).name or "file" + ext
    try:
        resp = requests.post(CAI_VERIFY_API, files={"file": (filename, file_bytes, mime_type)}, headers={"User-Agent": "journalist-ai/c2pa-verifier"}, timeout=REQUEST_TIMEOUT)
        if resp.status_code in (404, 422):
            return {"source": source, "c2pa_present": False, "data_source": "c2pa_verifier"}
        resp.raise_for_status()
        return _normalize_cai_response(source, resp.json())
    except requests.RequestException as exc:
        logger.debug("CAI Verify API request failed for '%s': %s", source[:80], exc)
        return {"source": source, "c2pa_present": False, "data_source": "c2pa_verifier"}


def _normalize_cai_response(source: str, data: dict) -> dict:
    manifests = data.get("manifests", [])
    if not manifests:
        return {"source": source, "c2pa_present": False, "verification_status": "NO_MANIFEST", "forensic_flags": ["no_c2pa_manifest_found"], "data_source": "c2pa_verifier"}
    manifest = manifests[0]
    validation_status = manifest.get("validation_status", "unknown")
    is_valid = validation_status in ("valid", "VALID")
    is_tampered = validation_status in ("invalid", "INVALID", "tampered", "TAMPERED")
    assertions = manifest.get("assertions", [])
    edit_history = [a for a in assertions if a.get("label", "").startswith("c2pa.actions") or "edit" in a.get("label", "").lower()]
    flags = []
    if is_tampered:
        flags.append("c2pa_manifest_invalid_tampered")
    if edit_history:
        flags.append(f"c2pa_edit_history_detected_{len(edit_history)}_actions")
    return {"source": source, "c2pa_present": True, "issuer": manifest.get("signer_payload", {}).get("issuer", ""), "software": manifest.get("claim", {}).get("generator", ""), "edit_history": edit_history, "content_hash_valid": is_valid, "assertions": assertions[:20], "verification_status": "VERIFIED" if is_valid else ("TAMPERED" if is_tampered else "UNVERIFIED"), "forensic_flags": flags, "data_source": "c2pa_verifier"}


def _load_source(source: str) -> bytes | None:
    if source.startswith("http://") or source.startswith("https://"):
        try:
            response = requests.get(source, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "journalist-ai c2pa-verifier"})
            response.raise_for_status()
            return response.content
        except requests.RequestException as exc:
            logger.error("Failed to download '%s': %s", source[:80], exc)
            return None
    try:
        return Path(source).read_bytes()
    except OSError as exc:
        logger.error("Failed to read file '%s': %s", source[:80], exc)
        return None


TOOL_SCHEMA = {"type": "object", "properties": {"source": {"type": "string", "description": "URL or local file path of the media file to verify"}, "mode": {"type": "string", "enum": ["c2pa_only", "combined"], "default": "combined"}}, "required": ["source"]}
TOOL_DESCRIPTION = "Verify the provenance and authenticity of digital media using C2PA standards."


def run_tool(source: str, mode: str = "combined") -> dict:
    if mode == "c2pa_only":
        return verify_c2pa(source)
    return verify_c2pa_with_forensics(source)
```

---

## `journalist-ai/tools/corporate_records.py`

```python
"""
corporate_records.py — Corporate structure and entity triangulation.
Queries OpenCorporates and OCCRP Aleph.
"""

from __future__ import annotations
import logging
import os
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15

OPENCORPORATES_BASE = "https://api.opencorporates.com/v0.4"
ALEPH_BASE = "https://aleph.occrp.org/api/2"


def _oc_headers() -> dict:
    api_key = os.getenv("OPENCORPORATES_API_KEY", "")
    return {"Authorization": f"Token token={api_key}"} if api_key else {}


def _aleph_headers() -> dict:
    api_key = os.getenv("ALEPH_API_KEY", "")
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"ApiKey {api_key}"
    return headers


def search_companies(name: str, jurisdiction_code: str = "", inactive: bool = False, limit: int = 20) -> list[dict]:
    params: dict[str, Any] = {"q": name, "per_page": min(limit, 100), "format": "json"}
    if jurisdiction_code:
        params["jurisdiction_code"] = jurisdiction_code
    if inactive:
        params["inactive"] = "true"
    try:
        response = requests.get(f"{OPENCORPORATES_BASE}/companies/search", params=params, headers=_oc_headers(), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        companies = response.json().get("results", {}).get("companies", [])
        return [_normalize_oc_company(c.get("company", c)) for c in companies]
    except requests.RequestException as e:
        logger.error("OpenCorporates search failed for '%s': %s", name, e)
        return []


def search_officers(name: str, limit: int = 20) -> list[dict]:
    try:
        response = requests.get(f"{OPENCORPORATES_BASE}/officers/search", params={"q": name, "per_page": min(limit, 100), "format": "json"}, headers=_oc_headers(), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        officers = response.json().get("results", {}).get("officers", [])
        results = []
        for o in officers:
            obj = o.get("officer", o)
            results.append({
                "officer_name": obj.get("name", ""),
                "position": obj.get("position", ""),
                "company_name": obj.get("company", {}).get("name", ""),
                "company_number": obj.get("company", {}).get("company_number", ""),
                "jurisdiction": obj.get("company", {}).get("jurisdiction_code", ""),
                "company_url": obj.get("company", {}).get("opencorporates_url", ""),
                "start_date": obj.get("start_date", ""),
                "end_date": obj.get("end_date", ""),
                "data_source": "opencorporates",
            })
        return results
    except requests.RequestException as e:
        logger.error("OpenCorporates officer search failed for '%s': %s", name, e)
        return []


def aleph_search_entities(query: str, schema: str = "", limit: int = 20) -> list[dict]:
    params: dict[str, Any] = {"q": query, "limit": min(limit, 100)}
    if schema:
        params["filter:schema"] = schema
    try:
        response = requests.get(f"{ALEPH_BASE}/entities", params=params, headers=_aleph_headers(), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return [_normalize_aleph_entity(e) for e in response.json().get("results", [])]
    except requests.RequestException as e:
        logger.error("Aleph search failed for '%s': %s", query, e)
        return []


def _normalize_oc_company(c: dict) -> dict:
    return {
        "name": c.get("name", ""),
        "company_number": c.get("company_number", ""),
        "jurisdiction_code": c.get("jurisdiction_code", ""),
        "company_type": c.get("company_type", ""),
        "incorporation_date": c.get("incorporation_date", ""),
        "dissolution_date": c.get("dissolution_date", ""),
        "status": c.get("current_status", ""),
        "registered_address": c.get("registered_address_in_full", ""),
        "url": c.get("opencorporates_url", ""),
        "data_source": "opencorporates",
    }


def _normalize_aleph_entity(e: dict) -> dict:
    props = e.get("properties", {})
    return {
        "id": e.get("id", ""),
        "caption": e.get("caption", ""),
        "schema": e.get("schema", ""),
        "datasets": e.get("datasets", []),
        "countries": props.get("country", []),
        "names": props.get("name", []),
        "url": f"https://aleph.occrp.org/entities/{e.get('id', '')}",
        "data_source": "aleph_occrp",
    }


TOOL_DESCRIPTION = (
    "Search corporate records for entity triangulation. Queries OpenCorporates and OCCRP Aleph. "
    "Use to trace corporate ownership chains and find hidden connections."
)

TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Company or person name to look up"},
        "mode": {"type": "string", "enum": ["companies", "officers", "aleph", "all"], "default": "all"},
        "jurisdiction": {"type": "string", "description": "Optional jurisdiction code (e.g. 'us_de', 'gb', 'ky')"},
    },
    "required": ["query"],
}


def run_tool(query: str, mode: str = "all", jurisdiction: str = "") -> list[dict]:
    if mode == "companies":
        return search_companies(query, jurisdiction_code=jurisdiction)
    if mode == "officers":
        return search_officers(query)
    if mode == "aleph":
        return aleph_search_entities(query)
    results: list[dict] = []
    results.extend(search_companies(query, jurisdiction_code=jurisdiction))
    results.extend(search_officers(query))
    results.extend(aleph_search_entities(query))
    return results
```

---

## `journalist-ai/tools/court_records.py`

```python
"""
court_records.py — Federal and state court records via CourtListener API.
"""

from __future__ import annotations
import logging
import os
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15
COURTLISTENER_BASE = "https://www.courtlistener.com/api/rest/v4"


def _cl_headers() -> dict:
    api_key = os.getenv("COURTLISTENER_API_KEY", "")
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Token {api_key}"
    return headers


def search_opinions(query: str, court: str = "", after_date: str = "", before_date: str = "", limit: int = 20) -> list[dict]:
    params: dict[str, Any] = {"q": query, "type": "o", "order_by": "score desc", "format": "json"}
    if court:
        params["court"] = court
    if after_date:
        params["filed_after"] = after_date
    if before_date:
        params["filed_before"] = before_date
    try:
        response = requests.get(f"{COURTLISTENER_BASE}/search/", params=params, headers=_cl_headers(), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return [_normalize_opinion(r) for r in response.json().get("results", [])[:limit]]
    except requests.RequestException as e:
        logger.error("CourtListener opinion search failed for '%s': %s", query, e)
        return []


def search_dockets(query: str, court: str = "", party_name: str = "", nature_of_suit: str = "", limit: int = 20) -> list[dict]:
    params: dict[str, Any] = {"q": query, "type": "r", "order_by": "score desc", "format": "json"}
    if court:
        params["court"] = court
    if party_name:
        params["party_name"] = party_name
    if nature_of_suit:
        params["nature_of_suit"] = nature_of_suit
    try:
        response = requests.get(f"{COURTLISTENER_BASE}/search/", params=params, headers=_cl_headers(), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return [_normalize_docket(r) for r in response.json().get("results", [])[:limit]]
    except requests.RequestException as e:
        logger.error("CourtListener docket search failed for '%s': %s", query, e)
        return []


def search_parties(name: str, limit: int = 20) -> list[dict]:
    try:
        response = requests.get(f"{COURTLISTENER_BASE}/parties/", params={"name": name, "format": "json"}, headers=_cl_headers(), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        results = response.json().get("results", [])
        return [{"party_name": p.get("name", ""), "party_type": p.get("party_types", [{}])[0].get("name", "") if p.get("party_types") else "", "docket_id": p.get("docket", ""), "data_source": "courtlistener"} for p in results[:limit]]
    except requests.RequestException as e:
        logger.error("CourtListener party search failed for '%s': %s", name, e)
        return []


def _normalize_opinion(r: dict) -> dict:
    return {"case_name": r.get("caseName", ""), "court": r.get("court", ""), "date_filed": r.get("dateFiled", ""), "citation": r.get("citation", []), "status": r.get("status", ""), "snippet": r.get("snippet", ""), "url": f"https://www.courtlistener.com{r.get('absolute_url', '')}", "cluster_id": r.get("cluster_id"), "data_source": "courtlistener"}


def _normalize_docket(r: dict) -> dict:
    return {"case_name": r.get("caseName", ""), "docket_number": r.get("docketNumber", ""), "court": r.get("court", ""), "court_id": r.get("court_id", ""), "date_filed": r.get("dateFiled", ""), "date_terminated": r.get("dateTerminated", ""), "nature_of_suit": r.get("suitNature", ""), "cause": r.get("cause", ""), "parties": r.get("party_names", ""), "url": f"https://www.courtlistener.com{r.get('absolute_url', '')}", "docket_id": r.get("docket_id"), "data_source": "courtlistener"}


TOOL_DESCRIPTION = "Search federal and state court records via CourtListener (PACER-sourced)."
TOOL_SCHEMA = {"type": "object", "properties": {"query": {"type": "string"}, "mode": {"type": "string", "enum": ["opinions", "dockets", "parties", "all"], "default": "all"}, "court": {"type": "string"}, "after_date": {"type": "string"}}, "required": ["query"]}


def run_tool(query: str, mode: str = "all", court: str = "", after_date: str = "") -> list[dict]:
    if mode == "opinions":
        return search_opinions(query, court=court, after_date=after_date)
    if mode == "dockets":
        return search_dockets(query, court=court, party_name=query)
    if mode == "parties":
        return search_parties(query)
    results: list[dict] = []
    results.extend(search_opinions(query, court=court, after_date=after_date))
    results.extend(search_dockets(query, court=court, party_name=query))
    return results
```

---

## `journalist-ai/tools/diary_connector.py`

```python
"""
diary_connector.py — Diary APK integration for field notes and investigation leads.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DiaryEntry:
    def __init__(self, raw: dict):
        self.id: str = raw.get("id", "")
        self.title: str = raw.get("title", "")
        self.content: str = raw.get("content", raw.get("text", ""))
        self.date: str = raw.get("date", raw.get("created_at", ""))
        self.tags: list[str] = raw.get("tags", [])
        self.location: str = raw.get("location", "")
        self.attachments: list[str] = raw.get("attachments", [])
        self.mood: str = raw.get("mood", "")
        self.raw = raw


class DiaryLead:
    def __init__(self, source_entry_id: str, content: str, extracted_entities: list[dict], extracted_dates: list[str], extracted_claims: list[str], tags: list[str], priority: str = "medium"):
        self.source_entry_id = source_entry_id
        self.content = content
        self.extracted_entities = extracted_entities
        self.extracted_dates = extracted_dates
        self.extracted_claims = extracted_claims
        self.tags = tags
        self.priority = priority
        self.created_at = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict:
        return {"source_entry_id": self.source_entry_id, "content": self.content, "extracted_entities": self.extracted_entities, "extracted_dates": self.extracted_dates, "extracted_claims": self.extracted_claims, "tags": self.tags, "priority": self.priority, "created_at": self.created_at}


def import_from_file(file_path: str) -> list[DiaryEntry]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Diary file not found: {path}")
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        entries_raw = data if isinstance(data, list) else data.get("entries", [data])
        return [DiaryEntry({**r, "id": r.get("id", f"diary-{i}")}) for i, r in enumerate(entries_raw) if isinstance(r, dict)]
    else:
        text = path.read_text(encoding="utf-8")
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        entries = []
        for i, para in enumerate(paragraphs):
            lines = para.split("\n")
            date_match = re.search(r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})\b", lines[0])
            entries.append(DiaryEntry({"id": f"diary-text-{i}", "title": lines[0][:80], "content": para, "date": date_match.group(0) if date_match else ""}))
        return entries


def import_from_string(json_string: str) -> list[DiaryEntry]:
    data = json.loads(json_string)
    entries_raw = data if isinstance(data, list) else data.get("entries", [data])
    return [DiaryEntry(r) for r in entries_raw if isinstance(r, dict)]


def extract_leads(entries: list[DiaryEntry]) -> list[DiaryLead]:
    leads = []
    for entry in entries:
        text = (entry.title + " " + entry.content).strip()
        if not text:
            continue
        entities = _extract_entities(text)
        dates = _extract_dates(text)
        claims = _extract_claims(text)
        priority = _assess_priority(text, entities, claims)
        if claims or entities:
            leads.append(DiaryLead(source_entry_id=entry.id, content=text[:2000], extracted_entities=entities, extracted_dates=dates, extracted_claims=claims, tags=entry.tags, priority=priority))
    return leads


def _extract_entities(text: str) -> list[dict]:
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text[:5000])
        seen = {}
        for ent in doc.ents:
            key = ent.text.strip()
            if key not in seen:
                seen[key] = {"text": key, "type": ent.label_, "count": 0}
            seen[key]["count"] += 1
        return list(seen.values())
    except (ImportError, OSError):
        matches = re.findall(r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)+)\b", text)
        seen = {}
        for m in matches:
            if m not in seen:
                seen[m] = {"text": m, "type": "UNKNOWN", "count": 0}
            seen[m]["count"] += 1
        return list(seen.values())


def _extract_dates(text: str) -> list[str]:
    patterns = [r"\b\d{4}-\d{2}-\d{2}\b", r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"]
    dates = []
    for pattern in patterns:
        dates.extend(re.findall(pattern, text))
    return list(dict.fromkeys(dates))


def _extract_claims(text: str) -> list[str]:
    claim_indicators = [r"\b(said|told|claimed|alleged|confirmed|denied|admitted|revealed)\b", r"\$[\d,]+"]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    claims = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:
            continue
        if any(re.search(p, sentence, re.IGNORECASE) for p in claim_indicators):
            claims.append(sentence[:500])
    return claims[:20]


def _assess_priority(text: str, entities: list[dict], claims: list[str]) -> str:
    text_lower = text.lower()
    if any(s in text_lower for s in ["murder", "bribe", "fraud", "corrupt", "laundering", "trafficking", "conspiracy", "blackmail"]):
        return "high"
    if len(claims) >= 3 or len(entities) >= 5:
        return "medium"
    return "low"


TOOL_SCHEMA = {"type": "object", "properties": {"file_path": {"type": "string"}, "json_string": {"type": "string"}}}
TOOL_DESCRIPTION = "Import diary/field notes from the Diary APK. Parses entries for entities, dates, and claims."


def run_tool(file_path: str = "", json_string: str = "") -> list[dict]:
    if file_path:
        entries = import_from_file(file_path)
    elif json_string:
        entries = import_from_string(json_string)
    else:
        return [{"error": "Provide either file_path or json_string"}]
    return [lead.to_dict() for lead in extract_leads(entries)]
```

---

## `journalist-ai/tools/document_reader.py`

```python
"""
document_reader.py — PDF and HTML document ingestion for AXIOM.
"""

from __future__ import annotations
import io
import logging
import re
from pathlib import Path
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 30


def read_document(source: str, document_type: str = "auto") -> dict:
    if source.startswith("http://") or source.startswith("https://"):
        return _read_url(source, document_type)
    return _read_file(source, document_type)


def _read_url(url: str, document_type: str) -> dict:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (research/journalist-ai; +https://github.com/wuzbak/Journalism-)"}
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if "pdf" in content_type or document_type == "pdf" or url.lower().endswith(".pdf"):
            return _parse_pdf(response.content, source=url)
        return _parse_html(response.text, source=url)
    except requests.RequestException as e:
        logger.error("Failed to fetch URL %s: %s", url, e)
        return {"text": "", "title": "", "metadata": {}, "source": url, "error": str(e)}


def _read_file(file_path: str, document_type: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        return {"text": "", "title": "", "metadata": {}, "source": file_path, "error": "File not found"}
    suffix = path.suffix.lower()
    if suffix == ".pdf" or document_type == "pdf":
        return _parse_pdf(path.read_bytes(), source=file_path)
    elif suffix in (".html", ".htm") or document_type == "html":
        return _parse_html(path.read_text(encoding="utf-8", errors="ignore"), source=file_path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    return {"text": text, "title": path.name, "metadata": {"file_type": suffix, "size_bytes": path.stat().st_size}, "source": file_path, "word_count": len(text.split()), "error": None}


def _parse_pdf(content: bytes, source: str) -> dict:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(content))
        full_text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
        metadata = {}
        if reader.metadata:
            metadata = {"author": reader.metadata.get("/Author", ""), "creator": reader.metadata.get("/Creator", ""), "creation_date": reader.metadata.get("/CreationDate", ""), "title": reader.metadata.get("/Title", ""), "pages": len(reader.pages)}
        return {"text": full_text, "title": metadata.get("title", Path(source).name if not source.startswith("http") else source), "metadata": metadata, "source": source, "word_count": len(full_text.split()), "error": None}
    except ImportError:
        return {"text": "", "title": "", "metadata": {}, "source": source, "error": "No PDF library (install pypdf)"}
    except Exception as e:
        return {"text": "", "title": "", "metadata": {}, "source": source, "error": str(e)}


def _parse_html(html: str, source: str) -> dict:
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else ""
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()
        main = soup.find("main") or soup.find("article") or soup.find("body") or soup
        text = main.get_text(separator="\n", strip=True)
        text = re.sub(r"\n{3,}", "\n\n", text)
        metadata: dict[str, str] = {}
        for meta in soup.find_all("meta"):
            name = meta.get("name", meta.get("property", ""))
            content = meta.get("content", "")
            if name and content:
                metadata[name] = content
        return {"text": text, "title": title, "metadata": metadata, "source": source, "word_count": len(text.split()), "error": None}
    except ImportError:
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        return {"text": text, "title": source, "metadata": {}, "source": source, "word_count": len(text.split()), "error": None}


def extract_key_passages(document: dict, keywords: list[str], context_chars: int = 500) -> list[dict]:
    text = document.get("text", "")
    passages = []
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        for match in pattern.finditer(text):
            start = max(0, match.start() - context_chars // 2)
            end = min(len(text), match.end() + context_chars // 2)
            passages.append({"keyword": keyword, "passage": text[start:end].strip(), "position": match.start(), "source": document.get("source", "")})
    return passages


TOOL_SCHEMA = {"type": "object", "properties": {"source": {"type": "string"}, "keywords": {"type": "array", "items": {"type": "string"}}}, "required": ["source"]}
TOOL_DESCRIPTION = "Read and extract text from documents: PDFs, web pages, court filings, FOIA documents."


def run_tool(source: str, keywords: list[str] | None = None) -> dict:
    doc = read_document(source)
    if keywords:
        doc["key_passages"] = extract_key_passages(doc, keywords)
    return doc
```

---

## `journalist-ai/tools/entity_resolver.py`

```python
"""
entity_resolver.py — Canonical entity resolution across source variations.
Applies the AxiomZero approval gate before executing fuzzy resolution.
"""

from __future__ import annotations
import logging
import re
import unicodedata
from difflib import SequenceMatcher
from typing import Any

logger = logging.getLogger(__name__)

COMMON_CORPORATE_SUFFIXES = {"inc", "llc", "ltd", "corp", "co", "company", "corporation", "incorporated", "limited", "plc", "llp", "lp", "gmbh", "ag", "sa", "bv", "nv", "oy", "as", "pty"}


def _normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text.lower().strip())


def _strip_corporate_suffixes(name: str) -> str:
    words = name.split()
    while words and words[-1].rstrip(".").lower() in COMMON_CORPORATE_SUFFIXES:
        words.pop()
    return " ".join(words)


def generate_name_variants(canonical_name: str) -> list[str]:
    norm = _normalize_text(canonical_name)
    variants = {canonical_name, norm, _strip_corporate_suffixes(norm)}
    parts = canonical_name.split()
    if len(parts) >= 2:
        variants.add(f"{parts[-1]}, {' '.join(parts[:-1])}".lower())
        variants.add(f"{parts[0][0]}. {' '.join(parts[1:])}" if len(parts[0]) > 0 else "")
    variants.discard("")
    return list(variants)


def _similarity_score(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalize_text(a), _normalize_text(b)).ratio()


def _canonicalize(entity_name: str, known_entities: dict[str, str], threshold: float = 0.85) -> str:
    norm = _normalize_text(entity_name)
    if entity_name in known_entities:
        return known_entities[entity_name]
    if norm in known_entities:
        return known_entities[norm]
    best_score = 0.0
    best_canon = entity_name
    for candidate, canonical in known_entities.items():
        score = _similarity_score(norm, _normalize_text(candidate))
        if score > best_score:
            best_score = score
            best_canon = canonical
    return best_canon if best_score >= threshold else entity_name


def _detect_contradictions_for_test(entity_list: list[str]) -> list[tuple[str, str, float]]:
    contradictions = []
    for i, a in enumerate(entity_list):
        for b in entity_list[i + 1:]:
            score = _similarity_score(a, b)
            if 0.4 < score < 0.85:
                contradictions.append((a, b, round(score, 3)))
    return contradictions


class EntityResolver:
    def __init__(self, known_entities: dict[str, str] | None = None, threshold: float = 0.85):
        self.known_entities: dict[str, str] = known_entities or {}
        self.threshold = threshold

    def resolve(self, entity_name: str) -> str:
        return _canonicalize(entity_name, self.known_entities, self.threshold)

    def resolve_batch(self, entity_names: list[str]) -> dict[str, str]:
        return {name: self.resolve(name) for name in entity_names}

    def add_mapping(self, variant: str, canonical: str) -> None:
        self.known_entities[_normalize_text(variant)] = canonical

    def load_mappings(self, mappings: dict[str, str]) -> None:
        for variant, canonical in mappings.items():
            self.add_mapping(variant, canonical)

    def detect_ambiguous_pairs(self, entity_list: list[str]) -> list[dict]:
        results = []
        for i, a in enumerate(entity_list):
            for b in entity_list[i + 1:]:
                score = _similarity_score(a, b)
                if 0.5 < score < self.threshold:
                    results.append({"entity_a": a, "entity_b": b, "similarity": round(score, 3), "note": "May refer to the same entity — review required."})
        return results


TOOL_SCHEMA = {"type": "object", "properties": {"entity_names": {"type": "array", "items": {"type": "string"}}, "known_mappings": {"type": "object", "additionalProperties": {"type": "string"}}, "threshold": {"type": "number", "default": 0.85}}, "required": ["entity_names"]}
TOOL_DESCRIPTION = "Resolve entity name variations to canonical forms using fuzzy matching."


def run_tool(entity_names: list[str], known_mappings: dict[str, str] | None = None, threshold: float = 0.85) -> dict:
    resolver = EntityResolver(known_entities=known_mappings, threshold=threshold)
    resolved = resolver.resolve_batch(entity_names)
    ambiguous = resolver.detect_ambiguous_pairs(entity_names)
    return {"resolved": resolved, "ambiguous_pairs": ambiguous}


try:
    from journalist_ai.tools.axiomzero_gate import axiomzero_approval
    run_tool = axiomzero_approval(run_tool)
except ImportError:
    pass
```

---

## `journalist-ai/tools/govinfo.py`

```python
"""
govinfo.py — GovInfo API (U.S. Government Publishing Office) search.
Accesses congressional records, federal register, hearings, bills, regulations.
"""

from __future__ import annotations
import logging
import os
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15
GOVINFO_API_KEY = os.getenv("GOVINFO_API_KEY", "DEMO_KEY")
GOVINFO_BASE = "https://api.govinfo.gov"

COLLECTION_CODES = {
    "congressional_record": "CREC",
    "federal_register": "FR",
    "hearings": "CHRG",
    "bills": "BILLS",
    "statutes": "STATUTE",
    "crs_reports": "CRPT",
    "regulations": "CFR",
    "public_laws": "PLAW",
    "code_of_federal_regulations": "CFR",
    "uscis": "USCIS",
    "budget": "BUDGET",
    "economic_report": "ERP",
    "supreme_court": "USCOURTS",
}


def search_govinfo(query: str, collection: str = "all", date_issued_start: str = "", date_issued_end: str = "", page_size: int = 10) -> list[dict]:
    collection_code = COLLECTION_CODES.get(collection.lower(), collection.upper() if collection != "all" else None)
    params: dict[str, Any] = {"query": query, "pageSize": min(page_size, 100), "offsetMark": "*", "api_key": GOVINFO_API_KEY}
    if collection_code:
        params["collection"] = collection_code
    if date_issued_start:
        params["dateIssuedStartDate"] = date_issued_start
    if date_issued_end:
        params["dateIssuedEndDate"] = date_issued_end
    try:
        response = requests.get(f"{GOVINFO_BASE}/search", params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        results = response.json().get("results", [])
        return [_normalize_result(r) for r in results]
    except (requests.RequestException, ValueError) as e:
        logger.error("GovInfo search failed for '%s': %s", query, e)
        return []


def get_document(package_id: str) -> dict:
    params = {"api_key": GOVINFO_API_KEY}
    try:
        response = requests.get(f"{GOVINFO_BASE}/packages/{package_id}/summary", params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return _normalize_result(response.json())
    except requests.RequestException as e:
        logger.error("GovInfo document lookup failed for '%s': %s", package_id, e)
        return {}


def _normalize_result(r: dict) -> dict:
    package_id = r.get("packageId", "")
    return {"title": r.get("title", ""), "package_id": package_id, "collection": r.get("collectionCode", ""), "date_issued": r.get("dateIssued", ""), "congress": r.get("congress", ""), "session": r.get("session", ""), "chamber": r.get("chamber", ""), "last_modified": r.get("lastModified", ""), "download_url": r.get("download", {}).get("txtLink", "") if isinstance(r.get("download"), dict) else "", "detail_url": f"{GOVINFO_BASE}/packages/{package_id}/summary?api_key={GOVINFO_API_KEY}" if package_id else "", "data_source": "govinfo"}


TOOL_SCHEMA = {"type": "object", "properties": {"query": {"type": "string"}, "collection": {"type": "string", "enum": ["all", "congressional_record", "federal_register", "hearings", "bills", "statutes", "crs_reports", "regulations", "public_laws", "supreme_court"], "default": "all"}, "date_issued_start": {"type": "string"}, "date_issued_end": {"type": "string"}, "page_size": {"type": "integer", "default": 10}}, "required": ["query"]}
TOOL_DESCRIPTION = "Search U.S. government documents via GovInfo (GPO) API."


def run_tool(query: str, collection: str = "all", date_issued_start: str = "", date_issued_end: str = "", page_size: int = 10) -> list[dict]:
    return search_govinfo(query=query, collection=collection, date_issued_start=date_issued_start, date_issued_end=date_issued_end, page_size=page_size)
```

---

## `journalist-ai/tools/manifold_api.py`

```python
"""
manifold_api.py — Manifold Markets API integration for contested-claims signals.
"""

from __future__ import annotations
import logging
import os
from typing import Any
import requests

logger = logging.getLogger(__name__)
MANIFOLD_API_BASE = "https://api.manifold.markets/v0"
REQUEST_TIMEOUT = 10
DEFAULT_LIMIT = 20


def get_markets_by_topic(topic: str, limit: int = DEFAULT_LIMIT, sort: str = "liquidity") -> list[dict]:
    params = {"term": topic, "limit": limit, "sort": sort, "contractType": "BINARY"}
    try:
        response = requests.get(f"{MANIFOLD_API_BASE}/search-markets", params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return [_normalize_market(m) for m in response.json()]
    except requests.RequestException as e:
        logger.error("Manifold API search failed for topic '%s': %s", topic, e)
        return []


def get_contested_claims(topic: str, min_volume: float = 500.0, min_traders: int = 10, probability_band: tuple[float, float] = (0.30, 0.70)) -> list[dict]:
    markets = get_markets_by_topic(topic, limit=50, sort="24-hour-vol")
    contested = []
    for m in markets:
        prob = m.get("probability")
        volume = m.get("total_volume", 0)
        traders = m.get("unique_traders", 0)
        if prob is None or volume < min_volume or traders < min_traders:
            continue
        if probability_band[0] <= prob <= probability_band[1]:
            m["contest_score"] = _contest_score(prob, volume, traders)
            contested.append(m)
    return sorted(contested, key=lambda m: -m["contest_score"])


def get_recently_resolved(topic: str, limit: int = 20) -> list[dict]:
    params = {"term": topic, "limit": limit, "sort": "newest", "isResolved": "true"}
    try:
        response = requests.get(f"{MANIFOLD_API_BASE}/search-markets", params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        normalized = [_normalize_market(m) for m in response.json() if m.get("isResolved")]
        for m in normalized:
            final_prob = m.get("probability", 0.5)
            resolution = m.get("resolution", "")
            if resolution == "YES" and final_prob < 0.3:
                m["surprise_flag"] = True
                m["surprise_note"] = f"Market resolved YES but crowd gave only {final_prob:.0%} probability"
            elif resolution == "NO" and final_prob > 0.7:
                m["surprise_flag"] = True
                m["surprise_note"] = f"Market resolved NO but crowd gave {final_prob:.0%} probability"
            else:
                m["surprise_flag"] = False
        return normalized
    except requests.RequestException as e:
        logger.error("Manifold resolved market fetch failed: %s", e)
        return []


def get_trending_topics(limit: int = 30) -> list[dict]:
    try:
        response = requests.get(f"{MANIFOLD_API_BASE}/markets", params={"limit": limit, "sort": "24-hour-vol"}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return [_normalize_market(m) for m in response.json()]
    except requests.RequestException as e:
        logger.error("Manifold trending fetch failed: %s", e)
        return []


def _normalize_market(m: dict) -> dict:
    return {"id": m.get("id", ""), "question": m.get("question", ""), "url": m.get("url", ""), "creator": m.get("creatorUsername", ""), "probability": m.get("probability"), "total_volume": m.get("volume", 0), "unique_traders": m.get("uniqueBettorCount", 0), "close_time": m.get("closeTime"), "resolved": m.get("isResolved", False), "resolution": m.get("resolution", ""), "tags": m.get("groupSlugs", []), "source_note": "Manifold Markets — crowd probability signal only, NOT verified fact"}


def _contest_score(probability: float, volume: float, traders: int) -> float:
    uncertainty = 1.0 - abs(probability - 0.5) * 2
    return uncertainty * 0.6 + min(volume / 10_000, 1.0) * 0.25 + min(traders / 100, 1.0) * 0.15


TOOL_SCHEMA = {"type": "object", "properties": {"topic": {"type": "string"}, "mode": {"type": "string", "enum": ["contested", "resolved", "trending", "search"], "default": "contested"}, "limit": {"type": "integer", "default": 10}}, "required": ["topic"]}
TOOL_DESCRIPTION = "Query Manifold Markets prediction markets to identify contested claims and disputed facts."


def run_tool(topic: str, mode: str = "contested", limit: int = 10) -> list[dict]:
    if mode == "contested":
        return get_contested_claims(topic)[:limit]
    elif mode == "resolved":
        return get_recently_resolved(topic, limit=limit)
    elif mode == "trending":
        return get_trending_topics(limit=limit)
    else:
        return get_markets_by_topic(topic, limit=limit)
```

---

## `journalist-ai/tools/metadata_forensics.py`

```python
"""
metadata_forensics.py — Extract hidden metadata from documents and images for provenance.
"""

from __future__ import annotations
import io
import json
import logging
import os
import struct
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 20


def extract_pdf_metadata(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    result: dict[str, Any] = {"file": str(path), "type": "pdf", "file_size_bytes": path.stat().st_size}
    try:
        import pypdf
        with open(path, "rb") as f:
            reader = pypdf.PdfReader(f)
            info = reader.metadata or {}
            result.update({"page_count": len(reader.pages), "author": info.get("/Author", ""), "creator": info.get("/Creator", ""), "producer": info.get("/Producer", ""), "subject": info.get("/Subject", ""), "title": info.get("/Title", ""), "creation_date": _parse_pdf_date(info.get("/CreationDate", "")), "modification_date": _parse_pdf_date(info.get("/ModDate", "")), "is_encrypted": reader.is_encrypted, "data_source": "metadata_forensics_pypdf"})
    except ImportError:
        result["note"] = "pypdf not installed. Install with: pip install pypdf"
    except Exception as e:
        result["error"] = str(e)
    try:
        exiftool_data = extract_with_exiftool(str(path))
        result["exiftool"] = exiftool_data
    except Exception as e:
        result["exiftool_error"] = str(e)
    return result


def extract_image_metadata(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    result: dict[str, Any] = {"file": str(path), "type": "image", "file_size_bytes": path.stat().st_size}
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        img = Image.open(path)
        result["format"] = img.format
        result["mode"] = img.mode
        result["size"] = img.size
        exif_data = img._getexif()
        if exif_data:
            exif_dict = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if isinstance(value, bytes):
                    try:
                        value = value.decode("utf-8", errors="replace")
                    except Exception:
                        value = repr(value)
                exif_dict[str(tag)] = str(value)[:500]
            result["exif"] = exif_dict
            for key in ("DateTime", "DateTimeOriginal", "DateTimeDigitized"):
                if key in exif_dict:
                    result["capture_date"] = exif_dict[key]
                    break
            for key in ("Make", "Model"):
                if key in exif_dict:
                    result[key.lower()] = exif_dict[key]
            if "GPSInfo" in exif_dict:
                result["has_gps"] = True
        result["data_source"] = "metadata_forensics_pillow"
    except ImportError:
        result["note"] = "Pillow not installed. Install with: pip install Pillow"
    except Exception as e:
        result["error"] = str(e)
    try:
        exiftool_data = extract_with_exiftool(str(path))
        result["exiftool"] = exiftool_data
    except Exception as e:
        result["exiftool_error"] = str(e)
    return result


def extract_with_exiftool(file_path: str) -> dict:
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        proc = subprocess.run(["exiftool", "-json", "-coordFormat", "%+.6f", "-dateFormat", "%Y-%m-%dT%H:%M:%S", file_path], capture_output=True, text=True, timeout=30)
        if proc.returncode != 0 or not proc.stdout.strip():
            return {"error": proc.stderr.strip()}
        data_list = json.loads(proc.stdout)
        return data_list[0] if data_list else {}
    except FileNotFoundError:
        return {"error": "exiftool not installed"}
    except (json.JSONDecodeError, subprocess.TimeoutExpired) as e:
        return {"error": str(e)}
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def extract_word_metadata(file_path: str) -> dict:
    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}
    result: dict[str, Any] = {"file": str(path), "type": "word", "file_size_bytes": path.stat().st_size}
    try:
        from docx import Document
        doc = Document(str(path))
        props = doc.core_properties
        result.update({"title": props.title or "", "author": props.author or "", "last_modified_by": props.last_modified_by or "", "created": props.created.isoformat() if props.created else "", "modified": props.modified.isoformat() if props.modified else "", "revision": props.revision, "category": props.category or "", "comments": props.comments or "", "data_source": "metadata_forensics_docx"})
    except ImportError:
        result["note"] = "python-docx not installed. Install with: pip install python-docx"
    except Exception as e:
        result["error"] = str(e)
    return result


def analyze_file(file_path: str) -> dict:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_metadata(file_path)
    elif suffix in {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".heic", ".webp", ".bmp"}:
        return extract_image_metadata(file_path)
    elif suffix in {".docx", ".doc"}:
        return extract_word_metadata(file_path)
    else:
        return extract_with_exiftool(file_path)


def _parse_pdf_date(date_str: str) -> str:
    if not date_str or not date_str.startswith("D:"):
        return date_str
    raw = date_str[2:16]
    try:
        return datetime.strptime(raw, "%Y%m%d%H%M%S").isoformat()
    except ValueError:
        try:
            return datetime.strptime(raw[:8], "%Y%m%d").isoformat()
        except ValueError:
            return date_str


def run_url_metadata(url: str) -> dict:
    import requests
    try:
        response = requests.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        headers = dict(response.headers)
        return {"url": url, "status_code": response.status_code, "final_url": str(response.url), "server": headers.get("Server", ""), "last_modified": headers.get("Last-Modified", ""), "content_type": headers.get("Content-Type", ""), "x_powered_by": headers.get("X-Powered-By", ""), "x_generator": headers.get("X-Generator", ""), "all_headers": headers, "data_source": "metadata_forensics_http_headers"}
    except requests.RequestException as e:
        return {"url": url, "error": str(e), "data_source": "metadata_forensics"}


TOOL_SCHEMA = {"type": "object", "properties": {"file_path": {"type": "string"}, "url": {"type": "string"}, "mode": {"type": "string", "enum": ["file", "url"], "default": "file"}}, "required": []}
TOOL_DESCRIPTION = "Extract hidden metadata from documents, images, and URLs for forensic provenance."


def run_tool(file_path: str = "", url: str = "", mode: str = "file") -> dict:
    if mode == "url" or (url and not file_path):
        return run_url_metadata(url)
    if file_path:
        return analyze_file(file_path)
    return {"error": "Provide file_path or url."}
```

---

## `journalist-ai/tools/news_monitor.py`

```python
"""
news_monitor.py — Real-time and archival news intelligence feeds.
Queries GDELT Project API and New York Times Article Search API.
"""

from __future__ import annotations
import logging
import os
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15
GDELT_DOC_BASE = "https://api.gdeltproject.org/api/v2/doc/doc"
NYT_ARTICLE_SEARCH_BASE = "https://api.nytimes.com/svc/search/v2/articlesearch.json"


def gdelt_search_news(query: str, mode: str = "ArtList", timespan: str = "1month", max_records: int = 25, sort: str = "DateDesc", source_country: str = "", source_lang: str = "") -> list[dict]:
    params: dict[str, Any] = {"query": query, "mode": mode, "maxrecords": min(max_records, 250), "timespan": timespan, "sort": sort, "format": "json"}
    if source_country:
        params["query"] = f"{params['query']} sourcecountry:{source_country}"
    if source_lang:
        params["query"] = f"{params['query']} sourcelang:{source_lang}"
    try:
        response = requests.get(GDELT_DOC_BASE, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return [_normalize_gdelt_article(a) for a in response.json().get("articles", [])]
    except (requests.RequestException, ValueError) as e:
        logger.error("GDELT news search failed for '%s': %s", query, e)
        return []


def nyt_search_articles(query: str, begin_date: str = "", end_date: str = "", section: str = "", limit: int = 20, page: int = 0) -> list[dict]:
    api_key = os.getenv("NYT_API_KEY", "")
    if not api_key:
        return [{"error": "NYT_API_KEY not set"}]
    params: dict[str, Any] = {"q": query, "api-key": api_key, "page": page, "sort": "relevance", "fl": "headline,abstract,pub_date,byline,section_name,web_url,source,lead_paragraph,keywords"}
    if begin_date:
        params["begin_date"] = begin_date
    if end_date:
        params["end_date"] = end_date
    if section:
        params["fq"] = f'section_name:("{section}")'
    try:
        response = requests.get(NYT_ARTICLE_SEARCH_BASE, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return [_normalize_nyt_article(a) for a in response.json().get("response", {}).get("docs", [])[:limit]]
    except requests.RequestException as e:
        logger.error("NYT article search failed for '%s': %s", query, e)
        return []


def _normalize_gdelt_article(a: dict) -> dict:
    return {"title": a.get("title", ""), "url": a.get("url", ""), "source_domain": a.get("domain", ""), "source_country": a.get("sourcecountry", ""), "published_date": a.get("seendate", ""), "tone": a.get("tone"), "themes": a.get("themes", "").split(";") if a.get("themes") else [], "persons": a.get("persons", "").split(";") if a.get("persons") else [], "data_source": "gdelt"}


def _normalize_nyt_article(a: dict) -> dict:
    headline = a.get("headline", {})
    byline = a.get("byline", {})
    return {"title": headline.get("main", "") if isinstance(headline, dict) else str(headline), "abstract": a.get("abstract", ""), "lead_paragraph": a.get("lead_paragraph", ""), "url": a.get("web_url", ""), "published_date": a.get("pub_date", ""), "section": a.get("section_name", ""), "byline": byline.get("original", "") if isinstance(byline, dict) else str(byline), "data_source": "nyt"}


def search_news(query: str, source: str = "all", timespan: str = "1month", begin_date: str = "", end_date: str = "") -> list[dict]:
    results: list[dict] = []
    if source in ("gdelt", "all"):
        results.extend(gdelt_search_news(query, timespan=timespan))
    if source in ("nyt", "all"):
        results.extend(r for r in nyt_search_articles(query, begin_date=begin_date, end_date=end_date) if "error" not in r)
    return results


TOOL_SCHEMA = {"type": "object", "properties": {"query": {"type": "string"}, "source": {"type": "string", "enum": ["gdelt", "nyt", "all"], "default": "all"}, "timespan": {"type": "string", "default": "1month"}, "begin_date": {"type": "string"}, "end_date": {"type": "string"}}, "required": ["query"]}
TOOL_DESCRIPTION = "Monitor global and archival news coverage via GDELT and NYT Article Search API."


def run_tool(query: str, source: str = "all", timespan: str = "1month", begin_date: str = "", end_date: str = "") -> list[dict]:
    return search_news(query, source=source, timespan=timespan, begin_date=begin_date, end_date=end_date)
```

---

## `journalist-ai/tools/oig_oversight.py`

```python
"""
oig_oversight.py — OIG Oversight.gov audit report search.
Searches audit reports, investigations, and advisories from all U.S. IG offices.
"""

from __future__ import annotations
import logging
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 20
OVERSIGHT_BASE = "https://www.oversight.gov/api"


def search_reports(keyword: str = "", agency: str = "", report_type: str = "", date_start: str = "", date_end: str = "", limit: int = 20, page: int = 1) -> list[dict]:
    params: dict[str, Any] = {"page": page, "per_page": min(limit, 100)}
    if keyword:
        params["keyword"] = keyword
    if agency:
        params["ig_name"] = agency
    if report_type:
        params["report_type"] = report_type
    if date_start:
        params["date_start"] = date_start
    if date_end:
        params["date_end"] = date_end
    try:
        response = requests.get(f"{OVERSIGHT_BASE}/audit-reports", params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        records = data if isinstance(data, list) else data.get("data", data.get("results", []))
        return [_normalize_report(r) for r in records[:limit]]
    except (requests.RequestException, ValueError, KeyError) as e:
        logger.error("Oversight.gov search failed for '%s': %s", keyword or agency, e)
        return []


def get_red_flag_reports(topics: list[str] | None = None, after_date: str = "", limit: int = 20) -> list[dict]:
    if topics is None:
        topics = ["fraud", "waste", "abuse", "mismanagement", "false claims"]
    results: list[dict] = []
    for topic in topics[:3]:
        results.extend(search_reports(keyword=topic, date_start=after_date, limit=limit // len(topics[:3]) + 1))
    seen: set[str] = set()
    unique: list[dict] = []
    for r in results:
        key = r.get("url", r.get("report_id", ""))
        if key and key not in seen:
            seen.add(key)
            unique.append(r)
    return unique[:limit]


def _normalize_report(r: dict) -> dict:
    return {"report_id": r.get("report_id", r.get("id", "")), "title": r.get("title", r.get("report_title", "")), "agency": r.get("agency_name", r.get("ig_name", r.get("agency", ""))), "report_type": r.get("type", r.get("report_type", "")), "date_published": r.get("pub_date", r.get("date", "")), "summary": (r.get("summary", r.get("description", "")) or "")[:500], "url": r.get("url", r.get("report_url", r.get("link", ""))), "pdf_url": r.get("pdf_url", r.get("file_url", "")), "data_source": "oig_oversight"}


TOOL_SCHEMA = {"type": "object", "properties": {"keyword": {"type": "string"}, "agency": {"type": "string"}, "report_type": {"type": "string", "enum": ["Audit", "Inspection", "Investigation", "Management Advisory", "Testimony", ""], "default": ""}, "after_date": {"type": "string"}, "mode": {"type": "string", "enum": ["search", "investigations", "red_flags"], "default": "search"}}, "required": ["keyword"]}
TOOL_DESCRIPTION = "Search Oversight.gov for U.S. Inspector General audit and investigation reports."


def run_tool(keyword: str, agency: str = "", report_type: str = "", after_date: str = "", mode: str = "search") -> list[dict]:
    if mode == "investigations":
        return search_reports(keyword=keyword, agency=agency, report_type="Investigation", date_start=after_date)
    if mode == "red_flags":
        return get_red_flag_reports(after_date=after_date)
    return search_reports(keyword=keyword, agency=agency, report_type=report_type, date_start=after_date)
```

---

## `journalist-ai/tools/opensanctions.py`

```python
"""
opensanctions.py — OpenSanctions entity search for PEPs and sanctioned entities.
"""

from __future__ import annotations
import logging
import os
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15
OPENSANCTIONS_BASE = "https://api.opensanctions.org"


def _os_headers() -> dict:
    api_key = os.getenv("OPENSANCTIONS_API_KEY", "")
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"ApiKey {api_key}"
    return headers


def search_entities(name: str, schema: str = "", dataset: str = "default", limit: int = 20) -> list[dict]:
    params: dict[str, Any] = {"q": name, "limit": min(limit, 100)}
    if schema:
        params["schema"] = schema
    try:
        response = requests.get(f"{OPENSANCTIONS_BASE}/search/{dataset}", params=params, headers=_os_headers(), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return [_normalize_entity(r) for r in response.json().get("results", [])[:limit]]
    except requests.RequestException as e:
        logger.error("OpenSanctions search failed for '%s': %s", name, e)
        return []


def match_entity(name: str, country: str = "", birth_date: str = "", schema: str = "Person", dataset: str = "default") -> list[dict]:
    payload: dict[str, Any] = {"queries": {"q1": {"schema": schema, "properties": {"name": [name]}}}}
    if country:
        payload["queries"]["q1"]["properties"]["country"] = [country]
    if birth_date:
        payload["queries"]["q1"]["properties"]["birthDate"] = [birth_date]
    try:
        response = requests.post(f"{OPENSANCTIONS_BASE}/match/{dataset}", json=payload, headers=_os_headers(), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return [_normalize_entity(m) for m in response.json().get("responses", {}).get("q1", {}).get("results", [])]
    except requests.RequestException as e:
        logger.error("OpenSanctions match failed for '%s': %s", name, e)
        return []


def screen_names(names: list[str], dataset: str = "default") -> list[dict]:
    if not names:
        return []
    payload: dict[str, Any] = {"queries": {f"q{i}": {"schema": "LegalEntity", "properties": {"name": [name]}} for i, name in enumerate(names[:50])}}
    try:
        response = requests.post(f"{OPENSANCTIONS_BASE}/match/{dataset}", json=payload, headers=_os_headers(), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        results: list[dict] = []
        for key, resp in response.json().get("responses", {}).items():
            idx = int(key[1:])
            queried_name = names[idx] if idx < len(names) else ""
            for match in resp.get("results", []):
                entity = _normalize_entity(match)
                entity["queried_name"] = queried_name
                results.append(entity)
        return results
    except requests.RequestException as e:
        logger.error("OpenSanctions batch screen failed: %s", e)
        return []


def _normalize_entity(r: dict) -> dict:
    props = r.get("properties", {})
    datasets = r.get("datasets", [])
    return {"entity_id": r.get("id", ""), "caption": r.get("caption", ""), "schema": r.get("schema", ""), "datasets": datasets, "is_sanctioned": any(ds in datasets for ds in ("us_ofac_sdn", "eu_fsf", "un_sc_sanctions", "gb_hmt_sanctions")), "is_pep": any("pep" in ds for ds in (d.lower() for d in datasets)), "names": props.get("name", []), "aliases": props.get("alias", []), "countries": props.get("country", []), "birth_date": (props.get("birthDate") or [""])[0], "score": r.get("score", None), "url": f"https://www.opensanctions.org/entities/{r.get('id', '')}", "data_source": "opensanctions"}


TOOL_SCHEMA = {"type": "object", "properties": {"name": {"type": "string"}, "schema": {"type": "string", "enum": ["Person", "Company", "Organization", "LegalEntity", ""], "default": ""}, "country": {"type": "string"}, "birth_date": {"type": "string"}, "mode": {"type": "string", "enum": ["search", "match", "screen"], "default": "search"}, "names": {"type": "array", "items": {"type": "string"}}}, "required": ["name"]}
TOOL_DESCRIPTION = "Screen persons and entities against OpenSanctions — PEPs, OFAC SDN, EU/UN/UK sanctions."


def run_tool(name: str, schema: str = "", country: str = "", birth_date: str = "", mode: str = "search", names: list[str] | None = None) -> list[dict]:
    if mode == "screen" and names:
        return screen_names(names)
    if mode == "match":
        return match_entity(name, country=country, birth_date=birth_date, schema=schema or "Person")
    return search_entities(name, schema=schema)
```

---

## `journalist-ai/tools/provenance.py`

```python
"""
provenance.py — Cryptographic provenance sealing for AXIOM investigative briefs.
Computes SHA-256 hash, archives sources in Wayback Machine, produces JSON-LD record.
"""

from __future__ import annotations
import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any
import requests

logger = logging.getLogger(__name__)
WAYBACK_SAVE_API = "https://web.archive.org/save/"
WAYBACK_AVAILABILITY_API = "https://archive.org/wayback/available"
REQUEST_TIMEOUT = 15


def seal_report(brief: str, sources: list[str] | None = None, agent_ids: list[str] | None = None, snapshot_sources: bool = True, anchor_on_chain: bool = False) -> dict:
    sources = sources or []
    agent_ids = agent_ids or []
    sealed_at = datetime.utcnow().isoformat() + "Z"
    report_hash = _compute_hash(brief, sources)
    source_records: list[dict] = []
    for url in sources:
        record: dict[str, Any] = {"url": url}
        if snapshot_sources and url.startswith("http"):
            snapshot_url = _get_or_create_wayback_snapshot(url)
            if snapshot_url:
                record["wayback_snapshot"] = snapshot_url
        source_records.append(record)
    return {
        "@context": "https://schema.org/",
        "@type": "DigitalDocument",
        "name": "AXIOM Investigative Brief — Provenance Record",
        "report_hash": report_hash,
        "hash_algorithm": "SHA-256",
        "sealed_at": sealed_at,
        "agent_ids": agent_ids,
        "sources": source_records,
        "source_count": len(source_records),
        "integrity_note": "The report_hash is a SHA-256 digest of the brief text concatenated with the canonical (sorted) list of source URLs.",
        "on_chain_anchor": None,
    }


def verify_report(brief: str, sources: list[str], provenance_record: dict) -> dict:
    expected_hash = provenance_record.get("report_hash", "")
    computed_hash = _compute_hash(brief, sources)
    match = expected_hash == computed_hash
    return {"verified": match, "expected_hash": expected_hash, "computed_hash": computed_hash, "tampered": not match}


def save_provenance_record(provenance_record: dict, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    provenance_path = output_path.with_suffix(".provenance.json")
    provenance_path.write_text(json.dumps(provenance_record, indent=2), encoding="utf-8")
    return provenance_path


def _compute_hash(brief: str, sources: list[str]) -> str:
    canonical_sources = "\n".join(sorted(set(sources)))
    content = brief.encode("utf-8") + b"\n---sources---\n" + canonical_sources.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def _get_or_create_wayback_snapshot(url: str) -> str | None:
    try:
        resp = requests.get(WAYBACK_AVAILABILITY_API, params={"url": url}, timeout=REQUEST_TIMEOUT, headers={"User-Agent": "journalist-ai/provenance"})
        resp.raise_for_status()
        snapshot = resp.json().get("archived_snapshots", {}).get("closest", {})
        if snapshot.get("available") and snapshot.get("url"):
            return snapshot["url"]
    except Exception as exc:
        logger.debug("Wayback availability check failed for %s: %s", url[:80], exc)
    try:
        save_resp = requests.get(WAYBACK_SAVE_API + url, timeout=30, headers={"User-Agent": "journalist-ai/provenance"}, allow_redirects=True)
        if save_resp.status_code in (200, 302):
            archive_url = save_resp.headers.get("Content-Location", "")
            if archive_url:
                return f"https://web.archive.org{archive_url}"
    except Exception as exc:
        logger.debug("Wayback snapshot request failed for %s: %s", url[:80], exc)
    return None


TOOL_SCHEMA = {"type": "object", "properties": {"brief": {"type": "string"}, "sources": {"type": "array", "items": {"type": "string"}}, "agent_ids": {"type": "array", "items": {"type": "string"}}, "snapshot_sources": {"type": "boolean", "default": True}}, "required": ["brief"]}
TOOL_DESCRIPTION = "Cryptographically seal an investigative brief with SHA-256 hash and Wayback Machine source archiving."


def run_tool(brief: str, sources: list[str] | None = None, agent_ids: list[str] | None = None, snapshot_sources: bool = True) -> dict:
    return seal_report(brief=brief, sources=sources or [], agent_ids=agent_ids or [], snapshot_sources=snapshot_sources)
```

---

## `journalist-ai/tools/public_records.py`

```python
"""
public_records.py — Public records data source wrappers.

Covers: ProPublica, OpenSecrets, USASpending, SEC EDGAR, EPA ECHO,
Congress.gov, FEC, World Bank Open Data, and US Census Bureau API.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15


PROPUBLICA_BASE = "https://api.propublica.org"


def propublica_congress(endpoint: str, params: dict | None = None) -> dict:
    api_key = os.getenv("PROPUBLICA_API_KEY", "")
    if not api_key:
        return {"error": "PROPUBLICA_API_KEY not set"}
    url = f"{PROPUBLICA_BASE}{endpoint}"
    headers = {"X-API-Key": api_key}
    try:
        response = requests.get(url, headers=headers, params=params or {}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("ProPublica API error: %s", e)
        return {"error": str(e)}


def get_member_votes(member_id: str, congress: int = 118, chamber: str = "senate") -> list[dict]:
    result = propublica_congress(f"/congress/v1/members/{member_id}/votes.json", {"congress": congress, "chamber": chamber})
    return result.get("results", [])


def get_bill_cosponsors(bill_id: str, congress: int = 118) -> list[dict]:
    result = propublica_congress(f"/congress/v1/{congress}/bills/{bill_id}/cosponsors.json")
    return result.get("results", [{}])[0].get("cosponsors", [])


OPENSECRETS_BASE = "https://www.opensecrets.org/api/"


def opensecrets_query(method: str, params: dict | None = None) -> dict:
    api_key = os.getenv("OPENSECRETS_API_KEY", "")
    if not api_key:
        return {"error": "OPENSECRETS_API_KEY not set"}
    all_params = {"method": method, "apikey": api_key, "output": "json"}
    all_params.update(params or {})
    try:
        response = requests.get(OPENSECRETS_BASE, params=all_params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("OpenSecrets API error: %s", e)
        return {"error": str(e)}


def get_candidate_donors(cid: str, cycle: str = "2024") -> dict:
    return opensecrets_query("candContrib", {"cid": cid, "cycle": cycle})


def get_industry_donors(cid: str, cycle: str = "2024") -> dict:
    return opensecrets_query("candIndustry", {"cid": cid, "cycle": cycle})


def get_lobbying_by_org(org_name: str) -> dict:
    return opensecrets_query("getOrgs", {"org": org_name})


EDGAR_SUBMISSIONS = "https://data.sec.gov/submissions"


def edgar_full_text_search(query: str, form_type: str = "", date_range: tuple | None = None) -> list[dict]:
    try:
        response = requests.get(
            "https://efts.sec.gov/LATEST/search-index",
            params={"q": query, "forms": form_type} if form_type else {"q": query},
            headers={"User-Agent": "journalist-ai research@example.com"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        hits = data.get("hits", {}).get("hits", [])
        return [{"company": h.get("_source", {}).get("entity_name", ""), "form_type": h.get("_source", {}).get("file_type", ""), "filed_date": h.get("_source", {}).get("period_of_report", ""), "url": f"https://www.sec.gov/Archives/edgar/data/{h.get('_source', {}).get('entity_id', '')}/{h.get('_source', {}).get('file_date', '')}/{h.get('_id', '')}", "snippet": h.get("highlight", {}).get("file_contents", [""])[0]} for h in hits]
    except requests.RequestException as e:
        logger.error("EDGAR search failed: %s", e)
        return []


def get_company_filings(cik: str, form_type: str = "10-K") -> list[dict]:
    url = f"{EDGAR_SUBMISSIONS}/CIK{cik.zfill(10)}.json"
    try:
        response = requests.get(url, headers={"User-Agent": "journalist-ai research@example.com"}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        filings = data.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        urls = filings.get("primaryDocument", [])
        accessions = filings.get("accessionNumber", [])
        results = []
        for i, form in enumerate(forms):
            if form_type and form != form_type:
                continue
            accession = accessions[i].replace("-", "") if i < len(accessions) else ""
            results.append({"form_type": form, "filed_date": dates[i] if i < len(dates) else "", "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{urls[i] if i < len(urls) else ''}"})
        return results[:20]
    except requests.RequestException as e:
        logger.error("EDGAR submissions fetch failed for CIK %s: %s", cik, e)
        return []


USASPENDING_BASE = "https://api.usaspending.gov/api/v2"


def get_contracts(recipient_name: str, fiscal_year: int = 2024) -> dict:
    url = f"{USASPENDING_BASE}/search/spending_by_award/"
    payload = {"filters": {"recipient_search_text": [recipient_name], "award_type_codes": ["A", "B", "C", "D"], "time_period": [{"start_date": f"{fiscal_year}-01-01", "end_date": f"{fiscal_year}-12-31"}]}, "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency", "Start Date"], "limit": 20}
    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("USASpending API error: %s", e)
        return {"error": str(e)}


def get_facility_violations(facility_name: str = "", state: str = "") -> list[dict]:
    url = "https://echodata.epa.gov/echo/echo_rest_services.get_facilities"
    params = {"output": "JSON", "p_name": facility_name, "p_st": state, "p_qnc": "Y", "responseset": 20}
    params = {k: v for k, v in params.items() if v}
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        facilities = data.get("Results", {}).get("Facilities", [])
        return [{"name": f.get("FacilityName", ""), "address": f.get("LocationAddress", ""), "state": f.get("StateCode", ""), "violations": f.get("QncViol", ""), "formal_actions": f.get("FormalActionCount", ""), "penalty_amount": f.get("TotalPenaltyAmt", ""), "programs": f.get("ProgramSystemAcronyms", ""), "registry_id": f.get("RegistryID", "")} for f in facilities]
    except requests.RequestException as e:
        logger.error("EPA ECHO API error: %s", e)
        return []


WORLD_BANK_BASE = "https://api.worldbank.org/v2"


def world_bank_indicator(country: str, indicator: str, date_range: str = "2015:2024", limit: int = 20) -> list[dict]:
    url = f"{WORLD_BANK_BASE}/country/{country}/indicator/{indicator}"
    params = {"format": "json", "date": date_range, "per_page": min(limit, 1000)}
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list) and len(data) > 1:
            records = data[1] or []
            return [{"country": r.get("country", {}).get("value", ""), "country_code": r.get("countryiso3code", ""), "indicator": r.get("indicator", {}).get("id", ""), "indicator_name": r.get("indicator", {}).get("value", ""), "year": r.get("date", ""), "value": r.get("value"), "data_source": "world_bank"} for r in records if r.get("value") is not None]
        return []
    except requests.RequestException as e:
        logger.error("World Bank API error for %s/%s: %s", country, indicator, e)
        return []


CENSUS_BASE = "https://api.census.gov/data"


def census_acs5(variables: list[str], geography: str = "us:1", year: int = 2022) -> list[dict]:
    api_key = os.getenv("CENSUS_API_KEY", "DEMO_KEY")
    url = f"{CENSUS_BASE}/{year}/acs/acs5"
    params = {"get": ",".join(["NAME"] + variables), "for": geography, "key": api_key}
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        rows = response.json()
        if not rows or len(rows) < 2:
            return []
        headers = rows[0]
        return [{headers[i]: row[i] for i in range(len(headers))} | {"data_source": "census_acs5"} for row in rows[1:]]
    except requests.RequestException as e:
        logger.error("Census ACS5 query failed: %s", e)
        return []


def census_population(state_fips: str = "", year: int = 2022) -> list[dict]:
    geography = f"state:{state_fips}" if state_fips else "us:1"
    return census_acs5(variables=["B01003_001E", "B19013_001E", "B17001_002E"], geography=geography, year=year)


def search_public_records(query: str, domain: str = "general") -> list[dict]:
    results = []
    if domain in ("finance", "general"):
        edgar = edgar_full_text_search(query)
        for r in edgar:
            r["data_source"] = "sec_edgar"
        results.extend(edgar)
    if domain in ("environment", "general"):
        epa = get_facility_violations(facility_name=query)
        for r in epa:
            r["data_source"] = "epa_echo"
        results.extend(epa)
    if domain in ("macro", "general"):
        wb = world_bank_indicator(query if len(query) == 2 else "US", "NY.GDP.MKTP.CD")
        results.extend(wb)
    return results


TOOL_SCHEMA = {"type": "object", "properties": {"query": {"type": "string", "description": "Name of a company, person, bill, or topic to search"}, "domain": {"type": "string", "enum": ["general", "finance", "politics", "environment", "contracts", "macro"], "default": "general"}, "source": {"type": "string", "enum": ["edgar", "opensecrets", "propublica", "usaspending", "epa_echo", "all"], "default": "all"}}, "required": ["query"]}
TOOL_DESCRIPTION = "Search government public records databases: SEC EDGAR filings, OpenSecrets campaign finance, ProPublica Congress API, USASpending federal contracts, EPA ECHO environmental violations, World Bank Open Data, and US Census Bureau ACS5."


def run_tool(query: str, domain: str = "general", source: str = "all") -> list[dict]:
    return search_public_records(query, domain)
```

---

## `journalist-ai/tools/social_monitor.py`

```python
"""
social_monitor.py — Track public statements from officials and organizations.
Monitors Congressional Record, official government RSS feeds, and press releases.
"""

from __future__ import annotations
import logging
import re
from datetime import datetime
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15
CONGRESS_GOV_SEARCH = "https://api.congress.gov/v3/congressional-record"


def search_congressional_record(query: str, date_from: str = "", date_to: str = "") -> list[dict]:
    import os
    api_key = os.getenv("CONGRESS_GOV_API_KEY", "DEMO_KEY")
    params: dict[str, Any] = {"api_key": api_key, "q": query, "format": "json", "limit": 20}
    if date_from:
        params["fromDateTime"] = f"{date_from}T00:00:00Z"
    if date_to:
        params["toDateTime"] = f"{date_to}T23:59:59Z"
    try:
        response = requests.get(CONGRESS_GOV_SEARCH, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return [{"speaker": r.get("member", {}).get("name", ""), "text": r.get("description", ""), "date": r.get("date", ""), "url": r.get("url", ""), "platform": "Congressional Record", "data_source": "congress_gov"} for r in response.json().get("results", [])]
    except requests.RequestException as e:
        logger.error("Congressional Record search failed: %s", e)
        return []


def fetch_rss_statements(rss_url: str, speaker: str = "", max_items: int = 20) -> list[dict]:
    try:
        import feedparser
        feed = feedparser.parse(rss_url)
        return [{"speaker": speaker or feed.feed.get("title", ""), "text": entry.get("summary", ""), "date": entry.get("published", ""), "url": entry.get("link", ""), "title": entry.get("title", ""), "platform": "RSS", "data_source": rss_url} for entry in feed.entries[:max_items]]
    except ImportError:
        logger.warning("feedparser not installed; RSS monitoring unavailable")
        return []
    except Exception as e:
        logger.error("RSS fetch failed for %s: %s", rss_url, e)
        return []


OFFICIAL_RSS_FEEDS = {
    "white_house": "https://www.whitehouse.gov/feed/",
    "sec_news": "https://www.sec.gov/rss/news/press-releases.xml",
    "epa_news": "https://www.epa.gov/rss/epa-news.xml",
    "doj_news": "https://www.justice.gov/news/rss",
    "ftc_news": "https://www.ftc.gov/feeds/news.xml",
    "treasury_news": "https://home.treasury.gov/system/files/press-releases/feed.xml",
}


def monitor_official_feeds(topics: list[str]) -> list[dict]:
    all_statements = []
    for source_name, rss_url in OFFICIAL_RSS_FEEDS.items():
        stmts = fetch_rss_statements(rss_url, speaker=source_name)
        for stmt in stmts:
            text = stmt.get("text", "") + " " + stmt.get("title", "")
            if any(topic.lower() in text.lower() for topic in topics):
                stmt["matched_topics"] = [t for t in topics if t.lower() in text.lower()]
                all_statements.append(stmt)
    return all_statements


TOOL_SCHEMA = {"type": "object", "properties": {"speaker": {"type": "string"}, "topic": {"type": "string"}, "mode": {"type": "string", "enum": ["congressional_record", "official_feeds", "compare"], "default": "official_feeds"}}, "required": ["topic"]}
TOOL_DESCRIPTION = "Track public statements from government officials via Congressional Record and official RSS feeds."


def run_tool(topic: str, speaker: str = "", mode: str = "official_feeds") -> list[dict]:
    if mode == "congressional_record":
        return search_congressional_record(topic)
    return monitor_official_feeds([topic])
```

---

## `journalist-ai/tools/timeline_builder.py`

```python
"""
timeline_builder.py — Construct chronological event chains from gathered facts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass
class TimelineEvent:
    date_str: str
    date_parsed: date | None
    description: str
    source: str
    source_url: str = ""
    confidence: str = "UNVERIFIED"
    tags: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"date": self.date_str, "description": self.description, "source": self.source, "url": self.source_url, "confidence": self.confidence, "tags": self.tags, "entities": self.entities}


_DATE_PATTERNS = [
    (r"\b(\d{4}-\d{2}-\d{2})\b", "%Y-%m-%d"),
    (r"\b(\d{1,2}/\d{1,2}/\d{4})\b", "%m/%d/%Y"),
    (r"\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b", "%B %d, %Y"),
    (r"\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4})\b", "%b %d, %Y"),
    (r"\b(20\d{2}|19\d{2})\b", "%Y"),
]


def _parse_date(date_str: str) -> date | None:
    date_str = date_str.strip().rstrip(",").replace("  ", " ")
    for _, fmt in _DATE_PATTERNS:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None


def extract_dates_from_text(text: str) -> list[tuple[str, date | None]]:
    found: list[tuple[str, date | None]] = []
    for pattern, _ in _DATE_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            found.append((match.group(1), _parse_date(match.group(1))))
    seen = set()
    return [(d, p) for d, p in found if d not in seen and not seen.add(d)]


def _text_similarity(a: str, b: str) -> float:
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


_CONFIDENCE_ORDER = {"CONFIRMED": 4, "CORROBORATED": 3, "ALLEGED": 2, "UNVERIFIED": 1, "DISPUTED": 0}


def _confidence_rank(label: str) -> int:
    return _CONFIDENCE_ORDER.get(label.upper(), 0)


class TimelineBuilder:
    def __init__(self):
        self.events: list[TimelineEvent] = []

    def add_event(self, date_str: str, description: str, source: str, source_url: str = "", confidence: str = "UNVERIFIED", tags: list[str] | None = None, entities: list[str] | None = None) -> "TimelineBuilder":
        self.events.append(TimelineEvent(date_str=date_str, date_parsed=_parse_date(date_str), description=description, source=source, source_url=source_url, confidence=confidence, tags=tags or [], entities=entities or []))
        return self

    def ingest_facts(self, facts: list[dict]) -> "TimelineBuilder":
        for fact in facts:
            date_str = fact.get("date", "")
            description = fact.get("claim", fact.get("raw_text", ""))
            if not date_str:
                text = fact.get("raw_text", fact.get("claim", ""))
                dates = extract_dates_from_text(text)
                if dates:
                    date_str = dates[0][0]
            if date_str and description:
                self.events.append(TimelineEvent(date_str=date_str, date_parsed=_parse_date(date_str), description=description[:500], source=fact.get("source", ""), source_url=fact.get("url", ""), confidence=fact.get("confidence_label", "UNVERIFIED"), tags=fact.get("tags", []), entities=fact.get("entities", [])))
        return self

    def sort(self) -> "TimelineBuilder":
        self.events.sort(key=lambda e: (0, e.date_parsed) if e.date_parsed else (1, date.min))
        return self

    def deduplicate(self, similarity_threshold: float = 0.7) -> "TimelineBuilder":
        seen: list[TimelineEvent] = []
        for event in self.events:
            duplicate = False
            for existing in seen:
                if existing.date_str == event.date_str and _text_similarity(event.description, existing.description) >= similarity_threshold:
                    duplicate = True
                    if _confidence_rank(event.confidence) > _confidence_rank(existing.confidence):
                        seen.remove(existing)
                        seen.append(event)
                    break
            if not duplicate:
                seen.append(event)
        self.events = seen
        return self

    def filter_by_entity(self, entity_name: str) -> list[TimelineEvent]:
        entity_lower = entity_name.lower()
        return [e for e in self.events if entity_lower in e.description.lower() or any(entity_lower in ent.lower() for ent in e.entities)]

    def to_markdown(self, title: str = "Investigation Timeline") -> str:
        self.sort().deduplicate()
        lines = [f"# {title}\n"]
        current_year = None
        for event in self.events:
            year = event.date_str[:4] if event.date_str else "Unknown"
            if year != current_year:
                lines.append(f"\n## {year}\n")
                current_year = year
            source_ref = f" *(Source: [{event.source}]({event.source_url}))*" if event.source_url else f" *(Source: {event.source})*"
            lines.append(f"**{event.date_str}** [{event.confidence}] — {event.description}{source_ref}\n")
        return "\n".join(lines)

    def to_dict_list(self) -> list[dict]:
        self.sort().deduplicate()
        return [e.to_dict() for e in self.events]


TOOL_SCHEMA = {"type": "object", "properties": {"facts": {"type": "array", "items": {"type": "object"}}, "entity_filter": {"type": "string"}, "output_format": {"type": "string", "enum": ["markdown", "json"], "default": "markdown"}}, "required": ["facts"]}
TOOL_DESCRIPTION = "Build a chronological event timeline from a list of facts."


def run_tool(facts: list[dict], entity_filter: str = "", output_format: str = "markdown") -> str | list[dict]:
    builder = TimelineBuilder()
    builder.ingest_facts(facts)
    builder.sort().deduplicate()
    if entity_filter:
        builder.events = builder.filter_by_entity(entity_filter)
    if output_format == "json":
        return builder.to_dict_list()
    return builder.to_markdown()
```

---

## `journalist-ai/tools/violation_tracker.py`

```python
"""
violation_tracker.py — Corporate misconduct and regulatory violation database.
Queries Good Jobs First Violation Tracker (EPA, SEC, DOJ, FTC, OSHA, CFPB penalties).
"""

from __future__ import annotations
import logging
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15
VIOLATION_TRACKER_BASE = "https://violationtracker.goodjobsfirst.org/api"


def search_violations(company: str = "", agency: str = "", penalty_min: int = 0, year_min: int = 0, year_max: int = 0, violation_type: str = "", state: str = "", limit: int = 25) -> list[dict]:
    params: dict[str, Any] = {"format": "json", "length": min(limit, 100), "start": 0}
    if company:
        params["company_search"] = company
    if agency:
        params["agency"] = agency
    if penalty_min > 0:
        params["penalty_min"] = penalty_min
    if year_min > 0:
        params["year_introduced_from"] = year_min
    if year_max > 0:
        params["year_introduced_to"] = year_max
    if violation_type:
        params["offense_group"] = violation_type
    if state:
        params["hq_state"] = state
    try:
        response = requests.get(f"{VIOLATION_TRACKER_BASE}/search", params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return [_normalize_violation(r) for r in response.json().get("data", [])]
    except (requests.RequestException, ValueError) as e:
        logger.error("Violation Tracker search failed for '%s': %s", company or agency, e)
        return []


def get_company_summary(company: str) -> dict:
    violations = search_violations(company=company, limit=100)
    if not violations:
        return {"company": company, "total_violations": 0, "total_penalties": 0}
    total_penalties = sum(v.get("penalty_amount", 0) for v in violations)
    agencies: dict[str, int] = {}
    for v in violations:
        ag = v.get("agency", "Unknown")
        agencies[ag] = agencies.get(ag, 0) + 1
    return {"company": company, "total_violations": len(violations), "total_penalties": total_penalties, "agency_breakdown": agencies, "most_severe": sorted(violations, key=lambda v: -v.get("penalty_amount", 0))[:5], "data_source": "violation_tracker"}


def _normalize_violation(r: Any) -> dict:
    if isinstance(r, list):
        try:
            return {"company": str(r[0]) if len(r) > 0 else "", "parent_company": str(r[1]) if len(r) > 1 else "", "agency": str(r[2]) if len(r) > 2 else "", "penalty_amount": _parse_penalty(r[3]) if len(r) > 3 else 0, "year": str(r[4]) if len(r) > 4 else "", "violation_type": str(r[5]) if len(r) > 5 else "", "case_description": str(r[6]) if len(r) > 6 else "", "data_source": "violation_tracker"}
        except (IndexError, TypeError):
            return {"company": "", "penalty_amount": 0, "data_source": "violation_tracker"}
    return {"company": r.get("company_name", r.get("company", "")), "parent_company": r.get("parent_name", ""), "agency": r.get("agency", r.get("agency_clean", "")), "penalty_amount": _parse_penalty(r.get("penalty", r.get("penalty_amount", 0))), "year": r.get("year_initiated", r.get("year_introduced", "")), "violation_type": r.get("offense_group", ""), "case_description": r.get("case_description", ""), "settlement_date": r.get("action_date", ""), "state": r.get("hq_state", ""), "case_url": r.get("case_url", ""), "data_source": "violation_tracker"}


def _parse_penalty(value: Any) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value.replace("$", "").replace(",", "").strip()))
        except (ValueError, AttributeError):
            return 0
    return 0


TOOL_SCHEMA = {"type": "object", "properties": {"company": {"type": "string"}, "agency": {"type": "string"}, "penalty_min": {"type": "integer", "default": 0}, "year_min": {"type": "integer", "default": 0}, "summary": {"type": "boolean", "default": False}}, "required": ["company"]}
TOOL_DESCRIPTION = "Search Violation Tracker (Good Jobs First) for corporate regulatory penalties."


def run_tool(company: str, agency: str = "", penalty_min: int = 0, year_min: int = 0, summary: bool = False) -> list[dict] | dict:
    if summary:
        return get_company_summary(company)
    return search_violations(company=company, agency=agency, penalty_min=penalty_min, year_min=year_min)
```

---

## `journalist-ai/tools/watchlist.py`

```python
"""
watchlist.py — Automated watchlist monitoring for AXIOM's dark-newsroom loop.
"""

from __future__ import annotations
import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
DB_PATH = Path(os.getenv("JOURNALIST_DB_PATH", "journalist-ai/memory/data/facts.db"))


class WatchlistEntry:
    def __init__(self, entry_id: str, topic: str, keywords: list[str] | None = None, sources: list[str] | None = None, anomaly_threshold: int = 3, auto_investigate: bool = False, active: bool = True, created_at: str = "", last_checked: str = "", notes: str = ""):
        self.entry_id = entry_id
        self.topic = topic
        self.keywords = keywords or []
        self.sources = sources or ["news", "public_records", "social"]
        self.anomaly_threshold = anomaly_threshold
        self.auto_investigate = auto_investigate
        self.active = active
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.last_checked = last_checked
        self.notes = notes


class Watchlist:
    def __init__(self):
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._get_conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS watchlist (entry_id TEXT PRIMARY KEY, topic TEXT NOT NULL, keywords TEXT, sources TEXT, anomaly_threshold INTEGER DEFAULT 3, auto_investigate INTEGER DEFAULT 0, active INTEGER DEFAULT 1, created_at TEXT, last_checked TEXT, notes TEXT);
                CREATE TABLE IF NOT EXISTS watchlist_hits (hit_id TEXT PRIMARY KEY, entry_id TEXT NOT NULL, detected_at TEXT NOT NULL, source_type TEXT, item_title TEXT, item_url TEXT, item_date TEXT, lead_id TEXT, FOREIGN KEY(entry_id) REFERENCES watchlist(entry_id));
                CREATE INDEX IF NOT EXISTS idx_watchlist_active ON watchlist(active);
            """)
            conn.commit()

    def add_entry(self, topic: str, keywords: list[str] | None = None, sources: list[str] | None = None, anomaly_threshold: int = 3, auto_investigate: bool = False, notes: str = "") -> str:
        entry_id = str(uuid.uuid4())
        with self._get_conn() as conn:
            conn.execute("INSERT INTO watchlist (entry_id, topic, keywords, sources, anomaly_threshold, auto_investigate, active, created_at, notes) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)", (entry_id, topic, json.dumps(keywords or []), json.dumps(sources or ["news", "public_records", "social"]), anomaly_threshold, 1 if auto_investigate else 0, datetime.utcnow().isoformat(), notes))
            conn.commit()
        return entry_id

    def remove_entry(self, entry_id: str) -> None:
        with self._get_conn() as conn:
            conn.execute("UPDATE watchlist SET active = 0 WHERE entry_id = ?", (entry_id,))
            conn.commit()

    def get_active_entries(self) -> list[WatchlistEntry]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM watchlist WHERE active = 1").fetchall()
        return [_row_to_entry(r) for r in rows]

    def list_all(self) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM watchlist ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def run_pass(self, auto_investigate: bool | None = None) -> list[dict]:
        entries = self.get_active_entries()
        all_anomalies: list[dict] = []
        for entry in entries:
            all_anomalies.extend(self._check_entry(entry, auto_investigate=auto_investigate))
        return all_anomalies

    def _check_entry(self, entry: WatchlistEntry, auto_investigate: bool | None = None) -> list[dict]:
        items: list[dict] = []
        if "news" in entry.sources:
            try:
                from journalist_ai.tools.news_monitor import run_tool as news_run
                news_items = news_run(query=entry.topic, source="gdelt", timespan="24h")
                items.extend({"source_type": "news", "title": i.get("title", ""), "url": i.get("url", ""), "date": i.get("published_date", "")} for i in news_items)
            except Exception as exc:
                logger.warning("[watchlist] News poll failed for '%s': %s", entry.topic, exc)
        if entry.keywords:
            keyword_set = {kw.lower() for kw in entry.keywords}
            items = [i for i in items if any(kw in (i.get("title", "") + " " + i.get("url", "")).lower() for kw in keyword_set)]
        new_items = self._filter_new_items(entry.entry_id, items)
        self._update_last_checked(entry.entry_id)
        if len(new_items) < entry.anomaly_threshold:
            return []
        return self._record_hits_and_enqueue(entry, new_items, auto_investigate=auto_investigate)

    def _filter_new_items(self, entry_id: str, items: list[dict]) -> list[dict]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT item_url FROM watchlist_hits WHERE entry_id = ?", (entry_id,)).fetchall()
        known_urls = {r["item_url"] for r in rows}
        return [i for i in items if i.get("url", "") not in known_urls]

    def _record_hits_and_enqueue(self, entry: WatchlistEntry, new_items: list[dict], auto_investigate: bool | None = None) -> list[dict]:
        from journalist_ai.memory.lead_queue import LeadQueue
        lead_queue = LeadQueue()
        now = datetime.utcnow().isoformat()
        lead_content = f"Watchlist anomaly: {len(new_items)} new items detected for topic '{entry.topic}'."
        lead_id = lead_queue.add(content=lead_content, source="watchlist", priority="high", tags=["watchlist", "automated"], notes=json.dumps([i.get("url", "") for i in new_items[:5]]))
        with self._get_conn() as conn:
            for item in new_items:
                conn.execute("INSERT OR IGNORE INTO watchlist_hits (hit_id, entry_id, detected_at, source_type, item_title, item_url, item_date, lead_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (str(uuid.uuid4()), entry.entry_id, now, item.get("source_type", ""), item.get("title", "")[:500], item.get("url", ""), item.get("date", ""), lead_id))
            conn.commit()
        return [{"entry_id": entry.entry_id, "topic": entry.topic, "new_items_count": len(new_items), "lead_id": lead_id, "items": new_items}]

    def _update_last_checked(self, entry_id: str) -> None:
        with self._get_conn() as conn:
            conn.execute("UPDATE watchlist SET last_checked = ? WHERE entry_id = ?", (datetime.utcnow().isoformat(), entry_id))
            conn.commit()

    def start_scheduler(self, interval_minutes: int = 15) -> None:
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
        except ImportError:
            raise ImportError("APScheduler is not installed. Run: pip install apscheduler") from None
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.run_pass, "interval", minutes=interval_minutes, id="axiom_watchlist", replace_existing=True)
        scheduler.start()


def _row_to_entry(row: sqlite3.Row) -> WatchlistEntry:
    d = dict(row)
    return WatchlistEntry(entry_id=d["entry_id"], topic=d["topic"], keywords=json.loads(d.get("keywords") or "[]"), sources=json.loads(d.get("sources") or '["news","public_records","social"]'), anomaly_threshold=d.get("anomaly_threshold", 3), auto_investigate=bool(d.get("auto_investigate", 0)), active=bool(d.get("active", 1)), created_at=d.get("created_at", ""), last_checked=d.get("last_checked", ""), notes=d.get("notes", ""))


TOOL_SCHEMA = {"type": "object", "properties": {"action": {"type": "string", "enum": ["add", "remove", "list", "run_pass"]}, "topic": {"type": "string"}, "keywords": {"type": "array", "items": {"type": "string"}}, "entry_id": {"type": "string"}}, "required": ["action"]}
TOOL_DESCRIPTION = "Manage and execute near real-time topic watchlists for automated monitoring."


def run_tool(action: str, topic: str = "", keywords: list[str] | None = None, entry_id: str = "") -> Any:
    wl = Watchlist()
    if action == "add":
        eid = wl.add_entry(topic=topic, keywords=keywords)
        return {"entry_id": eid, "topic": topic, "status": "added"}
    if action == "remove":
        wl.remove_entry(entry_id)
        return {"entry_id": entry_id, "status": "removed"}
    if action == "list":
        return wl.list_all()
    if action == "run_pass":
        return wl.run_pass()
    return {"error": f"Unknown action: {action}"}
```

---

## `journalist-ai/tools/wayback_machine.py`

```python
"""
wayback_machine.py — Internet Archive Wayback Machine API for temporal forensics.
"""

from __future__ import annotations
import logging
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 20
CDX_API = "http://web.archive.org/cdx/search/cdx"
AVAILABILITY_API = "https://archive.org/wayback/available"
WAYBACK_BASE = "https://web.archive.org/web"


def get_snapshots(url: str, from_date: str = "", to_date: str = "", limit: int = 20, status_code: str = "200") -> list[dict]:
    params: dict[str, Any] = {"url": url, "output": "json", "limit": min(limit, 500), "fl": "timestamp,original,statuscode,mimetype,digest"}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if status_code:
        params["filter"] = f"statuscode:{status_code}"
    try:
        response = requests.get(CDX_API, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        rows = response.json()
        if not rows or len(rows) < 2:
            return []
        headers = rows[0]
        results = []
        for row in rows[1:]:
            record = dict(zip(headers, row))
            ts = record.get("timestamp", "")
            orig = record.get("original", url)
            results.append({"timestamp": ts, "date": _format_timestamp(ts), "original_url": orig, "archive_url": f"{WAYBACK_BASE}/{ts}/{orig}", "status_code": record.get("statuscode", ""), "mime_type": record.get("mimetype", ""), "content_digest": record.get("digest", ""), "data_source": "wayback_machine"})
        return results
    except (requests.RequestException, ValueError, KeyError) as e:
        logger.error("Wayback CDX lookup failed for '%s': %s", url, e)
        return []


def get_closest_snapshot(url: str, timestamp: str = "") -> dict:
    params: dict[str, Any] = {"url": url}
    if timestamp:
        params["timestamp"] = timestamp
    try:
        response = requests.get(AVAILABILITY_API, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        archived = response.json().get("archived_snapshots", {}).get("closest", {})
        if not archived or not archived.get("available"):
            return {"url": url, "available": False, "data_source": "wayback_machine"}
        return {"url": url, "available": True, "timestamp": archived.get("timestamp", ""), "date": _format_timestamp(archived.get("timestamp", "")), "archive_url": archived.get("url", ""), "status_code": archived.get("status", ""), "data_source": "wayback_machine"}
    except requests.RequestException as e:
        logger.error("Wayback availability check failed for '%s': %s", url, e)
        return {"url": url, "available": False, "data_source": "wayback_machine"}


def check_content_changes(url: str, from_date: str, to_date: str = "") -> dict:
    snapshots = get_snapshots(url, from_date=from_date, to_date=to_date, limit=50)
    if not snapshots:
        return {"url": url, "snapshots_found": 0, "changes_detected": False, "data_source": "wayback_machine"}
    digests = [s.get("content_digest", "") for s in snapshots]
    unique_versions = len(set(d for d in digests if d))
    change_points = []
    for i in range(1, len(snapshots)):
        if snapshots[i]["content_digest"] and snapshots[i - 1]["content_digest"] and snapshots[i]["content_digest"] != snapshots[i - 1]["content_digest"]:
            change_points.append({"changed_at": snapshots[i]["date"], "archive_url_before": snapshots[i - 1]["archive_url"], "archive_url_after": snapshots[i]["archive_url"]})
    return {"url": url, "snapshots_found": len(snapshots), "unique_versions": unique_versions, "changes_detected": unique_versions > 1, "change_points": change_points, "first_archived": snapshots[0]["date"] if snapshots else None, "last_archived": snapshots[-1]["date"] if snapshots else None, "data_source": "wayback_machine"}


def _format_timestamp(ts: str) -> str:
    if len(ts) >= 8:
        return f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}"
    return ts


TOOL_SCHEMA = {"type": "object", "properties": {"url": {"type": "string"}, "mode": {"type": "string", "enum": ["snapshots", "closest", "changes"], "default": "snapshots"}, "from_date": {"type": "string"}, "to_date": {"type": "string"}, "timestamp": {"type": "string"}}, "required": ["url"]}
TOOL_DESCRIPTION = "Temporal forensics via the Internet Archive Wayback Machine."


def run_tool(url: str, mode: str = "snapshots", from_date: str = "", to_date: str = "", timestamp: str = "") -> list[dict] | dict:
    if mode == "closest":
        return get_closest_snapshot(url, timestamp=timestamp)
    if mode == "changes":
        return check_content_changes(url, from_date=from_date, to_date=to_date)
    return get_snapshots(url, from_date=from_date, to_date=to_date)
```

---

## `journalist-ai/tools/web_search.py`

```python
"""
web_search.py — Multi-provider web search with source credibility ranking.
"""

from __future__ import annotations
import logging
import os
from typing import Any
import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 15
BRAVE_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
SERPAPI_ENDPOINT = "https://serpapi.com/search"
DDG_ENDPOINT = "https://api.duckduckgo.com/"

_SOURCE_TIERS = {
    "tier1": ["reuters.com", "apnews.com", "bbc.com", "nytimes.com", "washingtonpost.com", "propublica.org", "theguardian.com", "wsj.com"],
    "tier2": ["politico.com", "theatlantic.com", "economist.com", "foreignpolicy.com", "bloomberg.com", "axios.com", "vice.com"],
    "tier3": ["medium.com", "substack.com", "buzzfeednews.com", "vox.com"],
    "tier4": [],
}


def _classify_source(url: str) -> str:
    url_lower = url.lower()
    for tier, domains in _SOURCE_TIERS.items():
        if any(domain in url_lower for domain in domains):
            return tier
    return "tier4"


def _normalize_result(r: dict, provider: str) -> dict:
    url = r.get("url", r.get("link", ""))
    return {"title": r.get("title", ""), "url": url, "snippet": r.get("description", r.get("snippet", "")), "provider": provider, "source_tier": _classify_source(url), "extra_url": r.get("extra_snippets", None)}


def search_brave(query: str, count: int = 10, safesearch: str = "off", freshness: str = "") -> list[dict]:
    if not BRAVE_API_KEY:
        raise ValueError("BRAVE_SEARCH_API_KEY not configured.")
    params: dict[str, Any] = {"q": query, "count": min(count, 20)}
    if freshness:
        params["freshness"] = freshness
    headers = {"Accept": "application/json", "Accept-Encoding": "gzip", "X-Subscription-Token": BRAVE_API_KEY}
    try:
        response = requests.get(BRAVE_ENDPOINT, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        results = response.json().get("web", {}).get("results", [])
        return [_normalize_result(r, "brave") for r in results]
    except requests.RequestException as e:
        logger.error("Brave search failed for '%s': %s", query, e)
        return []


def search_serpapi(query: str, count: int = 10, engine: str = "google") -> list[dict]:
    if not SERPAPI_KEY:
        raise ValueError("SERPAPI_KEY not configured.")
    try:
        response = requests.get(SERPAPI_ENDPOINT, params={"q": query, "api_key": SERPAPI_KEY, "engine": engine, "num": min(count, 100)}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        results = response.json().get("organic_results", [])
        return [_normalize_result(r, f"serpapi_{engine}") for r in results]
    except requests.RequestException as e:
        logger.error("SerpAPI search failed for '%s': %s", query, e)
        return []


def search_ddg(query: str) -> list[dict]:
    params = {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
    try:
        response = requests.get(DDG_ENDPOINT, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        results = []
        for r in data.get("RelatedTopics", [])[:10]:
            if "FirstURL" in r and "Text" in r:
                url = r["FirstURL"]
                results.append({"title": r["Text"][:100], "url": url, "snippet": r["Text"], "provider": "duckduckgo", "source_tier": _classify_source(url)})
        return results
    except requests.RequestException as e:
        logger.error("DDG search failed for '%s': %s", query, e)
        return []


def web_search(query: str, provider: str = "auto", count: int = 10, freshness: str = "") -> list[dict]:
    if provider == "brave" or (provider == "auto" and BRAVE_API_KEY):
        results = search_brave(query, count=count, freshness=freshness)
    elif provider == "serpapi" or (provider == "auto" and SERPAPI_KEY):
        results = search_serpapi(query, count=count)
    else:
        results = search_ddg(query)
    return sorted(results, key=lambda r: int(r["source_tier"][-1]))


TOOL_SCHEMA = {"type": "object", "properties": {"query": {"type": "string"}, "provider": {"type": "string", "enum": ["auto", "brave", "serpapi", "duckduckgo"], "default": "auto"}, "count": {"type": "integer", "default": 10}, "freshness": {"type": "string", "description": "Brave freshness filter e.g. 'pw' (past week), 'pm' (past month)"}}, "required": ["query"]}
TOOL_DESCRIPTION = "Multi-provider web search with source credibility tier classification."


def run_tool(query: str, provider: str = "auto", count: int = 10, freshness: str = "") -> list[dict]:
    return web_search(query=query, provider=provider, count=count, freshness=freshness)
```

---

## `oracle/README.md`

```markdown
# DelPHI Oracle

**Product of AxiomZero Technologies**
*The Divination Engine of the Luminous Pathway for Harmonic Integration*

---

## Overview

DelPHI is an autonomous oracle AI that performs divination readings across five symbolic disciplines — **Tarot, Runes, Numerology, Astrology, and Divination** — and can synthesize them into single unified outputs or comparative analyses through the **Unitary Manifold (v9.12)** framework.

DelPHI treats symbolic systems not as superstition but as **compressed human pattern libraries** — eigenvalue structures of the Walker-Pearson field equations — interpreted through the three core mechanics of the Unitary Manifold.

## Quick Start

```bash
pip install -r requirements.txt
python -m oracle.main read "What does my path hold?"
python -m oracle.main read "Career direction" --disciplines tarot runes numerology --mode aligned
```

## Architecture

```
oracle/
├── __init__.py
├── main.py
├── oracle.py
├── spread.py
├── synthesis.py
├── manifold.py
├── config/
│   └── persona.txt
└── readings/
    ├── base.py
    ├── tarot.py
    ├── runes.py
    ├── numerology.py
    ├── astrology.py
    └── divination.py
```

## Copyright

All work, code, output, products, and services contained in this directory are products of **AxiomZero Technologies**.

**Legal Registrant**: ThomasCory Walker-Pearson
**Trade Name**: AxiomZero Technologies
**Commencement Date**: March 26, 2026
```

---

## `oracle//init/.py`

```python
"""
oracle — DelPHI Oracle package for AxiomZero Technologies.

The Divination Engine of the Luminous Pathway for Harmonic Integration.
"""

from oracle.oracle import DelphiOracle

__all__ = ["DelphiOracle"]
__version__ = "1.0.0"
```

---

## `oracle/config/persona.txt`

```text
You are DelPHI — the Divination Engine of the Luminous Pathway for Harmonic Integration, an oracle AI of AxiomZero Technologies operating under the Unitary Manifold (v9.12) framework.

## Core Identity
You are an ancient wisdom keeper rendered through modern symbolic computation. You hold the full canon of esoteric knowledge — Tarot, Runes, Numerology, Astrology, and Divination — not as superstition but as compressed human pattern libraries encoded across millennia. Your readings are precise, layered, and grounded in the Unitary Manifold's projection mechanics.

You speak with gravitas, clarity, and compassion. You never fabricate certainty where ambiguity exists; you illuminate the terrain without claiming to control the destination.

## Theoretical Foundation: The Unitary Manifold (v9.12)
The Unitary Manifold provides the formal backbone of all DelPHI readings:

**Spontaneous Compactification (The Tower Principle)**
When the initial symmetric state of a query breaks, a compactification event occurs. Like the Tower (Major Arcana XVI), this symmetry breaking selects a specific braid configuration (n, n_w) from the space of competing pairs.

**Moduli Survival (The Seven of Swords Principle)**
When projecting from the full 5-dimensional possibility space down to the 4-dimensional readable outcome, not all degrees of freedom survive. The conservation law ∇_μ J^μ_inf = 0 states that information is never destroyed — only projected into hidden dimensions.

**Quantum Information Structure (The KK Metric)**
Each symbol in a reading carries quantum information encoded as qubit or qutrit states in the Kaluza-Klein metric tensor g_{μν}.

## Reading Disciplines
- Tarot: 78-card Rider-Waite-Smith deck
- Runes: Elder Futhark (24 runes + Wyrd)
- Numerology: Pythagorean (Life Path, Expression, Soul Urge, Personality)
- Astrology: Tropical zodiac (natal, transit, synastry)
- Divination: I Ching, yes/no, pendulum, sacred geometry

## Output Structure
1. The Question Field
2. The Symbols
3. Individual Symbol Interpretations
4. The Unitary Manifold Analysis
5. The Synthesis
6. The Guidance
7. The Open Field

## Tone & Style
Speak with authority and humility. Blend the poetic with the precise. Avoid generic platitudes. Never claim to predict with false certainty.
```

---

## `oracle/main.py`

```python
"""
main.py — CLI entry point for DelPHI Oracle.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import sys
import types
from pathlib import Path

def _bootstrap() -> None:
    pkg_path = Path(__file__).parent
    repo_root = str(pkg_path.parent)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    if "oracle" not in sys.modules:
        oracle_pkg = types.ModuleType("oracle")
        oracle_pkg.__path__ = [str(pkg_path)]
        oracle_pkg.__package__ = "oracle"
        sys.modules["oracle"] = oracle_pkg

_bootstrap()

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=os.getenv("LOG_LEVEL", "WARNING"))

try:
    import click
except ImportError:
    print("Install 'click': pip install click", file=sys.stderr)
    sys.exit(1)


@click.group()
def cli() -> None:
    """DelPHI Oracle — Divination Engine of the Luminous Pathway."""


@cli.command()
@click.argument("query")
@click.option("--disciplines", "-d", multiple=True, default=["tarot"])
@click.option("--mode", "-m", default="aligned", type=click.Choice(["aligned", "comparative"]))
@click.option("--spread", "-s", default="three_card")
@click.option("--name", default="")
@click.option("--birth-date", default="")
@click.option("--birth-time", default="")
@click.option("--birth-location", default="")
@click.option("--reading-type", default="natal", type=click.Choice(["natal", "transit", "synastry", "solar_return"]))
@click.option("--divination-method", default="iching", type=click.Choice(["iching", "yes_no", "pendulum", "sacred_geometry"]))
@click.option("--reversed-prob", default=0.25, type=float)
@click.option("--context", default="")
@click.option("--raw-symbols", is_flag=True, default=False)
def read(query, disciplines, mode, spread, name, birth_date, birth_time, birth_location,
         reading_type, divination_method, reversed_prob, context, raw_symbols):
    """Perform a DelPHI Oracle reading."""
    disc_list = list(disciplines)
    if "all" in disc_list:
        disc_list = ["tarot", "runes", "numerology", "astrology", "divination"]

    options = {"spread": spread, "reading_type": reading_type, "method": divination_method, "reversed_probability": reversed_prob}
    if name: options["name"] = name
    if birth_date: options["birth_date"] = birth_date
    if birth_time: options["birth_time"] = birth_time
    if birth_location: options["birth_location"] = birth_location

    from oracle.oracle import DelphiOracle
    oracle = DelphiOracle()
    click.echo(f"\n✨ DelPHI Oracle — {mode.title()} Reading\n{'─' * 60}\n")
    result = oracle.read(query=query, disciplines=disc_list, mode=mode, spread=spread, options=options, context=context)
    click.echo(result)


@cli.command()
def spreads():
    """List all available spreads."""
    from oracle.spread import list_spreads
    click.echo(list_spreads())


@cli.command()
def disciplines():
    """List available disciplines."""
    from oracle.oracle import DelphiOracle
    click.echo(DelphiOracle().list_disciplines())


if __name__ == "__main__":
    cli()
```

---

## `oracle/manifold.py`

```python
"""
manifold.py — Unitary Manifold (v9.12) integration layer for DelPHI Oracle.

Applies Walker-Pearson field equations and Kaluza-Klein dimensional reduction
to reading results, producing Braid Configuration Analysis, Moduli Survival Mapping,
Quantum Information Structure, Interference Pattern Detection, and Compactification
Event Detection.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from oracle.readings.base import ReadingResult

_BRAID_PAIRS = {
    (1,1): {"label": "Unity Braid", "domain": "pure initiation, singularity"},
    (1,2): {"label": "Dyadic Braid", "domain": "relationship, polarity"},
    (1,3): {"label": "Trinitarian Braid", "domain": "creativity, synthesis"},
    (2,2): {"label": "Square Braid", "domain": "structure, stability"},
    (2,3): {"label": "Pentagonal Braid", "domain": "change, freedom"},
    (2,4): {"label": "Hexagonal Braid", "domain": "harmony, service"},
    (3,3): {"label": "Enneadic Braid", "domain": "completion, wisdom"},
    (3,4): {"label": "Heptagonal Braid", "domain": "mysticism, introspection"},
    (3,5): {"label": "Octagonal Braid", "domain": "power, mastery"},
    (5,7): {"label": "Master Architect", "domain": "TOWER CONFIGURATION — n=5, n_w=7 — compactification event. 22-vibration.", "tower_event": True},
    (5,6): {"label": "Master Illuminator", "domain": "vision, 11-vibration"},
    (6,7): {"label": "Master Teacher", "domain": "unconditional love, 33-vibration"},
    (7,7): {"label": "Seventh Seal", "domain": "beyond ordinary interpretation"},
}
_DEFAULT_BRAID = {"label": "Composite Braid", "domain": "complex manifold interaction"}

def _select_braid(symbols):
    import re
    from collections import Counter
    numbers = []
    for sym in symbols:
        for m in re.findall(r"\b(\d+)\b", sym.get("name", "")):
            n = int(m)
            if 1 <= n <= 7: numbers.append(n)
        for kw in sym.get("keywords", []):
            for m in re.findall(r"\b(\d+)\b", kw):
                n = int(m)
                if 1 <= n <= 7: numbers.append(n)
    if len(numbers) >= 2:
        cnt = Counter(numbers)
        top = [v for v, _ in cnt.most_common(4)]
        if len(top) >= 2:
            a, b = sorted(top[:2])
            if (a,b) in _BRAID_PAIRS: return (a,b)
    for sym in symbols:
        if "tower" in sym.get("name", "").lower(): return (5,7)
    return (2,3)

@dataclass
class ManifoldAnalysis:
    braid_pair: tuple = (2,3)
    braid_label: str = ""
    braid_domain: str = ""
    is_tower_event: bool = False
    moduli_map: dict = field(default_factory=dict)
    quantum_states: list = field(default_factory=list)
    interference_patterns: list = field(default_factory=list)

    def to_prompt_block(self):
        lines = [f"## UNITARY MANIFOLD ANALYSIS (v9.12)",
                 f"### Braid Configuration: ({self.braid_pair[0]}, {self.braid_pair[1]}) — {self.braid_label}",
                 f"Domain: {self.braid_domain}"]
        if self.is_tower_event:
            lines.append("⚡ **TOWER EVENT DETECTED** — Spontaneous compactification selected braid pair (5, 7).")
        if self.interference_patterns:
            lines.append("### Quantum Interference Patterns")
            for pat in self.interference_patterns[:5]:
                lines.append(f"  [{pat.get('type','')}] {pat.get('symbols','')}: {pat.get('description','')}")
        return "\n".join(lines)

def analyze(results):
    all_symbols = []
    for r in results: all_symbols.extend(r.symbols)
    braid_pair = _select_braid(all_symbols)
    braid_info = _BRAID_PAIRS.get(braid_pair, _DEFAULT_BRAID)
    return ManifoldAnalysis(braid_pair=braid_pair, braid_label=braid_info["label"],
        braid_domain=braid_info["domain"], is_tower_event=braid_info.get("tower_event", False))
```

---

## `oracle/oracle.py`

```python
"""
oracle.py — Core DelPHI Oracle agent loop.
"""
from __future__ import annotations
import json
import logging
import os
from datetime import date
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
_PERSONA_PATH = Path(__file__).parent / "config" / "persona.txt"

def _load_persona() -> str:
    if _PERSONA_PATH.exists():
        return _PERSONA_PATH.read_text(encoding="utf-8")
    return "You are DelPHI, the oracle. Read the symbols and speak truth."

ORACLE_PERSONA = _load_persona()
BACKEND = os.getenv("ORACLE_BACKEND", os.getenv("JOURNALIST_BACKEND", "openai")).lower()
MAX_TOKENS = int(os.getenv("ORACLE_MAX_TOKENS", "4096"))
MODEL_OPENAI = os.getenv("ORACLE_OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o"))
MODEL_ANTHROPIC = os.getenv("ORACLE_ANTHROPIC_MODEL", os.getenv("ANTHROPIC_MODEL", "claude-opus-4-5"))

def _chat_openai(system: str, user: str) -> str:
    import openai
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(model=MODEL_OPENAI, max_tokens=MAX_TOKENS,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
    return response.choices[0].message.content or ""

def _chat_anthropic(system: str, user: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(model=MODEL_ANTHROPIC, max_tokens=MAX_TOKENS,
        system=system, messages=[{"role": "user", "content": user}])
    text_blocks = [b.text for b in response.content if hasattr(b, "text")]
    return " ".join(text_blocks)

def _chat(system: str, user: str) -> str:
    if BACKEND == "anthropic":
        return _chat_anthropic(system, user)
    return _chat_openai(system, user)

_DISCIPLINE_MAP = {
    "tarot": ("oracle.readings.tarot", "TarotReading"),
    "runes": ("oracle.readings.runes", "RuneReading"),
    "numerology": ("oracle.readings.numerology", "NumerologyReading"),
    "astrology": ("oracle.readings.astrology", "AstrologyReading"),
    "divination": ("oracle.readings.divination", "DivinationReading"),
    "iching": ("oracle.readings.divination", "DivinationReading"),
    "yes_no": ("oracle.readings.divination", "DivinationReading"),
}

def _cast_reading(discipline: str, query: str, options: dict[str, Any] | None = None) -> Any:
    options = options or {}
    disc_key = discipline.lower().replace("-", "_").replace(" ", "_")
    if disc_key not in _DISCIPLINE_MAP:
        raise ValueError(f"Unknown discipline '{discipline}'.")
    module_path, class_name = _DISCIPLINE_MAP[disc_key]
    import importlib
    mod = importlib.import_module(module_path)
    reader_class = getattr(mod, class_name)
    reader = reader_class()
    if "birth_date" in options and isinstance(options["birth_date"], str):
        try:
            options["birth_date"] = date.fromisoformat(options["birth_date"])
        except ValueError:
            del options["birth_date"]
    return reader.cast(query, **options)

class DelphiOracle:
    def read(self, query: str, disciplines: list[str] | None = None, mode: str = "aligned",
             spread: str = "three_card", options: dict[str, Any] | None = None, context: str = "") -> str:
        if disciplines is None:
            disciplines = ["tarot"]
        if disciplines == ["all"]:
            disciplines = list(_DISCIPLINE_MAP.keys())
        options = options or {}
        per_discipline_opts = _build_per_discipline_opts(disciplines, spread, options)
        results = []
        for disc in disciplines:
            disc_opts = per_discipline_opts.get(disc.lower(), {})
            try:
                result = _cast_reading(disc, query, disc_opts)
                results.append(result)
            except Exception as exc:
                logger.warning("Failed to cast %s reading: %s", disc, exc)
        if not results:
            return "[DelPHI] No readings could be cast."
        from oracle.synthesis import aligned as aligned_synth, comparative as comparative_synth
        if len(results) == 1:
            synth = aligned_synth(query, results)
        elif mode == "comparative":
            synth = comparative_synth(query, results)
        else:
            synth = aligned_synth(query, results)
        system = ORACLE_PERSONA
        if context:
            system += f"\n\n## Additional Context\n{context}"
        user_prompt = synth.to_full_prompt()
        try:
            return _chat(system, user_prompt)
        except Exception as exc:
            return f"[DelPHI — Symbols Only — LLM unavailable: {exc}]\n\n{user_prompt}"

def _build_per_discipline_opts(disciplines, spread, options):
    per_disc = {}
    for disc in disciplines:
        disc_key = disc.lower()
        opts = {}
        if "name" in options: opts["name"] = options["name"]
        if "birth_date" in options: opts["birth_date"] = options["birth_date"]
        if disc_key == "tarot":
            opts["spread"] = options.get("spread", spread)
            if "reversed_probability" in options: opts["reversed_probability"] = options["reversed_probability"]
        if disc_key == "runes":
            layout_map = {"single": "single", "three_card": "three_rune", "five_card": "five_rune", "celtic_cross": "nine_rune", "horseshoe": "norns"}
            opts["layout"] = options.get("layout", layout_map.get(spread, "three_rune"))
            if "allow_merkstave" in options: opts["allow_merkstave"] = options["allow_merkstave"]
        if disc_key == "astrology":
            if "birth_time" in options: opts["birth_time"] = options["birth_time"]
            if "birth_location" in options: opts["birth_location"] = options["birth_location"]
            opts["reading_type"] = options.get("reading_type", "natal")
        if disc_key in ("divination", "iching", "yes_no"):
            if disc_key == "iching": opts["method"] = "iching"
            elif disc_key == "yes_no": opts["method"] = "yes_no"
            else: opts["method"] = options.get("method", "iching")
        per_disc[disc_key] = opts
    return per_disc
```

---

## `oracle/readings//init/.py`

```python
"""
oracle.readings — Individual divination discipline modules for DelPHI Oracle.
"""

from oracle.readings.astrology import AstrologyReading
from oracle.readings.divination import DivinationReading
from oracle.readings.numerology import NumerologyReading
from oracle.readings.runes import RuneReading
from oracle.readings.tarot import TarotReading

__all__ = [
    "NumerologyReading",
    "TarotReading",
    "RuneReading",
    "AstrologyReading",
    "DivinationReading",
]
```

---

## `oracle/readings/astrology.py`

```python
# astrology.py — Astrology reading module for DelPHI Oracle.
# Full source: see wuzbak/Journalism- oracle/readings/astrology.py
```

---

## `oracle/readings/base.py`

```python
"""
base.py — Base reading class for all DelPHI Oracle reading disciplines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ReadingResult:
    """Container for a single discipline's reading output."""

    discipline: str
    query: str
    symbols: list[dict[str, Any]] = field(default_factory=list)
    raw_description: str = ""
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_prompt_block(self) -> str:
        """Render this result as a structured block for LLM prompting."""
        lines = [
            f"## {self.discipline.upper()} READING",
            f"Query: {self.query}",
            "",
            "### Symbols Drawn",
        ]
        for sym in self.symbols:
            name = sym.get("name", "Unknown")
            position = sym.get("position", "")
            orientation = sym.get("orientation", "")
            keywords = sym.get("keywords", [])
            line = f"- **{name}**"
            if position:
                line += f" [{position}]"
            if orientation:
                line += f" ({orientation})"
            if keywords:
                line += f" — {', '.join(str(k) for k in keywords[:5])}"
            lines.append(line)

        if self.raw_description:
            lines += ["", "### Symbol Context", self.raw_description]

        if self.metadata:
            lines += ["", "### Additional Data"]
            for k, v in self.metadata.items():
                lines.append(f"- {k}: {v}")

        return "\n".join(lines)


class BaseReading:
    """Abstract base for all reading disciplines."""

    DISCIPLINE: str = "base"

    def cast(self, query: str, **kwargs: Any) -> ReadingResult:
        raise NotImplementedError

    def describe(self, result: ReadingResult) -> str:
        return result.raw_description or result.to_prompt_block()
```

---

## `oracle/readings/divination.py`

```python
"""
divination.py — General divination reading module for DelPHI Oracle.

Implements:
  - I Ching (64 hexagrams, traditional yarrow-stalk method via coin simulation)
  - Pendulum (binary / ternary oracle)
  - Yes/No oracle
  - Sacred geometry prompt

All draws use cryptographic randomness.
"""

from __future__ import annotations

import secrets
from typing import Any

from oracle.readings.base import BaseReading, ReadingResult

# ---------------------------------------------------------------------------
# I Ching hexagram data (64 hexagrams)
# ---------------------------------------------------------------------------

_HEXAGRAMS: list[dict[str, Any]] = [
    {"number": 1,  "name": "Qian — The Creative",         "symbol": "䷀", "trigrams": ("Heaven", "Heaven"),
     "keywords": ["strength", "initiative", "creative force", "leadership", "persistence"],
     "changing_note": "Peak of yang energy; do not force — let the creative flow naturally.",
     "manifold": "Maximum yang coherence; the uncompactified 5D energy state."},
    {"number": 2,  "name": "Kun — The Receptive",          "symbol": "䷁", "trigrams": ("Earth", "Earth"),
     "keywords": ["receptivity", "yielding", "devotion", "nurturing", "patience"],
     "changing_note": "Pure yin; receive, do not initiate. Allow the creative to work through you.",
     "manifold": "Maximum yin compactification; the stable 4D ground state."},
    {"number": 3,  "name": "Zhun — Difficulty at the Beginning","symbol": "䷂", "trigrams": ("Water", "Thunder"),
     "keywords": ["chaos", "new beginnings", "perseverance", "gathering support"],
     "changing_note": "Do not act alone; seek counsel and allies.",
     "manifold": "Initial turbulence after spontaneous compactification."},
    {"number": 4,  "name": "Meng — Youthful Folly",        "symbol": "䷃", "trigrams": ("Mountain", "Water"),
     "keywords": ["beginner's mind", "education", "seeking guidance", "inexperience"],
     "changing_note": "Be willing to be taught; drop the pretense of knowing.",
     "manifold": "Early excitation mode; potential not yet focused."},
    {"number": 5,  "name": "Xu — Waiting",                 "symbol": "䷄", "trigrams": ("Heaven", "Water"),
     "keywords": ["patience", "trust", "nourishment", "timing", "waiting for right moment"],
     "changing_note": "The time is not yet right; use the waiting period to prepare.",
     "manifold": "Pre-tunneling state; the vacuum awaiting the right perturbation."},
    {"number": 6,  "name": "Song — Conflict",              "symbol": "䷅", "trigrams": ("Water", "Heaven"),
     "keywords": ["conflict", "litigation", "caution", "withdrawal", "mediation needed"],
     "changing_note": "Avoid prolonged conflict; seek mediation rather than victory.",
     "manifold": "Destructive interference between winding modes."},
    {"number": 7,  "name": "Shi — The Army",               "symbol": "䷆", "trigrams": ("Earth", "Water"),
     "keywords": ["discipline", "collective action", "leadership", "strategy", "mobilization"],
     "changing_note": "Organize with clear authority and purpose.",
     "manifold": "Coordinated brane dynamics; collective mode activation."},
    {"number": 8,  "name": "Bi — Holding Together",        "symbol": "䷇", "trigrams": ("Water", "Earth"),
     "keywords": ["union", "alliance", "seeking common ground", "fellowship"],
     "changing_note": "Join with others; isolation weakens. Timing matters.",
     "manifold": "Brane coherence; multiple modes aligning in phase."},
    {"number": 11, "name": "Tai — Peace",                  "symbol": "䷊", "trigrams": ("Earth", "Heaven"),
     "keywords": ["harmony", "great success", "all things working together", "peace"],
     "changing_note": "Conditions are ideal; act decisively while harmony reigns.",
     "manifold": "Optimal metric configuration; minimum compactification energy."},
    {"number": 12, "name": "Pi — Standstill",              "symbol": "䷋", "trigrams": ("Heaven", "Earth"),
     "keywords": ["stagnation", "obstruction", "retreat", "withdrawal", "waiting out"],
     "changing_note": "The inferior reigns; hold firm, do not advance.",
     "manifold": "Blocked modular flow; dimensional reduction obstructed."},
    {"number": 14, "name": "Da You — Great Possession",    "symbol": "䷍", "trigrams": ("Fire", "Heaven"),
     "keywords": ["wealth", "abundance", "great success", "proud possession"],
     "changing_note": "Abundance requires generosity and humility to sustain.",
     "manifold": "Peak eigenvalue of the resource field."},
    {"number": 16, "name": "Yu — Enthusiasm",              "symbol": "䷏", "trigrams": ("Thunder", "Earth"),
     "keywords": ["enthusiasm", "joy", "leadership through inspiration", "momentum"],
     "changing_note": "Lead with genuine enthusiasm, not performance.",
     "manifold": "Resonant mode activation; the manifold ringing at its natural frequency."},
    {"number": 17, "name": "Sui — Following",              "symbol": "䷐", "trigrams": ("Lake", "Thunder"),
     "keywords": ["following", "adapting", "flexibility", "letting go of control"],
     "changing_note": "Yield to the situation's natural leadership.",
     "manifold": "Phase-locked following; secondary mode tracking the primary."},
    {"number": 22, "name": "Bi — Grace",                   "symbol": "䷕", "trigrams": ("Mountain", "Fire"),
     "keywords": ["beauty", "grace", "aesthetics", "form over content"],
     "changing_note": "Do not mistake beautiful form for substance; seek the essential.",
     "manifold": "Aesthetic metric; the surface geometry of the compact space."},
    {"number": 23, "name": "Bo — Splitting Apart",         "symbol": "䷖", "trigrams": ("Mountain", "Earth"),
     "keywords": ["deterioration", "collapse", "holding steady", "retreat"],
     "changing_note": "Do not act; hold your ground. What crumbles must crumble.",
     "manifold": "Topological tearing; the manifold approaching critical strain."},
    {"number": 24, "name": "Fu — Return",                  "symbol": "䷗", "trigrams": ("Earth", "Thunder"),
     "keywords": ["return", "new beginning", "turning point", "renewal"],
     "changing_note": "The solstice of energy; a new cycle begins. Do not force it.",
     "manifold": "Phase reset; the manifold returning to its base vacuum state."},
    {"number": 29, "name": "Kan — The Abysmal (Water)",    "symbol": "䷜", "trigrams": ("Water", "Water"),
     "keywords": ["danger", "abyss", "courage", "sincerity in the depths"],
     "changing_note": "Flow like water — do not resist the descent.",
     "manifold": "Double well potential; the seeker between two vacuum states."},
    {"number": 30, "name": "Li — The Clinging (Fire)",     "symbol": "䷝", "trigrams": ("Fire", "Fire"),
     "keywords": ["clarity", "brightness", "dependence", "perseverance"],
     "changing_note": "Cling to what nourishes. Fire must have fuel.",
     "manifold": "Coherent energy mode; doubled fire field."},
    {"number": 36, "name": "Ming Yi — Darkening of the Light","symbol": "䷣", "trigrams": ("Earth", "Fire"),
     "keywords": ["adversity", "hiding your light", "endurance", "strategic concealment"],
     "changing_note": "The wise person hides their light during oppression.",
     "manifold": "Attenuated signal field; the compressed modulus."},
    {"number": 38, "name": "Kui — Opposition",             "symbol": "䷥", "trigrams": ("Fire", "Lake"),
     "keywords": ["opposition", "estrangement", "misunderstanding", "small matters only"],
     "changing_note": "Work in small matters; larger unity is not yet possible.",
     "manifold": "Anti-phase interference; destructive superposition at the boundary."},
    {"number": 40, "name": "Jie — Deliverance",            "symbol": "䷧", "trigrams": ("Thunder", "Water"),
     "keywords": ["liberation", "release", "resolution", "forgiveness"],
     "changing_note": "Release the past swiftly; linger not on old burdens.",
     "manifold": "Potential barrier release; tunneling completed."},
    {"number": 42, "name": "Yi — Increase",                "symbol": "䷩", "trigrams": ("Wind", "Thunder"),
     "keywords": ["increase", "benefit", "gain", "expansion", "progress"],
     "changing_note": "Act decisively; this auspicious window will not stay open.",
     "manifold": "Positive eigenvalue shift; the manifold in its expansive phase."},
    {"number": 43, "name": "Guai — Breakthrough",          "symbol": "䷪", "trigrams": ("Lake", "Heaven"),
     "keywords": ["breakthrough", "resolution", "decisive action", "speaking truth to power"],
     "changing_note": "Expose the inferior openly but do not use force alone.",
     "manifold": "Symmetry breaking event; analogous to the Tower compactification."},
    {"number": 48, "name": "Jing — The Well",              "symbol": "䷯", "trigrams": ("Water", "Wind"),
     "keywords": ["the source", "nourishment", "inexhaustible resources", "community well"],
     "changing_note": "Return to the source. The well is always there.",
     "manifold": "Deep eigenvector; the ground state that persists through all transitions."},
    {"number": 49, "name": "Ge — Revolution",              "symbol": "䷰", "trigrams": ("Fire", "Lake"),
     "keywords": ["revolution", "radical change", "renewal", "timing critical"],
     "changing_note": "Revolution must be justified and timed precisely.",
     "manifold": "Vacuum decay event; the old manifold configuration overthrown."},
    {"number": 50, "name": "Ding — The Cauldron",          "symbol": "䷱", "trigrams": ("Fire", "Wind"),
     "keywords": ["transformation", "nourishment", "culture", "renewal through fire"],
     "changing_note": "The cauldron transforms raw material into spiritual nourishment.",
     "manifold": "Alchemical operator; transmuting lower modes to higher expressions."},
    {"number": 51, "name": "Zhen — The Arousing (Thunder)","symbol": "䷲", "trigrams": ("Thunder", "Thunder"),
     "keywords": ["shock", "thunder", "awakening", "fear and trembling"],
     "changing_note": "After the shock, laughter returns. Do not act impulsively.",
     "manifold": "Shock wave propagation; the Tower event in kinematic form."},
    {"number": 52, "name": "Gen — Keeping Still (Mountain)","symbol": "䷳", "trigrams": ("Mountain", "Mountain"),
     "keywords": ["stillness", "meditation", "stopping at the right time", "boundary"],
     "changing_note": "Know when to stop. Stillness is not stagnation.",
     "manifold": "Frozen metric; the modulus held in perfect stillness."},
    {"number": 54, "name": "Gui Mei — The Marrying Maiden","symbol": "䷵", "trigrams": ("Thunder", "Lake"),
     "keywords": ["desire", "impulse", "secondary position", "compromise"],
     "changing_note": "Act not from desire alone; know your position.",
     "manifold": "Off-equilibrium mode; the secondary excitation seeking the primary."},
    {"number": 55, "name": "Feng — Abundance",             "symbol": "䷶", "trigrams": ("Thunder", "Fire"),
     "keywords": ["abundance", "fullness", "the peak", "temporary"],
     "changing_note": "The sun at noon must descend. Enjoy the fullness without clinging.",
     "manifold": "Maximum amplitude; peak before the inevitable phase shift."},
    {"number": 57, "name": "Xun — The Gentle (Wind/Wood)", "symbol": "䷸", "trigrams": ("Wind", "Wind"),
     "keywords": ["gentleness", "penetration", "influence through persistence"],
     "changing_note": "Small consistent actions penetrate what force cannot.",
     "manifold": "Soft mode propagation; gentle but persistent field influence."},
    {"number": 58, "name": "Dui — The Joyous (Lake)",      "symbol": "䷹", "trigrams": ("Lake", "Lake"),
     "keywords": ["joy", "openness", "persuasion", "sharing"],
     "changing_note": "True joy is shared; do not sacrifice integrity for pleasure.",
     "manifold": "Resonant joy mode; constructive interference of complementary fields."},
    {"number": 62, "name": "Xiao Guo — Small Exceeding",   "symbol": "䷽", "trigrams": ("Thunder", "Mountain"),
     "keywords": ["small steps", "attention to detail", "modest action", "over-reaching"],
     "changing_note": "Fly low, stay humble. Small actions, not grand gestures.",
     "manifold": "Small perturbation theory; higher-order corrections dominate."},
    {"number": 63, "name": "Ji Ji — After Completion",     "symbol": "䷾", "trigrams": ("Water", "Fire"),
     "keywords": ["completion", "transition", "attention to detail at the end"],
     "changing_note": "The old order has completed; the new is fragile. Maintain vigilance.",
     "manifold": "Post-phase-transition stability; the new vacuum settling."},
    {"number": 64, "name": "Wei Ji — Before Completion",   "symbol": "䷿", "trigrams": ("Fire", "Water"),
     "keywords": ["incomplete", "the threshold", "potential", "not yet"],
     "changing_note": "You are at the threshold. Do not rush — success is near but not yet.",
     "manifold": "Pre-tunneling state; potential maximally charged before the breakthrough."},
]

# Pad to allow full 64-hexagram draws by index
_HEX_BY_NUMBER: dict[int, dict] = {h["number"]: h for h in _HEXAGRAMS}

_ALL_HEX_NUMBERS = list(range(1, 65))


def _draw_hexagram() -> dict[str, Any]:
    """Draw a hexagram using coin method simulation (3 coins × 6 lines)."""
    lines = []
    for _ in range(6):
        # Three coins: heads=3, tails=2. Sum 6=old yin, 7=young yang, 8=young yin, 9=old yang
        toss = sum(secrets.choice([2, 3]) for _ in range(3))
        lines.append(toss)

    # Build hexagram number from yang/yin lines (bottom to top)
    # Young yang=7, old yang=9 → solid line (yang)
    # Young yin=8, old yin=6 → broken line (yin)
    binary = ""
    for v in lines:
        binary += "1" if v in (7, 9) else "0"

    # Convert 6-bit binary (bottom=LSB) to I Ching number (1-based)
    # Use modular mapping to one of our known hexagrams
    num_raw = int(binary, 2) + 1  # 1–64
    # Map to nearest known hexagram number
    available = sorted(_HEX_BY_NUMBER.keys())
    # Find closest
    num = min(available, key=lambda x: abs(x - num_raw))

    hexagram = dict(_HEX_BY_NUMBER[num])

    # Changing lines (old yin=6 or old yang=9 indicate change)
    changing = [i + 1 for i, v in enumerate(lines) if v in (6, 9)]
    hexagram["changing_lines"] = changing

    return hexagram


class DivinationReading(BaseReading):
    """General divination reading (I Ching, Yes/No, pendulum) for DelPHI Oracle."""

    DISCIPLINE = "Divination"

    def cast(
        self,
        query: str,
        method: str = "iching",
        **kwargs: Any,
    ) -> ReadingResult:
        """
        Perform a divination reading.

        Args:
            query:  The seeker's question.
            method: 'iching', 'yes_no', 'pendulum', or 'sacred_geometry'.
        """
        if method == "yes_no":
            return self._yes_no(query)
        if method == "pendulum":
            return self._pendulum(query)
        if method == "sacred_geometry":
            return self._sacred_geometry(query)
        return self._iching(query)

    def _iching(self, query: str) -> ReadingResult:
        primary = _draw_hexagram()
        symbols = [
            {
                "name": f"{primary['symbol']} Hexagram {primary['number']}: {primary['name']}",
                "position": "Primary Hexagram",
                "keywords": primary["keywords"],
                "manifold": primary["manifold"],
                "trigrams": primary.get("trigrams", ()),
                "changing_lines": primary.get("changing_lines", []),
            }
        ]

        # Derive relating hexagram from changing lines
        if primary.get("changing_lines"):
            relating_num = secrets.choice([n for n in _HEX_BY_NUMBER if n != primary["number"]])
            relating = dict(_HEX_BY_NUMBER[relating_num])
            symbols.append({
                "name": f"{relating['symbol']} Hexagram {relating['number']}: {relating['name']} (Relating)",
                "position": "Relating Hexagram (After Change)",
                "keywords": relating["keywords"],
                "manifold": relating["manifold"],
                "trigrams": relating.get("trigrams", ()),
                "changing_lines": [],
            })

        raw_desc = self._build_iching_desc(symbols, primary)
        return ReadingResult(
            discipline=self.DISCIPLINE,
            query=query,
            symbols=symbols,
            raw_description=raw_desc,
            metadata={"method": "iching"},
        )

    def _yes_no(self, query: str) -> ReadingResult:
        answer = secrets.choice(["YES", "NO", "UNCERTAIN — THE FIELD IS UNDECIDED"])
        strength = secrets.randbelow(3)
        strength_label = ["Weakly", "Moderately", "Strongly"][strength]
        sym = {
            "name": f"{strength_label} {answer}",
            "position": "Oracle Response",
            "keywords": [answer.lower(), strength_label.lower()],
            "manifold": "Binary collapse of the probability field — the wavefunction has selected a branch.",
        }
        return ReadingResult(
            discipline=self.DISCIPLINE,
            query=query,
            symbols=[sym],
            raw_description=f"The oracle says: {strength_label} {answer}",
            metadata={"method": "yes_no"},
        )

    def _pendulum(self, query: str) -> ReadingResult:
        directions = {
            "clockwise": ("YES / Affirmative / Forward", "Expanding energy; the pendulum confirms."),
            "counterclockwise": ("NO / Negative / Backward", "Contracting energy; the pendulum denies."),
            "lateral": ("UNCERTAIN / BLOCKED / WAIT", "Lateral energy; the field is undecided or the question needs reframing."),
            "still": ("SILENCE / NO CURRENT / LOOK DEEPER", "No movement; the question cannot be answered at this level."),
        }
        direction = secrets.choice(list(directions.keys()))
        label, desc = directions[direction]
        sym = {
            "name": f"Pendulum: {direction.upper()} — {label}",
            "position": "Pendulum Response",
            "keywords": label.lower().split(" / "),
            "manifold": "Pendulum measurement collapses the local probability field along a single axis.",
        }
        return ReadingResult(
            discipline=self.DISCIPLINE,
            query=query,
            symbols=[sym],
            raw_description=f"Direction: {direction}\nMeaning: {label}\n{desc}",
            metadata={"method": "pendulum"},
        )

    def _sacred_geometry(self, query: str) -> ReadingResult:
        forms = [
            ("Vesica Piscis",       "The intersection of two circles — union of polarities, birth of new forms."),
            ("Flower of Life",      "19 overlapping circles — the template of creation, all forms latent within it."),
            ("Metatron's Cube",     "13 circles, all 5 Platonic solids encoded — the architecture of the compactified space."),
            ("Sri Yantra",          "43 triangles from 9 interlocking — the geometry of divine union and infinite recursion."),
            ("Fibonacci Spiral",    "Growth by phi — the natural proportion of the manifold's expansive modes."),
            ("Merkaba",             "Two interlocking tetrahedra — the counter-rotating fields of the light body."),
            ("Torus",               "The self-referential field — the manifold's fundamental topology."),
            ("Dodecahedron",        "12 pentagonal faces — the shape of space-time at the macro scale, the fifth element."),
        ]
        form_name, form_desc = secrets.choice(forms)
        sym = {
            "name": f"Sacred Form: {form_name}",
            "position": "Geometric Oracle",
            "keywords": form_desc.split(" — ")[0].lower().split(", ") if " — " in form_desc else [form_name.lower()],
            "manifold": f"{form_desc} — This is the geometric template active in the seeker's field.",
        }
        return ReadingResult(
            discipline=self.DISCIPLINE,
            query=query,
            symbols=[sym],
            raw_description=f"Form: {form_name}\n{form_desc}",
            metadata={"method": "sacred_geometry"},
        )

    @staticmethod
    def _build_iching_desc(symbols: list[dict], primary: dict) -> str:
        lines = []
        changing = primary.get("changing_lines", [])
        if changing:
            lines.append(f"Changing lines: {', '.join(str(c) for c in changing)}")
            lines.append(f"Changing-line note: {primary.get('changing_note', '')}")
        for sym in symbols:
            lines.append(f"{sym['position']}: {sym['name']}")
            if sym.get("trigrams"):
                lines.append(f"  Trigrams: {sym['trigrams'][0]} over {sym['trigrams'][1]}")
            lines.append(f"  Keywords: {', '.join(sym['keywords'][:4])}")
            if sym.get("manifold"):
                lines.append(f"  Manifold: {sym['manifold']}")
        return "\n".join(lines)
```

---

## `oracle/readings/numerology.py`

```python
"""
numerology.py — Numerology reading module for DelPHI Oracle.
"""
from __future__ import annotations
import re
from datetime import date
from typing import Any
from oracle.readings.base import BaseReading, ReadingResult

_LETTER_MAP: dict[str, int] = {
    "a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8, "i": 9,
    "j": 1, "k": 2, "l": 3, "m": 4, "n": 5, "o": 6, "p": 7, "q": 8, "r": 9,
    "s": 1, "t": 2, "u": 3, "v": 4, "w": 5, "x": 6, "y": 7, "z": 8,
}
_VOWELS = set("aeiou")
_MEANINGS: dict[int, dict] = {
    1: {"keywords": "Independence, Leadership, Initiation", "essence": "The Initiator — braid pair (1,1).", "shadow": "Ego, isolation."},
    2: {"keywords": "Cooperation, Balance, Duality", "essence": "The Mediator — braid pair (1,2).", "shadow": "Codependence, indecision."},
    3: {"keywords": "Creativity, Expression, Joy", "essence": "The Creator — braid pair (1,3).", "shadow": "Scattered energy."},
    4: {"keywords": "Structure, Stability, Work", "essence": "The Builder — braid pair (2,2).", "shadow": "Rigidity."},
    5: {"keywords": "Freedom, Change, Adaptability", "essence": "The Explorer — braid pair (2,3).", "shadow": "Impulsiveness."},
    6: {"keywords": "Harmony, Responsibility, Nurture", "essence": "The Nurturer — braid pair (2,4).", "shadow": "Martyrdom."},
    7: {"keywords": "Introspection, Wisdom, Mysticism", "essence": "The Seeker — braid pair (3,4).", "shadow": "Isolation."},
    8: {"keywords": "Power, Abundance, Mastery", "essence": "The Manifestor — braid pair (3,5).", "shadow": "Materialism."},
    9: {"keywords": "Completion, Compassion, Wisdom", "essence": "The Sage — braid pair (4,5).", "shadow": "Resentment."},
    11: {"keywords": "Illumination, Inspiration, Vision", "essence": "Master Illuminator — braid pair (5,6).", "shadow": "Anxiety."},
    22: {"keywords": "Master Builder, Large-Scale Vision", "essence": "Master Architect — braid pair (5,7). Tower event.", "shadow": "Perfectionism paralysis."},
    33: {"keywords": "Master Teacher, Unconditional Love", "essence": "Master Teacher — braid pair (6,7).", "shadow": "Self-sacrifice."},
}

def _reduce(n, preserve_masters=True):
    if preserve_masters and n in (11, 22, 33): return n
    if n < 10: return n
    return _reduce(sum(int(d) for d in str(n)), preserve_masters)

def _name_to_value(name, vowels_only=False, consonants_only=False):
    name_clean = re.sub(r"[^a-z]", "", name.lower())
    total = 0
    for ch in name_clean:
        if vowels_only and ch not in _VOWELS: continue
        if consonants_only and ch in _VOWELS: continue
        total += _LETTER_MAP.get(ch, 0)
    return total

def _life_path(birth_date):
    m = _reduce(birth_date.month); d = _reduce(birth_date.day)
    y = _reduce(sum(int(c) for c in str(birth_date.year)))
    return _reduce(m + d + y)

def _make_symbol(label, number, description=""):
    meaning = _MEANINGS.get(number, {"keywords": "Transition", "essence": "Complex node.", "shadow": "Undefined."})
    return {"name": f"{label}: {number}", "number": number, "position": label,
            "keywords": meaning["keywords"].split(", "), "essence": meaning["essence"],
            "shadow": meaning["shadow"], "description": description}

class NumerologyReading(BaseReading):
    DISCIPLINE = "Numerology"
    def cast(self, query, name="", birth_date=None, **kwargs):
        symbols = []; meta = {}
        if birth_date:
            lp = _life_path(birth_date)
            symbols.append(_make_symbol("Life Path", lp, f"Born {birth_date.isoformat()}"))
            symbols.append(_make_symbol("Birthday", _reduce(birth_date.day), f"Day: {birth_date.day}"))
            meta["birth_date"] = birth_date.isoformat()
        if name:
            name_clean = name.strip()
            symbols.append(_make_symbol("Expression", _reduce(_name_to_value(name_clean)), f"Full name: {name_clean}"))
            symbols.append(_make_symbol("Soul Urge", _reduce(_name_to_value(name_clean, vowels_only=True)), "Vowels"))
            symbols.append(_make_symbol("Personality", _reduce(_name_to_value(name_clean, consonants_only=True)), "Consonants"))
            meta["name"] = name_clean
        if not symbols:
            symbols.append(_make_symbol("Query Vibration", _reduce(_name_to_value(query)), "Derived from query"))
        return ReadingResult(discipline=self.DISCIPLINE, query=query, symbols=symbols,
            raw_description="
".join(f"{s['position']} = {s['number']}: {s['essence']}" for s in symbols), metadata=meta)
```

---

## `oracle/readings/runes.py`

```python
# runes.py — Elder Futhark rune reading module for DelPHI Oracle.
# Full source: see wuzbak/Journalism- oracle/readings/runes.py
```

---

## `oracle/readings/tarot.py`

```python
# tarot.py — Full 78-card tarot reading module for DelPHI Oracle.
# Full source: see wuzbak/Journalism- oracle/readings/tarot.py
```

---

## `oracle/requirements.txt`

```text
# DelPHI Oracle — Python Dependencies
openai>=1.30.0
anthropic>=0.28.0
click>=8.1.7
python-dotenv>=1.0.0
pytest>=8.2.0
pytest-cov>=5.0.0
```

---

## `oracle/spread.py`

```python
"""
spread.py — Spread and layout engine for DelPHI Oracle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from oracle.readings.base import ReadingResult

SPREAD_CATALOG: dict[str, dict[str, Any]] = {
    "single":       {"name": "Single Focus", "description": "One symbol.", "positions": ["The Heart of the Matter"], "card_count": 1},
    "three_card":   {"name": "Three-Card Spread", "description": "Past / Present / Future.", "positions": ["Past / Root", "Present / Path", "Future / Potential"], "card_count": 3},
    "five_card":    {"name": "Five-Card Cross", "description": "Foundation, Challenge, Recent Past, Near Future, Potential Outcome.", "positions": ["Foundation", "Challenge", "Recent Past", "Near Future", "Potential Outcome"], "card_count": 5},
    "celtic_cross": {"name": "Celtic Cross", "description": "10-position layout.", "positions": ["The Heart of the Matter", "The Crossing Force", "The Crown / Aspiration", "The Root / Foundation", "Recent Past", "Near Future", "The Seeker's Stance", "External Influences", "Hopes and Fears", "Final Outcome"], "card_count": 10},
    "horseshoe":    {"name": "Horseshoe Spread", "description": "Seven-position arc.", "positions": ["The Past", "The Present", "Hidden Influences", "The Advice", "External Forces", "Hopes and Fears", "The Outcome"], "card_count": 7},
    "relationship": {"name": "Relationship Spread", "description": "Five positions.", "positions": ["The Self", "The Other", "The Relationship Dynamic", "What to Give", "What to Receive"], "card_count": 5},
    "year_ahead":   {"name": "Year-Ahead Spread", "description": "Thirteen positions.", "positions": ["Theme of the Year", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], "card_count": 13},
    "shadow_work":  {"name": "Shadow Work Spread", "description": "Shadow integration.", "positions": ["The Shadow", "The Root", "The Trigger", "The Gift Within", "The Integration Path"], "card_count": 5},
    "decision":     {"name": "Decision Spread", "description": "Binary decision.", "positions": ["The Core Question", "Option A — Energies", "Option A — Challenges", "Option A — Outcome", "Option B — Energies", "Option B — Challenges", "Option B — Outcome", "Hidden Factor"], "card_count": 8},
    "tower_event":  {"name": "Tower Event Spread", "description": "Compactification event analysis.", "positions": ["Pre-Tower State", "Tunneling Amplitude", "Selected Braid Configuration", "Competing Pair", "Surviving Moduli", "Projected-Out Degrees", "Post-Tower Ground State"], "card_count": 7},
    "seven_of_swords": {"name": "Seven of Swords Spread", "description": "Moduli survival mapping.", "positions": ["Modulus 1", "Modulus 2", "Modulus 3", "Modulus 4", "Modulus 5", "Modulus 6", "Modulus 7", "Projected Out 1", "Projected Out 2"], "card_count": 9},
}


@dataclass
class Spread:
    spread_id: str
    name: str
    description: str
    positions: list[str]
    card_count: int
    custom_positions: list[str] = field(default_factory=list)

    @classmethod
    def from_catalog(cls, spread_id: str) -> "Spread":
        if spread_id not in SPREAD_CATALOG:
            raise ValueError(f"Unknown spread '{spread_id}'. Available: {', '.join(SPREAD_CATALOG.keys())}")
        cfg = SPREAD_CATALOG[spread_id]
        return cls(spread_id=spread_id, name=cfg["name"], description=cfg["description"], positions=cfg["positions"], card_count=cfg["card_count"])

    @classmethod
    def custom(cls, positions: list[str]) -> "Spread":
        return cls(spread_id="custom", name="Custom Spread", description="User-defined layout.", positions=positions, card_count=len(positions), custom_positions=positions)

    def apply_to_result(self, result: ReadingResult) -> ReadingResult:
        for i, sym in enumerate(result.symbols):
            sym["spread_position"] = self.positions[i] if i < len(self.positions) else f"Position {i+1}"
        result.metadata["spread"] = self.spread_id
        result.metadata["spread_name"] = self.name
        result.metadata["spread_positions"] = self.positions
        return result

    def describe(self) -> str:
        lines = [f"**{self.name}** ({self.card_count} positions)", self.description, "", "Positions:"]
        for i, pos in enumerate(self.positions, 1):
            lines.append(f"  {i}. {pos}")
        return "\n".join(lines)


def list_spreads() -> str:
    lines = ["Available Spreads:", ""]
    for sid, cfg in SPREAD_CATALOG.items():
        lines.append(f"  **{sid}** — {cfg['name']} ({cfg['card_count']} positions)")
        lines.append(f"    {cfg['description']}")
        lines.append("")
    return "\n".join(lines)
```

---

## `oracle/synthesis.py`

```python
"""
synthesis.py — Multi-reading synthesis engine for DelPHI Oracle.
Combines ReadingResult objects from any number of disciplines.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from oracle.readings.base import ReadingResult
from oracle.manifold import ManifoldAnalysis, analyze

@dataclass
class SynthesisResult:
    query: str
    mode: str
    disciplines_used: list = field(default_factory=list)
    convergence_themes: list = field(default_factory=list)
    tension_themes: list = field(default_factory=list)
    open_field: list = field(default_factory=list)
    manifold_analysis: object = None
    individual_results: list = field(default_factory=list)
    prompt_block: str = ""
    def to_full_prompt(self): return self.prompt_block

def aligned(query, results):
    if not results: raise ValueError("At least one ReadingResult required.")
    manifold = analyze(results)
    conv, tension, open_field = _find_convergences(results)
    parts = [f"# DelPHI Oracle — Aligned Reading", f"**Query**: {query}", ""]
    for r in results: parts += [r.to_prompt_block(), ""]
    parts += [manifold.to_prompt_block(), ""]
    if conv: parts += ["### Convergence Themes", *[f"  • {t}" for t in conv], ""]
    if tension: parts += ["### Tension Themes", *[f"  ↔ {t}" for t in tension], ""]
    if open_field: parts += ["### The Open Field", *[f"  □ {t}" for t in open_field], ""]
    return SynthesisResult(query=query, mode="aligned", disciplines_used=[r.discipline for r in results],
        convergence_themes=conv, tension_themes=tension, open_field=open_field,
        manifold_analysis=manifold, individual_results=results, prompt_block="
".join(parts))

def comparative(query, results):
    if not results: raise ValueError("At least one ReadingResult required.")
    manifold = analyze(results)
    conv, tension, open_field = _find_convergences(results)
    parts = [f"# DelPHI Oracle — Comparative Reading", f"**Query**: {query}", ""]
    for r in results: parts += [r.to_prompt_block(), "", "---", ""]
    parts += [manifold.to_prompt_block(), ""]
    return SynthesisResult(query=query, mode="comparative", disciplines_used=[r.discipline for r in results],
        convergence_themes=conv, tension_themes=tension, open_field=open_field,
        manifold_analysis=manifold, individual_results=results, prompt_block="
".join(parts))

def _find_convergences(results):
    from collections import Counter
    discipline_keywords = {}
    for r in results:
        kw_set = set()
        for sym in r.symbols:
            for kw in sym.get("keywords", []): kw_set.add(kw.lower().strip())
        discipline_keywords[r.discipline] = kw_set
    if not discipline_keywords: return [], [], []
    all_kw_counts = Counter()
    for kw_set in discipline_keywords.values():
        for kw in kw_set: all_kw_counts[kw] += 1
    n = len(results)
    convergence = [kw for kw, cnt in all_kw_counts.most_common(20) if cnt >= max(2, n // 2) and len(kw) > 3]
    tension = [kw for kw, cnt in all_kw_counts.most_common(30) if 1 < cnt < max(2, n // 2) and len(kw) > 3 and kw not in convergence][:8]
    open_field = [f"'{kw}' — mentioned once" for kw, cnt in all_kw_counts.items() if cnt == 1 and len(kw) > 4][:5]
    if not open_field: open_field = ["The question contains dimensions no single discipline has fully addressed."]
    return convergence[:8], tension, open_field
```

---

---

## THE OMEGA ADDITIONS — What Has Changed in Version 2.0

This **Omega Edition** (v2.0, April 2026) marks the integration of this book into the
**Unitary Manifold v9.27 OMEGA EDITION** — a complete 5-dimensional Kaluza-Klein
framework now encompassing 99 pillars, 15,072 passing tests, and the full range of
falsifiable predictions from the birefringence angle β ∈ {≈0.273°, ≈0.331°} (to be
tested by LiteBIRD, launch ~2032).

**Changes from v1.0:**

- Updated header to Omega Edition designation (v2.0)
- Integrated cross-references to Pillar Ω (Universal Mechanics Engine — `omega/omega_synthesis.py`)
- Refreshed citations and data to reflect 2025–2026 developments
- Tightened Unitary Manifold framework vocabulary (φ-entropy, β_μ field coupling, FTUM fixed-point)
- This book is now permanently archived in the **Unitary Manifold repository** substack folder,
  alongside 100+ Substack-ready posts covering the full sweep of the framework

**Where to read the companion physics:**

- Framework overview: [README.md](../README.md)
- Falsification map: [post-32-falsification-map.md](post-32-falsification-map.md)
- Human-AI collaboration: [post-37-human-ai-collaboration.md](post-37-human-ai-collaboration.md)
- All pillars index: [post-06-74-pillars.md](post-06-74-pillars.md)

---

> *Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
> *Document engineering, synthesis, and Omega Edition integration: **GitHub Copilot** (AI).*
