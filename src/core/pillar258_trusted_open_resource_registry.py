# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 258 — Trusted Open Resource Registry (adjacent research track).

Adjacent applied research track (non-hardgate): deterministic registry of 100
trusted, free online resources plus query/prompt helpers for repository
research workflows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__provenance__ = {
    "pillar": 258,
    "title": "Trusted Open Resource Registry",
    "author": "ThomasCory Walker-Pearson",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT TRACK — trusted-source registry for research orchestration",
}

ADJACENCY_TRACK_LABEL = "NON_HARDGATE_ADJACENT"
OPERATIONAL_MODULE: bool = True
OPERATIONAL_MODULE_CATEGORY: str = "RESOURCE_REGISTRY"

N_W = 5
K_CS = 74
C_S = 12.0 / 37.0

CATEGORY_ACADEMIC = "academic_literature"
CATEGORY_DATA = "open_data_statistics"
CATEGORY_GOVERNMENT = "government_public_agency"
CATEGORY_LIBRARY = "digital_library_knowledge_base"
CATEGORY_TECH = "open_source_technology"
CATEGORY_BIOSCI = "life_sciences_medical"
CATEGORY_FACTCHECK = "fact_checking_journalism_legal"

ALL_CATEGORIES = (
    CATEGORY_ACADEMIC,
    CATEGORY_DATA,
    CATEGORY_GOVERNMENT,
    CATEGORY_LIBRARY,
    CATEGORY_TECH,
    CATEGORY_BIOSCI,
    CATEGORY_FACTCHECK,
)


@dataclass(frozen=True)
class TrustedResource:
    resource_id: int
    name: str
    category: str
    url: str
    description: str
    tags: tuple[str, ...]
    api_friendly: bool = False


def _r(
    resource_id: int,
    name: str,
    category: str,
    url: str,
    description: str,
    tags: tuple[str, ...],
    api_friendly: bool = False,
) -> TrustedResource:
    return TrustedResource(
        resource_id=resource_id,
        name=name,
        category=category,
        url=url,
        description=description,
        tags=tags,
        api_friendly=api_friendly,
    )


RESOURCES: tuple[TrustedResource, ...] = (
    _r(1, "Google Scholar", CATEGORY_ACADEMIC, "https://scholar.google.com", "Global academic search index.", ("academic", "papers", "citations")),
    _r(2, "PubMed / MEDLINE", CATEGORY_ACADEMIC, "https://pubmed.ncbi.nlm.nih.gov", "NIH biomedical literature database.", ("medical", "biomedical", "papers"), True),
    _r(3, "arXiv", CATEGORY_ACADEMIC, "https://arxiv.org", "Open preprint repository across STEM.", ("physics", "math", "preprints"), True),
    _r(4, "CORE", CATEGORY_ACADEMIC, "https://core.ac.uk", "Open-access paper aggregator.", ("open-access", "papers", "journals"), True),
    _r(5, "Dimensions", CATEGORY_ACADEMIC, "https://www.dimensions.ai", "Research publication and citation platform.", ("citations", "publications", "research")),
    _r(6, "Semantic Scholar", CATEGORY_ACADEMIC, "https://www.semanticscholar.org", "AI-assisted literature discovery.", ("ai", "papers", "citations"), True),
    _r(7, "BASE", CATEGORY_ACADEMIC, "https://www.base-search.net", "Large open-access academic search engine.", ("open-access", "repositories", "academic")),
    _r(8, "DOAJ", CATEGORY_ACADEMIC, "https://doaj.org", "Curated open-access journal directory.", ("journals", "open-access", "peer-reviewed")),
    _r(9, "bioRxiv", CATEGORY_ACADEMIC, "https://www.biorxiv.org", "Biology preprint server.", ("biology", "preprints", "life-science")),
    _r(10, "medRxiv", CATEGORY_ACADEMIC, "https://www.medrxiv.org", "Health-science preprint server.", ("health", "preprints", "medical")),
    _r(11, "SSRN", CATEGORY_ACADEMIC, "https://www.ssrn.com", "Social-science and legal preprint network.", ("social-science", "economics", "law")),
    _r(12, "OpenAlex", CATEGORY_ACADEMIC, "https://openalex.org", "Open research graph for papers/authors/institutions.", ("research-graph", "citations", "metadata"), True),
    _r(13, "ERIC", CATEGORY_ACADEMIC, "https://eric.ed.gov", "Education research library.", ("education", "policy", "research")),
    _r(14, "PhilPapers", CATEGORY_ACADEMIC, "https://philpapers.org", "Philosophy bibliography and index.", ("philosophy", "humanities", "papers")),
    _r(15, "PLOS ONE", CATEGORY_ACADEMIC, "https://journals.plos.org/plosone", "Open-access multidisciplinary journal.", ("journal", "science", "open-access")),
    _r(16, "Our World in Data", CATEGORY_DATA, "https://ourworldindata.org", "Global data visualizations and datasets.", ("global", "data", "health", "climate"), True),
    _r(17, "World Bank Open Data", CATEGORY_DATA, "https://data.worldbank.org", "Development and macroeconomic indicators.", ("economics", "development", "country-data"), True),
    _r(18, "UN Data", CATEGORY_DATA, "https://data.un.org", "United Nations statistical databases.", ("un", "statistics", "demographics")),
    _r(19, "IMF Data", CATEGORY_DATA, "https://www.imf.org/en/Data", "Global financial and economic statistics.", ("finance", "economics", "macroeconomics")),
    _r(20, "OECD Data", CATEGORY_DATA, "https://data.oecd.org", "Economic and social indicators.", ("oecd", "economics", "social-data")),
    _r(21, "Statista (Public)", CATEGORY_DATA, "https://www.statista.com", "Public-tier market and industry charts.", ("markets", "industry", "statistics")),
    _r(22, "WHO Global Health Observatory", CATEGORY_DATA, "https://www.who.int/data/gho", "Global public-health statistics.", ("health", "epidemiology", "public-health"), True),
    _r(23, "Eurostat", CATEGORY_DATA, "https://ec.europa.eu/eurostat", "EU statistics portal.", ("europe", "economics", "statistics")),
    _r(24, "UNESCO Institute for Statistics", CATEGORY_DATA, "https://uis.unesco.org", "Education/science/culture statistics.", ("education", "science", "culture")),
    _r(25, "FAOSTAT", CATEGORY_DATA, "https://www.fao.org/faostat", "Food and agriculture datasets.", ("agriculture", "food-security", "climate")),
    _r(26, "Kaggle Datasets", CATEGORY_DATA, "https://www.kaggle.com/datasets", "Public machine-learning datasets.", ("machine-learning", "datasets", "data-science")),
    _r(27, "Registry of Open Data on AWS", CATEGORY_DATA, "https://registry.opendata.aws", "Large public datasets hosted on AWS.", ("cloud", "genomics", "satellite")),
    _r(28, "Google Dataset Search", CATEGORY_DATA, "https://datasetsearch.research.google.com", "Dataset discovery search engine.", ("dataset-search", "metadata", "discovery")),
    _r(29, "UCI ML Repository", CATEGORY_DATA, "https://archive.ics.uci.edu", "Canonical ML benchmark datasets.", ("machine-learning", "benchmarks", "datasets")),
    _r(30, "Open Knowledge Foundation (CKAN)", CATEGORY_DATA, "https://okfn.org", "Open-data ecosystem and CKAN portal standard.", ("open-data", "ckan", "portals")),
    _r(31, "Data.gov", CATEGORY_GOVERNMENT, "https://www.data.gov", "U.S. federal open-data portal.", ("us-government", "datasets", "public-policy"), True),
    _r(32, "CDC", CATEGORY_GOVERNMENT, "https://www.cdc.gov", "U.S. public health and epidemiology resources.", ("health", "epidemiology", "public-agency")),
    _r(33, "NASA Open Data Portal", CATEGORY_GOVERNMENT, "https://data.nasa.gov", "NASA open science and space datasets.", ("space", "earth-science", "datasets"), True),
    _r(34, "NOAA Data Catalog", CATEGORY_GOVERNMENT, "https://www.noaa.gov/data", "Weather/ocean/climate records.", ("climate", "weather", "ocean")),
    _r(35, "U.S. Census Bureau", CATEGORY_GOVERNMENT, "https://www.census.gov/data.html", "U.S. demographic and economic data.", ("demographics", "economics", "census")),
    _r(36, "BLS", CATEGORY_GOVERNMENT, "https://www.bls.gov/data", "Labor and employment statistics.", ("labor", "economics", "employment")),
    _r(37, "USGS ScienceBase", CATEGORY_GOVERNMENT, "https://www.sciencebase.gov", "Earth science and mapping data.", ("geology", "mapping", "earth-science")),
    _r(38, "Data.gov.uk", CATEGORY_GOVERNMENT, "https://www.data.gov.uk", "UK government open-data portal.", ("uk", "government-data", "policy")),
    _r(39, "Open Data Portal of the EU", CATEGORY_GOVERNMENT, "https://data.europa.eu", "European Union institutional data.", ("eu", "government-data", "open-data")),
    _r(40, "EPA Environmental Data", CATEGORY_GOVERNMENT, "https://www.epa.gov/environmental-topics/data-and-tools", "Environmental quality and toxic release data.", ("environment", "air", "water")),
    _r(41, "SEC EDGAR", CATEGORY_GOVERNMENT, "https://www.sec.gov/edgar", "U.S. corporate filings and disclosures.", ("finance", "filings", "corporate")),
    _r(42, "USPTO Patent Search", CATEGORY_GOVERNMENT, "https://www.uspto.gov/patents/search", "U.S. patent and trademark search.", ("patents", "innovation", "ip")),
    _r(43, "Espacenet", CATEGORY_GOVERNMENT, "https://worldwide.espacenet.com", "European patent database.", ("patents", "innovation", "europe")),
    _r(44, "EIA", CATEGORY_GOVERNMENT, "https://www.eia.gov", "Energy production and consumption statistics.", ("energy", "economics", "infrastructure")),
    _r(45, "NIST Data Gateway", CATEGORY_GOVERNMENT, "https://data.nist.gov", "Standards and measurement datasets.", ("standards", "materials", "metrology")),
    _r(46, "Wikipedia / Wikimedia Commons", CATEGORY_LIBRARY, "https://www.wikipedia.org", "Open encyclopedia and media commons.", ("encyclopedia", "reference", "knowledge"), True),
    _r(47, "Internet Archive", CATEGORY_LIBRARY, "https://archive.org", "Historical web/books/audio archives.", ("archives", "history", "books")),
    _r(48, "Stanford Encyclopedia of Philosophy", CATEGORY_LIBRARY, "https://plato.stanford.edu", "Peer-reviewed philosophy encyclopedia.", ("philosophy", "reference", "peer-reviewed")),
    _r(49, "Britannica (Public)", CATEGORY_LIBRARY, "https://www.britannica.com", "Editorial reference encyclopedia.", ("encyclopedia", "reference", "education")),
    _r(50, "Project Gutenberg", CATEGORY_LIBRARY, "https://www.gutenberg.org", "Public-domain ebooks collection.", ("books", "public-domain", "texts")),
    _r(51, "WorldCat", CATEGORY_LIBRARY, "https://www.worldcat.org", "Global library holdings index.", ("libraries", "catalog", "books")),
    _r(52, "Library of Congress", CATEGORY_LIBRARY, "https://www.loc.gov/collections", "Digital collections and manuscripts.", ("archives", "history", "manuscripts")),
    _r(53, "Smithsonian Open Access", CATEGORY_LIBRARY, "https://www.si.edu/openaccess", "Museum open assets and datasets.", ("museums", "3d", "culture")),
    _r(54, "Europeana", CATEGORY_LIBRARY, "https://www.europeana.eu", "European cultural heritage portal.", ("culture", "archives", "europe")),
    _r(55, "Digital Public Library of America", CATEGORY_LIBRARY, "https://dp.la", "U.S. libraries/archives aggregator.", ("libraries", "archives", "usa")),
    _r(56, "Gallica", CATEGORY_LIBRARY, "https://gallica.bnf.fr", "National Library of France digital library.", ("france", "books", "archives")),
    _r(57, "British Library Digital Collections", CATEGORY_LIBRARY, "https://www.bl.uk/collection-guides/digital-collections", "British Library digital archives.", ("uk", "archives", "manuscripts")),
    _r(58, "Scholarpedia", CATEGORY_LIBRARY, "http://www.scholarpedia.org", "Expert-maintained peer-reviewed encyclopedia.", ("peer-reviewed", "encyclopedia", "science")),
    _r(59, "Wolfram Alpha", CATEGORY_LIBRARY, "https://www.wolframalpha.com", "Computational knowledge engine.", ("computation", "math", "science"), True),
    _r(60, "Wikidata", CATEGORY_LIBRARY, "https://www.wikidata.org", "Open structured knowledge graph.", ("knowledge-graph", "linked-data", "semantic-web"), True),
    _r(61, "GitHub", CATEGORY_TECH, "https://github.com", "Open-source code hosting and collaboration.", ("code", "open-source", "version-control"), True),
    _r(62, "Hugging Face", CATEGORY_TECH, "https://huggingface.co", "Open AI models, datasets, and apps.", ("ai", "models", "datasets"), True),
    _r(63, "GitLab Public Repositories", CATEGORY_TECH, "https://gitlab.com/explore/projects", "Public GitLab project index.", ("code", "devops", "git")),
    _r(64, "SourceForge", CATEGORY_TECH, "https://sourceforge.net", "Open-source software distribution.", ("software", "open-source", "downloads")),
    _r(65, "CRAN", CATEGORY_TECH, "https://cran.r-project.org", "R package repository.", ("r", "packages", "statistics")),
    _r(66, "PyPI", CATEGORY_TECH, "https://pypi.org", "Python package index.", ("python", "packages", "software"), True),
    _r(67, "NPM Registry", CATEGORY_TECH, "https://www.npmjs.com", "Node.js package registry.", ("javascript", "node", "packages"), True),
    _r(68, "Docker Hub", CATEGORY_TECH, "https://hub.docker.com", "Container image registry.", ("containers", "devops", "infrastructure")),
    _r(69, "W3C", CATEGORY_TECH, "https://www.w3.org", "Web standards specifications.", ("web-standards", "html", "css")),
    _r(70, "IETF RFCs", CATEGORY_TECH, "https://www.rfc-editor.org", "Internet standards and RFC archive.", ("networking", "standards", "protocols")),
    _r(71, "Linux Foundation", CATEGORY_TECH, "https://www.linuxfoundation.org", "Open-source project ecosystem.", ("linux", "open-source", "foundation")),
    _r(72, "Apache Software Foundation", CATEGORY_TECH, "https://www.apache.org", "Apache open-source projects.", ("apache", "open-source", "big-data")),
    _r(73, "Mozilla Developer Network", CATEGORY_TECH, "https://developer.mozilla.org", "Web developer reference docs.", ("documentation", "web", "javascript")),
    _r(74, "Stack Overflow / Stack Exchange", CATEGORY_TECH, "https://stackoverflow.com", "Community Q&A knowledge archive.", ("q-and-a", "debugging", "software")),
    _r(75, "Papers with Code", CATEGORY_TECH, "https://paperswithcode.com", "ML papers linked to implementations.", ("machine-learning", "papers", "code")),
    _r(76, "PubChem", CATEGORY_BIOSCI, "https://pubchem.ncbi.nlm.nih.gov", "Open chemical compound database.", ("chemistry", "molecules", "bioinformatics"), True),
    _r(77, "ChemSpider", CATEGORY_BIOSCI, "https://www.chemspider.com", "Chemical structure database.", ("chemistry", "structures", "compounds")),
    _r(78, "ClinicalTrials.gov", CATEGORY_BIOSCI, "https://clinicaltrials.gov", "Global clinical trials registry.", ("clinical-trials", "medicine", "health")),
    _r(79, "GenBank", CATEGORY_BIOSCI, "https://www.ncbi.nlm.nih.gov/genbank", "Public DNA sequence archive.", ("genomics", "dna", "bioinformatics"), True),
    _r(80, "RCSB Protein Data Bank", CATEGORY_BIOSCI, "https://www.rcsb.org", "3D macromolecular structures.", ("proteins", "structures", "biology"), True),
    _r(81, "DrugBank (Public)", CATEGORY_BIOSCI, "https://go.drugbank.com", "Drug and target knowledge base.", ("drugs", "targets", "pharmacology")),
    _r(82, "UniProt", CATEGORY_BIOSCI, "https://www.uniprot.org", "Protein sequence/function resource.", ("proteins", "sequence", "annotation"), True),
    _r(83, "KEGG", CATEGORY_BIOSCI, "https://www.kegg.jp", "Pathways and genomic functions.", ("pathways", "genomics", "systems-biology")),
    _r(84, "Ensembl", CATEGORY_BIOSCI, "https://www.ensembl.org", "Vertebrate genome browser.", ("genome", "comparative-genomics", "evolution"), True),
    _r(85, "Cochrane Library (Open Abstracts)", CATEGORY_BIOSCI, "https://www.cochranelibrary.com", "Evidence synthesis for healthcare.", ("evidence", "systematic-reviews", "medicine")),
    _r(86, "DailyMed", CATEGORY_BIOSCI, "https://dailymed.nlm.nih.gov", "Official drug labeling.", ("drug-labels", "medicine", "fda")),
    _r(87, "TOXNET (via NLM)", CATEGORY_BIOSCI, "https://www.nlm.nih.gov/toxnet/index.html", "Toxicology and hazard information.", ("toxicology", "environmental-health", "chemicals")),
    _r(88, "GISAID", CATEGORY_BIOSCI, "https://gisaid.org", "Influenza/coronavirus sequence sharing.", ("virology", "genomics", "surveillance")),
    _r(89, "Cancer.gov Data", CATEGORY_BIOSCI, "https://www.cancer.gov", "NCI cancer datasets and resources.", ("oncology", "cancer", "genomics")),
    _r(90, "Human Protein Atlas", CATEGORY_BIOSCI, "https://www.proteinatlas.org", "Human protein expression atlas.", ("proteomics", "tissues", "cells")),
    _r(91, "FactCheck.org", CATEGORY_FACTCHECK, "https://www.factcheck.org", "Non-partisan political fact-checking.", ("fact-checking", "politics", "claims")),
    _r(92, "PolitiFact", CATEGORY_FACTCHECK, "https://www.politifact.com", "Fact-check ratings for public claims.", ("fact-checking", "politics", "media")),
    _r(93, "Snopes", CATEGORY_FACTCHECK, "https://www.snopes.com", "Misinformation and rumor verification.", ("misinformation", "verification", "claims")),
    _r(94, "OpenSecrets", CATEGORY_FACTCHECK, "https://www.opensecrets.org", "Money-in-politics transparency data.", ("campaign-finance", "politics", "transparency")),
    _r(95, "ProPublica Data Store", CATEGORY_FACTCHECK, "https://www.propublica.org/datastore", "Investigative journalism datasets.", ("journalism", "investigations", "datasets")),
    _r(96, "Legal Information Institute", CATEGORY_FACTCHECK, "https://www.law.cornell.edu", "Open U.S. legal corpus.", ("law", "us-code", "case-law")),
    _r(97, "EUR-Lex", CATEGORY_FACTCHECK, "https://eur-lex.europa.eu", "Official EU law and legislation.", ("law", "eu", "regulation")),
    _r(98, "HUD User Open Data", CATEGORY_FACTCHECK, "https://www.huduser.gov/portal/datasets.html", "Housing and development data.", ("housing", "policy", "economics")),
    _r(99, "Pew Research Center", CATEGORY_FACTCHECK, "https://www.pewresearch.org", "Non-partisan social research.", ("public-opinion", "demographics", "social-research")),
    _r(100, "National Academies Press", CATEGORY_FACTCHECK, "https://nap.nationalacademies.org", "Free reports from U.S. National Academies.", ("science-policy", "reports", "engineering")),
)

_BY_CATEGORY: dict[str, tuple[TrustedResource, ...]] = {
    category: tuple(r for r in RESOURCES if r.category == category)
    for category in ALL_CATEGORIES
}


def trusted_resources() -> tuple[TrustedResource, ...]:
    return RESOURCES


def resources_by_category(category: str) -> tuple[TrustedResource, ...]:
    key = category.strip().lower()
    if key not in _BY_CATEGORY:
        raise ValueError(f"Unknown category '{category}'. Expected one of {ALL_CATEGORIES}.")
    return _BY_CATEGORY[key]


def _topic_tokens(topic: str) -> set[str]:
    raw = topic.lower().replace("-", " ").replace("/", " ")
    return {t for t in raw.split() if t}


def suggest_resources_for_topic(topic: str, limit: int = 12, api_first: bool = True) -> list[TrustedResource]:
    if limit <= 0:
        raise ValueError("limit must be > 0")

    tokens = _topic_tokens(topic)
    if not tokens:
        return list(RESOURCES[:limit])

    scored: list[tuple[int, int, int, TrustedResource]] = []
    for item in RESOURCES:
        haystack = " ".join((item.name, item.description, " ".join(item.tags))).lower()
        token_hits = sum(1 for token in tokens if token in haystack)
        category_hit = 1 if any(token in item.category for token in tokens) else 0
        api_bonus = 1 if (api_first and item.api_friendly) else 0
        scored.append((token_hits, category_hit, api_bonus, item))

    scored.sort(key=lambda row: (row[0], row[1], row[2], -row[3].resource_id), reverse=True)
    best = [row[3] for row in scored if row[0] > 0]
    if len(best) < limit:
        seen = {r.resource_id for r in best}
        for item in RESOURCES:
            if item.resource_id not in seen:
                best.append(item)
            if len(best) >= limit:
                break
    return best[:limit]


def build_ai_research_prompt(topic: str, *, limit: int = 12, api_first: bool = True) -> str:
    selected = suggest_resources_for_topic(topic=topic, limit=limit, api_first=api_first)
    lines = [
        f"Research topic: {topic}",
        "Instructions:",
        "1) Prioritize authoritative primary sources.",
        "2) Distinguish peer-reviewed evidence vs commentary.",
        "3) Record source URLs with retrieval dates.",
        "4) Flag disagreements and unresolved uncertainties.",
        "5) Produce a concise synthesis with falsifiable claims.",
        "Priority resources:",
    ]
    for item in selected:
        api_note = " [API-friendly]" if item.api_friendly else ""
        lines.append(f"- ({item.resource_id}) {item.name}{api_note} — {item.url}")
    return "\n".join(lines)


def category_summary() -> dict[str, int]:
    return {category: len(entries) for category, entries in _BY_CATEGORY.items()}


def pillar258_trusted_resource_registry_report() -> dict[str, Any]:
    summary = category_summary()
    return {
        "pillar": 258,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "provenance": __provenance__,
        "resource_total": len(RESOURCES),
        "category_count": len(ALL_CATEGORIES),
        "category_summary": summary,
        "api_friendly_total": sum(1 for r in RESOURCES if r.api_friendly),
        "integrity": {
            "all_categories_present": all(summary.get(c, 0) > 0 for c in ALL_CATEGORIES),
            "unique_resource_ids": len({r.resource_id for r in RESOURCES}) == len(RESOURCES),
            "unique_names": len({r.name for r in RESOURCES}) == len(RESOURCES),
        },
    }


__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "N_W",
    "K_CS",
    "C_S",
    "CATEGORY_ACADEMIC",
    "CATEGORY_DATA",
    "CATEGORY_GOVERNMENT",
    "CATEGORY_LIBRARY",
    "CATEGORY_TECH",
    "CATEGORY_BIOSCI",
    "CATEGORY_FACTCHECK",
    "ALL_CATEGORIES",
    "TrustedResource",
    "trusted_resources",
    "resources_by_category",
    "suggest_resources_for_topic",
    "build_ai_research_prompt",
    "category_summary",
    "pillar258_trusted_resource_registry_report",
]
