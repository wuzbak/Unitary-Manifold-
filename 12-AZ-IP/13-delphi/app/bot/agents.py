"""
DelPhi — Bot Agents
DelphiGovernor orchestrates five specialist agents (offline-first).
"""
from __future__ import annotations

import json
import logging
from datetime import date as _date
from typing import Any, Optional

from delphi.app.oracle.astrology import build_astrology_reading
from delphi.app.oracle.chinese_zodiac import build_chinese_zodiac_reading
from delphi.app.oracle.runes import build_rune_reading
from delphi.app.oracle.tarot import build_reading as build_tarot_reading

log = logging.getLogger(__name__)


class BaseAgent:
    name: str = "Base"

    def _try_llm(self, prompt: str) -> Optional[str]:
        try:
            from delphi.app.config import get_config
            cfg = get_config()
            if cfg.offline_mode or not cfg.openai_api_key:
                return None
            import openai
            openai.api_key = cfg.openai_api_key
            resp = openai.ChatCompletion.create(
                model=cfg.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
            )
            return resp.choices[0].message.content
        except Exception as exc:
            log.debug("LLM unavailable: %s", exc)
            return None

    def run(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class TarotAgent(BaseAgent):
    name = "TarotAgent"

    def run(
        self,
        spread_type: str = "three_card",
        question: str = "",
        user_id: str = "anonymous",
        date_str: Optional[str] = None,
    ) -> dict[str, Any]:
        date_str = date_str or _date.today().isoformat()
        reading = build_tarot_reading(
            question=question,
            user_id=user_id,
            reading_date=date_str,
            spread_type=spread_type,
        )
        llm_text = self._try_llm(
            f"You are a wise tarot reader. The querent asks: '{question}'. "
            f"Cards: {json.dumps([c['card_name'] for c in reading.get('cards', [])])}\n"
            "Provide a 3-sentence insightful synthesis."
        )
        if llm_text:
            reading["synthesis"] = llm_text
        return {"agent": self.name, "reading": reading}


class RuneAgent(BaseAgent):
    name = "RuneAgent"

    def run(
        self,
        spread_type: str = "three_rune",
        question: str = "",
        user_id: str = "anonymous",
        date_str: Optional[str] = None,
    ) -> dict[str, Any]:
        date_str = date_str or _date.today().isoformat()
        reading = build_rune_reading(
            question=question,
            user_id=user_id,
            reading_date=date_str,
            spread_type=spread_type,
        )
        llm_text = self._try_llm(
            f"You are a Norse rune reader. Question: '{question}'. "
            f"Runes: {json.dumps([c['rune']['name'] for c in reading.get('cast', [])])}\n"
            "Weave the rune meanings into a 3-sentence reading."
        )
        if llm_text:
            reading["synthesis"] = llm_text
        return {"agent": self.name, "reading": reading}


class AstrologyAgent(BaseAgent):
    name = "AstrologyAgent"

    def run(
        self,
        birth_date: str = "1990-01-01",
        birth_time: Optional[str] = None,
        question: str = "",
        user_id: str = "anonymous",
        date_str: Optional[str] = None,
    ) -> dict[str, Any]:
        reading = build_astrology_reading(
            birth_date_str=birth_date,
            birth_time_str=birth_time,
            user_id=user_id,
        )
        llm_text = self._try_llm(
            f"Astrologer. Birth: {birth_date}. "
            f"Sun: {reading.get('sun_sign', {}).get('name')}. Question: '{question}'.\n"
            "Give a 3-sentence reading."
        )
        synthesis = llm_text or reading.get("natal_summary", "")
        reading["synthesis"] = synthesis
        return {"agent": self.name, "reading": reading}


class ChineseZodiacAgent(BaseAgent):
    name = "ChineseZodiacAgent"

    def run(
        self,
        year: int = 1990,
        question: str = "",
        user_id: str = "anonymous",
        date_str: Optional[str] = None,
    ) -> dict[str, Any]:
        reading = build_chinese_zodiac_reading(birth_year=year, user_id=user_id)
        llm_text = self._try_llm(
            f"Chinese astrologer. Born {year} ({reading.get('animal')}). "
            f"Question: '{question}'.\nGive a 3-sentence forecast."
        )
        synthesis = llm_text or reading.get("summary", "")
        reading["synthesis"] = synthesis
        return {"agent": self.name, "reading": reading}


class SynthesisAgent(BaseAgent):
    name = "SynthesisAgent"

    def run(self, readings: list[dict[str, Any]], question: str = "") -> dict[str, Any]:
        summaries = []
        for r in readings:
            oracle = r.get("agent", "unknown")
            synthesis = r.get("reading", {}).get("synthesis", "")
            summaries.append(f"[{oracle}] {synthesis}")

        combined = "Across all oracles: " + " | ".join(summaries)
        llm_text = self._try_llm(
            f"Master diviner integrating oracles. Question: '{question}'.\n"
            + "\n".join(summaries)
            + "\nProvide a 4-sentence meta-synthesis."
        )
        return {
            "agent": self.name,
            "question": question,
            "synthesis": llm_text or combined,
            "source_readings": len(readings),
        }


class DelphiGovernor:
    """Orchestrates all five agents for multi-oracle consultations."""

    def __init__(self) -> None:
        self.tarot = TarotAgent()
        self.rune = RuneAgent()
        self.astrology = AstrologyAgent()
        self.chinese_zodiac = ChineseZodiacAgent()
        self.synthesis = SynthesisAgent()

    def consult(
        self,
        question: str,
        user_id: str = "anonymous",
        birth_date: Optional[str] = None,
        year: Optional[int] = None,
        oracles: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        date_str = _date.today().isoformat()
        oracles = oracles or ["tarot", "rune"]
        readings: list[dict] = []

        if "tarot" in oracles:
            readings.append(self.tarot.run(question=question, user_id=user_id, date_str=date_str))
        if "rune" in oracles:
            readings.append(self.rune.run(question=question, user_id=user_id, date_str=date_str))
        if "astrology" in oracles and birth_date:
            readings.append(self.astrology.run(birth_date=birth_date, question=question,
                                                user_id=user_id, date_str=date_str))
        if "chinese_zodiac" in oracles and year:
            readings.append(self.chinese_zodiac.run(year=year, question=question,
                                                      user_id=user_id, date_str=date_str))

        meta = self.synthesis.run(readings=readings, question=question)
        return {
            "governor": "DelphiGovernor",
            "question": question,
            "readings": readings,
            "meta_synthesis": meta["synthesis"],
        }


# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, and synthesis: GitHub Copilot (AI).
