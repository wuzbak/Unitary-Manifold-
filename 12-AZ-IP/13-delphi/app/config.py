"""
DelPhi — Configuration
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path

APP_DIR = Path(__file__).parent
DELPHI_DIR = APP_DIR.parent
REPO_ROOT = DELPHI_DIR.parent


@dataclass
class DelphiConfig:
    db_path: Path = field(
        default_factory=lambda: Path(os.getenv("DELPHI_DB_PATH", DELPHI_DIR / "data" / "delphi.db"))
    )
    port: int = field(default_factory=lambda: int(os.getenv("DELPHI_PORT", "7863")))
    host: str = field(default_factory=lambda: os.getenv("DELPHI_HOST", "0.0.0.0"))
    offline_mode: bool = field(
        default_factory=lambda: os.getenv("DELPHI_OFFLINE", "true").lower() == "true"
    )
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )
    local_llm_url: str = field(
        default_factory=lambda: os.getenv(
            "LOCAL_LLM_URL", "http://localhost:11434/api/generate"
        )
    )
    local_llm_model: str = field(
        default_factory=lambda: os.getenv("LOCAL_LLM_MODEL", "llama3.2:3b")
    )

    def __post_init__(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)


_config: DelphiConfig | None = None


def get_config() -> DelphiConfig:
    global _config
    if _config is None:
        env_file = DELPHI_DIR / ".env"
        if env_file.exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                pass
        _config = DelphiConfig()
    return _config


# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, and synthesis: GitHub Copilot (AI).
