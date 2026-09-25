# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Public-records source registry and standardized scan helpers for AXIOM Journalist."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from typing import Any, Callable
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from .source_ingest import normalize_tier_label


@dataclass(frozen=True)
class PublicRecordSource:
    slug: str
    display_name: str
    tier: str
    source_type: str
    query_template: str

    def build_query_url(self, query: str) -> str:
        return self.query_template.format(query=quote_plus(query.strip()))


PUBLIC_RECORD_SOURCES: dict[str, PublicRecordSource] = {
    'sec_edgar': PublicRecordSource(
        slug='sec_edgar',
        display_name='SEC EDGAR',
        tier='Tier 1 — Primary Record (court/regulatory/FOIA)',
        source_type='Regulatory filing',
        query_template='https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={query}',
    ),
    'courtlistener': PublicRecordSource(
        slug='courtlistener',
        display_name='CourtListener',
        tier='Tier 1 — Primary Record (court/regulatory/FOIA)',
        source_type='Court record',
        query_template='https://www.courtlistener.com/?q={query}',
    ),
    'fec': PublicRecordSource(
        slug='fec',
        display_name='FEC campaign finance',
        tier='Tier 1 — Primary Record (court/regulatory/FOIA)',
        source_type='Campaign finance filing',
        query_template='https://api.open.fec.gov/v1/names/candidates/?q={query}',
    ),
    'icij_offshore_leaks': PublicRecordSource(
        slug='icij_offshore_leaks',
        display_name='ICIJ Offshore Leaks',
        tier='Tier 3 — Secondary/Unverified',
        source_type='Investigative data',
        query_template='https://offshoreleaks.icij.org/search?q={query}',
    ),
    'opensanctions': PublicRecordSource(
        slug='opensanctions',
        display_name='OpenSanctions',
        tier='Tier 1 — Primary Record (court/regulatory/FOIA)',
        source_type='Sanctions and enforcement record',
        query_template='https://www.opensanctions.org/search/?q={query}',
    ),
    'opencorporates': PublicRecordSource(
        slug='opencorporates',
        display_name='OpenCorporates',
        tier='Tier 3 — Secondary/Unverified',
        source_type='Corporate registry aggregation',
        query_template='https://opencorporates.com/companies?q={query}',
    ),
    'propublica_nonprofit': PublicRecordSource(
        slug='propublica_nonprofit',
        display_name='ProPublica Nonprofit Explorer',
        tier='Tier 1 — Primary Record (court/regulatory/FOIA)',
        source_type='IRS 990 filing',
        query_template='https://projects.propublica.org/nonprofits/search?q={query}',
    ),
    'epa_echo': PublicRecordSource(
        slug='epa_echo',
        display_name='EPA ECHO',
        tier='Tier 1 — Primary Record (court/regulatory/FOIA)',
        source_type='Regulatory compliance record',
        query_template='https://echo.epa.gov/trends/comparative-maps-dashboards/state-comparative-map?search={query}',
    ),
    'govinfo': PublicRecordSource(
        slug='govinfo',
        display_name='GovInfo.gov',
        tier='Tier 1 — Primary Record (court/regulatory/FOIA)',
        source_type='Federal publication',
        query_template='https://www.govinfo.gov/app/search/{query}',
    ),
    'wayback_machine': PublicRecordSource(
        slug='wayback_machine',
        display_name='Wayback Machine',
        tier='Tier 3 — Secondary/Unverified',
        source_type='Web archive',
        query_template='https://webcache.allorigins.workers.dev/raw?url=https://web.archive.org/web/*/{query}',
    ),
    'ofac_sdn': PublicRecordSource(
        slug='ofac_sdn',
        display_name='OFAC SDN',
        tier='Tier 1 — Primary Record (court/regulatory/FOIA)',
        source_type='Sanctions designation',
        query_template='https://sanctionssearch.ofac.treas.gov/Details.aspx?id={query}',
    ),
}


def standardize_public_record(
    source: PublicRecordSource,
    entity_name: str,
    title: str,
    source_url: str,
    *,
    excerpt: str = '',
    retrieval_date: str | None = None,
    raw_metadata: dict[str, Any] | None = None,
    source_name: str | None = None,
    source_type: str | None = None,
    tier: str | None = None,
) -> dict[str, Any]:
    """Normalize a public-record result into AXIOM's structured record shape."""
    retrieved = retrieval_date or datetime.now(timezone.utc).isoformat(timespec='seconds')
    return {
        'entity_name': entity_name.strip(),
        'title': title.strip(),
        'source_name': (source_name or source.display_name).strip(),
        'source_url': source_url.strip(),
        'url_or_ref': source_url.strip(),
        'source_type': (source_type or source.source_type).strip(),
        'tier': normalize_tier_label(tier or source.tier),
        'retrieval_date': retrieved,
        'date': retrieved[:10],
        'excerpt': excerpt.strip(),
        'raw_metadata': dict(raw_metadata or {}),
        'source_slug': source.slug,
    }


def build_public_record_queries(query: str) -> list[dict[str, str]]:
    """Return query manifest entries for all registered public-record sources."""
    return [
        {
            'slug': source.slug,
            'display_name': source.display_name,
            'tier': source.tier,
            'source_type': source.source_type,
            'query_url': source.build_query_url(query),
        }
        for source in PUBLIC_RECORD_SOURCES.values()
    ]


def deduplicate_public_records(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Deduplicate records by (source_url + entity_name), linking duplicates by source slug."""
    deduped: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    seen: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        key = (
            str(record.get('source_url') or record.get('url_or_ref') or '').strip().casefold(),
            str(record.get('entity_name') or '').strip().casefold(),
        )
        if key in seen:
            original = seen[key]
            linked = list(original.get('linked_sources') or [])
            source_slug = str(record.get('source_slug') or '').strip()
            if source_slug and source_slug not in linked:
                linked.append(source_slug)
            original['linked_sources'] = linked
            duplicates.append(record)
            continue
        normalized = dict(record)
        normalized['linked_sources'] = [str(record.get('source_slug') or '').strip()] if record.get('source_slug') else []
        deduped.append(normalized)
        seen[key] = normalized
    return {'records': deduped, 'duplicates': duplicates}


def scan_public_records(
    entity_name: str,
    fetchers: dict[str, Callable[[str], list[dict[str, Any]]]] | None = None,
) -> dict[str, Any]:
    """Run a public-record scan using injected fetchers or return the query manifest."""
    manifest = build_public_record_queries(entity_name)
    if not fetchers:
        return {
            'entity_name': entity_name.strip(),
            'manifest': manifest,
            'records': [],
            'duplicates': [],
        }

    collected: list[dict[str, Any]] = []
    for item in manifest:
        fetcher = fetchers.get(item['slug']) if fetchers else None
        if fetcher is None:
            continue
        source = PUBLIC_RECORD_SOURCES[item['slug']]
        for row in fetcher(entity_name):
            collected.append(
                standardize_public_record(
                    source,
                    entity_name,
                    title=str(row.get('title') or row.get('source_name') or source.display_name),
                    source_url=str(row.get('source_url') or row.get('url_or_ref') or item['query_url']),
                    excerpt=str(row.get('excerpt') or ''),
                    retrieval_date=str(row.get('retrieval_date') or '') or None,
                    raw_metadata=dict(row.get('raw_metadata') or {}),
                    source_name=str(row.get('source_name') or source.display_name),
                    source_type=str(row.get('source_type') or source.source_type),
                    tier=str(row.get('tier') or source.tier),
                )
            )

    deduped = deduplicate_public_records(collected)
    return {
        'entity_name': entity_name.strip(),
        'manifest': manifest,
        'records': deduped['records'],
        'duplicates': deduped['duplicates'],
    }


def export_public_record_scan(scan: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-serializable export packet for a public-record scan."""
    return {
        'entity_name': scan.get('entity_name', ''),
        'source_count': len(scan.get('records') or []),
        'duplicate_count': len(scan.get('duplicates') or []),
        'manifest': scan.get('manifest') or [],
        'records': scan.get('records') or [],
    }


def public_record_source_catalog() -> list[dict[str, Any]]:
    """Return the full source catalog as dictionaries."""
    return [asdict(source) for source in PUBLIC_RECORD_SOURCES.values()]


def _json_request(
    url: str,
    *,
    method: str = 'GET',
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 10.0,
) -> dict[str, Any] | list[Any] | None:
    request_headers = {'User-Agent': 'AxiomZero-AXIOM-Journalist/1.0', **(headers or {})}
    data = None
    if payload is not None:
        request_headers.setdefault('Content-Type', 'application/json')
        data = json.dumps(payload).encode('utf-8')
    request = Request(url, data=data, headers=request_headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception:
        return None


def fetch_sec_edgar(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Fetch SEC EDGAR search hits for a named entity or issuer."""
    source = PUBLIC_RECORD_SOURCES['sec_edgar']
    payload = _json_request(
        'https://efts.sec.gov/LATEST/search-index',
        headers={'Accept': 'application/json'},
        payload={'q': query.strip(), 'forms': ['10-K', '10-Q', '8-K', '4', 'SC-13D'], 'from': 0, 'size': max(1, int(limit))},
        method='POST',
    )
    hits = []
    if not isinstance(payload, dict):
        return hits
    for item in list(payload.get('hits', {}).get('hits', []) or [])[:limit]:
        record = item.get('_source') if isinstance(item, dict) else {}
        if not isinstance(record, dict):
            continue
        title = str(record.get('display_names') or record.get('file_type') or record.get('entityName') or 'SEC filing')
        accession = str(record.get('adsh') or record.get('ciks') or '')
        link = str(record.get('linkToFilingDetails') or '')
        if link and link.startswith('/'):
            link = f'https://www.sec.gov{link}'
        url = link or source.build_query_url(query)
        hits.append(standardize_public_record(
            source,
            query,
            title=title,
            source_url=url,
            excerpt=str(record.get('display_names') or record.get('file_type') or ''),
            retrieval_date=str(record.get('file_date') or '') or None,
            raw_metadata={'adsh': accession, 'cik': record.get('ciks'), 'file_type': record.get('file_type')},
        ))
    return hits


def fetch_opensanctions(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Fetch OpenSanctions entity matches."""
    source = PUBLIC_RECORD_SOURCES['opensanctions']
    payload = _json_request(f'https://api.opensanctions.org/search/default?q={quote_plus(query.strip())}&limit={max(1, int(limit))}')
    results = []
    if not isinstance(payload, dict):
        return results
    for item in list(payload.get('results') or [])[:limit]:
        if not isinstance(item, dict):
            continue
        properties = item.get('properties') if isinstance(item.get('properties'), dict) else {}
        first_caption = ''
        topics = item.get('topics') if isinstance(item.get('topics'), list) else []
        if topics:
            first_caption = ', '.join(str(topic) for topic in topics[:3])
        caption = str(item.get('caption') or properties.get('name') or item.get('id') or 'OpenSanctions record')
        entity_url = str(item.get('openSanctionsUrl') or item.get('link') or '')
        url = entity_url or source.build_query_url(query)
        results.append(standardize_public_record(
            source,
            query,
            title=caption,
            source_url=url,
            excerpt=first_caption,
            raw_metadata={'id': item.get('id'), 'schema': item.get('schema'), 'topics': topics},
        ))
    return results


def fetch_icij_offshore_leaks(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Fetch ICIJ Offshore Leaks reconciliation matches."""
    source = PUBLIC_RECORD_SOURCES['icij_offshore_leaks']
    payload = _json_request(
        'https://offshoreleaks.icij.org/api/v1/reconcile',
        method='POST',
        payload={'queries': {'q0': {'query': query.strip(), 'limit': max(1, int(limit))}}},
    )
    results = []
    if not isinstance(payload, dict):
        return results
    query_results = payload.get('q0', {}).get('result') if isinstance(payload.get('q0'), dict) else []
    for item in list(query_results or [])[:limit]:
        if not isinstance(item, dict):
            continue
        title = str(item.get('name') or item.get('id') or 'ICIJ Offshore Leaks record')
        score = item.get('score')
        excerpt = f"type={item.get('type') or 'unknown'}; score={score}" if score is not None else str(item.get('type') or '')
        record_id = str(item.get('id') or '')
        url = f'https://offshoreleaks.icij.org/nodes/{record_id}' if record_id else source.build_query_url(query)
        results.append(standardize_public_record(
            source,
            query,
            title=title,
            source_url=url,
            excerpt=excerpt,
            raw_metadata={'id': record_id, 'type': item.get('type'), 'score': score},
        ))
    return results


def fetch_courtlistener(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Fetch CourtListener search hits."""
    source = PUBLIC_RECORD_SOURCES['courtlistener']
    payload = _json_request(f'https://www.courtlistener.com/api/rest/v4/search/?q={quote_plus(query.strip())}&page_size={max(1, int(limit))}')
    results = []
    if not isinstance(payload, dict):
        return results
    for item in list(payload.get('results') or [])[:limit]:
        if not isinstance(item, dict):
            continue
        title = str(item.get('caseName') or item.get('case_name') or item.get('docketNumber') or 'CourtListener result')
        url = str(item.get('absolute_url') or '')
        if url and url.startswith('/'):
            url = f'https://www.courtlistener.com{url}'
        excerpt = str(item.get('snippet') or item.get('court') or '')
        results.append(standardize_public_record(
            source,
            query,
            title=title,
            source_url=url or source.build_query_url(query),
            excerpt=excerpt,
            retrieval_date=str(item.get('dateFiled') or item.get('date_filed') or '') or None,
            raw_metadata={'docket': item.get('docketNumber'), 'court': item.get('court')},
        ))
    return results


LIVE_PUBLIC_RECORD_FETCHERS: dict[str, Callable[[str], list[dict[str, Any]]]] = {
    'sec_edgar': fetch_sec_edgar,
    'courtlistener': fetch_courtlistener,
    'icij_offshore_leaks': fetch_icij_offshore_leaks,
    'opensanctions': fetch_opensanctions,
}
