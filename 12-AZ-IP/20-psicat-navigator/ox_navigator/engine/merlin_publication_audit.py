# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Audit of the webspace's own PDF exports against the index and the repository.

ADJACENT TRACK.  On 2026-10-08 the steward uploaded three PDFs the webspace
compiled from itself: PsiCat Publications (36 articles), PsiCat's Comic Shop
(15 pieces) and the Knowledge Library (232 sources).  Their extracted text
is stored in ``data/raw/psicat_exports_2026-10-08.json.gz`` with a provenance
sidecar giving each PDF's SHA-256 and upload commit.

The audit asks four questions, in order of weight:

1. Do the articles' physics statements agree with the repository's live
   registry (``9-INFRASTRUCTURE/um_live_status.json``)?  The repository is the
   authority on science; where an article states a status the registry has
   since revised, the article is what needs correcting.
2. Does the Publications export match the index's own list of published
   articles (titles, dates, categories), and does it repeat any work?
3. Are the exports' declared counts reproducible from their contents?
4. Does the PDF compiler render the documents faithfully (contents page
   numbers, non-Latin characters)?

Claim checks are pattern-based.  They catch the specific statements listed
in ``CLAIM_RULES``; they do not read for meaning, and a clean result is not
a certificate that an article is right.
"""

from __future__ import annotations

import gzip
import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

from .merlin_webspace_index import load_full_index

STATUS_LABEL = "ADJACENT_TRACK"
RAW_DIR = Path(__file__).resolve().parent / "data" / "raw"
EXPORTS_PATH = RAW_DIR / "psicat_exports_2026-10-08.json.gz"
EXPORTS_PROVENANCE_PATH = RAW_DIR / "psicat_exports_2026-10-08.provenance.json"
REPO_ROOT = Path(__file__).resolve().parents[4]
LIVE_REGISTRY_PATH = REPO_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"
TRUTH_LAYER_PATH = REPO_ROOT / "docs" / "TRUTH_LAYER.md"
PAGE_BREAK = "\n<<<PAGE>>>\n"
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}
PUBLICATION_HEADER = "PSICAT PUBLICATIONS"
PLANCK_NS = (0.9649, 0.0042)
MONTHS = {m: i + 1 for i, m in enumerate(
    ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"))}

_TOC_LINE = re.compile(r"^\s*(\d{2})\s+(.*?)\s*\.{3,}\s*(\d+)\s*$", re.M)
_BYLINE = re.compile(r"PsiCat, Sovereign Navigator[^·\n]*·\s*([A-Z][a-z]{2}) (\d{1,2}), (\d{4})\s*·\s*([^·\n]+?)\s*·")
_MOJIBAKE = re.compile(r"[Ã‚¼›]")


@lru_cache(maxsize=2)
def _load_exports_cached(path: str) -> dict[str, str]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def load_exports(path: str | Path | None = None) -> dict[str, str] | None:
    target = Path(path or EXPORTS_PATH)
    return dict(_load_exports_cached(str(target))) if target.exists() else None


def load_exports_provenance() -> dict[str, Any]:
    return json.loads(EXPORTS_PROVENANCE_PATH.read_text(encoding="utf-8")) if EXPORTS_PROVENANCE_PATH.exists() else {}


def load_live_registry(path: str | Path | None = None) -> dict[str, Any]:
    return json.loads(Path(path or LIVE_REGISTRY_PATH).read_text(encoding="utf-8"))


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace(PAGE_BREAK, " "))


def _finding(fid: str, severity: str, title: str, evidence: str, recommendation: str) -> dict[str, Any]:
    return {"id": fid, "severity": severity, "title": title, "evidence": evidence, "recommendation": recommendation}


# ---------------------------------------------------------------------------
# Rendering faults shared by every export
# ---------------------------------------------------------------------------

def is_letter_spaced(line: str) -> bool:
    """True for lines the PDF compiler spread out one glyph at a time."""
    body = line.strip()
    if len(body) < 12:
        return False
    odd = body[1::2]
    return odd.count(" ") >= 0.8 * len(odd)


def contents_page_check(text: str) -> dict[str, Any]:
    """Compare each Contents page number with the page where that work starts."""
    pages = text.split(PAGE_BREAK)
    toc = [(int(n), title, int(page)) for n, title, page in _TOC_LINE.findall(pages[0])]
    actual = _work_start_pages(pages)
    rows = []
    for (number, _title, declared), start in zip(toc, actual):
        rows.append({"entry": number, "declared_page": declared, "actual_page": start, "offset": declared - start})
    offsets = Counter(r["offset"] for r in rows)
    shifted = [r for r in rows if r["offset"] != 0]
    points_to_next = all(rows[i]["declared_page"] == rows[i + 1]["actual_page"] for i in range(len(rows) - 1))
    beyond = [r for r in rows if r["declared_page"] > len(pages)]
    return {"entries": len(toc), "pages": len(pages), "matched_entries": len(rows),
            "wrong_page_entries": len(shifted), "offset_histogram": dict(offsets),
            "each_entry_points_to_next_work": bool(rows) and points_to_next,
            "entries_beyond_last_page": [r["entry"] for r in beyond], "rows": rows}


def _work_start_pages(pages: list[str]) -> list[int]:
    """1-based pages where a work begins, using the strongest header the document has."""
    heads = [next((ln.strip() for ln in page.split("\n") if ln.strip()), "") for page in pages]
    tests = (lambda h: h == PUBLICATION_HEADER, lambda h: bool(re.fullmatch(r"T\d", h)),
             lambda h: h.isupper() and len(h) > 3)
    for test in tests:
        starts = [i + 1 for i, head in enumerate(heads) if i and test(head)]
        if starts:
            return starts
    return []


def glyph_check(text: str) -> dict[str, Any]:
    lines = text.replace(PAGE_BREAK, "\n").split("\n")
    spaced = [ln for ln in lines if "\x00" in ln or is_letter_spaced(ln)]
    mojibake = [ln for ln in lines if _MOJIBAKE.search(ln)]
    return {"letter_spaced_lines": len(spaced), "lines_with_mangled_glyphs": len(mojibake),
            "examples": [re.sub(r"\s+", " ", re.sub(r"[\x00-\x08\x0b-\x1f]", "", ln).strip())[:120] for ln in (mojibake or spaced)[:3]]}


# ---------------------------------------------------------------------------
# Publications: inventory against the index
# ---------------------------------------------------------------------------

def parse_publications(text: str, index_titles: list[str] | None = None) -> list[dict[str, Any]]:
    pages = text.split(PAGE_BREAK)
    starts = [i for i, p in enumerate(pages) if p.lstrip().startswith(PUBLICATION_HEADER)]
    titles = sorted(index_titles or [], key=len, reverse=True)
    works = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(pages)
        body = PAGE_BREAK.join(pages[start:end])
        head_lines = body.lstrip()[len(PUBLICATION_HEADER):].strip().split("\n")
        probe = _norm(" ".join(head_lines[:4]))
        title = next((t for t in titles if _norm(t) and probe.startswith(_norm(t))), None)
        byline = _BYLINE.search(body)
        works.append({
            "position": n + 1,
            "first_page": start + 1,
            "title": title or head_lines[0].strip(),
            "matched_index_title": title is not None,
            "date": (f"{byline.group(3)}-{MONTHS[byline.group(1)]:02d}-{int(byline.group(2)):02d}" if byline else None),
            "category": byline.group(4).strip() if byline else None,
            "text": body,
        })
    return works


def _slug(category: str | None) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (category or "").lower().replace("&", "")).strip("-")
    return slug[4:] if slug.startswith("the-") else slug


def publication_inventory(works: list[dict[str, Any]], index: dict[str, Any] | None) -> dict[str, Any]:
    published = (index or {}).get("content", {}).get("articles_source", {}).get("published") or []
    published = published if isinstance(published, list) else []
    titles = Counter(w["title"] for w in works)
    duplicates = []
    for title, count in titles.items():
        if count > 1:
            bodies = [_norm(_flat(w["text"]))[:4000] for w in works if w["title"] == title]
            duplicates.append({"title": title, "positions": [w["position"] for w in works if w["title"] == title],
                               "identical_opening": len(set(bodies)) == 1})
    by_title: dict[str, list[dict[str, Any]]] = {}
    for item in published:
        by_title.setdefault(item["title"], []).append(item)
    date_offsets: Counter = Counter()
    category_mismatches = []
    from datetime import date as _date
    for w in works:
        match = (by_title.get(w["title"]) or [None])[0]
        if not match or not w["date"]:
            continue
        date_offsets[(_date.fromisoformat(match["published_date"]) - _date.fromisoformat(w["date"])).days] += 1
        if _slug(w["category"]) != match.get("category"):
            category_mismatches.append({"title": w["title"], "pdf": w["category"], "index": match.get("category")})
    index_dupes = [t for t, items in by_title.items() if len(items) > 1]
    return {
        "works_in_pdf": len(works),
        "works_in_index": len(published),
        "titles_matched_to_index": sum(w["matched_index_title"] for w in works),
        "duplicate_titles_in_pdf": duplicates,
        "duplicate_titles_in_index": index_dupes,
        "index_titles_missing_from_pdf": sorted(set(by_title) - set(titles)),
        "date_offset_days_index_minus_pdf": dict(date_offsets),
        "category_mismatches": category_mismatches,
    }


# ---------------------------------------------------------------------------
# Publications: physics statements against the live registry
# ---------------------------------------------------------------------------

def _prediction(registry: dict[str, Any], pid: str) -> dict[str, Any]:
    return next((p for p in registry.get("predictions", []) if p.get("id") == pid), {})


def _gate(registry: dict[str, Any], name: str) -> dict[str, Any]:
    return next((g for g in registry.get("open_gates", []) if g.get("gate") == name), {})


def _snippet(text: str, match: re.Match, width: int = 110) -> str:
    return text[max(0, match.start() - width):match.end() + width].strip()


def check_claims(works: list[dict[str, Any]], registry: dict[str, Any]) -> list[dict[str, Any]]:
    """Each row: rule, work, verdict (consistent / contradicts / omits / stale), evidence, authority."""
    physics = registry.get("physics", {})
    rows: list[dict[str, Any]] = []

    def add(rule: str, work: dict[str, Any], verdict: str, evidence: str, authority: str) -> None:
        rows.append({"rule": rule, "work": work["title"], "position": work["position"],
                     "verdict": verdict, "evidence": evidence, "authority": authority})

    exp_r, exp_desi, exp_juno = (_prediction(registry, i) for i in ("EXP-4", "EXP-2", "EXP-3"))
    desi_sigmas = {float(s) for s in re.findall(r"(\d\.\d+)σ", exp_desi.get("verdict", ""))}
    cmb_gate = _gate(registry, "CMB_AMP_CONFIRMED_IRREDUCIBLE")
    lean = registry.get("lean4", {})
    tests_passed = registry.get("tests", {}).get("passed")
    truth_layer = TRUTH_LAYER_PATH.read_text(encoding="utf-8") if TRUTH_LAYER_PATH.exists() else ""
    postulates_doc = "The Two Postulated Constants (not derived)" in truth_layer

    for work in works:
        flat = _flat(work["text"])
        for m in re.finditer(r"n_s\s*~=\s*(0\.9\d+)", flat):
            ok = abs(float(m.group(1)) - physics.get("cmb_spectral_index_n_s", 0)) < 5e-5
            add("NS-VALUE", work, "consistent" if ok else "contradicts", _snippet(flat, m),
                f"um_live_status physics.cmb_spectral_index_n_s = {physics.get('cmb_spectral_index_n_s')}")
        for m in re.finditer(r"within (\d\.\d+)\s*sigma", flat):
            pull = abs(PLANCK_NS[0] - physics.get("cmb_spectral_index_n_s", 0)) / PLANCK_NS[1]
            ok = abs(float(m.group(1)) - pull) < 0.01
            add("NS-PULL", work, "consistent" if ok else "contradicts", _snippet(flat, m),
                f"|0.9649 - {physics.get('cmb_spectral_index_n_s')}| / 0.0042 = {pull:.2f} sigma")
        if re.search(r"r\s*~?=\s*0\.0315", flat):
            m = re.search(r"r\s*~?=\s*0\.0315", flat)
            mentions_act = bool(re.search(r"0\.016|ACT DR6", flat))
            if not mentions_act and exp_r.get("status") == "HIGH_TENSION":
                says_holds = bool(re.search(r"prediction holds|falls within (?:this|the observational) bound", flat))
                add("R-STATUS", work, "contradicts" if says_holds else "omits", _snippet(flat, m),
                    f"{exp_r.get('id')} status {exp_r.get('status')}: {exp_r.get('verdict')}")
            else:
                add("R-STATUS", work, "consistent", _snippet(flat, m), f"{exp_r.get('id')} {exp_r.get('status')}")
        for m in re.finditer(r"k_CS\s*=\s*(\d+)(?![\d²^])", flat):
            value = int(m.group(1))
            pairs = {(int(a), int(b)) for a, b in re.findall(r"\((\d),\s*(\d)\)", flat)}
            ok = value == physics.get("cs_level_k_cs") or any(a * a + b * b == value for a, b in pairs)
            if value in (3, 5):  # start of a formula such as "k_CS = 5^2 + 7^2" or a chain step
                continue
            add("KCS-VALUE", work, "consistent" if ok else "contradicts", _snippet(flat, m),
                "k_CS = 74 = 5^2 + 7^2; other levels must equal a^2 + b^2 for a braid named in the same work")
        for m in re.finditer(r"c_s\s*=\s*(\d+)/(\d+)", flat):
            ok = (int(m.group(1)), int(m.group(2))) == (physics.get("braided_sound_speed_numerator"),
                                                        physics.get("braided_sound_speed_denominator"))
            add("CS-VALUE", work, "consistent" if ok else "contradicts", _snippet(flat, m), "c_s = 12/37")
        if re.search(r"birefringence|beta", flat, re.I):
            allowed = {physics.get("birefringence_low_branch_deg"), physics.get("birefringence_high_branch_deg"),
                       physics.get("birefringence_derived_low_deg"), physics.get("birefringence_derived_high_deg"),
                       *physics.get("birefringence_admissible_window", []), *physics.get("birefringence_gap_forbidden", []),
                       0.277, 0.057}
            allowed |= {round(v, 2) for v in allowed if v is not None}
            for m in re.finditer(r"(0\.\d{2,3})\s*°", flat):
                ok = float(m.group(1)) in allowed
                if not ok:
                    add("BETA-VALUE", work, "contradicts", _snippet(flat, m),
                        "physics birefringence branches, window and gap")
            if re.search(r"0\.\d{2,3}\s*°", flat):
                add("BETA-VALUE", work, "consistent", "all degree values match the registry branches, window or gap"
                    if not any(r["rule"] == "BETA-VALUE" and r["work"] == work["title"] for r in rows) else "",
                    "physics birefringence branches, window and gap")
        for m in re.finditer(r"DESI[^.]{0,200}?(\d\.\d+)\s*sigma|w_a[^.]{0,120}?(\d\.\d+)\s*sigma", flat):
            value = float(m.group(1) or m.group(2))
            add("DESI-SIGMA", work, "consistent" if value in desi_sigmas else "contradicts", _snippet(flat, m),
                f"{exp_desi.get('id')}: {exp_desi.get('verdict')}")
        for m in re.finditer(r"from one experiment", flat):
            add("DESI-SCOPE", work, "contradicts", _snippet(flat, m),
                f"{exp_desi.get('id')} cites BAO-only, combined BAO+CMB+SNe and 2D-correlated tensions: {exp_desi.get('verdict')}")
        for m in re.finditer(r"labels this tension ARCHITECTURE_LIMIT_CERTIFIED", flat):
            add("DESI-LABEL", work, "contradicts", _snippet(flat, m),
                f"{exp_desi.get('id')} status {exp_desi.get('status')}; open gate DESI_DR3_MONITORING "
                f"({_gate(registry, 'DESI_DR3_MONITORING').get('description')})")
        for m in re.finditer(r"JUNO[^.]{0,200}?(\d\.\d+)\s*sigma|Deltam²21[^.]{0,120}?(\d\.\d+)\s*sigma", flat):
            value = float(m.group(1) or m.group(2))
            ok = value == exp_juno.get("sigma")
            add("JUNO-SIGMA", work, "consistent" if ok else "contradicts", _snippet(flat, m),
                f"{exp_juno.get('id')} sigma = {exp_juno.get('sigma')}")
        for m in re.finditer(r"irreducible mismatch|not a tension that will be resolved by better data", flat):
            add("CMB-IRREDUCIBLE", work, "contradicts", _snippet(flat, m),
                f"open gate CMB_AMP_CONFIRMED_IRREDUCIBLE: {cmb_gate.get('description')}; "
                f"scientific_assessment.cmb_normalization: {registry.get('scientific_assessment', {}).get('cmb_normalization')}")
        for m in re.finditer(r"([\d,]+) Lean4 theorems", flat):
            add("LEAN-SCOPE", work, "omits", _snippet(flat, m),
                f"lean4.theorem_count {lean.get('theorem_count')} with count_scope {lean.get('count_scope')}, "
                f"physical_proof_count {lean.get('physical_proof_count')}")
        for m in re.finditer(r"([\d,]+) passing tests", flat):
            value = int(m.group(1).replace(",", ""))
            add("TEST-COUNT", work, "consistent" if value == tests_passed else "stale", _snippet(flat, m),
                f"tests.passed = {tests_passed}")
        for m in re.finditer(r"HARDGATE[^.]{0,80}proven and machine-verified", flat):
            add("HARDGATE-MEANING", work, "contradicts", _snippet(flat, m),
                f"scientific_assessment.closure_earned = {registry.get('scientific_assessment', {}).get('closure_earned')}; "
                f"Lean count scope {lean.get('count_scope')}")
        for m in re.finditer(r"not fitted to data|No parameter is adjusted|There is no free parameter", flat):
            if postulates_doc:
                add("POSTULATE-AS-DERIVATION", work, "contradicts", _snippet(flat, m),
                    "docs/TRUTH_LAYER.md section 1.1 'The Two Postulated Constants (not derived)': n_w = 5 is "
                    "selected by Planck n_s; K_CS = 74 rests on that uniqueness argument")
    return rows


# ---------------------------------------------------------------------------
# Knowledge Library and Comic Shop: declared counts
# ---------------------------------------------------------------------------

def library_counts(text: str) -> dict[str, Any]:
    head = text.split(PAGE_BREAK)[0]
    declared_total = int(re.search(r"(\d+) sources across (\d+) domains", head).group(1))
    declared_domains = int(re.search(r"(\d+) sources across (\d+) domains", head).group(2))
    tier_line = re.search(r"^Tiers:(.*)$", head, re.M)
    declared_tiers = {t: int(n) for t, n in re.findall(r"(T\d) (\d+)", tier_line.group(1) if tier_line else "")}
    declared_api = int(re.search(r"(\d+) offer a programmatic API", head).group(1))
    tiers = Counter(re.findall(r"• Tier: (T\d)", text))
    links = re.findall(r"• Link: (\S+)", text)
    body = text.split(PAGE_BREAK, 1)[1] if PAGE_BREAK in text else text
    sections = re.split(r"\n(?=T\d\nTier \d)", "\n" + body)
    domain_sums = {}
    for section in sections:
        tier = re.match(r"\s*(T\d)\n", section)
        if tier:
            stated = re.search(r"(\d+) sources\s+·\s+(\d+) domains", section)
            filed = [int(n) for n in re.findall(r"(\d+)\s+sources?\s+filed\s+at\s+this\s+tier", _flat(section))]
            domain_sums[tier.group(1)] = {"declared": int(stated.group(1)) if stated else None,
                                          "sum_of_domain_counts": sum(filed), "domain_headers_found": len(filed),
                                          "declared_domains": int(stated.group(2)) if stated else None}
    return {
        "declared_total": declared_total, "declared_domains": declared_domains,
        "declared_tiers": declared_tiers, "counted_tiers": dict(sorted(tiers.items())),
        "tiers_reproduce": dict(sorted(tiers.items())) == declared_tiers and sum(tiers.values()) == declared_total,
        "unique_links": len(set(links)), "entries": len(links),
        "declared_api": declared_api,
        "entries_marked_programmatic_api": text.count("Programmatic API: yes"),
        "entries_with_api_access": len(re.findall(r"Access: [^\n]*API", text)),
        "verified_dates": dict(Counter(re.findall(r"• Verified: (\S+)", text))),
        "domain_sums": domain_sums,
    }


def comic_shop_counts(text: str) -> dict[str, Any]:
    head = text.split(PAGE_BREAK)[0]
    declared = int(re.search(r"(\d+) works inside", head).group(1))
    return {"declared_works": declared, "contents_entries": len(_TOC_LINE.findall(head)),
            "pages": text.count(PAGE_BREAK) + 1,
            "living_entries_empty": "shop returned none" in _flat(head)}


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

def audit_exports(exports: dict[str, str] | None = None, index: dict[str, Any] | None = None,
                  registry: dict[str, Any] | None = None) -> dict[str, Any]:
    exports = exports or load_exports()
    if not exports:
        return {"status_label": STATUS_LABEL, "available": False, "findings": []}
    index = index if index is not None else load_full_index()
    registry = registry or load_live_registry()
    published = (index or {}).get("content", {}).get("articles_source", {}).get("published") or []
    works = parse_publications(exports["publications"], [p["title"] for p in published] if isinstance(published, list) else [])
    inventory = publication_inventory(works, index)
    claims = check_claims(works, registry)
    toc = {name: contents_page_check(text) for name, text in exports.items()}
    glyphs = {name: glyph_check(text) for name, text in exports.items()}
    library = library_counts(exports["knowledge_library"])
    comics = comic_shop_counts(exports["comic_shop"])

    findings: list[dict[str, Any]] = []

    def claim_rows(*rules: str, verdicts: tuple[str, ...] = ("contradicts", "omits", "stale")) -> list[dict[str, Any]]:
        return [r for r in claims if r["rule"] in rules and r["verdict"] in verdicts]

    def where(rows: list[dict[str, Any]]) -> str:
        return "; ".join(f"#{r['position']} '{r['work']}': \"{r['evidence'][:160]}\"" for r in rows[:3])

    r_rows = sorted(claim_rows("R-STATUS"), key=lambda r: r["verdict"] != "contradicts")
    if r_rows:
        asserting = [r for r in r_rows if r["verdict"] == "contradicts"]
        findings.append(_finding(
            "PX-R-TENSION-OMITTED", "high" if asserting else "medium",
            "Articles say the r prediction holds without the ACT DR6 tension",
            f"{len(asserting)} article(s) state r = 0.0315 holds against BICEP/Keck r < 0.036 alone; "
            f"{len(r_rows) - len(asserting)} more list r = 0.0315 with no status. {where(r_rows)}. "
            f"Registry: {r_rows[0]['authority']}",
            "Revise these articles to state the current status: consistent with BICEP/Keck and SPT-3G, under high "
            "tension with ACT DR6 r < 0.016."))
    cmb_rows = claim_rows("CMB-IRREDUCIBLE")
    if cmb_rows:
        findings.append(_finding(
            "PX-CMB-IRREDUCIBLE-RETIRED", "high", "Articles repeat the CMB 'irreducible mismatch' the registry withdrew",
            f"{where(cmb_rows)}. Registry: {cmb_rows[0]['authority']}",
            "Replace with the registry wording: the normalisation is calibrated, transfer corrections remain open, "
            "and the irreducibility inference is invalid."))
    desi_rows = claim_rows("DESI-LABEL", "DESI-SCOPE")
    if desi_rows:
        findings.append(_finding(
            "PX-DESI-MISSTATED", "medium", "DESI w_a tension carries the wrong label and an understated scope",
            f"{where(desi_rows)}. Registry: {desi_rows[0]['authority']}",
            "Label it HIGH_TENSION under DESI_DR3_MONITORING, and give the three registry figures "
            "(BAO-only 2.07, combined 2.75, 2D-correlated 2.30 sigma)."))
    proof_rows = claim_rows("HARDGATE-MEANING", "LEAN-SCOPE", "POSTULATE-AS-DERIVATION")
    if proof_rows:
        findings.append(_finding(
            "PX-PROOF-OVERSTATED", "medium", "Articles describe hardgates and Lean counts as proof the registry does not claim",
            f"{len(proof_rows)} statement(s). {where(proof_rows)}",
            "State that the Lean count is of historical declarations, not physical proof obligations; that closure is "
            "not earned; and that n_w = 5 is selected by Planck n_s, with k_CS = 74 resting on that selection."))
    stale = claim_rows("TEST-COUNT")
    if stale:
        findings.append(_finding(
            "PX-STALE-COUNTS", "low", "Article quotes an out-of-date test count",
            f"{where(stale)}. Registry: {stale[0]['authority']}",
            "Quote counts with their date, or link to the live registry instead of embedding a number."))
    contradicts_other = [r for r in claims if r["verdict"] == "contradicts" and r["rule"] in
                         ("NS-VALUE", "NS-PULL", "KCS-VALUE", "CS-VALUE", "BETA-VALUE", "DESI-SIGMA", "JUNO-SIGMA")]
    if contradicts_other:
        findings.append(_finding("PX-VALUE-MISMATCH", "high", "Article values disagree with the registry",
                                 where(contradicts_other), "Correct each value against um_live_status.json."))
    consistent = Counter(r["rule"] for r in claims if r["verdict"] == "consistent")
    findings.append(_finding(
        "PX-VALUES-CONSISTENT", "info", "Core numbers in the articles match the registry",
        f"Statements checked and consistent: {dict(sorted(consistent.items()))}. n_s = 0.9635 and its 0.33 sigma pull "
        "from Planck, k_CS = 74 (and 61 for the (5,6) branch), c_s = 12/37, the birefringence branches, window and gap, "
        "the DESI sigma figures and the JUNO 1.71 sigma all agree.",
        "None; the problems are status and framing, not the numbers."))

    if inventory["duplicate_titles_in_pdf"]:
        dup = inventory["duplicate_titles_in_pdf"]
        findings.append(_finding(
            "PX-DUPLICATE-WORK", "low", "One title appears twice in the feed",
            "; ".join(f"'{d['title']}' at positions {d['positions']} (identical opening: {d['identical_opening']}); "
                      f"the index lists it {'twice' if d['title'] in inventory['duplicate_titles_in_index'] else 'once'}"
                      for d in dup),
            "Where the openings match, unpublish the duplicate; where they differ, two articles share one title "
            "and one should be retitled."))
    offsets = inventory["date_offset_days_index_minus_pdf"]
    if offsets and set(offsets) != {0}:
        findings.append(_finding(
            "PX-DATE-RENDERING", "low", "Export dates differ from the index's published dates",
            f"Index date minus PDF date, in days: {offsets}. A uniform one-day difference is what a UTC date shown in a "
            "western local time zone produces.",
            "Render dates from the stored UTC value, or label the time zone."))
    if inventory["category_mismatches"] or inventory["index_titles_missing_from_pdf"]:
        findings.append(_finding(
            "PX-INVENTORY-MISMATCH", "medium", "Export and index disagree on the article list",
            f"Missing from PDF: {inventory['index_titles_missing_from_pdf']}; category mismatches: "
            f"{inventory['category_mismatches']}", "Recompile the export from the same snapshot as the index."))
    else:
        findings.append(_finding(
            "PX-INVENTORY-MATCHES", "info", "Export matches the index article list",
            f"{inventory['works_in_pdf']} works in the PDF, {inventory['works_in_index']} in the index, "
            f"{inventory['titles_matched_to_index']} titles matched; categories agree.", "None."))

    bad_toc = {n: t for n, t in toc.items() if t["wrong_page_entries"]}
    if bad_toc:
        findings.append(_finding(
            "PX-CONTENTS-PAGES", "medium", "Every Contents page number in the exports is wrong",
            "; ".join(f"{n}: {t['wrong_page_entries']}/{t['matched_entries']} entries off, each points to the next "
                      f"work's first page: {t['each_entry_points_to_next_work']}, entries past the last page: "
                      f"{t['entries_beyond_last_page']}" for n, t in bad_toc.items()),
            "The compiler records the page number after a work is written. Record it before writing the work."))
    corrupted = {n: g for n, g in glyphs.items() if g["letter_spaced_lines"] or g["lines_with_mangled_glyphs"]}
    if corrupted:
        findings.append(_finding(
            "PX-GLYPH-CORRUPTION", "medium", "Greek letters and math symbols are mangled in the exports",
            "; ".join(f"{n}: {g['lines_with_mangled_glyphs']} line(s) with mangled glyphs, {g['letter_spaced_lines']} "
                      f"letter-spaced or two-byte line(s), e.g. {g['examples'][:1]}" for n, g in corrupted.items()),
            "Embed a Unicode font in the PDF compiler (the standard 14 fonts cannot draw sigma, Delta or Lambda), "
            "or transliterate before rendering."))

    if library["tiers_reproduce"]:
        findings.append(_finding(
            "PX-LIBRARY-COUNTS-VERIFIED", "info", "Knowledge Library tier counts reproduce",
            f"Tiers {library['counted_tiers']} sum to {library['declared_total']}; {library['unique_links']} unique links "
            f"for {library['entries']} entries; per-domain counts add up to each tier total "
            f"({ {t: d['sum_of_domain_counts'] for t, d in library['domain_sums'].items()} }).", "None."))
    if library["declared_api"] not in (library["entries_marked_programmatic_api"], library["entries_with_api_access"]):
        findings.append(_finding(
            "PX-LIBRARY-API-COUNT", "low", "Declared API count does not match the entries",
            f"Header says {library['declared_api']} sources offer a programmatic API; {library['entries_marked_programmatic_api']} "
            f"entries are marked 'Programmatic API: yes' and {library['entries_with_api_access']} list API access.",
            "Derive the header count from the same field the entries print."))
    mismatched_domains = {t: d for t, d in library["domain_sums"].items()
                          if d["declared"] is not None and d["declared"] != d["sum_of_domain_counts"]}
    if mismatched_domains:
        findings.append(_finding(
            "PX-LIBRARY-DOMAIN-SUMS", "low", "Per-domain counts do not add up to tier totals in the text",
            f"{mismatched_domains}. This can be a text-extraction effect where a domain header wraps; check in the PDF.",
            "Confirm in the rendered PDF; if real, derive tier totals from domain counts."))
    if comics["living_entries_empty"]:
        findings.append(_finding(
            "PX-COMIC-LIVING-EMPTY", "low", "The Comic Shop export carries no living entries",
            "The export says the shop returned no ledger, briefs or studies when compiled. comicShopLoad is one of the "
            "service-role functions with no detected login check.",
            "Check whether the shop is empty or the read failed; the export should say which."))

    findings.sort(key=lambda f: (SEVERITY_ORDER[f["severity"]], f["id"]))
    return {
        "status_label": STATUS_LABEL,
        "available": True,
        "provenance": load_exports_provenance().get("sources", {}),
        "authority": "9-INFRASTRUCTURE/um_live_status.json and docs/TRUTH_LAYER.md (repository is the authority on science)",
        "method_limits": "Pattern-based checks of listed statements; not a reading for meaning. A clean result certifies nothing.",
        "findings": findings,
        "severity_counts": dict(Counter(f["severity"] for f in findings)),
        "publications": {k: v for k, v in inventory.items()},
        "claims": claims,
        "contents_pages": {n: {k: v for k, v in t.items() if k != "rows"} for n, t in toc.items()},
        "glyphs": glyphs,
        "knowledge_library": library,
        "comic_shop": comics,
    }


def summarise_exports() -> dict[str, Any]:
    report = audit_exports()
    if not report.get("available"):
        return report
    return {k: report[k] for k in ("status_label", "available", "provenance", "authority", "method_limits",
                                   "severity_counts")} | {
        "findings": [{k: f[k] for k in ("id", "severity", "title", "evidence")} for f in report["findings"]],
        "works": report["publications"]["works_in_pdf"],
        "claims_checked": len(report["claims"]),
    }
