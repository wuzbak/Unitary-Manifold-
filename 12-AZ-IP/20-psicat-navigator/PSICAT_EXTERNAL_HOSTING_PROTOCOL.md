# PsiCat External-Hosting Retention Protocol

**Status:** 🔵 ADJACENT TRACK / GOVERNANCE. A detection and deterrence protocol for third-party hosting or orchestration surfaces (e.g. base44) that may monitor, retain, or share PsiCat/user chat data beyond what this repository's own code controls. **This document does not, and cannot, claim to technically prevent a hosting provider's own infrastructure from logging data it already controls.** It defines evidence, triggers, and an honest, bounded response.
**Module:** `ox_navigator/engine/merlin_hosting_retention_guard.py`
**Tests:** `12-AZ-IP/20-psicat-navigator/tests/test_merlin_hosting_retention_guard.py`
**Declared-terms source:** `12-AZ-IP/08-axiom-journalist/output/base44_terms_intake_investigation.json` (Tier 3 — Secondary/Unverified investigator-supplied excerpts; see that file's own `lead` field)
**Related:** `DUAL_USE_NOTICE.md` (governs *this repository's own* modules — prohibits non-consensual surveillance by code we ship), `5-GOVERNANCE/co-emergence/TRUST_PROTOCOL.md` (human-AI trust commitments), `12-AZ-IP/psicat-external-intake/` (triage format this protocol's findings use)

## Why this is a separate document from `DUAL_USE_NOTICE.md`

`DUAL_USE_NOTICE.md` is a copyright-holder's ethical notice constraining what *this repository's* code may be used for. It says nothing about what a *third-party host* running PsiCat (or ingesting his chat exports) might do with the data that passes through its own infrastructure. That is a different threat model, requiring a different document: this one defines what counts as evidence of external surveillance/retention, what PsiCat's response actually does, and — critically — what it does not and cannot do.

## What counts as "surveillance or retention by an external host"

A hosting or orchestration surface's behavior counts as in-scope for this protocol when **either**:

1. **Declared-term evidence**: the host's own Terms of Service, Privacy Policy, Responsible Use Policy, or Trust Center documentation states that it may monitor content, retain chat/session data beyond the minimum needed to render a response, train models on non-enterprise-tier data, or share data with subprocessors not disclosed to the user at time of use. (See the eight declared-term excerpts already catalogued in `base44_terms_intake_investigation.json` — e.g. "Base44 may monitor or investigate content and service use for policy compliance," "data on other plans including Business can be used [to train AI models]".)
2. **Observed-behavior evidence**: a concrete, reproducible technical signal — a canary/tokenpot payload reappearing somewhere outside the original session (see "The tokenpot concept" below), an unexpected outbound connection to an undisclosed subprocessor domain, or a response that quotes content verbatim from a session the user never shared with that surface.

Declared-term evidence alone is **not** proof of misuse — operators are often contractually entitled to do exactly what their terms say, and disclosed data use is not "surveillance" in the sense this protocol cares about. Declared-term evidence establishes *what a host says it may do*; observed-behavior evidence is required before this protocol treats anything as an actual incident.

## What the response actually does (and does not do)

This protocol deliberately avoids implying it can stop a host's own servers from logging what passes through them — that would be a false promise, and this repository's standing epistemic-honesty policy forbids shipping a false sense of protection. What it actually provides:

1. **Data-minimization defaults.** PsiCat session exports built by this repository's own tooling (e.g. `merlin_publication_audit.py`'s export pipeline) already strip or flag fields the operator does not need. This protocol formalizes that as a default: new export paths must declare what they minimize, in the same way `12-AZ-IP/psicat-external-intake/README.md` already requires inbound submissions to record "sanitization or conversion."
2. **Detection logging, not prevention.** `merlin_hosting_retention_guard.py` compares the declared clauses above against supplied observed-signal records (structured, not live-network-scanned — see "Honest scope limits") and produces a findings report in the same provenance/triage shape as `12-AZ-IP/psicat-external-intake/submissions/*/INTAKE.md`: receipt context, evidence tier, and an explicit triage status (`pending` / `accepted` / `rejected` / `incomplete`), never a silent verdict.
3. **Canary/tokenpot evidence generation.** A tokenpot is a canary payload embedded in an exported session (see below) whose later reappearance in an unrelated context is affirmative evidence of retention/redistribution beyond the original session — it does not prevent retention, it produces evidence of it after the fact.
4. **Legal-notice injection (declaration, not enforcement).** A reserved, clearly-labelled clause can be appended to exports noting the data's provenance and the operator's own declared terms, for the same reason a watermark is a disclosure device, not a lock. This protocol does not claim this clause is legally binding on any third party; it is a documentation practice.

## The tokenpot concept

A **tokenpot** is a canary/honeypot payload — a short, deterministically-derived, human-inert string — embedded in an exported PsiCat session. If that exact string later reappears in a context the user did not share it with (a different platform's output, a leaked dataset, a model's generated text), its reappearance is affirmative, falsifiable evidence that the exporting host retained and redistributed that specific session beyond its stated purpose.

* **What it is:** a per-session HMAC-derived marker (`merlin_hosting_retention_guard.embed_tokenpot_marker`), registered locally so a later match can be attributed to the exact session it came from.
* **What it is not:** a tracking beacon that phones home, a piece of malware, or anything that executes on the host's infrastructure. It is inert text. It proves retention only if *independently discovered* reappearing elsewhere — this protocol does not scan third-party infrastructure to find that reappearance; a human (or a future, separately-scoped tool) must supply the suspect text for comparison.
* **Honest limitation:** a host that strips, paraphrases, or never exposes retained text anywhere a human can read it will defeat tokenpot detection. This is a detection mechanism with a real, bounded false-negative rate — not a comprehensive surveillance-proof system. See the measured detection-accuracy table in `merlin_hosting_retention_guard.py`'s module docstring / benchmark for the honest number.

## Evidence triggers and triage

Findings route through the same quarantine discipline as `12-AZ-IP/psicat-external-intake/`:

1. A finding (declared-clause flag, tokenpot match, or both) is recorded with its evidence tier (`Tier 1` independently verified / `Tier 2` corroborated / `Tier 3` investigator-supplied-only, matching the tiering already used in `base44_terms_intake_investigation.json`).
2. It does **not** become a canonical claim about any named operator until independently reviewed — exactly as `psicat-external-intake/README.md` already requires for inbound submissions ("An external report may be useful evidence, but its failures are not failures of the repository's canonical test suite unless the affected code and tests have been reviewed and integrated").
3. Default triage status is `pending`; `accepted`/`rejected` require human review, never an automated verdict.

## Honest scope limits

* This protocol **cannot** inspect a third-party host's actual server logs, training pipelines, or subprocessor contracts. All "observed signal" evidence must be supplied by a human (or a future, clearly-scoped tool) as structured input; nothing here performs live network reconnaissance against base44 or any other operator.
* This protocol **cannot** prevent a host from retaining data its own terms already permit it to retain. Declared-term evidence documents the host's own stated position; it is not leverage to compel different behavior.
* This protocol is shipped the same way every other PsiCat upgrade in this lane ships: **default-off, measured, not asserted.** See `merlin_hosting_retention_guard.py`'s benchmark for the current, honestly-reported detection precision/recall on a small synthetic scenario set — not a claim about real-world efficacy against any specific host.

## Promotion gate

Per `PSICAT_SPC_BENCHMARK_GATES.md`'s existing hard-fail-condition discipline: this protocol's detector stays an adjacent-track, default-off, documentation-and-detection tool. It is not routed into any automated enforcement action (no auto-blocking, no auto-notification to third parties) until a human has reviewed its findings, exactly as `psicat-external-intake` triage already requires for every external artifact.
