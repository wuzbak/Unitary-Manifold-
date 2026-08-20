from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SITE_ROOT = REPO_ROOT / "public-site"
OUTPUT_PATH = PUBLIC_SITE_ROOT / "data" / "reader-index.json"
POSTS_DIR = REPO_ROOT / "7-OUTREACH" / "substack" / "posts"
BOOKS_DIR = REPO_ROOT / "7-OUTREACH" / "books"

ALLOWED_TOPICS = [
    "Foundation & Core Theory",
    "Particle Physics & Standard Model",
    "Cosmology & Observation",
    "Philosophy & Consciousness",
    "AI, Ethics & Collaboration",
    "Applied Domains",
    "Mathematics & Formal Methods",
    "Open Science & Community",
    "Books",
]

TOPIC_KEYWORDS = [
    (
        "AI, Ethics & Collaboration",
        {
            "ai",
            "authorship",
            "human-ai",
            "human ai",
            "copilot",
            "safety",
            "governance",
            "steward",
            "stewardship",
            "collaboration",
            "robotics",
            "guard",
            "integrity",
            "community steward",
        },
    ),
    (
        "Philosophy & Consciousness",
        {
            "consciousness",
            "god",
            "religion",
            "free will",
            "afterlife",
            "prayer",
            "meditation",
            "evil",
            "suffering",
            "synchronicity",
            "time travel",
            "parallel universes",
            "simulation",
            "what is time",
            "soul",
            "buddhism",
            "hinduism",
            "abrahamic",
            "indigenous cosmologies",
        },
    ),
    (
        "Particle Physics & Standard Model",
        {
            "neutrino",
            "higgs",
            "ckm",
            "yukawa",
            "wolfenstein",
            "fermion",
            "flavor",
            "standard model",
            "sm parameters",
            "baryogenesis",
            "proton decay",
            "grand unification",
            "qcd",
            "confinement",
            "mass tension",
        },
    ),
    (
        "Cosmology & Observation",
        {
            "cmb",
            "litebird",
            "desi",
            "inflation",
            "dark matter",
            "dark energy",
            "gravitational wave",
            "gw",
            "roman telescope",
            "observatory",
            "cosmological constant",
            "act dr6",
            "spt3g",
            "juno",
            "lisa",
            "sky",
            "birefringence",
        },
    ),
    (
        "Applied Domains",
        {
            "medicine",
            "biology",
            "climate",
            "ecology",
            "psychology",
            "justice",
            "economics",
            "education",
            "genetics",
            "materials",
            "astronomy",
            "earth",
            "neuroscience",
            "synthetic biology",
            "cancer",
            "agriculture",
            "disease",
            "infrastructure",
            "solar physics",
            "prison",
            "detention",
            "military",
            "food security",
        },
    ),
    (
        "Mathematics & Formal Methods",
        {
            "lean4",
            "z3",
            "proof",
            "proofs",
            "theorem",
            "topology",
            "topological",
            "formal",
            "mathematics",
            "algebraic",
            "spectral",
            "millennium prize",
        },
    ),
    (
        "Open Science & Community",
        {
            "peer review",
            "open science",
            "falsification",
            "letter",
            "letters",
            "community",
            "review",
            "reader mail",
            "faq",
            "what we cannot claim",
            "what we claim",
            "honest",
            "audit",
            "experimentalists",
            "physicist",
            "roast editorial",
            "repository overview",
            "science without",
        },
    ),
]

FOUNDATION_FALLBACK = "Foundation & Core Theory"


def main() -> None:
    entries = [
        *build_entries(POSTS_DIR, "post"),
        *build_entries(BOOKS_DIR, "book"),
    ]
    entries.sort(key=sort_tuple)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} reader entries to {OUTPUT_PATH}")


def build_entries(directory: Path, item_type: str) -> Iterable[dict]:
    for file_path in sorted(directory.glob("*.md")):
        raw_text = file_path.read_text(encoding="utf-8")
        title = extract_title(file_path.stem, raw_text)
        series = extract_series(file_path.stem, item_type)
        number = extract_number(file_path.stem, item_type)
        preview = extract_preview(raw_text)
        topic = classify_topic(file_path.stem, title, item_type)
        word_count = count_words(raw_text)
        relative_from_html = Path("..") / Path("..") / file_path.relative_to(REPO_ROOT)
        yield {
            "id": file_path.stem,
            "title": title,
            "type": item_type,
            "series": series,
            "number": number,
            "preview": preview,
            "word_count": word_count,
            "topic": topic,
            "path": relative_from_html.as_posix(),
        }


def extract_title(stem: str, raw_text: str) -> str:
    for line in raw_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return re.sub(r"^#+\s*", "", stripped).strip()
    return clean_filename_title(stem)


def clean_filename_title(stem: str) -> str:
    cleaned = stem
    cleaned = re.sub(r"^(post|book)-", "", cleaned)
    cleaned = re.sub(r"^\d+[a-z]?-", "", cleaned)
    cleaned = re.sub(r"^s\d+e\d+-", "", cleaned)
    cleaned = cleaned.replace("_", "-")
    cleaned = re.sub(r"-+", " ", cleaned).strip()
    return " ".join(part.capitalize() if part.islower() else part for part in cleaned.split())


def extract_series(stem: str, item_type: str) -> str:
    if item_type == "book":
        return "book"
    match = re.search(r"(s\d{2})e\d{3}", stem)
    if match:
        return match.group(1)
    if "thematic" in stem:
        return "thematic"
    if "epilog" in stem:
        return "epilog"
    return "general"


def extract_number(stem: str, item_type: str) -> int:
    if item_type == "book":
        book_order = {"book-falsification-decade-2025-2035": 1, "book-two-time-physics-and-the-unitary-manifold-parent": 2}
        return 100000 + book_order.get(stem, 999)
    match = re.search(r"post-(\d+)", stem)
    if match:
        return int(match.group(1))
    thematic_match = re.search(r"(\d+)", stem)
    if thematic_match:
        return int(thematic_match.group(1))
    if "thematic" in stem:
        return 900000
    if "omega" in stem:
        return 900010
    if "epilog" in stem:
        return 900020
    return 999999


def extract_preview(raw_text: str) -> str:
    lines: list[str] = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped in {"---", "***"}:
            continue
        stripped = re.sub(r"^[>*`\-]+\s*", "", stripped)
        stripped = re.sub(r"\*|_|`", "", stripped)
        lines.append(stripped)
    preview = " ".join(lines)
    preview = re.sub(r"\s+", " ", preview).strip()
    return preview[:200].rstrip()


def count_words(raw_text: str) -> int:
    text = re.sub(r"```[\s\S]*?```", " ", raw_text)
    words = re.findall(r"\b[\w'’.-]+\b", text)
    return len(words)


def classify_topic(stem: str, title: str, item_type: str) -> str:
    if item_type == "book":
        return "Books"
    haystack = f"{stem} {title}".lower().replace("-", " ")
    for topic, keywords in TOPIC_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            return topic
    return FOUNDATION_FALLBACK


def sort_tuple(entry: dict) -> tuple:
    type_rank = 0 if entry["type"] == "post" else 1
    return (type_rank, entry["number"], entry["title"].lower())


if __name__ == "__main__":
    main()
