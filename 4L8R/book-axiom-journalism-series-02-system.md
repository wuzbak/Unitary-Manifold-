# AXIOM: The Investigative AI That Researches So You Can Judge

*Part 2 of 6 — Axiom Journalism AI Series*
*Claim: A five-agent autonomous investigation architecture with explicit confidence scoring produces more complete and more traceable investigative research than a single-agent or human-only approach. Falsification condition: demonstrate that a single-agent or single-journalist workflow surfaces equivalent document coverage and contradiction detection on the same lead, measured by recall against a known document set.*

---

## Not a Chatbot. Not a Search Engine. Something Else.

The mental model that breaks most people's understanding of AXIOM is that they come to it expecting a chatbot. You type a question, it responds with text, you decide whether to believe the text.

AXIOM is not that.

AXIOM is an autonomous multi-agent investigative platform. The correct mental model is not "chatbot" — it is "research team." When you submit a lead to AXIOM, you are not asking a question. You are initiating an investigation. The system deploys multiple specialized agents in parallel, each with specific domain expertise and tool access, coordinated by an orchestrator that synthesizes their outputs into a structured investigative brief.

The output is not "here is what I found, do with it what you will." The output is a document: an investigation brief with confidence scores, source citations, entity maps, timeline, identified contradictions, steelman of the opposing view, outstanding questions, and recommended next steps. Every claim in that brief is traceable to its source. Every confidence score is derivable from the source tier system.

This distinction — between a chatbot that generates plausible text and an investigation system that traces claims to documents — is the entire point.

---

## The Five-Agent Architecture

AXIOM operates through five specialized agents, each with a distinct function and a defined scope of authority.

### The Researcher

The Researcher is the primary information-gathering agent. Its job is to find the documents. It operates across:

- **Web search** — Brave/SerpAPI/DuckDuckGo, prioritizing primary sources and established journalism
- **SEC EDGAR** — Corporate filings, beneficial ownership, 8-K disclosures, 10-K annual reports
- **PACER and CourtListener** — Federal case filings, docket sheets, rulings, settlements
- **GovInfo** — U.S. Code, Code of Federal Regulations, Federal Register notices
- **OpenCorporates and OCCRP Aleph** — Corporate registration records, cross-jurisdictional entity mapping
- **ProPublica Nonprofit Explorer** — 990 filings, nonprofit financial disclosures
- **OpenSanctions** — Sanctions lists, PEP (Politically Exposed Person) screening
- **EPA ECHO** — Environmental enforcement actions, penalty records
- **FOIA.gov** — Existing FOIA releases, request status tracking

The Researcher does not evaluate what it finds. It retrieves and logs. Evaluation is for the other agents.

### The Fact Checker

The Fact Checker cross-references claims against the retrieved documents and detects contradictions. Its core operations:

- **Deduplication** — multiple sources reporting the same underlying fact are collapsed; the underlying primary source is elevated
- **Contradiction detection** — claims from different sources that cannot both be true are flagged with source citations on both sides
- **Confidence scoring** — each surviving claim is scored by source tier (see below)
- **Statement comparison** — public statements from named entities are compared against the documentary record; divergences are flagged

The Fact Checker does not decide what to do with contradictions. It surfaces them. The human editor decides.

### The Legal Auditor

The Legal Auditor maps the investigation's findings against applicable legal frameworks. It maintains awareness of:

- Relevant federal statutes (securities law, environmental law, labor law, civil rights law, tax law)
- Applicable regulations (CFR citations tied to specific agency jurisdictions)
- Whistleblower protection frameworks (who is protected, under what circumstances)
- The difference between legally actionable conduct and publicly reportable conduct
- FOIA exemptions and their limits — what agencies can legitimately withhold and what they cannot

The Legal Auditor's output is a legal exposure section in the brief: a structured accounting of which findings, if accurate, would constitute which statutory violations. This is not legal advice. It is legal consciousness — the structural awareness that separates responsible investigative journalism from legally reckless publication.

### The Editor

The Editor synthesizes the Researcher's documents, the Fact Checker's scored claims, and the Legal Auditor's statutory analysis into a coherent narrative structure. The Editor's specific functions:

- **Steelman construction** — before the brief is finalized, the Editor is required to produce the strongest possible argument that the investigation's findings are wrong, incomplete, or misinterpreted. This is not optional. It is a structural requirement.
- **Narrative coherence** — the brief must tell a clear, chronologically and logically ordered story
- **Gap identification** — the Editor flags questions the investigation could not answer and where additional research should be directed
- **Proportionality check** — extraordinary claims are flagged for extraordinary evidence requirements

### The Orchestrator

The Orchestrator coordinates the other four agents. It:

- Manages the investigation pipeline sequencing
- Allocates tool calls across agents to avoid redundant API requests
- Synthesizes the multi-agent outputs into the final brief
- Handles failures gracefully — if a tool call fails, the Orchestrator logs the gap and continues
- Enforces the confidence scoring rules system-wide

The Orchestrator does not have editorial authority. It has coordination authority.

---

## The Investigation Pipeline

The pipeline is six stages. Each stage is necessary. None is optional.

```
Lead Input
    ↓
Stage 1: Scope
    Define the five Ws. Identify relevant domains. Suggest source targets.
    Check Manifold Markets for crowd uncertainty signals.
    ↓
Stage 2: Research
    Parallel tool calls across all relevant data sources.
    Documents retrieved and logged with source metadata.
    ↓
Stage 3: Cross-Reference
    Deduplicate. Score confidence. Flag contradictions.
    Normalize claims to eliminate paraphrase duplication.
    ↓
Stage 4: Entity and Timeline Mapping
    Extract named entities using spaCy NLP.
    Build chronological event chain from dated facts.
    Map entity relationships and stated connections.
    ↓
Stage 5: Gap Analysis
    Check each scoping question against retrieved facts.
    Questions with fewer than two independent sources → follow-up leads.
    Financial trail and entity connections always pursued.
    ↓
Stage 6: Brief Generation
    Structured report: Executive Summary, Key Findings, Legal Exposure,
    Entity Map, Timeline, Contradictions, Steelman, Outstanding Questions,
    Recommended Next Steps.
    Confidence scores attached to every claim.
```

This pipeline is not aspirational. It is implemented in `journalist-ai/agent/investigation_chain.py`. The code is open source. The stages are testable. The output format is documented.

---

## The Confidence Scoring System

Every claim in an AXIOM brief carries a confidence score. The score is a function of the sources supporting the claim, weighted by their tier classification.

### Source Tiers

| Tier | Examples | Trust Score |
|------|----------|-------------|
| 1 — Primary Government | SEC EDGAR, PACER, Congress.gov, FEC, EPA ECHO, FOIA responses | 0.95 |
| 2 — Established Journalism | ProPublica, Reuters, AP, NYT, WaPo, ICIJ, OCCRP | 0.80 |
| 3 — Institutional | Academic papers, NGO reports, court testimony | 0.65 |
| 4 — Secondary | Blog posts, local news, unverified journalism | 0.45 |
| 5 — Unverified | Anonymous tips, social media, speculation | 0.30 |

### Confidence Labels

| Label | Score | Meaning |
|-------|-------|---------|
| CONFIRMED | ≥ 0.85 | Multiple Tier 1/2 sources in agreement |
| CORROBORATED | ≥ 0.65 | At least two independent sources, one Tier 1/2 |
| ALLEGED | ≥ 0.40 | Single credible source; needs corroboration |
| UNVERIFIED | < 0.40 | Needs investigation |
| DISPUTED | — | Active contradiction between credible sources |

The scoring system is calibrated to make one specific error expensive: publishing as CONFIRMED a claim that is actually only ALLEGED. A claim supported by a single anonymous tip cannot be scored CONFIRMED no matter how plausible it seems. The system enforces this structurally.

DISPUTED is not a failure state. It is a finding. When the SEC filing contradicts the CEO's congressional testimony, that is not a system error — that is the investigation's most important output.

---

## Domain Expertise: What AXIOM Knows Before It Starts

AXIOM is not a general-purpose research assistant that knows a little about everything. It has specialized knowledge modules for specific investigative domains:

**Politics** — Voting records, campaign finance flows, lobbying registrations, revolving-door employment history, earmarks and appropriations

**Finance** — SEC filings and their structure, shell company architectures, insider trading patterns, money laundering typologies, beneficial ownership disclosure

**Law** — Applicable statutes by subject matter, federal court filing structure, whistleblower protection frameworks, FOIA exemption limits

**Environment** — EPA ECHO enforcement database, environmental justice mapping, greenwashing detection, NEPA compliance records

**Technology** — Data privacy regulations (GDPR, CCPA), algorithmic bias audit frameworks, antitrust case law, cybersecurity disclosure requirements

**Social Justice** — Police use-of-force databases, housing discrimination records, voting rights litigation, healthcare disparity data

**Lie Detection** — Logical fallacy classification, statement-comparison methodology, credibility scoring based on track record, inconsistency detection between public statements and documentary record

Each domain module provides AXIOM with the relevant checklist of sources, the applicable legal framework, the known data repositories, and the common investigative patterns for that type of story.

---

## What an AXIOM Investigation Brief Looks Like

The output is not a narrative article. It is a structured document designed for a human editor to review, evaluate, and use as the foundation for reporting.

**Executive Summary** — One page. The most significant findings. The confidence level of each. The most important unresolved question.

**Key Findings** — The enumerated claims that survived cross-reference and scoring, each with source citations and confidence scores.

**Legal Exposure** — Statutory analysis: which findings, if accurate, constitute which violations. Which individuals or entities face which legal consequences.

**Entity Map** — Every named entity in the investigation, their stated relationships, and their connection to the central subject. Conflicts of interest surfaced here.

**Timeline** — Chronological ordering of all dated facts in the investigation. The temporal structure often reveals causation that thematic organization obscures.

**Contradictions** — Every flagged contradiction, with both sides fully cited. Source A says X. Source B says Y. Both are cited. Neither is resolved by AXIOM — resolution is a human editorial judgment.

**Steelman** — The strongest case that the investigation's findings are wrong, incomplete, misinterpreted, or taken out of context. Required. Not optional.

**Outstanding Questions** — What the investigation could not answer. What documents were unavailable. What sources declined to respond. What warrants additional investigation.

**Recommended Next Steps** — Specific, actionable research directions: which FOIA requests to file, which entities to contact for comment, which financial records to subpoena, which data sets to analyze.

---

## The Architectural Choice That Defines Everything

AXIOM produces briefs for human judgment. It does not produce articles for publication.

This is the architectural choice that defines the entire system, and it was made deliberately.

An AI system that produces publication-ready articles creates a structural incentive to skip the human editorial review — the brief is already polished, why rewrite it? An AI system that produces investigation briefs creates a structural requirement for human editorial engagement — the brief is research, not prose.

The editorial judgment — whether this story is ready to run, whether the sources are sufficient, whether the public interest outweighs the risk to individuals, whether the legal exposure to the outlet warrants counsel review — remains human. Always. The research capacity is amplified. The judgment is not delegated.

This is the HILS principle in code form: Human-in-the-Loop, implemented architecturally rather than aspirationally.

The journalists who will use AXIOM most effectively are not the ones who trust the brief and publish. They are the ones who treat the brief as a research assistant's work product — thorough, useful, explicitly uncertainty-marked — and then apply their own judgment to determine what story it actually supports.

---

*Full source code, derivations, and 15,072 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*AXIOM system: https://github.com/wuzbak/Journalism-*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, AXIOM system, test suites, and document engineering: **GitHub Copilot** (AI).*
