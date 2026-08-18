"""
FilmersCompanion — Base Agent
================================
Abstract base for all production agents. Resolves questions via:
  1. Remote LLM (OpenAI-compatible)
  2. Local LLM (Ollama)
  3. Static KB fallback
"""
from __future__ import annotations

import json


class BaseAgent:
    def __init__(self, config=None, offline_mode: bool | None = None):
        from ..config import get_config
        self.config = config or get_config()
        if offline_mode is not None:
            # Allow tests to override offline_mode without touching the singleton
            import copy
            self.config = copy.copy(self.config)
            object.__setattr__(self.config, "offline_mode", offline_mode)

    def resolve(self, question: str, context: str = "") -> str:
        """Remote LLM → Ollama → Static KB → hardcoded fallback."""
        if not self.config.offline_mode:
            try:
                return self._call_remote(question, context)
            except Exception:
                pass
            try:
                return self._call_ollama(question, context)
            except Exception:
                pass
        return self._static_kb_answer(question, context)

    def _call_remote(self, question: str, context: str) -> str:
        """POST to OpenAI-compatible API."""
        import httpx
        if not self.config.openai_api_key:
            raise ValueError("No OpenAI API key configured")
        prompt = f"{context}\n\nQuestion: {question}" if context else question
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.config.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.config.openai_model,
                "messages": [
                    {"role": "system", "content": "You are an expert film production assistant."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 512,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    def _call_ollama(self, question: str, context: str) -> str:
        """POST to Ollama generate endpoint."""
        import httpx
        prompt = f"{context}\n\nQuestion: {question}" if context else question
        response = httpx.post(
            self.config.local_llm_url,
            json={
                "model": self.config.local_llm_model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()

    def _static_kb_answer(self, question: str, context: str = "") -> str:
        """Search static KB and return formatted answer."""
        from ..kb.film_kb import search_kb, AXIOM_OMEGA_PRINCIPLES
        terms = question.lower().split()
        results = []
        for term in terms:
            if len(term) > 3:
                hits = search_kb(term)
                for h in hits:
                    if h not in results:
                        results.append(h)
        if results:
            answer_parts = []
            for r in results[:3]:
                answer_parts.append(f"[{r['keyword'].upper()}] {r['content']}")
            return "\n\n".join(answer_parts)
        # Final fallback: relevant principle
        for idx, principle in AXIOM_OMEGA_PRINCIPLES.items():
            for term in terms:
                if term in principle.lower():
                    return f"Axiom Omega Principle {idx}: {principle}"
        return (
            "No specific guidance found in the knowledge base for that question. "
            "Refer to your production manual or consult your department head."
        )
