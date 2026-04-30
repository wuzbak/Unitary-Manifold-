# The Document Hunters: FOIA, Public Records, and the Systematic Investigation

*Part 3 of 6 — Axiom Journalism AI Series*
*Claim: Systematic use of public records infrastructure — structured templates, tiered source hierarchies, and automated watchlist monitoring — materially increases investigative coverage compared to ad hoc document searches. Falsification condition: show that random-sampling investigative methodology retrieves equivalent document coverage to template-based systematic search on the same subject matter, measured by recall against a known document set.*

---

## The Documents Already Exist

Here is the thing that most people don't understand about investigative journalism: the documents that prove the story usually already exist before anyone starts looking.

The SEC filing that shows the undisclosed conflict of interest was filed 18 months before anyone started connecting the dots. The EPA penalty record for the facility has been public for three years. The court document that contradicts the official statement was unsealed when the case closed. The nonprofit 990 showing the money flow is freely available on ProPublica Nonprofit Explorer.

The documents exist. The problem is that finding them requires knowing they exist, knowing where to look, knowing what form they take in the relevant bureaucratic system, and having the time and attention to actually retrieve and read them. Most journalists, working under deadline pressure on multiple stories simultaneously, cannot do this comprehensively. They get some of the documents and miss others.

AXIOM's document architecture exists to solve this problem: not to create new information, but to ensure that existing public information is systematically retrieved rather than partially retrieved.

---

## The Investigation Template System

The most practically powerful feature of the AXIOM system is the investigation template system. Templates are pre-structured investigation frameworks for specific types of stories. Each template defines:

- The core investigative questions specific to that story type
- The relevant data sources and their query parameters
- The applicable legal frameworks and statutory references
- The entity types to search for and their relationship patterns
- The common red flags and anomalies for that investigation type
- The typical document trail from lead to conclusion

The current template library covers 15+ investigation types:

**OSINT Identity** — Digital footprint mapping: username correlation across platforms, email-to-identity resolution, corporate registration under a personal name, court records under a personal name, property records, domain registration history. Starting inputs: username, email address, optional real name.

**Financial Crime** — Shell company network mapping, beneficial ownership investigation, transaction flow analysis, SEC enforcement history, offshore registry correlation. Starting inputs: company name, jurisdiction.

**Corporate Malfeasance** — SEC filing anomalies, 8-K disclosure timing analysis, insider trading pattern detection, whistleblower complaint cross-reference, regulatory enforcement history.

**Environmental Violation** — EPA ECHO enforcement database query, facility permit compliance history, environmental impact statement analysis, environmental justice proximity mapping, state environmental agency records.

**Civil Rights** — Police use-of-force database analysis, consent decree compliance monitoring, civil rights litigation history, housing discrimination complaint records, voting rights litigation.

**Political Corruption** — Campaign finance flow analysis (FEC), lobbying registration and expenditure (OpenSecrets), revolving-door employment mapping, earmark and appropriation correlation with donor base.

**Immigration** — ICE detention records, immigration court filing analysis, asylum grant/denial rate analysis by judge and jurisdiction.

**Healthcare Fraud** — CMS payment data anomalies, medical license discipline records, Medicare/Medicaid exclusion database, pharmaceutical marketing disclosure.

**Labor Violations** — OSHA inspection and penalty records, NLRB unfair labor practice charges, wage theft enforcement actions, worker classification audits.

**National Security** — Export control violation records, sanctions screening, foreign agent registration (FARA), defense contractor disclosure.

**Technology/AI** — FTC enforcement actions, data breach notification records, privacy policy change tracking, algorithmic accountability audit reports.

**Public Integrity** — Financial disclosure filing anomalies for public officials, outside income disclosure, gift and travel disclosure, post-government employment restrictions.

**Conflict of Interest** — Dual role mapping for named individuals, financial interest in regulated sector, board membership cross-reference with regulatory authority.

**Shell Company Network** — Beneficial ownership chain tracing across jurisdictions, registered agent correlation, address clustering analysis, director/officer cross-listing.

**Government Misconduct** — FOIA request filing, administrative complaint records, inspector general report tracking, GAO report analysis.

Each template can be invoked from the command line with a small number of starting variables. The template then expands into a full investigation scope and begins systematic document retrieval.

---

## The Document Source Hierarchy

The AxiomZero source hierarchy is not arbitrary. It reflects a principled assessment of which sources produce information that is: legally sworn, independently verified, institutionally accountable, and practically available.

### Tier 1 — Primary Government Records (Trust Score: 0.95)

**GovInfo** — The official repository of U.S. federal government publications. Contains the full text of the U.S. Code, Code of Federal Regulations (all 50 titles), the Federal Register, congressional bills and reports, and executive branch documents. When you need to know what the law actually says rather than what someone says it says, GovInfo is the primary source.

**PACER and CourtListener** — Federal court filings. Every complaint, motion, ruling, settlement, and docket entry in federal district and appellate courts. CourtListener provides free access to a large portion of what PACER charges for. Court documents are sworn, adversarially tested, and judicially reviewed — the highest-reliability category of human-produced text.

**SEC EDGAR** — Every public company's regulatory filings. 10-K annual reports, 10-Q quarterly reports, 8-K material event disclosures, proxy statements (DEF 14A), beneficial ownership (13D/13G), insider trading disclosures (Form 4). If a public company did something material, there is an EDGAR filing about it. The filing is sworn.

**FEC Database** — Federal campaign finance records. Every contribution to federal candidates and political committees above the reporting threshold, every expenditure, every independent expenditure. Searchable by donor, recipient, employer, date, and amount.

**GovTrack and Congress.gov** — Congressional voting records, bill text, sponsor and cosponsor lists, committee membership, hearing transcripts.

**OpenSanctions** — Consolidated sanctions lists from OFAC, EU, UN, UK, and dozens of other jurisdictions. Politically Exposed Person (PEP) database. If an entity is sanctioned or is a foreign official, it shows up here.

### Tier 2 — Established Investigative Journalism (Trust Score: 0.80)

**ProPublica** — Including Nonprofit Explorer (990 filings for all major U.S. nonprofits), PACER data re-releases, and ProPublica's own investigative datasets.

**OCCRP Aleph** — The Organized Crime and Corruption Reporting Project's data platform. Cross-jurisdictional company and individual records from dozens of countries. The primary source for offshore entity mapping.

**OpenCorporates** — The largest open database of corporate entities globally. Over 200 million companies across 140+ jurisdictions.

**ICIJ Offshore Leaks** — The searchable database from the Panama Papers, Pandora Papers, Paradise Papers, and related leak investigations.

**Reuters, AP, Bloomberg** — Wire services with established fact-checking standards and legal accountability for published claims.

### The Wayback Machine as Evidence Tool

The Internet Archive's Wayback Machine is underused as an investigative resource and overused as a novelty.

Used correctly, the Wayback Machine answers a specific and important question: *what did this institution say about this topic before the story broke?*

Corporations, government agencies, and public officials change their websites. Statements that were convenient to make before an incident are removed after it. Policies that were claimed to be longstanding are quietly revised. The Wayback Machine preserves the version history.

The investigative protocol: before the subject of an investigation can claim their current stated position has "always been" their position, the Wayback Machine record is checked. If their website said something different six months ago, that's a contradiction. If their FAQ was updated in the week after the incident, that's a timeline data point.

Archived pages are downloadable, timestamped, and citable.

---

## The Watchlist System

The AXIOM watchlist is a curated list of entities under active monitoring for violations and enforcement actions. The system periodically queries relevant databases for new records related to watchlisted entities and adds new findings to the investigation queue.

Current monitored databases:

**SEC Enforcement** — Enforcement actions, litigation releases, administrative proceedings. When the SEC charges a company or individual, the enforcement database is updated.

**EPA Penalties** — ECHO enforcement database. Environmental enforcement actions, penalty amounts, compliance schedules.

**OSHA Violations** — Inspection records, citation data, penalty assessments, abatement status.

**CFPB Actions** — Consumer Financial Protection Bureau enforcement database. Consumer finance violations, restitution orders.

**FTC Enforcement** — Federal Trade Commission actions. Antitrust, privacy, deceptive practices.

**NLRB Charges** — National Labor Relations Board unfair labor practice charges. Includes charges, complaints, settlements.

The watchlist system converts passive monitoring into active investigation triggers. When a new enforcement action appears against a watchlisted entity, AXIOM automatically generates a scoped investigation lead and adds it to the queue.

This is how AXIOM finds stories that nobody is actively looking for — by systematically watching the databases where violations are recorded and flagging anomalies for human review.

---

## The Public Records Strategy

FOIA — the Freedom of Information Act — is one of the most powerful investigative tools available to journalists, and one of the most systematically underused.

The common failure mode: journalists file FOIA requests reactively, after a story has broken, to fill in gaps. The AxiomZero approach is proactive: FOIA as a prospecting tool, filed in advance of any specific story, to surface documents that might generate leads.

### The AXIOM FOIA Protocol

**Map the agency jurisdiction first.** Before filing, determine which agency or agencies hold the relevant records. For environmental violations, EPA ECHO shows which region has jurisdiction. For immigration proceedings, determine whether you need USCIS, ICE, EOIR, or CBP records. Filing to the wrong component wastes time.

**Be specific about document type.** Vague requests get vague responses (and maximum fee estimates). Specific requests — "all emails between [named official] and [named lobbyist] between [date range] regarding [specific rule]" — get targeted document sets.

**Use FOIA.gov to track existing releases.** Many records have already been released to other requesters. Searching the existing FOIA library before filing avoids duplicating work already done.

**State news media fee waiver requests.** Established news organizations are entitled to reduced or waived fees. Always request waiver and cite the public interest basis.

**Follow the appeal process.** Initial denials are not final. FOIA appeals are underused by journalists and overused by government agencies as delay tactics. The administrative appeal is required before judicial review, but judicial review is available and has a track record of overturning improper withholding.

### State Records

Every state has a public records law, and they vary significantly in scope and exemptions. Some state records laws are broader than federal FOIA. State corporate registration records, state court records, state environmental enforcement records, and state contractor records are often not accessible through federal databases and require state-specific requests.

AXIOM maintains a reference database of state records law provisions and the relevant state agencies for each data type.

---

## The Source Trust Scoring System in Practice

Understanding why the scoring works as it does requires understanding what each tier of source actually represents.

A **court document** (Tier 1, 0.95) was produced under oath, reviewed by legal counsel on both sides of an adversarial proceeding, and accepted by a federal judge as a legitimate filing. The information it contains may be disputed — that's what litigation is — but the document itself is real, its provenance is verifiable, and the claims it contains were made under legal penalty for perjury.

A **ProPublica investigation** (Tier 2, 0.80) was produced by journalists with FOIA access, editorial review, legal review, and institutional reputational accountability. ProPublica publishes corrections. Its methodology is documented. Its editors are identifiable.

An **anonymous tip** (Tier 5, 0.30) may come from someone with direct knowledge of wrongdoing, or from someone with an agenda, or from someone who misunderstood what they observed, or from someone who fabricated it entirely. There is no way to know which without corroboration. The score reflects the prior probability that an anonymous tip, before corroboration, accurately represents the underlying facts.

The scoring system does not tell you whether to believe a claim. It tells you how much verification work remains before the claim is publishable. A Tier 5 claim scoring 0.30 is not worthless — it is a lead. It needs corroboration from a Tier 1 or Tier 2 source before it can appear in a published story attributed to more than "an anonymous source."

---

## From Lead to Brief: What the Workflow Actually Looks Like

A journalist submits a lead: *"Senator Jane Smith sits on the Banking Committee and received $450,000 from financial industry PACs in the last cycle. Her voting record shows no votes against any financial industry bill in four years. Is there a story here?"*

AXIOM runs the conflict-of-interest template:

1. **FEC query** — Retrieves the actual contribution records, amounts, dates, and PAC names
2. **OpenSecrets query** — Cross-references with lobbying disclosure; identifies which financial companies lobbied the Banking Committee during the same period
3. **GovTrack query** — Retrieves the full voting record on all relevant bills
4. **EDGAR query** — Checks whether any named companies made disclosures related to regulatory benefit from Banking Committee actions during the period
5. **News archive query** — Retrieves press statements by the Senator on financial regulation
6. **Statement comparison** — The Fact Checker compares voting record against press statements

Output: An investigation brief. The FEC records are CONFIRMED (Tier 1, multiple filings). The vote-contribution correlation is CORROBORATED if the statistical analysis holds across enough data points. The implication of corrupt intent is UNVERIFIED — the data is consistent with it but also consistent with ideological alignment. The steelman notes that the Senator's stated positions on financial regulation predate the PAC contributions.

The journalist now knows what they actually have: confirmed facts, a correlation worth investigating further, an important gap (causation vs. correlation), and specific recommended next steps (request comment from the Senator's office; file FOIA for Banking Committee staff communications with named lobbyists; interview former committee staff).

That is what the document-first methodology produces: not a conclusion, but a precisely characterized state of knowledge with explicit gaps and explicit next steps.

---

*Full source code, derivations, and 15,072 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*AXIOM system: https://github.com/wuzbak/Journalism-*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, AXIOM system, test suites, and document engineering: **GitHub Copilot** (AI).*
