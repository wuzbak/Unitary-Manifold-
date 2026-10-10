"""Post-pipeline interchange bridge — DaVinci Resolve, OpenTimelineIO, EDL.

Provides offline-safe export of production data (shot lists, schedule
strips) into industry-interchange formats, plus an optional live bridge to
DaVinci Resolve's scripting API when running inside (or alongside) Resolve.

DaVinci Resolve (Blackmagic Design) ships a free "Resolve" edition with a
first-class Python scripting API (``DaVinciResolveScript``). That module is
only importable when ``RESOLVE_SCRIPT_API`` / ``RESOLVE_SCRIPT_LIB`` are set
(normally by the Resolve installer) — this bridge detects and uses it when
present, and otherwise degrades gracefully to file-based interchange (EDL /
CSV) that Resolve, Premiere, and Avid can all import directly.
"""
from __future__ import annotations

import csv
import io
import uuid
from pathlib import Path

from ..db.schema import get_conn

RESOLVE_CAPABILITY_PACKET = {
    "project": "DaVinci Resolve (Blackmagic Design) — free edition",
    "research_basis": [
        "Resolve Developer documentation: DaVinciResolveScript.py",
        "Comp/Readme.txt (Fusion scripting), Resolve API manual",
    ],
    "why": "Industry-standard, free (non-Studio) color grading, editing, "
    "Fusion VFX, and Fairlight audio NLE. Full Python/Lua scripting API "
    "covers project/timeline/media-pool automation end-to-end.",
    "integration": "connect_resolve() auto-detects DaVinciResolveScript on "
    "PYTHONPATH (set by the Resolve installer) and, when available, can "
    "create bins/timelines directly; otherwise export_edl()/export_otio_json() "
    "produce files for manual import via File > Import > Timeline.",
}

OPENTIMELINEIO_CAPABILITY_PACKET = {
    "project": "AcademySoftwareFoundation/OpenTimelineIO",
    "research_basis": ["README.md", "src/py-opentimelineio", "docs/tutorials"],
    "why": "Open-source (Academy Software Foundation) interchange format for "
    "editorial timelines — adapters exist for Resolve, Premiere, Final Cut, "
    "Avid, and Nuke; the de facto FOSS standard for cross-NLE conform.",
    "integration": "export_otio_json() emits a minimal OTIO-compatible JSON "
    "timeline; for full adapter support, pip install opentimelineio and feed "
    "this JSON (or the EDL export) to `otiotool`.",
}

EDL_CAPABILITY_PACKET = {
    "project": "CMX3600 EDL (open, de facto standard)",
    "research_basis": ["SMPTE / CMX3600 EDL specification (public domain lineage)"],
    "why": "Universally supported plain-text edit-decision-list format — "
    "importable by Resolve, Premiere, Avid, and virtually every NLE without "
    "a plugin.",
    "integration": "export_edl() renders scheduled shots as a conformed "
    "CMX3600 EDL with synthetic non-drop-frame timecodes at 24fps.",
}

_DEFAULT_FPS = 24
_DEFAULT_CLIP_SECONDS = 5.0


def _frames_to_timecode(total_frames: int, fps: int = _DEFAULT_FPS) -> str:
    total_frames = max(0, int(total_frames))
    frames = total_frames % fps
    total_seconds = total_frames // fps
    seconds = total_seconds % 60
    total_minutes = total_seconds // 60
    minutes = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"


class PostPipelineBridge:
    """DaVinci Resolve / OTIO / EDL interchange for FilmersCompanion."""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    # ------------------------------------------------------------------
    # Live DaVinci Resolve scripting bridge (optional, offline-safe)
    # ------------------------------------------------------------------

    def connect_resolve(self) -> dict:
        """Attempt to connect to a running DaVinci Resolve instance.

        Returns a status dict; never raises. Falls back cleanly when the
        Resolve application/scripting environment is not present (the
        normal case in a server/CI environment).
        """
        try:
            import DaVinciResolveScript as dvr_script  # type: ignore
        except ImportError:
            return {
                "connected": False,
                "mode": "offline",
                "reason": "DaVinciResolveScript module not on PYTHONPATH "
                "(Resolve not installed/running in this environment).",
            }
        try:
            resolve = dvr_script.scriptapp("Resolve")
        except Exception as exc:  # pragma: no cover - requires live Resolve
            return {"connected": False, "mode": "offline", "reason": str(exc)}
        if resolve is None:  # pragma: no cover - requires live Resolve
            return {"connected": False, "mode": "offline", "reason": "Resolve returned no app handle."}
        return {  # pragma: no cover - requires live Resolve
            "connected": True,
            "mode": "live",
            "product_name": resolve.GetProductName(),
        }

    # ------------------------------------------------------------------
    # File-based interchange (always available)
    # ------------------------------------------------------------------

    def export_edl(self, project_id: str, fps: int = _DEFAULT_FPS) -> str:
        """Render scheduled/shot-listed scenes as a CMX3600 EDL."""
        with get_conn(self.db_path) as conn:
            project = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
            rows = conn.execute(
                """SELECT sl.shot_number, sl.coverage_type, sl.lens, sl.movement, sl.notes,
                          sc.scene_number, sc.id AS scene_id
                   FROM shot_lists sl
                   JOIN scenes sc ON sc.id = sl.scene_id
                   WHERE sc.project_id = ?
                   ORDER BY sc.scene_number, sl.shot_number""",
                (project_id,),
            ).fetchall()
        title = (project["title"] if project else project_id) or project_id
        lines = [f"TITLE: {title}", "FCM: NON-DROP FRAME", ""]
        frames_per_clip = int(round(_DEFAULT_CLIP_SECONDS * fps))
        cursor = 0
        for index, row in enumerate(rows, start=1):
            clip_name = f"SC{row['scene_number']}_SH{row['shot_number']:03d}"
            src_in = _frames_to_timecode(0, fps)
            src_out = _frames_to_timecode(frames_per_clip, fps)
            rec_in = _frames_to_timecode(cursor, fps)
            rec_out = _frames_to_timecode(cursor + frames_per_clip, fps)
            lines.append(f"{index:03d}  {clip_name:<12} V     C        {src_in} {src_out} {rec_in} {rec_out}")
            lines.append(f"* FROM CLIP NAME: {clip_name}")
            if row["coverage_type"]:
                lines.append(f"* COMMENT: {row['coverage_type']} / {row['lens'] or 'n/a'} / {row['movement'] or 'n/a'}")
            lines.append("")
            cursor += frames_per_clip
        edl_text = "\n".join(lines)
        self._record_export(project_id, "EDL", "DaVinci Resolve / generic NLE", f"{project_id}.edl", edl_text)
        return edl_text

    def export_shotlist_csv(self, project_id: str) -> str:
        """Export the full shot list as CSV (Resolve, Premiere, spreadsheet-ready)."""
        with get_conn(self.db_path) as conn:
            rows = conn.execute(
                """SELECT sc.scene_number, sl.shot_number, sl.coverage_type, sl.lens,
                          sl.movement, sl.frame_rate, sl.notes
                   FROM shot_lists sl
                   JOIN scenes sc ON sc.id = sl.scene_id
                   WHERE sc.project_id = ?
                   ORDER BY sc.scene_number, sl.shot_number""",
                (project_id,),
            ).fetchall()
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["scene_number", "shot_number", "coverage_type", "lens", "movement", "frame_rate", "notes"])
        for row in rows:
            writer.writerow([row["scene_number"], row["shot_number"], row["coverage_type"],
                              row["lens"], row["movement"], row["frame_rate"], row["notes"]])
        csv_text = buf.getvalue()
        self._record_export(project_id, "CSV", "Shot List", f"{project_id}_shotlist.csv", csv_text)
        return csv_text

    def export_otio_json(self, project_id: str, fps: int = _DEFAULT_FPS) -> dict:
        """Export a minimal OpenTimelineIO-compatible timeline JSON."""
        with get_conn(self.db_path) as conn:
            project = conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
            rows = conn.execute(
                """SELECT sl.shot_number, sc.scene_number
                   FROM shot_lists sl
                   JOIN scenes sc ON sc.id = sl.scene_id
                   WHERE sc.project_id = ?
                   ORDER BY sc.scene_number, sl.shot_number""",
                (project_id,),
            ).fetchall()
        frames_per_clip = int(round(_DEFAULT_CLIP_SECONDS * fps))
        clips = [
            {
                "OTIO_SCHEMA": "Clip.1",
                "name": f"SC{row['scene_number']}_SH{row['shot_number']:03d}",
                "source_range": {
                    "OTIO_SCHEMA": "TimeRange.1",
                    "start_time": {"OTIO_SCHEMA": "RationalTime.1", "value": 0, "rate": fps},
                    "duration": {"OTIO_SCHEMA": "RationalTime.1", "value": frames_per_clip, "rate": fps},
                },
            }
            for row in rows
        ]
        timeline = {
            "OTIO_SCHEMA": "Timeline.1",
            "name": (project["title"] if project else project_id) or project_id,
            "tracks": {
                "OTIO_SCHEMA": "Stack.1",
                "children": [
                    {"OTIO_SCHEMA": "Track.1", "name": "V1", "kind": "Video", "children": clips}
                ],
            },
        }
        self._record_export(project_id, "OTIO-JSON", "OpenTimelineIO", f"{project_id}.otio.json", str(timeline))
        return timeline

    def list_exports(self, project_id: str) -> list[dict]:
        with get_conn(self.db_path) as conn:
            return [
                dict(r)
                for r in conn.execute(
                    "SELECT id, export_format, target_tool, file_name, created_at "
                    "FROM post_pipeline_exports WHERE project_id=? ORDER BY created_at DESC",
                    (project_id,),
                ).fetchall()
            ]

    def _record_export(self, project_id: str, export_format: str, target_tool: str,
                        file_name: str, content: str) -> None:
        with get_conn(self.db_path) as conn:
            conn.execute(
                """INSERT INTO post_pipeline_exports
                   (id, project_id, export_format, target_tool, file_name, content)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), project_id, export_format, target_tool, file_name, content),
            )
