# SPDX-License-Identifier: MIT
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""
app/db/cases.py
===============
SQLite persistence for AXIOM investigation cases.

Schema
------
  cases       (id, title, lead, journalist, created_at, status, notes, brief_cache)
  entities    (id, case_id, name, entity_type, description, stated_position, notes)
  contradictions (id, entity_id, text)
  sources     (id, case_id, title, tier, source_type, url_or_ref, date, excerpt, notes)
  claims      (id, case_id, statement, legal_risks, notes)
  claim_sources (claim_id, source_id)
  claim_entities (claim_id, entity_name)
  open_questions (id, case_id, question)
  watchlist_entries (id, case_id, name, entity_type, notes)
  watchlist_hits (id, entry_id, source_name, title, url_or_ref, excerpt, retrieval_date)
  audit_log   (id, case_id, action, actor, payload_json, created_at)
  deletion_log (id, case_id, action, actor, payload_json, created_at)

Theory, methodology: ThomasCory Walker-Pearson / AxiomZero.
Implementation: GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent.parent / "data" / "axiom_cases.db"


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    conn = _connect(db_path)
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS cases (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                lead        TEXT NOT NULL,
                journalist  TEXT DEFAULT '',
                created_at  TEXT NOT NULL,
                status      TEXT DEFAULT 'Active',
                notes       TEXT DEFAULT '',
                brief_cache TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS entities (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id         INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                name            TEXT NOT NULL,
                entity_type     TEXT DEFAULT 'Other',
                description     TEXT DEFAULT '',
                stated_position TEXT DEFAULT '',
                notes           TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS contradictions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id   INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
                text        TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sources (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id     INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                title       TEXT NOT NULL,
                tier        INTEGER DEFAULT 0,
                source_type TEXT DEFAULT '',
                url_or_ref  TEXT DEFAULT '',
                date        TEXT DEFAULT '',
                excerpt     TEXT DEFAULT '',
                notes       TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS claims (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id     INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                statement   TEXT NOT NULL,
                legal_risks TEXT DEFAULT 'NONE',
                notes       TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS claim_sources (
                claim_id    INTEGER NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
                source_id   INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                PRIMARY KEY (claim_id, source_id)
            );
            CREATE TABLE IF NOT EXISTS claim_entities (
                claim_id    INTEGER NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
                entity_name TEXT NOT NULL,
                PRIMARY KEY (claim_id, entity_name)
            );
            CREATE TABLE IF NOT EXISTS open_questions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id     INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                question    TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS watchlist_entries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id     INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                name        TEXT NOT NULL,
                entity_type TEXT DEFAULT 'Other',
                notes       TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS watchlist_hits (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id       INTEGER NOT NULL REFERENCES watchlist_entries(id) ON DELETE CASCADE,
                source_name    TEXT DEFAULT '',
                title          TEXT NOT NULL,
                url_or_ref     TEXT DEFAULT '',
                excerpt        TEXT DEFAULT '',
                retrieval_date TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS audit_log (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id      INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
                action       TEXT NOT NULL,
                actor        TEXT DEFAULT 'system',
                payload_json TEXT DEFAULT '{}',
                created_at   TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS deletion_log (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id      INTEGER NOT NULL,
                action       TEXT NOT NULL,
                actor        TEXT DEFAULT 'system',
                payload_json TEXT DEFAULT '{}',
                created_at   TEXT NOT NULL
            );
        """)
    conn.close()


def _log_action(
    conn: sqlite3.Connection,
    case_id: int,
    action: str,
    *,
    actor: str = 'system',
    payload: Optional[dict] = None,
) -> None:
    from datetime import datetime

    conn.execute(
        "INSERT INTO audit_log (case_id, action, actor, payload_json, created_at) VALUES (?,?,?,?,?)",
        (
            case_id,
            action,
            actor,
            json.dumps(payload or {}, sort_keys=True),
            datetime.now().isoformat(timespec="seconds"),
        ),
    )


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------

def create_case(title: str, lead: str, journalist: str = "",
                created_at: str = "", status: str = "Active",
                actor: str = "system",
                db_path: Path = DB_PATH) -> int:
    """Insert a new case; returns its id."""
    from datetime import datetime
    if not created_at:
        created_at = datetime.now().isoformat(timespec="seconds")
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO cases (title, lead, journalist, created_at, status) VALUES (?,?,?,?,?)",
            (title, lead, journalist, created_at, status),
        )
        case_id = cur.lastrowid
        _log_action(conn, case_id, 'case_created', actor=actor, payload={
            'title': title,
            'lead': lead,
            'journalist': journalist,
            'status': status,
        })
    conn.close()
    return case_id


def list_cases(db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT id, title, journalist, created_at, status FROM cases ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_case(case_id: int, db_path: Path = DB_PATH) -> Optional[dict]:
    conn = _connect(db_path)
    row = conn.execute("SELECT * FROM cases WHERE id=?", (case_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_case(case_id: int, actor: str = 'system', db_path: Path = DB_PATH) -> None:
    from datetime import datetime

    conn = _connect(db_path)
    with conn:
        # `audit_log` rows are cascade-deleted with their case, so a
        # 'case_deleted' entry written there would be erased by the DELETE
        # below. Record the deletion tombstone in `deletion_log`, which has
        # no foreign-key relationship to `cases` and therefore survives.
        conn.execute(
            "INSERT INTO deletion_log (case_id, action, actor, payload_json, created_at) VALUES (?,?,?,?,?)",
            (
                case_id,
                'case_deleted',
                actor,
                json.dumps({}, sort_keys=True),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.execute("DELETE FROM cases WHERE id=?", (case_id,))
    conn.close()


def list_deletion_log(case_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT id, action, actor, payload_json, created_at FROM deletion_log WHERE case_id=? ORDER BY id",
        (case_id,),
    ).fetchall()
    conn.close()
    records: list[dict] = []
    for row in rows:
        item = dict(row)
        item['payload'] = json.loads(item.pop('payload_json') or '{}')
        records.append(item)
    return records


def save_brief(case_id: int, brief_text: str, db_path: Path = DB_PATH) -> None:
    conn = _connect(db_path)
    with conn:
        conn.execute("UPDATE cases SET brief_cache=? WHERE id=?", (brief_text, case_id))
        _log_action(conn, case_id, 'brief_saved', payload={'length': len(brief_text)})
    conn.close()


def update_case(
    case_id: int,
    *,
    title: str | None = None,
    lead: str | None = None,
    journalist: str | None = None,
    status: str | None = None,
    notes: str | None = None,
    actor: str = 'system',
    db_path: Path = DB_PATH,
) -> None:
    fields: list[str] = []
    values: list[str] = []
    payload: dict[str, str] = {}
    for name, value in (
        ('title', title),
        ('lead', lead),
        ('journalist', journalist),
        ('status', status),
        ('notes', notes),
    ):
        if value is not None:
            fields.append(f"{name}=?")
            values.append(value)
            payload[name] = value
    if not fields:
        return
    values.append(str(case_id))
    conn = _connect(db_path)
    with conn:
        conn.execute(f"UPDATE cases SET {', '.join(fields)} WHERE id=?", tuple(values))
        _log_action(conn, case_id, 'case_updated', actor=actor, payload=payload)
    conn.close()


def archive_case(case_id: int, *, actor: str = 'system', db_path: Path = DB_PATH) -> None:
    update_case(case_id, status='Archived', actor=actor, db_path=db_path)


def add_entity(case_id: int, name: str, entity_type: str = "Other",
               description: str = "", stated_position: str = "",
               actor: str = "system",
               db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO entities (case_id, name, entity_type, description, stated_position) "
            "VALUES (?,?,?,?,?)",
            (case_id, name, entity_type, description, stated_position),
        )
        eid = cur.lastrowid
        _log_action(conn, case_id, 'entity_added', actor=actor, payload={
            'entity_id': eid,
            'name': name,
            'entity_type': entity_type,
        })
    conn.close()
    return eid


def list_entities(case_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT * FROM entities WHERE case_id=? ORDER BY id", (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_source(case_id: int, title: str, tier: int = 0, source_type: str = "",
               url_or_ref: str = "", date: str = "", excerpt: str = "",
               actor: str = "system",
               db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO sources (case_id, title, tier, source_type, url_or_ref, date, excerpt) "
            "VALUES (?,?,?,?,?,?,?)",
            (case_id, title, tier, source_type, url_or_ref, date, excerpt),
        )
        sid = cur.lastrowid
        _log_action(conn, case_id, 'source_added', actor=actor, payload={
            'source_id': sid,
            'title': title,
            'url_or_ref': url_or_ref,
        })
    conn.close()
    return sid


def add_sources(case_id: int, sources: list[dict], actor: str = "system", db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        conn.executemany(
            "INSERT INTO sources (case_id, title, tier, source_type, url_or_ref, date, excerpt) "
            "VALUES (?,?,?,?,?,?,?)",
            [
                (
                    case_id,
                    source.get('title', ''),
                    source.get('tier', 0),
                    source.get('source_type', ''),
                    source.get('url_or_ref', ''),
                    source.get('date', ''),
                    source.get('excerpt', ''),
                )
                for source in sources
            ],
        )
        _log_action(conn, case_id, 'sources_added', actor=actor, payload={'count': len(sources)})
    conn.close()
    return len(sources)


def list_sources(case_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT * FROM sources WHERE case_id=? ORDER BY tier, id", (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_claim(case_id: int, statement: str, legal_risks: str = "NONE",
              actor: str = "system",
              db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO claims (case_id, statement, legal_risks) VALUES (?,?,?)",
            (case_id, statement, legal_risks),
        )
        cid = cur.lastrowid
        _log_action(conn, case_id, 'claim_added', actor=actor, payload={
            'claim_id': cid,
            'legal_risks': legal_risks,
        })
    conn.close()
    return cid


def list_claims(case_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT * FROM claims WHERE case_id=? ORDER BY id", (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_open_question(case_id: int, question: str, actor: str = "system", db_path: Path = DB_PATH) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO open_questions (case_id, question) VALUES (?,?)",
            (case_id, question),
        )
        qid = cur.lastrowid
        _log_action(conn, case_id, 'open_question_added', actor=actor, payload={'question_id': qid})
    conn.close()
    return qid


def list_open_questions(case_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT * FROM open_questions WHERE case_id=? ORDER BY id", (case_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_audit_log(case_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT id, action, actor, payload_json, created_at FROM audit_log WHERE case_id=? ORDER BY id",
        (case_id,),
    ).fetchall()
    conn.close()
    records: list[dict] = []
    for row in rows:
        item = dict(row)
        item['payload'] = json.loads(item.pop('payload_json') or '{}')
        records.append(item)
    return records


def add_watchlist_entry(
    case_id: int,
    name: str,
    entity_type: str = 'Other',
    notes: str = '',
    *,
    actor: str = 'system',
    db_path: Path = DB_PATH,
) -> int:
    conn = _connect(db_path)
    with conn:
        cur = conn.execute(
            "INSERT INTO watchlist_entries (case_id, name, entity_type, notes) VALUES (?,?,?,?)",
            (case_id, name, entity_type, notes),
        )
        entry_id = cur.lastrowid
        _log_action(conn, case_id, 'watchlist_entry_added', actor=actor, payload={
            'entry_id': entry_id,
            'name': name,
            'entity_type': entity_type,
        })
    conn.close()
    return entry_id


def list_watchlist_entries(case_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT id, name, entity_type, notes FROM watchlist_entries WHERE case_id=? ORDER BY id",
        (case_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_watchlist_hits(
    entry_id: int,
    hits: list[dict],
    *,
    actor: str = 'system',
    db_path: Path = DB_PATH,
) -> int:
    conn = _connect(db_path)
    case_row = conn.execute("SELECT case_id FROM watchlist_entries WHERE id=?", (entry_id,)).fetchone()
    if case_row is None:
        conn.close()
        return 0
    case_id = int(case_row['case_id'])
    with conn:
        conn.executemany(
            "INSERT INTO watchlist_hits (entry_id, source_name, title, url_or_ref, excerpt, retrieval_date) VALUES (?,?,?,?,?,?)",
            [
                (
                    entry_id,
                    hit.get('source_name', ''),
                    hit.get('title', ''),
                    hit.get('url_or_ref', ''),
                    hit.get('excerpt', ''),
                    hit.get('retrieval_date', ''),
                )
                for hit in hits
            ],
        )
        _log_action(conn, case_id, 'watchlist_hits_added', actor=actor, payload={
            'entry_id': entry_id,
            'count': len(hits),
        })
    conn.close()
    return len(hits)


def list_watchlist_hits(entry_id: int, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT source_name, title, url_or_ref, excerpt, retrieval_date FROM watchlist_hits WHERE entry_id=? ORDER BY id",
        (entry_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
