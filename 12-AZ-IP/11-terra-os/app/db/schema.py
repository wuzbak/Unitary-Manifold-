"""
TerraOS — SQLite Database Schema
"""
from __future__ import annotations
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS soil_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    description TEXT,
    characteristics TEXT DEFAULT '{}',
    ph_min REAL,
    ph_max REAL,
    texture TEXT,
    organic_matter_pct REAL,
    cec REAL,
    typical_crops TEXT DEFAULT '[]',
    native_region TEXT,
    drainage TEXT,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS water_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    description TEXT,
    ph_typical REAL,
    tds_ppm REAL,
    hardness_ppm REAL,
    nitrate_ppm REAL,
    dissolved_o2_ppm REAL,
    potable INTEGER DEFAULT 0,
    contaminants TEXT DEFAULT '[]',
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS amendments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,
    description TEXT,
    application_rate TEXT,
    ph_effect TEXT,
    nutrient_content TEXT DEFAULT '{}',
    suitable_soils TEXT DEFAULT '[]',
    notes TEXT,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS contaminants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    contaminant_class TEXT,
    sources TEXT DEFAULT '[]',
    threshold_soil_ppm REAL,
    threshold_water_ppb REAL,
    health_effects TEXT,
    remediation_methods TEXT DEFAULT '[]',
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS crop_suitability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    soil_profile_id INTEGER REFERENCES soil_profiles(id) ON DELETE CASCADE,
    crop_name TEXT NOT NULL,
    suitability TEXT NOT NULL DEFAULT 'suitable',
    notes TEXT,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS remediation_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    contaminant_id INTEGER REFERENCES contaminants(id),
    method TEXT NOT NULL,
    description TEXT,
    duration_months INTEGER,
    effectiveness_pct REAL,
    cost_estimate TEXT,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER,
    profile_type TEXT NOT NULL DEFAULT 'soil',
    parameter TEXT NOT NULL,
    value REAL,
    unit TEXT,
    test_date TEXT,
    notes TEXT,
    version_hash TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS benchmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    parameter TEXT NOT NULL,
    optimal_min REAL,
    optimal_max REAL,
    unit TEXT,
    notes TEXT,
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
CREATE VIRTUAL TABLE IF NOT EXISTS soil_profiles_fts USING fts5(
    name,
    type,
    description,
    characteristics,
    content='soil_profiles',
    content_rowid='id'
);
CREATE VIRTUAL TABLE IF NOT EXISTS water_samples_fts USING fts5(
    name,
    source_type,
    description,
    content='water_samples',
    content_rowid='id'
);
CREATE TRIGGER IF NOT EXISTS soil_profiles_fts_insert AFTER INSERT ON soil_profiles BEGIN
    INSERT INTO soil_profiles_fts(rowid, name, type, description, characteristics)
    VALUES (new.id, new.name, new.type, new.description, new.characteristics);
END;
CREATE TRIGGER IF NOT EXISTS soil_profiles_fts_delete AFTER DELETE ON soil_profiles BEGIN
    INSERT INTO soil_profiles_fts(soil_profiles_fts, rowid, name, type, description, characteristics)
    VALUES ('delete', old.id, old.name, old.type, old.description, old.characteristics);
END;
CREATE TRIGGER IF NOT EXISTS soil_profiles_fts_update AFTER UPDATE ON soil_profiles BEGIN
    INSERT INTO soil_profiles_fts(soil_profiles_fts, rowid, name, type, description, characteristics)
    VALUES ('delete', old.id, old.name, old.type, old.description, old.characteristics);
    INSERT INTO soil_profiles_fts(rowid, name, type, description, characteristics)
    VALUES (new.id, new.name, new.type, new.description, new.characteristics);
END;
CREATE TRIGGER IF NOT EXISTS water_samples_fts_insert AFTER INSERT ON water_samples BEGIN
    INSERT INTO water_samples_fts(rowid, name, source_type, description)
    VALUES (new.id, new.name, new.source_type, new.description);
END;
CREATE TRIGGER IF NOT EXISTS water_samples_fts_delete AFTER DELETE ON water_samples BEGIN
    INSERT INTO water_samples_fts(water_samples_fts, rowid, name, source_type, description)
    VALUES ('delete', old.id, old.name, old.source_type, old.description);
END;
CREATE TRIGGER IF NOT EXISTS water_samples_fts_update AFTER UPDATE ON water_samples BEGIN
    INSERT INTO water_samples_fts(water_samples_fts, rowid, name, source_type, description)
    VALUES ('delete', old.id, old.name, old.source_type, old.description);
    INSERT INTO water_samples_fts(rowid, name, source_type, description)
    VALUES (new.id, new.name, new.source_type, new.description);
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

def upsert_soil_profile(conn: sqlite3.Connection, data: dict) -> int:
    h = record_hash(data)
    cur = conn.execute("""
        INSERT INTO soil_profiles
            (name, type, description, characteristics, ph_min, ph_max, texture,
             organic_matter_pct, cec, typical_crops, native_region, drainage, version_hash, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
        ON CONFLICT(name) DO UPDATE SET
            type=excluded.type, description=excluded.description,
            ph_min=excluded.ph_min, ph_max=excluded.ph_max,
            texture=excluded.texture, organic_matter_pct=excluded.organic_matter_pct,
            cec=excluded.cec, typical_crops=excluded.typical_crops,
            native_region=excluded.native_region, drainage=excluded.drainage,
            version_hash=excluded.version_hash, updated_at=datetime('now')
    """, (
        data["name"], data.get("type", "unknown"), data.get("description"),
        json.dumps(data.get("characteristics", {})),
        data.get("ph_min"), data.get("ph_max"), data.get("texture"),
        data.get("organic_matter_pct"), data.get("cec"),
        json.dumps(data.get("typical_crops", [])),
        data.get("native_region"), data.get("drainage"), h,
    ))
    if cur.lastrowid and cur.lastrowid > 0:
        return cur.lastrowid
    row = conn.execute("SELECT id FROM soil_profiles WHERE name=?", (data["name"],)).fetchone()
    return row[0] if row else 0

def upsert_water_sample(conn: sqlite3.Connection, data: dict) -> int:
    h = record_hash(data)
    cur = conn.execute("""
        INSERT INTO water_samples
            (name, source_type, description, ph_typical, tds_ppm, hardness_ppm,
             nitrate_ppm, dissolved_o2_ppm, potable, contaminants, version_hash, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,datetime('now'))
        ON CONFLICT(name) DO UPDATE SET
            source_type=excluded.source_type, description=excluded.description,
            ph_typical=excluded.ph_typical, tds_ppm=excluded.tds_ppm,
            hardness_ppm=excluded.hardness_ppm, nitrate_ppm=excluded.nitrate_ppm,
            dissolved_o2_ppm=excluded.dissolved_o2_ppm, potable=excluded.potable,
            contaminants=excluded.contaminants,
            version_hash=excluded.version_hash, updated_at=datetime('now')
    """, (
        data["name"], data.get("source_type", "unknown"), data.get("description"),
        data.get("ph_typical"), data.get("tds_ppm"), data.get("hardness_ppm"),
        data.get("nitrate_ppm"), data.get("dissolved_o2_ppm"), int(data.get("potable", 0)),
        json.dumps(data.get("contaminants", [])), h,
    ))
    if cur.lastrowid and cur.lastrowid > 0:
        return cur.lastrowid
    row = conn.execute("SELECT id FROM water_samples WHERE name=?", (data["name"],)).fetchone()
    return row[0] if row else 0

def upsert_amendment(conn: sqlite3.Connection, data: dict) -> int:
    h = record_hash(data)
    cur = conn.execute("""
        INSERT INTO amendments
            (name, type, description, application_rate, ph_effect, nutrient_content, notes, version_hash, updated_at)
        VALUES (?,?,?,?,?,?,?,?,datetime('now'))
        ON CONFLICT(name) DO UPDATE SET
            type=excluded.type, description=excluded.description,
            application_rate=excluded.application_rate, ph_effect=excluded.ph_effect,
            nutrient_content=excluded.nutrient_content, notes=excluded.notes,
            version_hash=excluded.version_hash, updated_at=datetime('now')
    """, (
        data["name"], data.get("type", "unknown"), data.get("description"),
        data.get("application_rate"), data.get("ph_effect"),
        json.dumps(data.get("nutrient_content", {})), data.get("notes"), h,
    ))
    if cur.lastrowid and cur.lastrowid > 0:
        return cur.lastrowid
    row = conn.execute("SELECT id FROM amendments WHERE name=?", (data["name"],)).fetchone()
    return row[0] if row else 0

def search_profiles(conn: sqlite3.Connection, query: str, limit: int = 20) -> list[dict]:
    if not query or not query.strip():
        return []
    results = []
    # Search soil profiles
    try:
        rows = conn.execute(
            "SELECT s.*, 'soil' as profile_type FROM soil_profiles s JOIN soil_profiles_fts f ON s.id=f.rowid WHERE soil_profiles_fts MATCH ? LIMIT ?",
            (query, limit)
        ).fetchall()
        results.extend([dict(r) for r in rows])
    except Exception:
        rows = conn.execute(
            "SELECT *, 'soil' as profile_type FROM soil_profiles WHERE name LIKE ? OR description LIKE ? OR type LIKE ? LIMIT ?",
            (f"%{query}%", f"%{query}%", f"%{query}%", limit)
        ).fetchall()
        results.extend([dict(r) for r in rows])
    # Search water samples
    try:
        rows = conn.execute(
            "SELECT s.*, 'water' as profile_type FROM water_samples s JOIN water_samples_fts f ON s.id=f.rowid WHERE water_samples_fts MATCH ? LIMIT ?",
            (query, limit)
        ).fetchall()
        results.extend([dict(r) for r in rows])
    except Exception:
        rows = conn.execute(
            "SELECT *, 'water' as profile_type FROM water_samples WHERE name LIKE ? OR description LIKE ? LIMIT ?",
            (f"%{query}%", f"%{query}%", limit)
        ).fetchall()
        results.extend([dict(r) for r in rows])
    return results[:limit]

def get_profile_full(conn: sqlite3.Connection, profile_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM soil_profiles WHERE id=?", (profile_id,)).fetchone()
    if not row:
        return None
    result = dict(row)
    result["amendments"] = []
    return result
