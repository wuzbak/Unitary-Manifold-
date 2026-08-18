"""
FilmersCompanion — Database Seed
==================================
Seeds the demo project "THE OMEGA PROTOCOL" on first run.
"""
from __future__ import annotations

import uuid
from pathlib import Path


PROJECT_ID = "omega-001"


def seed_database(db_path: Path, verbose: bool = False) -> None:
    """Seed demo data. Idempotent — skips if project already seeded."""
    from .schema import init_db, get_conn

    init_db(db_path)

    with get_conn(db_path) as conn:
        existing = conn.execute(
            "SELECT COUNT(*) FROM scenes WHERE project_id=?", (PROJECT_ID,)
        ).fetchone()[0]
        if existing > 0:
            if verbose:
                print(f"[seed] Project {PROJECT_ID} already seeded — skipping.")
            return

    _seed_locations(db_path, verbose)
    _seed_scenes(db_path, verbose)
    _seed_budget_lines(db_path, verbose)
    _seed_call_sheets(db_path, verbose)
    _seed_shot_lists(db_path, verbose)

    if verbose:
        print(f"[seed] THE OMEGA PROTOCOL seeded successfully.")


# ---------------------------------------------------------------------------
# Fixed IDs so tests are deterministic
# ---------------------------------------------------------------------------

LOC_ROOFTOP   = "loc-rooftop-001"
LOC_WAREHOUSE = "loc-warehouse-002"
LOC_CITYHALL  = "loc-cityhall-003"

SCENE_IDS = [
    "scene-001", "scene-002", "scene-003", "scene-004", "scene-005"
]

BUDGET_IDS = [
    "bud-atl-001", "bud-cam-002", "bud-loc-003",
    "bud-post-004", "bud-cont-005", "bud-misc-006",
]

CALL_IDS = ["call-001", "call-002"]

SHOT_IDS = ["shot-001", "shot-002", "shot-003"]


def _seed_locations(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    locations = [
        {
            "id": LOC_ROOFTOP,
            "project_id": PROJECT_ID,
            "name": "Rooftop Studio",
            "address": "1200 Apex Tower, Downtown",
            "int_ext": "EXT",
            "permit_status": "confirmed",
            "fee": 5000.0,
            "owner_contact": "apex-mgmt@example.com",
            "notes": "Access via freight elevator, key from security desk.",
        },
        {
            "id": LOC_WAREHOUSE,
            "project_id": PROJECT_ID,
            "name": "Warehouse District",
            "address": "88 Industrial Ave, South Side",
            "int_ext": "INT",
            "permit_status": "pending",
            "fee": 2500.0,
            "owner_contact": "holdings@example.com",
            "notes": "Permit application submitted 2026-03-01.",
        },
        {
            "id": LOC_CITYHALL,
            "project_id": PROJECT_ID,
            "name": "City Hall Exterior",
            "address": "1 Civic Plaza, Central",
            "int_ext": "EXT",
            "permit_status": "rejected",
            "fee": 0.0,
            "owner_contact": "permits@cityexample.gov",
            "notes": "Rejected — special event conflict. Seek alternative.",
        },
    ]
    with get_conn(db_path) as conn:
        for loc in locations:
            conn.execute(
                """INSERT OR IGNORE INTO locations
                   (id, project_id, name, address, int_ext, permit_status, fee, owner_contact, notes)
                   VALUES (:id,:project_id,:name,:address,:int_ext,:permit_status,:fee,:owner_contact,:notes)""",
                loc,
            )
    if verbose:
        print(f"[seed] Inserted {len(locations)} locations")


def _seed_scenes(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    scenes = [
        {
            "id": SCENE_IDS[0],
            "project_id": PROJECT_ID,
            "scene_number": "1",
            "location_id": LOC_ROOFTOP,
            "int_ext": "EXT",
            "day_night": "D",
            "synopsis": "Agent NOVA receives the mission briefing at sunrise on the rooftop.",
            "page_count": 2.5,
            "status": "scheduled",
            "shoot_date": "2026-06-15",
        },
        {
            "id": SCENE_IDS[1],
            "project_id": PROJECT_ID,
            "scene_number": "5",
            "location_id": LOC_WAREHOUSE,
            "int_ext": "INT",
            "day_night": "N",
            "synopsis": "The team infiltrates the warehouse at midnight.",
            "page_count": 3.0,
            "status": "scheduled",
            "shoot_date": "2026-06-16",
        },
        {
            "id": SCENE_IDS[2],
            "project_id": PROJECT_ID,
            "scene_number": "12",
            "location_id": LOC_ROOFTOP,
            "int_ext": "EXT",
            "day_night": "D",
            "synopsis": "The final confrontation under the open sky.",
            "page_count": 4.0,
            "status": "unscheduled",
            "shoot_date": None,
        },
        {
            "id": SCENE_IDS[3],
            "project_id": PROJECT_ID,
            "scene_number": "7",
            "location_id": LOC_WAREHOUSE,
            "int_ext": "INT",
            "day_night": "D",
            "synopsis": "NOVA deciphers the encrypted documents in the warehouse office.",
            "page_count": 1.5,
            "status": "scheduled",
            "shoot_date": "2026-06-16",
        },
        {
            "id": SCENE_IDS[4],
            "project_id": PROJECT_ID,
            "scene_number": "3",
            "location_id": LOC_CITYHALL,
            "int_ext": "EXT",
            "day_night": "D",
            "synopsis": "Press conference outside City Hall — location rejected.",
            "page_count": 1.0,
            "status": "hold",
            "shoot_date": None,
        },
    ]
    with get_conn(db_path) as conn:
        for scene in scenes:
            conn.execute(
                """INSERT OR IGNORE INTO scenes
                   (id,project_id,scene_number,location_id,int_ext,day_night,synopsis,page_count,status,shoot_date)
                   VALUES (:id,:project_id,:scene_number,:location_id,:int_ext,:day_night,:synopsis,:page_count,:status,:shoot_date)""",
                scene,
            )
    if verbose:
        print(f"[seed] Inserted {len(scenes)} scenes")


def _seed_budget_lines(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    lines = [
        {"id": BUDGET_IDS[0], "project_id": PROJECT_ID, "category": "above_the_line",
         "description": "Director, Writers, Lead Cast", "budgeted": 350000.0, "actual": 310000.0},
        {"id": BUDGET_IDS[1], "project_id": PROJECT_ID, "category": "camera_lighting",
         "description": "Camera package, gaffer, grip", "budgeted": 90000.0, "actual": 72000.0},
        {"id": BUDGET_IDS[2], "project_id": PROJECT_ID, "category": "locations",
         "description": "Location fees and permits", "budgeted": 50000.0, "actual": 7500.0},
        {"id": BUDGET_IDS[3], "project_id": PROJECT_ID, "category": "post_production",
         "description": "Edit, VFX, color, mix", "budgeted": 100000.0, "actual": 0.0},
        {"id": BUDGET_IDS[4], "project_id": PROJECT_ID, "category": "contingency",
         "description": "10% schedule/cost buffer", "budgeted": 120000.0, "actual": 0.0},
        {"id": BUDGET_IDS[5], "project_id": PROJECT_ID, "category": "misc",
         "description": "Insurance, legal, catering, travel", "budgeted": 80000.0, "actual": 45000.0},
    ]
    with get_conn(db_path) as conn:
        for line in lines:
            conn.execute(
                """INSERT OR IGNORE INTO budget_lines
                   (id,project_id,category,description,budgeted,actual)
                   VALUES (:id,:project_id,:category,:description,:budgeted,:actual)""",
                line,
            )
    if verbose:
        print(f"[seed] Inserted {len(lines)} budget lines")


def _seed_call_sheets(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    sheets = [
        {
            "id": CALL_IDS[0],
            "project_id": PROJECT_ID,
            "shoot_date": "2026-06-15",
            "general_call": "06:00",
            "location_id": LOC_ROOFTOP,
            "scenes": "1",
            "notes": "Sunrise shoot. BTS photographer on set.",
        },
        {
            "id": CALL_IDS[1],
            "project_id": PROJECT_ID,
            "shoot_date": "2026-06-16",
            "general_call": "07:00",
            "location_id": LOC_WAREHOUSE,
            "scenes": "5,7",
            "notes": "Double-up day: two scenes in warehouse.",
        },
    ]
    with get_conn(db_path) as conn:
        for sheet in sheets:
            conn.execute(
                """INSERT OR IGNORE INTO call_sheets
                   (id,project_id,shoot_date,general_call,location_id,scenes,notes)
                   VALUES (:id,:project_id,:shoot_date,:general_call,:location_id,:scenes,:notes)""",
                sheet,
            )
    if verbose:
        print(f"[seed] Inserted {len(sheets)} call sheets")


def _seed_shot_lists(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    shots = [
        {
            "id": SHOT_IDS[0],
            "scene_id": SCENE_IDS[0],
            "shot_number": 1,
            "coverage_type": "master",
            "lens": "35mm",
            "movement": "static",
            "frame_rate": "24fps",
            "notes": "Wide establishing rooftop shot.",
        },
        {
            "id": SHOT_IDS[1],
            "scene_id": SCENE_IDS[0],
            "shot_number": 2,
            "coverage_type": "CU",
            "lens": "85mm",
            "movement": "static",
            "frame_rate": "24fps",
            "notes": "Close-up on NOVA's face receiving intel.",
        },
        {
            "id": SHOT_IDS[2],
            "scene_id": SCENE_IDS[1],
            "shot_number": 1,
            "coverage_type": "master",
            "lens": "24mm",
            "movement": "dolly",
            "frame_rate": "24fps",
            "notes": "Master of warehouse infiltration.",
        },
    ]
    with get_conn(db_path) as conn:
        for shot in shots:
            conn.execute(
                """INSERT OR IGNORE INTO shot_lists
                   (id,scene_id,shot_number,coverage_type,lens,movement,frame_rate,notes)
                   VALUES (:id,:scene_id,:shot_number,:coverage_type,:lens,:movement,:frame_rate,:notes)""",
                shot,
            )
    if verbose:
        print(f"[seed] Inserted {len(shots)} shot list entries")


if __name__ == "__main__":
    import sys
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/film.db")
    seed_database(path, verbose=True)
