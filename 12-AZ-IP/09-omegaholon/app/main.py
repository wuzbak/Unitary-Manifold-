#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""
app/main.py — OmegaHolon: The Living Systems Engine
====================================================
A personal life coherence platform that applies the Unitary Manifold's
mathematical framework (holon completeness + omega synthesis) to daily life.

"Your life is a holon — a complete system and a part of something larger.
 The same mathematics that describes the universe also describes you."

Run:
    python run.py          # launches at http://localhost:7871

Tabs:
    1. Profile         — name, load or create
    2. Life Holon      — epistemic audit of your 5 domains
    3. Daily Pulse     — 5-domain daily check-in (scored + tracked)
    4. Decision Oracle — decision resonance analysis
    5. Omega Report    — full synthesis: score, grade, stability, gaps
    6. History         — longitudinal tracking dashboard

Theory: ThomasCory Walker-Pearson. Implementation: GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import gradio as gr

from app.engine.holon import DomainStatus, HolonAudit, LifeDomain
from app.engine.omega import (
    C_S, K_CS, N_2, N_W, XI_C,
    DailyPulse, DecisionOption, OmegaPersonalReport,
    coherence_grade, omega_score, stability_floor,
)
from app.db import tracker as db

# ---------------------------------------------------------------------------
# Init DB
# ---------------------------------------------------------------------------
db.init_db()

# ---------------------------------------------------------------------------
# In-memory session state
# ---------------------------------------------------------------------------
_state: dict = {
    "profile_id": None,
    "profile_name": "",
    "audit": None,
    "pulse": None,
    "decisions": [],
}


def _profile_id() -> int | None:
    return _state["profile_id"]


# ---------------------------------------------------------------------------
# Shared constants for UI dropdowns
# ---------------------------------------------------------------------------
DOMAIN_NAMES  = [d.value for d in LifeDomain]
STATUS_NAMES  = [s.value for s in DomainStatus]
IMPACT_VALUES = {
    "+2 — Significantly beneficial": 2,
    "+1 — Slightly beneficial":      1,
    " 0 — Neutral":                  0,
    "-1 — Slightly harmful":        -1,
    "-2 — Significantly harmful":   -2,
}


# ---------------------------------------------------------------------------
# Tab 1 — Profile
# ---------------------------------------------------------------------------

def load_profile(name: str) -> tuple[str, str]:
    name = name.strip()
    if not name:
        return "❌ Enter your name.", ""
    pid = db.get_or_create_profile(name)
    _state["profile_id"] = pid
    _state["profile_name"] = name
    _state["audit"] = HolonAudit(name=name)

    # Try to restore last audit
    audits = db.list_audits(pid, limit=1)
    if audits:
        last = audits[0]
        return (
            f"✅ Welcome back, **{name}**! (Profile #{pid})\n"
            f"Last audit: {last['recorded_at'][:10]} | Ω Score: {last['omega_score']:.4f}",
            _omega_summary_quick(),
        )
    return (
        f"✅ Profile created: **{name}** (#{pid})\n"
        "Start with the **Life Holon** tab to audit your 5 domains.",
        "",
    )


def _omega_summary_quick() -> str:
    pid = _profile_id()
    if pid is None:
        return ""
    audits = db.list_audits(pid, limit=1)
    if not audits:
        return "_No audit history yet._"
    a = audits[0]
    grade = coherence_grade(a["omega_score"])
    return (
        f"**Last Omega Score:** {a['omega_score']:.4f}  \n"
        f"**Grade:** {grade}  \n"
        f"**Stability:** {a['stability']:.4f} | **φ_trust:** {a['phi_trust']:.4f}"
    )


def list_all_profiles() -> str:
    profiles = db.list_profiles()
    if not profiles:
        return "_No profiles yet._"
    lines = ["**Existing Profiles**\n", "| # | Name | Created |", "|---|------|---------|"]
    for p in profiles:
        lines.append(f"| {p['id']} | {p['name']} | {p['created_at'][:10]} |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tab 2 — Life Holon Audit
# ---------------------------------------------------------------------------

def set_domain(domain_name: str, status_name: str,
               phi_trust: float, description: str,
               foundations: str, constraints: str,
               gaps_str: str, falsifiers_str: str) -> str:
    if _profile_id() is None:
        return "❌ Load your profile first (Tab 1)."
    audit: HolonAudit = _state["audit"]
    if audit is None:
        audit = HolonAudit(name=_state["profile_name"])
        _state["audit"] = audit

    domain = next((d for d in LifeDomain if d.value == domain_name), LifeDomain.BODY)
    status = next((s for s in DomainStatus if s.value == status_name), DomainStatus.ESTIMATED)

    gaps = [g.strip() for g in gaps_str.split("\n") if g.strip()]
    falsifiers = [f.strip() for f in falsifiers_str.split("\n") if f.strip()]

    audit.set_domain(
        domain, status, phi_trust, description.strip(),
        foundations.strip(), constraints.strip(), gaps, falsifiers,
    )
    return f"✅ **{domain_name}** → {status.emoji} {status_name}  φ_trust={phi_trust:.2f}\n\n" + _audit_md()


def _audit_md() -> str:
    audit: HolonAudit | None = _state.get("audit")
    if audit is None or not audit.domains:
        return "_No domains audited yet. Set each domain above._"
    return audit.render_certificate()


def save_audit_now() -> str:
    pid = _profile_id()
    if pid is None:
        return "❌ Load your profile first."
    audit: HolonAudit | None = _state.get("audit")
    if not audit or not audit.domains:
        return "❌ Complete at least one domain audit first."
    report = OmegaPersonalReport(audit=audit)
    data = json.dumps(audit.completeness_certificate(), ensure_ascii=False)
    db.save_audit(pid, report.score, report.stability, report.phi_trust, data)
    return (
        f"✅ Audit saved!\n\n"
        f"**Ω Score:** {report.score:.4f}  \n"
        f"**Grade:** {report.grade}  \n"
        f"**Stability:** {report.stability:.4f}  \n"
        f"**φ_trust:** {report.phi_trust:.4f}  \n"
        f"{'✅ Trust sufficient' if report.trust_ok else '⚠ φ_trust below C_S ≈ 0.324 — authenticity gap'}"
    )


def refresh_audit() -> str:
    return _audit_md()


# ---------------------------------------------------------------------------
# Tab 3 — Daily Pulse
# ---------------------------------------------------------------------------

def record_pulse(body: float, mind: float, work: float,
                 relations: float, resources: float, notes: str) -> str:
    pid = _profile_id()
    if pid is None:
        return "❌ Load your profile first."

    pulse = DailyPulse(date=date.today().isoformat())
    pulse.set(LifeDomain.BODY,      body)
    pulse.set(LifeDomain.MIND,      mind)
    pulse.set(LifeDomain.WORK,      work)
    pulse.set(LifeDomain.RELATIONS, relations)
    pulse.set(LifeDomain.RESOURCES, resources)
    _state["pulse"] = pulse

    db.save_pulse(
        pid, pulse.date, body, mind, work, relations, resources,
        notes.strip(), pulse.daily_omega,
    )

    n = pulse.n_aligned
    sf = stability_floor(n)
    grade = coherence_grade(pulse.daily_omega)

    return (
        f"✅ Pulse recorded for {pulse.date}\n\n"
        f"**Overall:** {pulse.overall:.1f}/10  \n"
        f"**Daily Ω:** {pulse.daily_omega:.4f}  \n"
        f"**Grade:** {grade}  \n"
        f"**Aligned domains (≥7):** {n}  \n"
        f"**Stability floor:** {sf:.4f}  \n\n"
        + _pulse_history_md()
    )


def _pulse_history_md() -> str:
    pid = _profile_id()
    if pid is None:
        return ""
    rows = db.list_pulses(pid, limit=14)
    if not rows:
        return "_No pulse history yet._"
    lines = [
        "**Recent Pulses (last 14 days)**\n",
        "| Date | Body | Mind | Work | Relations | Resources | Ω |",
        "|------|------|------|------|-----------|-----------|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['date']} | {r['body']:.0f} | {r['mind']:.0f} | "
            f"{r['work']:.0f} | {r['relations']:.0f} | {r['resources']:.0f} | "
            f"{r['daily_omega']:.3f} |"
        )
    return "\n".join(lines)


def refresh_pulse_history() -> str:
    return _pulse_history_md()


# ---------------------------------------------------------------------------
# Tab 4 — Decision Oracle
# ---------------------------------------------------------------------------

def analyze_decision(question: str,
                     opt_a_name: str, opt_a_desc: str,
                     body_a: str, mind_a: str, work_a: str, rel_a: str, res_a: str,
                     trust_a: float,
                     opt_b_name: str, opt_b_desc: str,
                     body_b: str, mind_b: str, work_b: str, rel_b: str, res_b: str,
                     trust_b: float,
                     opt_c_name: str, opt_c_desc: str,
                     body_c: str, mind_c: str, work_c: str, rel_c: str, res_c: str,
                     trust_c: float) -> str:
    if _profile_id() is None:
        return "❌ Load your profile first."
    audit: HolonAudit | None = _state.get("audit")
    if not audit or not audit.domains:
        return "❌ Complete your Life Holon audit first (Tab 2) — the Decision Oracle needs your domain state."

    def _impacts(b, m, w, r, rs) -> dict[str, int]:
        return {
            LifeDomain.BODY.value:      IMPACT_VALUES.get(b, 0),
            LifeDomain.MIND.value:      IMPACT_VALUES.get(m, 0),
            LifeDomain.WORK.value:      IMPACT_VALUES.get(w, 0),
            LifeDomain.RELATIONS.value: IMPACT_VALUES.get(r, 0),
            LifeDomain.RESOURCES.value: IMPACT_VALUES.get(rs, 0),
        }

    options: list[DecisionOption] = []
    for name, desc, b, m, w, r, rs, trust in [
        (opt_a_name, opt_a_desc, body_a, mind_a, work_a, rel_a, res_a, trust_a),
        (opt_b_name, opt_b_desc, body_b, mind_b, work_b, rel_b, res_b, trust_b),
        (opt_c_name, opt_c_desc, body_c, mind_c, work_c, rel_c, res_c, trust_c),
    ]:
        if name.strip():
            options.append(DecisionOption(
                name=name.strip(),
                description=desc.strip(),
                domain_impacts=_impacts(b, m, w, r, rs),
                phi_trust_impact=float(trust),
            ))

    if not options:
        return "❌ Enter at least one option name."

    _state["decisions"] = options

    report = OmegaPersonalReport(audit=audit, decision_options=options)
    ranked = sorted(options, key=lambda o: o.resonance_with(audit), reverse=True)

    pid = _profile_id()
    if pid:
        db.save_decision(pid, question.strip(),
                         json.dumps([o.to_dict() for o in options]))

    divider = "─" * 56
    lines = [
        f"**Decision Analysis: {question.strip()}**\n",
        divider,
        "",
        "**Resonance Ranking** (higher = better aligned with your life)**",
        "",
    ]
    for i, opt in enumerate(ranked, 1):
        r = opt.resonance_with(audit)
        bar_len = int(r * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        lines.append(f"**[{i}] {opt.name}**")
        lines.append(f"    `{bar}` {r:.3f}")
        if opt.description:
            lines.append(f"    _{opt.description}_")
        lines.append("")
        # Show domain breakdown
        for domain in LifeDomain:
            impact = opt.domain_impacts.get(domain.value, 0)
            da = audit.get_domain(domain)
            if da is None:
                continue
            impact_str = {2: "++", 1: " +", 0: " ·", -1: " −", -2: "−−"}.get(impact, " ·")
            lines.append(f"    {impact_str}  {da.status.emoji} {domain.value}")
        lines.append("")

    # Interpretation
    best = ranked[0]
    best_r = best.resonance_with(audit)
    lines.append(divider)
    if best_r >= 0.65:
        lines.append(f"✅ **{best.name}** resonates strongly with your current life state.")
    elif best_r >= 0.45:
        lines.append(f"〰️ **{best.name}** has moderate resonance — consider the domain impacts carefully.")
    else:
        lines.append(f"⚠ No option resonates strongly. Consider waiting, gathering more information, or reframing the decision.")
    lines.append("")
    lines.append("_Remember: The Oracle scores alignment with your current state._")
    lines.append("_The highest-resonance choice is not always the right choice — you are the judge._")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tab 5 — Omega Report
# ---------------------------------------------------------------------------

def generate_omega_report() -> str:
    if _profile_id() is None:
        return "❌ Load your profile first (Tab 1)."
    audit: HolonAudit | None = _state.get("audit")
    pulse: DailyPulse | None = _state.get("pulse")
    decisions: list[DecisionOption] = _state.get("decisions", [])

    if not audit and not pulse:
        return "❌ Complete a Life Holon audit or Daily Pulse before generating the Omega Report."

    report = OmegaPersonalReport(
        audit=audit,
        pulse=pulse,
        decision_options=decisions,
    )
    return report.render_report()


# ---------------------------------------------------------------------------
# Tab 6 — History
# ---------------------------------------------------------------------------

def _history_md() -> str:
    pid = _profile_id()
    if pid is None:
        return "_Load your profile first._"

    audits = db.list_audits(pid, limit=10)
    pulses = db.list_pulses(pid, limit=10)
    commitments = db.list_commitments(pid)

    lines = []

    if audits:
        lines += [
            "### 📊 Audit History",
            "",
            "| Date | Ω Score | Grade | Stability | φ_trust |",
            "|------|---------|-------|-----------|---------|",
        ]
        for a in audits:
            grade = coherence_grade(a["omega_score"])[:1]
            lines.append(
                f"| {a['recorded_at'][:10]} | {a['omega_score']:.4f} | {grade} "
                f"| {a['stability']:.4f} | {a['phi_trust']:.4f} |"
            )
        lines.append("")

    if pulses:
        lines += [
            "### 💓 Pulse History",
            "",
            "| Date | Body | Mind | Work | Rel | Res | Daily Ω |",
            "|------|------|------|------|-----|-----|---------|",
        ]
        for p in pulses:
            lines.append(
                f"| {p['date']} | {p['body']:.0f} | {p['mind']:.0f} | "
                f"{p['work']:.0f} | {p['relations']:.0f} | {p['resources']:.0f} | "
                f"{p['daily_omega']:.3f} |"
            )
        lines.append("")

    if commitments:
        lines += ["### 🔬 Active Commitments (Falsifiable)", ""]
        for c in commitments:
            lines.append(f"- [{c['domain']}] {c['commitment']}")
        lines.append("")

    if not lines:
        lines = ["_No history yet. Complete audits and daily pulses to see trends._"]

    return "\n".join(lines)


def refresh_history() -> str:
    return _history_md()


def add_commitment(domain_name: str, commitment: str) -> str:
    pid = _profile_id()
    if pid is None:
        return "❌ Load your profile first."
    commitment = commitment.strip()
    if not commitment:
        return "❌ Commitment text is required."
    db.save_commitment(pid, domain_name, commitment)
    return f"✅ Commitment saved: [{domain_name}] {commitment}"


# ---------------------------------------------------------------------------
# Build the Gradio UI
# ---------------------------------------------------------------------------

IMPACT_CHOICES = list(IMPACT_VALUES.keys())
IMPACT_DEFAULT = " 0 — Neutral"

HEADER_HTML = """
<div style="background:linear-gradient(135deg,#0d1117,#1a1f2e);padding:20px 28px;border-radius:10px;margin-bottom:16px;border:1px solid #30363d">
  <h2 style="color:#c9d1d9;margin:0;font-size:1.5em">
    <span style="color:#58a6ff">Ω</span> OmegaHolon — The Living Systems Engine
  </h2>
  <p style="color:#8b949e;margin:6px 0 0 0;font-size:0.95em">
    <em>Your life is a holon — a complete system and a part of something larger.<br>
    The same mathematics that describes the universe also describes you.</em>
  </p>
  <p style="color:#6e7681;margin:4px 0 0 0;font-size:0.82em">
    N_W={nw} domains · N_2={n2} days · K_CS={kcs} complexity · C_S={cs:.4f} threshold · Ξ_c={xic:.4f} coupling
  </p>
</div>
""".format(nw=N_W, n2=N_2, kcs=K_CS, cs=C_S, xic=XI_C)


def build_ui() -> gr.Blocks:
    with gr.Blocks(
        title="OmegaHolon — Living Systems Engine",
        theme=gr.themes.Base(
            primary_hue="blue",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
        ),
        css="footer { display: none !important; }",
    ) as demo:
        gr.HTML(HEADER_HTML)

        with gr.Tabs():

            # ─────────────────────────────────────────
            # Tab 1: Profile
            # ─────────────────────────────────────────
            with gr.Tab("👤 Profile"):
                gr.Markdown("### Your Profile\nAll data is stored locally. Your profile persists between sessions.")
                with gr.Row():
                    p_name    = gr.Textbox(label="Your Name", placeholder="e.g. Alex")
                    btn_load  = gr.Button("Load / Create Profile", variant="primary")
                p_status  = gr.Markdown()
                p_summary = gr.Markdown()
                btn_load.click(load_profile, [p_name], [p_status, p_summary])

                gr.Markdown("---")
                btn_profiles = gr.Button("Show All Profiles")
                p_all = gr.Markdown()
                btn_profiles.click(list_all_profiles, [], p_all)

                gr.Markdown("""
### How It Works

OmegaHolon applies the mathematical framework of the Unitary Manifold to your personal life.

**The Five Domains (Pentad mapping):**

| Domain | Pentad Body | What it covers |
|--------|-------------|----------------|
| 🫀 Body & Health | Ψ_brain | Sleep, nutrition, movement, physical energy |
| 🧠 Mind & Emotion | Ψ_human | Mental clarity, emotional state, learning |
| 💼 Work & Purpose | Ψ_AI | Career, creative output, purpose-alignment |
| 🤝 Relationships & Trust | Ψ_trust | Relationships, community, integrity |
| 🌍 Resources & Environment | Ψ_univ | Finances, material stability, environment |

**The Math:**
- `stability_floor(n) = min(1.0, C_S + n × C_S / N_2)` — how many aligned domains → how stable you are
- `omega_score = stability_floor × average_resonance` — your single coherence number
- `phi_trust < C_S ≈ 0.324` → authenticity gap (the system decouples)

**The Cycle:**
1. **Audit** your five domains quarterly (Life Holon tab)
2. **Pulse** daily (5-domain check-in)
3. **Analyze** decisions through your holon (Decision Oracle)
4. **Review** your Omega Report for the full picture
""")

            # ─────────────────────────────────────────
            # Tab 2: Life Holon Audit
            # ─────────────────────────────────────────
            with gr.Tab("🔭 Life Holon Audit"):
                gr.Markdown("""
### Life Holon Audit

Rate each of your 5 domains with honest epistemic status — like a physicist auditing the Standard Model.

**Status meanings:**
- ✅ **SOLID** — Well-founded; actively maintained; you know what you're doing here
- ⚙️ **CONSTRAINED** — Working within real limits; aware of the tradeoffs
- 〰️ **ESTIMATED** — Roughly on track; needs more attention or data
- 🔓 **OPEN** — Unresolved; broken; requires urgent attention
""")
                with gr.Row():
                    h_domain = gr.Dropdown(DOMAIN_NAMES, label="Domain", value=DOMAIN_NAMES[0])
                    h_status = gr.Dropdown(STATUS_NAMES, label="Status", value="ESTIMATED")
                    h_trust  = gr.Slider(0.0, 1.0, value=0.7, step=0.05,
                                         label="φ_trust — Authenticity/Integrity (0=false, 1=completely authentic)")
                h_desc  = gr.Textbox(label="Current State", lines=2,
                                     placeholder="Describe what's actually happening in this domain right now.")
                h_found = gr.Textbox(label="Foundations", lines=2,
                                     placeholder="What is this domain built on? What's working?")
                h_const = gr.Textbox(label="Real Constraints", lines=2,
                                     placeholder="What real limits are you working within? (financial, time, health, etc.)")
                h_gaps  = gr.Textbox(label="Open Gaps (one per line)", lines=3,
                                     placeholder="What's unresolved?\nWhat keeps you up at night?\nWhat are you avoiding?")
                h_fals  = gr.Textbox(label="Falsifiable Commitments (one per line)", lines=2,
                                     placeholder="What would prove your current strategy wrong?\ne.g. 'If I miss 3 workouts in a row, the plan needs to change.'")
                btn_set = gr.Button("✅ Set Domain Status", variant="primary")
                out_domain = gr.Markdown()
                btn_set.click(set_domain,
                              [h_domain, h_status, h_trust, h_desc, h_found, h_const, h_gaps, h_fals],
                              out_domain)

                gr.Markdown("---")
                with gr.Row():
                    btn_save_audit   = gr.Button("💾 Save Audit to History", variant="secondary")
                    btn_refresh_audit = gr.Button("🔄 Refresh Certificate")
                out_save = gr.Textbox(label="Save Status", interactive=False, lines=6)
                btn_save_audit.click(save_audit_now, [], out_save)
                btn_refresh_audit.click(refresh_audit, [], out_domain)

            # ─────────────────────────────────────────
            # Tab 3: Daily Pulse
            # ─────────────────────────────────────────
            with gr.Tab("💓 Daily Pulse"):
                gr.Markdown(f"""
### Daily Pulse Check-In

Rate each domain from **0–10** for today. Takes 60 seconds.

The pulse feeds your **Daily Ω score** (a quick coherence snapshot).
Domains scoring **≥7** count as "aligned" for the stability floor calculation.

`stability_floor(n) = min(1.0, {C_S:.4f} + n × {C_S:.4f} / {N_2})`
""")
                with gr.Row():
                    p_body    = gr.Slider(0, 10, value=7, step=0.5, label="🫀 Body & Health")
                    p_mind    = gr.Slider(0, 10, value=7, step=0.5, label="🧠 Mind & Emotion")
                with gr.Row():
                    p_work    = gr.Slider(0, 10, value=7, step=0.5, label="💼 Work & Purpose")
                    p_rel     = gr.Slider(0, 10, value=7, step=0.5, label="🤝 Relationships & Trust")
                p_res     = gr.Slider(0, 10, value=7, step=0.5, label="🌍 Resources & Environment")
                p_notes   = gr.Textbox(label="Today's Note (optional)", lines=2,
                                       placeholder="One sentence: what's the texture of today?")
                btn_pulse = gr.Button("📡 Record Today's Pulse", variant="primary", size="lg")
                out_pulse = gr.Markdown()
                btn_pulse.click(record_pulse,
                                [p_body, p_mind, p_work, p_rel, p_res, p_notes],
                                out_pulse)

                gr.Markdown("---")
                btn_hist_p = gr.Button("🔄 Refresh Pulse History")
                out_pulse_hist = gr.Markdown()
                btn_hist_p.click(refresh_pulse_history, [], out_pulse_hist)
                demo.load(refresh_pulse_history, [], out_pulse_hist)

            # ─────────────────────────────────────────
            # Tab 4: Decision Oracle
            # ─────────────────────────────────────────
            with gr.Tab("🔮 Decision Oracle"):
                gr.Markdown("""
### Decision Resonance Oracle

The Oracle analyzes how well each decision option resonates with your current life holon.

**How it works:**
- Options that improve your OPEN domains get the highest weight
- Options that harm your SOLID domains are penalized
- phi_trust impact is scaled by the consciousness coupling constant (Ξ_c ≈ 0.473)

**Input your decision and up to 3 options. Rate each domain impact -2 to +2.**

> ⚠ The Oracle is an alignment tool, not an authority. You are the judge.
""")
                d_question = gr.Textbox(label="The Decision", placeholder="e.g. Should I accept the job offer in another city?")

                gr.Markdown("**Option A**")
                with gr.Row():
                    da_name = gr.Textbox(label="Option A Name", placeholder="Accept the offer")
                    da_desc = gr.Textbox(label="Description", placeholder="Move city, higher salary, new team")
                with gr.Row():
                    da_body = gr.Dropdown(IMPACT_CHOICES, label="Body impact", value=IMPACT_DEFAULT)
                    da_mind = gr.Dropdown(IMPACT_CHOICES, label="Mind impact", value=IMPACT_DEFAULT)
                    da_work = gr.Dropdown(IMPACT_CHOICES, label="Work impact", value=IMPACT_DEFAULT)
                with gr.Row():
                    da_rel  = gr.Dropdown(IMPACT_CHOICES, label="Relations impact", value=IMPACT_DEFAULT)
                    da_res  = gr.Dropdown(IMPACT_CHOICES, label="Resources impact", value=IMPACT_DEFAULT)
                    da_trust = gr.Slider(-0.3, 0.3, value=0.0, step=0.05, label="φ_trust impact")

                gr.Markdown("**Option B**")
                with gr.Row():
                    db_name = gr.Textbox(label="Option B Name", placeholder="Decline, stay")
                    db_desc = gr.Textbox(label="Description", placeholder="Stay in current role")
                with gr.Row():
                    db_body = gr.Dropdown(IMPACT_CHOICES, label="Body impact", value=IMPACT_DEFAULT)
                    db_mind = gr.Dropdown(IMPACT_CHOICES, label="Mind impact", value=IMPACT_DEFAULT)
                    db_work = gr.Dropdown(IMPACT_CHOICES, label="Work impact", value=IMPACT_DEFAULT)
                with gr.Row():
                    db_rel  = gr.Dropdown(IMPACT_CHOICES, label="Relations impact", value=IMPACT_DEFAULT)
                    db_res  = gr.Dropdown(IMPACT_CHOICES, label="Resources impact", value=IMPACT_DEFAULT)
                    db_trust = gr.Slider(-0.3, 0.3, value=0.0, step=0.05, label="φ_trust impact")

                gr.Markdown("**Option C (optional)**")
                with gr.Row():
                    dc_name = gr.Textbox(label="Option C Name", placeholder="Negotiate remote")
                    dc_desc = gr.Textbox(label="Description")
                with gr.Row():
                    dc_body = gr.Dropdown(IMPACT_CHOICES, label="Body impact", value=IMPACT_DEFAULT)
                    dc_mind = gr.Dropdown(IMPACT_CHOICES, label="Mind impact", value=IMPACT_DEFAULT)
                    dc_work = gr.Dropdown(IMPACT_CHOICES, label="Work impact", value=IMPACT_DEFAULT)
                with gr.Row():
                    dc_rel  = gr.Dropdown(IMPACT_CHOICES, label="Relations impact", value=IMPACT_DEFAULT)
                    dc_res  = gr.Dropdown(IMPACT_CHOICES, label="Resources impact", value=IMPACT_DEFAULT)
                    dc_trust = gr.Slider(-0.3, 0.3, value=0.0, step=0.05, label="φ_trust impact")

                btn_oracle = gr.Button("🔮 Analyze Decision", variant="primary", size="lg")
                out_oracle = gr.Markdown()
                btn_oracle.click(
                    analyze_decision,
                    [d_question,
                     da_name, da_desc, da_body, da_mind, da_work, da_rel, da_res, da_trust,
                     db_name, db_desc, db_body, db_mind, db_work, db_rel, db_res, db_trust,
                     dc_name, dc_desc, dc_body, dc_mind, dc_work, dc_rel, dc_res, dc_trust],
                    out_oracle,
                )

            # ─────────────────────────────────────────
            # Tab 5: Omega Report
            # ─────────────────────────────────────────
            with gr.Tab("Ω Omega Report"):
                gr.Markdown("""
### Full Omega Personal Report

The complete synthesis: your Omega Score, stability floor, phi_trust status,
domain breakdown, today's pulse, decision rankings, and falsifiable commitments.

Mirrors the `UniversalEngine.compute_all()` report from the Unitary Manifold.
""")
                btn_report = gr.Button("Ω Generate Omega Report", variant="primary", size="lg")
                out_report = gr.Textbox(label="Omega Personal Report", lines=40, interactive=False)
                btn_report.click(generate_omega_report, [], out_report)

            # ─────────────────────────────────────────
            # Tab 6: History
            # ─────────────────────────────────────────
            with gr.Tab("📈 History"):
                gr.Markdown("### Longitudinal Tracking\nYour audit history, pulse trends, and active commitments.")
                btn_refresh_hist = gr.Button("🔄 Refresh History")
                out_hist = gr.Markdown()
                btn_refresh_hist.click(refresh_history, [], out_hist)
                demo.load(refresh_history, [], out_hist)

                gr.Markdown("---\n### Add a Falsifiable Commitment\n*A commitment you can test — something that would prove your current strategy wrong.*")
                with gr.Row():
                    com_domain = gr.Dropdown(DOMAIN_NAMES, label="Domain", value=DOMAIN_NAMES[0])
                    com_text   = gr.Textbox(label="Commitment", placeholder="If I haven't started exercise 3x/week by month's end, the plan needs to change.")
                btn_commit  = gr.Button("🔬 Add Commitment")
                out_commit  = gr.Textbox(label="", interactive=False)
                btn_commit.click(add_commitment, [com_domain, com_text], out_commit)

        gr.Markdown("""
---
*OmegaHolon — The Living Systems Engine* | AxiomZero Technologies  
*Theory, framework: ThomasCory Walker-Pearson. Implementation: GitHub Copilot (AI).*  
*Mathematics rooted in the Unitary Manifold (N_W=5, K_CS=74, C_S=12/37, Ξ_c=35/74).*
""")

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch(
        server_name="0.0.0.0",
        server_port=7871,
        share=False,
        inbrowser=True,
    )
