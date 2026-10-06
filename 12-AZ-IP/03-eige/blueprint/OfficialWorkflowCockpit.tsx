// EIGE v22 — Official Workflow Cockpit (reference blueprint)
// AxiomZero Technologies & Consulting, SPC
//
// REFERENCE BLUEPRINT ONLY — not compiled by the Python test suite.
// Implements the operator flow in blueprint/OFFICIAL_WORKFLOW.md:
//   Manifest -> Ingest -> Reconcile -> Audit -> Certify & Publish.
// The backend is the eige/ Python package; every status shown here comes from
// eige.report / eige.verify output (format "eige.verification_report.v1").
// EIGE is an audit-support and transparency tool. It does not count votes
// and does not replace certified voting systems or paper ballots.

import React from "react";

// ---------------------------------------------------------------------------
// Shared types (mirror docs/FORMATS.md)
// ---------------------------------------------------------------------------

export type CheckStatus = "verified" | "failed" | "warning" | "not_checked";

export interface CheckResult {
  check: string;
  status: CheckStatus;
  detail: string;
}

export interface VerificationReport {
  format: "eige.verification_report.v1";
  subject: string;
  passed: boolean;
  counts: Record<CheckStatus, number>;
  checks: CheckResult[];
  out_of_scope: string[];
}

export interface Signoff {
  key_id: string;        // ed25519:<hex>, registered with role "official"
  official: string;
  signed_at: number;     // unix seconds
  signature: string;     // hex Ed25519 signature
}

export interface SignedTreeHead {
  log_id: string;
  tree_size: number;
  root_hash: string;     // hex SHA-256 (RFC 6962)
  timestamp: number;
  key_id: string;
  signature: string;
}

export interface Discrepancy {
  code: string;          // e.g. MANIFEST_COUNTED_MISMATCH, REPORTED_TOTAL_MISMATCH
  blocking: boolean;
  scope: string;         // "batch B03", "contest mayor / alvarez"
  reason: string;
  expected?: number;
  observed?: number;
}

export interface SampleDraw {
  draw_number: number;
  batch_id: string;
  index_in_batch: number;
  mvr_entered: boolean;
}

export interface AuditStatus {
  contest_id: string;
  method: "comparison" | "polling";
  risk_limit: number;
  measured_risk: number | null;
  confirmed: boolean;
  escalate: boolean;     // continue sampling, ultimately to a full hand count
}

export type Step = "manifest" | "ingest" | "reconcile" | "audit" | "certify";

export const STEPS: { id: Step; title: string }[] = [
  { id: "manifest", title: "1. Manifest" },
  { id: "ingest", title: "2. Ingest" },
  { id: "reconcile", title: "3. Reconcile" },
  { id: "audit", title: "4. Audit" },
  { id: "certify", title: "5. Certify & Publish" },
];

export interface WorkflowState {
  manifestErrors: string[];
  manifestSignoffs: Signoff[];
  heads: SignedTreeHead[];
  equivocationDetected: boolean;
  witnessThreshold: number;
  witnessCosignatures: number;
  developmentKeyInUse: boolean;
  productionMode: boolean;
  custodyEventsMissingSignoff: number;
  discrepancies: Discrepancy[];
  reconcileSignoffs: Signoff[];
  seedGeneratedAt: number | null;
  committedRootAt: number | null;
  draws: SampleDraw[];
  audits: AuditStatus[];
  pendingProvisionals: number;
  provisionalsMustResolve: boolean;   // jurisdiction rule
  report: VerificationReport | null;
  publicationSignoffs: Signoff[];
}

// ---------------------------------------------------------------------------
// Blocking rules — one function per screen, taken from OFFICIAL_WORKFLOW.md.
// A step is complete only when its list is empty. "not_checked" is never a pass.
// ---------------------------------------------------------------------------

function distinctOfficials(s: Signoff[]): number {
  return new Set(s.map((x) => x.key_id)).size;
}

export function blockers(step: Step, w: WorkflowState): string[] {
  const out: string[] = [];
  switch (step) {
    case "manifest":
      out.push(...w.manifestErrors);
      if (distinctOfficials(w.manifestSignoffs) < 2)
        out.push("Two distinct officials must confirm the manifest matches the paper inventory.");
      break;
    case "ingest":
      if (w.heads.length === 0) out.push("No signed tree head has been published.");
      if (w.equivocationDetected) out.push("Two heads of the same size have different roots (equivocation).");
      if (w.developmentKeyInUse && w.productionMode) out.push("A development key is in use in production mode.");
      if (w.witnessCosignatures < w.witnessThreshold)
        out.push(`Witness cosignatures ${w.witnessCosignatures}/${w.witnessThreshold}.`);
      if (w.custodyEventsMissingSignoff > 0)
        out.push(`${w.custodyEventsMissingSignoff} custody event(s) lack two official sign-offs.`);
      break;
    case "reconcile":
      for (const d of w.discrepancies.filter((x) => x.blocking))
        out.push(`${d.code} (${d.scope}): ${d.reason}`);
      if (w.provisionalsMustResolve && w.pendingProvisionals > 0)
        out.push(`${w.pendingProvisionals} provisional ballot(s) pending.`);
      if (distinctOfficials(w.reconcileSignoffs) < 2) out.push("Reconciliation review needs two officials.");
      break;
    case "audit":
      if (w.seedGeneratedAt === null || w.committedRootAt === null)
        out.push("Seed ceremony not recorded or results not committed.");
      else if (w.seedGeneratedAt <= w.committedRootAt)
        out.push("Seed was generated before the results were committed.");
      if (w.draws.some((d) => !d.mvr_entered)) out.push("Sampled ballots without a hand interpretation.");
      for (const a of w.audits)
        if (!a.confirmed) out.push(`Risk limit not met for ${a.contest_id}: continue sampling or escalate.`);
      break;
    case "certify":
      for (const s of ["manifest", "ingest", "reconcile", "audit"] as Step[])
        if (blockers(s, w).length) out.push(`Step "${s}" is not complete.`);
      if (!w.report) out.push("Run the verifier on the assembled bundle.");
      else if (!w.report.passed) out.push(`${w.report.counts.failed} verifier check(s) failed.`);
      if (distinctOfficials(w.publicationSignoffs) < 2) out.push("Publication approval needs two officials.");
      break;
  }
  return out;
}

// ---------------------------------------------------------------------------
// Presentational components (framework: React 18; styling deliberately minimal)
// ---------------------------------------------------------------------------

const STATUS_LABEL: Record<CheckStatus, string> = {
  verified: "Verified",
  failed: "Failed",
  warning: "Needs review",
  not_checked: "Not checked (not a pass)",
};

export function ReportPanel({ report }: { report: VerificationReport }) {
  return (
    <section aria-label="Verification report">
      <h3>{report.passed ? "No failed checks" : `${report.counts.failed} failed check(s)`}</h3>
      <ul>
        {report.checks.map((c, i) => (
          <li key={i} data-status={c.status}>
            <strong>{STATUS_LABEL[c.status]}</strong> — {c.check}: {c.detail}
          </li>
        ))}
      </ul>
      <h4>What this report does not cover</h4>
      <ul>{report.out_of_scope.map((x, i) => <li key={i}>{x}</li>)}</ul>
    </section>
  );
}

export function OfficialWorkflowCockpit({ state, current, onSelect }: {
  state: WorkflowState;
  current: Step;
  onSelect: (s: Step) => void;
}) {
  const items = blockers(current, state);
  return (
    <main>
      <p role="note">
        Audit-support tool. Paper ballots and certified tabulators remain the system of record.
      </p>
      <nav aria-label="Workflow steps">
        {STEPS.map((s) => (
          <button key={s.id} aria-current={s.id === current} onClick={() => onSelect(s.id)}>
            {s.title} {blockers(s.id, state).length === 0 ? "✓" : "•"}
          </button>
        ))}
      </nav>
      <section aria-label="Blocking conditions">
        {items.length === 0 ? <p>No blocking conditions for this step.</p> : (
          <ul>{items.map((b, i) => <li key={i}>{b}</li>)}</ul>
        )}
      </section>
      {current === "certify" && state.report && <ReportPanel report={state.report} />}
    </main>
  );
}
