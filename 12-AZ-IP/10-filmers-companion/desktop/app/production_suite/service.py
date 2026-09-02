"""Unified end-to-end production-suite services for FilmersCompanion."""
from __future__ import annotations

import math
import re
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from ..agents.ad_suite import ADChief
from ..agents.finance import FinanceOfficer
from ..agents.locations import LocationManager
from ..db.schema import get_conn

ALL_DEPARTMENTS = [
    "Producing",
    "UPM / Production",
    "1st AD",
    "Script Supervisor",
    "Camera",
    "G&E",
    "Sound",
    "Art",
    "Wardrobe",
    "Hair/Makeup",
    "Locations",
    "Transport",
    "Stunts/SPFX",
    "VFX",
    "Editorial/Post",
    "Legal/Payroll",
    "Distribution/Marketing",
]

DEPARTMENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "VFX": ("vfx", "cg", "screen", "monitor", "hologram", "digital", "composite"),
    "Stunts/SPFX": ("explosion", "fight", "fall", "crash", "stunt", "gun", "fire"),
    "Transport": ("car", "truck", "van", "drive", "chase", "vehicle", "motorcycle"),
    "Wardrobe": ("dress", "coat", "uniform", "costume", "wardrobe", "suit"),
    "Hair/Makeup": ("blood", "bruise", "aging", "makeup", "hair", "prosthetic"),
    "Art": ("desk", "prop", "warehouse", "office", "set", "wall", "room"),
    "Sound": ("crowd", "music", "speech", "radio", "announcement", "sirens"),
    "Camera": ("close", "wide", "tracking", "look", "watch", "reveal"),
    "Locations": ("alley", "street", "rooftop", "warehouse", "city", "exterior", "interior"),
}

SCENE_HEADING_RE = re.compile(r"^(INT\.?|EXT\.?|INT/EXT\.?|I/E\.?)\s*(.+)$", re.IGNORECASE)
CHARACTER_RE = re.compile(r"^[A-Z][A-Z0-9 '\-().]{1,40}$")


@dataclass
class ParsedScene:
    scene_number: str
    int_ext: str
    day_night: str
    heading: str
    synopsis: str
    page_count: float
    characters: list[str]


def _fetch_all(conn, query: str, params: tuple = ()) -> list[dict]:
    return [dict(r) for r in conn.execute(query, params).fetchall()]


def _one_liner_date(date_value: str | None) -> str:
    return date_value or "UNSCHEDULED"


def _normalize_department(value: str) -> str:
    lowered = (value or "").strip().lower()
    for department in ALL_DEPARTMENTS:
        if lowered == department.lower():
            return department
    aliases = {
        "producer": "Producing",
        "producing": "Producing",
        "line producer": "UPM / Production",
        "upm": "UPM / Production",
        "production": "UPM / Production",
        "1st ad": "1st AD",
        "ad": "1st AD",
        "script": "Script Supervisor",
        "script supervisor": "Script Supervisor",
        "camera": "Camera",
        "cinematography": "Camera",
        "lighting": "G&E",
        "grip": "G&E",
        "electric": "G&E",
        "g&e": "G&E",
        "sound": "Sound",
        "art": "Art",
        "wardrobe": "Wardrobe",
        "costume": "Wardrobe",
        "hair": "Hair/Makeup",
        "makeup": "Hair/Makeup",
        "hair/makeup": "Hair/Makeup",
        "locations": "Locations",
        "transport": "Transport",
        "stunts": "Stunts/SPFX",
        "spfx": "Stunts/SPFX",
        "vfx": "VFX",
        "post": "Editorial/Post",
        "editorial": "Editorial/Post",
        "legal": "Legal/Payroll",
        "payroll": "Legal/Payroll",
        "distribution": "Distribution/Marketing",
        "marketing": "Distribution/Marketing",
    }
    return aliases.get(lowered, value or "Producing")


class FilmProductionSuiteService:
    """High-level application service for the full production suite."""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    def import_script_text(
        self,
        project_id: str,
        title: str,
        content: str,
        script_format: str = "feature",
        revision_name: str = "White Draft",
        revision_color: str = "White",
        replace_existing: bool = False,
    ) -> dict:
        parsed_scenes = self._parse_script(content)
        script_id = str(uuid.uuid4())

        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, project_id, title)
            if replace_existing:
                self._clear_script_related(conn, project_id)
            conn.execute(
                """INSERT INTO scripts (id, project_id, title, format, current_revision, content)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (script_id, project_id, title, script_format, revision_color, content),
            )
            conn.execute(
                """INSERT INTO script_versions
                   (id, script_id, revision_name, revision_color, change_summary, content)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid.uuid4()),
                    script_id,
                    revision_name,
                    revision_color,
                    "Initial structured import",
                    content,
                ),
            )
            imported_scene_ids: list[str] = []
            characters_seen: set[str] = set()
            for parsed in parsed_scenes:
                scene_id = str(uuid.uuid4())
                imported_scene_ids.append(scene_id)
                conn.execute(
                    """INSERT INTO scenes
                       (id, project_id, scene_number, location_id, int_ext, day_night, synopsis, page_count, status, shoot_date)
                       VALUES (?, ?, ?, NULL, ?, ?, ?, ?, 'draft', NULL)""",
                    (
                        scene_id,
                        project_id,
                        parsed.scene_number,
                        parsed.int_ext,
                        parsed.day_night,
                        parsed.synopsis[:500],
                        parsed.page_count,
                    ),
                )
                self._seed_storyboard_placeholders(conn, project_id, scene_id, parsed)
                for element in self._build_scene_breakdown(project_id, scene_id, parsed):
                    conn.execute(
                        """INSERT INTO breakdown_elements
                           (id, project_id, scene_id, department, element_type, name, quantity, status, notes)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            element["id"],
                            project_id,
                            scene_id,
                            element["department"],
                            element["element_type"],
                            element["name"],
                            element["quantity"],
                            element["status"],
                            element["notes"],
                        ),
                    )
                for character_name in parsed.characters:
                    if character_name in characters_seen:
                        continue
                    characters_seen.add(character_name)
                    conn.execute(
                        """INSERT OR IGNORE INTO characters (id, project_id, name, performer, notes)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            str(uuid.uuid4()),
                            project_id,
                            character_name,
                            "",
                            "Detected from screenplay import",
                        ),
                    )

        return {
            "project_id": project_id,
            "script_id": script_id,
            "title": title,
            "scene_count": len(parsed_scenes),
            "character_count": len({c for scene in parsed_scenes for c in scene.characters}),
            "storyboard_panels_created": len(parsed_scenes) * 2,
            "breakdown_elements_created": sum(len(self._build_scene_breakdown(project_id, "preview", s)) for s in parsed_scenes),
        }

    def script_overview(self, project_id: str) -> dict:
        with get_conn(self.db_path) as conn:
            scripts = _fetch_all(conn, "SELECT * FROM scripts WHERE project_id=? ORDER BY created_at DESC", (project_id,))
            scenes = _fetch_all(conn, "SELECT * FROM scenes WHERE project_id=? ORDER BY scene_number", (project_id,))
            versions = _fetch_all(
                conn,
                """SELECT sv.* FROM script_versions sv
                   JOIN scripts s ON s.id = sv.script_id
                   WHERE s.project_id=?
                   ORDER BY sv.created_at DESC""",
                (project_id,),
            )
            characters = _fetch_all(conn, "SELECT * FROM characters WHERE project_id=? ORDER BY name", (project_id,))
        total_pages = round(sum(float(scene.get("page_count") or 0.0) for scene in scenes), 2)
        return {
            "project_id": project_id,
            "script_count": len(scripts),
            "revision_count": len(versions),
            "scene_count": len(scenes),
            "character_count": len(characters),
            "total_pages": total_pages,
            "current_script": scripts[0]["title"] if scripts else None,
            "revision_colors": [v.get("revision_color") for v in versions[:5]],
            "scene_headings": [
                {
                    "scene_number": scene.get("scene_number"),
                    "int_ext": scene.get("int_ext"),
                    "day_night": scene.get("day_night"),
                    "synopsis": scene.get("synopsis"),
                    "shoot_date": scene.get("shoot_date"),
                }
                for scene in scenes[:20]
            ],
        }

    def breakdown_summary(self, project_id: str) -> dict:
        with get_conn(self.db_path) as conn:
            scenes = _fetch_all(conn, "SELECT * FROM scenes WHERE project_id=?", (project_id,))
            elements = _fetch_all(
                conn,
                "SELECT * FROM breakdown_elements WHERE project_id=? ORDER BY department, scene_id, name",
                (project_id,),
            )
        dept_counts = Counter(_normalize_department(row.get("department", "")) for row in elements)
        type_counts = Counter(row.get("element_type", "") for row in elements)
        scene_counts = Counter(row.get("scene_id", "") for row in elements)
        uncovered = [
            {
                "scene_number": scene.get("scene_number"),
                "synopsis": scene.get("synopsis"),
            }
            for scene in scenes
            if scene_counts.get(scene.get("id", ""), 0) == 0
        ]
        return {
            "project_id": project_id,
            "element_count": len(elements),
            "departments": dict(sorted(dept_counts.items())),
            "element_types": dict(sorted(type_counts.items())),
            "scenes_with_breakdowns": len(scene_counts),
            "scenes_without_breakdowns": uncovered,
            "sample_elements": elements[:25],
        }

    def schedule_overview(self, project_id: str) -> dict:
        with get_conn(self.db_path) as conn:
            scenes = _fetch_all(conn, "SELECT * FROM scenes WHERE project_id=? ORDER BY shoot_date, scene_number", (project_id,))
            days = _fetch_all(conn, "SELECT * FROM schedule_days WHERE project_id=? ORDER BY shoot_date", (project_id,))
            strips = _fetch_all(conn, "SELECT * FROM schedule_strips WHERE project_id=? ORDER BY schedule_day_id, strip_order", (project_id,))
            locations = _fetch_all(conn, "SELECT * FROM locations WHERE project_id=?", (project_id,))
            call_sheets = _fetch_all(conn, "SELECT * FROM call_sheets WHERE project_id=? ORDER BY shoot_date", (project_id,))
        location_names = {row["id"]: row["name"] for row in locations}
        scheduled_pages = round(sum(float(scene.get("page_count") or 0.0) for scene in scenes if scene.get("shoot_date")), 2)
        unscheduled = [scene for scene in scenes if not scene.get("shoot_date")]
        total_estimated_hours = round(sum(float(strip.get("estimated_hours") or 0.0) for strip in strips), 2)
        company_moves = sum(int(strip.get("company_move") or 0) for strip in strips)

        turnaround_risks = []
        ad = ADChief()
        for idx in range(len(days) - 1):
            current = days[idx]
            nxt = days[idx + 1]
            result = ad.check_turnaround(current.get("wrap_time") or "20:00", nxt.get("general_call") or "07:00")
            if result["violation"]:
                turnaround_risks.append(
                    {
                        "from_date": current.get("shoot_date"),
                        "to_date": nxt.get("shoot_date"),
                        "gap_hours": result["gap_hours"],
                    }
                )

        scene_lookup = {scene["id"]: scene for scene in scenes}
        one_liner_scenes = []
        for strip in strips:
            scene = scene_lookup.get(strip.get("scene_id"))
            if scene:
                one_liner_scenes.append(scene)

        return {
            "project_id": project_id,
            "shoot_day_count": len(days),
            "call_sheet_count": len(call_sheets),
            "scheduled_scene_count": len([scene for scene in scenes if scene.get("shoot_date")]),
            "unscheduled_scene_count": len(unscheduled),
            "scheduled_pages": scheduled_pages,
            "estimated_hours": total_estimated_hours,
            "company_moves": company_moves,
            "turnaround_risks": turnaround_risks,
            "one_liner": ad.generate_one_liner(one_liner_scenes) if one_liner_scenes else "",
            "days": [
                {
                    **day,
                    "location_name": location_names.get(day.get("location_id")),
                }
                for day in days
            ],
            "unscheduled_scenes": [
                {
                    "scene_number": scene.get("scene_number"),
                    "synopsis": scene.get("synopsis"),
                }
                for scene in unscheduled
            ],
        }

    def dood_report(self, project_id: str) -> dict:
        with get_conn(self.db_path) as conn:
            cast_rows = _fetch_all(
                conn,
                """SELECT be.name, s.shoot_date
                   FROM breakdown_elements be
                   JOIN scenes s ON s.id = be.scene_id
                   WHERE be.project_id=? AND lower(be.department)='cast'""",
                (project_id,),
            )
            dates = [
                row["shoot_date"]
                for row in conn.execute(
                    "SELECT shoot_date FROM schedule_days WHERE project_id=? ORDER BY shoot_date",
                    (project_id,),
                ).fetchall()
                if row["shoot_date"]
            ]
        unique_dates = sorted(dict.fromkeys(dates))
        workdays: dict[str, set[str]] = defaultdict(set)
        for row in cast_rows:
            if row.get("shoot_date"):
                workdays[row["name"]].add(row["shoot_date"])

        chart = []
        for performer, performer_dates in sorted(workdays.items()):
            timeline = {date_value: ("W" if date_value in performer_dates else "") for date_value in unique_dates}
            if performer_dates:
                first = min(performer_dates)
                last = max(performer_dates)
                for date_value in unique_dates:
                    if first < date_value < last and date_value not in performer_dates:
                        timeline[date_value] = "H"
            chart.append({"name": performer, "timeline": timeline})

        return {
            "project_id": project_id,
            "date_columns": unique_dates,
            "cast_rows": chart,
            "optimization_notes": [
                "W = work day, H = hold day.",
                "Reduce hold days by grouping cast-heavy scenes and protecting turnaround.",
            ],
        }

    def post_overview(self, project_id: str) -> dict:
        with get_conn(self.db_path) as conn:
            assets = _fetch_all(conn, "SELECT * FROM assets WHERE project_id=? ORDER BY department, name", (project_id,))
            deliverables = _fetch_all(conn, "SELECT * FROM deliverables WHERE project_id=? ORDER BY due_date, category", (project_id,))
            reviews = _fetch_all(
                conn,
                """SELECT r.*, a.name AS asset_name
                   FROM reviews r
                   JOIN assets a ON a.id = r.asset_id
                   WHERE a.project_id=?
                   ORDER BY r.created_at DESC""",
                (project_id,),
            )
        asset_status = Counter(row.get("status", "") for row in assets)
        deliverable_status = Counter(row.get("status", "") for row in deliverables)
        review_status = Counter(row.get("status", "") for row in reviews)
        return {
            "project_id": project_id,
            "asset_count": len(assets),
            "deliverable_count": len(deliverables),
            "review_count": len(reviews),
            "asset_status": dict(sorted(asset_status.items())),
            "deliverable_status": dict(sorted(deliverable_status.items())),
            "review_status": dict(sorted(review_status.items())),
            "pending_reviews": [row for row in reviews if row.get("status") != "approved"][:15],
            "deliverables": deliverables[:20],
        }

    def department_board(self, project_id: str, department: str) -> dict:
        normalized = _normalize_department(department)
        with get_conn(self.db_path) as conn:
            tasks = _fetch_all(
                conn,
                "SELECT * FROM tasks WHERE project_id=? AND department=? ORDER BY priority DESC, due_date",
                (project_id, normalized),
            )
            approvals = _fetch_all(
                conn,
                "SELECT * FROM approvals WHERE project_id=? AND department=? ORDER BY due_date",
                (project_id, normalized),
            )
            crew = _fetch_all(
                conn,
                "SELECT * FROM crew_members WHERE project_id=? AND department=? ORDER BY role, name",
                (project_id, normalized),
            )
            elements = _fetch_all(
                conn,
                "SELECT * FROM breakdown_elements WHERE project_id=? AND department=? ORDER BY scene_id, name",
                (project_id, normalized),
            )
            assets = _fetch_all(
                conn,
                "SELECT * FROM assets WHERE project_id=? AND department=? ORDER BY status, name",
                (project_id, normalized),
            )
        blocked = [task for task in tasks if task.get("blocker")]
        pending_approvals = [approval for approval in approvals if approval.get("status") != "approved"]
        open_tasks = [task for task in tasks if task.get("status") not in ("done", "approved")]
        readiness = "READY"
        if blocked or len(pending_approvals) >= 2:
            readiness = "AT_RISK"
        elif open_tasks or pending_approvals:
            readiness = "WATCH"
        return {
            "project_id": project_id,
            "department": normalized,
            "readiness": readiness,
            "crew": crew,
            "open_task_count": len(open_tasks),
            "blocked_task_count": len(blocked),
            "pending_approval_count": len(pending_approvals),
            "tasks": tasks[:20],
            "approvals": approvals[:20],
            "breakdown_elements": elements[:20],
            "assets": assets[:20],
        }

    def all_department_boards(self, project_id: str) -> dict:
        boards = [self.department_board(project_id, department) for department in ALL_DEPARTMENTS]
        return {
            "project_id": project_id,
            "departments": boards,
        }

    def producer_dashboard(self, project_id: str) -> dict:
        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, project_id, project_id)
            project_row = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
            scenes = _fetch_all(conn, "SELECT * FROM scenes WHERE project_id=?", (project_id,))
            locations = _fetch_all(conn, "SELECT * FROM locations WHERE project_id=?", (project_id,))
            budget_lines = _fetch_all(conn, "SELECT * FROM budget_lines WHERE project_id=?", (project_id,))
            approvals = _fetch_all(conn, "SELECT * FROM approvals WHERE project_id=?", (project_id,))
            tasks = _fetch_all(conn, "SELECT * FROM tasks WHERE project_id=?", (project_id,))

        finance = FinanceOfficer()
        loc_mgr = LocationManager()
        budget_health = finance.calc_burn_rate(budget_lines)
        budget_alerts = finance.budget_alert(budget_lines, 0.8)
        unconfirmed_locations = loc_mgr.check_unconfirmed(scenes, locations)
        schedule = self.schedule_overview(project_id)
        script = self.script_overview(project_id)
        breakdown = self.breakdown_summary(project_id)
        post = self.post_overview(project_id)
        department_boards = self.all_department_boards(project_id)["departments"]

        alerts: list[str] = []
        if unconfirmed_locations:
            alerts.append(f"{len(unconfirmed_locations)} scene(s) depend on pending or rejected locations.")
        if budget_alerts:
            alerts.append(f"{len(budget_alerts)} budget category alert(s) have crossed the configured burn threshold.")
        if schedule["unscheduled_scene_count"]:
            alerts.append(f"{schedule['unscheduled_scene_count']} scene(s) remain unscheduled.")
        if schedule["turnaround_risks"]:
            alerts.append(f"{len(schedule['turnaround_risks'])} turnaround risk(s) detected in the schedule.")
        pending_approvals = [item for item in approvals if item.get("status") != "approved"]
        if pending_approvals:
            alerts.append(f"{len(pending_approvals)} approval(s) are still pending.")
        blocked_tasks = [task for task in tasks if task.get("blocker") and task.get("status") not in ("done", "approved")]
        if blocked_tasks:
            alerts.append(f"{len(blocked_tasks)} blocked task(s) require producer or UPM intervention.")
        if post["pending_reviews"]:
            alerts.append(f"{len(post['pending_reviews'])} review item(s) are awaiting sign-off.")

        status = "GREEN"
        if len(alerts) >= 5:
            status = "RED"
        elif alerts:
            status = "YELLOW"

        at_risk_departments = [board["department"] for board in department_boards if board["readiness"] == "AT_RISK"]
        return {
            "project_id": project_id,
            "project": dict(project_row) if project_row else {"id": project_id},
            "status": status,
            "alerts": alerts,
            "summary": {
                "scripts": script["script_count"],
                "scenes": script["scene_count"],
                "pages": script["total_pages"],
                "shoot_days": schedule["shoot_day_count"],
                "scheduled_pages": schedule["scheduled_pages"],
                "budget_total": budget_health.get("total_budgeted", 0.0),
                "budget_actual": budget_health.get("total_actual", 0.0),
                "budget_burn_pct": budget_health.get("burn_rate_pct", 0.0),
                "pending_reviews": len(post["pending_reviews"]),
                "pending_approvals": len(pending_approvals),
            },
            "schedule": schedule,
            "script": script,
            "breakdown": {
                "element_count": breakdown["element_count"],
                "departments": breakdown["departments"],
            },
            "finance": {
                **budget_health,
                "alerts": budget_alerts,
            },
            "locations": {
                "total": len(locations),
                "unconfirmed": unconfirmed_locations,
            },
            "departments": department_boards,
            "at_risk_departments": at_risk_departments,
            "post": post,
            "upm_brief": self._build_upm_brief(project_row["title"] if project_row else project_id, alerts, at_risk_departments, schedule),
        }

    def create_task(self, body: dict) -> dict:
        task_id = body.get("id") or str(uuid.uuid4())
        department = _normalize_department(body.get("department", "Producing"))
        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, body.get("project_id", ""), body.get("project_id", "Untitled Project"))
            conn.execute(
                """INSERT OR REPLACE INTO tasks
                   (id, project_id, department, title, owner, status, priority, due_date, blocker, linked_scene_id, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    task_id,
                    body.get("project_id", ""),
                    department,
                    body.get("title", ""),
                    body.get("owner", ""),
                    body.get("status", "open"),
                    body.get("priority", "medium"),
                    body.get("due_date"),
                    body.get("blocker", ""),
                    body.get("linked_scene_id"),
                    body.get("notes", ""),
                ),
            )
        return {"id": task_id, "status": "created", "department": department}

    def create_approval(self, body: dict) -> dict:
        approval_id = body.get("id") or str(uuid.uuid4())
        department = _normalize_department(body.get("department", "Producing"))
        with get_conn(self.db_path) as conn:
            self._ensure_project(conn, body.get("project_id", ""), body.get("project_id", "Untitled Project"))
            conn.execute(
                """INSERT OR REPLACE INTO approvals
                   (id, project_id, department, approval_type, item_name, requested_by, status, due_date, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    approval_id,
                    body.get("project_id", ""),
                    department,
                    body.get("approval_type", "general"),
                    body.get("item_name", ""),
                    body.get("requested_by", ""),
                    body.get("status", "pending"),
                    body.get("due_date"),
                    body.get("notes", ""),
                ),
            )
        return {"id": approval_id, "status": "created", "department": department}

    def list_approvals(self, project_id: str) -> dict:
        with get_conn(self.db_path) as conn:
            approvals = _fetch_all(conn, "SELECT * FROM approvals WHERE project_id=? ORDER BY due_date", (project_id,))
        return {
            "project_id": project_id,
            "pending": [row for row in approvals if row.get("status") != "approved"],
            "all": approvals,
        }

    def _ensure_project(self, conn, project_id: str, title: str) -> None:
        conn.execute(
            """INSERT OR IGNORE INTO projects
               (id, title, format, stage, logline, status, shoot_days, target_day_hours, contingency_pct)
               VALUES (?, ?, 'feature', 'prep', '', 'active', 0, 10.0, 12.0)""",
            (project_id, title or project_id),
        )

    def _clear_script_related(self, conn, project_id: str) -> None:
        scene_ids = [row[0] for row in conn.execute("SELECT id FROM scenes WHERE project_id=?", (project_id,)).fetchall()]
        if scene_ids:
            placeholders = ",".join("?" for _ in scene_ids)
            conn.execute(f"DELETE FROM shot_lists WHERE scene_id IN ({placeholders})", scene_ids)
            conn.execute(f"DELETE FROM storyboard_panels WHERE scene_id IN ({placeholders})", scene_ids)
            conn.execute(f"DELETE FROM breakdown_elements WHERE scene_id IN ({placeholders})", scene_ids)
            conn.execute(f"DELETE FROM assets WHERE scene_id IN ({placeholders})", scene_ids)
            conn.execute(f"DELETE FROM schedule_strips WHERE scene_id IN ({placeholders})", scene_ids)
        conn.execute("DELETE FROM scenes WHERE project_id=?", (project_id,))
        conn.execute("DELETE FROM scripts WHERE project_id=?", (project_id,))
        conn.execute("DELETE FROM characters WHERE project_id=?", (project_id,))

    def _parse_script(self, content: str) -> list[ParsedScene]:
        lines = [line.rstrip() for line in content.splitlines()]
        parsed: list[ParsedScene] = []
        heading = None
        body_lines: list[str] = []
        characters: set[str] = set()
        scene_idx = 0

        def finalize() -> None:
            nonlocal scene_idx, heading, body_lines, characters
            if heading is None:
                return
            scene_idx += 1
            synopsis = " ".join(line.strip() for line in body_lines if line.strip())
            match = SCENE_HEADING_RE.match(heading)
            token = match.group(1).upper() if match else "INT"
            suffix = match.group(2).upper() if match else heading.upper()
            day_night = "N" if "NIGHT" in suffix or "EVENING" in suffix else "D"
            page_count = max(0.125, round(max(len(synopsis.split()), 12) / 125.0, 3))
            parsed.append(
                ParsedScene(
                    scene_number=str(scene_idx),
                    int_ext="EXT" if token.startswith("EXT") else "INT",
                    day_night=day_night,
                    heading=heading,
                    synopsis=synopsis or heading.title(),
                    page_count=page_count,
                    characters=sorted(characters),
                )
            )
            heading = None
            body_lines = []
            characters = set()

        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped:
                continue
            if SCENE_HEADING_RE.match(stripped):
                finalize()
                heading = stripped
                continue
            if heading is None:
                continue
            if CHARACTER_RE.match(stripped) and len(stripped.split()) <= 4:
                characters.add(stripped.title())
            else:
                body_lines.append(stripped)
        finalize()
        return parsed

    def _build_scene_breakdown(self, project_id: str, scene_id: str, parsed: ParsedScene) -> list[dict]:
        elements = []
        lowered = f"{parsed.heading} {parsed.synopsis}".lower()

        def add(department: str, element_type: str, name: str, quantity: int = 1, status: str = "identified", notes: str = ""):
            elements.append(
                {
                    "id": str(uuid.uuid4()),
                    "department": department,
                    "element_type": element_type,
                    "name": name,
                    "quantity": quantity,
                    "status": status,
                    "notes": notes,
                }
            )

        add("Camera", "coverage", "Master / coverage package", notes="Baseline coverage package.")
        add("G&E", "lighting", f"{parsed.int_ext} {parsed.day_night} lighting plan", notes="Protect 10-hour day with pre-rig as needed.")
        add("Sound", "sound", "Sync sound package", notes="Monitor ambient noise and wild lines.")
        add("1st AD", "schedule", "Scene scheduling strip", notes="Tie to one-liner and call sheet flow.")
        add("Script Supervisor", "continuity", "Continuity notes", notes="Track lined script, takes, and pickups.")
        add("Editorial/Post", "dailies", "Proxy/dailies ingest", notes="Deliver notes within 24h.")
        if parsed.characters:
            for character_name in parsed.characters:
                add("Cast", "cast", character_name, notes="Detected speaking role.")
                add("Wardrobe", "costume", f"{character_name} costume continuity")
                add("Hair/Makeup", "hmua", f"{character_name} hair/makeup continuity")
        if parsed.day_night == "N":
            add("Locations", "logistics", "Night access / neighborhood notification", notes="Confirm noise, parking, security.")
        for department, keywords in DEPARTMENT_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                add(department, "scene_requirement", f"{department} prep package", notes=f"Triggered by screenplay language in scene {parsed.scene_number}.")
        if parsed.int_ext == "EXT":
            add("Locations", "permit", "Exterior permit / backup weather plan", status="pending")
        else:
            add("Art", "set_dressing", "Interior set dressing and practicals")
        if "press" in lowered or "crowd" in lowered:
            add("Producing", "extras", "Background casting plan")
        if "mission" in lowered or "briefing" in lowered:
            add("VFX", "graphics", "On-screen briefing graphics / playback")
        return elements

    def _seed_storyboard_placeholders(self, conn, project_id: str, scene_id: str, parsed: ParsedScene) -> None:
        panels = [
            {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "scene_id": scene_id,
                "panel_number": 1,
                "shot_label": "Master",
                "visual_mode": "template",
                "description": f"{parsed.heading} master coverage",
                "lens": "35mm",
                "movement": "static",
                "duration_sec": 12.0,
                "notes": "Editorial safety / geography.",
            },
            {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "scene_id": scene_id,
                "panel_number": 2,
                "shot_label": "Coverage",
                "visual_mode": "template",
                "description": f"{parsed.heading} emotional coverage",
                "lens": "85mm",
                "movement": "push-in",
                "duration_sec": 8.0,
                "notes": "Performance emphasis.",
            },
        ]
        for panel in panels:
            conn.execute(
                """INSERT INTO storyboard_panels
                   (id, project_id, scene_id, panel_number, shot_label, visual_mode, description, lens, movement, duration_sec, notes)
                   VALUES (:id, :project_id, :scene_id, :panel_number, :shot_label, :visual_mode, :description, :lens, :movement, :duration_sec, :notes)""",
                panel,
            )

    def _build_upm_brief(self, title: str, alerts: list[str], at_risk_departments: list[str], schedule: dict) -> str:
        parts = [f"Project: {title}"]
        parts.append(f"Schedule: {schedule['scheduled_scene_count']} scheduled scene(s), {schedule['unscheduled_scene_count']} unscheduled.")
        if schedule["turnaround_risks"]:
            parts.append(f"Turnaround: {len(schedule['turnaround_risks'])} risk(s) need adjustment.")
        if at_risk_departments:
            parts.append("At-risk departments: " + ", ".join(at_risk_departments[:6]))
        if alerts:
            parts.append("Top alerts: " + "; ".join(alerts[:4]))
        else:
            parts.append("No critical alerts. Protect contingency and maintain information loops.")
        return "\n".join(parts)

