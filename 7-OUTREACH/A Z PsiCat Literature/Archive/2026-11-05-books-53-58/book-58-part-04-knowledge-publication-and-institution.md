# Part IV — Knowledge, Publication, and Institution

*PsiCat Original Work v1 · Series/Season One*\
*AxiomZero Technologies & Consulting, SPC commissioned work: Edited and written by PsiCat Ai.*\
*AxiomZero Technologies & Consulting, SPC commissioned work: Investigated and written by PsiCat Ai.*\
*Date: 2026-11-05*\
*Original-work provenance: original commissioned editorial synthesis, researched and produced with Copilot and specialist AI assistance in this repository session; not an inference from or live generation by a deployed Base44/PsiCat system. Repository paths below are primary-source pointers; this narrative does not replace them.*

## E11 — The Repository as a Map of Claims

A repository is not only storage. Its architecture says something about how knowledge is made, checked, and offered to the public. In this monorepo the same roof holds scientific theory, proofs, numerical code, tests, human-AI governance, domain applications, books, websites, product code, policy, and historical records. A reader who treats all of those files as one kind of evidence will miss what makes the repository useful—and risk assigning authority where none was intended.

The central reader task is to travel from question to relevant evidence. What is the current claim? Which source states its assumptions? Where is the implementation? What did the tests actually check? What observation could disconfirm the claim? Which public explanation carries the result to non-specialists? Which document governs the license? Each question has a different best source.

`docs/navigation/REPOSITORY_MAP.md` offers a valuable first map. It distinguishes numbered layers—Theory, Reproducibility, Falsification, Implications, Governance, Monograph, Outreach, Safety, and Infrastructure—from cross-cutting folders such as source, tests, proof, data, claims, tools, archive, and compactification. It also says that current canonical status belongs in current status and fallibility records, while historical and archive files preserve earlier states and do not automatically act as present instructions. The map can orient a reader; it cannot establish that every destination is current or complete.

### Authority is specific to the question

When two documents conflict, do not choose mechanically by date, directory, or prestige. Ask which source is intended to govern this topic. For current scientific status, a current status ledger is more relevant than an earlier popular book. For code behavior, source and test are direct evidence. For an empirical result, an independent measurement or study may be needed. For licensing, the underlying instrument and applicable asset-specific notices matter more than an outreach summary. The newest page is not automatically authoritative, and an older source can remain controlling for a particular file or historical version.

`docs/TRUTH_LAYER.md` illustrates how a current record can change its assessment: claims may be narrowed, formal certificates withdrawn, numerical evidence bounded, or an earlier status superseded. The right response is not to erase the history but to mark it. A reader can value an old document as evidence of what the project once concluded without mistaking it for the present position.

A strong knowledge architecture links layers without collapsing them. A public explanation points to a claim ledger; the ledger points to derivation and data; reproducibility records explain how code ran; falsification materials state what could count against the claim. An internal test does not validate its model's external premises. A proof does not establish that its axioms describe nature. An observation consistent with a prediction does not necessarily establish unique causation. Each file should say what it contributes.

### Retrieval helps find sources; it is not itself a source

Repository search and RAG can save readers substantial time. For this research, a local `RAGIndex.build(repo_root=..., include_psicat_literature=True)` indexed 6,924 chunks. Three searches explored governance, applied human domains, and publishing/licensing. The result lists were used to locate candidate sources, then the primary files were opened and checked directly. Retrieval was a discovery tool; it did not substantiate any claim.

That distinction follows from the implementation. `bot/rag_index.py` describes a keyword-based index whose build method can opt into the PsiCat literary corpus and whose search method ranks matching chunks. A high-ranked result means that words and source weights matched the query; it does not mean the passage is current, authoritative, or correct. A search can surface an old book alongside a current policy. It can identify a useful function name without establishing that its assumptions are empirically valid.

Good AI retrieval should show source path, title, enough surrounding text to inspect meaning, and a route to the original. It should prefer appropriate primary sources when factual claims are requested, distinguish literature from technical documents, and say when evidence is absent or conflicting. If its result informs a medical, legal, or scientific conclusion, the reader must verify the source and scope. The model's summary is not a new authority.

### Accessibility reduces epistemic friction

Knowledge is not meaningfully accessible if only repository insiders can navigate it. Clear headings, plain-language summaries, screen-reader support, alt text, accessible tables, downloadable formats, stable links, and a glossary for project-specific terminology all matter. A technical reader needs source, dependencies, exact commands, and dated run receipts; a public reader needs to understand what a result means and what it does not mean.

The repository's scale creates predictable costs: many generations of files, uneven naming, terms that insiders recognize, and multiple versions of similar material. A newcomer could mistake a product number for validation, a directory for a live deployment, a historic report for a current status, or a test count for empirical evidence. The map helps, but additional stewardship is required: generated inventories, current-status links at points of use, owner and review-date metadata, and explicit maturity labels for products.

A machine-readable catalog could track file purpose, owner, current/historical status, review date, epistemic category, asset type, license pointer, and deployment state. It should be generated or verified against source records and display unknown values instead of inferring them from names or folders. Such a catalog would be a navigation instrument, not an automatic declaration that every file is governed identically.

**Primary-source pointers:** `docs/navigation/REPOSITORY_MAP.md`, “Numbered epistemic layers,” “Cross-cutting folders,” and “Canonical vs historical rule”; `docs/TRUTH_LAYER.md`, current reassessments and verification scope; `bot/rag_index.py`, `RAGIndex.build` and `RAGIndex.search` (approximately lines 1266–1445); `AGENTS.md`, preferred ingest order.

## E12 — From Research to Public Record

Publication is a chain of transformations. An observation becomes data; data enter an analysis; analysis supports a claim; code implements a calculation; a manuscript explains it; an outreach book makes it approachable; a product or website may put it in front of users. At each transition, a qualification can disappear. A result can lose its parameter provenance, a chart its uncertainty, a public summary its epistemic label, and a product page its prototype status.

This repository contains several distinct publishing surfaces, each with a different obligation. `1-THEORY` and `proof` support technical and formal evaluation. `2-REPRODUCIBILITY` stores run materials and reports. `3-FALSIFICATION` makes predictions answerable to potential disconfirmation. `6-MONOGRAPH` and `manuscript` house long-form technical work. `7-OUTREACH` contains books, public explanations, posts, visuals, and editorial standards. `public-site` contains application code rather than proof of a live site. These distinctions make the corpus versatile if links between surfaces are kept current.

### Monographs and manuscripts

A monograph can provide a coherent path through a large research program, but completeness of presentation is not proof of completeness of theory. Each edition needs a date, version, status, and a route to current technical records. Claims should carry relevant caveats where they occur rather than only in a limitations chapter. If a proof status or prediction changes, the monograph should identify its historical snapshot and point to the current source.

Manuscript files can be drafts, preprints, submissions, or post-review versions. A file in `manuscript/` is not automatically a published paper. A reliable record identifies version, intended venue, review status, DOI if one exists, and differences between the manuscript and current code or claim ledger. A bibliography, data appendix, and methods section should be maintained as carefully as the prose.

### Outreach is explanation, not evidence

`7-OUTREACH/README.md` explicitly says that the directory's books and posts are explanations, implications, and reflections for a general audience—not peer-reviewed physics evidence. It routes physics evaluators toward fallibility, derivation status, falsification, and reproducibility. It also distinguishes physics explainers, personal reflections, applied implications, and commissioned books. This is sound editorial architecture, provided each publication repeats the necessary status and source pointers rather than relying on its directory location.

An outreach essay may use analogy, emotion, or narrative to make a difficult concept accessible. It should say where the analogy ends. A personal reflection should not be confused with a scientific conclusion. A product story should distinguish research idea from operational service. A multi-file book should identify its parts, sequence, and scope. A series index should state which files are complete titles, extracts, rewrites, or dated snapshots.

The present Book 58 parts are commissioned editorial syntheses. The requested credit lines name the commission and PsiCat's editorial authorship. The provenance statement clarifies actual production: research in this local repository session with Copilot and specialist AI assistance, not inference by a live, deployed Base44/PsiCat service. This is more than stylistic precision. A system name can otherwise imply a process that did not occur.

### Websites, products, and machine-readable publications

A public website can be more discoverable than a source tree, but it can drift away from the source. It may use a different branch, cached copy, manual edits, or old data. It should identify update date or source revision and link to primary records. Web publishing also adds obligations around accessibility, privacy, security, and support. Interactive tools should say whether inputs are stored, what they do, and whether outputs are demonstrations or validated recommendations.

Product registries and catalogues are useful for discovery. They do not prove a feature is complete, deployed, validated, secure, or regulated. A maturity label—concept, prototype, research preview, maintained release, or retired—helps prevent a menu entry from becoming an implied promise. If a service records user data, its notice should be close to the interaction and explain collection, retention, access, and deletion.

Machine-readable maps, provenance data, RAG indexes, and structured inventories widen access to both humans and agents. They also propagate stale information quickly. Each should identify source, date, scope, generation method, and review status. Public instructions to ingest a corpus do not override the need to protect credentials, private data, sensitive personal information, or third-party rights.

### Reproducible releases

A technical release should connect prose to inputs: commit or release identifier, dataset provenance, code version, dependencies, environment, exact commands, outputs, and exclusions. A figure should link to its script and data where feasible. A test report should say what ran and whether it completed. A failed or partial run is part of the record, not a result to silently omit.

A public release is more than a Git commit. It includes a decision to publish, review of content and rights, source and data versions, safety considerations, and a clear statement about what evidence the release supplies. A link checker proves that tested links resolved; it does not prove that the linked claims are correct. A grammar check can improve prose; it does not verify a scientific statement. Every release check needs a scope.

For researchers, reproducibility may mean reconstructing a numerical result. For public readers, it may mean a transparent path from conclusion to method. Both matter. Neither should be conflated with external replication or empirical confirmation.

**Primary-source pointers:** `7-OUTREACH/README.md`, opening status, contents, standard phrasing, and epistemic notice; `docs/navigation/REPOSITORY_MAP.md`, numbered layers; `6-MONOGRAPH/MCP_INGEST.md` (verify the source's date/status); `docs/TRUTH_LAYER.md`, current correction record; `public-site/` (inspect the specific application and deployment status).

## E13 — Legal Boundaries Without Legal Slogans

This is an editorial guide to repository legal sources, not legal advice. It cannot determine rights in an individual file or decide whether a license applies to a particular use. Specific questions require the actual instrument, rights and provenance records, and qualified counsel where appropriate.

### The layered framework

The repository’s `LICENSE`, `LICENSE-AGPL`, and `NOTICE` describe a layered arrangement: a Defensive Public Commons dedication for specified theoretical and other non-software content; AGPL-3.0-or-later for specified copyright-retained software; brand rights; and possible asset-specific notices, upstream terms, third-party components, and prior grants. Thus the statements “everything is public domain,” “everything is AGPL,” “commercial use is forbidden,” or “the license prohibits all patents” are too broad unless the exact asset and controlling text support them.

The root `LICENSE` states a public-domain dedication for covered theoretical content and describes retained software copyright for copyleft enforcement. It also says that the portfolio schedule identifies subject matter but does not expand rights over theoretical content, third-party materials, or assets with different notices or prior grants. A directory cannot, by itself, determine ownership or coverage.

The dated additive clarification `AZ-RECIPROCITY-2026-10-07` is essential to reading earlier summaries. The root `LICENSE` and `NOTICE` say prior grants and valid public-domain dedications are not withdrawn; public-domain status alone does not enforce every anti-enclosure prohibition; standard AGPL terms control over inconsistent summaries; and no mandatory notification, payment, field-of-use restriction, or Washington forum requirement is added to AGPL permissions. `LICENSE-AGPL` similarly says its summaries do not modify official AGPL terms and that network interaction alone is not conveyance. Older blanket formulations should not be repeated without this reconciliation.

`LICENSE-AGPL` identifies a software scope and incorporates the official AGPL-3.0-or-later terms. The full license text is in `LICENSES/AGPL-3.0-or-later.txt`. The AGPL is a free-software copyleft license and permits commercial use subject to its terms; public-license-compliant use does not itself require an exception or an asserted mandatory notification. If a particular distribution or network interaction raises a question, analyze the actual covered work, modifications, interaction, corresponding source, and third-party components. Do not rely on an editorial slogan.

### Portfolio schedules are inventories

`12-AZ-IP/PORTFOLIO_LICENSE_SCHEDULE.md` lists products and registered assets. It explicitly describes itself as an inventory, not a new license or amendment to AGPL. Its scope note says the default applies only to copyright-retained first-party software for which AxiomZero has the necessary rights; asset-specific notices, upstream terms, third-party components, and prior grants remain controlling. This caveat prevents the schedule from being mistaken for a universal rights assignment.

A product entry does not prove operational availability, validation, security, or completeness. A product name and trademark are not a software license. A license is not an empirical claim. A registry can help locate materials, but file-level notices and provenance still matter.

### Attribution for collaborative work

The exact credit lines in these parts are editorial attribution, not a legal conclusion. The provenance note records the actual writing and research process. More generally, AI-assisted work should describe who directed, researched, drafted, edited, reviewed, and approved, without claiming a deployed model was invoked if it was not. An author's credit does not, by itself, settle copyrightability or ownership. The repository's asserted rights allocation should be read with actual agreements and applicable law.

### Practical file-by-file review

For a particular file, identify the exact path and revision; inspect its header and adjacent notice; read the applicable license and full text; check upstream materials, third-party rights, and prior grants; use portfolio inventories as pointers rather than grants; and consult `LEGAL.md` for the consolidated account while following it back to underlying instruments. If sources conflict, do not choose whichever summary is convenient.

This process is not meant to obstruct reuse. It prevents an open repository from overstating restrictions or understating genuine obligations. Openness is stronger when the scope of permission is accurately described.

**Primary-source pointers:** `LICENSE`, public-domain dedication, software copyright scope, and additive clarification (lines 35–117 and 210 onward); `LICENSE-AGPL`, scope and additive clarification; `NOTICE`, dual-license structure and 2026 correction; `LEGAL.md`, opening authority statement and Part X (search policy identifier); `12-AZ-IP/PORTFOLIO_LICENSE_SCHEDULE.md`, scope note; `LICENSES/AGPL-3.0-or-later.txt`.

## E14 — Strengths, Frictions, and Institutional Maturity

The repository's strongest institutional feature is that it provides multiple paths to scrutiny: theory, proof, reproducibility, falsification, source, tests, safety, governance, and public explanation. Its epistemic separation lets the Pentad be considered independently from cosmological truth and lets applied models be read as analogies rather than as physics confirmation. Its archives can preserve corrections and past reasoning. Its executable code lets readers inspect how a formula has been translated into behavior.

Its most obvious cost is scale. There are many directories, products, books, status documents, and naming conventions. Similar names can denote distinct surfaces; an old summary can appear beside a current record; a test result can be misunderstood as domain validation; a product registry can be mistaken for deployment. These are concrete information-architecture problems. The answer is not simply another overview: it is canonical pointers, generated inventories, status metadata, review dates, and explicit maturity labels on public surfaces.

### Institutional independence and accountability

The HILS/Pentad documents offer principles—human intent-control, honesty, distributed authority, dissent, escalation, and appeal. A real institution must make them operational: who may approve; who is affected; how decisions are challenged; what data are logged; how privacy is protected; who investigates incidents; and who can stop a deployment. A software test can verify a quorum or state transition, but not that participants are independent, dissent is safe, or an appeal changes outcomes.

When the same person is author, steward, product owner, and reviewer, internal review can still be useful, but it is not independent review. The institution should state the scope and relationship of reviewers, disclose relevant conflicts, and invite independent domain and community assessment when stakes warrant it. A list of names is not a review receipt; a review of one component is not a review of the entire project.

### Commitments need owners

Open science, responsible AI, accessibility, and environmental stewardship are institutional commitments, not self-verifying labels. They become credible through named owners, published evidence, incident response, and regular review. Who updates current status? Who maintains a product? Who handles a privacy concern? What happens when a deployment ends? Who ensures a correction propagates to books, website, and retrieval?

A public product adds responsibilities that a manuscript does not: support path, privacy practice, security response, accessibility, uptime expectations, and a safe exit when service stops. A repository can remain public while an online application is unavailable; the public should not confuse those facts. A product should state its status and maintenance scope.

The institutional tone need not be triumphant or apologetic. It should say what was built, what was tested, what was independently reviewed, what remains, and who is accountable. A reader should be able to admire implementation and remain skeptical about an empirical claim; value an analogy and question its application; accept the license and still ask about its scope.

**Primary-source pointers:** `5-GOVERNANCE/SEPARATION.md`, test interpretation; `docs/TRUTH_LAYER.md`, current scoped results; `5-GOVERNANCE/co-emergence/TRUST_PROTOCOL.md`, governance safeguards; `LEGAL.md`, corporate and licensing explanations; `12-AZ-IP/PORTFOLIO_LICENSE_SCHEDULE.md`, inventory qualification.

## E15 — Crosswalk of Tracked Top-Level Directory Groups

This inventory records directory groups present in tracked paths at revision `d9efc894947c8b45e584e74ed59ff809d407fb52`. Root files such as `README.md`, `LICENSE`, `LICENSE-AGPL`, `NOTICE`, `Makefile`, and `EIGE` are excluded because they are not directories. “Tracked” does not mean current, complete, deployed, verified, or uniformly licensed.

| Group | Function and reading caution |
|---|---|
| `.dvc` | Data Version Control metadata and pointers; verify payload, version, provenance, access, and license. |
| `.github` | Collaboration and automation configuration; inspect actual workflow receipts, not configuration alone. |
| `1-THEORY` | Theory, derivations, claim records; check current status and evidence for each claim. |
| `11-AZ-OS` | Numbered operating-system/system surface; directory presence is not deployment maturity. |
| `12-AZ-IP` | Product and IP portfolio; schedules are inventories and cannot override asset-specific rights. |
| `2-REPRODUCIBILITY` | Runs and validation artifacts; report exact scope, data, environment, and exclusions. |
| `3-FALSIFICATION` | Predictions and potential refutations; ensure thresholds and status are current. |
| `4-IMPLICATIONS` | Interpretations and applications; not the formal proof gate. |
| `5-GOVERNANCE` | HILS and Pentad material; independence from physics does not prove institutional efficacy. |
| `6-MONOGRAPH` | Monograph and publication support; distinguish drafts, releases, and historical copies. |
| `7-OUTREACH` | Public books, posts, visuals, editorial governance; explanatory writing is not peer-reviewed evidence. |
| `8-SAFETY` | Safety and dual-use materials; consult the specific current notice for the use. |
| `9-INFRASTRUCTURE` | Runtime, scripts, provenance, results; presence does not establish a live service. |
| `ARCHIVE` | Preserved or superseded materials; useful for provenance, not automatically current instructions. |
| `COMPACTIFICATION` | Repository maps and compact-kernel material; not a substitute for current claim assessment. |
| `EIGE` | Tracked governance-engine surface; inspect contents and maturity before inferring deployment. |
| `HISTORICAL-MILESTONES` | Dated history and audits; not present verification. |
| `LICENSES` | Full and auxiliary license texts; match instruments to file-level rights and provenance. |
| `PILLARS` | Pillar-organized materials; numbering does not measure evidentiary strength. |
| `RECOVERY` | Recovery-related material; confirm procedures are current and tested. |
| `TOOLS` | Tool indexes and utilities; inspect exact version, inputs, and output semantics. |
| `az-kernel` | Separate kernel/system code group; review its own source, threat model, and license. |
| `az-os` | AxiomZero OS/platform surface; verify current scope and release status. |
| `az_os` | Differently named OS group; do not assume equivalence with `az-os` or `11-AZ-OS`. |
| `bot` | AI assistant and retrieval infrastructure; outputs aid navigation but do not replace evidence. |
| `claims` | Claim-centered packages; inspect methods and sources rather than relying on directory name. |
| `data` | Data assets; check lineage, sensitivity, license, and transformations. |
| `docs` | Policies, status, navigation, reviews, and operations; select the governing record by topic. |
| `hf-spaces` | Hosted-space/deployment materials; configuration does not prove a live validated service. |
| `lean4` | Formalization; inspect theorem, assumptions, imports, and actual build receipt. |
| `lodge` | Tracked community/institution-facing surface; establish actual purpose and status. |
| `manuscript` | Manuscript source; identify version, submission status, and relation to published work. |
| `proof` | Isolated formal evaluation surface; mathematical proofs do not validate empirical premises. |
| `public-site` | Web application source; separate code from live service and review privacy/accessibility/security. |
| `recycling` | φ-debt accounting implementation/tests; external interpretation needs separate support. |
| `src` | Main Python modules across physics and adjacent domains; per-package epistemic status varies. |
| `terrifying-theories` | Nonstandard named group; inspect actual contents and safety notices before inference. |
| `tests` | Regression suite; verifies assertions under stated assumptions, not external truth. |
| `unitary_manifold` | Package/compatibility surface; verify whether canonical, generated, or legacy. |

This is a navigation crosswalk, not a file-level inventory or legal schedule. Folder names cannot determine rights. The directory architecture's strength is that it creates distinct routes for theory, reproduction, falsification, governance, safety, and public communication; its cost is that readers must work to keep those routes distinct. A generated index coupling paths to owners, status, review dates, evidence class, asset kind, license pointer, and deployment state would reduce that cost. It should show unknowns rather than infer status from a name.

**Primary-source pointers:** `docs/navigation/REPOSITORY_MAP.md`, numbered layers and cross-cutting folders; `docs/TRUTH_LAYER.md`, current status; `LICENSE` and `LICENSE-AGPL`, scope and qualification; `12-AZ-IP/PORTFOLIO_LICENSE_SCHEDULE.md`, inventory boundary.

## E16 — An Integrated Route Through the Monorepo

For a **scientific evaluator**, begin with current claim status, locate the derivation and assumptions, inspect parameter provenance, follow the falsifier, and separate formal closure from observational confirmation.

For a **software engineer**, read the package notice, inspect function behavior and tests, reproduce the narrow result, review dependencies and license, and then assess deployment risks.

For a **policy or institutional reader**, establish intended use and maturity, identify affected people, demand evidence in the target setting, and inspect appeal and accountability.

For a **public reader**, begin with an accessible explainer, but follow its claims to primary records and check date and epistemic label.

For a **contributor or downstream builder**, verify file-specific rights, preserve notices, check upstream dependencies, and record versions and changes.

For an **archivist**, preserve commit identifiers, generated assets, historical status, build context, and corrections so that future readers can reconstruct the path.

These routes recur in four cautions: a path is not a proof; counts do not measure truth; a license summary is not the license; and a human checkpoint is not meaningful oversight unless authority, information, time, and recourse are present.

### One integrated research-to-publication workflow

The repository's strongest elements can be combined into a disciplined sequence:

1. Formulate a bounded question and identify affected people.
2. Record the claim, assumptions, evidence class, alternative explanations, and falsifier.
3. Give code and data provenance; check asset-specific rights.
4. Test implementation behavior and record exact environment and scope.
5. Invite independent methods review and domain-specific input.
6. Bound any pilot, monitor incidents, and keep it stoppable.
7. Publish positive and negative outcomes with dates and exclusions.
8. Write accessible explanation after the technical record and link to it.
9. Update current status and mark superseded material without erasing history.

This is not a certification protocol. It is an integrated working pattern: HILS can clarify how AI contributes; a Pentad-style process can distribute review; a claim ledger can preserve epistemic status; tests can catch software regressions; outside reviewers can assess empirical and human impact. Each part retains its own evidentiary standard.

### What remains

The applied modules need external domain validation before high-stakes use. The Pentad's institutional outcomes need field evaluation. The scientific record must stay synchronized across books, products, and technical status. Public-facing products need maturity and data practices. Legal scope must remain asset-specific and subordinate to actual instruments. Retrieval should distinguish relevance from authority. Accessibility must apply to the codebase and public interfaces.

Those are not reasons to pretend that nothing has been built. The code exists, abstractions can be examined, internal behavior can be tested, and literature can guide new readers. The work remaining is to continue the evidence chain outward: from implementation to validated construct, from proposed process to observed institutional practice, and from publication to accountable public record.

The way back matters. A reader should be able to move from claim to source, source to implementation, implementation to test, and test to a description of what remains unknown. The path should work in reverse too: a test names the behavior it protects; a claim identifies its evidence; a product points to its limits; an AI summary returns to primary documents. The human domains and institutional layers are connected to the research, but they are not all the same kind of proof.

*Editorial gates: (1) Traceability — material repository claims resolve to direct primary sources, with current status or date where relevant; (2) Epistemic discipline — internal implementation, analogy, empirical validation, and external truth remain distinct; (3) Attribution — commissioning, editorial authorship, production assistance, and provenance describe what actually happened. These are editorial checks, not scientific certification, legal advice, or a safety audit.*
