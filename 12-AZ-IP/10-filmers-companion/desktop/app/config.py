"""
FilmersCompanion — Configuration
==================================
Central config for the Filmmaker's Companion desktop app.
All settings can be overridden via environment variables or a .env file.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

APP_DIR   = Path(__file__).parent
DESKTOP_DIR = APP_DIR.parent
FILM_DIR  = DESKTOP_DIR.parent
REPO_ROOT = FILM_DIR.parent.parent  # apps/filmmakers-companion/ → repo root


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

@dataclass
class FilmConfig:
    # Database
    db_path: Path = field(
        default_factory=lambda: FILM_DIR / "data" / "film.db"
    )

    # Server
    port: int = field(
        default_factory=lambda: int(os.getenv("FILM_PORT", "7864"))
    )
    host: str = field(
        default_factory=lambda: os.getenv("FILM_HOST", "0.0.0.0")
    )

    # Remote LLM (OpenAI-compatible)
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("FILM_OPENAI_API_KEY", "")
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("FILM_OPENAI_MODEL", "gpt-4o-mini")
    )

    # Local LLM (Ollama)
    local_llm_url: str = field(
        default_factory=lambda: os.getenv(
            "FILM_LLM_URL", "http://localhost:11434/api/generate"
        )
    )
    local_llm_model: str = field(
        default_factory=lambda: os.getenv("FILM_LLM_MODEL", "llama3.2:3b")
    )

    # Offline mode
    offline_mode: bool = field(
        default_factory=lambda: os.getenv("FILM_OFFLINE", "false").lower() in ("true", "1", "yes")
    )

    def __post_init__(self):
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)


# Module-level singleton (lazy)
_config: FilmConfig | None = None


def get_config() -> FilmConfig:
    global _config
    if _config is None:
        env_file = FILM_DIR / ".env"
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                pass
        _config = FilmConfig()
    return _config
