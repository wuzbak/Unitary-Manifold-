"""
FilmersCompanion — AD Chief Agent
====================================
Assistant Director suite: call sheets, turnaround, one-liners.
"""
from __future__ import annotations

from .base import BaseAgent


class ADChief(BaseAgent):
    """Assistant Director tools for scheduling and crew management."""

    MIN_TURNAROUND_HOURS = 12

    def generate_call_sheet(
        self,
        scenes: list[dict],
        location: dict,
        shoot_date: str,
    ) -> str:
        """Generate a formatted call sheet string."""
        loc_name = location.get("name", "TBD")
        loc_address = location.get("address", "TBD")
        scene_numbers = ", ".join(s.get("scene_number", "?") for s in scenes)
        page_total = sum(float(s.get("page_count", 0)) for s in scenes)

        lines = [
            "=" * 60,
            f"  CALL SHEET — {shoot_date}",
            "=" * 60,
            f"  Location:     {loc_name}",
            f"  Address:      {loc_address}",
            f"  Scenes:       {scene_numbers}",
            f"  Total Pages:  {page_total:.1f}",
            "-" * 60,
            "  SCENES:",
        ]
        for scene in scenes:
            sn = scene.get("scene_number", "?")
            ie = scene.get("int_ext", "?")
            dn = scene.get("day_night", "?")
            syn = scene.get("synopsis", "")[:60]
            lines.append(f"    Sc {sn:>3}  {ie}/{dn}  {syn}")

        lines += [
            "-" * 60,
            "  NOTES: Distribute by midnight the prior night.",
            "  Nearest hospital on advance schedule.",
            "=" * 60,
        ]
        return "\n".join(lines)

    def check_turnaround(self, wrap_time: str, call_time: str) -> dict:
        """
        Check if turnaround between wrap and call is sufficient (≥12h).
        Accepts HH:MM strings. Handles overnight (call < wrap → add 24h to call).
        """
        def _parse(t: str) -> float:
            parts = t.strip().split(":")
            h = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else 0
            return h + m / 60.0

        wrap_h = _parse(wrap_time)
        call_h = _parse(call_time)

        # Handle overnight: if call is less than or equal to wrap, it's next day
        if call_h <= wrap_h:
            call_h += 24.0

        gap_hours = call_h - wrap_h
        violation = gap_hours < self.MIN_TURNAROUND_HOURS

        if violation:
            message = (
                f"⚠️ TURNAROUND VIOLATION: {gap_hours:.1f}h gap "
                f"(minimum {self.MIN_TURNAROUND_HOURS}h required). "
                f"Adjust call time or negotiate with SAG-AFTRA."
            )
        else:
            message = (
                f"✅ Turnaround OK: {gap_hours:.1f}h gap "
                f"(≥{self.MIN_TURNAROUND_HOURS}h minimum)."
            )

        return {
            "wrap_time": wrap_time,
            "call_time": call_time,
            "gap_hours": round(gap_hours, 2),
            "violation": violation,
            "message": message,
        }

    def generate_one_liner(self, scenes: list[dict]) -> str:
        """Generate a condensed one-liner scene list."""
        if not scenes:
            return "(No scenes scheduled)"
        lines = ["ONE-LINER", "-" * 50]
        for scene in scenes:
            sn = scene.get("scene_number", "?")
            ie = scene.get("int_ext", "?")
            dn = scene.get("day_night", "?")
            loc = scene.get("location_id", "TBD")
            syn = scene.get("synopsis", "")[:50]
            pg = scene.get("page_count", 0)
            lines.append(f"  {sn:>3}  {ie}/{dn}  [{loc}]  {syn}  ({pg}pp)")
        return "\n".join(lines)
