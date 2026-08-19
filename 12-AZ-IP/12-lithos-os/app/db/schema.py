"""
LithosOS — SQLite Database Schema
"""
from __future__ import annotations
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS specimens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    common_names TEXT NOT NULL DEFAULT '[]',
    mineral_class TEXT,
    crystal_system TEXT,
    mohs_hardness REAL,
    composition TEXT,
    description TEXT,
    luster TEXT,
    streak TEXT,
    cleavage TEXT,
    fracture TEXT,
    specific_gravity REAL,
    native_range TEXT,
    toxic INTEGER DEFAULT 0,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS minerals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    specimen_id INTEGER REFERENCES specimens(id) ON DELETE CASCADE,
    chemical_formula TEXT,
    crystal_class TEXT,
    crystal_habit TEXT,
    optical_properties TEXT,
    associated_minerals TEXT DEFAULT '[]',
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS gemstones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    specimen_id INTEGER REFERENCES specimens(id) ON DELETE CASCADE,
    variety TEXT,
    color TEXT,
    clarity_grade TEXT,
    cut_styles TEXT DEFAULT '[]',
    treatments TEXT DEFAULT '[]',
    synthetic_available INTEGER DEFAULT 0,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS metals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    specimen_id INTEGER REFERENCES specimens(id) ON DELETE CASCADE,
    atomic_number INTEGER,
    melting_point_c REAL,
    conductivity TEXT,
    ores TEXT DEFAULT '[]',
    industrial_uses TEXT DEFAULT '[]',
    toxicity_notes TEXT,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS alloys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    base_metals TEXT DEFAULT '[]',
    composition_percent TEXT DEFAULT '{}',
    properties TEXT,
    uses TEXT,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS formations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    specimen_id INTEGER REFERENCES specimens(id) ON DELETE CASCADE,
    formation_type TEXT,
    geological_environment TEXT,
    associated_rocks TEXT DEFAULT '[]',
    typical_locations TEXT DEFAULT '[]',
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS hazards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    specimen_id INTEGER REFERENCES specimens(id) ON DELETE CASCADE,
    hazard_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'moderate',
    description TEXT NOT NULL,
    exposure_route TEXT,
    symptoms TEXT,
    treatment TEXT,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    specimen_id INTEGER REFERENCES specimens(id) ON DELETE CASCADE,
    price_per_carat_usd TEXT,
    price_per_gram_usd TEXT,
    rarity TEXT,
    major_sources TEXT DEFAULT '[]',
    ethical_concerns TEXT,
    synthetic_price_ratio REAL,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS formulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    primary_specimens TEXT DEFAULT '[]',
    ingredients TEXT NOT NULL DEFAULT '[]',
    recipe TEXT,
    yield_amount TEXT,
    uses TEXT,
    safety_notes TEXT,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    action TEXT NOT NULL DEFAULT 'upsert',
    version_hash TEXT NOT NULL,
    synced_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS source_references (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    specimen_id     INTEGER REFERENCES specimens(id) ON DELETE CASCADE,
    source_name     TEXT    NOT NULL,  -- "Mindat" | "GIA" | "Smithsonian" | "USGS" | "Minerals.net" | "Webmineral" | "PDR-Rocks"
    source_url      TEXT,
    citation        TEXT,
    identification_notes TEXT,
    safety_notes    TEXT,
    market_notes    TEXT,
    last_fetched    TEXT,
    version_hash    TEXT    NOT NULL DEFAULT '',
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE VIRTUAL TABLE IF NOT EXISTS specimens_fts USING fts5(
    name,
    common_names,
    description,
    composition,
    content='specimens',
    content_rowid='id'
);
CREATE TRIGGER IF NOT EXISTS specimens_fts_insert AFTER INSERT ON specimens BEGIN
    INSERT INTO specimens_fts(rowid, name, common_names, description, composition)
    VALUES (new.id, new.name, new.common_names, new.description, new.composition);
END;
CREATE TRIGGER IF NOT EXISTS specimens_fts_delete AFTER DELETE ON specimens BEGIN
    INSERT INTO specimens_fts(specimens_fts, rowid, name, common_names, description, composition)
    VALUES ('delete', old.id, old.name, old.common_names, old.description, old.composition);
END;
CREATE TRIGGER IF NOT EXISTS specimens_fts_update AFTER UPDATE ON specimens BEGIN
    INSERT INTO specimens_fts(specimens_fts, rowid, name, common_names, description, composition)
    VALUES ('delete', old.id, old.name, old.common_names, old.description, old.composition);
    INSERT INTO specimens_fts(rowid, name, common_names, description, composition)
    VALUES (new.id, new.name, new.common_names, new.description, new.composition);
END;
"""

@contextmanager
def get_conn(db_path: Path):
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()

def record_hash(data: dict) -> str:
    blob = json.dumps(data, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(blob).hexdigest()[:16]

def upsert_specimen(conn: sqlite3.Connection, data: dict) -> int:
    h = record_hash(data)
    common_names = json.dumps(data.get("common_names", []))
    cur = conn.execute("""
        INSERT INTO specimens
            (name, common_names, mineral_class, crystal_system, mohs_hardness,
             composition, description, luster, streak, cleavage, fracture,
             specific_gravity, native_range, toxic, version_hash, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
        ON CONFLICT(name) DO UPDATE SET
            common_names=excluded.common_names,
            mineral_class=excluded.mineral_class,
            crystal_system=excluded.crystal_system,
            mohs_hardness=excluded.mohs_hardness,
            composition=excluded.composition,
            description=excluded.description,
            luster=excluded.luster,
            streak=excluded.streak,
            cleavage=excluded.cleavage,
            fracture=excluded.fracture,
            specific_gravity=excluded.specific_gravity,
            native_range=excluded.native_range,
            toxic=excluded.toxic,
            version_hash=excluded.version_hash,
            updated_at=datetime('now')
    """, (
        data.get("name", ""),
        common_names,
        data.get("mineral_class"),
        data.get("crystal_system"),
        data.get("mohs_hardness"),
        data.get("composition"),
        data.get("description"),
        data.get("luster"),
        data.get("streak"),
        data.get("cleavage"),
        data.get("fracture"),
        data.get("specific_gravity"),
        data.get("native_range"),
        int(data.get("toxic", 0)),
        h,
    ))
    if cur.lastrowid and cur.lastrowid > 0:
        return cur.lastrowid
    row = conn.execute("SELECT id FROM specimens WHERE name=?", (data["name"],)).fetchone()
    return row[0] if row else 0

def upsert_source_reference(conn: sqlite3.Connection, specimen_id: int, data: dict) -> int:
    """Insert a source reference for a specimen."""
    h = record_hash({**data, "specimen_id": specimen_id})
    cur = conn.execute(
        """
        INSERT INTO source_references
            (specimen_id, source_name, source_url, citation, identification_notes,
             safety_notes, market_notes, last_fetched, version_hash, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))
        ON CONFLICT DO NOTHING
        """,
        (
            specimen_id,
            data.get("source_name", ""),
            data.get("source_url", ""),
            data.get("citation", ""),
            data.get("identification_notes", ""),
            data.get("safety_notes", ""),
            data.get("market_notes", ""),
            data.get("last_fetched", ""),
            h,
        ),
    )
    return cur.lastrowid or 0


def get_source_references(conn: sqlite3.Connection, specimen_id: int) -> list[dict]:
    """Return all source references for a given specimen."""
    rows = conn.execute(
        "SELECT * FROM source_references WHERE specimen_id=?", (specimen_id,)
    ).fetchall()
    return [dict(r) for r in rows]


def search_specimens(conn: sqlite3.Connection, query: str, limit: int = 20) -> list[dict]:
    if not query or not query.strip():
        return []
    try:
        rows = conn.execute(
            "SELECT s.* FROM specimens s JOIN specimens_fts f ON s.id=f.rowid WHERE specimens_fts MATCH ? LIMIT ?",
            (query, limit)
        ).fetchall()
        if rows:
            return [dict(r) for r in rows]
    except Exception:
        pass
    rows = conn.execute(
        "SELECT * FROM specimens WHERE name LIKE ? OR composition LIKE ? OR description LIKE ? LIMIT ?",
        (f"%{query}%", f"%{query}%", f"%{query}%", limit)
    ).fetchall()
    return [dict(r) for r in rows]

def get_specimen_full(conn: sqlite3.Connection, specimen_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM specimens WHERE id=?", (specimen_id,)).fetchone()
    if not row:
        return None
    result = dict(row)
    result["minerals"] = [dict(r) for r in conn.execute("SELECT * FROM minerals WHERE specimen_id=?", (specimen_id,)).fetchall()]
    result["gemstones"] = [dict(r) for r in conn.execute("SELECT * FROM gemstones WHERE specimen_id=?", (specimen_id,)).fetchall()]
    result["metals"] = [dict(r) for r in conn.execute("SELECT * FROM metals WHERE specimen_id=?", (specimen_id,)).fetchall()]
    result["hazards"] = [dict(r) for r in conn.execute("SELECT * FROM hazards WHERE specimen_id=?", (specimen_id,)).fetchall()]
    result["market_data"] = [dict(r) for r in conn.execute("SELECT * FROM market_data WHERE specimen_id=?", (specimen_id,)).fetchall()]
    result["source_references"] = get_source_references(conn, specimen_id)
    return result
