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
    """Seed demo data. Idempotent — safe to run repeatedly."""
    from .schema import init_db, get_conn

    init_db(db_path)
    _seed_project(db_path, verbose)
    _seed_script_stack(db_path, verbose)
    _seed_locations(db_path, verbose)
    _seed_scenes(db_path, verbose)
    _seed_characters(db_path, verbose)
    _seed_breakdown_elements(db_path, verbose)
    _seed_storyboards(db_path, verbose)
    _seed_budget_lines(db_path, verbose)
    _seed_schedule(db_path, verbose)
    _seed_call_sheets(db_path, verbose)
    _seed_shot_lists(db_path, verbose)
    _seed_crew(db_path, verbose)
    _seed_tasks(db_path, verbose)
    _seed_approvals(db_path, verbose)
    _seed_assets(db_path, verbose)
    _seed_reviews(db_path, verbose)
    _seed_deliverables(db_path, verbose)

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
SCRIPT_ID = "script-omega-001"
SCRIPT_VERSION_ID = "script-version-001"
SCHEDULE_DAY_IDS = ["sched-001", "sched-002"]


def _seed_project(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    with get_conn(db_path) as conn:
        conn.execute(
            """INSERT OR IGNORE INTO projects
               (id, title, format, stage, logline, status, shoot_days, target_day_hours, contingency_pct)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                PROJECT_ID,
                "THE OMEGA PROTOCOL",
                "feature",
                "prep",
                "An independent thriller run on Axiom Omega principles.",
                "active",
                2,
                10.0,
                12.0,
            ),
        )
    if verbose:
        print("[seed] Inserted project")


def _seed_script_stack(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    script_content = """INT. PRODUCTION OFFICE - DAY
NOVA studies the call board while producer ELIAS flags the city hall permit issue.

EXT. ROOFTOP STUDIO - SUNRISE
NOVA receives the mission briefing and commits to the compressed schedule.

INT. WAREHOUSE DISTRICT - NIGHT
NOVA and MIRA infiltrate the warehouse as a silent drone watches from above.
"""
    with get_conn(db_path) as conn:
        conn.execute(
            """INSERT OR IGNORE INTO scripts
               (id, project_id, title, format, current_revision, content)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                SCRIPT_ID,
                PROJECT_ID,
                "THE OMEGA PROTOCOL",
                "feature",
                "Blue",
                script_content,
            ),
        )
        conn.execute(
            """INSERT OR IGNORE INTO script_versions
               (id, script_id, revision_name, revision_color, change_summary, content)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                SCRIPT_VERSION_ID,
                SCRIPT_ID,
                "Blue Draft",
                "Blue",
                "Lock prep draft with permit and warehouse revisions.",
                script_content,
            ),
        )
    if verbose:
        print("[seed] Inserted script stack")


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


def _seed_characters(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    characters = [
        {"id": "char-001", "project_id": PROJECT_ID, "name": "NOVA", "performer": "Lead TBD", "notes": "Lead operative"},
        {"id": "char-002", "project_id": PROJECT_ID, "name": "MIRA", "performer": "Supporting TBD", "notes": "Warehouse partner"},
        {"id": "char-003", "project_id": PROJECT_ID, "name": "ELIAS", "performer": "Supporting TBD", "notes": "Producer liaison"},
    ]
    with get_conn(db_path) as conn:
        for character in characters:
            conn.execute(
                """INSERT OR IGNORE INTO characters
                   (id, project_id, name, performer, notes)
                   VALUES (:id, :project_id, :name, :performer, :notes)""",
                character,
            )
    if verbose:
        print(f"[seed] Inserted {len(characters)} characters")


def _seed_breakdown_elements(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    elements = [
        {"id": "be-001", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[0], "department": "Cast", "element_type": "cast", "name": "NOVA", "quantity": 1, "status": "confirmed", "notes": "Lead call"},
        {"id": "be-002", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[0], "department": "Camera", "element_type": "coverage", "name": "Rooftop sunrise master", "quantity": 1, "status": "planned", "notes": "Golden-hour window"},
        {"id": "be-003", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[0], "department": "G&E", "element_type": "lighting", "name": "Sunrise neg fill / battery package", "quantity": 1, "status": "planned", "notes": "Fast rooftop setup"},
        {"id": "be-004", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[1], "department": "Cast", "element_type": "cast", "name": "NOVA", "quantity": 1, "status": "confirmed", "notes": "Night work"},
        {"id": "be-005", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[1], "department": "Cast", "element_type": "cast", "name": "MIRA", "quantity": 1, "status": "hold", "notes": "Travel pending"},
        {"id": "be-006", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[1], "department": "VFX", "element_type": "scene_requirement", "name": "Drone plate and screen replacement", "quantity": 1, "status": "pending", "notes": "Requires vendor estimate"},
        {"id": "be-007", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[1], "department": "Sound", "element_type": "sound", "name": "Warehouse wild lines", "quantity": 1, "status": "planned", "notes": "Noise floor check"},
        {"id": "be-008", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[2], "department": "Locations", "element_type": "permit", "name": "Rooftop return permit", "quantity": 1, "status": "pending", "notes": "Confirm backup rain cover"},
        {"id": "be-009", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[3], "department": "Art", "element_type": "set_dressing", "name": "Warehouse office document wall", "quantity": 1, "status": "planned", "notes": "Continuity-critical"},
        {"id": "be-010", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[3], "department": "Script Supervisor", "element_type": "continuity", "name": "Encrypted document inserts", "quantity": 1, "status": "planned", "notes": "Match close-ups"},
        {"id": "be-011", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[4], "department": "Locations", "element_type": "permit", "name": "City Hall replacement search", "quantity": 1, "status": "blocked", "notes": "Original permit rejected"},
        {"id": "be-012", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[4], "department": "Producing", "element_type": "extras", "name": "Press conference background performers", "quantity": 12, "status": "pending", "notes": "Depends on replacement exterior"},
    ]
    with get_conn(db_path) as conn:
        for element in elements:
            conn.execute(
                """INSERT OR IGNORE INTO breakdown_elements
                   (id, project_id, scene_id, department, element_type, name, quantity, status, notes)
                   VALUES (:id, :project_id, :scene_id, :department, :element_type, :name, :quantity, :status, :notes)""",
                element,
            )
    if verbose:
        print(f"[seed] Inserted {len(elements)} breakdown elements")


def _seed_storyboards(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    panels = [
        {"id": "sb-001", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[0], "panel_number": 1, "shot_label": "Master", "visual_mode": "template", "description": "Rooftop briefing wide", "lens": "35mm", "movement": "static", "duration_sec": 10.0, "notes": "Establish sunrise geography"},
        {"id": "sb-002", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[0], "panel_number": 2, "shot_label": "CU", "visual_mode": "template", "description": "NOVA receives intel", "lens": "85mm", "movement": "push-in", "duration_sec": 6.0, "notes": "Emotional beat"},
        {"id": "sb-003", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[1], "panel_number": 1, "shot_label": "Master", "visual_mode": "template", "description": "Warehouse infiltration wide", "lens": "24mm", "movement": "dolly", "duration_sec": 12.0, "notes": "Include drone eyeline"},
    ]
    with get_conn(db_path) as conn:
        for panel in panels:
            conn.execute(
                """INSERT OR IGNORE INTO storyboard_panels
                   (id, project_id, scene_id, panel_number, shot_label, visual_mode, description, lens, movement, duration_sec, notes)
                   VALUES (:id, :project_id, :scene_id, :panel_number, :shot_label, :visual_mode, :description, :lens, :movement, :duration_sec, :notes)""",
                panel,
            )
    if verbose:
        print(f"[seed] Inserted {len(panels)} storyboard panels")


def _seed_schedule(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    days = [
        {"id": SCHEDULE_DAY_IDS[0], "project_id": PROJECT_ID, "shoot_date": "2026-06-15", "unit_name": "Main Unit", "general_call": "06:00", "wrap_time": "17:00", "location_id": LOC_ROOFTOP, "pages_planned": 2.5, "status": "locked"},
        {"id": SCHEDULE_DAY_IDS[1], "project_id": PROJECT_ID, "shoot_date": "2026-06-16", "unit_name": "Main Unit", "general_call": "07:00", "wrap_time": "20:30", "location_id": LOC_WAREHOUSE, "pages_planned": 4.5, "status": "watch"},
    ]
    strips = [
        {"id": "strip-001", "project_id": PROJECT_ID, "schedule_day_id": SCHEDULE_DAY_IDS[0], "scene_id": SCENE_IDS[0], "strip_order": 1, "company_move": 0, "estimated_hours": 5.0, "notes": "Sunrise window"},
        {"id": "strip-002", "project_id": PROJECT_ID, "schedule_day_id": SCHEDULE_DAY_IDS[1], "scene_id": SCENE_IDS[1], "strip_order": 1, "company_move": 0, "estimated_hours": 6.0, "notes": "Night exterior prep"},
        {"id": "strip-003", "project_id": PROJECT_ID, "schedule_day_id": SCHEDULE_DAY_IDS[1], "scene_id": SCENE_IDS[3], "strip_order": 2, "company_move": 1, "estimated_hours": 3.5, "notes": "Office inserts after infiltration"},
    ]
    with get_conn(db_path) as conn:
        for day in days:
            conn.execute(
                """INSERT OR IGNORE INTO schedule_days
                   (id, project_id, shoot_date, unit_name, general_call, wrap_time, location_id, pages_planned, status)
                   VALUES (:id, :project_id, :shoot_date, :unit_name, :general_call, :wrap_time, :location_id, :pages_planned, :status)""",
                day,
            )
        for strip in strips:
            conn.execute(
                """INSERT OR IGNORE INTO schedule_strips
                   (id, project_id, schedule_day_id, scene_id, strip_order, company_move, estimated_hours, notes)
                   VALUES (:id, :project_id, :schedule_day_id, :scene_id, :strip_order, :company_move, :estimated_hours, :notes)""",
                strip,
            )
    if verbose:
        print(f"[seed] Inserted {len(days)} schedule days and {len(strips)} strips")


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


def _seed_crew(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    crew = [
        {"id": "crew-001", "project_id": PROJECT_ID, "name": "Ava Mercer", "department": "Producing", "role": "Producer", "call_time": "06:00", "status": "confirmed", "contact": "ava@example.com"},
        {"id": "crew-002", "project_id": PROJECT_ID, "name": "Tom Reyes", "department": "UPM / Production", "role": "UPM", "call_time": "05:45", "status": "confirmed", "contact": "tom@example.com"},
        {"id": "crew-003", "project_id": PROJECT_ID, "name": "Rina Vale", "department": "1st AD", "role": "1st AD", "call_time": "05:30", "status": "confirmed", "contact": "rina@example.com"},
        {"id": "crew-004", "project_id": PROJECT_ID, "name": "Dex Hall", "department": "Camera", "role": "DP", "call_time": "05:30", "status": "confirmed", "contact": "dex@example.com"},
        {"id": "crew-005", "project_id": PROJECT_ID, "name": "Mae Flint", "department": "G&E", "role": "Gaffer", "call_time": "05:15", "status": "confirmed", "contact": "mae@example.com"},
        {"id": "crew-006", "project_id": PROJECT_ID, "name": "Ira Stone", "department": "Sound", "role": "Production Mixer", "call_time": "05:30", "status": "confirmed", "contact": "ira@example.com"},
        {"id": "crew-007", "project_id": PROJECT_ID, "name": "June Porter", "department": "Art", "role": "Production Designer", "call_time": "05:00", "status": "confirmed", "contact": "june@example.com"},
        {"id": "crew-008", "project_id": PROJECT_ID, "name": "Leah Hart", "department": "Wardrobe", "role": "Costume Designer", "call_time": "05:15", "status": "confirmed", "contact": "leah@example.com"},
        {"id": "crew-009", "project_id": PROJECT_ID, "name": "Sage Nori", "department": "Hair/Makeup", "role": "HMU Head", "call_time": "04:45", "status": "confirmed", "contact": "sage@example.com"},
        {"id": "crew-010", "project_id": PROJECT_ID, "name": "Eli Brand", "department": "Editorial/Post", "role": "Editor", "call_time": "10:00", "status": "remote", "contact": "eli@example.com"},
    ]
    with get_conn(db_path) as conn:
        for member in crew:
            conn.execute(
                """INSERT OR IGNORE INTO crew_members
                   (id, project_id, name, department, role, call_time, status, contact)
                   VALUES (:id, :project_id, :name, :department, :role, :call_time, :status, :contact)""",
                member,
            )
    if verbose:
        print(f"[seed] Inserted {len(crew)} crew members")


def _seed_tasks(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    tasks = [
        {"id": "task-001", "project_id": PROJECT_ID, "department": "UPM / Production", "title": "Lock replacement exterior for City Hall scene", "owner": "Tom Reyes", "status": "open", "priority": "high", "due_date": "2026-06-12", "blocker": "Original permit rejected", "linked_scene_id": SCENE_IDS[4], "notes": "Need producer sign-off on move."},
        {"id": "task-002", "project_id": PROJECT_ID, "department": "1st AD", "title": "Rebalance warehouse day to protect 10-hour target", "owner": "Rina Vale", "status": "open", "priority": "high", "due_date": "2026-06-13", "blocker": "", "linked_scene_id": SCENE_IDS[1], "notes": "Reduce overtime risk."},
        {"id": "task-003", "project_id": PROJECT_ID, "department": "Camera", "title": "Prep rooftop dawn lens package", "owner": "Dex Hall", "status": "in_progress", "priority": "medium", "due_date": "2026-06-13", "blocker": "", "linked_scene_id": SCENE_IDS[0], "notes": "Anamorphic option pending."},
        {"id": "task-004", "project_id": PROJECT_ID, "department": "G&E", "title": "Secure rooftop battery distro", "owner": "Mae Flint", "status": "open", "priority": "medium", "due_date": "2026-06-13", "blocker": "", "linked_scene_id": SCENE_IDS[0], "notes": "Need rooftop power check."},
        {"id": "task-005", "project_id": PROJECT_ID, "department": "Sound", "title": "Warehouse noise floor scout", "owner": "Ira Stone", "status": "open", "priority": "medium", "due_date": "2026-06-12", "blocker": "", "linked_scene_id": SCENE_IDS[1], "notes": "Nearby freight line concern."},
        {"id": "task-006", "project_id": PROJECT_ID, "department": "Wardrobe", "title": "Fit MIRA night infiltration costume", "owner": "Leah Hart", "status": "open", "priority": "medium", "due_date": "2026-06-12", "blocker": "Talent travel pending", "linked_scene_id": SCENE_IDS[1], "notes": "Need measurements."},
        {"id": "task-007", "project_id": PROJECT_ID, "department": "Hair/Makeup", "title": "Continuity bible for rooftop to warehouse transition", "owner": "Sage Nori", "status": "in_progress", "priority": "medium", "due_date": "2026-06-13", "blocker": "", "linked_scene_id": SCENE_IDS[1], "notes": "Capture sweat progression."},
        {"id": "task-008", "project_id": PROJECT_ID, "department": "Locations", "title": "Neighborhood notification for night warehouse shoot", "owner": "Tom Reyes", "status": "open", "priority": "medium", "due_date": "2026-06-12", "blocker": "", "linked_scene_id": SCENE_IDS[1], "notes": "Traffic marshal required."},
        {"id": "task-009", "project_id": PROJECT_ID, "department": "VFX", "title": "Bid drone screen replacement", "owner": "Vendor TBD", "status": "open", "priority": "high", "due_date": "2026-06-11", "blocker": "Awaiting concept frames", "linked_scene_id": SCENE_IDS[1], "notes": "Need producer cost cap."},
        {"id": "task-010", "project_id": PROJECT_ID, "department": "Editorial/Post", "title": "Confirm overnight dailies proxy flow", "owner": "Eli Brand", "status": "open", "priority": "high", "due_date": "2026-06-13", "blocker": "", "linked_scene_id": None, "notes": "Frame.io-equivalent review timing target <24h."},
        {"id": "task-011", "project_id": PROJECT_ID, "department": "Legal/Payroll", "title": "Finalize location release packet", "owner": "Counsel", "status": "open", "priority": "medium", "due_date": "2026-06-12", "blocker": "", "linked_scene_id": SCENE_IDS[0], "notes": "Need insurance certificate attached."},
        {"id": "task-012", "project_id": PROJECT_ID, "department": "Distribution/Marketing", "title": "Assemble investor progress brief template", "owner": "Ava Mercer", "status": "open", "priority": "low", "due_date": "2026-06-20", "blocker": "", "linked_scene_id": None, "notes": "Use producer dashboard outputs."},
    ]
    with get_conn(db_path) as conn:
        for task in tasks:
            conn.execute(
                """INSERT OR IGNORE INTO tasks
                   (id, project_id, department, title, owner, status, priority, due_date, blocker, linked_scene_id, notes)
                   VALUES (:id, :project_id, :department, :title, :owner, :status, :priority, :due_date, :blocker, :linked_scene_id, :notes)""",
                task,
            )
    if verbose:
        print(f"[seed] Inserted {len(tasks)} tasks")


def _seed_approvals(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    approvals = [
        {"id": "appr-001", "project_id": PROJECT_ID, "department": "Producing", "approval_type": "budget", "item_name": "City Hall exterior replacement spend", "requested_by": "Tom Reyes", "status": "pending", "due_date": "2026-06-11", "notes": "Need contingency draw approval."},
        {"id": "appr-002", "project_id": PROJECT_ID, "department": "UPM / Production", "approval_type": "schedule", "item_name": "Warehouse day rebalance", "requested_by": "Rina Vale", "status": "pending", "due_date": "2026-06-12", "notes": "Protect 10-hour day."},
        {"id": "appr-003", "project_id": PROJECT_ID, "department": "VFX", "approval_type": "vendor", "item_name": "Drone cleanup vendor shortlist", "requested_by": "Vendor TBD", "status": "pending", "due_date": "2026-06-12", "notes": "Choose low-latency post path."},
        {"id": "appr-004", "project_id": PROJECT_ID, "department": "Editorial/Post", "approval_type": "workflow", "item_name": "Dailies review SLA", "requested_by": "Eli Brand", "status": "approved", "due_date": "2026-06-10", "notes": "24-hour max review latency."},
    ]
    with get_conn(db_path) as conn:
        for approval in approvals:
            conn.execute(
                """INSERT OR IGNORE INTO approvals
                   (id, project_id, department, approval_type, item_name, requested_by, status, due_date, notes)
                   VALUES (:id, :project_id, :department, :approval_type, :item_name, :requested_by, :status, :due_date, :notes)""",
                approval,
            )
    if verbose:
        print(f"[seed] Inserted {len(approvals)} approvals")


def _seed_assets(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    assets = [
        {"id": "asset-001", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[0], "department": "Editorial/Post", "asset_type": "dailies", "name": "Rooftop Dailies Batch A", "status": "ready_for_review", "version_label": "v1", "review_due": "2026-06-16", "notes": "Proxy upload complete"},
        {"id": "asset-002", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[1], "department": "VFX", "asset_type": "plate", "name": "Warehouse Drone Plate", "status": "pending", "version_label": "v0", "review_due": "2026-06-18", "notes": "Awaiting shoot"},
        {"id": "asset-003", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[3], "department": "Art", "asset_type": "reference", "name": "Encrypted Document Wall Ref", "status": "approved", "version_label": "final", "review_due": "2026-06-12", "notes": "Locked for continuity"},
        {"id": "asset-004", "project_id": PROJECT_ID, "scene_id": SCENE_IDS[1], "department": "Editorial/Post", "asset_type": "assembly", "name": "Warehouse Scene Assembly", "status": "in_progress", "version_label": "v0.2", "review_due": "2026-06-19", "notes": "Editor temp cut"},
        {"id": "asset-005", "project_id": PROJECT_ID, "scene_id": None, "department": "Distribution/Marketing", "asset_type": "presskit", "name": "Investor Lookbook PDF", "status": "in_progress", "version_label": "v0.1", "review_due": "2026-06-20", "notes": "Needs stills"},
    ]
    with get_conn(db_path) as conn:
        for asset in assets:
            conn.execute(
                """INSERT OR IGNORE INTO assets
                   (id, project_id, scene_id, department, asset_type, name, status, version_label, review_due, notes)
                   VALUES (:id, :project_id, :scene_id, :department, :asset_type, :name, :status, :version_label, :review_due, :notes)""",
                asset,
            )
    if verbose:
        print(f"[seed] Inserted {len(assets)} assets")


def _seed_reviews(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    reviews = [
        {"id": "review-001", "asset_id": "asset-001", "reviewer_role": "Director", "status": "pending", "note": "Check skyline continuity on frame edge.", "timecode": "00:00:08:12"},
        {"id": "review-002", "asset_id": "asset-001", "reviewer_role": "Producer", "status": "approved", "note": "Sunrise timing works.", "timecode": "00:00:03:05"},
        {"id": "review-003", "asset_id": "asset-004", "reviewer_role": "Editor", "status": "pending", "note": "Need insert pickup on encrypted document.", "timecode": "00:01:11:09"},
    ]
    with get_conn(db_path) as conn:
        for review in reviews:
            conn.execute(
                """INSERT OR IGNORE INTO reviews
                   (id, asset_id, reviewer_role, status, note, timecode)
                   VALUES (:id, :asset_id, :reviewer_role, :status, :note, :timecode)""",
                review,
            )
    if verbose:
        print(f"[seed] Inserted {len(reviews)} reviews")


def _seed_deliverables(db_path: Path, verbose: bool) -> None:
    from .schema import get_conn
    deliverables = [
        {"id": "deliv-001", "project_id": PROJECT_ID, "category": "legal", "name": "Chain of title packet", "status": "in_progress", "due_date": "2026-06-25", "recipient": "Distributor counsel", "notes": "Awaiting location release packet"},
        {"id": "deliv-002", "project_id": PROJECT_ID, "category": "editorial", "name": "Locked cut OTIO export", "status": "pending", "due_date": "2026-07-10", "recipient": "Post house", "notes": "Target OpenTimelineIO handoff"},
        {"id": "deliv-003", "project_id": PROJECT_ID, "category": "color", "name": "OpenColorIO show LUT package", "status": "pending", "due_date": "2026-07-14", "recipient": "Colorist", "notes": "Attach ACES/OCIO notes"},
        {"id": "deliv-004", "project_id": PROJECT_ID, "category": "marketing", "name": "Festival screener and lookbook", "status": "pending", "due_date": "2026-07-30", "recipient": "Festival strategy team", "notes": "Needs stills and logline polish"},
    ]
    with get_conn(db_path) as conn:
        for deliverable in deliverables:
            conn.execute(
                """INSERT OR IGNORE INTO deliverables
                   (id, project_id, category, name, status, due_date, recipient, notes)
                   VALUES (:id, :project_id, :category, :name, :status, :due_date, :recipient, :notes)""",
                deliverable,
            )
    if verbose:
        print(f"[seed] Inserted {len(deliverables)} deliverables")


if __name__ == "__main__":
    import sys
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/film.db")
    seed_database(path, verbose=True)
