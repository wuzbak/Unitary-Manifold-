// EIGE v21.0 — TypeScript Verification Cockpit Blueprint
// AxiomZero Technologies & Consulting, SPC
//
// REFERENCE BLUEPRINT ONLY — not compiled as part of the Python test suite.
// Intended for Phase 2 Next.js dashboard implementation.
//
// Theory & scientific direction: ThomasCory Walker-Pearson
// Code architecture & synthesis:  GitHub Copilot (AI)

// ---------------------------------------------------------------------------
// Core type definitions
// ---------------------------------------------------------------------------

export type ClosureStatus = "STABLE" | "DRIFTED" | "VIOLATED";

export interface CountyTelemetry {
  county_id: number;
  ballot_count: number;
  phi_eff: number;
  k_cs: number;
  primary_hash: string;    // hex-encoded SHA-512
  hmac_signature: string;  // hex-encoded HMAC-SHA-256
  timestamp_ms: number;
  closure_status: ClosureStatus;
}

export interface HolonZeroCert {
  cert_id: string;
  state_hash: string;
  phi_verified: boolean;
  k_cs_verified: boolean;
  proof_status: ClosureStatus;
  issued_at: string;       // ISO-8601
  county_count: number;
  engine_version: string;
}

export interface OverrideDossier {
  schema_version: "OSCAL-1.5.0";
  system_id: string;
  timestamp: string;       // ISO-8601
  operator_id: string;
  hardware_id: string;
  action_type: "ADMINISTRATIVE_OVERRIDE";
  phi_observed: number;
  phi_expected: number;
  k_cs_observed: number;
  k_cs_expected: 74;
  drift_value: number;
  metric_status: ClosureStatus;
  nist_controls_triggered: string[];
  escalation_required: boolean;
}

// ---------------------------------------------------------------------------
// Constants (mirrors constants.py)
// ---------------------------------------------------------------------------

export const K_CS = 74 as const;
export const PHI_0 = Math.PI / 4;
export const PHI_TOLERANCE = 1e-15;
export const PHI_DRIFT_WARNING = 1e-12;
export const ENGINE_VERSION = "EIGE-v21.0.0";

// ---------------------------------------------------------------------------
// Client-side metric closure check (lightweight, mirrors metric_closure.py)
// ---------------------------------------------------------------------------

export function checkMetricClosure(
  phi_eff: number,
  k_cs: number
): ClosureStatus {
  const delta = Math.abs(phi_eff - PHI_0);
  const k_cs_match = k_cs === K_CS;

  if (delta <= PHI_TOLERANCE && k_cs_match) return "STABLE";
  if (delta <= PHI_DRIFT_WARNING && k_cs_match) return "DRIFTED";
  return "VIOLATED";
}

// ---------------------------------------------------------------------------
// API client (wraps the Python EIGE REST endpoints)
// ---------------------------------------------------------------------------

const API_BASE = process.env.NEXT_PUBLIC_EIGE_API_URL ?? "https://eige.wa.gov/api/v1";

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`EIGE API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export async function fetchCountyTelemetry(
  county_id: number
): Promise<CountyTelemetry> {
  return apiGet<CountyTelemetry>(`/county/${county_id}/telemetry`);
}

export async function fetchAllCountyTelemetry(): Promise<CountyTelemetry[]> {
  return apiGet<CountyTelemetry[]>("/state/telemetry");
}

export async function fetchLatestHolonZeroCert(): Promise<HolonZeroCert> {
  return apiGet<HolonZeroCert>("/federal/cert/latest");
}

export async function fetchOverrideDossiers(
  since_ms?: number
): Promise<OverrideDossier[]> {
  const qs = since_ms != null ? `?since_ms=${since_ms}` : "";
  return apiGet<OverrideDossier[]>(`/sentinel/dossiers${qs}`);
}

// ---------------------------------------------------------------------------
// Real-time WebSocket feed (county metric updates)
// ---------------------------------------------------------------------------

export type TelemetryHandler = (update: CountyTelemetry) => void;

export function subscribeToStateFeed(
  onUpdate: TelemetryHandler,
  onError?: (err: Event) => void
): () => void {
  const WS_URL = (process.env.NEXT_PUBLIC_EIGE_WS_URL ?? "wss://eige.wa.gov/ws") + "/state-feed";
  const ws = new WebSocket(WS_URL);

  ws.onmessage = (evt) => {
    try {
      const payload = JSON.parse(evt.data as string) as CountyTelemetry;
      onUpdate(payload);
    } catch {
      // silently skip malformed frames
    }
  };

  if (onError) ws.onerror = onError;

  // Return unsubscribe handle
  return () => ws.close();
}

// ---------------------------------------------------------------------------
// VerificationCockpit React component
// ---------------------------------------------------------------------------

import React, { useEffect, useState, useCallback } from "react";

interface CockpitProps {
  refreshIntervalMs?: number;
}

interface CockpitState {
  telemetry: CountyTelemetry[];
  cert: HolonZeroCert | null;
  dossiers: OverrideDossier[];
  loading: boolean;
  error: string | null;
  lastUpdatedMs: number;
}

export function VerificationCockpit({
  refreshIntervalMs = 5_000,
}: CockpitProps): React.ReactElement {
  const [state, setState] = useState<CockpitState>({
    telemetry: [],
    cert: null,
    dossiers: [],
    loading: true,
    error: null,
    lastUpdatedMs: 0,
  });

  const refresh = useCallback(async () => {
    try {
      const [telemetry, cert, dossiers] = await Promise.all([
        fetchAllCountyTelemetry(),
        fetchLatestHolonZeroCert(),
        fetchOverrideDossiers(),
      ]);
      setState((prev) => ({
        ...prev,
        telemetry,
        cert,
        dossiers,
        loading: false,
        error: null,
        lastUpdatedMs: Date.now(),
      }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : "Unknown error",
      }));
    }
  }, []);

  useEffect(() => {
    void refresh();
    const interval = setInterval(() => void refresh(), refreshIntervalMs);
    return () => clearInterval(interval);
  }, [refresh, refreshIntervalMs]);

  // Real-time WebSocket overlay
  useEffect(() => {
    const unsub = subscribeToStateFeed((update) => {
      setState((prev) => {
        const updated = prev.telemetry.map((t) =>
          t.county_id === update.county_id ? update : t
        );
        return { ...prev, telemetry: updated, lastUpdatedMs: Date.now() };
      });
    });
    return unsub;
  }, []);

  if (state.loading) return <div className="eige-loading">Loading EIGE telemetry…</div>;
  if (state.error) return <div className="eige-error">Error: {state.error}</div>;

  const violatedCounties = state.telemetry.filter((t) => t.closure_status === "VIOLATED");
  const driftedCounties = state.telemetry.filter((t) => t.closure_status === "DRIFTED");
  const stableCounties = state.telemetry.filter((t) => t.closure_status === "STABLE");

  return (
    <main className="eige-cockpit">
      <header className="eige-header">
        <h1>AxiomZero EIGE v21.0 — Sovereign Elections Integrity</h1>
        <p>Washington State Elections Integrity Monitoring Dashboard</p>
        <p className="eige-timestamp">
          Last updated: {new Date(state.lastUpdatedMs).toISOString()}
        </p>
      </header>

      {/* Federal ZK Certificate Status */}
      {state.cert && (
        <section className="eige-federal-cert">
          <h2>Federal Holon Zero Certificate</h2>
          <table>
            <tbody>
              <tr><td>Status</td><td className={`status-${state.cert.proof_status.toLowerCase()}`}>{state.cert.proof_status}</td></tr>
              <tr><td>φ₀ Verified</td><td>{state.cert.phi_verified ? "✅" : "❌"}</td></tr>
              <tr><td>k_CS=74 Verified</td><td>{state.cert.k_cs_verified ? "✅" : "❌"}</td></tr>
              <tr><td>Counties Covered</td><td>{state.cert.county_count}</td></tr>
              <tr><td>Issued At</td><td>{state.cert.issued_at}</td></tr>
              <tr><td>Cert ID</td><td><code>{state.cert.cert_id.substring(0, 16)}…</code></td></tr>
            </tbody>
          </table>
        </section>
      )}

      {/* Summary Counts */}
      <section className="eige-summary">
        <div className="eige-stat stable">
          <span>{stableCounties.length}</span>
          <label>STABLE Counties</label>
        </div>
        <div className="eige-stat drifted">
          <span>{driftedCounties.length}</span>
          <label>DRIFTED Counties</label>
        </div>
        <div className="eige-stat violated">
          <span>{violatedCounties.length}</span>
          <label>VIOLATED Counties</label>
        </div>
      </section>

      {/* County telemetry table */}
      <section className="eige-county-table">
        <h2>County Telemetry ({state.telemetry.length} nodes)</h2>
        <table>
          <thead>
            <tr>
              <th>County ID</th>
              <th>Ballots</th>
              <th>φ_eff</th>
              <th>k_CS</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {state.telemetry.map((t) => (
              <tr key={t.county_id} className={`status-${t.closure_status.toLowerCase()}`}>
                <td>{t.county_id}</td>
                <td>{t.ballot_count.toLocaleString()}</td>
                <td><code>{t.phi_eff.toFixed(18)}</code></td>
                <td>{t.k_cs}</td>
                <td><strong>{t.closure_status}</strong></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* Override dossiers */}
      {state.dossiers.length > 0 && (
        <section className="eige-dossiers">
          <h2>⚠️ Override Dossiers ({state.dossiers.length})</h2>
          {state.dossiers.map((d, i) => (
            <article key={i} className="eige-dossier">
              <p><strong>Timestamp:</strong> {d.timestamp}</p>
              <p><strong>Operator:</strong> {d.operator_id}</p>
              <p><strong>Hardware:</strong> {d.hardware_id}</p>
              <p><strong>Metric Status:</strong> <span className={`status-${d.metric_status.toLowerCase()}`}>{d.metric_status}</span></p>
              <p><strong>Controls Triggered:</strong> {d.nist_controls_triggered.join(", ")}</p>
              <p><strong>Escalation Required:</strong> {d.escalation_required ? "YES" : "No"}</p>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}
