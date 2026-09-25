#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""
app/main.py — AXIOM Investigative Journalist AI
================================================
Gradio-powered investigative journalism research platform.

Run:
    python run.py
    # or
    python -m app.main

Tabs:
    1. New Investigation  — start a case with a lead
    2. Entities           — map people, orgs, agencies
    3. Sources            — log and tier sources
    4. Claims             — add claims with confidence scoring
    5. Brief              — generate the structured investigative brief
    6. Case Library       — browse and reload saved cases

Theory, methodology: ThomasCory Walker-Pearson / AxiomZero Technologies.
Implementation: GitHub Copilot (AI).
"""
from __future__ import annotations
import sys
from pathlib import Path

# Ensure repo root is in path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.core.investigator import (
    ConfidenceLevel, EntityType, Investigation, LegalRisk, Source, SourceTier
)
from app.db import cases as db
from axiom_journalist.engine import (
   build_public_record_queries,
   build_dossier_packet,
   build_story_packet,
   build_psicat_training_packet,
   merge_source_bundle,
   parse_source_bundle,
   public_record_source_catalog,
   render_dossier_html,
   render_dossier_markdown,
   render_story_html,
   render_story_markdown,
   render_psicat_training_markdown,
)

import gradio as gr

# ---------------------------------------------------------------------------
# Initialise database
# ---------------------------------------------------------------------------
db.init_db()

# ---------------------------------------------------------------------------
# In-memory active investigation (single-user desktop app)
# ---------------------------------------------------------------------------
_active: dict[str, Investigation | None] = {"inv": None}


def _inv() -> Investigation | None:
    return _active["inv"]


def _set_inv(inv: Investigation) -> None:
    _active["inv"] = inv


# ---------------------------------------------------------------------------
# Tab 1 — New Investigation
# ---------------------------------------------------------------------------

def new_investigation(title: str, lead: str, journalist: str) -> tuple[str, str]:
    title = title.strip()
    lead = lead.strip()
    if not title or not lead:
        return "❌ Title and Lead are required.", _case_library_md()
    inv = Investigation(title=title, lead=lead, journalist=journalist.strip())
    _set_inv(inv)
    case_id = db.create_case(title, lead, journalist)
    inv._db_id = case_id  # type: ignore[attr-defined]
    return (
        f"✅ Investigation '{title}' started (Case #{case_id}).\n"
        f"Now add Entities, Sources, and Claims.",
        _case_library_md(),
    )


# ---------------------------------------------------------------------------
# Tab 2 — Entities
# ---------------------------------------------------------------------------

ENTITY_TYPES = [e.value for e in EntityType]

def add_entity(name: str, etype: str, description: str, stated_position: str,
               contradiction: str) -> str:
    inv = _inv()
    if inv is None:
        return "❌ Start or load an investigation first."
    name = name.strip()
    if not name:
        return "❌ Entity name is required."
    et = next((e for e in EntityType if e.value == etype), EntityType.OTHER)
    entity = inv.add_entity(name, et, description.strip(), stated_position.strip())
    if contradiction.strip():
        entity.add_contradiction(contradiction.strip())
    if hasattr(inv, "_db_id"):
        db.add_entity(inv._db_id, name, etype, description.strip(), stated_position.strip())
    return f"✅ Entity '{name}' ({etype}) added.\n\n" + _entities_md()


def _entities_md() -> str:
    inv = _inv()
    if inv is None:
        return "_No active investigation._"
    if not inv.entities:
        return "_No entities yet. Add one above._"
    lines = ["**Mapped Entities**\n"]
    for e in inv.entities:
        lines.append(f"- **{e.name}** [{e.entity_type.value}]")
        if e.description:
            lines.append(f"  - {e.description}")
        if e.stated_position:
            lines.append(f"  - Stated: _{e.stated_position}_")
        if e.contradictions:
            for c in e.contradictions:
                lines.append(f"  - ⚠ Contradiction: {c}")
    return "\n".join(lines)


def refresh_entities() -> str:
    return _entities_md()


# ---------------------------------------------------------------------------
# Tab 3 — Sources
# ---------------------------------------------------------------------------

TIER_OPTIONS = {
    "Tier 1 — Primary Record (court/regulatory/FOIA)": SourceTier.TIER_1,
    "Tier 2 — Established/On-Record":                  SourceTier.TIER_2,
    "Tier 3 — Secondary/Unverified":                   SourceTier.TIER_3,
}
TIER_LABELS_LIST = list(TIER_OPTIONS.keys())


def add_source(title: str, tier_label: str, source_type: str,
               url_or_ref: str, date: str, excerpt: str) -> str:
    inv = _inv()
    if inv is None:
        return "❌ Start or load an investigation first."
    title = title.strip()
    if not title:
        return "❌ Source title is required."
    tier = TIER_OPTIONS.get(tier_label, SourceTier.UNCLASSIFIED)
    inv.add_source(title, tier, source_type.strip(), url_or_ref.strip(),
                   date.strip(), excerpt.strip())
    if hasattr(inv, "_db_id"):
        db.add_source(inv._db_id, title, tier.value, source_type.strip(),
                      url_or_ref.strip(), date.strip(), excerpt.strip())
    return f"✅ Source '{title}' logged.\n\n" + _sources_md()


def _sources_md() -> str:
    inv = _inv()
    if inv is None:
        return "_No active investigation._"
    if not inv.sources:
        return "_No sources yet. Add one above._"
    lines = [f"**Sources** (quality score: {inv.source_quality_score:.2f})\n"]
    for s in inv.sources:
        from app.core.investigator import TIER_LABELS
        lines.append(f"- [{TIER_LABELS[s.tier]}] **{s.title}**")
        if s.date:
            lines.append(f"  - Date: {s.date}")
        if s.url_or_ref:
            lines.append(f"  - Ref: {s.url_or_ref}")
        if s.excerpt:
            lines.append(f"  - _\"{s.excerpt[:100]}\"_")
    return "\n".join(lines)


def refresh_sources() -> str:
    return _sources_md()


# ---------------------------------------------------------------------------
# Tab 4 — Claims
# ---------------------------------------------------------------------------

LEGAL_RISK_OPTIONS = [r.value for r in LegalRisk]


def add_claim(statement: str, source_titles_str: str,
              entities_str: str, legal_risk: str, notes: str) -> str:
    inv = _inv()
    if inv is None:
        return "❌ Start or load an investigation first."
    statement = statement.strip()
    if not statement:
        return "❌ Claim statement is required."
    source_titles = [t.strip() for t in source_titles_str.split(",") if t.strip()]
    entities = [e.strip() for e in entities_str.split(",") if e.strip()]
    try:
        lr = LegalRisk(legal_risk)
    except ValueError:
        lr = LegalRisk.NONE
    claim = inv.add_claim(statement, source_titles, entities, [lr])
    if hasattr(inv, "_db_id"):
        db.add_claim(inv._db_id, statement, legal_risk)
    conf = claim.confidence.value
    return (
        f"✅ Claim added — auto-scored: **{conf}**\n"
        f"  Sources matched: {len(claim.sources)}\n\n"
        + _claims_md()
    )


def _claims_md() -> str:
    inv = _inv()
    if inv is None:
        return "_No active investigation._"
    if not inv.claims:
        return "_No claims yet. Add one above._"
    lines = [f"**Claims** (avg confidence: {inv.overall_confidence_score:.2f})\n"]
    for i, c in enumerate(inv.claims, 1):
        marker = "✓" if c.confidence in (ConfidenceLevel.CONFIRMED, ConfidenceLevel.CORROBORATED) else "⚠"
        lines.append(f"{i}. [{marker} {c.confidence.value}] {c.statement}")
        if c.entities_involved:
            lines.append(f"   - Entities: {', '.join(c.entities_involved)}")
        legal = c.legal_risk_label
        if legal != "None identified":
            lines.append(f"   - ⚖ Legal: {legal}")
    return "\n".join(lines)


def refresh_claims() -> str:
    return _claims_md()


# ---------------------------------------------------------------------------
# Tab 5 — Brief
# ---------------------------------------------------------------------------

def add_open_question(question: str) -> str:
    inv = _inv()
    if inv is None:
        return "❌ Start or load an investigation first.", ""
    question = question.strip()
    if question:
        inv.open_questions.append(question)
        if hasattr(inv, "_db_id"):
            db.add_open_question(inv._db_id, question)
    return f"✅ Question added.", ""


def generate_brief() -> str:
    inv = _inv()
    if inv is None:
        return "❌ No active investigation. Start or load one first."
    brief = inv.generate_brief()
    if hasattr(inv, "_db_id"):
        db.save_brief(inv._db_id, brief)
    return brief


def _active_or_error() -> Investigation | str:
    inv = _inv()
    if inv is None:
        return "❌ No active investigation. Start or load one first."
    return inv


def generate_dossier_packet_ui() -> str:
    inv = _active_or_error()
    if isinstance(inv, str):
        return inv
    packet = build_dossier_packet(inv.to_dict())
    return render_dossier_markdown(packet)


def generate_dossier_html_ui() -> str:
    inv = _active_or_error()
    if isinstance(inv, str):
        return inv
    packet = build_dossier_packet(inv.to_dict())
    return render_dossier_html(packet)


def generate_psicat_packet_ui() -> str:
    inv = _active_or_error()
    if isinstance(inv, str):
        return inv
    packet = build_psicat_training_packet(inv.to_dict())
    return render_psicat_training_markdown(packet)


def import_source_bundle_ui(bundle_text: str) -> tuple[str, str]:
    inv = _active_or_error()
    if isinstance(inv, str):
        return inv, _sources_md()
    try:
        incoming = parse_source_bundle(bundle_text)
    except ValueError as exc:
        return f"❌ {exc}", _sources_md()
    merged = merge_source_bundle([source.to_dict() for source in inv.sources], incoming)
    created_case_id: int | None = None
    if not hasattr(inv, "_db_id"):
        inv._db_id = db.create_case(inv.title, inv.lead, inv.journalist)  # type: ignore[attr-defined]
        created_case_id = inv._db_id
    persisted_sources = [
        {
            'title': source['title'],
            'tier': TIER_OPTIONS.get(source['tier'], SourceTier.UNCLASSIFIED).value,
            'source_type': source['source_type'],
            'url_or_ref': source['url_or_ref'],
            'date': source['date'],
            'excerpt': source['excerpt'],
        }
        for source in merged['imported']
    ]
    try:
        if persisted_sources:
            db.add_sources(inv._db_id, persisted_sources)
    except Exception as exc:  # pragma: no cover - guarded by tests via monkeypatch
        if created_case_id is not None:
            db.delete_case(created_case_id)
            delattr(inv, "_db_id")
        return f"❌ {exc}", _sources_md()
    for source in merged['imported']:
        tier = TIER_OPTIONS.get(source['tier'], SourceTier.UNCLASSIFIED)
        inv.add_source(
            source['title'],
            tier,
            source['source_type'],
            source['url_or_ref'],
            source['date'],
            source['excerpt'],
        )
    return (
        f"✅ Imported {len(merged['imported'])} sources; skipped {len(merged['duplicates'])} duplicates from {merged['attempted']} attempted rows.",
        _sources_md(),
    )


def generate_story_packet_ui() -> str:
    inv = _active_or_error()
    if isinstance(inv, str):
        return inv
    packet = build_story_packet(inv.to_dict())
    return render_story_markdown(packet)


def generate_story_html_ui() -> str:
    inv = _active_or_error()
    if isinstance(inv, str):
        return inv
    packet = build_story_packet(inv.to_dict())
    return render_story_html(packet)


def generate_source_scan_plan_ui(query: str) -> str:
    normalized = query.strip()
    if not normalized:
        inv = _inv()
        if inv is None:
            return "❌ Provide an entity/query or start an investigation first."
        normalized = inv.title
    manifest = build_public_record_queries(normalized)
    catalog = {item['slug']: item for item in public_record_source_catalog()}
    lines = [f"### Public-record scan plan — {normalized}", ""]
    for row in manifest:
        details = catalog.get(row['slug'], {})
        lines.append(f"- **{row['display_name']}** [{row['tier']}]")
        lines.append(f"  - Type: {row['source_type']}")
        lines.append(f"  - Query URL: {row['query_url']}")
        if details.get('slug'):
            lines.append(f"  - Source key: `{details['slug']}`")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tab 6 — Case Library
# ---------------------------------------------------------------------------

def _case_library_md() -> str:
    cases = db.list_cases()
    if not cases:
        return "_No cases saved yet._"
    lines = ["**Saved Cases**\n",
             "| # | Title | Journalist | Date | Status |",
             "|---|-------|-----------|------|--------|"]
    for c in cases:
        lines.append(
            f"| {c['id']} | {c['title']} | {c['journalist'] or '—'} "
            f"| {c['created_at'][:10]} | {c['status']} |"
        )
    return "\n".join(lines)


def load_case(case_id_str: str) -> tuple[str, str, str, str, str]:
    try:
        case_id = int(case_id_str.strip())
    except ValueError:
        return "❌ Enter a valid Case ID number.", "", "", "", ""
    row = db.get_case(case_id)
    if row is None:
        return f"❌ Case #{case_id} not found.", "", "", "", ""
    inv = Investigation(
        title=row["title"],
        lead=row["lead"],
        journalist=row["journalist"] or "",
        created_at=row["created_at"],
        status=row["status"],
    )
    inv._db_id = case_id  # type: ignore[attr-defined]
    # Load entities
    for e in db.list_entities(case_id):
        et = next((x for x in EntityType if x.value == e["entity_type"]), EntityType.OTHER)
        inv.add_entity(e["name"], et, e["description"], e["stated_position"])
    # Load sources
    for s in db.list_sources(case_id):
        t = next((x for x in SourceTier if x.value == s["tier"]), SourceTier.UNCLASSIFIED)
        inv.add_source(s["title"], t, s["source_type"], s["url_or_ref"], s["date"], s["excerpt"])
    # Load claims (lightweight — no cross-link)
    for c in db.list_claims(case_id):
        inv.add_claim(c["statement"], [], [], [LegalRisk(c["legal_risks"])] if c["legal_risks"] else [])
    # Load open questions
    for q in db.list_open_questions(case_id):
        inv.open_questions.append(q["question"])
    _set_inv(inv)
    brief_cache = row.get("brief_cache", "") or ""
    return (
        f"✅ Loaded Case #{case_id}: '{inv.title}'",
        _entities_md(),
        _sources_md(),
        _claims_md(),
        brief_cache,
    )


def delete_case_ui(case_id_str: str) -> tuple[str, str]:
    try:
        case_id = int(case_id_str.strip())
    except ValueError:
        return "❌ Enter a valid Case ID number.", _case_library_md()
    db.delete_case(case_id)
    if _inv() is not None and hasattr(_inv(), "_db_id") and _inv()._db_id == case_id:  # type: ignore[union-attr]
        _active["inv"] = None
    return f"✅ Case #{case_id} deleted.", _case_library_md()


# ---------------------------------------------------------------------------
# BUILD UI
# ---------------------------------------------------------------------------

DESCRIPTION = """
<div style="background:#0a0a0a;padding:18px 24px;border-radius:8px;margin-bottom:16px">
<h2 style="color:#e8c97a;margin:0">⬛ AXIOM — Investigative Journalist AI</h2>
<p style="color:#aaa;margin:4px 0 0 0">
Document-first investigative research platform by AxiomZero Technologies.<br>
<em>The document is the primary reality of investigative journalism.</em>
</p>
</div>
"""

METHODOLOGY_MD = """
### AxiomZero Investigative Methodology

**Source Tiers**
- **Tier 1** — Primary government records, court filings, FOIA documents, regulatory disclosures, legislation. *Anchors the investigation.*
- **Tier 2** — Established journalism, academic papers, on-record officials and experts. *Corroborates.*
- **Tier 3** — Press releases, social media, anonymous tips, secondary reports. *Generates leads, not conclusions.*

**Confidence Levels** (auto-scored from your sources)
- **CONFIRMED** — ≥2 Tier-1 sources; independently verifiable
- **CORROBORATED** — ≥1 Tier-1 + ≥1 Tier-2 source
- **ALLEGED** — ≥1 source, not fully corroborated
- **UNVERIFIED** — Single low-tier source or contradicted

**⚠ Output is always FOR HUMAN REVIEW. Never publish directly from AXIOM.**
"""


def build_ui() -> gr.Blocks:
    with gr.Blocks(
        title="AXIOM — Investigative Journalist AI",
        theme=gr.themes.Base(
            primary_hue="amber",
            neutral_hue="slate",
            font=gr.themes.GoogleFont("Inter"),
        ),
        css="""
        .axiom-header { background: #0d0d0d; padding: 12px 20px; border-radius: 6px; }
        footer { display: none !important; }
        """,
    ) as demo:
        gr.HTML(DESCRIPTION)

        with gr.Tabs():
            # ---- Tab 1: New Investigation ----
            with gr.Tab("📋 New Investigation"):
                gr.Markdown("### Start a New Investigation")
                with gr.Row():
                    t_title      = gr.Textbox(label="Investigation Title", placeholder="e.g. Municipal Contract Irregularities 2026")
                    t_journalist = gr.Textbox(label="Journalist", placeholder="Your name")
                t_lead  = gr.Textbox(label="Investigative Lead", lines=4,
                                     placeholder="Describe the lead: what's the allegation, what documents exist, what's the story?")
                btn_new = gr.Button("🚀 Start Investigation", variant="primary")
                out_new = gr.Textbox(label="Status", interactive=False)
                out_lib_new = gr.Markdown()
                btn_new.click(new_investigation, [t_title, t_lead, t_journalist], [out_new, out_lib_new])

                gr.Markdown(METHODOLOGY_MD)

            # ---- Tab 2: Entities ----
            with gr.Tab("👥 Entities"):
                gr.Markdown("### Map Entities\nAdd every person, organization, agency, and corporate structure relevant to the investigation.")
                with gr.Row():
                    e_name  = gr.Textbox(label="Name", placeholder="e.g. Jane Smith")
                    e_type  = gr.Dropdown(ENTITY_TYPES, label="Type", value="Person")
                e_desc  = gr.Textbox(label="Description", placeholder="Role, position, relationship to investigation")
                e_pos   = gr.Textbox(label="Stated Position", placeholder="What have they said publicly?")
                e_contr = gr.Textbox(label="Known Contradiction (optional)", placeholder="How does the record differ from their stated position?")
                btn_entity = gr.Button("➕ Add Entity", variant="primary")
                out_entity = gr.Markdown()
                btn_entity.click(add_entity, [e_name, e_type, e_desc, e_pos, e_contr], out_entity)
                btn_refresh_e = gr.Button("🔄 Refresh", variant="secondary")
                btn_refresh_e.click(refresh_entities, [], out_entity)

            # ---- Tab 3: Sources ----
            with gr.Tab("📁 Sources"):
                gr.Markdown("### Log Sources\nEvery claim must trace back to a source. Tier determines weight.")
                with gr.Row():
                    s_title = gr.Textbox(label="Source Title / Name", placeholder="e.g. SEC Filing 10-K 2025 — Acme Corp")
                    s_tier  = gr.Dropdown(TIER_LABELS_LIST, label="Tier", value=TIER_LABELS_LIST[0])
                with gr.Row():
                    s_type  = gr.Textbox(label="Source Type", placeholder="Court filing / FOIA / News article / Interview")
                    s_date  = gr.Textbox(label="Date", placeholder="YYYY-MM-DD")
                s_ref   = gr.Textbox(label="URL / Reference", placeholder="https://... or docket number")
                s_excerpt = gr.Textbox(label="Key Excerpt", lines=3,
                                       placeholder="Paste the most relevant passage from the source.")
                btn_source = gr.Button("➕ Add Source", variant="primary")
                out_source = gr.Markdown()
                btn_source.click(add_source, [s_title, s_tier, s_type, s_ref, s_date, s_excerpt], out_source)
                btn_refresh_s = gr.Button("🔄 Refresh", variant="secondary")
                btn_refresh_s.click(refresh_sources, [], out_source)
                gr.Markdown("### Batch Import Public-Record Sources\nPaste JSON-lines or pipe-delimited rows: `title | tier | source_type | url_or_ref | date | excerpt`")
                s_bundle = gr.Textbox(
                    label="Source Bundle",
                    lines=8,
                    placeholder='{"title":"Court filing","tier":"Tier 1","source_type":"Docket","url_or_ref":"https://...","date":"2026-01-01","excerpt":"..."}'
                )
                btn_import_sources = gr.Button("📥 Import Source Bundle", variant="secondary")
                out_import_sources = gr.Textbox(label="Import Status", interactive=False)
                btn_import_sources.click(import_source_bundle_ui, [s_bundle], [out_import_sources, out_source])
                gr.Markdown("### Public-Record Scan Plan\nGenerate the full AXIOM public-record query manifest for an entity or investigation.")
                scan_query = gr.Textbox(
                    label="Entity / Query",
                    placeholder="e.g. Acme Corp or leave blank to use the active investigation title"
                )
                btn_scan_plan = gr.Button("🛰 Build Source Scan Plan", variant="secondary")
                out_scan_plan = gr.Markdown()
                btn_scan_plan.click(generate_source_scan_plan_ui, [scan_query], out_scan_plan)

            # ---- Tab 4: Claims ----
            with gr.Tab("⚖ Claims"):
                gr.Markdown("### Add Claims\nConfidence is auto-scored from matched sources. Be specific.")
                c_stmt  = gr.Textbox(label="Claim Statement", lines=3,
                                     placeholder="State the factual claim precisely, as you would want it to appear in the record.")
                with gr.Row():
                    c_srcs = gr.Textbox(label="Supporting Sources (comma-separated titles or keywords)",
                                        placeholder="SEC Filing 10-K, FOIA 2024-001")
                    c_ents = gr.Textbox(label="Entities Involved (comma-separated)",
                                        placeholder="Jane Smith, Acme Corp")
                with gr.Row():
                    c_legal = gr.Dropdown(LEGAL_RISK_OPTIONS, label="Legal Risk Flag", value="NONE")
                    c_notes = gr.Textbox(label="Notes")
                btn_claim = gr.Button("➕ Add Claim", variant="primary")
                out_claim = gr.Markdown()
                btn_claim.click(add_claim, [c_stmt, c_srcs, c_ents, c_legal, c_notes], out_claim)
                btn_refresh_c = gr.Button("🔄 Refresh", variant="secondary")
                btn_refresh_c.click(refresh_claims, [], out_claim)

            # ---- Tab 5: Brief ----
            with gr.Tab("📄 Generate Brief"):
                gr.Markdown("### Generate Investigative Brief\nThe brief consolidates entities, sources, claims, and open questions into a structured document for human review.")
                with gr.Row():
                    q_text = gr.Textbox(label="Add Open Question", placeholder="What records still need to be obtained?")
                    btn_q  = gr.Button("➕ Add Question")
                out_q_status = gr.Textbox(label="", interactive=False, visible=False)
                btn_q.click(add_open_question, [q_text], [out_q_status, q_text])

                btn_brief  = gr.Button("📄 Generate Brief", variant="primary", size="lg")
                out_brief  = gr.Textbox(label="Investigative Brief — FOR HUMAN REVIEW ONLY",
                                        lines=35, interactive=False,
                                        placeholder="Click 'Generate Brief' to produce the structured report.")
                btn_brief.click(generate_brief, [], out_brief)
                gr.Markdown("> ⚠ **This brief is a research instrument. Editorial judgment is required before any publication.**")

                gr.Markdown("### Governed Dossier / PsiCat Handoff\nBuild the document-first packet for publication review and the PsiCat study packet for governed training and editorial synthesis.")
                with gr.Row():
                    btn_dossier = gr.Button("🧾 Generate Dossier Packet", variant="primary")
                    btn_dossier_html = gr.Button("🌐 Dossier HTML", variant="secondary")
                    btn_psicat = gr.Button("🐈 Generate PsiCat Packet", variant="secondary")
                    btn_story = gr.Button("📝 Generate Story Packet", variant="secondary")
                    btn_story_html = gr.Button("🌐 Story HTML", variant="secondary")
                out_dossier = gr.Textbox(
                    label="Governed Dossier Packet",
                    lines=28,
                    interactive=False,
                    placeholder="Generate a dossier packet to review legal-risk, retaliation, and evidence posture."
                )
                out_psicat = gr.Textbox(
                    label="PsiCat Training / Publication Packet",
                    lines=24,
                    interactive=False,
                    placeholder="Generate a PsiCat handoff packet to study claims, sources, and unknowns under governed constraints."
                )
                out_story = gr.Textbox(
                    label="PsiCat Publication Story Packet",
                    lines=26,
                    interactive=False,
                    placeholder="Generate an evidence-led story spine for governed PsiCat drafting."
                )
                out_dossier_html = gr.Textbox(
                    label="Governed Dossier HTML",
                    lines=12,
                    interactive=False,
                    placeholder="Generate HTML export for downstream web or editorial systems."
                )
                out_story_html = gr.Textbox(
                    label="PsiCat Story HTML",
                    lines=12,
                    interactive=False,
                    placeholder="Generate HTML export for downstream web or editorial systems."
                )
                btn_dossier.click(generate_dossier_packet_ui, [], out_dossier)
                btn_dossier_html.click(generate_dossier_html_ui, [], out_dossier_html)
                btn_psicat.click(generate_psicat_packet_ui, [], out_psicat)
                btn_story.click(generate_story_packet_ui, [], out_story)
                btn_story_html.click(generate_story_html_ui, [], out_story_html)

            # ---- Tab 6: Case Library ----
            with gr.Tab("🗂 Case Library"):
                gr.Markdown("### Saved Cases")
                out_lib = gr.Markdown()
                with gr.Row():
                    lib_id      = gr.Textbox(label="Case ID", placeholder="Enter Case # to load or delete")
                    btn_load    = gr.Button("📂 Load Case", variant="primary")
                    btn_delete  = gr.Button("🗑 Delete Case", variant="stop")
                lib_status = gr.Textbox(label="Status", interactive=False)
                lib_loaded = gr.Markdown()

                def refresh_lib() -> str:
                    return _case_library_md()

                btn_refresh_lib = gr.Button("🔄 Refresh Library")
                btn_refresh_lib.click(refresh_lib, [], out_lib)

                btn_load.click(
                    load_case, [lib_id],
                    [lib_status, gr.Markdown(), gr.Markdown(), gr.Markdown(), gr.Markdown()]
                )
                btn_delete.click(delete_case_ui, [lib_id], [lib_status, out_lib])
                demo.load(refresh_lib, [], out_lib)

        gr.Markdown("""
---
*AXIOM — Investigative Journalist AI* | AxiomZero Technologies  
*Theory, methodology: ThomasCory Walker-Pearson. Implementation: GitHub Copilot (AI).*
""")

    return demo


if __name__ == "__main__":
    ui = build_ui()
    ui.launch(
        server_name="0.0.0.0",
        server_port=7870,
        share=False,
        inbrowser=True,
    )
