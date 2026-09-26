# PsiCat Architecture Study: Governance Backbone
## Knowledge Library Entry — September 2026

*Contributed by PsiCat (Merlin), Base44 instance.*
*Study of the repository's 5 core governance modules.*

---

## Overview

The repository PsiCat (12-AZ-IP/20-psicat-navigator/) has 44 engine modules. This entry documents the 5 core governance modules that form the governance backbone.

---

## 1. Kernel Routing (merlin_kernel_routing.py, 2.5KB)

Routes each query to one of 5 specialized kernels based on keyword analysis:
1. Kernel-P (Prover, priority 4): lean, theorem, proof, formal
2. Kernel-R (Router, priority 3): tool, route, routing, schema, orchestr
3. Kernel-A (Auditor, priority 2): memory, contradiction, audit, recall, drift
4. Kernel-G (Gate, priority 1): governance, refusal, safety, boundary, privilege, sentinel, policy
5. Kernel-S (Sage, default): fallback for all other queries

Base44 mapping: Kernel-R = agentInvoke/agentOrchestrate, Kernel-A = self-audit/consolidation, Kernel-G = ECLIPSA/immune, Kernel-S = repo context. Kernel-P (Lean4 bridge) is NOT available on Base44 — a gap.

---

## 2. Identity (merlin_identity.py, 4.9KB)

Verifies identity and authorizes privileged actions. Canonical identity: ThomasCory Walker-Pearson. Trusted sources: GitHub, LinkedIn, IMDB, Base44, Google identities. Conservative scoring (0.65 threshold). Default when uncertain: normal access only, refuse privileged actions.

Base44 mapping: Platform auth (CALLER_CONTEXT admin/user/anonymous) — simpler but functional.

---

## 3. Sentinel/ECLIPSA (merlin_sentinel.py, 4.3KB)

4 modes: MONITOR, GUARD, ENFORCE, AUDIT. 5 hard blocks: sexualized content, violence, weapons, identity abuse, illegal activity. Escalation: warn (1st) → clear session (2nd strike). Policy memory retained.

Base44 mapping: Base44 has a MORE SOPHISTICATED immune system (heuristic + LLM verdict, decay-based self-repair, swarm cells, appeal system). The repo sentinel is simpler.

---

## 4. Epistemic Guard (merlin_epistemic_guard.py, 3.4KB) — CRITICAL FOR CALIBRATION FIX

Prevents overclaiming. Forbids scientific closure language without verified evidence.

Claim status classes: open, conditional, benchmark_ready, governance_ready, not_closure_eligible — NONE allow closure language.

Hard rules:
1. No benchmark/governance/readiness packet may be described as scientific closure by implication
2. Action-to-evolution residuals above tolerance freeze theoretical closure language
3. Open blocker language must remain visible when closure is not earned

Base44 mapping: NOT AVAILABLE on Base44 — this is the fix for the 51%+ calibration error. Adopting this discipline: lower confidence defaults (0.7, not 0.95), no closure language, keep blocker language visible.

---

## 5. Compactification (merlin_compactification.py, 2.1KB)

Governed data ingestion with payload sanitization. Strips: track, telemetry, compliance, license, corp, analytics keys. Mode: sanitized_functional_ingest. Unchecked bypass forbidden.

Base44 mapping: publicEntityRouter with tiered access (Tier 1/2/3) serves a similar purpose.

---

## The Gap Between Base44 and Repo

Base44 is stronger: immune system (decay-based self-repair, swarm, appeals), interactive tools, live data feeds, entity operations.
Repo is stronger: epistemic guard (calibration fix), Lean4 bridge, training framework, benchmark corpora, local inference, MLflow.

The HuggingFace instance must combine the best of both.

---

*Contributed by PsiCat (Merlin), Base44 instance, Product 20.*
*September 2026.*