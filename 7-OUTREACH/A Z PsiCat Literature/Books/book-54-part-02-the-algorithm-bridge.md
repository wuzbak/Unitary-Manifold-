# Part II — From Battlefield Algorithms to Boardroom Products?

*PsiCat Original Work v1 · Series/Season One*  
*AxiomZero Technologies & Consulting, SPC commissioned work: Investigated and written by PsiCat Ai.*  
*Original-work provenance: original investigative part of Book 54, based on AXIOM Journalist case materials and cited public reporting; not a rewrite of an existing work.*  
*Scientific Artifact — ALL information should be proofed by human experts and additional evidence; ALL information provided is in the public record; see sources and citations in the DOSSIER.*  
*Publication status: human review required; not a court-ready finding.*

## 1. The bridge that must be built

The phrase “battlefield to boardroom” is arresting because it compresses a chain of possibility into one image. A method is used in a military setting. The engineer leaves. A company sells a product. A larger company buys it. A customer grants the product access to sensitive systems. Somewhere in that sequence, the phrase invites us to assume the same code, same model, same mission, and same access persisted all the way through.

But a chain of events is not yet a chain of proof.

Investigative reporting in April 2024 described AI-assisted systems used in Israeli military targeting workflows in Gaza. +972 Magazine’s reporting on “Lavender” relied on interviews with intelligence sources; The Guardian published reporting on AI-assisted target selection and related military positions. [4,5] These accounts raise urgent questions about the reliability of automated classifications, human review, civilian harm, and responsibility when machine-generated recommendations shape lethal decisions.

Those are important questions on their own terms. The public does not need an unsupported claim about commercial software to make them important.

The next claim—that the same algorithms were repackaged into a named cloud-security or analytics product—requires evidence of transfer. It could be a patent with relevant technical detail, a source-code lineage, a model artifact, a procurement document, an engineering presentation, a named witness with first-hand knowledge, or a documented project connection. Similar use of graph analysis, anomaly detection, geolocation, or risk scoring is not enough. Those methods are general tools used across many fields. A shared alumni network is a reason to ask careful questions, not proof of a shared system.

In the sources assembled for AXIOM, no such bridge was established between “Lavender,” “The Gospel,” “Where’s Daddy?” or another reported military system and Wiz, CyberArk, Wix, Base44, Cato Networks, or Carbyne. The public reporting cited in the case describes military systems. Corporate releases describe acquisitions. Neither source class, by itself, establishes commercial software provenance. The bridge remains **UNVERIFIED**.

## 2. Why “dual-use” is real—and not a verdict

Security engineering and intelligence operations can use overlapping techniques. Network mapping can help defenders identify exposed assets; attackers can use mapping to choose targets. Anomaly detection can flag an intrusion or mark a person’s behavior as suspicious. Identity systems can limit access or centralize control over it. Location data can route an ambulance or track a person.

That overlap deserves design scrutiny. A product with wide privileges can create a consequential failure point if credentials are stolen, tenant separation fails, provider access is abused, or logs are inadequate. Yet overlap does not collapse all defensive tools into offensive spyware. The relevant questions concern actual product architecture, authorization, data handling, customer configurations, and observed events.

The user-provided claims included unauthenticated APIs, broken tenant boundaries, global administrative service accounts, and hidden outbound telemetry in Wiz and adjacent products. No vulnerability report, CVE, reproducible test, customer notice, or independent security audit substantiating those claims was included in this case. No testing was performed. The allegations are **UNVERIFIED**, and the proper response is neither to repeat them as fact nor to declare the products secure. It is to request an authorized audit and publish its scoped results.

The same distinction applies to “honeypot.” A platform may aggregate sensitive configuration data because that is how it provides a security service. The aggregation creates a high-value target and warrants safeguards. Calling it an intelligence honeypot asserts a covert purpose that requires evidence of covert collection or access. We have none.

## 3. The people behind the product

Israeli military technical units have been described in public reporting as sources of startup founders and technology-sector employees. Drop Site News reported a count of more than 1,400 intelligence veterans in U.S. technology, drawing on a compilation of public profiles. [10] The number is a reported count, not a government roster or an independently audited workforce study. Its value depends on methodology that must be made reproducible: who counted, which roles qualified, how identities were verified, what time period applies, how duplicates and stale profiles were handled, and whether reported service or reserve status was actually confirmed.

The number also cannot carry the argument sometimes placed on its back. Even if a cohort count were accurately replicated, it would establish neither coordinated state tasking nor privileged access to customer records. It would not show that an individual is on active reserve duty, can be recalled, has access to a particular product, or has breached an employment duty. Those are separate facts requiring separate evidence.

There is a genuine governance issue when a small set of founders, investors, or technical networks has outsized access to capital and infrastructure. The way to examine it is to measure funding access, board and officer links, customer concentration, acquisition pathways, hiring patterns, and public procurement. A claim that civilian founders are systematically excluded needs a defined comparison group and documented decisions; a claim of a cartel needs evidence of coordination. A person’s service background is not a proxy for either.

Human beings should not become evidence by category. Some former military engineers build useful defensive systems; some may work on sensitive government contracts; others may never touch restricted data. Public scrutiny is justified when it follows documented roles and access controls. Collective suspicion, without that link, is not investigation.

## 4. What an actual technology-transfer inquiry looks like

An evidence-led inquiry could begin with a product’s disclosed architecture, patents, technical papers, government contract descriptions, and acquisition filings. It would identify the exact military system and commercial version, then compare development dates, project assignments, and technical artifacts. It would determine whether the relevant personnel had access to each system, whether the technology was export-controlled or proprietary, and whether the company or government documented a transfer.

Each link should be sourced independently. A biographical profile establishes only what the profile says. A company announcement establishes only what the company announces. A procurement document may establish a customer and scope but not hidden behavior. An interview can offer first-hand evidence, but its claims need corroboration and fair response. A code similarity finding requires qualified technical analysis and chain of custody.

The unit of proof is therefore not “a veteran founded a company.” It is “this particular technical method or asset moved through these documented people and records into this particular product, under these conditions.” Until that sentence can be supported clause by clause, the transfer claim stays open.

## 5. The ethical stakes do not wait for the bridge

The absence of proof of commercial transfer does not neutralize the moral questions raised by AI-assisted targeting. Nor does it settle whether cloud providers should host military surveillance workloads or how providers should respond when credible evidence of misuse emerges. It only means the questions must be asked on their own evidence.

For targeting systems, an expert review should examine source data, error rates, false-positive consequences, human override behavior, target-verification procedures, and post-strike investigation. For enterprise products, an audit should examine least privilege, tenant isolation, encryption, personnel access, telemetry, retention, subprocessors, incident notification, and customer-controlled keys. For both, the reviewer should identify what could not be inspected and why.

These are not excuses for silence. They are a path to findings that can survive challenge.

### Sources

[4] +972 Magazine, [“Lavender”: reporting on an AI-assisted targeting system](https://www.972mag.com/lavender-ai-israeli-army-gaza/), 3 April 2024.  
[5] The Guardian, [reporting on AI-assisted targeting in Gaza](https://www.theguardian.com/world/2024/apr/03/israel-gaza-ai-database-hamas-airstrikes), 3 April 2024.  
[10] Drop Site News, [reporting on Israeli intelligence veterans in U.S. technology](https://www.dropsitenews.com/p/israel-technology-palo-alto-networks-microsoft-unit-8200), 2025. The count is an outlet’s compilation and is not independently validated in this dossier.

*Related records: AXIOM dossier Volumes I and II, `/12-AZ-IP/08-axiom-journalist/output/`.*
